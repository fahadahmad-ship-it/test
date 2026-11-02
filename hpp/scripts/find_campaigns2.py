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

# ---- Messaging-app CHANNEL INVITATION: telegram/t.me join-channel ----
chan_re = re.compile(r'(t\.me/|telegram|join our (whats\s?app|channel)|our .*chanel|whatsapp channel|join .*(telegram|whatsapp) (channel|group))', re.I)
# ---- Self-promotional LINK-SERVICE pitch: seller advertising own service, often w/ messaging contact ----
pitch_re = re.compile(r'(i will |whats\s?app us|dm (me|us)|contact (me|us)|order (now|your)|increase your (domain authority|da|dr)|rank(ing)? (your|#?1)|cheap .*back ?links|buy .*back ?links|\d+\s*(usd|\$)|\+\d[\d\s()\-]{6,})', re.I)

def group(pred):
    doms=defaultdict(list)
    for r in links:
        if pred(r["anchor"]):
            doms[canon_host(r["source_url"])].append(r)
    return doms

chan = group(lambda a: bool(chan_re.search(a)))
# pitch excluding ones that are channel invitations (telegram join) so WhatsApp-pitch stays in pitch
pitch = group(lambda a: bool(pitch_re.search(a)) and not chan_re.search(a))

def rootdom(h):
    # reduce subdomain to registrable-ish root for domain-count sanity (simple: last 2-3 labels)
    return h

print(f"CHANNEL-INVITATION domains = {len(chan)}")
# distinct anchors in channel group
ca=defaultdict(set)
for d,rs in chan.items():
    for r in rs: ca[r["anchor"]].add(d)
for a in sorted(ca, key=lambda x:-len(ca[x])):
    nf = 'allnofollow' if all(r['nofollow'] for d in chan for r in chan[d] if r['anchor']==a) else 'has-dofollow'
    print(f"   {len(ca[a]):3d}d  {nf:12s} {a[:80]!r}")

print(f"\nPITCH (self-promo link-service) domains = {len(pitch)}")
pa=defaultdict(set)
for d,rs in pitch.items():
    for r in rs: pa[r["anchor"]].add(d)
for a in sorted(pa, key=lambda x:-len(pa[x])):
    print(f"   {len(pa[a]):3d}d  {a[:85]!r}")

print("\noverlap chan&pitch:", sorted(set(chan)&set(pitch)))

# The flood template (names client domain, 'help ... rank higher' etc.) - count for context
flood_re=re.compile(r'(premium seo authority backlinks|white hat seo links|dofollow backlinks da \d+|link building services helping|tiered link building|boost domain authority)', re.I)
flood=group(lambda a: bool(flood_re.search(a)))
print(f"\nFLOOD (client-named sales copy) domains = {len(flood)}")
