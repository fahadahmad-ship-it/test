"""Authoritative XML-level style comparison (bypasses openpyxl's merged-cell blind spot).
Resolves each cell's real font/fill/border/alignment/numfmt from the saved xlsx XML and
compares built vs template for the fixed-layout cells (incl. merged ones).
Usage: python3 -I xmlcheck.py <built.xlsx> <template.xlsx>
"""
import sys, zipfile, re
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BUILTIN_FMT = {0:"General",9:"0%",10:"0.00%",14:"mm-dd-yy",3:"#,##0",1:"0",2:"0.00"}

def q(t): return f"{{{NS['m']}}}{t}"

class Styles:
    def __init__(self, z):
        x = ET.fromstring(z.read("xl/styles.xml"))
        self.fonts=[]
        for f in x.find(q("fonts")):
            name = f.find(q("name")); sz=f.find(q("sz")); b=f.find(q("b")); col=f.find(q("color"))
            self.fonts.append((name.get("val") if name is not None else None,
                               float(sz.get("val")) if sz is not None else None,
                               b is not None,
                               col.get("rgb") if col is not None else None))
        self.fills=[]
        for fl in x.find(q("fills")):
            pf = fl.find(q("patternFill"))
            pt = pf.get("patternType") if pf is not None else None
            if pt in (None, "none"):            # normalize "no fill"
                self.fills.append((None, None))
                continue
            fg = pf.find(q("fgColor")) if pf is not None else None
            self.fills.append((pt, fg.get("rgb") if fg is not None else None))
        self.borders=[]
        for bd in x.find(q("borders")):
            # normalize: an absent side OR a present-but-styleless side both mean "no border"
            sides=tuple((bd.find(q(s)).get("style") if bd.find(q(s)) is not None else None) or None
                        for s in ("left","right","top","bottom"))
            self.borders.append(sides)
        self.numfmts=dict(BUILTIN_FMT)
        nf=x.find(q("numFmts"))
        if nf is not None:
            for n in nf:
                self.numfmts[int(n.get("numFmtId"))]=n.get("formatCode")
        self.xfs=[]
        for xf in x.find(q("cellXfs")):
            al=xf.find(q("alignment"))
            align=(al.get("horizontal"), al.get("vertical"), al.get("wrapText")) if al is not None else (None,None,None)
            self.xfs.append((int(xf.get("fontId",0)), int(xf.get("fillId",0)),
                             int(xf.get("borderId",0)), int(xf.get("numFmtId",0)), align))
    def resolve(self, s):
        s=int(s or 0)
        fid,flid,bid,nfid,align=self.xfs[s]
        return (self.fonts[fid], self.fills[flid], self.borders[bid],
                self.numfmts.get(nfid,str(nfid)), align)

def sheet_map(z):
    wbx=ET.fromstring(z.read("xl/workbook.xml"))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid={r.get("Id"):r.get("Target") for r in rels}
    out=[]
    for sh in wbx.find(q("sheets")):
        rI=sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        tgt=rid[rI].lstrip("/")
        if not tgt.startswith("xl/"):
            tgt="xl/"+tgt
        out.append((sh.get("name"), tgt))
    return out

def cells(z, path):
    x=ET.fromstring(z.read(path))
    d={}
    sd=x.find(q("sheetData"))
    for row in sd:
        for c in row:
            d[c.get("r")]=c.get("s")
    return d

def load(path):
    z=zipfile.ZipFile(path); st=Styles(z); sm=sheet_map(z)
    data={name:cells(z,p) for name,p in sm}
    return sm, st, data

bsm,bst,bd = load(sys.argv[1])
tsm,tst,td = load(sys.argv[2])
diffs=[]

# cells to check per sheet (fixed layout)
CHECK = {
 "Summary": ["B1","A3","B3","E3","A4","B4","E4","A10","B10","A11","A12","A18","A19","A20","D20","A21","D21"],
 "Referring Domain Audit": ["A1","Q1","A2","C2","F2","K2"],
 "All Backlinks": ["A1","C1","F1","A2","F2"],
 "Anchor Analysis": ["A1","B1","D1","A2","D2"],
 "Exact Match Anchors": ["A1","G1","A2","F2","G2"],
 "Pending Disavow Lines": ["A1","C1","A2"],
 "Disavow List": ["A1","G1","A2","B2","E2"],
}
for sheet, refs in CHECK.items():
    if sheet not in bd or sheet not in td:
        diffs.append(f"missing sheet {sheet}"); continue
    for ref in refs:
        bs=bd[sheet].get(ref); ts=td[sheet].get(ref)
        bstyle=bst.resolve(bs); tstyle=tst.resolve(ts)
        if bstyle!=tstyle:
            diffs.append(f"[{sheet}] {ref}\n     built={bstyle}\n     tmpl ={tstyle}")

print(f"=== XML STYLE DIFFERENCES: {len(diffs)} ===")
for d in diffs: print(" -", d)
sys.exit(1 if diffs else 0)
