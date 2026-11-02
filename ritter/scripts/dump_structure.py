import sys, openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)
print("SHEETS:", wb.sheetnames)
for ws in wb.worksheets:
    print("\n" + "=" * 90)
    print(f"TAB: {ws.title!r}  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}")
    print(f"  freeze={ws.freeze_panes}  autofilter={ws.auto_filter.ref}  showGridLines={ws.sheet_view.showGridLines}")
    # column widths
    widths = {}
    for col, dim in ws.column_dimensions.items():
        if dim.width:
            widths[col] = round(dim.width, 2)
    print("  widths:", widths)
    # row heights (first 6 distinct)
    heights = {}
    for r, dim in ws.row_dimensions.items():
        if dim.height:
            heights[r] = dim.height
    print("  row_heights(sample):", dict(list(heights.items())[:12]))
    # merged
    print("  merged:", [str(m) for m in ws.merged_cells.ranges][:20])
    # print first ~6 rows of values
    nrows = min(ws.max_row, 8)
    ncols = min(ws.max_column, 20)
    for r in range(1, nrows + 1):
        rowvals = []
        for c in range(1, ncols + 1):
            v = ws.cell(row=r, column=c).value
            if v is not None:
                sv = str(v).replace("\n", "\\n")
                if len(sv) > 32:
                    sv = sv[:32] + "…"
                rowvals.append(f"{get_column_letter(c)}{r}={sv}")
        if rowvals:
            print("   ", " | ".join(rowvals))
