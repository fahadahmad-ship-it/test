import sys, openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)
print("SHEETS:", wb.sheetnames)
for ws in wb.worksheets:
    print("\n" + "="*80)
    print(f"TAB: {ws.title!r}  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}")
    print(f"  freeze_panes={ws.freeze_panes}  auto_filter={ws.auto_filter.ref}  gridlines={ws.sheet_view.showGridLines}")
    # column widths
    widths = {}
    for col, dim in ws.column_dimensions.items():
        if dim.width:
            widths[col] = round(dim.width,2)
    print("  col_widths:", widths)
    # row heights (first 10)
    rh = {}
    for r, dim in ws.row_dimensions.items():
        if dim.height:
            rh[r] = dim.height
    print("  row_heights(sample):", dict(list(sorted(rh.items()))[:12]))
    # merged
    print("  merged:", [str(m) for m in ws.merged_cells.ranges])
    # print first ~6 rows of values
    for r in range(1, min(ws.max_row, 8)+1):
        rowvals = []
        for c in range(1, min(ws.max_column, 20)+1):
            v = ws.cell(row=r, column=c).value
            if v is not None:
                rowvals.append(f"{get_column_letter(c)}{r}={v!r}")
        if rowvals:
            print("   ", " | ".join(rowvals))
