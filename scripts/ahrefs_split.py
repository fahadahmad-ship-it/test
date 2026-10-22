import sys, csv, io
rd_path=sys.argv[1]
def rows(path):
    raw=open(path,'rb').read().decode('utf-16')
    return list(csv.reader(io.StringIO(raw), delimiter='\t'))
rd=rows(rd_path); rh=rd[0]; ri={c.strip():i for i,c in enumerate(rh)}; rd=rd[1:]
def fnum(x):
    try: return float(x)
    except: return 0.0
genuine=[]; highdr_spam=[]; 
for r in rd:
    if len(r)<len(rh): continue
    dom=r[ri['Domain']]; dr=fnum(r[ri['DR']]); tr=fnum(r[ri['Traffic']]); sp=r[ri['Is spam']].lower()=='true'
    if dr>=20:
        if (not sp) and tr>0:
            genuine.append((dom,r[ri['DR']],int(tr)))
        else:
            highdr_spam.append((dom,r[ri['DR']],int(tr),sp))
print("DR>=20 total:", len(genuine)+len(highdr_spam))
print("  -> likely GENUINE (isspam=false AND traffic>0):", len(genuine))
print("  -> high-DR but zero-traffic or spam-flagged (manipulated DR / PBN):", len(highdr_spam))
print()
print("LIKELY-GENUINE citations (protect — do NOT disavow):")
for d in sorted(genuine, key=lambda x:-x[2]):
    print(f"  {d[0]:<28} DR={d[1]:<5} traffic={d[2]}")
# signature buckets among high-DR spam
import re
store=sum(1 for d in highdr_spam if d[0].endswith('.store'))
shop=sum(1 for d in highdr_spam if d[0].endswith('.shop'))
xyz=sum(1 for d in highdr_spam if d[0].endswith('.xyz'))
print()
print(f"high-DR spam signatures: .store={store}  .shop={shop}  .xyz={xyz}  other={len(highdr_spam)-store-shop-xyz}")
