import csv
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

TODAY='2026-11-02'
rows=list(csv.DictReader(open('out/domains_master.csv')))

KEEP={
 'bbb.org','yellowpages.com','yp.com','chamberofcommerce.com','dexknows.com','birdeye.com',
 '2findlocal.com','ibegin.com','mylocalservices.com','hometownguru.com','landscapeprofessionals.org',
 'superpages.com','bing.com','bingapis.com','brandfetch.com','cgmimm.com','rockwaterfarm.com',
 'completegardening.com','simplylawn.com','positivebloom.com','thelandscapeconnection.com',
 'lawnspedia.com','themowersguide.com','vohslandscaping.com','boyerslawncare.com',
 'averagedudeoutdoors.com','todayshomeowner.com','housemethod.com','landscapeleadership.com',
}
def status_of(b):
    if b in ('Spam (Disavow)','Spam (Disavow) [Semrush-only]','Review (Semrush-only)'): return 'Spam (Disavow)'
    if b=='Spam (Nofollow, No Action)': return 'Spam (Nofollow, No Action)'
    if b=='Held (Pending Partner)': return 'Held (Pending Partner)'
    if b=='Held (Nofollow, No Action)': return 'Held (Nofollow, No Action)'
    return 'Clean (No Action)'
ATYPE={'spam_sales':'Spam: keyword-stuffed SEO sales copy','telegram':'Spam: link-network / telegram advert',
 'ecom_injection':'Spam: injected e-commerce anchor','held_geo':'Exact-match commercial anchor (geo)',
 'held_commercial':'Exact-match commercial anchor','brand':'Brand / naked URL','other':'Other / editorial',
 'semrush_only':'(Semrush-only, anchor not retrieved)'}
def ig(x):
    try:return int(x)
    except:return 0
def df(x):
    try:return float(x.rstrip('.') or 0)
    except:return 0.0
for r in rows:
    r['status']=status_of(r['bucket'])
    d=r['domain'].strip().lower()
    r['in_disavow']='Yes' if d not in KEEP else 'No'
    bl=ig(r['links_grouped']) or (1 if r['source']=='Semrush' else 0)
    r['backlinks']=bl
    r['dofollow_links']=bl if r['is_dofollow']=='dofollow' else 0
    r['nofollow_links']=bl if r['is_dofollow']=='nofollow' else ''
    r['atype']=ATYPE.get(r['anchor_class'],'')

wb=openpyxl.Workbook()
HDR=Font(bold=True,color='FFFFFF'); HFILL=PatternFill('solid',fgColor='374151')
def sh(ws,row=1):
    for c in ws[row]: c.font=HDR; c.fill=HFILL; c.alignment=Alignment(vertical='center')
    ws.freeze_panes=ws.cell(row=row+1,column=1).coordinate

# ---- Summary ----
ws=wb.active; ws.title='Summary'
ws.append(['callturfsup.com']); ws['A1'].font=Font(bold=True,size=14)
ws.append([])
ws.append(['Status','Domains','Backlinks','Share of Domains','What it means'])
order=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Spam (Nofollow, No Action)','Clean (No Action)']
mean={
 'Spam (Disavow)':'Spam / link-scheme / PBN / brand-mention-farm. Disavowed in the complete file.',
 'Held (Pending Partner)':'Exact-match Gainesville/Haymarket commercial anchor. Folded into the complete disavow (Harbinger gate waived).',
 'Held (Nofollow, No Action)':'Exact-match commercial but all-nofollow; disavowed in complete file for completeness.',
 'Spam (Nofollow, No Action)':'Spam but all-nofollow (passes no value); disavowed in complete file for completeness.',
 'Clean (No Action)':'Brand mentions / editorial; 26 genuine citations kept, the rest disavowed in complete file.',
}
tot=len(rows)
for s in order:
    recs=[r for r in rows if r['status']==s]
    ws.append([s,len(recs),sum(r['backlinks'] for r in recs),round(len(recs)/tot,4),mean[s]])
disN=sum(1 for r in rows if r['in_disavow']=='Yes')
ws.append(['TOTAL',tot,sum(r['backlinks'] for r in rows),1.0,f'{disN} domains in complete disavow; {tot-disN} kept (legitimate).'])
for c in ws[3]: c.font=HDR; c.fill=HFILL
ws.column_dimensions['A'].width=30; ws.column_dimensions['E'].width=95
for col in 'BCD': ws.column_dimensions[col].width=14

# ---- Referring Domain Audit ----
ws=wb.create_sheet('Referring Domain Audit')
cols=['Domain','Status','AS','Backlinks','RD\'s','Traffic','In Disavow','Links Point To','Dofollow Links',
 'Nofollow Links','First Seen','Top Anchor Text','Example Linking Page','Linking Page Title','Source','IP','Disavow Line']
