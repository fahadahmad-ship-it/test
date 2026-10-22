import json, csv, re
from collections import defaultdict
with open("/home/user/test/audit/data/classified_domains.json", encoding="utf-8") as f:
    dom = json.load(f)
links=[]
with open("/home/user/test/audit/data/classified_links.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f): links.append(r)
dlinks=defaultdict(list)
for r in links: dlinks[r["referring_domain"]].append(r)

# Broad spam-copy keywords (visible sales/PBN/porn/pharma/casino copy)
KW = re.compile(r"(buy|sell|cheap|aged domain|back ?link|dofollow|pbn|guest post|"
    r"domain authority|domain rating|rank(ing)?|serp|citation flow|trust flow|"
    r"link building|link profile|outrank|casino|slot|poker|viagra|cialis|pharma|"
    r"escort|porn|\bsex\b|replica|payday|loan|forex|crypto|bitcoin)", re.I)

keepheld = {k:v for k,v in dom.items() if v.get("status","").startswith(("Keep","Held"))}
print("Keep/Held domains with a DOFOLLOW link whose anchor/title shows spam copy:")
seen=set()
for d,v in keepheld.items():
    for r in dlinks.get(d,[]):
        nf=str(r.get("nofollow","")).strip().lower()
        isdo = nf in ("false","0","","no")
        if not isdo: continue
        txt=(r.get("anchor","")+" || "+r.get("title",""))
        if KW.search(txt) and KW.search(r.get("title","")+r.get("anchor","")):
            # require a clear sales phrase, not just 'ranking'/'link' alone in benign ctx
            if re.search(r"(buy|sell|cheap|aged domain|back ?link|dofollow|pbn|guest post|domain authority|domain rating|outrank|link building|casino|slot|poker|viagra|cialis|pharma|escort|porn|replica|payday|forex|crypto)", txt, re.I):
                if d not in seen:
                    seen.add(d)
                    print(" *", d, "| status:", v["status"], "| title:", repr(r.get("title"))[:100])
print("\nTotal distinct dofollow-spam Keep/Held domains:", len(seen))
