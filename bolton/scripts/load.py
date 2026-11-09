"""
load.py — robust readers for the Semrush + Ahrefs exports for the Bolton audit.

Handles the Semrush CSV trap (playbook sec 4): Semrush ships UNQUOTED semicolon-delimited
CSV and leaves HTML entities in titles/anchors. An entity like "&amp;" literally contains a
trailing ';', so splitting the RAW line on ';' breaks a field. Rule: unescape entities FIRST,
split SECOND, and validate/repair the column count; never let a malformed row through silently.

Domain identity: Semrush's referring-domain list is the canonical set (it defines the RD row
count). Each link's source host is mapped onto that set by longest-suffix match; hosts not in
the set fall back to a registrable-domain heuristic.
"""
import html, re, csv, io, os, glob

# ---------- URL / host helpers ----------
_SCHEME = re.compile(r'^[a-z][a-z0-9+.\-]*://', re.I)

def host_of(url):
    if not url:
        return ''
    u = url.strip()
    u = _SCHEME.sub('', u)
    u = u.split('/', 1)[0]
    u = u.split('?', 1)[0].split('#', 1)[0]
    u = u.split('@')[-1]          # strip userinfo
    u = u.split(':', 1)[0]        # strip port
    u = u.strip().lower().rstrip('.')
    if u.startswith('www.'):
        u = u[4:]
    return u

# Multi-part public suffixes we might meet (fallback only; Semrush set is primary).
_MULTI = {
    'co.uk','org.uk','gov.uk','ac.uk','me.uk','com.au','net.au','org.au','co.nz','co.za',
    'com.br','com.mx','co.in','co.jp','com.sg','com.ph','com.tr','co.id','com.my','co.ke',
}
def registrable(hostname):
    """Registrable domain via a heuristic (used only for hosts absent from the Semrush set)."""
    h = host_of(hostname) if '/' in hostname or '://' in hostname else hostname.lower().lstrip('.')
    if h.startswith('www.'):
        h = h[4:]
    parts = h.split('.')
    if len(parts) <= 2:
        return h
    last2 = '.'.join(parts[-2:])
    last3 = '.'.join(parts[-3:])
    if last2 in _MULTI:
        return '.'.join(parts[-3:])
    return last2

class DomainIndex:
    """Maps any host to a canonical referring domain, preferring the Semrush RD set."""
    def __init__(self, rd_domains):
        self.set = set(d.lower().lstrip('.') for d in rd_domains)
        # index by last label for quick longest-suffix match
        self.by_tail = {}
        for d in self.set:
            self.by_tail.setdefault(d.split('.')[-1], []).append(d)
    def canon(self, host):
        h = host_of(host) if ('://' in host or '/' in host) else host.lower().lstrip('.')
        if h.startswith('www.'):
            h = h[4:]
        if not h:
            return ''
        if h in self.set:
            return h
        # longest matching known domain that h ends with ('.'+d)
        cands = self.by_tail.get(h.split('.')[-1], [])
        best = ''
        for d in cands:
            if h == d or h.endswith('.' + d):
                if len(d) > len(best):
                    best = d
        if best:
            return best
        return registrable(h)

# ---------- Semrush backlinks ----------
BL_COLS = ['source_url','source_title','target_url','anchor','nofollow',
           'first_seen','last_seen','response_code','redirect_url','page_ascore']
_TAIL = re.compile(r';(true|false);(-?\d+);(-?\d+);(-?\d+);([^;]*);(-?\d+)\s*$', re.I)

