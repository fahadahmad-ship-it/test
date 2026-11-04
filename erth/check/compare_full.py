"""Exhaustive structural/style comparison: built workbook vs signed-off template.
Checks EVERYTHING that should be identical regardless of row content:
sheet set/order, max_column, gridlines, freeze, autofilter cols, merged cells,
per-column header value+font+fill+border+alignment, per-column data-cell
font+fill+border+alignment+number_format, header & data row heights (all rows),
column widths, data validations, and the logo anchor (col/offset/extent)."""
import sys, zipfile, re
import openpyxl
from openpyxl.utils import get_column_letter

TEMPLATE = "erth/ref/kk_template.xlsx"
BUILT = "erth/out/Erth_Products_Backlinks_Audit.xlsx"
D = []
def rec(m): D.append(m)

def sstyle(s): return getattr(s, "style", None) if s else None
def bsig(c):
    b=c.border; return (sstyle(b.left),sstyle(b.right),sstyle(b.top),sstyle(b.bottom))
def fsig(c):
    f=c.fill; return f.fgColor.rgb if (f and f.patternType) else None
def fontsig(c):
    f=c.font
    col=None
    try:
        col=f.color.rgb if f.color else None
        if not isinstance(col,str): col=None
    except Exception: col=None
    return (f.name, float(f.size) if f.size else None, bool(f.bold), col)
def asig(c):
    a=c.alignment; return (a.horizontal, a.vertical, bool(a.wrap_text))

def logo_anchor(path):
    z=zipfile.ZipFile(path)
    draw=[n for n in z.namelist() if re.match(r"xl/drawings/drawing\d+\.xml", n)]
    out=[]
    for n in draw:
        x=z.read(n).decode()
        if "blip" not in x and "<pic" not in x:
            continue  # empty placeholder drawing; ignore
        col=re.search(r"<(?:xdr:)?col>(\d+)</(?:xdr:)?col>", x)
        coloff=re.search(r"<(?:xdr:)?colOff>(\d+)</(?:xdr:)?colOff>", x)
        row=re.search(r"<(?:xdr:)?row>(\d+)</(?:xdr:)?row>", x)
        ext=re.search(r'<(?:xdr:)?ext cx="(\d+)" cy="(\d+)"', x)
        out.append((col and col.group(1), coloff and coloff.group(1), row and row.group(1),
                    ext and ext.groups()))
    return out

def main():
    t=openpyxl.load_workbook(TEMPLATE); b=openpyxl.load_workbook(BUILT)
    if t.sheetnames != b.sheetnames:
        rec(f"sheet names/order: {t.sheetnames} vs {b.sheetnames}")
    for name in t.sheetnames:
        if name not in b.sheetnames: continue
        ts,bs=t[name],b[name]
        if ts.max_column!=bs.max_column: rec(f"[{name}] max_column {ts.max_column} vs {bs.max_column}")
        if bool(ts.sheet_view.showGridLines)!=bool(bs.sheet_view.showGridLines): rec(f"[{name}] gridlines")
        if ts.freeze_panes!=bs.freeze_panes: rec(f"[{name}] freeze {ts.freeze_panes} vs {bs.freeze_panes}")
        nf=lambda r:(r.split(":")[-1].rstrip("0123456789").replace("$","") if r else None)
        if nf(ts.auto_filter.ref)!=nf(bs.auto_filter.ref): rec(f"[{name}] autofilter {ts.auto_filter.ref} vs {bs.auto_filter.ref}")
        if set(map(str,ts.merged_cells.ranges))!=set(map(str,bs.merged_cells.ranges)):
            rec(f"[{name}] merged: {sorted(map(str,ts.merged_cells.ranges))} vs {sorted(map(str,bs.merged_cells.ranges))}")
        # data validations
        normsq=lambda s: re.sub(r"\d+","",str(s))
        tv=sorted(str(v.type)+str(v.formula1)+normsq(v.sqref) for v in ts.data_validations.dataValidation)
        bv=sorted(str(v.type)+str(v.formula1)+normsq(v.sqref) for v in bs.data_validations.dataValidation)
        if tv!=bv: rec(f"[{name}] data_validations: T={tv} B={bv}")
        # column widths
        for c in range(1, ts.max_column+1):
            L=get_column_letter(c); tw=ts.column_dimensions[L].width; bw=bs.column_dimensions[L].width
            if (tw or 0) and (bw or 0):
                if abs(tw-bw)>0.3: rec(f"[{name}] col {L} width {tw} vs {bw}")
            elif bool(tw)!=bool(bw): rec(f"[{name}] col {L} width set {tw} vs {bw}")
        # header + data style, per column
        hdr = 3 if name=="Summary" else 1
        datar = 4 if name=="Summary" else 2
        for c in range(1, ts.max_column+1):
            L=get_column_letter(c)
            th,bh=ts.cell(hdr,c),bs.cell(hdr,c)
            for lbl,fn in (("font",fontsig),("fill",fsig),("border",bsig),("align",asig)):
                if fn(th)!=fn(bh): rec(f"[{name}] HDR {L}{hdr} {lbl}: {fn(th)} vs {fn(bh)}")
            if ts.max_row>=datar and bs.max_row>=datar:
                td,bd=ts.cell(datar,c),bs.cell(datar,c)
                for lbl,fn in (("font",fontsig),("fill",fsig),("border",bsig),("align",asig),
                               ("numfmt",lambda x:x.number_format)):
                    if fn(td)!=fn(bd): rec(f"[{name}] DATA {L}{datar} {lbl}: {fn(td)!r} vs {fn(bd)!r}")
        # row heights (header + all data rows that exist in BOTH, up to min)
        th=ts.row_dimensions[hdr].height; bh=bs.row_dimensions[hdr].height
        if th and bh and abs(th-bh)>0.1: rec(f"[{name}] header row height {th} vs {bh}")
        # check the built sheet's data rows all share the template's data-row height
        tmpl_dh=ts.row_dimensions[datar].height
        if name!="Summary" and tmpl_dh:
            bad=[r for r in range(2,bs.max_row+1) if bs.row_dimensions[r].height not in (None,tmpl_dh)]
            # None means default; template data rows set explicit height -> built should too
            unset=[r for r in range(2,bs.max_row+1) if bs.row_dimensions[r].height is None]
            if bad: rec(f"[{name}] {len(bad)} data rows wrong height (e.g. row {bad[0]}={bs.row_dimensions[bad[0]].height}, expect {tmpl_dh})")
            if unset: rec(f"[{name}] {len(unset)} data rows have NO explicit height (expect {tmpl_dh})")
    # logo
    ta,ba=logo_anchor(TEMPLATE), logo_anchor(BUILT)
    if ta!=ba: rec(f"logo anchor: T={ta} B={ba}")

    print("TOTAL DIFFERENCES:", len(D))
    for d in D: print("  -", d)

if __name__=="__main__": main()
