"""
Workbook + disavow builder for the southerntreega.com audit.

Produces the seven-tab workbook in the signed-off Harbinger format (cell-for-cell
against the K&K template) plus disavow.txt. Change the format HERE, never by hand
in Excel.

Run (after the data pulls have landed):
    python3 -I southerntree/scripts/build.py

Styling comes from the signed template:
  Font Geist throughout; accent FF0C343D. Header rows Geist 9 bold white on accent,
  centred, wrapped, height 31.5, border L/R/T (no bottom). Data rows Geist 9 black on
  white, vertically centred, NO cell borders (sheet gridlines carry the grid),
  height 22.5 (Referring Domain Audit 15.75). Freeze B2, autofilter full range,
  gridlines on. Summary: gridlines off, its own small tables fully bordered, title
  Geist 21 bold accent merged B1:E2, logo top-left.
"""

import os
import sys
import glob
import datetime
from collections import Counter, defaultdict

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load as L
import classify as C

ROOT = "/home/user/test/southerntree"
OUT_XLSX = f"{ROOT}/out/Southern_Tree_Solutions_Backlinks_Audit.xlsx"
LOGO = f"{ROOT}/data/harbinger_logo.png"

CLIENT_NAME = "Southern Tree Solutions"
CLIENT_DOMAIN = "southerntreega.com"
PARTNER_WORD = "previous SEO partner"      # brief said "Harbinger"; see file header note
DISAVOW_FILE = "disavow_southerntreega.txt"

ACCENT = "FF0C343D"
WHITE = "FFFFFFFF"
BLACK = "FF000000"

# ---- styles -------------------------------------------------------------
f_header = Font(name="Geist", size=9, bold=True, color=WHITE)
f_data = Font(name="Geist", size=9, color=BLACK)
f_data_b = Font(name="Geist", size=9, bold=True, color=BLACK)
f_title = Font(name="Geist", size=21, bold=True, color=ACCENT)
f_sum_hdr = Font(name="Geist", size=10, bold=True, color=WHITE)
f_sum_find_hdr = Font(name="Geist", size=10, bold=True, color=BLACK)
f_sec = Font(name="Geist", size=11, bold=True, color=ACCENT)
fill_accent = PatternFill("solid", fgColor=ACCENT)
fill_white = PatternFill("solid", fgColor=WHITE)
thin = Side(style="thin")
bd_header = Border(left=thin, right=thin, top=thin)          # no bottom (data tabs)
bd_full = Border(left=thin, right=thin, top=thin, bottom=thin)
al_hdr = Alignment(horizontal="center", vertical="center", wrap_text=True)
al_c = Alignment(horizontal="center", vertical="center")
al_l = Alignment(vertical="center")


def header_row(ws, row, labels, borders=True):
    for i, lab in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = f_header
        c.fill = fill_accent
        c.alignment = al_hdr
        if borders:
            c.border = bd_header
    ws.row_dimensions[row].height = 31.5


def data_cell(ws, row, col, value, align="l", numfmt=None, bold=False, border=None, fill=True):
    c = ws.cell(row=row, column=col, value=value)
    c.font = f_data_b if bold else f_data
    if fill:
        c.fill = fill_white
    c.alignment = al_c if align == "c" else al_l
    if numfmt:
        c.number_format = numfmt
    if border:
        c.border = border
    return c


def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def finalize_data_tab(ws, nrows, ncols, row_height):
    last = get_column_letter(ncols)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{last}{nrows}"
    ws.sheet_view.showGridLines = True
    for r in range(2, nrows + 1):
        ws.row_dimensions[r].height = row_height


def to_date(ts):
    try:
        ts = int(float(ts))
        if ts > 10_000_000:
            return datetime.datetime.utcfromtimestamp(ts).date()
    except Exception:
        pass
    # ISO datetime (Ahrefs)
    try:
        return datetime.datetime.fromisoformat(str(ts).replace("Z", "")).date()
    except Exception:
        return None


