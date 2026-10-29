"""
classify.py — assign every referring domain exactly one of the six audit statuses
for superkexpress.com, and type every anchor. Imports load.build().

Client: Super K Express (superkexpress.com) — a trucking / freight / courier carrier
based in Newnan, GA, with a Kansas City, MO operation. Money pages are the deep
/services/<service>-<city>/ and /locations/<city>/ pages.

Three campaigns in this profile (confirmed from the data):
 1. Gambling injection — anchor "jogjatoto" (Indonesian online-gambling brand) and
    kin, pointed at /resources/ from hacked pages. bisicon.com alone = 58,903 links.
    Off-topic spam.
 2. PBN link-blast — keyword-stuffed SEO sales-copy anchors ("build powerful website
    authority with premium seo backlinks ...") pointed at the home page, ~900+ domains.
 3. Commissioned-looking exact-match campaign — the client's own trucking service +
    geography anchors pointed at deep /services/ and /locations/ pages. HELD for the
    previous SEO partner to confirm, never auto-disavowed.

Nothing is disavowed on Authority Score, TLD, or a shared IP alone: every Spam
(Disavow) line rests on a visible spam anchor, spam linking-page title, or spam host.
When in doubt, hold — do not disavow.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import load
from urllib.parse import urlsplit

OWNED = {"superkexpress.com"}   # money site; no redirect/owned domains per client

# Path-based free-hosting platforms: individual sites live on a PATH (angelfire.com/user/),
# not a subdomain, so a root domain: line would disavow the whole (now largely defunct)
# platform. Never disavow these at root; the specific spam URL is disavowed manually.
PATH_PLATFORM = {
    "angelfire.com", "tripod.com", "geocities.com", "geocities.ws", "50megs.com",
    "freeservers.com", "awardspace.com", "t35.com", "20m.com", "freewebsites.com",
    "homestead.com", "webspawner.com", "9f.com", "150m.com",
}

# ---- vocabulary ----
SERVICE_TERMS = [
    "trucking", "truck driving", "truck driver", "truck drivers", "truckload",
    "dry van", "dry van trucking", "dry van freight", "freight hauling", "freight",
    "otr", "over the road", "over-the-road", "regional trucking", "dedicated trucking",
    "dedicated route", "dedicated routes", "local trucking", "long haul", "full load",
    "cross docking", "cross dock", "cross-docking", "warehouse", "warehousing",
    "direct shippers", "direct shipper", "direct trucking", "truck services",
    "trucking service", "trucking services", "trucking company", "trucking companies",
    "trucking jobs", "truck driving jobs", "driving jobs", "lift gate", "lift gates",
    "shippers", "courier", "express delivery", "logistics", "transportation",
    "hauling", "carrier", "freight service", "otr freight", "cdl",
]
GEO_TERMS = [
    "newnan ga", "newnan georgia", "newnan, ga", "newnan", "coweta ga", "coweta",
    "kansas city mo", "kansas city, mo", "kansas city missouri", "kansas city",
    "georgia", "missouri", " ga", " mo",
]
GAMBLING_TERMS = [
    "jogjatoto", "toto", "slot", "gacor", "casino", "judi", "togel", "poker",
    "taruhan", "betting", " bet ", "gambling", "pragmatic", "maxwin", "rtp ",
    "bandar", "sbobet", "pulsa", "situs",
]
PHARMA_ADULT_TERMS = [
    "viagra", "cialis", "pharmacy", "escort", "porn", "sex ", "xxx", "cbd",
    "tramadol", "payday loan",
]
PBN_TERMS = [
    "backlink", "back link", "seo", "pbn", "dofollow", "do-follow", "nofollow service",
    "authority", "da 50", "pa 40", "da50", "link building", "linkbuilding",
    "link-building", "guest post", "guest posting", "ranking", "rank ", "high quality",
    "premium seo", "tiered link", "white hat", "white-hat", "indexation", "citation",
    "massive linkbuilding", "rankexperience", "serp", "domain authority", "high da",
    "web 2.0", "profile backlink", "niche edit", "outreach", "link placement",
    "increase your", "boost your", "improve your ranking", "organic traffic",
]
GENERIC_TERMS = [
    "visit website", "click here", "read more", "learn more", "website", "here",
    "this website", "home", "homepage", "visit site", "view website", "more info",
    "check it out", "link",
]
PR_HOSTS = [
    "prnewswire", "einnews", "openpr", "pressrelease", "pr.com", "prlog", "issuwire",
    "newswire", "pressreleasepoint", "1888pressrelease", "pr-inside", "prfree",
]
SPAM_HOST_SIGNATURES = [
    "backlink", "seo", "dapa", "rankchecker", "directory", "listing", "bookmark",
    "pbn", "linkbuilding", "guestpost", "submit", "indexer", "domainlist",
    "marketplace", "buydomain", "expireddomain", "articlesubmission", "web2",
    "freearticle", "articledirectory", "bizdirectory", "classified",
    # SEO/PBN tool-farm host tokens — unambiguous spam for a trucking carrier's profile
    "serpcheck", "serpchecker", "pacheck", "dacheck", "rankcheck", "rankservice",
    "siterank", "searchrank", "domainrank", "rankflow", "rankpilot", "rankexpress",
    "rankinsight", "seoexpress", "seogrowth", "seomexa", "seofree", "freechecker",
    "linkrivo", "linknexa", "linksnexa", "linksnexa", "growthalliance", "seoexperts",
    "checkerfree", "rankservice", "siterankservice",
    "outrank", "toprank", "rankgrow", "rankvance", "rankbox", "rankzaro", "rankauthority",
    "boosthub", "quickboost", "freshboost", "grandboost", "inboundlink", "websitelink",
    "cleanlink", "link-baron", "linkqira", "linkbaron",
]
CDN_IP_PREFIXES = ("104.21.", "172.67.", "104.18.", "172.64.", "188.114.")  # Cloudflare etc.

def _has(text, terms):
    t = (text or "").lower()
    return any(k in t for k in terms)

def _path(url):
    u = url or ""
    try:
        return urlsplit(u if "://" in u else "http://" + u).path or "/"
    except Exception:
        return "/"

def is_deep_money(url):
    p = _path(url).lower()
    return p.startswith("/services/") or p.startswith("/locations/")

def anchor_type(anchor, source_title=""):
    """Classify a single anchor into the audit's anchor-type vocabulary."""
    a = (anchor or "").strip()
    al = a.lower()
    if a == "" or al in ("<emptyanchor>", "emptyanchor") or al.startswith("icon -"):
        return "Empty/image"
    if _has(al, GAMBLING_TERMS) or _has(al, PHARMA_ADULT_TERMS):
        return "Spam: off topic"
    if _has(al, PBN_TERMS):
        return "Spam: keyword stuffed SEO sales copy"
    has_service = _has(al, SERVICE_TERMS)
    has_geo = _has(al, GEO_TERMS)
    if has_service and has_geo:
        return "Exact match commercial (geo)"
    if has_service:
        return "Exact match commercial"
    # naked URL / branded
    if "superkexpress" in al.replace(" ", ""):
        if al.replace(" ", "") in ("superkexpress.com", "https://superkexpress.com",
                                   "http://superkexpress.com", "www.superkexpress.com",
                                   "superkexpress.com/", "superkexpress.com→"):
            return "Naked URL"
        if re.search(r"https?://|www\.|\.com|\.net|/", al):
            return "Naked URL"
        return "Branded"
    if al in ("super k express", "super k express llc", "superk express"):
        return "Branded"
    if _has(al, GENERIC_TERMS):
        return "Generic"
    if re.match(r"^https?://", al) or re.search(r"\bwww\.", al) or re.match(r"^[a-z0-9.-]+\.(com|net|org|us|co|io|biz|info)\b", al):
        return "Naked URL"
    return "Contextual or other"

