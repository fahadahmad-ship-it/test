"""Classify the kandkmfg.com referring domains and decide what goes in the disavow file.

Semrush is the source for every metric. The client's Ahrefs exports are used only to
discover links Semrush missed and to confirm a linking page is still live.

One thing shapes this audit and is worth stating up front: just over half the links
reach kandkmfg.com through a redirect from two other domains the client controls,
gaworktrucks.com and kandkmanufacturing.com. Google processes a disavow file per
Search Console property, so a file filed on kandkmfg.com does nothing for the links
pointing at the other two. The three are therefore kept apart all the way through and
each gets its own file.
"""
import csv, collections, glob, re, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import read_semrush, host

D = '/home/user/test/kk/data/'
CLIENT = 'kandkmfg.com'
# Properties the client controls. Links to the other two arrive at kandkmfg.com only
# because those domains redirect; they still live on their own Search Console property.
OWN = {'kandkmfg.com', 'kandkmanufacturing.com', 'gaworktrucks.com'}

# The nine referring domains the client's own audit named in Tab 05.
TAB05 = {'takes.sbs', 'seol.store', 'goooogla.com', 'seodomains.website', 'getwebsiteworth.com',
         'allwebsitesdirectory.com', 'domainanalysis.org', 'wants.cfd', 'factmags.com'}

def num(x):
    try: return float(str(x).replace(',', '') or 0)
    except Exception: return 0.0

# ---------------- links ----------------
LINKS = []
_, srows, bad = read_semrush(glob.glob(D + 'fetch/b*.csv'))
if bad: print(f'warning: {len(bad)} Semrush rows could not be parsed')
seen = set()
for r in srows:
    k = (r['source_url'], r['target_url'], r['anchor'])
    if k in seen: continue
    seen.add(k)
    LINKS.append(dict(rd=host(r['source_url']), tool='Semrush', source_url=r['source_url'],
                      source_title=r['source_title'], target_url=r['target_url'], anchor=r['anchor'],
                      nofollow=r['nofollow'], first_seen=r['first_seen'], last_seen=r['last_seen'],
                      response_code=r['response_code'], redirect_url=r['redirect_url'],
                      page_ascore=r['page_ascore']))

# Ahrefs adds sites Semrush never indexed, and confirms a page is live.
AH = list(csv.DictReader(open(D + 'refdomains.tsv', encoding='utf-8-sig'), delimiter='\t'))
AHL = list(csv.DictReader(open(D + 'backlinks.tsv', encoding='utf-8-sig'), delimiter='\t'))
def canon(u):
    u = (u or '').strip().lower().split('#')[0]
    u = re.sub(r'^https?://', '', u); u = re.sub(r'^www\.', '', u)
    return u.rstrip('/')
