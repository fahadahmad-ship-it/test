import csv, sys, collections, re
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
spam={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
# shared exact title across >=3 distinct hosts
t=collections.defaultdict(set); tr=collections.defaultdict(list)
for r in bl:
    if r['Referring page title'].strip():
        t[r['Referring page title']].add(r['_h']); tr[r['Referring page title']].append(r)
print("=== titles shared by >=3 distinct hosts ===")
for k,v in sorted(t.items(), key=lambda x:-len(x[1])):
    if len(v)<3: break
    rows=tr[k]; df={r['_h'] for r in rows if r['Nofollow']=='false'}
    unfl=sorted(df-spam)
    print(f"hosts={len(v):4d} dofollow_hosts={len(df):4d} unflagged_dofollow={len(unfl):3d} | {k[:95]}")
    if unfl and len(unfl)<=25: print(f"     unflagged: {unfl}")
# shared exact path across >=3 hosts
p=collections.defaultdict(set); pr=collections.defaultdict(list)
for r in bl:
    path=re.sub(r'^https?://[^/]+','',r['Referring page URL'])
    if len(path)>6: p[path].add(r['_h']); pr[path].append(r)
print("\n=== paths shared by >=3 distinct hosts ===")
for k,v in sorted(p.items(), key=lambda x:-len(x[1])):
    if len(v)<3: break
    rows=pr[k]; df={r['_h'] for r in rows if r['Nofollow']=='false'}
    print(f"hosts={len(v):4d} dofollow_hosts={len(df):4d} unflagged_dofollow={len(sorted(df-spam)):3d} | {k[:95]}")
