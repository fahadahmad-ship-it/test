import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import load_semrush_backlinks, load_ahrefs_refdomains, load_ahrefs_backlinks, host
from rootdom import root_domain
from collections import defaultdict

fetch_dir = sys.argv[1]
ahrefs_rd = sys.argv[2]
ahrefs_bl = sys.argv[3]
outdir = sys.argv[4]

OWNED = {'ras-systems.com','rasmachines.com','ras-systems.net','ras-systems.us'}

sr_rows,_,_ = load_semrush_backlinks(fetch_dir)
sr_domains = set()
for r in sr_rows:
    rd = root_domain(host(r['source_url']))
    if rd and rd not in OWNED:
        sr_domains.add(rd)

ar_rd = load_ahrefs_refdomains(ahrefs_rd)
ar_domains = set()
dkey = None
for x in ar_rd:
    if dkey is None:
        dkey = [k for k in x.keys() if 'Domain' in k][0]
    rd = root_domain(x[dkey])
    if rd and rd not in OWNED:
        ar_domains.add(rd)

# ahrefs backlinks source hosts too
ar_bl = load_ahrefs_backlinks(ahrefs_bl)
abk = None
for x in ar_bl:
    if abk is None:
        abk = [k for k in x.keys() if 'Referring page URL' in k][0]
    rd = root_domain(host(x[abk]))
    if rd and rd not in OWNED:
        ar_domains.add(rd)

alld = sorted(sr_domains | ar_domains)
print("semrush source root-domains:", len(sr_domains))
print("ahrefs root-domains:", len(ar_domains))
print("UNION:", len(alld))
print("ahrefs-only (not in semrush):", len(ar_domains - sr_domains))
print("semrush-only:", len(sr_domains - ar_domains))

os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir,'domains_all.txt'),'w') as f:
    for d in alld:
        f.write(d+'\n')
# provenance
prov = {d: ('both' if d in sr_domains and d in ar_domains else ('Semrush' if d in sr_domains else 'Ahrefs')) for d in alld}
with open(os.path.join(outdir,'domain_source.json'),'w') as f:
    json.dump(prov,f)
print("wrote", len(alld), "domains to", os.path.join(outdir,'domains_all.txt'))
