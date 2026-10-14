import csv,collections,re,json,datetime
D='/home/user/test/audit/data/'
def dom(u):
    m=re.match(r'https?://([^/]+)',u or '')
    d=m.group(1).lower() if m else ''
    return re.sub(r'^www\.','',d).split(':')[0]

R=list(csv.DictReader(open(D+'backlinks_all.csv'),delimiter=';'))
for r in R: r['rd']=dom(r['source_url'])

RD={}
for r in csv.DictReader(open(D+'refdomains.csv'),delimiter=';'):
    RD[r['domain']]=r
TAB03=set(l.strip() for l in open(D+'tab03_named.txt') if l.strip())

OWN={'shadyvent.com','newimagecanopy.com'}
# Genuine / editorial properties verified by brand recognition + authority
KEEP_SEED={'yellowpages.com','grokipedia.com','birdeye.com','scam-detector.com','procore.com','accio.com',
 'superpages.com','owler.com','pei.org','roofingcalculator.com','dexknows.com','dandb.com','wexfordins.com',
 'bestprosintown.com','mykukun.com','qtego.us','processregister.com','empirepetroleum.com','domaineye.com',
 'robuta.com','nationalroofingdirectory.com','custommetalbuildings.com','tngrocersbuyersguide.com',
 'ibbpetroleum.com','homemendly.com','myfavoritebuilder.com','stopvanitymarketing.com','localstack.org'}

PBN  = re.compile(r'(seo authority|seo links|backlink|pbn|buy backlink|da 50|pa 40|rank first page|'
                  r'link building|dofollow|white hat seo|outreach backlinks|premium backlinks|sitetosocial|'
                  r'link profile|organic visibility|da and dr|safe link velocity|placement reporting)',re.I)
CANOPY=re.compile(r'(station canopy|gas canop|canopy light|canopy repair|canopy design|canopy construction|'
                  r'canopy solutions|canopy services|canopies|gas station imaging|gas pump canopy|fuel station|'
                  r'petrol station|canopy for sale|canopy installation|canopy manufacturers|commercial canopy|'
                  r'canopy in |canopy the purpose|purpose of a gas station canopy)',re.I)
GEO   = re.compile(r'(austin|dallas|houston|tulsa|oklahoma city|\bok\b|\btx\b)',re.I)
BRAND = re.compile(r'(new ?image ?canopy|shady ?vent)',re.I)
NAKED = re.compile(r'^(https?://|www\.)',re.I)
GENERIC=re.compile(r'^(visit website|website|click here|about|contact|services|project gallery|read more|'
                   r'check this source|here|link|visit site|icon - external link visit website|mistakes|6|,|\.)$',re.I)
CASINO=re.compile(r'(casino|poker|gambling|psilocybin|doxycycline|erythromycin|escort|slot|gacor|betting|bet\b|ufabet|sohbet)',re.I)
# Domain-name signature of the SEO-tool / link-selling / domain-auction network
SPAMNAME=re.compile(r'(backlink|dofollow|dapa|da-?pa|dachecker|drchecker|pachecker|serp|seo|rank(ing)?checker|'
                    r'rankchecker|linkbuilding|link-?building|buylink|aged-?domain|domraider|domains?\.|'
                    r'shorten|urls?-|checker|trafficfor|guestpost|pbn|citation|profilecreation|smm)',re.I)
JUNKTLD=re.compile(r'\.(top|cfd|monster|sbs|icu|website|shop|store|space|site|online|link|xyz|click|party|fyi|cv|art|bz|lc|pro|biz|us\.com|co\.com|br\.com|de\.com|eu\.com|gb\.net|it\.com|uk\.com|uk\.net|us|info)$',re.I)
SPAMIP=re.compile(r'^(64\.182\.|69\.13\.|94\.46\.|118\.139\.|184\.168\.|185\.(39|41|51|61|163|196|198|58)\.|188\.114\.|195\.20\.19\.|15\.204\.|51\.81\.)')

def anchor_type(a):
    a=(a or '').strip()
    if not a: return 'Empty or image'
    if PBN.search(a): return 'Spam: keyword stuffed SEO sales copy'
    if CANOPY.search(a):
        return 'Exact-match commercial (geo)' if GEO.search(a) else 'Exact-match commercial'
    if GENERIC.match(a): return 'Generic'
    if BRAND.search(a) and not NAKED.match(a): return 'Branded'
    if NAKED.match(a) or re.match(r'^[a-z0-9-]+\.(com|net|org|info)/?$',a,re.I): return 'Naked URL'
    return 'Contextual or other'

for r in R: r['atype']=anchor_type(r['anchor'])

# ---- per-domain aggregation ----
by=collections.defaultdict(list)
for r in R: by[r['rd']].append(r)

