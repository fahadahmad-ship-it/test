"""
classify.py — anchor typing + referring-domain verdicts for Bolton Service WNC.

Six statuses only (no Review buckets):
  Spam (Disavow) | Spam (Nofollow, No Action) | Held (Pending Partner) |
  Held (Nofollow, No Action) | Keep | Own Site

Every Spam/Held verdict carries a concrete, checkable evidence string (anchor / title / host
token / target page). Nothing is disavowed on score, TLD, or IP alone (playbook principle 2).
"""
import re

MONEY_SITE   = 'boltonservicewnc.com'
OWNED        = {'boltonservicewnc.com', 'boltonwnc.com', 'webolton.com'}
REDIRECTS    = {'boltonwnc.com', 'webolton.com'}
BRAND_TOKENS = ('bolton',)            # webolton / boltonwnc / boltonservicewnc all contain 'bolton'

# ---- client vocabulary (exact-match commercial anchors) ----
SERVICE_TERMS = [
    'hvac','air conditioning','air conditioner',' ac ','ac repair','ac service','a/c',
    'heating','heat pump','furnace','boiler','plumbing','plumber','plumbers','drain',
    'hydro jetting','hydrojetting','water heater','ductless','duct','cooling','mini split',
    'mini-split','sewer','gas line','repipe','hvac company','heating and cooling',
    'water leak','leak repair','leak detection','slab leak','pipe repair','pipe leak',
    'toilet repair','faucet','sump pump','garbage disposal','thermostat','air quality',
]
GEO_TERMS = [
    'asheville','weaverville','swannanoa','fletcher','mills river','woodfin','arden',
    'candler','black mountain','hendersonville','biltmore','leicester','enka','barnardsville',
    'wnc','western north carolina',' nc',
]

# ---- spam signals ----
OFFTOPIC = [
    'casino','gambling','gamble',' bet ','betting','poker','slot','roulette','baccarat',
    'viagra','cialis','pharma','pill','tadalaf','sildenaf','escort','porn',' sex ','xxx',
    'crypto','bitcoin','forex','loan','payday','togel','judi','slot gacor','bokep','kamagra',
    # toxic / illegal / adult negative-SEO anchors seen in this profile
    'boobs','big dick','big penis','penis','nude','naked child','child picture','kid nipple',
    'kid nipples','nipples','paedophile','pedophile','jihad','bomb for','bomber','obat kuat',
    'obat','herbal','capsule','medicine','telegram','t.me/','darksidelinks','incest','milf',
    'anal','blowjob','fuck','xnxx','gacor','pinay','bdsm','hentai','onlyfans','deepweb','dark web',
    'antrax','anthrax','nuke','weapon','vibrator','vagina','dildo','sex toy','steroid','ivermectin',
]
# PBN / link-service sales-copy markers (combination-based)
SALES_MARKERS = [
    'backlink','back link','dofollow','nofollow link','pbn','link building','link-building',
    'buy links','buy backlink','high quality link','high-quality link','domain authority',
    'da 50','pa 40','da50','pa40',' da ',' pa ','seo link','premium seo','seo authority',
    'search engine ranking','google ranking','first page google','rank first','outrank',
    'link placement','link placements','guest post','trust flow','link velocity','tiered link',
    'high authority','web 2.0','niche edit','serp','improve rankings','boost domain',
    'seo services','link service','citation','white hat seo','organic traffic',' seo ',
    'ranking','rankings','backlinks',
]
# spam host-name tokens (domain contains these)
SPAM_HOST_TOKENS = [
    'backlink','back-link','seocheck','seo-','dapa','rankchecker','rank-checker','dachecker',
    'checker','directory','listings','listing','dofollow','pbn','linkbuilding','link-building',
    'domainrating','trafficdata','webtraffic','buytraffic','visitors','visitormetrics',
    'analytics','keywordgenerator','keyword','domainpada','padachecker','authoritylink',
    'highqualitylink','bulkbacklink','freebacklink','createbacklink','linkmarketing',
    'seostrength','seovisibility','bizdir','stardirectory','gurulisting','weblookup',
    # spam-network host signatures (negative-SEO link scheme) — seen in this profile
    'seo','rank','smm','domain','traffic','aged-domain','ageddomain','topleveldomain',
    'nichelink','sponsoredlink','topranklink','rankandlink','linkbuilt','linksnatcher',
    'algolinker','atomizelink','offpagegrowth','indexaward','getwebsiteworth','webstats',
    'websiteworth','websitescrawl','websitesea','websiterace','organictraffic','boosttraffic',
    'trafficexpert','digitalboost','authorityrise','searchwins','getranked','fastranking',
    'localranking','global-ranks','growwithseo','eliteseo','premiumseo','winningseo',
    'domraider','domaineye','pagesearch','indexing','index-','linkify','linkbuild',
]
def norm_title(s):
    """Lowercase and replace any run of non-alphanumeric chars (incl. emoji) with a space."""
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()