# =====================================================================
#  Aggregation + classification
# =====================================================================
def build_domains(merged_links, refmeta):
    by_dom = defaultdict(list)
    for l in merged_links:
        by_dom[l["refdomain"]].append(l)

    domains = {}
    for dom, links in by_dom.items():
        for l in links:
            l["anchor_type"] = C.classify_anchor(l["anchor"], l.get("target_url", ""))
            l["is_pr"] = any(sig in l["source_host"] for sig in C.PR_SIGNATURES)
        any_do = any(l["is_dofollow"] for l in links)
        meta = refmeta.get(dom, {})
        as_score = meta.get("dr")
        if as_score is None:
            drs = [float(l["dr"]) for l in links if l.get("dr") not in (None, "")]
            as_score = max(drs) if drs else None
        agg = {
            "domain": dom,
            "owned": dom in C.OWNED_DOMAINS,
            "as_score": as_score,
            "links": links,
            "any_dofollow": any_do,
        }
        status, reason = C.classify_domain(agg)
        dofollow = sum(1 for l in links if l["is_dofollow"])
        nofollow = len(links) - dofollow
        anchors = Counter(l["anchor"] for l in links if l["anchor"].strip())
        top_anchor = anchors.most_common(1)[0][0] if anchors else ""
        # example linking page: prefer a live (200) dofollow page carrying the top anchor
        example = sorted(links, key=lambda l: (
            0 if str(l.get("response_code")) in ("200", "") else 1,
            0 if l["is_dofollow"] else 1,
            0 if l["anchor"] == top_anchor else 1,
        ))[0]
        points_to = sorted({(l.get("redirect_url") and L.host_of(l["redirect_url"])) or l["target_host"]
                             for l in links if l["target_host"]})
        first_seens = [to_date(l["first_seen"]) for l in links if to_date(l["first_seen"])]
        fs_meta = to_date(meta.get("first_seen")) if meta.get("first_seen") else None
        first_seen = min([d for d in first_seens + [fs_meta] if d], default=None)
        tool_set = {l["tool"] for l in links}
        source = "Both" if ("Both" in tool_set or {"Semrush", "Ahrefs"} <= tool_set) else tool_set.pop()
        domains[dom] = {
            "domain": dom, "status": status, "reason": reason,
            "as": as_score, "backlinks": meta.get("links_to_target", len(links)),
            "rds": meta.get("rds", ""), "traffic": meta.get("traffic", 0),
            "dofollow": dofollow, "nofollow": nofollow,
            "points_to": ", ".join(points_to) if points_to else CLIENT_DOMAIN,
            "first_seen": first_seen, "top_anchor": top_anchor,
            "example_page": example["source_url"], "example_title": example["source_title"],
            "source": source, "ip": meta.get("ip") or next((l.get("ip") for l in links if l.get("ip")), ""),
            "links": links,
        }
    return domains


# =====================================================================
#  Tab builders
# =====================================================================
STATUS_ORDER = ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
                "Spam (Nofollow, No Action)", "Keep", "Own Site"]
ANCHOR_ORDER = ["Spam: keyword stuffed SEO sales copy", "Spam: off topic", "Naked URL",
                "Exact match commercial", "Exact match commercial (geo)", "Generic",
                "Branded", "Empty or image", "Contextual or other"]


def in_disavow_value(status, redundant):
    if redundant:
        return "Covered by parent"
    if status == "Spam (Disavow)":
        return "Yes"
    if status.startswith("Held"):
        return "Held"
    return "No"


