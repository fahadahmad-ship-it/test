"""Fold the fetch3 results into the audit data.

Same discipline as the earlier merges: a row is rejected unless it names a domain
that was actually requested, carries non negative integers in range, and does not
contradict another chunk. Existing values are never overwritten.

Fills:
  refdomains.csv   ascore          for domains that had none
  semrush_rd.csv   own_refdomains  for the RD's column
  semrush_traffic.csv              organic keywords and traffic
"""
import csv,glob,sys,collections,os
D='/home/user/test/audit/data/'; F=D+'fetch3/'

def read_req(pat):
    req=set()
    for p in glob.glob(F+pat):
        for l in open(p):
            if l.strip(): req.add(l.strip())
    return req

# ---------- backlinks_overview: ascore + own refdomains ----------
req=read_req('r*.txt')
got={}; rej=collections.Counter(); err=[]
for p in sorted(glob.glob(F+'r*.csv')):
    for r in csv.DictReader(open(p),delimiter=';'):
        d=(r.get('domain') or '').strip().lower()
        a,t,n=(r.get('ascore') or '').strip(),(r.get('total') or '').strip(),(r.get('domains_num') or '').strip()
        if d not in req: rej['never requested']+=1; continue
        if 'ERROR' in (a,t,n): err.append(d); continue
        try: a,t,n=int(float(a)),int(float(t)),int(float(n))
        except Exception: rej['not a number']+=1; continue
        if min(a,t,n)<0 or a>100: rej['out of range']+=1; continue
        if d in got and got[d]!=(a,t,n): rej['chunks disagree']+=1; continue
        got[d]=(a,t,n)
print(f'backlinks_overview | requested {len(req):,} accepted {len(got):,} errors {len(err):,} '
      f'rejected {sum(rej.values()):,} {dict(rej) if rej else ""} missing {len(req-set(got)-set(err)):,}')

# ---------- domain_rank: traffic ----------
treq=read_req('tr_all.txt'); tgot={}; trej=collections.Counter()
for p in sorted(glob.glob(F+'tr_all.csv')):
    for r in csv.DictReader(open(p),delimiter=';'):
        d=(r.get('domain') or '').strip().lower()
        kw,tr=(r.get('organic_keywords') or '').strip(),(r.get('organic_traffic') or '').strip()
        if d not in treq: trej['never requested']+=1; continue
        if 'ERROR' in (kw,tr): continue
        try: kw,tr=int(float(kw)),int(float(tr))
        except Exception: trej['not a number']+=1; continue
        if kw<0 or tr<0: trej['negative']+=1; continue
        tgot[d]=(kw,tr)
print(f'domain_rank        | requested {len(treq):,} accepted {len(tgot):,} '
      f'rejected {sum(trej.values()):,} {dict(trej) if trej else ""}')

if '--write' not in sys.argv:
    print('\ndry run, nothing written. pass --write to apply.')
    raise SystemExit

# refdomains.csv: fill ascore only where blank
rows=list(csv.DictReader(open(D+'refdomains.csv'),delimiter=';'))
seen={r['domain'] for r in rows}; filled=0
for r in rows:
    if not r['ascore'] and r['domain'] in got: r['ascore']=got[r['domain']][0]; filled+=1
added=0
for d,(a,t,n) in got.items():
    if d not in seen:
        rows.append({'domain':d,'ascore':a,'backlinks':'','first_seen':'','ip':'','country':''}); added+=1
w=csv.DictWriter(open(D+'refdomains.csv','w',newline=''),
                 fieldnames=['domain','ascore','backlinks','first_seen','ip','country'],delimiter=';')
w.writeheader(); w.writerows(rows)
print(f'refdomains.csv     | ascore filled {filled}, rows added {added}')

# semrush_rd.csv: the domain's own backlink and referring-domain totals
rd={}
if os.path.exists(D+'semrush_rd.csv'):
    rd={r['domain']:(r['own_backlinks'],r['own_refdomains'])
        for r in csv.DictReader(open(D+'semrush_rd.csv'),delimiter=';')}
for d,(a,t,n) in got.items(): rd.setdefault(d,(t,n))
with open(D+'semrush_rd.csv','w',newline='') as f:
    ww=csv.writer(f,delimiter=';'); ww.writerow(['domain','own_backlinks','own_refdomains'])
    for d in sorted(rd): ww.writerow([d,rd[d][0],rd[d][1]])
print(f'semrush_rd.csv     | {len(rd):,} domains')

# semrush_traffic.csv
tr={r['domain']:(r['organic_keywords'],r['organic_traffic'])
    for r in csv.DictReader(open(D+'semrush_traffic.csv'),delimiter=';')}
for d,(kw,t) in tgot.items(): tr.setdefault(d,(kw,t))
with open(D+'semrush_traffic.csv','w',newline='') as f:
    ww=csv.writer(f,delimiter=';'); ww.writerow(['domain','organic_keywords','organic_traffic'])
    for d in sorted(tr): ww.writerow([d,tr[d][0],tr[d][1]])
print(f'semrush_traffic.csv| {len(tr):,} domains')
