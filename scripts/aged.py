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
drmap={r['Domain'].lower():r['DR'] for r in rdm}
spam={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
net=[r for r in bl if 'aged domains and backlinks' in r['Referring page title'].lower() or re.search(r'Top Domains . Page 168196', r['Referring page title'])]
print(f"aged-domain-market network links={len(net)} domains={len(set(r['_h'] for r in net))}")
d=collections.defaultdict(list)
for r in net: d[r['_h']].append(r)
print(f"{'domain':36s} DR     n  dofollow ahrefs_spam  pageid")
for h,rows in sorted(d.items()):
    nf=sorted(set(r['Nofollow'] for r in rows))
    pid=re.findall(r'\|\s*([\d-]+)$', rows[0]['Referring page title'].strip())
    print(f"{h:36s} {drmap.get(h,'?'):>5} {len(rows):3d}  nf={str(nf):17s} spam={h in spam}  id={pid}")
dof=[h for h,rows in d.items() if any(r['Nofollow']=='false' for r in rows)]
print(f"\ndofollow members: {len(dof)}; of those Ahrefs-flagged: {len([h for h in dof if h in spam])}; MISSED: {len([h for h in dof if h not in spam])}")
print("MISSED dofollow:", sorted(h for h in dof if h not in spam))
