import sys, csv, re, collections
path=sys.argv[1]
rows=[]
with open(path, encoding='utf-8') as f:
    r=csv.reader(f, delimiter=';')
    hdr=next(r)
    for x in r:
        if len(x)<5: continue
        d,bl,asc,ip,fs=x[0],x[1],x[2],x[3],x[4]
        rows.append((d,int(bl or 0),int(asc or 0),ip,int(fs or 0)))
print("rows",len(rows))
# AS distribution
asc=collections.Counter()
for d,bl,a,ip,fs in rows:
    asc['>=20' if a>=20 else ('10-19' if a>=10 else ('5-9' if a>=5 else '0-4'))]+=1
print("AS buckets", dict(asc))
print("AS>=20 count", sum(1 for r in rows if r[2]>=20))
# high AS domains (potential keep/genuine)
print("\n-- AS>=20 domains (potential Keep) --")
for d,bl,a,ip,fs in sorted(rows,key=lambda x:-x[2]):
    if a>=20: print(f"  {d} AS{a} bl{bl}")
# spam name signatures
sig=re.compile(r'(backlink|seo|dapa|pacheck|dachecker|drcheck|rankcheck|rankchecker|serp|checker|directory|listing|guestpost|guest-post|linkbuild|link-build|nichedit|niche-edit|pbn|domainrating|domainauthority|buybacklink|indexing|index-|bookmark|submit|ranking|rank-|authority|boost-traffic|traffic|casino|poker|slot|gacor|betting|bet-|escort|pharma|viagra|cialis|doxycycline|erythromycin|psilocybin|cannabis|aged-domain|aged_domain|domraider|all-aged|alllevel|topleveldomain|marketplace)', re.I)
cnt=sum(1 for d,bl,a,ip,fs in rows if sig.search(d))
print("\nname-signature spam domains:", cnt)
# IP /24 clustering
nets=collections.Counter()
for d,bl,a,ip,fs in rows:
    if ip and re.match(r'\d+\.\d+\.\d+\.\d+',ip):
        net='.'.join(ip.split('.')[:3])+'.0/24'
        nets[net]+=1
print("\n-- top /24 networks (excl cloudflare 104.21/172.6x) --")
for net,c in nets.most_common(25):
    print(f"  {net}: {c}")
# first_seen month distribution
mon=collections.Counter()
import datetime
for d,bl,a,ip,fs in rows:
    if fs:
        mon[datetime.datetime.utcfromtimestamp(fs).strftime('%Y-%m')]+=1
print("\n-- domains by first_seen month --")
for m in sorted(mon): print(f"  {m}: {mon[m]}")
