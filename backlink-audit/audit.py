#!/usr/bin/env python3
"""
Performance Lab (performancelab.com) backlink disavow audit.

Deterministic, rule-based classifier. Evaluates at referring-domain (root)
level first, then drills into individual URLs for borderline / high-risk cases.

Usage:
    python3 audit.py <backlinks.csv> <outdir>
"""
import csv
import re
import sys
import statistics
from collections import Counter, defaultdict
from urllib.parse import urlsplit

csv.field_size_limit(10**9)

# --------------------------------------------------------------------------
# Domain handling
# --------------------------------------------------------------------------

# Multi-part public suffixes we actually encounter in this dataset.
# Generic second-level labels that act as public suffixes under a ccTLD
# (co.uk, com.au, edu.co, gov.mg ...). Disavowing at that level would be
# catastrophically over-broad, so we always keep one more label.
GENERIC_2LD = {
    "co", "com", "net", "org", "edu", "gov", "ac", "gob", "mil", "sch",
    "or", "ne", "go", "in", "info", "biz", "nom", "asn", "id", "lg",
}

# Shared publishing / hosting platforms. Every account is an independent
# publisher, so the aggregation and disavow unit MUST be the full hostname.
# Keying these at the root would merge unrelated sites and, worse, emit a
# disavow line that nukes the entire platform.
PLATFORM_HOSTS = {
    "blogspot.com", "wordpress.com", "substack.com", "medium.com",
    "tumblr.com", "weebly.com", "wixsite.com", "wix.com", "blogger.com",
    "livejournal.com", "over-blog.com", "jimdosite.com", "webnode.com",
    "strikingly.com", "simplecast.com", "github.io", "netlify.app",
    "vercel.app", "herokuapp.com", "notion.site", "gitbook.io",
    "hashnode.dev", "hubpages.com", "ghost.io", "square.site",
    "myshopify.com", "bigcartel.com", "tripod.com", "angelfire.com",
    "sites.google.com", "groups.google.com", "wordpress.org",
    "substack.app", "beehiiv.com", "mystrikingly.com", "yolasite.com",
}
# Platform roots that are themselves two labels under a ccTLD, e.g.
# blogspot.co.uk, blogspot.com.au — matched by suffix below.
PLATFORM_SUFFIX_RE = re.compile(
    r"(^|\.)(blogspot|wordpress|tumblr|weebly|wixsite|jimdo|webnode)\."
)


def host_of(url: str) -> str:
    h = urlsplit(url).netloc.lower().split(":")[0].strip()
    return h[4:] if h.startswith("www.") else h


def _registrable(hostname: str) -> str:
    """Registrable domain, honouring generic ccTLD second-level labels."""
    parts = [p for p in hostname.split(".") if p]
    if len(parts) <= 2:
        return hostname
    # e.g. cecar.edu.co -> keep 3 labels; example.co.uk -> keep 3 labels
    if len(parts[-1]) <= 3 and parts[-2] in GENERIC_2LD:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def audit_key(hostname: str) -> str:
    """The unit of evaluation and of disavow output.

    Normally the registrable domain, but the FULL hostname for shared
    publishing platforms where each subdomain is a separate publisher.
    """
    reg = _registrable(hostname)
    if reg in PLATFORM_HOSTS or PLATFORM_SUFFIX_RE.search(reg + "."):
        return hostname
    return reg


def root_domain(hostname: str) -> str:
    return audit_key(hostname)


# --------------------------------------------------------------------------
# Whitelists — brand-owned estate, affiliate networks, trusted publishers
# --------------------------------------------------------------------------

# Opti-Nutra Ltd brand family. Performance Lab, Mind Lab Pro, Testo Lab Pro
# and Prelab Pro share ownership; cross-links are first-party brand estate
# and must never be disavowed.
BRAND_OWNED = {
    "performancelab.com", "mindlabpro.com", "testolabpro.com",
    "prelabpro.com", "burnlabpro.com", "opti-nutra.com", "optinutra.com",
}

# Affiliate / tracking / publisher-network infrastructure. Redirects and
# third-party hosting here are EXPECTED and are not a toxicity signal.
AFFILIATE_NETWORKS = {
    "wowtrk.com", "shareasale.com", "awin.com", "awin1.com", "zenaps.com",
    "cj.com", "anrdoezrs.net", "dpbolvw.net", "kqzyfj.com", "jdoqocy.com",
    "tkqlhce.com", "impact.com", "impactradius.com", "sjv.io", "pxf.io",
    "skimlinks.com", "redirectingat.com", "go2cloud.org", "hasoffers.com",
    "everflow.io", "trackonomics.net", "narrativ.com", "linksynergy.com",
    "rakuten.com", "partnerize.com", "prf.hn", "avantlink.com",
    "flexoffers.com", "shopstyle.com", "viglink.com", "clickbank.net",
    "hop.clickbank.net", "refersion.com", "postaffiliatepro.com",
    "tapfiliate.com", "trackdesk.com", "affilibox.com",
}

# Redirect hosts confirmed by the client as their affiliate infrastructure.
# A link routing through one of these is a paid/affiliate placement, and the
# brief protects it: a redirect is never itself a toxicity signal.
CONFIRMED_AFFILIATE_REDIRECTS = {"drect.net"}

