import csv, datetime
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

TODAY = '2026-11-02'
rows = list(csv.DictReader(open('out/domains_master.csv')))

def g(b): return [r for r in rows if r['bucket'] == b]

spam_ah      = g('Spam (Disavow)')                     # Ahrefs confirmed, dofollow
spam_ah_nf   = g('Spam (Nofollow, No Action)')
spam_sem     = g('Spam (Disavow) [Semrush-only]')      # name-classified, follow unconfirmed
held_do      = g('Held (Pending Partner)')
held_nf      = g('Held (Nofollow, No Action)')
clean        = g('Clean (No Action)')
review       = g('Review (Semrush-only)')

def intl(x):
    try: return int(x)
    except: return 0

# ---------------- disavow_callturfsup.txt ----------------
with open('out/disavow_callturfsup.txt','w') as f:
    f.write(f"# Google Disavow File - callturfsup.com\n")
    f.write(f"# Generated: {TODAY}\n")
    f.write(f"# Sources: Ahrefs (live backlinks) + Semrush (referring domains), union by source\n")
    f.write("#\n")
    f.write("# METHODOLOGY (K&K-template buckets):\n")
    f.write("#   Spam (Disavow)      = spam anchor AND >=1 dofollow link -> disavowed below\n")
    f.write("#   Nofollow/No Action  = spam but all-nofollow (passes no PageRank) -> NOT disavowed\n")
    f.write("#   Held (Pending Partner) = exact-match commercial anchor -> HELD, see pending_harbinger_held.txt\n")
    f.write("#   Clean (No Action)   = legitimate editorial / brand / citation -> NOT disavowed\n")
    f.write("#\n")
    f.write("# *** HARBINGER GATE ***\n")
    f.write(f"#   {len(held_do)} dofollow + {len(held_nf)} nofollow exact-match Gainesville/Haymarket\n")
    f.write("#   commercial-anchor domains are HELD OUT of this file. Do NOT submit until Harbinger\n")
    f.write("#   confirms who commissioned that activity (see pending_harbinger_held.txt).\n")
    f.write("#\n")
    f.write(f"# SECTION 1 - Confirmed spam, >=1 dofollow (Ahrefs-verified): {len(spam_ah)} domains\n")
    for r in sorted(spam_ah, key=lambda x: x['domain']):
        f.write(f"domain:{r['domain']}\n")
    f.write("#\n")
    f.write(f"# SECTION 2 - Semrush-only link-scheme domains (name-classified; follow status\n")
    f.write(f"#   unconfirmed by Ahrefs; Semrush profile is ~89% dofollow): {len(spam_sem)} domains\n")
    for r in sorted(spam_sem, key=lambda x: x['domain']):
        f.write(f"domain:{r['domain']}\n")

# ---------------- pending_harbinger_held.txt ----------------
with open('out/pending_harbinger_held.txt','w') as f:
    f.write("# HELD PENDING HARBINGER CONFIRMATION - callturfsup.com\n")
    f.write(f"# Generated: {TODAY}\n")
    f.write("# These are EXACT-MATCH COMMERCIAL (Gainesville/Haymarket) anchors that look like\n")
    f.write("# commissioned link-building. DO NOT append to the disavow file until Harbinger\n")
    f.write("# confirms who commissioned this activity.\n")
    f.write("#   - If NOT commissioned by us / our partner -> append these to disavow_callturfsup.txt\n")
    f.write("#   - If commissioned -> keep (do not disavow), log the vendor\n")
    f.write("#\n")
    f.write(f"# A) Dofollow (would pass value - decision needed): {len(held_do)} domains\n")
    for r in sorted(held_do, key=lambda x: x['domain']):
        f.write(f"domain:{r['domain']}    # {r['top_anchor'][:80]}\n")
    f.write("#\n")
    f.write(f"# B) Nofollow (no PageRank passed - no disavow needed either way): {len(held_nf)} domains\n")
    for r in sorted(held_nf, key=lambda x: x['domain']):
        f.write(f"# domain:{r['domain']}    # {r['top_anchor'][:60]}\n")

