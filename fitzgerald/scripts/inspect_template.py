import sys, re, xml.dom.minidom as M
from xml.etree import ElementTree as ET

NS = {
 'm':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
}
def q(t): return t.replace('m:', '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}')

unz = sys.argv[1]

def parse_styles():
    t = ET.parse(f'{unz}/xl/styles.xml').getroot()
    def tag(e): return e.tag.split('}')[-1]
    # numFmts
    numfmts={}
    for nf in t.iter(q('m:numFmt')):
        numfmts[nf.get('numFmtId')]=nf.get('formatCode')
    # fonts
    fonts=[]
    fts = t.find(q('m:fonts'))
    for f in fts.findall(q('m:font')):
        d={}
        for c in f:
            tg=tag(c)
            if tg=='sz': d['sz']=c.get('val')
            elif tg=='name': d['name']=c.get('val')
            elif tg=='b': d['bold']=True
            elif tg=='i': d['italic']=True
            elif tg=='color': d['color']=c.get('rgb') or ('theme:'+str(c.get('theme'))+'/'+str(c.get('tint'))) if (c.get('rgb') or c.get('theme') is not None) else None
        fonts.append(d)
    # fills
    fills=[]
    fls=t.find(q('m:fills'))
    for f in fls.findall(q('m:fill')):
        pf=f.find(q('m:patternFill'))
        d={}
        if pf is not None:
            d['pattern']=pf.get('patternType')
            fg=pf.find(q('m:fgColor'))
            bg=pf.find(q('m:bgColor'))
            if fg is not None: d['fg']=fg.get('rgb') or ('theme:'+str(fg.get('theme')))
            if bg is not None: d['bg']=bg.get('rgb') or ('indexed:'+str(bg.get('indexed')) if bg.get('indexed') else 'theme:'+str(bg.get('theme')))
        fills.append(d)
    # borders
    borders=[]
    bds=t.find(q('m:borders'))
    for b in bds.findall(q('m:border')):
        d={}
        for side in ['left','right','top','bottom']:
            s=b.find(q('m:'+side))
            if s is not None and s.get('style'):
                col=s.find(q('m:color'))
                d[side]=s.get('style')+('/'+(col.get('rgb') or 'theme'+str(col.get('theme'))) if col is not None else '')
        borders.append(d)
    # cellXfs
    xfs=[]
    cxf=t.find(q('m:cellXfs'))
    for x in cxf.findall(q('m:xf')):
        d={'font':x.get('fontId'),'fill':x.get('fillId'),'border':x.get('borderId'),'numFmt':x.get('numFmtId')}
        al=x.find(q('m:alignment'))
        if al is not None:
            d['align']={k:v for k,v in al.attrib.items()}
        xfs.append(d)
    return numfmts,fonts,fills,borders,xfs

numfmts,fonts,fills,borders,xfs=parse_styles()
print("=== NUMFMTS ==="); print(numfmts)
print("\n=== FONTS ===")
for i,f in enumerate(fonts): print(i,f)
print("\n=== FILLS ===")
for i,f in enumerate(fills): print(i,f)
print("\n=== BORDERS ===")
for i,b in enumerate(borders): print(i,b)
print("\n=== CELLXFS ===")
for i,x in enumerate(xfs): print(i,x)
