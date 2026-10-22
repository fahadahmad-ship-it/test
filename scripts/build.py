#!/usr/bin/env python3
"""Build the Controlled Comfort backlink-audit workbook + disavow file, matching the
signed-off K&K template cell-for-cell. Usage: build.py <data_dir> <out_dir> [logo_png]
"""
import sys, os, json, csv, datetime
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D

DATA, OUT = sys.argv[1], sys.argv[2]
LOGO = sys.argv[3] if len(sys.argv) > 3 else None
ACCENT = 'FF0C343D'; FONT = 'Geist'
os.makedirs(OUT, exist_ok=True)

D = json.load(open(os.path.join(DATA, 'classified_domains.json')))
LINKS = list(csv.DictReader(open(os.path.join(DATA, 'classified_links.csv'))))

# order used on the Summary status table (matches template)
STATUS_ORDER = ['Spam (Disavow)', 'Held (Pending Partner)', 'Held (Nofollow, No Action)',
                'Spam (Nofollow, No Action)', 'Keep', 'Own Site']
STATUS_MEANS = {
 'Spam (Disavow)': 'Confirmed spam with at least one dofollow link. In the file.',
 'Held (Pending Partner)': 'Exact match commercial or press release anchor, or a link aimed at a deep money page. Out of the file until the previous supplier confirms.',
 'Held (Nofollow, No Action)': 'Same, but every link is nofollow, so no decision is needed.',
 'Spam (Nofollow, No Action)': 'Spam, but every link is nofollow, so nothing passes.',
 'Keep': 'Genuine or harmless link. Keep.',
 'Own Site': 'Client owned property or redirect.'}

# ---- shared styles ----
hdr_fill = PatternFill('solid', fgColor=ACCENT)
white_fill = PatternFill('solid', fgColor='FFFFFFFF')
hdr_font = Font(name=FONT, size=9, bold=True, color='FFFFFFFF')
data_font = Font(name=FONT, size=9, color='FF000000')
input_font = Font(name=FONT, size=9, color='FFFFFFFF')
thin = Side(style='thin', color='FF000000')
hdr_border = Border(left=thin, right=thin, top=thin)          # header-only scheme (no bottom)
full_border = Border(left=thin, right=thin, top=thin, bottom=thin)
ctr = Alignment(horizontal='center', vertical='center', wrap_text=True)
gen_v = Alignment(vertical='center')
ctr_v = Alignment(horizontal='center', vertical='center')

def num(v):
    try:
        f = float(str(v).replace(',', '').strip())
        return int(f) if f == int(f) else f
    except Exception:
        return v if str(v).strip() else None

def as_date(v):
    s = str(v).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try: return datetime.datetime.strptime(s, fmt).date()
        except Exception: pass
    return s or None

def data_tab(ws, headers, rows, widths, halign, numfmt, row_h):
    ws.append(headers)
    for ci, _ in enumerate(headers, 1):
        c = ws.cell(1, ci); c.fill = hdr_fill; c.font = hdr_font; c.alignment = ctr; c.border = hdr_border
    ws.row_dimensions[1].height = 31.5
    for r in rows:
        ws.append(r)
    for ri in range(2, len(rows) + 2):
        ws.row_dimensions[ri].height = row_h
        for ci in range(1, len(headers) + 1):
            c = ws.cell(ri, ci); c.font = data_font; c.fill = white_fill
            c.alignment = ctr_v if halign[ci - 1] == 'center' else (
                Alignment(horizontal='left', vertical='center') if halign[ci - 1] == 'left' else gen_v)
            if numfmt[ci - 1] != 'General':
                c.number_format = numfmt[ci - 1]
    for ci, w in enumerate(widths, 1):
        if w: ws.column_dimensions[get_column_letter(ci)].width = w
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(rows) + 1}"
    ws.freeze_panes = 'B2'
    ws.sheet_view.showGridLines = True

wb = Workbook()
dist = Counter(d['status'] for d in D.values())
bl_by_status = Counter()
for d in D.values():
    bl_by_status[d['status']] += d['backlinks']
tot_dom = sum(dist.values()); tot_bl = len(LINKS)

# ================= Tab 1: Summary =================
ws = wb.active; ws.title = 'Summary'
ws.sheet_view.showGridLines = False
ws.merge_cells('B1:E2')
t = ws['B1']; t.value = 'Controlled Comfort'
t.font = Font(name=FONT, size=21, bold=True, color=ACCENT); t.alignment = ctr_v
for col, w in zip('ABCDE', [38.9, 16.3, 17.6, 18.7, 120.0]):
    ws.column_dimensions[col].width = w
# status table (rows 3-10)
sh = ['Status', 'Domains', 'Backlinks', 'Share of Domains', 'What it means']
for ci, h in enumerate(sh, 1):
    c = ws.cell(3, ci, h); c.fill = hdr_fill; c.font = Font(name=FONT, size=10, bold=True, color='FFFFFFFF')
    c.alignment = ctr; c.border = full_border