# Referring domains observed routing through a confirmed affiliate redirect.
# hexcolor.co and currencyconverts.com were verified directly from the
# Semrush API `redirect_url` column (drect.net/performancelab on every row).
# appsrankings.com shares the whole footprint -- auto-generated utility
# pages, a templated commerce CTA ("Satin Al!" = "Buy Now!"), bare homepage
# target, nofollow -- but its redirect was never pulled, so it is retained
# by inference rather than verification.
AFFILIATE_REDIRECT_SOURCES = {
    "hexcolor.co":          "verified",
    "currencyconverts.com": "verified",
    "appsrankings.com":     "inferred",
}

# Tracker / redirect subdomain patterns seen on partner infrastructure.
TRACKER_HOST_RE = re.compile(
    r"^(go|track|click|offers?|link|links|r|t|c|aff|partner|promo|out|ref)\."
)

# --------------------------------------------------------------------------
# Known-bad: scrapers, aggregators, AI answer engines, directory spam
# --------------------------------------------------------------------------

SCRAPER_AGGREGATOR = {
    "sitelike.org", "similarweb.com", "siteworthtraffic.com", "statshow.com",
    "urlrate.com", "websiteoutlook.com", "hypestat.com", "worthofweb.com",
    "sitelike.com", "alternativeto.net", "webstatsdomain.org",
    "site-stats.org", "rank2traffic.com", "expireddomains.net",
}

# Search engines / AI answer engines. Not editorial links; no equity, and
# nothing to disavow — excluded from the disavow file, reported separately.
SEARCH_AI_SURFACES = {
    "bing.com", "google.com", "yandex.ru", "duckduckgo.com",
    "glarity.app", "ithy.com", "perplexity.ai", "phind.com",
    "you.com", "kagi.com", "brave.com",
}

# Free-blog-hosting platforms used almost exclusively by cheap link vendors.
# No legitimate publisher operates on these, so the registrable domain is the
# correct disavow unit — it also catches future placements from the network.
SPAM_BLOG_NETWORK = {
    "tkzblog.com", "bligblogging.com", "blog4youth.com", "mpeblog.com",
    "blogkoo.com", "ampblogs.com", "diowebhost.com", "pointblog.net",
    "amoblog.com", "getblogs.net", "full-design.com", "fitnell.com",
    "activoblog.com", "activosblog.com", "bloggazza.com", "blog-gold.com",
    "blogadvize.com", "blogprodesign.com", "dailyblogzz.com", "idblogz.com",
    "livebloggs.com", "worldblogged.com", "liberty-blog.com",
    "sharebyblog.com", "blogolize.com", "onesmablog.com", "shotblogs.com",
    "tribunablog.com", "blogzet.com", "blogminds.com", "suomiblog.com",
    "affiliatblogger.com", "designertoblog.com", "bloginwi.com",
    "ezblogz.com", "blogdigy.com", "mybjjblog.com", "articlesblogger.com",
    "arwebo.com", "blogerus.com", "bloggerbags.com", "bloggerswise.com",
    "bloggosite.com", "blogpayz.com", "blogrelation.com", "blogrenanda.com",
    "blogsidea.com", "blogthisbiz.com", "blogunteer.com", "blogvivi.com",
    "atualblog.com", "blogaritma.com", "canariblogs.com", "qowap.com",
    "jaiblogs.com", "izrablog.com", "aioblogs.com", "look4blog.com",
    "ka-blogs.com", "blogofoto.com", "timeblog.net", "mybloglicious.com",
    "isblog.net", "post-blogs.com", "thezenweb.com", "tinyblogging.com",
    "widblog.com", "dbblog.net", "ampedpages.com", "myparisblog.com",
    "imblogs.net", "bcbloggers.com", "blogscribble.com", "elbloglibre.com",
    "loginblogin.com", "mdkblog.com", "mybuzzblog.com", "theobloggers.com",
    "topbloghub.com", "vblogetin.com", "win-blog.com", "blogspothub.com",
}

# Random auto-generated account subdomain, e.g. flynnbkwh412420.tkzblog.com
THROWAWAY_SUBDOMAIN_RE = re.compile(r"^[a-z]{4,14}[a-z0-9]*\d{4,8}\.")

# Synthetic affiliate doorway domains: geo-prefixed and/or doubled hyphens,
# e.g. us-en--prozenith.com, en-en-prozenith.us, us-us--reduburn.com
FAKE_OFFER_DOMAIN_RE = re.compile(
    r"^((us|uk|en|de|fr|es|it|ca|au|nl|pt|jp)-){2,}"
    r"|--"
    r"|^(us|uk|en|de|fr|es|it)-[a-z-]+-(us|uk|en|de|fr|es|it)\.",
    re.I,
)

DIRECTORY_SPAM_RE = re.compile(
    r"(link|seo|backlink|submit|article|guest|press|bookmark)"
    r"[a-z]*(directory|list|dir|submission|exchange|building)"
    r"|(directory|dir)[a-z]*(link|seo|submit)",
    re.I,
)

# --------------------------------------------------------------------------
# Topical relevance lexicon — health / fitness / supplementation / biohacking
# --------------------------------------------------------------------------

NICHE_TERMS = [
    "health", "fit", "gym", "muscle", "nutri", "supplement", "vitamin",
    "nootropic", "brain", "cognit", "biohack", "wellness", "workout",
    "protein", "keto", "paleo", "vegan", "diet", "weight", "athlet",
    "sport", "runner", "running", "cycling", "yoga", "pilates", "strength",
    "bodybuild", "physique", "testosterone", "hormone", "sleep", "recovery",
    "longevity", "performance", "energy", "endurance", "crossfit", "mma",
    "wellbeing", "medical", "doctor", "clinic", "nurse", "pharma", "herbal",
    "organic", "meal", "recipe", "wholefood", "calorie", "macro",
    "mind", "mental", "psycholog", "neuro", "focus", "memory", "stress",
    "immune", "gut", "probiotic", "prebiotic", "omega", "collagen",
    "joint", "mobility", "physio", "therap", "rehab", "trainer", "coach",
    "selfcare", "aging", "senior", "hiking", "climb", "swim", "surf",
    "rugby", "soccer", "football", "basketball", "boxing", "wrestl",
    ]
