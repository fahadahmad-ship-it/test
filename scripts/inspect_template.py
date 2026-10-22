import sys, json
from openpyxl import load_workbook
p=sys.argv[1]
wb=load_workbook(p)
print("SHEETS (in order):", wb.sheetnames)
for name in wb.sheetnames:
    ws=wb[name]
    print("\n"+"="*72)
    print(f"TAB: {name!r}  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}")
    print(f"  freeze_panes={ws.freeze_panes}  autofilter={ws.auto_filter.ref}  gridlines={ws.sheet_view.showGridLines}")
    print(f"  merged={[str(m) for m in ws.merged_cells.ranges][:8]}")
    print(f"  images={len(getattr(ws,'_images',[]))}")
    # column widths
    widths={k:round(v.width,1) for k,v in ws.column_dimensions.items() if v.width}
    print(f"  col widths={widths}")
    # row heights (first 4)
    rh={k:v.height for k,v in list(ws.row_dimensions.items())[:6] if v.height}
    print(f"  row heights(sample)={rh}")
    # header row values (row 1)
    hdr=[ws.cell(1,c).value for c in range(1,ws.max_column+1)]
    print(f"  ROW1 values={hdr}")
    # if row1 empty (summary title), show first non-empty rows
    if all(v is None for v in hdr):
        for r in range(1,8):
            vals=[ws.cell(r,c).value for c in range(1,min(ws.max_column,8)+1)]
            if any(v is not None for v in vals):
                print(f"    row{r}: {vals}")
