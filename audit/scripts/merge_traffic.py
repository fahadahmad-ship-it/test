"""Merge the per-chunk Semrush traffic fetches, validating before anything is trusted.

Every row must correspond to a domain that was actually requested, carry integer
values, and appear exactly once. Anything that fails is reported rather than
silently absorbed, because these figures drive a disavow decision.
"""
import csv,glob,os,sys
D='/home/user/test/audit/data/'
asked=set()
for f in sorted(glob.glob(D+'chunks/chunk*.txt')):
    asked|={l.strip() for l in open(f) if l.strip()}
rows={}; bad=[]; dupes=[]
for f in sorted(glob.glob(D+'chunks/out*.csv')):
    for r in csv.DictReader(open(f),delimiter=';'):
        d=(r.get('domain') or '').strip()
        if not d: continue
        if d not in asked: bad.append((f,d,'not in any chunk')); continue
        kw,tr=(r.get('organic_keywords') or '').strip(),(r.get('organic_traffic') or '').strip()
        if kw=='ERROR' or tr=='ERROR': bad.append((f,d,'agent reported ERROR')); continue
        try: kw=int(float(kw)); tr=int(float(tr))
        except ValueError: bad.append((f,d,f'non numeric: {kw!r} {tr!r}')); continue
        if kw<0 or tr<0: bad.append((f,d,'negative')); continue
        if d in rows and rows[d]!=(kw,tr): dupes.append((d,rows[d],(kw,tr)))
        rows[d]=(kw,tr)
missing=sorted(asked-set(rows))
print(f"requested      : {len(asked):,}")
print(f"returned       : {len(rows):,}")
print(f"missing        : {len(missing):,}")
print(f"rejected rows  : {len(bad):,}")
print(f"conflicting    : {len(dupes):,}")
for f,d,why in bad[:10]: print(f"   rejected {d} ({why})")
for d,a,b in dupes[:10]: print(f"   conflict {d}: {a} vs {b}")
if missing[:10]: print("   missing e.g.:", ', '.join(missing[:10]))

if '--write' in sys.argv:
    existing={r['domain']:(int(r['organic_keywords']),int(r['organic_traffic']))
              for r in csv.DictReader(open(D+'semrush_traffic.csv'),delimiter=';')}
    existing.update(rows)
    with open(D+'semrush_traffic.csv','w',newline='') as f:
        w=csv.writer(f,delimiter=';'); w.writerow(['domain','organic_keywords','organic_traffic'])
        for d in sorted(existing): w.writerow([d,existing[d][0],existing[d][1]])
    print(f"\nwrote semrush_traffic.csv with {len(existing):,} domains")