NICHE_RE = re.compile("|".join(NICHE_TERMS), re.I)

# --------------------------------------------------------------------------
# Anchor classification
# --------------------------------------------------------------------------

BRAND_TOKENS = ("performance lab", "performancelab", "mind lab pro",
                "mindlabpro", "testo lab pro", "prelab pro", "opti-nutra",
                "opti nutra", "nutrigenesis")

# Affiliate / commerce call-to-action anchors. Commercial in tone but
# generic — these are marketplace CTAs, NOT keyword-stuffed money anchors.
CTA_ANCHORS_RE = re.compile(
    r"^\W*(buy( it)?( now)?|shop( now)?|check (the )?(latest )?price|"
    r"check (out )?(the )?(best )?deals?|view (on|price)|get (it|yours)( now)?|"
    r"order( now)?|see price|best price|preview|link|visit( site| website)?|"
    r"here|click here|read more|learn more|more info|website|official site|"
    r"official website|source|via|\[\d+\]|\d+|)\W*$",
    re.I,
)

# Exact-match / keyword-stuffed commercial money anchors.
MONEY_ANCHOR_RE = re.compile(
    r"\b(best|top|cheap|buy|order|discount|coupon|review of|strongest|"
    r"most effective|leading|recommended|ultimate)\b.{0,60}?"
    r"\b(supplement|nootropic|booster|vitamin|multivitamin|protein|"
    r"pre-?workout|testosterone|omega|probiotic|prebiotic|collagen|"
    r"powder|capsule|pill|stack|brand|joint|sleep aid|fat burner|"
    r"energy|creatine|bcaa)s?\b",
    re.I,
)
MONEY_ANCHOR_RE2 = re.compile(
    r"\b(supplement|nootropic|booster|multivitamin|pre-?workout|"
    r"testosterone|fat burner|joint supplement|brain supplement)s?\b"
    r".{0,40}\b(best|top|cheap|buy|online|for sale|deal)\b",
    re.I,
)


# Hacked-site / link-vendor injection. These anchors are advertisements
# placed by the intruder, not by a publisher.
HACKED_INJECTION_RE = re.compile(
    r"(tg\s*@|@links_dealer|effective seo links|seo links for|"
    r"telegram\s*@|t\.me/|buy backlinks|xrumer|gsa ser|"
    r"\bсео\b|ссылк|прогон)",
    re.I,
)

# Coupon / deals / voucher aggregators — explicitly retained architecture.
COUPON_AGGREGATOR_RE = re.compile(
    r"(coupon|promo(code)?|deals?|discount|voucher|freestuff|savings?|"
    r"bargain|offers?|cashback|slickdeal|retailmenot|honey)",
    re.I,
)

# Standard Performance Lab site paths. A target path OUTSIDE this set that
# every link from a domain points at is a bespoke partner/sponsor landing
# page — i.e. deliberate co-marketing architecture, never toxicity.
STANDARD_PATHS = {
    "", "blogs", "products", "collections", "pages", "cart", "account",
    "search", "apps", "policies", "tools", "a", "discount",
}


def target_path_head(url: str) -> str:
    p = urlsplit(url).path.strip("/").split("/")
    return p[0].lower() if p and p[0] else ""


def anchor_type(anchor: str) -> str:
    a = (anchor or "").strip()
    if not a:
        return "Empty/Image"
    low = a.lower()
    if any(t in low for t in BRAND_TOKENS):
        return "Branded"
    if "performancelab.com" in low.replace(" ", "") or low.startswith(("http://", "https://", "www.")):
        return "URL"
    if MONEY_ANCHOR_RE.search(a) or MONEY_ANCHOR_RE2.search(a):
        return "Exact/Commercial"
    if CTA_ANCHORS_RE.match(a):
        return "CTA/Generic"
    return "Phrasing"


def _b(v: str) -> bool:
    return str(v).strip().lower() == "true"


def _i(v, default=0) -> int:
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return default


# --------------------------------------------------------------------------
# Domain aggregation
# --------------------------------------------------------------------------

