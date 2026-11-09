import sys, zipfile
from openpyxl import load_workbook

path = sys.argv[1]
wb = load_workbook(path, data_only=False)
print("=== SHEETS (order) ===")
for i, ws in enumerate(wb.worksheets):
    sv = ws.sheet_view
    print(f"[{i}] '{ws.title}'  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}  "
          f"gridlines={sv.showGridLines}  freeze={ws.freeze_panes}  autofilter={ws.auto_filter.ref}  state={ws.sheet_state}")

print("\n=== IMAGES ===")
for ws in wb.worksheets:
    imgs = getattr(ws, "_images", [])
    if imgs:
        for im in imgs:
            anc = im.anchor
            print(f"sheet='{ws.title}' image w={getattr(im,'width',None)} h={getattr(im,'height',None)} anchor={type(anc).__name__}")

print("\n=== zip media ===")
z = zipfile.ZipFile(path)
for n in z.namelist():
    if "media" in n or "drawing" in n.lower():
        print(n, z.getinfo(n).file_size)
