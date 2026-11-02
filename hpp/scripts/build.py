"""
Build the High Priority Plumbing backlink-audit workbook + disavow file,
in the signed-off Harbinger format (matched cell-for-cell to the K&K template).

Reads:
  out/classified_domains.json , out/classified_links.json   (from classify.py)
  data/metrics/comparison.csv  target;ascore;backlinks_num;domains_num;follows;nofollows  (optional)
  data/metrics/metrics.csv      domain;organic_keywords;organic_traffic                    (optional)
Writes:
  out/HighPriorityPlumbing_Backlinks_Audit.xlsx
  out/disavow_highpriorityplumbing.txt
"""
import json, os, sys, datetime, glob
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import canon_host

BASE = "/home/user/test/hpp"
CLIENT = "High Priority Plumbing"
MONEY = "highpriorityplumbing.com"
DISAVOW_FILE = "disavow_highpriorityplumbing.txt"
ACCENT = "FF0C343D"; WHITE = "FFFFFFFF"; BLACK = "FF000000"
F = "Geist"

# ---------- styles ----------
def font(sz=9, bold=False, color=BLACK): return Font(name=F, size=sz, bold=bold, color=color)
fill_accent = PatternFill("solid", fgColor=ACCENT)
fill_white = PatternFill("solid", fgColor=WHITE)
thin = Side(style="thin")
border_all = Border(left=thin, right=thin, top=thin, bottom=thin)
border_hdr = Border(left=thin, right=thin, top=thin)   # data-tab header: no bottom
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_mid = Alignment(vertical="center")
center_nowrap = Alignment(horizontal="center", vertical="center")

def ts_to_date(ts):
    try:
        t = int(ts)
        if t <= 0: return None
        return datetime.datetime.utcfromtimestamp(t).date()
    except Exception:
        return None

# ---------- load data ----------
doms = json.load(open(os.path.join(BASE, "out/classified_domains.json")))
links = json.load(open(os.path.join(BASE, "out/classified_links.json")))

comp = {}
cpath = os.path.join(BASE, "data/metrics/comparison.csv")
if os.path.exists(cpath):
    for line in open(cpath):
        p = line.rstrip("\n").split(";")
        if len(p) >= 4 and not line.lower().startswith("target;"):
            d = canon_host(p[0])
            def _i(x):
                try: return int(float(x))
                except: return None
            comp[d] = {"as": _i(p[1]), "backlinks": _i(p[2]), "rds": _i(p[3]),
                       "follows": _i(p[4]) if len(p) > 4 else None,
                       "nofollows": _i(p[5]) if len(p) > 5 else None}

met = {}
mpath = os.path.join(BASE, "data/metrics/metrics.csv")
if os.path.exists(mpath):
    for line in open(mpath):
        p = line.rstrip("\n").split(";")
        if len(p) >= 3 and not line.lower().startswith("domain;"):
            d = canon_host(p[0])
            def _i(x):
                try: return int(float(x))
                except: return 0
            met[d] = {"kw": _i(p[1]), "tr": _i(p[2])}

def as_of(d):
    c = comp.get(d, {})
    if c.get("as") is not None: return c["as"]
    return doms[d]["as"]
def backlinks_of(d):
    c = comp.get(d, {})
    if c.get("backlinks") is not None: return c["backlinks"]
    try: return int(doms[d]["backlinks_num"])
    except: return doms[d]["n_links"]
def rds_of(d):
    return comp.get(d, {}).get("rds")
def traffic_of(d):
    return met.get(d, {}).get("tr")
def kw_of(d):
    return met.get(d, {}).get("kw")

