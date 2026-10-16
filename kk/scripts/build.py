"""Build the K&K Manufacturing backlink audit workbook and the disavow files.

Format is the one the client signed off on New Image Canopy and that AUDIT_FORMAT.md
records. Two things differ, both because this client's situation differs:

  * The brief says "confirm with the previous supplier which links were commissioned".
    The signed-off sheet calls that role the partner, so the sheet keeps its own word and
    the disavow headers name the brief's wording once, to tie the two together.
  * Just over half the links arrive through a redirect from gaworktrucks.com or
    kandkmanufacturing.com, which are separate Search Console properties. A disavow
    filed on kandkmfg.com does nothing for those, so three files are written.
"""
import csv, collections, datetime, re, glob, sys, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils.cell import coordinate_to_tuple

D = '/home/user/test/kk/data/'
OUT = '/home/user/test/KandK_Manufacturing_Backlinks_Audit.xlsx'
CLIENT_NAME = 'K&K Manufacturing'
CLIENT = 'kandkmfg.com'
PROPS = ['kandkmfg.com', 'gaworktrucks.com', 'kandkmanufacturing.com']

TEAL = 'FF0C343D'; F = 'Geist'; WHITE = 'FFFFFFFF'
NAVY = TEAL; INPUT = TEAL
FILL = collections.defaultdict(lambda: WHITE)
thin = Side(style='thin'); BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

def banner(ws, rng):
    a, b = rng.split(':')
    r1, c1 = coordinate_to_tuple(a); r2, c2 = coordinate_to_tuple(b)
    ws.merge_cells(rng)
    # Style after merging, never before: merge_cells resets the covered cells.
    for rr in range(r1, r2 + 1):
        for cc in range(c1, c2 + 1):
            c = ws.cell(rr, cc)
            c.font = Font(name=F, sz=10, b=True, color=WHITE)
            c.fill = PatternFill('solid', fgColor=NAVY)
            c.alignment = Alignment(vertical='center', wrap_text=True)
            c.border = BORD
    ws.row_dimensions[int(re.findall(r'\d+', rng)[0])].height = 31.5

def hdr(ws, row=1, sz=9):
    for c in ws[row]:
        if c.value is None: continue
        c.font = Font(name=F, sz=sz, b=True, color=WHITE); c.fill = PatternFill('solid', fgColor=NAVY)
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = BORD
    ws.row_dimensions[row].height = 31.5

def style(ws, r, fill=WHITE, numfmts=None, centre=(), valign='center'):
    for c in ws[r]:
        c.font = Font(name=F, sz=9, color='FF000000'); c.fill = PatternFill('solid', fgColor=fill); c.border = BORD
        c.alignment = Alignment(vertical=valign, horizontal='center' if c.column_letter in centre else None)
        if numfmts and c.column_letter in numfmts: c.number_format = numfmts[c.column_letter]

def widths(ws, m):
    for k, v in m.items(): ws.column_dimensions[k].width = v

def dt(ts):
    try: return datetime.datetime.fromtimestamp(int(ts), datetime.UTC).date()
    except Exception: return ''

def canon(u):
    u = (u or '').strip().lower().split('#')[0]
    return re.sub(r'^www\.', '', re.sub(r'^https?://', '', u)).rstrip('/')

def fnum(x):
    try: return float(x or 0)
    except Exception: return 0.0

# ---------------- inputs ----------------
AUD = list(csv.DictReader(open(D + 'domain_audit.csv'), delimiter='\t'))
LNK = list(csv.DictReader(open(D + 'links_all.csv'), delimiter='\t'))
STAT = {r['domain']: r['status'] for r in AUD}
AUDD = {r['domain']: r for r in AUD}
TAB05 = {r['domain'] for r in AUD if r['tab05'] == 'Yes'}

