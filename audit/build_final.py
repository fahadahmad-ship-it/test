import csv, datetime
from collections import defaultdict, Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image as XLImage

TEAL='FF0C343D'
HFONT=Font(name='Geist', size=9, bold=True, color='FFFFFFFF')
BFONT=Font(name='Geist', size=9, color='FF000000')
BOLD=Font(name='Geist', size=9, bold=True, color='FF000000')
SECT=Font(name='Geist', size=10, bold=True, color='FF0C343D')
TITLE=Font(name='Geist', size=14, bold=True, color='FF0C343D')
HFILL=PatternFill('solid', fgColor=TEAL)
VC=Alignment(vertical='center'); WRAP=Alignment(vertical='center', wrap_text=True)

rows=list(csv.DictReader(open('out/domains_master.csv')))
KEEP={'bbb.org','yellowpages.com','yp.com','chamberofcommerce.com','dexknows.com','birdeye.com','2findlocal.com',
 'ibegin.com','mylocalservices.com','hometownguru.com','landscapeprofessionals.org','superpages.com','bing.com',
 'bingapis.com','brandfetch.com','cgmimm.com','rockwaterfarm.com','completegardening.com','simplylawn.com',
 'positivebloom.com','thelandscapeconnection.com','lawnspedia.com','themowersguide.com','vohslandscaping.com',
 'boyerslawncare.com','averagedudeoutdoors.com','todayshomeowner.com','housemethod.com','landscapeleadership.com'}
def ig(x):
    try:return int(x)
    except:return 0
def ff(x):
    try:return float(x.rstrip('.') or 0)
    except:return 0.0
def status(r):
    d=r['domain'].strip().lower()
    if d in KEEP: return 'Keep'
    ac=r['anchor_class']; df=r['is_dofollow']=='dofollow'; sem=r['source']=='Semrush'
    if ac in ('held_geo','held_commercial'):
        return 'Held (Pending Partner)' if df else 'Held (Nofollow, No Action)'
    spammy = ac in ('spam_sales','telegram','ecom_injection') or r['is_spam_ahrefs']=='1' or sem or r['bucket'].startswith(('Spam','Review'))
    if spammy:
        return 'Spam (Disavow)' if (df or sem) else 'Spam (Nofollow, No Action)'
    return 'Spam (Nofollow, No Action)' if not df else 'Keep'
def atype(r):
    ac=r['anchor_class']; al=(r['top_anchor'] or '').lower().strip()
    if ac in ('spam_sales','telegram'): return 'Spam: keyword stuffed SEO sales copy'
    if ac=='ecom_injection': return 'Spam: injected e-commerce anchor'
    if ac=='held_geo': return 'Exact match commercial (geo)'
    if ac=='held_commercial': return 'Exact match commercial'
    if ac=='brand':
        if al.startswith('http') or al in ('callturfsup.com','www.callturfsup.com') or 'callturfsup.com/' in al: return 'Naked URL'
        return 'Branded'
    if ac=='semrush_only': return '(Semrush-only, anchor not retrieved)'
    if al=='': return 'Empty or image'
    return 'Contextual or other'
def indis(st):
    if st=='Spam (Disavow)': return 'Yes'
    if st=='Held (Pending Partner)': return 'Held'
    return 'No'
for r in rows:
    r['st']=status(r); r['atype']=atype(r); r['indis']=indis(r['st'])
    r['bl']=ig(r['links_grouped']) or (1 if r['source']=='Semrush' else 0)
    r['dofollow_links']=r['bl'] if r['is_dofollow']=='dofollow' else 0
    r['nofollow_links']=r['bl'] if r['is_dofollow']=='nofollow' else ''

tot=len(rows)
C=Counter(r['st'] for r in rows)
BL=defaultdict(int)
for r in rows: BL[r['st']]+=r['bl']
STATUSES=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Spam (Nofollow, No Action)','Keep','Own Site']
MEAN={
 'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'Held (Pending Partner)':'Exact match commercial anchor, or a link aimed at a product, capability or service page. May have been commissioned. Not in the disavow file until the previous partner confirms.',
 'Held (Nofollow, No Action)':'Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
 'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Keep':'Genuine or harmless link. Keep.',
 'Own Site':'Client owned domain that redirects into the site.'}

