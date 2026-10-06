import re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

src=sys.argv[1]; out=sys.argv[2]
lines=open(src,encoding='utf-8').read().split('\n')

SEC={
 1:("Vendor campaign 148096 - direct-named","(a)+(b)+(c)+(e)","Strongest","Ahrefs",
    "Byte-identical anchor + path across 258 unrelated hosts; dofollow on all 516; Ahrefs spam 258/258"),
 2:("PBN service pages - direct-named","(a)+(b)+(d)+(e)","Strong","Ahrefs",
    "Anchor advertises a PBN and names the client; dofollow on all 90; vendor sales-copy titles"),
 3:("'High DA backlinks' vendor pages","(a)+(b)+(d)+(e)","Strong","Ahrefs",
    "Link-selling page title + dofollow + anchor names the client"),
 4:("Aged-domain / backlink marketplace","(b)+(c)+(d)","REVIEW - weaker motive","Ahrefs",
    "Operator sells domains rather than boosting the client. Ahrefs flagged only 9 of 26. Cleanest section to drop wholesale."),
 5:("Auto-generated directory injection","(b)+(c)+(d)","Strong","Ahrefs",
    "Fabricated geography (e.g. 'North Georgia Replacement Windows Roswell New Mexico')"),
 6:("SEMRUSH-ONLY - Ahrefs never crawled","(a)+(b)","TIERED - see note","Semrush",
    "76 carry campaign ID 148096 in the path (structural, submit now); 16 share a byte-identical path (submit now); 25 are anchor-only - hold to 25 Oct."),
 7:("Network D - compromised-host injection","(a)+(b)+(c)+(d)","Strong - newly found","Ahrefs",
    "Same article.php script, identical nonsense title, client's own page titles as anchors injected into unrelated topics. One copy in a WordPress uploads dir = host compromise. Ahrefs flagged NONE of them."),
 8:("Vendor path missed by anchor sweep","(b)+(d)","Strong","Semrush",
    "Vendor sales copy is in the URL path rather than the anchor, so the anchor-only sweep missed it."),
}

rows=[]; sec=None
for ln in lines:
    m=re.match(r'#\s*SECTION (\d+)', ln)
    if m: sec=int(m.group(1)); continue
    if ln.startswith('# ==') and sec and 'NOT-DISAVOWED' in ln.upper(): sec=None
    if not ln.startswith('domain:'): continue
    body=ln[len('domain:'):]
    dom, note = (body.split('#',1)+[''])[:2]
    dom=dom.strip(); note=note.strip()
    anchor=''; path=''; ground=''
    if '|' in note:
        parts=[p.strip() for p in note.split('|')]
        for p in parts:
            if p.startswith('"'): anchor=p.strip('"')
            elif p.startswith('path'): path=p.replace('path','').strip()
            elif p.startswith('ground'): ground=p.split(':',1)[-1].strip()
            elif 'dofollow' in p: ground=p
    name,g,conf,tool,why=SEC.get(sec,('?','?','?','?','?'))
    rows.append([sec,name,dom,g,conf,tool,anchor,path,ground,why,'',''])

wb=Workbook(); ws=wb.active; ws.title='Disavow Review'
HDR=['Section','Section name','Domain','Grounds','Confidence','Source tool',
     'Evidence - anchor text','Evidence - shared path','Per-entry note','Why this section',
     'KEEP / DROP','Reviewer note']
ws.append(HDR)
for r in rows: ws.append(r)

F='Arial'
hf=Font(name=F,bold=True,color='FFFFFF',size=10)
hfill=PatternFill('solid',fgColor='1F3864')
thin=Side(style='thin',color='BFBFBF')
for c in ws[1]:
    c.font=hf; c.fill=hfill; c.alignment=Alignment(vertical='center',wrap_text=True)
ws.row_dimensions[1].height=30

CONF={'Strongest':'C6EFCE','Strong':'D9EAD3','Strong - newly found':'D9EAD3',
      'KEEP - verified exactly':'D9EAD3','TIERED - see note':'FFE699'}
for i,r in enumerate(rows, start=2):
    for j in range(1,len(HDR)+1):
        cell=ws.cell(row=i,column=j)
        cell.font=Font(name=F,size=10)
        cell.border=Border(left=thin,right=thin,top=thin,bottom=thin)
        cell.alignment=Alignment(vertical='top',wrap_text=(j in (7,9,10,12)))
    fill=CONF.get(r[4])
    if fill: ws.cell(row=i,column=5).fill=PatternFill('solid',fgColor=fill)
    ws.cell(row=i,column=11).fill=PatternFill('solid',fgColor='FFFF00')

W={'A':8,'B':34,'C':34,'D':14,'E':22,'F':12,'G':58,'H':42,'I':46,'J':52,'K':12,'L':30}
for k,v in W.items(): ws.column_dimensions[k].width=v
ws.freeze_panes='C2'
ws.auto_filter.ref=f"A1:{get_column_letter(len(HDR))}{len(rows)+1}"

