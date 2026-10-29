#!/usr/bin/env python3
"""
classify.py — anchor typing + per-domain status for jacocontracting.com.

Reads data/domains.json, data/links.jsonl, data/metrics/comparison.csv,
data/metrics/rank_*.csv. Writes data/domains_classified.json and
data/links_classified.jsonl (each link gets anchor_type; each domain gets status).

Statuses (exactly six): Spam (Disavow), Spam (Nofollow, No Action),
Held (Pending Partner), Held (Nofollow, No Action), Keep, Own Site.

Run: python3 -I scripts/classify.py
"""
import csv, json, os, re, sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CLIENT = "jacocontracting.com"

# ---- client vocabulary (per reconnaissance of the live anchor profile) ----
SERVICE_TERMS = [
    "roofing", "roofer", "roof repair", "roof replacement", "roof installation",
    "metal roof", "metal roofing", "shingle", "commercial roofing",
    "residential roofing", "storm damage", "roof", "gutter", "siding",
    "flat roof", "roofing contractor", "roofing material", "roof restoration",
    "water damage", "fire damage", "restoration", "contractor", "contracting",
]
GEO_TERMS = [
    "covington", "atlanta", "chattanooga", "macon", "conyers", "newnan",
    "georgia", "tennessee", " ga", "ga ", " tn", "tn ", ", ga", ", tn",
]
BRAND_TERMS = ["jaco contracting", "jaco roofing", "jaco"]

# ---- spam signals ----
SALESCOPY = [
    "backlink", "back link", "link building", "link-building", "linkbuilding",
    "dofollow", "do-follow", "do follow", "nofollow backlink", "pbn",
    "domain authority", "da 50", "pa 40", "da/pa", "da pa", "dr boost",
    "boost da", "boost dr", "higher ranking", "rank first page", "first page",
    "search traffic", "serp", "seo authority", "white hat", "tiered link",
    "guest post", "manual outreach", "citation flow", "link velocity",
    "buy backlink", "premium backlink", "link placement", "outrank your competitor",
    "high quality dofollow", "lead-gen operator", "you can attribute",
    "higher rankings", "authority backlink", "backlink expert", "link profile",
    "organic traffic", "ranking", "rankings", "dr/da", "da/dr", "improve da",
    "improve dr", "traffic surged", "seo was only possible", "backlink building",
    "trust flow", "tf", "drive qualified visitor", "saas", "web development",
    "on-page seo", "local seo", "guest posts",
]
OFFTOPIC = [
    "casino", "poker", "slot", "gambling", "betting", "bet365", "viagra",
    "cialis", "pharma", "escort", "porn", "xxx", "adult", "payday", "loan",
    "crypto", "forex", "bitcoin", "888", "judi", "togel", "slot gacor",
    "telegram", "darksidelinks", "t.me/", "sportsbook", "roulette", "baccarat",
]
SPAM_HOST = [
    "backlink", "seo", "pbn", "dapa", "rankchecker", "ranking", "directory",
    "listing", "bookmark", "submityour", "submit-your", "classified",
    "webdirectory", "web-directory", "linkdir", "dofollow", "highda", "high-da",
    "marketplace", "buy", "aged-domain", "ageddomain", "domainmarket",
    "linkbuilding", "guestpost", "guest-post", "indexation", "serp",
]
SPAM_TITLE = [
    "where to buy", "aged domain", "buy backlink", "domain list", "pbn",
    "link building service", "powerful pbn", "dofollow backlink", "backlinks to",
    "link placement", "high da backlink", "citation flow", "link velocity",
    "buy aged", "sell backlink", "backlink service", "improve citation",
]
PR_HOST = [
    "einnews", "prnewswire", "openpr", "pressreleas", "pr.com", "prlog",
    "newswire", "issuewire", "pressat", "prfree", "release-news", "24-7pressrelease",
]

def has(text, needles):
    t = (text or "").lower()
    return any(n in t for n in needles)

def is_naked_url(anchor):
    a = (anchor or "").strip().lower()
    if not a:
        return False
    core = a.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    if core == CLIENT:
        return True
    if core.startswith(CLIENT + "/"):
        return True
    # url-ish and contains client
    if (a.startswith("http") or a.startswith("www.")) and CLIENT in core:
        return True
    return False

