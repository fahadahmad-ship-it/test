"""Build the frickecpa.com backlink audit workbook, replicating the Harbinger
Marketing template (7 tabs, logo, formatting) + the disavow .txt file.

Inputs (in data/):
  ahrefs_refdomains.csv   domain,domain_rating,links_to_target,dofollow_links,first_seen,ip_source,is_spam,traffic_domain,positions_source_domain
  ahrefs_backlinks.csv    name_source,root_name_source,anchor,is_dofollow,is_nofollow,link_type,url_from,url_to,title,is_spam,first_seen_link,domain_rating_source
  ahrefs_anchors.csv      anchor,<counts...>
  ahrefs_refdomains_rd.csv (optional) domain,refdomains
  semrush_refdomains.csv  domain,domain_authority_score,backlinks_num,ip,country,first_seen
  semrush_anchors.csv     anchor,domains_num,backlinks_num
  semrush_backlinks.csv   source_url,source_title,target_url,anchor,nofollow,first_seen
Outputs:
  frickecpa_backlinks_audit.xlsx
  disavow_frickecpa.txt
"""
import csv, os, re, collections, datetime, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(__file__))
from classify import (classify_anchor, classify_domain_status, is_pbn_domain)

DATA = "data"
CLIENT = "frickecpa.com"
CLIENT_DOMAINS = {"frickecpa.com", "www.frickecpa.com"}
BRAND_TOKENS = ["fricke cpa", "fricke, ", "frickecpa", "fricke &", "fricke and",
                "j fricke", "fricke"]
TITLE = "Fricke CPA"  # refined from data below if a better brand name is found
DISAVOW_FILE = "disavow_frickecpa.txt"

TEAL = "0C343D"
FONT = "Geist"
hdr_font = Font(name=FONT, size=9, bold=True, color="FFFFFF")
hdr_fill = PatternFill("solid", fgColor=TEAL)
body_font = Font(name=FONT, size=9, bold=False, color="000000")
title_font = Font(name=FONT, size=21, bold=True, color=TEAL)
sum_hdr_font = Font(name=FONT, size=10, bold=True, color="FFFFFF")


def host_of(url):
    if not url:
        return ""
    u = re.sub(r'^https?://', '', str(url).strip(), flags=re.I)
    u = u.split('/')[0]
    return u.lower()


def root_of(host):
    parts = (host or "").split('.')
    return host if len(parts) < 2 else ".".join(parts[-2:])


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def to_int(x, d=0):
    try:
        return int(float(x))
    except Exception:
        return d


def to_float(x, d=0.0):
    try:
        return float(str(x).rstrip('.'))
    except Exception:
        return d


def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            pass
    try:
        return datetime.datetime.fromisoformat(s.replace('Z', ''))
    except Exception:
        return None


# ---------------------------------------------------------------- load data
ah_rd = read_csv(f"{DATA}/ahrefs_refdomains.csv")
ah_bl = read_csv(f"{DATA}/ahrefs_backlinks.csv")
se_rd = read_csv(f"{DATA}/semrush_refdomains.csv")
se_bl = read_csv(f"{DATA}/semrush_backlinks.csv")
rd_extra = {r['domain'].lower(): to_int(r.get('refdomains'))
            for r in read_csv(f"{DATA}/ahrefs_refdomains_rd.csv") if r.get('domain')}

print(f"loaded: ahrefs_rd={len(ah_rd)} ahrefs_bl={len(ah_bl)} "
      f"semrush_rd={len(se_rd)} semrush_bl={len(se_bl)}")

# -------------------------------------------------- unify backlinks (both tools)
# Each backlink: domain, anchor, dofollow(bool), link_type, url_from, title,
#                url_to, tool, anchor_type.  Dedup across tools on
# (domain, url_from, url_to, anchor); mark tool "Both" when seen in both.
_bl_map = {}


def _norm(u):
    return re.sub(r'/+$', '', re.sub(r'^https?://', '', (u or '').strip(), flags=re.I).lower())


