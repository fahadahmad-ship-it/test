"""Shared constants + helpers for the ERTH Products backlink audit.
Only the constants in this block change per client."""
import html, re, datetime
from urllib.parse import urlparse

# ---------------- CLIENT CONSTANTS ----------------
CLIENT_NAME   = "ERTH Products"
MONEY_DOMAIN  = "erthproducts.com"
# Domains the client owns / that 301 into the money site. Detected from Semrush
# redirect_url column (empty => none). Add here if the client confirms others.
OWNED_DOMAINS = set()               # none detected
BRAND_TOKENS  = ["erth products", "erth product", "erthproducts", "erth food"]
GEO_TOKENS    = [" ga", " ga ", "georgia", " in ga", "atlanta"]   # client geography
# Exact-match commercial vocabulary (derived from ERTH deep-page anchors)
PRODUCT_TERMS = [
    "bio retention soil", "bioretention soil", "grass sand", "golf green top dressing",
    "golf course divot mix", "golf divot mix", "divot mix", "compost top dressing",
    "top dressing compost", "topdressing with compost", "top dressing lawn with compost",
    "lawn compost top dressing", "top dressing sand", "sand topdressing", "top dressing",
    "topdressing", "engineered soil", "engineered soils", "engineering fill",
    "structural soil", "leveling sand", "lawn leveling sand", "landscaping sand",
    "lawn top dressing", "lawns topdressing", "erth food", "bulk compost",
    "turf", "divot", "soil blend", "structural soil systems",
]
MONEY_PAGES = ["/products/", "/engineered-soils", "/what-is-erth-food", "/dnn/"]

# ---------------- SPAM PATTERNS (vendor patterns, "Tab 09" equivalent) ----------------
# PBN / link-service SEO sales-copy + guest-post + narrative anchor templates.
# Derived from erthproducts.com's own attack anchors + the K&K reference audit.
PBN_ANCHOR_RE = re.compile(
    r"("
    r"backlink|guest post|niche edit|\bpbn\b|link building|contextual link|"
    r"premium seo|seo authority|complete seo for|on.?page seo|off.?page seo|white hat seo|seo links for|"
    r"\bda\b.{0,6}\btf\b|\bdr\b.{0,6}\bda\b.{0,6}\btf\b|all.?in.?one off|"
    r"boost (domain authority|your? ?(da|dr))|domain authority|high.?dr|\bda \d+|\bpa \d+|"
    r"rank .*(higher|high)|higher google ranking|rankings improve|grow search traffic|"
    r"schema markup|reporting dashboard|local citation|page one|"           # 'covers schema markup...' / 'take <d> to page one'
    r"back when i first launched|felt like no one could find|"              # personal-narrative template
    r"power up |everything .*needs:|we deliver (high|premium|contextual|guest)|"
    r"improve .*(\bda\b|\bdr\b|\btf\b)"
    r")",
    re.I)
# Off-topic spam verticals (incl. exam-dump / essay-mill / replica spam).
OFFTOPIC_RE = re.compile(
    r"\b(casino|slot|gambl|betting|bet365|poker|pharma|viagra|cialis|escort|porn|xxx|"
    r"loan|payday|crypto|forex|replica|vape|cbd gumm|"
    r"vce|exam simulator|exam dumps?|braindump|\bdumps\b|essay writ|write my essay|"
    r"dissertation|term paper)", re.I)
# Spam host-name signatures (SEO/PBN/directory marketplace tokens as substrings).
SPAM_HOST_RE = re.compile(
    r"(backlink|seo|dofollow|rankchecker|ranking|rankvance|ranklab|rankpro|linkpro|"
    r"boosthub|guestpost|nicheedit|pbn|dapa|buybacklink|directory|listing|bookmark|"
    r"submiturl|addurl|webdir|zohodirectory|freeads|classified|dir\d|linkbuild)", re.I)
# Spam page title / URL templates (domain marketplace etc.).
SPAM_TITLE_RE = re.compile(
    r"(where to buy aged domain|domain list page|buy backlinks|aged domains and backlinks|"
    r"expired domains? for sale|domain marketplace|buy expired domain|"
    r"backlink package|backlink service|powerful backlink|outrank anyone|"
    r"top domains|seo resource|no resellers|boost your google ranking|"
    r"high da backlink|seo authority backlink|niche edit)", re.I)
SPAM_URL_RE = re.compile(
    r"(/domain/domain/|/domain-list|/buy-backlink|/aged-domain|/all/\d+/\d+|"
    r"/page/\d{4,}|backlink-service|white-hat-directory|backlink-audit-hub)", re.I)
PRESS_HOST_RE = re.compile(
    r"(pressrelease|prnewswire|einnews|openpr|issuewire|newswire|pr\.com|prlog|"
    r"abnewswire|pressat|pr-?urgent)", re.I)
