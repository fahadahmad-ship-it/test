import sys,os
from collections import defaultdict
sys.path.insert(0,"work/parkers/scripts")
import load as L, classify as C
bl,_=L.load_backlinks("work/parkers/data/fetch")
rd,_=L.load_refdomains("work/parkers/data/rd")
refmeta={r["domain"]:r for r in rd}
by=defaultdict(list)
for b in bl:
    if b["refdomain"]: by[b["refdomain"]].append(b)
def reg(h):
    p=h.split(".");return h if len(p)<=2 else ".".join(p[-2:])
held=[];keep=[];spam=[]
for d,links in by.items():
    rm=refmeta.get(d,refmeta.get(reg(d),{}))
    st,_,_,_=C.classify_domain(d,links,rm)
    if st.startswith("Held"): held.append(d)
    elif st=="Keep": keep.append(d)
    elif st=="Spam (Disavow)": spam.append(d)
os.makedirs("work/parkers/data/metrics",exist_ok=True)
open("work/parkers/data/metrics/_held.txt","w").write("\n".join(sorted(held)))
open("work/parkers/data/metrics/_keep.txt","w").write("\n".join(sorted(keep)))
open("work/parkers/data/metrics/_spam.txt","w").write("\n".join(sorted(spam)))
# a 50-domain spam sample for zero-validation
import random; random.seed(1)
samp=sorted(random.sample(spam,50))
open("work/parkers/data/metrics/_spam_sample.txt","w").write("\n".join(samp))
print(f"held={len(held)} keep={len(keep)} spam={len(spam)} sample=50")