spam_total=C['Spam (Disavow)']+C['Spam (Nofollow, No Action)']
held_total=C['Held (Pending Partner)']+C['Held (Nofollow, No Action)']
# recency
def dd(x):
    try:return datetime.date.fromisoformat(x[:10])
    except:return None
cut=datetime.date(2026,9,3)
ah=[r for r in rows if r['source']!='Semrush' and dd(r['first_seen'])]
recent=sum(1 for r in ah if dd(r['first_seen'])>=cut)
# biggest network
anet=Counter(r['top_anchor'] for r in rows if r['st']=='Spam (Disavow)' and r['source']!='Semrush')
big_anchor,big_n=anet.most_common(1)[0]
held_zero=sum(1 for r in rows if r['st'].startswith('Held') and ff(r['traffic'])==0)

FINDINGS=[
 f"{spam_total:,} of the {tot:,} referring domains are spam. {C['Spam (Disavow)']:,} have a dofollow link and go in the disavow file; the other {C['Spam (Nofollow, No Action)']:,} are nofollow and need no action.",
 f"The attack is recent: of the dated links, {recent:,} of {len(ah):,} first appeared in just the last two months. We audited the full live profile across Ahrefs and Semrush, not only Tab 09's 13 patterns.",
 "You can upload one disavow file for callturfsup.com; it covers every bad domain in the profile.",
 "Two patterns, easy to tell apart: keyword-stuffed SEO sales-copy / link-scheme anchors hit the site broadly, while exact-match commercial anchors ('lawn care gainesville va' style) point at the Gainesville/Haymarket service pages.",
 f"The single biggest dofollow network uses the anchor \"{big_anchor[:70]}...\" on {big_n} domains; two more ~220-domain networks are nofollow testimonial spam.",
 f"{held_total} domains are held for the previous partner to confirm, in case any were paid placements ({C['Held (Pending Partner)']} dofollow, {C['Held (Nofollow, No Action)']} nofollow).",
 f"Held does not mean good: {held_zero} of the {held_total} held domains have no organic traffic at all.",
]

# anchor profile (Ahrefs anchors only; collapse minor spam into sales-copy)
def ptype(r):
    t=r['atype']
    if t=='Spam: injected e-commerce anchor': return 'Spam: keyword stuffed SEO sales copy'
    return t
prof_bl=defaultdict(int); prof_rd=defaultdict(int)
for r in rows:
    if r['source']=='Semrush': continue
    prof_bl[ptype(r)]+=r['bl']; prof_rd[ptype(r)]+=1
prof_total=sum(prof_bl.values()) or 1
prof=sorted(prof_bl.items(), key=lambda kv:-kv[1])

wb=openpyxl.Workbook()
def setw(ws,w):
    for k,v in w.items(): ws.column_dimensions[k].width=v
def hdr(ws,r):
    for c in ws[r]:
        if c.value is not None: c.font=HFONT; c.fill=HFILL; c.alignment=VC
def bodyfont(ws,start):
    for row in ws.iter_rows(min_row=start):
        for c in row:
            if c.value is not None and c.font is not HFONT: c.font=BFONT

# ---------- Summary ----------
TITLE21=Font(name='Geist', size=21, bold=True, color='FF0C343D')
HDR10=Font(name='Geist', size=10, bold=True, color='FFFFFFFF')
HDR9=Font(name='Geist', size=9, bold=True, color='FFFFFFFF')
KFHDR=Font(name='Geist', size=10, bold=True, color='FF000000')
APHDR=Font(name='Geist', size=11, bold=True, color='FF0C343D')
WRAPH=Alignment(vertical='center', wrap_text=True)
PCT='0.0%'; NUM='#,##0'
ws=wb.active; ws.title='Summary'
ws.merge_cells('B1:E2'); ws['B1']='callturfsup.com'; ws['B1'].font=TITLE21; ws['B1'].alignment=Alignment(vertical='center')
for col,t in zip('ABCDE',['Status','Domains','Backlinks','Share of Domains','What it means']):
    c=ws[f'{col}3']; c.value=t; c.font=HDR10; c.fill=HFILL; c.alignment=WRAPH
