"""
Structural template comparison: my workbook vs the signed-off K&K template.
Reports differences in: tab names/order, header texts, column widths, row heights,
fonts/sizes, fills, header border scheme, freeze panes, autofilter, gridlines,
data validations (dropdowns), and the Summary logo. Ignores data values/counts.
"""
import sys, zipfile
import openpyxl
from openpyxl.utils import get_column_letter

tmpl_path = sys.argv[1]
mine_path = sys.argv[2]
T = openpyxl.load_workbook(tmpl_path)
M = openpyxl.load_workbook(mine_path)
diffs = []

def rgb(c):
    try: return str(c.rgb) if c else None
    except: return None

def bstyle(cell):
    b = cell.border
    def s(side): return side.style if side and side.style else None
    return (s(b.left), s(b.right), s(b.top), s(b.bottom))

# 1 tab names + order
if T.sheetnames != M.sheetnames:
    diffs.append(f"TAB ORDER/NAMES: template={T.sheetnames} mine={M.sheetnames}")

for name in T.sheetnames:
    if name not in M.sheetnames: continue
    t = T[name]; m = M[name]
    # gridlines
    if bool(t.sheet_view.showGridLines) != bool(m.sheet_view.showGridLines):
        diffs.append(f"[{name}] gridlines t={t.sheet_view.showGridLines} m={m.sheet_view.showGridLines}")
    # freeze
    if (t.freeze_panes or None) != (m.freeze_panes or None):
        diffs.append(f"[{name}] freeze t={t.freeze_panes} m={m.freeze_panes}")
    # autofilter presence
    if bool(t.auto_filter.ref) != bool(m.auto_filter.ref):
        diffs.append(f"[{name}] autofilter t={t.auto_filter.ref} m={m.auto_filter.ref}")
    # header row detection: Summary header is row3, data tabs row1
    hrow = 3 if name == "Summary" else 1
    ncol = t.max_column
    # headers text (data tabs only; summary has merged title)
    if name != "Summary":
        th = [t.cell(row=1, column=c).value for c in range(1, ncol+1)]
        mh = [m.cell(row=1, column=c).value for c in range(1, (m.max_column)+1)]
        if th != mh:
            diffs.append(f"[{name}] HEADERS differ:\n   t={th}\n   m={mh}")
        # header font/fill/border
        for c in range(1, ncol+1):
            tc = t.cell(row=1, column=c); mc = m.cell(row=1, column=c)
            if (tc.font.name, tc.font.size, tc.font.bold) != (mc.font.name, mc.font.size, mc.font.bold):
                diffs.append(f"[{name}] header {get_column_letter(c)} font t={tc.font.name},{tc.font.size},{tc.font.bold} m={mc.font.name},{mc.font.size},{mc.font.bold}")
            if rgb(tc.fill.fgColor) != rgb(mc.fill.fgColor):
                diffs.append(f"[{name}] header {get_column_letter(c)} fill t={rgb(tc.fill.fgColor)} m={rgb(mc.fill.fgColor)}")
            tb = bstyle(tc)
            mb = bstyle(mc)
            if tb != mb:
                diffs.append(f"[{name}] header {get_column_letter(c)} border t={tb} m={mb}")
        # column widths
        for c in range(1, ncol+1):
            L = get_column_letter(c)
            tw = t.column_dimensions[L].width; mw = m.column_dimensions[L].width
            if tw and mw and abs(tw-mw) > 0.5:
                diffs.append(f"[{name}] width {L} t={tw} m={mw}")
        # header + data row heights
        th1 = t.row_dimensions[1].height; mh1 = m.row_dimensions[1].height
        if th1 and mh1 and abs(th1-mh1) > 0.1:
            diffs.append(f"[{name}] header height t={th1} m={mh1}")
        th2 = t.row_dimensions[2].height; mh2 = m.row_dimensions[2].height
        if th2 and mh2 and abs(th2-mh2) > 0.1:
            diffs.append(f"[{name}] data row height t={th2} m={mh2}")
        # data cell font + border scheme (row2)
        tc = t.cell(row=2, column=1); mc = m.cell(row=2, column=1)
        if (tc.font.name, tc.font.size) != (mc.font.name, mc.font.size):
            diffs.append(f"[{name}] data font t={tc.font.name},{tc.font.size} m={mc.font.name},{mc.font.size}")
        tb = bstyle(tc)
        mb = bstyle(mc)
        if tb != mb:
            diffs.append(f"[{name}] data A2 border t={tb} m={mb}")
    # data validations
    tdv = sorted([(dv.type, str(dv.formula1), str(dv.sqref).split()[0].rstrip('0123456789').split(':')[0]) for dv in t.data_validations.dataValidation])
    mdv = sorted([(dv.type, str(dv.formula1), str(dv.sqref).split()[0].rstrip('0123456789').split(':')[0]) for dv in m.data_validations.dataValidation])
    if tdv != mdv:
        diffs.append(f"[{name}] dropdowns t={tdv} m={mdv}")

# logo presence (Summary drawing / media)
def has_logo(path):
    z = zipfile.ZipFile(path)
    return any("media/image" in n for n in z.namelist())
if has_logo(tmpl_path) != has_logo(mine_path):
    diffs.append(f"LOGO present t={has_logo(tmpl_path)} m={has_logo(mine_path)}")

# Summary title font size
t_title = T["Summary"]["B1"]; m_title = M["Summary"]["B1"]
if (t_title.font.size, t_title.font.bold, rgb(t_title.font.color)) != (m_title.font.size, m_title.font.bold, rgb(m_title.font.color)):
    diffs.append(f"[Summary] title B1 t={t_title.font.size},{t_title.font.bold},{rgb(t_title.font.color)} m={m_title.font.size},{m_title.font.bold},{rgb(m_title.font.color)}")

print(f"=== {len(diffs)} structural differences ===")
for d in diffs:
    print("-", d)
if not diffs:
    print("TEMPLATE MATCH: zero structural differences.")
