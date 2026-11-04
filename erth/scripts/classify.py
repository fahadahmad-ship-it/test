"""Classifier for the erthproducts.com backlink audit.

One status per referring domain, resolved on its own evidence, following the
playbook verdict order (first match wins). Six statuses, no Review buckets.

Metric source: Semrush. AS comes from the refdomains report (domain_ascore).
Ahrefs is used only for link discovery and live-page confirmation, never a metric.
"""
import glob
import sys
from urllib.parse import urlsplit

sys.path.insert(0, "erth/scripts")
from load import load_backlinks, load_refdomains, host_of, registrable

# ----------------------------------------------------------------------------
# CLIENT CONSTANTS (the only things that change per client)
# ----------------------------------------------------------------------------
MONEY_DOMAIN = "erthproducts.com"
# Client-owned domains that 301 into the money site. Fill from the client.
# erthproducts.com itself is always own-site. User confirmed other owned domains
# exist; names pending -> add here and re-run (instant).
OWNED_DOMAINS = {
    "erthproducts.com",
}

AS_GENUINE = 20  # Authority Score >= this => genuine site (Keep), per playbook rule 2

# Exact-match commercial vocabulary (product / service / capability terms)
PRODUCT_TERMS = [
    "top dressing sand", "top dressing compost", "compost top dressing",
    "top dressing lawn", "lawn top dressing", "lawns topdressing", "topdressing",
    "top dressing", "sand topdressing",
    "golf course divot mix", "golf divot mix", "divot mix", "golf green top dressing",
    "erth engineered soils", "engineered soils", "engineered soil", "engineering fill",
    "structural soil", "bio retention soil", "bioretention soil", "erth bio retention",
    "leveling sand", "lawn leveling sand", "leveling mix", "lawn leveling",
    "landscaping sand", "grass sand", "bulk compost", "compost supplier",
    "erth food", "soil blends", "lawn top dressing mix", "golf divot",
    "structural soil systems", "turf recovery", "lawn compost", "golf green",
]
GEO_TERMS = [" in ga", " ga ", "georgia", "in georgia", " ga.", "(ga)", " ga,"]
BRAND_TERMS = ["erth products", "erth product"]

# PBN / link-service sales-copy signatures (keyword-stuffed SEO sales copy)
PBN_PATTERNS = [
    "premium seo backlinks", "high quality dofollow backlinks", "dofollow backlinks",
    "pbn network", "premium pbn", "powerful pbn", "buy backlinks", "backlinks online",
    "niche edit", "link building", "da 50 pa 40", "da 50", "pa 40", "high da",
    "rank first page", "first page google", "tiered link", "white hat seo",
    "seo authority backlinks", "authority backlinks", "boost domain authority",
    "domain authority", "backlinks da", "guest post service", "link juice",
    "citation flow", "trust flow", "seo link", "backlinks for", "seo backlinks",
    "improve rankings", "rankings improve", "search engine performance",
    "link placement", "indexation", "backlink", "da dr", "link velocity",
    "boost organic traffic", "backlink packages", "outrank", "100% safe",
    "safe & powerful", "powerful backlink", "premium backlink", "link packages",
    "link insertion", "profile backlink", "increase trust flow", "high quality links",
    "rank your site", "boost your ranking", "rankings & authority", "serp results",
    "schema markup", "reporting dashboard", "seo stack", "sponsored posts",
    "mortgage seo", "link exchange", "covers schema", "programmatic seo",
]
OFF_TOPIC = [
    "casino", "gambling", "poker", "slot", "roulette", "betting", "escort",
    "porn", "viagra", "cialis", "pharmacy", "pharma", "payday loan", "crypto casino",
    "togel", "pick4d", "4d lottery", "situs", "judi", "exam simulator", "vce exam",
    "exam dumps", "jn0-", "braindump", "pinterest tool", "sitetosocial",
]