r=4
for s in STATUSES:
    ws.cell(r,1,s).font=BFONT
    b=ws.cell(r,2,C.get(s,0)); b.font=BFONT; b.number_format=NUM
    cc=ws.cell(r,3,BL.get(s,0)); cc.font=BFONT; cc.number_format=NUM
    d=ws.cell(r,4,(C.get(s,0)/tot) if tot else 0); d.font=BFONT; d.number_format=PCT
    e=ws.cell(r,5,MEAN[s]); e.font=BFONT; e.alignment=WRAP
    r+=1
ws.cell(r,1,'Total').font=BOLD
tb=ws.cell(r,2,tot); tb.font=BOLD; tb.number_format=NUM
tc=ws.cell(r,3,sum(BL.values())); tc.font=BOLD; tc.number_format=NUM
td=ws.cell(r,4,1.0); td.font=BOLD; td.number_format=PCT
total_row=r; r+=1
kf_hdr=r; ws.cell(r,1,'Key findings').font=KFHDR; r+=1
for f in FINDINGS:
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5)
    c=ws.cell(r,1,f); c.font=BFONT; c.alignment=WRAP; r+=1
ap_hdr=r; ws.cell(r,1,'Anchor text profile (all backlinks)').font=APHDR; r+=1
ap_cols=r
for col,t in zip('ABCD',['Anchor type','Backlinks','Share of Backlinks','Referring Domains']):
    c=ws[f'{col}{r}']; c.value=t; c.font=HDR9; c.fill=HFILL; c.alignment=WRAPH
r+=1
for t,bl in prof:
    ws.cell(r,1,t).font=BFONT
    b=ws.cell(r,2,bl); b.font=BFONT; b.number_format=NUM
    sc=ws.cell(r,3,bl/prof_total); sc.font=BFONT; sc.number_format=PCT
    rd=ws.cell(r,4,prof_rd[t]); rd.font=BFONT; rd.number_format=NUM
    r+=1
from openpyxl.styles import Border, Side
THIN=Side(style='thin', color='FF000000'); BORD=Border(THIN,THIN,THIN,THIN)
CENTER=Alignment(horizontal='center', vertical='center'); LEFTV=Alignment(horizontal='left', vertical='center')
# status table: borders + alignment (A3:E{total_row})
for rr in range(3, total_row+1):
    for ci in range(1,6):
        c=ws.cell(rr,ci); c.border=BORD
        if rr==3: c.alignment=CENTER
        elif ci in (2,3,4): c.alignment=CENTER
        elif ci==5: c.alignment=WRAP
        else: c.alignment=LEFTV
# anchor-profile table: borders + alignment (ap_cols .. last)
last_ap=r-1
for rr in range(ap_cols, last_ap+1):
    for ci in range(1,5):
        c=ws.cell(rr,ci); c.border=BORD
        if rr==ap_cols: c.alignment=CENTER
        elif ci in (2,3,4): c.alignment=CENTER
        else: c.alignment=LEFTV
