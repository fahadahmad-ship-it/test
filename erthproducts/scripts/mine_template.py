import sys, zipfile, collections
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

path = sys.argv[1]
wb = load_workbook(path)

# ---- 1. Summary full content ----
ws = wb["Summary"]
print("===== SUMMARY CONTENT (non-empty cells rows 1-28) =====")
for r in range(1, 29):
    for c in range(1, 6):
        cell = ws.cell(row=r, column=c)
        if cell.value not in (None, ""):
            f = cell.font
            fillc = cell.fill.fgColor.rgb if cell.fill and cell.fill.patternType else None
            print(f"  {get_column_letter(c)}{r} [{f.name},{f.size},b={f.bold},{f.color.rgb if f.color else None},fill={fillc}] = {repr(cell.value)[:160]}")

# ---- 2. Status distribution (Referring Domain Audit col B) ----
ws = wb["Referring Domain Audit"]
statuses = collections.Counter()
indis = collections.Counter()
for r in range(2, ws.max_row+1):
    s = ws.cell(row=r, column=2).value
    if s is not None:
        statuses[s]+=1
    g = ws.cell(row=r, column=7).value  # In Disavow
    indis[g]+=1
print("\n===== Referring Domain Audit: STATUS counts =====")
for k,v in statuses.most_common(): print(f"  {v:5d}  {k}")
print("  In Disavow values:", dict(indis))
print("  total data rows:", ws.max_row-1)

# ---- 3. Anchor Analysis: distinct Anchor Type ----
ws = wb["Anchor Analysis"]
at = collections.Counter()
for r in range(2, ws.max_row+1):
    v = ws.cell(row=r, column=2).value
    if v is not None: at[v]+=1
print("\n===== Anchor Analysis: distinct Anchor Type =====")
for k,v in at.most_common(): print(f"  {v:5d}  {k}")

# ---- 4. Disavow List sample + grouping (col A disavow line, G top anchor) ----
ws = wb["Disavow List"]
print("\n===== Disavow List: first 12 + last 4 rows (A,B,C,D,E,F,G) =====")
rows = list(range(2, min(14, ws.max_row+1))) + list(range(max(2,ws.max_row-3), ws.max_row+1))
for r in rows:
    vals = [ws.cell(row=r, column=c).value for c in range(1,8)]
    print(f"  r{r}:", vals)

# ---- 5. Pending Disavow Lines sample ----
ws = wb["Pending Disavow Lines"]
print("\n===== Pending Disavow Lines: first 8 rows =====")
for r in range(2, min(10, ws.max_row+1)):
    print(f"  r{r}:", [ws.cell(row=r, column=c).value for c in range(1,4)])
print("  total:", ws.max_row-1)

# ---- 6. Exact Match Anchors distinct Market / Site type / Final decision ----
ws = wb["Exact Match Anchors"]
mk = collections.Counter(); st = collections.Counter(); fd = collections.Counter()
for r in range(2, ws.max_row+1):
    mk[ws.cell(row=r,column=4).value]+=1
    st[ws.cell(row=r,column=5).value]+=1
    fd[ws.cell(row=r,column=7).value]+=1
print("\n===== Exact Match Anchors =====  total:", ws.max_row-1)
print("  Market:", dict(mk))
print("  Site type:", dict(st.most_common(12)))
print("  Final decision:", dict(fd))
print("  sample rows:")
for r in range(2, min(6, ws.max_row+1)):
    print("   ", [ws.cell(row=r,column=c).value for c in range(1,8)])

# ---- 7. extract logo + drawing anchor ----
z = zipfile.ZipFile(path)
with open("/home/user/test/erthproducts/data/harbinger_logo.png","wb") as fh:
    fh.write(z.read("xl/media/image1.png"))
import re
d = z.read("xl/drawings/drawing1.xml").decode("utf8","replace")
print("\n===== drawing1.xml (logo anchor) =====")
print(d[:1200])
