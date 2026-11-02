import glob, collections, sys
sys.path.insert(0, "/home/user/test/ritter/scripts")
from load import read_semrush_csv, host_of, path_of, canon_domain

bl, rej, hdr = read_semrush_csv(sorted(glob.glob("/home/user/test/ritter/data/fetch/backlinks_p*.csv")), 10)
print(f"TOTAL LINKS={len(bl)}  rejects={len(rej)}")

# nofollow distribution
nf = collections.Counter(r["nofollow"] for r in bl)
print("nofollow values:", dict(nf))

# response codes
rc = collections.Counter(r["response_code"] for r in bl)
print("response_code top:", rc.most_common(10))

# redirect_url present?
redir = sum(1 for r in bl if r.get("redirect_url", "").strip())
print("links with redirect_url set:", redir)

# target host + home vs deep
thost = collections.Counter(host_of(r["target_url"]) for r in bl)
print("target hosts:", thost.most_common(8))
paths = collections.Counter(path_of(r["target_url"]) for r in bl)
print("\nTOP TARGET PATHS (home vs deep):")
for p, c in paths.most_common(25):
    print(f"  {c:5d}  {p}")

home = sum(c for p, c in paths.items() if p in ("/", "", "/index.html", "/home", "/index.php"))
deep = len(bl) - home
print(f"\nHOME-page links={home}  DEEP-page links={deep}")

# unique referring domains in backlinks
rdset = set(canon_domain(host_of(r["source_url"])) for r in bl)
print("unique referring hosts in backlinks:", len(rdset))

# page_ascore distribution of source pages
print("\nsample source titles (first 12 distinct):")
seen = set()
for r in bl:
    t = r["source_title"][:70]
    if t not in seen:
        seen.add(t)
        print("   ", repr(t))
    if len(seen) >= 12:
        break
