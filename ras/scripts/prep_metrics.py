"""After as_comparison.csv lands: (1) list domains still missing AS (new PSL domains),
(2) select the domain_rank subset (where organic traffic/keywords plausibly non-zero)."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import build

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(BASE, 'data', 'work')
M = os.path.join(BASE, 'data', 'metrics')

def main():
    all_doms = [l.strip() for l in open(os.path.join(W, 'domains_all.txt')) if l.strip()]
    as_doms = set()
    p = os.path.join(M, 'as_comparison.csv')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            if line.startswith('target;') or not line.strip():
                continue
            as_doms.add(line.split(';')[0].strip().lower())
    missing_as = [d for d in all_doms if d not in as_doms]
    with open(os.path.join(W, 'domains_missing_as.txt'), 'w') as f:
        for d in missing_as:
            f.write(d + '\n')
    print('total domains:', len(all_doms), '| have AS:', len(as_doms), '| missing AS:', len(missing_as))

    # Build records (uses whatever AS exists) to pick subset
    R = build()
    recs = R['records']
    subset = set()
    for r in recs:
        # organic traffic is a meaningful signal only for kept/held domains (genuineness,
        # and the "held has no traffic" finding) and for high-authority domains.
        if r['status'] == 'Keep' or r['base'] == 'Held' or (r['ascore'] or 0) >= 15 or r.get('ar_spam') is False:
            subset.add(r['domain'])
    # validation sample of spam-disavow domains (confirm NOTHING FOUND = real zero)
    spam = [r['domain'] for r in recs if r['status'] == 'Spam (Disavow)' and r['domain'] not in subset]
    random.seed(42)
    sample = random.sample(spam, min(60, len(spam)))
    subset.update(sample)
    with open(os.path.join(W, 'domains_rank_subset.txt'), 'w') as f:
        for d in sorted(subset):
            f.write(d + '\n')
    print('domain_rank subset size:', len(subset), f'(incl {len(sample)} spam validation sample)')

if __name__ == '__main__':
    main()
