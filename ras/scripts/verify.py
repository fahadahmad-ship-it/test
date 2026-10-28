"""Both-directions correctness checks for the RAS Systems audit (playbook section 9)."""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import build, OWNED, MONEY_SITE
from classify import title_names_client_clean
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'out')

def main():
    R = build()
    records = R['records']
    links = R['links']
    by_dom = {r['domain']: r for r in records}
    dom_links = defaultdict(list)
    for l in links:
        dom_links[l['referring_domain']].append(l)
    fails = []
    warns = []

    disavow = [r for r in records if r['status'] == 'Spam (Disavow)']
    disavow_set = set(r['domain'] for r in disavow)
    held = [r for r in records if r['base'] == 'Held']
    keep = [r for r in records if r['status'] == 'Keep']

    SPAM_ATYPES = {'Spam: keyword stuffed SEO sales copy', 'Spam: off topic'}

    # ---- disavow file integrity ----
    files = glob.glob(os.path.join(OUT, 'disavow_*.txt'))
    file_domains = {}
    for fp in files:
        prop = os.path.basename(fp)[len('disavow_'):-4]
        doms = []
        with open(fp, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if not line.startswith('domain:'):
                    fails.append(f"{os.path.basename(fp)}: non-domain line {line!r}")
                    continue
                d = line[len('domain:'):]
                if d != d.lower() or '/' in d or ' ' in d or 'http' in d:
                    fails.append(f"{os.path.basename(fp)}: malformed domain {d!r}")
                doms.append(d)
        if len(doms) != len(set(doms)):
            fails.append(f"{os.path.basename(fp)}: duplicate domain lines")
        file_domains[prop] = set(doms)
        # every file domain must be Spam (Disavow)
        for d in doms:
            rec = by_dom.get(d)
            if rec is None:
                fails.append(f"{os.path.basename(fp)}: {d} not a known referring domain")
            elif rec['status'] != 'Spam (Disavow)':
                fails.append(f"{os.path.basename(fp)}: {d} has status {rec['status']} (leak!)")
            elif not rec['has_dofollow']:
                fails.append(f"{os.path.basename(fp)}: {d} has NO dofollow link")

    # money-site file == full union
    money = file_domains.get(MONEY_SITE, set())
    if money != disavow_set:
        fails.append(f"money-site file != full union (file={len(money)} union={len(disavow_set)}, "
                     f"missing={len(disavow_set-money)}, extra={len(money-disavow_set)})")
    # per-property files == attribution set
    for prop in ('rasmachines.com', 'ras-systems.net', 'ras-systems.us'):
        attrib = set(r['domain'] for r in disavow
                     if any(l['property'] == prop for l in dom_links[r['domain']]))
        if prop in file_domains and file_domains[prop] != attrib:
            fails.append(f"{prop} file != attribution set (file={len(file_domains[prop])} attrib={len(attrib)})")

    # ---- no false positives ----
    for r in disavow:
        dls = dom_links[r['domain']]
        has_evidence = (
            any(l['atype'] in SPAM_ATYPES for l in dls) or
            any(m in r['domain'] for m in ['seo','backlink','pbn','directory','listing','dapa','rankchecker','linkk','masslinker','guestpost']) or
            any(any(t in (l['title'] or '').lower() for t in ['backlink','pbn','buy aged domains','domain list page','publish your own backlinks','dofollow backlinks']) for l in dls)
        )
        if not has_evidence:
            fails.append(f"FALSE POSITIVE: {r['domain']} in disavow with NO visible evidence (reason={r['reason']})")
        # clean citation leak
        if any(title_names_client_clean(l['title']) for l in dls) and not any(l['atype'] in SPAM_ATYPES for l in dls):
            warns.append(f"REVIEW: {r['domain']} disavowed but a title names client without sales copy")
        if r['traffic'] and r['traffic'] > 0:
            warns.append(f"REVIEW: disavow domain {r['domain']} has organic traffic {r['traffic']}")

    # ---- no false negatives ----
    for r in keep + held:
        dls = dom_links[r['domain']]
        dofollow_spam = [l for l in dls if l['dofollow'] and l['atype'] in SPAM_ATYPES]
        if dofollow_spam:
            # allowed only if kept by AS>=20 genuine
            if not (r['status'] == 'Keep' and r['ascore'] >= 20):
                fails.append(f"FALSE NEGATIVE: {r['domain']} ({r['status']}) has {len(dofollow_spam)} dofollow spam link(s)")
            else:
                warns.append(f"NOTE: high-AS Keep {r['domain']} (AS {r['ascore']}) carries a dofollow spam anchor (kept per AS>=20 rule)")
    # nofollow-marked spam actually dofollow
    for r in records:
        if r['status'] in ('Spam (Nofollow, No Action)', 'Held (Nofollow, No Action)'):
            if any(l['dofollow'] for l in dom_links[r['domain']]):
                fails.append(f"NOFOLLOW MISLABEL: {r['domain']} marked nofollow but has a dofollow link")

    # ---- reconcile counts ----
    n_rows_rd = len(records)
    n_links = len(links)
    # one row per domain
    if len(set(r['domain'] for r in records)) != n_rows_rd:
        fails.append("duplicate domain rows in RD audit")

    print(f"records={len(records)} links={len(links)} disavow={len(disavow)} held={len(held)} keep={len(keep)}")
    print(f"disavow files: {sorted(os.path.basename(f) for f in files)}")
    print(f"\nFAILURES: {len(fails)}")
    for x in fails[:60]:
        print("  FAIL:", x)
    print(f"\nWARNINGS/REVIEW: {len(warns)}")
    for x in warns[:40]:
        print("  WARN:", x)
    if not fails:
        print("\nALL HARD CHECKS PASSED")

if __name__ == '__main__':
    main()
