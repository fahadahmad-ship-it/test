"""Build the 7-tab workbook + disavow file(s) in the signed-off Harbinger format.
Usage: python3 -I build.py <classified.json> <logo.png> <out.xlsx> <outdir_for_txt>
Matches KandK_template.xlsx cell-for-cell (fonts, accent, borders, heights, logo).
"""
import sys, os, json, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D

ACCENT = "FF0C343D"; WHITE = "FFFFFFFF"; BLACK = "FF000000"
CLASSIFIED, LOGO, OUTXLSX, OUTDIR = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
DISAVOW_FILE = f"disavow_{C.MONEY_DOMAIN.split('.')[0]}.txt"

def F(sz=9, b=False, color=BLACK):
    return Font(name="Geist", size=sz, bold=b, color=color)
ACC_FILL = PatternFill("solid", fgColor=ACCENT)
WHITE_FILL = PatternFill("solid", fgColor=WHITE)
thin = Side(style="thin", color="FF000000")
BORDER_FULL = Border(left=thin, right=thin, top=thin, bottom=thin)
BORDER_HDR = Border(left=thin, right=thin, top=thin)   # data-tab header: no bottom
C_CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
C_VC = Alignment(vertical="center")
C_VCW = Alignment(vertical="center", wrap_text=True)

data = json.load(open(CLASSIFIED, encoding="utf-8"))
by_status = collections.Counter(r["status"] for r in data)

def disavow_line(r):
    return f"domain:{r['domain']}"

def in_disavow_val(r):
    if r["status"] == "Spam (Disavow)":
        return "Yes"
    if r["status"].startswith("Held"):
        return "Held"
    return "No"

def as_date(iso):
    if not iso:
        return None
    try:
        return datetime.date.fromisoformat(iso)
    except Exception:
        return None

wb = Workbook()

# ============ data-tab helper ============
HDR_CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
HDR_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
HDR_CTR_NOWRAP = Alignment(horizontal="center", vertical="center", wrap_text=False)

def make_tab(title, headers, widths, rowheight, hdr_align_overrides=None):
    hdr_align_overrides = hdr_align_overrides or {}
    ws = wb.create_sheet(title)
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = F(9, True, WHITE); c.fill = ACC_FILL; c.border = BORDER_HDR
        c.alignment = hdr_align_overrides.get(i, HDR_CTR)
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.row_dimensions[1].height = 31.5
    ws.freeze_panes = "B2"
    # leave gridlines at the Excel default (on) to match the template exactly
    ws._audit_rowheight = rowheight
    return ws

def put(ws, r, c, val, *, nf=None, align=C_VC, font=None, fill=WHITE_FILL, border=None):
    cell = ws.cell(row=r, column=c, value=val)
    cell.font = font or F(9)
    cell.fill = fill
    cell.alignment = align
    if border:
        cell.border = border
    if nf:
        cell.number_format = nf
    return cell

def finalize(ws, nrows):
    last = get_column_letter(ws.max_column)
    ws.auto_filter.ref = f"A1:{last}{max(nrows+1,1)}"
    h = ws._audit_rowheight
    for r in range(2, nrows + 2):
        ws.row_dimensions[r].height = h

# ============ 2. Referring Domain Audit ============
rda_h = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To",
         "Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page",
         "Linking Page Title","Source","IP","Disavow Line"]
rda_w = {'A':36,'B':24.71,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,'J':8.71,
         'K':12,'L':45,'M':8.71,'N':40,'O':14,'P':15,'Q':14}
ws = make_tab("Referring Domain Audit", rda_h, rda_w, 15.75)
for i, r in enumerate(sorted(data, key=lambda x: x["domain"]), start=2):
    ex = r.get("example") or {}
    put(ws, i, 1, r["domain"])
    put(ws, i, 2, r["status"])
    put(ws, i, 3, r.get("as") if r.get("as") is not None else "")
    put(ws, i, 4, r.get("sem_backlinks") or r["n_links"], nf="#,##0", align=C_CTR)
    put(ws, i, 5, r.get("rds") if r.get("rds") is not None else "", nf="#,##0", align=C_CTR)
    put(ws, i, 6, r.get("traffic") if r.get("traffic") is not None else 0, nf="#,##0", align=C_CTR)
    put(ws, i, 7, in_disavow_val(r), align=C_CTR)
    put(ws, i, 8, r.get("links_point_to", ""))
    put(ws, i, 9, r["dofollow"], nf="#,##0", align=C_CTR)
    put(ws, i, 10, r["nofollow"], nf="#,##0", align=C_CTR)
    d = as_date(r.get("first_seen"))
    cell = put(ws, i, 11, d, align=C_CTR);
    if d: cell.number_format = "d mmm yyyy"
    put(ws, i, 12, r.get("top_anchor",""))
    put(ws, i, 13, ex.get("source_url",""))
    put(ws, i, 14, ex.get("source_title",""))
    put(ws, i, 15, r.get("tool",""))
    put(ws, i, 16, r.get("ip",""))
    put(ws, i, 17, disavow_line(r) if r["status"]=="Spam (Disavow)" else "")
