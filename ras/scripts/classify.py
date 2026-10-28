"""Anchor typing + domain status classification for the RAS Systems audit.
Client constants at top; everything else follows the signed-off playbook rules.
"""
from urllib.parse import urlsplit

CLIENT_NAME = "RAS Systems"
MONEY_SITE = "ras-systems.com"
OWNED = {"ras-systems.com", "rasmachines.com", "ras-systems.net", "ras-systems.us"}
# brand tokens that identify a genuine citation naming the client
BRAND_TOKENS = ["ras-systems", "ras systems", "rasmachines", "ras machines", "ras-machines"]

# Deep money pages: product/capability pages (what a commissioned link would target)
DEEP_MONEY_PREFIXES = ("/products/", "/en/products/")

SPAM_MARKERS = [
    "backlink", "pbn", "dofollow", "da 50", "pa 40", "da and dr", "higher da",
    "seo link", "seo backlink", "guest post", "link building", "link profile",
    "citation flow", "rank first page", "search engine ranking", "higher search engine",
    "mass backlinking", "homepage links", "crosslink", "buy backlinks", "link indexing",
    "traffic boost", "masslinker", "seo-link.vip", "seo_", "telegram @", "premium seo",
    "authority backlink", "seo authority", "domain authority", "google ranking",
    "google rankings", "organic visibility", "serp", "qualified visitors", "ranking growth",
    "we improved our site", "gained +", "more monthly leads", "press releases compared",
    "high-quality backlinks", "high quality dofollow", "link placement", "competitive niches",
    "placement reporting", "resource page links", "skyscraper", "tiered link", "grow your business online",
    "strengthen your link", "improve citation", "seoexpress", "indexation",
]
OFFTOPIC_MARKERS = [
    "casino", "poker", "gambling", "betting", " slot", "slots", "pharma", "viagra",
    "cialis", "escort", "porn", "xxx", " sex", "payday", "forex", "replica watch",
    "essay writing", "dissertation", " cbd", "vape", "e-cigarette",
]
# product / service / capability vocabulary (exact-match commercial)
RAS_TERMS = [
    "folding machine", "metal folding", "sheet metal", "panel bender", "panel bending",
    "guillotine", "swing beam", "shear", "forming machine", "swaging", "ventirounder",
    "profilecenter", "multibend", "flexibend", "gigabend", "updownbend", "updowncenter",
    "powercut", "smartcut", "primecut", "turbo2plus", "xlt", "xl center", "ductzipper",
    "ducting machine", "sheet flipper", "giljotiin", "giljot", "plieuse", "metallitöötlu",
    "server rack", "server cabinet", "details and options", "success stories",
    "metal machinery", "metal fabrication", "press brake", "bending machine", "fabrication machinery",
    "sheetflipper", "eurobond", "ducting", "profile center", "multibendcenter",
]
GEO_TERMS = ["usa", "germany", "deutschland", "america", "american", " uk", "canada",
            "saksa", "europe", "u.s.", " us ", "estonia", "eesti"]
GENERIC_ANCHORS = {
    "visit website", "click here", "read more", "contact us", "request a quote",
    "view doc", "visit document", "learn more", "website", "homepage", "here",
    "this website", "view", "... view doc", "... visit document", "icon - external link visit website",
    "visit site", "official website", "more info", "details", "quote",
}

def anchor_type(anchor, is_image=False):
    a = (anchor or "").strip()
    al = a.lower()
    if not a:
        return "Empty or image"
    # spam sales copy
    if any(m in al for m in SPAM_MARKERS):
        return "Spam: keyword stuffed SEO sales copy"
    if any(m in al for m in OFFTOPIC_MARKERS):
        return "Spam: off topic"
    # naked url / bare owned-domain mentions
    stripped = al.replace("https://", "").replace("http://", "").strip().strip("/")
    if al.startswith("http") or al.startswith("www."):
        return "Naked URL"
    if stripped in OWNED or any(stripped == o or stripped.startswith(o + "/") for o in OWNED):
        return "Naked URL"
    # single-token bare domain mention (e.g. "ras-systems.net")
    if len(a.split()) == 1 and any(o in al for o in OWNED):
        return "Naked URL"
    # exact-match commercial (product/service vocabulary)
    if any(t in al for t in RAS_TERMS):
        if any(g in (" " + al + " ") for g in GEO_TERMS):
            return "Exact match commercial (geo)"
        return "Exact match commercial"
    # branded
    if "ras systems" in al or "ras-systems" in al or al in ("ras", "ras llc") \
       or al.startswith("ras systems") or "about ras" in al or al == "ras germany":
        return "Branded"
    # generic
    if al in GENERIC_ANCHORS:
        return "Generic"
    return "Contextual or other"

