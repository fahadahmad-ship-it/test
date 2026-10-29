"""
build.py — produce the superkexpress.com backlink-audit workbook (7 tabs, signed
Harbinger format) and the disavow file. Run with python3 -I. Change the format here,
never by hand in Excel.

Single Search Console property (superkexpress.com); no owned/redirect domains, so one
disavow file. Held domains are EXCLUDED from the file pending the previous SEO partner's
confirmation of the exact-match commercial anchors.
"""
import os, sys, datetime, html
sys.path.insert(0, os.path.dirname(__file__))
import load, classify
import template_spec as T
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "out"))
REF = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "ref"))
CLIENT = "Super K Express"
MONEY = "superkexpress.com"
TODAY = datetime.date(2026, 10, 29)

# ---------- styling ----------
SIDE = Side(style="thin", color=T.BLACK)
BORDER_HEADER = Border(left=SIDE, right=SIDE, top=SIDE)        # header row: L/R/T, no bottom
BORDER_BOX = Border(left=SIDE, right=SIDE, top=SIDE, bottom=SIDE)
BORDER_NONE = Border()
FILL_ACCENT = PatternFill("solid", fgColor=T.ACCENT)
FILL_WHITE = PatternFill("solid", fgColor=T.WHITE)

F_TITLE   = Font(name=T.FONT, size=21, bold=True, color=T.ACCENT)
F_HEADER  = Font(name=T.FONT, size=9,  bold=True, color=T.WHITE)
F_DATA    = Font(name=T.FONT, size=9,  color=T.BLACK)
F_SECTION = Font(name=T.FONT, size=11, bold=True, color=T.ACCENT)
F_SUMHDR  = Font(name=T.FONT, size=10, bold=True, color=T.WHITE)
F_FIND    = Font(name=T.FONT, size=10, bold=True, color=T.BLACK)
F_INPUT   = Font(name=T.FONT, size=9,  color=T.WHITE)
F_DATA_B  = Font(name=T.FONT, size=9,  bold=True, color=T.BLACK)

AL_HEADER = Alignment(horizontal="center", vertical="center", wrap_text=True)
AL_DATA   = Alignment(vertical="center")
AL_DATA_W = Alignment(vertical="center", wrap_text=True)
AL_TITLE  = Alignment(horizontal="center", vertical="center")
AL_CTR    = Alignment(horizontal="center", vertical="center")

def ts_to_date(ts):
    if not ts:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).date()
    except Exception:
        return None

def idna(dom):
    try:
        return dom.encode("idna").decode("ascii")
    except Exception:
        return dom

def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = F_HEADER; cell.fill = FILL_ACCENT
        cell.border = BORDER_HEADER; cell.alignment = AL_HEADER
    ws.row_dimensions[row].height = T.HEADER_ROW_HEIGHT

