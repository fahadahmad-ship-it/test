"""verify.py — exhaustive, both-directions correctness check for the parkersair audit."""
import sys, os
from collections import Counter, defaultdict
from urllib.parse import urlsplit
sys.path.insert(0, "/home/user/test/work/parkers/scripts")
import load as L, classify as C

BASE="/home/user/test/work/parkers"
bl,_=L.load_backlinks(os.path.join(BASE,"data","fetch"))
rd,_=L.load_refdomains(os.path.join(BASE,"data","rd"))
refmeta={r["domain"]:r for r in rd}
redir=sorted({b["redirect_host"] for b in bl if b["redirect_host"]})
for h in redir: C.OWNED_DOMAINS.add(h)

def reg(host):
    p=host.split(".")
    if len(p)<=2: return host
    tp={"co.uk","com.au","co.in","co.nz","co.za","com.br","co.jp"}
    if ".".join(p[-2:]) in tp: return ".".join(p[-3:])
    return ".".join(p[-2:])

by=defaultdict(list)
for b in bl:
    if b["refdomain"]: by[b["refdomain"]].append(b)

V={}
for d,links in by.items():
    rm=refmeta.get(d, refmeta.get(reg(d),{}))
    st,types,ev,_=C.classify_domain(d,links,rm)
    V[d]={"status":st,"ev":ev,"links":links,"types":types}

def deep(u):
    try:p=urlsplit(u if "://" in u else "http://"+u).path
    except:return False
    return len(p.strip("/"))>0 and p.strip("/").lower() not in ("index.html","index.php","home")

print("="*60,"\nSTATUS COUNTS")
print(Counter(v["status"] for v in V.values()))

# held reason breakdown
hr=Counter(v["ev"].split(":")[0].split("(")[0].strip() for d,v in V.items() if v["status"].startswith("Held"))
print("\nHELD reasons:",dict(hr))
sr=Counter(v["ev"].split(":")[0].strip() for d,v in V.items() if v["status"].startswith("Spam"))
print("SPAM reasons:",dict(sr))

# ---- FALSE NEGATIVES: Keep/Held with a dofollow PBN/offtopic anchor ----
fn=[]
for d,v in V.items():
    if v["status"] in ("Keep",):
        for l in v["links"]:
            at=C.anchor_type(l["anchor"])
            if at in ("Spam: keyword stuffed SEO sales copy","Spam: off topic") and not l["is_nofollow"]:
                fn.append((d,v["status"],at,l["anchor"][:60])); break
print(f"\n[FALSE NEG] Keep domains with dofollow spam anchor: {len(fn)}")
for x in fn[:15]: print("   ",x)

# nofollow-marked spam that actually has a dofollow link
fn2=[]
for d,v in V.items():
    if v["status"]=="Spam (Nofollow, No Action)":
        if any(not l["is_nofollow"] for l in v["links"]): fn2.append(d)
print(f"[FALSE NEG] nofollow-spam with a dofollow link: {len(fn2)} {fn2[:10]}")

# ---- FALSE POSITIVES: disavow with no visible evidence ----
spam_dis=[d for d,v in V.items() if v["status"]=="Spam (Disavow)"]
noev=[]
clean_cite=[]
for d in spam_dis:
    v=V[d]; ev=v["ev"]
    has_evidence = any(k in ev for k in ("PBN","Off-topic","Spam host","Spam page"))
    if not has_evidence: noev.append((d,ev))
    # title names client without sales copy on ALL links => potential genuine citation
    names=any("parker" in l["source_title"].lower() for l in v["links"])
    pbn=any(C.anchor_type(l["anchor"])=="Spam: keyword stuffed SEO sales copy" for l in v["links"])
    if names and not pbn: clean_cite.append((d,ev))
print(f"\n[FALSE POS] disavow with NO visible evidence: {len(noev)}")
for x in noev[:15]: print("   ",x)
print(f"[FALSE POS] disavow whose title names client w/o sales copy: {len(clean_cite)}")
for x in clean_cite[:15]: print("   ",x)

# ---- every disavow domain has >=1 dofollow link ----
nod=[d for d in spam_dis if not any(not l["is_nofollow"] for l in V[d]["links"])]
print(f"\n[INTEGRITY] disavow domains with no dofollow link: {len(nod)} {nod[:10]}")

# ---- two-campaign split: where do links point? ----
def homeonly(links):
    return all(not deep(l["target_url"]) for l in links)
spam_home=sum(1 for d in spam_dis if homeonly(V[d]["links"]))
held=[d for d,v in V.items() if v["status"].startswith("Held")]
held_deep=sum(1 for d in held if any(deep(l["target_url"]) for l in V[d]["links"]))
print(f"\n[SPLIT] spam-disavow domains pointing ONLY at home page: {spam_home}/{len(spam_dis)}")
print(f"[SPLIT] held domains with >=1 deep-page link: {held_deep}/{len(held)}")

# target page distribution for spam vs held
def paths(dset):
    c=Counter()
    for d in dset:
        for l in V[d]["links"]:
            p=urlsplit(l["target_url"]).path.strip("/") or "(home)"
            c[p]+=1
    return c
print("\nSPAM target pages top:", paths(spam_dis).most_common(6))
print("HELD target pages top:", paths(held).most_common(10))

# ---- redundant children ----
sset=set(spam_dis)
redun=[d for d in sset if reg(d)!=d and reg(d) in sset]
print(f"\n[REDUNDANT] children whose registrable parent is also disavowed: {len(redun)} {redun[:10]}")

# ---- sample held domains ----
print("\nSAMPLE held domains:")
for d in sorted(held)[:12]:
    ex=V[d]["links"][0]
    print(f"   {d}  ev={V[d]['ev'][:40]}  anchor={ex['anchor'][:40]!r} -> {urlsplit(ex['target_url']).path[:30]}")
print("\nSAMPLE keep domains:")
for d in sorted([d for d,v in V.items() if v['status']=='Keep'])[:15]:
    ex=V[d]["links"][0]
    print(f"   {d}  AS={refmeta.get(d,{}).get('domain_authority_score_i','?')} ev={V[d]['ev'][:34]} anchor={ex['anchor'][:30]!r}")
