"""Build the erthproducts.com backlink-audit workbook + disavow files.

Matches the signed-off K&K template cell-for-cell: 7 tabs, Geist font, accent
FF0C343D headers, header-only borders on data tabs, full borders on the Summary
small tables, logo on the Summary, freeze B2, autofilter, gridlines on (off on
Summary). Change the format here, never by hand in Excel.
"""
import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

ACCENT = "FF0C343D"
WHITE = "FFFFFFFF"

fill_accent = PatternFill("solid", fgColor=ACCENT)
fill_white = PatternFill("solid", fgColor=WHITE)

thin = Side(style="thin")
HDR_BORDER = Border(left=thin, right=thin, top=thin)          # no bottom (data tabs)
FULL_BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)  # summary tables
NO_BORDER = Border()

A_CEN_WRAP = Alignment(horizontal="center", vertical="center", wrap_text=True)
A_CEN = Alignment(horizontal="center", vertical="center")
A_VC = Alignment(vertical="center")
A_VC_WRAP = Alignment(vertical="center", wrap_text=True)

F_DATA = dict(name="Geist", size=9, color="FF000000")
F_HDR = dict(name="Geist", size=9, bold=True, color=WHITE)
F_SUMHDR = dict(name="Geist", size=10, bold=True, color=WHITE)
F_TITLE = dict(name="Geist", size=21, bold=True, color=ACCENT)
F_KEYHEAD = dict(name="Geist", size=10, bold=True, color="FF000000")
F_SECTION = dict(name="Geist", size=11, bold=True, color=ACCENT)
F_TOTAL = dict(name="Geist", size=9, bold=True)
F_DATA_WHITEONACCENT = dict(name="Geist", size=9, color=WHITE)

NUM = "#,##0"
PCT = "0.0%"
DATEFMT = "d mmm yyyy"


def _hdr(ws, row, headers, font=F_HDR):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row, i, h)
        c.font = Font(**font)
        c.fill = fill_accent
        c.alignment = A_CEN_WRAP
        c.border = HDR_BORDER
    ws.row_dimensions[row].height = 31.5


def _data_cell(ws, r, cc, val, numfmt=None, align=A_VC, font=F_DATA, fill=fill_white):
    c = ws.cell(r, cc, val)
    c.font = Font(**font)
    c.fill = fill
    c.alignment = align
    c.border = NO_BORDER
    if numfmt:
        c.number_format = numfmt
    return c


def _ts_to_date(ts):
    if ts in (None, "", "0"):
        return None
    try:
        return dt.datetime.utcfromtimestamp(int(ts)).date()
    except (ValueError, TypeError, OverflowError):
        # maybe already a date/datetime iso string
        try:
            return dt.date.fromisoformat(str(ts)[:10])
        except Exception:
            return None