def build_referring_domain_audit(wb, domains, redundant_set):
    ws = wb.create_sheet("Referring Domain Audit")
    headers = ["Domain", "Status", "AS", "Backlinks", "RD's", "Traffic", "In Disavow",
               "Links Point To", "Dofollow Links", "Nofollow Links", "First Seen",
               "Top Anchor Text", "Example Linking Page", "Linking Page Title", "Source",
               "IP", "Disavow Line"]
    header_row(ws, 1, headers)
    rows = sorted(domains.values(), key=lambda d: (STATUS_ORDER.index(d["status"]) if d["status"] in STATUS_ORDER else 9, d["domain"]))
    r = 2
    for d in rows:
        redundant = d["domain"] in redundant_set
        disavow_line = f"domain:{d['domain']}" if d["status"] == "Spam (Disavow)" and not redundant else ""
        data_cell(ws, r, 1, d["domain"], "l")
        data_cell(ws, r, 2, d["status"], "l")
        data_cell(ws, r, 3, (f"{d['as']:g}" if d["as"] is not None else ""), "c")
        data_cell(ws, r, 4, d["backlinks"], "c", "#,##0")
        data_cell(ws, r, 5, (d["rds"] if d["rds"] != "" else None), "c", "#,##0")
        data_cell(ws, r, 6, d["traffic"], "c", "#,##0")
        data_cell(ws, r, 7, in_disavow_value(d["status"], redundant), "c")
        data_cell(ws, r, 8, d["points_to"], "l")
        data_cell(ws, r, 9, d["dofollow"], "c")
        data_cell(ws, r, 10, d["nofollow"], "c")
        data_cell(ws, r, 11, d["first_seen"], "c", "d mmm yyyy")
        data_cell(ws, r, 12, d["top_anchor"], "l")
        data_cell(ws, r, 13, d["example_page"], "l")
        data_cell(ws, r, 14, d["example_title"], "l")
        data_cell(ws, r, 15, d["source"], "c")
        data_cell(ws, r, 16, d["ip"], "c")
        data_cell(ws, r, 17, disavow_line, "l")
        r += 1
    set_widths(ws, {"A": 36, "B": 24.71, "C": 9.57, "D": 13, "E": 9.43, "F": 9.71,
                    "G": 12.43, "H": 21.29, "I": 14, "J": 8.71, "K": 12, "L": 45,
                    "M": 8.71, "N": 40, "O": 14, "P": 15, "Q": 14})
    finalize_data_tab(ws, r - 1, 17, 15.75)
    return ws


def build_all_backlinks(wb, domains):
    ws = wb.create_sheet("All Backlinks")
    headers = ["Referring Domain", "Status", "Tool", "Anchor Text", "Anchor Type",
               "Link Type", "Linking Page URL", "Linking Page Title", "Target URL"]
    header_row(ws, 1, headers)
    ws.cell(row=1, column=3).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    r = 2
    ordered = sorted(domains.values(), key=lambda d: (STATUS_ORDER.index(d["status"]) if d["status"] in STATUS_ORDER else 9, d["domain"]))
    for d in ordered:
        for l in sorted(d["links"], key=lambda x: x["anchor"]):
            data_cell(ws, r, 1, d["domain"], "l")
            data_cell(ws, r, 2, d["status"], "l")
            data_cell(ws, r, 3, l["tool"], "l")
            data_cell(ws, r, 4, l["anchor"], "l")
            data_cell(ws, r, 5, l["anchor_type"], "l")
            data_cell(ws, r, 6, "Dofollow" if l["is_dofollow"] else "Nofollow", "c")
            data_cell(ws, r, 7, l["source_url"], "l")
            data_cell(ws, r, 8, l["source_title"], "l")
            data_cell(ws, r, 9, l.get("redirect_url") or l["target_url"], "l")
            r += 1
    for col in (3,):
        for rr in range(2, r):
            ws.cell(row=rr, column=col).alignment = Alignment(horizontal="left", vertical="center")
    set_widths(ws, {"A": 25.43, "B": 27.14, "C": 14.71, "D": 55, "E": 32, "F": 10,
                    "G": 55, "H": 53.14, "I": 30.57})
    finalize_data_tab(ws, r - 1, 9, 22.5)
    return ws, r - 2


def build_anchor_analysis(wb, merged_links, domains):
    ws = wb.create_sheet("Anchor Analysis")
    headers = ["Anchor Text", "Anchor Type", "Backlinks", "Share of Backlinks",
               "Referring Domains", "Spam Domains Using It"]
    header_row(ws, 1, headers)
    ws.cell(row=1, column=1).alignment = Alignment(horizontal="center", vertical="center")
    dom_status = {d["domain"]: d["status"] for d in domains.values()}
    byanchor = defaultdict(lambda: {"bl": 0, "doms": set(), "spam": set(), "type": ""})
    total = len(merged_links)
    for l in merged_links:
        a = l["anchor"]
        e = byanchor[a]
        e["bl"] += 1
        e["doms"].add(l["refdomain"])
        e["type"] = l["anchor_type"]
        if dom_status.get(l["refdomain"], "").startswith("Spam"):
            e["spam"].add(l["refdomain"])
    rows = sorted(byanchor.items(), key=lambda kv: -kv[1]["bl"])
    r = 2
    for anchor, e in rows:
        data_cell(ws, r, 1, anchor, "l")
        data_cell(ws, r, 2, e["type"], "l")
        data_cell(ws, r, 3, e["bl"], "c", "#,##0")
        data_cell(ws, r, 4, (e["bl"] / total if total else 0), "c", "0.00%")
        data_cell(ws, r, 5, len(e["doms"]), "c", "#,##0")
        data_cell(ws, r, 6, len(e["spam"]), "c", "#,##0")
        r += 1
    set_widths(ws, {"A": 115.86, "B": 37.71, "C": 14, "D": 8.71, "E": 16, "F": 20.29})
    finalize_data_tab(ws, r - 1, 6, 22.5)
    return ws


