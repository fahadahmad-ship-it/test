import sys, openpyxl, re
from collections import Counter
p=sys.argv[1]
wb=openpyxl.load_workbook(p, read_only=True, data_only=True)

def norm(d):
    if d is None: return None
    s=str(d).strip().lower()
    s=re.sub(r'^domain:','',s)
    s=re.sub(r'^https?://','',s)
    s=s.rstrip('/')
    return s

# --- Referring Domain Audit ---
rda=wb["Referring Domain Audit"]
rows=list(rda.iter_rows(values_only=True))
hdr=rows[0]; idx={h:i for i,h in enumerate(hdr)}
data=rows[1:]
status_c=Counter()
audit_dom={}
dofollow_zero_but_disavow=[]
for r in data:
    dom=norm(r[idx['Domain']]); st=r[idx['Status']]
    status_c[st]+=1
    audit_dom[dom]={'status':st,'df':r[idx['Dofollow Links']],'nf':r[idx['Nofollow Links']],'indis':r[idx['In Disavow']],'bl':r[idx['Backlinks']],'as':r[idx['AS']]}
    if st=='Spam (Disavow)' and (r[idx['Dofollow Links']] in (0,None)):
        dofollow_zero_but_disavow.append(dom)

print("RDA data rows:", len(data))
print("Status counts:")
for k,v in status_c.most_common(): print(f"   {k}: {v}")

# --- Disavow List ---
dl=wb["Disavow List"]
dlrows=list(dl.iter_rows(values_only=True))
dl_doms=[norm(r[0]) for r in dlrows[1:] if r[0]]
dl_set=set(dl_doms)
print("\nDisavow List data rows:", len(dl_doms), "unique:", len(dl_set))
dup=[d for d,c in Counter(dl_doms).items() if c>1]
print("Duplicate disavow lines:", len(dup), dup[:10])

# --- Pending Disavow Lines ---
pd=wb["Pending Disavow Lines"]
pdrows=list(pd.iter_rows(values_only=True))
pend_doms=set(norm(r[0]) for r in pdrows[1:] if r[0])
print("\nPending Disavow Lines rows:", len(pend_doms))

# --- Exact Match Anchors (Tab 05) ---
em=wb["Exact Match Anchors"]
emrows=list(em.iter_rows(values_only=True))
em_doms=set(norm(r[0]) for r in emrows[1:] if r[0])
print("Exact Match Anchors (Tab 05) rows:", len(em_doms))

# ===== CRITICAL CROSS-CHECKS =====
print("\n===== CRITICAL CHECKS =====")
leak_pending = dl_set & pend_doms
print("[LEAK] Pending-partner domains that appear in Disavow List:", len(leak_pending), sorted(leak_pending)[:20])
leak_em = dl_set & em_doms
print("[LEAK] Tab05 exact-match domains in Disavow List:", len(leak_em), sorted(leak_em)[:20])

# Status-based: which statuses do disavow-list domains have in the audit?
dl_status=Counter(audit_dom.get(d,{}).get('status','<<NOT IN AUDIT>>') for d in dl_set)
print("\nStatus (per RDA) of each domain in the Disavow List:")
for k,v in dl_status.most_common(): print(f"   {k}: {v}")

# Spam(Disavow) in audit but NOT in disavow list
spam_disavow_doms=set(d for d,v in audit_dom.items() if v['status']=='Spam (Disavow)')
missing_from_dl = spam_disavow_doms - dl_set
extra_in_dl = dl_set - spam_disavow_doms
print("\nSpam(Disavow) domains in RDA missing from Disavow List:", len(missing_from_dl), sorted(missing_from_dl)[:20])
print("Disavow List domains NOT marked Spam(Disavow) in RDA:", len(extra_in_dl), sorted(extra_in_dl)[:20])

print("\nSpam(Disavow) rows with 0/None dofollow links (contradiction):", len(dofollow_zero_but_disavow), dofollow_zero_but_disavow[:20])

# Keep / Held domains leaking into disavow
keep_doms=set(d for d,v in audit_dom.items() if v['status']=='Keep')
print("\n[LEAK] 'Keep' domains in Disavow List:", len(keep_doms & dl_set), sorted(keep_doms & dl_set)[:20])
held_doms=set(d for d,v in audit_dom.items() if str(v['status']).startswith('Held'))
print("[LEAK] 'Held' domains in Disavow List:", len(held_doms & dl_set), sorted(held_doms & dl_set)[:20])

# Pending vs Held relationship
print("\nPending set vs Held(Pending Partner) RDA set:")
held_pending=set(d for d,v in audit_dom.items() if v['status']=='Held (Pending Partner)')
print("   Held(Pending Partner) in RDA:", len(held_pending))
print("   Pending tab not in Held(Pending Partner) RDA:", len(pend_doms-held_pending), sorted(pend_doms-held_pending)[:10])
print("   Tab05 that are Held(Nofollow,No Action):", len(em_doms & set(d for d,v in audit_dom.items() if v['status']=='Held (Nofollow, No Action)')))

# concentration
tot_bl_disavow=sum((audit_dom.get(d,{}).get('bl') or 0) for d in dl_set)
print("\nTotal backlinks represented by disavow domains:", tot_bl_disavow)
top=sorted(((audit_dom.get(d,{}).get('bl') or 0),d) for d in dl_set)[-5:]
print("Top 5 disavow domains by backlink count:", list(reversed(top)))
