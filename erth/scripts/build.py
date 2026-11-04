"""Build the erthproducts.com backlink-audit workbook + disavow files.

Matches the signed-off K&K template cell-for-cell: 7 tabs, Geist font, accent
FF0C343D headers, header-only borders on data tabs, full borders on the Summary
small tables, logo on the Summary, freeze B2, autofilter, gridlines (off on
Summary), exact per-column alignment / number formats, and the "Y,N" /
"Keep,Disavow" dropdowns on the Exact Match input columns.
"""
import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.worksheet.datavalidation import DataValidation

ACCENT = "FF0C343D"
WHITE = "FFFFFFFF"
fill_accent = PatternFill("solid", fgColor=ACCENT)
fill_white = PatternFill("solid", fgColor=WHITE)
thin = Side(style="thin")
HDR_BORDER = Border(left=thin, right=thin, top=thin)
FULL_BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
NO_BORDER = Border()

A_HDR = Alignment(horizontal="center", vertical="center", wrap_text=True)
A_HDR_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
A_HDR_NOWRAP = Alignment(horizontal="center", vertical="center", wrap_text=False)
A_CEN = Alignment(horizontal="center", vertical="center")
A_LEFT = Alignment(vertical="center")                 # horizontal None (default/left)
A_LEFT_WRAP = Alignment(vertical="center", wrap_text=True)

F_DATA = dict(name="Geist", size=9, color="FF000000")
F_HDR = dict(name="Geist", size=9, bold=True, color=WHITE)
F_SUMHDR = dict(name="Geist", size=10, bold=True, color=WHITE)
F_TITLE = dict(name="Geist", size=21, bold=True, color=ACCENT)
F_KEYHEAD = dict(name="Geist", size=10, bold=True, color="FF000000")
F_SECTION = dict(name="Geist", size=11, bold=True, color=ACCENT)
F_TOTAL = dict(name="Geist", size=9, bold=True)
F_WHITE_ON_ACCENT = dict(name="Geist", size=9, color=WHITE)

NUM = "#,##0"
PCT1 = "0.0%"
PCT2 = "0.00%"
DATEFMT = "d mmm yyyy"

# ---- per-sheet column specs: col -> (center?, numfmt or None). Header left/nowrap overrides. ----
SPECS = {
    "Referring Domain Audit": {
        "headers": ["Domain", "Status", "AS", "Backlinks", "RD's", "Traffic", "In Disavow",
                    "Links Point To", "Dofollow Links", "Nofollow Links", "First Seen",
                    "Top Anchor Text", "Example Linking Page", "Linking Page Title", "Source",
                    "IP", "Disavow Line"],
        "widths": {"A": 36.0, "B": 24.71, "C": 9.57, "D": 13.0, "E": 9.43, "F": 9.71,
                   "G": 12.43, "H": 21.29, "I": 14.0, "J": 8.71, "K": 12.0, "L": 45.0,
                   "M": 8.71, "N": 40.0, "O": 14.0, "P": 15.0, "Q": 14.0},
        "center": {3, 4, 5, 6, 7, 9, 10, 11, 15, 16},
        "numfmt": {4: NUM, 5: NUM, 6: NUM, 11: DATEFMT},
        "height": 15.75,
    },
    "All Backlinks": {
        "headers": ["Referring Domain", "Status", "Tool", "Anchor Text", "Anchor Type",
                    "Link Type", "Linking Page URL", "Linking Page Title", "Target URL"],
        "widths": {"A": 25.43, "B": 27.14, "C": 14.71, "D": 55.0, "E": 32.0, "F": 10.0,
                   "G": 55.0, "H": 53.14, "I": 30.57},
        "center": {6}, "left": {3}, "hdr_left": {3}, "numfmt": {}, "height": 22.5,
    },
    "Anchor Analysis": {
        "headers": ["Anchor Text", "Anchor Type", "Backlinks", "Share of Backlinks",
                    "Referring Domains", "Spam Domains Using It"],
        "widths": {"A": 115.86, "B": 37.71, "C": 14.0, "D": 8.71, "E": 13.0, "F": 20.29},
        "center": {3, 4, 5, 6}, "hdr_nowrap": {1},
        "numfmt": {3: NUM, 4: PCT2}, "height": 22.5,
    },
    "Exact Match Anchors": {
        "headers": ["Referring domain", "Example backlink (linking page)",
                    "Exact-match commercial anchor", "Market", "Site type (indicative)",
                    "Partner confirmed? (Y/N)", "Final decision"],
        "widths": {"A": 25.43, "B": 59.0, "C": 53.14, "D": 16.0, "E": 24.57, "F": 15.43, "G": 15.0},
        "center": {3, 4}, "numfmt": {}, "height": 22.5, "input_cols": {6, 7},
    },
    "Pending Disavow Lines": {
        "headers": ["Referring domain", "Disavow line (append to disavow.txt once confirmed)",
                    "Recommendation"],
        "widths": {"A": 32.0, "B": 44.0, "C": 48.0},
        "center": set(), "numfmt": {}, "height": 22.5,
    },
    "Disavow List": {
        "headers": ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic", "Organic Keywords",
                    "Top Anchor Text"],
        "widths": {"A": 44.0, "B": 14.0, "C": 15.57, "D": 14.0, "E": 11.14, "F": 14.86, "G": 98.86},
        "center": {2, 3, 4, 5, 6}, "numfmt": {3: NUM, 4: NUM, 5: NUM, 6: NUM}, "height": 22.5,
    },
}


