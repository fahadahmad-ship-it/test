import sys, collections
sys.path.insert(0, "erth/scripts")
import pipeline as P
import classify as C
from load import host_of

canon, links, by = P.run()
print("canon:", len(canon), "links:", len(links), "domains:", len(by))
print("source:", dict(collections.Counter(d["source"] for d in by.values())))
for k, v in collections.Counter(d["status"] for d in by.values()).most_common():
    print(f"  {v:5d}  {k}")

def sample_link(d):
    if not d["links"]:
        return ("", "", "")
    r = d["links"][0]
    return r["anchor"][:58], (r["title"] or "")[:52], r["target"]

print("\n================= KEEP (%d) =================" % sum(1 for d in by.values() if d["status"]=="Keep"))
for dom, d in sorted(by.items()):
    if d["status"] == "Keep":
        a,t,tg = sample_link(d)
        print(f"AS{d['ascore']:>3} {dom[:32]:32}|{d['evidence'][:26]:26}| a='{a}' t='{t}'")

print("\n===== POSSIBLE FALSE NEGATIVES: Keep/Held with a dofollow PBN anchor/title =====")
fn=0
for dom,d in by.items():
    if d["status"].startswith(("Keep","Held")):
        for r in d["links"]:
            if C.is_pbn(r["anchor"],r["title"],r["url_from"]) and not r["nofollow"]:
                fn+=1
                print(f"{d['status'][:13]:13} {dom[:28]:28} a='{r['anchor'][:50]}' t='{r['title'][:34]}'")
                break
print("FN candidates:", fn)