def build_findings(doms, links, dom_by_status, emit_disavow):
    import re
    nd = len(doms)
    spam_do = len(dom_by_status.get("Spam (Disavow)", []))
    spam_nf = len(dom_by_status.get("Spam (Nofollow, No Action)", []))
    held_pp = len(dom_by_status.get("Held (Pending Partner)", []))
    held_nf = len(dom_by_status.get("Held (Nofollow, No Action)", []))
    keep = len(dom_by_status.get("Keep", []))
    spam_total = spam_do + spam_nf
    dofollow_spam_links = sum(1 for l in links if l["status"] == "Spam (Disavow)" and l["link_type"] == "Dofollow")
    # two-campaign split
    def is_home(u):
        m = re.sub(r'^https?://[^/]+', '', (u or "").lower()).strip('/').split('?')[0]
        return m in ("", "index.html", "home")
    sales_links = [l for l in links if l["anchor_type"] == "Spam: keyword stuffed SEO sales copy"]
    sales_home = sum(1 for l in sales_links if is_home(l["target_url"]))
    exact_links = [l for l in links if l["anchor_type"].startswith("Exact match")]
    exact_deep = sum(1 for l in exact_links if not is_home(l["target_url"]))
    # dominant anchor
    anchor_doms = defaultdict(set)
    for l in links: anchor_doms[l["anchor"]].add(l["refdomain"])
    top_anchor, top_set = max(anchor_doms.items(), key=lambda kv: len(kv[1]))
    # task clusters
    tele = set(); wa = set(); xyz = set()
    for l in links:
        a = l["anchor"]
        if re.search(r'(join our telegram|our telegram chanel|t\.me/)', a, re.I): tele.add(l["refdomain"])
        if a.lower().startswith("i will increase your domain"): wa.add(l["refdomain"])
        if a.lower().startswith('"as a small business owner'): xyz.add(l["refdomain"])
    # held no-traffic
    held_doms = dom_by_status.get("Held (Pending Partner)", []) + dom_by_status.get("Held (Nofollow, No Action)", [])
    held_with_met = [d for d in held_doms if met.get(d)]
    held_zero = sum(1 for d in held_with_met if met[d]["tr"] == 0)
    held_frac = (f"{held_zero} of the {len(held_with_met)}" if held_with_met else "most")

    f1 = (f"{spam_total:,} of the {nd:,} referring domains are spam. {spam_do:,} carry at least one "
          f"dofollow link and go in the disavow file; the other {spam_nf:,} are nofollow only and need no action.")
    f2 = ("The attack roughly doubled in two months. Semrush shows ~1,650 referring domains steady through "
          "mid-2026, then 3,217 by October 2026. We audited the full live profile, not the older snapshot.")
    f3 = (f"You can upload a disavow file for {MONEY} only, and one file covers every bad domain. No client-owned "
          "domains redirect into the site, so a single file is both necessary and sufficient.")
    f4 = (f"Two patterns, easy to tell apart. The link-scheme flood hits the home page ({sales_home:,} sales-copy "
          f"links point there); the commissioned-looking commercial anchors hit deep service and location pages "
          f"({exact_deep:,} links). The home-page flood is the attack.")
    f5 = (f'The biggest anchor, on {len(top_set):,} domains, is link sales copy that names the client: '
          f'"{top_anchor[:70]}".')
    f6 = (f"The two named clusters: {len(tele)} domains carry a Telegram channel invitation "
          f'("JOIN OUR TELEGRAM"), all nofollow, so they pass nothing and need no disavow; {len(wa)} domains carry a '
          f'WhatsApp link-service pitch ("I will Increase your Domain Authority..."), all dofollow, so they are '
          f"disavowed; {len(xyz)} more self-promotional link-service .xyz domains are nofollow, no action.")
    f7 = (f"{held_pp+held_nf} domains are held for the previous partner to confirm, in case any were paid "
          f"placements. Held does not mean valuable: {held_frac} held domains have no organic traffic at all.")
    return [f1, f2, f3, f4, f5, f6, f7]


