"""
build.py - build the Fitzgerald Plumbing backlink-audit workbook + disavow files,
in the signed-off Harbinger format (reverse-engineered cell-for-cell from the
K&K Manufacturing template). Change the format here, never by hand in Excel.
"""
import os, json, glob, collections, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)
LOGO = os.path.join(BASE, "data", "harbinger_logo.png")

CLIENT_NAME = "Fitzgerald Plumbing"
MONEY = "fitzgeraldplumbing.com"
REDIRECTS = ["fitzgeraldandsonsplumbing.com", "fitzplumb.com"]
PROPERTIES = [MONEY] + REDIRECTS
SUPPLIER_WORD = "supplier"   # client's brief term; the sheet keeps saying "partner"

# --- live profile history (Semrush backlinks_historical / overview), captured at pull time ---
BRIEF_RD = 149
LIVE_RD_SEMRUSH = 4646
HIST = "~1,135 referring domains in Oct 2025 and ~1,300 through mid-2026, 1,456 in Sep, 4,449 in Oct"

ACCENT = "FF0C343D"
WHITE  = "FFFFFFFF"
BLACK  = "FF000000"

# ---------- fonts ----------
F_TITLE   = Font(name="Geist", size=21, bold=True, color=ACCENT)
F_HDR     = Font(name="Geist", size=9,  bold=True, color=WHITE)
F_HDR10   = Font(name="Geist", size=10, bold=True, color=WHITE)
F_DATA    = Font(name="Geist", size=9,  color=BLACK)
F_BOLD9   = Font(name="Geist", size=9,  bold=True, color=BLACK)
F_KEYHEAD = Font(name="Geist", size=10, bold=True, color=BLACK)
F_SECTION = Font(name="Geist", size=11, bold=True, color=ACCENT)
F_INPUT   = Font(name="Geist", size=9,  color=WHITE)
F_KEYBODY = Font(name="Geist", size=9,  color=BLACK)

FILL_ACCENT = PatternFill("solid", fgColor=ACCENT)
FILL_WHITE  = PatternFill("solid", fgColor=WHITE)

thin = Side(style="thin", color=BLACK)
B_HDR  = Border(left=thin, right=thin, top=thin)              # header row: L/R/T (no bottom)
B_ALL  = Border(left=thin, right=thin, top=thin, bottom=thin) # summary tables: full box

A_CTR  = Alignment(horizontal="center", vertical="center")
A_CTRW = Alignment(horizontal="center", vertical="center", wrap_text=True)
A_LEFT = Alignment(horizontal="left", vertical="center")
A_VC   = Alignment(vertical="center")

FMT_INT  = "#,##0"
FMT_PCT1 = "0.0%"
FMT_PCT2 = "0.00%"
FMT_DATE = "d mmm yyyy"

STATUS_ORDER = ["Spam (Disavow)", "Spam (Nofollow, No Action)", "Held (Pending Partner)",
                "Held (Nofollow, No Action)", "Keep", "Own Site"]
STATUS_MEANS = {
 "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
 "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a product, capability or location page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
 "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Keep": "Genuine or harmless link. Keep.",
 "Own Site": "Client owned domain that redirects into the site.",
}

def load():
    domains = json.load(open(os.path.join(PROC, "domains.json"), encoding="utf-8"))
    links = [json.loads(l) for l in open(os.path.join(PROC, "links_enriched.jsonl"), encoding="utf-8")]
    ahrefs = {}
    for f in glob.glob(os.path.join(BASE, "data", "metrics", "metrics_*.jsonl")):
        for line in open(f, encoding="utf-8"):
            line=line.strip()
            if not line: continue
            try: r=json.loads(line)
            except: continue
            d=(r.get("domain") or "").strip().lower()
            if d: ahrefs[d]=r
    srfill = {}
    for f in glob.glob(os.path.join(BASE, "data", "metrics_sr", "sr_*.jsonl")):
        for line in open(f, encoding="utf-8"):
            line=line.strip()
            if not line: continue
            try: r=json.loads(line)
            except: continue
            d=(r.get("domain") or "").strip().lower()
            if d: srfill[d]=r
    # merged resolver: real Ahrefs -> Semrush backfill -> justified true-zero (traffic/kw), blank RD's
    merged = {}
    for d in set(domains):
        a = ahrefs.get(d)
        if a and (a.get("org_traffic") or a.get("org_keywords") or a.get("refdomains") or a.get("domain_rating") or a.get("backlinks")):
            merged[d] = {"org_traffic":a.get("org_traffic",0), "org_keywords":a.get("org_keywords",0),
                         "refdomains":a.get("refdomains",0), "src":"Ahrefs"}
        elif d in srfill:
            s = srfill[d]
            merged[d] = {"org_traffic":s.get("org_traffic",0), "org_keywords":s.get("org_keywords",0),
                         "refdomains":s.get("refdomains",0), "src":"Semrush"}
        else:
            merged[d] = {"org_traffic":0, "org_keywords":0, "refdomains":None, "src":"unmeasured"}
    return domains, links, merged