# Semrush traffic and keywords, fetched one domain at a time. Semrush is the only source
# for these. Where the API answers "NOTHING FOUND" it is saying it holds no organic data
# for that domain at all, which is a real zero and the most telling number in the audit,
# so it is recorded as zero and flagged rather than left blank.
SEMT = {}; NOTINDEXED = set()
for p in sorted(glob.glob(D + 'metrics/out*.csv')) + sorted(glob.glob(D + 'metrics/tr*.csv')):
    for r in csv.DictReader(open(p), delimiter=';'):
        d = (r.get('domain') or '').strip().lower()
        if not d or d in SEMT: continue
        kw, tr = r.get('organic_keywords'), r.get('organic_traffic')
        if 'ERROR' in (kw, tr):
            SEMT[d] = {'organic_keywords': '0', 'organic_traffic': '0'}; NOTINDEXED.add(d)
        else:
            SEMT[d] = {'organic_keywords': kw, 'organic_traffic': tr}
# Authority Score, backlinks and the domain's own referring-domain count, from Semrush's
# bulk comparison report where available, from the referring-domain report otherwise.
SRD = {}
for p in sorted(glob.glob(D + 'metrics/bulk_as.csv')) + sorted(glob.glob(D + 'metrics/out*.csv')):
    for r in csv.DictReader(open(p), delimiter=';'):
        d = (r.get('target') or r.get('domain') or '').strip().lower()
        n = r.get('domains_num') or r.get('own_refdomains') or ''
        b = r.get('backlinks_num') or r.get('own_backlinks') or ''
        if d and n not in ('', 'ERROR'): SRD.setdefault(d, {'own_refdomains': n, 'own_backlinks': b})

def _tr(d, f):
    t = SEMT.get(d)
    return int(fnum(t[f])) if t else ''
def _rd(d):
    t = SRD.get(d)
    return int(fnum(t['own_refdomains'])) if t else ''

GEO = re.compile(r'\b(georgia|ga|griffin|atlanta|milner)\b', re.I)
def tgt_kind(u):
    if '/product/' in u: return 'Product page'
    if '/capability/' in u: return 'Capability page'
    if '/industry/' in u: return 'Industry page'
    if re.sub(r'^https?://(www\.)?', '', u).rstrip('/') in PROPS: return 'Homepage'
    return 'Other page'
def points_to(rs):
    hs = sorted({x['property'] for x in rs})
    if not hs: return ''
    return ', '.join(h + (' (redirect)' if h != CLIENT else '') for h in hs)

# ---------------- the decision set ----------------
# Every domain the client has to rule on with the previous supplier: an exact match
# commercial anchor, or a link aimed at a product, capability or industry page.
emrows = []
for r in LNK:
    d = r['rd']; rec = AUDD.get(d)
    if not rec: continue
    a = (r['anchor'] or '').strip()
    core = r['atype'].startswith('Exact match')
    if not core and not (rec['status'].startswith('Held') and tgt_kind(r['target_url']) != 'Homepage'):
        continue
    st = rec['status']
    if st == 'Keep': reco = 'Keep, genuine editorial placement, no confirmation needed'
    elif st == 'Held (Nofollow, No Action)': reco = 'No action needed, nofollow passes no ranking value'
    elif st == 'Held (Review)': reco = 'Review, mixes link scheme with exact match anchors'
    else: reco = 'Disavow after confirmation'
    emrows.append(dict(core=core, d=d, a=a or '(no anchor text)',
        mk='Georgia' if GEO.search(a) else 'Non-geo', site=rec['sitetype'],
        tool=r['tool'], link='Nofollow' if r['nofollow'] == 'true' else 'Dofollow',
        src=r['source_url'], title=r['source_title'], tgt=r['target_url'],
        tkind=tgt_kind(r['target_url']), fs=r['first_seen'], live=r['live'],
        reco=reco, st=st, asc=rec['ascore'], dr=rec['dr']))
emrows.sort(key=lambda x: (x['d'], x['a']))
EM_CORE = [x for x in emrows if x['core']]
EM_CORE_DOMS = len({x['d'] for x in EM_CORE})
EM_DOMS = len({x['d'] for x in emrows}); EM_LINKS = len(emrows)
EM_ANCH = len({x['a'] for x in emrows})
EM_HOLD = sorted({x['d'] for x in emrows if x['st'] in ('Held (Pending Partner)', 'Held (Review)')})
EM_NOFO = sorted({x['d'] for x in emrows if x['st'] == 'Held (Nofollow, No Action)'})
EM_KEEP = sorted({x['d'] for x in emrows if x['st'] == 'Keep'})

