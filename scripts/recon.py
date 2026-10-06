import csv, sys, collections, re
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
bl=rd(sys.argv[1]); rdm=rd(sys.argv[2])
sem=rd(sys.argv[3],';')
prior87=[l.strip() for l in open(sys.argv[4]) if l.strip()]
raw=[l.rstrip('\n').split('\t') for l in open(sys.argv[5],encoding='utf-8',errors='replace') if l.strip()]
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
ahr_all={r['Domain'].lower() for r in rdm}
ahr_spam={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
semd={r['domain'].lower() for r in sem}
for r in bl: r['_h']=host(r['Referring page URL'])
cand={r['_h'] for r in bl if r['Is spam']=='true' and r['Nofollow']=='false'}
print(f"Ahrefs domains {len(ahr_all)}  Semrush {len(semd)}  overlap {len(ahr_all&semd)}  sem-only {len(semd-ahr_all)}  ahr-only {len(ahr_all-semd)}")
cur5=['backlinksseochecker.space','dapaseochecker.online','onlinewebsitechecker.space','seostrengthchecker.online','siteseocheckerfree.store']
print("\n=== current 5-entry file vs Ahrefs ===")
for d in cur5:
    print(f"  {d:34s} in_ahrefs={d in ahr_all} spam={d in ahr_spam} dofollow_cand={d in cand}")
p87=set(prior87)
print(f"\n=== prior 87 ===")
print(f"  in Ahrefs refdomains : {len(p87&ahr_all)}")
print(f"  Ahrefs spam-flagged  : {len(p87&ahr_spam)}")
print(f"  Ahrefs spam+dofollow : {len(p87&cand)}")
print(f"  NOT seen by Ahrefs   : {len(p87-ahr_all)}")
# raw evidence for semrush-only
rawd=collections.defaultdict(list)
for row in raw:
    if len(row)>=3: rawd[host(row[0])].append(row)
semonly_87 = sorted(p87-ahr_all)
print(f"\n=== {len(semonly_87)} prior-87 NOT in Ahrefs: links_raw evidence ===")
for d in semonly_87:
    rows=rawd.get(d,[])
    df=[r for r in rows if r[2]=='false']
    anc=collections.Counter(r[1][:70] for r in df)
    print(f"  {d:36s} raw_rows={len(rows):3d} dofollow={len(df):3d} | {anc.most_common(1)}")
# new ahrefs dofollow spam candidates not in prior 87 and not in current 5
new = sorted(cand - p87 - set(cur5))
print(f"\n=== Ahrefs dofollow-spam domains NOT in prior 87/5: {len(new)} ===")
# semrush-only domains with vendor-anchor dofollow evidence
VEND=re.compile(r'backlink|pbn|dofollow|domain (rating|authority)|guest post|niche edit|rank (first|higher)|seo', re.I)
TARGET=re.compile(r'ngwindows\.com', re.I)
semonly=semd-ahr_all
hits=[]
for d in sorted(semonly):
    df=[r for r in rawd.get(d,[]) if len(r)>2 and r[2]=='false' and VEND.search(r[1]) and TARGET.search(r[1])]
    if df: hits.append((d,len(df),df[0][1][:80]))
print(f"\n=== Semrush-only domains w/ dofollow vendor anchor NAMING ngwindows.com: {len(hits)} ===")
for d,n,a in hits[:200]: print(f"  {d:40s} {n:3d} | {a}")
