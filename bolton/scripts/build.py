"""
build.py — assemble the Bolton Service WNC backlink-audit workbook + disavow files.
Matches KandK_Manufacturing_Backlinks_Audit.xlsx cell-for-cell (see TEMPLATE_SPEC.md).

Run:  python3 -I bolton/scripts/build.py
Outputs under bolton/out/.
"""
import os, sys, json, html, glob, re
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load, classify
from classify import host_of, link_property, is_deep_money_page, classify_anchor

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.worksheet.datavalidation import DataValidation

BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, 'data')
OUT  = os.path.join(BASE, 'out')
os.makedirs(OUT, exist_ok=True)

ACCENT, WHITE, BLACK = 'FF0C343D', 'FFFFFFFF', 'FF000000'
CLIENT_NAME = 'Bolton Service WNC'
MONEY = 'boltonservicewnc.com'
REDIRECTS = ['boltonwnc.com', 'webolton.com']
PROPERTIES = [MONEY] + REDIRECTS

# ---------------- styling ----------------
def F(size=9, bold=False, color=BLACK): return Font(name='Geist', size=size, bold=bold, color=color)
fill_accent = PatternFill('solid', fgColor=ACCENT)
fill_white  = PatternFill('solid', fgColor=WHITE)
_thin = Side(style='thin')
B_HEADER = Border(left=_thin, right=_thin, top=_thin)
B_FULL   = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
B_NONE   = Border()
A_CL = Alignment(horizontal='center', vertical='center', wrap_text=False)
A_CW = Alignment(horizontal='center', vertical='center', wrap_text=True)
A_LL = Alignment(horizontal='left',   vertical='center', wrap_text=False)
A_LW = Alignment(horizontal='left',   vertical='center', wrap_text=True)
A_NL = Alignment(vertical='center', wrap_text=False)

def hdr_cell(c, text, size=9, left=False, nowrap=False):
    c.value = text; c.font = F(size, True, WHITE); c.fill = fill_accent; c.border = B_HEADER
    c.alignment = Alignment(horizontal='left' if left else 'center', vertical='center',
                            wrap_text=not nowrap)

def write_data_tab(ws, headers, widths, aligns, numfmts, rows, row_h=22.5,
                   header_left=(), header_nowrap=()):
    ncol = len(headers); last = get_column_letter(ncol)
    for i, (h, w) in enumerate(zip(headers, widths), 1):
        ws.column_dimensions[get_column_letter(i)].width = w
        hdr_cell(ws.cell(1, i), h, 9, left=(i-1 in header_left), nowrap=(i-1 in header_nowrap))
    ws.row_dimensions[1].height = 31.5
    for r, row in enumerate(rows, start=2):
        ws.row_dimensions[r].height = row_h
        for i in range(ncol):
            c = ws.cell(r, i+1); v = row[i]; kind = aligns[i]
            c.value = v; c.number_format = numfmts[i]; c.border = B_NONE
            if kind == 'input':
                c.font = F(9, False, WHITE); c.fill = fill_accent; c.alignment = A_NL
            else:
                c.font = F(9, False, BLACK); c.fill = fill_white
                c.alignment = A_CL if kind == 'center' else (A_LL if kind == 'leftx' else A_NL)
    ws.freeze_panes = 'B2'
    ws.auto_filter.ref = f'A1:{last}{max(1, len(rows)+1)}'
    ws.sheet_view.showGridLines = True

def to_dt(ts):
    try: return datetime.fromtimestamp(int(ts), tz=timezone.utc).replace(tzinfo=None)
    except: return None

# ---------------- load + classify ----------------
def _num(x):
    try: return int(float(x))
    except: return None

