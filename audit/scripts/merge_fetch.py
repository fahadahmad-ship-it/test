"""Merge the agent fetched Semrush rows into semrush_traffic.csv.

Nothing is trusted on the way in. A row is rejected unless it names a domain that
was actually requested in that chunk, carries two non negative integers, and does
not contradict a value already held for the same domain.
"""
import csv,os,sys,collections
D='/home/user/test/audit/data/'; F=D+'fetch/'
req={}                                  # domain -> chunk it was requested in
for i in range(1,13):
    p=F+f't{i}.txt'
    if not os.path.exists(p): continue
    for l in open(p):
        d=l.strip()
        if d: req[d]=i
got={}; rej=collections.Counter(); err=[]
for i in range(1,13):
    p=F+f't{i}.csv'
    if not os.path.exists(p): rej[f'chunk {i} missing']+=1; continue
    for r in csv.DictReader(open(p),delimiter=';'):
        d=(r.get('domain') or '').strip().lower()
        kw=(r.get('organic_keywords') or '').strip(); tr=(r.get('organic_traffic') or '').strip()
        if d not in req: rej['domain was never requested']+=1; continue
        if req[d]!=i:    rej['domain returned by the wrong chunk']+=1; continue
        if kw=='ERROR' or tr=='ERROR': err.append(d); continue
        try: kw=int(float(kw)); tr=int(float(tr))
        except Exception: rej['value is not a number']+=1; continue
        if kw<0 or tr<0: rej['negative value']+=1; continue
        if d in got and got[d]!=(kw,tr): rej['two chunks disagree']+=1; continue
        got[d]=(kw,tr)
old={r['domain']:r for r in csv.DictReader(open(D+'semrush_traffic.csv'),delimiter=';')}
clash=[d for d in got if d in old and
       (int(float(old[d]['organic_keywords'] or 0)),int(float(old[d]['organic_traffic'] or 0)))!=got[d]]
print(f'requested      {len(req):,}')
print(f'accepted       {len(got):,}')
print(f'API errors     {len(err):,}')
print(f'rejected       {sum(rej.values()):,}  {dict(rej) if rej else ""}')
print(f'missing        {len(set(req)-set(got)-set(err)):,}')
print(f'clashes with existing held-domain data: {len(clash)}')
if '--write' in sys.argv:
    out=dict(old)
    for d,(kw,tr) in got.items():
        out.setdefault(d,{'domain':d}); out[d]={'domain':d,'organic_keywords':kw,'organic_traffic':tr}
    w=csv.DictWriter(open(D+'semrush_traffic.csv','w',newline=''),
                     fieldnames=['domain','organic_keywords','organic_traffic'],delimiter=';')
    w.writeheader()
    for d in sorted(out): w.writerow(out[d])
    print(f'WROTE semrush_traffic.csv with {len(out):,} domains')
