import csv,re,collections
csv.field_size_limit(10**9)
NG=re.compile(r'(?<![a-z0-9.-])ngwindows\.com',re.I)
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
listed=set()
for ln in open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8'):
    ln=ln.strip()
    if ln.startswith('domain:'): listed.add(ln[7:].split()[0].split('#')[0].strip())
# ahrefs-known domains
ah=set()
for r in csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-refdomains.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'):
    d=r['Domain'].lower().strip()
    ah.add(d[4:] if d.startswith('www.') else d)
rows=[l.rstrip('\n').split('\t') for l in open('/home/user/test/backlink-audit/work-s4/links_raw.tsv',encoding='utf-8')]
print('semrush rows',len(rows))
g=collections.defaultdict(list)
for p in rows:
    if len(p)<3: continue
    url,anch,nf=p[0],p[1],p[2]
    g[host(url)].append((url,anch,nf))
print('semrush hosts',len(g))
hits=[]
for h,rs in g.items():
    df=[x for x in rs if x[2]=='false' and NG.search(x[1] or '')]
    if df: hits.append((h,df,len(rs)))
print('\nhosts with DOFOLLOW word-boundary ngwindows.com anchor:',len(hits))
miss=[(h,df,n) for h,df,n in hits if h not in listed]
print('of which NOT in disavow file:',len(miss))
for h,df,n in sorted(miss):
    print(f'\n*** {h}   (ahrefs-known={h in ah})  dofollow-ng-rows={len(df)}/{n}')
    for u,a,nf in df[:3]:
        print('   URL :',u[:140]); print('   ANC :',a[:140])
# also: semrush-only domains (not in ahrefs) that ARE listed vs not
sonly=set(g)-ah
print('\nsemrush-only hosts in links_raw:',len(sonly),'| listed:',len(sonly&listed))
