#!/usr/bin/env python3
"""Backlink audit + disavow validation for ngwindows.com
Merges Ahrefs + Semrush referring domains and applies multi-signal validation.
Each flagged domain gets a category, a confidence tier, and explicit evidence.
"""
import csv, re, datetime, collections

def ts(v):
    try: return datetime.datetime.utcfromtimestamp(int(v)).strftime('%Y-%m-%d')
    except: return ''
def isots(v):
    return (v or '')[:10]

# ---------- load Ahrefs ----------
ah = {}
with open('ahrefs_refdomains.csv') as f:
    for r in csv.DictReader(f):
        d = r['domain'].strip().lower()
        if not d: continue
        ah[d] = {
            'dr': float(r['domain_rating'] or 0),
            'traffic': int(r['traffic_domain'] or 0),
            'links': int(r['links_to_target'] or 0),
            'dofollow': int(r['dofollow_links'] or 0),
            'is_spam': str(r['is_spam']).lower()=='true',
            'positions': int(r['positions_source_domain'] or 0),
            'ip': (r['ip_source'] or '').strip(),
            'first': isots(r['first_seen']), 'last': isots(r['last_seen']),
        }

# ---------- load Semrush ----------
sm = {}
with open('semrush_refdomains.csv') as f:
    for r in csv.DictReader(f, delimiter=';'):
        d = r['domain'].strip().lower()
        if not d: continue
        sm[d] = {
            'ascore': int(r['domain_score'] or 0),
            'trust': int(r['domain_trust_score'] or 0),
            'links': int(r['backlinks_num'] or 0),
            'ip': (r['ip'] or '').strip(),
            'country': (r['country'] or '').strip(),
            'first': ts(r['first_seen']), 'last': ts(r['last_seen']),
        }

all_domains = sorted(set(ah) | set(sm))

# ---------- IP cluster detection (link networks) ----------
# Exclude shared CDN / big-cloud ranges: an IP there is shared by millions of
# unrelated sites, so co-location is NOT evidence of a private link network.
CDN_PREFIXES = ('104.16.','104.17.','104.18.','104.19.','104.20.','104.21.','104.22.',
 '104.23.','104.24.','104.25.','104.26.','104.27.','104.28.','172.64.','172.65.','172.66.',
 '172.67.','172.68.','172.69.','172.70.','172.71.','188.114.','162.159.','131.0.72.','151.101.',
 '142.250.','142.251.','172.253.','173.194.','64.233.','192.178.','192.179.','108.177.',
 '150.171.','66.102.','216.58.','34.','35.','3.','13.','18.','20.','52.','54.','23.','2.','5.161.')
def is_cdn(ip): return ip.startswith(CDN_PREFIXES)

ipmap = collections.defaultdict(list)
for d in all_domains:
    ip = (sm.get(d,{}).get('ip') or ah.get(d,{}).get('ip') or '').strip()
    if ip and not is_cdn(ip): ipmap[ip].append(d)
# a NON-CDN IP shared by >=4 distinct referring domains = dedicated link network
network_ips = {ip:doms for ip,doms in ipmap.items() if len(doms)>=4}

# ---------- whitelist: legitimate / high-authority ----------
WHITELIST = {
 'apple.com','yahoo.com','bing.com','pinterest.com','bbb.org','yellowpages.com',
 'nextdoor.com','zoominfo.com','glass.com','glassonweb.com','chamberofcommerce.com',
 'porch.com','constantcontact.com','constantcontactpages.com','superpages.com',
 'dexknows.com','expertise.com','fixr.com','housedigest.com','moneytalksnews.com',
 'owler.com','inkl.com','barbend.com','accio.com','seamless.ai','castbox.fm',
 'coroflot.com','brightside.me','diamondcertified.org','qualifiedremodeler.com',
 'windowanddoor.com','windowdigest.com','dwmmag.com','growjo.com','enigma.com',
 'bloomberry.com','neverbounce.com','arounddeal.com','wiza.co','conves.io',
 'weblancer.net','re-thinkingthefuture.com','24-7pressrelease.com','vsbattles.com',
 'processregister.com','growthzoneapp.com','williamsonchamber.com','infinitywindows.com',
 'energyswingwindows.com','parse.gl','glarity.app','tntcode.com','hometownstation.com',
}

FREE_HOSTS = ('.blogspot.com','.pages.dev','.azurewebsites.net','.freemyip.com',
              '.web.app','.wordpress.com')

# ---------- pattern signals ----------
def matches(d, pat): return re.search(pat, d) is not None

