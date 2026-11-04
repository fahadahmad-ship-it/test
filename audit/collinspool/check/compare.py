"""Compare my workbook's FORMAT against the signed sample (NewGarden).
Structure/styling only, not data. Reports every difference.
Usage: python3 -I compare.py <mine.xlsx> <sample.xlsx>
"""
import sys, openpyxl
MINE = sys.argv[1] if len(sys.argv) > 1 else "audit/collinspool/out/CollinsPool_Backlinks_Audit.xlsx"
SAMP = sys.argv[2] if len(sys.argv) > 2 else "audit/_ref/NewGarden_SAMPLE.xlsx"

def rgb(c):
    try: return c.rgb if c and c.rgb else None
    except Exception: return None

def cellfmt(c):
    f = c.font; fl = c.fill; b = c.border; a = c.alignment
    return dict(
        font=(f.name, f.size, bool(f.bold), rgb(f.color)),
        fill=(fl.patternType, rgb(fl.fgColor)),
        border=(bool(b.left.style), bool(b.right.style), bool(b.top.style), bool(b.bottom.style)),
        align=(a.horizontal, a.vertical, a.wrap_text),
        numfmt=c.number_format,
    )

def load(p):
    return openpyxl.load_workbook(p)

m = load(MINE); s = load(SAMP)
diffs = []
def d(msg): diffs.append(msg)

# 1. tabs + order
if m.sheetnames != s.sheetnames:
    d(f"TAB ORDER/NAMES differ:\n  mine:   {m.sheetnames}\n  sample: {s.sheetnames}")

common = [t for t in s.sheetnames if t in m.sheetnames]
for t in common:
    wm, ws = m[t], s[t]
    # headers (row 1)
    hm = [wm.cell(row=1, column=c).value for c in range(1, wm.max_column+1)]
    hs = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column+1)]
    if t != "Summary" and hm != hs:
        d(f"[{t}] HEADERS differ:\n   mine:   {hm}\n   sample: {hs}")
    # sheet view
    if wm.freeze_panes != ws.freeze_panes:
        d(f"[{t}] freeze_panes mine={wm.freeze_panes} sample={ws.freeze_panes}")
    if bool(wm.auto_filter.ref) != bool(ws.auto_filter.ref):
        d(f"[{t}] autofilter mine={wm.auto_filter.ref} sample={ws.auto_filter.ref}")
    if wm.sheet_view.showGridLines != ws.sheet_view.showGridLines:
        d(f"[{t}] gridlines mine={wm.sheet_view.showGridLines} sample={ws.sheet_view.showGridLines}")
    # header row height
    if abs((wm.row_dimensions[1].height or 0) - (ws.row_dimensions[1].height or 0)) > 0.1:
        d(f"[{t}] header row height mine={wm.row_dimensions[1].height} sample={ws.row_dimensions[1].height}")
    # a data row height (row 2)
    if wm.max_row > 1 and ws.max_row > 1:
        rm = wm.row_dimensions[2].height; rs = ws.row_dimensions[2].height
        if (rm or 0) != (rs or 0):
            d(f"[{t}] data row(2) height mine={rm} sample={rs}")
    # header cell style (col1)
    if t != "Summary":
        fm = cellfmt(wm.cell(row=1,column=1)); fs = cellfmt(ws.cell(row=1,column=1))
        for k in ("font","fill","border","align"):
            if fm[k] != fs[k]:
                d(f"[{t}] HEADER cell {k} mine={fm[k]} sample={fs[k]}")
        # data cell style (row2 col1)
        if wm.max_row>1 and ws.max_row>1:
            dm = cellfmt(wm.cell(row=2,column=1)); dsx = cellfmt(ws.cell(row=2,column=1))
            for k in ("font","fill","border","align"):
                if dm[k] != dsx[k]:
                    d(f"[{t}] DATA cell {k} mine={dm[k]} sample={dsx[k]}")
    # column widths
    for c in range(1, max(wm.max_column, ws.max_column)+1):
        L = openpyxl.utils.get_column_letter(c)
        cwm = wm.column_dimensions[L].width; cws = ws.column_dimensions[L].width
        if cwm and cws and abs(cwm-cws) > 2:
            d(f"[{t}] col {L} width mine={cwm} sample={cws}")

# images/logo
def nimg(ws): return len(getattr(ws, "_images", []))
for t in common:
    if nimg(m[t]) != nimg(s[t]):
        d(f"[{t}] images/logo count mine={nimg(m[t])} sample={nimg(s[t])}")

print(f"Comparing MINE={MINE}\n     vs SAMPLE={SAMP}\n")
if not diffs:
    print("NO FORMAT DIFFERENCES FOUND")
else:
    print(f"{len(diffs)} DIFFERENCE GROUP(S):\n")
    for x in diffs: print("- " + x)
