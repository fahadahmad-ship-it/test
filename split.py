import sys, openpyxl, re
from collections import defaultdict, Counter
NG=sys.argv[1]
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^https?://','',s).rstrip('/')
wd=openpyxl.load_workbook(NG, read_only=True, data_only=True)
rda=wd["Referring Domain Audit"]; rows=list(rda.iter_rows(values_only=True)); I={h:i for i,h in enumerate(rows[0])}
status={}; AS={}
for r in rows[1:]:
    d=norm(r[I['Domain']]); status[d]=r[I['Status']]; AS[d]=r[I['AS']] or 0
ab=wd["All Backlinks"]; arows=list(ab.iter_rows(values_only=True)); A={h:i for i,h in enumerate(arows[0])}
em_dofollow=set(); em_any=set()
for r in arows[1:]:
    if 'exact match commercial' in str(r[A['Anchor Type']]).lower():
        d=norm(r[A['Referring Domain']]); em_any.add(d)
        if str(r[A['Link Type']]).lower().startswith('dofollow'): em_dofollow.add(d)
keep_em=[d for d in em_any if status.get(d)=='Keep']
# apply rule 2: AS>=20 stays Keep
stay_keep=[d for d in keep_em if AS[d]>=20]
move=[d for d in keep_em if AS[d]<20]
move_dofollow=[d for d in move if d in em_dofollow]      # -> Held (Pending Partner)
move_nofollow=[d for d in move if d not in em_dofollow]  # -> Held (Nofollow, No Action)
print("Keep w/ exact-match commercial:", len(keep_em))
print("  stay Keep (AS>=20, rule 2):", len(stay_keep))
print("    examples:", sorted((AS[d],d) for d in stay_keep)[-12:])
print("  MOVE to Held:", len(move), " dofollow->Pending:", len(move_dofollow), " nofollow->NoAction:", len(move_nofollow))
print("  AS distribution of movers:", Counter(('<10' if AS[d]<10 else '10-19') for d in move))
# save move lists for the builder
import json
json.dump({"move_dofollow":sorted(move_dofollow),"move_nofollow":sorted(move_nofollow),"stay_keep":sorted(stay_keep)}, open("/home/user/test/move_sets.json","w"))
print("\nwrote move_sets.json")
# new counts
base=Counter(status.values())
print("\nProjected new status counts:")
print("  Spam (Disavow):", base['Spam (Disavow)'])
print("  Spam (Nofollow, No Action):", base['Spam (Nofollow, No Action)'])
print("  Held (Pending Partner):", base['Held (Pending Partner)']+len(move_dofollow))
print("  Held (Nofollow, No Action):", base['Held (Nofollow, No Action)']+len(move_nofollow))
print("  Keep:", base['Keep']-len(move))
print("  Own Site:", base.get('Own Site',0))
print("  TOTAL:", base['Spam (Disavow)']+base['Spam (Nofollow, No Action)']+base['Held (Pending Partner)']+len(move_dofollow)+base['Held (Nofollow, No Action)']+len(move_nofollow)+base['Keep']-len(move)+base.get('Own Site',0))
