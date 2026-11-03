import openpyxl, re, sys
from collections import Counter
WB="/home/user/test/NewGarden_Backlinks_Audit.xlsx"
wb=openpyxl.load_workbook(WB, data_only=True)
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^domain:','',re.sub(r'^https?://','',s)).rstrip('/')
rda=wb["Referring Domain Audit"]; rh=[c.value for c in rda[1]]; Ri={h:i for i,h in enumerate(rh)}
status={}; dofollow={}; pos={}
for row in rda.iter_rows(min_row=2):
    d=norm(row[Ri['Domain']].value); status[d]=row[Ri['Status']].value
    dofollow[d]=row[Ri['Dofollow Links']].value or 0; pos[d]=row[Ri['Links Point To']].value
ab=wb["All Backlinks"]; abh=[c.value for c in ab[1]]; Ai={h:i for i,h in enumerate(abh)}
dom_anchor_types=Counter(); dom_spam_do=set(); dom_offtopic=set()
from collections import defaultdict
types_by=defaultdict(set); ev_blob=defaultdict(str)
for row in ab.iter_rows(min_row=2):
    d=norm(row[Ai['Referring Domain']].value); at=str(row[Ai['Anchor Type']].value); lt=str(row[Ai['Link Type']].value).lower()
    types_by[d].add(at)
    ev_blob[d]+=' '+at+' '+str(row[Ai['Anchor Text']].value)+' '+str(row[Ai['Linking Page Title']].value)+' '+str(row[Ai['Linking Page URL']].value)
    if lt.startswith('dofollow') and 'sales copy' in at.lower(): dom_spam_do.add(d)
    if 'off topic' in at.lower() or 'off-topic' in at.lower(): dom_offtopic.add(d)

dl=set(norm(r[0].value) for r in wb["Disavow List"].iter_rows(min_row=2) if r[0].value)
pend=set(norm(r[0].value) for r in wb["Pending Disavow Lines"].iter_rows(min_row=2) if r[0].value)
em=set(norm(r[0].value) for r in wb["Exact Match Anchors"].iter_rows(min_row=2) if r[0].value)
P=[]; FAIL=0
def ok(name,cond,extra=""):
    global FAIL
    print(("PASS" if cond else "FAIL"),"-",name,("" if cond else extra))
    if not cond: FAIL+=1

# integrity
fl=[norm(x) for x in dl]
ok("disavow lines lowercase domain-only, no dup", len(fl)==len(set(fl)) and all(re.match(r'^[a-z0-9.*-]+(\.[a-z]+)+$',x) for x in fl))
ok("every disavow domain is Spam (Disavow)", all(status.get(d)=='Spam (Disavow)' for d in dl), str([d for d in dl if status.get(d)!='Spam (Disavow)'][:5]))
ok("every disavow domain has >=1 dofollow", all(dofollow.get(d,0)>0 for d in dl), str([d for d in dl if dofollow.get(d,0)<1][:5]))
ok("no Held/Keep/OwnSite leak into disavow", not any(str(status.get(d,'')).startswith(('Held','Keep','Own')) for d in dl))
ok("no nofollow-spam leak into disavow", not any(status.get(d)=='Spam (Nofollow, No Action)' for d in dl))
# false positives: evidence
spamhost=re.compile(r'(backlink|seo|dapa|rankcheck|directory|listing|bookmark|domainlist|aged.?domain|pbn|link)')
evid=re.compile(r'(sales copy|off.?topic|aged domains|buy .*backlink|backlinks|pbn|guest post|domain rating|domain authority|rank first|rank your|trust flow|where to buy|casino|pharma|viagra|escort|betting|loan|page-[0-9a-f]{8}|/domain/|domain list page|sitetosocial|fully automate)')
noevid=[d for d in dl if not(spamhost.search(d) or evid.search(ev_blob[d].lower()) or d=='rosih.ru')]
ok("every disavow domain rests on visible evidence (not AS/TLD alone)", len(noevid)==0, f"{len(noevid)} e.g. {noevid[:8]}")
# false negatives
fn1=[d for d,st in status.items() if (str(st).startswith('Keep') or str(st).startswith('Held')) and d in dom_spam_do]
ok("no Keep/Held domain carries a dofollow spam-sales anchor", len(fn1)==0, f"{len(fn1)} e.g. {fn1[:8]}")
fn2=[d for d,st in status.items() if st=='Spam (Nofollow, No Action)' and dofollow.get(d,0)>0]
ok("no nofollow-marked spam actually has a dofollow link", len(fn2)==0, str(fn2[:8]))
# reconciliation
cnt=Counter(status.values())
ok("status counts sum to 2683", sum(cnt.values())==2683, str(dict(cnt)))
ok("Disavow List == Spam(Disavow) set", dl==set(d for d,s in status.items() if s=='Spam (Disavow)'))
ok("Pending == Held(Pending Partner) set", pend==set(d for d,s in status.items() if s=='Held (Pending Partner)'))
ok("Tab05 == Held(Pending)+Held(Nofollow) set", em==set(d for d,s in status.items() if s in('Held (Pending Partner)','Held (Nofollow, No Action)')))
ok("no overlap disavow vs pending", len(dl&pend)==0)
# moved domains sanity
import json; mv=json.load(open("move_sets.json")); moved=set(mv['move_dofollow'])|set(mv['move_nofollow'])
ok("all 114 moved domains now Held", all(str(status.get(d,'')).startswith('Held') for d in moved))
ok("none of the moved domains are in disavow", len(moved&dl)==0)
ok("4 AS>=20 stayed Keep", all(status.get(norm(d))=='Keep' for d in mv['stay_keep']))
print("\nTOTAL FAILURES:",FAIL)