def write_data_tab(wb, name, headers, rows, pct_cols=(), date_cols=(), int_cols=(),
                   header_nowrap_cols=(), pct_format="0.0%"):
    ws = wb.create_sheet(name)
    ncols = len(headers)
    for c, h in enumerate(headers, start=1):
        ws.cell(row=1, column=c, value=h)
    style_header_row(ws, 1, ncols)
    # template quirk: a few header cells on wide columns are not wrapped
    for c in header_nowrap_cols:
        ws.cell(row=1, column=c).alignment = Alignment(horizontal="center", vertical="center")
    h = T.DATA_ROW_HEIGHT[name]
    for i, row in enumerate(rows, start=2):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=i, column=c, value=row[c - 1])
            cell.font = F_DATA; cell.fill = FILL_WHITE
            cell.border = BORDER_NONE
            cell.alignment = AL_DATA
            if c in pct_cols:
                cell.number_format = pct_format
            elif c in date_cols:
                cell.number_format = "d mmm yyyy"
        ws.row_dimensions[i].height = h
    # widths
    for c, w in enumerate(T.COL_WIDTHS[name], start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    last = f"{get_column_letter(ncols)}{max(len(rows)+1,1)}"
    ws.auto_filter.ref = f"${'A'}$1:${get_column_letter(ncols)}${max(len(rows)+1,1)}"
    ws.freeze_panes = "B2"
    # gridlines on is the default (showGridLines stays None, as in the template)
    ws.sheet_format.defaultRowHeight = T.DEFAULT_ROW_HEIGHT
    ws.sheet_format.defaultColWidth = T.DEFAULT_COL_WIDTH
    return ws

# ---------- gather classified data ----------
def gather():
    data = classify.classify_all()
    doms = data["domains"]; cls = data["classification"]
    recs = []
    for dom, rec in doms.items():
        status = cls[dom]["status"]; evidence = cls[dom]["evidence"]
        links = rec["links"]
        # top anchor (non-empty)
        anchs = [l["anchor"] for l in links if (l["anchor"] or "").strip()]
        top_anchor = Counter(anchs).most_common(1)[0][0] if anchs else (links[0]["anchor"] if links else "")
        # example link: prefer a live (http 200) link, else first
        ex = None
        for l in links:
            if l.get("http_code") == 200:
                ex = l; break
        ex = ex or (links[0] if links else {})
        tool = "Semrush + Ahrefs" if len(rec["sources"]) > 1 and {"Semrush","Ahrefs"} <= set(rec["sources"]) else (rec["sources"][0] if rec["sources"] else "")
        # target host(s)
        tgt_hosts = sorted({load.canon_domain(load.host_of(t)) for t in rec["target_urls"] if t} or {MONEY})
        in_disavow = "Yes" if status == "Spam (Disavow)" else ("Held" if status.startswith("Held") else "No")
        disavow_line = f"domain:{idna(dom)}" if status == "Spam (Disavow)" else ""
        backlinks = rec["sr_backlinks"] if rec["sr_backlinks"] is not None else len(links)
        recs.append({
            "domain": dom, "status": status, "evidence": evidence,
            "as": rec["as"], "backlinks": backlinks, "rd": rec.get("ah_rd", 0),
            "traffic": rec.get("ah_traffic", 0), "positions": rec.get("ah_positions", 0),
            "in_disavow": in_disavow, "links_point_to": ", ".join(tgt_hosts),
            "dofollow": rec["dofollow_count"], "nofollow": rec["nofollow_count"],
            "first_seen": ts_to_date(rec["first_seen"]), "top_anchor": top_anchor,
            "example_page": ex.get("source_url", ""), "example_title": ex.get("source_title", ""),
            "tool": tool, "ip": rec.get("ip", "") or "", "disavow_line": disavow_line,
            "links": links,
        })
    recs.sort(key=lambda r: r["domain"])
    data["recs"] = recs
    return data

# ---------- build workbook ----------
def build():
    data = gather()
    recs = data["recs"]
    by_status = defaultdict(list)
    for r in recs:
        by_status[r["status"]].append(r)
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # ---- Tab 1: Summary (built last for ordering, but create placeholder first) ----
    ws_sum = wb.create_sheet("Summary")

    # ---- Tab 2: Referring Domain Audit ----
    rda_rows = []
    for r in recs:
        rda_rows.append([
            r["domain"], r["status"], (r["as"] if r["as"] is not None else ""),
            r["backlinks"], (r["rd"] or ""), (r["traffic"] or 0), r["in_disavow"],
            r["links_point_to"], r["dofollow"], r["nofollow"], r["first_seen"],
            r["top_anchor"], r["example_page"], r["example_title"], r["tool"], r["ip"],
            r["disavow_line"],
        ])
    write_data_tab(wb, "Referring Domain Audit", T.HEADERS["Referring Domain Audit"],
                   rda_rows, date_cols=(11,))

    # ---- Tab 3: All Backlinks (one row per link; dedup) ----
    cls = data["classification"]
    seen = set(); bl_rows = []
    for r in recs:
        for l in r["links"]:
            key = (r["domain"], l.get("anchor",""), l.get("target_url",""), l.get("source_url",""))
            if key in seen:
                continue
            seen.add(key)
            at = classify.anchor_type(l.get("anchor",""), l.get("source_title",""))
            lt = "Nofollow" if l.get("nofollow") else "Dofollow"
            bl_rows.append([
                r["domain"], r["status"], l.get("tool",""), l.get("anchor",""), at, lt,
                l.get("source_url",""), l.get("source_title",""), l.get("target_url",""),
            ])
    bl_rows.sort(key=lambda x: (x[0], x[3]))
    write_data_tab(wb, "All Backlinks", T.HEADERS["All Backlinks"], bl_rows)

    # ---- Tab 4: Anchor Analysis ----
    # Authoritative anchor distribution from Semrush backlinks_anchors (backlinks_num,
    # domains_num). Link-level pulls undercount the dominant anchors, so the counts here
    # are Semrush's, never the sample. "Spam Domains Using It" = domains_num for a spam-type
    # anchor (any domain using a spam anchor is spam), else spam domains observed using it.
    sem_anchors = data["anchors"]
    total_anchor_bl = sum(a["backlinks_num"] for a in sem_anchors) or 1
    obs_spam_by_anchor = defaultdict(set)
    for r in recs:
        if r["status"].startswith("Spam"):
            for l in r["links"]:
                obs_spam_by_anchor[(l.get("anchor","") or "")].add(r["domain"])
    an_rows = []
    for a in sem_anchors:
        anchor = a["anchor"]; at = classify.anchor_type(anchor)
        spam_dom = a["domains_num"] if at in classify.SPAM_ANCHOR_TYPES else len(obs_spam_by_anchor.get(anchor, ()))
        an_rows.append([anchor if anchor else "<EmptyAnchor>", at, a["backlinks_num"],
                        a["backlinks_num"]/total_anchor_bl, a["domains_num"], spam_dom])
    an_rows.sort(key=lambda x: -x[2])
    write_data_tab(wb, "Anchor Analysis", T.HEADERS["Anchor Analysis"], an_rows, pct_cols=(4,),
                   header_nowrap_cols=(1,), pct_format="0.00%")

    # ---- Tab 5: Exact Match Anchors ----
    em_rows = []
    for r in recs:
        exact_links = [l for l in r["links"]
                       if classify.anchor_type(l.get("anchor","")) in classify.EXACT_TYPES]
        if not exact_links:
            continue
        # one row per (domain, distinct exact anchor)
        by_anchor = defaultdict(list)
        for l in exact_links:
            by_anchor[l.get("anchor","")].append(l)
        for anchor, lks in by_anchor.items():
            ex = next((l for l in lks if l.get("http_code") == 200), lks[0])
            em_rows.append([
                r["domain"], ex.get("source_url",""), anchor,
                classify.market_of(anchor, lks),
                classify.site_type(r["domain"], {"as": r["as"]}),
                "", "",   # Partner confirmed? / Final decision -> partner input cells
            ])
    em_rows.sort(key=lambda x: (x[0], x[2]))
    ws_em = write_data_tab(wb, "Exact Match Anchors", T.HEADERS["Exact Match Anchors"], em_rows)
    # partner input cells (cols F,G) get accent fill + white font
    for i in range(2, len(em_rows) + 2):
        for c in (6, 7):
            cell = ws_em.cell(row=i, column=c)
            cell.fill = FILL_ACCENT; cell.font = F_INPUT

    # ---- Tab 6: Pending Disavow Lines (held domains awaiting a decision) ----
    pend_rows = []
    for r in recs:
        if r["status"].startswith("Held"):
            rec_note = ("Append to disavow.txt only if the partner does NOT confirm "
                        "commissioning this placement.")
            pend_rows.append([r["domain"], f"domain:{idna(r['domain'])}", rec_note])
    pend_rows.sort(key=lambda x: x[0])
    write_data_tab(wb, "Pending Disavow Lines", T.HEADERS["Pending Disavow Lines"], pend_rows)

    # ---- Tab 7: Disavow List (Spam (Disavow) only) ----
    dl_rows = []
    disavow_domains = []
    for r in recs:
        if r["status"] != "Spam (Disavow)":
            continue
        disavow_domains.append(r)
        dl_rows.append([
            f"domain:{idna(r['domain'])}", (r["as"] if r["as"] is not None else ""),
            r["backlinks"], (r["rd"] or ""), (r["traffic"] or 0), (r["positions"] or 0),
            r["top_anchor"],
        ])
    dl_rows.sort(key=lambda x: x[0])
    write_data_tab(wb, "Disavow List", T.HEADERS["Disavow List"], dl_rows)

    # ---- Summary content ----
    build_summary(ws_sum, recs, by_status, data)

    # reorder sheets to the signed order
    wb._sheets.sort(key=lambda s: T.SHEETS.index(s.title))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "SuperKExpress_Backlinks_Audit.xlsx")
    wb.save(path)

    # ---- disavow file ----
    write_disavow(disavow_domains, recs)
    return data, path, disavow_domains

