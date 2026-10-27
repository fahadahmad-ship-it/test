import sys, os
from collections import Counter, defaultdict
sys.path.insert(0,"work/parkers/scripts")
import load as L, classify as C
bl,_ = L.load_backlinks("work/parkers/data/fetch")
tc=Counter(); samples=defaultdict(list)
for b in bl:
    a=b["anchor"] if b["anchor"].strip() else "<EmptyAnchor>"
    t=C.anchor_type(a)
    tc[t]+=1
    if len(samples[t])<8 and a not in [s for s in samples[t]]:
        samples[t].append(a[:70])
print("ANCHOR TYPE COUNTS (of %d links):"%len(bl))
for t,n in tc.most_common():
    print(f"  {n:5d}  {t}")
print("\n--- samples of ambiguous buckets ---")
for t in ["Contextual or other","Generic","Branded","Empty or image","Exact match commercial","Exact match commercial (geo)"]:
    print(f"\n[{t}] ({tc.get(t,0)})")
    for s in samples[t]: print("   ",repr(s))
