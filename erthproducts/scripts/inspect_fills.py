import sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
wb = load_workbook(sys.argv[1])

def desc(c):
    f=c.font; fl=c.fill
    fg=fl.fgColor.rgb if fl and fl.patternType else None
    b=c.border
    sides="".join(k[0] for k in ("left","right","top","bottom") if getattr(b,k) and getattr(b,k).style)
    al=c.alignment
    return f"{f.name},{f.size},b={f.bold},col={f.color.rgb if f.color else None},fill={fg},bd=[{sides}],al={al.horizontal}/{al.vertical},wrap={al.wrap_text}"

# Summary table border check: status table rows 3-10, cols A-E; anchor table rows 20-28
ws=wb["Summary"]
print("== Summary status table borders/fills ==")
for r in [3,4,10]:
    for c in range(1,6):
        print(f"  {get_column_letter(c)}{r}: {desc(ws.cell(row=r,column=c))}")
print("== Summary findings row 12 & heading 11,19 ==")
for ref in [(11,1),(12,1),(19,1),(20,1),(20,4),(21,1)]:
    print(f"  {get_column_letter(ref[1])}{ref[0]}: {desc(ws.cell(row=ref[0],column=ref[1]))}")

# Exact Match Anchors: partner input cols F,G on data rows
ws=wb["Exact Match Anchors"]
print("== EMA input cols F,G (rows 2,3) + A,B ==")
for r in [2,3]:
    for c in [1,2,6,7]:
        print(f"  {get_column_letter(c)}{r}: {desc(ws.cell(row=r,column=c))}")

# Referring Domain Audit: check 'In Disavow'(G) and 'Disavow Line'(Q) data cell fills, + a Status cell
ws=wb["Referring Domain Audit"]
print("== RDA data cells row2 B(Status),G(InDisavow),Q(DisavowLine) ==")
for c in [2,7,17]:
    print(f"  {get_column_letter(c)}2: {desc(ws.cell(row=2,column=c))}")

# Pending Disavow Lines data cell
ws=wb["Pending Disavow Lines"]
print("== Pending Disavow data row2 A,B,C ==")
for c in [1,2,3]:
    print(f"  {get_column_letter(c)}2: {desc(ws.cell(row=2,column=c))}")

# number formats on Summary share col D and RDA numeric cols
ws=wb["Summary"]
print("== Summary D4 (share) number_format:", ws.cell(row=4,column=4).number_format)
ws=wb["Referring Domain Audit"]
print("== RDA C2 (AS) nf:", ws.cell(row=2,column=3).number_format, "| K2 (First Seen) nf:", ws.cell(row=2,column=11).number_format, "value:", repr(ws.cell(row=2,column=11).value))
print("== RDA F2 (Traffic) nf:", ws.cell(row=2,column=6).number_format)
