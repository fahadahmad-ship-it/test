"""Build the RAS Systems backlink-audit workbook (7 tabs) + disavow files,
matching the signed-off K&K/NIC template exactly."""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import build, OWNED, MONEY_SITE
from classify import anchor_type
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'out')
os.makedirs(OUT, exist_ok=True)
LOGO = os.path.join(BASE, 'data', 'harbinger_logo.png')

ACCENT = 'FF0C343D'
GEIST = 'Geist'
thin = Side(style='thin')
BORDER_ALL = Border(left=thin, right=thin, top=thin, bottom=thin)
BORDER_HDR = Border(left=thin, right=thin, top=thin)  # header-only: no bottom
WHITE_FILL = PatternFill('solid', fgColor='FFFFFFFF')
ACCENT_FILL = PatternFill('solid', fgColor=ACCENT)

def hdr_font(sz=9): return Font(name=GEIST, size=sz, bold=True, color='FFFFFFFF')
def data_font(sz=9): return Font(name=GEIST, size=sz, bold=False, color='FF000000')
def input_font(sz=9): return Font(name=GEIST, size=sz, bold=False, color='FFFFFFFF')

# Per-tab column styling: data horizontal alignment ('c'=center, None=default) and number format.
# header alignment overrides {col_idx: (h,v,wrap)}; default header = center/center/wrap.
COLSPEC = {
    'Referring Domain Audit': {
        'data': {3:'c',4:'c',5:'c',6:'c',9:'c',10:'c',11:'c',15:'c',16:'c'},
        'nfmt': {4:'#,##0',5:'#,##0',6:'#,##0',11:'d mmm yyyy'},
        'hdr': {},
    },
    'All Backlinks': {
        'data': {3:'l',6:'c'},
        'nfmt': {},
        'hdr': {3:('left','center',True)},
    },
    'Anchor Analysis': {
        'data': {3:'c',4:'c',5:'c',6:'c'},
        'nfmt': {3:'#,##0',4:'0.00%'},
        'hdr': {1:('center','center',None)},
    },
    'Exact Match Anchors': {
        'data': {3:'c',4:'c'},
        'nfmt': {},
        'hdr': {},
    },
    'Pending Disavow Lines': {
        'data': {},
        'nfmt': {},
        'hdr': {},
    },
    'Disavow List': {
        'data': {2:'c',3:'c',4:'c',5:'c',6:'c'},
        'nfmt': {3:'#,##0',4:'#,##0',5:'#,##0',6:'#,##0'},
        'hdr': {},
    },
}
_ALIGN = {'c': 'center', 'l': 'left', None: None}

def set_header(ws, headers, row=1, height=31.5, hdr_overrides=None):
    hdr_overrides = hdr_overrides or {}
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row, c, h)
        cell.font = hdr_font(9)
        cell.fill = ACCENT_FILL
        if c in hdr_overrides:
            hh, vv, ww = hdr_overrides[c]
            cell.alignment = Alignment(horizontal=hh, vertical=vv, wrap_text=ww)
        else:
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER_HDR
    ws.row_dimensions[row].height = height

def data_cell(ws, r, c, v, sz=9, halign=None, nfmt=None):
    cell = ws.cell(r, c, v)
    cell.font = data_font(sz)
    cell.fill = WHITE_FILL
    cell.alignment = Alignment(horizontal=halign, vertical='center')
    if nfmt:
        cell.number_format = nfmt
    return cell

def put_row(ws, tab, r, values, input_cols=()):
    spec = COLSPEC.get(tab, {'data': {}, 'nfmt': {}})
    for c, v in enumerate(values, start=1):
        halign = _ALIGN.get(spec['data'].get(c))
        nfmt = spec['nfmt'].get(c)
        cell = data_cell(ws, r, c, v, halign=halign, nfmt=nfmt)
        if c in input_cols:
            cell.fill = ACCENT_FILL
            cell.font = input_font(9)

def widths(ws, wmap):
    for col, w in wmap.items():
        ws.column_dimensions[col].width = w

