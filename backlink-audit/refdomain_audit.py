#!/usr/bin/env python3
"""Full referring-domain audit for performancelab.com.

The backlinks export is capped at 50,000 rows — 3.7% of the 1.36M-link
profile, and not a random sample: one domain occupies 91% of it. Auditing it
alone covers only 603 of 2,928 referring domains. This module audits the
FULL referring-domain export and merges in the richer link-level verdicts
where the sample provides them, so every domain gets a verdict and each
carries the evidence level it was decided on.

Usage:
    python3 refdomain_audit.py <backlinks.csv> <refdomains.csv> <outdir>
"""
import csv
import re
import sys
import statistics
from collections import Counter, defaultdict

from nameshape import name_shape
from audit import (
    AFFILIATE_REDIRECT_SOURCES, CONFIRMED_AFFILIATE_REDIRECTS,
    host_of, audit_key, _registrable, BRAND_OWNED, AFFILIATE_NETWORKS,
    SCRAPER_AGGREGATOR, SPAM_BLOG_NETWORK, SEARCH_AI_SURFACES,
    DIRECTORY_SPAM_RE, NICHE_RE, TRACKER_HOST_RE, COUPON_AGGREGATOR_RE,
    FAKE_OFFER_DOMAIN_RE, DISAVOW, KEEP, REVIEW,
)

# --------------------------------------------------------------------------
# Hosting: shared platforms vs genuine footprints
# --------------------------------------------------------------------------

# Co-location on these ranges means "same SaaS/CDN", not "same owner".
# Treating them as a footprint would flag Shopify stores (including the
# client's own brand estate) and every WordPress.com blog.
SHARED_PLATFORM_CBLOCK = {
    "23.227.38":   "Shopify",
    "192.0.78":    "WordPress.com / Automattic",
    "192.0.66":    "WordPress.com / Automattic",
    "141.193.213": "WP Engine / managed WordPress",
    "184.168.115": "GoDaddy shared hosting",
    "184.168.109": "GoDaddy shared hosting",
    "184.168.116": "GoDaddy shared hosting",
    "199.34.228":  "Weebly / Square",
    "34.102.136":  "Google Cloud front-end",
    "76.76.21":    "Vercel",
    "185.230.63":  "Wix",
    "185.230.62":  "Wix",
}
CLOUDFLARE_PREFIXES = (
    "172.64.", "172.65.", "172.66.", "172.67.", "172.68.", "172.69.",
    "104.16.", "104.17.", "104.18.", "104.19.", "104.20.", "104.21.",
    "104.22.", "104.23.", "104.24.", "104.25.", "104.26.", "104.27.",
    "104.28.", "162.159.", "188.114.", "198.41.",
)


def cblock(ip):
    ip = (ip or "").strip()
    return ".".join(ip.split(".")[:3]) if ip.count(".") == 3 else ""


def is_cloudflare(ip):
    return (ip or "").startswith(CLOUDFLARE_PREFIXES)


# --------------------------------------------------------------------------
# Domain-name spam signatures
# --------------------------------------------------------------------------

# Domains that sell or trade links, named as such.
LINK_VENDOR_NAME_RE = re.compile(
    r"backlink|linkbuild|buylink|linkfarm|linksnatcher|seoservice|"
    r"seoarticle|seobacklink|linkexchange|articlesubmit|guestpost|"
    r"pbn|linkwheel|seocartel|seo-anomaly|seoanomaly|rankbooster|"
    r"boostrank|highpr|dofollow|linkjuice|seosubmit|submitlink|"
    r"a2zseo|99ranks|clicktohigh|[-.]links?[-.]|^links?[-.]",
    re.I,
)

# Auto-generated site-profile / stats / directory scrapers.
STATS_DIRECTORY_NAME_RE = re.compile(
    r"(websitestats|webstats|siteworth|domainanalysis|domainstats|"
    r"websitesdirectory|webdirectory|sitestat|domaininfo|whoisdomain|"
    r"rank2traffic|urlrate|hypestat|indexaward|pagesearch|websiterace|"
    r"allwebsites|domainsc|domain\.com|domains\.com)",
    re.I,
)

