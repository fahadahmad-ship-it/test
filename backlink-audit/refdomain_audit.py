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
from urllib.parse import urlsplit

from nameshape import name_shape
from audit import (
    AFFILIATE_REDIRECT_SOURCES, BRAND_REDIRECT_HOSTS, CLIENT_OVERRIDES,
    anchor_type,
    CONFIRMED_AFFILIATE_REDIRECTS,
    host_of, audit_key, _registrable, BRAND_OWNED, AFFILIATE_NETWORKS,
    SCRAPER_AGGREGATOR, SPAM_BLOG_NETWORK, SEARCH_AI_SURFACES,
    DIRECTORY_SPAM_RE, NICHE_RE, TRACKER_HOST_RE, COUPON_AGGREGATOR_RE,
    FAKE_OFFER_DOMAIN_RE, AUTOGEN_PATH_RE, LINKDUMP_PATH_RE,
    has_opaque_segment,
    DISAVOW, KEEP, REVIEW,
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
    "198.185.159": "Squarespace",
    "198.202.211": "Squarespace",
    "34.149.87":   "Google Cloud",
    "184.168.110": "GoDaddy shared hosting",
    "192.124.249": "Sucuri / managed hosting",
    # Google ranges host Blogspot/Blogger tenants. Co-location here means
    # Google, not a shared owner.
    "64.233.180":  "Google / Blogger",
    "142.251.111": "Google / Blogger",
    "192.178.155": "Google / Blogger",
    "172.217.14":  "Google / Blogger",
    "216.58.194":  "Google / Blogger",
}

# Spam-associated TLDs used by the cross-TLD sibling detector below.
SIBLING_SPAM_TLDS = {
    "xyz", "top", "icu", "buzz", "click", "sbs", "cfd", "space", "website",
    "site", "online", "fun", "pw", "work", "live", "art", "world", "life",
    "shop", "store", "monster", "quest", "party", "beauty", "today", "bio",
    "fyi", "cyou", "bond", "rest",
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
    r"a2zseo|99ranks|clicktohigh|[-.]links?[-.]|^links?[-.]|"
    # Bare 'seo' only at a token boundary: houseofcoco.net contains the
    # letters s-e-o and is a magazine, not a link vendor.
    r"(^|[-.])seo([-.]|tool|space|domain|link|tech|analysis|\d)|"
    r"seo(link|tool|domain|submit)|(digital|new|blogger?)seo|"
    r"^addurl|(^|[-.])rankvance|buyseo|"
    r"dom(ain)?raider|links?crawl|crawl(er)?links?|scrapeb?o?x",
    re.I,
)

