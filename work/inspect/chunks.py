import sys,os
from collections import defaultdict
sys.path.insert(0,"work/parkers/scripts")
import load as L, classify as C
bl,_=L.load_backlinks("work/parkers/data/fetch")
by=defaultdict(list)
for b in bl:
    if b["refdomain"]: by[b["refdomain"]].append(b)
doms=sorted(by.keys())
os.makedirs("work/parkers/data/metrics/chunks",exist_ok=True)
N=16
chunks=[[] for _ in range(N)]
for i,d in enumerate(doms): chunks[i%N].append(d)
for i,c in enumerate(chunks):
    open(f"work/parkers/data/metrics/chunks/chunk_{i:02d}.txt","w").write("\n".join(c))
print(f"total domains={len(doms)} split into {N} chunks of ~{len(doms)//N}")