ws.append(cols)
for r in sorted(rows,key=lambda x:(x['status'],x['domain'])):
    ws.append([r['domain'],r['status'],r['as_semrush'],r['backlinks'],'',r['traffic'],r['in_disavow'],
     r['target_url'],r['dofollow_links'],r['nofollow_links'],r['first_seen'],r['top_anchor'],
     r['example_page'],'',r['source'],r['ip'],(f"domain:{r['domain']}" if r['in_disavow']=='Yes' else '')])
sh(ws)
for col,w in {'A':30,'B':24,'L':50,'M':40}.items(): ws.column_dimensions[col].width=w

# ---- All Backlinks (1 representative per domain) ----
ws=wb.create_sheet('All Backlinks')
ws.append(['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL','Linking Page Title','Target URL'])
for r in sorted(rows,key=lambda x:x['domain']):
    if r['source']=='Semrush': continue
    ws.append([r['domain'],r['status'],'Ahrefs',r['top_anchor'],r['atype'],'text',r['example_page'],'',r['target_url']])
sh(ws)
for col,w in {'A':30,'D':55,'E':34,'G':45,'I':40}.items(): ws.column_dimensions[col].width=w

# ---- Anchor Analysis ----
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains','Spam Domains Using It'])
dom_by_anchor=defaultdict(list)
for r in rows:
    if r['source']!='Semrush': dom_by_anchor[r['top_anchor']].append(r)
totbl=sum(r['backlinks'] for r in rows if r['source']!='Semrush') or 1
for a,recs in sorted(dom_by_anchor.items(),key=lambda kv:-len(kv[1])):
    bl=sum(x['backlinks'] for x in recs)
    spamdom=sum(1 for x in recs if x['status'] in ('Spam (Disavow)','Spam (Nofollow, No Action)'))
    ws.append([a,recs[0]['atype'],bl,round(bl/totbl,4),len(recs),spamdom])
sh(ws)
ws.column_dimensions['A'].width=70; ws.column_dimensions['B'].width=34
for col in ['C','D','E','F']: ws.column_dimensions[col].width=18

# ---- Exact Match Anchors ----
ws=wb.create_sheet('Exact Match Anchors')
ws.append(['Referring domain','Example backlink (linking page)','Exact-match commercial anchor','Market','Site type (indicative)','Partner confirmed? (Y/N)','Final decision'])
def market(a):
    al=a.lower()
    if 'gainesville' in al:return 'Gainesville, VA'
    if 'haymarket' in al:return 'Haymarket, VA'
    if 'south riding' in al:return 'South Riding, VA'
    if 'virginia' in al or ' va' in al:return 'Northern VA'
    return 'Non-geo'
def sitetype(d):
    dl=d.lower()
    if any(k in dl for k in ('bookmark','directory','dir.','listing','submit','list','pages')):return 'Low-quality web directory / bookmark'
    if any(k in dl for k in ('news','times','journal','report','magazine','daily','watch','ledger','gazette')):return 'PBN / news-style site'
    return 'Unknown'
em=[r for r in rows if r['anchor_class'] in ('held_geo','held_commercial')]
for r in sorted(em,key=lambda x:(x['is_dofollow'],x['domain'])):
    ws.append([r['domain'],r['example_page'],r['top_anchor'],market(r['top_anchor']),sitetype(r['domain']),'',
               'Disavow (included in complete file; Harbinger gate waived)'])
sh(ws)
for col,w in {'A':30,'B':45,'C':48,'G':48}.items(): ws.column_dimensions[col].width=w

# ---- Pending Disavow Lines ----
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation'])
for r in sorted(em,key=lambda x:x['domain']):
    rec='Included in complete disavow. (Exact-match commercial anchor - ideally confirm with Harbinger who commissioned it.)'
    ws.append([r['domain'],f"domain:{r['domain']}",rec])
sh(ws)
ws.column_dimensions['A'].width=30; ws.column_dimensions['B'].width=48; ws.column_dimensions['C'].width=70

# ---- Disavow List ----
ws=wb.create_sheet('Disavow List')
ws.append(['Disavow Line','AS','Backlinks','RD\'s','Traffic','Organic Keywords','Top Anchor Text'])
for r in sorted([x for x in rows if x['in_disavow']=='Yes'],key=lambda x:x['domain']):
    ws.append([f"domain:{r['domain']}",r['as_semrush'],r['backlinks'],'',r['traffic'],'',r['top_anchor']])
sh(ws)
ws.column_dimensions['A'].width=36; ws.column_dimensions['G'].width=60

wb.save('out/CallTurfsUp_Backlinks_Audit.xlsx')
print('sheets:',wb.sheetnames)
print('rows:',len(rows),'| disavow:',disN,'| kept:',tot-disN)
for s in order: print(' ',s,sum(1 for r in rows if r['status']==s))