r = 4
for s in STATUS_ORDER:
    vals = [s, dist.get(s, 0), bl_by_status.get(s, 0), (dist.get(s, 0) / tot_dom if tot_dom else 0), STATUS_MEANS[s]]
    for ci, v in enumerate(vals, 1):
        c = ws.cell(r, ci, v); c.font = data_font; c.fill = white_fill; c.border = full_border
        if ci in (2, 3, 4): c.alignment = ctr_v
        elif ci == 5: c.alignment = Alignment(vertical='center', wrap_text=True)
        else: c.alignment = gen_v
        if ci == 4: c.number_format = '0.0%'
    r += 1
for ci, v in enumerate(['Total', tot_dom, tot_bl, 1.0, ''], 1):
    c = ws.cell(r, ci, v); c.font = Font(name=FONT, size=9, bold=True, color='FF000000'); c.fill = white_fill; c.border = full_border
    if ci in (2, 3, 4): c.alignment = ctr_v
    if ci == 4: c.number_format = '0.0%'
total_row = r
# key findings
kf_hdr = total_row + 1
ws.cell(kf_hdr, 1, 'Key findings').font = Font(name=FONT, size=10, bold=True, color='FF000000')
disavow_n = dist['Spam (Disavow)']; held_n = dist['Held (Pending Partner)'] + dist['Held (Nofollow, No Action)']
home_links = sum(1 for l in LINKS if l['prop'] == 'home'); deep_links = sum(1 for l in LINKS if l['prop'] == 'deep')
top_anchor = Counter(l['anchor'] for l in LINKS).most_common(1)[0]
findings = [
 f"{disavow_n + dist['Spam (Nofollow, No Action)']} of the {tot_dom} referring domains are spam; {disavow_n} have a dofollow link and go in the disavow file, {dist['Spam (Nofollow, No Action)']} are all-nofollow (no action).",
 f"The brief listed 56 domains; the live profile is {tot_dom} referring domains / {tot_bl} backlinks and is still growing (~70+ new referring domains a day).",
 "You can upload a disavow file for controlledcomfort.com only. No owned domains redirect in, so one file applies, and no disavow file exists on the property yet, so this is a new upload.",
 f"Two patterns, easy to tell apart. A home-page PBN/'buy backlinks' flood ({home_links} links) and a deep service-page directory campaign ({deep_links} links). The page a link points at separates them.",
 f'The biggest anchor is backlink sales copy: "{top_anchor[0][:60]}" on {top_anchor[1]} links.',
 f"{held_n} domains are held for the previous supplier to confirm which placements were commissioned, before anything is disavowed.",
 f"Held does not mean good: the {held_n} held domains are DR~0, zero-traffic directory pages. Held means 'may be commissioned, so the supplier decides'.",
]
for i, fx in enumerate(findings):
    rr = kf_hdr + 1 + i
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
    c = ws.cell(rr, 1, fx); c.font = data_font; c.alignment = Alignment(vertical='center', wrap_text=True)
# anchor profile table
ap_hdr = kf_hdr + 1 + len(findings)
ws.cell(ap_hdr, 1, 'Anchor text profile (all backlinks)').font = Font(name=FONT, size=11, bold=True, color=ACCENT)
ah = ['Anchor type', 'Backlinks', 'Share of Backlinks', 'Referring Domains']
for ci, h in enumerate(ah, 1):
    c = ws.cell(ap_hdr + 1, ci, h); c.fill = hdr_fill; c.font = hdr_font; c.alignment = ctr; c.border = full_border
atype = defaultdict(lambda: {'bl': 0, 'rd': set()})
for l in LINKS:
    a = atype[l['anchor_type']]; a['bl'] += 1; a['rd'].add(l['referring_domain'])
r = ap_hdr + 2
for name, a in sorted(atype.items(), key=lambda x: -x[1]['bl']):
    for ci, v in enumerate([name, a['bl'], a['bl'] / tot_bl, len(a['rd'])], 1):
        c = ws.cell(r, ci, v); c.font = data_font; c.fill = white_fill; c.border = full_border
        c.alignment = ctr_v if ci in (2, 3, 4) else gen_v
        if ci == 3: c.number_format = '0.0%'
    r += 1
for rr in range(1, r + 1):
    ws.row_dimensions[rr].height = 22.5
# logo
if LOGO and os.path.exists(LOGO):
    img = Image(LOGO)
    img.anchor = OneCellAnchor(_from=AnchorMarker(col=0, row=0, colOff=381000, rowOff=0),
                               ext=XDRPositiveSize2D(cx=1866900, cy=552450))
    ws.add_image(img)

