import csv, sys
built=set(l.strip().lower() for l in open('built-bluegoat.txt') if l.strip())
def n(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0
NEWS={'news','media','journalism','community','politics','general','business','finance','entrepreneurship'}
JUNK=('casino','betting','crypto30x','adult','escort','torrent','mp3','downloader','apk','mod')
UGC=('blogspot','wordpress.com','tumblr','medium.com','substack','linktr','issuu','quora','reddit','.edu')
GEO_OUT=('.ng','.in','.pk','.ke','.zw','.gh','.bd','.lk','.ph','.id','.za','.ae','.qa')
rows=[]
for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built: continue
    if any(j in d for j in JUNK) or any(u in d for u in UGC): continue
    if any(d.endswith(g) for g in GEO_OUT): continue
    if (r.get('Language') or '').strip().lower()!='english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    if not (cats & NEWS): continue
    AS,TF,CF=n(r.get('AS')),n(r.get('TF')),n(r.get('CF'))
    tr,pr,rd=n(r.get('Traffic')),n(r.get('Price ($)')),n(r.get('RD'))
    if pr<=0 or pr>=320 or AS<38 or TF<30 or tr<15000 or rd<500: continue
    if TF<CF*0.55: continue
    rows.append((AS+TF,d,r.get('Category'),AS,TF,CF,tr,rd,pr))
rows.sort(key=lambda x:-x[0])
print(f"{len(rows)} unbuilt news/business candidates under $320\n")
print(f"{'Domain':34}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>8}  Category")
print('-'*122)
for s,d,c,A,T,C,tr,rd,p in rows[:45]:
    print(f"{d:34}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:8,.0f}{p:8,.0f}  {c[:38]}")
with open('bluegoat-news-candidates.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Domain','Category','AS','TF','CF','Traffic','RD','Price_USD'])
    for s,d,c,A,T,C,tr,rd,p in rows: w.writerow([d,c,int(A),int(T),int(C),int(tr),int(rd),round(p,2)])
print(f"\n-> bluegoat-news-candidates.csv ({len(rows)} rows)")
