"""
Authoritative layout + styling spec for the signed-off Harbinger backlink-audit
workbook, read cell-for-cell from the K&K Manufacturing signed template
(superk/ref/KandK_sample.xlsx) via its OOXML. build.py imports these constants so
the superkexpress workbook matches the template structurally (compare.py checks it).

Ground-truth notes (template beats looser prose in AUDIT_FORMAT.md):
 - Title in Summary B1 is Geist 21 bold, accent FF0C343D (NOT 9pt).
 - Data cells are UNBORDERED; only the header row carries a left/right/top (no
   bottom) thin border. Summary's own small tables are fully boxed.
 - Status column carries meaning; no status colour coding.
"""

ACCENT = "FF0C343D"      # single accent colour: headers + partner input cells
WHITE  = "FFFFFFFF"
BLACK  = "FF000000"
FONT   = "Geist"

# numFmts
FMT_PCT  = "0.0%"        # numFmtId 164 - share columns
FMT_DATE = "d mmm yyyy"  # numFmtId 165

# Sheet order (tab name -> 1-based index)
SHEETS = [
    "Summary",
    "Referring Domain Audit",
    "All Backlinks",
    "Anchor Analysis",
    "Exact Match Anchors",
    "Pending Disavow Lines",
    "Disavow List",
]

# Column widths (Excel width units), per sheet, in column order.
COL_WIDTHS = {
    "Summary": [38.86, 16.29, 17.57, 18.71, 120.0],
    "Referring Domain Audit": [36.0, 24.71, 9.57, 13.0, 9.43, 9.71, 12.43, 21.29,
                               14.0, 8.71, 12.0, 45.0, 8.71, 40.0, 14.0, 15.0, 14.0],
    "All Backlinks": [25.43, 27.14, 14.71, 55.0, 32.0, 10.0, 55.0, 53.14, 30.57],
    "Anchor Analysis": [115.86, 37.71, 14.0, 8.71, 13.0, 20.29],
    "Exact Match Anchors": [25.43, 59.0, 53.14, 16.0, 24.57, 15.43, 15.0],
    "Pending Disavow Lines": [32.0, 44.0, 48.0],
    "Disavow List": [44.0, 14.0, 15.57, 14.0, 11.14, 14.86, 98.86],
}

DEFAULT_COL_WIDTH = 14.43
DEFAULT_ROW_HEIGHT = 15.0

# Row heights
HEADER_ROW_HEIGHT = 31.5           # header row on every data tab
DATA_ROW_HEIGHT = {               # data rows per data tab
    "Referring Domain Audit": 15.75,
    "All Backlinks": 22.5,
    "Anchor Analysis": 22.5,
    "Exact Match Anchors": 22.5,
    "Pending Disavow Lines": 22.5,
    "Disavow List": 22.5,
}
SUMMARY_ROW_HEIGHT = 22.5          # every row on the Summary

# The six data tabs: freeze panes at B2, autofilter across full range, gridlines on.
DATA_TABS = SHEETS[1:]
FREEZE_DATA = "B2"
# Summary: gridlines off, no freeze, no filter, title merged B1:E2.
SUMMARY_TITLE_MERGE = "B1:E2"

# Logo (Summary only): oneCellAnchor from (col 0, colOff 381000, row 0, rowOff 0),
# ext cx 1866900 cy 552450. Image is the Harbinger Marketing logo (template image1.png).
LOGO_FROM_COL = 0
LOGO_FROM_COLOFF = 381000
LOGO_FROM_ROW = 0
LOGO_FROM_ROWOFF = 0
LOGO_EXT_CX = 1866900
LOGO_EXT_CY = 552450

# Headers per tab (exact strings, in column order)
HEADERS = {
    "Referring Domain Audit": ["Domain", "Status", "AS", "Backlinks", "RD's",
        "Traffic", "In Disavow", "Links Point To", "Dofollow Links",
        "Nofollow Links", "First Seen", "Top Anchor Text", "Example Linking Page",
        "Linking Page Title", "Source", "IP", "Disavow Line"],
    "All Backlinks": ["Referring Domain", "Status", "Tool", "Anchor Text",
        "Anchor Type", "Link Type", "Linking Page URL", "Linking Page Title",
        "Target URL"],
    "Anchor Analysis": ["Anchor Text", "Anchor Type", "Backlinks",
        "Share of Backlinks", "Referring Domains", "Spam Domains Using It"],
    "Exact Match Anchors": ["Referring domain", "Example backlink (linking page)",
        "Exact-match commercial anchor", "Market", "Site type (indicative)",
        "Partner confirmed? (Y/N)", "Final decision"],
    "Pending Disavow Lines": ["Referring domain",
        "Disavow line (append to disavow.txt once confirmed)", "Recommendation"],
    "Disavow List": ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic",
        "Organic Keywords", "Top Anchor Text"],
}

# Six statuses, no others.
STATUSES = [
    "Spam (Disavow)",
    "Spam (Nofollow, No Action)",
    "Held (Pending Partner)",
    "Held (Nofollow, No Action)",
    "Keep",
    "Own Site",
]
