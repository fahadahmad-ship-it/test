import csv, sys, collections, re, json
BL, RD = sys.argv[1], sys.argv[2]
def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quotechar='"'))
bl = rd(BL); rdom = rd(RD)
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
cand=[r for r in bl if r['Is spam']=='true' and r['Nofollow']=='false']
print("=== Page type (cand) ==="); [print(f"{n:5d} {k}") for k,n in collections.Counter(r['Page type'] for r in cand).most_common(25)]
print("=== Platform (cand) ==="); [print(f"{n:5d} {k}") for k,n in collections.Counter(r['Platform'] for r in cand).most_common(20)]
print("=== Type (cand) ==="); [print(f"{n:5d} {k}") for k,n in collections.Counter(r['Type'] for r in cand).most_common(10)]
print("=== Language ==="); [print(f"{n:5d} {k}") for k,n in collections.Counter(r['Language'] for r in cand).most_common(12)]
print("=== Top anchors (cand) ==="); [print(f"{n:5d} | {k[:110]}") for k,n in collections.Counter(r['Anchor'] for r in cand).most_common(45)]
print("=== Top domains (cand) ==="); [print(f"{n:5d} {k}") for k,n in collections.Counter(r['_h'] for r in cand).most_common(40)]
print("=== Page category sample ==="); [print(f"{n:5d} {k[:100]}") for k,n in collections.Counter(r['Page category'] for r in cand).most_common(20)]
print("=== Target URLs (cand) ==="); [print(f"{n:5d} {k[:110]}") for k,n in collections.Counter(r['Target URL'] for r in cand).most_common(15)]