def ah_ts(v):
    # Ahrefs ships 'First seen' as 'YYYY-MM-DD HH:MM:SS'. Semrush first_seen is a unix
    # timestamp, so convert, keeping the two sources in one comparable format.
    v = (v or '').strip()
    if not v: return ''
    try: return str(int(datetime.datetime.strptime(v[:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.UTC).timestamp()))
    except Exception: return ''
have = {(canon(r['source_url']), canon(r['target_url']), (r['anchor'] or '').strip().lower()) for r in LINKS}
added = 0
for r in AHL:
    k = (canon(r['Referring page URL']), canon(r['Target URL']), (r['Anchor'] or '').strip().lower())
    if k in have: continue
    have.add(k); added += 1
    LINKS.append(dict(rd=host(r['Referring page URL']), tool='Ahrefs', source_url=r['Referring page URL'],
                      source_title=r['Referring page title'], target_url=r['Target URL'], anchor=r['Anchor'],
                      nofollow='true' if r['Nofollow'] == 'true' else 'false',
                      first_seen=ah_ts(r.get('First seen')), last_seen=ah_ts(r.get('Last seen')),
                      response_code=r['Referring page HTTP code'], redirect_url='', page_ascore=''))
LINKS = [r for r in LINKS if r['rd']]
print(f'links: {len(srows):,} Semrush rows, {len(LINKS):,} unique after merging the Ahrefs export '
      f'({added:,} links only Ahrefs had)')

# Live-page confirmation, from whichever tool last fetched the page.
LIVE = {}
for r in AHL:
    LIVE[canon(r['Referring page URL'])] = (r['Referring page HTTP code'] == '200' and not r['Lost'])
for r in LINKS:
    if r['tool'] == 'Semrush' and r['response_code'] == '200':
        LIVE.setdefault(canon(r['source_url']), True)

# ---------------- which client property each link actually points at ----------------
def prop(r):
    h = host(r['redirect_url']) if r['redirect_url'].strip() else host(r['target_url'])
    return h if h in OWN else CLIENT
for r in LINKS:
    r['property'] = prop(r)

# ---------------- domain metrics ----------------
SEM = {}
_, rrows, rbad = read_semrush(glob.glob(D + 'rd/rd*.csv'))
if rbad: print(f'warning: {len(rbad)} referring-domain rows could not be parsed')
for r in rrows:
    SEM.setdefault(r['domain'], r)
# Semrush returns a domain's Authority Score from three reports and they do not always
# agree. The bulk comparison report and the per domain overview report match each other;
# the referring-domain report is the odd one out and runs up to 11 points low. Prefer the
# two that agree, fall back to the third, and count the corrections so the drift is visible.
BETTER = {}
for p_ in sorted(glob.glob(D + 'metrics/bulk_as.csv')) + sorted(glob.glob(D + 'metrics/out*.csv')):
    for r in csv.DictReader(open(p_), delimiter=';'):
        d = (r.get('target') or r.get('domain') or '').strip().lower()
        a = (r.get('ascore') or '').strip()
        if d and a not in ('', 'ERROR'): BETTER.setdefault(d, a)
_fixed = 0
for d, a in BETTER.items():
    if d in SEM:
        if SEM[d]['domain_ascore'] != a: _fixed += 1
        SEM[d] = dict(SEM[d], domain_ascore=a)
print(f'Authority Score: {len(BETTER):,} domains carry a figure from the bulk comparison or '
      f'overview report; {_fixed:,} of those corrected the referring-domain report')
AHD = {r['Domain'].lower().removeprefix('www.'): r for r in AH}
# The Ahrefs referring-domain export is registered-domain level, so a subdomain host
# finds nothing there. Its Domain rating sits on the backlink rows instead.
AHDR = {}
for r in AHL:
    h = host(r['Referring page URL'])
    if h and r['Domain rating'] and h not in AHDR: AHDR[h] = r['Domain rating']

# ---------------- vocabulary ----------------
# The anchors the attack network writes. Every one of these is sales copy for an SEO
# service, carrying the client's own domain name as the advertised example.
PBN = re.compile(r'(seo authority|seo links|backlink|pbn|buy backlink|da 50|pa 40|rank first page|'
                 r'link building|dofollow|white hat seo|white-hat|outreach|premium backlinks|'
                 r'link profile|organic visibility|da and dr|da, dr|placement reporting|'
                 r'authority link|sponsored post|guest post|tiered link|outrank your competitors|'
                 r'rank higher|websites grow|paid blog post|grow your website traffic|'
                 r'sitetosocial|trust flow|citation flow|serp|indexation|domain authority)', re.I)
# K&K's own product and service vocabulary. These are the anchors a commissioned
# campaign would buy, so they are held for the supplier to confirm, never auto disavowed.
PRODUCT = re.compile(r'(truck bod|truck bed|service bod|utility bod|utility bed|dump bod|dump bed|'
                     r'dump trailer|flatbed|flat dump|dovetail|beavertail|gooseneck|chipper|'
                     r'landscap|platform bod|platform truck|platform bed|roll[- ]?off|hook ?lift|'
                     r'ramp bod|ramp truck|powder[- ]?coat|ladder rack|contractor.{0,3}s? (truck|bed|dump)|'
                     r'mechanic(s|s.)? (truck|service)|work truck|hvac (truck|service|utility)|'
                     r'plumbing (truck|service)|van bodies|service body van|traffic control truck|'
                     r'utility hauler|truck with (a )?utility bed|heavy[- ]duty (truck|service|platform|flatbed))', re.I)
GEO = re.compile(r'\b(georgia|\bga\b|griffin|atlanta)\b', re.I)
BRAND = re.compile(r'(k ?& ?k|k ?and ?k|kandkmfg|kandkmanufacturing|gaworktrucks|ga work trucks|kkmaterial)', re.I)
NAKED = re.compile(r'^(https?://|www\.)', re.I)
GENERIC = re.compile(r'^(visit website.*|website|click here|about|contact|services|read more|here|link|'
                     r'visit site.*|go to website|icon - external link visit website|访问网站|[0-9]+|,|\.)$', re.I)
CASINO = re.compile(r'(casino|poker|gambling|gacor|slot|betting|\bbet\b|ufabet|sohbet|togel|judi|'
                    r'psilocybin|doxycycline|erythromycin|escort|viagra|porn)', re.I)
# A hostname that advertises what it sells. These exist to host outbound links.
SPAMNAME = re.compile(r'(backlink|baclink|backling|dofollow|da-?pa|dapa|dachecker|drchecker|pachecker|'
                      r'rankchecker|rankingchecker|serpchecker|seochecker|sitechecker|linkchecker|'
                      r'urlchecker|webchecker|statschecker|datachecker|auditchecker|trustflowchecker|'
                      r'\bseo\b|seo-|-seo|linkbuilding|link-building|buylink|buypbn|pbn|aged-?domain|'
                      r'guestpost|citation|profilecreation|smm|indexer|trafficfor|boost-?traffic|'
                      r'linkgenerator|linkmanagement|linkmonitoring|linksnatcher|wholinkstomysite|'
                      r'domraider|getwebsiteworth|domainanalysis|allwebsitesdirectory|'
                      r'bookmark|directori|directory|dir\.|listing|weblinx|urls-|shorten)', re.I)
# The part of SPAMNAME that names an SEO product rather than a directory. Used only to
# label the site type, so a listings site is not described as a backlink tool.
SEOTOOLNAME = re.compile(r'(backlink|baclink|backling|dofollow|da-?pa|dapa|dachecker|drchecker|'
                         r'pachecker|rankchecker|rankingchecker|serpchecker|seochecker|sitechecker|'
                         r'linkchecker|urlchecker|webchecker|statschecker|datachecker|auditchecker|'
                         r'trustflowchecker|\bseo\b|seo-|-seo|linkbuilding|link-building|buylink|'
                         r'buypbn|pbn|aged-?domain|guestpost|indexer|trafficfor|boost-?traffic|'
                         r'linkgenerator|domraider|getwebsiteworth|domainanalysis)', re.I)
JUNKTLD = re.compile(r'\.(top|cfd|monster|sbs|icu|website|shop|store|space|site|online|link|xyz|click|'
                     r'party|fyi|cv|art|bz|lc|pro|biz|agency|guru|club|us|info)$', re.I)
# Page titles that only ever appear on a link farm.
SPAMTITLE = re.compile(r'(where to buy .{0,12}aged domains|directory pages index|domain report|'
                       r'web directory|boost organic traffic|premium seo|link building services|'
                       r'domains? for sale|top list of .{0,10}domains|top domains [-–]|'
                       r'buy backlinks|backlink (checker|generator|service)|da pa checker|'
                       # signatures read off this profile's own link farms
                       r'seo domain research|url shared|any seo resource|few of top websites|'
                       r'aged domains and backlinks|directory pages index|'
                       r'domain list page|top domains? page|domain list \d)', re.I)
# A URL template shared by hundreds of throwaway hosts is one operator, not a site.
SPAMURL = re.compile(r'/domain/domain/part/|/best-for-ranking-|/share/[0-9]+$', re.I)
DEEP = re.compile(r'kandkmfg\.com/(product|capability|industry|blog|what-is|join-our-team)', re.I)
PRNET = re.compile(r'(einpresswire|presswire|pressrelease|newswire|prnews|newsdirect|xpr\.media)', re.I)
# A page whose title names the client is a listing, citation or editorial mention, not
# spam. The sales-copy templates also carry the client name, so they are excluded first.
CLIENTPAGE = re.compile(r'(k ?& ?k|k ?and ?k|kandkmfg|kandkmanufacturing|ga work ?trucks|gaworktrucks)', re.I)
SALESCOPY = re.compile(r'(backlink|seo|pbn|dofollow|da 50|pa 40|rank first page|link building|'
                       r'premium|authority|outreach|guest post)', re.I)

def anchor_type(a):
    a = (a or '').strip()
    if not a: return 'Empty or image'
    if PBN.search(a): return 'Spam: keyword stuffed SEO sales copy'
    if CASINO.search(a): return 'Spam: off topic'
    if NAKED.match(a) or re.match(r'^[a-z0-9.-]+\.(com|net|org|info)/?$', a, re.I): return 'Naked URL'
    if PRODUCT.search(a):
        # Anything this long is a sentence lifted from body copy, not an anchor a
        # supplier would recognise as a placement they bought.
        if len(a) > 120: return 'Contextual or other'
        return 'Exact match commercial (geo)' if GEO.search(a) else 'Exact match commercial'
    if GENERIC.match(a): return 'Generic'
    if BRAND.search(a): return 'Branded'
    return 'Contextual or other'

for r in LINKS:
    r['atype'] = anchor_type(r['anchor'])
    r['live'] = LIVE.get(canon(r['source_url']))

# ---------------- hosting clusters ----------------
# A /24 that hosts a pile of this client's referring domains is one operator running a
# network, not a coincidence. Cloudflare and the other big shared front ends are excluded
# because half the web sits behind them and the shared address proves nothing there.
CDN = re.compile(r'^(104\.(2[0-9]|1[6-9])\.|172\.6[4-9]\.|172\.7[01]\.|162\.159\.|188\.114\.|'
                 r'151\.101\.|199\.59\.|13\.|34\.|35\.|52\.|54\.|142\.250\.|172\.217\.|172\.253\.)')
def c24(ip): return '.'.join(ip.split('.')[:3]) if ip.count('.') == 3 else ''
_c = collections.Counter(c24(r['ip']) for r in SEM.values() if r['ip'] and not CDN.match(r['ip']))
NETBLOCK = {k for k, v in _c.items() if k and v >= 5}
print(f'shared hosting: {len(NETBLOCK)} /24 blocks carry 5 or more referring domains each, '
      f'{sum(_c[k] for k in NETBLOCK):,} domains in total (Cloudflare and the big CDNs excluded)')
# The same operator spreads a network across a whole /16 rather than one /24, so count
# those too. A /16 is far too coarse to condemn a site on, so this never decides a verdict;
# it is recorded on the row, because a client about to ask a supplier what it paid for
# should know the placements are not independent sites.
def c16(ip): return '.'.join(ip.split('.')[:2]) if ip.count('.') == 3 else ''
_c16 = collections.Counter(c16(r['ip']) for r in SEM.values() if r['ip'] and not CDN.match(r['ip']))
BIGNET = {k: v for k, v in _c16.items() if k and v >= 20}
print(f'network hosting: {len(BIGNET)} /16 ranges carry 20 or more referring domains each, '
      f'{sum(BIGNET.values()):,} domains in total')

# ---------------- per domain ----------------
by = collections.defaultdict(list)
for r in LINKS: by[r['rd']].append(r)
ALL = set(by) | set(SEM) | set(AHD)

out = []
for d in sorted(ALL):
    rs = by.get(d, [])
    sem, ahr = SEM.get(d), AHD.get(d)
    # The bulk comparison report covers every domain, including the subdomain hosts and
    # the Ahrefs-only sites the referring-domain report never returns.
    asc = int(num(BETTER[d])) if d in BETTER else (int(num(sem['domain_ascore'])) if sem else '')
    dr = num(ahr['DR']) if ahr else (num(AHDR[d]) if d in AHDR else '')
    ip = sem['ip'] if sem else ''
    country = (sem['country'] if sem else '') or ''
    atraffic = int(num(ahr['Traffic '])) if ahr else ''
    fs = [x for x in [(sem or {}).get('first_seen')] + [r['first_seen'] for r in rs] if x]
    first = min(fs, key=lambda v: int(v)) if fs else ''
    types = collections.Counter(x['atype'] for x in rs)
    dof = sum(1 for x in rs if x['nofollow'] == 'false')
    nof = len(rs) - dof
    bl = len(rs) or int(num((sem or {}).get('backlinks_num') or (ahr or {}).get('Links to target') or 1))
    anchors = [x['anchor'] for x in rs if (x['anchor'] or '').strip()]
    top = collections.Counter(anchors).most_common(1)[0][0] if anchors else ''
    props = sorted({x['property'] for x in rs}) or [CLIENT]

    eff = eff0 = asc if asc != '' else (dr / 10 if dr != '' else 0)
    has_pbn = types['Spam: keyword stuffed SEO sales copy'] > 0
    has_exact = types['Exact match commercial (geo)'] + types['Exact match commercial'] > 0
    offtopic = types['Spam: off topic'] > 0 or bool(CASINO.search(d))
    spam_title = any(SPAMTITLE.search(x['source_title'] or '') or SPAMURL.search(x['source_url'] or '')
                     for x in rs)
    # Not one of the 4,584 link scheme anchors points anywhere but the home page, while
    # every link that reaches a product, capability or industry page carries a commercial
    # anchor. The page a link asks Google to rank is therefore the cleanest line between
    # the two campaigns, and it decides before anything read off the host.
    deep = any(DEEP.search(x['target_url'] or '') for x in rs)
    # A host that fires the same naked domain name at the home page several times over is
    # running an automated listing, not making an editorial link.
    naked_farm = (len(rs) >= 3 and not deep
                  and all(x['atype'] in ('Naked URL', 'Empty or image') for x in rs)
                  and eff0 <= 6)
    ah_spam = (ahr or {}).get('Is spam') == 'true'
    netblock = c24(ip) in NETBLOCK
    pr = bool(PRNET.search(d))
    listed = any(CLIENTPAGE.search(x['source_title'] or '') and not SALESCOPY.search(x['source_title'] or '')
                 for x in rs)
    parent = '.'.join(d.split('.')[-2:])

    if d in OWN or parent in OWN:
        status, grp = 'Own Site', 'Client owned property'
    elif asc != '' and asc >= 20:
        status, grp = 'Keep', 'Genuine site, Semrush Authority Score 20 or above'
    elif has_exact and has_pbn:
        status, grp = 'Held (Review)', 'Mixes exact match commercial anchors with link scheme sales copy'
    elif has_exact or deep:
        _w = ('Exact match commercial anchor' if has_exact else
              'Links to a product, capability or industry page rather than the home page')
        _h = ('. The host is an article directory or bookmark farm, so the placement is low quality '
              'even if it was bought' if re.search(r'article|bookmark|directori|directory|listing|submit', d, re.I)
              else '')
        status, grp = ('Held (Pending Partner)' if dof else 'Held (Nofollow, No Action)',
                       _w + ', confirm with the previous partner who commissioned it' + _h)
    elif pr and rs:
        status, grp = ('Held (Pending Partner)' if dof else 'Held (Nofollow, No Action)',
                       'Press release syndication, confirm with the previous partner who commissioned it')
    elif listed and not has_pbn:
        status, grp = 'Keep', 'Business listing or editorial mention naming the client'
    elif offtopic:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'Off topic casino, gambling or pharma page'
    elif has_pbn:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'Automated link scheme advertising the client domain as its sales example'
    elif SPAMNAME.search(d):
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'SEO tool, bookmark or link selling network domain'
    elif spam_title:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'Templated link farm page'
    elif netblock:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), f'Link network host, {_c[c24(ip)]} of the client referring domains share the {c24(ip)}.0/24 block'
    elif not rs:
        status, grp = 'Keep', 'No link sample from either tool, so nothing passes and nothing is owed'
    elif naked_farm:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'Automated listing that fires the client domain name at the home page repeatedly'
    elif JUNKTLD.search(d) and eff <= 4:
        status, grp = ('Spam (Disavow)' if dof else 'Spam (Nofollow, No Action)'), 'Throwaway registration with no editorial signal of any kind'
    else:
        status, grp = 'Keep', 'Genuine or harmless link'

    if re.search(r'bookmark|bmark|social', d, re.I): st = 'Social bookmarking site'
    elif pr: st = 'PR and news distribution'
    elif SEOTOOLNAME.search(d): st = 'SEO tool or link selling site'
    elif re.search(r'directori|directory|listing|dir\.|local|biz|business|finder|pages', d, re.I):
        st = 'Low quality web directory'
    elif re.search(r'article|blog|content|post|news|magz|diary|writers|story|times|tribune|journal', d, re.I):
        st = 'Guest article or content farm'
    elif d in OWN: st = 'Client owned property'
    elif status == 'Keep': st = 'Genuine site'
    else: st = 'Low quality web directory'

    ex = None
    for want in (lambda x: x['live'] and x['nofollow'] == 'false', lambda x: x['live'],
                 lambda x: x['nofollow'] == 'false', lambda x: True):
        c = [x for x in rs if want(x)]
        if c: ex = c[0]; break
    out.append(dict(domain=d, status=status, group=grp, sitetype=st, ascore=asc, dr=dr,
        tool=('Both' if len({x['tool'] for x in rs}) > 1 else (sorted({x['tool'] for x in rs})[0] if rs
              else ('Semrush' if sem else 'Ahrefs'))),
        backlinks=bl, dofollow=dof if rs else '', nofollow=nof if rs else '',
        first_seen=first, ip=ip, country=country, ah_traffic=atraffic,
        properties=', '.join(props), top_anchor=top,
        example_page=(ex or {}).get('source_url', ''), page_title=(ex or {}).get('source_title', ''),
        example_target=(ex or {}).get('target_url', ''), example_anchor=(ex or {}).get('anchor', ''),
        example_live={True: 'Yes', False: 'No', None: ''}[(ex or {}).get('live')],
        atypes='; '.join(f'{k} x{v}' for k, v in types.most_common()),
        tab05='Yes' if d in TAB05 else '',
        redundant='', disavow_line='domain:' + d))