class DomainProfile:
    def __init__(self, domain):
        self.domain = domain
        self.rows = []

    def finalise(self):
        rows = self.rows
        self.n_links = len(rows)
        self.pages = {r["Source url"] for r in rows}
        self.n_pages = len(self.pages)

        ascores = [_i(r["Page ascore"]) for r in rows]
        self.max_ascore = max(ascores)
        self.median_ascore = statistics.median(ascores)

        ext = [_i(r["External links"]) for r in rows]
        self.avg_external = statistics.mean(ext) if ext else 0
        self.max_external = max(ext) if ext else 0

        anchors = [(r["Anchor"] or "").strip() for r in rows]
        self.anchor_counts = Counter(anchors)
        self.n_unique_anchors = len(self.anchor_counts)
        self.top_anchor, top_n = self.anchor_counts.most_common(1)[0]
        self.top_anchor_share = top_n / self.n_links
        self.top_anchor_type = anchor_type(self.top_anchor)

        types = Counter(anchor_type(a) for a in anchors)
        self.anchor_type_counts = types
        self.exact_share = types["Exact/Commercial"] / self.n_links
        self.branded_share = (types["Branded"] + types["URL"]) / self.n_links

        self.n_follow = sum(1 for r in rows if not _b(r["Nofollow"]))
        self.nofollow_rate = sum(1 for r in rows if _b(r["Nofollow"])) / self.n_links
        self.sponsored = any(_b(r["Sponsored"]) for r in rows)
        self.ugc = any(_b(r["Ugc"]) for r in rows)
        self.sitewide_flag = any(_b(r["Sitewide"]) for r in rows)
        self.lost_rate = sum(1 for r in rows if _b(r["Lost link"])) / self.n_links
        self.image_share = sum(1 for r in rows if _b(r["Image"])) / self.n_links

        self.titles = [r["Source title"] or "" for r in rows]
        self.n_unique_titles = len({t for t in self.titles})
        self.targets = Counter(r["Target url"] for r in rows)
        self.n_targets = len(self.targets)
        top_target_url = self.targets.most_common(1)[0][0]

        self.first_seen = min((r["First seen"] for r in rows if r["First seen"]), default="")
        self.last_seen = max((r["Last seen"] for r in rows if r["Last seen"]), default="")

        # Topical relevance: domain name OR a meaningful share of page titles
        # must intersect the health / performance lexicon.
        self.domain_relevant = bool(NICHE_RE.search(self.domain))
        matched = sum(1 for t in self.titles if NICHE_RE.search(t))
        self.title_relevance = matched / self.n_links
        self.relevant = self.domain_relevant or self.title_relevance >= 0.35

        # Templating: near-identical page titles across a large page count is
        # the signature of programmatic/auto-generated link placement.
        self.title_diversity = self.n_unique_titles / self.n_pages if self.n_pages else 1.0

        self.hosts = {host_of(r["Source url"]) for r in rows}
        self.registrable = _registrable(next(iter(self.hosts)))

        # Anchor diversity: distinct anchors per backlink. High values mean
        # an editorial profile; templated placements collapse toward zero.
        self.anchor_diversity = self.n_unique_anchors / self.n_links

        # Hacked / link-vendor injection anywhere in the anchor set.
        self.hacked = any(HACKED_INJECTION_RE.search(a) for a in self.anchor_counts)

        # Bespoke partner landing path, when every link shares one target.
        self.single_target_path = (target_path_head(top_target_url)
                                   if self.n_targets == 1 else None)


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

DISAVOW, KEEP, REVIEW = "DISAVOW", "KEEP_AFFILIATE_RETAIN", "REVIEW_MANUALLY"

# Domains held back from the disavow file for an explicit client decision,
# with the evidence that makes the call a judgement rather than a rule.
MANUAL_REVIEW_OVERRIDE = {
    "eastbayexpress.com":
        "HELD FOR CLIENT DECISION - established news outlet, but 667 FOLLOW "
        "links replicated across paginated archives carry the exact-match "
        "anchor 'best nootropics for improving physical performance'. This is "
        "the single largest equity exposure in the profile; confirm whether "
        "the placement was bought before filing.",
}


