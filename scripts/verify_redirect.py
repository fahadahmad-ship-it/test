import csv,re,collections,sys
def rd(p,d='\t'):
    with open(p,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter=d,quotechar='"'))
bl=rd('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv')
rdm=rd('/home/user/test/backlink-audit/data/ahrefs/ahrefs-refdomains.tsv')
raw=[l.rstrip('\n').split('\t') for l in open('/tmp/lr.tsv',encoding='utf-8',errors='replace') if l.strip()]
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
ahr={r['Domain'].lower() for r in rdm}
# semrush /dir/ campaigns
camp=collections.defaultdict(lambda: collections.defaultdict(set))  # host -> campaign -> anchors
for r in raw:
    m=re.search(r'/dir/([a-z-]+-\d+)$', r[0])
    if m: camp[host(r[0])][m.group(1)].add(r[1])
both=sorted(set(camp)&ahr)
print(f"Semrush /dir/ hosts={len(camp)}; also in Ahrefs={len(both)}")
allc=collections.Counter()
for h,c in camp.items(): allc.update(c.keys())
print("\ncampaign IDs in Semrush /dir/ data:")
for c,n in allc.most_common(): print(f"  {n:4d} hosts  {c}")
# brand named in anchors per campaign
NG=re.compile(r'(?<![A-Za-z0-9-])(?:www\.)?([a-z0-9-]+windows?\.(?:com|net))',re.I)
cb=collections.defaultdict(collections.Counter)
for h,c in camp.items():
    for cid,ancs in c.items():
        for a in ancs:
            for b in NG.findall(a): cb[cid][b.lower()]+=1
print("\ncampaign -> brand named in anchor:")
for cid,cnt in sorted(cb.items()): print(f"  {cid:46s} {dict(cnt)}")
# Ahrefs side for the 'both' hosts
abl=collections.defaultdict(set)
for r in bl:
    m=re.search(r'/dir/([a-z-]+-\d+)$', r['Referring page URL'])
    if m: abl[host(r['Referring page URL'])].add(m.group(1))
print(f"\nFor the {len(both)} hosts in BOTH tools:")
multi=0
for h in both:
    sc=set(camp[h]); ac=abl.get(h,set())
    if len(sc)>1: multi+=1
print(f"  hosts where Semrush shows >1 campaign crediting ngwindows.com: {multi}/{len(both)}")
print(f"  hosts where Ahrefs shows ONLY 148096: {sum(1 for h in both if abl.get(h)=={'quality-authority-backlinks-148096'})}/{len(both)}")
print(f"  Ahrefs campaign IDs seen overall: {set().union(*abl.values()) if abl else set()}")