def load_metrics():
    ah, scmp = {}, {}
    for p in sorted(glob.glob(os.path.join(DATA, 'metrics', 'ahrefs_batch_*.json'))):
        try: txt = open(p, encoding='utf-8').read()
        except: continue
        i = txt.find('{')
        if i < 0: continue
        try: obj, _ = json.JSONDecoder().raw_decode(txt[i:])
        except: continue
        for t in obj.get('targets', []):
            d = host_of(t.get('url', '')) or (t.get('url','').strip().lower())
            d = d[4:] if d.startswith('www.') else d
            if d: ah[d] = t
    for p in sorted(glob.glob(os.path.join(DATA, 'metrics', 'semrush_as_*.csv'))):
        for ln, raw in enumerate(open(p, encoding='utf-8')):
            raw = raw.rstrip('\r\n')
            if not raw or raw.startswith('target;'): continue
            parts = raw.split(';')
            if len(parts) < 2: continue
            d = parts[0].strip().lower()
            scmp[d] = parts
    return ah, scmp

def load_traffic():
    """Semrush domain_rank per domain: domain;organic_keywords;organic_traffic (no_data=0,0)."""
    tr = {}
    for p in sorted(glob.glob(os.path.join(DATA, 'traffic', '*.csv'))):
        for raw in open(p, encoding='utf-8'):
            raw = raw.rstrip('\r\n')
            if not raw or raw.lower().startswith('domain;'): continue
            parts = raw.split(';')
            if len(parts) < 3: continue
            d = parts[0].strip().lower(); d = d[4:] if d.startswith('www.') else d
            tr[d] = {'organic_keywords': _num(parts[1]), 'organic_traffic': _num(parts[2])}
    return tr

def load_ahrefs_rd():
    """Return dict domain-> row from the Ahrefs referring-domains pull (if present)."""
    out = {}
    p = os.path.join(DATA, 'ahrefs', 'ahrefs_refdomains.json')
    if not os.path.exists(p): return out
    txt = open(p, encoding='utf-8').read(); i = txt.find('{')
    if i < 0: return out
    try: obj, _ = json.JSONDecoder().raw_decode(txt[i:])
    except: return out
    arr = None
    for k in ('refdomains','referring_domains','domains','rows','data'):
        if isinstance(obj.get(k), list): arr = obj[k]; break
    if arr is None:
        for v in obj.values():
            if isinstance(v, list): arr = v; break
    for row in (arr or []):
        d = (row.get('domain') or row.get('name') or '').strip().lower()
        d = d[4:] if d.startswith('www.') else d
        if d: out[d] = row
    return out

def build():
    bl, blst = load.load_backlinks(os.path.join(DATA, 'fetch'))
    rd, rdst = load.load_refdomains(os.path.join(DATA, 'rd'))
    rd_by = {r['domain']: r for r in rd}
    idx = load.DomainIndex([r['domain'] for r in rd])   # canonical root set only; subdomains collapse
    ah, scmp = load_metrics()
    ard = load_ahrefs_rd()
    tr = load_traffic()

    by_dom = defaultdict(list)
    for b in bl:
        d = idx.canon(b['source_url'])
        if d: b['refdom'] = d; by_dom[d].append(b)

    # Ahrefs-only referring domains (seen by Ahrefs, no Semrush link captured)
    for d in ard:
        by_dom.setdefault(d, [])
    rows = {}
    for d, links in by_dom.items():
        as_score = None
        if d in scmp and len(scmp[d]) >= 2:
            as_score = _num(scmp[d][1])
        if as_score is None and d in rd_by:
            as_score = rd_by[d].get('domain_authority_score')
            as_score = as_score if isinstance(as_score, int) else _num(as_score)
        if not links:
            verdict = dict(status='Keep', reason='Ahrefs-only, no spam evidence', evidence='')
        else:
            verdict = classify.classify_domain(d, links, {'as_score': as_score})
        rows[d] = dict(domain=d, links=links, as_score=as_score, **verdict)
    return dict(bl=bl, rd=rd, rd_by=rd_by, idx=idx, ah=ah, scmp=scmp, ard=ard, tr=tr,
                by_dom=by_dom, rows=rows, blst=blst, rdst=rdst)