# spam page-title / URL templates (matched against the NORMALISED title)
SPAM_TITLE_RE = re.compile(
    r'(page\s*[\d,]{2,})|(page\s+no\b)|(backlinks?\s+for\s+websites)|(link\s+building\s+service)|'
    r'(premium\s+backlink)|(high\s+quality\s+(seo\s+)?backlinks)|(domain\s+list\s+page)|'
    r'(buy\s+(aged\s+)?(domains|backlinks))|(aged\s+domains)|(dofollow\s+backlinks)|(pbn)|'
    r'(url\s+shared)|(website\s+stats)|(seo\s+domain\s+research)|(premium\s+pbn)|'
    r'(link\s+placement)|(domain\s+report)|(web\s+directory)|(directory\s+pages)|'
    r'(backlink\s+service)|(purchasing\s+our\s+backlink)|(top\s+websites)|(sitetosocial)|'
    r'(tool\s+for\s+pinterest)|(buy\s+.{0,20}\s+backlink)|(backlinks?\s+from)',
    re.I)
SPAM_URL_RE = re.compile(r'(/dir/backlinks-for-websites)|(/dir/natural-link-building)|'
    r'(/domain/domain/part)|(/share/\d+)|(/stats/\d+)|(/search-authority-index/)|'
    r'(/search-visibility-network/)|(link-placement)', re.I)

PRESS_RELEASE_HOSTS = ('prnewswire','einnews','openpr','pr.com','prlog','issuewire','newswire',
    'pressrelease','abnewswire','prfree','releasewire','digitaljournal')

NAKED_RE = re.compile(r'^\s*(https?://|www\.)', re.I)
DOMAINY_RE = re.compile(r'^\s*[a-z0-9-]+(\.[a-z0-9-]+)+\s*$', re.I)
GENERIC_SET = {
    'visit website','visit site','website','view website','view site','click here','read more',
    'learn more','here','this website','more info','view jobs','view job','link','source',
    'official website','homepage','home page','see more','continue reading','details','web',
}

def _has(text, needles):
    t = ' ' + text.lower() + ' '
    for n in needles:
        if n in t:
            return n.strip()
    return None

def classify_anchor(anchor, target_url=''):
    """Return (anchor_type, hit) where hit is the matched token (evidence) or ''."""
    a = (anchor or '').strip()
    low = a.lower()
    if not a or a in ('-', '—') or len(a) == 0:
        return 'Empty or image', ''
    off = _has(low, OFFTOPIC)
    if off:
        return 'Spam: off topic', off
    # sales copy: match if any strong marker present (these anchors are long & stuffed)
    sc = _has(low, SALES_MARKERS)
    if sc:
        return 'Spam: keyword stuffed SEO sales copy', sc
    # exact-match commercial (service term present)
    svc = _has(low, SERVICE_TERMS)
    if svc:
        geo = _has(low, GEO_TERMS)
        if geo:
            return 'Exact match commercial (geo)', f'{svc}/{geo}'
        return 'Exact match commercial', svc
    # naked URL
    if NAKED_RE.match(a) or DOMAINY_RE.match(a):
        return 'Naked URL', ''
    # branded
    if any(b in low for b in BRAND_TOKENS):
        return 'Branded', ''
    # generic
    if low in GENERIC_SET or (len(low) <= 20 and any(g in low for g in ('visit','click','website','read more','learn more','view'))):
        return 'Generic', ''
    return 'Contextual or other', ''

