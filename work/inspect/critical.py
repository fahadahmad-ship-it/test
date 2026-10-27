import sys,os
from collections import defaultdict
from urllib.parse import urlsplit
sys.path.insert(0,"work/parkers/scripts")
import load as L, classify as C
bl,_=L.load_backlinks("work/parkers/data/fetch"); rd,_=L.load_refdomains("work/parkers/data/rd")
rm={r["domain"]:r for r in rd}
by=defaultdict(list)
for b in bl:
    if b["refdomain"]: by[b["refdomain"]].append(b)
def reg(h):
    p=h.split(".");return h if len(p)<=2 else ".".join(p[-2:])
def deep(u):
    try:p=urlsplit(u if "://" in u else "http://"+u).path
    except:return False
    return len(p.strip("/"))>0 and p.strip("/").lower() not in ("index.html","index.php","home")
V={}
for d,links in by.items():
    st,_,ev,_=C.classify_domain(d,links,rm.get(d,rm.get(reg(d),{})))
    V[d]=(st,links,ev)
# A) Any HELD domain carrying a PBN/off-topic anchor (flood leaking into held)?
a=[d for d,(st,links,ev) in V.items() if st.startswith("Held") and any(C.anchor_type(l["anchor"]) in ("Spam: keyword stuffed SEO sales copy","Spam: off topic") for l in links)]
print("A) HELD domains with a PBN/offtopic anchor (want 0):",len(a),a[:8])
# B) Any DISAVOW domain carrying an exact-match anchor OR a deep-page link (commissioned-looking leaking into disavow)?
b=[]
for d,(st,links,ev) in V.items():
    if st=="Spam (Disavow)":
        if any(C.anchor_type(l["anchor"]) in ("Exact match commercial","Exact match commercial (geo)") for l in links) or any(deep(l["target_url"]) for l in links):
            b.append(d)
print("B) DISAVOW domains with an exact-match anchor or deep-page link (want ~0):",len(b),b[:8])
# C) Every disavow domain has dofollow + evidence; every held is nofollow-or-dofollow but never in file
dis=[d for d,(st,_,_) in V.items() if st=="Spam (Disavow)"]
noev=[d for d in dis if not any(k in V[d][2] for k in ("PBN","Off-topic","Spam host","Spam page"))]
print("C) disavow w/o evidence (want 0):",len(noev))
# D) KEEP/HELD domains that are 100% home-page naked-URL dofollow with 0 traffic AND spammy TLD (possible missed spam)
import glob
metr={}
for f in glob.glob("work/parkers/data/metrics/parts/part_*.csv"):
    for ln in open(f).read().splitlines():
        p=ln.split(";")
        if len(p)==3: metr[p[0]]=(p[1],p[2])
susp=[]
for d,(st,links,ev) in V.items():
    if st=="Keep" and ev.startswith("Genuine"):
        tl=metr.get(d,("",""))
        traf=tl[1] if tl[1].isdigit() else "0"
        tld=d.split(".")[-1]
        if traf=="0" and tld in ("top","icu","cloud","xyz","online","site","club","world","party","fyi","website","wiki","cc","shop","dev","pages.dev"):
            susp.append((d,tld))
print("D) KEEP fall-through on spammy TLD w/ 0 traffic (manual look):",len(susp),susp[:12])
