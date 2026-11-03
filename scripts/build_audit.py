#!/usr/bin/env python3
"""Rebuild NewGarden backlink audit in the signed-off Harbinger format (AUDIT_FORMAT.md).
Reads the sample workbook as the template/source, applies the rosih.ru false-positive
correction (playbook 6/9/12), recomputes all derived numbers, and writes a conformant
workbook + disavow.txt. Styling follows AUDIT_FORMAT as written (user decision):
9pt accent title merged B1:E2; thin border all round on data cells.
"""
import sys, os, datetime, collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

SRC, LOGO, OUTXLSX, OUTDISAVOW = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
ACCENT = "FF0C343D"; WHITE = "FFFFFFFF"; BLACK = "FF000000"
TODAY = "2026-11-03"

wbs = openpyxl.load_workbook(SRC, data_only=True)
def read(tab):
    ws = wbs[tab]; rows = list(ws.iter_rows(values_only=True))
    hdr = [("" if c is None else str(c)).strip() for c in rows[0]]
    data = [list(r) for r in rows[1:] if any(c is not None and str(c).strip()!="" for c in r)]
    return hdr, data

rda_h, rda = read('Referring Domain Audit')
abl_h, abl = read('All Backlinks')
ema_h, ema = read('Exact Match Anchors')
pend_h, pend = read('Pending Disavow Lines')

ci = {name:i for i,name in enumerate(rda_h)}
ai = {name:i for i,name in enumerate(abl_h)}

# ---------- CORRECTION: rosih.ru false positive ----------
FP = "rosih.ru"
changes = []
for row in rda:
    if str(row[ci['Domain']]).lower() == FP:
        changes.append(("RDA", row[ci['Status']]))
        row[ci['Status']] = "Keep"
        row[ci['In Disavow']] = "No"
        row[ci['Disavow Line']] = None
for row in abl:
    if str(row[ai['Referring Domain']]).lower() == FP:
        row[ai['Status']] = "Keep"
        if row[ai['Anchor Type']] and "Spam" in str(row[ai['Anchor Type']]):
            row[ai['Anchor Type']] = "Empty or image"
print(f"Reclassified {FP}: {len(changes)} RDA row(s); {sum(1 for r in abl if str(r[ai['Referring Domain']]).lower()==FP)} backlink rows -> Keep / Empty or image")

# ---------- Recompute status table (domains from RDA, backlinks from All Backlinks) ----------
STATUS_ORDER = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
                "Spam (Nofollow, No Action)","Keep","Own Site"]
dom_by_status = collections.Counter(str(r[ci['Status']]) for r in rda)
bl_by_status  = collections.Counter(str(r[ai['Status']]) for r in abl)
TOTAL_DOM = len(rda); TOTAL_BL = len(abl)
MEANS = {
 "Spam (Disavow)":"Spam referring domain (link-scheme anchor or link-farm TLD) with at least one dofollow link. Included in the disavow-ready file.",
 "Held (Pending Partner)":"Non-spam domain with an exact-match commercial / geo anchor that MAY have been a commissioned placement. Held out of the disavow file until the client / previous SEO partner confirms.",
 "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)":"Spam domain, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep":"Genuine, branded or harmless link (incl. editorial citations, the plants.newgarden.com catalogue, and the rosih.ru image-source credit). Keep.",
 "Own Site":"Client-owned domain that redirects into the site.",
}

# ---------- Recompute anchor-type profile (Summary) ----------
type_bl = collections.Counter(str(r[ai['Anchor Type']]) for r in abl)
type_rd = collections.defaultdict(set)
for r in abl:
    type_rd[str(r[ai['Anchor Type']])].add(str(r[ai['Referring Domain']]).lower())
anchor_profile = sorted(type_bl.items(), key=lambda x:-x[1])

