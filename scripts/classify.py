"""Backlink anchor-type + referring-domain status classifier.
Reproduces the methodology of the Harbinger Marketing backlink-audit template.

Anchor types: Spam: keyword stuffed SEO sales copy | Naked URL | Exact match commercial |
Exact match commercial (geo) | Generic | Branded | Empty or image | Contextual or other

Statuses: Spam (Disavow) | Spam (Nofollow, No Action) | Held (Pending Partner) |
Held (Nofollow, No Action) | Keep | Own Site
"""
import re

# ---- lexicons -------------------------------------------------------------
SEO_SALES_TERMS = [
    "link building", "backlink", "back link", "pbn", "domain authority", "domain rating",
    "da and dr", "da/dr", " da ", " dr ", " tf ", "trust flow", "citation flow",
    "outrank", "rank higher", "ranking", "serp", "white hat", "guest post",
    "high da", "high quality links", "tiered link", "seo links", "seo authority",
    "boost your", "boost domain", "improve da", "buy backlinks", "link placement",
    "search traffic", "index", "crawl", "dofollow backlinks", "quality backlinks",
    "authority backlinks", "rank your", "first page", "google ranking", "off page seo",
    "link juice", "anchor text", "web 2.0", "profile backlinks", "edu backlinks",
]
GENERIC_TERMS = {
    "visit website", "visit site", "click here", "read more", "learn more", "here",
    "website", "web site", "this website", "view website", "more", "read", "link",
    "visit", "view", "see more", "homepage", "home page", "home", "visit us",
    "go to website", "view profile", "profile", "details", "view details", "this site",
}
# CPA / accounting commercial keywords (services for frickecpa.com)
COMMERCIAL_KW = [
    "cpa", "accountant", "accounting", "bookkeep", "book keeping", "tax ", "taxes",
    "tax preparation", "tax prep", "tax return", "tax planning", "tax service",
    "tax relief", "tax resolution", "payroll", "audit", "auditing", "advisory",
    "financial", "finance", "wealth", "estate planning", "quickbooks", "irs",
    "small business account", "bookkeeper", "controller", "cfo", "consulting",
    "retirement", "accounting firm", "accounting service", "tax consultant",
    "notary", "business valuation", "forensic account", "fractional cfo",
]
# US geo tokens (states + abbreviations + common/Georgia cities)
US_STATES = [
    "alabama","alaska","arizona","arkansas","california","colorado","connecticut",
    "delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa",
    "kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan",
    "minnesota","mississippi","missouri","montana","nebraska","nevada","new hampshire",
    "new jersey","new mexico","new york","north carolina","north dakota","ohio",
    "oklahoma","oregon","pennsylvania","rhode island","south carolina","south dakota",
    "tennessee","texas","utah","vermont","virginia","washington","west virginia",
    "wisconsin","wyoming","usa","u.s.a","united states","america","near me",
]
GEO_CITIES = [
    "atlanta","savannah","augusta","columbus","macon","athens","sandy springs","roswell",
    "albany","marietta","warner robins","valdosta","smyrna","brookhaven","gainesville",
    "newnan","peachtree","alpharetta","griffin","decatur","duluth","kennesaw","lawrenceville",
    "houston","dallas","miami","chicago","phoenix","denver","seattle","boston","orlando",
    "tampa","charlotte","nashville","dublin",  # Dublin GA
]
GEO_ABBR = re.compile(r'\b(ga|al|fl|sc|nc|tn|tx|ca|ny|nj|pa|oh|az|co|wa|va|md|mi|il)\b', re.I)

URL_RE = re.compile(r'^(https?://|www\.)', re.I)
DOMAINY_RE = re.compile(r'^[a-z0-9][a-z0-9\-]*(\.[a-z0-9\-]+)+(/.*)?$', re.I)
# TLDs essentially never used by a legitimate referrer of a US CPA firm; in this
# profile they are the auto-generated PBN / link-spam networks.
SPAMMY_TLD = (".shop", ".top", ".icu", ".xyz", ".store", ".online", ".space",
              ".website", ".site", ".fyi", ".party", ".agency", ".click", ".live",
              ".cloud", ".fun", ".sbs", ".lol", ".cfd", ".bond", ".rest", ".quest",
              ".skin", ".boats", ".autos", ".beauty", ".hair", ".mom", ".pics",
              ".monster", ".buzz", ".wiki", ".cyou", ".makeup", ".motorcycles")
