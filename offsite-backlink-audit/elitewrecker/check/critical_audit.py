#!/usr/bin/env python3
"""Exhaustive, both-directions audit of the disavow decision (playbook s9).
Checks EVERY domain, not a sample. Standard: not a single domain flagged wrong."""
import csv, io, re
from collections import defaultdict, Counter
B="/home/user/test/offsite-backlink-audit/elitewrecker"
doms={r["domain"]:r for r in csv.DictReader(open(B+"/out/domains_classified.csv"))}
links=list(csv.DictReader(open(B+"/out/links_classified.csv")))
L=defaultdict(list)
for l in links: L[l["referring_domain"]].append(l)

def asn(r):
    try: return float(r["as"]) if r["as"] not in ("","None") else None
    except: return None

SPAM_HOST=["backlink","seo","pbn","dofollow","linkbuild","link-build","linkplacement","link-placement",
    "guestpost","guest-post","nicheedit","niche-edit","rankboost","rank-boost","rankpro","linkrank",
    "buybacklinks","authoritylink","dapa","da-pa","dachecker","pachecker","serp","outrank","indexer",
    "trafficbot","linkfarm","darkside","toplink","linkbaron","link-baron","rankforge","rank-forge",
    "domainchecker","domainrating","aged-domain","agedomain","alltopleveldomains","webdirectory",
    "directory","directori","listing","bookmark","submit","rankchecker","checker","smm","index"]
def spam_host(d):
    return any(s in d for s in SPAM_HOST)
SPAM_TITLE=["backlink","pbn","buy backlinks","link building","guest post","dofollow","seo authority",
    "aged domain","premium authority","citation flow","white hat seo","tiered link","make ai recommend",
    "high da","niche edit","rank first","domain rating","da checker","pa checker","authority backlinks",
    "domain list page","where to buy"]
def spam_title(t):
    tl=(t or "").lower()
    return any(s in tl for s in SPAM_TITLE)

def names_client_clean(ls):
    for l in ls:
        tl=(l["linking_page_title"] or "").lower()
        if (("elite" in tl and ("tow" in tl or "wrecker" in tl or "recovery" in tl)) or "elitewrecker" in tl) \
           and not l["anchor_type"].startswith("Spam") and not spam_title(l["linking_page_title"]):
            return True
    return False

dis=[d for d,r in doms.items() if r["status"]=="Spam (Disavow)"]

# ---------- DIRECTION A: every disavow must have visible evidence ----------
ev_counter=Counter(); no_evidence=[]; citation_risk=[]
for d in dis:
    ls=L[d]
    e_anchor=any(l["anchor_type"].startswith("Spam") for l in ls)
    e_offtopic=any(l["anchor_type"]=="Spam: off topic" for l in ls)
    e_title=any(spam_title(l["linking_page_title"]) for l in ls)
    e_host=spam_host(d)
    tags=[]
    if e_anchor: tags.append("anchor")
    if e_offtopic: tags.append("offtopic")
    if e_title: tags.append("title")
    if e_host: tags.append("host")
    ev_counter[",".join(tags) or "NONE"]+=1
    if not tags: no_evidence.append(d)
    # genuine-citation risk: a title names the client cleanly AND no spam anchor on the domain
    if not e_anchor and not e_title and names_client_clean(ls):
        citation_risk.append(d)

print("=== DIRECTION A: false positives (wrong ones IN the disavow) ===")
print(f"disavow domains: {len(dis)}")
print("evidence breakdown (a domain can hold several):")
for k,v in ev_counter.most_common(): print(f"   {v:5d}  {k}")
print(f"\n[A1] disavow domains with NO visible evidence (anchor/title/host/offtopic): {len(no_evidence)}")
for d in no_evidence[:40]:
    r=doms[d]; print(f"      {d}  AS={r['as']} dofollow={r['dofollow']} top_anchor={r['top_anchor'][:40]!r} ex_title={r['example_title'][:40]!r}")
print(f"[A2] disavow with AS>=20: {sum(1 for d in dis if (asn(doms[d]) or 0)>=20)}")
print(f"[A3] disavow that reads like a clean client citation (no spam anchor/title): {len(citation_risk)}")
for d in citation_risk[:30]: print("      ",d, doms[d]["example_title"][:60])

# ---------- DIRECTION B: nothing bad left out ----------
print("\n=== DIRECTION B: false negatives (bad links wrongly kept out) ===")
# dofollow spam-anchor domains that are NOT in the file
dofollow_spam=set()
for l in links:
    if l["link_type"]=="Dofollow" and l["anchor_type"].startswith("Spam"):
        dofollow_spam.add(l["referring_domain"])
leaked=[(d,doms[d]) for d in dofollow_spam if doms[d]["status"]!="Spam (Disavow)"]
bystat=Counter(r["status"] for _,r in leaked)
print(f"[B1] domains with a DOFOLLOW spam anchor NOT in the file: {len(leaked)}  by status={dict(bystat)}")
# of those, the dangerous ones: AS<20 and Keep (rule 8 should have caught) -> real misses
real_miss=[(d,r) for d,r in leaked if r["status"]=="Keep" and (asn(r) or 0)<20]
print(f"     -> KEEP with AS<20 and dofollow spam (REAL MISSES): {len(real_miss)}")
for d,r in real_miss[:30]: print(f"        {d} AS={r['as']} anchor={r['top_anchor'][:45]!r}")
# AS>=20 keep with dofollow spam = genuine site w/ injected link (kept per rule 2) - report only
keep_as=[d for d,r in leaked if r["status"]=="Keep" and (asn(r) or 0)>=20]
print(f"     -> KEEP with AS>=20 and dofollow spam (genuine site, injected link, kept by design): {len(keep_as)}")
print("        e.g.",keep_as[:8])
# Held with dofollow spam = exact+PBN review case (allowed)
held_spam=[d for d,r in leaked if r["status"].startswith("Held")]
print(f"     -> HELD with dofollow spam (exact-commercial + spam, held for partner by design): {len(held_spam)}")

# nofollow-marked spam/held with an actual dofollow link
nf_leak=[d for d,r in doms.items() if r["status"].endswith("(Nofollow, No Action)") and int(r["dofollow"])>0]
print(f"[B2] '(Nofollow, No Action)' domains that actually have a dofollow link: {len(nf_leak)} {nf_leak[:10]}")

# junk-TLD KEEP with dofollow + low AS + not a clean citation (possible missed network spam)
JUNK={"shop","store","website","space","online","xyz","site","top","click","link","fun","cfd","sbs","rest"}
susp=[]
for d,r in doms.items():
    if r["status"]=="Keep" and d.rsplit(".",1)[-1] in JUNK and int(r["dofollow"])>0 and (asn(r) or 0)<10:
        if not names_client_clean(L[d]): susp.append(d)
print(f"[B3] KEEP on junk TLD w/ dofollow + AS<10 + not a clean citation (scrutinize): {len(susp)} {susp[:15]}")

# Own Site sanity
print("\n[C] Own Site:", [d for d,r in doms.items() if r['status']=='Own Site'])
print("\nFINAL STATUS COUNTS:", dict(Counter(r['status'] for r in doms.values())))