SPAM_TYPES   = {'Spam: keyword stuffed SEO sales copy', 'Spam: off topic'}
HELD_ANCHORS = {'Exact match commercial', 'Exact match commercial (geo)'}

def host_of(url):
    import re as _re
    if not url: return ''
    u = _re.sub(r'^[a-z][a-z0-9+.\-]*://', '', url.strip(), flags=_re.I)
    u = u.split('/',1)[0].split('?',1)[0].split('#',1)[0].split('@')[-1].split(':',1)[0]
    u = u.strip().lower().rstrip('.')
    return u[4:] if u.startswith('www.') else u

def link_property(link):
    """Property a link points at: redirect_url host if present, else target_url host."""
    r = link.get('redirect_url') or ''
    if r.strip():
        return host_of(r)
    return host_of(link.get('target_url') or '')

# Bolton's commercial money pages live under these path prefixes (service / location pages).
# /sitemap, /jobs, /blog etc. are NOT money pages and must not trigger a Held verdict.
MONEY_PAGE_PREFIXES = ('/service', '/location')
def is_deep_money_page(link):
    """Link aimed at a deep commercial money page (/service/* or /location/*), not home/sitemap/jobs."""
    r = (link.get('redirect_url') or '').strip()
    url = r if r else (link.get('target_url') or '')
    h = host_of(url)
    if h not in OWNED:
        return False
    m = re.sub(r'^[a-z]+://', '', url, flags=re.I)
    path = ('/' + m.split('/',1)[1]) if '/' in m else '/'
    path = path.split('?',1)[0].split('#',1)[0].lower()
    return any(path.startswith(p) for p in MONEY_PAGE_PREFIXES)