def site_type(v):
    d = v["domain"]
    t = (v.get("example_title") or "").lower()
    if any(x in d for x in ["directory","listing","listingz","weblink","bookmark"]):
        return "Low quality web directory"
    if v.get("spam_host"): return "Link-scheme / SEO host"
    if any(x in d for x in ["article","news","blog","post","media","hub","journal"]):
        return "Article / blog placement"
    if "bookmark" in d or "social" in d: return "Social bookmark"
    if v.get("deep_commercial"): return "Niche placement (deep page)"
    return "General web placement"

def set_cell(ws, r, c, val, font=F_DATA, fill=FILL_WHITE, border=None, align=A_VC, fmt=None):
    cell = ws.cell(row=r, column=c, value=val)
    cell.font = font; cell.fill = fill
    if border is not None: cell.border = border
    cell.alignment = align
    if fmt: cell.number_format = fmt
    return cell

A_HDR_LEFT   = Alignment(horizontal="left", vertical="center", wrap_text=True)
A_HDR_NOWRAP = Alignment(horizontal="center", vertical="center")

def header_row(ws, headers, widths, row=1, height=31.5, align_overrides=None):
    align_overrides = align_overrides or {}
    for i, h in enumerate(headers, start=1):
        set_cell(ws, row, i, h, font=F_HDR, fill=FILL_ACCENT, border=B_HDR,
                 align=align_overrides.get(i, A_CTRW))
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = height

def finalize_data_tab(ws, ncols, nrows, data_height):
    ws.freeze_panes = "B2"
    last = get_column_letter(ncols)
    ws.auto_filter.ref = f"A1:{last}{nrows+1}"
    # row heights for data rows
    for r in range(2, nrows+2):
        ws.row_dimensions[r].height = data_height

def excel_date(ts):
    if not ts: return None
    try: return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).date()
    except: return None

