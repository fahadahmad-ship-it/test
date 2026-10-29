"""Anchor-type and referring-domain status classification for the kbelectric.online audit.
Taxonomy matches the K&K template exactly."""
import re

CLIENT_DOMAIN = "kbelectric.online"
CLIENT_TOKENS = ["kbelectric", "kb electric", "kbelectric.online"]

# ---- Anchor types (match template vocab) ----
T_SPAM = "Spam: keyword stuffed SEO sales copy"
T_NAKED = "Naked URL"
T_EXACT = "Exact match commercial"
T_EXACT_GEO = "Exact match commercial (geo)"
T_GENERIC = "Generic"
T_BRANDED = "Branded"
T_EMPTY = "Empty or image"
T_OTHER = "Contextual or other"

# Oklahoma / KB Electric geo tokens (service area) — word-boundary regex
GEO_RE = re.compile(
    r"\b(oklahoma|okc|tulsa|shawnee|edmond|norman|moore|mustang|yukon|stillwater|tecumseh|"
    r"meeker|seminole|mcloud|bethel acres|earlsboro|newalla|prague|chandler|harrah|choctaw|"
    r"guthrie|el reno|piedmont|blanchard|purcell|noble|midwest city|del city|bethany|"
    r"broken arrow|ok)\b", re.I)

# SEO / link-selling sales-copy signals (strong spam tell)
SPAM_SIGNALS = [
    "backlink", "dofollow", "nofollow link", "pbn", "da 50", "pa 40", "da50", "pa40",
    "domain authority", "domain rating", "trust flow", "citation flow", "link building",
    "link-building", "seo service", "seo services", "rank first", "first page google",
    "page 1 ranking", "page one", "buy backlink", "cheap backlink", "whatsapp", "telegram",
    "niche edit", "guest post service", "tiered link", "serp", "boost ranking",
    "boost your ranking", "rankings for", "white hat", "high quality dofollow",
    "authority backlink", "improve google", "increase traffic", "increase your domain",
    "da/pa", "da pa", "google rank", "rank higher", "outrank", "link juice", "link placement",
    "increase trust", "increase trust flow", "seoexpress", "seo express", "moz da",
    "search engine ranking", "organic traffic", "page five", "page 5",
]

GENERIC_SET = {
    "website", "visit website", "click here", "read more", "learn more", "here", "this site",
    "this website", "view website", "homepage", "home page", "website link", "visit site",
    "www", "link", "visit", "view site", "more", "read more here", "website:", "official website",
    "visit our website", "go to website", "view", "details", "more info", "more information",
}

# Commercial service terms for KB Electric (electrical + sports/commercial lighting)
SERVICE_TERMS = [
    "electric", "electrical", "electrician", "lighting", "light ", "lights", "led",
    "sports lighting", "stadium", "arena", "football field", "tennis court", "basketball court",
    "baseball field", "parking lot", "municipal", "switchgear", "new construction", "contractor",
    "ev charg", "ev charger", "charging station", "panel upgrade", "wiring", "generator",
    "lighting installation", "court lighting", "field lighting", "gear installation",
    "commercial lighting", "industrial", "retrofit", "pole light", "flood light",
]

URLISH = re.compile(r"^(https?://)?(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]+)+(/\S*)?$", re.I)

def _norm(s):
    return (s or "").strip()

def anchor_type(anchor, link_type=""):
    a = _norm(anchor)
    al = a.lower()
    lt = (link_type or "").lower()
    # 1. empty / image
    if a == "" or lt == "image" or al in ("image", "img"):
        return T_EMPTY
    # 2. SEO sales-copy spam (strong signal, wins over everything)
    if any(sig in al for sig in SPAM_SIGNALS):
        return T_SPAM
    # long narrative/testimonial mentioning the client + promo tone = sales copy
    if len(a) > 90 and ("kbelectric" in al or "kb electric" in al):
        return T_SPAM
    # 3. branded (brand name, not a bare URL)
    if ("kb electric" in al) and not URLISH.match(al):
        return T_BRANDED
    # 4. naked URL / brand-as-url
    if URLISH.match(al) or al.replace(" ", "") in ("kbelectric.online", "www.kbelectric.online",
                                                   "kbelectric.online/", "http://kbelectric.online",
                                                   "https://kbelectric.online"):
        return T_NAKED
    # 5. exact-match commercial (geo vs non-geo)
    if any(t in al for t in SERVICE_TERMS):
        if GEO_RE.search(al):
            return T_EXACT_GEO
        return T_EXACT
    # geo-only commercial phrases without an explicit service word but clearly local biz
    # 6. generic
    if al in GENERIC_SET or al.rstrip(":").strip() in GENERIC_SET:
        return T_GENERIC
    if "visit website" in al or al in ("website", "visit"):
        return T_GENERIC
    # 7. everything else
    return T_OTHER


