import csv, sys, collections, re
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2]); sem=rd(sys.argv[3],';')
prior87={l.strip() for l in open(sys.argv[4]) if l.strip()}
raw=[l.rstrip('\n').split('\t') for l in open(sys.argv[5],encoding='utf-8',errors='replace') if l.strip()]
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
ahr_all={r['Domain'].lower() for r in rdm}
for r in bl: r['_h']=host(r['Referring page URL'])
cand={r['_h'] for r in bl if r['Is spam']=='true' and r['Nofollow']=='false'}
semd={r['domain'].lower() for r in sem}
rawd=collections.defaultdict(list)
for row in raw:
    if len(row)>=4: rawd[host(row[0])].append(row)
# STRICT: anchor names ngwindows.com with no letter/hyphen immediately before "ngwindows"
NG=re.compile(r'(?<![A-Za-z0-9-])(?:https?://)?(?:www\.)?ngwindows\.com', re.I)
VEND=re.compile(r'backlink|pbn|dofollow|domain rating|domain authority|guest post|niche edit|seo|google visibility|rankings?', re.I)
def strict(d):
    out=[]
    for r in rawd.get(d,[]):
        a=r[1]
        if r[2]=='false' and NG.search(a) and VEND.search(a): out.append(r)
    return out
print("=== prior 87: strict re-test on links_raw ===")
ok=[];bad=[]
for d in sorted(prior87):
    s=strict(d)
    (ok if s else bad).append(d)
print(f"  pass strict (dofollow vendor anchor naming ngwindows.com): {len(ok)}")
print(f"  FAIL strict: {len(bad)} -> {bad}")
for d in bad:
    for r in rawd.get(d,[])[:3]: print(f"     {d}: df={r[2]} anchor={r[1][:95]!r}")
semonly=semd-ahr_all
print(f"\n=== Semrush-only ({len(semonly)}): strict dofollow vendor anchor naming ngwindows.com ===")
hits={d:strict(d) for d in sorted(semonly)}
hits={d:v for d,v in hits.items() if v}
print(f"  count = {len(hits)}")
inter=sorted(set(hits)&prior87); extra=sorted(set(hits)-prior87)
print(f"  of which already in prior-87: {len(inter)}; NEW semrush-only not in 87: {len(extra)}")
for d in extra: print(f"    + {d:38s} n={len(hits[d])} | {hits[d][0][1][:80]}")
# write lists
open('/home/user/test/backlink-audit/work-v2/semonly_strict.txt','w').write('\n'.join(sorted(hits))+'\n')
# Ahrefs-side: no-anchor-evidence check across ALL semrush domains
allsem_strict={d for d in sorted(semd) if strict(d)}
print(f"\n=== all Semrush domains passing strict: {len(allsem_strict)} (semrush-only: {len(hits)}) ===")
# overlap domains
print(f"  overlap-domains passing strict: {len(allsem_strict & ahr_all)}; of those Ahrefs spam+dofollow: {len(allsem_strict & cand)}")
