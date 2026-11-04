"""Cell-for-cell structural comparison of the built workbook vs the signed-off
K&K template. Reports structural differences (not data values)."""
import sys
import openpyxl
from openpyxl.utils import get_column_letter

TEMPLATE = "erth/ref/kk_template.xlsx"
BUILT = "erth/out/Erth_Products_Backlinks_Audit.xlsx"

diffs = []


def rec(msg):
    diffs.append(msg)


def side(s):
    return getattr(s, "style", None) if s else None


def border_sig(c):
    b = c.border
    return (side(b.left), side(b.right), side(b.top), side(b.bottom))


def fill_sig(c):
    f = c.fill
    return f.fgColor.rgb if (f and f.patternType) else None


def font_sig(c):
    f = c.font
    col = None
    try:
        col = f.color.rgb if f.color else None
        if not isinstance(col, str):
            col = None
    except Exception:
        col = None
    return (f.name, float(f.size) if f.size else None, bool(f.bold), col)


def main():
    t = openpyxl.load_workbook(TEMPLATE)
    b = openpyxl.load_workbook(BUILT)
    if t.sheetnames != b.sheetnames:
        rec(f"SHEET ORDER/NAMES differ:\n  template={t.sheetnames}\n  built   ={b.sheetnames}")
    for name in t.sheetnames:
        if name not in b.sheetnames:
            continue
        ts, bs = t[name], b[name]
        # gridlines
        if bool(ts.sheet_view.showGridLines) != bool(bs.sheet_view.showGridLines):
            rec(f"[{name}] gridlines: template={ts.sheet_view.showGridLines} built={bs.sheet_view.showGridLines}")
        # freeze
        if ts.freeze_panes != bs.freeze_panes:
            rec(f"[{name}] freeze_panes: template={ts.freeze_panes} built={bs.freeze_panes}")
        # autofilter presence (ref range differs by row count, compare columns only)
        tf = ts.auto_filter.ref.split(":")[-1].rstrip("0123456789").replace("$", "") if ts.auto_filter.ref else None
        bf = bs.auto_filter.ref.split(":")[-1].rstrip("0123456789").replace("$", "") if bs.auto_filter.ref else None
        if tf != bf:
            rec(f"[{name}] autofilter last-col: template={tf} built={bf} (t={ts.auto_filter.ref} b={bs.auto_filter.ref})")
        # header row values
        hdr_row = 3 if name == "Summary" else 1
        maxc = ts.max_column
        for c in range(1, maxc + 1):
            tv = ts.cell(hdr_row, c).value
            bv = bs.cell(hdr_row, c).value
            if (tv or "") != (bv or ""):
                rec(f"[{name}] header {get_column_letter(c)}{hdr_row}: template={tv!r} built={bv!r}")
        # column widths
        for c in range(1, maxc + 1):
            L = get_column_letter(c)
            tw = ts.column_dimensions[L].width
            bw = bs.column_dimensions[L].width
            if tw and bw and abs(tw - bw) > 0.3:
                rec(f"[{name}] col {L} width: template={tw} built={bw}")
            elif bool(tw) != bool(bw):
                rec(f"[{name}] col {L} width set mismatch: template={tw} built={bw}")
        # header + first data row height
        for r in ([3, 4] if name == "Summary" else [1, 2]):
            th = ts.row_dimensions[r].height
            bh = bs.row_dimensions[r].height
            if th and bh and abs(th - bh) > 0.1:
                rec(f"[{name}] row {r} height: template={th} built={bh}")
        # header styling at A(hdr)
        hc_t, hc_b = ts.cell(hdr_row, 1), bs.cell(hdr_row, 1)
        if font_sig(hc_t) != font_sig(hc_b):
            rec(f"[{name}] header font A{hdr_row}: template={font_sig(hc_t)} built={font_sig(hc_b)}")
        if fill_sig(hc_t) != fill_sig(hc_b):
            rec(f"[{name}] header fill A{hdr_row}: template={fill_sig(hc_t)} built={fill_sig(hc_b)}")
        if border_sig(hc_t) != border_sig(hc_b):
            rec(f"[{name}] header border A{hdr_row}: template={border_sig(hc_t)} built={border_sig(hc_b)}")
        # data cell styling at A2 (data tabs)
        if name != "Summary" and ts.max_row >= 2 and bs.max_row >= 2:
            d_t, d_b = ts.cell(2, 1), bs.cell(2, 1)
            if border_sig(d_t) != border_sig(d_b):
                rec(f"[{name}] data border A2: template={border_sig(d_t)} built={border_sig(d_b)}")
            if fill_sig(d_t) != fill_sig(d_b):
                rec(f"[{name}] data fill A2: template={fill_sig(d_t)} built={fill_sig(d_b)}")
            if font_sig(d_t) != font_sig(d_b):
                rec(f"[{name}] data font A2: template={font_sig(d_t)} built={font_sig(d_b)}")
    # logo presence on Summary
    tdr = len(t["Summary"]._images)
    bdr = len(b["Summary"]._images)
    if tdr != bdr:
        rec(f"[Summary] image count: template={tdr} built={bdr}")

    print("STRUCTURAL DIFFERENCES:", len(diffs))
    for d in diffs:
        print("  -", d)
    return diffs


if __name__ == "__main__":
    main()
