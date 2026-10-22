#!/usr/bin/env python3
"""Build the Controlled Comfort backlink-audit workbook (7 tabs, AUDIT_FORMAT.md) and the
disavow file(s). Reads classified_domains.json + classified_links.csv from the data dir.
Usage: build.py <data_dir> <out_dir>
"""
import sys, os, json, csv, io
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DATA, OUT = sys.argv[1], sys.argv[2]
ACCENT = 'FF0C343D'
FONT = 'Geist'
os.makedirs(OUT, exist_ok=True)

D = json.load(open(os.path.join(DATA, 'classified_domains.json')))
LINKS = list(csv.DictReader(open(os.path.join(DATA, 'classified_links.csv'))))

STATUSES = ['Spam (Disavow)', 'Spam (Nofollow, No Action)', 'Held (Pending Partner)',
            'Held (Nofollow, No Action)', 'Keep', 'Own Site']
dist = Counter(d['status'] for d in D.values())

# ---------- styles ----------
hdr_fill = PatternFill('solid', fgColor=ACCENT)
hdr_font = Font(name=FONT, size=9, bold=True, color='FFFFFFFF')
data_font = Font(name=FONT, size=9, color='FF000000')
input_fill = hdr_fill
input_font = Font(name=FONT, size=9, color='FFFFFFFF')
hdr_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
data_align = Alignment(vertical='center', wrap_text=False)
thin = Side(style='thin', color='FF000000')
# header-only border scheme (playbook §8: left/right/top, no bottom; data cells unbordered)
hdr_border = Border(left=thin, right=thin, top=thin)

def write_tab(ws, headers, rows, widths=None, row_h=22.5, autofilter=True, freeze='B2'):
    ws.append(headers)
    for ci, _ in enumerate(headers, 1):
        c = ws.cell(row=1, column=ci)
        c.fill = hdr_fill; c.font = hdr_font; c.alignment = hdr_align; c.border = hdr_border
    ws.row_dimensions[1].height = 31.5
    for r in rows:
        ws.append(r)
    for ri in range(2, len(rows) + 2):
        ws.row_dimensions[ri].height = row_h
        for ci in range(1, len(headers) + 1):
            c = ws.cell(row=ri, column=ci)
            c.font = data_font; c.alignment = data_align
            c.fill = PatternFill('solid', fgColor='FFFFFFFF')
    if widths:
        for ci, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(ci)].width = w
    if autofilter:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(rows)+1}"
    if freeze:
        ws.freeze_panes = freeze
    ws.sheet_view.showGridLines = True

wb = Workbook()

# ---------- Tab 1: Summary ----------
ws = wb.active; ws.title = 'Summary'
ws.sheet_view.showGridLines = False
ws.merge_cells('B1:E2')
t = ws['B1']; t.value = 'Controlled Comfort — Backlink Audit & Disavow'
t.font = Font(name=FONT, size=9, bold=True, color=ACCENT)
t.alignment = Alignment(horizontal='left', vertical='center')
ws['B4'] = 'Status'; ws['C4'] = 'Referring domains'
for c in ('B4', 'C4'):
    ws[c].fill = hdr_fill; ws[c].font = Font(name=FONT, size=10, bold=True, color='FFFFFFFF')
    ws[c].alignment = Alignment(horizontal='left', vertical='center')
    ws[c].border = Border(left=thin, right=thin, top=thin, bottom=thin)
r = 5
for s in STATUSES:
    ws.cell(r, 2, s).font = data_font
    ws.cell(r, 3, dist.get(s, 0)).font = data_font
    for col in (2, 3):
        ws.cell(r, col).border = Border(left=thin, right=thin, top=thin, bottom=thin)
    r += 1
ws.cell(r, 2, 'Total').font = Font(name=FONT, size=9, bold=True)
ws.cell(r, 3, sum(dist.values())).font = Font(name=FONT, size=9, bold=True)

# key findings
tot_bl = len(LINKS)
dof_spam = sum(1 for d in D.values() if d['status'] == 'Spam (Disavow)')
home_links = sum(1 for l in LINKS if l['prop'] == 'home')
deep_links = sum(1 for l in LINKS if l['prop'] == 'deep')
anchor_counts = Counter(l['anchor'] for l in LINKS)
top_sales = anchor_counts.most_common(1)[0]
kf_row = r + 2
ws.cell(kf_row, 2, 'Key findings').font = Font(name=FONT, size=10, bold=True, color=ACCENT)
findings = [
 f"1. {dist['Spam (Disavow)']} referring domains are confirmed spam with a dofollow link and go in the disavow file; "
 f"another {dist['Spam (Nofollow, No Action)']} are spam but all-nofollow (no action).",
 f"2. The brief listed 56 domains; the live profile is {sum(dist.values())} referring hosts / {tot_bl} backlinks — the "
 f"attack is far larger and ongoing (the profile adds ~70+ referring domains/day).",
 f"3. No owned domains redirect into the money site, so ONE disavow file applies to one Search Console property "
 f"(controlledcomfort.com). No disavow file currently exists on that property — this is an ADD, not a replace.",
 f"4. Two campaigns split by target: a home-page PBN/'buy-backlinks' flood ({home_links} links) and a deep "
 f"service-page directory-listing campaign ({deep_links} links). The page a link points at separates them.",
 f'5. The dominant spam anchor is sales copy — "{top_sales[0][:70]}" ({top_sales[1]} links).',
 f"6. The held set ({dist['Held (Pending Partner)']+dist['Held (Nofollow, No Action)']} domains, incl. the brief's 56) is one "
 f"directory-listing vendor network with exact-match commercial anchors on deep money pages; held pending the supplier.",
 f"7. Held does NOT mean valuable: these are DR~0, zero-traffic directory pages. Held means 'may be commissioned, so the "
 f"supplier decides', not 'keep'.",
]
for i, fx in enumerate(findings):
    cell = ws.cell(kf_row + 1 + i, 2, fx); cell.font = data_font
    cell.alignment = Alignment(vertical='top', wrap_text=True)
    ws.merge_cells(start_row=kf_row + 1 + i, start_column=2, end_row=kf_row + 1 + i, end_column=8)