def _ts_to_date(ts):
    if ts in (None, "", "0"):
        return None
    try:
        return dt.datetime.utcfromtimestamp(int(ts)).date()
    except (ValueError, TypeError, OverflowError):
        try:
            return dt.date.fromisoformat(str(ts)[:10])
        except Exception:
            return None


def _write_tab(wb, name, rows):
    spec = SPECS[name]
    ws = wb.create_sheet(name)
    for col, w in spec["widths"].items():
        ws.column_dimensions[col].width = w
    # header
    for i, h in enumerate(spec["headers"], 1):
        c = ws.cell(1, i, h)
        c.font = Font(**F_HDR)
        c.fill = fill_accent
        if i in spec.get("hdr_left", set()):
            c.alignment = A_HDR_LEFT
        elif i in spec.get("hdr_nowrap", set()):
            c.alignment = A_HDR_NOWRAP
        else:
            c.alignment = A_HDR
        c.border = HDR_BORDER
    ws.row_dimensions[1].height = 31.5
    center = spec["center"]
    leftset = spec.get("left", set())
    numfmt = spec["numfmt"]
    inputs = spec.get("input_cols", set())
    r = 2
    for row in rows:
        for i, v in enumerate(row, 1):
            if i in inputs:
                c = ws.cell(r, i, None)
                c.font = Font(**F_WHITE_ON_ACCENT)
                c.fill = fill_accent
                c.alignment = A_LEFT
                c.border = NO_BORDER
                continue
            c = ws.cell(r, i, v)
            c.font = Font(**F_DATA)
            c.fill = fill_white
            c.border = NO_BORDER
            if i in center:
                c.alignment = A_CEN
            elif i in leftset:
                c.alignment = Alignment(horizontal="left", vertical="center")
            else:
                c.alignment = A_LEFT
            if i in numfmt:
                c.number_format = numfmt[i]
        ws.row_dimensions[r].height = spec["height"]
        r += 1
    ws.freeze_panes = "B2"
    last_col = get_column_letter(len(spec["headers"]))
    ws.auto_filter.ref = f"A1:{last_col}{max(r-1,1)}"
    return ws, r - 1