def build_exact_match(wb, domains):
    ws = wb.create_sheet("Exact Match Anchors")
    headers = ["Referring domain", "Example backlink (linking page)", "Exact-match commercial anchor",
               "Market", "Site type (indicative)", "Partner confirmed? (Y/N)", "Final decision"]
    header_row(ws, 1, headers)
    r = 2
    rows = [d for d in domains.values()
            if any(C.is_exact_commercial_type(l["anchor_type"]) for l in d["links"])]
    rows.sort(key=lambda d: d["domain"])
    for d in rows:
        exlink = next((l for l in d["links"] if C.is_exact_commercial_type(l["anchor_type"])), d["links"][0])
        anchor = exlink["anchor"]
        market = "Georgia" if C._has_geo(anchor.lower()) else "Non-geo"
        site_type = C.site_type_for(d["domain"], exlink["source_title"], exlink["anchor_type"])
        data_cell(ws, r, 1, d["domain"], "l")
        data_cell(ws, r, 2, exlink["source_url"], "l")
        data_cell(ws, r, 3, anchor, "c")
        data_cell(ws, r, 4, market, "c")
        data_cell(ws, r, 5, site_type, "l")
        # F,G are partner input cells: accent fill, white font (per AUDIT_FORMAT)
        for col in (6, 7):
            c = ws.cell(row=r, column=col, value=None)
            c.font = Font(name="Geist", size=9, color=WHITE)
            c.fill = fill_accent
            c.alignment = al_c
        r += 1
    set_widths(ws, {"A": 25.43, "B": 59, "C": 53.14, "D": 16, "E": 24.57, "F": 15.43, "G": 15})
    finalize_data_tab(ws, r - 1, 7, 22.5)
    return ws, r - 2


def build_pending_disavow(wb, domains):
    ws = wb.create_sheet("Pending Disavow Lines")
    headers = ["Referring domain", "Disavow line (append to disavow.txt once confirmed)", "Recommendation"]
    header_row(ws, 1, headers)
    r = 2
    held = sorted([d for d in domains.values() if d["status"].startswith("Held")], key=lambda d: d["domain"])
    rec = f"Append only if the {PARTNER_WORD} does not claim it, to {DISAVOW_FILE}"
    for d in held:
        data_cell(ws, r, 1, d["domain"], "l")
        data_cell(ws, r, 2, f"domain:{d['domain']}", "l")
        data_cell(ws, r, 3, rec, "l")
        r += 1
    set_widths(ws, {"A": 32, "B": 44, "C": 48})
    finalize_data_tab(ws, r - 1, 3, 22.5)
    return ws, r - 2


def build_disavow_list(wb, domains, redundant_set):
    ws = wb.create_sheet("Disavow List")
    headers = ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic", "Organic Keywords", "Top Anchor Text"]
    header_row(ws, 1, headers)
    r = 2
    dis = sorted([d for d in domains.values()
                  if d["status"] == "Spam (Disavow)" and d["domain"] not in redundant_set],
                 key=lambda d: d["domain"])
    for d in dis:
        data_cell(ws, r, 1, f"domain:{d['domain']}", "l")
        data_cell(ws, r, 2, (f"{d['as']:g}" if d["as"] is not None else ""), "c")
        data_cell(ws, r, 3, d["backlinks"], "c", "#,##0")
        data_cell(ws, r, 4, (d["rds"] if d["rds"] != "" else None), "c", "#,##0")
        data_cell(ws, r, 5, d["traffic"], "c", "#,##0")
        data_cell(ws, r, 6, d.get("organic_keywords", ""), "c", "#,##0")
        data_cell(ws, r, 7, d["top_anchor"], "l")
        r += 1
    set_widths(ws, {"A": 44, "B": 14, "C": 15.57, "D": 14, "E": 11.14, "F": 14.86, "G": 98.86})
    finalize_data_tab(ws, r - 1, 7, 22.5)
    return ws, dis


