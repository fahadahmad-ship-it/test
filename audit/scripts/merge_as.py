"""Merge agent fetched Authority Scores into refdomains.csv.

Same discipline as the traffic merge: a row is rejected unless it names a domain
that was actually requested, carries non negative integers, and does not disagree
with another chunk. Domains that already had a score are never overwritten.
"""
import csv,os,sys,collections,glob
D='/home/user/test/audit/data/'; F=D+'fetch2/'
req=set()
for p in glob.glob(F+'*.txt'):
    for l in open(p):
        if l.strip(): req.add(l.strip())
got={}; rej=collections.Counter(); err=[]
for p in sorted(glob.glob(F+'*.csv')):
    for r in csv.DictReader(open(p),delimiter=';'):
        d=(r.get('domain') or '').strip().lower()
        a,t,n=(r.get('ascore') or '').strip(),(r.get('total') or '').strip(),(r.get('domains_num') or '').strip()
        if d not in req: rej['never requested']+=1; continue
        if 'ERROR' in (a,t,n): err.append(d); continue
        try: a,t,n=int(float(a)),int(float(t)),int(float(n))
        except Exception: rej['not a number']+=1; continue
        if min(a,t,n)<0: rej['negative']+=1; continue
        if a>100: rej['score out of range']+=1; continue
        if d in got and got[d]!=(a,t,n): rej['chunks disagree']+=1; continue
        got[d]=(a,t,n)
print(f'requested {len(req):,} | accepted {len(got):,} | errors {len(err):,} | '
      f'rejected {sum(rej.values()):,} {dict(rej) if rej else ""} | missing {len(req-set(got)-set(err)):,}')
rows=list(csv.DictReader(open(D+'refdomains.csv'),delimiter=';'))
have={r['domain'] for r in rows if r['ascore']}
over=[d for d in got if d in have]
print(f'would overwrite an existing score: {len(over)} (not done)')
dist=collections.Counter(v[0] for v in got.values())
print('score distribution:', dict(sorted(dist.items())))
print('scoring 20 or above:', sum(1 for v in got.values() if v[0]>=20))
if '--write' in sys.argv:
    seen={r['domain'] for r in rows}
    for r in rows:
        if not r['ascore'] and r['domain'] in got: r['ascore']=got[r['domain']][0]
    for d,(a,t,n) in got.items():
        if d not in seen:
            rows.append({'domain':d,'ascore':a,'backlinks':'','first_seen':'','ip':'','country':''})
    w=csv.DictWriter(open(D+'refdomains.csv','w',newline=''),
                     fieldnames=['domain','ascore','backlinks','first_seen','ip','country'],delimiter=';')
    w.writeheader(); w.writerows(rows)
    # the referring domain's own referring-domain count, for the RD's column
    with open(D+'semrush_rd.csv','w',newline='') as f:
        ww=csv.writer(f,delimiter=';'); ww.writerow(['domain','own_backlinks','own_refdomains'])
        for d,(a,t,n) in sorted(got.items()): ww.writerow([d,t,n])
    print(f'WROTE refdomains.csv and semrush_rd.csv ({len(got):,} domains)')
