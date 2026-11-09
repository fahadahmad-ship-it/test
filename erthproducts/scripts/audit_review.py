"""Adversarial re-audit: hunt for wrongly-flagged domains (both directions).
Usage: python3 -I audit_review.py <classified.json>
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

data = json.load(open(sys.argv[1], encoding="utf-8"))
byd = {r["domain"]: r for r in data}
disav = [r for r in data if r["status"] == "Spam (Disavow)"]
keep  = [r for r in data if r["status"] == "Keep"]
held  = [r for r in data if r["status"].startswith("Held")]
spnf  = [r for r in data if r["status"] == "Spam (Nofollow, No Action)"]

def ev_basis(r):
    e = r["evidence"]
    b = []
    if e["pbn"]: b.append("pbn-anchor")
    if e["offtopic"]: b.append("offtopic")
    if e["spam_host"]: b.append("spam-host")
    if e["spam_title"]: b.append("spam-title/url")
    strong = bool(b)
    if e["numeric_host"]: b.append("numeric-host")
    if e["network_host"]: b.append("/24-network")
    if e["spam_tld"]: b.append("spam-tld")
    return b, strong

print("=== A. Disavow evidence-basis distribution (2054) ===")
basis_ct = collections.Counter()
weak_only = []
for r in disav:
    b, strong = ev_basis(r)
    basis_ct[", ".join(b)] += 1
    if not strong:
        weak_only.append(r)
for k, v in basis_ct.most_common(15):
    print(f"  {v:5d}  [{k}]")
print(f"\n=== B. Disavow resting ONLY on infra corroboration (no anchor/host/title): {len(weak_only)} ===")
for r in weak_only[:40]:
    e=r["evidence"]
    print(f"  {r['domain'][:34]:34} as={r.get('as')} df={r['dofollow']} tld={C.tld(r['domain']):6} "
          f"numeric={e['numeric_host']} net={e['network_host']} tld_spam={e['spam_tld']} top={r['top_anchor'][:34]!r}")

print(f"\n=== C. Disavow domains with ANY Semrush organic traffic (manual-review flag) ===")
tr = sorted([r for r in disav if r.get('traffic',0)], key=lambda x:-x['traffic'])
print(f"  count: {len(tr)}")
for r in tr[:25]:
    print(f"  {r['domain'][:32]:32} traffic={r['traffic']:>8} as={r.get('as')} ev={ev_basis(r)[0]} top={r['top_anchor'][:34]!r}")

print(f"\n=== D. Disavow domains with AS>=30 (could be genuine high-authority) ===")
hi=[r for r in disav if (r.get('as') or 0)>=30]
print(f"  count: {len(hi)}")
for r in sorted(hi,key=lambda x:-(x.get('as') or 0))[:25]:
    print(f"  {r['domain'][:32]:32} as={r.get('as')} df={r['dofollow']} ev={ev_basis(r)[0]} top={r['top_anchor'][:40]!r}")

print(f"\n=== E. Keep/Held with ANY spam signal (possible false negative) ===")
fn=0
for r in keep+held:
    e=r["evidence"]
    sig=[k for k in ("pbn","offtopic","spam_host","spam_title","numeric_host","network_host","spam_tld") if e[k]]
    if sig:
        fn+=1
        print(f"  {r['status'][:14]:14} {r['domain'][:30]:30} df={r['dofollow']} signals={sig} top={r['top_anchor'][:34]!r}")
if fn==0: print("  none")

print(f"\n=== F. Parent/child redundancy among disavow domains (domain: covers subdomains) ===")
dset={r['domain'] for r in disav}
red=[d for d in dset if any(d!=p and (d.endswith('.'+p)) for p in dset)]
print(f"  redundant children present: {len(red)} {red[:10]}")

print(f"\n=== G. Short real-word .com disavow domains (eyeball for genuine brands) ===")
import re
sw=[r for r in disav if C.tld(r['domain'])=='com' and len(r['domain'].split('.')[0])<=7 and r['domain'].split('.')[0].isalpha()]
for r in sorted(sw,key=lambda x:-(x.get('as') or 0))[:25]:
    print(f"  {r['domain'][:24]:24} as={r.get('as')} traffic={r.get('traffic')} ev={ev_basis(r)[0]} top={r['top_anchor'][:34]!r}")

print(f"\n=== H. Nofollow-spam sanity: any with dofollow? ===")
print("  ", [r['domain'] for r in spnf if r['dofollow']>0][:10] or "none")
