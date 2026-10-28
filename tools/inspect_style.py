import sys
import openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)

def fmt_font(f):
    if f is None:
        return "-"
    col = f.color.rgb if (f.color and f.color.rgb) else None
    return f"{f.name}/{f.size}/{'B' if f.bold else ''}{'I' if f.italic else ''}/col={col}"

def fmt_fill(c):
    fill = c.fill
    if fill is None or fill.patternType is None:
        return "-"
    fg = fill.fgColor.rgb if fill.fgColor else None
    return f"{fill.patternType}:{fg}"

def fmt_align(a):
    if a is None:
        return "-"
    return f"h={a.horizontal},v={a.vertical},wrap={a.wrap_text}"

def fmt_border(b):
    if b is None:
        return "-"
    def side(s):
        return s.style if (s and s.style) else "."
    return f"L{side(b.left)} R{side(b.right)} T{side(b.top)} B{side(b.bottom)}"

for name in wb.sheetnames:
    ws = wb[name]
    print("=" * 100)
    print(f"SHEET {name!r}  dims={ws.dimensions} gridlines={ws.sheet_view.showGridLines} freeze={ws.freeze_panes}")
    af = ws.auto_filter.ref if ws.auto_filter else None
    print(f"  autofilter={af}  merged={[str(m) for m in ws.merged_cells.ranges]}")
    # column widths
    widths = []
    for col, dim in sorted(ws.column_dimensions.items()):
        if dim.width:
            widths.append(f"{col}={round(dim.width,2)}")
    print(f"  col_widths: {widths}")
    # row heights (first 6 + any custom among first 30)
    heights = []
    for r in range(1, min(ws.max_row, 30) + 1):
        rd = ws.row_dimensions.get(r)
        if rd and rd.height is not None:
            heights.append(f"r{r}={rd.height}")
    print(f"  row_heights(1-30 custom): {heights}")
    # images
    imgs = getattr(ws, "_images", [])
    for im in imgs:
        a = im.anchor
        try:
            frm = a._from
            print(f"  IMAGE from col={frm.col} colOff={frm.colOff} row={frm.row} rowOff={frm.rowOff} ext.cx={a.ext.cx} ext.cy={a.ext.cy}")
        except Exception as e:
            print(f"  IMAGE (anchor {type(a).__name__}) {e}")
    # sample styled cells: header row 1 cols 1..maxcol, and rows 2-3
    maxc = min(ws.max_column, 17)
    for r in [1, 2, 3]:
        if r > ws.max_row:
            continue
        print(f"  --- row {r} styling ---")
        for c in range(1, maxc + 1):
            cell = ws.cell(row=r, column=c)
            if cell.value is None and r > 1:
                continue
            print(f"    {cell.coordinate}: font[{fmt_font(cell.font)}] fill[{fmt_fill(cell)}] align[{fmt_align(cell.alignment)}] bord[{fmt_border(cell.border)}] numfmt={cell.number_format!r}")

# Summary tab full dump with styling
print("\n" + "#" * 100)
print("SUMMARY FULL STYLING A1:E28")
ws = wb["Summary"]
for r in range(1, 29):
    for c in range(1, 6):
        cell = ws.cell(row=r, column=c)
        if cell.value is None and cell.fill.patternType is None:
            continue
        v = str(cell.value).replace("\n", "\\n")[:45] if cell.value is not None else ""
        print(f"  {cell.coordinate}: {v!r} | font[{fmt_font(cell.font)}] fill[{fmt_fill(cell)}] align[{fmt_align(cell.alignment)}] bord[{fmt_border(cell.border)}]")
