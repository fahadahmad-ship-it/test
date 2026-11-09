import sys, openpyxl
from openpyxl.utils import get_column_letter
path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)

def fnt(c):
    f = c.font
    return f"{f.name}|{f.size}|b{int(bool(f.bold))}|{(f.color.rgb if f.color else None)}"
def fill(c):
    p = c.fill
    if p and p.patternType:
        return f"{p.patternType}:{(p.fgColor.rgb if p.fgColor else None)}"
    return "none"
def align(c):
    a = c.alignment
    return f"h={a.horizontal},v={a.vertical},wrap={a.wrap_text}"
def bord(c):
    b=c.border
    def s(side): return side.style if side and side.style else "-"
    return f"L{s(b.left)} R{s(b.right)} T{s(b.top)} B{s(b.bottom)}"

ws = wb["Summary"]
print("===== SUMMARY: column widths =====")
for col, d in sorted(ws.column_dimensions.items()):
    print(f"  col {col}: width={d.width}")
print("===== SUMMARY: row heights =====")
for r, d in sorted(ws.row_dimensions.items()):
    print(f"  row {r}: height={d.height}")
print("===== SUMMARY: cells (non-empty) =====")
for row in ws.iter_rows():
    for c in row:
        if c.value is not None:
            v = str(c.value).replace("\n","\\n")
            if len(v) > 90: v = v[:90]+"..."
            print(f"  {c.coordinate}: [{v}]")
            print(f"      font={fnt(c)} fill={fill(c)} align={align(c)} bord={bord(c)}")