LINK_SELLER = r'(backlink|baclink|seolink|seobacklink|buyseolinks|linkbuy|buylink|guestpost|rankvance|qualitybacklinks|welinkbacklinks|linksnatcher|daolink|skylinkseo|trafficbooster|increasewebtraffic|worldbusinesspromote|goooogla|newblogerseo|blogerreviewers|mediaboooster|clicktobuy|quickseolinks|rarebacklinks|superbquality|viralbacklinks|eliteseo|bestrank|bestsites|buyrank|buyfair|booastranking|friendlybacklinks|webranking|topratedbacklinks|allbaclinks|atozbacklinks|99backlinks|blinks\.)'
GAMBLING   = r'(casino|poker|betwinner|ufabet|slot|pick4d|truebookies|m98ufa|\bbet\b|4d\.live|onlinegaming|hotonline)'
ADULT      = r'(porn|xxx|\bsex\b|ineed2pee|submissive|dominated)'
STATSPAM   = r'(webstats|websiteworth|worthchecker|domainanalysis|siteprice|sitelike|domaineye|gsitestatus|seodomains|websitescrawl|websiterace|domainsc\.com|getwebsiteworth|webworthchecker|complaintinfo|gsitestatus|siteprice|domaineye)'
DIR_SPAM   = r'(webdirectory|allwebsitesdirectory|newwebsiteslist|alltopleveldomains|topleveldomains|yesdomains|all-aged-domains|domainwork|domains\.space|uklistingz|toplist\.co|01webdirectory|trendspotdirectory|directorylinkservice)'
SHORTENER  = r'(shorten|shrink|byteshort|anchorurl|atomizelink|urls-shortener|screenshots\.wiki|buzzshrink|\.icu$)'
DOMRAIDER  = r'(domraider|expireddomain|all-aged-domains|alltopleveldomains)'

MOLDOVA_IP = '195.20.19.178'
KNOWN_FARM_IPS = {'203.161.54.114','118.139.181.85','118.139.176.46','118.139.178.200',
                  '118.139.161.199','118.139.181.255','184.168.115.60','184.168.111.168',
                  '184.168.116.137','184.168.113.185','118.139.178.110','118.139.177.45',
                  '184.168.108.151','184.168.109.253','184.168.107.83'}

rows=[]
for d in all_domains:
    a=ah.get(d,{}); s=sm.get(d,{})
    dr=a.get('dr',0.0); asc=s.get('ascore',0)
    auth=max(dr,asc)
    traffic=a.get('traffic',0); positions=a.get('positions',0)
    is_spam=a.get('is_spam',False)
    ip=(s.get('ip') or a.get('ip') or '').strip()
    country=s.get('country','')
    links=max(a.get('links',0), s.get('links',0))
    src=[]
    if d in ah: src.append('ahrefs')
    if d in sm: src.append('semrush')
    sources='+'.join(src)

    reasons=[]; cat=''; conf=''; signals=[]
    is_free=d.endswith(FREE_HOSTS)

    # ---- a hard "footprint" = self-evident spam category (name-based / free-host) ----
    footprint=None
    if matches(d,LINK_SELLER): footprint='Link-selling / SEO-service PBN'
    elif d.endswith('.blogspot.com'): footprint='Blogspot PBN / spam post'
    elif matches(d,GAMBLING): footprint='Gambling / casino spam'
    elif matches(d,ADULT): footprint='Adult spam'
    elif matches(d,SHORTENER) or ip==MOLDOVA_IP: footprint='URL-shortener / redirect link network'
    elif matches(d,DOMRAIDER): footprint='Expired-domain / auto network'
    elif matches(d,STATSPAM): footprint='Auto-generated stats / worth-checker'
    elif matches(d,DIR_SPAM): footprint='Low-quality directory / TLD list'
    elif is_free: footprint='Free-host throwaway page'

    # ---- whitelist / keep: high authority AND not a hard spam-seller/gambling/adult footprint ----
    hard_toxic = footprint in ('Link-selling / SEO-service PBN','Gambling / casino spam',
                               'Adult spam','URL-shortener / redirect link network',
                               'Blogspot PBN / spam post','Expired-domain / auto network')
    if d in WHITELIST or (auth>=30 and not is_free and not hard_toxic and ip!=MOLDOVA_IP):
        rows.append(dict(domain=d,sources=sources,dr=dr,ascore=asc,traffic=traffic,
            positions=positions,is_spam=is_spam,links=links,ip=ip,country=country,
            first=s.get('first') or a.get('first',''),last=s.get('last') or a.get('last',''),
            category='LEGITIMATE / high-authority',confidence='KEEP',
            evidence=f'authority={auth:.0f} (DR{dr:.0f}/AS{asc}); recognized or strong domain — do NOT disavow'))
        continue

    # ---- independent corroborating signals (S1..S6) ----
    if is_spam:
        signals.append('S:Ahrefs-is_spam=true')
    if ip in network_ips and ip:
        signals.append(f'S:link-network IP {ip} (+{len(network_ips[ip])-1} sibling domains)')
    if ip in KNOWN_FARM_IPS:
        signals.append('S:known link-farm IP block')
    if country=='md':
        signals.append('S:Moldova spam cluster')
    if auth<=3 and traffic==0 and positions==0:
        signals.append(f'S:dead (auth={auth:.0f}, 0 traffic, 0 keywords)')
    elif traffic==0 and positions==0 and auth<=6:
        signals.append(f'S:no organic traffic/keywords (auth={auth:.0f})')

    nsig=len(signals)

    # ---- tiering ----
    if footprint:
        cat=footprint
        # name/free-host footprints are self-evident -> HIGH (stats/dir are softer -> MEDIUM unless corroborated)
        if footprint in ('Auto-generated stats / worth-checker','Low-quality directory / TLD list','Free-host throwaway page'):
            conf='HIGH' if nsig>=1 else 'MEDIUM'
        else:
            conf='HIGH'
        reasons.append('footprint: '+footprint)
    elif nsig>=2:
        cat='Multi-signal spam'; conf='HIGH'
        reasons.append('two or more independent toxic signals')
    elif nsig==1:
        cat='Single-signal low-quality'; conf='MEDIUM'
        reasons.append('one strong toxic signal')
    elif auth<=6:
        cat='Low-authority (needs review)'; conf='REVIEW'
        reasons.append(f'low authority={auth:.0f}; no hard spam footprint')
    else:
        cat='Unclear — manual review'; conf='REVIEW'
        reasons.append(f'authority={auth:.0f}; borderline')

    reasons.extend(signals)

    rows.append(dict(domain=d,sources=sources,dr=dr,ascore=asc,traffic=traffic,
        positions=positions,is_spam=is_spam,links=links,ip=ip,country=country,
        first=s.get('first') or a.get('first',''),last=s.get('last') or a.get('last',''),
        category=cat,confidence=conf,evidence=' | '.join(reasons)))

