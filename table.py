import csv
rows={r['Domain']:r for r in csv.DictReader(open('nangwizard-reachgorilla-shortlist.csv'))}
PICKS=[
 ("AU / NZ",["scoop.co.nz","canberratimes.com.au","nzherald.co.nz","stuff.co.nz","newcastleherald.com.au",
   "illawarramercury.com.au","examiner.com.au","theadvocate.com.au","odt.co.nz","starobserver.com.au",
   "racingandsports.com.au","photoreview.com.au","theleader.com.au","hotcopper.com.au"]),
 ("Food & Drink",["cheese.com","visitdevon.co.uk","anyworkanywhere.com","miaminewtimes.com","phoenixnewtimes.com",
   "dallasobserver.com","washingtoncitypaper.com","ocregister.com","sandiegouniontribune.com","chowhound.com",
   "foodrepublic.com","thedailymeal.com","supermarketnews.com","mspmag.com","tastingtable.com"]),
 ("Home / Family / Events",["finegardening.com","hometips.com","nethouseprices.com","cafemom.com","countrylife.co.uk",
   "crosswalk.com","holisticmoms.org","askthebuilder.com","catalogs.com","theargus.co.uk","bournemouthecho.co.uk",
   "sfweekly.com","eastbayexpress.com"]),
 ("Best value (<$80)",["dorsetecho.co.uk","thesoulofseoul.net","milomagazine.co.uk","nomadlawyer.org","trendingus.com",
   "iharare.com","buddymagazine.org","thegooddogguide.com","fsiblog.co.uk","uploadarticle.com"]),
]
print("| Site | Bucket | AS | TF | CF | Traffic | RD | Price $ |")
print("|---|---|---:|---:|---:|---:|---:|---:|")
for b,ds in PICKS:
    for d in ds:
        r=rows.get(d)
        if not r: print(f"| {d} | {b} | - | - | - | - | - | MISSING |"); continue
        print(f"| {d} | {b} | {r['AS']} | {r['TF']} | {r['CF']} | {int(r['Traffic']):,} | {int(r['RD']):,} | {float(r['Price_USD']):,.0f} |")
