import csv
rows=[]
for r in csv.DictReader(open('nangwizard-reachgorilla-shortlist.csv')):
    p=float(r['Price_USD']); AS=int(r['AS']); TF=int(r['TF']); CF=int(r['CF'])
    tr=int(r['Traffic']); rd=int(r['RD'])
    if p>=400: continue
    if AS<30 or TF<22 or tr<8000: continue
    rows.append(dict(d=r['Domain'],b=r['Bucket'],c=r['Category'],AS=AS,TF=TF,CF=CF,tr=tr,rd=rd,p=p,
                     val=(AS+TF)*(tr**0.4)/p))
rows.sort(key=lambda x:-x['val'])
print(f"{len(rows)} sites under $400\n")
print("| Site | Bucket | AS | TF | CF | Traffic | RD | Price $ |")
print("|---|---|---:|---:|---:|---:|---:|---:|")
for x in rows[:45]:
    print(f"| {x['d']} | {x['b']} | {x['AS']} | {x['TF']} | {x['CF']} | {x['tr']:,} | {x['rd']:,} | {x['p']:,.0f} |")
