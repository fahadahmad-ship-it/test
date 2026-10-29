#!/usr/bin/env python3
"""
load.py — read + merge Semrush and Ahrefs backlink data for jacocontracting.com.

Semrush is the priority source. Ahrefs contributes extra links (new discovery),
live-page HTTP codes, and first/last seen recovery. Never a metric.

Outputs (written to data/):
  links.jsonl    — one JSON object per unique link (merged, deduped)
  domains.json   — per referring-domain aggregates (no metrics yet; classify.py adds them)

Run:  python3 -I scripts/load.py
"""
import csv, json, html, os, sys
from urllib.parse import urlsplit
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CLIENT_HOST = "jacocontracting.com"

# multi-label public suffixes we might hit (fallback only)
MULTI_TLD = {
    "co.in","co.uk","org.uk","com.au","co.nz","co.za","com.br","co.jp","com.mx",
    "co.id","com.sg","co.il","com.tr","net.in","org.in","co.kr","com.co","gov.uk",
    "ac.uk","com.pk","com.ua","co.th","com.ph","com.vn","com.my","co.ke",
}

def load_universe():
    """Known referring-domain roots from both refdomain exports."""
    uni = set()
    # Semrush refdomains (semicolon)
    for fn in sorted(os.listdir(os.path.join(DATA, "rd"))):
        if not fn.endswith(".csv"):
            continue
        with open(os.path.join(DATA, "rd", fn), encoding="utf-8", newline="") as fh:
            rd = csv.reader(fh, delimiter=";", quotechar='"')
            next(rd, None)
            for row in rd:
                if row and row[0].strip():
                    uni.add(row[0].strip().lower())
    # Ahrefs refdomains (tab)
    p = os.path.join(DATA, "ahrefs_export", "ahrefs_refdomains.utf8.csv")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh, delimiter="\t", quotechar='"')
        hdr = next(rd)
        di = hdr.index("Domain")
        for row in rd:
            if row and row[di].strip():
                uni.add(row[di].strip().lower())
    return uni

def host_of(u):
    if not u:
        return ""
    u = u.strip()
    if "//" not in u:
        u = "//" + u
    h = urlsplit(u).netloc.lower()
    if "@" in h:
        h = h.split("@")[-1]
    if ":" in h:
        h = h.split(":")[0]
    if h.startswith("www."):
        h = h[4:]
    return h

def etld1(host):
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    last2 = ".".join(parts[-2:])
    last3 = ".".join(parts[-3:])
    if last2 in MULTI_TLD and len(parts) >= 3:
        return last3
    return last2

def build_root_resolver(universe):
    # sort universe by length desc for longest-suffix match
    uni_sorted = sorted(universe, key=len, reverse=True)
    uni_set = set(universe)
    cache = {}
    def resolve(host):
        if not host:
            return ""
        if host in cache:
            return cache[host]
        r = None
        if host in uni_set:
            r = host
        else:
            for d in uni_sorted:
                if host == d or host.endswith("." + d):
                    r = d
                    break
        if r is None:
            r = etld1(host)
        cache[host] = r
        return r
    return resolve

def canon_url(u):
    if not u:
        return ""
    u = u.strip()
    if "//" in u:
        u = u.split("//", 1)[1]
    u = u.lower()
    if u.startswith("www."):
        u = u[4:]
    u = u.rstrip("/")
    return u

def canon_anchor(a):
    return " ".join((a or "").split()).lower()

