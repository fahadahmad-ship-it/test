import csv,re,collections
csv.field_size_limit(10**9)
rows=list(csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
S4=set("""alljobs.info allwebsitesdirectory.com backlinkon.com backlinksbank.com backlinkstree.com bestwebstats.com domain.com.lc domainanalysis.org domains.com.bz domainsc.com homefinance.co.in indexaward.com indians.cc itsyourgold.com linksnatcher.com pagesearch.net prashikshan.in theface.in tunca.org tyre.pro wallpapers.pro way2check.cv websiterace.com wonvision.com ycm.info youtoo.in""".split())
tot=df=0
for r in rows:
    if host(r['Referring page URL']) in S4:
        tot+=1
        if r['Nofollow']=='false': df+=1
print('S4 total links',tot,'dofollow',df)
# fingerprint host sets across WHOLE export
for frag in ['34962c4ce6e04e66bc6683ce26dd6c07','61a37460a2eed245244c9bc59896bc7b','/page/168196/']:
    hs=sorted({host(r['Referring page URL']) for r in rows if frag in r['Referring page URL']})
    print('\nFP',frag,'hosts',len(hs))
    print('  in S4   :',sorted(h for h in hs if h in S4))
    print('  MISSING :',sorted(h for h in hs if h not in S4))
# titles family: "aged domains" / "Top Domains" anywhere
tl=collections.Counter()
for r in rows:
    t=r['Referring page title']
    if re.search(r'aged domains|Top Domains', t, re.I):
        tl[host(r['Referring page URL'])]+=1
print('\nhosts with aged/TopDomains title:',len(tl))
print('  NOT in S4:',sorted(h for h in tl if h not in S4))