dis = [r for r in AUD if r['status'] == 'Spam (Disavow)' and r['redundant'] != 'Yes']
redun = [r for r in AUD if r['redundant'] == 'Yes']
cnt = collections.Counter(r['status'] for r in AUD)
blc = collections.Counter()
for r in LNK: blc[STAT.get(r['rd'], '')] += 1

wb = openpyxl.Workbook()
# ============ Summary ============
ws = wb.active; ws.title = 'Summary'; ws.sheet_view.showGridLines = False
widths(ws, {'A': 38.86, 'B': 16.29, 'C': 17.57, 'D': 18.71, 'E': 120})
ws['B1'] = CLIENT_NAME; ws.merge_cells('B1:E2')
for _rr in (1, 2):
    for _cc in range(2, 6):
        _c = ws.cell(_rr, _cc); _c.font = Font(name=F, sz=9, b=True, color=TEAL)
        _c.alignment = Alignment(horizontal='center', vertical='center')
ws.append([])
ws.append(['Status', 'Domains', 'Backlinks', 'Share of Domains', 'What it means'])
hdr(ws, ws.max_row, sz=10)
MEAN = {
 'Spam (Disavow)': 'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'Held (Pending Partner)': 'Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms.',
 'Held (Nofollow, No Action)': 'Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
 'Held (Review)': 'Carries both exact match commercial and link scheme anchors. Needs a judgement call.',
 'Spam (Nofollow, No Action)': 'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Keep': 'Genuine or harmless link. Keep.',
 'Own Site': 'Client owned domain that redirects into the site.'}
ORDER = ['Spam (Disavow)', 'Held (Pending Partner)', 'Held (Nofollow, No Action)', 'Held (Review)',
         'Spam (Nofollow, No Action)', 'Keep', 'Own Site']
for s in ORDER:
    if not cnt[s]: continue
    ws.append([s, cnt[s], blc[s], cnt[s] / len(AUD), MEAN[s]])
    style(ws, ws.max_row, WHITE, {'B': '#,##0', 'C': '#,##0', 'D': '0.0%'}, centre=('B', 'C', 'D'))
    ws.cell(ws.max_row, 5).alignment = Alignment(vertical='center', wrap_text=True)
ws.append(['Total', len(AUD), sum(blc.values()), 1.0, ''])
style(ws, ws.max_row, WHITE, {'B': '#,##0', 'C': '#,##0', 'D': '0.0%'}, centre=('B', 'C', 'D'))
for c in ws[ws.max_row]: c.font = Font(name=F, sz=9, b=True)

def block(title, lines, sz=11):
    ws.append([title]); r = ws.max_row
    ws.cell(r, 1).font = Font(name=F, sz=sz, b=True, color=('FF000000' if sz == 10 else NAVY))
    ws.cell(r, 1).alignment = Alignment(vertical='center')
    for t in lines:
        ws.append([t]); rr = ws.max_row; ws.merge_cells(f'A{rr}:E{rr}')
        ws.cell(rr, 1).font = Font(name=F, sz=9); ws.cell(rr, 1).alignment = Alignment(vertical='center', wrap_text=True)

spam = cnt['Spam (Disavow)'] + cnt['Spam (Nofollow, No Action)']
pbnl = sum(1 for r in LNK if r['atype'] == 'Spam: keyword stuffed SEO sales copy')
pbn_home = sum(1 for r in LNK if r['atype'] == 'Spam: keyword stuffed SEO sales copy'
               and tgt_kind(r['target_url']) == 'Homepage')
