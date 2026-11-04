import sys, zipfile, re, openpyxl
NG=sys.argv[1]; KK=sys.argv[2]
def order(p): return openpyxl.load_workbook(p, read_only=True).sheetnames
def headers(p):
    wb=openpyxl.load_workbook(p, read_only=True, data_only=True); h={}
    for ws in wb.worksheets: h[ws.title]=list(next(ws.iter_rows(values_only=True)))
    return h
def per(p):
    z=zipfile.ZipFile(p); names=z.namelist(); d={}
    for i in range(1,10):
        fn=f'xl/worksheets/sheet{i}.xml'
        if fn not in names: continue
        x=z.read(fn).decode('utf-8','ignore'); g=re.search(r'showGridLines="(\d)"',x)
        d[i]=dict(freeze=('topLeftCell="B2"' in x),af=('<autoFilter' in x),grid=(g.group(1) if g else '1'),merges=len(re.findall(r'<mergeCell ',x)))
    return d
def media(p): return [n for n in zipfile.ZipFile(p).namelist() if 'media' in n]
no,ko=order(NG),order(KK); print("ORDER MATCH:",no==ko); print(" NG",no)
hn,hk=headers(NG),headers(KK)
for t in ko: print(f"  {t}: {'MATCH' if hn.get(t)==hk.get(t) else 'DIFF -> NG:'+str(hn.get(t))}")
pn,pk=per(NG),per(KK)
for i in sorted(pk): print(f"  s{i} NG={pn.get(i)}  KK={pk.get(i)}")
print("media NG:",media(NG)," KK:",media(KK))
