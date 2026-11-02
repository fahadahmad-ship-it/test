"""Per-client constants for the Ritter Consulting Engineers backlink audit.
Only these change between clients; the format, status set, evidence rules and
verification do not. See BACKLINK_AUDIT_PLAYBOOK.md Section 10.
"""

CLIENT_NAME = "Ritter Consulting Engineers"
MONEY_DOMAIN = "ritterconsultingengineers.com"

# Domains the client owns that 301-redirect into the money site.
# Confirmed with client: none. Single Search Console property, single file.
OWNED_DOMAINS = set()

# Who confirms the held links. The sheet always says "partner"; the Ritter brief
# calls the role "previous supplier". We tie the two together once, in the
# disavow-file header, and never rename the column. (Playbook Section 10.)
CONFIRMER_WORD = "supplier"

# Search Console upload reality. Client answered "not sure yet" -> default to the
# single money-site file and say in the header it is the only one to submit.
SINGLE_FILE_ONLY = True

# ---- Exact-match commercial vocabulary (drives the HELD verdict) --------------
# Ritter's service vocabulary, taken from the live anchor profile (Semrush
# backlinks_anchors) and the site's /service/ pages.
SERVICE_TERMS = [
    "asbestos",            # survey, inspection, testing, abatement, clearance, inspector
    "mold",                # testing, inspection, remediation, removal, inspectors
    "plumbing design",
    "mechanical engineering",
    "mechanical & environmental",
    "hvac design",
    "commercial hvac",
    "fire sprinkler design",
    "fire sprinkler",
    "deq testing",
    "deq inspection",
    "deq",
    "lead paint inspection",
    "lead based paint",
    "lead paint",
    "air quality",
    "indoor air",
    "environmental consulting",
    "environmental consultant",
]

# Geography that makes an exact-match anchor a (geo) anchor.
GEO_TERMS = ["louisiana"]  # primary market; "la" is too short to match safely

# ---- Brand vocabulary --------------------------------------------------------
BRAND_TERMS = [
    "ritter consulting engineers",
    "ritter consulting",
    "ritterconsultingengineers",
]

# ---- Spam: keyword-stuffed SEO sales copy (PBN / link-service template) -------
# Any anchor OR linking-page title containing one of these is PBN sales copy.
PBN_ANCHOR_SIGNALS = [
    "link building", "backlink", "back link", "dofollow", "do follow",
    "pbn", "domain authority", "domain rating", "da 50", "pa 40", "da50", "pa40",
    "seo link", "seo service", "seo authority", "buy backlinks", "buying backlinks",
    "rank first page", "first page google", "white hat seo", "tiered link",
    "premium link", "raise domain rating", "increase your domain authority",
    "google rankings", "better rankings", "high quality dofollow",
    "guest post", "guest posting", "link placement", "niche edit",
    "whatsapp us", "t.me/", "telegram", "join our telegram", "our telegram",
    "sitetosocial", "grow your website traffic", "increase your domain",
    "experienced a 150% growth", "proven dofollow", "authority backlinks",
    "link building experts", "link building services",
]

# ---- Spam: off-topic (casino/pharma/adult/etc.) ------------------------------
OFFTOPIC_SIGNALS = [
    "casino", "gambling", "betting", "poker", "slot", "roulette", "baccarat",
    "viagra", "cialis", "pharma", "pharmacy", "tadalafil", "sildenafil",
    "escort", "porn", "sex", "adult", "xxx", "crypto", "forex", "bitcoin",
    "replica", "vape", "cbd gummies",
]

# ---- Spam host-name signatures ----------------------------------------------
SPAM_HOST_SIGNALS = [
    "backlink", "dofollow", "rankchecker", "seobacklink", "linkbuilding",
    "buybacklink", "pbn", "dapa", "da-pa", "seolink", "linkseller",
]

# ---- Spam page-title / URL templates (domain-marketplace / tool-page sigs) ----
# Each token below is a visible spam-template page title observed on Ritter's
# profile, shared across multiple referring domains (domain-marketplace, aged-
# domain seller, reverse-IP/stat tool, URL-shortener, auto-directory, or an
# off-topic content-farm article unrelated to an engineering firm). These are
# evidence you can see on the page, not an Authority-Score or TLD guess.
SPAM_TITLE_SIGNALS = [
    "where to buy", "aged domains", "domain list", "buy backlinks",
    "expired domains", "domain marketplace", "powerful pbn", "pbn backlinks",
    "high da backlinks", "cheap backlinks",
    # domain-marketplace / aged-domain seller auto pages
    "directory pages index", "seo domain research", "domain research",
    "top domains – page", "top domains - page", "web directory",
    "domains on ip", "any seo resource", "no resellers", "domain report",
    # reverse-IP / stat / shortener tool pages
    "url shared", "website stats", "website stat",
    # SEO-agency pitch / rank-boost sales pages
    "linkly.agency", "transformed my website", "make ai recommend your brand",
    "boost your google rankings",
    # off-topic content-farm article repeated across unrelated PBN hosts
    "morel mushrooms",
]

# ---- Free-blog hosts used as throwaway PBN scrap pages -----------------------
# A page on one of these whose title does not name the client and whose only
# anchor is a bare URL / brand token is a throwaway PBN page, not an editorial
# mention. (Observed: gibberish-titled *.blogspot.com pages, many already 404.)
FREE_BLOG_PBN_HOSTS = ["blogspot.com"]

# ---- Thresholds --------------------------------------------------------------
KEEP_AS_THRESHOLD = 20     # Authority Score >= this => genuine site => Keep
NETWORK_MIN_HOSTS = 5      # 5+ ref domains on one /24 (ex-CDN) => network host

# CDN / big-host /24s to exclude from the network-host signal
CDN_IP_PREFIXES_EXCLUDE = ["172.67.", "104.21.", "104.26.", "104.27.", "188.114.",
                           "162.159.", "104.16.", "104.17.", "104.18.", "104.19.",
                           "104.20.", "104.22.", "104.23.", "104.24.", "104.25.",
                           "131.0.72.", "151.101."]  # Cloudflare + Fastly ranges
