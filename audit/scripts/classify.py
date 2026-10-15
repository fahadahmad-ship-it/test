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
RAW=[]
for r in csv.DictReader(open(D+'backlinks_all.csv'),delimiter=';'):
    r['tool']='Semrush'; r['rd']=host(r['source_url']); r['ltype']='text'; RAW.append(r)
for r in csv.DictReader(open(D+'ahrefs/ah_backlinks.csv'),delimiter=';'):
    r['tool']='Ahrefs'; r['rd']=host(r['source_url']); r['ltype']=r.get('type','text'); RAW.append(r)
RAW=[r for r in RAW if r['rd']]

def canon(u):
    u=(u or '').strip().lower().split('#')[0]
    u=re.sub(r'^https?://','',u); u=re.sub(r'^www\.','',u)
    return u.rstrip('/')
# The same physical link is reported by both tools with http/https, www and
# trailing-slash variations. Counting it twice inflates every figure, so collapse
# on (source page, target page, anchor) and keep the Semrush row as the priority
# source, recording which tools saw it.
LINKS=[]; seen={}
for r in sorted(RAW,key=lambda x:(x['tool']!='Semrush',)):
    k=(canon(r['source_url']),canon(r['target_url']),(r['anchor'] or '').strip().lower())
    if k in seen:
        if seen[k]['tool']!=r['tool']: seen[k]['seen_in']='Both'
        continue
    r['seen_in']=r['tool']; seen[k]=r; LINKS.append(r)
print(f"links: {len(RAW):,} reported by the two tools, {len(LINKS):,} unique after removing {len(RAW)-len(LINKS):,} duplicates")

# ---------------- domain-level metrics, Semrush first ----------------
SEM={r['domain']:r for r in csv.DictReader(open(D+'refdomains.csv'),delimiter=';')}
AHR={r['domain']:r for r in csv.DictReader(open(D+'ahrefs/ah_refdomains.csv'),delimiter=';')}
# Semrush metrics fetched in bulk for domains Ahrefs found but Semrush's
# referring-domain report did not return. Semrush stays the priority source.
EXTRA={r['domain']:r for r in csv.DictReader(open(D+'semrush_extra.csv'),delimiter=';')}
# The Ahrefs refdomains export is registered-domain level, so subdomain hosts find
# nothing there. Their Domain rating is on the backlink rows instead.
AHDR={}
for _r in csv.DictReader(open(D+'ahrefs/ah_backlinks.csv'),delimiter=';'):
    _h=host(_r['source_url']); _d=_r.get('page_ascore') or ''
    if _h and _d and _h not in AHDR: AHDR[_h]=_d
TAB03=set(l.strip() for l in open(D+'tab03_named.txt') if l.strip())
OWN={'shadyvent.com','newimagecanopy.com'}
# Domains the client reviewed by hand and ruled on. A decision made on the live page
# beats anything inferred from the link data, so these are applied last and win.
CLIENT_DISAVOW={'pr-new.domaineye.com'}   # SEO domains for sale listing, dofollow, client call
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
                  r'link profile|organic visibility|da and dr|safe link velocity|placement reporting|'
                  r'da boost|tf boost|dr improvement|authority link|sponsored post|anchor text audit|'
                  r'referring domain|digital pr|page one results|replacement policy|no obvious footprint|'
                  r'seoexpress|rankzly|landing page design|outrank competitors|metrics-verified|'
                  r'content optimization|log file analysis|nap consistency|indexation service|map pack|'
                  r'hreflang|rank tracking|skyscraper|topical authority|monthly retainer|white-hat|'
                  r'editorial links|more clients than capacity|shopify development|api integration|'
                  r'high-authority|vanity metrics|order placement)',re.I)
CANOPY=re.compile(r'(station canopy|station island canopy|gas canop|canopy light|canopy led light|'
                  r'canopy repair|canopy design|canopy construction|canopy solutions|canopy services|canopies|'
                  r'gas station re-?imaging|gas station imaging|re-?imaging services|gas pump canopy|'
                  r'petrol pump canopy|fuel station|petrol station|canopy for sale|canopy installation|'
                  r'canopy manufacturers|commercial canopy|canopy in |canopy the purpose|'
                  r"purpose of a gas station canopy|gas station's design)",re.I)
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
                     r'boost organic traffic|premium seo|link building services|'
                     # a page that exists to sell domains is a link farm page, whoever hosts it
                     r'domains? for sale|top list of .{0,10}domains|top domains [-–]|seo\.domains)',re.I)
