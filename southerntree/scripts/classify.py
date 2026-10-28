"""
Classifier for the southerntreega.com backlink audit.

Six statuses, no "Review" bucket (playbook section 6). Every verdict rests on
visible link evidence (anchor text, linking-page title, target page, or host
name) -- never on a score, TLD, or IP alone.

Client constants (the only things that change per client):
  CLIENT   = southerntreega.com (money site, tree-service company, Griffin GA)
  OWNED    = {southerntreega.com}  (no known redirect domains; verified against data)
  Vocab    = tree-service terms + Georgia geography (exact-match commercial anchors)

This module is pure logic: it takes normalized per-link / per-domain records and
returns an anchor type or a status. load.py builds those records; build.py calls
these functions.
"""

import re

# --------------------------------------------------------------------------
# Client constants
# --------------------------------------------------------------------------
CLIENT_DOMAIN = "southerntreega.com"
OWNED_DOMAINS = {"southerntreega.com"}          # extend if redirect domains are confirmed
KEEP_AS_THRESHOLD = 20                            # AS/DR >= this => genuine site (playbook rule 2)

# Service / product vocabulary (exact-match commercial anchors)
SERVICE_TERMS = [
    "tree service", "tree services", "tree removal", "tree trimming",
    "tree pruning", "tree cutting", "tree care", "tree health", "tree experts",
    "tree expert", "tree company", "tree surgeon", "stump grinding",
    "stump removal", "stump grinder", "crane tree", "crane service",
    "crane removal", "emergency tree", "land clearing", "lot clearing",
    "brush removal", "deadwood", "cabling", "bracing", "arborist",
    "tree pruning", "tree & stump", "tree and stump", "tree trimming service",
    "pruning", "trimming", "limb removal", "storm damage",
]

# Georgia geography (adds the "(geo)" variant). Core towns from the brief's
# anchors plus the surrounding Spalding / Henry / Coweta county area.
GEO_TERMS = [
    "griffin", "mcdonough", "senoia", "georgia", " ga", "ga ", ", ga", "(ga",
    "hampton", "locust grove", "peachtree city", "newnan", "fayetteville",
    "stockbridge", "jackson", "barnesville", "zebulon", "thomaston",
    "williamson", "concord", "luthersville", "moreland", "grantville",
    "experiment", "sunny side", "orchard hill", "milner", "brooks",
    "spalding", "henry county", "coweta", "fayette",
]

BRAND_TERMS = ["southern tree", "southerntreega", "southern tree solutions"]

# Keyword-stuffed SEO / PBN sales-copy signatures
SPAM_SALES_PHRASES = [
    "seo backlink", "seo backlinks", "backlink", "backlinks", "pbn",
    "dofollow", "nofollow link", "da 50", "pa 40", "da50", "pa40",
    "link building", "link-building", "buy backlink", "authority backlink",
    "white hat", "tiered link", "guest post", "rank first page",
    "first page google", "google fast", "higher rankings", "boost your ranking",
    "domain authority", "link profile", "serp", "search engine ranking",
    "seo service", "seo services", "seo expert", "seo agency", "rank higher",
    "dr improved", "dr from", "increase dr", "ranking fast", "cheap seo",
    "premium seo", "seo authority", "authority links", "high quality backlink",
    "get higher rankings", "expert seo", "link placement", "darksidelinks",
    "t.me/", "telegram", "buy backlinks online", "rankchecker", "backlink service",
]

# Off-topic spam verticals
OFFTOPIC_TERMS = [
    "casino", "gambling", "poker", "slot", "betting", "bet365", "sportsbook",
    "pharma", "viagra", "cialis", "tadalafil", "pills", "escort", "porn",
    "xxx", "adult", "payday", "loan", "forex", "crypto", "bitcoin", "replica",
    "essay writing", "write my essay", "vape", "cbd gummies", "weight loss",
]

# Host-name spam signatures (a signature in the HOST => likely a link-service host)
SPAM_HOST_SIGNATURES = [
    "backlink", "seobacklink", "dofollow", "linkbuilding", "link-building",
    "pbn", "rankchecker", "dapa", "seochecker", "trafficanalysis",
    "domainanalyzer", "dacheck", "checkerbulk", "bulkda", "pagechecker",
    "blogchecker", "profitseo", "profitsurge", "seoservice", "buybacklink",
    "aadomain", "domainlist", "buydomain", "ageddomain", "indexation",
    "webtracking", "trafficbot", "rankbooster", "linkfarm",
    # link-indexer / URL-shortener / SEO-report / PBN-network hosts seen in this profile
    "addurl", "atomizelink", "urls-shortener", "urlshortener", "shortener",
    "seodomains", "freemyip", "goooogla", "byteshort", "seohub", "seolink",
    "linkpro", "ranklab", "blinks.", "linkcentre", "submiturl", "pingmylink",
]

