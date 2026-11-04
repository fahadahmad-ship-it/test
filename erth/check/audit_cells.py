"""Definitive per-cell style audit: iterate EVERY cell / EVERY row of the built
workbook and assert it matches the template's style for that position/column.
Catches any per-row inconsistency the representative-row compare could miss."""
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
    f=c.font; col=None
    try:
        col=f.color.rgb if f.color else None
        if not isinstance(col,str): col=None
    except Exception: col=None
    return (f.name, float(f.size) if f.size else None, bool(f.bold), col)
def asig(c):
    a=c.alignment; return (a.horizontal, a.vertical, bool(a.wrap_text))
def allsig(c): return (fontsig(c), fsig(c), bsig(c), asig(c), c.number_format)

def main():
    t=openpyxl.load_workbook(TEMPLATE); b=openpyxl.load_workbook(BUILT)
    checked=0
    for name in t.sheetnames:
        ts,bs=t[name],b[name]
        if name=="Summary":
            # fixed layout: compare every cell rows 1..28, cols A..E, STYLE only
            for r in range(1,29):
                th=ts.row_dimensions[r].height; bh=bs.row_dimensions[r].height
                if (th or 22.5)!=(bh or 22.5) and abs((th or 0)-(bh or 0))>0.1:
                    rec(f"[Summary] row {r} height {th} vs {bh}")
                for c in range(1,6):
                    tc,bc=ts.cell(r,c),bs.cell(r,c)
                    # compare style only where template cell has content or fill/border
                    if tc.value is None and fsig(tc) is None and bsig(tc)==(None,None,None,None):
                        continue
                    if allsig(tc)!=allsig(bc):
                        rec(f"[Summary] {get_column_letter(c)}{r}: T={allsig(tc)} B={allsig(bc)}")
                    checked+=1
            continue
        # data tabs: header style from template row1; data style from template row2
        hdr_ref={c:allsig(ts.cell(1,c)) for c in range(1,ts.max_column+1)}
        data_ref={c:allsig(ts.cell(2,c)) for c in range(1,ts.max_column+1)}
        hh_ref=ts.row_dimensions[1].height
        dh_ref=ts.row_dimensions[2].height
        # header row of built
        for c in range(1,ts.max_column+1):
            if allsig(bs.cell(1,c))!=hdr_ref[c]:
                rec(f"[{name}] HDR {get_column_letter(c)}1: T={hdr_ref[c]} B={allsig(bs.cell(1,c))}")
            checked+=1
        if hh_ref and bs.row_dimensions[1].height and abs(hh_ref-bs.row_dimensions[1].height)>0.1:
            rec(f"[{name}] header height {hh_ref} vs {bs.row_dimensions[1].height}")
        # EVERY data row
        input_cols = {6,7} if name=="Exact Match Anchors" else set()
        for r in range(2, bs.max_row+1):
            bh=bs.row_dimensions[r].height
            if dh_ref and (bh is None or abs(dh_ref-bh)>0.1):
                rec(f"[{name}] data row {r} height {bh} (expect {dh_ref})");
                if len([x for x in D if 'data row' in x and name in x])>3: pass
            for c in range(1,ts.max_column+1):
                if c in input_cols:
                    continue  # accent input cells: verified separately
                sig=allsig(bs.cell(r,c))
                if sig!=data_ref[c]:
                    rec(f"[{name}] DATA {get_column_letter(c)}{r}: T={data_ref[c]} B={sig}")
                checked+=1
            # cap noise: stop detailed per-cell after many diffs on a sheet
            if len(D)>60: break
        # input cells accent across all rows
        if input_cols:
            ref=allsig(ts.cell(2,6))
            for r in range(2, bs.max_row+1):
                for c in input_cols:
                    if allsig(bs.cell(r,c))!=ref:
                        rec(f"[{name}] INPUT {get_column_letter(c)}{r}: T={ref} B={allsig(bs.cell(r,c))}"); break
    print("cells checked:", checked)
    print("DIFFERENCES:", len(D))
    for d in D[:50]: print("  -", d)

if __name__=="__main__": main()