def build_summary(ws, recs, by_status, data):
    ws.sheet_view.showGridLines = False
    # widths + logo
    for c, w in enumerate(T.COL_WIDTHS["Summary"], start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    img = XLImage(os.path.join(REF, "harbinger_logo.png"))
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
    from openpyxl.drawing.xdr import XDRPositiveSize2D
    img.anchor = OneCellAnchor(
        _from=AnchorMarker(col=T.LOGO_FROM_COL, colOff=T.LOGO_FROM_COLOFF,
                           row=T.LOGO_FROM_ROW, rowOff=T.LOGO_FROM_ROWOFF),
        ext=XDRPositiveSize2D(cx=T.LOGO_EXT_CX, cy=T.LOGO_EXT_CY))
    ws.add_image(img)
    # title
    ws.merge_cells("B1:E2")
    t = ws["B1"]; t.value = CLIENT; t.font = F_TITLE; t.alignment = AL_TITLE
    for rr in range(1, 29):
        ws.row_dimensions[rr].height = T.SUMMARY_ROW_HEIGHT

    total_dom = len(recs)
    total_bl = sum(r["backlinks"] for r in recs)
    status_order = ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
                    "Spam (Nofollow, No Action)", "Keep", "Own Site"]
    meanings = {
        "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
        "Held (Pending Partner)": "Exact-match commercial anchor, or a link aimed at a deep money page. May be commissioned; excluded from the file until the previous SEO partner confirms.",
        "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value; no decision needed.",
        "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value; left out of the file.",
        "Keep": "Genuine or harmless link. Keep.",
        "Own Site": "Client-owned domain that redirects into the site.",
    }
    # status table header row 3
    hdr = ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"]
    for c, h in enumerate(hdr, start=1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font = F_SUMHDR; cell.fill = FILL_ACCENT; cell.border = BORDER_BOX; cell.alignment = AL_HEADER
    row = 4
    for s in status_order:
        rs = by_status.get(s, [])
        dom_n = len(rs); bl_n = sum(r["backlinks"] for r in rs)
        vals = [s, dom_n, bl_n, (dom_n/total_dom if total_dom else 0), meanings[s]]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.font = F_DATA; cell.fill = FILL_WHITE; cell.border = BORDER_BOX
            cell.alignment = AL_DATA_W if c == 5 else AL_DATA
            if c == 4:
                cell.number_format = T.FMT_PCT
        row += 1
    # total row
    tot = ["Total", total_dom, total_bl, 1.0, ""]
    for c, v in enumerate(tot, start=1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.font = F_DATA_B; cell.fill = FILL_WHITE; cell.border = BORDER_BOX; cell.alignment = AL_DATA
        if c == 4:
            cell.number_format = T.FMT_PCT
    total_row = row
    # key findings
    kf_head_row = total_row + 1
    ws.cell(row=kf_head_row, column=1, value="Key findings").font = F_SECTION
    findings = key_findings(recs, by_status, data, total_dom, total_bl)
    r = kf_head_row + 1
    for f in findings:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        cell = ws.cell(row=r, column=1, value=f)
        cell.font = F_DATA; cell.alignment = Alignment(vertical="center", wrap_text=True)
        r += 1
    # anchor profile table
    ap_head_row = r
    ws.cell(row=ap_head_row, column=1, value="Anchor text profile (all backlinks)").font = F_SECTION
    aph = ["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"]
    hr = ap_head_row + 1
    for c, h in enumerate(aph, start=1):
        cell = ws.cell(row=hr, column=c, value=h)
        cell.font = F_SUMHDR; cell.fill = FILL_ACCENT; cell.border = BORDER_BOX; cell.alignment = AL_HEADER
    # aggregate anchor types: backlinks from Semrush (authoritative), referring domains as
    # distinct domains observed using that anchor type (avoids double-counting across anchors)
    type_bl = Counter()
    for a in data["anchors"]:
        type_bl[classify.anchor_type(a["anchor"])] += a["backlinks_num"]
    type_dom = defaultdict(set)
    for rec in recs:
        for l in rec["links"]:
            type_dom[classify.anchor_type(l.get("anchor",""))].add(rec["domain"])
    tot_bl = sum(type_bl.values()) or 1
    rr = hr + 1
    for at, n in type_bl.most_common():
        vals = [at, n, n/tot_bl, len(type_dom[at])]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=rr, column=c, value=v)
            cell.font = F_DATA; cell.fill = FILL_WHITE; cell.border = BORDER_BOX; cell.alignment = AL_DATA
            if c == 3:
                cell.number_format = T.FMT_PCT
        rr += 1

def key_findings(recs, by_status, data, total_dom, total_bl):
    spam_dis = by_status.get("Spam (Disavow)", [])
    spam_nf = by_status.get("Spam (Nofollow, No Action)", [])
    held = by_status.get("Held (Pending Partner)", []) + by_status.get("Held (Nofollow, No Action)", [])
    keep = by_status.get("Keep", [])
    spam_total = len(spam_dis) + len(spam_nf)
    # gambling
    gamb = [r for r in recs if any(classify.anchor_type(l.get("anchor","")) == "Spam: off topic" for l in r["links"])]
    gamb_bl = sum(r["backlinks"] for r in gamb)
    bisicon_bl = next((r["backlinks"] for r in recs if r["domain"] == "bisicon.com"), 0)
    # history growth
    hist = data["history"]
    growth = ""
    def fmt_month(d):
        try:
            return datetime.datetime.fromtimestamp(int(float(d)), datetime.timezone.utc).strftime("%b %Y")
        except Exception:
            return str(d)
    if hist:
        try:
            nums = [(int(float(h["date"])), int(float(h["domains_num"]))) for h in hist
                    if h.get("domains_num") and h.get("date")]
            nums_sorted = sorted(nums, key=lambda x: x[0])
            if len(nums_sorted) >= 2:
                first, last = nums_sorted[0], nums_sorted[-1]
                growth = (f"The referring-domain count has grown from {first[1]:,} ({fmt_month(first[0])}) to "
                          f"{last[1]:,} ({fmt_month(last[0])}) in Semrush's history — an active, still-growing attack.")
        except Exception:
            growth = ""
    held_no_traffic = sum(1 for r in held if (r["traffic"] or 0) == 0)
    # dominant sales-copy anchor
    sc = Counter()
    for r in recs:
        for l in r["links"]:
            if classify.anchor_type(l.get("anchor","")) == "Spam: keyword stuffed SEO sales copy":
                sc[(l.get("anchor","") or "").strip()[:60]] += 1
    dom_anchor = sc.most_common(1)[0] if sc else ("", 0)
    findings = [
        f"{spam_total:,} of {total_dom:,} referring domains are spam ({len(spam_dis):,} with at least one "
        f"dofollow link go in the disavow file; {len(spam_nf):,} are nofollow-only and pass no value).",
        growth or "Semrush shows a large, recently-built spam link profile against the site.",
        "The client can upload a disavow file for superkexpress.com only. There are no owned/redirect "
        "domains, so this is a single file covering the whole property.",
        "Two campaigns, easy to tell apart. The link-scheme flood (gambling injection + SEO sales-copy PBN) "
        "points at the home page and /resources/; the commissioned-looking exact-match trucking anchors point "
        "at deep /services/ and /locations/ pages.",
        f"One domain, bisicon.com, accounts for {bisicon_bl:,} of the links on its own; the full \"jogjatoto\" "
        f"gambling injection spans {len(gamb)} domains and {gamb_bl:,} links aimed at /resources/ (off-topic spam).",
        f"The biggest sales-copy anchor, on {dom_anchor[1]:,} links, is \"{dom_anchor[0]}…\" — the keyword-stuffed "
        f"PBN template that defines the link blast.",
        f"{len(held):,} domains are held for the previous SEO partner to confirm; held does not mean valuable — "
        f"{held_no_traffic:,} of them have no organic traffic at all.",
    ]
    return findings[:7]

def write_disavow(disavow_domains, recs):
    # group by reason
    groups = defaultdict(list)
    def group_of(r):
        ev = r["evidence"]
        if "off-topic" in ev or "gambling" in ev:
            return "Gambling link injection (off-topic spam)"
        if "SEO sales-copy" in ev or "PBN" in ev:
            return "PBN / keyword-stuffed SEO sales-copy link blast"
        if "host-name" in ev:
            return "Spam directory / bookmark / SEO-tool host"
        if "title" in ev or "URL" in ev:
            return "Spam linking-page title or URL template"
        return "Other confirmed spam (visible evidence)"
    for r in disavow_domains:
        groups[group_of(r)].append(idna(r["domain"]))
    n = len(disavow_domains)
    held_n = sum(1 for r in recs if r["status"].startswith("Held"))
    lines = []
    lines.append(f"# Google disavow file — {MONEY}")
    lines.append(f"# Generated {TODAY.isoformat()} for {CLIENT}.")
    lines.append(f"# {n} referring domains, grouped by reason below.")
    lines.append("#")
    lines.append("# PROPERTY: this file applies to the superkexpress.com Search Console property only.")
    lines.append("#   There are no owned/redirect domains, so this single file covers the whole site.")
    lines.append("# DO NOT UPLOAD before the previous SEO partner has confirmed the exact-match commercial")
    lines.append(f"#   anchors: {held_n} 'held' domains are EXCLUDED from this file pending that conversation,")
    lines.append("#   because they may be placements the client paid for. Disavowing a paid link hurts the site.")
    lines.append("# Uploading a disavow file REPLACES any file currently on the property. Confirm with the")
    lines.append("#   client whether a disavow file already exists before uploading; if one does, this replaces it.")
    lines.append("# Every line below rests on visible evidence (spam anchor, spam linking-page title, or spam host).")
    lines.append("# Metrics shown in the workbook: Authority Score / backlinks / referring-domain counts are")
    lines.append("#   Semrush; Traffic / Organic Keywords / RD's are Ahrefs (Semrush exposes no bulk per-domain")
    lines.append("#   metric via the available API). Do not submit anything to Google yourself.")
    lines.append("")
    for g in sorted(groups):
        lines.append(f"# --- {g} ({len(groups[g])}) ---")
        for d in sorted(set(groups[g])):
            lines.append(f"domain:{d}")
        lines.append("")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "disavow_superkexpress.com.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    data, path, disavow = build()
    print("Workbook:", path)
    print("Disavow domains:", len(disavow))
    from collections import Counter as C
    c = C(r["status"] for r in data["recs"])
    for s in ["Spam (Disavow)","Spam (Nofollow, No Action)","Held (Pending Partner)",
              "Held (Nofollow, No Action)","Keep","Own Site"]:
        print(f"  {s:32s} {c.get(s,0)}")
    print("  TOTAL", sum(c.values()))
