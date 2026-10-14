"""Classify newimagecanopy.com referring domains from BOTH Semrush and Ahrefs.

Semrush is the priority source for metrics (Authority Score, IP, country).
Ahrefs contributes additional SITES that Semrush never indexed, plus Domain
Rating and its own spam flag as corroborating evidence.
"""
import csv,collections,re,datetime
D='/home/user/test/audit/data/'
def host(u):
    m=re.match(r'https?://([^/]+)',u or '')
    return re.sub(r'^www\.','',m.group(1).lower().split(':')[0]) if m else ''
def num(x):
    try: return float(str(x).replace(',','') or 0)
    except: return 0.0

# ---------------- link-level evidence, both tools ----------------
LINKS=[]
for r in csv.DictReader(open(D+'backlinks_all.csv'),delimiter=';'):
    r['tool']='Semrush'; r['rd']=host(r['source_url']); LINKS.append(r)
for r in csv.DictReader(open(D+'ahrefs/ah_backlinks.csv'),delimiter=';'):
    r['tool']='Ahrefs'; r['rd']=host(r['source_url']); LINKS.append(r)
LINKS=[r for r in LINKS if r['rd']]

# ---------------- domain-level metrics, Semrush first ----------------
SEM={r['domain']:r for r in csv.DictReader(open(D+'refdomains.csv'),delimiter=';')}
AHR={r['domain']:r for r in csv.DictReader(open(D+'ahrefs/ah_refdomains.csv'),delimiter=';')}
TAB03=set(l.strip() for l in open(D+'tab03_named.txt') if l.strip())
OWN={'shadyvent.com','newimagecanopy.com'}
KEEP_SEED={'yellowpages.com','grokipedia.com','birdeye.com','scam-detector.com','procore.com','accio.com',
 'superpages.com','owler.com','pei.org','roofingcalculator.com','dexknows.com','dandb.com','wexfordins.com',
 'bestprosintown.com','mykukun.com','qtego.us','processregister.com','empirepetroleum.com','domaineye.com',
 'robuta.com','nationalroofingdirectory.com','custommetalbuildings.com','tngrocersbuyersguide.com',
 'ibbpetroleum.com','homemendly.com','myfavoritebuilder.com','stopvanitymarketing.com','localstack.org',
 'crunchbase.com','einpresswire.com','natlawreview.com','chamberofcommerce.com','wboc.com','yp.com',
 'newsblaze.com','appsruntheworld.com','trustburn.com','capitolhilltimes.com','massnews.com','d-h.st',
 'businesslistus.com','klazify.com','rackcdn.com'}

PBN  = re.compile(r'(seo authority|seo links|backlink|pbn|buy backlink|da 50|pa 40|rank first page|'
                  r'link building|dofollow|white hat seo|outreach backlinks|premium backlinks|sitetosocial|'
                  r'link profile|organic visibility|da and dr|safe link velocity|placement reporting)',re.I)
CANOPY=re.compile(r'(station canopy|station island canopy|gas canop|canopy light|canopy led light|'
                  r'canopy repair|canopy design|canopy construction|canopy solutions|canopy services|canopies|'
                  r'gas station re-?imaging|gas station imaging|re-?imaging services|gas pump canopy|'
                  r'petrol pump canopy|fuel station|petrol station|canopy for sale|canopy installation|'
                  r'canopy manufacturers|commercial canopy|canopy in |canopy the purpose|'
                  r'purpose of a gas station canopy)',re.I)
GEO   = re.compile(r'(austin|dallas|houston|tulsa|oklahoma city)',re.I)
BRAND = re.compile(r'(new ?image ?canopy|shady ?vent)',re.I)
NAKED = re.compile(r'^(https?://|www\.)',re.I)
GENERIC=re.compile(r'^(visit website|website|click here|about|contact|services|project gallery|read more|'
                   r'check this source|here|link|visit site|icon - external link visit website|mistakes|6|,|\.)$',re.I)
CASINO=re.compile(r'(casino|poker|gambling|psilocybin|doxycycline|erythromycin|escort|slot|gacor|betting|bet\b|ufabet|sohbet)',re.I)
SPAMNAME=re.compile(r'(backlink|dofollow|dapa|da-?pa|dachecker|drchecker|pachecker|serp|seo|rank(ing)?checker|'
                    r'rankchecker|linkbuilding|link-?building|buylink|aged-?domain|domraider|domains?\.|'
                    r'shorten|urls?-|checker|trafficfor|guestpost|pbn|citation|profilecreation|smm|'
                    r'rankboost|linkrank|ranklink|rankforge|outrank|indexer|link-baron)',re.I)
