import sys, zipfile, os, openpyxl
from openpyxl.utils import get_column_letter

src = sys.argv[1]
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

# 1) extract embedded images
with zipfile.ZipFile(src) as z:
    for name in z.namelist():
        if name.startswith("xl/media/"):
            data = z.read(name)
            base = os.path.basename(name)
            with open(os.path.join(outdir, base), "wb") as fh:
                fh.write(data)
            print(f"IMAGE {name} -> {outdir}/{base} ({len(data)} bytes)")

# 2) detailed Summary styling
wb = openpyxl.load_workbook(src)
ws = wb["Summary"]
print("\nSUMMARY cell styles (non-empty):")
def fc(c):
    f = c.font
    fill = c.fill
    fg = fill.fgColor.rgb if fill and fill.patternType else None
    al = c.alignment
    b = c.border
    def s(x): return x.style if x and x.style else "-"
    return (f"sz={f.size} b={int(bool(f.bold))} color={f.color.rgb if f.color and isinstance(f.color.rgb,str) else '-'} "
            f"fill={fg} h={al.horizontal} v={al.vertical} wrap={int(bool(al.wrap_text))} "
            f"bord={s(b.left)}/{s(b.right)}/{s(b.top)}/{s(b.bottom)} numfmt={c.number_format}")
for r in range(1, ws.max_row + 1):
    for cc in range(1, 6):
        c = ws.cell(row=r, column=cc)
        if c.value is not None:
            print(f"  {get_column_letter(cc)}{r} {fc(c)}  val={str(c.value)[:44]!r}")
print("\nSummary merged:", [str(m) for m in ws.merged_cells.ranges])
print("Summary col widths:", {k: round(v.width,2) for k,v in ws.column_dimensions.items() if v.width})
print("Summary gridlines:", ws.sheet_view.showGridLines)
# row heights distinct
hh = {}
for r,dim in ws.row_dimensions.items():
    if dim.height: hh[r]=dim.height
print("Summary row heights:", hh)

# 3) confirm data-tab header vs data styling on one tab + numeric alignment
for tab in ["Referring Domain Audit", "Disavow List"]:
    ws2 = wb[tab]
    print(f"\n[{tab}] numeric-cell alignment check:")
    for addr in ["C2","D2","E2","F2","B2"]:
        c = ws2[addr]
        print(f"  {addr} val={str(c.value)[:16]!r} h={c.alignment.horizontal} numfmt={c.number_format}")
