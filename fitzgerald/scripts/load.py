"""
load.py - Semrush + Ahrefs reader/normaliser for the Fitzgerald backlink audit.

Handles the Semrush unquoted semicolon-delimited CSV trap: HTML entities are
unescaped FIRST, then the row is parsed by right-anchoring the structured tail
fields (which have strict patterns) so stray semicolons inside titles/anchors
cannot shift the structured columns.

Reads:
  data/rd/refdomains_*.csv   Semrush referring domains (authoritative domain list + AS)
  data/fetch/backlinks_*.csv Semrush backlinks (links, anchors, targets, redirect_url)
  data/ahrefs/ahrefs_refdomains.csv   Ahrefs referring domains (discovery)
  data/ahrefs/ahrefs_backlinks.csv    Ahrefs backlinks (discovery + HTTP code)

Writes:
  data/processed/refdomains.json   {domain: {...semrush metrics...}}
  data/processed/links.jsonl       one normalised link record per line
"""
import os, sys, json, html, glob, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(DATA, "processed")
os.makedirs(OUT, exist_ok=True)

MONEY = "fitzgeraldplumbing.com"

# multi-part public suffixes we are likely to meet (fallback reg-domain extraction)
MULTI_SUFFIX = {
    "co.uk","org.uk","me.uk","gov.uk","ac.uk","co.in","net.in","org.in","co.za",
    "com.au","net.au","org.au","co.nz","com.br","com.mx","co.jp","or.jp","ne.jp",
    "com.sg","com.my","co.id","or.id","com.ph","com.tr","com.ar","com.co","com.pk",
    "co.ke","com.ng","com.ua","co.il","com.vn","com.tw","com.hk","org.au","gov.au",
}
def regdom(host):
    """Best-effort registered domain from a host, honouring common 2-level suffixes."""
    if not host: return host
    labels = host.split('.')
    if len(labels) <= 2:
        return host
    last2 = ".".join(labels[-2:])
    last3 = ".".join(labels[-3:])
    if last2 in MULTI_SUFFIX:
        return last3
    return last2

def host_of(url):
    if not url:
        return ""
    u = url.strip()
    u = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', u)   # strip scheme
    u = u.split('/')[0].split('?')[0].split('#')[0]      # netloc
    u = u.split('@')[-1]                                  # strip userinfo
    u = u.split(':')[0]                                   # strip port
    u = u.lower().strip('.')
    if u.startswith('www.'):
        u = u[4:]
    return u

def canon(url):
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', u)
    if u.startswith('www.'):
        u = u[4:]
    u = u.rstrip('/')
    return u

# ---------- referring domains (Semrush) ----------
def _i(x):
    try: return int(float(x))
    except: return 0

