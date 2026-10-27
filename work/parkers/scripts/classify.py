"""
classify.py — status classifier for the parkersair.com backlink audit.

Six statuses, no "Review" buckets (playbook section 6). First match wins, per domain.
Nothing is disavowed on Authority Score, TLD, or shared IP alone: every Spam (Disavow)
row carries visible evidence (a spam anchor, a spam title/URL, or a spam host name).

Client: Parker's Heating & Air Conditioning Inc. (parkersair.com) — HVAC contractor,
Cordele / Leesburg, Georgia.
"""
import re
from collections import defaultdict

CLIENT_DOMAIN = "parkersair.com"
OWNED_DOMAINS = {CLIENT_DOMAIN}  # extended at runtime with any detected redirect hosts

# ---- vocabulary -----------------------------------------------------------
SERVICE_TERMS = [
    "hvac", "air conditioning", "air-conditioning", "air conditioner", "a/c ", "ac repair", "ac unit", "ac install",
    "ac service", "heating", "furnace", "heat pump", "cooling", "thermostat",
    "attic insulation", "blown in insulation", "blown-in insulation", "insulation",
    "duct sealing", "duct leak", "duct leakage", "air duct", "ductwork",
    "hvac repair", "hvac service", "hvac contractor", "hvac installation",
    "air conditioning repair", "air conditioning service", "air conditioning installation",
    "heating and air", "heating & air", "heating repair",
]
GEO_TERMS = [
    "cordele", "leesburg", "americus", "dawson", "calvary", "bronwood", "albany",
    "sylvester", "tifton", "ashburn", "georgia", " ga", ", ga", " ga ", "ga.",
]
BRAND_TERMS = ["parker"]

# PBN / link-service keyword-stuffed sales copy
PBN_KW = [
    "link building", "link-building", "backlink", "back link", "pbn", "buy backlinks",
    "niche edit", "guest post", "tiered link", "tier link", "white hat seo", "seo link",
    "seo service", "seo expert", "seo authority", "domain authority", "domain rating",
    "rank higher", "rank first page", "first page google", "serp", "da 50", "pa 40",
    "da/pa", "dr score", "citation flow", "trust flow", "outrank your competitor",
    "premium seo", "dofollow backlinks", "link placement", "link juice", "rank your",
    "boost domain", "boost your ranking", "higher rankings", "search traffic", "aged domain",
    "darksidelinks", "t.me/s/", "telegram", "cheap", "google fast", "link velocity",
    "powerful pbn", "authority backlinks", "grow your business online",
]
OFFTOPIC_KW = [
    "casino", "gambling", "betting", "poker", "slot", "roulette", "baccarat", "togel",
    "judi", "bandar", "sbobet", "viagra", "cialis", "pharma", "pill", "escort", "porn",
    "sex", "xxx", "adult", "nude", "loan", "payday", "forex", "crypto", "bitcoin casino",
    "replica watch", "vape", "cbd", "weed", "essay writing", "write my essay",
]
GENERIC_KW = [
    "visit website", "website", "click here", "read more", "learn more", "see more",
    "this site", "this website", "homepage", "home page", "see special offers",
    "special offers", "view website", "go to website", "link", "more info",
]
# spam host-name signatures (known link-tool / url-shortener / domain-stats infrastructure)
SPAM_HOST_KW = [
    "backlink", "buybacklink", "seolink", "linkbuild", "pbn", "dapa", "rankchecker",
    "rank-checker", "domainlist", "domainmarket", "directory", "listing", "seo-", "-seo",
    "aalaa", "linkfarm", "cheapseo", "linkplacement", "linkhub", "boostrank", "topseo",
    "anchorurl", "atomizelink", "buzzshrink", "byteshort", "shortenurl", "shorturl",
    "webranksite", "websitescrawl", "domraider", "domaineye", "goooogla", "linksnatcher",
    "getwebsiteworth", "bestwebstats", "domainanalysis", "websiteworth", "seostats",
]
# spam page title / URL template signatures (auto-generated SEO / domain-marketplace /
# stats / crawler / url-shortener pages — visible evidence per playbook rule 10)
SPAM_TITLE_URL = [
    "powerful pbn backlinks", "where to buy", "domain list page", "aged domains",
    "buy backlinks", "link placement", "link-placement-hub", "/domain/", "buy aged",
    "/link/", "tiered link building", "citation flow", "safe link velocity",
    "outrank your competitors", "high quality tiered link", "/pbn", "backlinks to improve",
    "website stats", "url shared", "domain report", "directory pages index",
    "top domains", "any seo resource", "seo.domains", "seo domain", "websites spidered",
    "spidered today", "few of top websites", "websitescrawl", "domaineye",
    "showcase your business online", "domain worth", "website worth", "estimated worth",
    "web stats", "domain stats",
]
PRESS_RELEASE_HOSTS = [
    "prnewswire", "einnews", "openpr", "pr.com", "pressrelease", "prweb", "newswire",
    "issuewire", "accesswire", "digitaljournal", "benzinga", "marketersmedia",
]

NAKED_URL_FORMS = {
    "parkersair.com", "www.parkersair.com", "http://parkersair.com",
    "https://parkersair.com", "http://www.parkersair.com", "https://www.parkersair.com",
    "parkersair.com/", "https://parkersair.com/", "http://parkersair.com/",
}