# ---------- Recompute Anchor Analysis tab ----------
anc_bl = collections.Counter()
anc_rd = collections.defaultdict(set)
anc_spamrd = collections.defaultdict(set)
anc_type = {}
for r in abl:
    a = r[ai['Anchor Text']]; akey = "" if a is None else str(a)
    dom = str(r[ai['Referring Domain']]).lower()
    anc_bl[akey]+=1; anc_rd[akey].add(dom)
    anc_type.setdefault(akey, str(r[ai['Anchor Type']]))
    if str(r[ai['Status']]).startswith("Spam"):
        anc_spamrd[akey].add(dom)
anchor_rows = []
for a,bl in sorted(anc_bl.items(), key=lambda x:-x[1]):
    anchor_rows.append([a if a!="" else None, anc_type[a], bl, bl/TOTAL_BL, len(anc_rd[a]), len(anc_spamrd[a])])

# ---------- Disavow List (from corrected RDA, spam-disavow only) ----------
dis_rows = []
for r in rda:
    if str(r[ci['Status']])=="Spam (Disavow)":
        dis_rows.append([f"domain:{str(r[ci['Domain']]).lower()}", r[ci['AS']], r[ci['Backlinks']],
                         None, None, None, r[ci['Top Anchor Text']]])
print("Disavow rows:", len(dis_rows))

# ---------- disavow.txt grouped by reason ----------
def reason(top):
    t = (str(top) or "").lower()
    if any(k in t for k in ["casino","gambl","porn","escort","viagra","pharma","loan","crypto"]): return "Off-topic (gambling / pharma / adult)"
    if any(k in t for k in ["backlink","seo","pbn","dofollow","da 50","rank","premium","niche edit","link building","boost your google"]): return "Link-service / PBN sales-copy anchor"
    if any(k in t for k in ["directory","listing","aged domain","domain list","buy "]): return "Spam directory / domain-marketplace"
    return "Other confirmed spam (anchor / host / page evidence)"
groups = collections.OrderedDict()
for r in rda:
    if str(r[ci['Status']])=="Spam (Disavow)":
        groups.setdefault(reason(r[ci['Top Anchor Text']]), []).append(str(r[ci['Domain']]).lower())
with open(OUTDISAVOW,"w") as f:
    f.write(f"# Disavow file - newgarden.com\n")
    f.write(f"# Property: newgarden.com (Google Search Console). Covers subdomains incl. plants.newgarden.com.\n")
    f.write(f"# Generated: {TODAY} | Domains: {len(dis_rows)}\n")
    f.write(f"# 'Partner' = the previous SEO partner who may have commissioned links.\n")
    f.write(f"# HELD domains (exact-match commercial anchors) are EXCLUDED pending partner confirmation.\n")
    f.write(f"# DO NOT UPLOAD before that conversation and before checking GSC for a manual action.\n")
    f.write(f"# Whether a disavow file already exists on this property is UNKNOWN - confirm with the client;\n")
    f.write(f"#   uploading REPLACES any existing file (it does not append).\n")
    f.write(f"# rosih.ru is intentionally NOT listed (image-source credit, not a link scheme).\n")
    for g, doms in groups.items():
        f.write(f"\n# --- {g} ({len(doms)}) ---\n")
        for d in sorted(set(doms)):
            f.write(f"domain:{d}\n")
print("Wrote disavow.txt groups:", {k:len(v) for k,v in groups.items()})

# ================= BUILD WORKBOOK =================
wb = openpyxl.Workbook(); wb.remove(wb.active)
thin = Side(style="thin", color="FFBFBFBF")
border_all = Border(left=thin,right=thin,top=thin,bottom=thin)
def F(size=9,bold=False,color=BLACK): return Font(name="Geist",size=size,bold=bold,color=color)
fill_accent = PatternFill("solid", fgColor=ACCENT)
fill_white  = PatternFill("solid", fgColor=WHITE)
hdr_al = Alignment(horizontal="center",vertical="center",wrap_text=True)
data_al = Alignment(vertical="center")

def style_header(ws, ncol, rowh=31.5):
    for c in range(1,ncol+1):
        cell = ws.cell(1,c); cell.font=F(9,True,WHITE); cell.fill=fill_accent
        cell.alignment=hdr_al; cell.border=border_all
    ws.row_dimensions[1].height=rowh
