import sys, os, glob, json
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(__file__))
import load, classify

bl,dr,rec = load.read_backlinks(sorted(glob.glob('data/fetch/bl_*.csv')))
rd,rdd = load.read_refdomains(sorted(glob.glob('data/rd/rd_*.csv')))
def num(x):
    try: return float(x)
    except: return None
rdmap = {r['domain'].strip().lower(): r for r in rd}
match = load.build_refdomain_matcher(rdmap.keys())

groups = defaultdict(list)
for l in bl:
    groups[match(l['source_url'])].append(l)

all_domains = set(groups) | set(rdmap)
print("link-groups=%d refdomains=%d union=%d"%(len(groups),len(rdmap),len(all_domains)))
print("refdomains w/o links:", len([d for d in rdmap if d not in groups]))
print("groups w/o refdomain row:", len([d for d in groups if d not in rdmap]), [d for d in groups if d not in rdmap][:8])

results={}
for d in all_domains:
    links=groups.get(d,[])
    if not links: continue
    r=rdmap.get(d); asc=num(r['domain_ascore']) if r else None
    status,reason=classify.classify_domain(d,links,asc)
    results[d]=(status,reason,asc,links)

dist=Counter(v[0] for v in results.values())
print("\n=== DISTRIBUTION (domains=%d) ==="%len(results))
for k,v in dist.most_common(): print("  %-30s %d"%(k,v))

# AUDIT the Keep "no spam evidence" + benign-cite buckets: show titles/anchors to catch false negatives
print("\n=== AUDIT: Keep domains — check for hidden spam evidence ===")
keeps=[(d,v) for d,v in results.items() if v[0]=='Keep']
for d,v in keeps:
    l0=v[3][0]
    df=any(l['nofollow'].strip().lower()=='false' for l in v[3])
    print("  %-30s AS=%-5s dofollow=%s | reason=%s" % (d[:30], v[2], df, v[1]))
    print("        anchor=%s" % (l0['anchor'] or '')[:70])
    print("        title =%s" % (l0['source_title'] or '')[:70])

# ---- FALSE-NEGATIVE PROBE: Keep/Held carrying a dofollow spam-typed anchor or spam title
print("\n=== FALSE-NEGATIVE PROBE (should be empty / only documented genuine) ===")
viol=0
for d,v in results.items():
    st=v[0]
    if st in ("Spam (Disavow)","Spam (Nofollow, No Action)","Own Site"): continue
    for l in v[3]:
        df = l['nofollow'].strip().lower()=='false'
        at = classify.anchor_type(l['anchor'])
        ts = classify._any(classify.SPAM_TITLE,(l['source_title'] or '').lower())
        if df and (at in classify.SPAM_ANCHOR_TYPES or ts):
            print("  VIOL %-26s [%s] dofollow spam: type=%s title=%s"%(d[:26],st,at,(l['source_title'] or '')[:40]))
            viol+=1; break
print("violations:", viol)

# full Keep list quick
print("\n=== Keep (%d) all, 1-line ===" % sum(1 for v in results.values() if v[0]=='Keep'))
for d,v in sorted(results.items()):
    if v[0]=='Keep':
        print("  %-28s AS=%-6s %s | %s"%(d[:28],v[2],v[1][:30],(v[3][0]['source_title'] or '')[:40]))