def add_bl(domain, anchor, dofollow, link_type, url_from, title, url_to, tool,
           is_image=False):
    domain = (domain or "").lower()
    key = (domain, _norm(url_from), _norm(url_to), (anchor or "").strip().lower())
    cur = _bl_map.get(key)
    if cur:
        if tool not in cur['tool'].split('+'):
            cur['tool'] = 'Both'
        cur['dofollow'] = cur['dofollow'] or dofollow
        if not cur['title'] and title:
            cur['title'] = title
        return
    at = classify_anchor(anchor, BRAND_TOKENS, CLIENT_DOMAINS,
                         link_type=link_type, is_image=is_image)
    _bl_map[key] = dict(domain=domain, anchor=anchor or "", dofollow=dofollow,
                        link_type=link_type or "", url_from=url_from or "",
                        title=title or "", url_to=url_to or "", tool=tool,
                        anchor_type=at)


for r in ah_bl:
    host = (r.get('name_source') or host_of(r.get('url_from'))).lower()
    df = str(r.get('is_dofollow', '')).strip() in ('1', 'true', 'True')
    lt = (r.get('link_type') or '').strip() or 'text'
    add_bl(host, r.get('anchor'), df, lt, r.get('url_from'),
           r.get('title'), r.get('url_to'), 'Ahrefs',
           is_image=(r.get('link_type') == 'image'))

for r in se_bl:
    host = host_of(r.get('source_url'))
    nofollow = str(r.get('nofollow', '')).strip() in ('1', 'true', 'True')
    add_bl(host, r.get('anchor'), (not nofollow),
           'Nofollow' if nofollow else 'Dofollow',
           r.get('source_url'), r.get('source_title'), r.get('target_url'),
           'Semrush')

backlinks = list(_bl_map.values())
for b in backlinks:
    b['tool'] = 'Both' if b['tool'] == 'Both' else b['tool']

# per-domain backlink aggregates
dom_bl = collections.defaultdict(list)
for b in backlinks:
    dom_bl[b['domain']].append(b)

# -------------------------------------------------- unify referring domains
ah_rd_map = {r['domain'].lower(): r for r in ah_rd if r.get('domain')}
se_rd_map = {r['domain'].lower(): r for r in se_rd if r.get('domain')}
all_domains = set(ah_rd_map) | set(se_rd_map) | set(dom_bl)
# ignore client's own domain as a referring domain
all_domains = {d for d in all_domains if d and root_of(d) != CLIENT}