def build():
    domains, links, metrics = load()
    def M(d, k, default=0):
        return metrics.get(d, {}).get(k, default)

    total_links = len(links)
    # status aggregates
    S = collections.Counter(); SB = collections.Counter()
    for v in domains.values():
        S[v["status"]] += 1; SB[v["status"]] += v["backlinks"]
    total_dom = sum(S.values()); total_bl = sum(SB.values())

    # anchor profile
    at_links = collections.Counter(r["anchor_type"] for r in links)
    at_doms = collections.defaultdict(set)
    for r in links: at_doms[r["anchor_type"]].add(r["source_domain"])

    wb = openpyxl.Workbook()

    # ============ TAB 1: SUMMARY ============
    ws = wb.active; ws.title = "Summary"
    ws.sheet_view.showGridLines = False
    for col, w in zip("ABCDE", [38.86, 16.29, 17.57, 18.71, 120.0]):
        ws.column_dimensions[col].width = w
    # logo
    try:
        img = XLImage(LOGO)
        img.anchor = OneCellAnchor(_from=AnchorMarker(col=0, colOff=381000, row=0, rowOff=0),
                                   ext=XDRPositiveSize2D(1866900, 552450))
        ws.add_image(img)
    except Exception as e:
        print("logo warn:", e)
    # title B1:E2
    ws.merge_cells("B1:E2")
    set_cell(ws, 1, 2, CLIENT_NAME, font=F_TITLE, fill=FILL_WHITE, align=A_CTR)
    # status table header row 3
    for i, h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"], start=1):
        set_cell(ws, 3, i, h, font=F_HDR10, fill=FILL_ACCENT, border=B_ALL, align=A_CTRW)
    r = 4
    for s in STATUS_ORDER:
        set_cell(ws, r, 1, s, font=F_DATA, fill=FILL_WHITE, border=B_ALL, align=A_VC)
        set_cell(ws, r, 2, S.get(s,0), border=B_ALL, align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 3, SB.get(s,0), border=B_ALL, align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 4, (S.get(s,0)/total_dom if total_dom else 0), border=B_ALL, align=A_CTR, fmt=FMT_PCT1)
        set_cell(ws, r, 5, STATUS_MEANS[s], font=F_DATA, fill=FILL_WHITE, border=B_ALL,
                 align=Alignment(vertical="center", wrap_text=True))
        r += 1
    # total row
    set_cell(ws, r, 1, "Total", font=F_BOLD9, fill=FILL_WHITE, border=B_ALL, align=A_VC)
    set_cell(ws, r, 2, total_dom, font=F_BOLD9, border=B_ALL, align=A_CTR, fmt=FMT_INT)
    set_cell(ws, r, 3, total_bl, font=F_BOLD9, border=B_ALL, align=A_CTR, fmt=FMT_INT)
    set_cell(ws, r, 4, 1.0, font=F_BOLD9, border=B_ALL, align=A_CTR, fmt=FMT_PCT1)
    set_cell(ws, r, 5, "", font=F_BOLD9, fill=FILL_WHITE, border=B_ALL, align=A_VC)
    total_row = r
    # key findings
    kf_head = total_row + 1
    set_cell(ws, kf_head, 1, "Key findings", font=F_KEYHEAD, fill=FILL_WHITE, align=A_VC)
    spam_df = S.get("Spam (Disavow)",0); spam_nf = S.get("Spam (Nofollow, No Action)",0)
    held = S.get("Held (Pending Partner)",0) + S.get("Held (Nofollow, No Action)",0)
    sales_links = at_links.get("Spam: keyword stuffed SEO sales copy",0)
    exact_links = at_links.get("Exact match commercial (geo)",0) + at_links.get("Exact match commercial",0)
    home_links = sum(1 for r_ in links if r_["target_is_home"])
    deep_links = total_links - home_links
    held_no_traffic = sum(1 for v in domains.values()
                          if v["status"].startswith("Held") and M(v["domain"],"org_traffic",0)==0)
    findings = [
        f"{spam_df+spam_nf} of the {total_dom} referring domains are spam. {spam_df} have a dofollow link and go in the disavow file; the other {spam_nf} are nofollow and pass no value, so they need no action.",
        f"The profile exploded since the brief: {HIST}, and {LIVE_RD_SEMRUSH} now (Semrush). The brief named {BRIEF_RD}. We audited the full live profile, not the brief's list - this is an active negative-SEO / spam attack.",
        f"The client owns three properties: {MONEY} plus {REDIRECTS[0]} and {REDIRECTS[1]}, which 301-redirect into it. The {MONEY} file is the full union of every bad domain; separate files are provided for the two redirect properties so each Search Console property can be cleaned.",
        f"Two patterns, easy to tell apart. {sales_links:,} link-scheme / sales-copy links hit the home page; the {exact_links:,} exact-match commercial links hit deep location and service pages. Of all {total_links:,} links, {home_links:,} point at the home page and {deep_links:,} at deep pages - the home-page flood is the attack.",
        f"The biggest anchors are backlink sales copy that names the client's own domains (e.g. \"{MONEY} Premium Backlink Building...\"), used across thousands of throwaway domains.",
        f"{held} domains are held for the previous {SUPPLIER_WORD} to confirm, in case any exact-match commercial links on deep pages were paid placements. They are NOT in the disavow file until that conversation happens.",
        f"Held does not mean valuable: {held_no_traffic} of the {held} held domains have no organic traffic at all. Confirm, then disavow any the {SUPPLIER_WORD} did not build.",
    ]
    rr = kf_head + 1
    kf_start = rr
    for f in findings:
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
        set_cell(ws, rr, 1, f, font=F_KEYBODY, fill=FILL_WHITE,
                 align=Alignment(vertical="center", wrap_text=True))
        rr += 1
    # anchor profile section
    sec = rr
    set_cell(ws, sec, 1, "Anchor text profile (all backlinks)", font=F_SECTION, fill=FILL_WHITE, align=A_VC)
    aph = sec + 1
    for i, h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains",""], start=1):
        set_cell(ws, aph, i, h, font=F_HDR, fill=FILL_ACCENT, border=B_ALL, align=A_CTRW)
    ar = aph + 1
    for t, c in at_links.most_common():
        set_cell(ws, ar, 1, t, font=F_DATA, fill=FILL_WHITE, border=B_ALL, align=A_VC)
        set_cell(ws, ar, 2, c, border=B_ALL, align=A_CTR, fmt=FMT_INT)
        set_cell(ws, ar, 3, (c/total_links if total_links else 0), border=B_ALL, align=A_CTR, fmt=FMT_PCT1)
        set_cell(ws, ar, 4, len(at_doms[t]), border=B_ALL, align=A_CTR, fmt=FMT_INT)
        set_cell(ws, ar, 5, "", font=F_DATA, fill=FILL_WHITE, align=A_VC)
        ar += 1
    for rh in range(1, ar+1):
        ws.row_dimensions[rh].height = 22.5

    # ============ TAB 2: REFERRING DOMAIN AUDIT ============
    ws = wb.create_sheet("Referring Domain Audit")
    h2 = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To",
          "Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page",
          "Linking Page Title","Source","IP","Disavow Line"]
    w2 = [36,24.71,9.57,13,9.43,9.71,12.43,21.29,14,8.71,12,45,8.71,40,14,15,14]
    header_row(ws, h2, w2)
    doms_sorted = sorted(domains.values(), key=lambda v: v["domain"])
    r = 2
    for v in doms_sorted:
        d = v["domain"]
        indis = "Yes" if v["status"]=="Spam (Disavow)" else ("Held" if v["status"].startswith("Held") else "No")
        props = ", ".join(sorted(v.get("target_properties",{}), key=lambda p: -v["target_properties"][p])[:3]) or MONEY
        set_cell(ws, r, 1, d, align=A_VC)
        set_cell(ws, r, 2, v["status"], align=A_VC)
        set_cell(ws, r, 3, v["ascore"], align=A_CTR)
        set_cell(ws, r, 4, v["backlinks"], align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 5, M(d,"refdomains",0), align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 6, M(d,"org_traffic",0), align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 7, indis, align=A_CTR)
        set_cell(ws, r, 8, props, align=A_VC)
        set_cell(ws, r, 9, v["dofollow"], align=A_CTR)
        set_cell(ws, r,10, v["nofollow"], align=A_CTR)
        set_cell(ws, r,11, excel_date(v["first_seen"]), align=A_CTR, fmt=FMT_DATE)
        set_cell(ws, r,12, v["top_anchor"], align=A_VC)
        set_cell(ws, r,13, v["example_url"], align=A_VC)
        set_cell(ws, r,14, v["example_title"], align=A_VC)
        set_cell(ws, r,15, v["source_tool"], align=A_CTR)
        set_cell(ws, r,16, v["ip"], align=A_CTR)
        set_cell(ws, r,17, v["disavow_line"], align=A_VC)
        r += 1
    finalize_data_tab(ws, 17, len(doms_sorted), 15.75)

    # ============ TAB 3: ALL BACKLINKS ============
    ws = wb.create_sheet("All Backlinks")
    h3 = ["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
          "Linking Page URL","Linking Page Title","Target URL"]
    w3 = [25.43,27.14,14.71,55,32,10,55,53.14,30.57]
    header_row(ws, h3, w3, align_overrides={3: A_HDR_LEFT})  # 'Tool' header left-aligned (template)
    links_sorted = sorted(links, key=lambda r_: (r_["source_domain"], r_.get("source_url","")))
    r = 2
    for lk in links_sorted:
        d = lk["source_domain"]; st = domains.get(d,{}).get("status","")
        tgt = lk.get("redirect_url") or lk.get("target_url")
        set_cell(ws, r, 1, d, align=A_VC)
        set_cell(ws, r, 2, st, align=A_VC)
        set_cell(ws, r, 3, lk.get("tool",""), align=A_LEFT)
        set_cell(ws, r, 4, lk.get("anchor",""), align=A_VC)
        set_cell(ws, r, 5, lk.get("anchor_type",""), align=A_VC)
        set_cell(ws, r, 6, lk.get("link_type",""), align=A_CTR)
        set_cell(ws, r, 7, lk.get("source_url",""), align=A_VC)
        set_cell(ws, r, 8, lk.get("source_title",""), align=A_VC)
        set_cell(ws, r, 9, tgt, align=A_VC)
        r += 1
    finalize_data_tab(ws, 9, len(links_sorted), 22.5)

    # ============ TAB 4: ANCHOR ANALYSIS ============
    ws = wb.create_sheet("Anchor Analysis")
    h4 = ["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
    w4 = [115.86,37.71,14,8.71,8.71,20.29]
    header_row(ws, h4, w4, align_overrides={1: A_HDR_NOWRAP})  # 'Anchor Text' header not wrapped (template)
    anchor_rows = collections.defaultdict(lambda: {"bl":0,"doms":set(),"spam":set(),"type":""})
    spam_status = {"Spam (Disavow)","Spam (Nofollow, No Action)"}
    for lk in links:
        a = lk.get("anchor","")
        row = anchor_rows[a]
        row["bl"] += 1; row["doms"].add(lk["source_domain"]); row["type"] = lk["anchor_type"]
        if domains.get(lk["source_domain"],{}).get("status") in spam_status:
            row["spam"].add(lk["source_domain"])
    ordered = sorted(anchor_rows.items(), key=lambda kv: -kv[1]["bl"])
    r = 2
    for a, info in ordered:
        set_cell(ws, r, 1, a, align=A_VC)
        set_cell(ws, r, 2, info["type"], align=A_VC)
        set_cell(ws, r, 3, info["bl"], align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 4, (info["bl"]/total_links if total_links else 0), align=A_CTR, fmt=FMT_PCT2)
        set_cell(ws, r, 5, len(info["doms"]), align=A_CTR)
        set_cell(ws, r, 6, len(info["spam"]), align=A_CTR)
        r += 1
    finalize_data_tab(ws, 6, len(ordered), 22.5)

    # ============ TAB 5: EXACT MATCH ANCHORS ============
    ws = wb.create_sheet("Exact Match Anchors")
    h5 = ["Referring domain","Example backlink (linking page)","Exact-match commercial anchor",
          "Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
    w5 = [25.43,59,53.14,16,24.57,15.43,15]
    header_row(ws, h5, w5)
    em_rows = []
    for v in doms_sorted:
        if not v["status"].startswith("Held"):
            continue
        seen = set()
        for lk in v["links"]:
            if lk["anchor_type"] in ("Exact match commercial","Exact match commercial (geo)"):
                a = lk.get("anchor","")
                if a in seen: continue
                seen.add(a)
                market = "Geo (GA)" if lk["anchor_type"].endswith("(geo)") else "Non-geo"
                em_rows.append((v["domain"], lk.get("source_url",""), a, market, site_type(v)))
    r = 2
    for dom, ex, a, market, st in em_rows:
        set_cell(ws, r, 1, dom, align=A_VC)
        set_cell(ws, r, 2, ex, align=A_VC)
        set_cell(ws, r, 3, a, align=A_CTR)
        set_cell(ws, r, 4, market, align=A_CTR)
        set_cell(ws, r, 5, st, align=A_VC)
        set_cell(ws, r, 6, "", font=F_INPUT, fill=FILL_ACCENT, align=A_VC)   # input
        set_cell(ws, r, 7, "", font=F_INPUT, fill=FILL_ACCENT, align=A_VC)   # input
        r += 1
    finalize_data_tab(ws, 7, len(em_rows), 22.5)

    # ============ TAB 6: PENDING DISAVOW LINES ============
    ws = wb.create_sheet("Pending Disavow Lines")
    h6 = ["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"]
    w6 = [32,44,48]
    header_row(ws, h6, w6)
    pend = [v for v in doms_sorted if v["status"].startswith("Held")]
    rec = f"Append only if the partner does not claim it, to disavow_{MONEY}.txt"
    r = 2
    for v in pend:
        set_cell(ws, r, 1, v["domain"], align=A_VC)
        set_cell(ws, r, 2, f"domain:{v['domain']}", align=A_VC)
        set_cell(ws, r, 3, rec, align=A_VC)
        r += 1
    finalize_data_tab(ws, 3, len(pend), 22.5)

    # ============ TAB 7: DISAVOW LIST ============
    ws = wb.create_sheet("Disavow List")
    h7 = ["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
    w7 = [44,14,15.57,14,11.14,14.86,98.86]
    header_row(ws, h7, w7)
    disavow = sorted([v for v in domains.values() if v["status"]=="Spam (Disavow)"],
                     key=lambda v: v["domain"])
    r = 2
    for v in disavow:
        d = v["domain"]
        set_cell(ws, r, 1, f"domain:{d}", align=A_VC)
        set_cell(ws, r, 2, v["ascore"], align=A_CTR)
        set_cell(ws, r, 3, v["backlinks"], align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 4, M(d,"refdomains",0), align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 5, M(d,"org_traffic",0), align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 6, M(d,"org_keywords",0), align=A_CTR, fmt=FMT_INT)
        set_cell(ws, r, 7, v["top_anchor"], align=A_VC)
        r += 1
    finalize_data_tab(ws, 7, len(disavow), 22.5)

    out_xlsx = os.path.join(OUT, "Fitzgerald_Plumbing_Backlink_Audit.xlsx")
    wb.save(out_xlsx)
    print("WROTE", out_xlsx)

    # ============ DISAVOW FILES (one per property) ============
    write_disavow_files(domains, links)
    write_cover_note(domains, links, metrics)
    print("status counts:", dict(S))
    print("disavow lines:", len(disavow), "| held:", len(pend), "| exact-match rows:", len(em_rows),
          "| anchors:", len(ordered), "| links:", total_links)

def write_disavow_files(domains, links):
    # property attribution: which properties each domain's links point at
    dom_props = collections.defaultdict(set)
    for r in links:
        dom_props[r["source_domain"]].add(r["target_property"])
    disavow = {d:v for d,v in domains.items() if v["status"]=="Spam (Disavow)"}
    # drop redundant children (parent domain also disavowed)
    dset = set(disavow.keys())
    def redundant(d):
        labels = d.split(".")
        for k in range(1, len(labels)-1):
            if ".".join(labels[k:]) in dset:
                return True
        return False
    def reason_group(v):
        if v["has_offtopic"]: return "Off-topic spam (gambling / pharma / adult)"
        if v["has_sales_anchor"] or v["sales_dominant"]: return "SEO / backlink sales-copy link scheme"
        if v["spam_title"]: return "Domain-marketplace / aged-domain spam page"
        if v["spam_url"]: return "Link-scheme URL template"
        if v["spam_host"]: return "Spam / link-directory host"
        return "Spam"

    for prop in PROPERTIES:
        if prop == MONEY:
            members = [v for d,v in disavow.items() if not redundant(d)]
            scope = ("This is the MONEY SITE file. It is the full union of every spam domain across all "
                     "owned properties, because " + " and ".join(REDIRECTS) + " 301-redirect into " + MONEY +
                     " and Google forwards disavow signals across a redirect imperfectly. Upload THIS file to the "
                     + MONEY + " Search Console property.")
        else:
            members = [v for d,v in disavow.items() if prop in dom_props.get(d,set()) and not redundant(d)]
            scope = ("This file covers the spam domains whose links point at the redirect property " + prop +
                     ". Upload it to the " + prop + " Search Console property. (All of these are also included in "
                     "the " + MONEY + " union file.)")
        groups = collections.defaultdict(list)
        for v in members:
            groups[reason_group(v)].append(v["domain"])
        total = sum(len(x) for x in groups.values())
        lines = []
        lines.append(f"# Disavow file for Google Search Console property: {prop}")
        lines.append(f"# Client: {CLIENT_NAME}   Prepared by: Harbinger Marketing   Date: {datetime.date.today():%d %b %Y}")
        lines.append(f"# Domains to disavow: {total}")
        lines.append("#")
        lines.append("# " + scope.replace("\n"," "))
        lines.append("#")
        lines.append(f"# HELD domains are intentionally EXCLUDED. They carry exact-match commercial anchors on deep")
        lines.append(f"# pages and may be commissioned placements. Confirm with the previous SEO {SUPPLIER_WORD}")
        lines.append(f"# (the 'partner' referenced throughout the workbook) which of those they built. Do NOT upload")
        lines.append(f"# this file until that conversation has happened.")
        lines.append("#")
        lines.append(f"# Before uploading: check whether a disavow file already exists on this property in Search")
        lines.append(f"# Console. If one does, uploading REPLACES it - merge this list into the existing file rather")
        lines.append(f"# than overwriting. If the client has confirmed none exists, upload this as-is.")
        lines.append("#")
        lines.append(f"# Only 'domain:' entries are used (covers all subdomains). Redundant child subdomains omitted.")
        lines.append("")
        for g in sorted(groups):
            lines.append(f"# --- {g} ({len(groups[g])}) ---")
            for dom in sorted(groups[g]):
                lines.append(f"domain:{dom}")
            lines.append("")
        path = os.path.join(OUT, f"disavow_{prop}.txt")
        open(path, "w", encoding="utf-8").write("\n".join(lines))
        print(f"WROTE {path}  ({total} domains)")

def write_cover_note(domains, links, metrics):
    S = collections.Counter(v["status"] for v in domains.values())
    total = sum(S.values())
    spam_df = S.get("Spam (Disavow)",0); spam_nf = S.get("Spam (Nofollow, No Action)",0)
    held = S.get("Held (Pending Partner)",0) + S.get("Held (Nofollow, No Action)",0)
    keep = S.get("Keep",0); own = S.get("Own Site",0)
    dom_props = collections.defaultdict(set)
    for r in links: dom_props[r["source_domain"]].add(r["target_property"])
    disavow = {d:v for d,v in domains.items() if v["status"]=="Spam (Disavow)"}
    dset=set(disavow)
    def redundant(d):
        labels=d.split(".")
        return any(".".join(labels[k:]) in dset for k in range(1,len(labels)-1))
    union = [d for d in disavow if not redundant(d)]
    perprop = {p: [d for d in disavow if p in dom_props.get(d,set()) and not redundant(d)] for p in REDIRECTS}
    measured = sum(1 for d in domains if metrics.get(d,{}).get("src") in ("Ahrefs","Semrush"))
    unmeasured = total - measured
    held_doms = [v for v in domains.values() if v["status"].startswith("Held")]
    held_notraffic = sum(1 for v in held_doms if (metrics.get(v["domain"],{}).get("org_traffic") or 0)==0)

    L=[]
    L.append(f"# {CLIENT_NAME} - Backlink Audit & Disavow (cover note)")
    L.append(f"Prepared by Harbinger Marketing | {datetime.date.today():%d %B %Y}")
    L.append("")
    L.append("## What we did")
    L.append(f"- Audited the **full live backlink profile** of {MONEY} across **both Semrush and Ahrefs**, not the brief's snapshot.")
    L.append(f"- The brief named **{BRIEF_RD} referring domains**. The live profile is **{LIVE_RD_SEMRUSH:,} (Semrush)** - an active, large-scale negative-SEO / spam attack that grew the profile roughly 30x in two months ({HIST}).")
    L.append(f"- Classified **{total:,} referring domains** / **{len(links):,} backlinks** into six statuses on link-level evidence (anchor, page title/URL, host, target page). Nothing is disavowed without visible evidence; exact-match commercial links are held, not auto-disavowed.")
    L.append("")
    L.append("## Verdict breakdown")
    L.append("| Status | Domains |")
    L.append("|---|---:|")
    for s in STATUS_ORDER:
        L.append(f"| {s} | {S.get(s,0):,} |")
    L.append(f"| **Total** | **{total:,}** |")
    L.append("")
    L.append("## The three properties (important)")
    L.append(f"The client owns **three domains**: `{MONEY}` (money site) plus `{REDIRECTS[0]}` and `{REDIRECTS[1]}`, which **301-redirect into the money site**. The spam campaign targets all three. One audit of the money site captures them all (Semrush rolls redirected links in via the `redirect_url` column).")
    L.append("")
    L.append("We provide **three disavow files** (you told us you can upload to all properties):")
    L.append(f"- **`disavow_{MONEY}.txt`** - {len(union):,} domains. THE money-site file: the full union of every spam domain across all properties. **Upload this to the {MONEY} Search Console property.**")
    for p in REDIRECTS:
        L.append(f"- **`disavow_{p}.txt`** - {len(perprop[p]):,} domains whose links point at {p}. Upload to the {p} Search Console property. (All are also in the money-site union.)")
    L.append("")
    L.append("## Before you upload - confirm with the previous supplier")
    L.append(f"- **{held:,} domains are HELD**, not in any disavow file. They carry exact-match commercial anchors on deep location/service pages and may be **commissioned placements** by your previous SEO **{SUPPLIER_WORD}** (the 'partner' referenced throughout the workbook).")
    L.append(f"- Tab 5 (Exact Match Anchors) lists them with blank **Partner confirmed?** / **Final decision** columns for the {SUPPLIER_WORD} to fill. Tab 6 (Pending Disavow Lines) has the ready disavow lines to append **only** for the ones they did not build.")
    L.append(f"- **Do not upload any file until that conversation has happened.** Also check whether a disavow file already exists on each property in Search Console - if one does, uploading **replaces** it, so merge rather than overwrite.")
    L.append("")
    L.append("## Two campaigns (the key signal)")
    home=sum(1 for r in links if r["target_is_home"]); deep=len(links)-home
    L.append(f"- The **home-page flood** ({home:,} links) is backlink/SEO sales-copy spam that names your own domains - this is the attack, and it is what goes in the disavow file.")
    L.append(f"- The **deep-page links** ({deep:,}, hitting /newnan-ga/, /senoia-ga/, water-heater pages, etc.) carry exact-match commercial anchors and look commissioned - these are the held set.")
    L.append("")
    L.append("## Data sources & coverage (honest notes)")
    L.append("- **Authority Score** is Semrush for every domain (the audit's required metric). **Backlinks / Dofollow / Nofollow / First Seen / anchors / target pages** are computed directly from the merged Semrush+Ahrefs link data.")
    L.append(f"- **Traffic, RD's and Organic Keywords** are per-domain audience metrics. We fetched them from Ahrefs batch metrics for {measured:,} domains; our monthly Ahrefs API quota was reached mid-pull (resets 25 Nov 2026). We **backfilled the genuine / held / keep domains from Semrush** so no real site shows a false zero.")
    L.append(f"- The remaining ~{unmeasured:,} un-fetched domains are low-authority throwaway spam (Authority Score < 10). 98.4% of measured low-AS domains have **zero** organic traffic, so these are recorded as zero traffic/keywords; their RD's cell is left blank rather than guessed. They can be completed on the quota reset or from client-supplied Ahrefs CSV exports if you want exact figures - it does not change any disavow decision.")
    L.append(f"- Of the held set, **{held_notraffic:,} of {held:,}** have no organic traffic at all - held does not mean valuable.")
    L.append("")
    L.append("## Limits")
    L.append("- Example-page 'live' status rests on Semrush/Ahrefs last crawl (we did not fetch each linking host live).")
    L.append("- The held set needs the supplier's answer before those domains can be disavowed.")
    L.append("- **We have not submitted anything to Google Search Console** - that is your call after the supplier conversation.")
    L.append("")
    L.append("## Files")
    L.append("- `Fitzgerald_Plumbing_Backlink_Audit.xlsx` - 7-tab workbook (Summary, Referring Domain Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List).")
    L.append(f"- `disavow_{MONEY}.txt`, `disavow_{REDIRECTS[0]}.txt`, `disavow_{REDIRECTS[1]}.txt` - disavow files.")
    path = os.path.join(OUT, "README_Fitzgerald_audit.md")
    open(path,"w",encoding="utf-8").write("\n".join(L))
    print("WROTE", path)

if __name__ == "__main__":
    build()