def set_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def build(records, out_xlsx, logo_path=None):
    wb = Workbook()

    # ============================ Summary ============================
    ws = wb.active
    ws.title = "Summary"
    ws.sheet_view.showGridLines = False
    set_widths(ws, {"A": 38.86, "B": 16.29, "C": 17.57, "D": 18.71, "E": 120.0})
    ws.merge_cells("B1:E2")
    t = ws["B1"]
    t.value = records["client_name"]
    t.font = Font(**F_TITLE)
    t.alignment = A_CEN
    for r in range(1, 40):
        ws.row_dimensions[r].height = 22.5

    # status table header row 3
    for i, h in enumerate(["Status", "Domains", "Backlinks", "Share of Domains", "What it means"], 1):
        c = ws.cell(3, i, h)
        c.font = Font(**F_SUMHDR)
        c.fill = fill_accent
        c.alignment = A_CEN_WRAP
        c.border = FULL_BORDER
    # status rows 4..9 + total row 10
    r = 4
    for row in records["summary_status"]:  # list of (status, domains, backlinks, share, meaning)
        ws.cell(r, 1, row[0]).font = Font(**F_DATA)
        ws.cell(r, 2, row[1]).font = Font(**F_DATA)
        ws.cell(r, 3, row[2]).font = Font(**F_DATA)
        ws.cell(r, 4, row[3]).font = Font(**F_DATA)
        ws.cell(r, 5, row[4]).font = Font(**F_DATA)
        ws.cell(r, 2).number_format = NUM
        ws.cell(r, 3).number_format = NUM
        ws.cell(r, 4).number_format = PCT
        for cc in range(1, 6):
            cell = ws.cell(r, cc)
            cell.fill = fill_white
            cell.border = FULL_BORDER
            cell.alignment = A_CEN_WRAP if cc == 5 else (A_CEN if cc in (2, 3, 4) else A_VC)
        r += 1
    # total row
    tot = records["summary_total"]  # (label, domains, backlinks, share)
    for cc, val in enumerate(tot, 1):
        cell = ws.cell(10, cc, val)
        cell.font = Font(**F_TOTAL)
        cell.fill = fill_white
        cell.border = FULL_BORDER
        cell.alignment = A_CEN if cc in (2, 3, 4) else A_VC
    ws.cell(10, 2).number_format = NUM
    ws.cell(10, 3).number_format = NUM
    ws.cell(10, 4).number_format = PCT

    # Key findings heading row 11, findings rows 12..18 (merged A:E)
    ws.cell(11, 1, "Key findings").font = Font(**F_KEYHEAD)
    fr = 12
    for kf in records["key_findings"]:
        ws.merge_cells(start_row=fr, start_column=1, end_row=fr, end_column=5)
        c = ws.cell(fr, 1, kf)
        c.font = Font(**F_DATA)
        c.alignment = A_VC_WRAP
        fr += 1

    # Anchor profile section heading + table
    sec = fr
    ws.cell(sec, 1, "Anchor text profile (all backlinks)").font = Font(**F_SECTION)
    hdr = sec + 1
    for i, h in enumerate(["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"], 1):
        c = ws.cell(hdr, i, h)
        c.font = Font(**F_HDR)
        c.fill = fill_accent
        c.alignment = A_CEN_WRAP
        c.border = FULL_BORDER
    rr = hdr + 1
    for a_type, bl, share, rd in records["summary_anchor"]:
        ws.cell(rr, 1, a_type).font = Font(**F_DATA)
        ws.cell(rr, 2, bl).font = Font(**F_DATA)
        ws.cell(rr, 3, share).font = Font(**F_DATA)
        ws.cell(rr, 4, rd).font = Font(**F_DATA)
        ws.cell(rr, 1).number_format = NUM
        ws.cell(rr, 2).number_format = NUM
        ws.cell(rr, 3).number_format = PCT
        ws.cell(rr, 4).number_format = NUM
        for cc in range(1, 5):
            ws.cell(rr, cc).fill = fill_white
            ws.cell(rr, cc).border = FULL_BORDER
            ws.cell(rr, cc).alignment = A_CEN if cc in (2, 3, 4) else A_VC
        rr += 1

    if logo_path:
        try:
            img = XLImage(logo_path)
            img.anchor = "A1"
            # oneCellAnchor emulation: openpyxl places at cell; offset via anchor obj
            ws.add_image(img, "A1")
        except Exception as e:
            print("logo skip:", e)

    # ===================== Referring Domain Audit =====================
    ws = wb.create_sheet("Referring Domain Audit")
    rda_headers = ["Domain", "Status", "AS", "Backlinks", "RD's", "Traffic", "In Disavow",
                   "Links Point To", "Dofollow Links", "Nofollow Links", "First Seen",
                   "Top Anchor Text", "Example Linking Page", "Linking Page Title", "Source",
                   "IP", "Disavow Line"]
    _hdr(ws, 1, rda_headers)
    set_widths(ws, {"A": 36.0, "B": 24.71, "C": 9.57, "D": 13.0, "E": 9.43, "F": 9.71,
                    "G": 12.43, "H": 21.29, "I": 14.0, "J": 8.71, "K": 12.0, "L": 45.0,
                    "M": 8.71, "N": 40.0, "O": 14.0, "P": 15.0, "Q": 14.0})
    r = 2
    for row in records["rda_rows"]:
        vals = [row["domain"], row["status"], row["as"], row["backlinks"], row["rds"],
                row["traffic"], row["in_disavow"], row["points_to"], row["dofollow"],
                row["nofollow"], _ts_to_date(row["first_seen"]), row["top_anchor"],
                row["example_page"], row["title"], row["source"], row["ip"], row["disavow_line"]]
        for cc, v in enumerate(vals, 1):
            nf = None
            if cc in (4, 5, 6):
                nf = NUM
            if cc in (9, 10):
                nf = NUM
            if cc == 11:
                nf = DATEFMT
            _data_cell(ws, r, cc, v, numfmt=nf)
        ws.row_dimensions[r].height = 15.75
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:Q{r-1}"

    # ========================= All Backlinks =========================
    ws = wb.create_sheet("All Backlinks")
    abl_headers = ["Referring Domain", "Status", "Tool", "Anchor Text", "Anchor Type",
                   "Link Type", "Linking Page URL", "Linking Page Title", "Target URL"]
    _hdr(ws, 1, abl_headers)
    set_widths(ws, {"A": 25.43, "B": 27.14, "C": 14.71, "D": 55.0, "E": 32.0, "F": 10.0,
                    "G": 55.0, "H": 53.14, "I": 30.57})
    r = 2
    for row in records["abl_rows"]:
        vals = [row["domain"], row["status"], row["tool"], row["anchor"], row["anchor_type"],
                row["link_type"], row["url_from"], row["title"], row["target"]]
        for cc, v in enumerate(vals, 1):
            _data_cell(ws, r, cc, v)
        ws.row_dimensions[r].height = 22.5
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:I{r-1}"

    # ========================= Anchor Analysis =========================
    ws = wb.create_sheet("Anchor Analysis")
    _hdr(ws, 1, ["Anchor Text", "Anchor Type", "Backlinks", "Share of Backlinks",
                 "Referring Domains", "Spam Domains Using It"])
    set_widths(ws, {"A": 115.86, "B": 37.71, "C": 14.0, "D": 8.71, "E": 13.0, "F": 20.29})
    r = 2
    for row in records["anchor_rows"]:
        vals = [row["anchor"], row["anchor_type"], row["backlinks"], row["share"],
                row["refdomains"], row["spam_domains"]]
        for cc, v in enumerate(vals, 1):
            nf = NUM if cc in (3, 5, 6) else (PCT if cc == 4 else None)
            _data_cell(ws, r, cc, v, numfmt=nf)
        ws.row_dimensions[r].height = 22.5
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:F{r-1}"

    # ======================= Exact Match Anchors =======================
    ws = wb.create_sheet("Exact Match Anchors")
    _hdr(ws, 1, ["Referring domain", "Example backlink (linking page)",
                 "Exact-match commercial anchor", "Market", "Site type (indicative)",
                 "Partner confirmed? (Y/N)", "Final decision"])
    set_widths(ws, {"A": 25.43, "B": 59.0, "C": 53.14, "D": 16.0, "E": 24.57, "F": 15.43, "G": 15.0})
    r = 2
    for row in records["exact_rows"]:
        vals = [row["domain"], row["example"], row["anchor"], row["market"], row["site_type"]]
        for cc, v in enumerate(vals, 1):
            _data_cell(ws, r, cc, v)
        # F, G are partner-input: accent fill, white font, empty
        for cc in (6, 7):
            c = _data_cell(ws, r, cc, None, font=F_DATA_WHITEONACCENT, fill=fill_accent)
        ws.row_dimensions[r].height = 22.5
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:G{r-1}"

    # ======================= Pending Disavow Lines =======================
    ws = wb.create_sheet("Pending Disavow Lines")
    _hdr(ws, 1, ["Referring domain", "Disavow line (append to disavow.txt once confirmed)",
                 "Recommendation"])
    set_widths(ws, {"A": 32.0, "B": 44.0, "C": 48.0})
    r = 2
    for row in records["pending_rows"]:
        for cc, v in enumerate([row["domain"], row["line"], row["reco"]], 1):
            _data_cell(ws, r, cc, v)
        ws.row_dimensions[r].height = 22.5
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:C{r-1}"

    # ========================= Disavow List =========================
    ws = wb.create_sheet("Disavow List")
    _hdr(ws, 1, ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic", "Organic Keywords",
                 "Top Anchor Text"])
    set_widths(ws, {"A": 44.0, "B": 14.0, "C": 15.57, "D": 14.0, "E": 11.14, "F": 14.86, "G": 98.86})
    r = 2
    for row in records["disavow_rows"]:
        vals = [row["line"], row["as"], row["backlinks"], row["rds"], row["traffic"],
                row["org_kw"], row["top_anchor"]]
        for cc, v in enumerate(vals, 1):
            nf = NUM if cc in (3, 4, 5, 6) else None
            _data_cell(ws, r, cc, v, numfmt=nf)
        ws.row_dimensions[r].height = 22.5
        r += 1
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:G{r-1}"

    wb.save(out_xlsx)
    return out_xlsx


if __name__ == "__main__":
    print("build.py is a library; run pipeline.py to produce records and call build().")
