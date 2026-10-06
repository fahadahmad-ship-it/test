import csv, re, sys, collections
csv.field_size_limit(10**9)
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig',newline=''),delimiter='\t'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
def reg(h):
    return h
S4="""alljobs.info allwebsitesdirectory.com backlinkon.com backlinksbank.com backlinkstree.com bestwebstats.com domain.com.lc domainanalysis.org domains.com.bz domainsc.com homefinance.co.in indexaward.com indians.cc itsyourgold.com linksnatcher.com pagesearch.net prashikshan.in theface.in tunca.org tyre.pro wallpapers.pro way2check.cv websiterace.com wonvision.com ycm.info youtoo.in""".split()
by=collections.defaultdict(list)
for r in rows:
    h=host(r['Referring page URL'])
    by[h].append(r)
print("=== SECTION 4 PER-DOMAIN ===")
for d in S4:
    hits=[(h,rs) for h,rs in by.items() if h==d or h.endswith('.'+d)]
    tot=sum(len(rs) for _,rs in hits)
    if not hits:
        print(f"\n### {d}  *** NOT FOUND IN AHREFS ***"); continue
    allr=[r for _,rs in hits for r in rs]
    df=[r for r in allr if r['Nofollow']=='false']
    spam=sum(1 for r in allr if r['Is spam']=='true')
    print(f"\n### {d}  links={tot} dofollow={len(df)} spamflag={spam} DR={allr[0]['Domain rating']}")
    seen=set()
    for r in allr:
        key=(r['Referring page URL'],r['Anchor'],r['Nofollow'])
        if key in seen: continue
        seen.add(key)
        print("   URL   :",r['Referring page URL'])
        print("   TITLE :",r['Referring page title'][:160])
        print("   ANCHOR:",repr(r['Anchor'])[:160]," NF=",r['Nofollow']," SPAM=",r['Is spam'])
        print("   TARGET:",r['Target URL'])
        print("   LCTX  :",(r['Left context'] or '')[:200])
        print("   RCTX  :",(r['Right context'] or '')[:200])
        print("   PTYPE :",r['Page type'],"| PCAT:",r['Page category'],"| LOST:",r['Lost status'],"| Type:",r['Type'])
