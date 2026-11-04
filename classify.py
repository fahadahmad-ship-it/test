import csv, re, json, html
from collections import defaultdict, Counter
DATA="/home/user/test/data"; CLIENT="blackwalnutconstruction.com"
def host(u):
    s=html.unescape(str(u or "")).strip().lower(); s=re.sub(r'^https?://','',s).split('/')[0]; return re.sub(r'^www\.','',s)
def path_of(u):
    s=html.unescape(str(u or "")).strip(); s=re.sub(r'^https?://[^/]+','',s); return s.strip('/').lower()

# ---- refdomains (root universe) ----
rd={}
for fn in ["rd_p1.csv","rd_p2.csv"]:
    r=csv.reader(open(f"{DATA}/{fn}",encoding="utf-8"),delimiter=';'); next(r)
    for row in r:
        if len(row)<9: continue
        d=host(row[0]); 
        try: asc=int(row[2] or 0)
        except: asc=0
        try: bl=int(row[1] or 0)
        except: bl=0
        rec=dict(as_=asc,bl=bl,ip=row[5],country=row[6],first_seen=row[7],last_seen=row[8])
        if d not in rd or bl>rd[d]["bl"]: rd[d]=rec
roots=sorted(rd.keys(), key=len, reverse=True)
def to_root(h):
    for k in roots:
        if h==k or h.endswith("."+k): return k
    return h  # not in refdomains

# ---- backlinks ----
def parse_line(line):
    parts=line.split(';')
    if len(parts)<8: return None
    ni=None
    for i in range(len(parts)-1,-1,-1):
        if parts[i] in ('true','false'): ni=i;break
    if ni is None or ni<3: return None
    anchor=parts[ni-1]; source_url=parts[0]; left=parts[1:ni-1]
    ti=None
    for j in range(len(left)-1,-1,-1):
        if 'blackwalnutconstruction' in left[j]: ti=j;break
    target=left[ti] if ti is not None else (left[-1] if left else "")
    title=";".join(left[:ti]) if ti is not None else (";".join(left[:-1]) if len(left)>1 else "")
    return dict(src=source_url,title=html.unescape(title),target=target,anchor=html.unescape(anchor),
                nofollow=parts[ni]=='true',first_seen=parts[ni+1] if ni+1<len(parts) else "")
links=[]
for fn in ["bl_p1.csv","bl_p2.csv","bl_p3.csv"]:
    for line in open(f"{DATA}/{fn}",encoding="utf-8").read().splitlines()[1:]:
        if line.strip():
            p=parse_line(line)
            if p: links.append(p)

dom=defaultdict(lambda: dict(anchors=[],targets=[],titles=[],nf=[],ex=[]))
for L in links:
    d=to_root(host(L["src"]))
    if not d: continue
    D=dom[d]; D["anchors"].append(L["anchor"]); D["targets"].append(L["target"])
    D["titles"].append(L["title"]); D["nf"].append(L["nofollow"])
    D["ex"].append((L["src"],L["anchor"],L["title"],L["nofollow"],L["target"]))
for d in rd: _=dom[d]

GEO=re.compile(r'lexington|,?\s*sc\b|south carolina',re.I)
CONSTR=re.compile(r'construction|builder|contractor|home build|custom home|office|retail|residential|commercial|renovat|new house|homes build|house builder',re.I)
SALES=re.compile(r'premium authority backlink|buy backlink|backlinks online cheap|pbn|da 50|pa 40|guest post|white hat seo link|raise domain rating|dofollow backlink|premium backlink|rank first page|seo link building|outrank|guest posting|premium seo|authority backlink|visit site seo|links for blackwalnut|outshine competitors',re.I)
OFF=re.compile(r'casino|escort|porn|viagra|pharma|gambling|betting|slot|bonanza|\btoto|tokyopush|malatya|\bufa\b|sbobet',re.I)
GENERIC=re.compile(r'^(visit website|visit site|read more|click here|website|visit website\s*[→↗])\s*$',re.I)
SPAMHOST=re.compile(r'backlink|dapa|pacheck|rankcheck|checker|\bseo|directory|listing|bookmark|domainlist|aged.?domain|\bpbn|linkbuild|trafficsource|serp|keyword|getwebsiteworth|webworth|linksnatcher|ranktool|ranktracker|traffic|whitehat|dofollow|domraider|all-aged|yesdomains')
SPAMTITLE=re.compile(r'aged domains and backlinks|seo domain research|domain report|website stats|url shared|buy .*backlink|/domain/domain/part/|page-[0-9a-f]{8}|where to buy',re.I)
NAKED=re.compile(r'^(https?://)?(www\.)?blackwalnutconstruction\.com',re.I)
BRAND=re.compile(r'black walnut construction',re.I)
DEEP=re.compile(r'(commercial|office|residential|retail)-construction-services|/office-construction',re.I)
def atype(a):
    al=(a or "").strip().lower()
    if al=="": return "Empty or image"
    if OFF.search(al): return "Spam: off topic"
    if SALES.search(al): return "Spam: keyword stuffed SEO sales copy"
    if CONSTR.search(al) and GEO.search(al): return "Exact match commercial (geo)"
    if CONSTR.search(al) and not NAKED.match(al): return "Exact match commercial"
    if BRAND.search(al): return "Branded"
    if NAKED.match(al): return "Naked URL"
    if GENERIC.match(al): return "Generic"
    if 'png' in al or 'banner' in al: return "Empty or image"
    return "Contextual or other"