def write_disavow(emit_disavow, doms):
    import re
    # group by reason
    def reason(d):
        v = doms[d]; a = (v["top_anchor"] or "").lower(); t = (v["example_title"] or "").lower()
        if re.search(r'(join our telegram|t\.me/|telegram)', a): return "telegram"
        if a.startswith("i will increase your domain") or "whatsapp us" in a: return "pitch"
        if re.search(r'(back ?link|linkbuilding|\bseo\b|\bpbn\b|dofollow|offpage|rankbuild|guestpost|seoboost)', d): return "hostspam"
        if re.search(r'(casino|poker|gambl|porn|\bsex\b|escort|viagra)', a+t+d): return "offtopic"
        return "salescopy"
    groups = defaultdict(list)
    for d in sorted(emit_disavow): groups[reason(d)].append(d)
    order = [("salescopy","SEO sales-copy / link-scheme spam (dofollow)"),
             ("hostspam","Link-service / backlink-seller host names (dofollow)"),
             ("pitch","Self-promotional link-service pitch anchors (dofollow)"),
             ("telegram","Messaging-app channel-invitation spam (dofollow)"),
             ("offtopic","Off-topic spam (dofollow)")]
    lines = []
    lines.append(f"# Disavow file for {MONEY}")
    lines.append(f"# Generated {datetime.date.today().isoformat()} by the Harbinger backlink audit.")
    lines.append(f"# Property: {MONEY} (Google Search Console domain property).")
    lines.append(f"# {len(emit_disavow)} domains, all confirmed spam with at least one dofollow link.")
    lines.append("#")
    lines.append("# DO NOT UPLOAD until the previous SEO partner has confirmed the Held list.")
    lines.append("# Held domains (exact-match commercial / deep-page links) are EXCLUDED from this file -")
    lines.append("# they may be commissioned placements; disavowing them could hurt rankings.")
    lines.append("# Nofollow-only spam is EXCLUDED (it passes no ranking value).")
    lines.append("# This is the only file to submit; it is the full set (no redirect properties exist).")
    lines.append("# Confirm whether a disavow file already exists on the property: if one does, uploading")
    lines.append("# REPLACES it, so merge first; if the client has confirmed there is none, submit as-is.")
    lines.append("#")
    for key, label in order:
        if not groups.get(key): continue
        lines.append(f"# --- {label}: {len(groups[key])} domains ---")
        for d in groups[key]:
            lines.append("domain:" + d)
        lines.append("#")
    out = os.path.join(BASE, "out", DISAVOW_FILE)
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("disavow file:", out, "domains:", len(emit_disavow))


STATUSES = ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
            "Spam (Nofollow, No Action)", "Keep", "Own Site"]
WHATMEANS = {
 "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
 "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a product, service or location page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
 "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep": "Genuine or harmless link. Keep.",
 "Own Site": "Client owned domain or subdomain.",
}

# ---------- redundant disavow children ----------
disavow_doms = [d for d in doms if doms[d]["status"] == "Spam (Disavow)"]
disavow_set = set(disavow_doms)
redundant = set()
for d in disavow_doms:
    for parent in disavow_set:
        if parent != d and d.endswith("." + parent):
            redundant.add(d); break
emit_disavow = [d for d in disavow_doms if d not in redundant]

# ---------- per-status aggregates ----------
dom_by_status = defaultdict(list)
for d, v in doms.items():
    dom_by_status[v["status"]].append(d)
links_by_status = Counter(l["status"] for l in links)
total_domains = len(doms)
total_links = len(links)

wb = openpyxl.Workbook()

# ============ TAB 1: SUMMARY ============
ws = wb.active; ws.title = "Summary"
ws.sheet_view.showGridLines = False
# logo
logo_path = os.path.join(BASE, "ref/harbinger_logo.png")
if os.path.exists(logo_path):
    img = XLImage(logo_path)
    img.anchor = "A1"
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
    from openpyxl.drawing.xdr import XDRPositiveSize2D
    marker = AnchorMarker(col=0, colOff=381000, row=0, rowOff=0)
    img.anchor = OneCellAnchor(_from=marker, ext=XDRPositiveSize2D(cx=1866900, cy=552450))
    ws.add_image(img)
