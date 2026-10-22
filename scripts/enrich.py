import json, sys, csv, io
from urllib.parse import urlparse

rd_file, bl_file = sys.argv[1], sys.argv[2]

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
DSET = set(DOMAINS)

def load_csv(path):
    with open(path) as f:
        j = json.load(f)
    data = j["data"]
    usage = j.get("metadata",{}).get("usage")
    rows = list(csv.reader(io.StringIO(data), delimiter=';'))
    hdr = rows[0]
    return hdr, rows[1:], usage

def regdom(host):
    host = host.lower().lstrip('.')
    if host.startswith('www.'): host = host[4:]
    parts = host.split('.')
    # match against known set by longest suffix
    for d in DSET:
        if host == d or host.endswith('.'+d):
            return d
    return host

# refdomains
rh, rrows, rusage = load_csv(rd_file)
ri = {c:i for i,c in enumerate(rh)}
rd = {}
for r in rrows:
    if len(r) < len(rh): continue
    dom = r[ri['domain']].lower()
    if dom in DSET:
        rd[dom] = {
            'AS': r[ri.get('domain_authority_score', ri.get('domain_score'))],
            'trust': r[ri['domain_trust_score']] if 'domain_trust_score' in ri else '',
            'bl_num': r[ri['backlinks_num']] if 'backlinks_num' in ri else '',
            'first_seen': r[ri['first_seen']] if 'first_seen' in ri else '',
            'ip': r[ri['ip']] if 'ip' in ri else '',
        }

# backlinks
bh, brows, busage = load_csv(bl_file)
bi = {c:i for i,c in enumerate(bh)}
bl = {}
for r in brows:
    if len(r) < len(bh): continue
    host = urlparse(r[bi['source_url']]).netloc
    dom = regdom(host)
    if dom in DSET:
        entry = {
            'nofollow': r[bi['nofollow']] if 'nofollow' in bi else '',
            'target': r[bi['target_url']] if 'target_url' in bi else '',
            'anchor': r[bi['anchor']] if 'anchor' in bi else '',
            'first_seen': r[bi['first_seen']] if 'first_seen' in bi else '',
            'resp': r[bi['response_code']] if 'response_code' in bi else '',
            'src': r[bi['source_url']],
        }
        bl.setdefault(dom, []).append(entry)

print("REFDOMAINS rows total:", len(rrows), "| matched of 56:", len(rd), "| usage:", rusage)
print("BACKLINKS   rows total:", len(brows), "| domains matched:", len(bl), "| usage:", busage)
# date range covered by refdomains pull
fs = [r[ri['first_seen']] for r in rrows if len(r)>=len(rh)]
print("refdomains first_seen range:", min(fs) if fs else None, "->", max(fs) if fs else None)
print()
print("dom | AS | trust | first_seen | #links | nofollow(all?) | targets | resp")
missing_rd=[]; missing_bl=[]
for d in DOMAINS:
    r = rd.get(d); links = bl.get(d, [])
    if not r: missing_rd.append(d)
    if not links: missing_bl.append(d)
    nf = set(l['nofollow'] for l in links)
    tg = set(l['target'].replace('https://www.controlledcomfort.com','').replace('https://controlledcomfort.com','') or '/' for l in links)
    rc = set(l['resp'] for l in links)
    AS = r['AS'] if r else '-'
    tr = r['trust'] if r else '-'
    fsd = (r['first_seen'] if r else (links[0]['first_seen'] if links else '-'))
    print(f"{d} | {AS} | {tr} | {fsd} | {len(links)} | {sorted(nf)} | {sorted(tg)} | {sorted(rc)}")
print()
print("NOT in refdomains pull:", missing_rd)
print("NOT in backlinks pull :", missing_bl)