# Spam host-name signatures (backlink/seo/marketplace networks)
SPAM_HOST_TOKENS = [
    "backlink", "backling", "baclink", "dofollow", "linkbuilding", "link-building", "pbn",
    "dapa", "dacheck", "drcheck", "rankchecker", "rankingchecker", "siteranking",
    "seocheck", "seoblog", "seolink", "linkseo", "seotool", "seodomains", "seowebsite",
    "web20backlink", "submissiontool", "indexation", "aibacklink", "automatedbacklink",
    "getorganictraffic", "realvisitors", "pageviews", "localtraffic", "trafficbot",
    "24rankings", "agencylinkbuilding", "digitseotools", "backlinkocean", "backlinkindia",
    "backlinkbazaar", "backlinkedu", "naturalbacklink", "freebacklink",
    "rankvance", "keyrush", "skylink", "trafficbooster", "increasewebtraffic",
    "directorylinkservice", "buzzshrink", "atomizelink", "anchorurl", "byteshort",
    "best-seo-domain", "seo-domain", "linkservice", "authoritylink", "rankboost",
    "boostrank", "bulklink", "allbaclink", "algolinkers", "linkpackage", "shorten",
    "seohub", "ranklab", "linkpro", "boosthub", "rankforge", "rank-forge",
    "forge-academy", "bulkda", "dachecker", "pachecker", "growthfront",
    "contentreach", "crawllora", "crawlvexa", "crawlzaro", "cluster-rank",
    "ranklytics", "linkvault", "rankwave", "seostack", "checker", "serpcheck",
    "onlineserp", "scorechecker", "sepchecker",
]
# Spam page-title / URL template signatures (visible evidence on the page)
SPAM_TITLE_TOKENS = [
    "high authority seo backlinks", "professional link building services",
    "powerful pbn backlinks", "high da backlinks", "seo authority backlinks",
    "tiered link building", "guest post service", "domain list page",
    "top domains", "aged domains", "buy backlinks", "link juice", "citation flow",
    "trust flow", "da, dr", "link velocity", "where to buy",
    "website stats", "domain report", "url shared", "web directory",
    "directory pages index", "directory link service", "domains on ip",
    "any seo resource", "seo resource", "no resellers", "seo domains",
    "domains for sale", "backlink packages", "white hat seo links",
    "boost domain authority", "boost organic traffic", "outrank anyone",
    "make ai recommend", "100% safe", "link building service",
    "grow your website traffic", "powerful white hat", "safe & powerful backlink",
    "high quality dofollow", "powerful backlinks", "premium backlinks",
    "wisconsin parade", "digital transformation, drive your",
]
SPAM_URL_TOKENS = [
    "/dir/backlinks-for-business", "/domain/domain/part", "/link-placement-hub",
    "/tiered-link-archive", "/ranking-resources", "/indexation-directory",
    "/link-juice-directory", "/best-for-ranking", "backlinks-for-business",
    "domain-list", "aged-domain", "/link-building", "/guest-post",
]


def _l(s):
    return (s or "").strip().lower()


def is_pbn(anchor, title, url):
    a, t, u = _l(anchor), _l(title), _l(url)
    if any(p in a for p in PBN_PATTERNS):
        return True
    if any(p in t for p in SPAM_TITLE_TOKENS):
        return True
    if any(p in u for p in SPAM_URL_TOKENS):
        return True
    return False


def is_off_topic(anchor, title, host):
    blob = _l(anchor) + " " + _l(title) + " " + _l(host)
    return any(k in blob for k in OFF_TOPIC)


def is_geo(anchor):
    return any(g in _l(anchor) for g in GEO_TERMS)


def is_exact_match(anchor):
    a = _l(anchor)
    if any(p in a for p in PBN_PATTERNS):
        return False
    return any(term in a for term in PRODUCT_TERMS)


def is_branded(anchor):
    a = _l(anchor)
    if "backlink" in a or "seo" in a:
        return False
    return any(b in a for b in BRAND_TERMS)


def is_naked(anchor):
    a = _l(anchor).replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    return a in (MONEY_DOMAIN, "erthproducts.com") or a.startswith("erthproducts.com")


def is_empty(anchor):
    a = _l(anchor)
    return a in ("", "<emptyanchor>", "emptyanchor", "image")