SPAM_TLDS = {
    "xyz", "top", "icu", "buzz", "click", "sbs", "cfd", "bond", "rest",
    "cyou", "quest", "monster", "beauty", "hair", "skin", "makeup", "pw",
    "tk", "ml", "ga", "cf", "gq", "work", "loan", "date", "racing", "win",
    "bid", "stream", "download", "review", "party", "faith", "cricket",
    "space", "website", "site", "online", "fun", "life", "world", "art",
}


# Generic web directories. Directory submission is a textbook link scheme and
# these are near-uniformly auto-generated; a real niche directory carries
# authority, so the score gate protects those.
GENERIC_DIRECTORY_RE = re.compile(r"director(y|ies)", re.I)

# Free throwaway app/page hosting. Legitimate projects use these too, so this
# only fires alongside near-zero authority.
FREE_HOST_SUFFIXES = (
    ".pages.dev", ".workers.dev", ".netlify.app", ".vercel.app", ".web.app",
    ".firebaseapp.com", ".github.io", ".glitch.me", ".repl.co",
    ".onrender.com", ".surge.sh", ".herokuapp.com", ".gitbook.io",
    ".blogspot.com", ".weebly.com", ".wixsite.com", ".000webhostapp.com",
)


def sibling_family(domain):
    """Collapse generated siblings into one family key.

    Handles both numeric sequences (seo-anomaly-top-7.xyz) and short trailing
    geo/letter codes (bhs-links-fr.xyz, bhs-links-gb.xyz), which are the same
    generator with a different suffix scheme.
    """
    d = re.sub(r"\d+", "#", domain)
    return re.sub(r"-[a-z]{2}(?=\.)", "-@@", d)


def _i(v, d=0):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return d


# --------------------------------------------------------------------------
# Domain-level classifier (used where no link-level sample exists)
# --------------------------------------------------------------------------