# Record the shared range on the rows it applies to. This changes no verdict.
for x in out:
    k = c16(x['ip'] or '')
    if k in BIGNET:
        x['group'] += (f". Hosted in {k}.0.0/16, a range carrying {BIGNET[k]:,} of the "
                       f"referring domains in this profile, so this is one network rather "
                       f"than an independent site")

# A root that carries no link of its own, while a subdomain of it does, is not a second
# referring site: Semrush counts at root level and Ahrefs at subdomain level, so merging
# the two lists the same site twice. Keep the row that holds the evidence.
linked = {r['rd'] for r in LINKS}
dupe = {x['domain'] for x in out if x['domain'] not in linked
        and any(k['domain'] != x['domain'] and k['domain'].endswith('.' + x['domain'])
                and k['domain'] in linked for k in out)}
out = [x for x in out if x['domain'] not in dupe]
print(f'dropped {len(dupe)} root domains that carry no link of their own and were counted twice with a subdomain')

# A genuine parent lends its standing to a subdomain only where that subdomain shows
# nothing of its own; a subdomain caught serving a link scheme page keeps its own verdict.
BY = {x['domain']: x for x in out}
def parent_of(d):
    p = d.split('.')
    for i in range(1, len(p) - 1):
        if '.'.join(p[i:]) in BY: return '.'.join(p[i:])
    return None
