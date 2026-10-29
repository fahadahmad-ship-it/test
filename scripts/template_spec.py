# Build spec extracted from the K&K template — reused verbatim for kbelectric.online
# Colors / fonts
HEADER_FILL = "0C343D"      # dark teal, header rows
HEADER_FONT = "FFFFFF"      # white
TITLE_COLOR = "0C343D"
FONT_NAME = "Arial"
# Number formats
FMT_INT = "#,##0"
FMT_PCT = "0.0%"
FMT_DATE = "d mmm yyyy"

# Tab order + headers (exact)
TABS = {
    "Summary": None,  # custom layout
    "Referring Domain Audit": ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow",
        "Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text",
        "Example Linking Page","Linking Page Title","Source","IP","Disavow Line"],
    "All Backlinks": ["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
        "Linking Page URL","Linking Page Title","Target URL"],
    "Anchor Analysis": ["Anchor Text","Anchor Type","Backlinks","Share of Backlinks",
        "Referring Domains","Spam Domains Using It"],
    "Exact Match Anchors": ["Referring domain","Example backlink (linking page)",
        "Exact-match commercial anchor","Market","Site type (indicative)",
        "Partner confirmed? (Y/N)","Final decision"],
    "Pending Disavow Lines": ["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"],
    "Disavow List": ["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"],
}

# Column widths per tab (col letter -> width)
WIDTHS = {
    "Summary": {"A":38.9,"B":16.3,"C":17.6,"D":18.7,"E":120.0},
    "Referring Domain Audit": {"A":36.0,"B":24.7,"C":9.6,"D":13.0,"E":9.4,"F":9.7,"G":12.4,"H":21.3,
        "I":14.0,"J":8.7,"K":12.0,"L":45.0,"M":8.7,"N":40.0,"O":14.0,"P":15.0,"Q":14.0},
    "All Backlinks": {"A":25.4,"B":27.1,"C":14.7,"D":55.0,"E":32.0,"F":10.0,"G":55.0,"H":53.1,"I":30.6},
    "Anchor Analysis": {"A":115.9,"B":37.7,"C":14.0,"D":8.7,"F":20.3},
    "Exact Match Anchors": {"A":25.4,"B":59.0,"C":53.1,"D":16.0,"E":24.6,"F":15.4,"G":15.0},
    "Pending Disavow Lines": {"A":32.0,"B":44.0,"C":48.0},
    "Disavow List": {"A":44.0,"B":14.0,"C":15.6,"D":14.0,"E":11.1,"F":14.9,"G":98.9},
}

# Status taxonomy -> "What it means" copy (Summary tab col E)
STATUS_MEANING = {
    "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
    "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
    "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
    "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
    "Keep": "Genuine or harmless link. Keep.",
    "Own Site": "Client owned domain that redirects into the site.",
}
# Summary status table row order
STATUS_ORDER = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
    "Spam (Nofollow, No Action)","Keep","Own Site"]

# Anchor-type taxonomy, Summary "Anchor text profile" row order
ANCHOR_TYPES = ["Spam: keyword stuffed SEO sales copy","Naked URL","Exact match commercial",
    "Exact match commercial (geo)","Generic","Branded","Empty or image","Contextual or other"]

CLIENT_NAME = "KB Electric LLC"
CLIENT_DOMAIN = "kbelectric.online"
