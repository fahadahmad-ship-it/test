import sys, csv, io
from urllib.parse import urlparse
rd_path, bl_path = sys.argv[1], sys.argv[2]
def rows(path):
    raw=open(path,'rb').read().decode('utf-16')
    return list(csv.reader(io.StringIO(raw), delimiter='\t'))
rd=rows(rd_path); rh=rd[0]; ri={c.strip():i for i,c in enumerate(rh)}; rd=rd[1:]
bl=rows(bl_path); bh=bl[0]; bi={c.strip():i for i,c in enumerate(bh)}; bl=bl[1:]

def fnum(x):
    try: return float(x)
    except: return 0.0

# refdomain level
tot=len(rd)
dr_ge20=[]; dr_10_20=[]; spam=0; zerotraf=0
for r in rd:
    if len(r)<len(rh): continue
    dom=r[ri['Domain']]; dr=fnum(r[ri['DR']]); tr=r[ri['Traffic']].strip()
    if r[ri['Is spam']].lower()=='true': spam+=1
    if tr in ('0',''): zerotraf+=1
    if dr>=20: dr_ge20.append((dom,r[ri['DR']],tr,r[ri['Is spam']]))
    elif dr>=10: dr_10_20.append((dom,r[ri['DR']]))

print(f"TOTAL referring domains (Ahrefs): {tot}")
print(f"Ahrefs 'Is spam'=true: {spam} ({100*spam//tot}%)")
print(f"zero organic traffic : {zerotraf} ({100*zerotraf//tot}%)")
print(f"DR>=20 (potential genuine/Keep): {len(dr_ge20)}")
print(f"DR 10-19.9: {len(dr_10_20)}")
print()
print("--- DR>=20 domains (candidate KEEP — review, do NOT disavow) ---")
for d in sorted(dr_ge20, key=lambda x:-fnum(x[1])):
    print(f"  {d[0]}  DR={d[1]}  traffic={d[2]}  isspam={d[3]}")

# backlink level: targets + anchors
EMC_WORDS=('furnace','hvac','air conditioner','air conditioning','ac repair','heating','cooling','furnance')
deep=0; home=0; other=0; emc=0; dofollow=0; total_bl=len(bl); live=0
tgtcount={}
refdom_targets={}
for r in bl:
    if len(r)<len(bh): continue
    t=r[bi['Target URL']]
    tl=t.lower()
    key='deep' if '/services/' in tl else ('home' if tl.rstrip('/').endswith('controlledcomfort.com') else 'other')
    if key=='deep': deep+=1
    elif key=='home': home+=1
    else: other+=1
    a=r[bi['Anchor']].lower()
    if any(w in a for w in EMC_WORDS): emc+=1
    nf=(r[bi['Nofollow']].lower()=='true' or r[bi['UGC']].lower()=='true' or r[bi['Sponsored']].lower()=='true')
    if not nf: dofollow+=1
    if r[bi['Referring page HTTP code']]=='200': live+=1
    host=urlparse(r[bi['Referring page URL']]).netloc.lower().replace('www.','')
    refdom_targets.setdefault(host, set()).add(key)

print()
print(f"TOTAL backlinks: {total_bl} | dofollow: {dofollow} | live(200): {live}")
print(f"target: deep /services/ pages: {deep} | home: {home} | other: {other}")
print(f"anchors containing HVAC/furnace/AC/heating/cooling terms: {emc} ({100*emc//total_bl}%)")

# how many refdomains point ONLY at deep pages (commissioned-signal), vs only home, vs mixed
onlydeep=sum(1 for h,s in refdom_targets.items() if s=={'deep'})
onlyhome=sum(1 for h,s in refdom_targets.items() if s=={'home'})
print(f"referring hosts pointing ONLY at deep /services pages: {onlydeep}")
print(f"referring hosts pointing ONLY at home: {onlyhome}")
