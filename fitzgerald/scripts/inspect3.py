import sys
from xml.etree import ElementTree as ET
M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def q(t): return t.replace('m:',M)
unz=sys.argv[1]
ss=[]
root=ET.parse(f'{unz}/xl/sharedStrings.xml').getroot()
for si in root.findall(q('m:si')):
    ss.append(''.join(t.text or '' for t in si.iter(q('m:t'))))
def val(c):
    t=c.get('t'); v=c.find(q('m:v'))
    if t=='s' and v is not None: return ss[int(v.text)]
    if v is not None: return v.text
    return ''
def cells(sid):
    r=ET.parse(f'{unz}/xl/worksheets/sheet{sid}.xml').getroot()
    d={}
    for row in r.find(q('m:sheetData')).findall(q('m:row')):
        for c in row.findall(q('m:c')):
            d[c.get('r')]=val(c)
    return d
s1=cells('1')
print("=== SUMMARY: status 'what it means' (E4:E9) ===")
for rr in range(4,10):
    print(f"A{rr}={s1.get('A'+str(rr))!r}  | E{rr}={s1.get('E'+str(rr))!r}")
print("\n=== SUMMARY: KEY FINDINGS (A12:A18) ===")
for rr in range(12,19):
    print(f"[{rr-11}] {s1.get('A'+str(rr))}")
print("\n=== PendingDisavow C2:C4 (recommendation wording) ===")
s6=cells('6')
for rr in range(2,5):
    print(f"C{rr}={s6.get('C'+str(rr))!r}")