status={}; meta={}
for d,D in dom.items():
    asc=rd.get(d,{}).get("as_",0)
    types=[atype(a) for a in D["anchors"]]
    has_exact=any(t.startswith("Exact match commercial") for t in types)
    deep=any(DEEP.search(t or "") for t in D["targets"])
    has_off=any(t=="Spam: off topic" for t in types) or OFF.search(d)
    has_sales=any(t=="Spam: keyword stuffed SEO sales copy" for t in types)
    nf=D["nf"]; any_do=any(not x for x in nf) if nf else True
    titles=" ".join(D["titles"]).lower()
    if d==CLIENT: st="Own Site"
    elif asc>=20: st="Keep"
    elif has_exact or deep: st="Held"
    elif has_off: st="Spam"
    elif has_sales: st="Spam"
    elif SPAMHOST.search(d): st="Spam"
    elif SPAMTITLE.search(titles): st="Spam"
    else: st="Keep"
    if st=="Spam": st="Spam (Disavow)" if any_do else "Spam (Nofollow, No Action)"
    elif st=="Held": st="Held (Pending Partner)" if any_do else "Held (Nofollow, No Action)"
    status[d]=st
    top=Counter(D["anchors"]).most_common(1)[0][0] if D["anchors"] else ""
    ex=None
    for (su,an,ti,nfl,tu) in D["ex"]:
        if st.startswith("Held") and (atype(an).startswith("Exact match") or DEEP.search(tu or "")) and not nfl: ex=(su,an,ti,tu);break
    if not ex:
        for (su,an,ti,nfl,tu) in D["ex"]:
            if not nfl: ex=(su,an,ti,tu);break
    if not ex and D["ex"]: su,an,ti,nfl,tu=D["ex"][0]; ex=(su,an,ti,tu)
    pts=Counter(host(t) for t in D["targets"] if t).most_common(1)
    meta[d]=dict(status=st,as_=asc,top=top,bl=rd.get(d,{}).get("bl",len(D["anchors"]) or 1),
        ex_url=ex[0] if ex else "",ex_anchor=ex[1] if ex else "",ex_title=ex[2] if ex else "",ex_target=ex[3] if ex else "",
        points=pts[0][0] if pts else CLIENT, dofollow=sum(1 for x in nf if not x), nofollow=sum(1 for x in nf if x),
        first_seen=rd.get(d,{}).get("first_seen",""), ip=rd.get(d,{}).get("ip",""),
        deep=bool(deep), market="Lexington SC" if (has_exact and any(GEO.search(a or '') for a in D["anchors"])) or deep else "Non-geo")
json.dump({"status":status,"meta":meta},open(f"{DATA}/domains.json","w"))
c=Counter(status.values())
print("referring domains:",len(status)," (Semrush refdomains:",len(rd),")")
for k,v in c.most_common(): print(f"   {k}: {v}")
print("\nKeep bucket (review for false negatives):")
for d in [d for d,s in status.items() if s=='Keep']: print(f"   {d}  AS={rd.get(d,{}).get('as_',0)} top={meta[d]['top'][:45]!r}")