def finalize_data_tab(ws, nrows, ncols, data_height=22.5):
    last = get_column_letter(ncols)
    ws.freeze_panes = 'B2'
    ws.auto_filter.ref = f'A1:{last}{nrows}'
    for r in range(2, nrows + 1):
        ws.row_dimensions[r].height = data_height

def ts_to_dt(ts):
    if not ts:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).replace(tzinfo=None)
    except Exception:
        return None

# ---- status metadata ----
STATUS_ORDER = [
    ("Spam (Disavow)", "Confirmed spam with at least one dofollow link. Included in the disavow file."),
    ("Held (Pending Partner)", "Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous SEO partner confirms."),
    ("Held (Nofollow, No Action)", "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way."),
    ("Spam (Nofollow, No Action)", "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed."),
    ("Keep", "Genuine or harmless link. Keep."),
    ("Own Site", "Client owned domain that redirects into the site."),
]

ANCHOR_TYPE_ORDER = [
    "Spam: keyword stuffed SEO sales copy", "Naked URL", "Exact match commercial",
    "Exact match commercial (geo)", "Generic", "Branded", "Empty or image",
    "Spam: off topic", "Contextual or other",
]

def fmt_pct(x):
    return x

def main():
    R = build()
    records = R['records']
    links = R['links']
    by_status = defaultdict(list)
    for rec in records:
        by_status[rec['status']].append(rec)
    total_domains = len(records)
    total_backlinks = len(links)

    # ---------- anchor profile (all backlinks) ----------
    atype_bl = Counter()
    atype_rd = defaultdict(set)
    for l in links:
        atype_bl[l['atype']] += 1
        atype_rd[l['atype']].add(l['referring_domain'])

    wb = openpyxl.Workbook()

    # ================= SUMMARY =================
    ws = wb.active
    ws.title = 'Summary'
    ws.sheet_view.showGridLines = False
    widths(ws, {'A': 38.86, 'B': 16.29, 'C': 17.57, 'D': 18.71, 'E': 120.0})
    for r in range(1, 40):
        ws.row_dimensions[r].height = 22.5
    # title
    ws.merge_cells('B1:E2')
    t = ws['B1']; t.value = 'RAS Systems'
    t.font = Font(name=GEIST, size=21, bold=True, color=ACCENT)
    t.alignment = Alignment(horizontal='center', vertical='center')
    # logo
    if os.path.exists(LOGO):
        img = XLImage(LOGO)
        img.width = 170; img.height = 50
        ws.add_image(img, 'A1')
        # nudge anchor to match template colOff 381000
        from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
        from openpyxl.drawing.xdr import XDRPositiveSize2D
        marker = AnchorMarker(col=0, colOff=381000, row=0, rowOff=0)
        img.anchor = OneCellAnchor(_from=marker, ext=XDRPositiveSize2D(cx=1866900, cy=552450))

    # status table
    hdrs = ['Status', 'Domains', 'Backlinks', 'Share of Domains', 'What it means']
    for c, h in enumerate(hdrs, 1):
        cell = ws.cell(3, c, h)
        cell.font = Font(name=GEIST, size=10, bold=True, color='FFFFFFFF')
        cell.fill = ACCENT_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER_ALL
    row = 4
    sum_bl_by_status = {}
    for status, meaning in STATUS_ORDER:
        recs = by_status.get(status, [])
        dom_n = len(recs)
        bl_n = sum(x['backlinks'] for x in recs)
        sum_bl_by_status[status] = bl_n
        share = dom_n / total_domains if total_domains else 0
        vals = [status, dom_n, bl_n, share, meaning]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row, c, v)
            cell.font = data_font(9)
            cell.fill = WHITE_FILL
            cell.alignment = Alignment(horizontal=('center' if c in (2, 3, 4) else None),
                                       vertical='center', wrap_text=(c == 5))
            cell.border = BORDER_ALL
            if c in (2, 3):
                cell.number_format = '#,##0'
            if c == 4:
                cell.number_format = '0.0%'
        row += 1
    # total
    tot_vals = ['Total', total_domains, total_backlinks, 1.0, '']
    for c, v in enumerate(tot_vals, 1):
        cell = ws.cell(row, c, v)
        cell.font = Font(name=GEIST, size=9, bold=True, color='FF000000')
        cell.fill = WHITE_FILL
        cell.alignment = Alignment(horizontal=('center' if c in (2, 3, 4) else None), vertical='center')
        cell.border = BORDER_ALL
        if c in (2, 3):
            cell.number_format = '#,##0'
        if c == 4:
            cell.number_format = '0.0%'
    total_row = row
    row += 1

    # Key findings
    kf_head = ws.cell(row, 1, 'Key findings')
    kf_head.font = Font(name=GEIST, size=10, bold=True, color=ACCENT)
    row += 1
    disavow_recs = by_status.get('Spam (Disavow)', [])
    nofollow_spam = by_status.get('Spam (Nofollow, No Action)', [])
    held_recs = by_status.get('Held (Pending Partner)', []) + by_status.get('Held (Nofollow, No Action)', [])
    keep_recs = by_status.get('Keep', [])
    spam_total = len(disavow_recs) + len(nofollow_spam)
    # home vs deep
    home_links = sum(1 for l in links if l['tpath'] in ('/', ''))
    deep_links = total_backlinks - home_links
    top_anchor_item = atype_bl.most_common(1)
    # biggest single anchor text
    anc_text = Counter(l['anchor'] for l in links if l['anchor'].strip())
    big_anchor, big_anchor_n = anc_text.most_common(1)[0]
    big_anchor_rd = len(set(l['referring_domain'] for l in links if l['anchor'] == big_anchor))
    held_zero_traffic = sum(1 for x in held_recs if x['traffic'] == 0)
    # property attribution counts
    prop_counts = Counter(l['property'] for l in links)
    redirect_doms = sum(1 for l in links if l['property'] in OWNED and l['property'] != MONEY_SITE)

    findings = [
        f"{spam_total} of the {total_domains} referring domains are spam. {len(disavow_recs)} have a dofollow link and go in the disavow file; the other {len(nofollow_spam)} are nofollow and need no action.",
        f"The attack has exploded since the brief: about 458 referring domains in the brief's snapshot, {total_domains} now (Semrush counts 2,815 at root level; Ahrefs adds the rest). We audited the full live profile, not the brief's list.",
        f"You can upload a disavow file for ras-systems.com only. That one file carries the complete union of every bad domain, including the {redirect_doms} links that reach the site through the rasmachines.com, ras-systems.net and ras-systems.us redirects.",
        f"Two patterns, easy to tell apart. {home_links} of {total_backlinks} links ({home_links/total_backlinks*100:.0f}%) hit the home page — the link-selling flood; the deep links to product and news pages are the smaller, separate set.",
        f"The single biggest anchor, on {big_anchor_rd} domains, is backlink sales copy: “{big_anchor[:70]}…” — it advertises a link-selling service and names the client's own domain.",
        f"{len(held_recs)} domains are held for the previous SEO partner to confirm, in case any were commissioned placements (exact-match product anchors or deep product-page links). Nothing is submitted until that question is answered.",
        f"Held does not mean valuable: {held_zero_traffic} of the {len(held_recs)} held domains have no organic traffic at all. The nine anchor families in Tab 05 all advertise link-selling services, not the business.",
    ]
    for f_txt in findings:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        cell = ws.cell(row, 1, f_txt)
        cell.font = data_font(9)
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        row += 1

    # Anchor profile table
    ap_head = ws.cell(row, 1, 'Anchor text profile (all backlinks)')
    ap_head.font = Font(name=GEIST, size=10, bold=True, color=ACCENT)
    row += 1
    for c, h in enumerate(['Anchor type', 'Backlinks', 'Share of Backlinks', 'Referring Domains'], 1):
        cell = ws.cell(row, c, h)
        cell.font = Font(name=GEIST, size=10, bold=True, color='FFFFFFFF')
        cell.fill = ACCENT_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER_ALL
    row += 1
    for at in ANCHOR_TYPE_ORDER:
        bl = atype_bl.get(at, 0)
        if bl == 0:
            continue
        rd = len(atype_rd.get(at, set()))
        share = bl / total_backlinks if total_backlinks else 0
        vals = [at, bl, share, rd]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row, c, v)
            cell.font = data_font(9)
            cell.fill = WHITE_FILL
            cell.alignment = Alignment(horizontal=('center' if c in (2, 3, 4) else None), vertical='center')
            cell.border = BORDER_ALL
            if c in (2, 4):
                cell.number_format = '#,##0'
            if c == 3:
                cell.number_format = '0.0%'
        row += 1

    # ================= REFERRING DOMAIN AUDIT =================
    ws = wb.create_sheet('Referring Domain Audit')
    rd_headers = ['Domain', 'Status', 'AS', 'Backlinks', "RD's", 'Traffic', 'In Disavow',
                  'Links Point To', 'Dofollow Links', 'Nofollow Links', 'First Seen',
                  'Top Anchor Text', 'Example Linking Page', 'Linking Page Title', 'Source',
                  'IP', 'Disavow Line']
    set_header(ws, rd_headers, hdr_overrides=COLSPEC['Referring Domain Audit']['hdr'])
    widths(ws, {'A': 36.0, 'B': 24.71, 'C': 9.57, 'D': 13.0, 'E': 9.43, 'F': 9.71, 'G': 12.43,
                'H': 21.29, 'I': 14.0, 'J': 8.71, 'K': 12.0, 'L': 45.0, 'M': 8.71, 'N': 40.0,
                'O': 14.0, 'P': 15.0, 'Q': 14.0})
    recs_sorted = sorted(records, key=lambda x: (STATUS_SORT.get(x['status'], 9), -x['backlinks'], x['domain']))
    r = 2
    for rec in recs_sorted:
        in_disavow = 'Yes' if rec['status'] == 'Spam (Disavow)' else ('Held' if rec['base'] == 'Held' else 'No')
        disavow_line = f"domain:{rec['domain']}" if rec['status'] == 'Spam (Disavow)' else ''
        ex = rec['example']
        fs = ts_to_dt(rec['first_seen'])
        row_vals = [rec['domain'], rec['status'], rec['ascore'], rec['backlinks'], rec['rds_own'],
                    rec['traffic'], in_disavow, rec['links_point_to'], rec['dofollow'], rec['nofollow'],
                    fs, rec['top_anchor'], ex['source_url'], ex['title'], rec['source'], rec['ip'], disavow_line]
        put_row(ws, 'Referring Domain Audit', r, row_vals)
        r += 1
    finalize_data_tab(ws, r - 1, len(rd_headers), data_height=15.75)

    # ================= ALL BACKLINKS =================
    ws = wb.create_sheet('All Backlinks')
    bl_headers = ['Referring Domain', 'Status', 'Tool', 'Anchor Text', 'Anchor Type', 'Link Type',
                  'Linking Page URL', 'Linking Page Title', 'Target URL']
    set_header(ws, bl_headers, hdr_overrides=COLSPEC['All Backlinks']['hdr'])
    widths(ws, {'A': 25.43, 'B': 27.14, 'C': 14.71, 'D': 55.0, 'E': 32.0, 'F': 10.0, 'G': 55.0,
                'H': 53.14, 'I': 30.57})
    status_by_dom = {rec['domain']: rec['status'] for rec in records}
    links_sorted = sorted(links, key=lambda l: (l['referring_domain'], l['source_url']))
    r = 2
    for l in links_sorted:
        st = status_by_dom.get(l['referring_domain'], '')
        lt = 'Nofollow' if l['nofollow'] else 'Dofollow'
        row_vals = [l['referring_domain'], st, l['source'], l['anchor'], l['atype'], lt,
                    l['source_url'], l['title'], l['target_url']]
        put_row(ws, 'All Backlinks', r, row_vals)
        r += 1
    finalize_data_tab(ws, r - 1, len(bl_headers))

    # ================= ANCHOR ANALYSIS =================
    ws = wb.create_sheet('Anchor Analysis')
    an_headers = ['Anchor Text', 'Anchor Type', 'Backlinks', 'Share of Backlinks',
                  'Referring Domains', 'Spam Domains Using It']
    set_header(ws, an_headers, hdr_overrides=COLSPEC['Anchor Analysis']['hdr'])
    widths(ws, {'A': 115.86, 'B': 37.71, 'C': 14.0, 'D': 8.71, 'E': 13.0, 'F': 20.29})
    anc_bl = Counter(l['anchor'] for l in links)
    anc_rd = defaultdict(set)
    anc_spamrd = defaultdict(set)
    spam_statuses = {'Spam (Disavow)', 'Spam (Nofollow, No Action)'}
    for l in links:
        anc_rd[l['anchor']].add(l['referring_domain'])
        if status_by_dom.get(l['referring_domain']) in spam_statuses:
            anc_spamrd[l['anchor']].add(l['referring_domain'])
    r = 2
    for anc, bl in sorted(anc_bl.items(), key=lambda kv: -kv[1]):
        row_vals = [anc, anchor_type(anc), bl, bl / total_backlinks,
                    len(anc_rd[anc]), len(anc_spamrd[anc])]
        put_row(ws, 'Anchor Analysis', r, row_vals)
        r += 1
    finalize_data_tab(ws, r - 1, len(an_headers))

    # ================= EXACT MATCH ANCHORS =================
    ws = wb.create_sheet('Exact Match Anchors')
    em_headers = ['Referring domain', 'Example backlink (linking page)', 'Exact-match commercial anchor',
                  'Market', 'Site type (indicative)', 'Partner confirmed? (Y/N)', 'Final decision']
    set_header(ws, em_headers)
    widths(ws, {'A': 25.43, 'B': 59.0, 'C': 53.14, 'D': 16.0, 'E': 24.57, 'F': 15.43, 'G': 15.0})
    # one row per domain+exact-match anchor
    em_rows = []
    seen_em = set()
    for l in links:
        if l['atype'] in ('Exact match commercial', 'Exact match commercial (geo)'):
            key = (l['referring_domain'], l['anchor'])
            if key in seen_em:
                continue
            seen_em.add(key)
            market = 'Geo' if l['atype'].endswith('(geo)') else 'Non-geo'
            em_rows.append((l['referring_domain'], l['source_url'], l['anchor'], market))
    em_rows.sort(key=lambda x: (x[0], x[2]))
    r = 2
    for dom, page, anchor, market in em_rows:
        put_row(ws, 'Exact Match Anchors', r,
                [dom, page, anchor, market, 'Low quality web directory / blog', '', ''],
                input_cols=(6, 7))
        r += 1
    finalize_data_tab(ws, max(r - 1, 1), len(em_headers))

    # ================= PENDING DISAVOW LINES =================
    ws = wb.create_sheet('Pending Disavow Lines')
    pd_headers = ['Referring domain', 'Disavow line (append to disavow.txt once confirmed)', 'Recommendation']
    set_header(ws, pd_headers)
    widths(ws, {'A': 32.0, 'B': 44.0, 'C': 48.0})
    r = 2
    held_sorted = sorted(held_recs, key=lambda x: x['domain'])
    for rec in held_sorted:
        rec_text = 'Append only if the partner does not claim it, to disavow_ras-systems.com.txt'
        put_row(ws, 'Pending Disavow Lines', r, [rec['domain'], f"domain:{rec['domain']}", rec_text])
        r += 1
    finalize_data_tab(ws, max(r - 1, 1), len(pd_headers))

    # ================= DISAVOW LIST =================
    ws = wb.create_sheet('Disavow List')
    dl_headers = ['Disavow Line', 'AS', 'Backlinks', "RD's", 'Traffic', 'Organic Keywords', 'Top Anchor Text']
    set_header(ws, dl_headers)
    widths(ws, {'A': 44.0, 'B': 14.0, 'C': 15.57, 'D': 14.0, 'E': 11.14, 'F': 14.86, 'G': 98.86})
    disavow_sorted = sorted(disavow_recs, key=lambda x: x['domain'])
    r = 2
    for rec in disavow_sorted:
        put_row(ws, 'Disavow List', r, [f"domain:{rec['domain']}", rec['ascore'], rec['backlinks'],
                rec['rds_own'], rec['traffic'], rec['keywords'], rec['top_anchor']])
        r += 1
    finalize_data_tab(ws, max(r - 1, 1), len(dl_headers))

    out_path = os.path.join(OUT, 'RAS_Systems_Backlinks_Audit.xlsx')
    wb.save(out_path)

    # ---------- disavow files ----------
    write_disavow_files(records, links)
    # ---------- client delivery note ----------
    write_delivery_note(records, links)

    # ---------- counts ----------
    print('=== COUNTS ===')
    print('total domains:', total_domains, '| total backlinks:', total_backlinks)
    for status, _ in STATUS_ORDER:
        print(f'  {status}: {len(by_status.get(status, []))} domains, {sum_bl_by_status.get(status,0)} backlinks')
    print('disavow domains (union):', len(disavow_recs))
    print('held domains:', len(held_recs))
    print('workbook:', out_path)
    return R

