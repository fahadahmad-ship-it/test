#!/usr/bin/env python3
"""Structural compare of the built workbook vs the signed K&K template.
Ignores data VALUES and row counts; checks layout/style parity."""
import sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
TMPL=sys.argv[1]; OUT=sys.argv[2]
a=load_workbook(TMPL); b=load_workbook(OUT)
issues=[]
def f(c):
    fn=c.font; fl=c.fill
    return (fn.name,fn.sz,bool(fn.bold),(fn.color.rgb if fn.color and isinstance(fn.color.rgb,str) else None),
            (fl.fgColor.rgb if fl.patternType else None),
            c.alignment.horizontal,c.alignment.vertical,bool(c.alignment.wrap_text),
            tuple((getattr(s,'style',None) if s else None) for s in (c.border.left,c.border.right,c.border.top,c.border.bottom)),
            c.number_format)

if a.sheetnames!=b.sheetnames: issues.append(f"SHEET ORDER: tmpl={a.sheetnames} out={b.sheetnames}")
for name in a.sheetnames:
    if name not in b.sheetnames: continue
    wa,wb_=a[name],b[name]
    # gridlines, freeze, filter
    ga=wa.sheet_view.showGridLines; ga=True if ga is None else ga
    gb=wb_.sheet_view.showGridLines; gb=True if gb is None else gb
    if ga!=gb: issues.append(f"{name}: gridlines {ga}!={gb}")
    if wa.freeze_panes!=wb_.freeze_panes: issues.append(f"{name}: freeze {wa.freeze_panes}!={wb_.freeze_panes}")
    if (wa.auto_filter.ref is None)!=(wb_.auto_filter.ref is None):
        issues.append(f"{name}: autofilter presence {wa.auto_filter.ref}!={wb_.auto_filter.ref}")
    # max col
    if wa.max_column!=wb_.max_column: issues.append(f"{name}: ncols {wa.max_column}!={wb_.max_column}")
    # headers row1
    for c in range(1,wa.max_column+1):
        va,vb=wa.cell(1,c).value,wb_.cell(1,c).value
        if name=="Summary" and c==2: continue  # B1 client-name title is intentionally client-specific
        if va!=vb: issues.append(f"{name}!R1C{c}: header {va!r}!={vb!r}")
        if f(wa.cell(1,c))!=f(wb_.cell(1,c)): issues.append(f"{name}!R1C{c} hdr style:\n   tmpl={f(wa.cell(1,c))}\n   out ={f(wb_.cell(1,c))}")
    # column widths
    for c in range(1,wa.max_column+1):
        L=get_column_letter(c)
        xa=round(wa.column_dimensions[L].width or 0,1); xb=round(wb_.column_dimensions[L].width or 0,1)
        if abs(xa-xb)>0.6: issues.append(f"{name}: col {L} width {xa}!={xb}")
    # header height + a data row height
    if (wa.row_dimensions[1].height or 0)!=(wb_.row_dimensions[1].height or 0):
        issues.append(f"{name}: R1 height {wa.row_dimensions[1].height}!={wb_.row_dimensions[1].height}")
    if wa.max_row>=2 and wb_.max_row>=2:
        if (wa.row_dimensions[2].height or 0)!=(wb_.row_dimensions[2].height or 0):
            issues.append(f"{name}: R2 height {wa.row_dimensions[2].height}!={wb_.row_dimensions[2].height}")
        # data cell style (col1 and a numeric col) row2
        if name not in ("Summary",):
            if f(wa.cell(2,1))!=f(wb_.cell(2,1)):
                issues.append(f"{name}!R2C1 data style:\n   tmpl={f(wa.cell(2,1))}\n   out ={f(wb_.cell(2,1))}")
    # images
    if len(getattr(wa,'_images',[]))!=len(getattr(wb_,'_images',[])):
        issues.append(f"{name}: image count {len(wa._images)}!={len(wb_._images)}")

if not issues:
    print("STRUCTURAL MATCH: no differences found.")
else:
    print(f"{len(issues)} structural difference(s):")
    for i in issues: print(" -",i)
