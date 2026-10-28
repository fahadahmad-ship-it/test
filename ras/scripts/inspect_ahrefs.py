import sys, csv
from collections import Counter
from urllib.parse import urlsplit

bl_path, rd_path = sys.argv[1], sys.argv[2]

def host(u):
    try:
        h = urlsplit(u).netloc.lower()
        if h.startswith('www.'): h = h[4:]
        return h
    except Exception:
        return ''

# Backlinks
with open(bl_path, encoding='utf-8') as f:
    r = csv.DictReader(f, delimiter='\t')
    rows = list(r)
print("BACKLINKS rows:", len(rows))
print("cols:", r.fieldnames)
# target hosts
tgt = Counter(host(x['Target URL']) for x in rows)
print("\nTarget URL hosts:", tgt.most_common(15))
# target path home vs deep
def is_home(u):
    p = urlsplit(u).path
    return p in ('', '/')
home = sum(1 for x in rows if is_home(x['Target URL']))
print(f"\nTarget is homepage: {home} / {len(rows)} ({home/len(rows)*100:.1f}%)")
# redirect chain presence
rc = sum(1 for x in rows if x.get('Redirect Chain URLs','').strip())
print("rows with Redirect Chain URLs:", rc)
# http codes
print("\nHTTP codes:", Counter(x['Referring page HTTP code'] for x in rows).most_common(10))
print("Is spam:", Counter(x['Is spam'] for x in rows).most_common())
print("Nofollow:", Counter(x['Nofollow'] for x in rows).most_common())
print("Type:", Counter(x['Type'] for x in rows).most_common())
print("Lost:", Counter(x.get('Lost','') for x in rows).most_common())
# sample anchors
print("\nTop anchors:")
for a,c in Counter(x['Anchor'] for x in rows).most_common(20):
    print(f"  [{c}] {a[:90]!r}")
# sample redirect chains that are non-empty
print("\nSample redirect chains:")
n=0
for x in rows:
    if x.get('Redirect Chain URLs','').strip():
        print("  tgt=",x['Target URL'][:60],"| chain=",x['Redirect Chain URLs'][:120])
        n+=1
        if n>=8: break

# Refdomains
print("\n"+"="*60)
with open(rd_path, encoding='utf-8') as f:
    r2 = csv.DictReader(f, delimiter='\t')
    rds = list(r2)
print("REFDOMAINS rows:", len(rds))
print("cols:", r2.fieldnames)
print("Is spam:", Counter(x['Is spam'] for x in rds).most_common())
# traffic/keywords distribution
def num(x):
    x=(x or '').strip().replace(',','')
    try: return float(x)
    except: return 0.0
zero_traf = sum(1 for x in rds if num(x.get('Traffic ',x.get('Traffic','')))==0)
print(f"refdomains with 0 traffic: {zero_traf}/{len(rds)}")
print("sample rd rows:")
for x in rds[:5]:
    print("  ", {k:x[k] for k in list(x)[:9]})