SPAM_HOST_MARKERS = [
    "backlink", "seo", "pbn", "dapa", "rankchecker", "directory", "listing", "dofollow",
    "linkbuilding", "link-building", "masslinker", "seo-link", "linkk", "ranking",
    "guestpost", "domainmarket", "buydomain", "a-zbusinesses", "bizlisting",
]
SPAM_TITLE_MARKERS = [
    "buy aged domains", "aged domains and backlinks", "domain list page", "where to buy",
    "publish your own backlinks", "pbn", "premium pbn", "link building service",
    "high da backlinks", "dofollow backlinks", "backlinks da", "mass backlinking",
]
PRESS_RELEASE_HOSTS = ["prlog", "pressrelease", "openpr", "einnews", "pr.com", "prfree",
                       "newswire", "prweb", "issuewire", "pressat"]

def target_path(target_url, redirect_url=""):
    u = (target_url or "")
    try:
        p = urlsplit(u if "://" in u else "http://" + u).path or "/"
    except Exception:
        p = "/"
    return p

def is_deep_money(path):
    pl = path.lower()
    return pl.startswith(DEEP_MONEY_PREFIXES) and pl not in DEEP_MONEY_PREFIXES

def title_names_client_clean(title):
    t = (title or "").lower()
    if not t:
        return False
    if not any(b in t for b in BRAND_TOKENS) and "ras systems" not in t:
        return False
    if any(m in t for m in SPAM_MARKERS):
        return False
    return True

def classify_domain(dom, links, ascore, ip=None):
    """links: list of dicts each with anchor_type, nofollow(bool), target_path, title, is_dofollow.
    Returns (status, base, reason)."""
    if dom in OWNED:
        return "Own Site", "Own Site", "client-owned / redirect domain"
    atypes = set(l["atype"] for l in links)
    has_dofollow = any(l["dofollow"] for l in links)
    has_pbn = "Spam: keyword stuffed SEO sales copy" in atypes
    has_offtopic = "Spam: off topic" in atypes
    has_exact = ("Exact match commercial" in atypes) or ("Exact match commercial (geo)" in atypes)
    deep = any(is_deep_money(l["tpath"]) for l in links)
    titles = [l.get("title", "") for l in links]
    host_spam = any(m in dom for m in SPAM_HOST_MARKERS)
    title_spam = any(any(m in (t or "").lower() for m in SPAM_TITLE_MARKERS) for t in titles)
    clean_citation = (not has_pbn and not has_offtopic) and any(title_names_client_clean(t) for t in titles)

    def finish(base):
        if base == "Spam":
            return ("Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"), base
        if base == "Held":
            return ("Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"), base
        return base, base

    # 1 own site handled above
    # 2 AS >= 20 -> Keep
    if ascore is not None and ascore >= 20:
        return (*finish("Keep"), "authority score >= 20 (genuine site)")
    # 3 exact-match AND pbn -> Held
    if has_exact and has_pbn:
        s, b = finish("Held"); return (s, b, "exact-match commercial + PBN anchors on same domain")
    # 4 exact-match OR deep money page -> Held
    if has_exact or deep:
        s, b = finish("Held")
        return (s, b, "exact-match commercial anchor" if has_exact else "links a deep product page")
    # 5 press release host
    if any(h in dom for h in PRESS_RELEASE_HOSTS):
        s, b = finish("Held"); return (s, b, "press-release syndication host")
    # 6 clean citation -> Keep
    if clean_citation:
        return (*finish("Keep"), "linking page title names client without sales copy")
    # 7 off-topic -> Spam
    if has_offtopic:
        s, b = finish("Spam"); return (s, b, "off-topic (casino/pharma/etc.) anchor")
    # 8 pbn sales copy -> Spam
    if has_pbn:
        s, b = finish("Spam"); return (s, b, "PBN / link-selling sales-copy anchor")
    # 9 spam host name
    if host_spam:
        s, b = finish("Spam"); return (s, b, "spam host name (seo/backlink/directory signature)")
    # 10 spam page title / url template
    if title_spam:
        s, b = finish("Spam"); return (s, b, "spam page title template")
    # 12 else Keep
    return (*finish("Keep"), "no spam evidence")
