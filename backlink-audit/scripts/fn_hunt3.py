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
un=[r for r in rows if host(r['Referring page URL']) not in listed and r['Nofollow']=='false']
print('=== ALL 138 UNLISTED DOFOLLOW HOSTS ===')
g=collections.defaultdict(list)
for r in un: g[host(r['Referring page URL'])].append(r)
for h,rs in sorted(g.items()):
    print(f'{h:40s} {len(rs):3d} | {(rs[0]["Referring page title"] or "")[:62]!r:66s} | {rs[0]["Page type"][:30]}')
# verify the big nofollow exclusions really are 100% nofollow
print('\n=== NOFOLLOW-EXCLUSION VERIFICATION ===')
for frag,label in [('after-years-of-struggling-with-low-engagement','SEOExpress 577'),
                   ('ysh5qk2-what-29-campaigns','ysh5qk2 65'),
                   ('/bibiacseo/','bibiacseo'),('/buytfnseo/','buytfnseo'),('/ashgeoseo/','ashgeoseo'),
                   ('/report/97119-20','report'),('/stats/97119-20','stats'),
                   ('/dir/quality-authority-backlinks-148096','Sec1 /dir/ 148096')]:
    sub=[r for r in rows if frag in r['Referring page URL']]
    hs={host(r['Referring page URL']) for r in sub}
    df=[r for r in sub if r['Nofollow']=='false']
    print(f'{label:22s} rows={len(sub):4d} hosts={len(hs):4d} DOFOLLOW={len(df)}  unlisted-dofollow-hosts={sorted({host(r["Referring page URL"]) for r in df} - listed)}')
# title-based exclusions
for t,label in [('Directory Pages Index','DirIndex'),('Domain Report','DomReport'),('Website Stats','WebStats'),('Dark Side Links','DarkSide')]:
    sub=[r for r in rows if t.lower() in (r['Referring page title'] or '').lower()]
    df=[r for r in sub if r['Nofollow']=='false']
    print(f'{label:22s} rows={len(sub):4d} hosts={len({host(r["Referring page URL"]) for r in sub}):4d} DOFOLLOW={len(df)} unlisted-df-hosts={sorted({host(r["Referring page URL"]) for r in df} - listed)}')
for d in ['intermeritocracy.com','monetaryhistoryofworld.com','worldbusinesspromote.com','marketingexperts.click','dreamscometroup.com']:
    sub=[r for r in rows if host(r['Referring page URL'])==d]
    print(f'{d:30s} rows={len(sub):3d} dofollow={sum(1 for r in sub if r["Nofollow"]=="false")}')
