import sys, openpyxl, re
from collections import Counter, defaultdict
p=sys.argv[1]
wb=openpyxl.load_workbook(p, read_only=True, data_only=True)
def norm(d):
    if d is None: return None
    s=str(d).strip().lower(); s=re.sub(r'^domain:','',s); s=re.sub(r'^https?://','',s); return s.rstrip('/')

rda=wb["Referring Domain Audit"]; rows=list(rda.iter_rows(values_only=True))
hdr=rows[0]; I={h:i for i,h in enumerate(hdr)}
audit={}
for r in rows[1:]:
    audit[norm(r[I['Domain']])]={'status':r[I['Status']],'as':r[I['AS']] or 0,'df':r[I['Dofollow Links']] or 0,'nf':r[I['Nofollow Links']] or 0,'bl':r[I['Backlinks']] or 0,'anchor':r[I['Top Anchor Text']],'points':r[I['Links Point To']]}

disavow=set(d for d,v in audit.items() if v['status']=='Spam (Disavow)')

# 1. High-AS domains being disavowed (false-positive risk)
hi=sorted(((audit[d]['as'],d,audit[d]['bl'],audit[d]['anchor']) for d in disavow), reverse=True)[:20]
print("=== Highest-AS domains in the DISAVOW set (manual-review candidates) ===")
for a,d,bl,anc in hi:
    print(f"  AS={a:>3}  bl={bl:>4}  {d:30}  anchor={str(anc)[:70]!r}")

# 2. Nofollow-no-action contradictions
contr=[d for d,v in audit.items() if v['status']=='Spam (Nofollow, No Action)' and v['df']>0]
print("\nSpam(Nofollow,No Action) with dofollow>0 (contradiction):", len(contr), contr[:10])
contr2=[d for d,v in audit.items() if v['status']=='Held (Nofollow, No Action)' and v['df']>0]
print("Held(Nofollow,No Action) with dofollow>0 (contradiction):", len(contr2), contr2[:10])

# 3. Keep bucket: distribution of AS and 'points to'; flag Keep domains whose top anchor looks like spam sales copy
keep=set(d for d,v in audit.items() if v['status']=='Keep')
spam_kw=re.compile(r'(backlink|seo|guest post|pbn|domain rating|domain authority|rank|trust flow|da 50|pa 40|buy |premium.*link)', re.I)
keep_spammy=[(d,audit[d]['anchor'],audit[d]['df']) for d in keep if audit[d]['anchor'] and spam_kw.search(str(audit[d]['anchor']))]
print(f"\nKeep domains whose TOP anchor matches spam-sales regex (possible false negatives): {len(keep_spammy)}")
for d,anc,df in keep_spammy[:15]:
    print(f"   {d:30} df={df} anchor={str(anc)[:70]!r}")

# 4. Disavow domains whose top anchor is branded/naked only (possible false positives)
brandnaked=re.compile(r'^(newgarden\.com|new garden|https?://(www\.)?newgarden\.com/?)$', re.I)
dis_brand=[(d,audit[d]['anchor']) for d in disavow if audit[d]['anchor'] and brandnaked.match(str(audit[d]['anchor']).strip())]
print(f"\nDisavow domains whose TOP anchor is purely branded/naked URL (possible FP): {len(dis_brand)}")
for d,anc in dis_brand[:15]: print(f"   {d:30} {anc!r}")

# 5. 'Links Point To' distribution across whole profile and within disavow
pt=Counter(v['points'] for v in audit.values())
print("\n'Links Point To' (whole profile) top:", pt.most_common(6))
ptd=Counter(audit[d]['points'] for d in disavow)
print("'Links Point To' (disavow only) top:", ptd.most_common(6))

# 6. Tab 05 full breakdown
em=wb["Exact Match Anchors"]; emrows=list(em.iter_rows(values_only=True)); eh=emrows[0]
print("\n=== Tab 05 (Exact Match Anchors) columns:", eh)
mkt=Counter(); sitetype=Counter(); dfsplit=Counter()
em_doms=[]
for r in emrows[1:]:
    dom=norm(r[0]); em_doms.append(dom)
    mkt[r[3]]+=1; sitetype[r[4]]+=1
    st=audit.get(dom,{}).get('status','?'); dfsplit[st]+=1
print("Tab05 markets:", mkt.most_common())
print("Tab05 site types:", sitetype.most_common())
print("Tab05 by RDA status:", dfsplit.most_common())
