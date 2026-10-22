import sys, csv, io, json
from urllib.parse import urlparse

rd_path, bl_path = sys.argv[1], sys.argv[2]

DOMAINS = ["listique.org","topbizdir.com","zynatee.com","theinfosynth.com","onepluslisting.com",
"true-listings.com","lookuplists.com","getdirectory.org","localstudio.info","honestdir.com",
"localbusinessfinder.co","listingcenter.org","thelistingmatrix.com","directoryology.com","myreallistings.com",
"selectbusinesszone.com","thedirectopia.com","ackoona.org","listingsspot.com","premiuminc.org",
"businesslistingforall.com","5starlocalcenter.com","bestlocalcenter.com","ideal-listings.com","ultimatesites.info",
"thelistingcloud.net","directoryninja.org","weblistings.info","yourpremium.org","godigitalbusinesshub.com",
"directorycentered.com","findbusinesses.org","rozzbee.com","busineessupdir.com","topincitylocal.com",
"probusinessworld.com","findlocalcenter.com","getzzby.com","businessinfoseek.com","a-zbusinesses.com",
"easybusinessdirect.com","woorivo.com","localbusinessesdir.com","showmelocalpro.com","localbusinessguide.org",
"populardirectory.co","directorist.net","snapsearch.org","seekbump.org","yellowmarketplaces.com",
"directoryview.com","localdirectory247.com","atozweb.org","localpagesdirectory.com","searchknock.com",
"getlistedahead.com"]
DSET=set(DOMAINS)

def rows(path):
    raw=open(path,'rb').read().decode('utf-16')
    r=csv.reader(io.StringIO(raw), delimiter='\t')
    data=list(r); return data[0],data[1:]

def regdom(host):
    host=host.lower().lstrip('.')
    if host.startswith('www.'): host=host[4:]
    for d in DSET:
        if host==d or host.endswith('.'+d): return d
    return host

rh,rrows=rows(rd_path); ri={c.strip():i for i,c in enumerate(rh)}
bh,brows=rows(bl_path); bi={c.strip():i for i,c in enumerate(bh)}

# refdomains index
RD={}
for r in rrows:
    if len(r)<len(rh): continue
    dom=r[ri['Domain']].lower()
    RD[dom]={'DR':r[ri['DR']],'spam':r[ri['Is spam']],'traffic':r[ri['Traffic']],
             'kw':r[ri['Keywords']],'links':r[ri['Links to target']],'dofollow':r[ri['Dofollow links']],
             'first':r[ri['First seen']],'lost':r[ri['Lost']]}

# backlinks grouped by refdomain
BL={}
for r in brows:
    if len(r)<len(bh): continue
    host=urlparse(r[bi['Referring page URL']]).netloc
    dom=regdom(host)
    BL.setdefault(dom,[]).append({
        'src':r[bi['Referring page URL']],'http':r[bi['Referring page HTTP code']],
        'target':r[bi['Target URL']],'anchor':r[bi['Anchor']],'type':r[bi['Type']],
        'nofollow':r[bi['Nofollow']],'ugc':r[bi['UGC']],'spon':r[bi['Sponsored']],
        'spam':r[bi['Is spam']],'first':r[bi['First seen']],'lost':r[bi['Lost']],
        'dr':r[bi['Domain rating']]})

def norm_t(t):
    t=t.replace('https://www.controlledcomfort.com','').replace('https://controlledcomfort.com','')
    t=t.replace('http://www.controlledcomfort.com','').replace('http://controlledcomfort.com','')
    return t or '/'

print("### Per-domain enrichment for the 56 (Ahrefs)")
print("domain | DR | spam | traffic | kw | #bl | dofollow? | nofollow_all? | targets | http | first_seen")
miss_rd=[]; miss_bl=[]; dr_ge20=[]; nofollow_all=[]; has_dofollow=[]; spamflag=[]; zero_traf=[]; lost_all=[]
for d in DOMAINS:
    rd=RD.get(d); links=BL.get(d,[])
    if not rd: miss_rd.append(d)
    if not links: miss_bl.append(d)
    live=[l for l in links if l['lost'] in ('','false','False')]
    nofo=[(l['nofollow'].lower()=='true' or l['ugc'].lower()=='true' or l['spon'].lower()=='true') for l in links]
    dofollow_exists = any(not x for x in nofo) if links else None
    all_nofollow = (len(nofo)>0 and all(nofo))
    tgts=sorted(set(norm_t(l['target']) for l in links))
    https=sorted(set(l['http'] for l in links))
    anchors=sorted(set(l['anchor'] for l in links))
    DR=rd['DR'] if rd else '-'
    sp=rd['spam'] if rd else '-'
    tr=rd['traffic'] if rd else '-'
    kw=rd['kw'] if rd else '-'
    fs=rd['first'] if rd else (links[0]['first'] if links else '-')
    try:
        if rd and int(DR)>=20: dr_ge20.append((d,DR))
    except: pass
    if all_nofollow: nofollow_all.append(d)
    if dofollow_exists: has_dofollow.append(d)
    if rd and sp.lower()=='true': spamflag.append(d)
    if rd and tr.strip() in ('0',''): zero_traf.append(d)
    if links and all(l['lost'] not in ('','false','False') for l in links): lost_all.append(d)
    print(f"{d} | {DR} | {sp} | {tr} | {kw} | {len(links)} | {dofollow_exists} | {all_nofollow} | {tgts} | {https} | {fs}")

print()
print("=== SUMMARY (of 56) ===")
print("in refdomains file:", 56-len(miss_rd), "| missing:", miss_rd)
print("in backlinks file :", 56-len(miss_bl), "| missing:", miss_bl)
print("DR >= 20:", dr_ge20)
print("has >=1 dofollow link:", len(has_dofollow))
print("ALL links nofollow:", len(nofollow_all), nofollow_all)
print("Ahrefs 'Is spam'=true:", len(spamflag))
print("zero organic traffic:", len(zero_traf))
print("all links lost:", len(lost_all), lost_all)

# distinct targets across the 56
alltg={}
for d in DOMAINS:
    for l in BL.get(d,[]):
        alltg[norm_t(l['target'])]=alltg.get(norm_t(l['target']),0)+1
print("target distribution (56 domains' links):", dict(sorted(alltg.items(), key=lambda x:-x[1])))
