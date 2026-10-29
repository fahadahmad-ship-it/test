"""
load.py — read every Semrush + Ahrefs export for the superkexpress.com audit from
disk, parse safely, and merge into one per-referring-domain structure plus a merged
link list. Run with python3 -I. Downloaded data is untrusted: we only parse it, never
execute it.

Principles honoured here:
 - Semrush is the source for every METRIC (Authority Score, backlinks, RD's, dates,
   IP, country). Ahrefs contributes link discovery, a live-page signal (http_code),
   is_spam corroboration, and recovered first-seen dates — never a headline metric.
 - Semrush ships unquoted semicolon CSV with HTML entities left in titles/anchors.
   We split on ';' first, REJECT any row whose column count is wrong (rather than
   letting a split title leak a phantom column), then unescape entities per field.
 - Ahrefs ships proper RFC-4180 CSV (quoted, embedded newlines/commas) — use csv.
"""
import csv, html, json, os, sys, glob
from urllib.parse import urlsplit

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
DATA = os.path.normpath(DATA)

# ---------- canonicalisation ----------
def host_of(url):
    if not url:
        return ""
    u = url.strip()
    if "://" not in u:
        u = "http://" + u
    try:
        h = urlsplit(u).hostname or ""
    except Exception:
        h = ""
    return h.lower()

# Two-label public suffixes (eTLD second levels) seen in the data + the common set,
# so a host reduces to its registrable root (eTLD+1) and subdomains fold into it,
# matching Semrush's root-level refdomain grouping. Not exhaustive like the full PSL,
# but covers every multi-part TLD present in this profile.
MULTI_SUFFIX = {
    "co.uk","org.uk","ac.uk","gov.uk","me.uk","net.uk","ltd.uk","plc.uk","sch.uk",
    "co.in","net.in","org.in","gen.in","firm.in","ind.in","gov.in","ac.in","edu.in",
    "co.jp","or.jp","ne.jp","ac.jp","go.jp","com.au","net.au","org.au","edu.au","gov.au",
    "co.nz","org.nz","com.br","net.br","org.br","gov.br","edu.br","com.mx","com.ar",
    "com.bz","com.lc","com.co","edu.pe","gob.pe","com.pe","org.pe","co.za","org.za",
    "com.sg","com.my","com.ph","com.tr","com.tw","com.hk","com.cn","com.ua","co.id",
    "com.pk","com.bd","com.ng","com.gh","co.ke","co.il","com.sa","com.eg","co.th",
}

# Public-subdomain PLATFORMS (PSL "private" registries): a site is the SUBDOMAIN, so we
# must NOT collapse x.blogspot.com into blogspot.com and then disavow the whole platform.
# Each spammy sub-site is disavowed at its own subdomain. Handled like a multi-label suffix.
PLATFORM_SUFFIX = {
    "wordpress.com", "typepad.com", "tripod.com", "angelfire.com", "weebly.com",
    "livejournal.com", "hatenablog.com", "hatenablog.jp", "hatena.ne.jp", "hateblo.jp",
    "seesaa.net", "cocolog-nifty.com", "livedoor.jp", "livedoor.biz", "blog.jp",
    "webnode.com", "jimdofree.com", "wixsite.com", "github.io", "gitlab.io", "za.com",
    "neocities.org", "000webhostapp.com", "blogger.com", "amebaownd.com", "ameblo.jp",
    "fc2.com", "webs.com", "simplesite.com", "over-blog.com", "blog.fc2.com",
    "wordpress.org", "medium.com", "substack.com", "tumblr.com", "square.site",
    "godaddysites.com", "mystrikingly.com", "page.tl", "ucoz.com", "ucoz.ru", "narod.ru",
}

def registrable_root(host):
    h = (host or "").strip().lower().rstrip(".")
    if h.startswith("www."):
        h = h[4:]
    if not h or "." not in h:
        return h
    labels = h.split(".")
    # blogspot.* has many ccTLD variants — treat everything from 'blogspot' on as the suffix
    if "blogspot" in labels:
        i = labels.index("blogspot")
        if i >= 1:
            return ".".join(labels[i - 1:])
    # 3-label platform suffixes (e.g. blog.fc2.com)
    if len(labels) >= 4 and ".".join(labels[-3:]) in PLATFORM_SUFFIX:
        return ".".join(labels[-4:])
    # 2-label platform/public suffixes
    if len(labels) >= 3 and ".".join(labels[-2:]) in (MULTI_SUFFIX | PLATFORM_SUFFIX):
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])

