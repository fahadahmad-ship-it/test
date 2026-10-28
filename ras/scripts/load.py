"""Robust loaders for Semrush (semicolon, unquoted) and Ahrefs (TSV, quoted) exports.
Semrush backlinks columns requested (in order):
  source_url;target_url;redirect_url;nofollow;response_code;page_ascore;first_seen;last_seen;anchor;source_title
First 8 fields are structured (no semicolons possible). anchor is field[8], source_title is field[9..].
On overflow (>10 fields) the surplus is rejoined into source_title (title far likelier to carry ';').
"""
import csv, glob, os, html
from urllib.parse import urlsplit

BL_COLS = ["source_url","target_url","redirect_url","nofollow","response_code",
           "page_ascore","first_seen","last_seen","anchor","source_title"]
NSTRUCT = 8  # fields 0..7 are structured

def _host(u):
    if not u: return ''
    u = u.strip()
    if not u: return ''
    if '://' not in u:
        u = 'http://' + u
    try:
        h = urlsplit(u).netloc.lower()
    except Exception:
        return ''
    if h.startswith('www.'):
        h = h[4:]
    # strip port
    if ':' in h:
        h = h.split(':')[0]
    return h

def host(u):
    return _host(u)

def canon(u):
    """canonical link id: strip scheme, www, trailing slash, lowercase"""
    if not u: return ''
    s = u.strip()
    if '://' in s:
        s = s.split('://',1)[1]
    s = s.lower()
    if s.startswith('www.'):
        s = s[4:]
    s = s.rstrip('/')
    return s

def load_semrush_backlinks(fetch_dir):
    rows = []
    bad = 0
    overflow = 0
    files = sorted(glob.glob(os.path.join(fetch_dir, 'bl_*.csv')), key=lambda p:int(''.join(c for c in os.path.basename(p) if c.isdigit()) or 0))
    seen_header = False
    for fp in files:
        with open(fp, encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.rstrip('\n').rstrip('\r')
                if not line:
                    continue
                if line.startswith('source_url;target_url;'):
                    seen_header = True
                    continue
                parts = line.split(';')
                if len(parts) < 10:
                    bad += 1
                    continue
                struct = parts[:NSTRUCT]
                rest = parts[NSTRUCT:]
                if len(rest) == 2:
                    anchor, title = rest[0], rest[1]
                else:
                    overflow += 1
                    anchor = rest[0]
                    title = ';'.join(rest[1:])
                d = dict(zip(BL_COLS[:NSTRUCT], struct))
                d['anchor'] = anchor
                d['source_title'] = title
                d['source'] = 'Semrush'
                rows.append(d)
    return rows, bad, overflow

def load_semrush_refdomains(rd_dir):
    rows = []
    files = sorted(glob.glob(os.path.join(rd_dir, 'rd_*.csv')))
    cols = ["domain","backlinks_num","domain_authority_score","domain_trust_score","ip","country","first_seen","last_seen"]
    for fp in files:
        with open(fp, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n').rstrip('\r')
                if not line or line.startswith('domain;'):
                    continue
                parts = line.split(';')
                if len(parts) < len(cols):
                    continue
                # domain has no semicolon; take first len(cols) fields
                d = dict(zip(cols, parts[:len(cols)]))
                rows.append(d)
    return rows

def load_ahrefs_backlinks(path):
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter='\t')
        rows = []
        for x in r:
            # normalise BOM/quote on first column name
            rows.append(x)
    return rows

def load_ahrefs_refdomains(path):
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter='\t')
        return list(r)

if __name__ == '__main__':
    import sys
    rows, bad, overflow = load_semrush_backlinks(sys.argv[1])
    print("semrush backlinks parsed:", len(rows), "bad(<10 fields):", bad, "overflow(>10):", overflow)
    from collections import Counter
    # field sanity: nofollow values, response codes
    print("nofollow values:", Counter(r['nofollow'] for r in rows).most_common())
    print("sample response_code:", Counter(r['response_code'] for r in rows).most_common(8))
    # target hosts
    th = Counter(_host(r['target_url']) for r in rows)
    print("target hosts:", th.most_common(12))
    # redirect_url presence
    redir = Counter(_host(r['redirect_url']) for r in rows if r['redirect_url'].strip())
    print("redirect_url hosts (non-empty):", redir.most_common(12))
    print("rows with redirect_url:", sum(1 for r in rows if r['redirect_url'].strip()))
    # source host count
    sh = set(_host(r['source_url']) for r in rows)
    print("distinct source hosts:", len(sh))
    # show a few overflow examples (anchors with ; ?) -- print rows where anchor contains weirdness
    # check anchors that look truncated
    print("sample anchors:")
    for r in rows[:3]:
        print("   ", repr(r['anchor'][:70]), "| title:", repr(r['source_title'][:50]))