# Exact-match-domain keyword stuffing: several niche terms welded together
# with hyphens on a near-zero-authority domain.
EMD_STUFFING_RE = re.compile(
    r"^(?=(?:[a-z]+-){2,})(?=.*(supplement|nootropic|health|vitamin|fitness|"
    r"weightloss|testosterone|wellness|nutrition|protein))[a-z-]+$",
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

# Domains first seen on or after this date are "new" for velocity purposes.
# Set from the export's own latest-seen date (2026-08-24) minus ~3 months.
NEW_DOMAIN_CUTOFF = "2026-06-01"


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

    # -- client overrides ---------------------------------------------------
    if d in CLIENT_OVERRIDES or reg in CLIENT_OVERRIDES:
        act, rf, why = CLIENT_OVERRIDES.get(d) or CLIENT_OVERRIDES[reg]
        return (act, rf, "High", why)

    # -- protected ---------------------------------------------------------
    if d in CONFIRMED_AFFILIATE_REDIRECTS or reg in CONFIRMED_AFFILIATE_REDIRECTS:
        brand = d in BRAND_REDIRECT_HOSTS or reg in BRAND_REDIRECT_HOSTS
        return (KEEP,
                "None - Brand Redirect / Tracking Host" if brand
                else "None - Confirmed Affiliate Redirect Infrastructure",
                "High",
                "Brand-owned redirect shell carrying the programme's own "
                "affiliate parameters." if brand
                else "Client-confirmed affiliate redirect host.")

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
        return (KEEP, "None - Search / AI Surface (Not Disavowable)", "High",
                "Search engine or AI answer surface. Passes no manipulable "
                "equity and cannot be disavowed meaningfully — a review step "
                "has no possible outcome.")

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

    # Sitting on a free host is not evidence. This rule used to disavow 37
    # subdomains outright, then a "deployment cohort" variant disavowed 29;
    # both were wrong. The 19 *.pages.dev domains that look like a single
    # operator's batch (aabigaildedman, sareeyharriett, loneeykimberli) have
    # first-seen dates spread over 18 months, one backlink each, and IPs in
    # 172.66.44-47 -- which is Cloudflare Pages' shared anycast range, so
    # every pages.dev site resolves there. The "cohort" was therefore just
    # "hosted on Cloudflare Pages", the same mistake as condemning
    # futurefood.website for sharing a Google IP with Blogspot spam.
    #
    # What is actually left is a name-shape judgment, and name shape is not
    # allowed to disavow anywhere else in this audit. So these fall through
    # to the ordinary rules: a free-host subdomain with link-level spam
    # evidence is still condemned on that evidence, and one without it lands
    # in the exposure triage, which is the honest answer for 1 backlink at
    # authority 2.
    if d.endswith(FREE_HOST_SUFFIXES) and asc <= 5:
        host = next(s for s in FREE_HOST_SUFFIXES if d.endswith(s))
        return (REVIEW, "Disposable Host, No Independent Evidence", "Low",
                f"{host.lstrip('.')} subdomain at authority {asc}. The host "
                "tells you nothing on its own — framework demo apps and "
                "throwaway doorways share it — and no spam signal was "
                "observed on the placement itself.")

    if EMD_STUFFING_RE.match(reg.rsplit(".", 1)[0]) and asc <= 3:
        return (DISAVOW, "Keyword-Stuffed Exact-Match Domain", "High",
                "Several niche terms hyphenated together on a domain scoring "
                f"{asc} — an exact-match domain registered for the anchor, "
                "not a publisher.")

    if LINK_VENDOR_NAME_RE.search(d):
        return (DISAVOW, "Link-Selling / SEO Vendor Domain", "High",
                "Domain name advertises link sales or SEO link services.")

    if reg in SPAM_BLOG_NETWORK:
        return (DISAVOW, "Vendor Blog Network (Spun-Content PBN)", "High",
                "Free-blog host used exclusively by link vendors.")

    if reg in SCRAPER_AGGREGATOR:
        if asc >= 15:
            return (KEEP, "None - Site-Profile Aggregator (No Equity Passed)", "High",
                    f"Established profile-listing service at authority {asc}. "
                    "An auto-generated profile is an incidental citation, not "
                    "a placed link.")
        return (REVIEW, "Site-Profile Aggregator - Low Authority", "Low",
                "Auto-generated profile listing; not disavowable on the "
                "pattern alone.")

    if STATS_DIRECTORY_NAME_RE.search(d):
        return (DISAVOW, "Auto-Generated Domain-Flipping / Stats Farm", "High",
                "Domain-parking or bulk-stats marketplace page, "
                f"authority {asc} — generated inventory, not a publisher.")

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

    # Link velocity, which the brief asked for and nothing implemented until
    # now. A domain first seen weeks ago at near-zero authority did not earn
    # a hundred links editorially. This only downgrades to review: velocity
    # is a reason to look, not a signature, and a genuinely new publisher
    # exists. It deliberately outranks the name-based relevance KEEP below,
    # which was retaining brand-new zero-authority domains purely because
    # their names contained niche words.
    if (r["First seen"] >= NEW_DOMAIN_CUTOFF and asc <= 3 and bl >= 20):
        return (REVIEW, "Newly-Seen Domain, Aggressive Link Velocity", "Medium",
                f"First seen {r['First seen']} at authority {asc}, already "
                f"carrying {bl} backlinks. Acquiring that volume that fast is "
                "not editorial; needs a look before it is retained on a "
                "niche-sounding name.")

    if tld in SPAM_TLDS and asc <= 5:
        return (REVIEW, "Spam-Associated TLD, Near-Zero Authority", "Medium",
                f".{tld} domain at authority score {asc}.")

    if asc <= 2 and bl >= 50:
        return (REVIEW, "High Link Volume from Near-Zero Authority Domain", "Medium",
                f"{bl:,} backlinks from a domain scoring {asc} — templated "
                "or sitewide placement.")

    if COUPON_AGGREGATOR_RE.search(reg.split(".")[0]):
        return (KEEP, "None - Coupon / Deals Aggregator (Protected)", "Medium",
                "The brief protects coupon and deals aggregators explicitly. "
                "Retained; no manual step adds anything without a liveness "
                "check that this data cannot provide.")

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


def remediation_priority(action, bl_true, fol, known):
    """Work order for a verdict. Follow links first, nofollow last.

    Kept as a function because the resolution pass rewrites verdicts after
    this has already run: _set() was flipping a row to DISAVOW and leaving
    the priority at "-", which put 92 domains -- one network with 158 follow
    links among them -- below the nofollow-only work in the sheet.
    """
    if action == REVIEW and bl_true >= 1000:
        return "P1 - Review first (dominates the profile)"
    if action != DISAVOW:
        return "-"
    if known and fol == 0:
        return "P3 - Nofollow only (no equity passed)"
    if known and fol >= 25:
        return "P1 - Follow links at volume"
    if known:
        return "P2 - Follow links, low volume"
    return ("P1 - Follow status unknown, high volume" if bl_true >= 100
            else "P2 - Follow status unknown")


def main(backlinks_csv, refdomains_csv, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)

    rd = list(csv.DictReader(open(refdomains_csv, encoding="utf-8", errors="replace")))
    # Raw link rows: the resolution pass needs every anchor, not just each
    # domain's most frequent one.
    with open(backlinks_csv, encoding="utf-8", errors="replace", newline="") as _fh:
        link_rows = list(csv.DictReader(_fh))

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

        if bl < 10 and asc >= 3:
            return (KEEP, "None - Negligible Exposure (Risk-Triaged)", "Medium",
                    f"{bl} backlink(s) from an authority-{asc} domain with no "
                    "spam signature, plausible name and no hosting cluster. "
                    "Too little exposure to justify either a disavow or a "
                    "manual review — retained on risk, not verified on merit.",
                    evid + " + risk triage")

        # Authority 0-2 is the floor, so a clean name and no cluster is the
        # weakest evidence in the audit. But one or two links from such a
        # domain cannot move a profile of 1.36M: disavowing gains nothing
        # measurable and a review has no data to work from. Retained on
        # exposure alone, and labelled as the lowest-evidence tier.
        if bl <= 2:
            return (KEEP, "None - Negligible Exposure (Lowest Evidence Tier)", "Low",
                    f"{bl} backlink(s) from an authority-{asc} domain. No spam "
                    "signature, no hosting cluster, plausible name — but also "
                    "no link-level data and near-zero authority. Retained "
                    "because the exposure is immaterial either way, not "
                    "because the domain was verified.",
                    evid + " + risk triage (lowest tier)")
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
        # A structural, name-based signature outranks a link-level affiliate
        # KEEP. Affiliate tracking says who is paid, not whether the
        # placement is legitimate: the brief's own exception is "a spam
        # network masquerading as an affiliate". The guard added to stop
        # anchor rules condemning tracked partners was shielding 196
        # directory-spam domains as "Tracked Affiliate Partner", collapsing
        # the Directory Submission Spam Network from 274 condemned to 14 --
        # all of them the same rogue affiliate account seen earlier.
        NAME_BASED_SPAM = (
            "Directory Submission Spam Network",
            "Link-Selling / SEO Vendor Domain",
            "Auto-Generated Domain-Flipping / Stats Farm",
            "Numbered Sibling Domain Network (PBN)",
            "Vendor Blog Network (Spun-Content PBN)",
            "Synthetic Affiliate Doorway Domain",
            "Directory / Link-Scheme Spam Footprint",
            "Keyword-Stuffed Exact-Match Domain",
            "Throwaway Free-Host Subdomain",
        )
        _dv = classify_domain(r, ctx)
        structural = _dv[0] == DISAVOW and _dv[1] in NAME_BASED_SPAM

        lv = link.get(d)
        # A name-based structural signature outranks two link-level readings:
        # an affiliate label it should never have earned (196 directory
        # domains were retained as "Tracked Affiliate Partner"), and an
        # unresolved REVIEW. kingranks.com, wayranks.com and skylinkseo.site
        # sat in review on outbound volume the research-corpus guard rightly
        # blocks, while their names -- "ranks", "seo", "link" -- are the SEO
        # vendor signature the domain-level pass already recognises. Breaking
        # a tie is not the same as overruling positive behavioural evidence,
        # so a KEEP earned on an observed redirect or affiliate parameter is
        # left alone.
        _override = lv is not None and structural and (
            "Affiliate Partner" in lv["Primary Risk Factor"]
            or lv["Action Recommendation"] == REVIEW)
        if _override:
            action, risk, conf, why = _dv
            evid = "Link-level, overridden by structural signature"
            counts[action] += 1
            lv = None
        elif lv:
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
        elif not lv:
            action, risk, conf, why = _dv
            evid = "Domain-level only (outside sample)"

        # An authoritative source citing the brand is a good link even when
        # its own subject is something else: a marketing blog illustrating a
        # point with an e-commerce example, an SEO tool using the site as a
        # case study, a genetics site linking a creatine article. The
        # link-level pass cannot judge this -- it sees only PAGE authority,
        # which is low on a deep blog post even at ranktracker.com's domain
        # authority of 42. Domain authority exists only here.
        OFF_NICHE_REVIEWS = (
            "Off-Topic Source, Branded Anchor Profile",
            "High-OBL Page, Branded Anchor Profile",
            "Low-Authority / Off-Topic Single Placement",
            "Unclassified - Insufficient Signal",
            "Off-Topic Source, Editorial Anchor Diversity",
        )
        if (action == REVIEW and risk in OFF_NICHE_REVIEWS
                and _i(r["Domain ascore"]) >= 20):
            action = KEEP
            risk = "None - Authoritative Off-Niche Citation"
            conf = "Medium"
            why = (f"Domain authority {_i(r['Domain ascore'])} source outside "
                   "the health niche, no exact-match anchor abuse and no spam "
                   "signature. Reads as an editorial citation; the niche "
                   "lexicon does not cover the source's own subject, and the "
                   "link-level pass saw only low page-level authority.")

        action, risk, conf, why, evid = residual_triage(
            r, action, risk, conf, why, evid)
        counts[action] += 1

        bl_true = _i(r["Backlinks"])
        fol = _i(lv["Follow (Equity) Links"]) if lv else ""
        pri = remediation_priority(action, bl_true, fol, known=lv is not None)

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

    # ---- resolution pass -------------------------------------------------
    # Three cross-domain signatures that only exist in aggregate, applied
    # after every domain has a provisional verdict.
    idx = {o["Referring Domain"]: o for o in out}

    def _set(o, action, risk, conf, why):
        if o["Referring Domain"] in CLIENT_OVERRIDES:
            return  # a client decision is not overturned by a later signature
        o["Action Recommendation"] = action
        o["Primary Risk Factor"] = risk
        o["Confidence Score"] = conf
        o["Rationale"] = why
        o["Disavow Entry"] = f"domain:{o['Referring Domain']}" if action == DISAVOW else ""
        o["Remediation Priority"] = remediation_priority(
            action, o["Backlinks (true)"], o["Follow (Equity) Links"],
            known=o["Follow (Equity) Links"] != "")

    # 1. Same second-level name registered across multiple spam TLDs. A human
    #    picks one TLD; a generator takes whatever is cheap.
    cores = defaultdict(list)
    for o in out:
        parts = o["Referring Domain"].split(".")
        if len(parts) == 2 and parts[1] in SIBLING_SPAM_TLDS:
            cores[parts[0]].append(o)
    n_sib = 0
    for core, group in cores.items():
        if len(group) >= 2 and all(o["Domain ascore"] <= 5 for o in group):
            for o in group:
                if o["Action Recommendation"] == REVIEW:
                    n_sib += 1
                    _set(o, DISAVOW, "Cross-TLD Sibling Network (Generated Domains)",
                         "High",
                         f"'{core}' is registered across {len(group)} "
                         f"spam-associated TLDs ({', '.join(sorted(x['Referring Domain'].split('.')[1] for x in group))}) "
                         "at near-zero authority — a domain generator, not a publisher.")

    # 2. Identical backlink counts across near-zero-authority domains. Organic
    #    link acquisition does not produce three domains with exactly the same
    #    total; one deployment script does.
    bycount = defaultdict(list)
    for o in out:
        if o["Domain ascore"] <= 3 and o["Backlinks (true)"] >= 20:
            bycount[o["Backlinks (true)"]].append(o)
    n_cohort = 0
    for n, group in bycount.items():
        if len(group) >= 3:
            for o in group:
                if o["Action Recommendation"] == REVIEW:
                    n_cohort += 1
                    _set(o, DISAVOW, "Identical-Footprint Cohort (Same Operator)",
                         "High",
                         f"{len(group)} referring domains carry exactly {n} "
                         "backlinks each at authority 3 or below "
                         f"({', '.join(sorted(x['Referring Domain'] for x in group)[:4])}) — "
                         "a single deployment, not organic acquisition.")

    # 3. Verbatim scraped-content clones. A commerce comparison table lifted
    #    from a real publisher carries its price cells across as anchor text,
    #    so the clones share exact anchor strings like "Taster box - 4 bars
    #    (£8.99)" or "£132 at performancelab.com". The originals share them
    #    too, which is why the authority gate is essential: bbcgoodfood.com
    #    scores 87 and goodhousekeeping.com is the source, while every clone
    #    sits at 2. This footprint is invisible to the outbound-link and
    #    anchor rules -- the anchors read as branded and OBL is only ~72.
    # Built from raw link rows, not per-domain top anchors. Two earlier
    # attempts failed here: keying on the summary column flagged 451 domains
    # (driven by "performancelab.com", "Performance Lab" and the literal
    # placeholder "(empty/image)"), and after tightening it flagged 0 --
    # because the index was built on cleaned anchors while the match still
    # used the raw column with its "(+N more)" suffix, so nothing ever
    # matched. The raw rows avoid both problems.
    #
    # A lifted price cell is recognisable: a currency amount or a unit count,
    # and never a branded or bare-URL anchor.
    PRICE_CELL_RE = re.compile(
        r"[\u00a3$\u20ac]\s?\d|\(\s*[\u00a3$\u20ac]?\d"
        r"|\d+\s*(bars?|pack|caps?|servings?|tabs?)\b", re.I)

    def _distinctive(a):
        a = (a or "").strip()
        if len(a) < 10:
            return None
        # The price test comes FIRST: "\u00a3132 at performancelab.com" is typed
        # Branded because it names the brand, but it is a price cell lifted
        # from a table. Checking the type first excluded seven clones.
        if PRICE_CELL_RE.search(a):
            return a
        return None

    anchor_owners = defaultdict(set)
    domain_anchors = defaultdict(set)
    for _lr in link_rows:
        _a = _distinctive(_lr.get("Anchor"))
        if _a:
            _d = audit_key(host_of(_lr["Source url"]))
            anchor_owners[_a].add(_d)
            domain_anchors[_d].add(_a)
    shared = {a for a, ds in anchor_owners.items() if len(ds) >= 4}

    n_clone = 0
    for o in out:
        # Fires on KEEP as well as REVIEW: the branded-anchor brake reads
        # "\u00a3132 at performancelab.com" as a brand mention when it is a price
        # cell carried over with the rest of the table. At authority 5 or
        # below, sharing a publisher's exact price cell is conclusive.
        _hit = sorted(domain_anchors.get(o["Referring Domain"], set()) & shared)
        if (_hit and o["Action Recommendation"] != DISAVOW
                and o["Domain ascore"] <= 5):
            a = _hit[0]
            n_clone += 1
            _set(o, DISAVOW, "Verbatim Scraped-Content Clone", "High",
                 f"Carries the verbatim anchor {a[:44]!r}, which appears on "
                 f"{len(anchor_owners[a])} other referring domains including "
                 "established publishers. A lifted commerce table at "
                 f"authority {o['Domain ascore']}, not original content.")

    # 3b. Shared link-template footprint. When five or more referring
    #     domains link from the byte-identical URL path, they are running one
    #     operator's script -- 96 domains served /domain-list-456 with ~1,000
    #     outbound links each, and 100 served
    #     /czechia_farm-13-08-2025/seo-anomaly-czechia_farm-10.
    #
    #     Two exclusions keep this off legitimate publishers. A path naming
    #     the client's own products is a natural slug that independent
    #     reviewers converge on (29 domains publish /performance-lab-mind),
    #     and an on-niche topical path is the same story
    #     (/review/best-vitamin-d-supplements is shared by 15 domains, one of
    #     them bbcgoodfood.com). So a readable on-niche slug is excluded
    #     unless the path is itself machine-generated; what survives is
    #     off-niche syndicated filler and generated identifiers.
    BRAND_PATH_TOKEN = re.compile(
        r"performance[-_ ]?lab|mind[-_ ]?lab|opti[-_ ]?nutra|nutropic|"
        r"testo[-_ ]?lab|burn[-_ ]?lab|pre[-_ ]?lab|prelab", re.I)

    path_owners = defaultdict(set)
    for _lr in link_rows:
        _p = urlsplit(_lr["Source url"]).path.rstrip("/")
        if len(_p) >= 8:
            path_owners[_p].add(audit_key(host_of(_lr["Source url"])))

    template_domains = {}
    for _p, _ds in path_owners.items():
        if BRAND_PATH_TOKEN.search(_p):
            continue
        generated = bool(AUTOGEN_PATH_RE.search(_p)
                         or LINKDUMP_PATH_RE.search(_p))
        # An opaque mixed-case segment is decisive at two owners; a readable
        # path needs five, because independent publishers do converge on the
        # same slug.
        floor = 2 if has_opaque_segment(_p) else 5
        if len(_ds) < floor:
            continue
        if not generated and not has_opaque_segment(_p) \
                and NICHE_RE.search(re.sub(r"[-_/]+", " ", _p)):
            continue
        for _d in _ds:
            prev = template_domains.get(_d)
            if not prev or len(_ds) > len(path_owners[prev]):
                template_domains[_d] = _p

    n_tmpl = 0
    for o in out:
        _p = template_domains.get(o["Referring Domain"])
        if _p and o["Action Recommendation"] != DISAVOW:
            n_tmpl += 1
            _set(o, DISAVOW, "Shared Link-Template Footprint (Same Operator)",
                 "High",
                 f"Links from the path {_p[:52]!r}, served byte-identically by "
                 f"{len(path_owners[_p])} other referring domains. One "
                 "operator's script deployed across many hosts, not "
                 "independent editorial placements.")

    # 4. Verdict propagation inside a concentrated hosting footprint. Only
    #    where the cluster is already overwhelmingly condemned on evidence
    #    independent of hosting, and never on a shared platform.
    cl = defaultdict(list)
    for o in out:
        if o["C-Block"] and not o["Hosting"]:
            cl[o["C-Block"]].append(o)
    n_prop = 0
    for cbk, members in cl.items():
        if len(members) < 8:
            continue
        dis = [m for m in members if m["Action Recommendation"] == DISAVOW]
        # Count only condemnations that do NOT themselves derive from
        # hosting, otherwise the cluster justifies itself in a loop.
        independent = [m for m in dis
                       if "Hosting Footprint" not in m["Primary Risk Factor"]]
        if (len(dis) / len(members) >= 0.70
                or (len(dis) / len(members) >= 0.50
                    and len(independent) / len(members) >= 0.30)):
            for o in members:
                if o["Action Recommendation"] == REVIEW:
                    n_prop += 1
                    _set(o, DISAVOW, "PBN Hosting Footprint (Cluster Propagation)",
                         "High",
                         f"{len(dis)} of {len(members)} domains on {cbk} are "
                         f"condemned, {len(independent)} of them on evidence "
                         "independent of hosting (link-vendor naming, directory "
                         "spam, generated siblings). Not a mainstream host, so "
                         "co-location indicates the same operator.")

    log = {"cross_tld_siblings": n_sib, "identical_cohorts": n_cohort,
           "scraped_clones": n_clone, "shared_link_templates": n_tmpl,
           "cluster_propagation": n_prop}

    # The resolution pass rewrites verdicts after the per-domain counter was
    # incremented, so recount from the final rows rather than trusting it.
    counts = Counter(o["Action Recommendation"] for o in out)

    out.sort(key=lambda x: (order[x["Action Recommendation"]],
                            -x["Backlinks (true)"]))

    dis = [x for x in out if x["Action Recommendation"] == DISAVOW]
    total_bl = sum(x["Backlinks (true)"] for x in out)
    dis_bl = sum(x["Backlinks (true)"] for x in dis)


    # Split the disavow file by whether the links can actually pass equity.
    # A nofollow-only footprint passes none, so filing it changes nothing --
    # it is hygiene, and mixing it into the main file inflates the list and
    # buries the domains that matter. Kept as a separate addendum so the
    # decision to file it is explicit rather than implied.
    core = [x for x in out if x["Action Recommendation"] == DISAVOW
            and not x["Remediation Priority"].startswith("P3")]
    hygiene = [x for x in out if x["Action Recommendation"] == DISAVOW
               and x["Remediation Priority"].startswith("P3")]

    # A hacked site is a victim, not a bad actor: its other pages are
    # legitimate and may link again. Where the compromised page sits on a
    # subdomain, disavow that subdomain rather than the registrable root --
    # uba.ar is the University of Buenos Aires at authority 68, and the
    # injection is on quantitativemarxism.economicas.uba.ar alone. A
    # domain:uba.ar line would discard every future academic citation.
    hacked_hosts = defaultdict(set)
    for _lr in link_rows:
        _h = host_of(_lr["Source url"])
        hacked_hosts[audit_key(_h)].add(_h)

    def _ascii_host(h):
        """Punycode an internationalised host for the disavow file.

        Google's tool takes ASCII; a Unicode line is at best ignored. One
        entry hit this -- a compromised Korean university,
        한국사이버신학대학교.kr, which has to be written
        xn--9d0b4b70vnol89ezvdmykd32abaw.kr to have any effect. The audit
        keeps the readable form everywhere else, because that is the name a
        human recognises.
        """
        if all(ord(c) < 128 for c in h):
            return h
        try:
            return h.encode("idna").decode("ascii")
        except UnicodeError:
            # Better a line that cannot work than a silently wrong domain.
            return h

    def _scope(x):
        """The narrowest disavow scope that still covers the placement."""
        d = x["Referring Domain"]
        if "Hacked Site" not in x["Primary Risk Factor"]:
            hosts = [d]
        else:
            hosts = sorted(hacked_hosts.get(d, {d}))
            # Only narrow when every compromised host is a subdomain; if the
            # root itself is hit there is no narrower scope available.
            if not (hosts and all(h != d for h in hosts)):
                hosts = [d]
        return [f"domain:{_ascii_host(h)}" for h in hosts]

    # The sheet's Disavow Entry column must say exactly what the submitted
    # file says. It was showing "domain:uba.ar" while the file correctly
    # narrowed to the compromised subdomain -- the client reads the sheet.
    for x in out:
        if x["Action Recommendation"] == DISAVOW:
            x["Disavow Entry"] = " ".join(_scope(x))

    with open(f"{outdir}/full_refdomain_audit.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    def _write_disavow(path, rows_, title, note):
        """Entries only -- no comment headers, no grouping, no blank lines.

        Google ignores comment lines, so they only ever served a human
        reading the file, and the client does not want them. The grouping
        and the reasoning live in the workbook and in
        full_refdomain_audit.csv, which is where they belong: the submitted
        file should contain exactly what is being submitted and nothing
        else. `title` and `note` are kept in the signature because the
        callers still describe each file, and those descriptions are what
        the README documents.
        """
        with open(path, "w", encoding="utf-8") as fh:
            for line in sorted({s for x in rows_ for s in _scope(x)}):
                fh.write(f"{line}\n")

    _write_disavow(
        f"{outdir}/disavow.txt", dis,
        "disavow file - THE ONE TO SUBMIT (full profile)",
        [f"Referring domains evaluated: {len(out):,}",
         f"Total backlinks represented: {total_bl:,}",
         f"Disavowed backlinks: {dis_bl:,}",
         "Includes nofollow-only domains per client decision; see",
         "disavow_core.txt for the equity-passing subset alone.",
         "Search/AI surfaces and affiliate infrastructure excluded by design.",
         "Hacked sites are scoped to the compromised host, not the",
         "institution's root domain."])
    _write_disavow(
        f"{outdir}/disavow_core.txt", core,
        "disavow file (equity-passing)",
        ["These domains carry follow links, or their follow status is unknown.",
         "A subset of disavow.txt, not a replacement for it -- kept so the",
         "equity-passing share of the list is visible.",
         "Search/AI surfaces and affiliate infrastructure are excluded by design."])
    _write_disavow(
        f"{outdir}/disavow_nofollow_hygiene.txt", hygiene,
        "disavow addendum (nofollow only - optional)",
        ["Every sampled link on these domains is nofollow, so none of them",
         "passes equity and disavowing them changes nothing measurable.",
         "Filed only if you want the profile clean on paper. Most are hacked-site",
         "injections and link-farm listings, which are worth knowing about even",
         "though they are inert."])

    ev = Counter(x["Evidence Level"] for x in out)
    print(f"Referring domains evaluated : {len(out):,}")
    print(f"Total backlinks represented : {total_bl:,}")
    print(f"  link-level evidence       : {ev['Link-level (in 50k sample)']:,}")
    print(f"  domain-level only         : {ev['Domain-level only (outside sample)']:,}")
    print()
    print(f"{'ACTION':<24}{'DOMAINS':>9}{'BACKLINKS':>14}{'% LINKS':>10}")
    final = Counter(x["Action Recommendation"] for x in out)
    for a in (DISAVOW, REVIEW, KEEP):
        b = sum(x["Backlinks (true)"] for x in out
                if x["Action Recommendation"] == a)
        print(f"{a:<24}{final[a]:>9,}{b:>14,}{b/total_bl:>9.1%}")
    print()
    print("Disavow risk factors:")
    # Recomputed from the final rows, not from a counter kept during
    # classification: the resolution pass rewrites verdicts after the fact.
    by_risk = Counter(x["Primary Risk Factor"] for x in out
                      if x["Action Recommendation"] == DISAVOW)
    for k, v in by_risk.most_common():
        print(f"  {v:>4}  {k}")
    print()
    print()
    print("Resolution pass:")
    for k, v in log.items():
        print(f"  {v:>4}  {k}")
    print()
    print(f"Written: {outdir}/full_refdomain_audit.csv, disavow.txt "
          f"(the file to submit), disavow_core.txt, "
          f"disavow_nofollow_hygiene.txt")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
