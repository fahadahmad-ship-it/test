"""Compare the K&K workbook against the client's signed-off New Image Canopy file.

Anything structural that differs is listed. Differences in the DATA are expected and are
ignored; differences in layout, wording of headers, widths, heights, fills, fonts,
alignment, freeze panes, filters and gridlines are not.
"""
import openpyxl, sys, collections
A = '/home/user/test/New_Image_Canopy_Backlinks_Audit.xlsx'   # the signed-off template
B = '/home/user/test/KandK_Manufacturing_Backlinks_Audit.xlsx'
wa = openpyxl.load_workbook(A); wb = openpyxl.load_workbook(B)
diffs = []
def d(msg): diffs.append(msg); print('  DIFF ' + msg)
def ok(msg): print('  ok   ' + msg)

print('\n== tabs ==')
if wa.sheetnames == wb.sheetnames: ok(f'same seven tabs in the same order')
else: d(f'tab list\n        template: {wa.sheetnames}\n        K&K:      {wb.sheetnames}')

for n in wa.sheetnames:
    if n not in wb.sheetnames: continue
    sa, sb = wa[n], wb[n]
    print(f'\n== {n} ==')
    # header row text
    ha = [c.value for c in sa[1]]
    hb = [c.value for c in sb[1]]
    if n == 'Summary':
        pass
    elif ha == hb: ok(f'{len(ha)} column headers identical')
    else:
        for i, (x, y) in enumerate(zip(ha, hb)):
            if x != y: d(f'header col {i+1}: template {x!r} vs K&K {y!r}')
        if len(ha) != len(hb): d(f'column count {len(ha)} vs {len(hb)}')
    # widths
    wda = {k: round(v.width, 2) for k, v in sa.column_dimensions.items() if v.width}
    wdb = {k: round(v.width, 2) for k, v in sb.column_dimensions.items() if v.width}
    if wda == wdb: ok(f'column widths identical ({len(wda)} set)')
    else:
        for k in sorted(set(wda) | set(wdb)):
            if wda.get(k) != wdb.get(k): d(f'width {k}: template {wda.get(k)} vs K&K {wdb.get(k)}')
    # freeze / filter / gridlines
    if sa.freeze_panes != sb.freeze_panes: d(f'freeze panes {sa.freeze_panes} vs {sb.freeze_panes}')
    else: ok(f'freeze panes {sa.freeze_panes}')
    fa = bool(sa.auto_filter.ref); fb = bool(sb.auto_filter.ref)
    if fa != fb: d(f'autofilter present {fa} vs {fb}')
    else: ok(f'autofilter {fa}')
    if sa.sheet_view.showGridLines != sb.sheet_view.showGridLines:
        d(f'gridlines {sa.sheet_view.showGridLines} vs {sb.sheet_view.showGridLines}')
    else: ok(f'gridlines {sa.sheet_view.showGridLines}')
    # header row style
    for i in range(1, min(len(ha), len(hb)) + 1):
        ca, cb = sa.cell(1, i), sb.cell(1, i)
        for attr, get in (('font name', lambda c: c.font.name), ('font size', lambda c: c.font.sz),
                          ('bold', lambda c: c.font.b),
                          ('font colour', lambda c: c.font.color.rgb if c.font.color else None),
                          ('fill', lambda c: c.fill.fgColor.rgb if c.fill and c.fill.fgColor else None),
                          ('h align', lambda c: c.alignment.horizontal),
                          ('v align', lambda c: c.alignment.vertical),
                          ('wrap', lambda c: c.alignment.wrap_text)):
            if get(ca) != get(cb): d(f'header col {i} {attr}: {get(ca)!r} vs {get(cb)!r}')
    # row heights
    ra = sa.row_dimensions[1].height; rb = sb.row_dimensions[1].height
    if ra != rb: d(f'header row height {ra} vs {rb}')
    else: ok(f'header row height {ra}')
    if n != 'Summary':
        ha2 = sa.row_dimensions[2].height if 2 in sa.row_dimensions else None
        hb2 = sb.row_dimensions[2].height if 2 in sb.row_dimensions else None
        if ha2 != hb2: d(f'data row height {ha2} vs {hb2}')
        else: ok(f'data row height {ha2}')
    # first data row style
    if sa.max_row > 1 and sb.max_row > 1:
        for i in range(1, min(len(ha), len(hb)) + 1):
            ca, cb = sa.cell(2, i), sb.cell(2, i)
            for attr, get in (('font name', lambda c: c.font.name), ('font size', lambda c: c.font.sz),
                              ('fill', lambda c: c.fill.fgColor.rgb if c.fill and c.fill.fgColor else None),
                              ('h align', lambda c: c.alignment.horizontal),
                              ('v align', lambda c: c.alignment.vertical),
                              ('number format', lambda c: c.number_format),
                              ('border', lambda c: (c.border.left.style, c.border.top.style))):
                if get(ca) != get(cb): d(f'data row col {i} ({hb[i-1]}) {attr}: {get(ca)!r} vs {get(cb)!r}')
    # data validation
    va = sorted(str(v.formula1) for v in sa.data_validations.dataValidation)
    vb = sorted(str(v.formula1) for v in sb.data_validations.dataValidation)
    if va != vb: d(f'data validation lists {va} vs {vb}')
    elif va: ok(f'data validation {va}')

print('\n== Summary layout ==')
sa, sb = wa['Summary'], wb['Summary']
print(f'  template rows {sa.max_row}, K&K rows {sb.max_row}')
for r in range(1, max(sa.max_row, sb.max_row) + 1):
    x = sa.cell(r, 1).value; y = sb.cell(r, 1).value
    lx = (str(x)[:46] + '...') if x and len(str(x)) > 46 else x
    ly = (str(y)[:46] + '...') if y and len(str(y)) > 46 else y
    print(f'  {r:3d}  {str(lx):52s} | {ly}')
print('  merges: template', len(sa.merged_cells.ranges), 'K&K', len(sb.merged_cells.ranges))

print('\n' + (f'{len(diffs)} STRUCTURAL DIFFERENCE(S)' if diffs else 'NO STRUCTURAL DIFFERENCES'))