# Auto-generated indexer / stub / PBN linking-page title templates (strong spam signal)
INDEXER_TITLE_PHRASES = [
    "website stats", "domain report", "url shared", "seo domain research",
    "domain research", "directory pages index", "pages index", "web directory",
    "url shortener", "few of top websites", "top billion", "attribution for anchor",
    "blogroll", "ecommerce seo", "seo stack", "digital transformation",
]
# Emoji / pictographic symbols in a title -- these auto-gen spam pages are riddled with them;
# genuine business-directory listings in this profile never use them.
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️←-⇿‼⁉]")

# Directory / bookmarking host signatures (for site-type labelling, not spam on their own)
DIRECTORY_SIGNATURES = [
    "directory", "listing", "listings", "bookmark", "bizlist", "localcenter",
    "findlocal", "business", "bizmark", "yellow", "localbiz", "citylocal",
]
PR_SIGNATURES = [
    "einnews", "pr.com", "prnewswire", "newswire", "openpr", "pressrelease",
    "press-release", "issuewire", "digitaljournal", "xpr-", "gannett",
]

URL_LIKE = re.compile(r"^\s*(https?://)?([a-z0-9][a-z0-9\-]*\.)+[a-z]{2,}(/\S*)?\s*$", re.I)
GENERIC_ANCHORS = {
    "visit website", "visit site", "click here", "read more", "website",
    "this website", "here", "learn more", "view website", "more info",
    "read full article", "continue reading", "link", "homepage", "home page",
    "visit", "go to website", "see more", "www",
}


def _norm(s):
    return (s or "").strip().lower()


def _has_geo(a):
    return any(g in a for g in GEO_TERMS)


def _has_service(a):
    return any(t in a for t in SERVICE_TERMS)


def classify_anchor(anchor, target_url=""):
    """Return one of the nine anchor-type labels used across the workbook."""
    a = _norm(anchor)
    if a == "" :
        return "Empty or image"
    # 1. spam sales copy first (it often embeds the brand/domain, so it must win)
    if any(p in a for p in SPAM_SALES_PHRASES):
        return "Spam: keyword stuffed SEO sales copy"
    # 2. off-topic spam
    if any(t in a for t in OFFTOPIC_TERMS):
        return "Spam: off topic"
    # 3. naked URL / domain
    if URL_LIKE.match(a) and " " not in a.strip():
        return "Naked URL"
    # 4. exact-match commercial (service vocabulary)
    if _has_service(a):
        return "Exact match commercial (geo)" if _has_geo(a) else "Exact match commercial"
    # geo + likely service context but service term missed: treat geo-only commercial
    # 5. branded
    if any(b in a for b in BRAND_TERMS):
        return "Branded"
    # 6. generic
    if a in GENERIC_ANCHORS or a.rstrip("!.") in GENERIC_ANCHORS:
        return "Generic"
    # 7. fallback
    return "Contextual or other"


def is_spam_anchor_type(t):
    return t.startswith("Spam:")


def is_exact_commercial_type(t):
    return t.startswith("Exact match commercial")


def host_is_spam(host):
    h = _norm(host)
    return any(sig in h for sig in SPAM_HOST_SIGNATURES)


def _domain_label(domain):
    d = (domain or "").lower().split("//")[-1].split("/")[0]
    parts = d.split(".")
    return parts[0] if parts else d


def title_is_spam(title, domain=""):
    t = _norm(title)
    if any(p in t for p in SPAM_SALES_PHRASES):
        return True
    if any(o in t for o in OFFTOPIC_TERMS):
        return True
    # domain-marketplace / listing-farm title templates (playbook lesson)
    if re.search(r"(page\s*[\d,]{2,})|(domain list)|(aged domains)|(buy .*backlink)", t):
        return True
    # auto-generated indexer / SEO-report / PBN title templates
    if any(p in t for p in INDEXER_TITLE_PHRASES):
        return True
    if EMOJI_RE.search(title or ""):
        return True
    # directory-submission stub: the linking page's title is just the referring
    # domain's own name (e.g. "Addurl.in", "Acquire.co.in", "Top Billion")
    if domain and t:
        lab = _domain_label(domain)
        norm_t = re.sub(r"[^a-z0-9]", "", t)
        norm_d = re.sub(r"[^a-z0-9]", "", domain.lower())
        if lab and len(norm_t) <= len(norm_d) + 2 and (norm_t == norm_d or norm_t == lab):
            return True
    return False


def title_names_client_cleanly(title):
    """Linking-page title names the client without SEO sales copy => genuine citation."""
    t = _norm(title)
    if not t:
        return False
    names_client = any(b in t for b in BRAND_TERMS) or "southerntreega" in t
    return names_client and not title_is_spam(t)


