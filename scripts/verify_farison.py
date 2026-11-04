import sys, re, collections, json, glob, html
import openpyxl
from urllib.parse import urlparse
X="/home/user/test/deliverables/Farison_Backlinks_Audit.xlsx"
FA="/home/user/test/deliverables/disavow_farison.com.txt"
LC="/home/user/test/deliverables/disavow_lawncare-louisvilleky.com.txt"
wb=openpyxl.load_workbook(X); wbv=openpyxl.load_workbook(X,data_only=True)
def rows(t):
    ws=wbv[t]; rr=list(ws.iter_rows(values_only=True)); h=[str(x).strip() if x else "" for x in rr[0]]
    return h,[r for r in rr[1:] if any(c is not None for c in r)]
fails=[];oks=[]
def chk(c,m): (oks if c else fails).append(m)
chk(wb.sheetnames==['Summary','Referring Domain Audit','All Backlinks','Anchor Analysis','Exact Match Anchors','Pending Disavow Lines','Disavow List'],f"tab order {wb.sheetnames}")
rh,rda=rows('Referring Domain Audit'); ci={n:i for i,n in enumerate(rh)}
ah,abl=rows('All Backlinks'); ai={n:i for i,n in enumerate(ah)}
dh,dis=rows('Disavow List'); eh,ema=rows('Exact Match Anchors'); ph,pend=rows('Pending Disavow Lines')
status={str(r[ci['Domain']]).lower():str(r[ci['Status']]) for r in rda}
dofo={str(r[ci['Domain']]).lower():(r[ci['Dofollow Links']] or 0) for r in rda}
dom_by=collections.Counter(str(r[ci['Status']]) for r in rda)
# counts reconcile with summary
sws=wbv['Summary']; srows=list(sws.iter_rows(values_only=True))
sumtab={str(r[0]).strip():r[1] for r in srows if r and r[0] and str(r[0]).strip() in dom_by}
for st,n in dom_by.items(): chk(sumtab.get(st)==n, f"Summary {st}={sumtab.get(st)} vs RDA {n}")
# disavow list integrity
dl=[str(r[0]).strip() for r in dis]
chk(all(re.fullmatch(r'domain:[a-z0-9.\-]+',l) for l in dl), "all disavow lines well-formed")
chk(len(set(dl))==len(dl), f"no dup disavow lines (n={len(dl)})")
leak=[l for l in dl if status.get(l.split('domain:')[1])!="Spam (Disavow)"]
chk(not leak, f"no non-spam leak in Disavow List ({len(leak)})")
nod=[l for l in dl if not (dofo.get(l.split('domain:')[1]) or 0)>0]
chk(not nod, f"every disavow domain has >=1 dofollow ({len(nod)})")
# tab08 all held, none disavowed
TAB08=["gotolistings.org","getzzby.com","findzy.net","listingspace.net","showyourbizz.com","directoryhop.com","premiumlistings.co","downtownlists.com","b-listings.com","prolocalbusinesssearch.com","boblistings.org","smallbizdir.com","local-business-center.com"]
t8=[d for d in TAB08 if status.get(d,"MISSING")!="Held (Pending Partner)"]
chk(not t8, f"all 13 Tab08 domains Held ({t8})")
chk(not any(f"domain:{d}" in dl for d in TAB08), "no Tab08 domain in disavow")
# held never in disavow
held=set(d for d,s in status.items() if s.startswith("Held"))
chk(not (held & set(l.split('domain:')[1] for l in dl)), "no Held domain in disavow")
# files
def readf(p): return [l.strip() for l in open(p) if l.strip() and not l.startswith('#')]
fa=readf(FA); lc=readf(LC)
chk(len(fa)==len(dl), f"farison.txt lines={len(fa)} == Disavow List {len(dl)}")
chk(set(x.split('domain:')[1] for x in fa)==set(l.split('domain:')[1] for l in dl), "farison.txt set == Disavow List set")
chk(set(lc)<=set(fa), f"lawncare file subset of farison union (lc={len(lc)}, extra={len(set(lc)-set(fa))})")
chk(all(status.get(l.split('domain:')[1])=="Spam (Disavow)" for l in lc), "lawncare file all spam-disavow")
# exact match tab: all held + has exact anchor present
ema_doms=[str(r[0]).lower() for r in ema]
chk(all(status.get(d,'').startswith('Held') for d in ema_doms), "all Exact-Match-tab domains are Held")
# pending == held pending partner count
chk(len(pend)==dom_by['Held (Pending Partner)'], f"Pending rows {len(pend)} == Held(Pending) {dom_by['Held (Pending Partner)']}")
# anchor analysis sum
nh,anc=rows('Anchor Analysis'); chk(sum(int(r[2]) for r in anc)==len(abl), f"Anchor Analysis sum {sum(int(r[2]) for r in anc)} == backlinks {len(abl)}")