rows = []          # Referring Domain Audit rows (dicts)
for d in sorted(all_domains):
    a = ah_rd_map.get(d, {})
    s = se_rd_map.get(d, {})
    bls = dom_bl.get(d, [])
    in_ah, in_se = d in ah_rd_map, d in se_rd_map
    # also infer tool presence from backlinks if not in refdomain lists
    tools_seen = {b['tool'] for b in bls}
    if in_ah:
        tools_seen.add('Ahrefs')
    if in_se:
        tools_seen.add('Semrush')
    source = ("Both" if {'Ahrefs', 'Semrush'} <= tools_seen
              else ('Ahrefs' if 'Ahrefs' in tools_seen else 'Semrush'))

    # AS: prefer Semrush authority score, else Ahrefs DR
    as_val = s.get('domain_authority_score')
    as_val = to_float(as_val) if as_val not in (None, '') else to_float(a.get('domain_rating'))

    backlinks_n = (to_int(a.get('links_to_target')) if in_ah
                   else to_int(s.get('backlinks_num')))
    if not backlinks_n:
        backlinks_n = len(bls)
    rds = rd_extra.get(d, "")

    traffic = to_int(a.get('traffic_domain'))
    org_kw = to_int(a.get('positions_source_domain'))
    first_seen = (parse_date(a.get('first_seen')) or parse_date(s.get('first_seen')))
    if not first_seen and bls:
        pass
    ip = (a.get('ip_source') or s.get('ip') or "").strip()

    dofollow_n = to_int(a.get('dofollow_links'))
    if not in_ah:  # derive from backlinks
        dofollow_n = sum(1 for b in bls if b['dofollow'])
    nofollow_n = (backlinks_n - dofollow_n) if backlinks_n >= dofollow_n else \
        sum(1 for b in bls if not b['dofollow'])
    # robust dofollow presence
    has_df = dofollow_n > 0 or any(b['dofollow'] for b in bls)

    # anchor-type signals for status
    types = collections.Counter(b['anchor_type'] for b in bls)
    has_sales = types.get("Spam: keyword stuffed SEO sales copy", 0) > 0
    has_commercial = (types.get("Exact match commercial", 0) +
                      types.get("Exact match commercial (geo)", 0)) > 0
    is_spam_flag = (str(a.get('is_spam', '')).strip() in ('1', 'true', 'True') or
                    any(str(b.get('tool')) and False for b in bls))
    pbn = is_pbn_domain(d)
    client_owned = root_of(d) == CLIENT

    status, in_disav = classify_domain_status(
        is_spam_flag=is_spam_flag, has_sales_copy_anchor=has_sales, pbn=pbn,
        has_commercial_anchor=has_commercial,
        dofollow_links=(dofollow_n if in_ah else (1 if has_df else 0)),
        client_owned=client_owned)

    # representative backlink: prefer dofollow, then most-informative anchor
    rep = None
    for pref in (lambda b: b['dofollow'] and b['anchor'],
                 lambda b: bool(b['anchor']),
                 lambda b: True):
        cand = [b for b in bls if pref(b)]
        if cand:
            rep = cand[0]
            break
    top_anchor = rep['anchor'] if rep else ""
    example_page = rep['url_from'] if rep else ""
    page_title = rep['title'] if rep else ""
    # Links Point To -> host of most common url_to
    tos = collections.Counter(host_of(b['url_to']) for b in bls if b['url_to'])
    links_to = tos.most_common(1)[0][0] if tos else CLIENT

    disavow_line = f"domain:{d}" if in_disav == "Yes" else ""

    rows.append(dict(
        domain=d, status=status, as_val=as_val, backlinks=backlinks_n, rds=rds,
        traffic=traffic, in_disavow=in_disav, links_to=links_to,
        dofollow=dofollow_n, nofollow=max(nofollow_n, 0), first_seen=first_seen,
        top_anchor=top_anchor, example_page=example_page, page_title=page_title,
        source=source, ip=ip, disavow_line=disavow_line, org_kw=org_kw,
        has_sales=has_sales, has_commercial=has_commercial, pbn=pbn,
        is_spam_flag=is_spam_flag))

print(f"referring domains unified: {len(rows)}")
status_counts = collections.Counter(r['status'] for r in rows)
print("status counts:", dict(status_counts))

# save a classified cache for inspection
with open(f"{DATA}/_classified_domains.csv", "w", newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["domain", "status", "source", "as", "backlinks", "dofollow",
                "nofollow", "traffic", "first_seen", "top_anchor", "ip",
                "has_sales", "has_commercial", "pbn", "is_spam_flag"])
    for r in rows:
        w.writerow([r['domain'], r['status'], r['source'], r['as_val'],
                    r['backlinks'], r['dofollow'], r['nofollow'], r['traffic'],
                    r['first_seen'], r['top_anchor'][:60], r['ip'],
                    r['has_sales'], r['has_commercial'], r['pbn'], r['is_spam_flag']])
print("wrote data/_classified_domains.csv")

# ======================================================================
# WORKBOOK BUILD
# ======================================================================
dom_status = {r['domain']: r['status'] for r in rows}
dom_row = {r['domain']: r for r in rows}

ANCHOR_ORDER = ["Spam: keyword stuffed SEO sales copy", "Naked URL",
                "Exact match commercial", "Exact match commercial (geo)",
                "Generic", "Branded", "Empty or image", "Contextual or other"]
STATUS_ORDER = ["Spam (Disavow)", "Held (Pending Partner)",
                "Held (Nofollow, No Action)", "Spam (Nofollow, No Action)",
                "Keep", "Own Site"]
