import sys, json, collections, re
import openpyxl

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=True)

def sheet(name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    header = [("" if c is None else str(c)).strip() for c in rows[0]]
    data = []
    for r in rows[1:]:
        if all(c is None or str(c).strip()=="" for c in r):
            continue
        data.append({header[i] if i < len(header) else f"col{i}": r[i] for i in range(len(r))})
    return header, data

out = {}

# ---- Summary ----
ws = wb['Summary']
summ = [[("" if c is None else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]
print("===== SUMMARY (raw) =====")
for r in summ:
    if any(x.strip() for x in r):
        print(" | ".join(x for x in r))

# ---- Referring Domain Audit ----
h, rda = sheet('Referring Domain Audit')
print("\n===== REFERRING DOMAIN AUDIT =====")
print("header:", h)
print("rows:", len(rda))

def num(v):
    try: return float(v)
    except: return None

status_c = collections.Counter(str(d.get('Status')) for d in rda)
print("\nStatus distribution:")
for k,v in status_c.most_common():
    print(f"  {k}: {v}")

# In Disavow vs Status
indis = collections.Counter((str(d.get('Status')), str(d.get('In Disavow'))) for d in rda)
print("\n(Status, In Disavow) pairs:")
for k,v in sorted(indis.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# AS distribution by status
print("\nAS stats by status:")
by_status = collections.defaultdict(list)
for d in rda:
    a = num(d.get('AS'))
    by_status[str(d.get('Status'))].append(a if a is not None else -1)
for st, arr in by_status.items():
    vals = [a for a in arr if a>=0]
    if vals:
        print(f"  {st}: n={len(arr)} AS min={min(vals)} max={max(vals)} mean={sum(vals)/len(vals):.2f}")

# Potential false positives: Spam/Disavow with high AS or traffic
print("\nSpam(Disavow) domains with AS >= 20 (potential false positives):")
fp = [(d.get('Domain'), num(d.get('AS')), d.get('Backlinks'), d.get('Traffic'), d.get('Dofollow Links'), d.get('Nofollow Links'), str(d.get('Top Anchor Text'))[:40]) for d in rda if str(d.get('Status')).startswith('Spam') and (num(d.get('AS')) or 0) >= 20]
fp.sort(key=lambda x: -(x[1] or 0))
for row in fp[:40]:
    print("  ", row)
print("  count AS>=20 in spam:", len(fp))

# Nofollow-only domains that are in disavow (pointless to disavow)
nofollow_in_disavow = [d for d in rda if str(d.get('In Disavow'))=='Yes' and num(d.get('Dofollow Links'))==0 and (num(d.get('Nofollow Links')) or 0)>0]
print("\nDomains In Disavow=Yes but 0 dofollow / >0 nofollow (disavow has no effect):", len(nofollow_in_disavow))
for d in nofollow_in_disavow[:15]:
    print("   ", d.get('Domain'), "AS", d.get('AS'), "nofollow", d.get('Nofollow Links'), str(d.get('Top Anchor Text'))[:30])

# IP / subnet clustering
ipc = collections.Counter()
subnet16 = collections.Counter()
subnetC = collections.Counter()
noip = 0
for d in rda:
    ip = d.get('IP')
    if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', str(ip)):
        parts = str(ip).split('.')
        subnet16[".".join(parts[:2])]+=1
        subnetC[".".join(parts[:3])]+=1
        ipc[str(ip)]+=1
    else:
        noip+=1
print("\nTop /16 subnets across ALL referring domains:")
for k,v in subnet16.most_common(12):
    print(f"  {k}.x.x : {v}")
print("domains w/o usable IP:", noip)

# Backlinks concentration
bl = [(d.get('Domain'), num(d.get('Backlinks')) or 0, str(d.get('Status')), str(d.get('Top Anchor Text'))[:45]) for d in rda]
bl.sort(key=lambda x:-x[1])
print("\nTop 10 domains by backlink count:")
for row in bl[:10]:
    print("  ", row)

# First seen distribution (year-month)
ym = collections.Counter()
for d in rda:
    fs = str(d.get('First Seen'))
    m = re.match(r'(\d{4})-(\d{2})', fs)
    if m: ym[m.group(1)+"-"+m.group(2)]+=1
print("\nFirst-seen by month (top 15):")
for k,v in sorted(ym.items()):
    pass
for k,v in ym.most_common(15):
    print(f"  {k}: {v}")

# ---- All Backlinks ----
h2, allbl = sheet('All Backlinks')
print("\n===== ALL BACKLINKS =====")
print("header:", h2, "rows:", len(allbl))
lt = collections.Counter(str(d.get('Link Type')) for d in allbl)
at = collections.Counter(str(d.get('Anchor Type')) for d in allbl)
tool = collections.Counter(str(d.get('Tool')) for d in allbl)
st2 = collections.Counter(str(d.get('Status')) for d in allbl)
print("Link Type:", dict(lt))
print("Tool:", dict(tool))
print("Status:", dict(st2))
print("Anchor Type (top):")
for k,v in at.most_common(12):
    print(f"  {k}: {v}")
# target URL distribution
tgt = collections.Counter()
for d in allbl:
    u = str(d.get('Target URL') or '')
    u = u.split('?')[0]
    tgt[u]+=1
print("Top target URLs:")
for k,v in tgt.most_common(12):
    print(f"  {v}: {k[:70]}")
# domain concentration in all backlinks
rdc = collections.Counter(str(d.get('Referring Domain')) for d in allbl)
print("Top referring domains by backlink rows:")
for k,v in rdc.most_common(8):
    print(f"  {v}: {k}")

# ---- Anchor Analysis ----
h3, anc = sheet('Anchor Analysis')
print("\n===== ANCHOR ANALYSIS =====  rows:", len(anc))
for d in anc[:15]:
    print(f"  [{d.get('Anchor Type')}] bl={d.get('Backlinks')} rd={d.get('Referring Domains')} spamRD={d.get('Spam Domains Using It')} :: {str(d.get('Anchor Text'))[:45]}")

# ---- Exact Match Anchors ----
h4, ema = sheet('Exact Match Anchors')
print("\n===== EXACT MATCH ANCHORS =====  rows:", len(ema))
print("header:", h4)
conf = collections.Counter(str(d.get('Partner confirmed? (Y/N)')) for d in ema)
dec = collections.Counter(str(d.get('Final decision')) for d in ema)
mkt = collections.Counter(str(d.get('Market')) for d in ema)
print("Partner confirmed values:", dict(conf))
print("Final decision values:", dict(dec))
print("Market distribution:", dict(mkt))

# ---- Pending Disavow Lines ----
h5, pend = sheet('Pending Disavow Lines')
print("\n===== PENDING DISAVOW LINES =====  rows:", len(pend))
print("sample recommendation:", str(pend[0].get('Recommendation'))[:120] if pend else None)

# ---- Disavow List ----
h6, dis = sheet('Disavow List')
print("\n===== DISAVOW LIST =====  rows:", len(dis))
lines = [str(d.get('Disavow Line') or '').strip() for d in dis]
bad = [l for l in lines if l and not (l.startswith('domain:') or l.startswith('http'))]
dom_lines = [l for l in lines if l.startswith('domain:')]
url_lines = [l for l in lines if l.startswith('http')]
dups = [k for k,v in collections.Counter(lines).items() if v>1 and k]
print("domain: lines:", len(dom_lines), "| url lines:", len(url_lines), "| malformed:", len(bad), "| duplicate lines:", len(dups))
if bad[:10]: print("malformed sample:", bad[:10])
if dups[:10]: print("dup sample:", dups[:10])

# overlap between disavow list domains and pending
dis_domains = set(l.split('domain:')[1].strip().lower() for l in dom_lines if 'domain:' in l)
pend_domains = set(str(d.get('Referring domain') or '').strip().lower() for d in pend)
overlap = dis_domains & pend_domains
print("Disavow-list domains:", len(dis_domains), "| Pending domains:", len(pend_domains), "| OVERLAP (in both):", len(overlap))
if overlap: print("overlap sample:", list(overlap)[:10])

# cross-check: every RDA domain with In Disavow=Yes present in Disavow List?
rda_yes = set(str(d.get('Domain') or '').strip().lower() for d in rda if str(d.get('In Disavow'))=='Yes')
missing = rda_yes - dis_domains
print("RDA In-Disavow=Yes:", len(rda_yes), "| missing from Disavow List:", len(missing))
if missing: print("missing sample:", list(missing)[:10])

print("\nDONE")