# Press-release distribution and its syndication footprint
PRNET=re.compile(r'(einpresswire|presswire|pressrelease|newswire|xpr\.media|prnews|'
                 r'^lifestyle\.|businessesinthenews|newsdirect)',re.I)
# A linking page whose TITLE names the client is a business listing, citation or
# editorial mention, not spam. Never disavow one automatically. The SEO sales-copy
# templates also contain the client name, so those are excluded first.
CLIENTPAGE=re.compile(r'(shady ?vent|new ?image ?canopy)',re.I)
CLIENTSERVICE=re.compile(r'(gas station canop|canopy construction|canopy repair|fuel station canop|'
                         r'petrol station canop|gas canop|canopy lighting|station canopy|gas station imaging)',re.I)
SALESCOPY=re.compile(r'(backlink|seo|pbn|dofollow|da 50|pa 40|rank first page|link building|'
                     r'premium|authority|outreach)',re.I)

def anchor_type(a):
    a=(a or '').strip()
    if not a: return 'Empty or image'
    if PBN.search(a): return 'Spam: keyword stuffed SEO sales copy'
    if CANOPY.search(a) and not NAKED.match(a):
        # anything this long is a sentence scraped from body copy, not an anchor a
        # partner would recognise as a placement they bought
        if len(a)>120: return 'Contextual or other'
        return 'Exact match commercial (geo)' if GEO.search(a) else 'Exact match commercial'
    if GENERIC.match(a): return 'Generic'
    if NAKED.match(a) or re.match(r'^[a-z0-9.-]+\.(com|net|org|info)/?$',a,re.I): return 'Naked URL'
    if BRAND.search(a): return 'Branded'
    return 'Contextual or other'
for r in LINKS:
    r['atype']=anchor_type(r['anchor'])
    if r['ltype'] in ('image','redirect') and r['atype'].startswith('Exact match'):
        r['atype']='Empty or image'

SEM_HOSTS={r['rd'] for r in RAW if r['tool']=='Semrush'}
AHR_HOSTS={r['rd'] for r in RAW if r['tool']=='Ahrefs'}
by=collections.defaultdict(list)
for r in LINKS: by[r['rd']].append(r)
ALLDOM=set(by)|set(SEM)|set(AHR)