def classify(p: DomainProfile):
    """Return (action, risk_factor, confidence, rationale).

    Ordered rules, first match wins. Protected assets are resolved BEFORE
    any spam rule can fire, and a branded-anchor safety brake prevents
    circumstantial signals (relevance, outbound-link counts) from ever
    disavowing a domain whose links are overwhelmingly brand mentions.
    """
    d = p.domain

    # -- Tier 1: protected assets -------------------------------------------
    # Must precede every spam rule: these domains carry templated footprints
    # that would otherwise trip the PBN rules, but the placement routes
    # through client-confirmed affiliate infrastructure.
    if (p.registrable in CONFIRMED_AFFILIATE_REDIRECTS
            or d in CONFIRMED_AFFILIATE_REDIRECTS):
        return (KEEP, "None - Confirmed Affiliate Redirect Infrastructure", "High",
                "Client-confirmed affiliate redirect host.")

    if d in AFFILIATE_REDIRECT_SOURCES or p.registrable in AFFILIATE_REDIRECT_SOURCES:
        key = d if d in AFFILIATE_REDIRECT_SOURCES else p.registrable
        host = sorted(CONFIRMED_AFFILIATE_REDIRECTS)[0]
        if AFFILIATE_REDIRECT_SOURCES[key] == "verified":
            return (KEEP, "None - Affiliate Placement (Verified Redirect)", "High",
                    f"All {p.n_links:,} sampled links route through {host}, "
                    "client-confirmed affiliate infrastructure. A templated "
                    "placement is a commercial decision, not a toxicity "
                    "signal; the brief protects affiliate redirects.")
        return (KEEP, "None - Affiliate Placement (Inferred Same Network)", "Medium",
                f"Shares the {host} network footprint but its redirect was "
                "not pulled. Retained by inference; confirm via the API "
                "redirect_url column.")

    if p.registrable in BRAND_OWNED:
        return (KEEP, "None - Brand-Owned Estate (Opti-Nutra network)", "High",
                "First-party brand property; cross-brand linking is expected.")

    if p.registrable in AFFILIATE_NETWORKS or any(TRACKER_HOST_RE.match(h) for h in p.hosts):
        if p.avg_external >= 400 or (not p.relevant and p.median_ascore <= 2):
            return (REVIEW, "Affiliate Gateway w/ Link-Farm Traits", "Medium",
                    "Matches affiliate infrastructure but shows OBL bloat; "
                    "verify the redirect resolves to a live partner offer.")
        return (KEEP, "None - Safe Affiliate Redirect / Tracking Gateway", "High",
                "Affiliate or partner-network infrastructure; redirects and "
                "third-party hosting are expected, not a toxicity signal.")

    # Bespoke partner/sponsor landing page: every link lands on one custom
    # path outside the standard site structure, with brand-led anchors.
    if (p.n_targets == 1 and p.n_links >= 3 and p.branded_share >= 0.60
            and p.single_target_path not in STANDARD_PATHS
            and not p.hacked):
        return (KEEP, "None - Dedicated Partner / Sponsor Landing Page", "High",
                f"All {p.n_links} links resolve to the bespoke landing path "
                f"'/{p.single_target_path}' with brand-led anchors — "
                "co-marketing architecture, not manipulation.")

    if p.registrable in SEARCH_AI_SURFACES:
        return (KEEP, "None - Search / AI Surface (Not Disavowable)", "High",
                "Search engine or AI answer surface. Passes no manipulable "
                "equity and cannot be disavowed meaningfully — a review step "
                "has no possible outcome.")

    # -- Tier 2: unambiguous spam (fires regardless of anchor profile) -------
    if p.hacked:
        return (DISAVOW, "Hacked Site / Injected Link-Vendor Spam", "High",
                "Anchor carries a link-vendor advertisement — the placement "
                "is an intrusion on a compromised host, not an editorial link.")

    if p.registrable in SPAM_BLOG_NETWORK:
        return (DISAVOW, "Vendor Blog Network (Spun-Content PBN)", "High",
                "Free-blog-host domain used exclusively by link vendors; "
                f"{p.n_links} link(s) on throwaway auto-generated accounts.")

    if p.network_titles >= 1 and p.median_ascore <= 25:
        return (DISAVOW, "Spun-Content Network (Duplicate Article Footprint)", "High",
                f"Runs {p.network_titles} article(s) that appear near-verbatim "
                "on 3+ other referring domains — syndicated spun content, not "
                "original editorial.")

    if FAKE_OFFER_DOMAIN_RE.search(p.registrable):
        return (DISAVOW, "Synthetic Affiliate Doorway Domain", "High",
                "Geo-prefixed / doubled-hyphen domain pattern characteristic "
                "of throwaway affiliate offer pages for unrelated products.")

    if any(THROWAWAY_SUBDOMAIN_RE.match(h) for h in p.hosts) and p.median_ascore <= 25:
        return (DISAVOW, "Throwaway Auto-Generated Host", "High",
                "Randomly generated account subdomain — disposable link-vendor "
                "infrastructure.")

    if p.registrable in SCRAPER_AGGREGATOR:
        return (DISAVOW, "Scraped Aggregator / Stats-Site Profile", "High",
                "Auto-generated site-profile scraper; no editorial intent.")

    if DIRECTORY_SPAM_RE.search(d):
        return (DISAVOW, "Directory / Link-Scheme Spam Footprint", "High",
                "Domain name matches a link-scheme or paid-directory pattern.")

    # Programmatic mass footprint: many auto-generated pages carrying one
    # identical templated link, on a domain with no topical overlap.
    if (p.n_pages >= 20 and p.n_unique_anchors <= 2
            and p.title_diversity > 0.8 and not p.relevant):
        return (DISAVOW, "PBN / Templated Mass Footprint (Irrelevant Niche)", "High",
                f"{p.n_pages:,} auto-generated pages carrying an identical "
                f"templated anchor ({p.top_anchor!r}) with zero niche overlap.")

    # Sitewide paid-insertion signature: one non-branded anchor on ~every page.
    if (p.n_pages >= 8 and p.top_anchor_share >= 0.80
            and p.top_anchor_type in ("Exact/Commercial", "Phrasing")):
        rf = ("Exact-Match Anchor Abuse (Sitewide Injection)"
              if p.top_anchor_type == "Exact/Commercial"
              else "Sitewide Link Injection (Templated Anchor)")
        return (DISAVOW, rf, "High",
                f"Single non-branded anchor {p.top_anchor!r} repeated across "
                f"{p.n_pages} pages — paid sitewide insertion signature.")

    # Extreme outbound-link farms.
    if p.avg_external >= 1500:
        return (DISAVOW, "Link Farm / Outbound-Link Bloat", "High",
                f"Average {p.avg_external:.0f} external links per source page.")

    # -- Safety brake -------------------------------------------------------
    # A profile that is overwhelmingly branded or bare-URL anchors cannot be
    # anchor manipulation. Past this point, circumstantial signals may only
    # downgrade to REVIEW, never to DISAVOW.
    branded_safe = p.branded_share >= 0.80

    if COUPON_AGGREGATOR_RE.search(p.registrable.split(".")[0]):
        return (REVIEW, "Coupon / Deals Aggregator - Retain by Default", "Medium",
                "Coupon and deals aggregators are protected architecture; "
                "confirm the offer resolves before considering any action.")

    if p.avg_external >= 200:
        if branded_safe:
            return (REVIEW, "High-OBL Page, Branded Anchor Profile", "Low",
                    f"Pages average {p.avg_external:.0f} outbound links, but "
                    f"{p.branded_share:.0%} of anchors are brand/URL mentions. "
                    "Verify the placement is a directory listing before acting.")
        return (DISAVOW, "Link Farm / Outbound-Link Bloat", "High"
                if p.n_links >= 3 else "Medium",
                f"Average {p.avg_external:.0f} external links per source page "
                f"across {p.n_pages} linking page(s).")

    # Exact-match anchor abuse at scale — exempted when anchor diversity is
    # high enough to be editorial rather than templated.
    if (p.n_pages >= 15 and p.exact_share >= 0.15 and p.median_ascore <= 20
            and p.anchor_diversity < 0.50 and not branded_safe):
        return (DISAVOW, "Exact-Match Anchor Abuse (Syndicated Placement)", "High",
                f"{p.exact_share:.0%} exact-match commercial anchors across "
                f"{p.n_pages} low-authority pages (median AS {p.median_ascore:g}) "
                f"with only {p.n_unique_anchors} distinct anchors.")

    # Irrelevant niche at volume.
    if not p.relevant and p.n_pages >= 3 and p.median_ascore <= 10:
        if p.branded_share >= 0.40:
            return (REVIEW, "Off-Topic Source, Branded Anchor Profile", "Low",
                    f"No topical overlap, but {p.branded_share:.0%} of anchors "
                    "are brand/URL mentions. Retain unless manual review "
                    "shows a paid placement.")
        if p.anchor_diversity >= 0.60:
            return (REVIEW, "Off-Topic Source, Editorial Anchor Diversity", "Low",
                    f"No topical overlap, but {p.n_unique_anchors} distinct "
                    f"anchors across {p.n_links} links reads as editorial "
                    "rather than templated placement.")
        return (DISAVOW, "Irrelevant Niche Spam (No Topical Overlap)", "Medium",
                f"No semantic overlap with health/performance across "
                f"{p.n_pages} linking pages; median AS {p.median_ascore:g}.")

    # -- Tier 3: borderline --------------------------------------------------
    if not p.relevant and p.median_ascore <= 5 and not branded_safe:
        return (REVIEW, "Low-Authority / Off-Topic Single Placement", "Low",
                "Off-topic and low authority, but too little volume to "
                "classify with confidence. Manual eyeball recommended.")

    if p.avg_external >= 80 and p.median_ascore <= 10 and not branded_safe:
        return (REVIEW, "Elevated OBL on Low-Authority Pages", "Low",
                f"Average {p.avg_external:.0f} outbound links on low-authority "
                "pages; check for guest-post-network traits.")

    if p.exact_share >= 0.30 and p.n_links >= 3 and not branded_safe:
        return (REVIEW, "Elevated Exact-Match Anchor Ratio", "Medium",
                f"{p.exact_share:.0%} exact-match commercial anchors; verify "
                "placements are editorial rather than purchased.")

    # -- Tier 4: retain ------------------------------------------------------
    if p.relevant:
        return (KEEP, "None - Topically Relevant Editorial / Affiliate Link", "High",
                "Niche-aligned source with a natural anchor distribution "
                f"({p.branded_share:.0%} branded/URL anchors).")

    if branded_safe:
        return (KEEP, "None - Brand Mention / Citation", "Medium",
                f"{p.branded_share:.0%} branded or bare-URL anchors; reads as "
                "an unsolicited citation rather than a placed link.")

    return (REVIEW, "Unclassified - Insufficient Signal", "Low",
            "Does not match any spam pattern but relevance is unproven.")


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

