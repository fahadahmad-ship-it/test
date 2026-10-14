import csv, sys
path = sys.argv[1]
built = set(l.strip().lower() for l in open('built.txt') if l.strip())

def num(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0

CORE = {'food & drink','home','parenting','family','events','wellness','cooking','recipes'}
SOFT = {'lifestyle','culture','shopping','health & fitness','beauty','travel'}

rows=[]
for r in csv.DictReader(open(path, encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built: continue
    if (r.get('Language') or '').strip().lower() != 'english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    core=bool(cats & CORE); soft=bool(cats & SOFT)
    if not (core or soft): continue
    AS,TF,CF = num(r.get('AS')), num(r.get('TF')), num(r.get('CF'))
    tr, pr, rd = num(r.get('Traffic')), num(r.get('Price ($)')), num(r.get('RD'))
    if pr<=0 or AS<20 or TF<15 or tr<1000: continue
    if TF < CF*0.45: continue              # drop inflated/spammy link profiles
    au = d.endswith('.com.au') or d.endswith('.au') or d.endswith('.co.nz')
    score = (tr**0.5)*(AS+TF)/pr * (1.6 if core else 1.0) * (1.5 if au else 1.0)
    rows.append((score,d,r.get('Category'),AS,TF,CF,tr,rd,pr,core,au))

rows.sort(reverse=True)
print(f"{len(rows)} candidates passed filters\n")
hdr=f"{'Domain':34}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>10}  Cat"
print(hdr); print('-'*len(hdr)+'-'*30)
for s,d,c,A,T,C,tr,rd,pr,core,au in rows[:55]:
    tag = ' [AU/NZ]' if au else (' [core]' if core else '')
    print(f"{d:34}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:8,.0f}{pr:10,.0f}  {c[:40]}{tag}")

with open('nangwizard-reachgorilla-shortlist.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Domain','Category','AS','TF','CF','Traffic','RD','Price_USD','CoreNiche','AU_NZ'])
    for s,d,c,A,T,C,tr,rd,pr,core,au in rows[:150]:
        w.writerow([d,c,int(A),int(T),int(C),int(tr),int(rd),round(pr,2),'yes' if core else 'no','yes' if au else 'no'])
print("\n-> nangwizard-reachgorilla-shortlist.csv (top 150)")
