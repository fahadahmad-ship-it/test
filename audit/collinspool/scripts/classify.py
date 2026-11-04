"""
Classifier for the New Garden backlink audit (playbook section 6).

One status per referring domain, decided from ALL of that domain's links.
Six statuses, no "Review" bucket (AUDIT_FORMAT): anything uncertain is resolved
on its own evidence. Every Spam verdict must rest on visible evidence
(anchor, page title, URL, or host) — never AS, TLD, or IP alone (principle 2).
When in doubt, hold, do not disavow (principle 3).

Client constants (the only per-client part, playbook section 10) are at the top.
"""
import re

# ------------------------------------------------------------------ client
CLIENT_NAME = "Collins Pool Management"
MONEY_DOMAIN = "collinspoolmanagement.com"
OWNED_ROOTS = {"collinspoolmanagement.com"}   # referring domains the client owns
BRAND_TOKENS = ["collins pool", "collinspool"]

# STRONG commercial service vocabulary -> exact-match commercial.
# Collins Pool Management: commercial pool services + lifeguard staffing.
SERVICE_TERMS = [
    "commercial pool", "pool service", "pool repair", "pool maintenance",
    "pool cleaning", "pool opening", "pool closing", "pool contractor",
    "pool compan", "pool management", "pool staffing", "pool monitor",
    "swimming pool", "pool deck", "lifeguard", "lifeguards",
    "lifeguard certification", "lifeguard training", "red cross lifeguard",
]
# geography -> exact-match commercial (geo)
GEO_TERMS = [
    "atlanta", "alpharetta", "marietta", "roswell", "sandy springs",
    "johns creek", "kennesaw", "smyrna", "decatur", "georgia",
    " ga", ", ga", "ga ",
]

# ----------------------------------------------------------- spam signatures
# PBN / link-selling sales copy (anchor or title)
SPAM_SALES = [
    "link building", "backlink", "dofollow", "pbn", "buy backlink",
    "premium backlink", "domain rating", "domain authority", "da 50",
    "pa 40", "rank first page", "first page google", "seo service",
    "seo backlinks", "niche edit", "guest post service", "guest post",
    "boost your google", "boost your ranking", "website authority",
    "rank higher", "aged domain", "link velocity", "high quality dofollow",
    "premium seo", "seo outreach", "raise domain rating", "buy backlinks",
    "premium pbn", "link service", "powerful website authority",
]
# off-topic (gambling / pharma / adult / etc.)
SPAM_OFFTOPIC = [
    "casino", "gambling", "betting", "slot", "poker", "ufabet", "judi",
    "togel", "baccarat", "viagra", "cialis", "pharmacy", "escort", "porn",
    "xxx", "adult", " sex", "replica", "psilocybin", "cbd oil", "vape",
    "crypto casino", "sportsbook", "bet365", "sbobet", "mirror",
]
# spam host-name tokens (host contains)
SPAM_HOST = [
    "backlink", "dofollow", "pbn", "linkbuild", "buybacklink", "rankchecker",
    "seotool", "seosuite", "ranking", "dapa", "aged-domain", "agedomain",
    "toplevel", "domainmarket", "domainwork", "allbacklink", "automationtool",
]
# directory / listing / bookmark host tokens (corroborating, see verdict)
DIR_HOST = [
    "directory", "listing", "bookmark", "submit", "weblink", "weblinx",
    "bizdirect", "localhub", "citylocal", "addbiz", "addbusiness",
]
# spam page-title / URL templates
SPAM_TITLE_URL = [
    "where to buy", "aged domains and backlinks", "domain list page",
    "buy backlinks", "premium pbn", "boost your google rankings",
    "premium backlink building", "link building service",
    "seo outreach backlinks", "/dir/seo-outreach", "/domain/domain/",
    "trusted guest post", "/link-velocity-hub/",
]
# throwaway gTLDs (contributing signal only, never alone)
SPAM_TLDS = {"shop", "space", "website", "site", "store", "online", "link",
             "xyz", "icu", "click", "live", "fun", "cyou", "sbs", "rest"}

GENERIC = {"visit website", "click here", "read more", "website", "visit site",
           "learn more", "here", "more", "visit", "link", "homepage", "home",
           "source", "read more.", "website.", "view website"}


def host_of(url):
    m = re.sub(r"^\w+://", "", (url or "").strip().lower())
    m = m.split("/")[0]
    return m[4:] if m.startswith("www.") else m


