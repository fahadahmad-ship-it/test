"""Structural cell-for-cell comparison of the built workbook vs the signed-off template.
Usage: python3 -I compare.py <built.xlsx> <template.xlsx>
Compares STRUCTURE/STYLING (sheets, order, headers, widths, heights, fonts, fills,
borders, alignment, freeze, filter, gridlines, logo). Client data is expected to differ.
Reports 0 differences on a clean match.
"""
import sys, zipfile
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

built = load_workbook(sys.argv[1])
tmpl = load_workbook(sys.argv[2])
diffs = []

def sstyle(c):
    f = c.font; fl = c.fill
    fg = fl.fgColor.rgb if fl and fl.patternType else None
    b = c.border
    sides = "".join(k[0] for k in ("left","right","top","bottom") if getattr(b,k) and getattr(b,k).style)
    al = c.alignment
    col = None
    try:
        col = f.color.rgb if f.color and isinstance(f.color.rgb, str) else None
    except Exception:
        col = None
    return (f.name, f.size, bool(f.bold), col, fl.patternType, fg, sides,
            al.horizontal, al.vertical, bool(al.wrap_text))

# 1. sheet names + order
if built.sheetnames != tmpl.sheetnames:
    diffs.append(f"SHEET ORDER: built={built.sheetnames} tmpl={tmpl.sheetnames}")

for name in tmpl.sheetnames:
    if name not in built.sheetnames:
        continue
    b = built[name]; t = tmpl[name]
    # gridlines, freeze, filter-start
    if bool(b.sheet_view.showGridLines) != bool(t.sheet_view.showGridLines):
        diffs.append(f"[{name}] gridlines {b.sheet_view.showGridLines} vs {t.sheet_view.showGridLines}")
    if (b.freeze_panes or None) != (t.freeze_panes or None):
        diffs.append(f"[{name}] freeze {b.freeze_panes} vs {t.freeze_panes}")
    bhas = b.auto_filter.ref is not None; thas = t.auto_filter.ref is not None
    if bhas != thas:
        diffs.append(f"[{name}] autofilter present {bhas} vs {thas}")
    # column count via header
    ncol = t.max_column
    # Summary row 1 is the client-name title (handled separately, value is client-specific)
    if name == "Summary":
        continue
    # header row 1 values + style (data tabs)
    for c in range(1, ncol+1):
        bc = b.cell(row=1, column=c); tc = t.cell(row=1, column=c)
        if (bc.value or None) != (tc.value or None):
            diffs.append(f"[{name}] header {get_column_letter(c)}1 value {bc.value!r} vs {tc.value!r}")
        if sstyle(bc) != sstyle(tc):
            diffs.append(f"[{name}] header {get_column_letter(c)}1 style\n     built={sstyle(bc)}\n     tmpl ={sstyle(tc)}")
    # header height
    if (b.row_dimensions[1].height or 0) != (t.row_dimensions[1].height or 0):
        diffs.append(f"[{name}] header height {b.row_dimensions[1].height} vs {t.row_dimensions[1].height}")
    # column widths
    for col, dim in t.column_dimensions.items():
        if dim.width is None:
            continue
        bw = b.column_dimensions[col].width
        if bw is None or abs(bw - dim.width) > 0.3:
            diffs.append(f"[{name}] col {col} width {bw} vs {dim.width}")
    # data-row height + first data cell style (row 2), for data tabs (skip Summary)
    if name != "Summary" and t.max_row >= 2 and b.max_row >= 2:
        if (b.row_dimensions[2].height or 0) != (t.row_dimensions[2].height or 0):
            diffs.append(f"[{name}] data row height {b.row_dimensions[2].height} vs {t.row_dimensions[2].height}")
        bc = b.cell(row=2, column=1); tc = t.cell(row=2, column=1)
        if sstyle(bc) != sstyle(tc):
            diffs.append(f"[{name}] data A2 style\n     built={sstyle(bc)}\n     tmpl ={sstyle(tc)}")

# Summary specifics
b = built["Summary"]; t = tmpl["Summary"]
# title style B1
if sstyle(b.cell(row=1,column=2)) != sstyle(t.cell(row=1,column=2)):
    diffs.append(f"[Summary] title B1 style built={sstyle(b.cell(1,2))} tmpl={sstyle(t.cell(1,2))}")
# merged ranges
bm = sorted(str(x) for x in b.merged_cells.ranges)
tm = sorted(str(x) for x in t.merged_cells.ranges)
if bm != tm:
    diffs.append(f"[Summary] merged ranges\n     built={bm}\n     tmpl ={tm}")
# status table header row 3 + anchor table header row 20 values/styles
for rrow in (3, 20):
    for c in range(1, 6):
        bc=b.cell(row=rrow,column=c); tc=t.cell(row=rrow,column=c)
        if (bc.value or None)!=(tc.value or None):
            diffs.append(f"[Summary] {get_column_letter(c)}{rrow} value {bc.value!r} vs {tc.value!r}")
        if tc.value is not None and sstyle(bc)!=sstyle(tc):
            diffs.append(f"[Summary] {get_column_letter(c)}{rrow} style built={sstyle(bc)} tmpl={sstyle(tc)}")

# logo present on Summary
def has_logo(path):
    z = zipfile.ZipFile(path)
    return any("media/image" in n for n in z.namelist())
if has_logo(sys.argv[1]) != has_logo(sys.argv[2]):
    diffs.append(f"logo image present built={has_logo(sys.argv[1])} tmpl={has_logo(sys.argv[2])}")

print(f"=== STRUCTURAL DIFFERENCES: {len(diffs)} ===")
for d in diffs:
    print(" -", d)
sys.exit(1 if diffs else 0)
