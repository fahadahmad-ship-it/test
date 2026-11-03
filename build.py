import sys, json, re, copy
import openpyxl
from collections import Counter, defaultdict
SRC=sys.argv[1]; MOVE=json.load(open(sys.argv[2])); OUT="/home/user/test/NewGarden_Backlinks_Audit.xlsx"
move_do=set(MOVE['move_dofollow']); move_no=set(MOVE['move_nofollow']); moved=move_do|move_no
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^https?://','',s).rstrip('/')
wb=openpyxl.load_workbook(SRC)

# ---------- gather exact-match example per moved domain from All Backlinks ----------
ab=wb["All Backlinks"]; abh=[c.value for c in ab[1]]; Ai={h:i for i,h in enumerate(abh)}
examples={}
for row in ab.iter_rows(min_row=2):
    dom=norm(row[Ai['Referring Domain']].value)
    if dom in moved and 'exact match commercial' in str(row[Ai['Anchor Type']].value).lower():
        url=row[Ai['Linking Page URL']].value; anc=row[Ai['Anchor Text']].value
        isdo=str(row[Ai['Link Type']].value).lower().startswith('dofollow')
        if dom not in examples or (isdo and not examples[dom][2]):
            examples[dom]=(url,anc,isdo)

# ---------- 1. All Backlinks: update Status ----------
sc=Ai['Status']
for row in ab.iter_rows(min_row=2):
    dom=norm(row[Ai['Referring Domain']].value)
    if dom in move_do: row[sc].value='Held (Pending Partner)'
    elif dom in move_no: row[sc].value='Held (Nofollow, No Action)'

# ---------- 2. Referring Domain Audit: update Status; collect counts ----------
rda=wb["Referring Domain Audit"]; rh=[c.value for c in rda[1]]; Ri={h:i for i,h in enumerate(rh)}
dom_status={}; dom_bl={}
for row in rda.iter_rows(min_row=2):
    dom=norm(row[Ri['Domain']].value)
    if dom in move_do: row[Ri['Status']].value='Held (Pending Partner)'
    elif dom in move_no: row[Ri['Status']].value='Held (Nofollow, No Action)'
    dom_status[dom]=row[Ri['Status']].value; dom_bl[dom]=row[Ri['Backlinks']].value or 0

# ---------- helper to clone a cell's style ----------
def clone(dst, src):
    dst._style=copy.copy(src._style)

# ---------- 3. Rebuild Exact Match Anchors (Tab 05) sorted, keep existing + append ----------
em=wb["Exact Match Anchors"]
existing=[[c.value for c in row] for row in em.iter_rows(min_row=2) if any(c.value is not None for c in row)]
have={norm(r[0]) for r in existing}
newrows=[]
for dom in sorted(moved):
    if dom in have: continue
    url,anc,_=examples.get(dom,(None,None,False))
    lo=str(anc).lower()
    market='Winston-Salem' if 'winston' in lo else ('Greensboro' if 'greensboro' in lo else 'Non-geo')
    newrows.append([dom,url,anc,market,'Directory / blog (review source quality)',None,None])
allrows=existing+newrows; allrows.sort(key=lambda r: norm(r[0]))
tpl=[em.cell(row=2,column=c) for c in range(1,8)]
for i,rowvals in enumerate(allrows):
    rr=2+i
    for c in range(1,8):
        cell=em.cell(row=rr,column=c); cell.value=rowvals[c-1]; clone(cell,tpl[c-1])
# clear any leftover rows if new <old (not the case here)
em.auto_filter.ref=f"A1:G{1+len(allrows)}"
tab05_count=len(allrows)

# ---------- 4. Rebuild Pending Disavow Lines (add dofollow movers), fix header ----------
pend=wb["Pending Disavow Lines"]
pex=[[c.value for c in row] for row in pend.iter_rows(min_row=2) if any(c.value is not None for c in row)]
phave={norm(r[0]) for r in pex}
rec="Append ONLY if the previous SEO partner does not confirm this was a commissioned placement."
for dom in sorted(move_do):
    if dom in phave: continue
    pex.append([dom,f"domain:{dom}",rec])
pex.sort(key=lambda r: norm(r[0]))
ptpl=[pend.cell(row=2,column=c) for c in range(1,4)]
for i,rowvals in enumerate(pex):
    rr=2+i
    for c in range(1,4):
        cell=pend.cell(row=rr,column=c); cell.value=rowvals[c-1]; clone(cell,ptpl[c-1])
pend.auto_filter.ref=f"A1:C{1+len(pex)}"
pend["B1"].value="Disavow line (append to disavow.txt once confirmed)"  # match signed format
pending_count=len(pex)

# ---------- 5. Summary recompute + 7 findings + style fixes ----------
from openpyxl.styles import Font, Alignment
sm=wb["Summary"]
order=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Spam (Nofollow, No Action)','Keep','Own Site']
dcount=Counter(dom_status.values()); blby=defaultdict(int)
for d,st in dom_status.items(): blby[st]+=dom_bl.get(d,0)
tot_d=sum(dcount.values()); tot_b=sum(blby.values())
desc={
 'Spam (Disavow)':"Confirmed spam with at least one dofollow link. Included in the disavow file.",
 'Held (Pending Partner)':"Exact-match commercial / geo anchor, or a link aimed at a deep money page. MAY be a commissioned placement. Out of the disavow file until the previous SEO supplier (the 'partner') confirms.",
 'Held (Nofollow, No Action)':"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 'Spam (Nofollow, No Action)':"Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 'Keep':"Genuine, branded or harmless link (incl. editorial citations, press, and the plants.newgarden.com catalogue). Keep.",
 'Own Site':"Client-owned domain that redirects into the site.",
}
for i,st in enumerate(order):
    r=4+i
    sm.cell(row=r,column=1).value=st
    sm.cell(row=r,column=2).value=dcount.get(st,0)
    sm.cell(row=r,column=3).value=blby.get(st,0)
    sm.cell(row=r,column=4).value=(dcount.get(st,0)/tot_d if tot_d else 0)
    sm.cell(row=r,column=5).value=desc[st]
