import csv, sys
from collections import Counter
from urllib.parse import urlparse
rd=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig',newline=''),delimiter='\t'))
bl=list(csv.DictReader(open(sys.argv[2],encoding='utf-8-sig',newline=''),delimiter='\t'))

def host(u):
    try: return urlparse(u).netloc.lower().replace('www.','')
    except: return ''

print("=== THE DISAVOW-RELEVANT SLICE: Ahrefs spam=true AND dofollow AND live ===")
cand=[r for r in bl if r.get('Is spam')=='true' and r.get('Nofollow')=='false']
doms={host(r.get('Referring page URL','')) for r in cand}
print(f"links: {len(cand)}   distinct referring domains: {len(doms)}")

print("\n=== by contrast: spam but nofollow (NOT disavowable) ===")
nf=[r for r in bl if r.get('Is spam')=='true' and r.get('Nofollow')=='true']
print(f"links: {len(nf)}   domains: {len({host(r.get('Referring page URL','')) for r in nf})}")

print("\n=== DR distribution of Ahrefs spam-flagged referring domains ===")
b=Counter()
for r in rd:
    if r.get('Is spam')!='true': continue
    try: dr=float(r.get('DR') or 0)
    except: dr=0
    b['DR 0-5' if dr<=5 else 'DR 6-29' if dr<30 else 'DR 30-59' if dr<60 else 'DR 60+']+=1
for k in ['DR 0-5','DR 6-29','DR 30-59','DR 60+']: print(f"  {k:10} {b[k]}")

print("\n=== HIGH-DR SPAM (DR>=30, Ahrefs-flagged) — the ones an authority filter would miss ===")
hi=[(r['Domain'], r.get('DR'), r.get('Links to target')) for r in rd
    if r.get('Is spam')=='true' and (r.get('DR') or '0').replace('.','',1).isdigit() and float(r['DR'])>=30]
hi.sort(key=lambda x:-float(x[1]))
for d,dr,l in hi[:20]: print(f"  {d:45} DR {dr:>5}  {l} links")
print(f"  ...total high-DR spam domains: {len(hi)}")

print("\n=== LOST links (Ahrefs 'Lost' column on refdomains) ===")
lost=[r for r in rd if (r.get('Lost') or '').strip()]
print(f"referring domains with a Lost date: {len(lost)}")
clean=[r for r in lost if r.get('Is spam')!='true']
clean.sort(key=lambda r: -float(r.get('DR') or 0))
print("  highest-DR NON-SPAM lost domains (real losses worth reclaiming):")
for r in clean[:12]: print(f"    {r['Domain']:40} DR {r.get('DR'):>5}  lost {r.get('Lost')}")

print("\n=== Top NON-SPAM referring domains by DR (the real profile) ===")
good=[r for r in rd if r.get('Is spam')!='true' and (r.get('DR') or '0').replace('.','',1).isdigit()]
good.sort(key=lambda r:-float(r['DR']))
for r in good[:15]: print(f"  {r['Domain']:40} DR {r['DR']:>5}  {r.get('Links to target')} links  traffic {r.get('Traffic ')}")