def load_refdomains():
    """Authoritative referring-domain metrics from the clean, sorted rd_as/ pull
    (header: domain;domain_ascore;domain_trust_score;ip;country;first_seen;backlinks_num).
    Falls back to the older rd/ 8-col pull for any domain not present."""
    rd = {}
    # primary: rd_as (clean, non-overlapping)
    for f in sorted(glob.glob(os.path.join(DATA, "rd_as", "refdomains_as_*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("domain;"):
                    continue
                parts = html.unescape(line).split(";")
                if len(parts) != 7:
                    continue
                dom, asc, trust, ip, country, fs, bn = parts
                dom = dom.strip().lower()
                if dom.startswith("www."): dom = dom[4:]
                if not dom or dom in rd:
                    continue
                rd[dom] = {"domain": dom, "backlinks_num": _i(bn), "ascore": _i(asc),
                           "trust": _i(trust), "ip": ip.strip(), "country": country.strip(),
                           "first_seen": _i(fs), "last_seen": 0}
    # fallback: old rd/ 8-col pull (domain;backlinks_num;domain_ascore;domain_trust_score;ip;country;first_seen;last_seen)
    for f in sorted(glob.glob(os.path.join(DATA, "rd", "refdomains_*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("domain;"):
                    continue
                parts = html.unescape(line).split(";")
                if len(parts) != 8:
                    continue
                dom = parts[0].strip().lower()
                if dom.startswith("www."): dom = dom[4:]
                if not dom or dom in rd:
                    continue
                rd[dom] = {"domain": dom, "backlinks_num": _i(parts[1]), "ascore": _i(parts[2]),
                           "trust": _i(parts[3]), "ip": parts[4].strip(), "country": parts[5].strip(),
                           "first_seen": _i(parts[6]), "last_seen": _i(parts[7])}
    return rd

# ---------- backlinks (Semrush) ----------
BL_HDR = "source_url;source_title;target_url;anchor;nofollow;first_seen;last_seen;response_code;redirect_url;page_ascore"

def parse_backlink_line(line):
    """Return dict or None. Right-anchor the 6 structured tail fields."""
    line = html.unescape(line)
    t = line.split(";")
    if len(t) < 10:
        return None
    page_ascore = t[-1]
    redirect_url = t[-2]
    response_code = t[-3]
    last_seen = t[-4]
    first_seen = t[-5]
    nofollow = t[-6]
    source_url = t[0]
    middle = t[1:-6]            # source_title, target_url, anchor (possibly split)
    # find target_url = first token that looks like an http(s) URL
    ti = None
    for idx, tok in enumerate(middle):
        if tok.startswith("http://") or tok.startswith("https://"):
            ti = idx
            break
    if ti is None:
        # no clear url; assume middle = [title, target, anchor] best-effort
        source_title = middle[0] if middle else ""
        target_url = middle[1] if len(middle) > 1 else ""
        anchor = ";".join(middle[2:]) if len(middle) > 2 else ""
    else:
        source_title = ";".join(middle[:ti])
        target_url = middle[ti]
        anchor = ";".join(middle[ti+1:])
    def i(x):
        try: return int(float(x))
        except: return 0
    return {
        "source_url": source_url,
        "source_title": source_title,
        "target_url": target_url,
        "anchor": anchor,
        "nofollow": str(nofollow).strip().lower() == "true",
        "first_seen": i(first_seen),
        "last_seen": i(last_seen),
        "response_code": i(response_code),
        "redirect_url": redirect_url.strip(),
        "page_ascore": i(page_ascore),
        "tool": "Semrush",
    }

def load_semrush_backlinks():
    links = []
    bad = 0
    files = sorted(glob.glob(os.path.join(DATA, "fetch", "backlinks_*.csv")))
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("source_url;"):
                    continue
                rec = parse_backlink_line(line)
                if rec is None:
                    bad += 1
                    continue
                links.append(rec)
    return links, bad

# ---------- Ahrefs ----------
def load_ahrefs_backlinks():
    """Ahrefs backlinks exported as JSON-lines or CSV we control. Expect a TSV/CSV
    written by our fetch worker with columns we pick. We standardise on JSON here."""
    path = os.path.join(DATA, "ahrefs", "ahrefs_backlinks.jsonl")
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except:
                    continue
                out.append(r)
    return out

def load_ahrefs_refdomains():
    path = os.path.join(DATA, "ahrefs", "ahrefs_refdomains.jsonl")
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except:
                    continue
                d = (r.get("domain") or "").strip().lower()
                if d.startswith("www."): d = d[4:]
                if d:
                    out[d] = r
    return out

# ---------- domain matching ----------
def build_domain_matcher(domains):
    dset = set(domains)
    def match(h):
        if not h:
            return None
        if h in dset:
            return h
        labels = h.split(".")
        for k in range(1, len(labels)-1):
            cand = ".".join(labels[k:])
            if cand in dset:
                return cand
        return None
    return match

def main():
    rd = load_refdomains()
    sl, bad = load_semrush_backlinks()
    print(f"Semrush refdomains: {len(rd)}")
    print(f"Semrush backlinks parsed: {len(sl)}  (unparseable: {bad})")

    # ---- load Ahrefs first so the domain universe is complete before matching ----
    ar = load_ahrefs_refdomains()
    ab = load_ahrefs_backlinks()

    # domain universe = Semrush refdomains U Ahrefs refdomains (authoritative registered-domain lists)
    universe = set(rd.keys()) | set(ar.keys())
    match = build_domain_matcher(universe)

    # assign source_domain to each semrush link; fall back to registered-domain heuristic
    dedup = {}
    fellback = 0
    for r in sl:
        h = host_of(r["source_url"])
        d = match(h)
        if d is None:
            d = regdom(h)
            fellback += 1
        r["source_domain"] = d
        key = (canon(r["source_url"]), canon(r["target_url"]), r["anchor"].strip().lower())
        if key not in dedup:
            dedup[key] = r
    print(f"Semrush links deduped: {len(dedup)}  (keyed by reg-domain fallback: {fellback})")
    print(f"Ahrefs refdomains: {len(ar)}   Ahrefs backlinks: {len(ab)}")

    # Ahrefs-only link discovery
    added = 0
    for r in ab:
        su = r.get("url_from") or r.get("source_url") or ""
        tu = r.get("url_to") or r.get("target_url") or ""
        anc = (r.get("anchor") or "").strip()
        key = (canon(su), canon(tu), anc.lower())
        h = host_of(su)
        d = match(h) or regdom(h)
        if key in dedup:
            dedup[key]["tool"] = "Semrush+Ahrefs"
            # carry Ahrefs http code / first seen if semrush missing
            if not dedup[key].get("response_code") and r.get("http_code"):
                dedup[key]["response_code"] = int(r.get("http_code") or 0)
            if not dedup[key].get("first_seen") and r.get("first_seen_ts"):
                dedup[key]["first_seen"] = int(r.get("first_seen_ts") or 0)
            continue
        nofollow = bool(r.get("nofollow"))
        rec = {
            "source_url": su, "source_title": r.get("title") or "",
            "target_url": tu, "anchor": anc,
            "nofollow": nofollow,
            "first_seen": int(r.get("first_seen_ts") or 0),
            "last_seen": int(r.get("last_seen_ts") or 0),
            "response_code": int(r.get("http_code") or 0),
            "redirect_url": "",
            "page_ascore": 0,
            "tool": "Ahrefs",
            "source_domain": d,
        }
        dedup[key] = rec
        added += 1
    print(f"Ahrefs-only links added: {added}")

    # Ahrefs-only referring domains (not in Semrush set)
    ar_added = 0
    for d, r in ar.items():
        if match(d) is None and d not in rd:
            rd[d] = {
                "domain": d, "backlinks_num": int(r.get("backlinks") or 0),
                "ascore": 0, "trust": 0,
                "ip": r.get("ip") or "", "country": "",
                "first_seen": int(r.get("first_seen_ts") or 0),
                "last_seen": int(r.get("last_seen_ts") or 0),
                "ahrefs_only": True,
            }
            ar_added += 1
    print(f"Ahrefs-only referring domains added: {ar_added}")

    links = list(dedup.values())

    # ensure every domain referenced by a link has a refdomain record (metrics may be empty)
    stub_added = 0
    link_doms = set(r["source_domain"] for r in links)
    for d in link_doms:
        if d not in rd:
            # try to inherit Ahrefs metrics if the exact domain is an Ahrefs refdomain
            a = ar.get(d, {})
            rd[d] = {
                "domain": d, "backlinks_num": int(a.get("backlinks") or 0),
                "ascore": 0, "trust": 0,
                "ip": a.get("ip","") or "", "country": "",
                "first_seen": int(a.get("first_seen_ts") or 0), "last_seen": 0,
                "metrics_missing": True,
                "dr": a.get("domain_rating"),
            }
            stub_added += 1
    print(f"Stub refdomain records added for link-only domains: {stub_added}")

    with open(os.path.join(OUT, "refdomains.json"), "w", encoding="utf-8") as fh:
        json.dump(rd, fh)
    with open(os.path.join(OUT, "links.jsonl"), "w", encoding="utf-8") as fh:
        for r in links:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"WROTE refdomains.json ({len(rd)}) and links.jsonl ({len(links)})")

if __name__ == "__main__":
    main()
