import csv,re,collections
csv.field_size_limit(10**9)
rows=list(csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
def path(u):
    m=re.match(r'https?://[^/]+(/.*)?$',u or ''); return (m.group(1) or '/') if m else '/'
# listed domains in disavow file
listed=set()
for ln in open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8'):
    ln=ln.strip()
    if ln.startswith('domain:'): listed.add(ln[7:].split()[0].split('#')[0].strip())
print('listed domains in file:',len(listed))
# dofollow rows whose host not listed
un=[r for r in rows if host(r['Referring page URL']) not in listed and r['Nofollow']=='false']
print('dofollow rows from UNLISTED hosts:',len(un),'hosts:',len({host(r['Referring page URL']) for r in un}))
# cluster by exact path
c=collections.defaultdict(set)
for r in un: c[path(r['Referring page URL'])].add(host(r['Referring page URL']))
print('\n=== SHARED EXACT PATH across >=2 unlisted hosts (dofollow) ===')
for p,hs in sorted(c.items(),key=lambda x:-len(x[1])):
    if len(hs)>=2:
        print(f'{len(hs):3d}  {p[:110]}')
        print('      ',sorted(hs)[:25])
