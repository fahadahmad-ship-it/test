#!/usr/bin/env python3
"""Both-directions verification of the classification (playbook s9)."""
import csv, io, sys
from collections import Counter
BASE="/home/user/test/offsite-backlink-audit/elitewrecker"
doms=list(csv.DictReader(open(BASE+"/out/domains_classified.csv")))
links=list(csv.DictReader(open(BASE+"/out/links_classified.csv")))

def asn(r):
    try: return float(r["as"]) if r["as"] not in ("","None") else None
    except: return None

fails=[]
# AS source coverage
src=Counter(r["as_src"] for r in doms)
print("AS source:",dict(src))
noas=[r for r in doms if r["as_src"]=="none"]
print("domains with NO AS at all:",len(noas))
print("  of those, status:",Counter(r["status"] for r in noas))

dis=[r for r in doms if r["status"]=="Spam (Disavow)"]
keep=[r for r in doms if r["status"]=="Keep"]
held=[r for r in doms if r["status"].startswith("Held")]

# FALSE POSITIVES: disavow w/ AS>=20
fp_as=[r for r in dis if (asn(r) or 0)>=20]
print("\n[FP] disavow with AS>=20:",len(fp_as), [r["domain"] for r in fp_as][:20])
# disavow with real organic traffic (review)
fp_tr=[r for r in dis if int(r["traffic"] or 0)>0]
print("[FP] disavow with organic traffic>0:",len(fp_tr))
for r in sorted(fp_tr,key=lambda x:-int(x["traffic"]))[:15]:
    print(f"     {r['domain']} AS={r['as']} traffic={r['traffic']} top_anchor={r['top_anchor'][:50]!r}")
# disavow resting on NO visible evidence (not spam anchor, not ahrefs_spam host/title). has_spam flag proxy
fp_noevid=[r for r in dis if r["has_spam"]!="True"]
print("[FP] disavow where has_spam flag is False (check host/title/tld evidence):",len(fp_noevid))
print("     sample:",[r["domain"] for r in fp_noevid][:25])

# FALSE NEGATIVES: Keep/Held with a dofollow keyword-stuffed spam link
# build per-domain dofollow-spam presence from links
dofollow_spam=set()
for l in links:
    if l["link_type"]=="Dofollow" and l["anchor_type"].startswith("Spam"):
        dofollow_spam.add(l["referring_domain"])
fn=[r for r in doms if r["status"] in ("Keep","Held (Pending Partner)","Held (Nofollow, No Action)")
    and r["domain"] in dofollow_spam and r["status"]!="Spam (Disavow)"]
# Keep with dofollow spam is a real FN; Held w/ spam is the 'exact+spam' review case (allowed) -> separate
fn_keep=[r for r in keep if r["domain"] in dofollow_spam]
print("\n[FN] KEEP domains that have a dofollow spam link:",len(fn_keep))
print("     sample:",[r["domain"] for r in fn_keep][:25])
# nofollow-marked spam that actually has a dofollow link
nf=[r for r in doms if r["status"]=="Spam (Nofollow, No Action)" and int(r["dofollow"])>0]
print("[FN] 'Spam (Nofollow)' domains with dofollow>0:",len(nf))

# integrity: every disavow domain has >=1 dofollow
nod=[r for r in dis if int(r["dofollow"])==0]
print("\n[INT] disavow domains with 0 dofollow links:",len(nod))
# Own site / keep / held must NOT be in disavow list (by construction one status each) - ok

print("\nSTATUS COUNTS:",Counter(r["status"] for r in doms))
print("KEEP sample (should be genuine):")
for r in sorted(keep,key=lambda x:-(asn(x) or 0))[:12]:
    print(f"   {r['domain']} AS={r['as']} traffic={r['traffic']} anchor={r['top_anchor'][:40]!r}")