# ================= Tab 2: Referring Domain Audit =================
ws = wb.create_sheet('Referring Domain Audit')
hdrs = ['Domain', 'Status', 'AS', 'Backlinks', "RD's", 'Traffic', 'In Disavow', 'Links Point To',
        'Dofollow Links', 'Nofollow Links', 'First Seen', 'Top Anchor Text', 'Example Linking Page',
        'Linking Page Title', 'Source', 'IP', 'Disavow Line']
rows = []
for dom in sorted(D, key=lambda x: (STATUS_ORDER.index(D[x]['status']), x)):
    d = D[dom]
    rows.append([dom, d['status'], num(d['dr']), num(d['backlinks']), num(d['refdomains']), num(d['traffic']),
                 'Yes' if d['in_disavow'] else 'No', d['links_point_to'], num(d['dofollow']), num(d['nofollow']),
                 as_date(d['first_seen']), d['top_anchor'], d['example_url'], d['example_title'], 'Ahrefs',
                 'n/a (not in export)', f"domain:{dom}" if d['in_disavow'] else ''])
data_tab(ws, hdrs, rows,
         [36, 24.7, 9.6, 13, 9.4, 9.7, 12.4, 21.3, 14, 8.7, 12, 45, 8.7, 40, 14, 15, 14],
         ['gen', 'gen', 'center', 'center', 'center', 'center', 'center', 'gen', 'center', 'center', 'center', 'gen', 'gen', 'gen', 'center', 'center', 'gen'],
         ['General', 'General', 'General', '#,##0', '#,##0', '#,##0', 'General', 'General', 'General', 'General', 'd mmm yyyy', 'General', 'General', 'General', 'General', 'General', 'General'],
         15.75)

# ================= Tab 3: All Backlinks =================
ws = wb.create_sheet('All Backlinks')
hdrs = ['Referring Domain', 'Status', 'Tool', 'Anchor Text', 'Anchor Type', 'Link Type',
        'Linking Page URL', 'Linking Page Title', 'Target URL']
rows = [[l['referring_domain'], l['status'], 'Ahrefs', l['anchor'], l['anchor_type'],
         ('Nofollow' if l['nofollow'] == 'True' else 'Dofollow'), l['url'], l['title'], l['target']] for l in LINKS]
data_tab(ws, hdrs, rows, [25.4, 27.1, 14.7, 55, 32, 10, 55, 53.1, 30.6],
         ['gen', 'gen', 'left', 'gen', 'gen', 'center', 'gen', 'gen', 'gen'],
         ['General'] * 9, 22.5)
ws.cell(1, 3).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)   # template quirk: "Tool" header left

# ================= Tab 4: Anchor Analysis =================
ws = wb.create_sheet('Anchor Analysis')
by_a = defaultdict(lambda: {'bl': 0, 'rd': set(), 'spam': set(), 'type': ''})
for l in LINKS:
    a = by_a[l['anchor']]; a['bl'] += 1; a['rd'].add(l['referring_domain']); a['type'] = l['anchor_type']
    if l['status'].startswith('Spam'): a['spam'].add(l['referring_domain'])
hdrs = ['Anchor Text', 'Anchor Type', 'Backlinks', 'Share of Backlinks', 'Referring Domains', 'Spam Domains Using It']
rows = [[anchor or '(empty)', a['type'], a['bl'], a['bl'] / tot_bl, len(a['rd']), len(a['spam'])]
        for anchor, a in sorted(by_a.items(), key=lambda x: -x[1]['bl'])]
data_tab(ws, hdrs, rows, [115.9, 37.7, 14, 8.7, None, 20.3],
         ['gen', 'gen', 'center', 'center', 'center', 'center'],
         ['General', 'General', '#,##0', '0.00%', 'General', 'General'], 22.5)
ws.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)  # template quirk: "Anchor Text" header no-wrap

# ================= Tab 5: Exact Match Anchors =================
ws = wb.create_sheet('Exact Match Anchors')
hdrs = ['Referring domain', 'Example backlink (linking page)', 'Exact-match commercial anchor', 'Market',
        'Site type (indicative)', 'Partner confirmed? (Y/N)', 'Final decision']
rows = []
for dom, d in sorted(D.items()):
    if not d['status'].startswith('Held'):
        continue
    ex = next((l for l in LINKS if l['referring_domain'] == dom and l['anchor_type'].startswith('Exact match')), None)
    if not ex:
        continue
    tgt = ex['target'].lower()
    market = 'Omaha NE, Heating/Furnace' if 'heating' in tgt else ('Omaha NE, Air Conditioning' if 'air-condition' in tgt else 'Omaha NE, HVAC')
    rows.append([dom, ex['url'], ex['anchor'], market, 'Directory / business listing', '', ''])
