"""Orchestrate the erthproducts.com audit:
load -> merge Semrush+Ahrefs -> classify -> enrich metrics -> records.

Metric sources (documented honestly in the delivery):
- AS: Semrush refdomains (domain_ascore). The one metric used in a decision rule.
- Backlinks (to erth), IP, First Seen, per-link detail: Semrush (Ahrefs fills gaps/discovery).
- RD's, Traffic, Organic Keywords: footprint columns from Ahrefs batch-analysis (bulk),
  because per-domain Semrush pulls for ~2,200 domains exceed the API budget. These are
  descriptive, never decision inputs; every verdict rests on anchor/host/target/dofollow.
"""
import glob
import json
import os
import sys
import datetime as dt
import collections
from urllib.parse import urlsplit

sys.path.insert(0, "erth/scripts")
from load import load_backlinks, load_refdomains, load_csv_comma, host_of, registrable
import classify as C

CLIENT_NAME = "Erth Products"
MONEY_DOMAIN = "erthproducts.com"


def _ts(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return None


def _iso_to_ts(s):
    if not s:
        return None
    try:
        s = s.replace("Z", "+00:00")
        return int(dt.datetime.fromisoformat(s).timestamp())
    except Exception:
        try:
            return int(dt.datetime.strptime(s[:10], "%Y-%m-%d").timestamp())
        except Exception:
            return None


def _canon_link_key(url_from, url_to, anchor):
    def c(u):
        u = (u or "").lower().strip()
        u = u.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        return u
    return (c(url_from), c(url_to), (anchor or "").strip().lower())


def load_universe():
    """Return canon dict of every referring domain with source + Semrush AS + Ahrefs DR."""
    sem, _ = load_refdomains(sorted(glob.glob("erth/data/rd/rd_p*.csv")))
    canon = {}
    for r in sem:
        d = r["domain"].strip().lower()
        try:
            asc = int(r.get("domain_ascore") or 0)
        except ValueError:
            asc = 0
        canon[d] = {"domain": d, "ascore": asc,
                    "backlinks_num": int(r.get("backlinks_num") or 0),
                    "ip": r.get("ip") or "", "first_seen": _ts(r.get("first_seen")),
                    "src_semrush": True, "src_ahrefs": False, "dr": None,
                    "ah_traffic": None, "ah_kw": None}
    # Ahrefs referring domains (comma csv)
    apath = "erth/data/ahrefs/rd_ahrefs.csv"
    if os.path.exists(apath):
        for r in load_csv_comma(apath):
            d = r["domain"].strip().lower()
            dr = (r.get("domain_rating") or "").rstrip(".")
            node = canon.get(d)
            if node:
                node["src_ahrefs"] = True
                node["dr"] = dr
                if not node["ip"]:
                    node["ip"] = r.get("ip_source") or ""
            else:
                canon[d] = {"domain": d, "ascore": 0, "backlinks_num": int(r.get("links_to_target") or 0),
                            "ip": r.get("ip_source") or "", "first_seen": _iso_to_ts(r.get("first_seen")),
                            "src_semrush": False, "src_ahrefs": True, "dr": dr,
                            "ah_traffic": r.get("traffic_domain"), "ah_kw": r.get("positions_source_domain")}
    return canon


def source_label(node):
    if node["src_semrush"] and node["src_ahrefs"]:
        return "Both"
    if node["src_ahrefs"]:
        return "Ahrefs"
    return "Semrush"


def load_all_links(canon):
    """Load Semrush + Ahrefs links, normalized to one schema, deduped."""
    canon_list = sorted(canon.keys(), key=len, reverse=True)

    def assign(host):
        h = host.lower()
        if h.startswith("www."):
            h = h[4:]
        if h in canon:
            return h
        for d in canon_list:
            if h.endswith("." + d):
                return d
        return registrable(h)

    links = []
    seen = set()
    # Semrush
    bl, _ = load_backlinks(sorted(glob.glob("erth/data/fetch/bl_p*.csv")))
    for r in bl:
        src = host_of(r["source_url"])
        dom = assign(src)
        key = _canon_link_key(r["source_url"], r["target_url"], r["anchor"])
        seen.add(key)
        links.append({
            "domain": dom, "tool": "Semrush", "url_from": r["source_url"],
            "title": r["source_title"], "target": r["target_url"], "anchor": r["anchor"],
            "nofollow": C._l(r["nofollow"]) == "true", "first_seen": _ts(r["first_seen"]),
            "http": r.get("response_code") or "", "redirect": r.get("redirect_url") or "",
        })
    # Ahrefs
    apath = "erth/data/ahrefs/bl_ahrefs.csv"
    if os.path.exists(apath):
        for r in load_csv_comma(apath):
            uf, ut, an = r.get("url_from"), r.get("url_to"), r.get("anchor")
            key = _canon_link_key(uf, ut, an)
            if key in seen:
                continue  # already have it from Semrush
            seen.add(key)
            src = host_of(uf)
            dom = assign(src)
            links.append({
                "domain": dom, "tool": "Ahrefs", "url_from": uf, "title": r.get("title") or "",
                "target": ut, "anchor": an or "", "nofollow": str(r.get("is_nofollow")) in ("1", "true", "True"),
                "first_seen": _iso_to_ts(r.get("first_seen_link")), "http": r.get("http_code") or "",
                "redirect": "",
            })
    return links


def build_domain_records(canon, links):
    by = {}
    for lk in links:
        dom = lk["domain"]
        d = by.setdefault(dom, {"domain": dom, "hosts": set(), "links": [],
                                "any_dofollow": False, "first_seen": None,
                                "tools": set()})
        d["hosts"].add(host_of(lk["url_from"]))
        d["links"].append(lk)
        d["tools"].add(lk["tool"])
        if not lk["nofollow"]:
            d["any_dofollow"] = True
        if lk["first_seen"] and (d["first_seen"] is None or lk["first_seen"] < d["first_seen"]):
            d["first_seen"] = lk["first_seen"]
    # attach canon metadata
    for dom, d in by.items():
        node = canon.get(dom, {"ascore": 0, "ip": "", "src_semrush": False,
                               "src_ahrefs": True, "dr": None, "backlinks_num": len(d["links"]),
                               "first_seen": d["first_seen"], "ah_traffic": None, "ah_kw": None})
        d["ascore"] = node["ascore"]
        d["ip"] = node["ip"]
        d["node"] = node
        d["source"] = source_label(node) if dom in canon else "Ahrefs"
        if d["first_seen"] is None:
            d["first_seen"] = node.get("first_seen")
    # include canon domains that have NO links captured (rare) so counts match refdomains
    for dom, node in canon.items():
        if dom not in by:
            by[dom] = {"domain": dom, "hosts": {dom}, "links": [], "any_dofollow": False,
                       "first_seen": node.get("first_seen"), "tools": set(),
                       "ascore": node["ascore"], "ip": node["ip"], "node": node,
                       "source": source_label(node)}
    return by


def classify_all(by):
    for dom, d in by.items():
        base, ev = C.classify_domain(d)
        d["base"], d["evidence"] = base, ev
        d["status"] = C.final_status(base, d["any_dofollow"])
    return by


def run():
    canon = load_universe()
    links = load_all_links(canon)
    by = build_domain_records(canon, links)
    classify_all(by)
    return canon, links, by


if __name__ == "__main__":
    canon, links, by = run()
    print("canon domains:", len(canon), "| links:", len(links), "| domain records:", len(by))
    print("source split:", dict(collections.Counter(d["source"] for d in by.values())))
    print("status split:")
    for k, v in collections.Counter(d["status"] for d in by.values()).most_common():
        print(f"  {v:5d}  {k}")