def build(records, out_xlsx, logo_path=None):
    wb = Workbook()

    # ===================== Summary =====================
    ws = wb.active
    ws.title = "Summary"
    ws.sheet_view.showGridLines = False
    for col, w in {"A": 38.86, "B": 16.29, "C": 17.57, "D": 18.71, "E": 120.0}.items():
        ws.column_dimensions[col].width = w
    ws.merge_cells("B1:E2")
    t = ws["B1"]; t.value = records["client_name"]; t.font = Font(**F_TITLE); t.alignment = A_CEN
    for rr in range(1, 40):
        ws.row_dimensions[rr].height = 22.5

    for i, h in enumerate(["Status", "Domains", "Backlinks", "Share of Domains", "What it means"], 1):
        c = ws.cell(3, i, h); c.font = Font(**F_SUMHDR); c.fill = fill_accent
        c.alignment = A_HDR; c.border = FULL_BORDER

    r = 4
    for row in records["summary_status"]:
        for cc, val in enumerate(row, 1):
            c = ws.cell(r, cc, val); c.font = Font(**F_DATA); c.fill = fill_white; c.border = FULL_BORDER
            if cc in (2, 3):
                c.number_format = NUM; c.alignment = A_CEN
            elif cc == 4:
                c.number_format = PCT1; c.alignment = A_CEN
            elif cc == 5:
                c.alignment = A_LEFT_WRAP
            else:
                c.alignment = A_LEFT
        r += 1
    total = list(records["summary_total"]) + [None]   # E10 empty but styled
    for cc in range(1, 6):
        c = ws.cell(10, cc, total[cc - 1]); c.font = Font(**F_TOTAL)
        c.fill = fill_white; c.border = FULL_BORDER
        if cc in (2, 3):
            c.number_format = NUM; c.alignment = A_CEN
        elif cc == 4:
            c.number_format = PCT1; c.alignment = A_CEN
        else:
            c.alignment = A_LEFT

    kh = ws.cell(11, 1, "Key findings"); kh.font = Font(**F_KEYHEAD); kh.alignment = A_LEFT
    fr = 12
    for kf in records["key_findings"]:
        ws.merge_cells(start_row=fr, start_column=1, end_row=fr, end_column=5)
        c = ws.cell(fr, 1, kf); c.font = Font(name="Geist", size=9); c.alignment = A_LEFT_WRAP
        fr += 1

    sc = ws.cell(fr, 1, "Anchor text profile (all backlinks)")
    sc.font = Font(**F_SECTION); sc.alignment = A_LEFT
    hdr = fr + 1
    for i, h in enumerate(["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains", None], 1):
        c = ws.cell(hdr, i, h); c.font = Font(**F_HDR); c.fill = fill_accent
        c.alignment = A_HDR; c.border = FULL_BORDER
    rr = hdr + 1
    for a_type, bl, share, rd in records["summary_anchor"]:
        vals = [a_type, bl, share, rd]
        for cc, v in enumerate(vals, 1):
            c = ws.cell(rr, cc, v); c.font = Font(**F_DATA); c.fill = fill_white; c.border = FULL_BORDER
            if cc == 1:
                c.number_format = NUM; c.alignment = A_LEFT
            elif cc == 3:
                c.number_format = PCT1; c.alignment = A_CEN
            else:
                c.number_format = NUM; c.alignment = A_CEN
        rr += 1

    if logo_path:
        try:
            img = XLImage(logo_path)
            marker = AnchorMarker(col=0, colOff=381000, row=0, rowOff=0)
            img.anchor = OneCellAnchor(_from=marker, ext=XDRPositiveSize2D(cx=1866900, cy=552450))
            ws.add_image(img)
        except Exception as e:
            print("logo skip:", e)

    # ===================== data tabs =====================
    rda = [[row["domain"], row["status"], row["as"], row["backlinks"], row["rds"], row["traffic"],
            row["in_disavow"], row["points_to"], row["dofollow"], row["nofollow"],
            _ts_to_date(row["first_seen"]), row["top_anchor"], row["example_page"], row["title"],
            row["source"], row["ip"], row["disavow_line"]] for row in records["rda_rows"]]
    _write_tab(wb, "Referring Domain Audit", rda)

    abl = [[r["domain"], r["status"], r["tool"], r["anchor"], r["anchor_type"], r["link_type"],
            r["url_from"], r["title"], r["target"]] for r in records["abl_rows"]]
    _write_tab(wb, "All Backlinks", abl)

    anch = [[r["anchor"], r["anchor_type"], r["backlinks"], r["share"], r["refdomains"],
             r["spam_domains"]] for r in records["anchor_rows"]]
    _write_tab(wb, "Anchor Analysis", anch)

    exact = [[r["domain"], r["example"], r["anchor"], r["market"], r["site_type"], None, None]
             for r in records["exact_rows"]]
    ws_e, last_e = _write_tab(wb, "Exact Match Anchors", exact)
    if last_e >= 2:
        dv_f = DataValidation(type="list", formula1='"Y,N"', allow_blank=True)
        dv_f.showDropDown = False
        dv_g = DataValidation(type="list", formula1='"Keep,Disavow"', allow_blank=True)
        dv_g.showDropDown = False
        ws_e.add_data_validation(dv_f); dv_f.add(f"F2:F{last_e}")
        ws_e.add_data_validation(dv_g); dv_g.add(f"G2:G{last_e}")

    pend = [[r["domain"], r["line"], r["reco"]] for r in records["pending_rows"]]
    _write_tab(wb, "Pending Disavow Lines", pend)

    disl = [[r["line"], r["as"], r["backlinks"], r["rds"], r["traffic"], r["org_kw"], r["top_anchor"]]
            for r in records["disavow_rows"]]
    _write_tab(wb, "Disavow List", disl)

    wb.save(out_xlsx)
    return out_xlsx


if __name__ == "__main__":
    print("build.py is a library; run records.py to produce records and call build().")
