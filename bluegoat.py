import csv, sys
path=sys.argv[1]
built=set(l.strip().lower() for l in open('built-bluegoat.txt') if l.strip())
def num(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0
TECH={'technology','software','ai','saas','cybersecurity','security','tech news','software development','data'}
HEALTH={'health & fitness','health and medicine','mental health','wellness'}
BIZ={'business','entrepreneurship','finance','marketing','digital marketing'}
BAD=('casino','crypto30x','betting','adult','escort')
out=[]
for r in csv.DictReader(open(path,encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built or any(b in d for b in BAD): continue
    if (r.get('Language') or '').strip().lower()!='english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    AS,TF,CF=num(r.get('AS')),num(r.get('TF')),num(r.get('CF'))
    tr,pr,rd=num(r.get('Traffic')),num(r.get('Price ($)')),num(r.get('RD'))
    if pr<=0 or pr>=300 or AS<30 or TF<25 or tr<10000 or rd<300: continue
    if TF<CF*0.55: continue
    tech=bool(cats&TECH); health=bool(cats&HEALTH); biz=bool(cats&BIZ)
    if not (tech or health): continue
    b='Tech/Security' if tech else 'Health/Med'
    if tech and health: b='Tech+Health'
    out.append((AS+TF,d,b,r.get('Category'),AS,TF,CF,tr,rd,pr))
out.sort(reverse=True)
print(f"{len(out)} unbuilt candidates under $300\n")
print(f"{'Domain':34}{'Bucket':14}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>8}  Category")
print('-'*128)
for s,d,b,c,A,T,C,tr,rd,p in out[:40]:
    print(f"{d:34}{b:14}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:8,.0f}{p:8,.0f}  {c[:40]}")
with open('bluegoat-candidates.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Domain','Bucket','Category','AS','TF','CF','Traffic','RD','Price_USD'])
    for s,d,b,c,A,T,C,tr,rd,p in out:
        w.writerow([d,b,c,int(A),int(T),int(C),int(tr),int(rd),round(p,2)])
print(f"\n-> bluegoat-candidates.csv ({len(out)} rows)")