out=[]
for d,rs in by.items():
    types=collections.Counter(x['atype'] for x in rs)
    dof=sum(1 for x in rs if x['nofollow']=='false'); nof=len(rs)-dof
    meta=RD.get(d,{})
    asc=int(meta.get('ascore') or 0)
    anchors=[x['anchor'] for x in rs if (x['anchor'] or '').strip()]
    top=collections.Counter(anchors).most_common(1)[0][0] if anchors else ''
    has_pbn   = types['Spam: keyword stuffed SEO sales copy']>0
    has_exact = types['Exact-match commercial (geo)']+types['Exact-match commercial']>0
    casino    = any(CASINO.search(d) or CASINO.search(x['anchor'] or '') for x in rs)

    if d in OWN: status,grp='Own Site','Client owned property'
    elif d in KEEP_SEED: status,grp='Keep','Genuine / editorial'
    elif has_exact and has_pbn:
        status,grp='HELD - review','Mixes exact-match commercial with link-scheme anchors'
    elif has_exact:
        status,grp='HELD - pending partner','Exact-match commercial anchor - confirm who commissioned'
    elif casino: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Off-topic casino / pharma anchor'
    elif has_pbn: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Automated PBN / service-advertising anchor network'
    elif SPAMNAME.search(d):
        status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'SEO-tool / link-selling network domain'
    elif asc<=6 and (JUNKTLD.search(d) or SPAMIP.match(meta.get('ip',''))):
        status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Low-authority directory / bookmark placement'
    elif asc<=2:
        status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Low-authority directory / bookmark placement'
    else: status,grp='Keep','Genuine or harmless link'

    if re.search(r'bookmark|bmark|marks?\\.|social',d,re.I): sitetype='Social bookmarking site'
    elif re.search(r'article|blog|content|post|news|magz|magzine|diary|writers|story',d,re.I): sitetype='Guest-article / content farm'
    elif re.search(r'director|listing|local|biz|business|citation|pages|yellow',d,re.I): sitetype='Low-quality web directory'
    elif d in KEEP_SEED or d in OWN: sitetype='Genuine site'
    else: sitetype='Low-quality web directory'
    out.append(dict(domain=d,status=status,group=grp,sitetype=sitetype,ascore=asc,backlinks=len(rs),
        dofollow=dof,nofollow=nof,first_seen=meta.get('first_seen',''),ip=meta.get('ip',''),
        country=meta.get('country',''),top_anchor=top,
        example_page=rs[0]['source_url'],page_title=rs[0]['source_title'],
        atypes='; '.join(f'{k} x{v}' for k,v in types.most_common()),
        tab03='Yes' if d in TAB03 else '',
        disavow_line='domain:'+d))

# --- union in referring domains that have no row in the link table ---
seen={x['domain'] for x in out}
extra=0
for d,meta in RD.items():
    if d in seen: continue
    asc=int(meta.get('ascore') or 0)
    if d in OWN: status,grp='Own Site','Client owned property'
    elif d in KEEP_SEED: status,grp='Keep','Genuine / editorial'
    elif CASINO.search(d): status,grp='Spam (Disavow)','Off-topic casino / pharma anchor'
    elif SPAMNAME.search(d): status,grp='Spam (Disavow)','SEO-tool / link-selling network domain'
    elif asc<=6 and (JUNKTLD.search(d) or SPAMIP.match(meta.get('ip',''))):
        status,grp='Spam (Disavow)','Low-authority directory / bookmark placement'
    elif asc<=2: status,grp='Spam (Disavow)','Low-authority directory / bookmark placement'
    else: status,grp='Keep','Genuine or harmless link'
    if re.search(r'bookmark|bmark|social',d,re.I): st='Social bookmarking site'
    elif re.search(r'article|blog|content|post|news|diary|writers|story',d,re.I): st='Guest-article / content farm'
    elif d in KEEP_SEED or d in OWN: st='Genuine site'
    else: st='Low-quality web directory'
    out.append(dict(domain=d,status=status,group=grp,sitetype=st,ascore=asc,
        backlinks=int(meta.get('backlinks') or 1),dofollow='',nofollow='',
        first_seen=meta.get('first_seen',''),ip=meta.get('ip',''),country=meta.get('country',''),
        top_anchor='(not in link sample)',example_page='',page_title='',
        atypes='(not in link sample)',tab03='Yes' if d in TAB03 else '',disavow_line='domain:'+d))
    extra+=1
print("refdomain-only rows added:",extra)

out.sort(key=lambda x:(x['status'],-x['backlinks'],x['domain']))
with open(D+'domain_audit.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys()),delimiter=';'); w.writeheader(); w.writerows(out)

print("=== STATUS ===")
for k,v in collections.Counter(x['status'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("\n=== GROUP ===")
for k,v in collections.Counter(x['group'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("\n=== ANCHOR TYPES (backlinks) ===")
at=collections.Counter(r['atype'] for r in R)
for k,v in at.most_common(): print(f"  {v:5d}  {k}   ({v/len(R)*100:.1f}%)")
print("\nTab03 domains resolved:", sum(1 for x in out if x['tab03']=='Yes'), "of", len(TAB03))
print("Tab03 statuses:", collections.Counter(x['status'] for x in out if x['tab03']=='Yes'))