# ---------------- per-domain aggregate ----------------
SPAM_STATUS = {'Spam (Disavow)', 'Spam (Nofollow, No Action)'}
def agg_domain(d, R, ctx):
    links = R['links']; status = R['status']
    ah = ctx['ah'].get(d, {}); scmp = ctx['scmp'].get(d, []); rd_by = ctx['rd_by'].get(d, {})
    ard = ctx['ard'].get(d, {})
    tr = ctx['tr'].get(d, {})
    as_score = R['as_score']
    bl_count = len(links)
    dofollow = sum(1 for L in links if not L['nofollow'])
    nofollow = sum(1 for L in links if L['nofollow'])
    # RD's of this domain (its own profile) from Semrush comparison domains_num, else Ahrefs
    rds = None
    if len(scmp) >= 4: rds = _num(scmp[3])
    if rds is None and ard: rds = _num(ard.get('refdomains') or ard.get('refdomains_source_domain'))
    # Traffic/keywords: Semrush domain_rank is primary (playbook); Ahrefs batch is fallback
    traffic = tr.get('organic_traffic')
    if traffic is None: traffic = _num(ah.get('org_traffic'))
    orgkw = tr.get('organic_keywords')
    if orgkw is None: orgkw = _num(ah.get('org_keywords'))
    ip = (rd_by.get('ip') or ah.get('ip') or ard.get('ip_source') or '') or ''
    fs_list = [L['first_seen'] for L in links if L.get('first_seen')]
    first_seen = to_dt(min(fs_list)) if fs_list else None
    # example: prefer dofollow + response 200, live; else dofollow; else any
    def score(L):
        return (0 if not L['nofollow'] else 1, 0 if L.get('response_code') == 200 else 1)
    example = sorted(links, key=score)[0] if links else None
    top_anchor = Counter((L['anchor'] or '') for L in links).most_common(1)
    top_anchor = top_anchor[0][0] if top_anchor else ''
    props = Counter(link_property(L) for L in links)
    links_point_to = ', '.join(sorted(p for p,_ in props.most_common(3) if p)) if props else ''
    in_disavow = 'Yes' if status == 'Spam (Disavow)' else ('Held' if status.startswith('Held') else 'No')
    disavow_line = f'domain:{d}' if status == 'Spam (Disavow)' else ''
    source = 'Both' if (links and d in ctx['ard']) else ('Ahrefs' if not links else 'Semrush')
    return dict(domain=d, status=status, as_score=as_score, bl_count=bl_count, rds=rds,
                traffic=traffic, orgkw=orgkw, in_disavow=in_disavow,
                links_point_to=links_point_to, dofollow=dofollow, nofollow=nofollow,
                first_seen=first_seen, top_anchor=top_anchor,
                example_url=(example['source_url'] if example else ''),
                example_title=(example['source_title'] if example else ''),
                source=source, ip=ip, disavow_line=disavow_line, reason=R['reason'],
                evidence=R['evidence'])