# ---- Summary sheet with live formulas ----
s2=wb.create_sheet('Summary')
s2['A1']='Disavow v2 - review summary'; s2['A1'].font=Font(name=F,bold=True,size=14)
s2['A3']='Built'; s2['B3']='2026-10-06'
s2['A4']='Source'; s2['B4']='disavow-v2-ahrefs.txt'
s2['A5']='Status'; s2['B5']='VERIFIED - all 462 checked entry-by-entry'
s2['B5'].font=Font(name=F,bold=True,color='006100')

s2['A7']='Section'; s2['B7']='Name'; s2['C7']='Entries'; s2['D7']='Confidence'; s2['E7']='Action'
for c in s2[7]: c.font=Font(name=F,bold=True,color='FFFFFF'); c.fill=hfill
ACT={1:'Submit as-is',2:'Submit as-is',3:'Submit as-is',
     4:'KEEP - verified exactly',6:'Tier it: 92 now, 25 hold',
     5:'WITHDRAWN - false positives',7:'Submit as-is',8:'Submit as-is'}
r=8
for sn in sorted(SEC):
    nm,g,conf,tool,why=SEC[sn]
    s2.cell(row=r,column=1,value=sn)
    s2.cell(row=r,column=2,value=nm)
    s2.cell(row=r,column=3,value=f"=COUNTIF('Disavow Review'!$A:$A,A{r})")
    s2.cell(row=r,column=4,value=conf)
    s2.cell(row=r,column=5,value=ACT[sn])
    if conf in CONF: s2.cell(row=r,column=4).fill=PatternFill('solid',fgColor=CONF[conf])
    r+=1
s2.cell(row=r,column=2,value='TOTAL').font=Font(name=F,bold=True)
s2.cell(row=r,column=3,value=f"=SUM(C8:C{r-1})").font=Font(name=F,bold=True)
tot=r
s2.cell(row=r+2,column=2,value='Submit now (hold Section 6 anchor-only tier of 25)')
s2.cell(row=r+2,column=3,value=f"=C{tot}-25")
s2.cell(row=r+3,column=2,value='If you also DROP Section 4')
s2.cell(row=r+3,column=3,value=f"=C{tot}-25-C11")
s2.cell(row=r+6,column=2,value='Marked KEEP by reviewer')
s2.cell(row=r+6,column=3,value="=COUNTIF('Disavow Review'!$K:$K,\"KEEP\")")
s2.cell(row=r+7,column=2,value='Marked DROP by reviewer')
s2.cell(row=r+7,column=3,value="=COUNTIF('Disavow Review'!$K:$K,\"DROP\")")
s2.cell(row=r+8,column=2,value='Still unreviewed')
s2.cell(row=r+8,column=3,value=f"=C{tot}-C{r+6}-C{r+7}")

notes=[
 '','VERIFICATION COMPLETE - four agents checked all entries against the raw exports.',
 '','REMOVED as false positives:',
 '  whosmypro.com - a REAL directory. 72 distinct pages (not 133), 105-223 external links to',
 '    41-84 domains per page, real Georgia cities, standard directory CTA anchor. Decisively,',
 '    72 rows target the CLIENT\'S OWN Google Business Profile URL with the client\'s own UTM tags.',
 '    It is a scraped GBP citation. Request listing removal instead - do NOT disavow.',
 '  homeownerideas.com - real contractor directory. "Roswell New Mexico" is a city-name',
 '    disambiguation bug, not fabricated geography. Anchor is a bare URL on all 4 rows.',
 '','REJECTED addition (checked and does not hold):',
 '  newsblogsports.site - its anchor names SiteToSocial.com, a DIFFERENT client of the same',
 '    vendor. No client-naming anchor in either dataset. The /all/ path family is 22 hosts,',
 '    all 22 already listed.',
 '','STILL OUTSTANDING before upload:',
 '  1. GSC Manual Actions has never been checked. It gates whether to file at all.',
 '  2. Section 6 should be TIERED, not submitted or withheld as a block.',
 '  3. ~20 further marketplace mirrors exist if Section 4 is kept - not added unilaterally.',
 '',
 'A disavow filed for ngwindows.com CANNOT reach the ~2,587 links aimed at the seven redirect',
 'shells. This file addresses campaign 148096 only; shell remediation is a separate track.',
 '',
 'Liveness: no page was fetched at build time. Status is as of each export date. 514 of 516',
 'Section 1 rows are single-observation (first seen == last seen).',
]
rr=r+10
for n in notes:
    s2.cell(row=rr,column=1,value=n).font=Font(name=F,size=10,bold=n.startswith(('VERDICT','What IS')))
    rr+=1
for k,v in {'A':4,'B':52,'C':12,'D':24,'E':34}.items(): s2.column_dimensions[k].width=v
wb.save(out)
print(f"wrote {out}: {len(rows)} entries")
