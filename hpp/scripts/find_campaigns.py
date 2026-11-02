import sys, re, glob, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import parse_backlinks, canon_host

base = "/home/user/test/hpp"
bl, rej = parse_backlinks(glob.glob(os.path.join(base, "data/fetch/bl_*.csv")))
seen=set(); links=[]
for r in bl:
    k=(r["source_url"].rstrip("/").lower(), r["target_url"].rstrip("/").lower(), r["anchor"])
    if k in seen: continue
    seen.add(k); links.append(r)

# messaging-app channel invitation patterns
msg_re = re.compile(r'(t\.me/|telegram|whats\s?app|wa\.me/|\bviber\b|\bsignal\b app|wechat|\bskype\b|join our (telegram|whatsapp|channel)|join .* channel)', re.I)
# self-promotional link-service pitch (seller advertising their OWN service, often w/ contact/CTA)
selfpromo_re = re.compile(r'(i will |we (will )?(provide|offer|build|increase|boost)|order now|buy (back ?links|seo)|cheap (back ?links|seo)|contact (us|me)|\bhire\b|rank(ing)? #?1|in \d+ days|increase your (domain authority|da|dr)|\bda\s*\d+\b.*\bpa\s*\d+\b|dofollow backlinks|pbn (network|service)|link building service|seo service)', re.I)

def dom_group(pred):
    doms=defaultdict(list)
    for r in links:
        if pred(r):
            doms[canon_host(r["source_url"])].append(r)
    return doms

msg_doms = dom_group(lambda r: bool(msg_re.search(r["anchor"])))
sp_doms  = dom_group(lambda r: bool(selfpromo_re.search(r["anchor"])))

print(f"=== MESSAGING-APP INVITATION: {len(msg_doms)} domains ===")
for d in sorted(msg_doms):
    rs=msg_doms[d]
    df=any(not r["nofollow"] for r in rs)
    ex=rs[0]["anchor"][:70]
    print(f"  {d:34s} links={len(rs):3d} dofollow={df}  e.g. {ex!r}")

print(f"\n=== SELF-PROMO LINK-SERVICE: {len(sp_doms)} domains ===")
for d in sorted(sp_doms):
    rs=sp_doms[d]
    df=any(not r["nofollow"] for r in rs)
    ex=rs[0]["anchor"][:70]
    print(f"  {d:34s} links={len(rs):3d} dofollow={df}  e.g. {ex!r}")

# overlap
ov=set(msg_doms)&set(sp_doms)
print(f"\noverlap (in both): {len(ov)} -> {sorted(ov)}")

# distinct messaging anchors
print("\n--- distinct messaging anchors ---")
ma=defaultdict(int)
for r in links:
    if msg_re.search(r["anchor"]): ma[r["anchor"]]+=1
for a,c in sorted(ma.items(), key=lambda x:-x[1])[:25]:
    print(f"  {c:4d}  {a[:95]!r}")
