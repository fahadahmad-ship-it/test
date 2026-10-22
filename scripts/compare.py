#!/usr/bin/env python3
"""Structural cell-for-cell comparison of the built workbook against the signed-off template.
Compares layout + styling (not data values). Zero differences = pass.
Usage: compare.py <built.xlsx> <template.xlsx>
"""
import sys, re
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

built = load_workbook(sys.argv[1])
tmpl = load_workbook(sys.argv[2])
diffs = []
def d(msg): diffs.append(msg)

def fkey(c):
    f = c.font
    col = None
    try: col = f.color.rgb if f.color and isinstance(f.color.rgb, str) else None
    except Exception: col = None
    return (f.name, float(f.size or 0), bool(f.bold), col)
def fillkey(c):
    return c.fill.fgColor.rgb if c.fill and c.fill.patternType else None
def bkey(c):
    return ''.join(s[0] for s in ['left', 'right', 'top', 'bottom'] if getattr(c.border, s) and getattr(c.border, s).style)
def akey(c):
    return (c.alignment.horizontal, c.alignment.vertical, bool(c.alignment.wrap_text))

if built.sheetnames != tmpl.sheetnames:
    d(f"sheet names/order differ: {built.sheetnames} vs {tmpl.sheetnames}")

for name in tmpl.sheetnames:
    if name not in built.sheetnames: continue
    b, t = built[name], tmpl[name]
    # gridlines
    if bool(b.sheet_view.showGridLines) != bool(t.sheet_view.showGridLines):
        # openpyxl None == default True
        bg = True if b.sheet_view.showGridLines is None else b.sheet_view.showGridLines
        tg = True if t.sheet_view.showGridLines is None else t.sheet_view.showGridLines
        if bg != tg: d(f"[{name}] gridlines {bg} vs {tg}")
    if name == 'Summary':
        # title B1
        if fkey(b['B1']) != fkey(t['B1']): d(f"[Summary] B1 title style {fkey(b['B1'])} vs {fkey(t['B1'])}")
        if {str(x) for x in b.merged_cells.ranges if 'B1' in str(x)} != {str(x) for x in t.merged_cells.ranges if 'B1' in str(x)}:
            d("[Summary] title merge differs")
        if len(getattr(b, '_images', [])) != len(getattr(t, '_images', [])):
            d(f"[Summary] image count {len(b._images)} vs {len(t._images)}")
        # status table header row 3
        for ci in range(1, 6):
            cb, ct = b.cell(3, ci), t.cell(3, ci)
            if cb.value != ct.value: d(f"[Summary] R3C{ci} header {cb.value!r} vs {ct.value!r}")
            if (fkey(cb), fillkey(cb), akey(cb), bkey(cb)) != (fkey(ct), fillkey(ct), akey(ct), bkey(ct)):
                d(f"[Summary] R3C{ci} header style differs")
        continue
    # data tabs: headers
    for ci in range(1, t.max_column + 1):
        cb, ct = b.cell(1, ci), t.cell(1, ci)
        if cb.value != ct.value: d(f"[{name}] header C{ci} {cb.value!r} vs {ct.value!r}")
        if (fkey(cb), fillkey(cb), akey(cb), bkey(cb)) != (fkey(ct), fillkey(ct), akey(ct), bkey(ct)):
            d(f"[{name}] header C{ci} style: font/fill/align/border {(fkey(cb),fillkey(cb),akey(cb),bkey(cb))} vs {(fkey(ct),fillkey(ct),akey(ct),bkey(ct))}")
    # row heights
    if (b.row_dimensions[1].height, b.row_dimensions[2].height) != (t.row_dimensions[1].height, t.row_dimensions[2].height):
        d(f"[{name}] row heights {(b.row_dimensions[1].height,b.row_dimensions[2].height)} vs {(t.row_dimensions[1].height,t.row_dimensions[2].height)}")
    # freeze
    if b.freeze_panes != t.freeze_panes: d(f"[{name}] freeze {b.freeze_panes} vs {t.freeze_panes}")
    # autofilter end column
    def endcol(ws):
        m = re.search(r':\$?([A-Z]+)\$?\d+', ws.auto_filter.ref or ''); return m.group(1) if m else None
    if endcol(b) != endcol(t): d(f"[{name}] autofilter end-col {endcol(b)} vs {endcol(t)}")
    # column widths
    for ci in range(1, t.max_column + 1):
        L = get_column_letter(ci)
        tw = t.column_dimensions[L].width if L in t.column_dimensions else None
        bw = b.column_dimensions[L].width if L in b.column_dimensions else None
        if tw and (bw is None or abs(bw - tw) > 0.6): d(f"[{name}] col {L} width {bw} vs {tw}")
    # data row2 per-column style
    for ci in range(1, t.max_column + 1):
        cb, ct = b.cell(2, ci), t.cell(2, ci)
        kb = (fkey(cb), fillkey(cb), bkey(cb), cb.alignment.horizontal, cb.alignment.vertical, cb.number_format)
        kt = (fkey(ct), fillkey(ct), bkey(ct), ct.alignment.horizontal, ct.alignment.vertical, ct.number_format)
        if kb != kt: d(f"[{name}] data C{ci} style {kb} vs {kt}")
    # Exact Match dropdowns
    if name == 'Exact Match Anchors':
        def dvs(ws): return sorted((str(dv.type), str(dv.formula1), str(dv.sqref).split(':')[0]) for dv in ws.data_validations.dataValidation)
        bd, td = dvs(b), dvs(t)
        if [(x[0], x[1]) for x in bd] != [(x[0], x[1]) for x in td]:
            d(f"[Exact Match] data validations {bd} vs {td}")

print(f"=== COMPARE vs template: {len(diffs)} difference(s) ===")
for x in diffs: print("  -", x)
print("\nMATCH ✓" if not diffs else f"\n{len(diffs)} DIFFERENCE(S)")
sys.exit(0 if not diffs else 1)