SPAMMY_NAME_BITS = ("seo", "rank", "backlink", "link", "index", "crawl", "serp",
                    "boost", "dofollow", "domainauthority", "trustflow", "dachecker",
                    "webdirectory", "aged-domain", "agedomain", "toplevel",
                    "anchorurl", "bestsite", "seodir", "submiturl", "pingmylink",
                    "indexer", "freedirectory", "linkdir", "bookmark", "ping-")


def _words(s):
    return [w for w in re.split(r'\s+', s.strip()) if w]


def classify_anchor(anchor, brand_tokens, client_domains, link_type=None,
                    is_image=False):
    """Return anchor-type label."""
    if anchor is None or str(anchor).strip() == "":
        return "Empty or image"
    a = str(anchor).strip()
    al = a.lower()
    if is_image or (link_type and str(link_type).lower() == "image"):
        return "Empty or image"

    # Naked URL: the anchor is *just* a bare url/domain (optionally the client's)
    bare = al.rstrip("/")
    if URL_RE.match(a) and len(_words(a)) == 1:
        return "Naked URL"
    if DOMAINY_RE.match(bare) and len(_words(a)) == 1 and " " not in a:
        # a lone domain token
        return "Naked URL"

    # Spam SEO sales copy: jargon present (strong signal, overrides most)
    if any(t in (" " + al + " ") for t in SEO_SALES_TERMS):
        return "Spam: keyword stuffed SEO sales copy"
    # very long marketing sentence that names a domain = spam copy
    if len(_words(a)) >= 9 and (re.search(r'[a-z0-9\-]+\.(com|net|org|co|io|biz)', al)):
        return "Spam: keyword stuffed SEO sales copy"

    # Branded: contains a brand token (name), or decorated brand domain
    if any(bt and bt in al for bt in brand_tokens):
        return "Branded"

    # Generic
    if al in GENERIC_TERMS or al.rstrip(".!") in GENERIC_TERMS:
        return "Generic"

    # Commercial (geo vs non-geo)
    is_commercial = False
    if any(kw in (" " + al + " ") for kw in COMMERCIAL_KW):
        is_commercial = True
    else:
        # short Title-ish service phrase heuristic (2-7 words, not a sentence)
        wds = _words(a)
        if 2 <= len(wds) <= 7 and not a.endswith(('.', '!', '?')) and len(a) <= 60:
            caps = sum(1 for w in wds if w[:1].isupper())
            if caps >= max(2, len(wds) - 1):
                is_commercial = True
    if is_commercial:
        has_geo = (any(g in al for g in GEO_CITIES) or
                   any((" " + st + " ") in (" " + al + " ") or al.endswith(st)
                       for st in US_STATES) or
                   bool(GEO_ABBR.search(a)))
        return "Exact match commercial (geo)" if has_geo else "Exact match commercial"

    return "Contextual or other"


def is_pbn_domain(domain):
    d = (domain or "").lower()
    # abused TLD alone is a sufficient signal in this attack profile
    if d.endswith(SPAMMY_TLD):
        return True
    # SEO/link-spam name signatures on any TLD
    if any(bit in d for bit in SPAMMY_NAME_BITS):
        return True
    return False


# Major legitimate domains that must never be disavowed, even if a scraper/UGC
# page on them happens to carry a spammy anchor.
MAJOR_LEGIT = {
    "google.com", "yahoo.com", "bing.com", "facebook.com", "instagram.com",
    "youtube.com", "linkedin.com", "twitter.com", "x.com", "reddit.com",
    "pinterest.com", "wikipedia.org", "amazon.com", "apple.com", "microsoft.com",
    "tiktok.com", "medium.com", "wordpress.com", "blogspot.com", "tumblr.com",
    "yelp.com", "bbb.org", "glassdoor.com", "yellowpages.com", "manta.com",
    "chamberofcommerce.com", "indeed.com", "mapquest.com", "foursquare.com",
    "gscpa.org", "aicpa.org", "sba.gov", "irs.gov",
}


