import csv, sys, collections, re, random
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
byd=collections.defaultdict(list)
for r in bl: byd[r['_h']].append(r)
spam=[r['Domain'].lower() for r in rdm if r['Is spam']=='true']
random.seed(20261006)
smp=random.sample(sorted(spam),25)
drmap={r['Domain'].lower():r['DR'] for r in rdm}
for i,d in enumerate(sorted(smp),1):
    rows=byd.get(d) or byd.get('www.'+d) or []
    print(f"\n### {i}. {d}  DR={drmap.get(d)}  links_in_export={len(rows)}")
    for r in rows[:3]:
        print(f"   url   : {r['Referring page URL'][:150]}")
        print(f"   title : {r['Referring page title'][:130]}")
        print(f"   anchor: {r['Anchor'][:110]!r}  nofollow={r['Nofollow']} ugc={r['UGC']} sponsored={r['Sponsored']}")
        print(f"   ptype : {r['Page type']} | {r['Page category'][:80]}")
        print(f"   ctx   : L=<{r['Left context'][:70]}> R=<{r['Right context'][:70]}>")
    if not rows: print("   (no live link rows)")
