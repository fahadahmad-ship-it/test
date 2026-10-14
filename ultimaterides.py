import csv, sys
built=set(l.strip().lower() for l in open('built-ultimaterides.txt') if l.strip())
def n(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0
AUTO={'automotive','cars','motoring','transport','vehicles'}
SOFT={'lifestyle','travel','news','media','journalism','business','technology','sports','reviews','general'}
UGC=('blogspot','wordpress.com','tumblr','medium.com','substack','linktr','issuu','quora','reddit','.edu',
'merchantcircle','behance','patreon','gofundme','tinyurl','dev.to','ko-fi','crunchbase','wufoo','clickup')
JUNK=('casino','betting','adult','escort','torrent','mp3','downloader','apk')
FOREIGN=('.in','.ng','.pk','.ke','.za','.bd','.lk','.ph','.id','india','nigeria','kashmir')
rows=[]
for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built: continue
    if any(u in d for u in UGC) or any(j in d for j in JUNK): continue
    if any(d.endswith(f) for f in FOREIGN): continue
    if (r.get('Language') or '').strip().lower()!='english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    AS,TF,CF=n(r.get('AS')),n(r.get('TF')),n(r.get('CF'))
    tr,pr,rd=n(r.get('Traffic')),n(r.get('Price ($)')),n(r.get('RD'))
    if pr<=0 or pr>320 or AS<35 or TF<28 or tr<15000 or rd<300: continue
    if TF<CF*0.5: continue
    auto=bool(cats&AUTO)
    if not (auto or (cats&SOFT)): continue
    rows.append((auto, AS+TF, d, r.get('Category'), AS,TF,CF,tr,rd,pr))
rows.sort(key=lambda x:(not x[0], -x[1]))
a=[r for r in rows if r[0]]; o=[r for r in rows if not r[0]]
print(f"\n=== AUTOMOTIVE category ({len(a)}) ===")
print(f"{'Domain':34}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>8}  Category")
print('-'*120)
for _,s,d,c,A,T,C,tr,rd,p in a[:22]:
    print(f"{d:34}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:8,.0f}{p:8,.0f}  {c[:36]}")
print(f"\n=== ADJACENT lifestyle/news ({len(o)}) - top 14 ===")
for _,s,d,c,A,T,C,tr,rd,p in o[:14]:
    print(f"{d:34}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:8,.0f}{p:8,.0f}  {c[:36]}")