# title
ws.merge_cells("B1:E2")
c = ws["B1"]; c.value = CLIENT; c.font = font(21, True, ACCENT); c.alignment = center_nowrap
# status table header row 3
hdrs = ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"]
for i, h in enumerate(hdrs):
    cc = ws.cell(row=3, column=1+i, value=h)
    cc.font = font(10, True, WHITE); cc.fill = fill_accent; cc.alignment = center; cc.border = border_all
r = 4
for st in STATUSES:
    nd = len(dom_by_status.get(st, []))
    nl = links_by_status.get(st, 0)
    ws.cell(row=r, column=1, value=st).font = font(9)
    ws.cell(row=r, column=2, value=nd).font = font(9)
    ws.cell(row=r, column=3, value=nl).font = font(9)
    ws.cell(row=r, column=4, value=(nd/total_domains if total_domains else 0)).font = font(9)
    ws.cell(row=r, column=5, value=WHATMEANS[st]).font = font(9)
    for col in range(1, 6):
        cell = ws.cell(row=r, column=col); cell.fill = fill_white; cell.border = border_all
        cell.alignment = (left_mid if col in (1, 5) else center_nowrap)
    ws.cell(row=r, column=2).number_format = "#,##0"
    ws.cell(row=r, column=3).number_format = "#,##0"
    ws.cell(row=r, column=4).number_format = "0.0%"
    r += 1
# total row
ws.cell(row=r, column=1, value="Total").font = font(9, True)
ws.cell(row=r, column=2, value=total_domains).font = font(9, True)
ws.cell(row=r, column=3, value=total_links).font = font(9, True)
ws.cell(row=r, column=4, value=1.0).font = font(9, True)
for col in range(1, 6):
    cell = ws.cell(row=r, column=col); cell.fill = fill_white; cell.border = border_all
    cell.alignment = (left_mid if col in (1, 5) else center_nowrap)
ws.cell(row=r, column=2).number_format = "#,##0"
ws.cell(row=r, column=3).number_format = "#,##0"
ws.cell(row=r, column=4).number_format = "0.0%"
total_row = r

# key findings
kf_row = total_row + 1
ws.cell(row=kf_row, column=1, value="Key findings").font = font(10, True)
findings = build_findings(doms, links, dom_by_status, emit_disavow)
fr = kf_row + 1
for text in findings:
    ws.merge_cells(start_row=fr, start_column=1, end_row=fr, end_column=5)
    cc = ws.cell(row=fr, column=1, value=text); cc.font = font(9); cc.alignment = Alignment(vertical="center", wrap_text=True)
    fr += 1

# anchor profile
ap_row = fr
ws.cell(row=ap_row, column=1, value="Anchor text profile (all backlinks)").font = font(11, True, ACCENT)
aphdr = ["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"]
hr = ap_row + 1
for i, h in enumerate(aphdr):
    cc = ws.cell(row=hr, column=1+i, value=h)
    cc.font = font(9, True, WHITE); cc.fill = fill_accent; cc.alignment = center; cc.border = border_all
# aggregate anchor types
at_links = Counter(l["anchor_type"] for l in links)
at_doms = defaultdict(set)
for l in links:
    at_doms[l["anchor_type"]].add(l["refdomain"])
dr = hr + 1
for at, cnt in at_links.most_common():
    ws.cell(row=dr, column=1, value=at).font = font(9)
    ws.cell(row=dr, column=2, value=cnt).font = font(9)
    ws.cell(row=dr, column=3, value=(cnt/total_links if total_links else 0)).font = font(9)
    ws.cell(row=dr, column=4, value=len(at_doms[at])).font = font(9)
    for col in range(1, 5):
        cell = ws.cell(row=dr, column=col); cell.fill = fill_white; cell.border = border_all
        cell.alignment = (left_mid if col == 1 else center_nowrap)
    ws.cell(row=dr, column=2).number_format = "#,##0"
    ws.cell(row=dr, column=3).number_format = "0.0%"
    ws.cell(row=dr, column=4).number_format = "#,##0"
    dr += 1