# ---------- write merged CSV ----------
cols=['domain','sources','confidence','category','dr','ascore','traffic','positions',
      'is_spam','links','ip','country','first','last','evidence']
with open('merged_all_domains.csv','w',newline='') as o:
    w=csv.DictWriter(o,fieldnames=cols); w.writeheader()
    for r in sorted(rows,key=lambda x:(x['confidence'],x['domain'])): w.writerow(r)

# ---------- flagged for review (exclude KEEP) ----------
order={'HIGH':0,'MEDIUM':1,'REVIEW':2}
flagged=[r for r in rows if r['confidence']!='KEEP']
flagged.sort(key=lambda x:(order[x['confidence']],x['category'],x['domain']))
with open('disavow_flagged_for_review.csv','w',newline='') as o:
    w=csv.DictWriter(o,fieldnames=cols); w.writeheader()
    for r in flagged: w.writerow(r)

# ---------- disavow.txt (HIGH + MEDIUM) ----------
def disavow_line(d):
    return f'domain:{d}'
high=[r for r in flagged if r['confidence']=='HIGH']
med =[r for r in flagged if r['confidence']=='MEDIUM']
rev =[r for r in flagged if r['confidence']=='REVIEW']
with open('disavow.txt','w') as o:
    o.write('# Disavow file for ngwindows.com\n')
    o.write(f'# Generated {datetime.date.today()} from Ahrefs + Semrush referring-domain audit\n')
    o.write('# Review before submitting to Google Search Console Disavow Tool.\n')
    o.write(f'# HIGH-confidence (strong spam footprint): {len(high)} domains\n')
    o.write(f'# MEDIUM-confidence (recommended, verify): {len(med)} domains\n#\n')
    bycat=collections.defaultdict(list)
    for r in high: bycat[r['category']].append(r['domain'])
    o.write('# ===== HIGH CONFIDENCE =====\n')
    for c in sorted(bycat):
        o.write(f'# -- {c} ({len(bycat[c])}) --\n')
        for d in sorted(bycat[c]): o.write(disavow_line(d)+'\n')
    o.write('#\n# ===== MEDIUM CONFIDENCE (verify before submit) =====\n')
    bycat=collections.defaultdict(list)
    for r in med: bycat[r['category']].append(r['domain'])
    for c in sorted(bycat):
        o.write(f'# -- {c} ({len(bycat[c])}) --\n')
        for d in sorted(bycat[c]): o.write(disavow_line(d)+'\n')

# ---------- stats ----------
from collections import Counter
conf_c=Counter(r['confidence'] for r in rows)
cat_c=Counter(r['category'] for r in rows if r['confidence']!='KEEP')
print('TOTAL unique referring domains:',len(all_domains))
print('  ahrefs-only:',len(set(ah)-set(sm)),' semrush-only:',len(set(sm)-set(ah)),' both:',len(set(ah)&set(sm)))
print('Confidence:',dict(conf_c))
print('Disavow.txt entries: HIGH',len(high),'+ MEDIUM',len(med),'=',len(high)+len(med))
print('REVIEW (manual, not in disavow):',len(rev))
print('KEEP (protected/whitelist):',conf_c['KEEP'])
print('\nCategory breakdown (flagged):')
for c,n in cat_c.most_common(): print(f'  {n:3d}  {c}')
print('\nTop link-network IPs (>=4 domains):')
for ip,doms in sorted(network_ips.items(),key=lambda x:-len(x[1]))[:12]:
    print(f'  {len(doms):3d}  {ip}')
