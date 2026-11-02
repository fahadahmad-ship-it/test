import csv
from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

TODAY = '2026-11-02'
rows = list(csv.DictReader(open('out/domains_master.csv')))

KEEP = {
 'bbb.org','yellowpages.com','yp.com','chamberofcommerce.com','dexknows.com',
 'birdeye.com','2findlocal.com','ibegin.com','mylocalservices.com','hometownguru.com',
 'landscapeprofessionals.org','superpages.com','bing.com','bingapis.com','brandfetch.com',
 'cgmimm.com','rockwaterfarm.com','completegardening.com','simplylawn.com','positivebloom.com',
 'thelandscapeconnection.com','lawnspedia.com','themowersguide.com','vohslandscaping.com',
 'boyerslawncare.com','averagedudeoutdoors.com','todayshomeowner.com','housemethod.com',
 'landscapeleadership.com',
}
for r in rows:
    r['decision'] = 'KEEP (legit)' if r['domain'].strip().lower() in KEEP else 'DISAVOW'

disavowed = [r for r in rows if r['decision']=='DISAVOW']
kept = [r for r in rows if r['decision']=='KEEP (legit)']

wb = openpyxl.Workbook()
HDR = Font(bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='374151')
def sh(ws):
    for c in ws[1]: c.font=HDR; c.fill=HFILL; c.alignment=Alignment(vertical='center')
    ws.freeze_panes='A2'

# Summary
ws=wb.active; ws.title='Summary'
ws.append(['callturfsup.com - Backlink Audit & COMPLETE Disavow']); ws['A1'].font=Font(bold=True,size=14)
ws.append([f'Generated {TODAY} | Ahrefs (live) + Semrush union | complete consolidation'])
ws.append([])
ws.append(['Metric','Domains','Note'])
ws.append(['Total referring domains assessed', len(rows), 'Ahrefs live + Semrush union'])
ws.append(['DISAVOWED (complete)', len(disavowed), 'All spam, link-scheme, PBN, brand-farm, exact-match anchors'])
ws.append(['KEPT (legitimate, not disavowed)', len(kept), 'Genuine citations/directories/industry blogs'])
ws.append([])
ws.append(['Original bucket','Domains','In complete disavow?'])
bc = Counter((r['bucket'], r['decision']) for r in rows)
seen=Counter(r['bucket'] for r in rows)
for b,n in seen.most_common():
    dis=sum(1 for r in rows if r['bucket']==b and r['decision']=='DISAVOW')
    ws.append([b, n, f'{dis}/{n} disavowed'])
for rn in (4,9):
    for c in ws[rn]: c.font=HDR; c.fill=HFILL
ws.column_dimensions['A'].width=42; ws.column_dimensions['B'].width=14; ws.column_dimensions['C'].width=60

# Referring Domain Audit (ALL domains)
ws=wb.create_sheet('Referring Domain Audit')
ws.append(['Domain','Decision','Original Bucket','Source','Follow','Ahrefs is_spam','DR (Ahrefs)',
           'AS (Semrush)','Traffic','Top Anchor','Target URL','Example Page','IP','First Seen','Disavow Line'])
for r in sorted(rows, key=lambda x:(x['decision'],x['bucket'],x['domain'])):
    dl = f"domain:{r['domain']}" if r['decision']=='DISAVOW' else ''
    ws.append([r['domain'],r['decision'],r['bucket'],r['source'],r['is_dofollow'],r['is_spam_ahrefs'],
               r['dr_ahrefs'],r['as_semrush'],r['traffic'],r['top_anchor'],r['target_url'],
               r['example_page'],r['ip'],r['first_seen'],dl])
sh(ws)
for col,w in {'A':30,'B':14,'C':26,'J':50,'K':38,'L':38}.items(): ws.column_dimensions[col].width=w

# Disavow List (COMPLETE)
ws=wb.create_sheet('Disavow List (COMPLETE)')
ws.append(['Disavow Line','Source','Follow','DR (Ahrefs)','AS (Semrush)','Original Bucket','Top Anchor'])
for r in sorted(disavowed, key=lambda x:x['domain']):
    ws.append([f"domain:{r['domain']}",r['source'],r['is_dofollow'],r['dr_ahrefs'],r['as_semrush'],r['bucket'],r['top_anchor']])
sh(ws)
ws.column_dimensions['A'].width=36; ws.column_dimensions['F'].width=26; ws.column_dimensions['G'].width=55

# Kept (NOT disavowed)
ws=wb.create_sheet('Kept - NOT disavowed')
ws.append(['Domain','Original Bucket','Source','Follow','DR (Ahrefs)','Top Anchor','Why kept'])
for r in sorted(kept, key=lambda x:x['domain']):
    ws.append([r['domain'],r['bucket'],r['source'],r['is_dofollow'],r['dr_ahrefs'],r['top_anchor'],
               'Genuine citation/directory/industry site - disavowing would harm local SEO'])
sh(ws)
ws.column_dimensions['A'].width=30; ws.column_dimensions['F'].width=45; ws.column_dimensions['G'].width=60

# Anchor Analysis
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Domains (representative)','Example Bucket'])
ac=Counter(r['top_anchor'] for r in rows if r['source']!='Semrush')
ab={}
for r in rows:
    if r['source']!='Semrush': ab.setdefault(r['top_anchor'],r['bucket'])
for a,n in ac.most_common(): ws.append([a,n,ab.get(a,'')])
sh(ws); ws.column_dimensions['A'].width=70; ws.column_dimensions['B'].width=24; ws.column_dimensions['C'].width=26

# Exact Match Anchors (the former Harbinger set - now disavowed)
ws=wb.create_sheet('Exact Match Anchors')
ws.append(['Domain','Exact-match commercial anchor','Market','Follow','Decision','Example backlink'])
def mkt(a):
    al=a.lower()
    if 'gainesville' in al: return 'Gainesville, VA'
    if 'haymarket' in al: return 'Haymarket, VA'
    if 'south riding' in al: return 'South Riding, VA'
    if 'virginia' in al or ' va' in al: return 'Northern VA'
    return 'Non-geo'
em=[r for r in rows if r['anchor_class'] in ('held_geo','held_commercial')]
for r in sorted(em, key=lambda x:(x['is_dofollow'],x['domain'])):
    ws.append([r['domain'],r['top_anchor'],mkt(r['top_anchor']),r['is_dofollow'],r['decision'],r['example_page']])
sh(ws)
for col,w in {'A':30,'B':50,'F':45}.items(): ws.column_dimensions[col].width=w

wb.save('out/callturfsup_backlinks_audit_COMPLETE.xlsx')
print('sheets:', wb.sheetnames)
print('total:',len(rows),'| disavowed:',len(disavowed),'| kept:',len(kept))