WHATITMEANS = {
 "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
 "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous supplier confirms.",
 "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep": "Genuine or harmless link. Keep.",
 "Own Site": "Client owned domain that redirects into the site.",
}

wb = openpyxl.Workbook()


def style_header(ws, ncols, row=1, font=hdr_font):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = font
        cell.fill = hdr_fill
        cell.alignment = Alignment(vertical="center")


def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def write_body(ws, start_row, data, numfmts=None, datecols=()):
    numfmts = numfmts or {}
    for i, rec in enumerate(data):
        rr = start_row + i
        for c, val in enumerate(rec, start=1):
            cell = ws.cell(row=rr, column=c, value=val)
            cell.font = body_font
            L = get_column_letter(c)
            if L in numfmts:
                cell.number_format = numfmts[L]
            if L in datecols and isinstance(val, datetime.datetime):
                cell.number_format = "d mmm yyyy"

# ---------------------------------------------------------------- Summary
ws = wb.active
ws.title = "Summary"
set_widths(ws, {'A': 38.86, 'B': 16.29, 'C': 17.57, 'D': 18.71, 'E': 120.0})
for r in range(1, 60):
    ws.row_dimensions[r].height = 22.5
ws.merge_cells("B1:E2")
ws["B1"] = TITLE
ws["B1"].font = title_font
ws["B1"].alignment = Alignment(vertical="center")
if os.path.exists("assets/template_logo.png"):
    img = XLImage("assets/template_logo.png")
    img.width, img.height = 170, 50
    ws.add_image(img, "A1")

# status table
ws.append([])  # placeholder to keep row index logic explicit; we set by coord
hdr = ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"]
for c, h in enumerate(hdr, 1):
    cell = ws.cell(row=3, column=c, value=h); cell.font = sum_hdr_font
    cell.fill = hdr_fill
total_dom = len(rows)
bl_by_status = collections.Counter()
dom_by_status = collections.Counter()
for r in rows:
    dom_by_status[r['status']] += 1
    bl_by_status[r['status']] += r['backlinks']
rr = 4
for st in STATUS_ORDER:
    ws.cell(row=rr, column=1, value=st).font = body_font
    c2 = ws.cell(row=rr, column=2, value=dom_by_status.get(st, 0)); c2.font = body_font; c2.number_format = "#,##0"
    c3 = ws.cell(row=rr, column=3, value=bl_by_status.get(st, 0)); c3.font = body_font; c3.number_format = "#,##0"
    c4 = ws.cell(row=rr, column=4, value=f"=B{rr}/$B$10"); c4.font = body_font; c4.number_format = "0.0%"
    c5 = ws.cell(row=rr, column=5, value=WHATITMEANS[st]); c5.font = body_font
    rr += 1
# total row 10
ws.cell(row=10, column=1, value="Total").font = body_font
ws.cell(row=10, column=2, value=f"=SUM(B4:B9)").font = body_font; ws.cell(row=10, column=2).number_format = "#,##0"
ws.cell(row=10, column=3, value=f"=SUM(C4:C9)").font = body_font; ws.cell(row=10, column=3).number_format = "#,##0"
ws.cell(row=10, column=4, value="=B10/$B$10").font = body_font; ws.cell(row=10, column=4).number_format = "0.0%"

# ---- key findings (computed) ----
total_bl = sum(r['backlinks'] for r in rows)
spam_dom = dom_by_status['Spam (Disavow)'] + dom_by_status['Spam (Nofollow, No Action)']
disavow_dom = dom_by_status['Spam (Disavow)']
spam_nofollow = dom_by_status['Spam (Nofollow, No Action)']
held_pp = dom_by_status['Held (Pending Partner)']
# recent burst
recent_cut = datetime.datetime(2026, 9, 1)
recent = sum(1 for r in rows if r['first_seen'] and r['first_seen'] >= recent_cut)
# ip clustering among spam
ip_counter = collections.Counter(r['ip'].rsplit('.', 1)[0] for r in rows
                                 if r['status'].startswith('Spam') and r['ip'])
