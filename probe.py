import csv, re, html
from collections import Counter, defaultdict
DATA="/home/user/test/data"
def host(u):
    s=html.unescape(str(u or "")).strip().lower(); s=re.sub(r'^https?://','',s).split('/')[0]; return re.sub(r'^www\.','',s)
def path_of(u):
    s=html.unescape(str(u or "")).strip(); s=re.sub(r'^https?://[^/]+','',s); return s.strip('/').lower()
# reuse tolerant parse
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
    return dict(src=source_url,anchor=html.unescape(anchor),target=target,nofollow=parts[ni]=='true')
links=[]
for fn in ["bl_p1.csv","bl_p2.csv","bl_p3.csv"]:
    for line in open(f"{DATA}/{fn}",encoding="utf-8").read().splitlines()[1:]:
        if line.strip():
            p=parse_line(line)
            if p: links.append(p)
print("parsed links:",len(links))
SALES=re.compile(r'premium authority backlink|buy backlink|backlinks online cheap|pbn|da 50|guest post|white hat seo link|raise domain rating|premium backlink|premium seo|authority backlink',re.I)
GEO=re.compile(r'lexington|,?\s*sc\b',re.I); CONSTR=re.compile(r'construction|builder|contractor|office|retail|residential|commercial|home',re.I)
def home(t): return path_of(t)=="" 
# split: for each anchor category, home vs deep
cat=defaultdict(lambda:Counter())
for L in links:
    a=L["anchor"].lower()
    if SALES.search(a): c="sales/PBN"
    elif CONSTR.search(a) and GEO.search(a): c="geo-commercial"
    elif CONSTR.search(a): c="commercial(non-geo)"
    elif re.match(r'^(https?://)?(www\.)?blackwalnutconstruction',a): c="naked"
    elif 'visit' in a or a in ('website','read more'): c="generic"
    else: c="other"
    cat[c]["home" if home(L["target"]) else "deep"]+=1
for c,v in cat.items(): print(f"  {c:20} home={v['home']:>5} deep={v['deep']:>5}")
# top deep target pages
deep=Counter(path_of(L["target"]) for L in links if not home(L["target"]))
print("\nTop deep target paths:")
for k,v in deep.most_common(10): print(f"   {v:>5}  /{k}")
# where does the big sales anchor point, by host sample
print("\nsales/PBN anchor example targets:", Counter(path_of(L['target']) for L in links if SALES.search(L['anchor'].lower())).most_common(5))
