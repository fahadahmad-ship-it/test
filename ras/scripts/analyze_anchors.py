import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import load_semrush_backlinks, host
from collections import Counter
from urllib.parse import urlsplit

rows,_,_ = load_semrush_backlinks(sys.argv[1])

# anchor frequency (by backlinks)
ac = Counter(r['anchor'] for r in rows)
print("distinct anchors:", len(ac))
print("\n=== TOP 40 anchors by backlink count ===")
for a,c in ac.most_common(40):
    print(f"  [{c}] {a[:110]!r}")

# deep page targets (non-home). property = redirect_url host if present else target_url host
def prop(r):
    ru = r['redirect_url'].strip()
    return host(ru) if ru else host(r['target_url'])
def path_of(r):
    ru = r['redirect_url'].strip()
    u = ru if ru else r['target_url']
    try: return urlsplit(u if '://' in u else 'http://'+u).path
    except: return ''
# Actually the deep-page signal should use target_url path (what google ranks). redirect_url is the owned domain root.
def tpath(r):
    u=r['target_url']
    try: return urlsplit(u if '://' in u else 'http://'+u).path or '/'
    except: return '/'
home = sum(1 for r in rows if tpath(r) in ('/',''))
print(f"\ntarget homepage links: {home}/{len(rows)} ({home/len(rows)*100:.1f}%)")
print("\n=== top deep target paths (non-home) ===")
dp = Counter(tpath(r) for r in rows if tpath(r) not in ('/',''))
for p,c in dp.most_common(30):
    print(f"  [{c}] {p[:80]}")

# property distribution
print("\n=== property (attribution) distribution ===")
print(Counter(prop(r) for r in rows).most_common())
