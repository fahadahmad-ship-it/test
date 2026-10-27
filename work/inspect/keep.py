import sys, os
from collections import Counter, defaultdict
from urllib.parse import urlsplit
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
V={}
for d,links in by.items():
    rm=refmeta.get(d,refmeta.get(reg(d),{}))
    st,ty,ev,_=C.classify_domain(d,links,rm); V[d]=(st,ev,links,rm)
keep=sorted([d for d in V if V[d][0]=="Keep"])
print(f"KEEP={len(keep)}")
ev_c=Counter(V[d][1].split("(")[0].split(":")[0].strip() for d in keep)
print("Keep evidence:",dict(ev_c))
# group by evidence kind
fallthrough=[d for d in keep if V[d][1].startswith("Genuine")]
titlecite=[d for d in keep if V[d][1].startswith("Linking-page")]
asbased=[d for d in keep if V[d][1].startswith("Authority")]
print(f"\nfall-through(Genuine or harmless)={len(fallthrough)}  title-cite={len(titlecite)}  AS>=20={len(asbased)}")
print("\n==== FALL-THROUGH 'Genuine or harmless' (SUSPECT) ====")
for d in fallthrough:
    L0=V[d][2]; rm=V[d][3]
    anchs=Counter([l['anchor'][:34] for l in L0])
    tgt=Counter([urlsplit(l['target_url']).path.strip('/') or '(home)' for l in L0])
    titles=set(l['source_title'][:40] for l in L0)
    dof=sum(1 for l in L0 if not l['is_nofollow'])
    print(f"{d} AS={rm.get('domain_authority_score_i','?')} n={len(L0)} dof={dof} tld=.{d.split('.')[-1]} tgt={list(tgt)[:2]} anch={list(anchs)[:2]} title={list(titles)[:1]}")