def site_type_for(host, title, anchor_type):
    """Indicative site-type label for the Exact Match Anchors tab."""
    h = _norm(host)
    t = _norm(title)
    if any(sig in h for sig in PR_SIGNATURES) or "press" in t:
        return "Press release / syndication"
    if any(sig in h for sig in DIRECTORY_SIGNATURES) or "directory" in t or "listing" in t:
        return "Low quality web directory"
    if any(k in h for k in ["bookmark", "pin", "story", "submit"]) or "bookmark" in t:
        return "Social bookmarking site"
    if "guest" in t or "blog" in h or "article" in h or "news" in h:
        return "Guest article or content farm"
    return "Low quality web directory"


def classify_domain(agg):
    """
    Decide the status of one referring domain from its aggregate.

    `agg` is a dict with at least:
      domain            registrable root domain (str)
      owned             bool
      as_score          Authority Score / Domain Rating (float)   -- DR under Ahrefs sourcing
      links             list of link dicts, each with:
                          anchor_type, is_dofollow (bool), target_host, source_host,
                          title, is_pr (bool), target_is_deep (bool)
      any_dofollow      bool  (at least one dofollow link)
    Returns (status, reason).

    Verdict order follows the playbook (first match wins). Nofollow variants are
    applied where a Spam/Held domain has no dofollow link at all.
    """
    links = agg["links"]
    any_dofollow = agg["any_dofollow"]

    def nofollow_variant(base):
        if any_dofollow:
            return base
        if base == "Spam (Disavow)":
            return "Spam (Nofollow, No Action)"
        if base == "Held (Pending Partner)":
            return "Held (Nofollow, No Action)"
        return base

    # 1. owned / redirect
    if agg["owned"]:
        return "Own Site", "Client-owned property"

    has_exact = any(is_exact_commercial_type(l["anchor_type"]) for l in links)
    has_pbn = any(l["anchor_type"] == "Spam: keyword stuffed SEO sales copy" for l in links)
    has_offtopic = any(l["anchor_type"] == "Spam: off topic" for l in links)
    has_deep = any(l.get("target_is_deep") for l in links)
    has_pr = any(l.get("is_pr") for l in links)
    host_spam = host_is_spam(agg["domain"]) or any(host_is_spam(l["source_host"]) for l in links)
    title_spam = any(title_is_spam(l.get("source_title", ""), agg["domain"]) for l in links)
    any_spam_evidence = has_pbn or has_offtopic or host_spam or title_spam

    # 2. genuine high-authority site => Keep -- BUT only when there is no spam
    #    evidence. Ahrefs DR is heavily inflated on PBN/link-farm domains (DR 49-79
    #    on pure spam here), so authority alone must NOT rescue a spammy domain.
    if (agg.get("as_score") is not None and agg["as_score"] >= KEEP_AS_THRESHOLD
            and not any_spam_evidence and not has_exact):
        return "Keep", f"Authority {agg['as_score']:g} >= {KEEP_AS_THRESHOLD} and no spam evidence: genuine site"

    # 3. exact-match AND PBN anchor on same domain => Held (review-level) -> Held (Pending Partner)
    if has_exact and has_pbn:
        return nofollow_variant("Held (Pending Partner)"), \
            "Carries both an exact-match commercial anchor and sales-copy spam"

    # 4. exact-match commercial, OR a link to a deep money page => Held
    if has_exact or has_deep:
        why = "Exact-match commercial anchor" if has_exact else "Links to a deep service/location page"
        return nofollow_variant("Held (Pending Partner)"), why + " -- may be commissioned"

    # 5. press-release syndication host => Held
    if has_pr:
        return nofollow_variant("Held (Pending Partner)"), "Press-release syndication host"

    # 6. title names client without SEO sales copy => Keep (genuine citation / listing)
    if any(title_names_client_cleanly(l.get("source_title", "")) for l in links) and not (has_pbn or has_offtopic):
        return "Keep", "Linking page names the client without SEO sales copy (genuine citation)"

    # 7. off-topic spam
    if has_offtopic:
        return nofollow_variant("Spam (Disavow)"), "Off-topic (casino/pharma/etc.) spam anchor"

    # 8. PBN sales-copy anchor
    if has_pbn:
        return nofollow_variant("Spam (Disavow)"), "Keyword-stuffed SEO sales-copy anchor (PBN/link service)"

    # 9. spam host name
    if host_spam:
        return nofollow_variant("Spam (Disavow)"), "Known link-service / spam host name"

    # 10. spam page title or URL template
    if title_spam:
        return nofollow_variant("Spam (Disavow)"), "Spam linking-page title / domain-marketplace template"

    # 12. otherwise keep
    return "Keep", "No spam evidence found"


if __name__ == "__main__":
    # quick self-check on the known anchors
    tests = [
        "Get Higher Rankings with Expert SEO Backlinks southerntreega.com",
        "tree services in griffin, ga",
        "stump grinding senoia ga",
        "southern tree solutions",
        "visit website",
        "southerntreega.com",
        "join our telegram https://t.me/s/darksidelinks",
        "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service",
        "Crane Tree Removal Griffin GA",
    ]
    for t in tests:
        print(f"{classify_anchor(t)!r:45}  <=  {t}")
