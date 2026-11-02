import sys, json
import openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)

def cellinfo(ws, coord):
    c = ws[coord]
    f = c.font; fill = c.fill; al = c.alignment; b = c.border
    def side(s): return s.style if s and s.style else None
    def rgb(x):
        try: return str(x) if x is not None else None
        except Exception: return None
    return {
        "coord": coord,
        "val": (str(c.value)[:70] if c.value is not None else None),
        "font": f.name, "sz": f.size, "bold": f.bold, "color": rgb(f.color.rgb if f.color else None),
        "fill": rgb(fill.fgColor.rgb if fill and fill.patternType else None),
        "patt": fill.patternType if fill else None,
        "halign": al.horizontal, "valign": al.vertical, "wrap": al.wrap_text,
        "border": {k: side(getattr(b, k)) for k in ("left","right","top","bottom")},
        "numfmt": c.number_format,
    }

# Full Summary text (untruncated), columns A-E rows 1-30
summ = wb.worksheets[0]
print("### FULL SUMMARY TEXT ###")
for r in range(1, 30):
    for col in range(1,6):
        v = summ.cell(row=r, column=col).value
        if v is not None:
            print(f"{get_column_letter(col)}{r}\t{v!r}")

print("\n### SUMMARY KEY CELL STYLES ###")
for coord in ["B1","A3","B3","E3","A4","B4","D4","A10","A11","A12","A19","A20","A21"]:
    print(json.dumps(cellinfo(summ, coord)))

print("\n### SUMMARY ROW HEIGHTS ###")
for r in range(1, 29):
    rd = summ.row_dimensions[r]
    print(f"row {r}: height={rd.height}")
print("### SUMMARY COL WIDTHS ###")
for col in range(1,7):
    cd = summ.column_dimensions[get_column_letter(col)]
    print(f"col {get_column_letter(col)}: width={cd.width}")

# Per data tab: headers, widths, first data row style, row heights
for idx in range(1, len(wb.worksheets)):
    ws = wb.worksheets[idx]
    print(f"\n### TAB [{idx}] {ws.title} ###")
    hdr = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column+1)]
    print("HEADERS:", hdr)
    print("header A1 style:", json.dumps(cellinfo(ws,"A1")))
    print("data  A2 style:", json.dumps(cellinfo(ws,"A2")))
    # column widths
    widths = {get_column_letter(c): ws.column_dimensions[get_column_letter(c)].width for c in range(1, ws.max_column+1)}
    print("WIDTHS:", widths)
    print("row1 height:", ws.row_dimensions[1].height, " row2 height:", ws.row_dimensions[2].height, " row3 height:", ws.row_dimensions[3].height)
    # sample a couple data rows fully
    print("sample row2:", [ws.cell(row=2, column=c).value for c in range(1, ws.max_column+1)])
    print("sample row3:", [ws.cell(row=3, column=c).value for c in range(1, ws.max_column+1)])
