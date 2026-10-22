#!/usr/bin/env python3
"""Controlled Comfort backlink classifier.
Reads the two Ahrefs CSVs (UTF-16, tab-delimited), assigns one of six statuses to each
referring domain on visible evidence (anchor / host / target / audience), and writes
classified_domains.json + classified_links.csv for build.py.

Status set (exactly these six, per AUDIT_FORMAT.md):
  Spam (Disavow) | Spam (Nofollow, No Action) | Held (Pending Partner) |
  Held (Nofollow, No Action) | Keep | Own Site
"""
import sys, csv, io, json, re
from urllib.parse import urlparse
from collections import Counter

RD_PATH, BL_PATH, OUT_DIR = sys.argv[1], sys.argv[2], sys.argv[3]
CLIENT_HOSTS = ("controlledcomfort.com",)   # owned/redirect domains (none beyond the money site)

def read_utf16_tsv(path):
    raw = open(path, 'rb').read().decode('utf-16')
    rows = list(csv.reader(io.StringIO(raw), delimiter='\t'))
    hdr = [c.strip() for c in rows[0]]
    idx = {c: i for i, c in enumerate(hdr)}
    return idx, [r for r in rows[1:] if len(r) >= len(hdr)]

def host_of(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h

def fnum(x):
    try: return float(str(x).replace(',', '').strip() or 0)
    except: return 0.0

# ---- evidence predicates -------------------------------------------------
GEO = re.compile(r'\bomaha\b|\bne\b|nebraska', re.I)
SERVICE = re.compile(r'furnace|furnance|hvac|air\s*condition|\bac\b|a/?c\b|heating|cooling|heat\s*pump', re.I)
def is_exact_match(anchor):
    a = anchor or ''
    return bool(SERVICE.search(a) and GEO.search(a)) and not is_pbn_anchor(a)

PBN_ANCHOR = re.compile(
    r'premium seo backlink|buy backlink|dofollow backlink|pbn network|da ?\d{2}|pa ?\d{2}|'
    r'increase your domain (authority|rating)|domain authority/?rating|whatsapp us|'
    r'high quality .*backlink|backlinks for higher|rank .*higher with backlink|'
    r'first page google|rank first page|seo link building|link building|higher google ranking|'
    r'strengthen .* through high|rank .* higher|cheap', re.I)
SPUN_FILLER = re.compile(r'if you had told me last year|ranking in europe is not the same', re.I)
def is_pbn_anchor(a):
    a = a or ''
    return bool(PBN_ANCHOR.search(a) or SPUN_FILLER.search(a))

GENERIC = re.compile(r'^(visit\s*website|website|visit site|click here|read more|'
                     r'icon - external link.*|here|link)$', re.I)
BRANDED = re.compile(r'controlled\s*comfort', re.I)
NAKED = re.compile(r'^https?://|^www\.|controlledcomfort\.com$', re.I)

PBN_HOST = re.compile(r'(seo|link|rank|backlink|outrank|baron|forge|dapa|guestpost|serp|crawl|'
                      r'anchor|indexer|domainrank|pagerank|boost|authority|velocity|niche-edit|'
                      r'white-hat|tier|keyword|organic|digital-pr|press-release)', re.I)
def is_pbn_host(h):
    if re.match(r'^\d+\.xyz$', h):                 # numbered .xyz network
        return True
    if h.endswith('.store') or h.endswith('.shop'):
        return bool(PBN_HOST.search(h)) or h.count('-') >= 2
    bad = ('buybacklink', 'backlinksbuy', 'backlinkbuy', '99backlink', 'worldtopbacklink',
           'allbaclink', 'rarebacklink', 'superbquality', 'bestrankbacklink', 'buyrankbacklink',
           'quickseolink', 'trafficbooster', 'webbacklink', 'increasewebtraffic', 'dapachecker',
           'multidapa', 'backlinkreport', 'highprbacklink', 'seohighranking', 'rankboost',
           'backlinker', 'webrankingsolution')
    return any(b in h for b in bad)

OFFTOPIC = re.compile(r'casino|gambling|poker|pharma|viagra|cialis|escort|porn|erythromycin', re.I)

def anchor_type(a):
    a = (a or '').strip()
    if a == '':                      return 'Empty/image'
    if is_exact_match(a):            return 'Exact match commercial (geo)'
    if is_pbn_anchor(a):            return 'Spam: PBN sales copy'
    if OFFTOPIC.search(a):           return 'Spam: off topic'
    if BRANDED.search(a) and not NAKED.match(a): return 'Branded'
    if NAKED.match(a):               return 'Naked URL'
    if GENERIC.match(a):             return 'Generic'
    return 'Contextual or other'

# ---- load ----------------------------------------------------------------
ri, rrows = read_utf16_tsv(RD_PATH)
bi, brows = read_utf16_tsv(BL_PATH)

RD = {}
for r in rrows:
    d = r[ri['Domain']].lower()
    RD[d] = dict(dr=r[ri['DR']], spam=r[ri['Is spam']].lower() == 'true',
                 traffic=int(fnum(r[ri['Traffic']])), keywords=int(fnum(r[ri['Keywords']])),
                 refdomains=r[ri['Dofollow ref. domains']], first=r[ri['First seen']],
                 links_to_target=r[ri['Links to target']])

links_by_dom = {}
all_links = []
for r in brows:
    h = host_of(r[bi['Referring page URL']])
    tgt = r[bi['Target URL']]
    tl = tgt.lower()
    prop = 'deep' if '/services/' in tl else ('home' if tl.rstrip('/').endswith('controlledcomfort.com') else 'other')
    nf = (r[bi['Nofollow']].lower() == 'true' or r[bi['UGC']].lower() == 'true' or r[bi['Sponsored']].lower() == 'true')
    rec = dict(host=h, url=r[bi['Referring page URL']], title=r[bi['Referring page title']],
               anchor=r[bi['Anchor']], target=tgt, prop=prop, nofollow=nf,
               http=r[bi['Referring page HTTP code']], type=r[bi['Type']],
               spam=r[bi['Is spam']].lower() == 'true', first=r[bi['First seen']])
    rec['atype'] = anchor_type(rec['anchor'])
    links_by_dom.setdefault(h, []).append(rec)
    all_links.append(rec)

# ---- classify per domain -------------------------------------------------
def classify(dom, links):
    meta = RD.get(dom, {})
    traffic = meta.get('traffic', 0)
    spam_flag = meta.get('spam', False)
    anydofollow = any(not l['nofollow'] for l in links)
    pbn_host = is_pbn_host(dom)
    pbn_anchor = any(is_pbn_anchor(l['anchor']) for l in links)
    offtopic = any(OFFTOPIC.search((l['anchor'] or '') + ' ' + (l['title'] or '')) for l in links)
    exact = [l for l in links if is_exact_match(l['anchor'])]
    deep = [l for l in links if l['prop'] == 'deep']
    held_links = exact + [l for l in deep if l not in exact]

    dr = fnum(meta.get('dr', 0))
    clean = (not spam_flag) and (not pbn_host) and (not pbn_anchor) and (not offtopic)
    # 1. Own site
    if dom in CLIENT_HOSTS:
        return 'Own Site', 'Client-owned / money site.'
    # 2. Keep — strongly genuine citation (real authority/audience). This wins over Held so a
    #    real directory's exact-match citation is not needlessly held. Authority, not traffic>=1:
    #    a token 1-visit directory must NOT qualify (that is the DR/traffic trap).
    if clean and (traffic >= 100 or (dr >= 20 and traffic > 0)):
        return 'Keep', f'Genuine authoritative citation: DR {meta.get("dr","")}, organic traffic {traffic}, not spam-flagged.'
    # 3. Held — exact-match commercial anchor and/or deep money-page target (non-PBN host)
    if held_links and (not pbn_host) and (not pbn_anchor) and (not offtopic):
        reason = []
        if exact: reason.append(f'exact-match commercial anchor ("{exact[0]["anchor"]}")')
        if deep:  reason.append(f'links to deep money page ({deep[0]["target"]})')
        all_nf = all(l['nofollow'] for l in held_links)
        status = 'Held (Nofollow, No Action)' if all_nf else 'Held (Pending Partner)'
        return status, 'May be commissioned: ' + ' + '.join(reason) + '.'
    # 4. Spam — PBN host / sales-copy anchor / off-topic / spam-flagged with spam evidence
    if pbn_host or pbn_anchor or offtopic:
        ev = []
        if pbn_host:   ev.append('PBN/link-farm host name')
        if pbn_anchor: ev.append('PBN sales-copy anchor')
        if offtopic:   ev.append('off-topic (pharma/casino) anchor')
        status = 'Spam (Disavow)' if anydofollow else 'Spam (Nofollow, No Action)'
        return status, 'Spam evidence: ' + ', '.join(ev) + '.'
    # 5. Otherwise Keep (no disavow without visible evidence)
    return 'Keep', 'No spam evidence visible; kept (never disavow on score/flag alone).'

domains_out = {}
for dom, links in links_by_dom.items():
    status, reason = classify(dom, links)
    meta = RD.get(dom, {})
    nof = sum(1 for l in links if l['nofollow'])
    dof = len(links) - nof
    props = sorted({l['prop'] for l in links})
    prop_label = {'deep': 'Deep service page', 'home': 'Home page', 'other': 'Other page'}
    pt = ', '.join(prop_label.get(p, p) for p in props)
    top_anchor = Counter(l['anchor'] for l in links).most_common(1)[0][0]
    ex = sorted(links, key=lambda l: (l['http'] != '200', l['nofollow']))[0]   # prefer live, dofollow
    domains_out[dom] = dict(
        domain=dom, status=status, reason=reason,
        dr=meta.get('dr', ''), traffic=meta.get('traffic', ''), keywords=meta.get('keywords', ''),
        refdomains=meta.get('refdomains', ''), spam_flag=meta.get('spam', False),
        backlinks=len(links), dofollow=dof, nofollow=nof,
        links_point_to=pt, first_seen=meta.get('first', ex['first']),
        top_anchor=top_anchor, example_url=ex['url'], example_title=ex['title'],
        example_target=ex['target'], in_disavow=(status == 'Spam (Disavow)'))

# ---- write outputs -------------------------------------------------------
import os
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, 'classified_domains.json'), 'w') as f:
    json.dump(domains_out, f)
with open(os.path.join(OUT_DIR, 'classified_links.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['referring_domain', 'status', 'anchor', 'anchor_type', 'link_type',
                'nofollow', 'http', 'url', 'title', 'target', 'prop'])
    for l in all_links:
        st = domains_out[l['host']]['status']
        w.writerow([l['host'], st, l['anchor'], l['atype'], l['type'],
                    l['nofollow'], l['http'], l['url'], l['title'], l['target'], l['prop']])

# ---- console summary -----------------------------------------------------
dist = Counter(d['status'] for d in domains_out.values())
print("referring domains classified:", len(domains_out))
for s in ['Spam (Disavow)', 'Spam (Nofollow, No Action)', 'Held (Pending Partner)',
          'Held (Nofollow, No Action)', 'Keep', 'Own Site']:
    print(f"  {s:<30} {dist.get(s,0)}")
print("disavow (Spam Disavow) lines:", dist.get('Spam (Disavow)', 0))
print("total backlinks:", len(all_links))
