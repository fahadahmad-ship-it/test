import csv, re, os, datetime, json

RAW = 'raw'
OUT = 'out'
os.makedirs(OUT, exist_ok=True)

def low(s): return (s or '').lower()

# ---------- keyword signatures ----------
TELEGRAM = ['telegram', 't.me']
SPAM_SALES = [
    'backlink', 'guest post', 'guest posting', 'dofollow', 'pbn', 'da 50', 'da 40',
    'dr/da/tf', 'dr80', 'dr 80', 'domain authority', 'domain rating', 'trust flow',
    'majestic', 'moz domain', 'ahrefs domain rating', 'seoexpress', 'uplinke', 'itxoft',
    'rankva', 'sitetosocial', 'sitetosocial.com', 'rank first page', 'buy backlinks',
    'link building', 'serp', 'outrank', 'tiered link', 'premium seo', 'white hat',
    'indexation', 'link reclamation', 'link profile', 'link velocity', 'high-dr',
    'high quality dofollow', 'keyword research in southeast', 'infographic links',
    'top rank', 'seo authority', 'authority backlinks', 'gambling accepted', 'page one',
    'e-commerce seo', 'economical backlink', 'next-level solutions',
    'grow your website traffic', 'domain metrics', 'skyrocket', 'rank callturfsup',
    'strengthen your link', 'contextual backlinks', 'saas tools', 'automation tools',
    'da/dr', 'pinterest tool', 'da dr', 'web development', 'seo link',
]
ECOM_INJECTION = [
    'on sale', 'hot sale', 'hotsell', 'hot-sale', 'hotsale', 'for sale', 'best sale',
    'sale care', 'care secrets', 'clearance', 'new arrivals', 'new arrival', 'discount',
    'outlet', 'army grub', 'providers', 'on-sale', ' sales ', 'in store', 'shop',
    'store ', ' store', '2024', '2025',
]
GEO = ['gainesville', 'haymarket', 'south riding', 'northern virginia', 'prince william']
SERVICE = [
    'lawn care', 'lawn treatment', 'lawn maintenance', 'lawn aeration', 'aeration',
    'weed control', 'weed killer', 'flea and tick', 'flea & tick', 'flea tick',
    'mosquito', 'irrigation', 'pest control', 'fertiliz', 'overseeding', 'grub',
    'lawn spray', 'tick', 'chigger', 'core aeration',
]
# non-geo exact-match commercial anchors that target service pages
NONGEO_COMMERCIAL = {
    'irrigation maintenance', 'lawn care plan', 'core aeration', 'weed control',
    'professional lawn aeration service', 'lawn care providers',
}
BRAND_EXACT = {
    'callturfsup.com', 'www.callturfsup.com', 'callturfsup', "turf's up", 'turf’s up',
    "turf's up!", 'turfs up', '© turf’s up', 'from turf’s up', 'website',
    'visit website', 'source', 'image source', 'go now', 'visit their website',
    "visit the turf's up site for lawn programs & pricing", '\U0001f517', '', ' ',
    'view complete answer on callturfsup.com', 'icon - external link visit website',
    'virginia', 'core aeration',
}

def is_naked_url(a):
    al = low(a)
    return al.startswith('http') or al.startswith('www.callturfsup') or \
           al.startswith('callturfsup.com') or 'callturfsup.com/' in al

def has(a, kws):
    al = low(a); return any(k in al for k in kws)

def anchor_class(anchor):
    a = anchor or ''
    al = low(a)
    if has(a, TELEGRAM):               return 'telegram'
    if has(a, SPAM_SALES):             return 'spam_sales'
    if has(a, ECOM_INJECTION):         return 'ecom_injection'
    # Held: exact-match commercial (geo service, or known non-geo commercial)
    if has(a, GEO) and has(a, SERVICE):return 'held_geo'
    if al.strip() in NONGEO_COMMERCIAL:return 'held_commercial'
    if al.strip() in BRAND_EXACT or is_naked_url(a): return 'brand'
    return 'other'   # resolve via is_spam flag

SPAM_CLASSES = {'telegram', 'spam_sales', 'ecom_injection'}
HELD_CLASSES = {'held_geo', 'held_commercial'}

def bucket(cls, is_spam, is_dofollow):
    held = cls in HELD_CLASSES
    spammy = (cls in SPAM_CLASSES) or (cls == 'other' and is_spam)
    if held:
        return 'Held (Pending Partner)' if is_dofollow else 'Held (Nofollow, No Action)'
    if spammy:
        return 'Spam (Disavow)' if is_dofollow else 'Spam (Nofollow, No Action)'
    return 'Clean (No Action)'

