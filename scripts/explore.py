import sys, csv, io, re
from collections import Counter, defaultdict
from urllib.parse import urlparse
rd_path, bl_path = sys.argv[1], sys.argv[2]
def rows(p):
    raw=open(p,'rb').read().decode('utf-16'); return list(csv.reader(io.StringIO(raw), delimiter='\t'))
rd=rows(rd_path); rh=rd[0]; ri={c.strip():i for i,c in enumerate(rh)}; rd=rd[1:]
bl=rows(bl_path); bh=bl[0]; bi={c.strip():i for i,c in enumerate(bh)}; bl=bl[1:]
def host(u): return urlparse(u).netloc.lower().replace('www.','')
DRof={}; SPof={}; TRof={}
for r in rd:
    if len(r)<len(rh): continue
    DRof[r[ri['Domain']].lower()]=r[ri['DR']]; SPof[r[ri['Domain']].lower()]=r[ri['Is spam']]; TRof[r[ri['Domain']].lower()]=r[ri['Traffic']]

def bucket(h):
    if h.endswith('.store'): return '.store'
    if h.endswith('.shop'): return '.shop'
    if re.match(r'^\d+\.xyz$', h): return 'num.xyz'
    return 'other'
BK=defaultdict(list)
for r in bl:
    if len(r)<len(bh): continue
    h=host(r[bi['Referring page URL']])
    BK[bucket(h)].append(r)

def show(name, rows, n=8):
    print(f"\n===== {name}  (links={len(rows)}, hosts={len(set(host(r[bi['Referring page URL']]) for r in rows))}) =====")
    nof=sum(1 for r in rows if r[bi['Nofollow']].lower()=='true')
    print(f"nofollow links: {nof}/{len(rows)}")
    tg=Counter()
    for r in rows:
        t=r[bi['Target URL']].lower().replace('https://www.controlledcomfort.com','').replace('https://controlledcomfort.com','') or '/'
        tg[t]+=1
    print("top targets:", tg.most_common(5))
    print("sample [host | anchor | target | nofollow | type]:")
    seen=set()
    for r in rows:
        h=host(r[bi['Referring page URL']])
        if h in seen: continue
        seen.add(h)
        t=r[bi['Target URL']].replace('https://www.controlledcomfort.com','').replace('https://controlledcomfort.com','') or '/'
        print(f"  {h[:42]:<42} | {r[bi['Anchor']][:46]:<46} | {t[:28]:<28} | nf={r[bi['Nofollow']]:<5} | {r[bi['Type']]}")
        if len(seen)>=n: break

for b in ['.store','.shop','num.xyz']:
    show(b, BK[b])

# home-page flood: hosts that only point home, DR<20, not in .store/.shop/.xyz — what anchors?
homeflood=[r for r in bl if (r[bi['Target URL']].lower().rstrip('/').endswith('controlledcomfort.com')) and bucket(host(r[bi['Referring page URL']]))=='other']
# anchor frequency in home flood
ac=Counter(r[bi['Anchor']] for r in homeflood)
print("\n===== HOME-PAGE flood (other hosts) =====  links:", len(homeflood))
print("top anchors:", ac.most_common(15))