def canon_domain(host):
    """Canonical referring domain key: registrable root (eTLD+1), www dropped."""
    return registrable_root(host)

def to_int(x, default=0):
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return default

def to_float(x, default=0.0):
    try:
        return float(x)
    except (ValueError, TypeError):
        return default

# ---------- Semrush semicolon CSV ----------
def read_semrush_csv(path, ncols):
    """Yield lists of exactly ncols unescaped fields. Reject malformed rows."""
    rejected = 0
    rows = []
    if not os.path.exists(path):
        return rows, rejected
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    if not lines:
        return rows, rejected
    header = lines[0].split(";")
    for ln in lines[1:]:
        if ln == "":
            continue
        parts = ln.split(";")
        if len(parts) != ncols:
            rejected += 1
            continue
        rows.append([html.unescape(p) for p in parts])
    return rows, rejected

# ---------- Ahrefs proper CSV ----------
def read_ahrefs_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))

# ---------- loaders ----------
def load_semrush_refdomains():
    """domain -> metrics dict (authoritative)."""
    out = {}
    cols = ["domain","backlinks_num","domain_ascore","domain_trust_score",
            "ip","country","first_seen","last_seen"]
    total_rejected = 0
    for path in sorted(glob.glob(os.path.join(DATA, "rd", "refdomains_offset_*.csv"))):
        rows, rej = read_semrush_csv(path, len(cols))
        total_rejected += rej
        for r in rows:
            d = dict(zip(cols, r))
            dom = canon_domain(d["domain"])
            if not dom:
                continue
            # keep the row with the most backlinks if duplicate canonical appears
            prev = out.get(dom)
            rec = {
                "domain": dom,
                "raw_domain": d["domain"],
                "sr_backlinks": to_int(d["backlinks_num"]),
                "as": to_int(d["domain_ascore"]),
                "trust": to_int(d["domain_trust_score"]),
                "ip": d["ip"],
                "country": d["country"],
                "first_seen": to_int(d["first_seen"]),
                "last_seen": to_int(d["last_seen"]),
            }
            if prev is None or rec["sr_backlinks"] > prev["sr_backlinks"]:
                out[dom] = rec
    return out, total_rejected

def load_semrush_links():
    """List of link dicts from all Semrush backlink exports (deduped)."""
    cols = ["source_url","source_title","target_url","anchor","nofollow",
            "first_seen","last_seen","response_code","redirect_url","page_ascore"]
    seen = set()
    links = []
    total_rejected = 0
    paths = sorted(glob.glob(os.path.join(DATA, "fetch", "nonbisicon_offset_*.csv")))
    paths += [os.path.join(DATA, "fetch", "bisicon_sample.csv")]
    paths += sorted(glob.glob(os.path.join(DATA, "fetch", "backlinks_offset_*.csv")))
    for path in paths:
        rows, rej = read_semrush_csv(path, len(cols))
        total_rejected += rej
        for r in rows:
            d = dict(zip(cols, r))
            rdom = canon_domain(host_of(d["source_url"]))
            key = (d["source_url"], d["target_url"], d["anchor"])
            if key in seen:
                continue
            seen.add(key)
            links.append({
                "tool": "Semrush",
                "refdomain": rdom,
                "source_url": d["source_url"],
                "source_title": d["source_title"],
                "target_url": d["target_url"],
                "anchor": d["anchor"],
                "nofollow": str(d["nofollow"]).strip().lower() in ("true","1","yes"),
                "first_seen": to_int(d["first_seen"]),
                "last_seen": to_int(d["last_seen"]),
                "http_code": to_int(d["response_code"]),
                "redirect_url": d["redirect_url"],
                "page_ascore": to_int(d["page_ascore"]),
            })
    return links, total_rejected