GENERIC_TERMS = ["visit website", "click here", "read more", "website", "learn more",
                 "here", "this site", "homepage", "home page", "view website"]


def is_generic(anchor):
    return _l(anchor) in GENERIC_TERMS or _l(anchor) in ("website",)


def anchor_type(anchor, title, url, host):
    """Return one of the 8 template anchor types for a single link."""
    if is_empty(anchor):
        return "Empty or image"
    if is_off_topic(anchor, title, host):
        return "Spam: keyword stuffed SEO sales copy"  # off-topic folds into spam copy bucket if no separate col
    if is_pbn(anchor, title, url):
        return "Spam: keyword stuffed SEO sales copy"
    if is_naked(anchor):
        return "Naked URL"
    if is_branded(anchor):
        return "Branded"
    if is_exact_match(anchor):
        return "Exact match commercial (geo)" if is_geo(anchor) else "Exact match commercial"
    if is_generic(anchor):
        return "Generic"
    return "Contextual or other"


def deep_page(target_url):
    """True if the link points at a deep product/capability/industry page, not home."""
    p = urlsplit(target_url if "//" in target_url else "http://" + target_url).path.rstrip("/")
    p = p.strip().rstrip("%20").rstrip()
    if p in ("", "/"):
        return False
    low = p.lower()
    # treat product/capability/industry pages as deep money pages
    return any(k in low for k in ["/products/", "/product/", "engineered-soil",
                                  "/what-is", "/dnn/", "/services", "/industries"]) or low.count("/") >= 1


def spam_host(host):
    h = host.lower()
    if any(tok in h for tok in SPAM_HOST_TOKENS):
        return True
    # auto-generated domains: the registrable label is all digits (e.g. 11763813.xyz,
    # 37486399.xyz) -- a visible machine-generated signature, not a vendor flag.
    label = h.split(".")[0]
    if label.isdigit() and len(label) >= 6:
        return True
    return False


# ----------------------------------------------------------------------------
# Aggregate links by registrable referring domain and classify
# ----------------------------------------------------------------------------
def build_domain_records(bl):
    by = {}
    for r in bl:
        host = host_of(r["source_url"])
        root = registrable(host)
        d = by.setdefault(root, {
            "domain": root, "hosts": set(), "links": [], "anchors": set(),
            "first_seen": None, "any_dofollow": False, "all_nofollow": True,
        })
        d["hosts"].add(host)
        d["links"].append(r)
        d["anchors"].add(r["anchor"])
        nf = _l(r["nofollow"]) == "true"
        if not nf:
            d["any_dofollow"] = True
            d["all_nofollow"] = False
        fs = r["first_seen"]
        try:
            fsi = int(fs)
            if d["first_seen"] is None or fsi < d["first_seen"]:
                d["first_seen"] = fsi
        except (ValueError, TypeError):
            pass
    return by


