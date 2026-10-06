import csv, sys, re
from collections import Counter, defaultdict
from urllib.parse import urlparse

SHELLS = ['ngawindows.com','roiwindows.com','thermalprowindows.com','qualitypluswindows.com',
'northpointwindows.com','performingwindows.com','thermatrustwindows.com','northgeorgiawindows.net',
'thermalastwindows.com','e2windows.com','choiceviewwindows.com','ngwindow.com','northgawindows.com',
'northgeorgiawindow.com']

rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig',newline=''),delimiter='\t'))
print("total backlink rows in Ahrefs export:", len(rows))

def host(u):
    try: return urlparse(u).netloc.lower().replace('www.','')
    except: return ''

# Which anchors name a shell?
shell_anchor = 0
shell_anchor_target_is_client = 0
shell_in_chain = 0
chain_hosts = Counter()
target_hosts = Counter()
examples=[]

for r in rows:
    a=(r.get('Anchor') or '')
    t=r.get('Target URL') or ''
    chain=r.get('Redirect Chain URLs') or ''
    target_hosts[host(t)] += 1
    named = [s for s in SHELLS if s in a.lower()]
    if named:
        shell_anchor += 1
        if 'ngwindows.com' in host(t): shell_anchor_target_is_client += 1
        if any(s in chain.lower() for s in SHELLS):
            shell_in_chain += 1
            if len(examples)<3: examples.append((a[:60], t, chain))
    for h in [host(x) for x in chain.split(',') if x.strip()]:
        if h: chain_hosts[h]+=1

print("\n=== THE DECISIVE TEST ===")
print(f"rows whose ANCHOR names a shell domain: {shell_anchor}")
print(f"  ...of those, Target URL is ngwindows.com: {shell_anchor_target_is_client}")
print(f"  ...of those, a shell appears in the REDIRECT CHAIN: {shell_in_chain}")
print("\nTarget URL hosts (top 10):")
for h,c in target_hosts.most_common(10): print(f"  {h:40} {c}")
print("\nRedirect-chain hosts (top 10):")
for h,c in chain_hosts.most_common(10): print(f"  {h:40} {c}")
if examples:
    print("\nexamples of shell-in-chain:")
    for e in examples: print(" ", e)
