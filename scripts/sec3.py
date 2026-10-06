import csv, collections, re, json
from urllib.parse import urlparse
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
def host(u):
    h=urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h
for r in rows: r['_h']=host(r['Referring page URL'])
secs=json.load(open('/tmp/secs.json'))
s2=set(secs['2'])
r2=[r for r in rows if r['_h'] in s2]
print("sec2 rows",len(r2),"domains",len(set(r['_h'] for r in r2)))
TR="🏆🏆Boost your Google rankings with Premium PBN & Link Building🏆🏆"
t=set(r['_h'] for r in r2 if r['Referring page title']==TR)
print("hosts with trophy title:",len(t))
p=set(r['_h'] for r in r2 if urlparse(r['Referring page URL']).path=='/all/2066/26.html')
print("hosts with /all/2066/26.html:",len(p))
p2=set(r['_h'] for r in r2 if urlparse(r['Referring page URL']).path=='/all/947/16.html')
print("hosts with /all/947/16.html:",len(p2),sorted(p2))
# does trophy title appear outside sec2?
allt=set(r['_h'] for r in rows if r['Referring page title']==TR)
print("all hosts trophy title in whole export:",len(allt), sorted(allt-t))
# performingwindows trap
pw=[r for r in rows if 'performingwindows' in (r['Anchor']+r['Target URL']+r['Referring page URL']).lower()]
print("\nperformingwindows rows:",len(pw), collections.Counter(r['_h'] for r in pw).most_common(10))
for r in pw[:5]: print("  ",r['_h'],"|",r['Anchor'][:100],"| tgt",r['Target URL'][:80])
# naive vs wb across sec2/3/5
CL=re.compile(r'(?<![a-z0-9-])ngwindows\.com',re.I)
for S in ['2','3','5']:
    ss=set(secs[S]); rr=[r for r in rows if r['_h'] in ss]
    naive=[r for r in rr if 'ngwindows.com' in r['Anchor'].lower()]
    wb=[r for r in rr if CL.search(r['Anchor'])]
    print(f"S{S}: rows={len(rr)} naive_anchor={len(naive)} wb_anchor={len(wb)} mismatch={len(naive)-len(wb)}")
    bad=[r for r in rr if host(r['Target URL'])!='ngwindows.com']
    print("   non-client targets:",len(bad), collections.Counter(host(r['Target URL']) for r in bad))
    print("   redirect chains:",sum(1 for r in rr if r['Redirect Chain URLs'].strip()))
    print("   lost:",collections.Counter(r['Lost status'] for r in rr), "httpcode:",collections.Counter(r['Referring page HTTP code'] for r in rr))
