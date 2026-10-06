import csv, collections, re, sys
from urllib.parse import urlparse
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
def host(u):
    h=urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h
for r in rows: r['_h']=host(r['Referring page URL'])
byd=collections.defaultdict(list)
for r in rows: byd[r['_h']].append(r)

D=open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt',encoding='utf-8').read().split('\n')
# section boundaries
secs={}
cur=None
for l in D:
    m=re.match(r'# SECTION (\d)',l)
    if m: cur=m.group(1); secs[cur]=[]
    elif cur and l.startswith('domain:'):
        secs[cur].append(l.split('#')[0].strip()[7:].strip())
for k in sorted(secs): print("SEC",k,len(secs[k]))
import json
json.dump({k:v for k,v in secs.items()},open('/tmp/secs.json','w'))