def _has(text, needles):
    t = text.lower()
    return any(n in t for n in needles)


def anchor_type(anchor):
    a = (anchor or "").strip().lower()
    if a == "" or a == "<emptyanchor>" or a == "<empty anchor>":
        return "Empty or image"
    if _has(a, OFFTOPIC_KW):
        return "Spam: off topic"
    if _has(a, PBN_KW):
        return "Spam: keyword stuffed SEO sales copy"
    if a in NAKED_URL_FORMS or re.fullmatch(r"https?://(www\.)?parkersair\.com/?", a):
        return "Naked URL"
    if "parkersair" in a and ("http" in a or a.endswith(".com")):
        return "Naked URL"
    # Branded: company name present, not a pure service+geo phrase
    if _has(a, BRAND_TERMS):
        return "Branded"
    if _has(a, SERVICE_TERMS):
        if _has(a, GEO_TERMS):
            return "Exact match commercial (geo)"
        return "Exact match commercial"
    if _has(a, GENERIC_KW):
        return "Generic"
    return "Contextual or other"


def _deep_page(target_url):
    """True if the link points at a deep money page rather than the home page."""
    from urllib.parse import urlsplit
    try:
        p = urlsplit(target_url if "://" in target_url else "http://" + target_url).path
    except Exception:
        return False
    p = p.strip("/")
    return len(p) > 0 and p.lower() not in ("index.html", "index.php", "home")


def classify_domain(domain, links, refdom_meta):
    """links: list of backlink dicts for this domain. Returns (status, anchor_types,
    evidence, flags)."""
    as_score = refdom_meta.get("domain_authority_score_i", 0)
    page_as = max([l["page_as"] for l in links], default=0)
    eff_as = as_score if as_score else page_as

    types = [anchor_type(l["anchor"]) for l in links]
    tset = set(types)
    any_dofollow = any(not l["is_nofollow"] for l in links)
    all_nofollow = not any_dofollow

    has_pbn = "Spam: keyword stuffed SEO sales copy" in tset
    has_offtopic = "Spam: off topic" in tset
    has_exact = ("Exact match commercial" in tset) or ("Exact match commercial (geo)" in tset)
    points_deep = any(_deep_page(l["target_url"]) for l in links
                      if anchor_type(l["anchor"]) in (
                          "Exact match commercial", "Exact match commercial (geo)",
                          "Branded", "Generic", "Naked URL"))

    host = domain.lower()
    spam_host = _has(host, SPAM_HOST_KW)
    is_press = _has(host, PRESS_RELEASE_HOSTS)
    spam_title_url = any(_has(l["source_title"], SPAM_TITLE_URL) or
                         _has(l["source_url"], SPAM_TITLE_URL) for l in links)
    title_names_client_clean = any(
        ("parker" in l["source_title"].lower()) for l in links
    ) and not (has_pbn or has_offtopic)

    def held(reason):
        st = "Held (Pending Partner)" if any_dofollow else "Held (Nofollow, No Action)"
        return st, reason

    def spam(reason):
        st = "Spam (Disavow)" if any_dofollow else "Spam (Nofollow, No Action)"
        return st, reason

    # ---- verdict order (playbook section 6) ----
    if host in OWNED_DOMAINS or host == CLIENT_DOMAIN:
        return "Own Site", types, "Client-owned / redirect property", locals()
    # genuine high-authority site (guard against obvious spam hosts / offtopic dofollow)
    if eff_as >= 20 and not spam_host and not (has_offtopic and any_dofollow) and not (has_pbn and any_dofollow):
        return "Keep", types, f"Authority Score {eff_as} (genuine site)", locals()
    if has_exact and has_pbn:
        st, r = held("Exact-match commercial anchor alongside PBN sales copy (review-level)")
        return st, types, r, locals()
    if has_exact or points_deep:
        why = "Exact-match commercial anchor" if has_exact else "Link points at a deep money page"
        st, r = held(why)
        return st, types, r, locals()
    if is_press:
        st, r = held("Press-release syndication host")
        return st, types, r, locals()
    if title_names_client_clean:
        return "Keep", types, "Linking-page title names the client without SEO sales copy", locals()
    if has_offtopic:
        ex = next((l["anchor"] for l in links if anchor_type(l["anchor"]) == "Spam: off topic"), "")
        st, r = spam(f"Off-topic spam anchor: {ex[:80]}")
        return st, types, r, locals()
    if has_pbn:
        ex = next((l["anchor"] for l in links if anchor_type(l["anchor"]) == "Spam: keyword stuffed SEO sales copy"), "")
        st, r = spam(f"PBN sales-copy anchor: {ex[:90]}")
        return st, types, r, locals()
    if spam_host:
        st, r = spam(f"Spam host name: {host}")
        return st, types, r, locals()
    if spam_title_url:
        ex = next((l["source_title"] for l in links if _has(l["source_title"], SPAM_TITLE_URL)
                   or _has(l["source_url"], SPAM_TITLE_URL)), "")
        st, r = spam(f"Spam page title/URL: {ex[:80]}")
        return st, types, r, locals()
    # otherwise
    return "Keep", types, "Genuine or harmless", locals()
