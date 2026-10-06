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
def f(x):
    try: return float(x)
    except: return 0.0
spam=[r for r in rdm if r['Is spam']=='true']
print("flagged DR>=30:", sum(1 for r in spam if f(r['DR'])>=30))
print("flagged DR>=30 with >=1 dofollow link:", sum(1 for r in spam if f(r['DR'])>=30 and int(r['Dofollow links'] or 0)>0))
print("flagged with dofollow links:", sum(1 for r in spam if int(r['Dofollow links'] or 0)>0))
kept=[r for r in rdm if r['Is spam']=='false']
print(f"\n=== KEEP-LIST: {len(kept)} domains (Is spam=false) ===")
bydom=collections.defaultdict(list)
for r in bl: bydom[r['_h']].append(r)
# sanity check: any Is spam=false domain carrying vendor anchor / PBN language?
VEND=re.compile(r'backlink|pbn|dofollow|domain rating|domain authority|guest post|niche edit|rank first page|link building|trust flow|citation flow', re.I)
sus=[]
for r in kept:
    d=r['Domain'].lower(); rows=bydom.get(d) or bydom.get('www.'+d) or []
    txt=' '.join(x['Anchor']+' '+x['Referring page title'] for x in rows)
    if VEND.search(txt): sus.append((d,r['DR'],rows))
print(f"\nMISFLAG CHECK — keep-list domains carrying SEO-vendor vocabulary: {len(sus)}")
for d,dr,rows in sus:
    x=rows[0]
    print(f"  {d:34s} DR={dr:5} nofollow={sorted(set(y['Nofollow'] for y in rows))} | A={x['Anchor'][:60]!r}")
    print(f"       {x['Referring page title'][:100]}")
print("\n=== top keep-list by DR ===")
for r in sorted(kept,key=lambda r:-f(r['DR']))[:30]:
    print(f"  DR={r['DR']:>5} {r['Domain']:34s} links={r['Links to target']:>3} dofollow={r['Dofollow links']:>3}")
print("\n=== keep-list page types ===")
kd={r['Domain'].lower() for r in kept}
kr=[r for r in bl if r['Is spam']=='false']
print(collections.Counter(r['Page type'] for r in kr).most_common(12))
print("keep links dofollow:",collections.Counter(r['Nofollow'] for r in kr))