promoted = redundant = 0
for x in out:
    par = parent_of(x['domain'])
    if not par or par == x['domain']: continue
    pst = BY[par]['status']
    if pst in ('Keep', 'Own Site') and x['status'].startswith('Spam') and not x['group'].startswith(
            ('Automated link scheme', 'Off topic', 'SEO tool', 'Templated link farm')):
        x['status'] = pst; x['group'] = f'Genuine or editorial (subdomain of {par})'; promoted += 1
    elif pst == 'Spam (Disavow)' and x['status'] == 'Spam (Disavow)':
        x['group'] += f' (covered by domain:{par})'; x['redundant'] = 'Yes'; redundant += 1

for x in out:
    if x['status'] != 'Spam (Disavow)': x['disavow_line'] = ''
assert not [x for x in out if x['disavow_line'] and x['status'] != 'Spam (Disavow)']
print(f'post pass: {promoted} subdomains took their parent status, {redundant} child lines already covered by a parent line')

out.sort(key=lambda x: (x['status'], -x['backlinks'], x['domain']))
with open(D + 'domain_audit.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(out)
cols = ['rd', 'tool', 'property', 'source_url', 'source_title', 'target_url', 'anchor', 'atype',
        'nofollow', 'first_seen', 'response_code', 'redirect_url', 'live']
with open(D + 'links_all.csv', 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(cols)
    for r in sorted(LINKS, key=lambda x: (x['rd'], x['anchor'] or '')):
        w.writerow([r.get(c, '') for c in cols])

print('\n=== STATUS ===')
for k, v in collections.Counter(x['status'] for x in out).most_common(): print(f'  {v:5d}  {k}')
print('  TOTAL', len(out))
print('\n=== ANCHOR TYPES (links) ===')
for k, v in collections.Counter(r['atype'] for r in LINKS).most_common():
    print(f'  {v:5d}  {k}  ({v / len(LINKS) * 100:.1f}%)')
print('\n=== PROPERTY THE LINK ACTUALLY POINTS AT ===')
for k, v in collections.Counter(r['property'] for r in LINKS).most_common(): print(f'  {v:5d}  {k}')
