"""
Deep, independent template comparison (does NOT trust compare.py).
Compares STYLE of equivalent elements between the signed-off K&K template and
the HPP output: fonts, fills, borders, alignment, number formats, widths, row
heights, sheet settings, merges, logo anchor/extent, and dropdowns.
Data values and row counts legitimately differ, so only style/structure is diffed.
"""
import sys, zipfile, re
import openpyxl
from openpyxl.utils import get_column_letter

T = openpyxl.load_workbook(sys.argv[1])
M = openpyxl.load_workbook(sys.argv[2])
tpath, mpath = sys.argv[1], sys.argv[2]
diffs = []
def D(msg): diffs.append(msg)

def ncolor(c):
    """Normalize a color to a token; collapse all blacks (rgb FF000000, theme 0/1,
    auto/None) to BLACK and all whites to WHITE, so theme-vs-rgb isn't a false diff."""
    if c is None: return "BLACK"
    v = None
    try:
        if isinstance(c.rgb, str): v = c.rgb
    except Exception: v = None
    if v is None:
        th = getattr(c, "theme", None)
        if th in (0, 1): return "BLACK"
        if th is not None: return f"theme{th}"
        return "BLACK"
    if v in ("FF000000", "00000000"): return "BLACK"
    if v == "FFFFFFFF": return "WHITE"
    return v
def nhoriz(h):
    return "left" if h in (None, "general", "left") else h
def sig(cell):
    f, fl, al, b = cell.font, cell.fill, cell.alignment, cell.border
    def s(sd): return sd.style if sd and sd.style else None
    return {
        "font": (f.name, f.size, bool(f.bold), ncolor(f.color)),
        "fill": (fl.patternType, ncolor(fl.fgColor) if fl and fl.patternType else None),
        "align": (nhoriz(al.horizontal), al.vertical, bool(al.wrap_text)),
        "border": (s(b.left), s(b.right), s(b.top), s(b.bottom)),
        "numfmt": cell.number_format,
    }
def cmpcell(name, tc, mc, label):
    ts, ms = sig(tc), sig(mc)
    for k in ts:
        if ts[k] != ms[k]:
            D(f"[{name}] {label} {k}: template={ts[k]} mine={ms[k]}")

# ---------------- data tabs ----------------
for name in T.sheetnames[1:]:
    t, m = T[name], M[name]
    nc = t.max_column
    if m.max_column != nc:
        D(f"[{name}] column count template={nc} mine={m.max_column}")
    # headers text
    th = [t.cell(row=1,column=c).value for c in range(1,nc+1)]
    mh = [m.cell(row=1,column=c).value for c in range(1,nc+1)]
    if th != mh: D(f"[{name}] header text differs: {th} vs {mh}")
    for c in range(1, nc+1):
        L = get_column_letter(c)
        cmpcell(name, t.cell(row=1,column=c), m.cell(row=1,column=c), f"hdr {L}")
        cmpcell(name, t.cell(row=2,column=c), m.cell(row=2,column=c), f"data {L}")
        tw = t.column_dimensions[L].width; mw = m.column_dimensions[L].width
        if (tw or 0) and (mw or 0) and abs(tw-mw) > 0.3:
            D(f"[{name}] width {L} template={tw} mine={mw}")
    for rr,lbl in [(1,"hdr"),(2,"data")]:
        th_ = t.row_dimensions[rr].height; mh_ = m.row_dimensions[rr].height
        if (th_ or 0) and (mh_ or 0) and abs(th_-mh_) > 0.05:
            D(f"[{name}] {lbl} row height template={th_} mine={mh_}")
    if (t.freeze_panes or None) != (m.freeze_panes or None):
        D(f"[{name}] freeze template={t.freeze_panes} mine={m.freeze_panes}")
    if bool(t.auto_filter.ref) != bool(m.auto_filter.ref):
        D(f"[{name}] autofilter template={t.auto_filter.ref} mine={m.auto_filter.ref}")
    if bool(t.sheet_view.showGridLines) != bool(m.sheet_view.showGridLines):
        D(f"[{name}] gridlines template={t.sheet_view.showGridLines} mine={m.sheet_view.showGridLines}")
    # data validations
    def dvs(ws):
        out=[]
        for dv in ws.data_validations.dataValidation:
            out.append((dv.type, str(dv.formula1), re.sub(r'\d+','#',str(dv.sqref))))
        return sorted(out)
    if dvs(t) != dvs(m):
        D(f"[{name}] dropdowns template={dvs(t)} mine={dvs(m)}")