finalize(ws, len(data))

# ============ 3. All Backlinks ============
ab_h = ["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
        "Linking Page URL","Linking Page Title","Target URL"]
ab_w = {'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':30.57}
ws = make_tab("All Backlinks", ab_h, ab_w, 22.5, hdr_align_overrides={3: HDR_LEFT})
rowi = 2
for r in sorted(data, key=lambda x: x["domain"]):
    for l in r["links"]:
        put(ws, rowi, 1, r["domain"])
        put(ws, rowi, 2, r["status"])
        put(ws, rowi, 3, l.get("tool",""), align=Alignment(horizontal="left", vertical="center"))
        put(ws, rowi, 4, l.get("anchor",""))
        put(ws, rowi, 5, l.get("anchor_type",""))
        put(ws, rowi, 6, "Nofollow" if l["nofollow"] else "Dofollow", align=C_CTR)
        put(ws, rowi, 7, l.get("source_url",""))
        put(ws, rowi, 8, l.get("source_title",""))
        put(ws, rowi, 9, l.get("target_url",""))
        rowi += 1
finalize(ws, rowi-2)

# ============ 4. Anchor Analysis ============
aa_h = ["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
aa_w = {'A':115.86,'B':37.71,'C':14,'D':8.71,'F':20.29}
ws = make_tab("Anchor Analysis", aa_h, aa_w, 22.5, hdr_align_overrides={1: HDR_CTR_NOWRAP})
anchor_bl = collections.Counter(); anchor_rd = collections.defaultdict(set); anchor_spam = collections.defaultdict(set)
anchor_type_map = {}
total_links = 0
for r in data:
    for l in r["links"]:
        a = (l.get("anchor") or "").strip()
        anchor_bl[a]+=1; anchor_rd[a].add(r["domain"]); anchor_type_map[a]=l.get("anchor_type","")
        total_links += 1
        if r["status"].startswith("Spam"):
            anchor_spam[a].add(r["domain"])
rowi=2
for a,cnt in anchor_bl.most_common():
    put(ws, rowi, 1, a)
    put(ws, rowi, 2, anchor_type_map.get(a,""))
    put(ws, rowi, 3, cnt, nf="#,##0", align=C_CTR)
    put(ws, rowi, 4, cnt/total_links if total_links else 0, nf="0.0%", align=C_CTR)
    put(ws, rowi, 5, len(anchor_rd[a]), nf="#,##0", align=C_CTR)
    put(ws, rowi, 6, len(anchor_spam[a]), nf="#,##0", align=C_CTR)
    rowi+=1
finalize(ws, rowi-2)

# ============ 5. Exact Match Anchors ============
ema_h = ["Referring domain","Example backlink (linking page)","Exact-match commercial anchor",
         "Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
ema_w = {'A':25.43,'B':59,'C':53.14,'D':16,'E':24.57,'F':15.43,'G':15}
ws = make_tab("Exact Match Anchors", ema_h, ema_w, 22.5)
rowi=2
for r in sorted(data, key=lambda x: x["domain"]):
    if not r["evidence"]["exact"]:
        continue
    # one row per distinct exact-match anchor on this domain
    seen=set()
    for l in r["links"]:
        if l.get("anchor_type") in ("Exact match commercial","Exact match commercial (geo)"):
            a=(l.get("anchor") or "").strip()
            if a in seen: continue
            seen.add(a)
            put(ws, rowi, 1, r["domain"])
            put(ws, rowi, 2, l.get("source_url",""))
            put(ws, rowi, 3, a)
            put(ws, rowi, 4, "Georgia" if l["anchor_type"].endswith("(geo)") else "Non-geo", align=C_CTR)
            put(ws, rowi, 5, r.get("site_type",""))
            put(ws, rowi, 6, None, fill=ACC_FILL, font=F(9,False,WHITE))   # partner input
            put(ws, rowi, 7, None, fill=ACC_FILL, font=F(9,False,WHITE))   # partner input
            rowi+=1
finalize(ws, rowi-2)

# ============ 6. Pending Disavow Lines ============
pd_h = ["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"]
pd_w = {'A':32,'B':44,'C':48}
ws = make_tab("Pending Disavow Lines", pd_h, pd_w, 22.5)
rowi=2
held = [r for r in data if r["status"]=="Held (Pending Partner)"]
for r in sorted(held, key=lambda x:x["domain"]):
    put(ws, rowi,1, r["domain"])
    put(ws, rowi,2, disavow_line(r))
    put(ws, rowi,3, f"Append only if the partner does not claim it, to {DISAVOW_FILE}")
    rowi+=1
finalize(ws, rowi-2)

# ============ 7. Disavow List ============
dl_h = ["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
dl_w = {'A':44,'B':14,'C':15.57,'D':14,'E':11.14,'F':14.86,'G':98.86}
ws = make_tab("Disavow List", dl_h, dl_w, 22.5)
rowi=2
disav = [r for r in data if r["status"]=="Spam (Disavow)"]
for r in sorted(disav, key=lambda x:x["domain"]):
    put(ws, rowi,1, disavow_line(r))
    put(ws, rowi,2, r.get("as") if r.get("as") is not None else "", align=C_CTR)
    put(ws, rowi,3, r.get("sem_backlinks") or r["n_links"], nf="#,##0", align=C_CTR)
    put(ws, rowi,4, r.get("rds") if r.get("rds") is not None else "", nf="#,##0", align=C_CTR)
    put(ws, rowi,5, r.get("traffic") if r.get("traffic") is not None else 0, nf="#,##0", align=C_CTR)
    put(ws, rowi,6, r.get("organic_keywords") if r.get("organic_keywords") is not None else 0, nf="#,##0", align=C_CTR)
    put(ws, rowi,7, r.get("top_anchor",""))
    rowi+=1
finalize(ws, rowi-2)

# ============ 1. Summary (first sheet) ============
ws = wb["Sheet"]; ws.title = "Summary"; wb.move_sheet("Summary", -(len(wb.sheetnames)-1))
ws.sheet_view.showGridLines = False
for col,w in {'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120}.items():
    ws.column_dimensions[col].width = w
# title
ws.merge_cells("B1:E2")
tc = ws.cell(row=1,column=2, value=C.CLIENT_NAME); tc.font=F(21,True,ACCENT)
tc.alignment=Alignment(horizontal="center", vertical="center", wrap_text=False)
ws.row_dimensions[1].height=22.5; ws.row_dimensions[2].height=22.5
# logo
img = Image(LOGO)
img.anchor = OneCellAnchor(_from=AnchorMarker(col=0, colOff=381000, row=0, rowOff=0),
                           ext=XDRPositiveSize2D(1866900, 552450))
ws.add_image(img)
# status table (rows 3-10)
st_hdr = ["Status","Domains","Backlinks","Share of Domains","What it means"]
for i,h in enumerate(st_hdr,1):
    c=ws.cell(row=3,column=i,value=h); c.font=F(10,True,WHITE); c.fill=ACC_FILL; c.border=BORDER_FULL; c.alignment=C_CTR
MEANS = {
 "Spam (Disavow)":"Confirmed spam with at least one dofollow link. Included in the disavow file.",
 "Held (Pending Partner)":"Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous SEO partner confirms.",
 "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)":"Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep":"Genuine or harmless link. Keep.",
 "Own Site":"Client owned domain that redirects into the site.",
}
order = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
         "Spam (Nofollow, No Action)","Keep","Own Site"]
bl_by_status = collections.Counter()
for r in data:
    bl_by_status[r["status"]] += r["n_links"]
total_dom = len(data); total_bl = sum(bl_by_status.values())
rr=4
for s in order:
    dn=by_status.get(s,0); bn=bl_by_status.get(s,0)
    vals=[s, dn, bn, (dn/total_dom if total_dom else 0), MEANS[s]]
    for i,v in enumerate(vals,1):
        c=ws.cell(row=rr,column=i,value=v); c.font=F(9); c.fill=WHITE_FILL; c.border=BORDER_FULL
        c.alignment = C_VCW if i==5 else (C_VC if i==1 else Alignment(horizontal="center",vertical="center"))
        if i==4: c.number_format="0.0%"
        if i in (2,3): c.number_format="#,##0"
    rr+=1
# total row 10
tot=["Total", total_dom, total_bl, 1.0, None]
for i,v in enumerate(tot,1):
    c=ws.cell(row=10,column=i,value=v); c.font=F(9,True); c.fill=WHITE_FILL; c.border=BORDER_FULL
    c.alignment = C_VC if i==1 else Alignment(horizontal="center",vertical="center")
    if i==4: c.number_format="0.0%"
    if i in (2,3): c.number_format="#,##0"
for r in range(1,11):
    ws.row_dimensions[r].height=22.5

# Key findings (row 11 heading, 12-18 seven findings)
ws.cell(row=11,column=1,value="Key findings").font=F(10,True,BLACK)
from findings_text import FINDINGS   # generated by compute_findings.py
for idx,txt in enumerate(FINDINGS):
    rr=12+idx
    ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5)
    c=ws.cell(row=rr,column=1,value=txt); c.font=F(9); c.alignment=Alignment(vertical="center",wrap_text=True)
    ws.row_dimensions[rr].height=22.5
# Anchor profile (row 19 heading, 20 header, 21+ rows)
ws.cell(row=19,column=1,value="Anchor text profile (all backlinks)").font=F(11,True,ACCENT)
ap_hdr=["Anchor type","Backlinks","Share of Backlinks","Referring Domains"]
for i,h in enumerate(ap_hdr,1):
    c=ws.cell(row=20,column=i,value=h); c.font=F(9,True,WHITE); c.fill=ACC_FILL; c.border=BORDER_FULL; c.alignment=C_CTR
type_bl=collections.Counter(); type_rd=collections.defaultdict(set)
for r in data:
    for l in r["links"]:
        t=l.get("anchor_type","Contextual or other"); type_bl[t]+=1; type_rd[t].add(r["domain"])
rr=21
for t in C.ANCHOR_TYPES:
    if type_bl.get(t,0)==0:
        continue
    vals=[t, type_bl[t], (type_bl[t]/total_links if total_links else 0), len(type_rd[t])]
    for i,v in enumerate(vals,1):
        c=ws.cell(row=rr,column=i,value=v); c.font=F(9); c.fill=WHITE_FILL; c.border=BORDER_FULL
        c.alignment=C_VC if i==1 else Alignment(horizontal="center",vertical="center")
        if i==3: c.number_format="0.0%"
        if i==2: c.number_format="#,##0"
    rr+=1
for r in range(11,rr):
    if ws.row_dimensions[r].height is None:
        ws.row_dimensions[r].height=22.5

wb.save(OUTXLSX)
print("saved workbook", OUTXLSX)

# ============ disavow .txt ============
# group disavow domains by reason
groups = collections.OrderedDict([
    ("PBN / SEO sales-copy link network", []),
    ("Spam directories, listings and bookmarking sites", []),
    ("Off-topic spam", []),
    ("Other confirmed spam (anchor / page evidence)", []),
])
for r in sorted(disav, key=lambda x:x["domain"]):
    ev=r["evidence"]
    if ev["offtopic"]:
        groups["Off-topic spam"].append(r)
    elif ev["pbn"]:
        groups["PBN / SEO sales-copy link network"].append(r)
    elif ev["spam_host"] or ev["spam_title"]:
        groups["Spam directories, listings and bookmarking sites"].append(r)
    else:
        groups["Other confirmed spam (anchor / page evidence)"].append(r)
lines=[]
lines.append(f"# Disavow file for {C.MONEY_DOMAIN} (Google Search Console property: {C.MONEY_DOMAIN})")
lines.append(f"# Generated {datetime.date.today().isoformat()} by Harbinger Marketing backlink audit.")
lines.append(f"# {len(disav)} domains to disavow. Confirmed spam with at least one dofollow link.")
lines.append(f"# Held domains ({by_status.get('Held (Pending Partner)',0)}) are NOT in this file: the SEO partner")
lines.append(f"#   who commissioned the links must confirm first. Do NOT upload before that conversation.")
lines.append(f"# No redirect/owned domains were detected, so this single file covers the whole property.")
lines.append(f"# Check Search Console: if a disavow file already exists, uploading REPLACES it.")
lines.append("")
for reason, rs in groups.items():
    if not rs: continue
    lines.append(f"# --- {reason} ({len(rs)}) ---")
    for r in rs:
        lines.append(disavow_line(r))
    lines.append("")
os.makedirs(OUTDIR, exist_ok=True)
with open(os.path.join(OUTDIR, DISAVOW_FILE), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote", os.path.join(OUTDIR, DISAVOW_FILE), "with", len(disav), "domains")