sm.cell(row=10,column=1).value="Total"; sm.cell(row=10,column=2).value=tot_d
sm.cell(row=10,column=3).value=tot_b; sm.cell(row=10,column=4).value=1

# unmerge everything from row 11 down (and title) then re-merge as needed
for mr in list(sm.merged_cells.ranges):
    if mr.min_row>=11 or (mr.min_row==1): sm.unmerge_cells(str(mr))

spam_total=dcount['Spam (Disavow)']+dcount['Spam (Nofollow, No Action)']
held_total=dcount['Held (Pending Partner)']+dcount['Held (Nofollow, No Action)']
findings=[
 f"{spam_total:,} of {tot_d:,} referring domains are spam. {dcount['Spam (Disavow)']:,} carry a dofollow link and go in the disavow file; {dcount['Spam (Nofollow, No Action)']} are nofollow and need no action.",
 f"The attack is recent. Referring domains sat near 700-1,200 for most of the past year, then jumped from ~1,170 in Sep 2026 to ~2,640 in Oct. The live profile (Semrush, 2026-11-03) is {tot_d:,} domains / {tot_b:,} backlinks - matching this workbook exactly.",
 "One disavow file covers newgarden.com. No client-owned redirect domains were found (Own Site = 0); a domain-level property covers the www., plants. and estimate. subdomains, so a single file is enough.",
 "Two patterns, easy to tell apart. The link-scheme flood points at the home page; the commissioned-looking geo campaign points at deep /service/ and /location/ pages (Greensboro and Winston-Salem).",
 "The biggest single anchor, on 1,469 domains, is SEO sales copy naming the site ('Build Powerful Website Authority with Premium SEO Backlinks newgarden.com'). This is auto-generated spam, not links the client bought.",
 f"{held_total} domains are held for the previous SEO supplier to confirm, in case any were paid placements ({dcount['Held (Pending Partner)']} dofollow in the pending file, {dcount['Held (Nofollow, No Action)']} nofollow = no action). They are one directory/bookmark vendor network using local-service anchors.",
 "Held does not mean valuable: almost all held domains sit at Authority Score 2-3 with no organic traffic. Disavow only if Search Console shows a manual action or the supplier confirms buying links; otherwise monitor.",
]
sm.cell(row=11,column=1).value="Key findings"
sm.cell(row=11,column=1).font=Font(name="Geist",size=10,bold=True,color="FF000000")
base_find=sm.cell(row=4,column=1)  # for a data-ish font baseline
for i,ftext in enumerate(findings):
    r=12+i
    c=sm.cell(row=r,column=1); c.value=ftext
    c.font=Font(name="Geist",size=9,bold=False,color="FF000000")
    c.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)
    sm.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5)
    sm.row_dimensions[r].height=22.5
# Anchor text profile section: heading row 19, header row 20, data 21-28 (preserve old values from rows 22-29)
old_anchor=[]
# old anchor table was rows 22..29 in the source (read from a fresh copy to avoid our edits—values unchanged)
srcwb=openpyxl.load_workbook(SRC, data_only=True); ssm=srcwb["Summary"]
for r in range(22,30):
    old_anchor.append([ssm.cell(row=r,column=c).value for c in range(1,5)])
# clear rows 19..31 then write
for r in range(19,32):
    for c in range(1,6):
        cell=sm.cell(row=r,column=c); cell.value=None
sm.cell(row=19,column=1).value="Anchor text profile (all backlinks)"
sm.cell(row=19,column=1).font=Font(name="Geist",size=11,bold=True,color="FF0C343D")
hdr=["Anchor type","Backlinks","Share of Backlinks","Referring Domains"]
from openpyxl.styles import PatternFill
accent=PatternFill("solid",fgColor="FF0C343D")
for c in range(1,5):
    cell=sm.cell(row=20,column=c); cell.value=hdr[c-1]
    cell.font=Font(name="Geist",size=9,bold=True,color="FFFFFFFF")
    cell.fill=accent; cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
for i,rowv in enumerate(old_anchor):
    r=21+i
    for c in range(1,5):
        cell=sm.cell(row=r,column=c); cell.value=rowv[c-1]
        cell.font=Font(name="Geist",size=9,bold=False,color="FF000000")
        cell.fill=PatternFill("solid",fgColor="FFFFFFFF")
# source note row 30
src=sm.cell(row=30,column=1)
src.value=("Source: Semrush Backlink Analytics export, 2026-11-03 ({:,} backlinks / {:,} referring domains); "
           "cross-checked against Ahrefs. AS = Semrush Authority Score (0-100). Semrush's referring-domains export has no per-domain "
           "RD/traffic, so those columns in Tab 02 are blank. Anchor-type profile covers all backlinks. "
           "Tab 05: supplier fills columns F (Y/N) and G (Keep/Disavow).").format(tot_b,tot_d)
src.font=Font(name="Geist",size=8,bold=False,color="FF666666")
src.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)
sm.merge_cells("A30:E30")
# title merge
sm.merge_cells("B1:E2")

wb.save(OUT)
print("SAVED",OUT)
print("Tab05 rows:",tab05_count," Pending rows:",pending_count)
print("Status counts:",dict(dcount)," total_d:",tot_d," total_b:",tot_b)