def classify_domain(domain, links, metrics, ip_24_counts=None):
    """
    links: list of dicts with keys anchor, nofollow(bool), target_url, redirect_url,
           source_url, source_title, response_code, first_seen
    metrics: dict with as_score (Semrush AS int or None)
    Returns dict: status, reason, evidence, anchor_types(list per link)
    """
    dom = domain.lower()
    # per-link anchor types
    types = []
    for L in links:
        t, hit = classify_anchor(L.get('anchor',''), L.get('target_url',''))
        types.append((t, hit))
    any_dofollow = any(not L['nofollow'] for L in links)
    has_exact    = any(t in HELD_ANCHORS for t,_ in types)
    has_pbn      = any(t == 'Spam: keyword stuffed SEO sales copy' for t,_ in types)
    has_offtopic = any(t == 'Spam: off topic' for t,_ in types)
    deep         = any(is_deep_money_page(L) for L in links)
    titles       = ' || '.join((L.get('source_title') or '') for L in links)
    anchors_join = ' || '.join((L.get('anchor') or '') for L in links)
    as_score     = metrics.get('as_score')

    def spam_status(ev_rule, ev):
        return dict(status=('Spam (Disavow)' if any_dofollow else 'Spam (Nofollow, No Action)'),
                    reason=ev_rule, evidence=ev)
    def held_status(ev_rule, ev):
        return dict(status=('Held (Pending Partner)' if any_dofollow else 'Held (Nofollow, No Action)'),
                    reason=ev_rule, evidence=ev)

    # 1. owned / redirect
    if dom in OWNED:
        return dict(status='Own Site', reason='Client-owned / redirect domain', evidence=dom)
    # 2. AS >= 20 -> genuine site (Keep)  [but never let an off-topic/pharma or pure-PBN host through on AS alone:
    #    those are evidence; still, playbook ranks AS>=20 as Keep. We keep the playbook order but require that
    #    the domain is not a spam-host-named / pharma host.]
    host_spam = _has(dom, SPAM_HOST_TOKENS)
    if as_score is not None and as_score >= 20 and not host_spam and not has_offtopic:
        return dict(status='Keep', reason='Authority Score >= 20 (genuine site)', evidence=f'AS={as_score}')
    # 2b. institutional TLD (.edu/.gov/.mil/.ac) with only WEAK evidence -> Keep. A benign injected
    #     link (naked URL / sitemap) on a real university/government domain is not worth disavowing the
    #     whole authoritative domain. BUT a toxic off-topic anchor (pharma/casino/"bomb"/adult) is kept
    #     out of this protection and still disavowed below — you never want that association, .edu or not.
    if re.search(r'\.(edu|gov|mil|ac)(\.[a-z]{2,3})?$', dom) and not host_spam and not has_offtopic:
        return dict(status='Keep', reason='Institutional TLD (.edu/.gov) — authoritative, link likely injected', evidence=dom)
    # 3. exact-match AND pbn on same domain -> Held (review-level)
    if has_exact and has_pbn:
        ev = next((h for t,h in types if t in HELD_ANCHORS), '')
        return held_status('Exact-match commercial + PBN anchor on same domain (review)', ev)
    # 4. exact-match OR deep money-page link -> Held
    if has_exact:
        ev = next((L.get('anchor','') for L,(t,h) in zip(links,types) if t in HELD_ANCHORS), '')
        return held_status('Exact-match commercial anchor', ev)
    if deep:
        dp = next((L for L in links if is_deep_money_page(L)), None)
        tgt = (dp.get('redirect_url') or dp.get('target_url')) if dp else ''
        return held_status('Link aimed at a deep money page', tgt)
    # 5. press-release host
    if any(p in dom for p in PRESS_RELEASE_HOSTS):
        return held_status('Press-release syndication host', dom)
    # 6. title names client without sales copy -> Keep (editorial / business listing)
    if _has(titles, BRAND_TOKENS) and not has_pbn and not has_offtopic and not host_spam:
        # ensure no sales-copy markers in the titles themselves
        if not _has(titles, SALES_MARKERS):
            ex = next((L.get('source_title','') for L in links if _has((L.get('source_title') or ''), BRAND_TOKENS)), '')
            return dict(status='Keep', reason='Linking page names client, no sales copy (editorial/listing)', evidence=ex[:120])
    # 7. off-topic -> Spam
    if has_offtopic:
        ev = next((h for t,h in types if t=='Spam: off topic'), '')
        return spam_status('Off-topic (casino/pharma/etc.) anchor', ev)
    # 8. PBN sales-copy anchor -> Spam
    if has_pbn:
        ev = next((L.get('anchor','') for L,(t,h) in zip(links,types) if t=='Spam: keyword stuffed SEO sales copy'), '')
        return spam_status('PBN keyword-stuffed SEO sales-copy anchor', ev[:140])
    # 9. spam host name -> Spam
    if host_spam:
        return spam_status('Spam host name', host_spam)
    # 9b. link injected at the client's /sitemap page -> Spam (no genuine site links to a sitemap
    #     with a content anchor; these are hacked/PBN blog injections). Client-naming citations are
    #     already protected by rule 6 above, so anything here does not name the client.
    def _targets_sitemap(L):
        url = (L.get('redirect_url') or '').strip() or (L.get('target_url') or '')
        if host_of(url) not in OWNED: return False
        m = re.sub(r'^[a-z]+://', '', url, flags=re.I)
        path = ('/' + m.split('/',1)[1]) if '/' in m else '/'
        return path.split('?',1)[0].split('#',1)[0].lower().startswith('/sitemap')
    if any(_targets_sitemap(L) for L in links):
        return spam_status('Link injected at client /sitemap page', 'target=/sitemap')
    # 10. spam page title / URL template -> Spam  (match against normalised titles)
    norm_titles = ' || '.join(norm_title(L.get('source_title') or '') for L in links)
    mt = SPAM_TITLE_RE.search(norm_titles)
    if mt:
        return spam_status('Spam page title template', mt.group(0)[:80])
    mu = None
    for L in links:
        mu = SPAM_URL_RE.search(L.get('source_url','') or '')
        if mu: break
    if mu:
        return spam_status('Spam URL template', mu.group(0)[:80])
    # 11. shared /24 with 5+ client RDs -> network host (spam only WITH other evidence; here none left) -> record, keep
    # (handled upstream; without other evidence we do not disavow on IP alone)
    # 12. default
    return dict(status='Keep', reason='No spam evidence', evidence='')