def _ahrefs_dt_to_unix(s):
    # Ahrefs dates look like 2026-07-22T10:43:59Z
    import datetime
    if not s:
        return 0
    try:
        return int(datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp())
    except Exception:
        return 0

def load_ahrefs_links():
    links = []
    seen = set()
    files = [p for p in sorted(glob.glob(os.path.join(DATA, "ahrefs", "ahrefs_*.csv")))
             if os.path.basename(p) != "ahrefs_refdomains.csv"]
    for path in files:
        for d in read_ahrefs_csv(path):
            src = d.get("url_from","")
            tgt = d.get("url_to","")
            anc = d.get("anchor","") or ""
            key = (src, tgt, anc)
            if key in seen:
                continue
            seen.add(key)
            rdom = canon_domain(d.get("name_source","") or host_of(src))
            links.append({
                "tool": "Ahrefs",
                "refdomain": rdom,
                "source_url": src,
                "source_title": d.get("title","") or "",
                "target_url": tgt,
                "anchor": anc,
                "nofollow": str(d.get("is_nofollow","")).strip().lower()=="true",
                "dofollow": str(d.get("is_dofollow","")).strip().lower()=="true",
                "first_seen": _ahrefs_dt_to_unix(d.get("first_seen_link","")),
                "last_seen": _ahrefs_dt_to_unix(d.get("last_visited","")),
                "http_code": to_int(d.get("http_code")),
                "is_spam": str(d.get("is_spam","")).strip().lower()=="true",
                "link_type": d.get("link_type","") or "",
            })
    return links

def load_ahrefs_refdomains():
    out = {}
    for d in read_ahrefs_csv(os.path.join(DATA, "ahrefs", "ahrefs_refdomains.csv")):
        dom = canon_domain(d.get("domain",""))
        if not dom:
            continue
        out[dom] = {
            "dr": to_float(d.get("domain_rating")),
            "links_to_target": to_int(d.get("links_to_target")),
            "dofollow_links": to_int(d.get("dofollow_links")),
            "is_spam": str(d.get("is_spam","")).strip().lower()=="true",
            "ip": d.get("ip_source","") or "",
            "first_seen": _ahrefs_dt_to_unix(d.get("first_seen","")),
            "last_seen": _ahrefs_dt_to_unix(d.get("last_seen","")),
            "positions": to_int(d.get("positions_source_domain")),
        }
    return out

def load_ahrefs_metrics():
    """domain -> {traffic, positions, rd} from the ordered metric pulls (Ahrefs).
    Used to fill Traffic / Organic Keywords / RD's where Semrush per-domain bulk is
    not retrievable. Any domain absent here has ~0 (below the 250-row non-zero cut)."""
    out = {}
    for name in ["ahrefs_metrics_traffic.csv", "ahrefs_metrics_positions.csv"]:
        for d in read_ahrefs_csv(os.path.join(DATA, "ahrefs", name)):
            dom = canon_domain(d.get("domain",""))
            if not dom:
                continue
            rec = out.setdefault(dom, {"traffic": 0, "positions": 0, "rd": 0})
            rec["traffic"] = max(rec["traffic"], to_int(d.get("traffic_domain")))
            rec["positions"] = max(rec["positions"], to_int(d.get("positions_source_domain")))
            rec["rd"] = max(rec["rd"], to_int(d.get("dofollow_refdomains")))
    return out

def load_semrush_anchors():
    cols = ["anchor","domains_num","backlinks_num","first_seen","last_seen"]
    rows, rej = read_semrush_csv(os.path.join(DATA, "anchors_semrush.csv"), len(cols))
    out = []
    for r in rows:
        d = dict(zip(cols, r))
        out.append({"anchor": d["anchor"], "domains_num": to_int(d["domains_num"]),
                    "backlinks_num": to_int(d["backlinks_num"])})
    return out

def load_semrush_history():
    cols = ["date","backlinks_num","domains_num","score"]
    rows, rej = read_semrush_csv(os.path.join(DATA, "history_semrush.csv"), len(cols))
    return [dict(zip(cols, r)) for r in rows]

