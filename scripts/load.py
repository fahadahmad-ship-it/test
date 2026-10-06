import csv, sys, collections, re
BL, RD = sys.argv[1], sys.argv[2]
def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quotechar='"'))
bl = rd(BL); rdom = rd(RD)
print("backlinks rows", len(bl), "refdom rows", len(rdom))
print("BL cols:", list(bl[0].keys()))
print("RD cols:", list(rdom[0].keys()))
c=collections.Counter((r['Is spam'], r['Nofollow']) for r in bl)
print("BL (isspam,nofollow):", c)
print("RD isspam:", collections.Counter(r['Is spam'] for r in rdom))
# candidate
cand=[r for r in bl if r['Is spam']=='true' and r['Nofollow']=='false']
print("cand links", len(cand))
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
dom=collections.Counter(host(r['Referring page URL']) for r in cand)
print("cand domains", len(dom))
# redirect chains
rc=[r for r in bl if (r['Redirect Chain URLs'] or '').strip()]
print("rows with redirect chain", len(rc))
