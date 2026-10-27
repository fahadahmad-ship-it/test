"""Structural comparison of the built workbook against the signed K&K template.
Reads XML from both .xlsx (openpyxl drops merged-cell styling on read). Compares
format invariants that must match regardless of client content."""
import os, sys, re, zipfile
import xml.etree.ElementTree as ET
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
HERE=os.path.dirname(__file__)
TEMPLATE=os.path.join(HERE,"..","ref","KK_template.xlsx")
BUILT=os.path.join(HERE,"..","out","Premier_Blinds_and_Designs_Backlinks_Audit.xlsx")
diffs=[]

def sheets(path):
    z=zipfile.ZipFile(path)
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    order=[s.get("name") for s in wb.findall(NS+"sheets/"+NS+"sheet")]
    files=sorted([n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$",n)],
                 key=lambda n:int(re.search(r"\d+",n.split("/")[-1]).group()))
    out={}
    for i,f in enumerate(files):
        root=ET.fromstring(z.read(f)); nm=order[i]
        sv=root.find(NS+"sheetViews/"+NS+"sheetView")
        g=sv.get("showGridLines") if sv is not None else None
        grid = "off" if g=="0" else "on"   # absent or "1" => gridlines on
        pane=sv.find(NS+"pane") if sv is not None else None
        cols=[]
        for c in root.findall(NS+"cols/"+NS+"col"):
            lo,hi=int(c.get("min")),int(c.get("max")); w=round(float(c.get("width")),1)
            for _ in range(lo,hi+1): cols.append(w)   # expand ranges to per-column widths
        rows=root.findall(NS+"sheetData/"+NS+"row")
        h1=rows[0].get("ht") if rows else None
        h2=rows[1].get("ht") if len(rows)>1 else None
        af=root.find(NS+"autoFilter")
        out[nm]=dict(grid=grid,
                     freeze=(pane.get("topLeftCell"),pane.get("state")) if pane is not None else None,
                     cols=cols, hdr_h=h1, data_h=h2,
                     autofilter=af is not None)
    # logo: which sheets have a drawing rel
    draw=[n for n in z.namelist() if re.match(r"xl/drawings/drawing\d+\.xml$",n)]
    media=[n for n in z.namelist() if n.startswith("xl/media/")]
    return out, order, media

def main():
    tpl,torder,tmedia=sheets(TEMPLATE)
    blt,border,bmedia=sheets(BUILT)
    def D(msg): diffs.append(msg)
    if torder!=border: D("sheet order differs: %s vs %s"%(torder,border))
    for nm in torder:
        if nm not in blt: D("missing sheet: %s"%nm); continue
        a,b=tpl[nm],blt[nm]
        if a["grid"]!=b["grid"]: D("%s: gridlines %s vs %s"%(nm,a["grid"],b["grid"]))
        if a["freeze"]!=b["freeze"]: D("%s: freeze %s vs %s"%(nm,a["freeze"],b["freeze"]))
        if a["hdr_h"]!=b["hdr_h"]: D("%s: header height %s vs %s"%(nm,a["hdr_h"],b["hdr_h"]))
        if nm!="Summary":
            if a["data_h"]!=b["data_h"]: D("%s: data row height %s vs %s"%(nm,a["data_h"],b["data_h"]))
            if a["autofilter"]!=b["autofilter"]: D("%s: autofilter %s vs %s"%(nm,a["autofilter"],b["autofilter"]))
            # column widths (count + values)
            if a["cols"]!=b["cols"]: D("%s: column widths differ\n     tpl=%s\n     blt=%s"%(nm,a["cols"],b["cols"]))
    # media present (logo)
    if not bmedia: D("built workbook has no logo image")
    print("media in template:",len(tmedia)," built:",len(bmedia))
    print("\n=== STRUCTURAL DIFFS ===")
    if not diffs:
        print("ZERO structural differences vs signed template.")
    else:
        for d in diffs: print(" X",d)
        sys.exit(1)

if __name__=="__main__":
    main()