def anchor_type(anchor):
    """Return the anchor type label used in the workbook."""
    a = (anchor or "").strip()
    al = a.lower()
    if a == "" :
        return "Empty or image"
    # off-topic spam first (unambiguous)
    if has(al, OFFTOPIC):
        return "Spam: off topic"
    # PBN / SEO sales copy
    if has(al, SALESCOPY):
        return "Spam: keyword stuffed SEO sales copy"
    # naked url / domain
    if is_naked_url(a):
        return "Naked URL"
    # exact match commercial (geo if carries client geography)
    svc = has(al, SERVICE_TERMS)
    geo = has(al, GEO_TERMS)
    if svc and geo:
        return "Exact match commercial (geo)"
    if svc:
        return "Exact match commercial"
    if geo and len(a) < 40:
        # geo-only short anchors ("Covington", "Atlanta, GA") used as local anchors
        return "Exact match commercial (geo)"
    # branded
    if al in ("jaco contracting", "jaco roofing", "jaco", "jaco contracting llc",
              "jaco contracting solutions", "jaco contracting solutions, inc.",
              "jaco contracting solutions inc") or (("jaco" in al) and not svc and len(a) < 30):
        return "Branded"
    # generic
    if al in ("visit website", "website", "click here", "read more", "learn more",
              "here", "go to company website", "↗ go to company website",
              "icon - external link visit website", "visit site", "view website",
              "this website", "homepage", "home page", "more info", "see more") \
       or al.startswith("↗") or al.startswith("icon"):
        return "Generic"
    return "Contextual or other"

def is_image_link(L):
    return L.get("link_type") == "image" or (L.get("anchor", "").strip() == "")

def deep_page(target_url):
    u = (target_url or "").lower().split("//", 1)[-1].replace("www.", "").rstrip("/")
    if not u.startswith(CLIENT):
        # external target (shouldn't happen) -> not a client deep page
        return False
    path = u[len(CLIENT):]
    return path not in ("", "/")

def load_metrics():
    comp = {}
    p = os.path.join(DATA, "metrics", "comparison.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8", newline="") as fh:
            rd = csv.reader(fh, delimiter=";")
            hdr = next(rd, None)
            for row in rd:
                if len(row) < 4:
                    continue
                d = row[0].strip().lower()
                def gi(x):
                    x = x.strip()
                    return int(x) if x.lstrip("-").isdigit() else None
                comp[d] = {"ascore": gi(row[1]), "backlinks_num": gi(row[2]), "domains_num": gi(row[3])}
    rank = {}
    mdir = os.path.join(DATA, "metrics")
    if os.path.isdir(mdir):
        for fn in sorted(os.listdir(mdir)):
            if re.match(r"rank_\d+\.csv$", fn):
                with open(os.path.join(mdir, fn), encoding="utf-8", newline="") as fh:
                    rd = csv.reader(fh)
                    hdr = next(rd, None)
                    for row in rd:
                        if len(row) < 3:
                            continue
                        d = row[0].strip().lower()
                        def gi(x):
                            x = x.strip()
                            return int(float(x)) if re.match(r"^-?\d+(\.\d+)?$", x) else None
                        rank[d] = {"organic_keywords": gi(row[1]), "organic_traffic": gi(row[2])}
    return comp, rank

