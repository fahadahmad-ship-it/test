import csv, io, sys
from collections import Counter
from urllib.parse import urlparse

bl = sys.argv[1]
with io.open(bl,"r",encoding="utf-8") as f:
    rows=list(csv.reader(f,delimiter="\t",quotechar='"'))
h,rows=rows[0],rows[1:]
i={n:k for k,n in enumerate(h)}
A=i["Anchor"]; T=i["Target URL"]; RC=i.get("Redirect Chain URLs"); NF=i["Nofollow"]

def target_prop(r):
    # property the link points at = redirect chain final host if present else target host+path
    t=r[T].strip()
    u=urlparse(t)
    path=u.path or "/"
    host=u.netloc.lower().replace("www.","")
    return host, path

def is_home(path):
    return path in ("","/","/ ") or path.strip("/")==""

spam_sig=["backlink","guest post","pbn","dofollow","da 50","pa 40","link building","buy backlinks",
          "premium authority","authority backlinks","niche edit","darksidelinks","dr/da/tf","seo ","complete seo",
          "search visibility","there was a time when","doubled my leads","automation tools","saas tools","igaming",
          "dedicated account management","white-label","press release links","secured us top","increase in sales"]
def is_spam_anchor(a):
    al=a.lower()
    return any(s in al for s in spam_sig)

home_spam=home_comm=deep_spam=deep_comm=0
tgt_hosts=Counter(); tgt_paths=Counter()
for r in rows:
    if len(r)<=max(A,T,NF): continue
    host,path=target_prop(r)
    tgt_hosts[host]+=1
    tgt_paths[(host,path)]+=1
    sp=is_spam_anchor(r[A])
    if is_home(path):
        if sp: home_spam+=1
        else: home_comm+=1
    else:
        if sp: deep_spam+=1
        else: deep_comm+=1

print("TARGET HOSTS (where links point):", dict(tgt_hosts.most_common(10)))
print("\nHome vs deep x spam vs commercial (link counts):")
print(f"  HOME  page: spam={home_spam:5d}  non-spam={home_comm:5d}")
print(f"  DEEP  page: spam={deep_spam:5d}  non-spam={deep_comm:5d}")
print("\nTop 20 target paths:")
for (host,path),c in tgt_paths.most_common(20):
    print(f"  {c:5d}  {host}{path[:60]}")