# ---------------- Summary (equivalent fixed cells) ----------------
ts, ms = T["Summary"], M["Summary"]
for coord,label in [("B1","title"),("A3","stat-hdr"),("B3","stat-hdr-num"),("E3","stat-hdr-txt"),
                    ("A4","stat-data"),("B4","stat-num"),("D4","stat-share"),("A10","total"),
                    ("A11","kf-heading"),("A12","kf-cell"),("A19","anchor-section"),
                    ("A20","anchor-hdr"),("A21","anchor-data"),("B21","anchor-num"),("C21","anchor-share")]:
    cmpcell("Summary", ts[coord], ms[coord], label)
# gridlines + merges
if bool(ts.sheet_view.showGridLines) != bool(ms.sheet_view.showGridLines):
    D(f"[Summary] gridlines template={ts.sheet_view.showGridLines} mine={ms.sheet_view.showGridLines}")
tm = set(str(r) for r in ts.merged_cells.ranges); mm = set(str(r) for r in ms.merged_cells.ranges)
if "B1:E2" not in mm: D(f"[Summary] title merge B1:E2 missing in mine (mine merges include: {sorted(mm)[:6]})")
# findings merged across A:E?
if not any(str(r).startswith("A12:E12") for r in ms.merged_cells.ranges):
    D("[Summary] finding row A12 not merged A12:E12 in mine")

# ---------------- logo anchor/extent ----------------
def logo_info(path):
    z = zipfile.ZipFile(path)
    draw = [n for n in z.namelist() if re.search(r'xl/drawings/drawing\d+\.xml$', n)]
    for n in draw:
        xml = z.read(n).decode("utf-8","ignore")
        if "blipFill" in xml or "pic" in xml:
            col = re.search(r'<(?:xdr:)?col>(\d+)</(?:xdr:)?col>', xml)
            coloff = re.search(r'<(?:xdr:)?colOff>(\d+)</(?:xdr:)?colOff>', xml)
            row = re.search(r'<(?:xdr:)?row>(\d+)</(?:xdr:)?row>', xml)
            ext = re.search(r'<(?:xdr:)?ext cx="(\d+)" cy="(\d+)"/>', xml)
            which = [s for s in z.namelist() if 'media/image' in s]
            return (col.group(1) if col else None, coloff.group(1) if coloff else None,
                    row.group(1) if row else None, ext.groups() if ext else None, bool(which))
    return None
tl, ml = logo_info(tpath), logo_info(mpath)
if tl != ml:
    D(f"[logo] template={tl} mine={ml}")

# ---------------- XML cross-check: mine's merged title really 21pt accent ----------------
zz = zipfile.ZipFile(mpath)
names = zz.namelist()
sheet1 = zz.read("xl/worksheets/sheet1.xml").decode("utf-8","ignore")
styles = zz.read("xl/styles.xml").decode("utf-8","ignore")
if 'sz val="21"' not in styles: D("[XML] no 21pt font in mine styles.xml")
if 'FF0C343D' not in styles: D("[XML] accent FF0C343D missing in mine styles.xml")

print(f"=== {len(diffs)} style/structure differences ===")
for d in diffs: print(" -", d)
if not diffs: print("DEEP MATCH: template and output are stylistically identical.")
