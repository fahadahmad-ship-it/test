"""Merge Semrush + Ahrefs, build per-link and per-domain records, classify.
Produces in-memory structures consumed by build.py."""
import os, sys, glob, csv, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import (load_semrush_backlinks, load_semrush_refdomains,
                  load_ahrefs_backlinks, load_ahrefs_refdomains, host, canon)
from rootdom import root_domain
from classify import (anchor_type, classify_domain, OWNED, MONEY_SITE, target_path,
                      is_deep_money)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ras/
D = os.path.join(BASE, 'data')

def parse_ts(s):
    s = (s or '').strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return int(datetime.datetime.strptime(s[:19], fmt).replace(tzinfo=datetime.timezone.utc).timestamp())
        except Exception:
            pass
    # try just date part
    try:
        return int(datetime.datetime.strptime(s[:10], '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc).timestamp())
    except Exception:
        return None

def prop_of(target_url, redirect_url):
    ru = (redirect_url or '').strip()
    h = host(ru) if ru else host(target_url)
    rd = root_domain(h)
    return rd if rd in OWNED else (h or MONEY_SITE)

def load_metrics_as():
    """comparison AS: target;ascore;backlinks_num;domains_num -> domain -> (ascore, bl_num, dom_num)"""
    m = {}
    for fn in ('as_comparison.csv', 'as_delta.csv'):
        path = os.path.join(D, 'metrics', fn)
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line or line.startswith('target;'):
                    continue
                p = line.split(';')
                if len(p) >= 4:
                    try:
                        m[p[0].strip().lower()] = (int(float(p[1])), int(float(p[2])), int(float(p[3])))
                    except Exception:
                        pass
    return m

def load_metrics_rank():
    """domain_rank: domain;organic_keywords;organic_traffic -> (kw, traffic).
    Reads domain_rank.csv and/or domain_rank_*.csv part files."""
    m = {}
    paths = [os.path.join(D, 'metrics', 'domain_rank.csv')]
    paths += sorted(glob.glob(os.path.join(D, 'metrics', 'domain_rank_*.csv')))
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line or line.lower().startswith('domain;'):
                    continue
                p = line.split(';')
                if len(p) >= 3:
                    try:
                        m[p[0].strip().lower()] = (int(float(p[1])), int(float(p[2])))
                    except Exception:
                        pass
    return m

def build():
    sr_bl, bad, overflow = load_semrush_backlinks(os.path.join(D, 'fetch'))
    sr_rd = load_semrush_refdomains(os.path.join(D, 'rd'))
    ar_bl = load_ahrefs_backlinks(os.path.join(D, 'ahrefs', 'ahrefs_backlinks.utf8.csv'))
    ar_rd = load_ahrefs_refdomains(os.path.join(D, 'ahrefs', 'ahrefs_refdomains.utf8.csv'))
    as_map = load_metrics_as()
    rank_map = load_metrics_rank()

    # --- refdomains meta (Semrush): ip, country, first_seen, as_fallback ---
    rd_meta = {}
    for r in sr_rd:
        d = r['domain'].strip().lower()
        rd_meta[d] = {
            'ip': r.get('ip', ''),
            'country': r.get('country', ''),
            'first_seen': parse_ts(r.get('first_seen', '')),
            'as_fallback': _int(r.get('domain_authority_score')),
        }
    # Ahrefs refdomain meta (DR, ahrefs traffic/kw, is_spam) keyed by root domain
    ar_rd_meta = {}
    for x in ar_rd:
        dk = [k for k in x.keys() if 'Domain' in k][0]
        d = root_domain(x[dk])
        ar_rd_meta[d] = {
            'dr': _int(x.get('DR')),
            'is_spam': (x.get('Is spam', '') == 'true'),
        }

    # --- build link records ---
    links = []
    seen = {}
    def add_link(rec):
        key = (canon(rec['source_url']), canon(rec['target_url']), (rec['anchor'] or '').strip().lower())
        if key in seen:
            # mark both tools
            idx = seen[key]
            if rec['tool'] not in links[idx]['tools']:
                links[idx]['tools'].add(rec['tool'])
            # prefer a live response_code / fill title if missing
            if not links[idx]['title'] and rec['title']:
                links[idx]['title'] = rec['title']
            return
        seen[key] = len(links)
        rec['tools'] = {rec['tool']}
        links.append(rec)

    for r in sr_bl:
        src = host(r['source_url'])
        dom = root_domain(src)
        tp = target_path(r['target_url'])
        nf = (r['nofollow'].strip().lower() == 'true')
        at = anchor_type(r['anchor'])
        add_link({
            'referring_domain': dom, 'source_url': r['source_url'], 'source_host': src,
            'target_url': r['target_url'], 'redirect_url': r['redirect_url'],
            'property': prop_of(r['target_url'], r['redirect_url']),
            'anchor': r['anchor'], 'atype': at, 'nofollow': nf, 'dofollow': (not nf),
            'tpath': tp, 'title': r['source_title'], 'first_seen': parse_ts(r['first_seen']),
            'response_code': r['response_code'], 'tool': 'Semrush',
        })
    # Ahrefs
    kmap = {k2: [k for k in ar_bl[0].keys() if k2 in k][0] for k2 in
            ['Referring page title', 'Referring page URL', 'Target URL', 'Anchor',
             'Nofollow', 'Type', 'First seen', 'Referring page HTTP code', 'Redirect Chain URLs']} if ar_bl else {}
    for x in ar_bl:
        src_url = x[kmap['Referring page URL']]
        src = host(src_url)
        dom = root_domain(src)
        tgt = x[kmap['Target URL']]
        tp = target_path(tgt)
        nf = (x[kmap['Nofollow']] == 'true')
        is_img = (x[kmap['Type']] == 'image')
        anc = x[kmap['Anchor']]
        at = 'Empty or image' if (is_img and not anc.strip()) else anchor_type(anc, is_image=is_img)
        add_link({
            'referring_domain': dom, 'source_url': src_url, 'source_host': src,
            'target_url': tgt, 'redirect_url': '',
            'property': prop_of(tgt, ''),
            'anchor': anc, 'atype': at, 'nofollow': nf, 'dofollow': (not nf),
            'tpath': tp, 'title': x[kmap['Referring page title']],
            'first_seen': parse_ts(x[kmap['First seen']]),
            'response_code': x[kmap['Referring page HTTP code']], 'tool': 'Ahrefs',
        })

    # finalize tools -> source string
    for l in links:
        ts = l['tools']
        l['source'] = 'Both' if len(ts) > 1 else list(ts)[0]

    # --- per-domain aggregation ---
    domains = {}
    for l in links:
        d = l['referring_domain']
        if not d or d in OWNED:
            continue
        domains.setdefault(d, []).append(l)

    records = []
    for d, dls in domains.items():
        cmp_row = as_map.get(d)
        if cmp_row is not None:
            ascore, _blnum, rds_own = cmp_row
        else:
            ascore, rds_own = None, None
        if ascore is None:
            ascore = rd_meta.get(d, {}).get('as_fallback')
        if rds_own is None:
            rds_own = 0
        status, base, reason = classify_domain(d, dls, ascore)
        kw, traf = rank_map.get(d, (None, None))
        meta = rd_meta.get(d, {})
        first_seens = [l['first_seen'] for l in dls if l['first_seen']]
        # choose example link: prefer live (200) + dofollow + has title
        def score_ex(l):
            rc = str(l['response_code'])
            live = 1 if rc == '200' else 0
            return (live, 1 if l['dofollow'] else 0, 1 if l['title'] else 0, 1 if l['tpath'] != '/' else 0)
        ex = sorted(dls, key=score_ex, reverse=True)[0]
        # top anchor (most frequent)
        from collections import Counter
        anc_counter = Counter(l['anchor'] for l in dls)
        top_anchor = anc_counter.most_common(1)[0][0] if anc_counter else ''
        props = sorted(set(l['property'] for l in dls))
        records.append({
            'domain': d, 'status': status, 'base': base, 'reason': reason,
            'ascore': ascore if ascore is not None else 0,
            'rds_own': rds_own,
            'backlinks': len(dls),
            'dofollow': sum(1 for l in dls if l['dofollow']),
            'nofollow': sum(1 for l in dls if l['nofollow']),
            'has_dofollow': any(l['dofollow'] for l in dls),
            'traffic': traf if traf is not None else 0,
            'keywords': kw if kw is not None else 0,
            'ip': meta.get('ip', ''), 'country': meta.get('country', ''),
            'first_seen': min(first_seens) if first_seens else meta.get('first_seen'),
            'links_point_to': ', '.join(props),
            'top_anchor': top_anchor,
            'example': ex,
            'source': 'Both' if (d in rd_meta and d in ar_rd_meta) else ('Semrush' if d in rd_meta else ('Ahrefs' if d in ar_rd_meta else ex['source'])),
            'links': dls,
            'ar_spam': ar_rd_meta.get(d, {}).get('is_spam'),
        })
    return {'links': links, 'records': records, 'bad': bad, 'overflow': overflow,
            'n_sr_bl': len(sr_bl), 'n_ar_bl': len(ar_bl), 'as_map_n': len(as_map), 'rank_map_n': len(rank_map)}

def _int(v):
    try:
        return int(float(str(v).strip()))
    except Exception:
        return None

if __name__ == '__main__':
    r = build()
    from collections import Counter
    print('links merged:', len(r['links']), '| semrush bl:', r['n_sr_bl'], '| ahrefs bl:', r['n_ar_bl'])
    print('AS map:', r['as_map_n'], '| rank map:', r['rank_map_n'])
    print('domains:', len(r['records']))
    print('status:', Counter(x['status'] for x in r['records']).most_common())
    print('base:', Counter(x['base'] for x in r['records']).most_common())
    # link-level source
    print('link source:', Counter(l['source'] for l in r['links']).most_common())
    print('property:', Counter(l['property'] for l in r['links']).most_common())