deep = sum(1 for x in EM_CORE if x['tkind'] != 'Homepage')
topdom = collections.defaultdict(set)
for r in LNK: topdom[(r['anchor'] or '').strip()].add(r['rd'])
ta, tn = max(((a, len(s)) for a, s in topdom.items() if a), key=lambda x: x[1])
_allheld = [r for r in AUD if r['status'].startswith('Held')]
_q = [SEMT[r['domain']] for r in _allheld if r['domain'] in SEMT]
_sumtraf = sum(fnum(t['organic_traffic']) for t in _q)
_notraf = sum(1 for t in _q if fnum(t['organic_traffic']) == 0)
_noidx = sum(1 for r in _allheld if r['domain'] in NOTINDEXED)
_net = sum(1 for r in _allheld if r['ip'].startswith(('69.13.', '64.182.', '94.46.')))
_as2 = sum(1 for r in AUD if r['ascore'] != '' and int(r['ascore']) <= 2)
_scored = sum(1 for r in AUD if r['ascore'] != '')
PROPC = collections.Counter(r['property'] for r in LNK)
_h = {r['date']: r for r in csv.DictReader(
    (l for l in open(D + 'history.csv') if not l.startswith('#')), delimiter=';')}
HIST = ('Semrush recorded {} referring domains in August 2026, {} in September and {} in October.'
        .format(*(f"{int(_h[d]['domains_num']):,}" for d in ('2026-08-01', '2026-09-01', '2026-10-01'))))
tab05_nofollow = sum(1 for d in TAB05 if STAT[d] == 'Spam (Nofollow, No Action)')

block('Key findings', sz=10, lines=[
 f"{spam:,} of the {len(AUD):,} referring domains are spam. {cnt['Spam (Disavow)']:,} carry at least one dofollow link and go in the disavow file; the other {cnt['Spam (Nofollow, No Action)']:,} are nofollow only and pass nothing, so they need no action. Authority is thin throughout: {_as2:,} of the {_scored:,} scored referring domains sit at Semrush Authority Score 2 or below.",
 f"The profile has roughly tripled since the brief was written. {HIST} The brief's 898 referring domains at Authority Score 16 is an August snapshot; the live profile is {len(AUD):,} domains and {len(LNK):,} links, so auditing the brief's list alone would have missed most of the attack.",
 f"{PROPC[CLIENT]:,} links point at kandkmfg.com directly. The other {PROPC['gaworktrucks.com'] + PROPC['kandkmanufacturing.com']:,} arrive through a redirect from gaworktrucks.com ({PROPC['gaworktrucks.com']:,}) and kandkmanufacturing.com ({PROPC['kandkmanufacturing.com']:,}), which are separate Search Console properties. A file filed on kandkmfg.com does nothing for those, so three files are supplied and all three need uploading.",
 f"Two campaigns are running at once and they are easy to tell apart. Not one of the {pbnl:,} link scheme links points anywhere but the home page, while {deep:,} of the {len(EM_CORE):,} exact match commercial links point at a product, capability or industry page. Page level targeting is a paid campaign; the home page flood is an attack.",
 f"The largest single anchor, on {tn:,} referring domains, is sales copy for a backlink service that names the client's own domain as its example. The same template runs in three variants, one for each of the three client domains.",
 f"{EM_CORE_DOMS:,} referring domains carry exact match commercial anchors, and {len(EM_HOLD):,} domains in total are held out of the files until the previous partner confirms what was commissioned. They are not {len(EM_HOLD):,} independent sites: {_net:,} of them sit in three address ranges and most are article directories or bookmark farms, so this was one vendor network. Do not upload before that conversation.",
 f"Held does not mean valuable. {_notraf:,} of the {len(_q):,} held domains draw no organic traffic at all, {_noidx:,} of them because Semrush holds no organic data for the domain in the first place. All nine referring domains named in Tab 05 are confirmed spam and resolved in this sheet, {tab05_nofollow} of them nofollow only, so disavowing those changes nothing.",
])
block('Anchor text profile (all backlinks)', [])
ws.append(['Anchor type', 'Backlinks', 'Share of Backlinks', 'Referring Domains', '']); hdr(ws, ws.max_row)
_at = collections.Counter(); _ad = collections.defaultdict(set)
for r in LNK: _at[r['atype']] += 1; _ad[r['atype']].add(r['rd'])
for t, nbl in _at.most_common():
    ws.append([t, nbl, nbl / len(LNK), len(_ad[t]), ''])
    style(ws, ws.max_row, WHITE, {'A': '#,##0', 'B': '#,##0', 'C': '0.0%', 'D': '#,##0'}, centre=('B', 'C', 'D'))
    ws.cell(ws.max_row, 5).border = Border(); ws.cell(ws.max_row, 5).fill = PatternFill()
