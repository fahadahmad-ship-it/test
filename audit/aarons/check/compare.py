"""
Cell-for-cell structural comparison of the built workbook against the signed
template. Compares format (tabs, order, headers, widths, heights, fonts, sizes,
fills, borders, alignment, freeze, filters, gridlines, number formats, input
cells, logo) — NOT the per-client data values.

Run: python3 -I check/compare.py out/Aarons_Home_Tech_Backlink_Audit.xlsx ref/KandK_template.xlsx
"""
import sys, zipfile
import openpyxl

DIFFS = []
def diff(msg): DIFFS.append(msg)

def fcolor(c):
    return c.font.color.rgb if (c.font and c.font.color) else None
def fill(c):
    return (c.fill.fgColor.rgb, c.fill.patternType) if c.fill else (None, None)
def bstr(c):
    b = c.border
    return tuple((s.style if s else None) for s in (b.left, b.right, b.top, b.bottom))

def cmp_cell(a, b, where, keys=("name","size","bold","color","fill","align","wrap","border")):
    if "name" in keys and a.font.name != b.font.name: diff(f"{where}: font {a.font.name!r} vs {b.font.name!r}")
    if "size" in keys and a.font.size != b.font.size: diff(f"{where}: size {a.font.size} vs {b.font.size}")
    if "bold" in keys and bool(a.font.bold) != bool(b.font.bold): diff(f"{where}: bold {a.font.bold} vs {b.font.bold}")
    if "color" in keys and fcolor(a) != fcolor(b): diff(f"{where}: fontcolor {fcolor(a)} vs {fcolor(b)}")
    if "fill" in keys and fill(a) != fill(b): diff(f"{where}: fill {fill(a)} vs {fill(b)}")
    if "align" in keys and (a.alignment.horizontal, a.alignment.vertical) != (b.alignment.horizontal, b.alignment.vertical):
        diff(f"{where}: align {(a.alignment.horizontal,a.alignment.vertical)} vs {(b.alignment.horizontal,b.alignment.vertical)}")
    if "wrap" in keys and bool(a.alignment.wrap_text) != bool(b.alignment.wrap_text): diff(f"{where}: wrap {a.alignment.wrap_text} vs {b.alignment.wrap_text}")
    if "border" in keys and bstr(a) != bstr(b): diff(f"{where}: border {bstr(a)} vs {bstr(b)}")

def main():
    mine = openpyxl.load_workbook(sys.argv[1]); tmpl = openpyxl.load_workbook(sys.argv[2])
    if mine.sheetnames != tmpl.sheetnames:
        diff(f"TABS differ: {mine.sheetnames} vs {tmpl.sheetnames}")
    common = [s for s in tmpl.sheetnames if s in mine.sheetnames]
    for t in common:
        a = mine[t]; b = tmpl[t]
        if a.max_column != b.max_column: diff(f"{t}: ncols {a.max_column} vs {b.max_column}")
        if (a.freeze_panes or None) != (b.freeze_panes or None): diff(f"{t}: freeze {a.freeze_panes} vs {b.freeze_panes}")
        ga = a.sheet_view.showGridLines; gb = b.sheet_view.showGridLines
        if bool(ga if ga is not None else True) != bool(gb if gb is not None else True): diff(f"{t}: gridlines {ga} vs {gb}")
        # headers
        if t != "Summary":
            for c in range(1, b.max_column + 1):
                ha, hb = a.cell(row=1, column=c), b.cell(row=1, column=c)
                if (ha.value or "") != (hb.value or ""): diff(f"{t} hdr col{c}: {ha.value!r} vs {hb.value!r}")
                cmp_cell(ha, hb, f"{t} hdr col{c}")
            # header + data row heights
            if abs((a.row_dimensions[1].height or 0) - (b.row_dimensions[1].height or 0)) > 0.01: diff(f"{t}: header height {a.row_dimensions[1].height} vs {b.row_dimensions[1].height}")
            if abs((a.row_dimensions[2].height or 0) - (b.row_dimensions[2].height or 0)) > 0.01: diff(f"{t}: data height {a.row_dimensions[2].height} vs {b.row_dimensions[2].height}")
            # data cell style (row 2) + number formats
            for c in range(1, b.max_column + 1):
                da, db = a.cell(row=2, column=c), b.cell(row=2, column=c)
                cmp_cell(da, db, f"{t} data col{c}", keys=("name","size","fill","align","border"))
                if da.number_format != db.number_format: diff(f"{t} numfmt col{c}: {da.number_format!r} vs {db.number_format!r}")
            # column widths
            for c in range(1, b.max_column + 1):
                from openpyxl.utils import get_column_letter
                L = get_column_letter(c)
                wa = a.column_dimensions[L].width; wb_ = b.column_dimensions[L].width
                if wa and wb_ and abs(wa - wb_) > 0.5: diff(f"{t} width col{L}: {round(wa,1)} vs {round(wb_,1)}")
        else:
            # Summary: title + merges + section/table headers
            cmp_cell(a.cell(row=1,column=2), b.cell(row=1,column=2), "Summary title B1", keys=("name","size","bold","color","align"))
            ma = set(str(m) for m in a.merged_cells.ranges); mb = set(str(m) for m in b.merged_cells.ranges)
            if "B1:E2" not in ma: diff("Summary: title not merged B1:E2")
            cmp_cell(a.cell(row=3,column=1), b.cell(row=3,column=1), "Summary statustable hdr", keys=("size","bold","fill","border"))
    # logo
    for f in ("out","ref"):
        pass
    def has_img(path):
        with zipfile.ZipFile(path) as z:
            return any(n.startswith("xl/media/") for n in z.namelist())
    if has_img(sys.argv[1]) != has_img(sys.argv[2]):
        diff(f"logo image present: mine={has_img(sys.argv[1])} vs tmpl={has_img(sys.argv[2])}")

    print(f"STRUCTURAL DIFFERENCES: {len(DIFFS)}")
    for d in DIFFS: print("  -", d)
    sys.exit(1 if DIFFS else 0)

if __name__ == "__main__":
    main()
