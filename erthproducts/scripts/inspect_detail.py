import sys, zipfile
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = load_workbook(path)

def fdesc(c):
    f = c.font
    fill = c.fill
    fg = None
    if fill and fill.patternType:
        fg = fill.fgColor.rgb
    b = c.border
    sides = "".join(k[0] for k in ("left","right","top","bottom") if getattr(b,k) and getattr(b,k).style)
    al = c.alignment
    return (f"font={f.name},{f.size},b={f.bold},color={f.color.rgb if f.color else None} "
            f"fill={fill.patternType}:{fg} border=[{sides}] "
            f"align={al.horizontal}/{al.vertical},wrap={al.wrap_text}")

for ws in wb.worksheets:
    print(f"\n########## '{ws.title}' ##########")
    # column widths
    widths = {}
    for col, dim in ws.column_dimensions.items():
        if dim.width is not None:
            widths[col] = round(dim.width,2)
    print("col_widths:", widths)
    print("default_row_height:", ws.sheet_format.defaultRowHeight)
    # header row 1
    hr = ws.row_dimensions[1].height
    print(f"row1_height={hr}")
    hdr = []
    for cc in range(1, ws.max_column+1):
        c = ws.cell(row=1, column=cc)
        hdr.append(f"{get_column_letter(cc)}1='{c.value}' | {fdesc(c)}")
    print("HEADER:")
    for h in hdr: print("  ", h)
    # first 2 data rows style + heights
    for r in (2,3):
        if r <= ws.max_row:
            rh = ws.row_dimensions[r].height
            c = ws.cell(row=r, column=1)
            print(f"row{r}_height={rh}  A{r}style: {fdesc(c)}")
    # merged
    if ws.merged_cells.ranges:
        print("merged:", [str(m) for m in ws.merged_cells.ranges])