# ---- Domain-level status ----
S_SPAM_DISAVOW = "Spam (Disavow)"
S_SPAM_NOFOLLOW = "Spam (Nofollow, No Action)"
S_HELD_PARTNER = "Held (Pending Partner)"
S_HELD_NOFOLLOW = "Held (Nofollow, No Action)"
S_KEEP = "Keep"
S_OWN = "Own Site"

# Genuine citation / directory / social domains -> Keep
LEGIT_DOMAINS = {
    "yellowpages.com", "superpages.com", "dexknows.com", "procore.com", "downtobid.com",
    "bbb.org", "yelp.com", "mapquest.com", "manta.com", "angi.com", "angieslist.com",
    "houzz.com", "thumbtack.com", "facebook.com", "linkedin.com", "instagram.com",
    "youtube.com", "twitter.com", "x.com", "g.page", "google.com", "bing.com",
    "foursquare.com", "chamberofcommerce.com", "buildzoom.com", "porch.com", "nextdoor.com",
    "indeed.com", "glassdoor.com", "crunchbase.com", "zoominfo.com", "apple.com",
    "pinterest.com", "tiktok.com", "trustpilot.com", "birdeye.com", "alignable.com",
    "electricianslist.com", "homeadvisor.com", "expertise.com", "networx.com", "ziplink.com",
    "mlive.com", "cylex-usa.com", "hotfrog.com", "brownbook.net", "ezlocal.com",
    "elocal.com", "citysquares.com", "sportsvenuecalculator.com",
}

# obvious throwaway / PBN TLDs
SPAM_TLDS = {
    "xyz", "shop", "online", "sbs", "monster", "store", "top", "space", "site", "cv",
    "pro", "click", "live", "buzz", "icu", "cfd", "bond", "sbs", "lol", "quest", "autos",
    "boats", "makeup", "hair", "skin", "beauty", "mom", "rest", "cyou", "work", "fun",
    "pics", "cam", "bio", "wiki", "digital",
}

def domain_tld(domain):
    return domain.rsplit(".", 1)[-1].lower() if "." in domain else ""

def is_throwaway_domain(domain):
    """random-hex/digit domains, pbn farms, junk TLDs."""
    d = domain.lower()
    root = d.split(".")[0]
    tld = domain_tld(d)
    if tld in SPAM_TLDS:
        return True
    # all-digit or long hex-ish root
    if re.fullmatch(r"\d{5,}", root):
        return True
    if re.fullmatch(r"[a-f0-9]{8,}", root):
        return True
    if d.endswith(".pages.dev") or ".pages.dev" in d:
        return True
    return False

def is_client_domain(domain):
    d = domain.lower()
    return "kbelectric" in d.replace("-", "")

KEEP_TRAFFIC_MIN = 30  # a benign-anchor domain must show real organic traffic to be "Keep"

def classify_domain(domain, anchor_types, has_dofollow, has_spam_copy, dr=None, traffic=None,
                    titles=None):
    """Return status string. anchor_types: set of T_* present on this domain."""
    d = domain.lower()
    titles = titles or []
    # 0. own site
    if is_client_domain(d):
        return S_OWN
    tld = domain_tld(d)
    legit = (d in LEGIT_DOMAINS)
    # strong spam indicators
    review_spam_title = any(("seoexpress" in (t or "").lower()
                             or "outrank" in (t or "").lower()
                             or "pbn backlink" in (t or "").lower()
                             or "buy backlink" in (t or "").lower()) for t in titles)
    throwaway = is_throwaway_domain(d)
    # PBN tell: inflated DR with no traffic
    pbn_metric = (dr is not None and traffic is not None and dr >= 20 and traffic == 0 and not legit)
    spammy = has_spam_copy or review_spam_title or (throwaway and not legit)
    commercial = (T_EXACT in anchor_types) or (T_EXACT_GEO in anchor_types)

    # 1. Keep: genuine directory/citation, or benign anchors on a domain with REAL organic traffic
    only_benign = anchor_types.issubset({T_BRANDED, T_GENERIC, T_NAKED, T_EMPTY, T_OTHER})
    real_traffic = (traffic is not None and traffic >= KEEP_TRAFFIC_MIN)
    if legit:
        return S_KEEP
    if only_benign and not spammy and not pbn_metric and tld not in SPAM_TLDS and real_traffic:
        return S_KEEP
    # 2. Held: real commercial anchors, possibly commissioned (checked before spam-by-flood,
    #    but AFTER explicit spam-copy/pbn which set `spammy`)
    if commercial and not spammy and not pbn_metric:
        return S_HELD_PARTNER if has_dofollow else S_HELD_NOFOLLOW
    # 3. Spam: sales-copy, throwaway/PBN domains, or the benign naked/generic flood on junk domains
    return S_SPAM_DISAVOW if has_dofollow else S_SPAM_NOFOLLOW
