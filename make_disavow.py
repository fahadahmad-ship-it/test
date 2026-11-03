import sys, openpyxl, re, datetime
p=sys.argv[1]
wb=openpyxl.load_workbook(p, read_only=True, data_only=True)
today="2026-11-03"

def clean_line(v):
    s=str(v).strip()
    return s

# ---- Ready-to-submit disavow (spam, dofollow) ----
dl=wb["Disavow List"]
lines=[clean_line(r[0]) for r in dl.iter_rows(min_row=2, values_only=True) if r[0]]
# sanity: all must start with domain:
assert all(l.startswith("domain:") for l in lines), "unexpected non-domain line"
assert len(lines)==len(set(lines)), "duplicates!"

header=[
"# Google Disavow file - New Garden Landscaping & Nursery (newgarden.com)",
f"# Generated: {today}",
"# Source: Semrush Backlink Analytics export (2,683 referring domains / 8,086 backlinks),",
"#   cross-checked against Ahrefs. Verified: Semrush live totals match the export exactly.",
"#",
"# SCOPE: This file lists ONLY referring domains classified as spam/link-scheme placements",
"#   that carry at least one DOFOLLOW link (1,646 domains). Nofollow-only spam is omitted",
"#   (passes no ranking value). Domains with exact-match commercial/geo anchors that MAY be",
"#   commissioned placements are HELD OUT pending confirmation - see the separate file",
"#   'disavow_newgarden_PENDING_partner_confirmation.txt'.",
"#",
"# DO NOT SUBMIT until: (a) Google Search Console is checked for a manual action, AND",
"#   (b) the previous SEO supplier confirms which anchors/placements were commissioned.",
"# Disavow is a last resort - prefer monitoring unless a manual action exists or the client",
"#   confirms links were bought.",
f"# Spam domains (dofollow): {len(lines)}",
"#",
]
with open("disavow_newgarden.txt","w",encoding="utf-8") as f:
    f.write("\n".join(header)+"\n")
    f.write("\n".join(lines)+"\n")
print("disavow_newgarden.txt ->", len(lines), "domain lines")

# ---- Pending (held) lines - append only if NOT confirmed ----
pd=wb["Pending Disavow Lines"]
prows=[r for r in pd.iter_rows(min_row=2, values_only=True) if r[0]]
plines=[clean_line(r[1]) for r in prows]
assert all(l.startswith("domain:") for l in plines)
phdr=[
"# PENDING - New Garden Landscaping & Nursery (newgarden.com)",
f"# Generated: {today}",
"# These 120 referring domains carry an EXACT-MATCH commercial/geo anchor (Greensboro /",
"#   Winston-Salem landscape-service copy) and MAY have been a commissioned/paid placement.",
"#   Independent check: Ahrefs marks these anchors NOT spam (DR up to 60).",
"#",
"# ACTION: Do NOT disavow yet. First confirm with the previous SEO supplier which of these",
"#   placements were commissioned. APPEND these lines to disavow_newgarden.txt ONLY for the",
"#   domains the supplier does NOT confirm. Keep (do not disavow) any the supplier confirms",
"#   as a legitimate commissioned placement and that are worth keeping.",
"# (13 further Tab 05 domains are nofollow-only = no action needed either way.)",
f"# Held domains (dofollow): {len(plines)}",
"#",
]
with open("disavow_newgarden_PENDING_partner_confirmation.txt","w",encoding="utf-8") as f:
    f.write("\n".join(phdr)+"\n")
    f.write("\n".join(plines)+"\n")
print("pending file ->", len(plines), "domain lines")

# quick final guard: no overlap between the two files
a=set(l.lower() for l in lines); b=set(l.lower() for l in plines)
print("overlap between submit & pending files:", len(a&b))