def classify_domain(r, ctx):
    """Verdict from referring-domain metrics alone.

    Signal here is thinner than the link-level pass — no anchors, no
    outbound-link counts, no per-page context — so the bar for DISAVOW is a
    signature that cannot plausibly be innocent, and everything else routes
    to review.
    """
    d = r["Domain"]
    reg = _registrable(d)
    asc = _i(r["Domain ascore"])
    bl = _i(r["Backlinks"])
    ip = (r["IP Address"] or "").strip()
    cb = cblock(ip)
    tld = d.rsplit(".", 1)[-1].lower()

    # -- protected ---------------------------------------------------------
    if d in CONFIRMED_AFFILIATE_REDIRECTS or reg in CONFIRMED_AFFILIATE_REDIRECTS:
        return (KEEP, "None - Confirmed Affiliate Redirect Infrastructure", "High",
                "Client-confirmed affiliate redirect host.")

    if d in AFFILIATE_REDIRECT_SOURCES:
        how = AFFILIATE_REDIRECT_SOURCES[d]
        host = sorted(CONFIRMED_AFFILIATE_REDIRECTS)[0]
        if how == "verified":
            return (KEEP, "None - Affiliate Placement (Verified Redirect)", "High",
                    f"Every link routes through {host}, client-confirmed "
                    "affiliate infrastructure. A templated placement is a "
                    "commercial decision, not a toxicity signal, and the "
                    "brief protects affiliate redirects explicitly.")
        return (KEEP, "None - Affiliate Placement (Inferred Same Network)", "Medium",
                f"Shares the full {host} network footprint -- auto-generated "
                "utility pages, templated commerce CTA, bare homepage target, "
                "nofollow -- but its redirect was not pulled. Retained by "
                "inference; confirm via the API redirect_url column.")

    if reg in BRAND_OWNED or d in BRAND_OWNED:
        return (KEEP, "None - Brand-Owned Estate (Opti-Nutra network)", "High",
                "First-party brand property.")
    if reg in AFFILIATE_NETWORKS or TRACKER_HOST_RE.match(d):
        return (KEEP, "None - Safe Affiliate Redirect / Tracking Gateway", "High",
                "Affiliate or partner-network infrastructure.")
    if reg in SEARCH_AI_SURFACES:
        return (REVIEW, "Search / AI Answer Surface - Not Disavowable", "High",
                "Passes no manipulable equity; exclude from the disavow file.")

    # -- unambiguous spam signatures ---------------------------------------
    fam = ctx["families"].get(sibling_family(d), 0)
    if fam >= 3 and re.search(r"\d", d):
        return (DISAVOW, "Numbered Sibling Domain Network (PBN)", "High",
                f"One of {fam} numerically-sequenced sibling domains "
                f"({sibling_family(d)}) — machine-generated network.")

    if GENERIC_DIRECTORY_RE.search(d) and asc <= 8:
        return (DISAVOW, "Directory Submission Spam Network", "High",
                f"Generic web directory at authority score {asc}. Directory "
                "submission is a link scheme and these are auto-generated; "
                "278 such domains link to the site.")

    if d.endswith(FREE_HOST_SUFFIXES) and asc <= 5:
        host = next(s for s in FREE_HOST_SUFFIXES if d.endswith(s))
        return (DISAVOW, "Throwaway Free-Host Subdomain", "High",
                f"Disposable {host.lstrip('.')} subdomain at authority score "
                f"{asc} — no editorial publisher behind it.")

    if LINK_VENDOR_NAME_RE.search(d):
        return (DISAVOW, "Link-Selling / SEO Vendor Domain", "High",
                "Domain name advertises link sales or SEO link services.")

    if reg in SPAM_BLOG_NETWORK:
        return (DISAVOW, "Vendor Blog Network (Spun-Content PBN)", "High",
                "Free-blog host used exclusively by link vendors.")

    if reg in SCRAPER_AGGREGATOR or STATS_DIRECTORY_NAME_RE.search(d):
        return (DISAVOW, "Scraped Aggregator / Auto-Generated Directory", "High",
                "Auto-generated site-profile or directory scraper.")

    if DIRECTORY_SPAM_RE.search(d):
        return (DISAVOW, "Directory / Link-Scheme Spam Footprint", "High",
                "Domain name matches a link-scheme or paid-directory pattern.")

    if FAKE_OFFER_DOMAIN_RE.search(reg):
        return (DISAVOW, "Synthetic Affiliate Doorway Domain", "High",
                "Geo-prefixed / doubled-hyphen throwaway offer-page pattern.")

    # Concentrated hosting footprint. Only meaningful off shared platforms,
    # and only when the whole cluster is near-zero authority.
    cl = ctx["cblocks"].get(cb)
    if (cl and cb not in SHARED_PLATFORM_CBLOCK and not is_cloudflare(ip)
            and cl["n"] >= 10 and cl["median_as"] <= 3 and asc <= 5):
        return (DISAVOW, "PBN Hosting Footprint (Shared C-Block)", "High",
                f"{cl['n']} referring domains share {cb}.0/24 with a median "
                f"authority of {cl['median_as']:g} — a single-owner footprint, "
                "not a mainstream host.")

    # Mass templated footprint. hexcolor.co, currencyconverts.com and
    # appsrankings.com are confirmed one network from the sample: auto-
    # generated utility pages injecting a localised commerce CTA ("Buy Now!",
    # "Satin Al!") at the bare homepage. Volume at this scale on a low-
    # authority domain is that same shape, but these are held for the client
    # decision already taken on hexcolor.co rather than filed unilaterally.
    if bl >= 1000 and asc <= 30:
        return (REVIEW, "Mass Templated Footprint (Held with hexcolor.co)", "High",
                f"{bl:,} backlinks from a domain scoring {asc} — the "
                "templated-injection profile confirmed for hexcolor.co / "
                "appsrankings.com. No link-level sample here, and held for "
                "the same client decision.")

    # -- borderline --------------------------------------------------------
    if (cl and cb not in SHARED_PLATFORM_CBLOCK and not is_cloudflare(ip)
            and cl["n"] >= 8):
        return (REVIEW, "Hosting Cluster - Verify Ownership", "Medium",
                f"{cl['n']} referring domains share {cb}.0/24 (median AS "
                f"{cl['median_as']:g}). Could be one owner or a niche host.")

    if tld in SPAM_TLDS and asc <= 5:
        return (REVIEW, "Spam-Associated TLD, Near-Zero Authority", "Medium",
                f".{tld} domain at authority score {asc}.")

    if asc <= 2 and bl >= 50:
        return (REVIEW, "High Link Volume from Near-Zero Authority Domain", "Medium",
                f"{bl:,} backlinks from a domain scoring {asc} — templated "
                "or sitewide placement.")

    if COUPON_AGGREGATOR_RE.search(reg.split(".")[0]):
        return (REVIEW, "Coupon / Deals Aggregator - Retain by Default", "Medium",
                "Protected architecture; confirm the offer resolves.")

    if NICHE_RE.search(d):
        return (KEEP, "None - Topically Aligned Domain", "Low",
                "Domain name aligns with the health/performance niche. "
                "No link-level sample available to confirm placement quality.")

    if asc >= 20:
        return (KEEP, "None - Established Authority Domain", "Low",
                f"Authority score {asc}; no spam signature. No link-level "
                "sample available to confirm anchor or placement quality.")

    return (REVIEW, "No Link-Level Sample - Unverified", "Low",
            f"Authority {asc}, {bl:,} backlink(s). Outside the 50k sample, so "
            "no anchor, placement or outbound-link signal exists to judge on.")