JUNKTLD=re.compile(r'\.(top|cfd|monster|sbs|icu|website|shop|store|space|site|online|link|xyz|click|party|fyi|'
                   r'cv|art|bz|lc|pro|biz|agency|us\.com|co\.com|br\.com|de\.com|eu\.com|gb\.net|it\.com|'
                   r'uk\.com|uk\.net|us|info)$',re.I)
SPAMIP=re.compile(r'^(64\.182\.|69\.13\.|94\.46\.|118\.139\.|184\.168\.|185\.(39|41|51|61|163|196|198|58)\.|'
                  r'188\.114\.|195\.20\.19\.|15\.204\.|51\.81\.|203\.161\.54\.|5\.100\.156\.|92\.249\.46\.)')
SPAMTITLE=re.compile(r'(where to buy .{0,12}aged domains|directory pages index|domain report|web directory|'
                     r'boost organic traffic|premium seo|link building services)',re.I)
# Press-release distribution and its syndication footprint
PRNET=re.compile(r'(einpresswire|presswire|pressrelease|newswire|xpr\.media|prnews|'
                 r'^lifestyle\.|businessesinthenews|newsdirect)',re.I)

def anchor_type(a):
    a=(a or '').strip()
    if not a: return 'Empty or image'
    if PBN.search(a): return 'Spam: keyword stuffed SEO sales copy'
    if CANOPY.search(a) and not NAKED.match(a):
        return 'Exact-match commercial (geo)' if GEO.search(a) else 'Exact-match commercial'
    if GENERIC.match(a): return 'Generic'
    if BRAND.search(a) and not NAKED.match(a): return 'Branded'
    if NAKED.match(a) or re.match(r'^[a-z0-9-]+\.(com|net|org|info)/?$',a,re.I): return 'Naked URL'
    return 'Contextual or other'
for r in LINKS: r['atype']=anchor_type(r['anchor'])

by=collections.defaultdict(list)
for r in LINKS: by[r['rd']].append(r)
ALLDOM=set(by)|set(SEM)|set(AHR)

out=[]
for d in ALLDOM:
    rs=by.get(d,[])
    sem,ahr=SEM.get(d),AHR.get(d)
    src='Both' if (sem and ahr) else ('Semrush' if sem else 'Ahrefs')
    asc=int(num(sem['ascore'])) if sem else ''
    dr=num(ahr['dr']) if ahr else ''
    ip=sem['ip'] if sem else ''
    country=sem['country'] if sem else ''
    fs=[x for x in [(sem or {}).get('first_seen'),(ahr or {}).get('first_seen')]+[r['first_seen'] for r in rs] if x]
    first=min(fs,key=lambda v:int(v)) if fs else ''
    types=collections.Counter(x['atype'] for x in rs)
    dof=sum(1 for x in rs if x['nofollow']=='false'); nof=len(rs)-dof
    bl=len(rs) or int(num((sem or {}).get('backlinks') or (ahr or {}).get('links') or 1))
    anchors=[x['anchor'] for x in rs if (x['anchor'] or '').strip()]
    top=collections.Counter(anchors).most_common(1)[0][0] if anchors else ('(not in link sample)' if not rs else '')
    has_pbn=types['Spam: keyword stuffed SEO sales copy']>0
    has_exact=types['Exact-match commercial (geo)']+types['Exact-match commercial']>0
    casino=any(CASINO.search(d) or CASINO.search(x['anchor'] or '') for x in rs) or CASINO.search(d)
    ah_spam=(ahr or {}).get('is_spam')=='true'
    spam_title=any(SPAMTITLE.search(x['source_title'] or '') for x in rs)
    pr=bool(PRNET.search(d))
    eff_auth=asc if asc!='' else (dr/10 if dr!='' else 0)   # Semrush AS first, DR as fallback

    parent='.'.join(d.split('.')[-2:])
    if d in OWN or parent in OWN: status,grp='Own Site','Client owned property'
    elif d in KEEP_SEED: status,grp='Keep','Genuine / editorial'
    elif parent in KEEP_SEED and parent!=d:
        status,grp='Keep',f'Genuine / editorial (subdomain of {parent})'
    elif has_exact and has_pbn: status,grp='HELD - review','Mixes exact-match commercial with link-scheme anchors'
    elif has_exact and nof==len(rs) and rs:
        status,grp='HELD - nofollow','Exact-match commercial anchor, but every link is nofollow - passes no ranking value'
    elif has_exact: status,grp='HELD - pending partner','Exact-match commercial anchor - confirm who commissioned'
    elif pr and rs: status,grp='HELD - pending partner','Press-release syndication - confirm who commissioned'
    elif casino: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Off-topic casino / pharma anchor'
    elif has_pbn: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Automated PBN / service-advertising anchor network'
    elif not rs:
        if SPAMNAME.search(d) or JUNKTLD.search(d) or SPAMIP.match(ip) or ah_spam or eff_auth<=6:
            status,grp='Review - no link sample','Spam signature or low authority, no link sample to confirm dofollow'
        else: status,grp='Keep','Genuine or harmless link'
    elif SPAMNAME.search(d): status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'SEO-tool / link-selling network domain'
    elif SPAMIP.match(ip) or spam_title: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Link-network host (shared IP / templated page)'
    elif ah_spam and eff_auth<=10: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Flagged spam by Ahrefs, low authority'
    elif JUNKTLD.search(d) or eff_auth<=2: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Low-authority directory / bookmark placement'
    else: status,grp='Keep','Genuine or harmless link'

    if re.search(r'bookmark|bmark|social',d,re.I): st='Social bookmarking site'
    elif pr: st='PR / news distribution'
    elif re.search(r'article|blog|content|post|news|magz|diary|writers|story|times|tribune|journal',d,re.I): st='Guest-article / content farm'
    elif d in KEEP_SEED or d in OWN: st='Genuine site'
    else: st='Low-quality web directory'

    tools=sorted({x['tool'] for x in rs}) or ([ 'Both' ] if src=='Both' else [src])
    out.append(dict(domain=d,status=status,group=grp,sitetype=st,ascore=asc,dr=dr,source=src,
        tool='Both' if len(tools)>1 else tools[0],backlinks=bl,dofollow=dof if rs else '',nofollow=nof if rs else '',
        first_seen=first,ip=ip,country=country,top_anchor=top,
        example_page=rs[0]['source_url'] if rs else '',page_title=rs[0]['source_title'] if rs else '',
        atypes='; '.join(f'{k} x{v}' for k,v in types.most_common()) or '(not in link sample)',
        tab03='Yes' if d in TAB03 else '',redundant='',disavow_line='domain:'+d))

