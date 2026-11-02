import sys, zipfile, re
import openpyxl
from openpyxl.utils import get_column_letter
path = sys.argv[1]
wb = openpyxl.load_workbook(path)

def nf(ws, coord):
    c = ws[coord]; return c.number_format

rda = wb["Referring Domain Audit"]
print("RDA K2 (First Seen) numfmt:", nf(rda,"K2"), "val:", rda["K2"].value)
print("RDA C2 (AS) numfmt:", nf(rda,"C2"), " D2 (Backlinks):", nf(rda,"D2"), " F2 (Traffic):", nf(rda,"F2"))
aa = wb["Anchor Analysis"]
print("AnchorAnalysis D2 (Share) numfmt:", nf(aa,"D2"))
summ = wb["Summary"]
print("Summary C21 (Share Backlinks) numfmt:", nf(summ,"C21"), " D21:", nf(summ,"D21"))
print("Summary D4 numfmt:", nf(summ,"D4"))
ema = wb["Exact Match Anchors"]
for coord in ["F2","G2","F3","G3"]:
    c = ema[coord]; fill = c.fill
    print(f"EMA {coord}: val={c.value!r} fill={(fill.fgColor.rgb if fill and fill.patternType else None)} fontcolor={c.font.color.rgb if c.font.color else None}")

# data validations per sheet
print("\n### DATA VALIDATIONS ###")
for ws in wb.worksheets:
    dvs = ws.data_validations.dataValidation
    if dvs:
        for dv in dvs:
            print(f"{ws.title}: type={dv.type} formula1={dv.formula1} ranges={dv.sqref}")

# zip contents: media + drawings
print("\n### ZIP MEDIA / DRAWINGS ###")
z = zipfile.ZipFile(path)
for n in z.namelist():
    if "media" in n or "drawing" in n.lower():
        print(n, z.getinfo(n).file_size)
# dump the drawing xml for summary to get anchor
for n in z.namelist():
    if re.search(r"drawings/drawing\d+\.xml$", n):
        print(f"\n--- {n} ---")
        print(z.read(n).decode("utf-8", "ignore")[:1500])