# --------------------------------------------------------------------------
# Merge + output
# --------------------------------------------------------------------------

COLS = [
    "Referring Domain", "Action Recommendation", "Primary Risk Factor",
    "Confidence Score", "Evidence Level", "Remediation Priority",
    "Backlinks (true)", "Backlinks (in sample)", "Follow (Equity) Links",
    "Domain ascore", "IP Address", "C-Block", "Hosting", "Country",
    "Target URL", "Anchor Text", "Unique Anchors", "Exact-Match Anchor %",
    "Branded/URL Anchor %", "Avg External Links", "Nofollow %",
    "Topically Relevant", "First seen", "Last seen", "Disavow Entry",
    "Rationale",
]


def main(backlinks_csv, refdomains_csv, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)

    rd = list(csv.DictReader(open(refdomains_csv, encoding="utf-8", errors="replace")))

    # Link-level verdicts already computed by audit.py
    link = {}
    try:
        for r in csv.DictReader(open(f"{outdir}/domain_audit.csv", encoding="utf-8")):
            link[r["Referring Domain / URL"]] = r
    except FileNotFoundError:
        sys.exit("run audit.py first — domain_audit.csv not found")

    # context: sibling families and C-block clusters
    families = Counter(sibling_family(r["Domain"]) for r in rd)
    cb_rows = defaultdict(list)
    for r in rd:
        cb = cblock(r["IP Address"])
        if cb:
            cb_rows[cb].append(r)
    cblocks = {
        cb: {"n": len(v),
             "median_as": statistics.median([_i(x["Domain ascore"]) for x in v])}
        for cb, v in cb_rows.items()
    }
    ctx = {"families": families, "cblocks": cblocks}

    order = {DISAVOW: 0, REVIEW: 1, KEEP: 2}
    out, counts = [], Counter()

    def residual_triage(r, action, risk, conf, why, evid, ctx=ctx):
        """Resolve low-exposure review rows instead of parking them.

        For the 957 domains outside the sample there is no anchor, target or
        placement signal — that data simply is not in the export. What is
        left is exposure, authority, hosting and name shape. A domain with a
        couple of links, ordinary authority and no spam marker is not worth a
        human hour: disavowing it gains nothing and keeping it costs nothing.
        That is a risk decision, not a quality endorsement, and the risk
        factor says so.

        Name shape is deliberately NOT allowed to disavow on its own. It
        misreads initialisms (jsrproductions, hmscicomms) as generated, and
        the domains it would catch carry negligible exposure anyway.
        """
        if action != REVIEW:
            return action, risk, conf, why, evid
        d = r["Domain"]
        asc, bl = _i(r["Domain ascore"]), _i(r["Backlinks"])
        tld = d.rsplit(".", 1)[-1].lower()
        shape = name_shape(d)[0]
        held = "client decision" in risk or "Held with" in risk

        # Check cluster membership against the real C-block index rather than
        # the risk-factor string: a domain that arrived via the link-level
        # path never carries the "Hosting Cluster" label even when it sits in
        # one.
        cb_here = cblock(r["IP Address"])
        in_cluster = (cb_here and cb_here not in SHARED_PLATFORM_CBLOCK
                      and not is_cloudflare(r["IP Address"] or "")
                      and ctx["cblocks"].get(cb_here, {}).get("n", 0) >= 8)

        marker = (held
                  or in_cluster
                  or risk.startswith("Hosting Cluster")
                  or "Search / AI" in risk
                  or tld in SPAM_TLDS
                  or shape != "plausible"
                  or bl >= 25
                  or (bl >= 10 and asc <= 5))
        if marker:
            if shape != "plausible" and not held and "shape" not in why:
                why += f" Domain name shape reads as {shape}."
            return action, risk, conf, why, evid

        if bl <= 5 and asc >= 3:
            return (KEEP, "None - Negligible Exposure (Risk-Triaged)", "Medium",
                    f"{bl} backlink(s) from an authority-{asc} domain with no "
                    "spam signature, plausible name and no hosting cluster. "
                    "Too little exposure to justify either a disavow or a "
                    "manual review — retained on risk, not verified on merit.",
                    evid + " + risk triage")
        if asc >= 6 and bl < 10:
            return (KEEP, "None - Ordinary Small Publisher (Risk-Triaged)", "Medium",
                    f"Authority {asc}, {bl} backlink(s), brandable name, no "
                    "spam marker. Reads as an ordinary small site; retained "
                    "on risk without link-level verification.",
                    evid + " + risk triage")
        return action, risk, conf, why, evid
    for r in rd:
        d = r["Domain"]
        ip = (r["IP Address"] or "").strip()
        cb = cblock(ip)
        host = SHARED_PLATFORM_CBLOCK.get(cb, "Cloudflare (shared CDN)"
                                          if is_cloudflare(ip) else "")
        lv = link.get(d)
        if lv:
            action = lv["Action Recommendation"]
            risk, conf = lv["Primary Risk Factor"], lv["Confidence Score"]
            why, evid = lv["Rationale"], "Link-level (in 50k sample)"
            # A handful of sampled rows cannot characterise a domain carrying
            # thousands of links. Where the sample covers under 1% of the
            # domain's real volume, the thin link-level verdict is replaced by
            # the mass-footprint reading and the evidence level says so.
            n_s = _i(lv["Backlinks"])
            # A protected-affiliate verdict is evidence about the placement
            # itself, not an artefact of a thin sample, so it is not
            # displaced by volume.
            protected = "Affiliate" in risk or "Brand-Owned" in risk
            if (_i(r["Backlinks"]) >= 1000 and n_s / max(_i(r["Backlinks"]), 1) < 0.01
                    and action != DISAVOW and not protected):
                action = REVIEW
                risk = "Mass Templated Footprint (Held with hexcolor.co)"
                conf = "High"
                why = (f"{_i(r['Backlinks']):,} backlinks but only {n_s} row(s) "
                       "in the 50k sample, so the link-level verdict rests on "
                       "under 1% of the domain. Volume at this scale on an "
                       f"authority-{_i(r['Domain ascore'])} domain is the "
                       "hexcolor.co / "
                       "appsrankings.com templated-injection profile; held for "
                       "the same client decision.")
                evid = "Link-level sample too thin (<1% of domain)"
        else:
            action, risk, conf, why = classify_domain(r, ctx)
            evid = "Domain-level only (outside sample)"

        action, risk, conf, why, evid = residual_triage(
            r, action, risk, conf, why, evid)
        counts[action] += 1

        bl_true = _i(r["Backlinks"])
        fol = _i(lv["Follow (Equity) Links"]) if lv else ""
        if action == REVIEW and bl_true >= 1000:
            pri = "P1 - Review first (dominates the profile)"
        elif action != DISAVOW:
            pri = "-"
        elif lv and fol == 0:
            pri = "P3 - Nofollow only (no equity passed)"
        elif lv and fol >= 25:
            pri = "P1 - Follow links at volume"
        elif lv:
            pri = "P2 - Follow links, low volume"
        else:
            pri = ("P1 - Follow status unknown, high volume" if bl_true >= 100
                   else "P2 - Follow status unknown")

        out.append({
            "Referring Domain": d,
            "Action Recommendation": action,
            "Primary Risk Factor": risk,
            "Confidence Score": conf,
            "Evidence Level": evid,
            "Remediation Priority": pri,
            "Backlinks (true)": bl_true,
            "Backlinks (in sample)": _i(lv["Backlinks"]) if lv else 0,
            "Follow (Equity) Links": fol,
            "Domain ascore": _i(r["Domain ascore"]),
            "IP Address": ip,
            "C-Block": f"{cb}.0/24" if cb else "",
            "Hosting": host,
            "Country": r.get("Country", ""),
            "Target URL": lv["Target URL"] if lv else "",
            "Anchor Text": lv["Anchor Text"] if lv else "",
            "Unique Anchors": lv["Unique Anchors"] if lv else "",
            "Exact-Match Anchor %": lv["Exact-Match Anchor %"] if lv else "",
            "Branded/URL Anchor %": lv["Branded/URL Anchor %"] if lv else "",
            "Avg External Links": lv["Avg External Links"] if lv else "",
            "Nofollow %": lv["Nofollow %"] if lv else "",
            "Topically Relevant": lv["Topically Relevant"] if lv else "",
            "First seen": r["First seen"],
            "Last seen": r["Last seen"],
            "Disavow Entry": f"domain:{d}" if action == DISAVOW else "",
            "Rationale": why,
        })

    out.sort(key=lambda x: (order[x["Action Recommendation"]],
                            -x["Backlinks (true)"]))

    with open(f"{outdir}/full_refdomain_audit.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    dis = sorted(x["Referring Domain"] for x in out
                 if x["Action Recommendation"] == DISAVOW)
    by_risk = defaultdict(list)
    for x in out:
        if x["Action Recommendation"] == DISAVOW:
            by_risk[x["Primary Risk Factor"]].append(x["Referring Domain"])
    total_bl = sum(x["Backlinks (true)"] for x in out)
    dis_bl = sum(x["Backlinks (true)"] for x in out
                 if x["Action Recommendation"] == DISAVOW)
    with open(f"{outdir}/disavow_full.txt", "w", encoding="utf-8") as fh:
        fh.write("# Performance Lab (performancelab.com) - disavow file (FULL profile)\n")
        fh.write(f"# Referring domains evaluated: {len(out):,}\n")
        fh.write(f"# Total backlinks represented: {total_bl:,}\n")
        fh.write(f"# Domains disavowed: {len(dis):,} ({dis_bl:,} backlinks)\n")
        fh.write("# Search/AI surfaces and affiliate infrastructure excluded by design.\n#\n")
        for risk in sorted(by_risk):
            fh.write(f"\n# --- {risk} ---\n")
            for d in sorted(by_risk[risk]):
                fh.write(f"domain:{d}\n")

    ev = Counter(x["Evidence Level"] for x in out)
    print(f"Referring domains evaluated : {len(out):,}")
    print(f"Total backlinks represented : {total_bl:,}")
    print(f"  link-level evidence       : {ev['Link-level (in 50k sample)']:,}")
    print(f"  domain-level only         : {ev['Domain-level only (outside sample)']:,}")
    print()
    print(f"{'ACTION':<24}{'DOMAINS':>9}{'BACKLINKS':>14}{'% LINKS':>10}")
    for a in (DISAVOW, REVIEW, KEEP):
        b = sum(x["Backlinks (true)"] for x in out
                if x["Action Recommendation"] == a)
        print(f"{a:<24}{counts[a]:>9,}{b:>14,}{b/total_bl:>9.1%}")
    print()
    print("Disavow risk factors:")
    for k, v in sorted(by_risk.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(v):>4}  {k}")
    print()
    print(f"Written: {outdir}/full_refdomain_audit.csv, disavow_full.txt")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