def _parse_backlink_line(line):
    line = html.unescape(line.rstrip('\r\n'))
    parts = line.split(';')
    if len(parts) == 10 and parts[4].lower() in ('true','false'):
        return parts, 'clean'
    # repair using the structured 6-field tail
    m = _TAIL.search(line)
    if not m:
        return None, 'reject'
    nofollow, fs, ls, rc, redir, pasc = m.groups()
    head = line[:m.start()]                 # source_url;source_title;target_url;anchor
    i = head.find(';')
    if i < 0:
        return None, 'reject'
    source_url = head[:i]
    mid = head[i+1:]                         # source_title;target_url;anchor
    tm = re.search(r';(https?://)', mid)
    if not tm:
        # no target url with scheme; give up on middle split, reject
        return None, 'reject'
    source_title = mid[:tm.start()]
    rest2 = mid[tm.start()+1:]              # target_url;anchor
    j = rest2.find(';')
    if j < 0:
        target_url, anchor = rest2, ''
    else:
        target_url, anchor = rest2[:j], rest2[j+1:]
    return [source_url, source_title, target_url, anchor, nofollow, fs, ls, rc, redir, pasc], 'repair'

def load_backlinks(fetch_dir):
    rows, stats = [], {'clean':0,'repair':0,'reject':0,'files':0,'dupe_header':0}
    for path in sorted(glob.glob(os.path.join(fetch_dir, '*.csv'))):
        stats['files'] += 1
        with open(path, encoding='utf-8') as f:
            for ln, raw in enumerate(f):
                if not raw.strip():
                    continue
                if ln == 0 and raw.startswith('source_url;'):
                    continue
                if raw.startswith('source_url;'):   # repeated header mid-file
                    stats['dupe_header'] += 1
                    continue
                parsed, kind = _parse_backlink_line(raw)
                stats[kind] += 1
                if parsed is None:
                    continue
                d = dict(zip(BL_COLS, parsed))
                d['nofollow'] = d['nofollow'].lower() == 'true'
                for k in ('first_seen','last_seen','response_code','page_ascore'):
                    try: d[k] = int(d[k])
                    except: d[k] = None
                rows.append(d)
    return rows, stats

# ---------- Semrush referring domains ----------
RD_COLS = ['domain','backlinks_num','domain_authority_score','domain_score',
           'domain_trust_score','ip','country','first_seen','last_seen']
def load_refdomains(rd_dir):
    rows, seen, stats = [], {}, {'rows':0,'reject':0,'files':0,'dupe':0}
    for path in sorted(glob.glob(os.path.join(rd_dir, '*.csv'))):
        stats['files'] += 1
        with open(path, encoding='utf-8') as f:
            for ln, raw in enumerate(f):
                raw = html.unescape(raw.rstrip('\r\n'))
                if not raw.strip():
                    continue
                if raw.startswith('domain;'):
                    continue
                parts = raw.split(';')
                if len(parts) != 9:
                    stats['reject'] += 1
                    continue
                d = dict(zip(RD_COLS, parts))
                dom = d['domain'].lower().lstrip('.')
                if dom in seen:
                    stats['dupe'] += 1
                    continue
                seen[dom] = 1
                d['domain'] = dom
                for k in ('backlinks_num','domain_authority_score','domain_score',
                          'domain_trust_score','first_seen','last_seen'):
                    try: d[k] = int(d[k])
                    except:
                        try: d[k] = float(d[k])
                        except: d[k] = None
                rows.append(d)
                stats['rows'] += 1
    return rows, stats

# ---------- generic key=value metric CSVs we write ourselves ----------
def load_kv_csv(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out[row['domain'].lower().lstrip('.')] = row
    return out

if __name__ == '__main__':
    import sys, json
    base = sys.argv[1] if len(sys.argv) > 1 else '/home/user/test/bolton/data'
    bl, s1 = load_backlinks(os.path.join(base, 'fetch'))
    rd, s2 = load_refdomains(os.path.join(base, 'rd'))
    print('backlinks:', len(bl), s1)
    print('refdomains:', len(rd), s2)
    idx = DomainIndex([r['domain'] for r in rd])
    # quick sanity: how many backlink hosts map into the RD set
    inset = sum(1 for b in bl if idx.canon(b['source_url']) in idx.set)
    print('backlink rows whose source maps into Semrush RD set:', inset, '/', len(bl))
    # distinct canonical referring domains across all backlinks
    doms = set(idx.canon(b['source_url']) for b in bl)
    print('distinct canonical referring domains from backlinks:', len(doms))
