import sys, openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path)
print("SHEETS:", wb.sheetnames)
for ws in wb.worksheets:
    print("\n" + "="*80)
    print(f"TAB: {ws.title!r}  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}")
    print(f"  freeze={ws.freeze_panes} autofilter={ws.auto_filter.ref} gridlines={ws.sheet_view.showGridLines}")
    print(f"  merged={list(ws.merged_cells.ranges)[:20]}")
    # column widths
    widths = {}
    for col, dim in ws.column_dimensions.items():
        if dim.width:
            widths[col] = round(dim.width,2)
    print(f"  col_widths={widths}")
    # row heights (first 6)
    rh = {r: round(d.height,2) for r,d in ws.row_dimensions.items() if d.height}
    print(f"  row_heights(sample)={dict(list(rh.items())[:8])}")
    # print first 4 rows content
    for r in range(1, min(ws.max_row, 5)+1):
        cells=[]
        for c in range(1, min(ws.max_column, 20)+1):
            v = ws.cell(r,c).value
            if v is not None:
                cells.append(f"{get_column_letter(c)}{r}={v!r}")
        if cells:
            print("   ROW", r, "|".join(cells))