def _root(d):
    parts = (d or "").lower().split('.')
    return d.lower() if len(parts) < 2 else ".".join(parts[-2:])


COMMERCIAL_TYPES = {"Exact match commercial", "Exact match commercial (geo)"}
SALES_TYPE = "Spam: keyword stuffed SEO sales copy"


def classify_domain_status(*, dominant=None, is_spam_flag=False, pbn=False,
                           has_commercial_anchor=False, dofollow_links=0,
                           as_val=0.0, traffic=0, domain="", client_owned=False):
    """Return (status, in_disavow_flag).

    Driven by the DOMINANT anchor type (the rule the template demonstrates):
      - dominant commercial anchor  -> Held (candidate commissioned placement)
      - dominant SEO-sales-copy     -> Spam (the link-spam / negative-SEO attack)
      - naked URL / branded / etc.  -> Spam only if the domain itself is spammy,
                                       else Held (if commercial present) or Keep
    Guards protect major and strong-legit domains from being disavowed.
    """
    if client_owned:
        return "Own Site", "No"
    d = (domain or "").lower()
    as_val = as_val or 0.0
    traffic = traffic or 0
    has_df = (dofollow_links or 0) > 0
    spammy_domain = bool(is_spam_flag) or pbn

    def held():
        return ("Held (Pending Partner)", "Held") if has_df else ("Held (Nofollow, No Action)", "Held")

    def spam():
        return ("Spam (Disavow)", "Yes") if has_df else ("Spam (Nofollow, No Action)", "No")

    def keep():
        return "Keep", "No"

    # Guard 1: never disavow a major legitimate domain.
    if d in MAJOR_LEGIT or _root(d) in MAJOR_LEGIT:
        return held() if has_commercial_anchor else keep()

    # Decide the base category from the dominant anchor type.
    if dominant in COMMERCIAL_TYPES:
        cat = "HELD"
    elif dominant == SALES_TYPE:
        cat = "SPAM"
    elif dominant == "Naked URL":
        cat = "SPAM" if spammy_domain else ("HELD" if has_commercial_anchor else "KEEP")
    elif dominant in ("Branded", "Generic", "Empty or image", "Contextual or other"):
        if has_commercial_anchor:
            cat = "HELD"
        elif spammy_domain:
            cat = "SPAM"
        else:
            cat = "KEEP"
    else:  # no backlinks pulled / no dominant anchor -> rely on domain spam signals
        cat = "SPAM" if spammy_domain else "KEEP"

    # Guard 2: never AUTO-disavow a strong-legit domain (high authority + real
    # organic traffic); route to Held (if commercial) or Keep for manual review.
    if cat == "SPAM" and as_val >= 40 and traffic >= 2000:
        cat = "HELD" if has_commercial_anchor else "KEEP"

    return {"SPAM": spam(), "HELD": held(), "KEEP": keep()}[cat]


if __name__ == "__main__":
    # ---- self-test structural rules against the K&K template labels ----
    import openpyxl, collections
    wb = openpyxl.load_workbook("template_sample.xlsx", data_only=True)
    ab = wb["All Backlinks"]
    h = [c.value for c in ab[1]]; I = {x: i for i, x in enumerate(h)}
    brand = ["k&k", "k & k", "kandk", "kandkmfg", "kandkmanufacturing", "gaworktrucks"]
    client = ["kandkmfg.com", "kandkmanufacturing.com", "gaworktrucks.com"]
    STRUCT = {"Naked URL", "Generic", "Empty or image",
              "Spam: keyword stuffed SEO sales copy"}
    conf = collections.Counter(); n = 0; hit = 0
    mism = collections.Counter()
    for r in ab.iter_rows(min_row=2, values_only=True):
        gold = r[I['Anchor Type']]; anc = r[I['Anchor Text']]; lt = r[I['Link Type']]
        pred = classify_anchor(anc, brand, client, link_type=lt)
        if gold in STRUCT:
            n += 1
            if pred == gold:
                hit += 1
            else:
                mism[(gold, pred)] += 1
    print(f"Structural anchor-typing accuracy on template: {hit}/{n} = {hit/n:.1%}")
    print("Top mismatches (gold -> pred):")
    for (g, p), c in mism.most_common(8):
        print(f"  {c:5d}  {g}  ->  {p}")