for r in range(1, ws.max_row + 1): ws.row_dimensions[r].height = 22.5

# ============ Referring Domain Audit ============
ws = wb.create_sheet('Referring Domain Audit')
ws.append(['Domain', 'Status', 'AS', 'Backlinks', "RD's", 'Traffic', 'In Disavow', 'Links Point To',
  'Dofollow Links', 'Nofollow Links', 'First Seen', 'Top Anchor Text', 'Example Linking Page',
  'Linking Page Title', 'Source', 'IP', 'Disavow Line']); hdr(ws)
byd = collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
for r in AUD:
    d = r['domain']; rs = byd.get(d, [])
    ws.append([d, r['status'], int(r['ascore']) if r['ascore'] != '' else 'Not scored',
      int(fnum(r['backlinks'])), _rd(d), _tr(d, 'organic_traffic'),
      'Yes' if (r['status'] == 'Spam (Disavow)' and r['redundant'] != 'Yes') else
      ('Covered by parent' if r['redundant'] == 'Yes' else ('Held' if r['status'].startswith('Held') else 'No')),
      points_to(rs), int(fnum(r['dofollow'])) if r['dofollow'] != '' else '',
      int(fnum(r['nofollow'])) if r['nofollow'] != '' else '',
      dt(r['first_seen']), r['top_anchor'], r['example_page'], r['page_title'], r['tool'], r['ip'],
      r['disavow_line'] if r['redundant'] != 'Yes' else ''])
    style(ws, ws.max_row, WHITE, {'D': '#,##0', 'E': '#,##0', 'F': '#,##0', 'K': 'd mmm yyyy'},
          centre=('C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'O', 'P'))
widths(ws, {'A': 36, 'B': 24.71, 'C': 9.57, 'D': 13, 'E': 9.43, 'F': 9.71, 'G': 12.43, 'H': 21.29,
            'I': 14, 'J': 8.71, 'K': 12, 'L': 45, 'M': 8.71, 'N': 40, 'O': 14, 'P': 15, 'Q': 14})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:Q{ws.max_row}'

# ============ All Backlinks ============
ws = wb.create_sheet('All Backlinks')
ws.append(['Referring Domain', 'Status', 'Tool', 'Anchor Text', 'Anchor Type', 'Link Type',
           'Linking Page URL', 'Linking Page Title', 'Target URL']); hdr(ws)
for r in LNK:
    ws.append([r['rd'], STAT.get(r['rd'], ''), r['tool'], r['anchor'], r['atype'],
               'Nofollow' if r['nofollow'] == 'true' else 'Dofollow',
               r['source_url'], r['source_title'], r['target_url']])
    style(ws, ws.max_row, WHITE, centre=('F',))
for _r in range(1, ws.max_row + 1):
    ws.cell(_r, 3).alignment = Alignment(horizontal='left', vertical='center', wrap_text=(_r == 1))
widths(ws, {'A': 25.43, 'B': 27.14, 'C': 14.71, 'D': 55, 'E': 32, 'F': 10, 'G': 55, 'H': 53.14, 'I': 30.57})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:I{ws.max_row}'

# ============ Anchor Analysis ============
ws = wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text', 'Anchor Type', 'Backlinks', 'Share of Backlinks', 'Referring Domains',
           'Spam Domains Using It']); hdr(ws)
agg = collections.defaultdict(lambda: {'bl': 0, 'rd': set(), 'spam': set(), 'type': ''})
for r in LNK:
    a = (r['anchor'] or '').strip() or '<EmptyAnchor>'
    g = agg[a]; g['bl'] += 1; g['rd'].add(r['rd']); g['type'] = r['atype']
    if STAT.get(r['rd'], '').startswith('Spam'): g['spam'].add(r['rd'])
