"""
deep_compare.py - exhaustive cell-level style comparison of the generated workbook
vs the K&K template, for EVERY column of every tab (header + a representative data
cell), plus Summary layout from raw XML. Reports every structural difference.
"""
import os, sys, zipfile
import openpyxl
from openpyxl.utils import get_column_letter
from xml.etree import ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN  = os.path.join(BASE, "out", "Fitzgerald_Plumbing_Backlink_Audit.xlsx")
TMPL = sys.argv[1] if len(sys.argv)>1 else "/home/user/test/_tmpl_inspect/template.xlsx"
TABS = ["Summary","Referring Domain Audit","All Backlinks","Anchor Analysis",
        "Exact Match Anchors","Pending Disavow Lines","Disavow List"]
diffs=[]
def D(m): diffs.append(m); print("DIFF -", m)

def sig(cell):
    f=cell.font; fill=cell.fill; b=cell.border; al=cell.alignment
    fg=None
    try: fg=fill.fgColor.rgb if fill and fill.patternType else None
    except: pass
    def side(s):
        x=getattr(b,s); return x.style if x is not None else None
    col = f.color.rgb if (f.color and f.color.type=="rgb") else (("theme:"+str(f.color.theme)) if (f.color and f.color.type=="theme") else None)
    return (f.name, float(f.sz or 0), bool(f.bold), col,
            fill.patternType if fill else None, fg,
            (side("left"),side("right"),side("top"),side("bottom")),
            al.horizontal, al.vertical, bool(al.wrap_text),
            cell.number_format)

g=openpyxl.load_workbook(GEN); t=openpyxl.load_workbook(TMPL)
print("tabs gen:",g.sheetnames)
print("tabs tpl:",t.sheetnames)
if g.sheetnames!=t.sheetnames: D("tab order differs")

for name in TABS[1:]:  # data tabs (Summary handled via XML separately)
    gw=g[name]; tw=t[name]; n=tw.max_column
    # header: every column
    for c in range(1,n+1):
        gc, tc = gw.cell(1,c), tw.cell(1,c)
        if gc.value!=tc.value:
            D(f"[{name}] header col{c} label {gc.value!r} vs {tc.value!r}")
        gs, ts = sig(gc), sig(tc)
        if gs!=ts:
            # compare field by field for a precise message
            fields=["font","size","bold","color","fillpat","fillfg","borders","halign","valign","wrap","numfmt"]
            for i,fn in enumerate(fields):
                if gs[i]!=ts[i]:
                    D(f"[{name}] header col{c} '{tc.value}' {fn}: gen={gs[i]} tpl={ts[i]}")
    # data cell row2: every column (style+numfmt only; values differ)
    for c in range(1,n+1):
        gs, ts = sig(gw.cell(2,c)), sig(tw.cell(2,c))
        if gs!=ts:
            fields=["font","size","bold","color","fillpat","fillfg","borders","halign","valign","wrap","numfmt"]
            for i,fn in enumerate(fields):
                if gs[i]!=ts[i]:
                    D(f"[{name}] data col{c} {fn}: gen={gs[i]} tpl={ts[i]}")
    # heights
    if round(gw.row_dimensions[1].height or 0,2)!=round(tw.row_dimensions[1].height or 0,2):
        D(f"[{name}] header height {gw.row_dimensions[1].height} vs {tw.row_dimensions[1].height}")
    if round(gw.row_dimensions[2].height or 0,2)!=round(tw.row_dimensions[2].height or 0,2):
        D(f"[{name}] data height {gw.row_dimensions[2].height} vs {tw.row_dimensions[2].height}")
    if gw.freeze_panes!=tw.freeze_panes: D(f"[{name}] freeze {gw.freeze_panes} vs {tw.freeze_panes}")
    if bool(gw.sheet_view.showGridLines)!=bool(tw.sheet_view.showGridLines):
        D(f"[{name}] gridlines {gw.sheet_view.showGridLines} vs {tw.sheet_view.showGridLines}")
    if (gw.auto_filter.ref is not None)!=(tw.auto_filter.ref is not None):
        D(f"[{name}] autofilter presence differs")

# ---- Summary via XML (merged styling) ----
M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def summ_info(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        # find sheet1 (Summary is first)
        root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        sv=root.find(f"{M}sheetViews/{M}sheetView")
        grid=sv.get("showGridLines") if sv is not None else None
        merges=set()
        mc=root.find(f"{M}mergeCells")
        if mc is not None:
            merges={m.get("ref") for m in mc.findall(f"{M}mergeCell")}
        has_logo=any(nm.startswith("xl/media/") for nm in names)
        # logo anchor
        anchor=None
        if "xl/drawings/drawing1.xml" in names:
            dr=z.read("xl/drawings/drawing1.xml").decode()
            import re
            cols=re.search(r'<(?:xdr:)?col>(\d+)</(?:xdr:)?col>',dr)
            coff=re.search(r'<(?:xdr:)?colOff>(\d+)</(?:xdr:)?colOff>',dr)
            row=re.search(r'<(?:xdr:)?row>(\d+)</(?:xdr:)?row>',dr)
            ext=re.search(r'<(?:xdr:)?ext cx="(\d+)" cy="(\d+)"',dr)
            anchor=(cols.group(1) if cols else None, coff.group(1) if coff else None,
                    row.group(1) if row else None, ext.groups() if ext else None)
    return grid, merges, has_logo, anchor
gg=summ_info(GEN); tt=summ_info(TMPL)
print("\n[Summary] gridlines gen",gg[0],"tpl",tt[0])
if (gg[0] in ("0",None,"false"))!=(tt[0] in ("0",None,"false")) and gg[0]!=tt[0]:
    # both should be gridlines off (0)
    if gg[0]!=tt[0]: D(f"[Summary] gridlines gen={gg[0]} tpl={tt[0]}")
print("[Summary] title/merge B1:E2 present gen",("B1:E2" in gg[1]),"tpl",("B1:E2" in tt[1]))
if ("B1:E2" in gg[1])!=("B1:E2" in tt[1]): D("[Summary] title merge B1:E2 differs")
print("[Summary] logo present gen",gg[2],"tpl",tt[2],"| anchor gen",gg[3],"tpl",tt[3])
if gg[2]!=tt[2]: D("[Summary] logo presence differs")
if gg[3]!=tt[3]: D(f"[Summary] logo anchor differs gen={gg[3]} tpl={tt[3]}")

print("\n===== DEEP COMPARE: %d differences =====" % len(diffs))
sys.exit(1 if diffs else 0)