# ---------------- main assembly ----------------
def main():
    ctx = build()
    rows = ctx['rows']
    doms = sorted(rows.keys())
    aggs = {d: agg_domain(d, rows[d], ctx) for d in doms}

    # ---- Referring Domain Audit ----
    rd_headers = ['Domain','Status','AS','Backlinks',"RD's",'Traffic','In Disavow','Links Point To',
                  'Dofollow Links','Nofollow Links','First Seen','Top Anchor Text',
                  'Example Linking Page','Linking Page Title','Source','IP','Disavow Line']
    rd_widths  = [36,24.71,9.57,13,9.43,9.71,12.43,21.29,14,8.71,12,45,8.71,40,14,15,14]
    rd_aligns  = ['left','left','center','center','center','center','center','left','center',
                  'center','center','left','left','left','center','center','left']
    rd_numfmt  = ['General','General','General','#,##0','#,##0','#,##0','General','General',
                  'General','General','d mmm yyyy','General','General','General','General','General','General']
    rd_rows = []
    for d in doms:
        a = aggs[d]
        rd_rows.append([a['domain'], a['status'], (a['as_score'] if a['as_score'] is not None else ''),
                        a['bl_count'], (a['rds'] if a['rds'] is not None else ''),
                        (a['traffic'] if a['traffic'] is not None else ''), a['in_disavow'],
                        a['links_point_to'], a['dofollow'], a['nofollow'], a['first_seen'],
                        a['top_anchor'], a['example_url'], a['example_title'], a['source'], a['ip'],
                        a['disavow_line']])
    # sort: by status priority then backlinks desc
    order = {'Spam (Disavow)':0,'Held (Pending Partner)':1,'Spam (Nofollow, No Action)':2,
             'Held (Nofollow, No Action)':3,'Keep':4,'Own Site':5}
    rd_rows.sort(key=lambda r: (order.get(r[1], 9), -r[3], r[0]))

    # ---- All Backlinks ----
    ab_headers = ['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type',
                  'Linking Page URL','Linking Page Title','Target URL']
    ab_widths  = [25.43,27.14,14.71,55,32,10,55,53.14,30.57]
    ab_aligns  = ['left','left','leftx','left','left','center','left','left','left']
    ab_numfmt  = ['General']*9
    ab_rows = []
    for d in doms:
        st = rows[d]['status']
        for L in rows[d]['links']:
            at, _h = classify_anchor(L['anchor'], L.get('target_url',''))
            ab_rows.append([d, st, aggs[d]['source'], L['anchor'], at,
                            'Nofollow' if L['nofollow'] else 'Dofollow',
                            L['source_url'], L['source_title'], L['target_url']])

    # ---- Anchor Analysis ----
    an_headers = ['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains',
                  'Spam Domains Using It']
    an_widths  = [115.86,37.71,14,8.71,13,20.29]
    an_aligns  = ['left','left','center','center','center','center']
    an_numfmt  = ['General','General','#,##0','0.00%','General','General']
    anchor_links = defaultdict(list)   # anchor -> list of (dom, link)
    for d in doms:
        for L in rows[d]['links']:
            anchor_links[L['anchor'] or ''].append((d, L))
    total_links = sum(len(rows[d]['links']) for d in doms)
    an_rows = []
    for anchor, items in anchor_links.items():
        at, _h = classify_anchor(anchor, items[0][1].get('target_url',''))
        bcount = len(items)
        rdoms = {dd for dd,_ in items}
        spam_doms = {dd for dd,_ in items if rows[dd]['status'] in SPAM_STATUS}
        an_rows.append([anchor, at, bcount, (bcount/total_links if total_links else 0),
                        len(rdoms), len(spam_doms)])
    an_rows.sort(key=lambda r: -r[2])

    # ---- Exact Match Anchors (held exact-match commercial) ----
    em_headers = ['Referring domain','Example backlink (linking page)','Exact-match commercial anchor',
                  'Market','Site type (indicative)','Partner confirmed? (Y/N)','Final decision']
    em_widths  = [25.43,59,53.14,16,24.57,15.43,15]
    em_aligns  = ['left','left','center','center','left','input','input']
    em_numfmt  = ['General']*7
    em_rows = []
    def site_type(dom, title):
        t = (title or '').lower(); h = dom.lower()
        if any(k in h for k in ('directory','listing','dir.','bizdir','locale','listings')): return 'Low quality web directory'
        if any(k in h for k in ('blog','news','daily','times','post','media')): return 'Blog / content site'
        if 'chamber' in h or '.gov' in h or '.edu' in h: return 'Institutional / editorial'
        return 'Low quality web directory'
    for d in doms:
        if not rows[d]['status'].startswith('Held'): continue
        seen = set()
        for L in rows[d]['links']:
            at, _h = classify_anchor(L['anchor'], L.get('target_url',''))
            if at in ('Exact match commercial','Exact match commercial (geo)'):
                key = (L['anchor'] or '')
                if key in seen: continue
                seen.add(key)
                market = 'Geo' if '(geo)' in at else 'Non-geo'
                em_rows.append([d, L['source_url'], L['anchor'], market,
                                site_type(d, L['source_title']), None, None])
    em_rows.sort(key=lambda r: r[0])

    # ---- Pending Disavow Lines (held domains) ----
    pd_headers = ['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation']
    pd_widths  = [32,44,48]
    pd_aligns  = ['left','left','left']
    pd_numfmt  = ['General']*3
    pd_rows = []
    for d in doms:
        if rows[d]['status'] == 'Held (Pending Partner)':
            pd_rows.append([d, f'domain:{d}',
                'Append only if the supplier does not claim this link as a commissioned placement.'])
    pd_rows.sort(key=lambda r: r[0])

    # ---- Disavow List (money-site union = all Spam (Disavow)) ----
    dl_headers = ['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text']
    dl_widths  = [44,14,15.57,14,11.14,14.86,98.86]
    dl_aligns  = ['left','center','center','center','center','center','left']
    dl_numfmt  = ['General','General','#,##0','#,##0','#,##0','#,##0','General']
    disavow_doms = sorted(d for d in doms if rows[d]['status'] == 'Spam (Disavow)')
    dl_rows = []
    for d in disavow_doms:
        a = aggs[d]
        dl_rows.append([f'domain:{d}', (a['as_score'] if a['as_score'] is not None else ''),
                        a['bl_count'], (a['rds'] if a['rds'] is not None else ''),
                        (a['traffic'] if a['traffic'] is not None else ''),
                        (a['orgkw'] if a['orgkw'] is not None else ''), a['top_anchor']])

    # ---- counts ----
    status_counter = Counter(rows[d]['status'] for d in doms)
    status_links = Counter()
    for d in doms: status_links[rows[d]['status']] += len(rows[d]['links'])
    total_domains = len(doms)

    counts = dict(total_domains=total_domains, total_links=total_links,
                  status_domains=dict(status_counter), status_links=dict(status_links),
                  disavow_domains=len(disavow_doms),
                  held_pending=status_counter.get('Held (Pending Partner)',0),
                  held_nofollow=status_counter.get('Held (Nofollow, No Action)',0),
                  spam_nofollow=status_counter.get('Spam (Nofollow, No Action)',0),
                  keep=status_counter.get('Keep',0), own=status_counter.get('Own Site',0))

    workbook_data = dict(
        rd=(rd_headers,rd_widths,rd_aligns,rd_numfmt,rd_rows,15.75,(),()),
        ab=(ab_headers,ab_widths,ab_aligns,ab_numfmt,ab_rows,22.5,{2},()),
        an=(an_headers,an_widths,an_aligns,an_numfmt,an_rows,22.5,(),{0}),
        em=(em_headers,em_widths,em_aligns,em_numfmt,em_rows,22.5,(),()),
        pd=(pd_headers,pd_widths,pd_aligns,pd_numfmt,pd_rows,22.5,(),()),
        dl=(dl_headers,dl_widths,dl_aligns,dl_numfmt,dl_rows,22.5,(),()),
    )
    render(workbook_data, counts, aggs, rows, doms, an_rows)
    write_disavow_files(rows, aggs, doms, counts)
    json.dump(counts, open(os.path.join(OUT,'counts.json'),'w'), indent=2)
    print('STATUS:', dict(status_counter))
    print('total domains', total_domains, 'total links', total_links,
          'disavow', len(disavow_doms), 'pending', counts['held_pending'])
    return ctx, aggs, rows, doms, counts

