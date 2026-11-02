import sys, re, glob, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import parse_backlinks, canon_host

base = "/home/user/test/hpp"
bl, rej = parse_backlinks(glob.glob(os.path.join(base, "data/fetch/bl_*.csv")))
seen=set(); links=[]
for r in bl:
    k=(r["source_url"].rstrip("/").lower(), r["target_url"].rstrip("/").lower(), r["anchor"])
    if k in seen: continue
    seen.add(k); links.append(r)

# vendor self-promo: advertises linker's OWN link/seo service, NOT naming the client domain,
# NOT a telegram channel invite. Typically 1st person / imperative / contact handle.
def is_client_named(a): return 'highpriorityplumbing' in a.lower()
chan_re = re.compile(r'(t\.me/|telegram)', re.I)
vendor_re = re.compile(r'(i will |whats\s?app|dm (me|us)|contact (me|us) (on|at|via)|order (now|your)|\+\d[\d\s()\-]{6,}|increase your (domain authority|da/?dr|da |dr )|boost your (da|dr|domain)|rank your (site|website)|cheap .*back ?links|buy .*back ?links|guest post service|link building service)', re.I)

doms=defaultdict(list)
for r in links:
    a=r["anchor"]
    if is_client_named(a): continue
    if chan_re.search(a): continue
    if vendor_re.search(a):
        doms[canon_host(r["source_url"])].append(r)

print(f"VENDOR SELF-PROMO (not client-named, not telegram) domains = {len(doms)}")
anchors=defaultdict(set)
for d,rs in doms.items():
    for r in rs: anchors[r["anchor"]].add(d)
for a in sorted(anchors, key=lambda x:-len(anchors[x])):
    dl='dofollow' if any(not r['nofollow'] for d in doms for r in doms[d] if r['anchor']==a) else 'nofollow'
    print(f"   {len(anchors[a]):3d}d {dl:9s} {a[:95]!r}")
print("\nDomains:")
for d in sorted(doms):
    df=any(not r['nofollow'] for r in doms[d])
    print(f"   {d:36s} n={len(doms[d]):2d} dofollow={df}")