# ---------------- review_manual.txt ----------------
with open('out/review_manual.txt','w') as f:
    f.write("# MANUAL REVIEW - Semrush-only domains not name-matched as spam - callturfsup.com\n")
    f.write(f"# Generated: {TODAY}. {len(review)} domains. Mostly low-AS link schemes on inspection;\n")
    f.write("# confirm before adding to disavow.\n")
    for r in sorted(review, key=lambda x: x['domain']):
        f.write(f"domain:{r['domain']}    # AS={r['as_semrush']}\n")

# ---------------- workbook ----------------
wb = openpyxl.Workbook()
HDR = Font(bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='374151')
def style_header(ws):
    for c in ws[1]:
        c.font = HDR; c.fill = HFILL; c.alignment = Alignment(vertical='center')
    ws.freeze_panes = 'A2'

# Summary
ws = wb.active; ws.title = 'Summary'
ws.append(['callturfsup.com - Backlink Audit & Disavow'])
ws['A1'].font = Font(bold=True, size=14)
ws.append([f'Generated {TODAY} | Sources: Ahrefs (live) + Semrush | Union by source'])
ws.append([])
ws.append(['Status','Domains','Est. backlinks','Share of domains','What it means'])
total_dom = len(rows)
def est_bl(recs): return sum(intl(r['links_grouped']) for r in recs) or len(recs)
summ = [
 ('Spam (Disavow) - Ahrefs confirmed', spam_ah, 'Spam anchor + >=1 dofollow. In disavow file (Section 1).'),
 ('Spam (Disavow) - Semrush-only', spam_sem, 'Link-scheme domains by name; follow unconfirmed. In disavow file (Section 2).'),
 ('Spam (Nofollow, No Action)', spam_ah_nf, 'Spam but all-nofollow; passes no value. Not disavowed.'),
 ('Held (Pending Partner) - dofollow', held_do, 'Exact-match commercial anchor. HELD until Harbinger confirms who commissioned.'),
 ('Held (Nofollow, No Action)', held_nf, 'Exact-match commercial but all-nofollow. No disavow needed.'),
 ('Clean (No Action)', clean, 'Legitimate editorial / brand / citation. Not disavowed.'),
 ('Review (Semrush-only)', review, 'Semrush-only, not name-matched. Manual review before disavow.'),
]
hdr_row = 4
for name, recs, meaning in summ:
    ws.append([name, len(recs), est_bl(recs), round(len(recs)/total_dom,4), meaning])
ws.append(['TOTAL', total_dom, '', 1.0, ''])
for c in ws[hdr_row]:
    c.font = HDR; c.fill = HFILL
ws.column_dimensions['A'].width = 34; ws.column_dimensions['E'].width = 90
for col in 'BCD': ws.column_dimensions[col].width = 16

# Referring Domain Audit
ws = wb.create_sheet('Referring Domain Audit')
ws.append(['Domain','Bucket','In Disavow','Source','Follow','Ahrefs is_spam','DR (Ahrefs)',
           'AS (Semrush)','Traffic','Top Anchor Text','Target URL','Example Linking Page','IP','First Seen','Disavow Line'])
disavow_buckets = {'Spam (Disavow)','Spam (Disavow) [Semrush-only]'}
for r in sorted(rows, key=lambda x:(x['bucket'], x['domain'])):
    ind = 'YES' if r['bucket'] in disavow_buckets else ('HELD' if 'Held' in r['bucket'] else 'no')
    dl = f"domain:{r['domain']}" if r['bucket'] in disavow_buckets else ''
    ws.append([r['domain'], r['bucket'], ind, r['source'], r['is_dofollow'], r['is_spam_ahrefs'],
               r['dr_ahrefs'], r['as_semrush'], r['traffic'], r['top_anchor'], r['target_url'],
               r['example_page'], r['ip'], r['first_seen'], dl])
