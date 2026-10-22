"""
Client constants for the aaronshometech.com backlink audit.
Only this file changes per client (per BACKLINK_AUDIT_PLAYBOOK.md section 10).
Derived from the live Semrush anchor/target profile and the client brief.

Terminology note (per AUDIT_FORMAT.md "Things that change per client"):
the client brief calls the confirming party the "supplier"; the sheet keeps
saying "partner". The two are tied together once, in the disavow file header.
"""

CLIENT_NAME = "Aaron's Home Tech"
MONEY_SITE = "aaronshometech.com"

# Domains the client appears to own / that share the "Aaron's" brand and the
# legal name "Aaron's Systems Integrators, Inc." Pending client confirmation of
# ownership and of whether they 301 into the money site (Section 7).
# Until confirmed they are treated as Own Site (not disavowed, held out of files).
OWNED_DOMAINS = {
    "aaronshometech.com",
    "aaronssystems.com",      # Aaron's Systems Integrators, Inc.
    "aaronssecurity.com",     # Aaron's Security
}
OWNED_CONFIRMED = False  # flip to True once the client confirms ownership/redirects

# Our own agency (the audit is in Harbinger format). Agency links are genuine.
AGENCY_DOMAINS = {"harbingermarketing.com"}

# Brand tokens (for branded-anchor / genuine-citation detection).
BRAND_TOKENS = [
    "aaron's home tech", "aarons home tech", "aaron s home tech",
    "aaronshometech", "aaron's systems integrators", "aarons systems integrators",
    "aaron's systems", "aaronssystems", "aaron's security", "aaronssecurity",
]

# Service vocabulary (exact-match commercial anchor detection).
SERVICE_TERMS = [
    "home automation", "smart home", "home theater", "home theatre",
    "home audio", "sound system", "whole home audio", "whole house audio",
    "whole-home audio", "security system", "security camera", "cctv",
    "commercial security", "access control", "key card entry",
    "home network", "network installation", "network setup",
    "smart lighting", "lighting automation", "lighting control",
    "smart blinds", "motorized shade", "outdoor speaker", "outdoor audio",
    "alarm system", "home security", "surveillance", "av installation",
    "audio visual", "home entertainment", "smart home automation",
    "whole-house vacuum", "whole house vacuum",
]

# Geography (exact-match commercial *(geo)* anchors). Metro-Atlanta GA + Highlands NC.
GEO_TERMS = [
    "atlanta", "greensboro", "senoia", "roswell", "decatur", "marietta",
    "johns creek", "smyrna", "sandy springs", "vinings", "brookhaven",
    "peachtree city", "eatonton", "chattahoochee hills", "fayetteville",
    "highlands", " ga", ", ga", " nc", ", nc",
]

# Other businesses serviced by the same link vendor's PBN. Their names appearing
# in an anchor pointing at the money site is positive PBN evidence (the referring
# page is a link-farm selling placements to many clients).
PBN_COCLIENT_TOKENS = [
    "msrs", "msroofs", "ms-roofs", "msrsgroup", "mid-south", "midsouthroof",
    "mid-southroof", "mid-southgroup", "regenerativespinesatl", "drbyronharper",
    "jpbakerconstruction", "brilliantnightlighting", "nascreening",
    "nationalapplicantscreening", "prefabatl", "towtruckelpaso", "msrm.services",
]

# Spam anchor signatures: the PBN/link-service sales-copy template and friends.
# Any of these in an anchor => keyword-stuffed SEO sales copy (PBN) spam.
SPAM_ANCHOR_SIGNATURES = [
    "buy backlinks", "premium pbn", "pbn backlinks", "pbn network",
    "niche edit", "manual outreach backlink", "seo link building",
    "link building service", "link building experts", "link insertion",
    "guest post", "guest posting", "dofollow backlink", "da 50 pa 40",
    "da 50", "pa 40", "visit site seo", "for latest info", "premium backlinks",
    "premium seo", "high da backlinks", "high authority backlinks",
    "authority backlinks", "white hat seo link", "tiered link building",
    "contextual link placement", "contextual backlinks", "citation flow",
    "trust flow", "domain rating", "domain authority", "backlink building",
    "backlink experts", "backlink service", "seo backlinks", "seo links",
    "rank higher", "rank first page", "first page positions",
    "first page google", "higher da and dr", "da and dr", "dr scores",
    "outrank your competitors", "link velocity", "placement reporting",
    "buy aged domains", "paid blog post", "press releases via",
    "backlinks for", "backlinks from", "backlink for",
]

# Spam testimonial / off-template signatures (emoji-laden fake reviews, telegram).
SPAM_SOFT_SIGNATURES = [
    "t.me/", "telegram", "@happygrannypies", "darksidelinks", "quarterlinks",
    "da rose from", "da from", "traffic surged", "traffic jumped",
    "traffic up by", "increase in engagement", "increase in traffic",
    "boost in sales", "conversion rate skyrocket", "went viral",
    "ranks in the top", "top 3 on google", "top 3 in google",
    "made its first sale", "revenue jumped", "fiverr", "sitetosocial",
    "itxoft", "📊", "🚀", "💎", "💯", "🔝", "📈", "💪", "✨", "⚡", "🔥", "💰", "😎", "🌟", "🎯", "🌐",
]

# Spam host-name signatures (Section 6 rule 9).
SPAM_HOST_SIGNATURES = [
    "backlink", "seo", "dapa", "rankchecker", "rank-checker", "directory",
    "listing", "pbn", "linkbuilding", "link-building", "buybacklink",
    "domainlist", "aged-domain", "agedomain", "bookmark", "socialbookmark",
    "websitescrawl", "domaineye", "seo-revealed", "knows.monster",
    "screenshots.wiki", "sergechel", "parse.gl",
]

# Spam page-title / URL-template signatures (Section 6 rule 10).
SPAM_TITLE_SIGNATURES = [
    "domain list", "where to buy", "aged domains", "buy backlinks",
    "backlinks for sale", "link marketplace", "buy links", "pbn",
    "/domain/", "page 14", "cheap backlinks", "casino", "poker", "slot",
    "gambling", "pharma", "viagra", "cialis", "escort", "porn", "adult",
    "web directory", "websites directory", "global websites directory",
    "seo rank boost", "backlink building services", "authority backlink",
    "link spreader", "top list of websites", "few of top websites",
    "top websites", "link list", "toplist", "top billion",
    "backlinks, guest", "guest posts, press", "backlinks and guest",
]

# Press-release syndication hosts (playbook rule 5 -> Held, Pending Partner):
# syndicated PR can be a commissioned placement; confirm before any action.
PRESS_RELEASE_HOSTS = [
    "ezpr.org", "einpresswire.com", "prlog.org", "openpr.com", "newswire.com",
    "pressrelease", "prfree", "24-7pressrelease", "issuewire.com", "prweb.com",
    "pr.com", "releasewire", "newsnetmedia", "yoursourcenews", "economicpolicytimes",
    "businesstimes", "onlygolfnews", "timesla.com", "xpr.media",
]

# Off-topic (casino/pharma/etc.) hard-spam tokens (Section 6 rule 7).
OFFTOPIC_TOKENS = [
    "casino", "poker", "slot", "gambling", "betting", "pharma", "viagra",
    "cialis", "escort", "porn", "adult", "cbd", "crypto", "forex",
]

# Authority-Score threshold at/above which a domain is treated as a genuine site
# (Section 6 rule 2).
KEEP_AS_THRESHOLD = 20
