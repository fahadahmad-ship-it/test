import sys
from xml.etree import ElementTree as ET
M='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def q(t): return t.replace('m:',M)
unz=sys.argv[1]

# shared strings
ss=[]
root=ET.parse(f'{unz}/xl/sharedStrings.xml').getroot()
for si in root.findall(q('m:si')):
    txt=''.join(t.text or '' for t in si.iter(q('m:t')))
    ss.append(txt)

def val(c):
    t=c.get('t'); v=c.find(q('m:v')); isv=c.find(q('m:is'))
    if t=='s' and v is not None: return ss[int(v.text)]
    if isv is not None: return ''.join(x.text or '' for x in isv.iter(q('m:t')))
    if v is not None: return v.text
    return ''

sheets={'1':'Summary','2':'RefDomainAudit','3':'AllBacklinks','4':'AnchorAnalysis','5':'ExactMatch','6':'PendingDisavow','7':'DisavowList'}
for sid,nm in sheets.items():
    r=ET.parse(f'{unz}/xl/worksheets/sheet{sid}.xml').getroot()
    print(f"\n########## SHEET {sid} = {nm} ##########")
    sv=r.find(q('m:sheetViews/m:sheetView'))
    if sv is not None:
        print("showGridLines:", sv.get('showGridLines'))
        pane=sv.find(q('m:pane'))
        if pane is not None: print("pane:", pane.attrib)
    fmt=r.find(q('m:sheetFormatPr'))
    if fmt is not None: print("sheetFormatPr:", fmt.attrib)
    af=r.find(q('m:autoFilter'))
    if af is not None: print("autoFilter ref:", af.get('ref'))
    cols=r.find(q('m:cols'))
    if cols is not None:
        print("COLS:")
        for col in cols.findall(q('m:col')):
            print("  ", col.attrib)
    merges=r.find(q('m:mergeCells'))
    if merges is not None:
        print("MERGES:", [mc.get('ref') for mc in merges.findall(q('m:mergeCell'))])
    # rows
    data=r.find(q('m:sheetData'))
    rows=data.findall(q('m:row'))
    limit = len(rows) if sid in ('1',) else 3
    print(f"ROWS (showing {limit} of {len(rows)}):")
    for row in rows[:limit]:
        rh=row.get('ht'); ch=row.get('customHeight')
        cells=[]
        for c in row.findall(q('m:c')):
            cells.append((c.get('r'), c.get('s'), repr(val(c))[:60]))
        print(f"  r{row.get('r')} ht={rh} custom={ch}: {cells}")