STATUS_MEANING = {
    "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
    "Held (Pending Partner)": "Exact-match commercial anchor, or a link aimed at a deep service/location page. May have been commissioned. Not in the disavow file until the previous SEO partner confirms.",
    "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed.",
    "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
    "Keep": "Genuine or harmless link. Keep.",
    "Own Site": "Client-owned domain that redirects into the site.",
}


def build_summary(wb, domains, merged_links, redundant_set, findings):
    ws = wb.create_sheet("Summary", 0)
    ws.sheet_view.showGridLines = False
    # title
    ws.merge_cells("B1:E2")
    t = ws.cell(row=1, column=2, value=CLIENT_NAME)
    t.font = f_title
    t.alignment = al_c
    # logo
    try:
        img = XLImage(LOGO)
        from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
        from openpyxl.drawing.xdr import XDRPositiveSize2D
        img.anchor = OneCellAnchor(_from=AnchorMarker(col=0, colOff=381000, row=0, rowOff=0),
                                   ext=XDRPositiveSize2D(cx=1866900, cy=552450))
        ws.add_image(img)
    except Exception as e:
        print("logo skipped:", e)

    # status table (rows 3-9) + total (row 10)
    hdr = ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(row=3, column=i, value=h)
        c.font = f_sum_hdr; c.fill = fill_accent; c.alignment = al_hdr; c.border = bd_full
    dom_by_status = Counter(d["status"] for d in domains.values())
    bl_by_status = Counter()
    for d in domains.values():
        bl_by_status[d["status"]] += len(d["links"])
    total_dom = sum(dom_by_status.values()) or 1
    r = 4
    for st in STATUS_ORDER:
        nd = dom_by_status.get(st, 0)
        nb = bl_by_status.get(st, 0)
        ws.cell(row=r, column=1, value=st)
        ws.cell(row=r, column=2, value=nd).number_format = "#,##0"
        ws.cell(row=r, column=3, value=nb).number_format = "#,##0"
        sc = ws.cell(row=r, column=4, value=nd / total_dom); sc.number_format = "0.0%"
        ws.cell(row=r, column=5, value=STATUS_MEANING[st])
        for cidx in range(1, 6):
            c = ws.cell(row=r, column=cidx)
            c.font = f_data; c.fill = fill_white; c.border = bd_full
            c.alignment = al_c if cidx in (2, 3, 4) else al_l
        r += 1
    # total row
    tot_bl = sum(bl_by_status.values())
    ws.cell(row=r, column=1, value="Total")
    ws.cell(row=r, column=2, value=total_dom).number_format = "#,##0"
    ws.cell(row=r, column=3, value=tot_bl).number_format = "#,##0"
    ws.cell(row=r, column=4, value=1.0).number_format = "0.0%"
    for cidx in range(1, 5):
        c = ws.cell(row=r, column=cidx)
        c.font = f_data_b; c.fill = fill_white; c.border = bd_full
        c.alignment = al_c if cidx in (2, 3, 4) else al_l
    r += 1

    # key findings
    kf_row = r
    kh = ws.cell(row=kf_row, column=1, value="Key findings"); kh.font = f_sum_find_hdr
    r = kf_row + 1
    for text in findings:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        c = ws.cell(row=r, column=1, value=text); c.font = f_data
        c.alignment = Alignment(vertical="center", wrap_text=False)
        r += 1

    # anchor-type profile table
    sec = ws.cell(row=r, column=1, value="Anchor text profile (all backlinks)"); sec.font = f_sec
    r += 1
    for i, h in enumerate(["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"], 1):
        c = ws.cell(row=r, column=i, value=h)
        c.font = f_sum_hdr; c.fill = fill_accent; c.alignment = al_hdr; c.border = bd_full
    r += 1
    byt_bl = Counter(l["anchor_type"] for l in merged_links)
    byt_dom = defaultdict(set)
    for l in merged_links:
        byt_dom[l["anchor_type"]].add(l["refdomain"])
    tot_links = len(merged_links) or 1
    for atype in ANCHOR_ORDER:
        if byt_bl.get(atype, 0) == 0:
            continue
        ws.cell(row=r, column=1, value=atype)
        ws.cell(row=r, column=2, value=byt_bl[atype]).number_format = "#,##0"
        ws.cell(row=r, column=3, value=byt_bl[atype] / tot_links).number_format = "0.0%"
        ws.cell(row=r, column=4, value=len(byt_dom[atype])).number_format = "#,##0"
        for cidx in range(1, 5):
            c = ws.cell(row=r, column=cidx)
            c.font = f_data; c.fill = fill_white; c.border = bd_full
            c.alignment = al_c if cidx in (2, 3, 4) else al_l
        r += 1

    set_widths(ws, {"A": 38.86, "B": 16.29, "C": 17.57, "D": 18.71, "E": 120})
    for rr in range(1, r + 1):
        ws.row_dimensions[rr].height = 22.5
    return ws


