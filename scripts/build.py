import csv, sys, collections, re, json
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2])
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
drmap={r['Domain'].lower():r['DR'] for r in rdm}
cand=[r for r in bl if r['Is spam']=='true' and r['Nofollow']=='false']
byd=collections.defaultdict(list)
for r in cand: byd[r['_h']].append(r)
FP={'brandfetch.com','prospeo.io','clientsbee.com','prosgrade.com','missfrugalmommy.com',
    'hghomeclub.com','100xrecruiting.com','nearmelisting.com','struvia.co','robuta.com'}
def tier(h,rows):
    a=' '.join(r['Anchor'] for r in rows); t=' '.join(r['Referring page title'] for r in rows)
    u=' '.join(r['Referring page URL'] for r in rows)
    if 'quality-authority-backlinks-148096' in u: return 'T1'
    if 'Premium PBN Network Service' in a: return 'T2'
    if 'Trusted High DA Backlinks for ngwindows.com' in a: return 'T3'
    if 'aged domains and backlinks' in t.lower() or 'Top Domains' in t: return 'T4'
    if h=='whosmypro.com': return 'T5'
    if h=='homeownerideas.com': return 'T5'
    return 'X'
res=collections.defaultdict(list)
for h,rows in sorted(byd.items()):
    if h in FP: res['FP'].append((h,rows)); continue
    res[tier(h,rows)].append((h,rows))
for k in ['T1','T2','T3','T4','T5','X','FP']:
    print(f"{k}: {len(res[k])} domains, {sum(len(r) for _,r in res[k])} links")
print("\nX (unclassified, excluded):")
for h,rows in res['X']: print(f"   {h} DR={drmap.get(h)} | {rows[0]['Anchor'][:60]!r} | {rows[0]['Referring page title'][:70]}")
print("\nT4:"); [print(f"   {h} DR={drmap.get(h)} n={len(r)} | {r[0]['Referring page title'][:70]}") for h,r in res['T4']]
# high DR spam within kept tiers
kept=[(h,rows,k) for k in ['T1','T2','T3','T4','T5'] for h,rows in res[k]]
print(f"\nTOTAL KEPT (Ahrefs side): {len(kept)} domains")
hi=[(h,rows,k) for h,rows,k in kept if float(drmap.get(h,0) or 0)>=30]
print(f"\n=== HIGH-DR (>=30) kept: {len(hi)} ===")
for h,rows,k in sorted(hi,key=lambda x:-float(drmap.get(x[0],0) or 0)):
    r=rows[0]
    print(f"  DR={drmap.get(h):>5} {k} {h:34s} n={len(rows)} | A={r['Anchor'][:70]!r}")
    print(f"        url={r['Referring page URL'][:115]}")
json.dump({k:[h for h,_ in v] for k,v in res.items()}, open('/home/user/test/backlink-audit/work-v2/tiers.json','w'), indent=0)
# dump evidence per domain
ev={}
for h,rows,k in kept:
    r=rows[0]
    ev[h]=dict(tier=k,dr=drmap.get(h,''),n=len(rows),anchor=r['Anchor'],url=r['Referring page URL'],
               title=r['Referring page title'],ptype=r['Page type'])
json.dump(ev, open('/home/user/test/backlink-audit/work-v2/evidence.json','w'), indent=0)
