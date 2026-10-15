import csv,collections,re,json
D='/home/user/test/audit/data/'
LNK=list(csv.DictReader(open(D+'links_all.csv'),delimiter=';'))
AUDD={r['domain']:r for r in csv.DictReader(open(D+'domain_audit.csv'),delimiter=';')}
def tk(u):
    if '/location/' in u or re.search(r'/gas-?station-canopy-construction-',u): return 'Geo landing page'
    if '/service/' in u: return 'Service page'
    if u.rstrip('/') in ('https://newimagecanopy.com','http://newimagecanopy.com'): return 'Homepage'
    return 'Other'
rows=[]
for r in LNK:
    a=(r['anchor'] or '').strip()
    if not a or not r['atype'].startswith('Exact match'): continue
    if AUDD.get(r['rd'],{}).get('status','')=='Review (Host Artefact)': continue
    rows.append(r)
seen={r['rd'] for r in rows}
for r in LNK:
    d=r['rd']
    if d in seen or not AUDD.get(d,{}).get('status','').startswith('Held'): continue
    rows.append(r); seen.add(d)
# candidates per (domain, anchor), best first
g=collections.defaultdict(list)
for r in rows:
    k=(r['rd'],(r['anchor'] or '').strip() or '(no anchor text)')
    g[k].append(r)
out={}
for k,v in g.items():
    v.sort(key=lambda x:(x['nofollow']=='true', tk(x['target_url']) not in ('Service page','Geo landing page'), x['source_url']))
    seenu=[];
    for x in v:
        if x['source_url'] not in seenu: seenu.append(x['source_url'])
    out['\t'.join(k)]=seenu
json.dump(out,open('/home/user/test/audit/check/cands.json','w'))
allu=sorted({u for v in out.values() for u in v})
open('/home/user/test/audit/check/urls.txt','w').write('\n'.join(allu))
print('groups',len(out),'unique urls',len(allu))