SPAM_ANCHOR_TYPES = {"Spam: off topic", "Spam: keyword stuffed SEO sales copy"}
EXACT_TYPES = {"Exact match commercial", "Exact match commercial (geo)"}

def market_of(anchor, links):
    """Geo market label for the Exact Match Anchors tab."""
    text = (anchor or "").lower() + " " + " ".join(_path(l["target_url"]).lower() for l in links)
    if "kansas" in text or "-mo/" in text or " mo" in text or "missouri" in text:
        if "newnan" in text or "-ga/" in text or "georgia" in text:
            return "Georgia + Missouri"
        return "Kansas City, MO"
    if "newnan" in text or "-ga/" in text or "georgia" in text or " ga" in text:
        return "Newnan, GA"
    return "Non-geo"

def site_type(domain, rec):
    dl = domain.lower()
    if _has(dl, ["directory", "listing", "bizdir", "yellow", "local", "spot", "find"]):
        return "Low quality web directory"
    if _has(dl, ["bookmark", "social", "crowd"]):
        return "Social bookmark site"
    if _has(dl, ["blog", "article", "news", "press", "mag", "post"]):
        return "Low quality blog / article site"
    if (rec.get("as") or 0) >= 20:
        return "Established site (review)"
    return "Low quality / PBN site"