def style_data(ws, nrow, ncol, rowh):
    for r in range(2,nrow+1):
        ws.row_dimensions[r].height=rowh
        for c in range(1,ncol+1):
            cell=ws.cell(r,c); cell.font=F(9); cell.fill=fill_white
            cell.alignment=data_al; cell.border=border_all
WIDTHS = {
 'Referring Domain Audit':{'A':36,'B':24.71,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,'J':8.71,'K':12,'L':45,'M':8.71,'N':40,'O':14,'P':15,'Q':14},
 'All Backlinks':{'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':30.57},
 'Anchor Analysis':{'A':55,'B':32,'C':12,'D':15.57,'E':15,'F':18},
 'Exact Match Anchors':{'A':25.43,'B':59,'C':53.14,'D':16,'E':24.57,'F':15.43,'G':15},
 'Pending Disavow Lines':{'A':25.43,'B':45,'C':80},
 'Disavow List':{'A':44,'B':14,'C':15.57,'D':14,'E':11.14,'F':14.86,'G':98.86},
}
def write_tab(name, header, rows, rowh, input_cols=()):
    ws=wb.create_sheet(name)
    for c,h in enumerate(header,1): ws.cell(1,c,h)
    for ri,row in enumerate(rows,2):
        for c,v in enumerate(row,1): ws.cell(ri,c,v)
    ncol=len(header); nrow=len(rows)+1
    style_header(ws,ncol); style_data(ws,nrow,ncol,rowh)
    # partner input cells (accent fill, white font)
    for ic in input_cols:
        for r in range(2,nrow+1):
            cell=ws.cell(r,ic); cell.fill=fill_accent; cell.font=F(9,False,WHITE)
    for col,w in WIDTHS.get(name,{}).items(): ws.column_dimensions[col].width=w
    ws.freeze_panes="B2"
    ws.auto_filter.ref=f"A1:{get_column_letter(ncol)}{nrow}"
    return ws

