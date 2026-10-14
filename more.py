import csv
done={'dorsetecho.co.uk','atn.com.au','autostraddle.com','finegardening.com','cheese.com',
'sometimes-homemade.com','live-less-ordinary.com','visitdevon.co.uk','visitsouthdevon.co.uk',
'fancyhouse-design.com','bullz-eye.com','thearchitectsdiary.com','sociallifemagazine.com',
'lorddecor.com','great-days-out.co.uk','thesoulofseoul.net','trendingus.com','milomagazine.co.uk',
'nomadlawyer.org','uploadarticle.com','buddymagazine.org','thegooddogguide.com','iwaymagazine.com',
'elevatedmagazines.com','firsttouchonline.com','iharare.com'}
HEALTH=('health','wellness','medic','nurse','yoga','doctor','fitness')
GEO=('.ng','.gh','.in','.pk','.ke','.zw','.ae','guardian.ng','qatarday','kuwait','udaipur','deccan','yen.com')
out=[]
for r in csv.DictReader(open('nangwizard-reachgorilla-shortlist.csv')):
    d=r['Domain']; p=float(r['Price_USD']); AS=int(r['AS']); TF=int(r['TF']); tr=int(r['Traffic'])
    cat=r['Category'].lower()
    if d in done or p>=400 or AS<32 or TF<22 or tr<15000: continue
    if any(g in d for g in GEO): continue
    if r['Bucket'] not in ('Food','Home/Family','AU/NZ'): continue
    if sum(h in cat for h in HEALTH)>=2: continue
    out.append((AS+TF,d,r['Bucket'],r['Category'],AS,TF,tr,p))
out.sort(reverse=True)
print(f"{len(out)} unchecked candidates\n")
for s,d,b,c,A,T,tr,p in out[:30]:
    print(f"{d:33}{b:13}{A:4}{T:4}{tr:10,}{p:8,.0f}  {c[:44]}")
