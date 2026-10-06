import csv, sys, collections, re
def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quotechar='"'))
bl=rd(sys.argv[1])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
TGT={'ngwindows.com'}
rows=[r for r in bl if (r['Redirect Chain URLs'] or '').strip()]
print("rows with chain:",len(rows))
third=collections.Counter(); exam=collections.defaultdict(list)
for r in rows:
    urls=[u for u in re.split(r'[,\s]+', r['Redirect Chain URLs'].strip()) if u.startswith('http')]
    hs=[host(u) for u in urls]
    ext=[h for h in hs if h not in TGT]
    for h in set(ext):
        third[h]+=1
        if len(exam[h])<2: exam[h].append((r['Referring page URL'],r['Anchor'][:60],r['Redirect Chain URLs'][:260],r['Redirect Chain status codes'],r['Is spam'],r['Nofollow']))
print("\n=== third-party redirect hosts ===")
for h,n in third.most_common(60):
    print(f"{n:5d} {h}")
print("\n=== examples ===")
for h in ['atlantabestmedia.com','bizhwy.com']:
    for e in exam.get(h,[]): print(h,'|',e)
# chains with no third party at all
nz=[r for r in rows if not [h for h in [host(u) for u in re.split(r'[,\s]+', r['Redirect Chain URLs'].strip()) if u.startswith('http')] if h not in TGT]]
print("\nchains purely self:",len(nz))
print("status code patterns:",collections.Counter(r['Redirect Chain status codes'] for r in rows).most_common(15))