# ---------------- render workbook ----------------
def render(wd, counts, aggs, rows, doms, an_rows):
    wb = openpyxl.Workbook()
    ws0 = wb.active; ws0.title = 'Summary'
    render_summary(ws0, counts, aggs, rows, doms, an_rows)
    names = [('Referring Domain Audit','rd'),('All Backlinks','ab'),('Anchor Analysis','an'),
             ('Exact Match Anchors','em'),('Pending Disavow Lines','pd'),('Disavow List','dl')]
    for title, key in names:
        ws = wb.create_sheet(title)
        H,W,AL,NF,R,RH,HL,HNW = wd[key]
        write_data_tab(ws, H, W, AL, NF, R, row_h=RH, header_left=HL, header_nowrap=HNW)
        if key == 'em':  # partner-input dropdowns on the Exact Match Anchors tab (match template)
            last = len(R) + 1
            dvF = DataValidation(type='list', formula1='"Y,N"', allow_blank=True,
                                 showDropDown=False, showErrorMessage=True, showInputMessage=True,
                                 prompt='Enter Y or N - Type Y if the previous partner commissioned this placement, or N if not.')
            dvG = DataValidation(type='list', formula1='"Keep,Disavow"', allow_blank=True,
                                 showDropDown=False, showErrorMessage=True, showInputMessage=True,
                                 prompt='Choose Keep or Disavow - Only the domains awaiting confirmation can be set.')
            ws.add_data_validation(dvF); dvF.add(f'F2:F{last}')
            ws.add_data_validation(dvG); dvG.add(f'G2:G{last}')
    path = os.path.join(OUT, 'Bolton_Service_WNC_Backlinks_Audit.xlsx')
    wb.save(path)
    print('wrote', path)

