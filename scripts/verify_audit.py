import sys, collections, re
import openpyxl
xlsx, disavow_txt = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(xlsx)
wbv = openpyxl.load_workbook(xlsx, data_only=True)
def rows(tab):
    ws=wbv[tab]; rr=list(ws.iter_rows(values_only=True)); h=[str(x).strip() if x else "" for x in rr[0]]
    return h,[r for r in rr[1:] if any(c is not None for c in r)]
fails=[]; oks=[]
def chk(cond,msg):
    (oks if cond else fails).append(msg)

# order
chk(wb.sheetnames==['Summary','Referring Domain Audit','All Backlinks','Anchor Analysis','Exact Match Anchors','Pending Disavow Lines','Disavow List'], f"tab order: {wb.sheetnames}")

rh,rda=rows('Referring Domain Audit'); ci={n:i for i,n in enumerate(rh)}
ah,abl=rows('All Backlinks'); ai={n:i for i,n in enumerate(ah)}
dh,dis=rows('Disavow List')
eh,ema=rows('Exact Match Anchors')
nh,anc=rows('Anchor Analysis')

# counts
dom_by=collections.Counter(str(r[ci['Status']]) for r in rda)
bl_by=collections.Counter(str(r[ai['Status']]) for r in abl)
chk(len(rda)==2683, f"RDA rows=2683 -> {len(rda)}")
chk(len(abl)==8086, f"All Backlinks rows=8086 -> {len(abl)}")
chk(dom_by['Spam (Disavow)']==1645, f"Spam(Disavow) domains=1645 -> {dom_by['Spam (Disavow)']}")
chk(dom_by['Keep']==849, f"Keep domains=849 -> {dom_by['Keep']}")
chk(bl_by['Spam (Disavow)']==1680, f"Spam(Disavow) backlinks=1680 -> {bl_by['Spam (Disavow)']}")
chk(bl_by['Keep']==5987, f"Keep backlinks=5987 -> {bl_by['Keep']}")
chk(sum(dom_by.values())==2683, "status domains sum to 2683")
chk(sum(bl_by.values())==8086, "status backlinks sum to 8086")

# disavow list integrity
chk(len(dis)==1645, f"Disavow List rows=1645 -> {len(dis)}")
dislines=[str(r[0]).strip() for r in dis]
chk(all(re.fullmatch(r'domain:[a-z0-9.\-]+', l) for l in dislines), "all disavow lines well-formed lowercase domain:")
chk(len(set(dislines))==len(dislines), "no duplicate disavow lines")
chk(not any('rosih.ru' in l for l in dislines), "rosih.ru NOT in disavow")
# every disavow domain is Spam(Disavow) with >=1 dofollow; no Held/Keep/Own leak
status_of={str(r[ci['Domain']]).lower():str(r[ci['Status']]) for r in rda}
dofo_of={str(r[ci['Domain']]).lower():r[ci['Dofollow Links']] for r in rda}
leak=[l for l in dislines if status_of.get(l.split('domain:')[1])!="Spam (Disavow)"]
chk(not leak, f"no non-spam leak in disavow ({len(leak)})")
nodofo=[l for l in dislines if not (dofo_of.get(l.split('domain:')[1]) or 0)>0]
chk(not nodofo, f"every disavow domain has >=1 dofollow ({len(nodofo)} missing)")

# In Disavow consistency
inconsistent=[r for r in rda if (str(r[ci['Status']])=="Spam (Disavow)") != (str(r[ci['In Disavow']])=="Yes")]
chk(not inconsistent, f"In-Disavow flag matches Spam(Disavow) status ({len(inconsistent)} off)")

# false-negative: no Keep/Held has dofollow spam-salescopy anchor
fn=[r for r in abl if str(r[ai['Status']]) in ("Keep",) and str(r[ai['Anchor Type']]).startswith("Spam") and str(r[ai['Link Type']])=="Dofollow"]
chk(not fn, f"no Keep domain carries a dofollow spam-anchor link ({len(fn)})")

# disavow.txt vs tab
txt=[l.strip() for l in open(disavow_txt) if l.strip() and not l.startswith('#')]
chk(len(txt)==1645, f"disavow.txt domain lines=1645 -> {len(txt)}")
chk(set(txt)==set(dislines), "disavow.txt set == Disavow List tab set")

# anchor analysis sums
chk(sum(int(r[2]) for r in anc)==8086, f"Anchor Analysis backlinks sum=8086 -> {sum(int(r[2]) for r in anc)}")

# styling spot checks (read back)
s=wb['Summary']; chk(s.sheet_view.showGridLines==False,"Summary gridlines off")
chk(round(s['B1'].font.size)==9 and s['B1'].font.bold,"B1 title Geist 9 bold (AUDIT_FORMAT)")
chk(s['B1'].font.name=="Geist","B1 font Geist")
chk(len(getattr(s,'_images',[]))==1,"logo present on Summary")
r2=wb['Referring Domain Audit']; chk(r2.freeze_panes=="B2","RDA freeze B2")
chk(r2['A1'].fill.fgColor.rgb=="FF0C343D" and r2['A1'].font.color.rgb=="FFFFFFFF","RDA header accent fill/white font")
chk(r2['A2'].border.left.style=="thin","RDA data cell bordered (AUDIT_FORMAT)")
chk(round(r2.row_dimensions[1].height,2)==31.5,"RDA header height 31.5")
e=wb['Exact Match Anchors']; chk(e['F2'].fill.fgColor.rgb=="FF0C343D","EMA partner input cell F accent-filled")

print("PASS:",len(oks)); print("FAIL:",len(fails))
for m in fails: print("  FAIL ->",m)
print("--- sample oks ---")
for m in oks[:6]: print("  ok:",m)