out=[]
for d in ALLDOM:
    rs=by.get(d,[])
    sem,ahr=SEM.get(d),AHR.get(d)
    # Semrush's referring-domain report is registered-domain level while its link
    # file carries subdomain hosts, so membership of the link files counts too.
    in_sem=(d in SEM) or (d in SEM_HOSTS); in_ahr=(d in AHR) or (d in AHR_HOSTS)
    src='Both' if (in_sem and in_ahr) else ('Semrush' if in_sem else 'Ahrefs')
    asc=int(num(sem['ascore'])) if sem else (int(num(EXTRA[d]['ascore'])) if d in EXTRA else '')
    # Semrush's referring-domain report does not return the referring domain's OWN
    # referring-domain count, so this is populated only where the bulk fetch supplied it.
    srd=int(num(EXTRA[d]['domains'])) if (not sem and d in EXTRA) else ''
    dr=num(ahr['dr']) if ahr else (num(AHDR[d]) if d in AHDR else '')
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
    has_exact=types['Exact match commercial (geo)']+types['Exact match commercial']>0
    casino=any(CASINO.search(d) or CASINO.search(x['anchor'] or '') for x in rs) or CASINO.search(d)
    ah_spam=(ahr or {}).get('is_spam')=='true'
    spam_title=any(SPAMTITLE.search(x['source_title'] or '') for x in rs)
    pr=bool(PRNET.search(d))
    listed=any(CLIENTPAGE.search(x['source_title'] or '') and not SALESCOPY.search(x['source_title'] or '')
               for x in rs)
    svc_listed=any(CLIENTSERVICE.search(x['source_title'] or '') and not SALESCOPY.search(x['source_title'] or '')
               for x in rs)
    eff_auth=asc if asc!='' else (dr/10 if dr!='' else 0)   # Semrush AS first, DR as fallback

    parent='.'.join(d.split('.')[-2:])
    if d in OWN or parent in OWN: status,grp='Own Site','Client owned property'
    elif d in KEEP_SEED: status,grp='Keep','Genuine or editorial'
    elif asc!='' and asc>=20: status,grp='Keep','Genuine site, Semrush Authority Score 20 or above'
    elif parent in KEEP_SEED and parent!=d and not (has_pbn or casino or spam_title or SPAMNAME.search(d)):
        status,grp='Keep',f'Genuine or editorial (subdomain of {parent})'
    elif parent in KEEP_SEED and parent!=d:
        # The parent is genuine but this subdomain carries link scheme evidence of its own,
        # so neither keeping nor disavowing it follows from the parent. The client decides.
        status,grp=('Review (Conflicts With Parent)',
                    f'Parent {parent} is genuine, but this subdomain serves a link scheme page')
    elif has_exact and has_pbn: status,grp='Held (Review)','Mixes exact match commercial with link scheme anchors'
    elif has_exact and nof==len(rs) and rs:
        status,grp='Held (Nofollow, No Action)','Exact match commercial anchor, every link is nofollow and passes no ranking value'
    elif has_exact: status,grp='Held (Pending Partner)','Exact match commercial anchor, confirm who commissioned'
    elif pr and rs: status,grp='Held (Pending Partner)','Press release syndication, confirm who commissioned'
    elif listed and not has_pbn:
        status,grp='Keep','Business listing or editorial mention naming the client'
    elif svc_listed and not has_pbn:
        status,grp='Held (Pending Partner)','Directory listing page titled after the client service, confirm who commissioned'
    elif casino: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Off topic casino or pharma anchor'
    elif has_pbn: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Automated PBN and service advertising anchor network'
    elif not rs:
        if SPAMNAME.search(d) or JUNKTLD.search(d) or SPAMIP.match(ip) or ah_spam or eff_auth<=6:
            status,grp='Review (No Link Sample)','Spam signature or low authority, no link sample to confirm dofollow'
        else: status,grp='Keep','Genuine or harmless link'
    elif SPAMNAME.search(d): status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'SEO tool and link selling network domain'
    elif SPAMIP.match(ip) or spam_title: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Link network host (shared IP, templated page)'
    elif JUNKTLD.search(d) or eff_auth<=2: status,grp=('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'),'Low authority directory or bookmark placement'
    else: status,grp='Keep','Genuine or harmless link'

    if re.search(r'bookmark|bmark|social',d,re.I): st='Social bookmarking site'
    elif pr: st='PR and news distribution'
    elif re.search(r'article|blog|content|post|news|magz|diary|writers|story|times|tribune|journal',d,re.I): st='Guest article or content farm'
    elif d in KEEP_SEED or d in OWN: st='Genuine site'
    else: st='Low quality web directory'

    seen_both=any(x.get('seen_in')=='Both' for x in rs)
    tools=sorted({x['tool'] for x in rs})
    tool=('Both' if (seen_both or len(tools)>1) else (tools[0] if tools else src))
    out.append(dict(domain=d,status=status,group=grp,sitetype=st,ascore=asc,semrush_rd=srd,dr=dr,source=src,
        tool=tool,backlinks=bl,dofollow=dof if rs else '',nofollow=nof if rs else '',
        first_seen=first,ip=ip,country=country,top_anchor=top,
        example_page=rs[0]['source_url'] if rs else '',page_title=rs[0]['source_title'] if rs else '',
        atypes='; '.join(f'{k} x{v}' for k,v in types.most_common()) or '(not in link sample)',
        tab03='Yes' if d in TAB03 else '',redundant='',disavow_line='domain:'+d))

# A nameserver or demo hostname is infrastructure, not a site of its own, but it still
# carries whatever anchor it carries. It is classified on that anchor like anything else;
# the hostname is noted in the group so nobody reads it as a separate placement.
ARTEFACT=re.compile(r'^(ns[0-9]+|demo[0-9]*|mail|web|cpanel|webmail|ftp)\.',re.I)
for x in out:
    if ARTEFACT.match(x['domain']):
        x['group']+=". Served on a nameserver or demo hostname of "+'.'.join(x['domain'].split('.')[1:])+", not a site of its own"