# Public-suffix approximation: two-label suffixes where the registrable domain
# is the last THREE labels, plus platform hosts whose subdomain is the real site.
MULTI_SUFFIX = {
    "co.uk","org.uk","me.uk","gov.uk","ac.uk","com.au","net.au","org.au",
    "co.nz","com.br","com.ar","com.mx","co.in","net.in","org.in","co.id",
    "com.tr","co.za","com.sg","com.my","co.jp","com.ua","com.pl","co.il",
    "com.co","com.ph","com.vn","com.hk","com.tw","or.kr","ne.kr","go.kr",
    # platform hosts (registrable site is the subdomain)
    "blogspot.com","wordpress.com","web.app","pages.dev","netlify.app",
    "github.io","firebaseapp.com","weebly.com","wixsite.com","squarespace.com",
    "blogspot.co.id","medium.com","substack.com","shopify.com",
}

def root_of(hostname):
    parts = (hostname or "").split(".")
    if len(parts) < 2:
        return hostname
    last2 = ".".join(parts[-2:])
    last3 = ".".join(parts[-3:]) if len(parts) >= 3 else last2
    if last2 in MULTI_SUFFIX and len(parts) >= 3:
        return last3
    return last2


def _has(text, needles):
    t = (text or "").lower()
    return any(n in t for n in needles)


def anchor_type(anchor, target_url=""):
    a = (anchor or "").strip()
    al = a.lower()
    if a == "" or al in ("", "-"):
        return "Empty or image"
    if "(ссылка" in al or al in ("image", "img") or "источник изображения" in al:
        return "Empty or image"
    if _has(al, SPAM_SALES):
        return "Spam: keyword stuffed SEO sales copy"
    if _has(al, SPAM_OFFTOPIC):
        return "Spam: off topic"
    # naked url / domain (before service, so "newgarden.com" is not exact-match)
    if "newgarden" in al and ("." in al or al.startswith("http")):
        return "Naked URL"
    if al.startswith("http") or re.match(r"^[\w.-]+\.\w{2,}$", al):
        return "Naked URL"
    svc = _has(al, SERVICE_TERMS)
    geo = _has(al, GEO_TERMS)
    brand = _has(al, BRAND_TOKENS)
    # brand name contains "Landscape": brand wins UNLESS a geo token is present
    # (a brand+geo anchor reads as a commissioned local-SEO placement -> exact)
    if brand and not geo:
        return "Branded"
    if svc and geo:
        return "Exact match commercial (geo)"
    if svc:
        return "Exact match commercial"
    if brand:
        return "Branded"
    if al in GENERIC or len(al) <= 4:
        return "Generic"
    return "Contextual or other"


# Real money-page path prefixes (from the Tab-08 target URLs):
# /services/..., /location/..., /positions/... are the commercial money pages.
MONEY_PATH_PREFIXES = ("service", "location", "positions", "commercial-pool",
                       "pool", "lifeguard")
MONEY_HOSTS = ("collinspoolmanagement.com",)

def is_deep_money_page(target_url, redirect_url=""):
    """A link aimed at a deep SERVICE/LOCATION/POSITIONS money page on the site."""
    url = redirect_url or target_url or ""
    h = host_of(url)
    if h not in MONEY_HOSTS:
        return False
    path = re.sub(r"^\w+://[^/]+", "", url).split("?")[0].split("#")[0].strip("/")
    if not path:
        return False
    seg0 = path.split("/")[0]
    return any(seg0.startswith(p) for p in MONEY_PATH_PREFIXES)


