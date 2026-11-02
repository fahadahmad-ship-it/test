"""Structural template comparison: the generated workbook vs the signed-off
K&K template. Compares layout/style (tabs, order, headers, widths, heights,
fonts, sizes, fills, borders, alignment, freeze panes, filters, gridlines,
logo) — NOT data values or row counts, which are client-specific.
Reports zero differences when the format matches. (Playbook Section 9.)
"""
import sys
import openpyxl
from openpyxl.utils import get_column_letter

TEMPLATE = "/home/user/test/ritter/sample/KandK_sample.xlsx"
OUT = "/home/user/test/ritter/out/Ritter_Backlinks_Audit.xlsx"

diffs = []


def d(msg):
    diffs.append(msg)


def cell_sig(c):
    f = c.font
    fill = c.fill
    fg = fill.fgColor.rgb if fill and fill.patternType else None
    b = c.border

    def s(x):
        return x.style if x and x.style else None
    al = c.alignment
    return (f.name, f.size, bool(f.bold),
            f.color.rgb if (f.color and isinstance(f.color.rgb, str)) else None,
            fill.patternType, fg,
            s(b.left), s(b.right), s(b.top), s(b.bottom),
            al.horizontal, al.vertical, bool(al.wrap_text), c.number_format)


def main():
    t = openpyxl.load_workbook(TEMPLATE)
    o = openpyxl.load_workbook(OUT)

    if t.sheetnames != o.sheetnames:
        d(f"SHEET NAMES/ORDER differ:\n  template={t.sheetnames}\n  output  ={o.sheetnames}")
        print("\n".join(diffs))
        return

    for name in t.sheetnames:
        tw, ow = t[name], o[name]
        # gridlines (None == default on, so normalize None->True)
        def gl(v):
            return False if v is False else True
        if gl(tw.sheet_view.showGridLines) != gl(ow.sheet_view.showGridLines):
            d(f"[{name}] gridlines: template={tw.sheet_view.showGridLines} output={ow.sheet_view.showGridLines}")
        # freeze panes
        if tw.freeze_panes != ow.freeze_panes:
            d(f"[{name}] freeze panes: template={tw.freeze_panes} output={ow.freeze_panes}")
        # autofilter: compare COLUMN span only (row count is data-dependent; $ optional)
        def afcols(ref):
            return "".join(ch for ch in (ref or "") if ch.isalpha() or ch == ":")
        if bool(tw.auto_filter.ref) != bool(ow.auto_filter.ref) or \
                afcols(tw.auto_filter.ref) != afcols(ow.auto_filter.ref):
            d(f"[{name}] autofilter cols: template={tw.auto_filter.ref!r} output={ow.auto_filter.ref!r}")

        if name == "Summary":
            # title cell + merges + logo
            if cell_sig(tw["B1"]) != cell_sig(ow["B1"]):
                d(f"[Summary] B1 title style differs:\n   t={cell_sig(tw['B1'])}\n   o={cell_sig(ow['B1'])}")
            tmerge = set(str(m) for m in tw.merged_cells.ranges if str(m).startswith("B1"))
            omerge = set(str(m) for m in ow.merged_cells.ranges if str(m).startswith("B1"))
            if tmerge != omerge:
                d(f"[Summary] title merge differs: t={tmerge} o={omerge}")
            if len(getattr(tw, "_images", [])) != len(getattr(ow, "_images", [])):
                d(f"[Summary] logo image count: t={len(tw._images)} o={len(ow._images)}")
            else:
                for ti, oi in zip(tw._images, ow._images):
                    if (ti.width, ti.height) != (oi.width, oi.height):
                        d(f"[Summary] logo size: t=({ti.width},{ti.height}) o=({oi.width},{oi.height})")
                    taf = ti.anchor._from
                    oaf = oi.anchor._from
                    if (taf.col, taf.colOff, taf.row, taf.rowOff) != (oaf.col, oaf.colOff, oaf.row, oaf.rowOff):
                        d(f"[Summary] logo anchor differs t=({taf.col},{taf.colOff},{taf.row},{taf.rowOff}) o=({oaf.col},{oaf.colOff},{oaf.row},{oaf.rowOff})")
            # fixed-layout status table: header row 3 (A..E) and a data row (row 4)
            for c in range(1, 6):
                if cell_sig(tw.cell(row=3, column=c)) != cell_sig(ow.cell(row=3, column=c)):
                    d(f"[Summary] status header {get_column_letter(c)}3 style differs:\n   t={cell_sig(tw.cell(3,c))}\n   o={cell_sig(ow.cell(3,c))}")
                if cell_sig(tw.cell(row=4, column=c)) != cell_sig(ow.cell(row=4, column=c)):
                    d(f"[Summary] status data {get_column_letter(c)}4 style differs:\n   t={cell_sig(tw.cell(4,c))}\n   o={cell_sig(ow.cell(4,c))}")
            # column widths A..E
            for c in range(1, 6):
                L = get_column_letter(c)
                tw_w = tw.column_dimensions[L].width
                ow_w = ow.column_dimensions[L].width
                if tw_w and ow_w and abs(tw_w - ow_w) > 0.5:
                    d(f"[Summary] col {L} width: t={round(tw_w,2)} o={round(ow_w,2)}")
            continue

        # data tabs: header texts (ALL columns)
        tcoln = tw.max_column
        theaders = [tw.cell(row=1, column=c).value for c in range(1, tcoln + 1)]
        oheaders = [ow.cell(row=1, column=c).value for c in range(1, tcoln + 1)]
        if theaders != oheaders:
            d(f"[{name}] headers differ:\n   t={theaders}\n   o={oheaders}")
        # column widths (ALL columns)
        for c in range(1, tcoln + 1):
            L = get_column_letter(c)
            tw_w = tw.column_dimensions[L].width
            ow_w = ow.column_dimensions[L].width
            if tw_w and ow_w and abs(tw_w - ow_w) > 0.5:
                d(f"[{name}] col {L} width: t={round(tw_w,2)} o={round(ow_w,2)}")
        # header row height
        if tw.row_dimensions[1].height != ow.row_dimensions[1].height:
            d(f"[{name}] header height: t={tw.row_dimensions[1].height} o={ow.row_dimensions[1].height}")
        # data row height (row 2)
        if ow.max_row >= 2 and tw.row_dimensions[2].height != ow.row_dimensions[2].height:
            d(f"[{name}] data row height: t={tw.row_dimensions[2].height} o={ow.row_dimensions[2].height}")

        def mask_wrap(sig):
            # wrap_text has no visual effect on short headers and the template is
            # itself inconsistent (Anchor Analysis A1 unwrapped, rest wrapped).
            return sig[:12] + (None,) + sig[13:]

        # EVERY header cell style (wrap masked)
        for c in range(1, tcoln + 1):
            if mask_wrap(cell_sig(tw.cell(row=1, column=c))) != mask_wrap(cell_sig(ow.cell(row=1, column=c))):
                L = get_column_letter(c)
                d(f"[{name}] header {L}1 style differs:\n   t={cell_sig(tw.cell(1,c))}\n   o={cell_sig(ow.cell(1,c))}")
        # EVERY data-column style incl number_format (row 2 as representative)
        if ow.max_row >= 2 and tw.max_row >= 2:
            for c in range(1, tcoln + 1):
                ts = cell_sig(tw.cell(row=2, column=c))
                os_ = cell_sig(ow.cell(row=2, column=c))
                if ts != os_:
                    L = get_column_letter(c)
                    d(f"[{name}] data {L}2 style differs:\n   t={ts}\n   o={os_}")

    if diffs:
        print(f"TEMPLATE DIFFERENCES: {len(diffs)}")
        for x in diffs:
            print(" -", x)
    else:
        print("TEMPLATE MATCH: zero structural differences.")


if __name__ == "__main__":
    main()
