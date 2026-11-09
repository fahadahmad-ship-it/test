import sys, openpyxl
from openpyxl.utils import get_column_letter
wb = openpyxl.load_workbook(sys.argv[1], data_only=False)
def fnt(c):
    f=c.font; return f"{f.name}|{f.size}|b{int(bool(f.bold))}|{(f.color.rgb if f.color else None)}"
def fill(c):
    p=c.fill
    return f"{p.patternType}:{(p.fgColor.rgb if p.fgColor else None)}" if p and p.patternType else "none"
def al(c):
    a=c.alignment; return f"h={a.horizontal},v={a.vertical},wrap={a.wrap_text}"
def bd(c):
    b=c.border
    def s(x): return x.style if x and x.style else "-"
    return f"L{s(b.left)} R{s(b.right)} T{s(b.top)} B{s(b.bottom)}"
for ws in wb.worksheets:
    if ws.title=="Summary": continue
    print(f"\n########## {ws.title}  (maxcol={ws.max_column}) ##########")
    print("col widths:", {get_column_letter(i): round(ws.column_dimensions[get_column_letter(i)].width,2) if ws.column_dimensions[get_column_letter(i)].width else None for i in range(1, ws.max_column+1)})
    print("row heights r1-3:", {r: ws.row_dimensions[r].height for r in (1,2,3)})
    print("-- HEADER row 1 --")
    for i in range(1, ws.max_column+1):
        c=ws.cell(1,i)
        print(f"  {c.coordinate} [{c.value}]  f={fnt(c)} fill={fill(c)} al={al(c)} bd={bd(c)} nf={c.number_format}")
    print("-- DATA row 2 --")
    for i in range(1, ws.max_column+1):
        c=ws.cell(2,i)
        v=str(c.value); v=v[:40]+"..." if len(v)>40 else v
        print(f"  {c.coordinate} [{v}]  f={fnt(c)} fill={fill(c)} al={al(c)} bd={bd(c)} nf={c.number_format}")