style_header(ws)
for col,w in {'A':30,'B':26,'J':50,'K':40,'L':40}.items(): ws.column_dimensions[col].width = w

# All Backlinks (1 per domain representative)
ws = wb.create_sheet('All Backlinks (1-per-domain)')
ws.append(['Referring Domain','Bucket','Tool','Anchor Text','Follow','Linking Page URL','Target URL','Grouped Links'])
for r in sorted(rows, key=lambda x:x['domain']):
    if r['source']=='Semrush': continue
    ws.append([r['domain'], r['bucket'], 'Ahrefs', r['top_anchor'], r['is_dofollow'],
               r['example_page'], r['target_url'], r['links_grouped']])
style_header(ws)
for col,w in {'A':30,'B':26,'D':55,'F':45,'G':40}.items(): ws.column_dimensions[col].width = w

# Anchor Analysis (from representative anchors)
ws = wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Domains (representative)','Example Bucket'])
ac = Counter(r['top_anchor'] for r in rows if r['source']!='Semrush')
abuck = {}
for r in rows:
    if r['source']!='Semrush': abuck.setdefault(r['top_anchor'], r['bucket'])
for a,n in ac.most_common():
    ws.append([a, n, abuck.get(a,'')])
style_header(ws)
ws.column_dimensions['A'].width = 70; ws.column_dimensions['B'].width = 24; ws.column_dimensions['C'].width = 26

# Exact Match Anchors (Held)
ws = wb.create_sheet('Exact Match Anchors')
ws.append(['Referring domain','Exact-match commercial anchor','Market','Follow','Example backlink',
           'Partner confirmed? (Y/N)','Final decision'])
def market(a):
    al=a.lower()
    if 'gainesville' in al: return 'Gainesville, VA'
    if 'haymarket' in al: return 'Haymarket, VA'
    if 'south riding' in al: return 'South Riding, VA'
    if 'virginia' in al or ' va' in al: return 'Northern VA'
    return 'Non-geo'
for r in sorted(held_do+held_nf, key=lambda x:(x['is_dofollow'], x['domain'])):
    ws.append([r['domain'], r['top_anchor'], market(r['top_anchor']), r['is_dofollow'],
               r['example_page'], '', ''])
style_header(ws)
for col,w in {'A':30,'B':50,'E':45}.items(): ws.column_dimensions[col].width=w

# Pending Disavow Lines (Held)
ws = wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append only if Harbinger does NOT claim it)','Follow','Recommendation'])
for r in sorted(held_do+held_nf, key=lambda x:x['domain']):
    rec = 'Append to disavow only if partner/Harbinger does not claim it' if r['is_dofollow']=='dofollow' else 'Nofollow - no disavow needed either way'
    ws.append([r['domain'], f"domain:{r['domain']}", r['is_dofollow'], rec])
style_header(ws)
ws.column_dimensions['A'].width=30; ws.column_dimensions['B'].width=40; ws.column_dimensions['D'].width=55

# Disavow List
ws = wb.create_sheet('Disavow List')
ws.append(['Disavow Line','Source','Follow','DR (Ahrefs)','AS (Semrush)','Top Anchor Text'])
for r in sorted(spam_ah+spam_sem, key=lambda x:x['domain']):
    ws.append([f"domain:{r['domain']}", r['source'], r['is_dofollow'], r['dr_ahrefs'], r['as_semrush'], r['top_anchor']])
style_header(ws)
ws.column_dimensions['A'].width=36; ws.column_dimensions['F'].width=60

wb.save('out/callturfsup_backlinks_audit.xlsx')

# ---- console summary ----
print('disavow Section1 (Ahrefs):', len(spam_ah))
print('disavow Section2 (Semrush-only):', len(spam_sem))
print('TOTAL disavow lines:', len(spam_ah)+len(spam_sem))
print('held dofollow (Harbinger):', len(held_do), '| held nofollow:', len(held_nf))
print('review:', len(review), '| clean:', len(clean), '| spam-nofollow(no action):', len(spam_ah_nf))
print('workbook sheets:', wb.sheetnames)