# Throwaway TLDs favoured by link networks (corroboration only, never on their own).
SPAM_TLDS = {"shop", "xyz", "store", "site", "top", "online", "website", "click",
             "link", "pro", "agency", "icu", "cyou", "sbs", "autos", "bond", "rest",
             "lol", "makeup", "quest", "cfd", "monster", "fun", "live"}
# CDN / shared-infra /24 prefixes to EXCLUDE from the link-network IP test.
CDN_PREFIX_RE = re.compile(
    r"^(104\.1[6-9]|104\.2[0-9]|104\.3[01]|172\.6[4-9]|172\.7[0-9]|162\.159|188\.114|"
    r"108\.162|173\.245|141\.101|103\.2[1-3]|190\.93|197\.234|198\.41|151\.101|"
    r"146\.75|199\.232|192\.0\.6|13\.|52\.|54\.|34\.|35\.|18\.|3\.1)")

def is_numeric_host(domain):
    first = (domain or "").split(".")[0]
    return first.isdigit() and len(first) >= 4

def is_cdn_ip(ip):
    return bool(ip) and bool(CDN_PREFIX_RE.match(ip))

def slash24(ip):
    return ".".join(ip.split(".")[:3]) if ip and ip.count(".") == 3 else ""

def tld(domain):
    return domain.rsplit(".", 1)[-1] if "." in domain else ""

ANCHOR_TYPES = [
    "Spam: keyword stuffed SEO sales copy", "Spam: off topic",
    "Exact match commercial", "Exact match commercial (geo)",
    "Naked URL", "Branded", "Generic", "Empty or image", "Contextual or other",
]
GENERIC_ANCHORS = {"visit website", "click here", "read more", "website", "this website",
                   "learn more", "here", "visit site", "homepage", "home page", "view more"}

# ---------------- HELPERS ----------------
def unescape(s):
    return html.unescape(s) if s else s

def canon_host(u):
    if not u:
        return ""
    u = u.strip()
    if "://" not in u:
        u = "http://" + u
    h = urlparse(u).netloc.lower()
    if h.startswith("www."):
        h = h[4:]
    return h.split(":")[0]

# Shared/public multi-label suffixes: each subdomain is an INDEPENDENT site, so the
# registrable unit (and disavow line) must include one label beyond the suffix. Without
# this, spam subdomains of co.com/us.com/uk.com collapse into one over-broad domain: line.
PUBLIC_SUFFIXES = {
    "co.com", "us.com", "uk.com", "eu.com", "br.com", "de.com", "cn.com", "sa.com",
    "ru.com", "gb.com", "no.com", "qc.com", "se.com", "jpn.com", "gr.com", "hu.com", "it.com",
    "gb.net", "uk.net", "se.net", "in.net", "us.org", "ae.org", "com.bz",
    "co.uk", "org.uk", "me.uk", "com.au", "net.au", "org.au", "co.nz", "co.za",
    "com.br", "co.in", "net.in", "org.in", "com.de", "com.se",
}

def reg_domain(host):
    """Registrable domain, respecting shared public suffixes (so x.co.com stays x.co.com)."""
    if not host:
        return ""
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    last2 = ".".join(parts[-2:])
    last3 = ".".join(parts[-3:])
    if last3 in PUBLIC_SUFFIXES and len(parts) >= 4:
        return ".".join(parts[-4:])
    if last2 in PUBLIC_SUFFIXES:
        return last3
    two = {"co", "com", "org", "net", "gov", "edu", "ac", "gob", "go", "or"}
    if parts[-2] in two and len(parts[-1]) == 2:
        return last3
    return last2

def path_of(u):
    if not u:
        return "/"
    if "://" not in u:
        u = "http://" + u
    return urlparse(u).path or "/"

def is_home(u):
    return path_of(u).rstrip("/") in ("", "/")

def ts_to_date(v):
    """unix seconds or ISO8601 -> datetime.date (or None)."""
    if v is None:
        return None
    v = str(v).strip()
    if not v:
        return None
    if v.isdigit():
        try:
            return datetime.datetime.fromtimestamp(int(v), datetime.timezone.utc).date()
        except Exception:
            return None
    try:
        return datetime.datetime.fromisoformat(v.replace("Z", "+00:00")).date()
    except Exception:
        return None

def read_semrush_csv(path, expect):
    """Unescape entities, split on ';', reject wrong column count (K&K trap)."""
    out, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        header = fh.readline().rstrip("\r\n").split(";")
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            line = unescape(line)
            parts = line.split(";")
            if len(parts) != expect:
                bad += 1
                continue
            out.append(dict(zip(header, parts)))
    return header, out, bad