def classify_domain(d):
    """Return (base_verdict, evidence) where base_verdict in
    {Own Site, Keep, Held, Spam}. Dofollow split applied by caller."""
    root = d["domain"]
    links = d["links"]

    def _a(r):
        return r.get("anchor", "")

    def _t(r):
        return r.get("title", r.get("source_title", "")) or ""

    def _u(r):
        return r.get("url_from", r.get("source_url", "")) or ""

    def _tg(r):
        return r.get("target", r.get("target_url", "")) or ""

    # link-level signals
    has_pbn = False
    has_exact = False
    has_deep = False
    has_offtopic = False
    names_client_clean = False  # title names client without sales copy
    for r in links:
        a, t, u = _a(r), _t(r), _u(r)
        if is_pbn(a, t, u):
            has_pbn = True
        if is_exact_match(a):
            has_exact = True
        if deep_page(_tg(r)) and not is_pbn(a, t, u):
            has_deep = True
        if is_off_topic(a, t, host_of(u)):
            has_offtopic = True
        tl = _l(t)
        if ("erth" in tl or "erthproducts" in tl) and not is_pbn(a, t, u) \
                and not any(x in tl for x in SPAM_TITLE_TOKENS):
            names_client_clean = True
    # commercial-category directory placement: the linking page TITLE carries the
    # client's product term + geography (e.g. "Compost Supplier GA - <site>") while
    # the anchor is naked/branded. A coordinated directory network, commissioned-
    # looking -> Held for the partner, not treated as a genuine citation.
    has_title_commercial_geo = False
    for r in links:
        t = _l(_t(r))
        if not t or "erth" in t or is_pbn(_a(r), _t(r), _u(r)):
            continue
        if any(term in t for term in PRODUCT_TERMS) and any(g in t for g in GEO_TERMS):
            has_title_commercial_geo = True

    host_spam = any(spam_host(h) for h in d["hosts"])
    title_spam = any(any(x in _l(_t(r)) for x in SPAM_TITLE_TOKENS) for r in links)
    url_spam = any(any(x in _l(_u(r)) for x in SPAM_URL_TOKENS) for r in links)

    # ---- verdict order (first match wins) ----
    # 1. owned / redirect
    if root in OWNED_DOMAINS or root == MONEY_DOMAIN:
        return "Own Site", "client-owned / redirect domain"
    # 2. genuine high-authority site
    if d.get("ascore") is not None and d["ascore"] >= AS_GENUINE and not (host_spam or title_spam or url_spam):
        return "Keep", f"Authority Score {d['ascore']} >= {AS_GENUINE}"
    # 3. exact-match AND pbn on same domain -> held (review-level)
    if has_exact and has_pbn:
        return "Held", "exact-match commercial + PBN anchor on same domain (review)"
    # 4. exact-match OR deep money-page link OR commercial-category directory -> held
    if has_exact or has_deep or has_title_commercial_geo:
        why = []
        if has_exact:
            why.append("exact-match commercial anchor")
        if has_deep:
            why.append("link to deep product page")
        if has_title_commercial_geo:
            why.append("commercial-category directory listing (product + geo in page title)")
        return "Held", " / ".join(why)
    # 6. title names client cleanly -> keep (genuine citation) -- checked before spam-copy
    if names_client_clean and not (has_pbn or host_spam or title_spam or url_spam):
        return "Keep", "linking page names the client without SEO sales copy (citation)"
    # 7. off-topic
    if has_offtopic:
        return "Spam", "off-topic (casino/pharma/etc.) anchor or host"
    # 8-10. pbn sales copy / spam host / spam title / spam url
    ev = []
    if has_pbn:
        ev.append("PBN sales-copy anchor")
    if title_spam:
        ev.append("spam page title")
    if url_spam:
        ev.append("spam URL template")
    if host_spam:
        ev.append("spam host name")
    if ev:
        return "Spam", "; ".join(ev)
    # 12. otherwise keep
    return "Keep", "no spam evidence"


def final_status(base, any_dofollow):
    if base in ("Own Site", "Keep"):
        return base
    if base == "Held":
        return "Held (Pending Partner)" if any_dofollow else "Held (Nofollow, No Action)"
    if base == "Spam":
        return "Spam (Disavow)" if any_dofollow else "Spam (Nofollow, No Action)"
    return base


if __name__ == "__main__":
    import collections
    bl, _ = load_backlinks(sorted(glob.glob("erth/data/fetch/bl_p*.csv")))
    rd, _ = load_refdomains(sorted(glob.glob("erth/data/rd/rd_p*.csv")))
    as_by = {}
    for r in rd:
        root = registrable(host_of(r["domain"]))
        try:
            asc = int(r.get("domain_ascore") or 0)
        except ValueError:
            asc = 0
        # keep the max AS seen for a root
        as_by[root] = max(as_by.get(root, 0), asc)

    by = build_domain_records(bl)
    for root, d in by.items():
        d["ascore"] = as_by.get(root)
    counts = collections.Counter()
    base_counts = collections.Counter()
    for root, d in by.items():
        base, ev = classify_domain(d)
        d["base"], d["evidence"] = base, ev
        st = final_status(base, d["any_dofollow"])
        d["status"] = st
        counts[st] += 1
        base_counts[base] += 1
    print("domains classified:", len(by))
    print("\nBASE verdicts:", dict(base_counts))
    print("\nFINAL statuses:")
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")
