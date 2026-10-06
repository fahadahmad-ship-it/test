import csv, sys, collections, re, json
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
rdspam={r['Domain'].lower().lstrip('www.'):r for r in rdm}
rdmap={r['Domain'].lower():r for r in rdm}
cand=[r for r in bl if r['Is spam']=='true' and r['Nofollow']=='false']
def fp(r):
    a=r['Anchor']; u=r['Referring page URL']; t=r['Referring page title']
    if a.startswith('Increase Google Visibility with High Quality Backlinks'): return 'F1-dir148096'
    if 'Premium PBN Network Service' in a: return 'F2-pbn-vendor'
    if a.startswith('Trusted High DA Backlinks'): return 'F3-highda-vendor'
    if 'aged domains and backlinks' in t.lower(): return 'F4-aged-domain-market'
    if r['_h']=='whosmypro.com': return 'F5-whosmypro-city'
    return 'F6-other'
byd=collections.defaultdict(list)
for r in cand: byd[r['_h']].append(r)
print("=== fingerprint link/domain counts ===")
c=collections.Counter(fp(r) for r in cand)
dd=collections.defaultdict(set)
for r in cand: dd[fp(r)].add(r['_h'])
for k,n in c.most_common(): print(f"{k:26s} links={n:4d} domains={len(dd[k])}")
# F1 path check
f1=[r for r in cand if fp(r)=='F1-dir148096']
print("\nF1 unique URL paths:", len(set(re.sub(r'^https?://[^/]+','',r['Referring page URL']) for r in f1)))
print("F1 path sample:", collections.Counter(re.sub(r'^https?://[^/]+','',r['Referring page URL']) for r in f1).most_common(6))
print("F1 unique titles:", len(set(r['Referring page title'] for r in f1)))
# F6 detail
f6=[r for r in cand if fp(r)=='F6-other']
print("\n=== F6 other: domains ===")
for h,n in collections.Counter(r['_h'] for r in f6).most_common(100):
    ex=[r for r in f6 if r['_h']==h][0]
    dr=rdmap.get(h,{}).get('DR','?')
    print(f"{n:3d} {h:36s} DR={dr:5s} | {ex['Anchor'][:60]!r} | {ex['Page type'][:28]} | {ex['Referring page title'][:70]}")