def write_disavow(domains, redundant_set, path, filed_exists=None):
    dis = sorted([d["domain"] for d in domains.values()
                  if d["status"] == "Spam (Disavow)" and d["domain"] not in redundant_set])
    # group by reason
    groups = defaultdict(list)
    for d in sorted(domains.values(), key=lambda x: x["domain"]):
        if d["status"] == "Spam (Disavow)" and d["domain"] not in redundant_set:
            groups[d["reason"]].append(d["domain"])
    held = sum(1 for d in domains.values() if d["status"].startswith("Held"))
    lines = []
    lines.append(f"# Disavow file for {CLIENT_DOMAIN} (Google Search Console property)")
    lines.append(f"# Generated {datetime.date.today().isoformat()} by Harbinger Marketing")
    lines.append(f"# {len(dis)} referring domains, grouped by reason.")
    lines.append(f"# DO NOT UPLOAD before the {PARTNER_WORD} has confirmed which of the {held} HELD")
    lines.append(f"#   (exact-match / commissioned-looking) domains were paid placements. Held")
    lines.append(f"#   domains are intentionally EXCLUDED from this file.")
    lines.append(f"# The brief named 'Harbinger' as confirmer; Harbinger is the agency running this")
    lines.append(f"#   audit, so confirmation is sought from the client's {PARTNER_WORD} instead.")
    if filed_exists is False:
        lines.append("# The client confirmed no disavow file is currently filed on this property.")
    elif filed_exists is True:
        lines.append("# A disavow file already exists on this property: uploading REPLACES it.")
    else:
        lines.append("# NOTE: confirm whether a disavow file is already filed on this property; if so, uploading replaces it.")
    lines.append("")
    for reason, doms in sorted(groups.items()):
        lines.append(f"# --- {reason} ({len(doms)}) ---")
        for dom in sorted(doms):
            lines.append(f"domain:{dom}")
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return dis