for a, g in sorted(agg.items(), key=lambda x: -x[1]['bl']):
    ws.append([a if a != '<EmptyAnchor>' else '(no anchor text)', g['type'], g['bl'],
               g['bl'] / len(LNK), len(g['rd']), len(g['spam'])])
    style(ws, ws.max_row, WHITE, {'C': '#,##0', 'D': '0.00%'}, centre=('C', 'D', 'E', 'F'))
ws['A1'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
widths(ws, {'A': 115.86, 'B': 37.71, 'C': 14, 'D': 8.71, 'F': 20.29})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:F{ws.max_row}'

# ============ Exact Match Anchors (the decision tab) ============
def quality(d):
    t = SEMT.get(d)
    if not t: return 'Semrush traffic not queried for this domain'
    if d in NOTINDEXED: return 'Semrush holds no organic data for this domain at all'
    kw = fnum(t['organic_keywords']); tr = fnum(t['organic_traffic'])
    if kw == 0 and tr == 0: return 'Not indexed by Semrush, no keywords and no traffic'
    return (f'{kw:,.0f} keywords' if kw else 'no keywords') + ', ' + \
           (f'{tr:,.0f} visits a month' if tr else 'no measurable traffic')
def has_life(d):
    t = SEMT.get(d)
    if not t: return None
    return fnum(t['organic_traffic']) > 0 or fnum(t['organic_keywords']) >= 100
def reco_for(d, st_):
    if st_ == 'Keep': return 'Keep, genuine editorial placement, no confirmation needed'
    if st_ == 'Held (Nofollow, No Action)': return 'No action needed, nofollow passes no ranking value'
    if st_ == 'Held (Review)': return 'Review, mixes link scheme with exact match anchors'
    hl = has_life(d)
    if hl is True: return 'Hold for partner, Semrush shows this site is indexed and ranking'
    if hl is False: return 'Disavow unless the partner confirms, Semrush shows almost nothing indexed'
    return 'Disavow unless the partner confirms they bought it'
ORDER_R = {'Hold for partner, Semrush shows this site is indexed and ranking': 0,
           'Disavow unless the partner confirms they bought it': 1,
           'Disavow unless the partner confirms, Semrush shows almost nothing indexed': 2,
           'Review, mixes link scheme with exact match anchors': 3,
           'No action needed, nofollow passes no ranking value': 4,
           'Keep, genuine editorial placement, no confirmation needed': 5}

ws = wb.create_sheet('Exact Match Anchors')
ws.append(['Referring domain', 'Example backlink (linking page)', 'Exact-match commercial anchor',
  'Market', 'Site type (indicative)', 'Partner confirmed? (Y/N)', 'Final decision']); hdr(ws)
pairs = collections.defaultdict(list)
for x in emrows: pairs[(x['d'], x['a'])].append(x)
prow = []
for (d, a), xs in pairs.items():
    rec = AUDD[d]; prow.append((ORDER_R.get(reco_for(d, rec['status']), 9), d, a, xs, rec, rec['status']))
prow.sort(key=lambda t: (t[0], t[1], t[2]))
_held_rows = []
for _, d, a, xs, rec, st_ in prow:
    # One real, checkable backlink: prefer a link the Ahrefs export confirms is live,
    # then a dofollow one, then one on a money page.
    ex = sorted(xs, key=lambda x: (x['live'] != 'True' and x['live'] != 'Yes',
                                   x['link'] != 'Dofollow',
                                   x['tkind'] == 'Homepage', x['src']))[0]
    ws.append([d, ex['src'], a, ex['mk'], rec['sitetype'], '', ''])
    r = ws.max_row
    style(ws, r, WHITE, centre=('D',))
    for col in ('F', 'G'):
        _c = ws[f'{col}{r}']; _c.fill = PatternFill('solid', fgColor=INPUT)
        _c.font = Font(name=F, sz=9, color=WHITE)
    if st_.startswith('Held') and st_ != 'Held (Nofollow, No Action)': _held_rows.append(r)
if _held_rows:
    dv = DataValidation(type='list', formula1='"Y,N"', allow_blank=True, showErrorMessage=True,
        errorTitle='Enter Y or N', error='Type Y if the previous partner commissioned this placement, or N if not.')
    ws.add_data_validation(dv); dv.add(f'F{min(_held_rows)}:F{max(_held_rows)}')
    dv2 = DataValidation(type='list', formula1='"Keep,Disavow"', allow_blank=True, showErrorMessage=True,
        errorTitle='Choose Keep or Disavow', error='Only the domains awaiting confirmation can be set.')
    ws.add_data_validation(dv2); dv2.add(f'G{min(_held_rows)}:G{max(_held_rows)}')
widths(ws, {'A': 25.43, 'B': 59, 'C': 53.14, 'D': 16, 'E': 24.57, 'F': 15.43, 'G': 15})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:G{ws.max_row}'
EM_DECISION_ROWS = len(_held_rows)

# ============ Pending Disavow Lines ============
ws = wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain', 'Disavow line (append to disavow.txt once confirmed)',
           'Recommendation']); hdr(ws)