def classify_domain(domain, links, authority_score, ip_group_size=0,
                    cdn_ip=False):
    """links: list of dicts with keys
         anchor, target_url, redirect_url, source_url, source_title, nofollow
       Returns dict(status, in_disavow, reason, top_anchor, top_anchor_type,
                    any_dofollow, n_links, exact, pbn).
    Verdict order = playbook section 6; first match wins.
    """
    host = domain.lower()
    root = root_of(host)
    atypes = [anchor_type(l.get("anchor"), l.get("target_url")) for l in links]
    titles = " || ".join((l.get("source_title") or "") for l in links).lower()
    srcurls = " || ".join((l.get("source_url") or "") for l in links).lower()
    anchors = " || ".join((l.get("anchor") or "") for l in links).lower()

    any_dofollow = any(not _truthy(l.get("nofollow")) for l in links)
    exact = any(t.startswith("Exact match") for t in atypes)
    pbn = any(t == "Spam: keyword stuffed SEO sales copy" for t in atypes)
    offtopic = any(t == "Spam: off topic" for t in atypes)
    deep = any(is_deep_money_page(l.get("target_url"), l.get("redirect_url"))
               for l in links)
    names_client_clean = _has(titles, BRAND_TOKENS) and not _has(
        titles, SPAM_SALES) and not pbn and not offtopic
    spam_host = _has(host, SPAM_HOST)
    dir_host = _has(host, DIR_HOST)
    spam_titleurl = _has(titles, SPAM_TITLE_URL) or _has(srcurls, SPAM_TITLE_URL)
    tld = root.rsplit(".", 1)[-1]
    throwaway_tld = tld in SPAM_TLDS

    def finalize(base_status, evidence):
        """Resolve dofollow/nofollow + disavow flag."""
        if base_status == "Spam":
            if any_dofollow:
                return _mk("Spam (Disavow)", "Yes", evidence)
            return _mk("Spam (Nofollow, No Action)", "No", evidence)
        if base_status == "Held":
            if any_dofollow:
                return _mk("Held (Pending Partner)", "Held", evidence)
            return _mk("Held (Nofollow, No Action)", "Held", evidence)
        if base_status == "Keep":
            return _mk("Keep", "No", evidence)
        if base_status == "Own":
            return _mk("Own Site", "No", evidence)

    def _mk(status, indis, evidence):
        top = _top_anchor(links)
        return dict(status=status, in_disavow=indis, reason=evidence,
                    top_anchor=top, top_anchor_type=anchor_type(top),
                    any_dofollow=any_dofollow, n_links=len(links),
                    exact=exact, pbn=pbn)

    # 1. owned / redirect domain
    if root in OWNED_ROOTS:
        return finalize("Own", "client-owned domain")
    # 2. AS >= 20 -> genuine site (Keep)  [but never let obvious spam through:
    #    AS>=20 keep only if no PBN/offtopic anchor evidence on the domain]
    if isinstance(authority_score, (int, float)) and authority_score >= 20 \
            and not pbn and not offtopic and not spam_host:
        return finalize("Keep", f"AS {authority_score} >= 20, no spam evidence")
    # 3. exact-match AND pbn anchor on same domain -> Held (resolve review)
    if exact and pbn:
        return finalize("Held", "exact-match + PBN anchors both present")
    # 4. exact-match anchor OR deep money-page link -> Held
    if exact:
        return finalize("Held", "exact-match commercial/geo anchor")
    if deep:
        return finalize("Held", "link points at a deep money page")
    # 5. press-release syndication host
    if _has(host, ["prnewswire", "prweb", "einpresswire", "openpr",
                   "pressrelease", "issuewire", "newswire"]):
        return finalize("Held", "press-release syndication host")
    # 6. title names client without sales copy -> genuine citation (Keep)
    if names_client_clean:
        return finalize("Keep", "linking page names client, no sales copy")
    # 7. off-topic
    if offtopic:
        return finalize("Spam", "off-topic (gambling/pharma/adult) anchor")
    # 8. PBN sales-copy anchor
    if pbn:
        return finalize("Spam", "PBN / link-selling sales-copy anchor")
    # 9. spam host name
    if spam_host:
        return finalize("Spam", f"spam host name ({host})")
    # 10. spam page title / url template
    if spam_titleurl:
        return finalize("Spam", "spam page title / URL template")
    # 10b. directory/listing host WITH a corroborating signal (not alone)
    if dir_host and (throwaway_tld or spam_titleurl or
                     (isinstance(authority_score, (int, float)) and authority_score <= 3)):
        return finalize("Spam", "directory/listing host + corroborating signal")
    # 11. network /24 host (>=5 of client's refdomains, non-CDN) + other evidence
    if ip_group_size >= 5 and not cdn_ip and (throwaway_tld or spam_host):
        return finalize("Spam", f"shared /24 network host ({ip_group_size}) + evidence")
    # 12. otherwise keep
    return finalize("Keep", "no spam evidence")


def _truthy(v):
    return str(v).strip().lower() in ("true", "1", "yes", "y")


def _top_anchor(links):
    from collections import Counter
    c = Counter((l.get("anchor") or "") for l in links)
    return c.most_common(1)[0][0] if c else ""
