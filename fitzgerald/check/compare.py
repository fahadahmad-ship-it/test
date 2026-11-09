"""
compare.py - structural fidelity check of the generated workbook vs the signed-off
K&K template. Compares layout/style, not data values. Reports differences; exits
non-zero if any structural difference is found.
"""
import os, sys, zipfile
import openpyxl
from openpyxl.utils import get_column_letter
from xml.etree import ElementTree as ET

M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def xml_col_widths(path, sheet_pos, n):
    """Authoritative column widths from raw XML (expands min-max ranged <col> defs)."""
    widths = {}
    with zipfile.ZipFile(path) as z:
        try:
            data = z.read(f"xl/worksheets/sheet{sheet_pos}.xml")
        except KeyError:
            return [0]*n
    root = ET.fromstring(data)
    cols = root.find(f"{M}cols")
    if cols is not None:
        for c in cols.findall(f"{M}col"):
            lo, hi = int(c.get("min")), int(c.get("max"))
            w = round(float(c.get("width") or 0), 2)
            for i in range(lo, hi+1):
                widths[i] = w
    return [widths.get(i, 0) for i in range(1, n+1)]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN  = os.path.join(BASE, "out", "Fitzgerald_Plumbing_Backlink_Audit.xlsx")
TMPL = sys.argv[1] if len(sys.argv)>1 else "/home/user/test/_tmpl_inspect/template.xlsx"

diffs = []
def d(msg): diffs.append(msg); print("DIFF -", msg)
def ok(msg): print("ok   -", msg)

# data tabs and their expected column counts (header labels compared too)
TABS = ["Summary","Referring Domain Audit","All Backlinks","Anchor Analysis",
        "Exact Match Anchors","Pending Disavow Lines","Disavow List"]

g = openpyxl.load_workbook(GEN)
t = openpyxl.load_workbook(TMPL)

# 1. tab names & order
if g.sheetnames != t.sheetnames:
    d(f"tab names/order differ: {g.sheetnames} vs {t.sheetnames}")
else:
    ok(f"tab names & order match: {g.sheetnames}")

def col_widths(ws, n):
    return [round(ws.column_dimensions[get_column_letter(i)].width or 0, 2) for i in range(1, n+1)]

def style_sig(cell):
    f = cell.font; fill = cell.fill; b = cell.border
    fg = None
    try: fg = fill.fgColor.rgb if fill and fill.patternType else None
    except: pass
    sides = tuple((s, (getattr(b, s).style if getattr(b, s) is not None else None))
                  for s in ("left","right","top","bottom"))
    return (f.name, float(f.sz or 0), bool(f.bold),
            (f.color.rgb if f.color else None), fill.patternType if fill else None, fg, sides)

for name in TABS:
    if name not in g.sheetnames or name not in t.sheetnames:
        continue
    gw = g[name]; tw = t[name]
    ncol = tw.max_column
    pos = TABS.index(name) + 1
    # column widths (authoritative, from raw XML)
    gcw, tcw = xml_col_widths(GEN, pos, ncol), xml_col_widths(TMPL, pos, ncol)
    if gcw != tcw:
        d(f"[{name}] column widths differ:\n       gen={gcw}\n       tpl={tcw}")
    else:
        ok(f"[{name}] column widths match ({ncol} cols)")
    # header labels
    gh = [gw.cell(1,i).value for i in range(1,ncol+1)]
    th = [tw.cell(1,i).value for i in range(1,ncol+1)]
    if name != "Summary":
        if gh != th:
            d(f"[{name}] header labels differ:\n       gen={gh}\n       tpl={th}")
        else:
            ok(f"[{name}] header labels match")
    # header row height
    if round(gw.row_dimensions[1].height or 0,2) != round(tw.row_dimensions[1].height or 0,2):
        d(f"[{name}] header row height {gw.row_dimensions[1].height} vs {tw.row_dimensions[1].height}")
    # data row height (row 2)
    if name != "Summary":
        if round(gw.row_dimensions[2].height or 0,2) != round(tw.row_dimensions[2].height or 0,2):
            d(f"[{name}] data row height {gw.row_dimensions[2].height} vs {tw.row_dimensions[2].height}")
        else:
            ok(f"[{name}] data row height matches ({gw.row_dimensions[2].height})")
    # freeze panes
    if gw.freeze_panes != tw.freeze_panes:
        d(f"[{name}] freeze panes {gw.freeze_panes} vs {tw.freeze_panes}")
    # gridlines
    if bool(gw.sheet_view.showGridLines) != bool(tw.sheet_view.showGridLines):
        d(f"[{name}] showGridLines {gw.sheet_view.showGridLines} vs {tw.sheet_view.showGridLines}")
    else:
        ok(f"[{name}] gridlines match ({gw.sheet_view.showGridLines})")
    # autofilter
    if name != "Summary":
        ga = gw.auto_filter.ref is not None; ta = tw.auto_filter.ref is not None
        if ga != ta: d(f"[{name}] autofilter presence {ga} vs {ta}")
        else: ok(f"[{name}] autofilter present={ga}")
    # header cell style (A1) and data cell style (A2) - skip Summary (no real header at A1)
    if name == "Summary":
        continue
    if style_sig(gw.cell(1,1)) != style_sig(tw.cell(1,1)):
        d(f"[{name}] header A1 style differs:\n       gen={style_sig(gw.cell(1,1))}\n       tpl={style_sig(tw.cell(1,1))}")
    else:
        ok(f"[{name}] header A1 style matches")
    if name not in ("Summary",) and gw.max_row>1 and tw.max_row>1:
        if style_sig(gw.cell(2,1)) != style_sig(tw.cell(2,1)):
            d(f"[{name}] data A2 style differs:\n       gen={style_sig(gw.cell(2,1))}\n       tpl={style_sig(tw.cell(2,1))}")
        else:
            ok(f"[{name}] data A2 style matches")

# logo present on Summary in both
def has_logo(path):
    with zipfile.ZipFile(path) as z:
        return any(n.startswith("xl/media/") for n in z.namelist())
if has_logo(GEN) and has_logo(TMPL):
    ok("logo image present in both workbooks")
else:
    d(f"logo presence gen={has_logo(GEN)} tpl={has_logo(TMPL)}")

print("\n===== COMPARE SUMMARY =====")
print(f"differences: {len(diffs)}")
if diffs:
    sys.exit(1)
print("STRUCTURAL MATCH: no differences")