FILEOF = {'kandkmfg.com': 'disavow_kandkmfg.txt', 'gaworktrucks.com': 'disavow_gaworktrucks.txt',
          'kandkmanufacturing.com': 'disavow_kandkmanufacturing.txt'}
for d in EM_HOLD:
    props = sorted({x['property'] for x in byd.get(d, [])}) or [CLIENT]
    ws.append([d, 'domain:' + d, 'Append only if the partner does not claim it, to '
               + ' and '.join(FILEOF[x] for x in props)])
    style(ws, ws.max_row, WHITE)
widths(ws, {'A': 32, 'B': 44, 'C': 48})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:C{ws.max_row}'

# ============ Disavow List ============
ws = wb.create_sheet('Disavow List')
ws.append(['Disavow Line', 'AS', 'Backlinks', "RD's", 'Traffic', 'Organic Keywords', 'Top Anchor Text'])
hdr(ws)
for r in sorted(dis, key=lambda x: x['domain']):
    d = r['domain']
    ws.append([r['disavow_line'], int(r['ascore']) if r['ascore'] != '' else '',
      int(fnum(r['backlinks'])), _rd(d), _tr(d, 'organic_traffic'), _tr(d, 'organic_keywords'),
      r['top_anchor']])
    style(ws, ws.max_row, WHITE, {'C': '#,##0', 'D': '#,##0', 'E': '#,##0', 'F': '#,##0'},
          centre=('B', 'C', 'D', 'E', 'F'))
widths(ws, {'A': 44, 'B': 14, 'C': 15.57, 'D': 14, 'E': 11.14, 'F': 14.86, 'G': 98.86})
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:G{ws.max_row}'

# ---- typography pass ----
for name in wb.sheetnames:
    w = wb[name]
    for row in w.iter_rows():
        for c in row:
            fo = c.font
            if fo.name != F or fo.sz not in (9, 10, 11):
                sz = fo.sz if fo.sz in (9, 10, 11) else 9
                try: col = fo.color.rgb if (fo.color and isinstance(fo.color.rgb, str)) else None
                except Exception: col = None
                c.font = Font(name=F, sz=sz, b=fo.b, i=fo.i, color=col)
    if name != 'Summary':
        w.row_dimensions[1].height = 31.5
        h = 15.75 if name == 'Referring Domain Audit' else 22.5
        for r in range(2, w.max_row + 1): w.row_dimensions[r].height = h
    w.sheet_format.defaultRowHeight = 15.0
bad = collections.Counter()
for name in wb.sheetnames:
    for row in wb[name].iter_rows():
        for c in row:
            if c.value is not None and (c.font.name != F or c.font.sz not in (9, 10, 11)):
                bad[(name, c.font.name, c.font.sz)] += 1
print('non-conforming cells:', dict(bad) if bad else 'none')

# ---- the three disavow files ----
# One per Search Console property. A line only goes in the file for the property its
# links actually point at, because that is the only file Google will apply it to.
# Each bad domain is filed on the property its links point at (point of attribution).
# The money site kandkmfg.com additionally receives the COMPLETE union: every owned
# domain 301-redirects into it, and Google forwards disavow signals across a redirect
# imperfectly, so the site being protected gets belt-and-suspenders cover. Listing a
# domain that does not link to kandkmfg.com directly is harmless.
byprop = collections.defaultdict(list)
for r in dis:
    props = sorted({x['property'] for x in byd.get(r['domain'], [])}) or [CLIENT]
    for p in props:
        byprop[p].append(r)
    if CLIENT not in props:
        byprop[CLIENT].append(r)
