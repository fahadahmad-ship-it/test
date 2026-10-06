import re,sys,csv,collections
p='/home/user/test/backlink-audit/disavow-v2-ahrefs.txt'
def rd(x):
    with open(x,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter='\t',quotechar='"'))
bl=rd('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv')
rdm=rd('/home/user/test/backlink-audit/data/ahrefs/ahrefs-refdomains.tsv')
spam={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
pid={}
for r in bl:
    if r['Nofollow']!='false': continue
    t=r['Referring page title']
    if 'aged domains and backlinks' in t.lower() or re.search(r'Top Domains . Page 168196',t):
        u=re.sub(r'^https?://[^/]+','',r['Referring page URL'])
        pid.setdefault(host(r['Referring page URL']), u)
s=open(p).read()
def rep(m):
    d=m.group(1)
    g='Ahrefs Is spam=true, + fingerprint' if d in spam else 'fingerprint + page title ONLY (Ahrefs did NOT flag it)'
    return f"domain:{d}  # path {pid.get(d,'?')} | ground: {g}"
s=re.sub(r'domain:([^\s]+)  # DR=[^\n]*', rep, s)
open(p,'w').write(s)
print("patched")
