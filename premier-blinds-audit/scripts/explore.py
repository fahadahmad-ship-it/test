import sys, os
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import load
bl,dropped,rec = load.read_backlinks(sorted(__import__('glob').glob('data/fetch/bl_*.csv')))
rd,rddrop = load.read_refdomains(sorted(__import__('glob').glob('data/rd/rd_*.csv')))
print("backlinks parsed=%d dropped=%d recovered=%d | refdomains parsed=%d dropped=%d"%(len(bl),dropped,rec,len(rd),rddrop))

# target path distribution (home vs deep)
def path(u):
    h=load.host_of(u); 
    rest=u.lower().split(h,1)[-1] if h else u
    rest=rest.split('?')[0]
    return rest if rest else '/'
tp=Counter(path(r['target_url']) for r in bl)
print("\n=== target paths top 25 (home vs deep) ===")
for k,v in tp.most_common(25): print("  %5d  %s"%(v,k[:70]))

# redirect_url hosts (owned/redirect domains)
rh=Counter(load.host_of(r['redirect_url']) for r in bl if r['redirect_url'].strip())
print("\n=== redirect_url hosts (owned/redirect candidates) ===")
for k,v in rh.most_common(20): print("  %5d  %s"%(v,k))

# nofollow distribution
nf=Counter(r['nofollow'] for r in bl); print("\nnofollow values:",dict(nf))

# anchor top 40
an=Counter(r['anchor'].strip() for r in bl)
print("\n=== top 40 anchors ===")
for k,v in an.most_common(40): print("  %5d  %s"%(v,k[:90]))

# referring host tld
tld=Counter(load.host_of(r['domain']).rsplit('.',1)[-1] for r in rd)
print("\n=== refdomain TLDs top 20 ===")
for k,v in tld.most_common(20): print("  %5d  .%s"%(v,k))
