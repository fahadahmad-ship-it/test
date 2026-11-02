import json, os, re, sys, glob
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from load import parse_backlinks, canon_host

BASE = "/home/user/test/hpp"
doms = json.load(open(BASE+"/out/classified_domains.json"))
links = json.load(open(BASE+"/out/classified_links.json"))
lbd = defaultdict(list)
for l in links: lbd[l["refdomain"]].append(l)

print("==== 1. METRICS COVERAGE / DUPES ====")
def load_kv(path, idx_val=2):
    kv={}; dup=0
    for line in open(path):
        p=line.rstrip("\n").split(";")
        if len(p)<idx_val+1 or p[0]=="target" or p[0]=="domain": continue
        d=canon_host(p[0])
        if d in kv: dup+=1
        kv[d]=p
    return kv,dup
met,metdup = load_kv(BASE+"/data/metrics/metrics.csv")
cmp,cmpdup = load_kv(BASE+"/data/metrics/comparison.csv")
domset=set(doms)
print(f"domains={len(domset)} metrics={len(met)} (dups {metdup}) comparison={len(cmp)} (dups {cmpdup})")
print(f"domains missing metrics: {len(domset-set(met))} -> {list(domset-set(met))[:10]}")
print(f"domains missing comparison: {len(domset-set(cmp))} -> {list(domset-set(cmp))[:10]}")
print(f"metrics domains NOT in domset: {len(set(met)-domset)} -> {list(set(met)-domset)[:10]}")
print(f"comparison domains NOT in domset: {len(set(cmp)-domset)} -> {list(set(cmp)-domset)[:10]}")

print("\n==== 2. DISAVOW DOMAINS WITH HIGH AUTHORITY (false-positive risk) ====")
dis=[d for d in doms if doms[d]["status"]=="Spam (Disavow)"]
def cas(d):
    try: return int(cmp.get(d,["",0])[1])
    except: return 0
hi=sorted([(cas(d),d) for d in dis if cas(d)>=15],reverse=True)
print(f"disavow domains with comparison AS>=15: {len(hi)}")
for a,d in hi[:25]:
    anchors=set(l['anchor_type'] for l in lbd[d])
    print(f"   AS{a:>3} {d:35s} types={sorted(anchors)}")

print("\n==== 3. GENUINE HIGH-AUTHORITY DIRECTORIES — statuses ====")
for d in ["superpages.com","bbb.org","yellowpages.com","birdeye.com","expertise.com","nextdoor.com","chamberofcommerce.com","yahoo.com","ziprecruiter.com","hub.biz","angi.com","yelp.com","mapquest.com","manta.com"]:
    v=doms.get(d)
    print(f"   {d:28s} {v['status'] if v else '(not a referring domain)'}  AS{cas(d)} traffic={met.get(d,['','',''])[2] if d in met else '-'}")

print("\n==== 4. FALSE-NEGATIVE: Keep/Held with ANY dofollow spam-type anchor ====")
leak=[]
for d,v in doms.items():
    if v["status"] in ("Keep","Held (Pending Partner)","Held (Nofollow, No Action)"):
        for l in lbd[d]:
            if l["link_type"]=="Dofollow" and l["anchor_type"] in ("Spam: keyword stuffed SEO sales copy","Spam: off-topic","Spam: messaging-app invitation"):
                leak.append((d,v["status"],l["anchor_type"])); break
print(f"leaks: {len(leak)} -> {leak[:10]}")

print("\n==== 5. RE-DERIVE key counts from scratch ====")
seen=set(); ulinks=[]
rawbl,rej=parse_backlinks(glob.glob(BASE+"/data/fetch/bl_*.csv"))
for r in rawbl:
    k=(r["source_url"].rstrip("/").lower(),r["target_url"].rstrip("/").lower(),r["anchor"])
    if k in seen: continue
    seen.add(k); ulinks.append(r)
print(f"raw unique links={len(ulinks)} (classified links={len(links)})")
tele=set(); wa=set(); xyz=set()
for r in ulinks:
    a=r["anchor"]
    if re.search(r'(join our telegram|our telegram chanel|t\.me/)',a,re.I): tele.add(canon_host(r['source_url']))
    if a.lower().startswith("i will increase your domain"): wa.add(canon_host(r['source_url']))
    if a.lower().startswith('"as a small business owner'): xyz.add(canon_host(r['source_url']))
print(f"telegram hosts={len(tele)} whatsapp hosts={len(wa)} xyz hosts={len(xyz)}")
dofollow_spam_links=sum(1 for l in links if l['status']=='Spam (Disavow)' and l['link_type']=='Dofollow')
print(f"dofollow spam links={dofollow_spam_links}")

print("\n==== 6. SELF-LINK / OWN SITE check ====")
selfhosts=[h for h in doms if h=="highpriorityplumbing.com" or h.endswith(".highpriorityplumbing.com")]
print(f"client-owned source hosts in referring set: {selfhosts}")

print("\n==== 7. NOFOLLOW/DOFOLLOW integrity on clusters ====")
for name,s in [("telegram",tele),("whatsapp",wa),("xyz",xyz)]:
    # map host->refdomain row status via doms (host may have folded)
    statuses=Counter()
    for h in s:
        # find the row: exact or suffix
        row=doms.get(h)
        if not row:
            for d in doms:
                if h.endswith("."+d): row=doms[d]; break
        statuses[row['status'] if row else 'MISSING']+=1
    print(f"   {name}: {dict(statuses)}")