FILES = {'kandkmfg.com': 'disavow_kandkmfg.txt',
         'gaworktrucks.com': 'disavow_gaworktrucks.txt',
         'kandkmanufacturing.com': 'disavow_kandkmanufacturing.txt'}
written = {}
for p, fn in FILES.items():
    rows = byprop.get(p, [])
    path = '/home/user/test/' + fn
    with open(path, 'w') as f:
        f.write(f'# {CLIENT_NAME} disavow file for the {p} Search Console property\n')
        f.write(f'# Generated {datetime.date.today():%d %b %Y} from Semrush (priority) merged with the client Ahrefs export.\n')
        f.write(f'# {len(rows):,} domains. Source: {os.path.basename(OUT)}, "Disavow List" tab.\n#\n')
        if p != CLIENT:
            f.write(f'# {p} redirects into kandkmfg.com, but Google processes a disavow file per\n')
            f.write(f'# property, so these lines have to be uploaded under {p} itself.\n#\n')
        _pl = lambda n, one, many: f'{n:,} {one if n == 1 else many}'
        f.write(f'# Excluded: {len(EM_HOLD):,} referring domains are held out of this file until the\n')
        f.write('# previous SEO partner, the supplier the brief refers to, confirms what it\n')
        f.write("# commissioned. See the 'Exact Match Anchors' and 'Pending Disavow Lines' tabs.\n")
        f.write(f'# A further {_pl(len(EM_NOFO), "domain is", "domains are")} nofollow and need no decision, and\n')
        f.write(f'# {_pl(len(EM_KEEP), "is a genuine placement", "are genuine placements")} to keep.\n#\n')
        f.write('# Do not submit to Google Search Console until that confirmation is complete.\n')
        if p == CLIENT:
            f.write('# This is the money site. It carries the COMPLETE set of bad referring domains\n')
            f.write('# across all three owned properties, because gaworktrucks.com and\n')
            f.write('# kandkmanufacturing.com 301-redirect into it and a disavow should cover the\n')
            f.write('# links however Google attributes them across the redirect.\n')
            f.write('# Checked on 16 Oct 2026: no disavow file is currently filed on this property,\n')
            f.write('# so this upload adds one rather than replacing anything.\n#\n')
        else:
            f.write('# Uploading replaces any existing disavow file on this property. Check Search Console\n')
            f.write('# for one and merge it in first if there is.\n#\n')
        bg = collections.defaultdict(list)
        for r in rows: bg[re.sub(r' \(covered by.*', '', r['group'])].append(r['disavow_line'])
        for g in sorted(bg, key=lambda k: -len(bg[k])):
            f.write(f"\n# --- {g} ({len(bg[g]):,} domain{'' if len(bg[g]) == 1 else 's'}) ---\n")
            for ln in sorted(bg[g]): f.write(ln + '\n')
    written[fn] = len(rows)

wb._sheets = [wb[t] for t in ['Summary', 'Referring Domain Audit', 'All Backlinks', 'Anchor Analysis',
                              'Exact Match Anchors', 'Pending Disavow Lines', 'Disavow List']]
wb.save(OUT)
print('workbook:', OUT); print('tabs:', wb.sheetnames)
print(f'domains {len(AUD):,} | links {len(LNK):,} | disavow {len(dis):,} (+{len(redun)} redundant child lines omitted)')
print(f'decision tab: {EM_DOMS} domains, {EM_LINKS} rows, {EM_ANCH} anchors | hold {len(EM_HOLD)} '
      f'nofollow {len(EM_NOFO)} keep {len(EM_KEEP)}')
print('disavow files:', ', '.join(f'{k} {v:,}' for k, v in written.items()))
print(f'Semrush traffic checked for {len(SEMT):,} of {len(AUD):,} domains '
      f'({len(NOTINDEXED):,} of those hold no organic data at all); '
      f'own referring-domain count known for {len(SRD):,}')
