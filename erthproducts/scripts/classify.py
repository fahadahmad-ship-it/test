"""Classify every referring domain into exactly one of six statuses.
Usage: python3 -I classify.py <merged.json> <out_classified.json>
Verdict order per playbook section 6; six statuses, no Review buckets.
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

def anchor_type(anchor):
    a = (anchor or "").strip()
    al = a.lower()
    if not a:
        return "Empty or image"
    if C.PBN_ANCHOR_RE.search(al):
        return "Spam: keyword stuffed SEO sales copy"
    if C.OFFTOPIC_RE.search(al):
        return "Spam: off topic"
    # naked url / bare domain
    if (al.startswith("http://") or al.startswith("https://") or al.startswith("www.")
            or (("." in al) and (" " not in al) and len(al) < 60
                and any(al.endswith(t) or (t + "/") in al for t in (".com", ".net", ".org", ".info", ".co", ".io", ".us")))):
        return "Naked URL"
    has_prod = any(t in al for t in C.PRODUCT_TERMS)
    has_geo = any(g.strip() in al for g in C.GEO_TOKENS)
    if has_prod and has_geo:
        return "Exact match commercial (geo)"
    if has_prod:
        return "Exact match commercial"
    if any(t in al for t in C.BRAND_TOKENS):
        return "Branded"
    if al in C.GENERIC_ANCHORS or (len(al) <= 20 and any(g in al for g in ("website", "click", "here", "visit", "more", "link"))):
        return "Generic"
    return "Contextual or other"


def classify_domain(rec):
    links = rec["links"]
    reg = rec["domain"]
    hosts = rec.get("hosts", [reg])
    as_ = rec.get("as")
    dofollow = rec["dofollow"]

    # per-link anchor types
    for l in links:
        l["anchor_type"] = anchor_type(l["anchor"])

    def df(pred):   # any dofollow link matching
        return any(pred(l) for l in links if not l["nofollow"])
    def any_l(pred):
        return any(pred(l) for l in links)

    numeric_host = C.is_numeric_host(reg)
    spam_tld = C.tld(reg) in C.SPAM_TLDS
    network_host = bool(rec.get("network_host"))

    owned = reg in C.OWNED_DOMAINS or reg == C.MONEY_DOMAIN
    has_pbn_df   = df(lambda l: l["anchor_type"] == "Spam: keyword stuffed SEO sales copy") \
                   or df(lambda l: bool(C.PBN_ANCHOR_RE.search((l["source_title"] or "").lower())))
    has_pbn_any  = any_l(lambda l: l["anchor_type"] == "Spam: keyword stuffed SEO sales copy")
    has_off_df   = df(lambda l: l["anchor_type"] == "Spam: off topic") \
                   or bool(C.OFFTOPIC_RE.search(reg))
    has_exact    = any_l(lambda l: l["anchor_type"] in ("Exact match commercial", "Exact match commercial (geo)"))
    has_exact_df = df(lambda l: l["anchor_type"] in ("Exact match commercial", "Exact match commercial (geo)"))
    has_deep_df  = df(lambda l: (not C.is_home(l["target_url"])) and any(m in C.path_of(l["target_url"]).lower() for m in C.MONEY_PAGES))
    is_press     = any(C.PRESS_HOST_RE.search(h) for h in hosts)
    spam_host    = any(C.SPAM_HOST_RE.search(h) for h in hosts)
    spam_title   = any_l(lambda l: bool(C.SPAM_TITLE_RE.search((l["source_title"] or "").lower())
                                        or C.SPAM_URL_RE.search((l["source_url"] or "").lower())))
    clean_cit    = any_l(lambda l: (l["anchor_type"] in ("Branded", "Contextual or other", "Generic"))
                         and any(b in (l["source_title"] or "").lower() for b in C.BRAND_TOKENS)
                         and not C.PBN_ANCHOR_RE.search((l["source_title"] or "").lower()))

    spam_evidence = has_pbn_any or has_off_df or spam_host or spam_title
    # Note: clean_citation is deliberately NOT a genuine signal here — spam pages on
    # throwaway infra routinely put the brand in their <title> to look like citations.
    genuine_signal = has_exact or (as_ is not None and as_ >= 20)
    low_auth = (as_ is None) or (as_ < 20)
    naked_type = {"Naked URL", "Empty or image", "Generic", "Contextual or other"}
    top_naked = all((l.get("anchor_type") in naked_type) for l in links) if links else False
    # Throwaway domain on a known link-network host (numeric label, non-CDN /24 cluster,
    # or throwaway TLD) with no genuine signal and only naked/empty anchors -> spam.
    # Composite evidence, never TLD alone.
    throwaway_spam = ((numeric_host or network_host or spam_tld)
                      and not genuine_signal and low_auth and top_naked)

    # ---- verdict (first match) ----
    if owned:
        base = "Own Site"
    elif has_exact and has_pbn_df and has_deep_df:
        base = "Held"           # review-level: commissioned signal + manipulation
    elif has_exact_df or has_deep_df or is_press:
        base = "Held"
    elif spam_evidence:
        base = "Spam"
    elif throwaway_spam:
        base = "Spam"
    elif clean_cit:
        base = "Keep"
    elif (as_ is not None and as_ >= 20):
        base = "Keep"
    else:
        base = "Keep"

    if base == "Spam":
        status = "Spam (Disavow)" if dofollow > 0 else "Spam (Nofollow, No Action)"
    elif base == "Held":
        status = "Held (Pending Partner)" if dofollow > 0 else "Held (Nofollow, No Action)"
    else:
        status = base

    # top anchor (by frequency, prefer dofollow)
    cnt = collections.Counter((l["anchor"] or "").strip() for l in links if (l["anchor"] or "").strip())
    top_anchor = cnt.most_common(1)[0][0] if cnt else ""
    top_type = anchor_type(top_anchor) if top_anchor else ("Empty or image" if links else "")

    # example backlink: prefer a live (200) dofollow link; else any live; else any
    def score(l):
        live = l["response_code"] in ("", "200") or l["response_code"].startswith("2")
        return (1 if live else 0, 1 if not l["nofollow"] else 0, 1 if not C.is_home(l["target_url"]) else 0)
    example = max(links, key=score) if links else None

    # geo / site-type for exact-match held (for Exact Match Anchors tab)
    market = "Non-geo"
    if any(l["anchor_type"] == "Exact match commercial (geo)" for l in links):
        market = "Georgia"
    if spam_host and ("directory" in reg or "listing" in reg or "bookmark" in reg):
        site_type = "Low quality web directory"
    elif is_press:
        site_type = "Guest article or content farm"
    elif "bookmark" in reg:
        site_type = "Social bookmarking site"
    else:
        site_type = "Low quality web directory"

    rec.update({
        "status": status,
        "top_anchor": top_anchor,
        "top_anchor_type": top_type,
        "example": example,
        "evidence": {
            "pbn": has_pbn_any, "offtopic": has_off_df, "exact": has_exact,
            "deep": has_deep_df, "press": is_press, "spam_host": spam_host,
            "spam_title": spam_title, "clean_citation": clean_cit,
            "numeric_host": numeric_host, "spam_tld": spam_tld,
            "network_host": network_host, "throwaway": throwaway_spam,
        },
        "market": market, "site_type": site_type,
    })
    return rec


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    # ---- /24 link-network pre-pass (exclude CDN/shared infra) ----
    cl = collections.Counter()
    for rec in data:
        ip = rec.get("ip", "")
        if ip and not C.is_cdn_ip(ip):
            s = C.slash24(ip)
            if s:
                cl[s] += 1
    net24 = {s for s, n in cl.items() if n >= 5}
    for rec in data:
        ip = rec.get("ip", "")
        rec["network_host"] = bool(ip and not C.is_cdn_ip(ip) and C.slash24(ip) in net24)
    print(f"non-CDN /24 link-network ranges (>=5 domains): {len(net24)}; "
          f"domains on them: {sum(1 for r in data if r['network_host'])}")
    for rec in data:
        classify_domain(rec)
    # parent/child redundancy: a Spam(Disavow) child whose registrable parent is also
    # Spam(Disavow) is covered by `domain:` -> mark redundant. (reg-domain keyed, so
    # subdomains already rolled up; this guards any stray host rows.)
    json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
    cnt = collections.Counter(r["status"] for r in data)
    print("=== STATUS COUNTS ===")
    for k, v in cnt.most_common():
        print(f"  {v:5d}  {k}")
    print("  total:", len(data))
    indis = sum(1 for r in data if r["status"] == "Spam (Disavow)")
    print("  disavow (dofollow spam):", indis)
    # sanity: any Keep/Held with dofollow off-topic?
    bad = [r["domain"] for r in data if r["status"].startswith(("Keep", "Held"))
           and r["evidence"]["offtopic"]]
    print("  WARN Keep/Held w/ dofollow off-topic:", len(bad), bad[:5])


if __name__ == "__main__":
    main()
