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
VOC=re.compile(r'backlink|pbn|niche edit|guest post|link build|dofollow|domain authority|domain rating|buy links|link selling|seo service|rank(ing)? (first|top) page|high da|trust flow|citation flow|aged domain|t\.me/|telegram|link vendor|white hat seo|tiered link|increase google visibility|boost your google',re.I)
print('=== UNLISTED DOFOLLOW rows with vendor vocabulary in title OR anchor ===')
seen=collections.defaultdict(list)
for r in un:
    blob=(r['Referring page title'] or '')+' || '+(r['Anchor'] or '')
    if VOC.search(blob): seen[host(r['Referring page URL'])].append(r)
for h,rs in sorted(seen.items()):
    print(f'\n--- {h}  ({len(rs)} dofollow rows)  spam={sum(1 for r in rs if r["Is spam"]=="true")}')
    for r in rs[:3]:
        print('   URL  :',r['Referring page URL'][:150])
        print('   TITLE:',(r['Referring page title'] or '')[:150])
        print('   ANCH :',repr(r['Anchor'])[:150])
        print('   TGT  :',r['Target URL'][:100],'| PTYPE:',r['Page type'],'| PCAT:',r['Page category'][:80])
print('\n\n=== UNLISTED DOFOLLOW hosts flagged Is spam=true by Ahrefs ===')
sp=collections.defaultdict(list)
for r in un:
    if r['Is spam']=='true': sp[host(r['Referring page URL'])].append(r)
for h,rs in sorted(sp.items()):
    r=rs[0]
    print(f'{h:35s} {len(rs):3d}df | {(r["Referring page title"] or "")[:70]!r} | anch={r["Anchor"][:50]!r} | {r["Page type"]}')
