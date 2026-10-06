import csv, collections, re, json
from urllib.parse import urlparse
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
def host(u):
    h=urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h
for r in rows: r['_h']=host(r['Referring page URL'])
byd=collections.defaultdict(list)
for r in rows: byd[r['_h']].append(r)
secs=json.load(open('/tmp/secs.json'))
CLIENT=re.compile(r'(?<![a-z0-9-])ngwindows\.com',re.I)
for S in ['2','3','5']:
    print("="*70); print("SECTION",S)
    tot=0
    for d in secs[S]:
        rs=byd.get(d,[])
        tot+=len(rs)
        nf=collections.Counter(r['Nofollow'] for r in rs)
        sp=collections.Counter(r['Is spam'] for r in rs)
        anch=collections.Counter(r['Anchor'] for r in rs)
        titles=collections.Counter(r['Referring page title'] for r in rs)
        paths=collections.Counter(urlparse(r['Referring page URL']).path for r in rs)
        lost=collections.Counter(r['Lost status'] for r in rs)
        tgt=collections.Counter(host(r['Target URL']) for r in rs)
        named=sum(1 for r in rs if CLIENT.search(r['Anchor']))
        naive=sum(1 for r in rs if 'ngwindows.com' in r['Anchor'].lower())
        pt=collections.Counter(r['Page type'] for r in rs)
        dr=collections.Counter(r['Domain rating'] for r in rs)
        print(f"\n--- {d}  links={len(rs)} DR={list(dr)} nofollow={dict(nf)} spam={dict(sp)} lost={dict(lost)} named_wb={named} naive={naive}")
        print("   targets:",dict(tgt))
        print("   pagetype:",dict(pt))
        for a,c in anch.most_common(4): print(f"   ANCHOR x{c}: {a[:160]}")
        for t,c in titles.most_common(3): print(f"   TITLE  x{c}: {t[:160]}")
        for p,c in paths.most_common(3): print(f"   PATH   x{c}: {p[:120]}")
        print("   lastseen:",sorted(set(r['Last seen'][:10] for r in rs))[:3],"..",sorted(set(r['Last seen'][:10] for r in rs))[-1:])
    print("SECTION",S,"TOTAL LINKS",tot)
