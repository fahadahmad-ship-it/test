import csv
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image as XLImage

TEAL='FF0C343D'
HFONT=Font(name='Geist', size=9, bold=True, color='FFFFFFFF')
HFONT10=Font(name='Geist', size=10, bold=True, color='FFFFFFFF')
BFONT=Font(name='Geist', size=9, color='FF000000')
TITLE=Font(name='Geist', size=14, bold=True, color='FF0C343D')
HFILL=PatternFill('solid', fgColor=TEAL)
VC=Alignment(vertical='center')

rows=list(csv.DictReader(open('out/domains_master.csv')))
KEEP={'bbb.org','yellowpages.com','yp.com','chamberofcommerce.com','dexknows.com','birdeye.com',
 '2findlocal.com','ibegin.com','mylocalservices.com','hometownguru.com','landscapeprofessionals.org',
 'superpages.com','bing.com','bingapis.com','brandfetch.com','cgmimm.com','rockwaterfarm.com',
 'completegardening.com','simplylawn.com','positivebloom.com','thelandscapeconnection.com','lawnspedia.com',
 'themowersguide.com','vohslandscaping.com','boyerslawncare.com','averagedudeoutdoors.com',
 'todayshomeowner.com','housemethod.com','landscapeleadership.com'}
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

def setw(ws, widths):
    for col,w in widths.items(): ws.column_dimensions[col].width=w
def hdrrow(ws, r, big=False):
    for c in ws[r]:
        if c.value is None: continue
        c.font=HFONT10 if big else HFONT; c.fill=HFILL; c.alignment=VC
def body(ws, start):
    for row in ws.iter_rows(min_row=start):
        for c in row:
            if c.font is BFONT: continue
            c.font=BFONT
def rowh(ws, h, hdr_r=1, hdr_h=31.5):
    ws.sheet_format.defaultRowHeight=h; ws.sheet_format.customHeight=True
    ws.row_dimensions[hdr_r].height=hdr_h

# ---------- Summary ----------
ws=wb.active; ws.title='Summary'
ws['B1']='callturfsup.com'; ws['B1'].font=TITLE
ws.append([]) # placeholder won't work after direct set; build manually
# rebuild rows explicitly
ws['A3']='Status'; ws['B3']='Domains'; ws['C3']='Backlinks'; ws['D3']='Share of Domains'; ws['E3']='What it means'
order=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Spam (Nofollow, No Action)','Clean (No Action)']
mean={'Spam (Disavow)':'Spam / link-scheme / PBN / brand-mention-farm. In the disavow file.',
 'Held (Pending Partner)':'Exact-match Gainesville/Haymarket commercial anchor. Folded into complete disavow (confirm commissioning).',
 'Held (Nofollow, No Action)':'Exact-match commercial but all-nofollow; included in complete file.',
 'Spam (Nofollow, No Action)':'Spam but all-nofollow (passes no value); included in complete file.',
 'Clean (No Action)':'Brand mentions / editorial; 26 genuine citations kept, the rest disavowed.'}
tot=len(rows); rr=4
for s in order:
    recs=[r for r in rows if r['status']==s]
    ws.cell(rr,1,s); ws.cell(rr,2,len(recs)); ws.cell(rr,3,sum(x['backlinks'] for x in recs))
    ws.cell(rr,4,round(len(recs)/tot,4)); ws.cell(rr,5,mean[s]); rr+=1
disN=sum(1 for r in rows if r['in_disavow']=='Yes')
ws.cell(rr,1,'TOTAL'); ws.cell(rr,2,tot); ws.cell(rr,3,sum(x['backlinks'] for x in rows)); ws.cell(rr,4,1.0)
ws.cell(rr,5,f'{disN} domains in complete disavow; {tot-disN} legitimate kept.')
body(ws,3); hdrrow(ws,3)
ws.cell(rr,1).font=Font(name='Geist',size=9,bold=True); ws.cell(rr,2).font=Font(name='Geist',size=9,bold=True)
setw(ws,{'A':38.9,'B':16.3,'C':17.6,'D':18.7,'E':120})
for i in range(1,rr+1): ws.row_dimensions[i].height=22.5
try:
    img=XLImage('assets/image1.png'); img.width=186; img.height=55; ws.add_image(img,'A1')
except Exception as e: print('logo skip:',e)

# ---------- helper to build a data sheet ----------
def datasheet(title, headers, records, widths, bodyh=22.5, big_hdr=False):
    ws=wb.create_sheet(title)
    ws.append(headers)
    for rec in records: ws.append(rec)
    hdrrow(ws,1); body(ws,2); ws.freeze_panes='B2'
    setw(ws,widths); rowh(ws,bodyh)
    return ws