DOMAIN_COLS = [
    "Referring Domain / URL", "Target URL", "Anchor Text",
    "Action Recommendation", "Primary Risk Factor", "Confidence Score",
    "Backlinks", "Linking Pages", "Unique Anchors", "Top Anchor Share",
    "Remediation Priority", "Follow (Equity) Links",
    "Exact-Match Anchor %", "Branded/URL Anchor %", "Median Page AScore",
    "Max Page AScore", "Avg External Links", "Nofollow %", "Sponsored",
    "Topically Relevant", "Distinct Targets", "Lost %",
    "First Seen", "Last Seen", "Rationale",
]

URL_COLS = [
    "Referring Domain / URL", "Target URL", "Anchor Text", "Anchor Type",
    "Action Recommendation", "Primary Risk Factor", "Confidence Score",
    "Referring Domain", "Page AScore", "External Links", "Nofollow",
    "Sponsored", "Sitewide", "Lost Link", "First Seen", "Last Seen",
]


def priority_of(action, p):
    """Disavow urgency. Nofollow links pass no equity, so a nofollow-only
    footprint is hygiene, not remediation — sequencing this correctly stops
    a headline row count from driving the workload."""
    if action != DISAVOW:
        return "-"
    if p.n_follow == 0:
        return "P3 - Nofollow only (no equity passed)"
    if p.n_follow >= 25:
        return "P1 - Follow links at volume"
    return "P2 - Follow links, low volume"


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main(src, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)

    with open(src, encoding="utf-8", errors="replace", newline="") as fh:
        rows = list(csv.DictReader(fh))

    profiles = defaultdict(lambda: None)
    buckets = defaultdict(DomainProfile.__new__)
    grouped = defaultdict(list)
    for r in rows:
        grouped[root_domain(host_of(r["Source url"]))].append(r)

    profiles = {}
    for dom, rs in grouped.items():
        p = DomainProfile(dom)
        p.rows = rs
        p.finalise()
        profiles[dom] = p

    # ---- cross-domain spun-content network detection --------------------
    # A vendor blog network reuses one spun article across many throwaway
    # domains. Any single domain looks harmless; the network is obvious only
    # in aggregate, so membership is computed globally before classification.
    def _norm_title(t):
        t = re.sub(r"[^a-z0-9 ]", "", (t or "").lower())
        return re.sub(r"\s+", " ", t).strip()[:70]

    title_domains = defaultdict(set)
    for dom, p in profiles.items():
        for t in p.titles:
            n = _norm_title(t)
            if len(n) >= 25:
                title_domains[n].add(dom)

    # One publisher syndicating its own article across its international
    # editions (thesun.co.uk / the-sun.com / thesun.ie) is not a network.
    # Collapse domains to a brand core and require genuinely distinct brands.
    def _brand_core(dom):
        core = dom.split(".")[0]
        return re.sub(r"[^a-z0-9]", "", core.lower())

    network_members = defaultdict(set)
    for n, doms in title_domains.items():
        if len({_brand_core(x) for x in doms}) >= 3:
            for dom in doms:
                network_members[dom].add(n)
    for dom, p in profiles.items():
        p.network_titles = len(network_members.get(dom, ()))

    verdicts = {d: classify(p) for d, p in profiles.items()}

    # ---- confidence gate + explicit manual-review overrides -------------
    # Anything short of High confidence is routed to manual review rather
    # than disavowed. A disavow is irreversible in practice; a review is not.
    for d, (a, rf, conf, why) in list(verdicts.items()):
        if d in MANUAL_REVIEW_OVERRIDE:
            verdicts[d] = (REVIEW, rf + " [flagged for client decision]",
                           conf, why + " " + MANUAL_REVIEW_OVERRIDE[d])
        elif a == DISAVOW and conf != "High":
            verdicts[d] = (REVIEW, rf + " [below disavow confidence bar]",
                           conf, why + " Confidence is not High; routed to "
                           "manual review rather than disavowed.")

    # ---- domain-level report ------------------------------------------
    dom_out = []
    for d, p in profiles.items():
        action, risk, conf, why = verdicts[d]
        top_target = p.targets.most_common(1)[0][0]
        dom_out.append({
            "Referring Domain / URL": d,
            "Target URL": (top_target if p.n_targets == 1
                           else f"{top_target} (+{p.n_targets - 1} more)"),
            "Anchor Text": (p.top_anchor or "(empty/image)")
                           + ("" if p.n_unique_anchors == 1
                              else f" (+{p.n_unique_anchors - 1} more)"),
            "Action Recommendation": action,
            "Primary Risk Factor": risk,
            "Confidence Score": conf,
            "Remediation Priority": priority_of(action, p),
            "Follow (Equity) Links": p.n_follow,
            "Backlinks": p.n_links,
            "Linking Pages": p.n_pages,
            "Unique Anchors": p.n_unique_anchors,
            "Top Anchor Share": f"{p.top_anchor_share:.0%}",
            "Exact-Match Anchor %": f"{p.exact_share:.0%}",
            "Branded/URL Anchor %": f"{p.branded_share:.0%}",
            "Median Page AScore": f"{p.median_ascore:g}",
            "Max Page AScore": p.max_ascore,
            "Avg External Links": f"{p.avg_external:.0f}",
            "Nofollow %": f"{p.nofollow_rate:.0%}",
            "Sponsored": "yes" if p.sponsored else "no",
            "Topically Relevant": "yes" if p.relevant else "no",
            "Distinct Targets": p.n_targets,
            "Lost %": f"{p.lost_rate:.0%}",
            "First Seen": p.first_seen,
            "Last Seen": p.last_seen,
            "Rationale": why,
        })
    order = {DISAVOW: 0, REVIEW: 1, KEEP: 2}
    dom_out.sort(key=lambda r: (order[r["Action Recommendation"]], -r["Backlinks"]))
    write_csv(f"{outdir}/domain_audit.csv", DOMAIN_COLS, dom_out)

    # ---- URL-level drill-down (DISAVOW + REVIEW only) -------------------
    # Templated mass footprints are capped: the domain-level verdict governs
    # and the sample is representative. Capping is reported, never silent.
    url_out, capped = [], {}
    CAP = 250
    for d, p in profiles.items():
        action, risk, conf, _ = verdicts[d]
        if action == KEEP:
            continue
        rs = p.rows
        if len(rs) > CAP:
            capped[d] = (len(rs), CAP)
            rs = rs[:CAP]
        for r in rs:
            url_out.append({
                "Referring Domain / URL": r["Source url"],
                "Target URL": r["Target url"],
                "Anchor Text": r["Anchor"],
                "Anchor Type": anchor_type(r["Anchor"]),
                "Action Recommendation": action,
                "Primary Risk Factor": risk,
                "Confidence Score": conf,
                "Referring Domain": d,
                "Page AScore": r["Page ascore"],
                "External Links": r["External links"],
                "Nofollow": r["Nofollow"],
                "Sponsored": r["Sponsored"],
                "Sitewide": r["Sitewide"],
                "Lost Link": r["Lost link"],
                "First Seen": r["First seen"],
                "Last Seen": r["Last seen"],
            })
    url_out.sort(key=lambda r: (order[r["Action Recommendation"]],
                                r["Referring Domain"]))
    write_csv(f"{outdir}/url_drilldown.csv", URL_COLS, url_out)

    # ---- Google disavow file -------------------------------------------
    dis = sorted(d for d in profiles if verdicts[d][0] == DISAVOW)
    with open(f"{outdir}/disavow.txt", "w", encoding="utf-8") as fh:
        fh.write("# Performance Lab (performancelab.com) - disavow file\n")
        fh.write("# Generated by backlink-audit/audit.py\n")
        fh.write(f"# Source rows: {len(rows):,} | Referring domains: {len(profiles):,}\n")
        fh.write(f"# Domains disavowed: {len(dis):,}\n")
        fh.write("# Search/AI surfaces and affiliate infrastructure are excluded by design.\n#\n")
        by_risk = defaultdict(list)
        for d in dis:
            by_risk[verdicts[d][1]].append(d)
        for risk in sorted(by_risk):
            fh.write(f"\n# --- {risk} ---\n")
            for d in sorted(by_risk[risk]):
                fh.write(f"domain:{d}\n")

    # ---- console summary ------------------------------------------------
    tot = Counter(v[0] for v in verdicts.values())
    links = Counter()
    for d, p in profiles.items():
        links[verdicts[d][0]] += p.n_links
    print(f"Rows parsed              : {len(rows):,}")
    print(f"Referring domains        : {len(profiles):,}")
    print(f"Unique linking pages     : {sum(p.n_pages for p in profiles.values()):,}")
    print()
    print(f"{'ACTION':<24}{'DOMAINS':>9}{'BACKLINKS':>12}{'% LINKS':>10}")
    for a in (DISAVOW, REVIEW, KEEP):
        print(f"{a:<24}{tot[a]:>9,}{links[a]:>12,}{links[a]/len(rows):>9.1%}")
    print()
    print("Top risk factors:")
    rf = Counter(verdicts[d][1] for d in profiles if verdicts[d][0] == DISAVOW)
    for k, n in rf.most_common():
        print(f"  {n:>4} domains  {k}")
    if capped:
        print()
        print(f"NOTE: URL drill-down capped at {CAP} rows/domain for "
              f"{len(capped)} templated domain(s):")
        for d, (n, c) in sorted(capped.items(), key=lambda k: -k[1][0]):
            print(f"  {d}: {n:,} backlinks -> {c} sampled "
                  "(domain-level verdict governs)")
    print()
    # ---- markdown summary ------------------------------------------------
    p1 = [(d, profiles[d]) for d in profiles
          if verdicts[d][0] == DISAVOW and profiles[d].n_follow > 0]
    p1.sort(key=lambda kv: -kv[1].n_follow)
    dis_links = sum(profiles[d].n_links for d in profiles if verdicts[d][0] == DISAVOW)
    dis_follow = sum(profiles[d].n_follow for d in profiles if verdicts[d][0] == DISAVOW)

    with open(f"{outdir}/SUMMARY.md", "w", encoding="utf-8") as fh:
        w = fh.write
        w("# Performance Lab - Backlink Disavow Audit\n\n")
        w(f"- Rows analysed: **{len(rows):,}**\n")
        w(f"- Referring domains (evaluation units): **{len(profiles):,}**\n")
        w(f"- Unique linking pages: **{sum(p.n_pages for p in profiles.values()):,}**\n\n")
        w("## Verdict split\n\n")
        w("| Action | Domains | Backlinks | % of links |\n|---|---:|---:|---:|\n")
        for a in (DISAVOW, REVIEW, KEEP):
            w(f"| {a} | {tot[a]:,} | {links[a]:,} | {links[a]/len(rows):.1%} |\n")
        w(f"\n## Equity exposure\n\n")
        w(f"Of **{dis_links:,}** disavow-flagged backlinks, only "
          f"**{dis_follow:,} ({dis_follow/dis_links:.1%})** are follow links that "
          f"pass equity. The remaining **{dis_links-dis_follow:,}** are nofollow "
          "and pass none.\n\n")
        w("### Priority remediation targets (follow links only)\n\n")
        w("| Domain | Follow links | Risk factor |\n|---|---:|---|\n")
        for d, p in p1:
            w(f"| {d} | {p.n_follow:,} | {verdicts[d][1]} |\n")
        held = [d for d in profiles if d in MANUAL_REVIEW_OVERRIDE]
        if held:
            w("\n## Held for client decision\n\n")
            w("Excluded from the disavow file pending your call. Each carries "
              "the evidence that makes it a judgement rather than a rule.\n\n")
            for d in sorted(held, key=lambda x: -profiles[x].n_links):
                p = profiles[d]
                w(f"**`{d}`** — {p.n_links:,} backlinks "
                  f"({p.n_follow:,} follow). {MANUAL_REVIEW_OVERRIDE[d]}\n\n")

        below = [d for d in profiles
                 if verdicts[d][0] == REVIEW
                 and "below disavow confidence bar" in verdicts[d][1]]
        if below:
            w("## Below the disavow confidence bar\n\n")
            w(f"{len(below)} domain(s) matched a spam rule at Medium or Low "
              "confidence and were routed to review rather than disavowed.\n\n")
            w("| Domain | Backlinks | Follow | Risk factor |\n|---|---:|---:|---|\n")
            for d in sorted(below, key=lambda x: -profiles[x].n_links):
                p = profiles[d]
                w(f"| {d} | {p.n_links:,} | {p.n_follow:,} | "
                  f"{verdicts[d][1].replace(' [below disavow confidence bar]','')} |\n")
            w("\n")

        w("\n## Risk factor breakdown\n\n")
        w("| Risk factor | Domains |\n|---|---:|\n")
        for k, n in rf.most_common():
            w(f"| {k} | {n} |\n")
        if capped:
            w("\n## Sampling disclosure\n\n")
            for d, (n, c) in sorted(capped.items(), key=lambda k: -k[1][0]):
                w(f"- `{d}`: {n:,} backlinks, {c} sampled into the URL "
                  "drill-down. The domain-level verdict governs all rows.\n")

    print(f"Written: {outdir}/domain_audit.csv, url_drilldown.csv, "
          "disavow.txt, SUMMARY.md")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