ws.column_dimensions['A'].width = 3
for col in 'BCDE':
    ws.column_dimensions[col].width = 20
for rr in range(1, kf_row + 12):
    ws.row_dimensions[rr].height = 22.5

# ---------- Tab 2: Referring Domain Audit (17) ----------
ws = wb.create_sheet('Referring Domain Audit')
hdrs = ['Domain', 'Status', 'AS', 'Backlinks', "RD's", 'Traffic', 'In Disavow', 'Links Point To',
        'Dofollow Links', 'Nofollow Links', 'First Seen', 'Top Anchor Text', 'Example Linking Page',
        'Linking Page Title', 'Source', 'IP', 'Disavow Line']
rows = []
for dom in sorted(D, key=lambda x: (STATUSES.index(D[x]['status']), x)):
    d = D[dom]
    rows.append([dom, d['status'], d['dr'], d['backlinks'], d['refdomains'], d['traffic'],
                 'Yes' if d['in_disavow'] else 'No', d['links_point_to'], d['dofollow'], d['nofollow'],
                 d['first_seen'], d['top_anchor'], d['example_url'], d['example_title'], 'Ahrefs',
                 'n/a (not in export)', f"domain:{dom}" if d['in_disavow'] else ''])
write_tab(ws, hdrs, rows, widths=[26,24,6,9,7,9,9,16,9,9,18,34,40,34,8,16,22], row_h=15.75)

# ---------- Tab 3: All Backlinks (9) ----------
ws = wb.create_sheet('All Backlinks')
hdrs = ['Referring Domain', 'Status', 'Tool', 'Anchor Text', 'Anchor Type', 'Link Type',
        'Linking Page URL', 'Linking Page Title', 'Target URL']
rows = [[l['referring_domain'], l['status'], 'Ahrefs', l['anchor'], l['anchor_type'],
         ('Nofollow' if l['nofollow'] == 'True' else 'Dofollow'), l['url'], l['title'], l['target']]
        for l in LINKS]
write_tab(ws, hdrs, rows, widths=[26,24,8,40,26,10,42,36,40])

# ---------- Tab 4: Anchor Analysis (6) ----------
ws = wb.create_sheet('Anchor Analysis')
by_anchor = defaultdict(lambda: {'bl': 0, 'rd': set(), 'spamrd': set(), 'type': ''})
for l in LINKS:
    a = by_anchor[l['anchor']]; a['bl'] += 1; a['rd'].add(l['referring_domain']); a['type'] = l['anchor_type']
    if l['status'].startswith('Spam'):
        a['spamrd'].add(l['referring_domain'])
hdrs = ['Anchor Text', 'Anchor Type', 'Backlinks', 'Share of Backlinks', 'Referring Domains', 'Spam Domains Using It']
rows = []
for anchor, a in sorted(by_anchor.items(), key=lambda x: -x[1]['bl']):
    rows.append([anchor or '(empty)', a['type'], a['bl'], f"{100*a['bl']/len(LINKS):.1f}%",
                 len(a['rd']), len(a['spamrd'])])
write_tab(ws, hdrs, rows, widths=[60,26,10,16,16,20])

# ---------- Tab 5: Exact Match Anchors (7) ----------
ws = wb.create_sheet('Exact Match Anchors')
hdrs = ['Referring domain', 'Example backlink (linking page)', 'Exact-match commercial anchor', 'Market',
        'Site type (indicative)', 'Partner confirmed? (Y/N)', 'Final decision']
rows = []
emx = []
for dom, d in D.items():
    if not d['status'].startswith('Held'):
        continue
    # this tab is EXACT-MATCH anchors only; held-by-deep-target-only domains appear on the
    # Pending Disavow Lines tab instead (keeps this tab true to its name).
    exlink = next((l for l in LINKS if l['referring_domain'] == dom and l['anchor_type'].startswith('Exact match')), None)
    if not exlink:
        continue
    anchor = exlink['anchor']
    tgt = exlink['target'].lower()
    market = 'Omaha NE — Heating/Furnace' if 'heating' in tgt else ('Omaha NE — Air Conditioning' if 'air-condition' in tgt else 'Omaha NE — HVAC (home)')
    rows.append([dom, exlink['url'], anchor, market,
                 'Directory / business listing', '', 'Hold — pending supplier confirmation'])
    emx.append(dom)