def main():
    domains = json.load(open(os.path.join(DATA, "domains.json")))
    links = [json.loads(l) for l in open(os.path.join(DATA, "links.jsonl"))]
    comp, rank = load_metrics()
    print(f"metrics: comparison={len(comp)} rank={len(rank)}", file=sys.stderr)

    # per-domain link lists + anchor typing
    by_dom = {}
    for L in links:
        L["anchor_type"] = anchor_type(L["anchor"])
        by_dom.setdefault(L["refdomain"], []).append(L)

    # IP -> count for /24 network detection (class C). Use Semrush ip from domains.
    c24 = Counter()
    for d, v in domains.items():
        ip = v.get("ip", "")
        if ip and re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
            c24[".".join(ip.split(".")[:3])] += 1

    for d, v in domains.items():
        ls = by_dom.get(d, [])
        AS = (comp.get(d, {}).get("ascore"))
        if AS is None:
            AS = v.get("domain_ascore_sem_rd")
        v["AS"] = AS if AS is not None else 0
        v["RDs"] = comp.get(d, {}).get("domains_num")
        v["domain_total_backlinks"] = comp.get(d, {}).get("backlinks_num")
        v["organic_traffic"] = rank.get(d, {}).get("organic_traffic", 0) or 0
        v["organic_keywords"] = rank.get(d, {}).get("organic_keywords", 0) or 0

        types = [L["anchor_type"] for L in ls]
        has_salescopy = any(t == "Spam: keyword stuffed SEO sales copy" for t in types)
        has_offtopic = any(t == "Spam: off topic" for t in types)
        dof_salescopy = any((L["anchor_type"] == "Spam: keyword stuffed SEO sales copy" and not L["nofollow"]) for L in ls)
        dof_offtopic = any((L["anchor_type"] == "Spam: off topic" and not L["nofollow"]) for L in ls)
        exact = any(t in ("Exact match commercial", "Exact match commercial (geo)") for t in types)
        deep_commercial = any(
            deep_page(L["target_url"]) and L["anchor_type"] in
            ("Exact match commercial", "Exact match commercial (geo)", "Branded", "Contextual or other")
            for L in ls
        )
        spam_host = has(d, SPAM_HOST)
        spam_title = any(has(L.get("source_title", ""), SPAM_TITLE) for L in ls)
        pr_host = has(d, PR_HOST)
        titles_name_client = any(
            (CLIENT.split(".")[0] in (L.get("source_title", "").lower()) or "jaco" in (L.get("source_title", "").lower()))
            and not has(L.get("source_title", ""), SPAM_TITLE)
            for L in ls
        )
        any_dofollow = v["dofollow"] > 0
        all_nofollow = (v["dofollow"] == 0 and v["backlinks"] > 0)
        c24key = ".".join(v["ip"].split(".")[:3]) if v.get("ip") and re.match(r"^\d+\.\d+\.\d+\.\d+$", v["ip"]) else None
        network_host = bool(c24key and c24[c24key] >= 5)

        v["anchor_types"] = dict(Counter(types))
        v["network_c24"] = c24key if network_host else ""

        # ---- verdict (first match wins), honouring "when in doubt, hold" ----
        status = None
        reason = ""

        # 1. Own site: none for jaco (no owned/redirect domains)

        # 2 & 3. Exact-match or deep commercial -> Held (possibly commissioned)
        if exact or deep_commercial:
            if all_nofollow:
                status = "Held (Nofollow, No Action)"
            else:
                status = "Held (Pending Partner)"
            if exact and has_salescopy:
                reason = "exact-match commercial anchor + SEO sales copy on same domain (review-level hold)"
            elif exact:
                reason = "exact-match commercial anchor (may be commissioned)"
            else:
                reason = "link to a deep money page with a commercial/branded anchor (may be commissioned)"
        # 4. Press release syndication
        elif pr_host:
            status = "Held (Nofollow, No Action)" if all_nofollow else "Held (Pending Partner)"
            reason = "press-release syndication host (may be commissioned)"
        # 5. Genuine high-AS site with no spam signal -> Keep
        elif (v["AS"] or 0) >= 20 and not (has_salescopy or has_offtopic or spam_host or spam_title):
            status = "Keep"
            reason = f"authority score {v['AS']} with no spam signal (genuine site)"
        # 6. Linking title names client without sales copy -> Keep (citation/listing)
        elif titles_name_client and not (has_salescopy or has_offtopic or spam_host or spam_title):
            status = "Keep"
            reason = "linking page names the client without SEO sales copy (business listing / editorial mention)"
        # 7. Off-topic spam
        elif has_offtopic:
            status = "Spam (Disavow)" if dof_offtopic else "Spam (Nofollow, No Action)"
            reason = "off-topic (gambling/pharma/adult/telegram) spam anchor"
        # 8. PBN sales copy
        elif has_salescopy:
            status = "Spam (Disavow)" if dof_salescopy else "Spam (Nofollow, No Action)"
            reason = "keyword-stuffed SEO/PBN sales-copy anchor"
        # 9. Spam host name
        elif spam_host:
            status = "Spam (Disavow)" if any_dofollow else "Spam (Nofollow, No Action)"
            reason = "link-network / directory / backlink-marketplace host name"
        # 10. Spam page title / url
        elif spam_title:
            status = "Spam (Disavow)" if any_dofollow else "Spam (Nofollow, No Action)"
            reason = "spam page title (backlink marketplace / domain list / PBN template)"
        # 11. network host with other evidence only (never on IP alone) -> skip to keep
        else:
            status = "Keep"
            reason = "no spam evidence in anchor, title, host, or target"
            if network_host:
                reason += f" (note: shares /24 {c24key} with other referring domains, but held to Keep absent other evidence)"

        v["status"] = status
        v["reason"] = reason
        v["in_disavow"] = (status == "Spam (Disavow)")

    # Drop empty roots: a root domain carrying no link of its own (its links sit on
    # a subdomain kept as a separate referring domain) is not a second referring site.
    dropped = [d for d, v in domains.items() if v["backlinks"] == 0]
    for d in dropped:
        del domains[d]
    if dropped:
        print(f"dropped {len(dropped)} empty-root domains: {dropped}", file=sys.stderr)

    # write classified
    with open(os.path.join(DATA, "domains_classified.json"), "w", encoding="utf-8") as fh:
        json.dump(domains, fh, ensure_ascii=False)
    with open(os.path.join(DATA, "links_classified.jsonl"), "w", encoding="utf-8") as fh:
        for L in links:
            fh.write(json.dumps(L, ensure_ascii=False) + "\n")
        # attach status to each link via domain
    # report
    sc = Counter(v["status"] for v in domains.values())
    print("=== STATUS DISTRIBUTION (domains) ===")
    tot = 0
    for s in ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
              "Spam (Nofollow, No Action)", "Keep", "Own Site"]:
        print(f"  {s:32s} {sc.get(s,0):5d}")
        tot += sc.get(s, 0)
    print(f"  {'TOTAL':32s} {tot:5d}")
    # backlinks per status
    bl = Counter()
    for v in domains.values():
        bl[v["status"]] += v["backlinks"]
    print("=== BACKLINKS per status ===")
    for s in ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
              "Spam (Nofollow, No Action)", "Keep", "Own Site"]:
        print(f"  {s:32s} {bl.get(s,0):6d}")

if __name__ == "__main__":
    main()
