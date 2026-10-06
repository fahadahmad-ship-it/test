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
spamdom={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
byd=collections.defaultdict(list)
for r in bl: byd[r['_h']].append(r)
VEND=re.compile(r'backlink|pbn|link.build|seo|anchor text|domain rating|domain authority|guest post|niche edit|serp|rank first page|link.juice|trust flow|citation flow|da 50|dofollow', re.I)
tail=[]; netw=[]
for d in sorted(spamdom):
    rows=byd.get(d) or byd.get('www.'+d) or []
    if not rows: tail.append((d,rows,'NO-LIVE-LINK')); continue
    txt=' '.join((r['Referring page title']+' '+r['Anchor']+' '+r['Referring page URL']) for r in rows)
    if VEND.search(txt): netw.append(d)
    else: tail.append((d,rows,'tail'))
print(f"flagged domains={len(spamdom)}  matching SEO-vendor vocabulary={len(netw)}  heterogeneous tail={len(tail)}")
print("\n=== HETEROGENEOUS TAIL (flagged but no SEO-vendor vocabulary) ===")
drmap={r['Domain'].lower():r['DR'] for r in rdm}
for d,rows,k in tail:
    if k=='NO-LIVE-LINK':
        print(f"- {d:40s} DR={drmap.get(d):5} [no live link row in export]"); continue
    r=rows[0]
    nf=set(x['Nofollow'] for x in rows)
    print(f"- {d:40s} DR={drmap.get(d):5} n={len(rows):3d} nofollow={sorted(nf)} | {r['Page type'][:26]:26s} | A={r['Anchor'][:52]!r}")
    print(f"      title: {r['Referring page title'][:110]}")
    print(f"      url  : {r['Referring page URL'][:120]}")
