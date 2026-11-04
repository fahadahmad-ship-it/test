import glob
import collections
import sys
sys.path.insert(0, "erth/scripts")
from load import load_backlinks, host_of, registrable

bl, meta = load_backlinks(sorted(glob.glob("erth/data/fetch/bl_p*.csv")))
print("total backlinks:", len(bl))

# target page distribution: home vs deep
home = 0
deep = 0
deep_paths = collections.Counter()
for r in bl:
    t = r["target_url"]
    # strip to path
    from urllib.parse import urlsplit
    pth = urlsplit(t if "//" in t else "http://" + t).path.rstrip("/")
    if pth in ("", "/"):
        home += 1
    else:
        deep += 1
        deep_paths[pth] += 1
print("links to HOME page:", home, "| links to DEEP page:", deep)
print("\ntop 25 deep target paths:")
for p, c in deep_paths.most_common(25):
    print(f"  {c:4d}  {p}")

# nofollow distribution
nf = collections.Counter(r["nofollow"] for r in bl)
print("\nnofollow flag distribution:", dict(nf))

# referring host universe
hosts = collections.Counter(host_of(r["source_url"]) for r in bl)
roots = collections.Counter(registrable(host_of(r["source_url"])) for r in bl)
print("\ndistinct referring hosts:", len(hosts), "| distinct registrable roots:", len(roots))

# anchors (lowercased) top
anch = collections.Counter(r["anchor"].strip().lower() for r in bl)
print("\ntop 30 anchors:")
for a, c in anch.most_common(30):
    print(f"  {c:4d}  {a[:95]}")

# TLD distribution of referring hosts
tld = collections.Counter(h.rsplit(".", 1)[-1] for h in hosts if "." in h)
print("\ntop referring TLDs:", tld.most_common(25))

# response codes
rc = collections.Counter(r["response_code"] for r in bl)
print("\nresponse codes:", rc.most_common())
