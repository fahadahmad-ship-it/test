import csv, sys
from collections import Counter
from urllib.parse import urlparse
rd=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig',newline=''),delimiter='\t'))
bl=list(csv.DictReader(open(sys.argv[2],encoding='utf-8-sig',newline=''),delimiter='\t'))
sem={l.split(';')[0].lower() for l in open(sys.argv[3],encoding='utf-8',errors='replace').read().splitlines()[1:] if l.strip()}

ah={ (r.get('Domain') or '').lower().strip() for r in rd if r.get('Domain')}
print(f"Ahrefs referring domains: {len(ah)}")
print(f"Semrush referring domains: {len(sem)}")
print(f"overlap: {len(ah&sem)}   Ahrefs-only: {len(ah-sem)}   Semrush-only: {len(sem-ah)}")

# Network A = the /dir/ PBN template domains Semrush found
netA={d for d in sem if any(k in d for k in ('dachecker','pachecker','backlink','seocheck','rankcheck','checkerseo','linkaudit','trustflow','seostrength','domainmetrics','bulkpa','dapa'))}
print(f"\nNetwork A-style domains in Semrush: {len(netA)}")
print(f"  ...also seen by Ahrefs: {len(netA&ah)}")
print(f"  examples NOT in Ahrefs: {sorted(netA-ah)[:8]}")

print("\n=== Is the Ahrefs export capped? ===")
tot=sum(int(r['Links to target']) for r in rd if (r.get('Links to target') or '').isdigit())
print(f"sum of 'Links to target' across Ahrefs refdomains: {tot}")
print(f"backlink rows actually in export: {len(bl)}")
lost=Counter((r.get('Lost status') or 'live') for r in bl)
print(f"Lost status breakdown: {dict(lost)}")
spam=Counter((r.get('Is spam') or '') for r in bl)
print(f"Is spam breakdown: {dict(spam)}")
nf=Counter((r.get('Nofollow') or '') for r in bl)
print(f"Nofollow breakdown: {dict(nf)}")

print("\n=== Ahrefs 'Is spam' flag on referring domains ===")
rs=Counter((r.get('Is spam') or '') for r in rd)
print(dict(rs))