STATUS_SORT = {'Spam (Disavow)': 0, 'Held (Pending Partner)': 1, 'Held (Nofollow, No Action)': 2,
               'Spam (Nofollow, No Action)': 3, 'Keep': 4, 'Own Site': 5}

REASON_GROUP = {
    'PBN / link-selling sales-copy anchor': 'Link-selling / PBN sales-copy anchors',
    'off-topic (casino/pharma/etc.) anchor': 'Off-topic (casino / pharma / adult) anchors',
    'spam host name (seo/backlink/directory signature)': 'Spam host-name signatures',
    'spam page title template': 'Spam page-title templates',
}

def write_delivery_note(records, links):
    by_status = defaultdict(list)
    for r in records:
        by_status[r['status']].append(r)
    total_domains = len(records)
    total_backlinks = len(links)
    disavow = by_status.get('Spam (Disavow)', [])
    nf_spam = by_status.get('Spam (Nofollow, No Action)', [])
    held = by_status.get('Held (Pending Partner)', []) + by_status.get('Held (Nofollow, No Action)', [])
    keep = by_status.get('Keep', [])
    spam_total = len(disavow) + len(nf_spam)
    home_links = sum(1 for l in links if l['tpath'] in ('/', ''))
    dom_links = defaultdict(list)
    for l in links:
        dom_links[l['referring_domain']].append(l)
    # attribution counts
    prop_doms = defaultdict(set)
    disavow_set = set(r['domain'] for r in disavow)
    for l in links:
        if l['referring_domain'] in disavow_set:
            prop_doms[l['property']].add(l['referring_domain'])
    held_zero = sum(1 for r in held if r['traffic'] == 0)
    # nine anchor families
    anc_fam = Counter()
    for l in links:
        if l['atype'] == 'Spam: keyword stuffed SEO sales copy':
            anc_fam[family_of(l['anchor'])] += 1
    today = datetime.date.today().isoformat()
    md = []
    md.append(f"# RAS Systems — Backlink Audit & Disavow Review")
    md.append(f"*Prepared by Harbinger Marketing — {today}*\n")
    md.append("## The short version\n")
    md.append(f"- Your referring-domain profile is under a large, **active link-selling / negative-SEO flood**. "
              f"Of **{total_domains:,} referring domains**, **{spam_total:,} are spam** "
              f"({len(disavow):,} with a dofollow link that passes value — these go in the disavow file — "
              f"and {len(nf_spam):,} nofollow that need no action).")
    md.append(f"- The brief's figure (about 458 referring domains, 183 link-selling) was a months-old snapshot. "
              f"The attack has since **roughly quadrupled**: Semrush counted ~629 referring domains in September and "
              f"**2,815 now**; with Ahrefs-only discoveries the full live profile is **{total_domains:,}**. "
              f"We audited the full live profile, not the brief's list.")
    md.append(f"- **{len(held):,} domains are held**, not disavowed — they carry exact-match product anchors or point at "
              f"deep product pages and *may* have been commissioned by a previous SEO partner. "
              f"**Nothing is submitted to Google until that question is answered.**")
    md.append(f"- **{len(keep):,} domains are genuine** (real directories, business listings and editorial mentions) and are kept.\n")
    md.append("## What's actually happening\n")
    md.append(f"Two separate campaigns, easy to tell apart by the page they point at:\n")
    md.append(f"1. **The link-selling flood (the problem).** {home_links:,} of {total_backlinks:,} links "
              f"({home_links/total_backlinks*100:.0f}%) point at the **home page**, carrying keyword-stuffed SEO sales-copy "
              f"anchors that advertise a backlink service and name your own domains "
              f"(ras-systems.com, rasmachines.com, ras-systems.net). This is the negative-SEO / link-spam pattern.")
    md.append(f"2. **The commissioned-looking set (the open question).** A much smaller set uses exact-match product anchors "
              f"(e.g. *Panel Bending Machine*, *Metal Folding Machinery*, *FLEXIbend*) or points at deep `/products/` pages. "
              f"These look like they could have been paid placements. They are **held** for the partner to confirm.\n")
    md.append(f"The nine link-selling anchor families driving the flood:\n")
    for fam, n in anc_fam.most_common(9):
        md.append(f"   - {fam} — ~{n:,} links")
    md.append("")
    md.append("## The redirect reality — one file to upload\n")
    md.append(f"Three domains you own 301-redirect into the money site, so Semrush folds their inbound links into "
              f"ras-systems.com's profile:\n")
    md.append(f"| Redirects into ras-systems.com | Spam domains attributed |")
    md.append(f"|---|---|")
    for p in ('rasmachines.com', 'ras-systems.net', 'ras-systems.us'):
        md.append(f"| {p} | {len(prop_doms.get(p, set())):,} |")
    md.append("")
    md.append(f"A disavow file applies to **one** Search Console property. We produced one file per property, but the "
              f"**`disavow_ras-systems.com.txt`** file carries the **complete union** of every bad domain "
              f"({len(disavow):,} domains) — because all owned domains redirect into the money site and Google forwards "
              f"disavow signals across redirects imperfectly. ")
    md.append(f"**If you can only upload to the ras-systems.com Search Console property (the usual case), submit that one "
              f"file and ignore the rest.** If you have Search Console access to the redirect domains too, you may upload "
              f"their per-property files as well. Please tell us which properties you can upload to.\n")
    md.append("## Before you upload — two decisions we need from you\n")
    md.append(f"1. **The commissioned question (blocking).** Were any of the **{len(held):,} held domains** paid for by your "
              f"previous SEO partner? If yes, name them and we remove them from consideration; if no, we append them to the "
              f"disavow file. Until you answer, they stay out. (Worth knowing: held does **not** mean valuable — "
              f"{held_zero} of the {len(held)} held domains have no organic traffic at all.)")
    md.append(f"2. **Disavow vs. dilute.** Uploading a disavow file is the direct fix, but it is a strong signal to Google and "
              f"is not easily reversed. The alternative is to **dilute** the spam by building a steady stream of genuine, "
              f"branded, on-topic links so the bad ratio falls over time, and disavow only the worst offenders. "
              f"Our recommendation: **disavow the {len(disavow):,} confirmed-spam dofollow domains** (they are unambiguous "
              f"link-spam and carry no value to lose), and run branded-link building alongside to rebuild profile health. "
              f"We can set out a dilution plan if you prefer to hold off on disavowing.\n")
    md.append("## Honest limits\n")
    md.append(f"- **Nothing has been submitted to Google.** The disavow files are drafts pending your answer on the held set.")
    md.append(f"- We have **not** been told whether a disavow file is already filed on ras-systems.com. If one exists, "
              f"uploading ours **replaces** it — check first and send us any existing file so we can merge.")
    md.append(f"- Organic traffic / keyword figures are Semrush. For the low-authority spam domains that Semrush holds no "
              f"organic data for, we record a true zero (spot-checked); that absence of any audience is itself the clearest "
              f"sign the domain is a link farm.")
    md.append(f"- Linking-page live status reflects each tool's last crawl ({sum(1 for l in links if str(l['response_code'])=='200'):,} "
              f"of {total_backlinks:,} link sources last seen returning HTTP 200).\n")
    md.append("## Files in this delivery\n")
    md.append("- `RAS_Systems_Backlinks_Audit.xlsx` — the full 7-tab audit workbook.")
    md.append("- `disavow_ras-systems.com.txt` — **the file to upload** (full union; do not upload before the held question is answered).")
    md.append("- `disavow_rasmachines.com.txt`, `disavow_ras-systems.net.txt` — per-property reference files.")
    with open(os.path.join(OUT, 'DELIVERY.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')

FAMILY_PATTERNS = [
    ('"High Authority … Backlinks for … SEO Ranking Growth"', ['high authority', 'ranking growth']),
    ('"… Premium SEO Links for Higher … Rankings"', ['premium seo links']),
    ('"High Quality Dofollow Backlinks DA 50 PA 40 … PBN Network Service"', ['da 50 pa 40', 'premium pbn network']),
    ('Guest-post service ("Proven/Expert Guest Post Service for …")', ['guest post service']),
    ('"Effective PBN Backlinks for … Strengthen Your Link Profile"', ['effective pbn backlinks', 'strengthen your link']),
    ('TELEGRAM @… link-service handles', ['telegram @']),
    ('MASSLINKER.COM backlink software', ['masslinker']),
    ('SEO-LINK.VIP / SEOExpress link vendors', ['seo-link.vip', 'seoexpress']),
    ('Fake testimonials ("Thanks to … +50% traffic", "… 300 new leads")', ['we improved our site', 'more monthly leads', 'gained +']),
]

def family_of(anchor):
    al = (anchor or '').lower()
    for name, pats in FAMILY_PATTERNS:
        if any(p in al for p in pats):
            return name
    return 'Other link-selling sales copy'

def write_disavow_files(records, links):
    disavow_recs = [r for r in records if r['status'] == 'Spam (Disavow)']
    # property -> set of disavow domains whose links point there
    prop_doms = defaultdict(set)
    dom_links = defaultdict(list)
    for l in links:
        dom_links[l['referring_domain']].append(l)
    disavow_set = set(r['domain'] for r in disavow_recs)
    for l in links:
        if l['referring_domain'] in disavow_set:
            prop_doms[l['property']].add(l['referring_domain'])
    today = datetime.date.today().isoformat()
    # money-site file = full union
    properties = ['ras-systems.com', 'rasmachines.com', 'ras-systems.net', 'ras-systems.us']
    reason_by_dom = {r['domain']: r['reason'] for r in disavow_recs}
    for prop in properties:
        if prop == MONEY_SITE:
            doms = sorted(disavow_set)  # full union
            union_note = ("# This is the MONEY-SITE file. It carries the COMPLETE UNION of every spam\n"
                          "# domain found, including domains whose links reach the site only through the\n"
                          "# rasmachines.com, ras-systems.net and ras-systems.us 301 redirects. Google forwards\n"
                          "# disavow signals across redirects imperfectly, so the union is intentional and safe.\n")
        else:
            doms = sorted(prop_doms.get(prop, set()))
            union_note = ("# Reference file for this redirect property. If the client can only upload to the\n"
                          "# ras-systems.com Search Console property, submit disavow_ras-systems.com.txt only;\n"
                          "# this per-property file is reference.\n")
        if not doms and prop != MONEY_SITE:
            continue
        lines = []
        lines.append(f"# Disavow file for property: {prop}")
        lines.append(f"# Generated {today} — RAS Systems backlink audit (Harbinger Marketing)")
        lines.append(f"# Domains listed: {len(doms)}")
        lines.append("#")
        lines.append("# WARNING: Do NOT upload this file to Google Search Console before the previous SEO")
        lines.append("#          partner has confirmed which (if any) of the HELD domains were commissioned.")
        lines.append("#          Held domains are intentionally EXCLUDED from this file (see Tab 06).")
        lines.append("#          We have not been told whether a disavow file is already filed on this")
        lines.append("#          property; if one exists, uploading REPLACES it — confirm with the client first.")
        lines.append("#")
        for ln in union_note.rstrip('\n').split('\n'):
            lines.append(ln)
        lines.append("#")
        # group by reason
        groups = defaultdict(list)
        for d in doms:
            groups[REASON_GROUP.get(reason_by_dom.get(d, ''), 'Other spam evidence')].append(d)
        for gname in sorted(groups):
            glist = sorted(groups[gname])
            lines.append(f"# --- {gname} ({len(glist)}) ---")
            for d in glist:
                lines.append(f"domain:{d}")
            lines.append("#")
        path = os.path.join(OUT, f'disavow_{prop}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()
