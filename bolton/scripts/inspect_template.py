import sys, openpyxl
path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)
print("=== SHEETS (in order) ===")
for i, ws in enumerate(wb.worksheets, 1):
    dims = ws.dimensions
    mx = ws.max_row, ws.max_column
    print(f"{i}. '{ws.title}'  dims={dims}  max=({mx[0]}r x {mx[1]}c)  "
          f"freeze={ws.freeze_panes}  autofilter={ws.auto_filter.ref}  "
          f"gridlines={ws.sheet_view.showGridLines}")
    if ws.merged_cells.ranges:
        print("   merged:", [str(r) for r in ws.merged_cells.ranges])
    # images
    imgs = getattr(ws, "_images", [])
    if imgs:
        for im in imgs:
            anc = im.anchor
            print("   IMAGE:", type(anc).__name__, "w/h:", getattr(im,'width',None), getattr(im,'height',None))