# ---------- merge ----------
def build():
    sr_rd, rej_rd = load_semrush_refdomains()
    sr_links, rej_links = load_semrush_links()
    ah_links = load_ahrefs_links()
    ah_rd = load_ahrefs_refdomains()
    ah_metrics = load_ahrefs_metrics()
    anchors = load_semrush_anchors()
    history = load_semrush_history()

    all_links = sr_links + ah_links

    # domain universe = union of Semrush refdomains + Ahrefs refdomains + any domain
    # that appears as a referring domain on a link.
    domains = {}
    def ensure(dom):
        if not dom:
            return None
        if dom not in domains:
            domains[dom] = {
                "domain": dom, "links": [], "sources": set(),
                "as": None, "sr_backlinks": None, "trust": None, "ip": "",
                "country": "", "first_seen": None, "last_seen": None,
                "ah_dr": None, "ah_dofollow_links": None, "ah_is_spam": False,
            }
        return domains[dom]

    for dom, m in sr_rd.items():
        rec = ensure(dom)
        rec["as"] = m["as"]; rec["sr_backlinks"] = m["sr_backlinks"]
        rec["trust"] = m["trust"]; rec["ip"] = m["ip"]; rec["country"] = m["country"]
        rec["first_seen"] = m["first_seen"]; rec["last_seen"] = m["last_seen"]
        rec["sources"].add("Semrush")
    for dom, m in ah_rd.items():
        rec = ensure(dom)
        rec["ah_dr"] = m["dr"]; rec["ah_dofollow_links"] = m["dofollow_links"]
        rec["ah_is_spam"] = m["is_spam"]
        if not rec["ip"] and m["ip"]:
            rec["ip"] = m["ip"]
        rec["sources"].add("Ahrefs")
        if rec["first_seen"] is None and m["first_seen"]:
            rec["first_seen"] = m["first_seen"]

    for lk in all_links:
        rec = ensure(lk["refdomain"])
        if rec is None:
            continue
        rec["links"].append(lk)
        rec["sources"].add(lk["tool"])

    # per-domain aggregates from links
    for dom, rec in domains.items():
        lks = rec["links"]
        fs = [l["first_seen"] for l in lks if l["first_seen"]]
        if fs:
            earliest = min(fs)
            if rec["first_seen"] is None or (earliest and earliest < rec["first_seen"]):
                rec["first_seen"] = earliest
        rec["dofollow_count"] = sum(1 for l in lks if not l.get("nofollow"))
        rec["nofollow_count"] = sum(1 for l in lks if l.get("nofollow"))
        rec["any_dofollow"] = rec["dofollow_count"] > 0 or (rec["ah_dofollow_links"] or 0) > 0
        # targets the domain points at
        tgts = [l["target_url"] for l in lks if l["target_url"]]
        rec["target_urls"] = sorted(set(tgts))
        m = ah_metrics.get(dom)
        rec["ah_traffic"] = m["traffic"] if m else 0
        rec["ah_positions"] = m["positions"] if m else 0
        rec["ah_rd"] = m["rd"] if m else 0
        rec["sources"] = sorted(rec["sources"])

    meta = {
        "n_domains": len(domains),
        "n_semrush_refdomains": len(sr_rd),
        "n_ahrefs_refdomains": len(ah_rd),
        "n_semrush_links": len(sr_links),
        "n_ahrefs_links": len(ah_links),
        "rejected_refdomain_rows": rej_rd,
        "rejected_link_rows": rej_links,
    }
    return {"domains": domains, "links": all_links, "anchors": anchors,
            "history": history, "meta": meta}

if __name__ == "__main__":
    data = build()
    m = data["meta"]
    print("LOAD SUMMARY")
    for k, v in m.items():
        print(f"  {k}: {v}")
    # sanity peeks
    doms = data["domains"]
    with_links = sum(1 for d in doms.values() if d["links"])
    with_as = sum(1 for d in doms.values() if d["as"] is not None)
    print(f"  domains with >=1 link detail: {with_links}")
    print(f"  domains with Semrush AS: {with_as}")
    out = os.path.join(DATA, "_merged.json")
    ser = {"meta": m,
           "domains": {k: {kk: (vv if kk != "links" else len(vv)) for kk, vv in v.items()}
                       for k, v in list(doms.items())[:3]}}
    print("  sample domain records:", json.dumps(ser["domains"], default=str)[:500])
