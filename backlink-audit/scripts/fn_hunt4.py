import csv,re,collections
csv.field_size_limit(10**9)
rows=list(csv.DictReader(open('/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv',encoding='utf-8-sig',newline=''),delimiter='\t'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
C=['beihaishitrade.com','nextndt.com','matyesz.hu','maverickmansions.com','newsblogsports.site','ihiwg.org','foaminsulationtips.com','octanecdn.com','dynamix.site','pinqube.com','p.eurekster.com','processregister.com','windowssearch-exp.com','smb.co','ryanssearch.com','cdon.info','find-us-here.com','windowdoor-test.com','klazify.com','bulkdataprovider.com','customerservicetrust.com','homeservicebase.com','koalatyremodel.com','01webdirectory.com','realreviews.org','reputation.authenticfeedback.com','growcycle.com','partnerbase.com','appsruntheworld.com','justgotlive.com','thehomefixitpage.com','buildermuse.com','mylocalservices.com','enthrallinggumption.com','lorddecor.com','toxigon.com','cultivatehd.com','nextfounder.it']
for d in C:
    rs=[r for r in rows if host(r['Referring page URL'])==d]
    df=[r for r in rs if r['Nofollow']=='false']
    if not df: continue
    print(f'\n##### {d}  links={len(rs)} dofollow={len(df)} spam={sum(1 for r in rs if r["Is spam"]=="true")} DR={rs[0]["Domain rating"]}')
    seenp=set()
    for r in df:
        if r['Referring page URL'] in seenp: continue
        seenp.add(r['Referring page URL'])
        print('  URL :',r['Referring page URL'][:140])
        print('  TTL :',(r['Referring page title'] or '')[:130])
        print('  ANC :',repr(r['Anchor'])[:120],'| TGT:',r['Target URL'][:80])
        print('  CTX : ...',(r['Left context'] or '')[-90:],'[[',(r['Right context'] or '')[:90],']]')
        print('  TYPE:',r['Page type'],'| CAT:',(r['Page category'] or '')[:90],'| spam=',r['Is spam'],'| lang=',r['Language'])
        if len(seenp)>=4: break
