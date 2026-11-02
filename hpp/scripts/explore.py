import sys, re, glob, os
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import parse_backlinks, canon_host

base = "/home/user/test/hpp"
bl, rej = parse_backlinks(glob.glob(os.path.join(base, "data/fetch/bl_*.csv")))
print(f"rows={len(bl)} rejected={rej}")

# dedupe on (source_url,target_url,anchor)
seen=set(); links=[]
for r in bl:
    k=(r["source_url"].rstrip("/").lower(), r["target_url"].rstrip("/").lower(), r["anchor"])
    if k in seen: continue
    seen.add(k); links.append(r)
print("unique links", len(links))

# ---- target page split: home vs deep ----
def target_prop(r):
    u = r["redirect_url"] or r["target_url"]
    return u
home=0; deep=0
deeppaths=Counter()
for r in links:
    u=(r["target_url"] or "").lower()
    path=u.split("highpriorityplumbing.com",1)[-1] if "highpriorityplumbing.com" in u else u.split("/",3)[-1] if u.count("/")>=3 else ""
    path=path.strip("/")
    # strip scheme-host generally
    m=re.sub(r'^https?://[^/]+','',u)
    m=m.strip('/')
    if m=="" or m in ("index.html","home"):
        home+=1
    else:
        deep+=1
        deeppaths[m.split("?")[0]]+=1
print(f"\nTARGET: home-page links={home}  deep-page links={deep}")
print("top deep paths:")
for p,c in deeppaths.most_common(25):
    print(f"  {c:5d}  {p[:80]}")

# ---- dofollow split ----
df=sum(1 for r in links if not r["nofollow"]); nf=sum(1 for r in links if r["nofollow"])
print(f"\nDOFOLLOW links={df}  NOFOLLOW links={nf}")

# ---- anchor frequency ----
anch=Counter(r["anchor"] for r in links)
print(f"\ndistinct anchors: {len(anch)}")
print("TOP 40 anchors (count | #domains):")
anch_dom=defaultdict(set)
for r in links:
    anch_dom[r["anchor"]].add(canon_host(r["source_url"]))
for a,c in anch.most_common(40):
    print(f"  {c:5d} | {len(anch_dom[a]):4d}d | {a[:90]!r}")