# ---- CRITICAL SWEEPS ----
# FP: disavow domain with AS>=20 (should be Keep per rule 2)
as_of={str(r[ci['Domain']]).lower():r[ci['AS']] for r in rda}
def num(x):
    try:return float(x)
    except:return None
fp_as=[l.split('domain:')[1] for l in dl if (num(as_of.get(l.split('domain:')[1])) or 0)>=20]
chk(not fp_as, f"no disavow domain with AS>=20 ({len(fp_as)}: {fp_as[:5]})")
# FN: Keep domain with dofollow sales/off anchor
SALES=["backlink","pbn","da 50","pa 40"," seo ","premium seo","dofollow backlinks","buy backlink","rank higher","authority backlinks","link building","traffic focused","grow your website","website authority"]
OFF=["casino","gambl","poker","porn","viagra","pharma","payday","loan","crypto","escort","telegram @"]
def hit(t,toks): tl=(t or "").lower(); return any(k in tl for k in toks)
keepset=set(d for d,s in status.items() if s=="Keep")
fn=[]
for r in abl:
    if str(r[ai['Status']])=="Keep" and str(r[ai['Link Type']])=="Dofollow":
        if str(r[ai['Anchor Type']]).startswith("Spam") or hit(r[ai['Anchor Text']],OFF):
            fn.append((r[ai['Referring Domain']],str(r[ai['Anchor Text']])[:40]))
chk(not fn, f"no Keep domain with dofollow spam anchor ({len(fn)}: {fn[:5]})")
# over-holding: Held domain whose EVERY link is sales-copy (should be spam)
held_salesonly=[]
by=collections.defaultdict(list)
for r in abl: by[str(r[ai['Referring Domain']]).lower()].append(r)
for d in held:
    ls=by.get(d,[])
    if ls and all(str(x[ai['Anchor Type']])=="Spam: keyword stuffed SEO sales copy" for x in ls):
        held_salesonly.append(d)
chk(not held_salesonly, f"no Held domain is 100% sales-copy ({len(held_salesonly)}: {held_salesonly[:5]})")
# disavow domain with NO visible evidence (anchor type benign & host benign & title benign)
HOSTSPAM=["backlink","pbn","seo","dapa","dacheck","pacheck","rank","buy","directory","listing","traffic","domain","web","link","dir","checker"]
noev=[]
for l in dl:
    d=l.split('domain:')[1]; ls=by.get(d,[])
    has=any(str(x[ai['Anchor Type']]).startswith("Spam") for x in ls) or hit(d,HOSTSPAM) or any(hit(x[ai['Linking Page Title']],SALES+OFF) for x in ls)
    tld=d.rsplit('.',1)[-1]
    if not has and tld not in ("store","site","shop","online","space","website","cfd","sbs","icu","top","click","live","xyz"):
        noev.append(d)
chk(len(noev)<=5, f"disavow domains with thin visible evidence: {len(noev)} (sample {noev[:8]})")

print("PASS:",len(oks),"FAIL:",len(fails))
for m in fails: print("  FAIL ->",m)
print("\nHeld sample (first 12 exact-match held domains + anchor):")
for r in ema[:12]: print("  ",str(r[0]),"=>",str(r[2])[:46],"| market:",r[3])
print("\nnoev sample:",noev[:12])