# ---- Summary ----
ws=wb.create_sheet("Summary"); ws.sheet_view.showGridLines=False
for col,w in {'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120}.items(): ws.column_dimensions[col].width=w
try:
    img=XLImage(LOGO); img.width=196; img.height=58; ws.add_image(img,"A1")
except Exception as e:
    print("logo warn:",e)
ws.merge_cells("B1:E2"); t=ws.cell(1,2,"New Garden Landscaping & Nursery")
t.font=F(9,True,ACCENT); t.alignment=Alignment(horizontal="left",vertical="center")
ws.row_dimensions[1].height=22.5; ws.row_dimensions[2].height=22.5
# status table header row 3
sh=["Status","Domains","Backlinks","Share of Domains","What it means"]
for c,h in enumerate(sh,1):
    cell=ws.cell(3,c,h); cell.font=F(10,True,WHITE); cell.fill=fill_accent
    cell.alignment=hdr_al; cell.border=border_all
rr=4
for st in STATUS_ORDER:
    vals=[st,dom_by_status.get(st,0),bl_by_status.get(st,0),
          (dom_by_status.get(st,0)/TOTAL_DOM if TOTAL_DOM else 0),MEANS[st]]
    for c,v in enumerate(vals,1):
        cell=ws.cell(rr,c,v); cell.font=F(9); cell.fill=fill_white
        cell.alignment=Alignment(vertical="center",wrap_text=(c==5)); cell.border=border_all
    rr+=1
# total
tot=["Total",TOTAL_DOM,TOTAL_BL,1,""]
for c,v in enumerate(tot,1):
    cell=ws.cell(rr,c,v); cell.font=F(9,True); cell.fill=fill_white
    cell.alignment=Alignment(vertical="center"); cell.border=border_all
for r in range(3,rr+1): ws.row_dimensions[r].height=22.5
# key findings
kf_row=rr+2
ws.cell(kf_row,1,"Key findings").font=F(10,True,ACCENT)
spam_dom=dom_by_status['Spam (Disavow)']+dom_by_status['Spam (Nofollow, No Action)']
findings=[
 f"{spam_dom:,} of {TOTAL_DOM:,} referring domains are spam. {dom_by_status['Spam (Disavow)']:,} have a dofollow link and go in the disavow file; {dom_by_status['Spam (Nofollow, No Action)']} are nofollow and pass nothing.",
 "Referring domains doubled from 1,171 (Sep 2026) to 2,637 (Oct 2026) - a single recent flood. Semrush Authority Score stayed flat at 30, so the spam is not moving the profile.",
 "One link-service anchor, \"build powerful website authority with premium seo backlinks newgarden.com\", appears on ~1,469 domains. This is auto-generated spam, not links the client bought.",
 "rosih.ru is NOT in the disavow set: its 2,536 Semrush \"backlinks\" are one hot-linked plant image (an image-source credit). Ahrefs sees 3 links and does not flag it as spam. Reclassified Keep.",
 "133 domains carry exact-match local-service anchors (Greensboro / Winston-Salem). These may be a commissioned package - held for the partner to confirm in Tab 05 (columns F and G are blank).",
 "This audit is built on Semrush. Ahrefs indexes a different ~1,694 referring domains live; a cross-tool merge would add discovery. Every metric quoted here is Semrush.",
 "No manual action is visible in this data - check Search Console. Disavow only if there is a manual action or the client confirms buying links; otherwise monitor.",
]
r=kf_row+1
for fnd in findings:
    ws.merge_cells(f"A{r}:E{r}")
    cell=ws.cell(r,1,fnd); cell.font=F(9); cell.alignment=Alignment(vertical="center",wrap_text=True)
    ws.row_dimensions[r].height=22.5; r+=1
# anchor profile
ap_row=r+1
ws.cell(ap_row,1,"Anchor text profile (all backlinks)").font=F(10,True,ACCENT)
aph=["Anchor type","Backlinks","Share of Backlinks","Referring Domains"]
for c,h in enumerate(aph,1):
    cell=ws.cell(ap_row+1,c,h); cell.font=F(9,True,WHITE); cell.fill=fill_accent
    cell.alignment=hdr_al; cell.border=border_all
rr2=ap_row+2
for atype,bl in anchor_profile:
    vals=[atype,bl,bl/TOTAL_BL,len(type_rd[atype])]
    for c,v in enumerate(vals,1):
        cell=ws.cell(rr2,c,v); cell.font=F(9); cell.fill=fill_white
        cell.alignment=Alignment(vertical="center"); cell.border=border_all
    ws.row_dimensions[rr2].height=22.5; rr2+=1
# source note
src_row=rr2+1
ws.merge_cells(f"A{src_row}:E{src_row}")
note=(f"Source: Semrush Backlink Analytics export, {TODAY} ({TOTAL_BL:,} backlinks / {TOTAL_DOM:,} referring domains), "
      "cross-checked against Ahrefs. 'AS' = Semrush Authority Score (0-100). Per the signed format the RD's and Traffic "
      "columns are left blank (Semrush's referring-domains export omits them). rosih.ru reclassified from Spam to Keep "
      "(image-source credit, Ahrefs-confirmed). Tab 05: fill column F (Y/N) and column G (Keep/Disavow).")
cell=ws.cell(src_row,1,note); cell.font=F(9); cell.alignment=Alignment(vertical="center",wrap_text=True)
ws.row_dimensions[src_row].height=60

# ---- data tabs in signed order ----
write_tab('Referring Domain Audit', rda_h, rda, 15.75)
write_tab('All Backlinks', abl_h, abl, 22.5)
write_tab('Anchor Analysis',
          ['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains','Spam Domains Using It'],
          anchor_rows, 22.5)
write_tab('Exact Match Anchors', ema_h, ema, 22.5, input_cols=(6,7))
write_tab('Pending Disavow Lines', pend_h, pend, 22.5)
write_tab('Disavow List',
          ['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text'],
          dis_rows, 22.5)

# order sheets: Summary first
wb.move_sheet("Summary", -(len(wb.sheetnames)-1))
wb.save(OUTXLSX)
print("Saved", OUTXLSX, "sheets:", wb.sheetnames)
