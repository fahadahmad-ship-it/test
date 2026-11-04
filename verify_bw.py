import openpyxl, re
from collections import Counter, defaultdict
WB="/home/user/test/BlackWalnut_Backlinks_Audit.xlsx"
wb=openpyxl.load_workbook(WB, data_only=True)
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^domain:','',re.sub(r'^https?://','',s)).rstrip('/')
rda=wb["Referring Domain Audit"]; rh=[c.value for c in rda[1]]; Ri={h:i for i,h in enumerate(rh)}
status={}; dof={}
for r in rda.iter_rows(min_row=2,values_only=True):
    d=norm(r[Ri['Domain']]); status[d]=r[Ri['Status']]; dof[d]=r[Ri['Dofollow Links']] or 0
ab=wb["All Backlinks"]; abh=[c.value for c in ab[1]]; Ai={h:i for i,h in enumerate(abh)}
blob=defaultdict(str); spam_do=set()
for r in ab.iter_rows(min_row=2,values_only=True):
    d=norm(r[Ai['Referring Domain']]); at=str(r[Ai['Anchor Type']]); lt=str(r[Ai['Link Type']]).lower()
    blob[d]+=" "+at+" "+str(r[Ai['Anchor Text']])+" "+str(r[Ai['Linking Page Title']])
    if lt=="dofollow" and ('sales copy' in at.lower() or 'off topic' in at.lower()): spam_do.add(d)
dl=set(norm(r[0].value) for r in wb["Disavow List"].iter_rows(min_row=2) if r[0].value)
pend=set(norm(r[0].value) for r in wb["Pending Disavow Lines"].iter_rows(min_row=2) if r[0].value)
em=set(norm(r[0].value) for r in wb["Exact Match Anchors"].iter_rows(min_row=2) if r[0].value)
FAIL=0
def ok(n,c,x=""):
    global FAIL; print(("PASS" if c else "FAIL"),"-",n,("" if c else x)); FAIL+= 0 if c else 1
ok("disavow lowercase domain-only, no dup", all(re.match(r'^[a-z0-9.*-]+\.[a-z]+$',x) for x in dl) and len(dl)==len(dl))
ok("every disavow domain is Spam (Disavow)", all(status.get(d)=="Spam (Disavow)" for d in dl), str([d for d in dl if status.get(d)!="Spam (Disavow)"][:5]))
ok("every disavow domain has dofollow>0", all(dof.get(d,0)>0 for d in dl), str([d for d in dl if dof.get(d,0)<1][:5]))
ok("no Held/Keep/Own leak into disavow", not any(str(status.get(d,'')).startswith(('Held','Keep','Own')) for d in dl))
ok("no nofollow-spam in disavow", not any(status.get(d)=="Spam (Nofollow, No Action)" for d in dl))
spamhost=re.compile(r'backlink|seo|dapa|pacheck|rankcheck|checker|directory|listing|bookmark|serp|keyword|traffic|linkbuild|dofollow|domain|pbn|aged|whitehat|getwebsiteworth|webworth|linksnatcher|ranktool')
evid=re.compile(r'sales copy|off topic|aged domains and backlinks|seo domain research|where to buy|premium authority backlink|buy backlink|pbn|da 50|guest post|raise domain rating|premium seo|authority backlink|domain report|website stats|/domain/domain/part|page-[0-9a-f]{8}|sitetosocial|pinterest tool|domraider|no middlemen|seo resource|lowest pr',re.I)
noev=[d for d in dl if not(spamhost.search(d) or evid.search(blob[d]))]
ok("every disavow domain rests on visible evidence (not AS/TLD alone)", len(noev)==0, f"{len(noev)}: {noev[:10]}")
fn=[d for d,s in status.items() if (str(s).startswith('Keep') or str(s).startswith('Held')) and d in spam_do]
ok("no Keep/Held carries dofollow spam/offtopic anchor", len(fn)==0, str(fn[:8]))
ok("counts sum to 1631", sum(Counter(status.values()).values())==1631, str(dict(Counter(status.values()))))
ok("Disavow List == Spam(Disavow) set", dl==set(d for d,s in status.items() if s=="Spam (Disavow)"))
ok("Pending == Held(Pending Partner) set", pend==set(d for d,s in status.items() if s=="Held (Pending Partner)"))
ok("Tab05 == all Held set", em==set(d for d,s in status.items() if str(s).startswith("Held")))
ok("no overlap disavow vs pending", len(dl&pend)==0)
ok("powerbizdirectory & webmash are Held (deep-page rule)", status.get("powerbizdirectory.com","").startswith("Held") and status.get("webmash.org","").startswith("Held"))
print("\nTOTAL FAILURES:",FAIL)
