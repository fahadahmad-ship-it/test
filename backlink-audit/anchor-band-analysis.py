import json, sys, csv, re
from urllib.parse import urlparse
from collections import defaultdict

blfile, rdfile = sys.argv[1], sys.argv[2]

# authority score per registrable domain
asc = {}
with open(rdfile, encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f, delimiter=';'):
        try: asc[row['domain'].lower()] = int(row['ascore'])
        except: pass

doms = sorted(asc, key=len, reverse=True)
by_suffix = defaultdict(list)
for d in doms: by_suffix[d.split('.')[-1]].append(d)

def reg(host):
    host = host.lower().lstrip('.')
    if host.startswith('www.'): host = host[4:]
    for d in by_suffix.get(host.split('.')[-1], []):
        if host == d or host.endswith('.' + d): return d
    return host

VENDOR = re.compile(r'backlink|dofollow|pbn|seo link|link building|guest post|niche edit|domain rating|citation flow|trust flow|da 50|t\.me/|telegram|rank first page|buy backlink|white hat|serp|domain authority|outrank|link profile|link placement|outreach', re.I)
SISTER = re.compile(r'^(ngawindows|thermalprowindows|qualitypluswindows|roiwindows|northpointwindows|performingwindows|thermatrustwindows|northgeorgiawindows|thermalastwindows|e2windows|choiceviewwindows|ngwindow|northgawindows|northgeorgiawindow)\.(com|net)$', re.I)
BRAND = re.compile(r'^(https?://)?(www\.)?ngwindows\.com/?.*$|north georgia replacement|^ng windows$', re.I)
GENERIC = re.compile(r'^(visit website|website|view website|site web|visit website →|read more|here|click here|more)$', re.I)
TOPICAL = re.compile(r'window|door|glass|thermopane|patio|siding', re.I)

def bucket(a):
    a = (a or '').strip()
    if not a or a == '<EmptyAnchor>': return 'd_empty_image'
    if VENDOR.search(a): return 'a_vendor_spam'
    if SISTER.match(a): return 'b_sister_domain'
    if BRAND.match(a): return 'c_brand_url'
    if GENERIC.match(a): return 'd_empty_image'
    if TOPICAL.search(a): return 'e_topical'
    return 'f_other'

raw = json.load(open(blfile, encoding='utf-8', errors='replace'))['data']
rows = list(csv.DictReader(raw.splitlines(), delimiter=';'))

# per-link counts by band+bucket+follow, and per-domain bucket sets
link = defaultdict(int)
dom_buckets = defaultdict(set)
dom_follow = defaultdict(set)
for r in rows:
    try: host = urlparse(r['source_url']).netloc
    except: continue
    d = reg(host)
    if d not in asc: continue
    band = 'AS0-5' if asc[d] <= 5 else ('AS6-29' if asc[d] <= 29 else 'AS30+')
    b = bucket(r.get('anchor'))
    nf = str(r.get('nofollow','')).lower() == 'true'
    link[(band, b, 'nofollow' if nf else 'dofollow')] += 1
    if band == 'AS0-5':
        dom_buckets[d].add(b)
        dom_follow[d].add('nofollow' if nf else 'dofollow')

print(f"links parsed: {len(rows)}  matched to a scored domain: {sum(link.values())}")
print(f"distinct AS0-5 domains in sample: {len(dom_buckets)}\n")

print("=== LINK-LEVEL: anchor bucket x authority band x follow ===")
buckets = ['a_vendor_spam','b_sister_domain','c_brand_url','d_empty_image','e_topical','f_other']
print(f"{'bucket':<18}{'AS0-5 df':>10}{'AS0-5 nf':>10}{'AS6-29':>9}{'AS30+':>8}")
for b in buckets:
    print(f"{b:<18}{link[('AS0-5',b,'dofollow')]:>10}{link[('AS0-5',b,'nofollow')]:>10}"
          f"{link[('AS6-29',b,'dofollow')]+link[('AS6-29',b,'nofollow')]:>9}"
          f"{link[('AS30+',b,'dofollow')]+link[('AS30+',b,'nofollow')]:>8}")

print("\n=== DOMAIN-LEVEL: AS0-5 domains classified by worst anchor seen ===")
prio = ['a_vendor_spam','b_sister_domain','f_other','e_topical','c_brand_url','d_empty_image']
dcount = defaultdict(int); dfollow = defaultdict(int)
for d, bs in dom_buckets.items():
    w = next(b for b in prio if b in bs)
    dcount[w] += 1
    if 'dofollow' in dom_follow[d]: dfollow[w] += 1
tot = len(dom_buckets)
for b in prio:
    if dcount[b]:
        print(f"{b:<18}{dcount[b]:>5} domains ({100*dcount[b]/tot:>5.1f}%)   of which dofollow: {dfollow[b]}")

print("\n=== SAMPLE: AS0-5 domains whose ONLY anchors are benign (DO NOT DISAVOW) ===")
benign = [d for d,bs in dom_buckets.items() if not (bs & {'a_vendor_spam'})]
print(f"count: {len(benign)} of {tot} AS0-5 domains ({100*len(benign)/tot:.1f}%)")
print("examples:", ', '.join(sorted(benign)[:25]))