def to_unix(dtstr):
    """Ahrefs 'YYYY-MM-DD HH:MM:SS' -> unix int, or None."""
    import datetime
    dtstr = (dtstr or "").strip()
    if not dtstr:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return int(datetime.datetime.strptime(dtstr, fmt).replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            continue
    return None

def main():
    universe = load_universe()
    resolve = build_root_resolver(universe)
    print(f"universe roots: {len(universe)}", file=sys.stderr)

    # Semrush refdomains -> ip, first_seen, in_semrush
    sem_rd = {}
    for fn in sorted(os.listdir(os.path.join(DATA, "rd"))):
        if not fn.endswith(".csv"):
            continue
        with open(os.path.join(DATA, "rd", fn), encoding="utf-8", newline="") as fh:
            rd = csv.reader(fh, delimiter=";", quotechar='"')
            hdr = next(rd)
            # domain;backlinks_num;domain_ascore;domain_trust_score;ip;country;first_seen;last_seen
            for row in rd:
                if len(row) < 8:
                    continue
                d = row[0].strip().lower()
                sem_rd[d] = {
                    "ip": row[4].strip(),
                    "domain_ascore": int(row[2]) if row[2].strip().isdigit() else None,
                    "first_seen": int(row[6]) if row[6].strip().isdigit() else None,
                    "links_to_target": int(row[1]) if row[1].strip().isdigit() else None,
                }

    # Ahrefs refdomains -> first_seen, is_spam flag (as corroboration only)
    ah_rd = {}
    p = os.path.join(DATA, "ahrefs_export", "ahrefs_refdomains.utf8.csv")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh, delimiter="\t", quotechar='"')
        hdr = next(rd)
        ix = {h.strip(): i for i, h in enumerate(hdr)}
        for row in rd:
            if not row:
                continue
            d = row[ix["Domain"]].strip().lower()
            ah_rd[d] = {
                "is_spam": row[ix["Is spam"]].strip().lower() == "true",
                "first_seen": to_unix(row[ix["First seen"]]),
            }

    links = {}  # key -> link dict

    # ---- Semrush backlinks ----
    sem_rows = 0
    for fn in sorted(os.listdir(os.path.join(DATA, "fetch"))):
        if not fn.endswith(".csv"):
            continue
        with open(os.path.join(DATA, "fetch", fn), encoding="utf-8", newline="") as fh:
            rd = csv.reader(fh, delimiter=";", quotechar='"')
            hdr = next(rd)
            for row in rd:
                if len(row) != 10:
                    continue
                source_url, source_title, target_url, anchor, nofollow, first_seen, last_seen, resp, redirect_url, pasc = row
                source_title = html.unescape(source_title)
                anchor = html.unescape(anchor)
                src_host = host_of(source_url)
                refdom = resolve(src_host)
                key = (canon_url(source_url), canon_url(target_url), canon_anchor(anchor))
                nf = (nofollow.strip().lower() == "true")
                prop = host_of(redirect_url) if redirect_url.strip() else host_of(target_url)
                rc = int(resp) if resp.strip().lstrip("-").isdigit() else None
                links[key] = {
                    "refdomain": refdom,
                    "source_url": source_url,
                    "source_title": source_title,
                    "target_url": target_url,
                    "anchor": anchor,
                    "nofollow": nf,
                    "link_type": "image" if False else "text",
                    "first_seen": int(first_seen) if first_seen.strip().isdigit() else None,
                    "last_seen": int(last_seen) if last_seen.strip().isdigit() else None,
                    "http_code": rc,
                    "redirect_url": redirect_url.strip(),
                    "target_property": prop or CLIENT_HOST,
                    "sources": {"Semrush"},
                }
                sem_rows += 1

    # ---- Ahrefs backlinks ----
    ah_rows = 0
    ah_only = 0
    p = os.path.join(DATA, "ahrefs_export", "ahrefs_backlinks.utf8.csv")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rd = csv.reader(fh, delimiter="\t", quotechar='"')
        hdr = next(rd)
        ix = {h.strip(): i for i, h in enumerate(hdr)}
        for row in rd:
            if not row or len(row) < len(hdr):
                continue
            source_url = row[ix["Referring page URL"]]
            target_url = row[ix["Target URL"]]
            anchor = row[ix["Anchor"]]
            title = row[ix["Referring page title"]]
            nf = row[ix["Nofollow"]].strip().lower() == "true"
            ltype = row[ix["Type"]].strip() or "text"
            httpc = row[ix["Referring page HTTP code"]].strip()
            httpc = int(httpc) if httpc.lstrip("-").isdigit() else None
            fs = to_unix(row[ix["First seen"]])
            ls = to_unix(row[ix["Last seen"]])
            lost = row[ix["Lost status"]].strip()
            src_host = host_of(source_url)
            refdom = resolve(src_host)
            key = (canon_url(source_url), canon_url(target_url), canon_anchor(anchor))
            ah_rows += 1
            if key in links:
                L = links[key]
                L["sources"].add("Ahrefs")
                if L.get("http_code") is None and httpc is not None:
                    L["http_code"] = httpc
                if L.get("first_seen") is None and fs is not None:
                    L["first_seen"] = fs
                if L.get("last_seen") is None and ls is not None:
                    L["last_seen"] = ls
                if not L.get("source_title") and title:
                    L["source_title"] = title
                L["ahrefs_lost"] = lost
            else:
                ah_only += 1
                links[key] = {
                    "refdomain": refdom,
                    "source_url": source_url,
                    "source_title": title,
                    "target_url": target_url,
                    "anchor": anchor,
                    "nofollow": nf,
                    "link_type": ltype,
                    "first_seen": fs,
                    "last_seen": ls,
                    "http_code": httpc,
                    "redirect_url": "",
                    "target_property": host_of(target_url) or CLIENT_HOST,
                    "sources": {"Ahrefs"},
                    "ahrefs_lost": lost,
                }

    # ---- write links.jsonl ----
    outp = os.path.join(DATA, "links.jsonl")
    with open(outp, "w", encoding="utf-8") as fh:
        for L in links.values():
            L = dict(L)
            L["sources"] = sorted(L["sources"])
            fh.write(json.dumps(L, ensure_ascii=False) + "\n")

    # ---- per-domain aggregates ----
    domains = {}
    by_dom = defaultdict(list)
    for L in links.values():
        by_dom[L["refdomain"]].append(L)

    # ensure every universe domain has an entry even if (rare) no link mapped to it
    for d in universe:
        by_dom.setdefault(d, [])

    for d, ls in by_dom.items():
        n = len(ls)
        dof = sum(1 for L in ls if not L["nofollow"])
        nof = sum(1 for L in ls if L["nofollow"])
        # first seen = min across links, fallback to refdomain export
        fs_candidates = [L["first_seen"] for L in ls if L["first_seen"]]
        fs = min(fs_candidates) if fs_candidates else None
        if fs is None:
            fs = (sem_rd.get(d, {}).get("first_seen")
                  or ah_rd.get(d, {}).get("first_seen"))
        # top anchor
        anc = Counter(L["anchor"] for L in ls if L["anchor"] is not None)
        top_anchor = anc.most_common(1)[0][0] if anc else ""
        # example linking page: prefer live (http 200) + dofollow
        def score(L):
            live = 1 if (L.get("http_code") == 200) else 0
            dofo = 1 if not L["nofollow"] else 0
            return (live, dofo)
        example = max(ls, key=score) if ls else None
        in_sem = d in sem_rd
        in_ah = d in ah_rd
        src = "Semrush" if in_sem else ("Ahrefs" if in_ah else "Semrush")
        props = Counter(L["target_property"] for L in ls) if ls else Counter()
        links_point_to = props.most_common(1)[0][0] if props else CLIENT_HOST
        domains[d] = {
            "domain": d,
            "backlinks": n,                       # links to target (dofollow+nofollow)
            "dofollow": dof,
            "nofollow": nof,
            "first_seen": fs,
            "top_anchor": top_anchor,
            "example_url": example["source_url"] if example else "",
            "example_title": example["source_title"] if example else "",
            "links_point_to": links_point_to,
            "source": src,
            "ip": sem_rd.get(d, {}).get("ip", "") if in_sem else "",
            "in_semrush": in_sem,
            "in_ahrefs": in_ah,
            "domain_ascore_sem_rd": sem_rd.get(d, {}).get("domain_ascore"),
            "ahrefs_is_spam": ah_rd.get(d, {}).get("is_spam", False),
            "all_nofollow": (dof == 0 and n > 0),
        }

    with open(os.path.join(DATA, "domains.json"), "w", encoding="utf-8") as fh:
        json.dump(domains, fh, ensure_ascii=False)

    print(f"Semrush link rows read: {sem_rows}")
    print(f"Ahrefs link rows read:  {ah_rows}  (ahrefs-only new: {ah_only})")
    print(f"unique merged links:    {len(links)}")
    print(f"referring domains:      {len(domains)}")
    nonempty = sum(1 for d in domains.values() if d['backlinks'] > 0)
    print(f"domains with >=1 mapped link: {nonempty}")
    print(f"domains with zero mapped links: {len(domains)-nonempty}")

if __name__ == "__main__":
    main()