rows.sort(key=lambda r: r[0])
write_tab(ws, hdrs, rows, widths=[26,42,34,26,24,22,30])
# mark the "Partner confirmed?" column as input cells (accent fill, white font)
col_pc = 6
for ri in range(2, len(rows) + 2):
    c = ws.cell(ri, col_pc); c.fill = input_fill; c.font = input_font

# ---------- Tab 6: Pending Disavow Lines (3) ----------
ws = wb.create_sheet('Pending Disavow Lines')
hdrs = ['Referring domain', 'Disavow line (append to disavow.txt once confirmed)', 'Recommendation']
rows = [[dom, f"domain:{dom}", 'Hold — append to disavow.txt only if the supplier confirms it was NOT commissioned']
        for dom, d in sorted(D.items()) if d['status'].startswith('Held')]
write_tab(ws, hdrs, rows, widths=[28,48,60])

# ---------- Tab 7: Disavow List (7) ----------
ws = wb.create_sheet('Disavow List')
hdrs = ['Disavow Line', 'AS', 'Backlinks', "RD's", 'Traffic', 'Organic Keywords', 'Top Anchor Text']
dis_domains = sorted(dom for dom, d in D.items() if d['status'] == 'Spam (Disavow)')
# redundancy: drop a child whose parent domain is also disavowed (domain: covers subdomains)
disset = set(dis_domains)
emitted = [dom for dom in dis_domains if not any(dom != p and dom.endswith('.' + p) for p in disset)]
rows = [[f"domain:{dom}", D[dom]['dr'], D[dom]['backlinks'], D[dom]['refdomains'],
         D[dom]['traffic'], D[dom]['keywords'], D[dom]['top_anchor']] for dom in emitted]
write_tab(ws, hdrs, rows, widths=[46,6,10,8,9,16,50])

wb.save(os.path.join(OUT, 'controlled_comfort_backlink_audit.xlsx'))

# ---------- disavow.txt ----------
reason_of = {}
for dom in emitted:
    rs = D[dom]['reason']
    if 'PBN/link-farm host' in rs or 'host name' in rs:
        reason_of[dom] = 'PBN / link-farm host'
    elif 'sales-copy' in rs:
        reason_of[dom] = 'PBN sales-copy anchor'
    elif 'spam page title' in rs:
        reason_of[dom] = 'Spam page title (link-broker/PBN)'
    elif 'off-topic' in rs:
        reason_of[dom] = 'Off-topic (pharma/casino)'
    else:
        reason_of[dom] = 'Spam'
groups = defaultdict(list)
for dom in emitted:
    groups[reason_of[dom]].append(dom)
held = sorted(dom for dom, d in D.items() if d['status'].startswith('Held'))

lines = []
lines.append('# Google disavow file — controlledcomfort.com (Controlled Comfort, Omaha NE)')
lines.append('# Generated 2026-10-22 from Ahrefs export (1,089 ref. domains / 2,514 backlinks).')
lines.append(f'# ACTIVE DISAVOW LINES: {len(emitted)}')
lines.append('#')
lines.append('# Scope: ONE Search Console property (controlledcomfort.com). No owned domains redirect')
lines.append('#   into the money site, so a single file applies. No disavow file currently exists on')
lines.append('#   the property (client-confirmed) — this is a NEW upload (add), not a replace.')
lines.append('# "Partner" in the workbook = the previous SEO SUPPLIER this brief names; same role.')
lines.append('#')
lines.append(f'# EXCLUDED pending the supplier: {len(held)} HELD domains (exact-match commercial anchors /')
lines.append('#   deep money-page links that may be COMMISSIONED directory placements). They are NOT in')
lines.append('#   this file. Confirm with the supplier which were commissioned before relying on this.')
lines.append('#   The held list is in the workbook (Pending Disavow Lines / Exact Match Anchors tabs).')
lines.append('# Every line below rests on visible evidence (PBN host / sales-copy anchor / off-topic).')
lines.append('# Do not submit to Google Search Console on the client\'s behalf.')
lines.append('')
for g in ['PBN / link-farm host', 'PBN sales-copy anchor', 'Spam page title (link-broker/PBN)',
          'Off-topic (pharma/casino)', 'Spam']:
    if not groups.get(g):
        continue
    lines.append(f'# === {g} ({len(groups[g])}) ===')
    for dom in sorted(groups[g]):
        lines.append(f'domain:{dom}')
    lines.append('')
open(os.path.join(OUT, 'disavow_controlledcomfort.txt'), 'w').write('\n'.join(lines))

print('workbook + disavow written to', OUT)
print('active disavow lines:', len(emitted), '| held excluded:', len(held))
print('status distribution:', dict(dist))
print('exact-match held rows:', len(emx))
