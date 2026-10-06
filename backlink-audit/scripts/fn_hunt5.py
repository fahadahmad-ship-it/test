import csv,re,collections
csv.field_size_limit(10**9)
rows=list(csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
listed=set()
for ln in open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8'):
    ln=ln.strip()
    if ln.startswith('domain:'): listed.add(ln[7:].split()[0].split('#')[0].strip())
print('=== /all/<n>/<n> PBN PATH FAMILY (Section 2 structure) ===')
pat=re.compile(r'/all/\d+/\d+')
g=collections.defaultdict(lambda:[0,0])
for r in rows:
    if pat.search(r['Referring page URL']):
        h=host(r['Referring page URL']); g[h][0]+=1
        if r['Nofollow']=='false': g[h][1]+=1
for h,(t,d) in sorted(g.items()):
    print(f'  {"LISTED  " if h in listed else "*MISSING"} {h:32s} links={t} dofollow={d}')
print('\n=== article.php / injected-script FAMILY ===')
for r in rows:
    if 'article.php' in r['Referring page URL'] or re.search(r'/[a-z0-9]{5,8}/[a-z0-9-]+$',''):
        h=host(r['Referring page URL'])
        print(f'  {"LISTED " if h in listed else "*MISS "} {h:28s} NF={r["Nofollow"]} {r["Referring page URL"][:110]}')
print('\n=== ANCHOR "Our Family | North Georgia Replacement Windows" ===')
for r in rows:
    if 'Our Family' in (r['Anchor'] or ''):
        print(' ',host(r['Referring page URL']),'NF=',r['Nofollow'],r['Referring page URL'][:110])
print('\n=== Page category contains "SEO and marketing", dofollow, UNLISTED ===')
for r in rows:
    if 'SEO and marketing' in (r['Page category'] or '') and r['Nofollow']=='false' and host(r['Referring page URL']) not in listed:
        print(' ',host(r['Referring page URL']),'|',r['Referring page URL'][:90],'|',(r['Referring page title'] or '')[:70])