top_ips = ip_counter.most_common(3)
ip_cluster_dom = sum(c for _, c in top_ips)
# biggest anchor by domains
anchor_dom = collections.defaultdict(set)
for b in backlinks:
    if b['anchor'].strip():
        anchor_dom[b['anchor'].strip()].add(b['domain'])
biggest_anchor, biggest_set = ("", set())
if anchor_dom:
    biggest_anchor, biggest_set = max(anchor_dom.items(), key=lambda x: len(x[1]))
# homepage vs service page links (spam)
home_links = sum(1 for b in backlinks if host_of(b['url_to']) and
                 re.sub(r'^www\.', '', host_of(b['url_to'])) == CLIENT and
                 _norm(b['url_to']).rstrip('/') in (CLIENT, 'www.' + CLIENT))
# held with no traffic
held_notraffic = sum(1 for r in rows if r['status'].startswith('Held') and not r['traffic'])
held_total = dom_by_status['Held (Pending Partner)'] + dom_by_status['Held (Nofollow, No Action)']

findings = [
 f"{spam_dom:,} of the {total_dom:,} referring domains are spam. {disavow_dom:,} have a dofollow link and go in the disavow file; the other {spam_nofollow:,} are nofollow and need no action.",
 f"A recent spam burst is visible: {recent:,} referring domains were first seen since 1 Sep 2026, consistent with an automated link-spam / negative-SEO campaign.",
 f"Upload one disavow file for {CLIENT}. The attached {DISAVOW_FILE} lists all {disavow_dom:,} spam domains that currently pass a dofollow link.",
 (f"The spam is networked, not {len(ip_counter):,} independent sites: {ip_cluster_dom:,} spam domains share just {len(top_ips)} class-C IP ranges "
  f"({', '.join(ip+'.x' for ip,_ in top_ips)})." if top_ips else "Spam domains are spread across many IPs."),
 (f"The biggest single anchor, used on {len(biggest_set):,} referring domains, is: \"{biggest_anchor[:90]}\"." if biggest_anchor else ""),
 f"{held_pp:,} domains are held for the previous supplier to confirm, in case any were paid placements commissioned on the client's behalf. They carry exact-match commercial anchors and are NOT in the disavow file yet.",
 f"Held does not mean good: {held_notraffic:,} of the {held_total:,} held domains have no organic traffic at all. See the Exact Match Anchors tab for the list to send to the supplier.",
 f"Methodology: live backlink profile audited from BOTH Ahrefs and Semrush (de-duplicated). Classification is an automated first pass; the Held bucket in particular needs human + supplier review before any domain is removed from or added to the disavow file.",
]
findings = [f for f in findings if f]
ws.cell(row=11, column=1, value="Key findings").font = Font(name=FONT, size=10, bold=True, color="000000")
fr = 12
for f in findings:
    ws.merge_cells(start_row=fr, start_column=1, end_row=fr, end_column=5)
    cell = ws.cell(row=fr, column=1, value=f); cell.font = body_font
    cell.alignment = Alignment(vertical="center", wrap_text=False)
    fr += 1

# ---- anchor text profile ----
ap_row = fr + 1
ws.cell(row=ap_row, column=1, value="Anchor text profile (all backlinks)").font = Font(name=FONT, size=10, bold=True, color="000000")
ap_hdr = ap_row + 1
for c, h in enumerate(["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"], 1):
    cell = ws.cell(row=ap_hdr, column=c, value=h); cell.font = sum_hdr_font; cell.fill = hdr_fill
bl_by_type = collections.Counter(b['anchor_type'] for b in backlinks)
dom_by_type = collections.defaultdict(set)
for b in backlinks:
    dom_by_type[b['anchor_type']].add(b['domain'])