BY={x['domain']:x for x in out}
def parent_of(d):
    # walk every suffix, so multi-part TLDs (domain.com.lc, site.co.in) resolve correctly
    p=d.split('.')
    for i in range(1,len(p)-1):
        cand='.'.join(p[i:])
        if cand in BY: return cand
    return None
promoted=redundant=demoted=0
for x in out:
    d=x['domain']; parent=parent_of(d)
    if not parent or parent==d: continue
    pst=BY[parent]['status']
    if pst in ('Keep','Own Site') and x['status'].startswith('Spam'):
        x['status']=pst; x['group']=f'Genuine / editorial (subdomain of {parent})'; promoted+=1
    elif pst.startswith('Review') and x['status'].startswith('Spam'):
        x['status']='Review - no link sample'; x['group']=f'Parent {parent} unresolved - client to confirm'; promoted+=1
    elif pst=='Spam (Disavow)' and x['status']=='Spam (Disavow)':
        x['group']+=f' (covered by domain:{parent})'; x['redundant']='Yes'; redundant+=1
for x in out:
    if x['status']=='Keep' and x['group'].startswith('Genuine or harmless'):
        a=x['ascore'] if x['ascore']!='' else (x['dr']/10 if x['dr']!='' else 0)
        if a<=6:
            x['status']='Review - low authority'
            x['group']='Low-authority site, no editorial signal - client to confirm keep or disavow'; demoted+=1
for x in out:
    if x['status']!='Spam (Disavow)': x['disavow_line']=''
assert not [x for x in out if x['disavow_line'] and x['status']!='Spam (Disavow)']
print(f"post-pass: {promoted} subdomains inherited parent status, {redundant} redundant child lines, {demoted} low-authority Keeps -> Review")

out.sort(key=lambda x:(x['status'],-x['backlinks'],x['domain']))
with open(D+'domain_audit.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys()),delimiter=';'); w.writeheader(); w.writerows(out)
with open(D+'links_all.csv','w',newline='') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['rd','tool','source_url','source_title','target_url','anchor','atype','nofollow','first_seen'])
    for r in sorted(LINKS,key=lambda x:(x['rd'],x['tool'],x['anchor'] or '')):
        w.writerow([r['rd'],r['tool'],r['source_url'],r['source_title'],r['target_url'],r['anchor'],r['atype'],r['nofollow'],r['first_seen']])

print("\n=== STATUS ===")
for k,v in collections.Counter(x['status'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("  TOTAL",len(out))
print("\n=== SOURCE ===")
for k,v in collections.Counter(x['source'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("\n=== ANCHOR TYPES (links) ===")
for k,v in collections.Counter(r['atype'] for r in LINKS).most_common(): print(f"  {v:5d}  {k}  ({v/len(LINKS)*100:.1f}%)")
print(f"\nlinks total: {len(LINKS)}  (Semrush {sum(1 for r in LINKS if r['tool']=='Semrush')}, Ahrefs {sum(1 for r in LINKS if r['tool']=='Ahrefs')})")
print("Tab03:",collections.Counter(x['status'] for x in out if x['tab03']=='Yes'))