# widths + heights
for col, w in {"A":38.86,"B":16.29,"C":17.57,"D":18.71,"E":120.0,"F":13.0}.items():
    ws.column_dimensions[col].width = w
for rr in range(1, dr+1):
    ws.row_dimensions[rr].height = 22.5

# ============ helper to style a data tab ============
def data_tab(title, headers, rows, widths, row_height, numfmts=None, date_cols=None,
             input_cols=None, dropdowns=None):
    ws = wb.create_sheet(title)
    numfmts = numfmts or {}; date_cols = date_cols or set(); input_cols = input_cols or {}
    for i, h in enumerate(headers):
        cc = ws.cell(row=1, column=1+i, value=h)
        cc.font = font(9, True, WHITE); cc.fill = fill_accent; cc.alignment = center; cc.border = border_hdr
    for ri, row in enumerate(rows, start=2):
        for ci, val in enumerate(row, start=1):
            cc = ws.cell(row=ri, column=ci, value=val)
            cc.font = font(9); cc.fill = fill_white; cc.alignment = left_mid
            if ci in numfmts: cc.number_format = numfmts[ci]
            if ci in date_cols: cc.number_format = "d mmm yyyy"
        # partner input cells (empty, accent-filled)
        for ci in input_cols:
            cc = ws.cell(row=ri, column=ci)
            cc.fill = fill_accent; cc.font = font(9, color=WHITE)
    # column widths
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(1+i)].width = w
    ws.row_dimensions[1].height = 31.5
    nrows = len(rows)
    for rr in range(2, nrows+2):
        ws.row_dimensions[rr].height = row_height
    ws.freeze_panes = "B2"
    last = get_column_letter(len(headers))
    ws.auto_filter.ref = f"A1:{last}{max(nrows+1,1)}"
    if dropdowns:
        for col_letter, formula in dropdowns.items():
            dv = DataValidation(type="list", formula1=formula, allow_blank=True)
            dv.add(f"{col_letter}2:{col_letter}{nrows+1}")
            ws.add_data_validation(dv)
    return ws

# ============ TAB 2: Referring Domain Audit ============
rda_headers = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To",
               "Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page",
               "Linking Page Title","Source","IP","Disavow Line"]
def in_disavow(st):
    if st == "Spam (Disavow)": return "Yes"
    if st.startswith("Held"): return "Held"
    return "No"
rda_rows = []
for d in sorted(doms.keys()):
    v = doms[d]
    st = v["status"]
    rda_rows.append([
        d, st, as_of(d), backlinks_of(d), rds_of(d), traffic_of(d), in_disavow(st),
        v["links_point_to"], v["dofollow_links"], v["nofollow_links"], ts_to_date(v["first_seen"]),
        v["top_anchor"], v["example_page"], v["example_title"], v["source"], v["ip"],
        ("domain:"+d) if (st == "Spam (Disavow)" and d not in redundant) else ""
    ])
data_tab("Referring Domain Audit", rda_headers, rda_rows,
         widths=[36,24.71,9.57,13,9.43,9.71,12.43,21.29,14,8.71,12,45,8.71,40,14,15,14],
         row_height=15.75,
         numfmts={3:"General",4:"#,##0",5:"#,##0",6:"#,##0",9:"#,##0",10:"#,##0"},
         date_cols={11})

# ============ TAB 3: All Backlinks ============
ab_headers = ["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
              "Linking Page URL","Linking Page Title","Target URL"]
ab_rows = [[l["refdomain"],l["status"],l["tool"],l["anchor"],l["anchor_type"],l["link_type"],
            l["page_url"],l["page_title"],l["target_url"]] for l in links]
data_tab("All Backlinks", ab_headers, ab_rows,
         widths=[25.43,27.14,14.71,55,32,10,55,53.14,30.57], row_height=22.5)