total_bl_all = sum(bl_by_type.values()) or 1
rr = ap_hdr + 1
for at in ANCHOR_ORDER:
    ws.cell(row=rr, column=1, value=at).font = body_font
    c2 = ws.cell(row=rr, column=2, value=bl_by_type.get(at, 0)); c2.font = body_font; c2.number_format = "#,##0"
    c3 = ws.cell(row=rr, column=3, value=bl_by_type.get(at, 0) / total_bl_all); c3.font = body_font; c3.number_format = "0.00%"
    c4 = ws.cell(row=rr, column=4, value=len(dom_by_type.get(at, set()))); c4.font = body_font; c4.number_format = "#,##0"
    rr += 1

# ---------------------------------------------------------------- Referring Domain Audit
ws = wb.create_sheet("Referring Domain Audit")
set_widths(ws, {'A':36,'B':24.71,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,'J':8.71,'K':12,'L':45,'M':8.71,'N':40,'O':14,'P':15,'Q':14})
cols = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To",
        "Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page",
        "Linking Page Title","Source","IP","Disavow Line"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"
# order: status severity then backlinks desc
order_rank = {s: i for i, s in enumerate(STATUS_ORDER)}
rows_sorted = sorted(rows, key=lambda r: (order_rank.get(r['status'], 9), -r['backlinks'], r['domain']))
body = []
for r in rows_sorted:
    body.append([r['domain'], r['status'], (r['as_val'] or None), r['backlinks'],
                 (r['rds'] if r['rds'] != "" else None), r['traffic'], r['in_disavow'],
                 r['links_to'], r['dofollow'], r['nofollow'], r['first_seen'],
                 r['top_anchor'], r['example_page'], r['page_title'], r['source'],
                 r['ip'], r['disavow_line']])
write_body(ws, 2, body,
           numfmts={'D':"#,##0",'E':"#,##0",'F':"#,##0",'I':"#,##0",'J':"#,##0",'K':"d mmm yyyy"},
           datecols=('K',))