data_tab(ws, hdrs, rows, [25.4, 59, 53.1, 16, 24.6, 15.4, 15],
         ['gen', 'gen', 'center', 'center', 'gen', 'gen', 'gen'], ['General'] * 7, 22.5)
# input cells F (Partner confirmed) and G (Final decision): accent fill, white font, dropdowns
nrows = len(rows)
for ri in range(2, nrows + 2):
    for ci in (6, 7):
        c = ws.cell(ri, ci); c.fill = hdr_fill; c.font = input_font
if nrows:
    dv_yn = DataValidation(type='list', formula1='"Y,N"'); dv_kd = DataValidation(type='list', formula1='"Keep,Disavow"')
    ws.add_data_validation(dv_yn); ws.add_data_validation(dv_kd)
    dv_yn.add(f"F2:F{nrows + 1}"); dv_kd.add(f"G2:G{nrows + 1}")

# ================= Tab 6: Pending Disavow Lines =================
ws = wb.create_sheet('Pending Disavow Lines')
hdrs = ['Referring domain', 'Disavow line (append to disavow.txt once confirmed)', 'Recommendation']
rows = [[dom, f"domain:{dom}", 'Hold. Append to disavow.txt only if the supplier confirms it was NOT commissioned']
        for dom, d in sorted(D.items()) if d['status'].startswith('Held')]
data_tab(ws, hdrs, rows, [32, 44, 48], ['gen', 'gen', 'gen'], ['General'] * 3, 22.5)

# ================= Tab 7: Disavow List =================
ws = wb.create_sheet('Disavow List')
hdrs = ['Disavow Line', 'AS', 'Backlinks', "RD's", 'Traffic', 'Organic Keywords', 'Top Anchor Text']
dis = sorted(dom for dom, d in D.items() if d['status'] == 'Spam (Disavow)')
disset = set(dis)
emitted = [dom for dom in dis if not any(dom != p and dom.endswith('.' + p) for p in disset)]
rows = [[f"domain:{dom}", num(D[dom]['dr']), num(D[dom]['backlinks']), num(D[dom]['refdomains']),
         num(D[dom]['traffic']), num(D[dom]['keywords']), D[dom]['top_anchor']] for dom in emitted]
data_tab(ws, hdrs, rows, [44, 14, 15.6, 14, 11.1, 14.9, 98.9],
         ['gen', 'center', 'center', 'center', 'center', 'center', 'gen'],
         ['General', 'General', '#,##0', '#,##0', '#,##0', '#,##0', 'General'], 22.5)

wb.save(os.path.join(OUT, 'controlled_comfort_backlink_audit.xlsx'))

# ---------- disavow.txt ----------
def reason_group(dom):
    rs = D[dom]['reason']
    if 'host name' in rs: return 'PBN / link-farm host'
    if 'sales-copy' in rs: return 'PBN sales-copy anchor'
    if 'spam page title' in rs: return 'Spam page title (link-broker/PBN)'
    if 'off-topic' in rs: return 'Off-topic (pharma/casino)'
    return 'Spam'
groups = defaultdict(list)
for dom in emitted:
    groups[reason_group(dom)].append(dom)
held = sorted(dom for dom, d in D.items() if d['status'].startswith('Held'))
L = ['# Google disavow file for controlledcomfort.com (Controlled Comfort, Omaha NE)',
     '# Generated 2026-10-22 from Ahrefs export (1,089 ref. domains / 2,514 backlinks).',
     f'# ACTIVE DISAVOW LINES: {len(emitted)}', '#',
     '# Scope: ONE Search Console property (controlledcomfort.com). No owned domains redirect',
     '#   into the money site, so a single file applies. No disavow file currently exists on',
     '#   the property (client-confirmed), so this is a NEW upload (add), not a replace.',
     '# "Partner" in the workbook = the previous SEO SUPPLIER this brief names; same role.', '#',
     f'# EXCLUDED pending the supplier: {len(held)} HELD domains (exact-match commercial anchors /',
     '#   deep money-page links that may be COMMISSIONED directory placements). They are NOT in',
     '#   this file. Confirm with the supplier which were commissioned before relying on this.',
     '# Every line below rests on visible evidence (PBN host / sales-copy anchor / spam title).',
     "# Do not submit to Google Search Console on the client's behalf.", '']
for g in ['PBN / link-farm host', 'PBN sales-copy anchor', 'Spam page title (link-broker/PBN)',
          'Off-topic (pharma/casino)', 'Spam']:
    if groups.get(g):
        L.append(f'# === {g} ({len(groups[g])}) ===')
        L += [f'domain:{dom}' for dom in sorted(groups[g])]
        L.append('')
open(os.path.join(OUT, 'disavow_controlledcomfort.txt'), 'w').write('\n'.join(L))
print('built | domains', tot_dom, '| disavow', len(emitted), '| held', len(held), '| dist', dict(dist))
