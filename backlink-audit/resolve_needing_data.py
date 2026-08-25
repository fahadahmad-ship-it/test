#!/usr/bin/env python3
"""Resolve the 334 domains that had no link-level evidence.

Input: DOMAINSNEEDINGDATA.md listed 334 referring domains / 3,522 backlinks
whose verdicts rested only on domain authority, backlink count, IP and domain
name — none of their links appeared in the 50,000-row CSV export, so there
were no anchors, no target URLs and no redirect data behind any of them.

Every one now has rows in semrush_backlinks_filtered.csv, pulled per-domain
through the Semrush connector. This script reads the anchors, targets and
redirect chains and assigns each domain a network classification and verdict.

Classification is signature-based, not score-based: each rule fires on an
observable footprint (an anchor that advertises link-selling, a bare-domain
anchor on a high-outlink stats page, an affiliate ID in the target URL),
so every verdict traces to a quotable row.

Usage:
    python3 resolve_needing_data.py <outdir>
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import parse_qs, unquote, urlsplit

from audit import BRAND_OWNED, _registrable, host_of

# --- signature vocabularies -------------------------------------------------

# Anchors that advertise a link-selling or hacked-site service. The anchor is
# the product listing: these pages exist to sell links, and the link to the
# client is the sample being sold. Not ambiguous.
VENDOR_ANCHOR = re.compile(
    r"t\.me/|telegram|buy backlinks|dofollow (article )?links|premium pbn|"
    r"link building|links_dealer|quarterlinks|darksidelinks|salesoven|"
    r"access to hacked sites|effective seo links", re.I)

# Bare-domain anchors ("nutropic.com") on pages carrying thousands of outbound
# links: a domain-stats/URL-shortener scraper reproducing a directory, not a
# citation. The anchor being exactly a hostname is the tell.
BARE_DOMAIN_ANCHOR = re.compile(r"^(https?://)?(www\.)?[a-z0-9-]+\.[a-z.]{2,12}/?$", re.I)

# Cloned-publisher fingerprints. Each is a verbatim commerce string lifted from
# one real UK publisher article and replicated across many throwaway domains.
# Filler anchors that carry no editorial meaning. Dominant filler plus follow
# links across many domains on one affiliate account is blog-platform
# link-building, not citation.
FILLER_ANCHOR = re.compile(
    r"^(here|click here|more info|check here|check it out|website|read more|"
    r"this site|link|info|visit|visit website|learn more|see more|source|"
    r"go here|view|details)$", re.I)

# Generic site furniture. A path like /search is not a bespoke sponsor page,
# so it must never satisfy the partner-landing-page rule.
GENERIC_PATHS = {
    "search", "login", "signin", "signup", "cart", "checkout", "account",
    "contact", "about", "blog", "shop", "store", "home", "index", "sitemap",
    "terms", "privacy", "faq", "support", "help", "news", "products",
}

# Hosts where a page listing thousands of domains is the site's legitimate
# purpose — open-source data sets, documentation, reference works. The
# bare-domain/high-outlink signature fires on them correctly but the spam
# reading does not follow, the same trap as blogspot.com and the Shopify
# C-block in the original audit. These are held for review, never disavowed
# on the scraper signature alone.
REPUTABLE_LISTING_HOSTS = (
    ".github.io", ".gitlab.io", ".readthedocs.io", ".sourceforge.net",
    "wikipedia.org", "wikimedia.org", "archive.org", ".edu", ".gov",
)

# Zero-width / word-joiner characters that podcast feeds append to link URLs.
# onlyboosts.social carries six links to the same sponsor page across five
# "distinct" paths that differ only by trailing U+2060, so the path has to be
# normalised before any same-path rule is applied.
INVISIBLE = "\u2060\u200b\u200c\u200d\ufeff"


def norm_path(target):
    return unquote(urlsplit(target).path).strip(INVISIBLE).rstrip("/")


CLONE_FINGERPRINTS = {
    "goodfood": ("Taster box", "Performance Lab (from £19)", "£19"),
    "nailsupps": ("£132 at performancelab.com", "£44 at performancelab.com",
                  "UK Approved(Esquire"),
}


def affiliate_ids(target):
    """Affiliate ACCOUNT ids carried in the target URL query string.

    Only a_aid (and the bare `aff` variant) identify an account. a_bid is a
    banner/creative id shared programme-wide — a2ad38c1 alone appears on 66 of
    these domains — so counting it as an account would merge unrelated
    affiliates into one phantom network. It is captured separately as evidence
    of programme membership, not of common ownership.
    """
    q = parse_qs(urlsplit(target).query)
    return {v for k in ("a_aid", "aff") for v in q.get(k, [])}


def banner_ids(target):
    return set(parse_qs(urlsplit(target).query).get("a_bid", []))


def anchor_class(anchor, target):
    a = (anchor or "").strip()
    if not a:
        return "empty"
    if VENDOR_ANCHOR.search(a):
        return "vendor-advert"
    if BARE_DOMAIN_ANCHOR.match(a):
        return "bare-domain"
    if a.lower().startswith("http"):
        return "raw-url"
    if re.search(r"performance ?lab|nutrigenesis|mind lab|testo ?lab|pre ?lab|"
                 r"nutropic|burn ?lab", a, re.I):
        return "branded"
    if re.search(r"\b(buy|satın|price|deal|cheap|discount|order|shop|visit|"
                 r"click here|check|see (current )?pric)", a, re.I):
        return "commercial-cta"
    return "descriptive"


def target_class(target):
    p = urlsplit(target).path.strip("/")
    if not p:
        return "homepage"
    if p.startswith("products/") or p.startswith("collections/"):
        return "product"
    if p.startswith("blogs/"):
        return "article"
    return "other"


def main(outdir):
    stated = json.load(open("stated_counts.json"))
    rows = list(csv.DictReader(open("semrush_backlinks_filtered.csv"),
                              delimiter=";"))
    by = defaultdict(list)
    for r in rows:
        by[_registrable(host_of(r["source_url"]))].append(r)

    # Pass 1: gather per-domain evidence.
    ev = {}
    for d in stated:
        rs = by.get(d) or by.get(_registrable(d)) or []
        anchors = Counter((r["anchor"] or "").strip() for r in rs)
        aclass = Counter(anchor_class(r["anchor"], r["target_url"]) for r in rs)
        tclass = Counter(target_class(r["target_url"]) for r in rs)
        hops = Counter(_registrable(host_of(r["redirect_url"]))
                       for r in rs if r["redirect_url"].strip())
        codes = Counter(r["response_code"] for r in rs)
        aff, banners = set(), set()
        for r in rs:
            aff |= affiliate_ids(r["target_url"])
            banners |= banner_ids(r["target_url"])
        ext = sorted(int(r["external_num"] or 0) for r in rs)
        nofollow = sum(1 for r in rs if r["nofollow"] == "true")
        # A bespoke non-product path used by (almost) every link is a partner
        # landing page — the audit already rescued whatismoneypodcast.com on
        # exactly this basis, so the rule has to apply to its peers too.
        paths = Counter(norm_path(r["target_url"]) for r in rs)
        sponsor = None
        if rs:
            top_path, top_n = paths.most_common(1)[0]
            seg = top_path.strip("/")
            if (top_n / len(rs) >= 0.9 and len(rs) >= 3 and seg
                    and "/" not in seg
                    and seg.lower() not in GENERIC_PATHS
                    and not seg.startswith(("products", "collections", "blogs",
                                            "pages"))):
                sponsor = top_path
        filler = sum(1 for r in rs if FILLER_ANCHOR.match((r["anchor"] or "").strip()))
        clone = None
        for name, marks in CLONE_FINGERPRINTS.items():
            if any(m in (r["anchor"] or "") for r in rs for m in marks):
                clone = name
        ev[d] = dict(rows=len(rs), anchors=anchors, aclass=aclass,
                     tclass=tclass, hops=hops, codes=codes, aff=aff,
                     ext_median=ext[len(ext) // 2] if ext else 0,
                     nofollow=nofollow, follow=len(rs) - nofollow, clone=clone,
                     banners=banners, sponsor=sponsor, filler=filler,
                     stated=stated[d][0], authority=stated[d][1],
                     old_flag=stated[d][2])

    # Pass 2: cross-domain — a clone or affiliate ID shared across many
    # domains is one operator, which is what makes it a network.
    clone_members = defaultdict(list)
    aff_members = defaultdict(list)
    for d, e in ev.items():
        if e["clone"]:
            clone_members[e["clone"]].append(d)
        for a in e["aff"]:
            aff_members[a].append(d)

    out, counts = [], Counter()
    for d, e in sorted(ev.items()):
        n = e["rows"]
        vendor = e["aclass"].get("vendor-advert", 0)
        bare = e["aclass"].get("bare-domain", 0)
        verdict = reason = None

        if vendor:
            verdict = "DISAVOW"
            reason = ("Anchor text advertises a link-selling or hacked-site "
                      f"service ({vendor}/{n} links). The page exists to sell "
                      "links; this one is the sample.")
        elif bare and e["ext_median"] >= 1000:
            if d.endswith(REPUTABLE_LISTING_HOSTS):
                verdict = "REVIEW_MANUALLY"
                reason = (f"Bare-domain anchors on pages carrying "
                          f"~{e['ext_median']} outbound links, but the host is "
                          "an open-source/reference platform where publishing a "
                          "large domain list is the point. Machine listing, not "
                          "a link scheme — no equity intent either way.")
            else:
                verdict = "DISAVOW"
                reason = (f"Bare-domain anchors on pages carrying "
                          f"~{e['ext_median']} outbound links — a domain-stats/"
                          "shortener scraper reproducing a directory, not a "
                          "citation.")
        elif e["clone"]:
            peers = len(clone_members[e["clone"]])
            verdict = "DISAVOW"
            reason = (f"Verbatim clone of a UK publisher commerce table, "
                      f"replicated across {peers} throwaway domains "
                      f"({e['clone']} fingerprint).")
        elif e["sponsor"]:
            verdict = "KEEP_AFFILIATE_RETAIN"
            reason = (f"All {n} links point at {e['sponsor']} — a bespoke "
                      "sponsor/partner landing page, not a commercial product "
                      "path. Same footprint the audit already accepted for "
                      "whatismoneypodcast.com.")
        elif e["aff"] and max(len(aff_members[a]) for a in e["aff"]) >= 10 \
                and e["filler"] >= n / 2 and e["follow"] > e["nofollow"]:
            acct = max(e["aff"], key=lambda a: len(aff_members[a]))
            verdict = "REVIEW_MANUALLY"
            reason = (f"Affiliate account {acct} operates "
                      f"{len(aff_members[acct])} of these domains, and this one "
                      f"is {e['filler']}/{n} filler anchors on follow links "
                      "from a free blog platform. An affiliate ID says who "
                      "built the link, not that it is safe to keep: follow "
                      "affiliate links are a link-scheme exposure whoever "
                      "placed them. This is a programme-compliance decision "
                      "(require nofollow) rather than a spam call.")
        elif e["aff"] or e["banners"]:
            verdict = "KEEP_AFFILIATE_RETAIN"
            if e["aff"]:
                shared = max(len(aff_members[a]) for a in e["aff"])
                reason = (f"Target URLs carry affiliate account "
                          f"{'/'.join(sorted(e['aff']))} — a tracked partner in "
                          f"the client's own programme"
                          + (f"; that account operates {shared} of these domains."
                             if shared > 1 else "."))
            else:
                reason = ("Target URLs carry a programme banner ID "
                          f"({'/'.join(sorted(e['banners']))}) but no account "
                          "ID — programme traffic, account unattributed.")
        elif any(h in BRAND_OWNED for h in e["hops"]):
            verdict = "KEEP_AFFILIATE_RETAIN"
            reason = ("Links route through the client's own brand estate "
                      f"({', '.join(h for h in e['hops'] if h in BRAND_OWNED)}).")
        elif e["tclass"].get("article", 0) + e["tclass"].get("product", 0) == n \
                and e["aclass"].get("descriptive", 0) + e["aclass"].get("branded", 0) >= n / 2 \
                and e["ext_median"] < 120:
            verdict = "KEEP_AFFILIATE_RETAIN"
            reason = ("Descriptive or branded anchors pointing at deep articles "
                      "and product pages, on a page with a normal outbound-link "
                      "count — editorial citation shape.")
        elif e["nofollow"] == n:
            verdict = "REVIEW_MANUALLY"
            reason = (f"All {n} links are nofollow, so no equity passes; "
                      "sequence as hygiene, not repair.")
        elif e["aclass"].get("raw-url", 0) >= n / 2:
            verdict = "REVIEW_MANUALLY"
            reason = (f"{e['aclass']['raw-url']}/{n} anchors are the bare "
                      "target URL, replicated across a templated footprint. "
                      "No exact-match commercial anchor, so low equity risk, "
                      "but not editorial either.")
        else:
            verdict = "REVIEW_MANUALLY"
            reason = (f"No single footprint dominates: anchors "
                      f"{dict(e['aclass'].most_common(3))}, targets "
                      f"{dict(e['tclass'].most_common(2))}, "
                      f"{e['follow']} follow / {e['nofollow']} nofollow.")

        dead = sum(v for k, v in e["codes"].items() if k in ("0", "404", "410"))
        counts[verdict] += 1
        top = e["anchors"].most_common(1)[0][0] if e["anchors"] else ""
        out.append({
            "Referring Domain": d,
            "Old Flag": e["old_flag"],
            "Verdict": verdict,
            "Backlinks (stated)": e["stated"],
            "Links Pulled": n,
            "Follow": e["follow"],
            "Nofollow": e["nofollow"],
            "Unique Anchors": len(e["anchors"]),
            "Top Anchor": top[:120],
            "Anchor Profile": ";".join(f"{k}={v}" for k, v in e["aclass"].most_common()),
            "Target Profile": ";".join(f"{k}={v}" for k, v in e["tclass"].most_common()),
            "Redirect Hosts": ";".join(sorted(e["hops"])),
            "Affiliate Account IDs": ";".join(sorted(e["aff"])),
            "Programme Banner IDs": ";".join(sorted(e["banners"])),
            "Sponsor Path": e["sponsor"] or "",
            "Filler Anchors": e["filler"],
            "Dead/Unreachable": dead,
            "Median Outlinks": e["ext_median"],
            "Reason": reason,
        })

    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/needing_data_resolved.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    print(f"domains resolved: {len(out)}  from {sum(o['Links Pulled'] for o in out)} links")
    for k, v in counts.most_common():
        print(f"  {v:4d}  {k}")
    print("\nclone networks:")
    for k, v in clone_members.items():
        print(f"  {len(v):3d} domains  {k}")
    print("\naffiliate accounts spanning >1 domain:")
    for a, ds in sorted(aff_members.items(), key=lambda kv: -len(kv[1])):
        if len(ds) > 1:
            print(f"  {len(ds):3d}  {a}  {', '.join(sorted(ds)[:5])}")
    print(f"\nWritten: {outdir}/needing_data_resolved.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