def classify_domain(domain, rec):
    """Return (status, reason_evidence, flags dict). First match wins."""
    links = rec["links"]
    anchors = [l["anchor"] for l in links]
    titles = [l.get("source_title", "") for l in links]
    types = [anchor_type(l["anchor"], l.get("source_title", "")) for l in links]
    any_dofollow = rec.get("any_dofollow", False)
    as_ = rec.get("as")
    ip = rec.get("ip", "") or ""

    has_exact = any(t in EXACT_TYPES for t in types)
    has_pbn = "Spam: keyword stuffed SEO sales copy" in types
    has_offtopic = "Spam: off topic" in types
    has_deep = any(is_deep_money(l["target_url"]) for l in links)
    names_client = any(("superkexpress" in (t or "").lower() or "super k express" in (t or "").lower())
                       for t in titles)
    title_has_salescopy = any(_has(t, PBN_TERMS) or _has(t, GAMBLING_TERMS) for t in titles)
    host_is_spam = _has(domain, SPAM_HOST_SIGNATURES)
    spam_title = any(_has(t, PBN_TERMS) or _has(t, GAMBLING_TERMS) or _has(t, PHARMA_ADULT_TERMS) for t in titles)
    spam_url = any(re.search(r"/(domain|backlink|link-?placement|indexation|seo|pbn)", _path(l["source_url"]).lower()) for l in links)

    def spam_status():
        return "Spam (Disavow)" if any_dofollow else "Spam (Nofollow, No Action)"
    def held_status():
        return "Held (Pending Partner)" if any_dofollow else "Held (Nofollow, No Action)"

    # evidence string used by verify.py
    ev = []
    # 1. owned
    if domain in OWNED:
        return "Own Site", "client owned / money site", {}
    # 1b. path-based free-hosting platform root — never disavow the whole platform
    if domain in PATH_PLATFORM:
        return "Keep", "free-hosting platform root; disavow the specific spam URL manually, not the platform", {}
    # 2. genuine high-AS site
    if as_ is not None and as_ >= 20 and not has_offtopic:
        # a genuine site; keep (never disavow a real site on its own link)
        return "Keep", f"genuine site, Authority Score {as_}", {}
    # 3. exact-match AND pbn on same domain -> held (review-level) -> Held (Pending Partner)
    if has_exact and has_pbn:
        return held_status(), "exact-match commercial anchor present alongside SEO sales copy (review)", {"held": True}
    # 4. exact-match commercial OR deep money-page link -> held
    if has_exact or has_deep:
        why = "exact-match commercial anchor" if has_exact else "link points at a deep money page"
        return held_status(), why, {"held": True}
    # 5. press release syndication
    if _has(domain, PR_HOSTS):
        return held_status(), "press-release syndication host", {"held": True}
    # 6. genuine citation: title names client without SEO sales copy
    if names_client and not title_has_salescopy and not host_is_spam:
        return "Keep", "linking page names the client without SEO sales copy (citation/listing)", {}
    # 7. off-topic spam
    if has_offtopic:
        return spam_status(), "off-topic (gambling/pharma) anchor", {"spam": True}
    # 8. PBN sales-copy anchor
    if has_pbn:
        return spam_status(), "keyword-stuffed SEO sales-copy anchor (PBN)", {"spam": True}
    # 9. spam host name
    if host_is_spam:
        return spam_status(), f"spam host-name signature ({domain})", {"spam": True}
    # 10. spam page title / URL
    if spam_title or spam_url:
        return spam_status(), "spam linking-page title or URL template", {"spam": True}
    # 12. otherwise keep (shared-IP rule 11 handled as corroboration in build, never alone)
    return "Keep", "no visible spam evidence", {}

def classify_all(data=None):
    if data is None:
        data = load.build()
    domains = data["domains"]
    results = {}
    for dom, rec in domains.items():
        status, evidence, flags = classify_domain(dom, rec)
        results[dom] = {"status": status, "evidence": evidence, "flags": flags}
    data["classification"] = results
    return data

if __name__ == "__main__":
    data = classify_all()
    from collections import Counter
    c = Counter(v["status"] for v in data["classification"].values())
    print("STATUS COUNTS (domains):")
    for s in load.canon_domain.__doc__ and ["Spam (Disavow)","Spam (Nofollow, No Action)",
              "Held (Pending Partner)","Held (Nofollow, No Action)","Keep","Own Site"]:
        print(f"  {s:32s} {c.get(s,0)}")
    print("  TOTAL", sum(c.values()))
    # how many disavow-bound have visible evidence?
    dis = [(d,v) for d,v in data["classification"].items() if v["status"]=="Spam (Disavow)"]
    print(f"  Spam(Disavow) domains: {len(dis)}; sample evidence:")
    for d,v in dis[:5]:
        print(f"    {d}: {v['evidence']}")
