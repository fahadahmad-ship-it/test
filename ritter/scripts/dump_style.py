import sys, openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path)

def cellfmt(c):
    f = c.font
    fill = c.fill
    fg = fill.fgColor.rgb if fill and fill.patternType else None
    b = c.border
    def side(s): return s.style if s and s.style else None
    borders = f"L{side(b.left)} R{side(b.right)} T{side(b.top)} B{side(b.bottom)}"
    al = c.alignment
    return (f"font={f.name} sz={f.size} bold={f.bold} color={f.color.rgb if f.color else None} | "
            f"fill={fill.patternType}:{fg} | {borders} | "
            f"align(h={al.horizontal},v={al.vertical},wrap={al.wrap_text}) | numfmt={c.number_format!r}")

for ws in wb.worksheets:
    print("\n" + "=" * 100)
    print(f"TAB {ws.title!r}")
    # header row 1 cell A1 and B1
    for addr in ["A1", "B1", "A2", "B2"]:
        c = ws[addr]
        if c.value is not None or addr in ("A1","A2"):
            print(f"  {addr} val={str(c.value)[:30]!r:34} {cellfmt(c)}")
    # images
    imgs = getattr(ws, "_images", [])
    for im in imgs:
        anc = im.anchor
        try:
            frm = anc._from
            print(f"  IMAGE: {getattr(im,'path',getattr(im,'ref','?'))} w={im.width} h={im.height} "
                  f"from(col={frm.col},colOff={frm.colOff},row={frm.row},rowOff={frm.rowOff})")
            if hasattr(anc, "ext"):
                print(f"         ext cx={anc.ext.cx} cy={anc.ext.cy}")
        except Exception as e:
            print("  IMAGE(anchor parse err)", e)

print("\n\n##### SUMMARY FULL TEXT (rows 1-30) #####")
ws = wb["Summary"]
for r in range(1, 31):
    for c in range(1, 6):
        cell = ws.cell(row=r, column=c)
        if cell.value is not None:
            print(f"  {get_column_letter(c)}{r}: {str(cell.value)!r}")
