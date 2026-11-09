"""
compare.py — structural, cell-for-cell comparison of the Bolton workbook against the
signed-off K&K template. Compares STRUCTURE + STYLING (tabs, order, headers, widths,
heights, fonts, sizes, fills, borders, alignment, number formats, freeze panes, filters,
gridlines, merges, logo) — NOT row counts or data values (those legitimately differ).

Usage: python3 -I bolton/check/compare.py <template.xlsx> <output.xlsx>
Exit 0 and "ZERO structural differences" when clean.
"""
import sys, openpyxl
from openpyxl.utils import get_column_letter

def fstyle(c):
    f=c.font; col = f.color.rgb if (f.color and f.color.type=='rgb') else None
    return (f.name, float(f.size or 0), bool(f.bold), col)
def fillstyle(c):
    p=c.fill
    if p and p.patternType: return (p.patternType, p.fgColor.rgb if p.fgColor else None)
    return ('none', None)
def align(c):
    a=c.alignment; return (a.horizontal, a.vertical, bool(a.wrap_text))
def border(c):
    b=c.border
    def s(x): return x.style if (x and x.style) else None
    return (s(b.left), s(b.right), s(b.top), s(b.bottom))

def hrow(ws): return ws.row_dimensions[1].height
def drow(ws,r=2): return ws.row_dimensions[r].height

def main(tpl_path, out_path):
    tpl = openpyxl.load_workbook(tpl_path)
    out = openpyxl.load_workbook(out_path)
    diffs = []
    # 1. sheet order/names
    if tpl.sheetnames != out.sheetnames:
        diffs.append(f"SHEET ORDER: template={tpl.sheetnames} output={out.sheetnames}")
        print('\n'.join(diffs)); print(f"{len(diffs)} structural differences"); return 1
    for name in tpl.sheetnames:
        t, o = tpl[name], out[name]
        if name == 'Summary':
            # gridlines off
            if bool(o.sheet_view.showGridLines) != False:
                diffs.append("Summary: gridlines should be OFF")
            # merges
            for mg in ['B1:E2','A12:E12','A18:E18']:
                if mg not in [str(r) for r in o.merged_cells.ranges]:
                    diffs.append(f"Summary: missing merge {mg}")
            # logo
            if not getattr(o, '_images', []):
                diffs.append("Summary: logo image missing")
            # title style
            if fstyle(o['B1'])[:3] != ('Geist',21.0,True):
                diffs.append(f"Summary B1 title style {fstyle(o['B1'])} != ('Geist',21,True)")
            # status header row 3 style vs template
            for col in range(1,6):
                tc,oc = t.cell(3,col), o.cell(3,col)
                if tc.value != oc.value:
                    diffs.append(f"Summary R3C{col} header '{oc.value}' != '{tc.value}'")
                if fstyle(oc)!=fstyle(tc): diffs.append(f"Summary R3C{col} font {fstyle(oc)}!={fstyle(tc)}")
                if fillstyle(oc)!=fillstyle(tc): diffs.append(f"Summary R3C{col} fill differs")
                if border(oc)!=border(tc): diffs.append(f"Summary R3C{col} border {border(oc)}!={border(tc)}")
            # col widths
            for col in 'ABCDE':
                tw=t.column_dimensions[col].width; ow=o.column_dimensions[col].width
                if round(tw or 0,1)!=round(ow or 0,1):
                    diffs.append(f"Summary col {col} width {ow}!={tw}")
            continue
        # data tabs
        tmax = t.max_column
        omax = o.max_column
        if tmax != omax:
            diffs.append(f"{name}: col count {omax}!={tmax}")
        for col in range(1, tmax+1):
            L = get_column_letter(col)
            tc,oc = t.cell(1,col), o.cell(1,col)
            if tc.value != oc.value:
                diffs.append(f"{name} header C{col} '{oc.value}' != '{tc.value}'")
            if fstyle(oc)!=fstyle(tc): diffs.append(f"{name} header C{col} font {fstyle(oc)}!={fstyle(tc)}")
            if fillstyle(oc)!=fillstyle(tc): diffs.append(f"{name} header C{col} fill {fillstyle(oc)}!={fillstyle(tc)}")
            if align(oc)!=align(tc): diffs.append(f"{name} header C{col} align {align(oc)}!={align(tc)}")
            if border(oc)!=border(tc): diffs.append(f"{name} header C{col} border {border(oc)}!={border(tc)}")
            tw=t.column_dimensions[L].width; ow=o.column_dimensions[L].width
            if round(tw or 0,2)!=round(ow or 0,2):
                diffs.append(f"{name} col {L} width {ow}!={tw}")
            # data row 2 style + numfmt (if both have a data row)
            if t.max_row>=2 and o.max_row>=2:
                td,od = t.cell(2,col), o.cell(2,col)
                if fstyle(od)!=fstyle(td): diffs.append(f"{name} data C{col} font {fstyle(od)}!={fstyle(td)}")
                if fillstyle(od)!=fillstyle(td): diffs.append(f"{name} data C{col} fill {fillstyle(od)}!={fillstyle(td)}")
                if align(od)!=align(td): diffs.append(f"{name} data C{col} align {align(od)}!={align(td)}")
                if border(od)!=border(td): diffs.append(f"{name} data C{col} border {border(od)}!={border(td)}")
                if td.number_format!=od.number_format:
                    diffs.append(f"{name} data C{col} numfmt '{od.number_format}'!='{td.number_format}'")
        # sheet props
        if round(hrow(t) or 0,2)!=round(hrow(o) or 0,2):
            diffs.append(f"{name} header height {hrow(o)}!={hrow(t)}")
        if round(drow(t) or 0,2)!=round(drow(o) or 0,2):
            diffs.append(f"{name} data-row height {drow(o)}!={drow(t)}")
        if (t.freeze_panes or '') != (o.freeze_panes or ''):
            diffs.append(f"{name} freeze {o.freeze_panes}!={t.freeze_panes}")
        if bool(t.auto_filter.ref) != bool(o.auto_filter.ref):
            diffs.append(f"{name} autofilter presence differs")
        tg = t.sheet_view.showGridLines; og = o.sheet_view.showGridLines
        if (tg in (None,True)) != (og in (None,True)):
            diffs.append(f"{name} gridlines {og}!={tg}")
    if diffs:
        print('STRUCTURAL DIFFERENCES:')
        for d in diffs: print('  -', d)
        print(f"{len(diffs)} structural differences")
        return 1
    print("ZERO structural differences")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
