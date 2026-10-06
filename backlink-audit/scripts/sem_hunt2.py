import csv,re,collections
NG=re.compile(r'(?<![a-z0-9.-])ngwindows\.com',re.I)
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
listed=set()
for ln in open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8'):
    ln=ln.strip()
    if ln.startswith('domain:'): listed.add(ln[7:].split()[0].split('#')[0].strip())
rows=[l.rstrip('\n').split('\t') for l in open('/home/user/test/backlink-audit/work-s4/links_raw.tsv',encoding='utf-8') if l.strip()]
def cov(h): return h in listed or any(h.endswith('.'+d) for d in listed)
print('=== SEMRUSH: marketplace fingerprint paths ===')
for frag in ['34962c4ce6e04e66bc6683ce26dd6c07','61a37460a2eed245244c9bc59896bc7b','/page/168196/']:
    hs=collections.defaultdict(lambda:[0,0])
    for p in rows:
        if frag in p[0]:
            hs[host(p[0])][0]+=1
            if len(p)>2 and p[2]=='false': hs[host(p[0])][1]+=1
    print(f'\n-- {frag}: {len(hs)} hosts')
    for h,(t,d) in sorted(hs.items()):
        print(f'   {"COVERED " if cov(h) else "*MISSING"} {h:35s} rows={t} df={d}')
print('\n=== SEMRUSH: random-token listing-path kit  /<token>-l|li|list|listing/ ===')
pat=re.compile(r'/[a-z0-9]{6,12}-(l|li|list|listing)/?$')
hs=collections.defaultdict(lambda:[0,0,set()])
for p in rows:
    u=p[0].split('?')[0]
    if pat.search(u):
        h=host(u); hs[h][0]+=1
        if len(p)>2 and p[2]=='false': hs[h][1]+=1
        hs[h][2].add(u)
for h,(t,d,us) in sorted(hs.items()):
    print(f'   {"COVERED " if cov(h) else "*MISSING"} {h:28s} rows={t} df={d}  {sorted(us)[0][:80]}')
print('\n=== SEMRUSH: vendor-ish paths among UNCOVERED hosts with any dofollow ng anchor OR vendor path words ===')
VP=re.compile(r'link-building|backlink|seo-link|buy-link|pbn|niche-edit|guest-post|aged-domain',re.I)
seen=collections.defaultdict(list)
for p in rows:
    h=host(p[0])
    if cov(h): continue
    if len(p)>2 and p[2]=='false' and (VP.search(p[0]) and NG.search(p[1] or '')):
        seen[h].append(p)
for h,ps in sorted(seen.items()):
    print(f'   *{h}: {ps[0][0][:110]} | {ps[0][1][:90]}')
