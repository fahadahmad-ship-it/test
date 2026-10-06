import csv, sys
from collections import Counter, defaultdict
from urllib.parse import urlparse
bl=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig',newline=''),delimiter='\t'))

def host(u):
    try: return urlparse(u.strip()).netloc.lower()
    except: return ''

print("=== EVERY DISTINCT REDIRECT CHAIN (full, not just hosts) ===")
chains=Counter()
for r in bl:
    c=(r.get('Redirect Chain URLs') or '').strip()
    codes=(r.get('Redirect Chain status codes') or '').strip()
    if c: chains[(c,codes,r.get('Target URL'))]+=1
for (c,codes,t),n in chains.most_common(25):
    print(f"[{n:>4}] {c}  --({codes})-->  {t}")

print(f"\ndistinct chains: {len(chains)}")
print("\n=== chains NOT involving ngwindows.com at all (third-party redirects) ===")
for (c,codes,t),n in chains.most_common():
    if 'ngwindows' not in c.lower():
        print(f"[{n:>4}] {c}  --({codes})-->  {t}")

print("\n=== all distinct Target URLs (where links actually land) ===")
tu=Counter(r.get('Target URL','') for r in bl)
for u,n in tu.most_common(15): print(f"  {n:>5}  {u}")
print(f"  distinct target URLs: {len(tu)}")