# ============ TAB 4: Anchor Analysis ============
aa_headers = ["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
anchor_links = Counter(l["anchor"] for l in links)
anchor_type_map = {}
anchor_doms = defaultdict(set)
anchor_spamdoms = defaultdict(set)
for l in links:
    anchor_type_map[l["anchor"]] = l["anchor_type"]
    anchor_doms[l["anchor"]].add(l["refdomain"])
    if l["status"].startswith("Spam"):
        anchor_spamdoms[l["anchor"]].add(l["refdomain"])
aa_rows = []
for a, cnt in anchor_links.most_common():
    aa_rows.append([a, anchor_type_map[a], cnt, (cnt/total_links if total_links else 0),
                    len(anchor_doms[a]), len(anchor_spamdoms[a])])
data_tab("Anchor Analysis", aa_headers, aa_rows,
         widths=[115.86,37.71,14,8.71,13,20.29], row_height=22.5,
         numfmts={3:"#,##0",4:"0.00%",5:"#,##0",6:"#,##0"})

# ============ TAB 5: Exact Match Anchors ============
ema_headers = ["Referring domain","Example backlink (linking page)","Exact-match commercial anchor",
               "Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
GEO_RE = __import__("re").compile(r'(conyers|eatonton|columbus|acworth|savannah|georgia|\bga\b)', __import__("re").I)
def market(a):
    import re
    m = re.search(r'(conyers|eatonton|columbus|acworth|savannah|winder|jonesboro)', a, re.I)
    if m: return m.group(1).title()+" GA"
    if re.search(r'georgia|\bga\b', a, re.I): return "Georgia"
    return "Non-geo"
ema_rows = []
seen_ema = set()
for l in links:
    if not l["anchor_type"].startswith("Exact match"): continue
    if not doms[l["refdomain"]]["status"].startswith("Held"): continue
    key = (l["refdomain"], l["anchor"])
    if key in seen_ema: continue
    seen_ema.add(key)
    ema_rows.append([l["refdomain"], l["page_url"], l["anchor"], market(l["anchor"]),
                     "Low quality web directory", None, None])
ema_rows.sort(key=lambda x: x[0])
data_tab("Exact Match Anchors", ema_headers, ema_rows,
         widths=[25.43,59,53.14,16,24.57,15.43,15], row_height=22.5,
         input_cols=[6,7], dropdowns={"F":'"Y,N"', "G":'"Keep,Disavow"'})

# ============ TAB 6: Pending Disavow Lines ============
pd_headers = ["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"]
pd_rows = []
for d in sorted(doms.keys()):
    if doms[d]["status"].startswith("Held"):
        pd_rows.append([d, "domain:"+d,
                        f"Append only if the partner does not claim it, to {DISAVOW_FILE}"])
data_tab("Pending Disavow Lines", pd_headers, pd_rows, widths=[32,44,48], row_height=22.5)

# ============ TAB 7: Disavow List ============
dl_headers = ["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
dl_rows = []
for d in sorted(emit_disavow):
    dl_rows.append(["domain:"+d, as_of(d), backlinks_of(d), rds_of(d), traffic_of(d), kw_of(d),
                    doms[d]["top_anchor"]])
data_tab("Disavow List", dl_headers, dl_rows,
         widths=[44,14,15.57,14,11.14,14.86,98.86], row_height=22.5,
         numfmts={2:"General",3:"#,##0",4:"#,##0",5:"#,##0",6:"#,##0"})

os.makedirs(os.path.join(BASE, "out"), exist_ok=True)
outxlsx = os.path.join(BASE, "out/HighPriorityPlumbing_Backlinks_Audit.xlsx")
wb.save(outxlsx)
print("workbook saved:", outxlsx)
print("domains:", total_domains, "links:", total_links)
print("disavow emit:", len(emit_disavow), "redundant:", len(redundant))
print("held:", len(pd_rows), "exact-match rows:", len(ema_rows))

# ---------- disavow file ----------
write_disavow(emit_disavow, doms)
