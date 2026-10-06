import csv,re,collections
csv.field_size_limit(10**9)
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
listed=[]
for ln in open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8'):
    ln=ln.strip()
    if ln.startswith('domain:'): listed.append(ln[7:].split()[0].split('#')[0].strip())
L=set(listed); print('file entries:',len(listed),'unique:',len(L))
A=list(csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'))
S=[l.rstrip('\n').split('\t') for l in open('/home/user/test/backlink-audit/work-s4/links_raw.tsv',encoding='utf-8') if l.strip()]
for frag in ['34962c4ce6e04e66bc6683ce26dd6c07','61a37460a2eed245244c9bc59896bc7b','/page/168196/']:
    ha={host(r['Referring page URL']) for r in A if frag in r['Referring page URL']}
    hs={host(p[0]) for p in S if frag in p[0]}
    u=ha|hs
    print(f'\n{frag}: ahrefs={len(ha)} semrush={len(hs)} UNION={len(u)} covered={len(u&L)} new={sorted(u-L)}')
# matyesz / injection kit detail
print('\n=== matyesz.hu rows ===')
for r in A:
    if host(r['Referring page URL'])=='matyesz.hu':
        print(' ',r['Referring page URL'],'| NF=',r['Nofollow'],'| anchor=',repr(r['Anchor'])[:90],'| tgt=',r['Target URL'][:60])
print('\n=== semrush rows for matyesz/nextndt/beihaishitrade/newsblogsports ===')
for p in S:
    if host(p[0]) in {'matyesz.hu','nextndt.com','beihaishitrade.com','newsblogsports.site','ihiwg.org','maverickmansions.com'}:
        print(' ',p[0][:110],'|',p[1][:70],'| nf=',p[2])