# Referring Domain Audit
rda=[]
for r in sorted(rows,key=lambda x:(x['status'],x['domain'])):
    rda.append([r['domain'],r['status'],r['as_semrush'],r['backlinks'],'',r['traffic'],r['in_disavow'],
      r['target_url'],r['dofollow_links'],r['nofollow_links'],r['first_seen'],r['top_anchor'],
      r['example_page'],'',r['source'],r['ip'],(f"domain:{r['domain']}" if r['in_disavow']=='Yes' else '')])
datasheet('Referring Domain Audit',
  ['Domain','Status','AS','Backlinks',"RD's",'Traffic','In Disavow','Links Point To','Dofollow Links',
   'Nofollow Links','First Seen','Top Anchor Text','Example Linking Page','Linking Page Title','Source','IP','Disavow Line'],
  rda, {'A':36,'B':24.7,'C':9.6,'D':13,'E':9.4,'F':9.7,'G':12.4,'H':21.3,'I':14,'J':8.7,'K':12,'L':45,'M':8.7,'N':40,'O':14,'P':15,'Q':14},
  bodyh=15.75)

# All Backlinks
ab=[[r['domain'],r['status'],'Ahrefs',r['top_anchor'],r['atype'],'text',r['example_page'],'',r['target_url']]
    for r in sorted(rows,key=lambda x:x['domain']) if r['source']!='Semrush']
datasheet('All Backlinks',
  ['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL','Linking Page Title','Target URL'],
  ab, {'A':25.4,'B':27.1,'C':14.7,'D':55,'E':32,'F':10,'G':55,'H':53.1,'I':30.6})

# Anchor Analysis
dba=defaultdict(list)
for r in rows:
    if r['source']!='Semrush': dba[r['top_anchor']].append(r)
totbl=sum(r['backlinks'] for r in rows if r['source']!='Semrush') or 1
aa=[]
for a,recs in sorted(dba.items(),key=lambda kv:-len(kv[1])):
    bl=sum(x['backlinks'] for x in recs)
    sd=sum(1 for x in recs if x['status'] in ('Spam (Disavow)','Spam (Nofollow, No Action)'))
    aa.append([a,recs[0]['atype'],bl,round(bl/totbl,4),len(recs),sd])
datasheet('Anchor Analysis',
  ['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains','Spam Domains Using It'],
  aa, {'A':115.9,'B':37.7,'C':14,'D':8.7,'E':18,'F':20.3})

# Exact Match Anchors
def market(a):
    al=a.lower()
    for k,v in [('gainesville','Gainesville, VA'),('haymarket','Haymarket, VA'),('south riding','South Riding, VA')]:
        if k in al: return v
    return 'Northern VA' if ('virginia' in al or ' va' in al) else 'Non-geo'
def sitetype(d):
    dl=d.lower()
    if any(k in dl for k in ('bookmark','directory','dir.','listing','submit','list','pages')): return 'Low-quality web directory / bookmark'
    if any(k in dl for k in ('news','times','journal','report','magazine','daily','watch','ledger','gazette')): return 'PBN / news-style site'
    return 'Unknown'
em=[r for r in rows if r['anchor_class'] in ('held_geo','held_commercial')]
ema=[[r['domain'],r['example_page'],r['top_anchor'],market(r['top_anchor']),sitetype(r['domain']),'',
      'Disavow (in complete file; confirm commissioning)'] for r in sorted(em,key=lambda x:(x['is_dofollow'],x['domain']))]
datasheet('Exact Match Anchors',
  ['Referring domain','Example backlink (linking page)','Exact-match commercial anchor','Market','Site type (indicative)','Partner confirmed? (Y/N)','Final decision'],
  ema, {'A':25.4,'B':59,'C':53.1,'D':16,'E':24.6,'F':15.4,'G':15})

# Pending Disavow Lines
pdl=[[r['domain'],f"domain:{r['domain']}",'Included in complete disavow. Exact-match commercial anchor - confirm with Harbinger who commissioned it.']
     for r in sorted(em,key=lambda x:x['domain'])]
datasheet('Pending Disavow Lines',
  ['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation'],
  pdl, {'A':32,'B':44,'C':48})

# Disavow List
dl=[[f"domain:{r['domain']}",r['as_semrush'],r['backlinks'],'',r['traffic'],'',r['top_anchor']]
    for r in sorted([x for x in rows if x['in_disavow']=='Yes'],key=lambda x:x['domain'])]
datasheet('Disavow List',
  ['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text'],
  dl, {'A':44,'B':14,'C':15.6,'D':14,'E':11.1,'F':14.9,'G':98.9})

wb.save('out/CallTurfsUp_Backlinks_Audit.xlsx')
print('saved. sheets:',wb.sheetnames,'| rows:',tot,'| disavow:',disN)