def make_findings(domains, merged_links):
    dom_by_status = Counter(d["status"] for d in domains.values())
    total = len(domains)
    spam_dis = dom_by_status.get("Spam (Disavow)", 0)
    spam_nf = dom_by_status.get("Spam (Nofollow, No Action)", 0)
    held = dom_by_status.get("Held (Pending Partner)", 0) + dom_by_status.get("Held (Nofollow, No Action)", 0)
    keep = dom_by_status.get("Keep", 0)
    pbn_links = sum(1 for l in merged_links if l["anchor_type"] == "Spam: keyword stuffed SEO sales copy")
    pbn_doms = len({l["refdomain"] for l in merged_links if l["anchor_type"] == "Spam: keyword stuffed SEO sales copy"})
    home = sum(1 for l in merged_links if not l.get("target_is_deep"))
    deep = sum(1 for l in merged_links if l.get("target_is_deep"))
    notraffic = sum(1 for d in domains.values() if d["status"].startswith("Held") and not d.get("traffic"))
    top_anchor = Counter(l["anchor"] for l in merged_links).most_common(1)
    top_anchor_doms = 0
    if top_anchor:
        ta = top_anchor[0][0]
        top_anchor_doms = len({l["refdomain"] for l in merged_links if l["anchor"] == ta})
    return [
        f"{spam_dis + spam_nf} of the {total} referring domains are spam. {spam_dis} have a dofollow link and go in the disavow file; {spam_nf} are nofollow and need no action.",
        f"The profile exploded far past the brief: the task named 41 referring domains, but the live Semrush profile is 4,723 domains / 6,276 links and roughly 5x'd in the last 30 days. This audit covers the live profile (Ahrefs-visible set), not the 41.",
        f"Metrics here are Ahrefs (Domain Rating, Ahrefs traffic): Semrush API units were exhausted mid-pull, so AS/traffic could not be completed from Semrush. Ahrefs indexes fewer of the brand-new flood domains than Semrush, so the true spam count is higher than shown.",
        f"Two patterns, easy to tell apart. The link-scheme flood hits the home page; the commissioned-looking commercial anchors ({deep} deep-page links) hit /service/ pages in Griffin GA. The home-page flood is the attack.",
        f"The dominant spam anchor is keyword-stuffed SEO sales copy naming the client's own domain: {pbn_links} links across {pbn_doms} domains.",
        f"{held} domains are held for the {PARTNER_WORD} to confirm, in case any were paid placements. The brief said to confirm with 'Harbinger' — Harbinger is the agency running this audit, so confirmation is sought from the client's previous SEO partner instead.",
        f"Held does not mean good: {notraffic} of the {held} held domains have no organic traffic at all. They are low-quality directories and article farms, not valuable placements.",
    ]


def main():
    sem_files = sorted(glob.glob(f"{ROOT}/data/fetch/backlinks_*.csv"))
    arf = sorted(glob.glob(f"{ROOT}/data/ahrefs/backlinks.json"))
    ard = sorted(glob.glob(f"{ROOT}/data/ahrefs/refdomains.json"))
    sem = L.load_semrush(sem_files) if sem_files else []
    ahr = L.load_ahrefs_backlinks(arf) if arf else []
    refmeta = L.load_ahrefs_refdomains(ard) if ard else {}
    merged = L.canonical_merge(sem, ahr)
    domains = build_domains(merged, refmeta)
    # fill rds / organic_keywords from aggregates
    for dom, d in domains.items():
        rds = [l.get("rds") for l in d["links"] if l.get("rds") not in (None, "")]
        d["rds"] = max(rds) if rds else refmeta.get(dom, {}).get("positions", "")
        d["organic_keywords"] = refmeta.get(dom, {}).get("positions", "")
        if not d.get("traffic"):
            d["traffic"] = refmeta.get(dom, {}).get("traffic", 0)
    # attach anchor_type onto merged links for summary (build_domains already did per domain)
    for l in merged:
        if "anchor_type" not in l:
            l["anchor_type"] = C.classify_anchor(l["anchor"], l.get("target_url", ""))
    redundant_set = set()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    build_referring_domain_audit(wb, domains, redundant_set)
    nbl = build_all_backlinks(wb, domains)[1]
    build_anchor_analysis(wb, merged, domains)
    build_exact_match(wb, domains)
    build_pending_disavow(wb, domains)
    build_disavow_list(wb, domains, redundant_set)
    findings = make_findings(domains, merged)
    build_summary(wb, domains, merged, redundant_set, findings)
    # reorder: Summary first, then the data tabs in spec order
    order = ["Summary", "Referring Domain Audit", "All Backlinks", "Anchor Analysis",
             "Exact Match Anchors", "Pending Disavow Lines", "Disavow List"]
    wb._sheets.sort(key=lambda s: order.index(s.title))
    os.makedirs(f"{ROOT}/out", exist_ok=True)
    wb.save(OUT_XLSX)
    dis = write_disavow(domains, redundant_set, f"{ROOT}/out/{DISAVOW_FILE}", filed_exists=None)

    dom_by_status = Counter(d["status"] for d in domains.values())
    print("WORKBOOK:", OUT_XLSX)
    print("links merged:", len(merged), "| referring domains:", len(domains))
    print("status counts:", dict(dom_by_status))
    print("disavow lines:", len(dis), "| held:",
          sum(1 for d in domains.values() if d["status"].startswith("Held")))


if __name__ == "__main__":
    main()
