import sys, collections
from urllib.parse import urlparse

# Safe Semrush CSV reader: unescape entities, split on ';', reject wrong col count
import html
path = sys.argv[1]
EXPECT = 10
rows = []
bad = 0
with open(path, encoding="utf-8", errors="replace") as fh:
    header = fh.readline().rstrip("\n").split(";")
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split(";")
        if len(parts) != EXPECT:
            bad += 1
            continue
        rows.append(dict(zip(header, parts)))

print("header:", header)
print("rows:", len(rows), "malformed:", bad)

def host(u):
    try:
        h = urlparse(u).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def path_of(u):
    try:
        return urlparse(u).path or "/"
    except Exception:
        return "/"

# target property distribution (home vs deep)
tgt_host = collections.Counter()
home=deep=0
deep_paths = collections.Counter()
redirects = collections.Counter()
nofollow = collections.Counter()
resp = collections.Counter()
anchors = collections.Counter()
deep_anchors = collections.Counter()
first_years = collections.Counter()
for r in rows:
    th = host(r["target_url"]); tgt_host[th]+=1
    p = path_of(r["target_url"])
    if p in ("/","",) :
        home+=1
    else:
        deep+=1
        deep_paths[p]+=1
        deep_anchors[r["anchor"]]+=1
    ru = r.get("redirect_url","").strip()
    if ru:
        redirects[host(ru)]+=1
    nofollow[r["nofollow"]]+=1
    resp[r["response_code"]]+=1
    anchors[r["anchor"]]+=1
    fs = r.get("first_seen","")
    if fs.isdigit():
        import datetime
        first_years[datetime.datetime.utcfromtimestamp(int(fs)).strftime("%Y-%m")] += 1

print("\ntarget hosts:", tgt_host.most_common(8))
print("HOME vs DEEP:", {"home":home,"deep":deep})
print("\nredirect_url hosts (owned/redirect domains?):", redirects.most_common(20))
print("\nnofollow:", dict(nofollow))
print("response_code:", dict(resp.most_common(8)))
print("\nTOP 25 anchors overall:")
for a,c in anchors.most_common(25):
    print(f"  {c:5d}  {a[:90]!r}")
print("\nTOP 30 DEEP-PAGE anchors (exact-match commercial candidates):")
for a,c in deep_anchors.most_common(30):
    print(f"  {c:5d}  {a[:70]!r}")
print("\nTOP 20 deep paths:")
for p,c in deep_paths.most_common(20):
    print(f"  {c:5d}  {p[:70]}")
print("\nfirst_seen by month (backlinks):")
for m,c in sorted(first_years.items()):
    print(f"  {m}: {c}")