# ---------- load Semrush ----------
sem = {}   # domain -> dict
with open(f'{RAW}/semrush_refdomains.csv') as f:
    for r in csv.DictReader(f):
        d = r['domain'].strip().lower()
        if not d: continue
        def epoch(x):
            try: return datetime.date.fromtimestamp(int(x)).isoformat()
            except: return ''
        sem[d] = {'as': r.get('domain_score',''), 'trust': r.get('domain_trust_score',''),
                  'first': epoch(r.get('first_seen','')), 'last': epoch(r.get('last_seen','')),
                  'ip': r.get('ip',''), 'country': r.get('country','')}
if os.path.exists(f'{RAW}/semrush_p3_domains.txt'):
    for line in open(f'{RAW}/semrush_p3_domains.txt'):
        d = line.strip().lower()
        if d and d not in sem:
            sem[d] = {'as':'', 'trust':'', 'first':'', 'last':'', 'ip':'', 'country':''}

# ---------- load Ahrefs & classify ----------
rows = list(csv.DictReader(open(f'{RAW}/backlinks.csv')))
ahrefs_domains = set()
master = []
for r in rows:
    d = r['root_name_source'].strip().lower()
    ahrefs_domains.add(d)
    anchor = r['anchor']
    is_spam = r['is_spam'] == '1'
    is_df = r['is_dofollow'] == '1'
    cls = anchor_class(anchor)
    b = bucket(cls, is_spam, is_df)
    in_sem = d in sem
    master.append({
        'domain': d, 'bucket': b, 'anchor_class': cls,
        'source': 'Ahrefs+Semrush' if in_sem else 'Ahrefs',
        'is_dofollow': 'dofollow' if is_df else 'nofollow',
        'is_spam_ahrefs': '1' if is_spam else '0',
        'top_anchor': anchor, 'target_url': r['url_to'], 'example_page': r['url_from'],
        'dr_ahrefs': r['domain_rating_source'], 'as_semrush': sem.get(d,{}).get('as',''),
        'traffic': r['traffic_domain'], 'ip': r['ip_source'],
        'first_seen': (r['first_seen_link'][:10] if r['first_seen_link'] else ''),
        'links_grouped': r['link_group_count'],
    })

# ---------- Semrush-only domains ----------
SPAM_NAME = re.compile(r'(backlink|seocheck|dachecker|pachecker|prchecker|rankchecker|'
    r'rankingchecker|trafficchecker|trafficgrow|trafficforseo|seotool|seobiz|seogeko|'
    r'linkbuilding|bookmark|submitarticle|articles?|directory|dir\.|checker|traffic|'
    r'whitehatbacklinks|wholinkstomysite|webrank|websiteseo|websitescrawl|seo\.|\.seo|'
    r'trustflow|domainrating|linkz|weblink|getwebsiteworth|indexaward|rank\.|ranking\.)')
SPAM_TLD = re.compile(r'\.(shop|store|space|website|online|site|link|icu|best|art|cv)$')

semrush_only_spam = []
semrush_only_review = []
for d, info in sem.items():
    if d in ahrefs_domains:
        continue
    name_spam = bool(SPAM_NAME.search(d)) or bool(SPAM_TLD.search(d))
    rec = {'domain': d, 'bucket': 'Spam (Disavow) [Semrush-only]' if name_spam else 'Review (Semrush-only)',
           'anchor_class': 'semrush_only', 'source': 'Semrush',
           'is_dofollow': 'unknown', 'is_spam_ahrefs': '',
           'top_anchor': '', 'target_url': '', 'example_page': '',
           'dr_ahrefs': '', 'as_semrush': info.get('as',''), 'traffic': '',
           'ip': info.get('ip',''), 'first_seen': info.get('first',''), 'links_grouped': ''}
    (semrush_only_spam if name_spam else semrush_only_review).append(rec)

# ---------- write master ----------
cols = ['domain','bucket','anchor_class','source','is_dofollow','is_spam_ahrefs',
        'top_anchor','target_url','example_page','dr_ahrefs','as_semrush','traffic',
        'ip','first_seen','links_grouped']
allrecs = master + semrush_only_spam + semrush_only_review
with open(f'{OUT}/domains_master.csv','w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for rec in allrecs: w.writerow(rec)

# ---------- summary ----------
from collections import Counter
bc = Counter(r['bucket'] for r in allrecs)
print('=== BUCKET COUNTS (domains) ===')
for b,n in bc.most_common(): print(f'{n:5d}  {b}')
print('total records:', len(allrecs))
print('ahrefs live domains:', len(ahrefs_domains))
print('semrush domains:', len(sem))
print('semrush-only spam(name):', len(semrush_only_spam), '| semrush-only review:', len(semrush_only_review))
both = sum(1 for r in master if r['source']=='Ahrefs+Semrush')
print('ahrefs domains also in semrush:', both, '| ahrefs-only:', len(master)-both)