# Linking pages checked by hand and found dead. The link is gone, so there is nothing
# to disavow; the status stays out of the file and the group says why.
DEAD={}
try:
    for _l in open(D+'dead_pages.txt'):
        _l=_l.strip()
        if _l and not _l.startswith('#'):
            _p=_l.split(';'); DEAD[_p[0]]=_p[1]
except FileNotFoundError: pass
for x in out:
    if x['domain'] in DEAD:
        x['group']=f"{x['group']}. Linking page checked by hand and dead ({DEAD[x['domain']]}), so the link is gone"
        if x['status']=='Spam (Disavow)': x['status']='Review (Host Artefact)'
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
        # Only inherit a clean parent where the child shows nothing of its own. A child that
        # was classed spam on its own anchor or page title is a conflict, not a clean link.
        if x['group'].startswith(('Automated PBN','Off topic casino','Link network host','SEO tool')):
            x['status']='Review (Conflicts With Parent)'
            x['group']=f'Parent {parent} is genuine, but this subdomain serves a link scheme page'
        else:
            x['status']=pst; x['group']=f'Genuine or editorial (subdomain of {parent})'
        promoted+=1
    elif pst.startswith('Review') and x['status'].startswith('Spam'):
        x['status']='Review (Parent Unresolved)'; x['group']=f'Parent {parent} unresolved, client to confirm'; promoted+=1
    elif pst=='Spam (Disavow)' and x['status']=='Spam (Disavow)':
        x['group']+=f' (covered by domain:{parent})'; x['redundant']='Yes'; redundant+=1
for x in out:
    if x['status']=='Keep' and x['group'].startswith('Genuine or harmless'):
        a=x['ascore'] if x['ascore']!='' else (x['dr']/10 if x['dr']!='' else 0)
        if a<=6:
            x['status']='Review (Low Authority)'
            x['group']='Low authority site with no editorial signal, client to confirm keep or disavow'; demoted+=1
# Last word, after every inference: a domain the client ruled on by hand.
for x in out:
    if x['domain'] in CLIENT_DISAVOW:
        x['status']='Spam (Disavow)'
        x['group']='Link selling page, reviewed and disavowed by the client'
        x['disavow_line']='domain:'+x['domain']
        x['redundant']=''
for x in out:
    if x['status']!='Spam (Disavow)': x['disavow_line']=''
assert not [x for x in out if x['disavow_line'] and x['status']!='Spam (Disavow)']
print(f"post-pass: {promoted} subdomains inherited parent status, {redundant} redundant child lines, {demoted} low-authority Keeps -> Review")

out.sort(key=lambda x:(x['status'],-x['backlinks'],x['domain']))
with open(D+'domain_audit.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys()),delimiter=';'); w.writeheader(); w.writerows(out)
with open(D+'links_all.csv','w',newline='') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(['rd','tool','seen_in','ltype','source_url','source_title','target_url','anchor','atype','nofollow','first_seen'])
    for r in sorted(LINKS,key=lambda x:(x['rd'],x['tool'],x['anchor'] or '')):
        w.writerow([r['rd'],r['tool'],r['seen_in'],r['ltype'],r['source_url'],r['source_title'],r['target_url'],r['anchor'],r['atype'],r['nofollow'],r['first_seen']])

print("\n=== STATUS ===")
for k,v in collections.Counter(x['status'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("  TOTAL",len(out))
print("\n=== SOURCE ===")
for k,v in collections.Counter(x['source'] for x in out).most_common(): print(f"  {v:5d}  {k}")
print("\n=== ANCHOR TYPES (links) ===")
for k,v in collections.Counter(r['atype'] for r in LINKS).most_common(): print(f"  {v:5d}  {k}  ({v/len(LINKS)*100:.1f}%)")
print(f"\nlinks total: {len(LINKS)}  (Semrush {sum(1 for r in LINKS if r['tool']=='Semrush')}, Ahrefs {sum(1 for r in LINKS if r['tool']=='Ahrefs')})")
print("Tab03:",collections.Counter(x['status'] for x in out if x['tab03']=='Yes'))
