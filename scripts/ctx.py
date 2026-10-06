import csv, sys, collections, re
def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quotechar='"'))
bl=rd(sys.argv[1])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
cand=[r for r in bl if r['Is spam']=='true' and r['Nofollow']=='false']
def show(rs,n=4,lbl=''):
    print(f"\n----- {lbl} (n={len(rs)}) -----")
    for r in rs[:n]:
        print(f"  dom={r['_h']} DR={r['Domain rating']} pagetype={r['Page type']}")
        print(f"  title={r['Referring page title'][:120]}")
        print(f"  url={r['Referring page URL'][:140]}")
        print(f"  L=<{r['Left context'][:90]}> A=<{r['Anchor'][:100]}> R=<{r['Right context'][:90]}>")
        print()
show([r for r in cand if r['Anchor'].startswith('Increase Google Visibility')],5,'A1 Increase Google Visibility')
show([r for r in cand if 'Premium PBN Network' in r['Anchor']],4,'A2 Premium PBN')
show([r for r in cand if r['Anchor'].startswith('Trusted High DA')],3,'A3 Trusted High DA')
show([r for r in cand if r['_h']=='whosmypro.com'],4,'whosmypro')
show([r for r in cand if r['Anchor'].strip().lower() in ('ngwindows.com','www.ngwindows.com','https://www.ngwindows.com/','https://ngwindows.com')],8,'bare-URL anchors')
show([r for r in cand if r['Page type'].startswith('Article')],8,'Article pagetype')