# ---------------------------------------------------------------- All Backlinks
ws = wb.create_sheet("All Backlinks")
set_widths(ws, {'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':30.57})
cols = ["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
        "Linking Page URL","Linking Page Title","Target URL"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"
bl_sorted = sorted(backlinks, key=lambda b: (order_rank.get(dom_status.get(b['domain'], 'Keep'), 9), b['domain']))
body = []
for b in bl_sorted:
    body.append([b['domain'], dom_status.get(b['domain'], ""), b['tool'], b['anchor'],
                 b['anchor_type'], ("Dofollow" if b['dofollow'] else "Nofollow"),
                 b['url_from'], b['title'], b['url_to']])
write_body(ws, 2, body)
print(f"all backlinks rows: {len(body)}")

# ---------------------------------------------------------------- Anchor Analysis
ws = wb.create_sheet("Anchor Analysis")
set_widths(ws, {'A':115.86,'B':37.71,'C':14,'D':8.71,'E':20,'F':20.29})
cols = ["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"
anc_bl = collections.Counter()
anc_type = {}
anc_doms = collections.defaultdict(set)
anc_spam = collections.defaultdict(set)
for b in backlinks:
    a = b['anchor'].strip()
    key = a if a else "(empty / image)"
    anc_bl[key] += 1
    anc_type[key] = b['anchor_type']
    anc_doms[key].add(b['domain'])
    if dom_status.get(b['domain'], '').startswith('Spam'):
        anc_spam[key].add(b['domain'])
tot_anc_bl = sum(anc_bl.values()) or 1
anc_sorted = sorted(anc_bl.items(), key=lambda x: -x[1])
body = []
for a, n in anc_sorted:
    body.append([a, anc_type.get(a, ""), n, n / tot_anc_bl, len(anc_doms[a]), len(anc_spam[a])])
write_body(ws, 2, body, numfmts={'C':"#,##0",'D':"0.00%"})
print(f"distinct anchors: {len(body)}")

# ---------------------------------------------------------------- Exact Match Anchors
ws = wb.create_sheet("Exact Match Anchors")
set_widths(ws, {'A':25.43,'B':59,'C':53.14,'D':16,'E':24.57,'F':15.43,'G':15})
cols = ["Referring domain","Example backlink (linking page)","Exact-match commercial anchor",
        "Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"

def site_type(domain, url):
    d = domain.lower(); u = (url or "").lower()
    if any(k in d for k in ("bookmark",)):
        return "Social bookmarking site"
    if any(k in d for k in ("directory", "listing", "listings", "bizlist", "localcenter",
                            "businesses", "bizdir", "dir.", "biz", "local")) or "/detail/" in u:
        return "Low quality web directory"
    if any(k in d for k in ("article", "articles", "blog", "news", "press", "content", "post")):
        return "Article / blog network"
    if d.endswith((".shop", ".top", ".icu", ".store", ".online", ".space", ".site", ".website")):
        return "PBN / link-selling site"
    return "Low quality site"

em_rows = []
for r in rows_sorted:
    bls = dom_bl.get(r['domain'], [])
    comm = [b for b in bls if b['anchor_type'] in ("Exact match commercial", "Exact match commercial (geo)")]
    if not comm:
        continue
    rep = comm[0]
    market = "Geo" if rep['anchor_type'].endswith("(geo)") else "Non-geo"
    em_rows.append([r['domain'], rep['url_from'], rep['anchor'], market,
                    site_type(r['domain'], rep['url_from']), "", ""])
write_body(ws, 2, em_rows)
print(f"exact-match-anchor domains: {len(em_rows)}")

# ---------------------------------------------------------------- Pending Disavow Lines
ws = wb.create_sheet("Pending Disavow Lines")
set_widths(ws, {'A':32,'B':44,'C':48})
cols = ["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"
pend = []
for r in rows_sorted:
    if r['status'] == "Held (Pending Partner)":
        pend.append([r['domain'], f"domain:{r['domain']}",
                     f"Append only if the previous supplier does NOT claim it, to {DISAVOW_FILE}"])
write_body(ws, 2, pend)
print(f"pending disavow (held) domains: {len(pend)}")

# ---------------------------------------------------------------- Disavow List
ws = wb.create_sheet("Disavow List")
set_widths(ws, {'A':44,'B':14,'C':15.57,'D':14,'E':11.14,'F':14.86,'G':98.86})
cols = ["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
for c, h in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, len(cols))
ws.freeze_panes = "B2"
disav = [r for r in rows if r['status'] == "Spam (Disavow)"]
disav.sort(key=lambda r: r['domain'])
body = []
for r in disav:
    body.append([f"domain:{r['domain']}", (r['as_val'] or None), r['backlinks'],
                 (r['rds'] if r['rds'] != "" else None), r['traffic'], r['org_kw'],
                 r['top_anchor']])
write_body(ws, 2, body, numfmts={'C':"#,##0",'D':"#,##0",'E':"#,##0",'F':"#,##0"})
print(f"disavow domains: {len(disav)}")

# ---------------------------------------------------------------- save
OUT = "frickecpa_backlinks_audit.xlsx"
wb.save(OUT)
print("saved", OUT)

# ---------------------------------------------------------------- disavow.txt
with open(DISAVOW_FILE, "w", encoding="utf-8") as f:
    f.write(f"# Disavow file for {CLIENT}\n")
    f.write(f"# Generated {datetime.date.today().isoformat()} by Harbinger Marketing backlink audit\n")
    f.write(f"# Source: Ahrefs + Semrush live backlink profile (de-duplicated)\n")
    f.write(f"# Contains {len(disav)} spam referring domains that currently pass a dofollow link.\n")
    f.write(f"# NOTE: {len(pend)} additional domains with exact-match commercial anchors are HELD\n")
    f.write(f"#       pending the previous supplier's confirmation (see 'Pending Disavow Lines' tab).\n")
    f.write(f"#       Do NOT submit to Google Search Console until that confirmation is complete.\n")
    f.write("#\n")
    for r in disav:
        f.write(f"domain:{r['domain']}\n")
print("saved", DISAVOW_FILE)