def render_summary(ws, counts, aggs, rows, doms, an_rows):
    ws.sheet_view.showGridLines = False
    widths = {'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120.0}
    for c,w in widths.items(): ws.column_dimensions[c].width = w
    for r in range(1,40): ws.row_dimensions[r].height = 22.5
    # logo
    try:
        img = XLImage(os.path.join(DATA,'harbinger_logo.png'))
        img.anchor = OneCellAnchor(_from=AnchorMarker(col=0,colOff=381000,row=0,rowOff=0),
                                   ext=XDRPositiveSize2D(1866900,552450))
        ws.add_image(img)
    except Exception as e:
        print('logo warn:', e)
    ws.merge_cells('B1:E2')
    t = ws['B1']; t.value = CLIENT_NAME; t.font = F(21, True, ACCENT); t.alignment = A_CL
    # status table
    hdrs = ['Status','Domains','Backlinks','Share of Domains','What it means']
    for i,h in enumerate(hdrs):
        c = ws.cell(3, i+1); c.value=h; c.font=F(10,True,WHITE); c.fill=fill_accent
        c.alignment=A_CW; c.border=B_FULL
    EXPL = {
      'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
      'Held (Pending Partner)':'Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms.',
      'Held (Nofollow, No Action)':'Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
      'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
      'Keep':'Genuine or harmless link. Keep.',
      'Own Site':'Client owned domain that redirects into the site.'}
    order = ['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)',
             'Spam (Nofollow, No Action)','Keep','Own Site']
    td = counts['total_domains']
    r = 4
    for st in order:
        dn = counts['status_domains'].get(st,0); bn = counts['status_links'].get(st,0)
        vals = [st, dn, bn, (dn/td if td else 0), EXPL[st]]
        nf = ['General','#,##0','#,##0','0.0%','General']
        al = [A_NL,A_CL,A_CL,A_CL,A_LW]
        for i,v in enumerate(vals):
            c=ws.cell(r,i+1); c.value=v; c.font=F(9,False,BLACK); c.fill=fill_white
            c.alignment=al[i]; c.border=B_FULL; c.number_format=nf[i]
        r += 1
    # Total
    tn = sum(counts['status_links'].values())
    vals = ['Total', td, tn, 1.0, '']
    nf = ['General','#,##0','#,##0','0.0%','General']; al=[A_NL,A_CL,A_CL,A_CL,A_LW]
    for i,v in enumerate(vals):
        c=ws.cell(10,i+1); c.value=v; c.font=F(9,True,BLACK); c.fill=fill_white
        c.alignment=al[i]; c.border=B_FULL; c.number_format=nf[i]
    # Key findings heading
    ws.cell(11,1).value='Key findings'; ws.cell(11,1).font=F(10,True,BLACK)
    findings = build_findings(counts, aggs, rows, doms)
    for i,text in enumerate(findings):
        rr = 12+i
        ws.merge_cells(f'A{rr}:E{rr}')
        c=ws.cell(rr,1); c.value=text; c.font=F(9,False,BLACK); c.alignment=A_LW
    # Anchor profile heading
    ws.cell(19,1).value='Anchor text profile (all backlinks)'; ws.cell(19,1).font=F(11,True,ACCENT)
    ah_hdr = ['Anchor type','Backlinks','Share of Backlinks','Referring Domains']
    for i,h in enumerate(ah_hdr):
        c=ws.cell(20,i+1); c.value=h; c.font=F(9,True,WHITE); c.fill=fill_accent
        c.alignment=A_CW; c.border=B_FULL
    # anchor type aggregation from an_rows: [anchor,type,backlinks,share,rds,spam]
    type_bl = Counter(); type_rd = defaultdict(set)
    total_links = counts['total_links']
    # recompute per-type from rows for accuracy
    for d in doms:
        for L in rows[d]['links']:
            at,_h = classify_anchor(L['anchor'], L.get('target_url',''))
            type_bl[at]+=1; type_rd[at].add(d)
    tr = 21
    for at,_bl in type_bl.most_common():
        vals=[at, _bl, (_bl/total_links if total_links else 0), len(type_rd[at])]
        nf=['General','#,##0','0.0%','#,##0']; al=[A_NL,A_CL,A_CL,A_CL]
        for i,v in enumerate(vals):
            c=ws.cell(tr,i+1); c.value=v; c.font=F(9,False,BLACK); c.fill=fill_white
            c.alignment=al[i]; c.border=B_FULL; c.number_format=nf[i]
        tr+=1

def build_findings(counts, aggs, rows, doms):
    sd = counts['status_domains']
    spam_total = sd.get('Spam (Disavow)',0)+sd.get('Spam (Nofollow, No Action)',0)
    disavow = counts['disavow_domains']; spam_nf = sd.get('Spam (Nofollow, No Action)',0)
    td = counts['total_domains']
    # growth from history.csv
    growth = ''
    try:
        import csv
        hrows = list(csv.DictReader(open(os.path.join(DATA,'history.csv')), delimiter=';'))
        sep = next((h for h in hrows if h['date_unix']=='1788235200'), None)  # 2026-09
        jul = next((h for h in hrows if h['date_unix']=='1782878400'), None)  # 2026-07
        now = hrows[-1]
        growth = (f"{sep['domains_num']} referring domains in September 2026, {now['domains_num']} by November"
                  if sep else '')
    except: pass
    # home vs deep
    home=deep=0
    for d in doms:
        for L in rows[d]['links']:
            if is_deep_money_page(L): deep+=1
            else: home+=1
    # dominant anchor
    anc = Counter()
    for d in doms:
        for L in rows[d]['links']: anc[L['anchor'] or '']+=1
    # held: use Authority Score (Semrush, complete) rather than Ahrefs traffic (quota-limited)
    held = [d for d in doms if rows[d]['status'].startswith('Held')]
    held_as0 = sum(1 for d in held if aggs[d]['as_score'] in (0, 1, 2))
    now_rd = counts['total_domains']
    f=[]
    f.append(f"{spam_total:,} of the {td:,} referring domains are spam. {disavow:,} have a dofollow link and go in the disavow file; the other {spam_nf:,} are nofollow and need no action.")
    f.append(f"The attack has grown sharply: {growth}, and the live profile we audited holds {now_rd:,} referring domains. We audited the full live profile, not the brief's snapshot.")
    f.append(f"You can upload a disavow file to all three Search Console properties. The money-site file (boltonservicewnc.com) carries every bad domain, including those that reach the site through the boltonwnc.com and webolton.com redirects.")
    f.append(f"Two patterns, easy to tell apart. {home:,} link-scheme links hit the home page; {deep:,} commercial-anchor links hit deep service and location pages. The home-page flood is the attack.")
    f.append(f"The biggest anchor, on {len({d for d in doms for L in rows[d]['links'] if (L['anchor'] or '')==anc.most_common(1)[0][0]}):,} domains, is backlink sales copy that names the client's own domain.")
    f.append(f"{counts['held_pending']:,} domains are held for the previous supplier to confirm, in case any were commissioned placements. They are not in the disavow file.")
    f.append(f"Held does not mean valuable: {held_as0:,} of the {len(held):,} held domains carry an Authority Score of 0-2, the bottom of the scale — low-value link-network sites, not evidently genuine placements. The supplier still confirms before any are disavowed.")
    return f

# ---------------- disavow files ----------------
def write_disavow_files(rows, aggs, doms, counts):
    disavow = [d for d in doms if rows[d]['status']=='Spam (Disavow)']
    # group by reason bucket
    def bucket(d):
        rs = rows[d]['reason']
        if 'off-topic' in rs.lower() or 'off topic' in rs.lower(): return 'Off-topic / adult / illegal spam'
        if 'host name' in rs.lower(): return 'Spam host name'
        if 'title' in rs.lower() or 'url template' in rs.lower(): return 'Spam page title / URL template'
        return 'PBN keyword-stuffed SEO sales-copy links'
    # property attribution
    prop_doms = {p:set() for p in PROPERTIES}
    for d in disavow:
        for L in rows[d]['links']:
            p = link_property(L)
            if p in prop_doms: prop_doms[p].add(d)
    # money-site file = full union
    today = datetime.now().strftime('%Y-%m-%d')
    def write_file(path, domain_list, title, is_money):
        by_b = defaultdict(list)
        for d in sorted(domain_list): by_b[bucket(d)].append(d)
        lines = []
        lines.append(f"# Google disavow file — {title}")
        lines.append(f"# Generated {today} for Bolton Service WNC ({MONEY})")
        lines.append(f"# {len(domain_list)} domains. Each line disavows a referring (source) domain and its subdomains.")
        lines.append(f"# 'Supplier' in the brief = the 'partner' named throughout the audit workbook; held domains")
        lines.append(f"#  (exact-match commercial / deep-page links) are EXCLUDED pending that supplier's confirmation.")
        lines.append(f"# DO NOT submit before the supplier confirms which anchors were commissioned.")
        if is_money:
            lines.append(f"# This is the money-site file: it carries the FULL UNION of every bad source domain,")
            lines.append(f"#  including those reaching the site via the boltonwnc.com and webolton.com 301 redirects.")
        else:
            lines.append(f"# This file covers only domains whose links point at {title} (point of attribution).")
        lines.append(f"# NOTE: confirm with the client whether a disavow file already exists on this property.")
        lines.append(f"#  If one does, uploading REPLACES it (merge first). If none exists, this is the first file.")
        lines.append("")
        for b in sorted(by_b):
            lines.append(f"# --- {b} ({len(by_b[b])}) ---")
            for d in by_b[b]:
                lines.append(f"domain:{d}")
            lines.append("")
        open(path,'w').write('\n'.join(lines).rstrip()+'\n')
        return len(domain_list)
    n_money = write_file(os.path.join(OUT,f'disavow_{MONEY}.txt'), disavow, MONEY, True)
    for p in REDIRECTS:
        write_file(os.path.join(OUT,f'disavow_{p}.txt'), prop_doms[p], p, False)
    counts['disavow_money'] = n_money
    counts['disavow_by_property'] = {p: len(prop_doms[p]) for p in PROPERTIES}

if __name__ == '__main__':
    main()