setw(ws,{'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120})
for i in range(1,r+2): ws.row_dimensions[i].height=22.5
try:
    img=XLImage('assets/image1.png'); img.width=186; img.height=55; ws.add_image(img,'A1')
except Exception as e: print('logo skip',e)

NUMH={'AS','Backlinks',"RD's",'Traffic','In Disavow','Dofollow Links','Nofollow Links',
      'Share of Backlinks','Referring Domains','Domains','Spam Domains Using It','Organic Keywords'}
def datasheet(title, headers, records, widths, bodyh=22.5):
    ws=wb.create_sheet(title); ws.append(headers)
    for rec in records: ws.append(rec)
    # header: teal fill, white bold, centered, bordered (data rows stay borderless like sample)
    for c in ws[1]:
        if c.value is not None:
            c.font=HFONT; c.fill=HFILL
            c.alignment=Alignment(horizontal='center', vertical='center', wrap_text=True); c.border=BORD
    bodyfont(ws,2); ws.freeze_panes='B2'; setw(ws,widths)
    ws.sheet_format.defaultRowHeight=bodyh; ws.sheet_format.customHeight=True
    ws.row_dimensions[1].height=31.5
    numcols=[i+1 for i,h in enumerate(headers) if h in NUMH]
    cen=Alignment(horizontal='center', vertical='center')
    if numcols:
        for row in ws.iter_rows(min_row=2):
            for ci in numcols:
                row[ci-1].alignment=cen
    return ws

# Referring Domain Audit
rda=[[r['domain'],r['st'],r['as_semrush'],r['bl'],'',r['traffic'],r['indis'],r['target_url'],r['dofollow_links'],
      r['nofollow_links'],r['first_seen'],r['top_anchor'],r['example_page'],'',r['source'],r['ip'],
      (f"domain:{r['domain']}" if r['indis']=='Yes' else '')] for r in sorted(rows,key=lambda x:(x['st'],x['domain']))]
datasheet('Referring Domain Audit',
 ['Domain','Status','AS','Backlinks',"RD's",'Traffic','In Disavow','Links Point To','Dofollow Links','Nofollow Links',
  'First Seen','Top Anchor Text','Example Linking Page','Linking Page Title','Source','IP','Disavow Line'],
 rda, {'A':36,'B':24.7,'C':9.6,'D':13,'E':9.4,'F':9.7,'G':12.4,'H':21.3,'I':14,'J':8.7,'K':12,'L':45,'M':8.7,'N':40,'O':14,'P':15,'Q':14}, 15.75)

# All Backlinks (1 per domain, Ahrefs)
ab=[[r['domain'],r['st'],'Ahrefs',r['top_anchor'],r['atype'],'text',r['example_page'],'',r['target_url']]
    for r in sorted(rows,key=lambda x:x['domain']) if r['source']!='Semrush']
datasheet('All Backlinks',
 ['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL','Linking Page Title','Target URL'],
 ab, {'A':25.4,'B':27.1,'C':14.7,'D':55,'E':32,'F':10,'G':55,'H':53.1,'I':30.6})

# Anchor Analysis (per anchor)
dba=defaultdict(list)
for r in rows:
    if r['source']!='Semrush': dba[r['top_anchor']].append(r)
totbl=sum(r['bl'] for r in rows if r['source']!='Semrush') or 1
aa=[]
for a,recs in sorted(dba.items(),key=lambda kv:-len(kv[1])):
    bl=sum(x['bl'] for x in recs); sd=sum(1 for x in recs if x['st'].startswith('Spam'))
    aa.append([a,recs[0]['atype'],bl,round(bl/totbl,6),len(recs),sd])
datasheet('Anchor Analysis',
 ['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains','Spam Domains Using It'],
 aa, {'A':115.9,'B':37.7,'C':14,'D':8.7,'E':18,'F':20.3})

# Exact Match Anchors (Partner confirmed + Final decision BLANK, like sample)
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
ema=[[r['domain'],r['example_page'],r['top_anchor'],market(r['top_anchor']),sitetype(r['domain']),'','']
     for r in sorted(em,key=lambda x:(x['is_dofollow'],x['domain']))]
datasheet('Exact Match Anchors',
 ['Referring domain','Example backlink (linking page)','Exact-match commercial anchor','Market','Site type (indicative)','Partner confirmed? (Y/N)','Final decision'],
 ema, {'A':25.4,'B':59,'C':53.1,'D':16,'E':24.6,'F':15.4,'G':15})

# Pending Disavow Lines
pdl=[[r['domain'],f"domain:{r['domain']}",'Append only if the partner does not claim it, to disavow_callturfsup.txt']
     for r in sorted(em,key=lambda x:x['domain'])]
datasheet('Pending Disavow Lines',
 ['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation'],
 pdl, {'A':32,'B':44,'C':48})

# Disavow List = In Disavow Yes only
dl=[[f"domain:{r['domain']}",r['as_semrush'],r['bl'],'',r['traffic'],'',r['top_anchor']]
    for r in sorted([x for x in rows if x['indis']=='Yes'],key=lambda x:x['domain'])]
datasheet('Disavow List',
 ['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text'],
 dl, {'A':44,'B':14,'C':15.6,'D':14,'E':11.1,'F':14.9,'G':98.9})

wb.save('out/CallTurfsUp_Backlinks_Audit.xlsx')
print('saved | statuses:',dict(C),'| disavow list:',len(dl),'| held:',len(em))
