"""
verify.py — exhaustive, both-directions correctness checks for the Bolton audit.
Recomputes the classification from source data and validates the emitted disavow files and
workbook. Prints PASS/FAIL per check and a final verdict. Nothing is sampled — every entry
is checked.

Usage: python3 -I bolton/check/verify.py
"""
import os, sys, re, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BASE, 'scripts'))
import build, classify
from classify import classify_anchor, link_property, host_of

OUT = os.path.join(BASE, 'out')
SPAM_DISAVOW = 'Spam (Disavow)'
SALES = 'Spam: keyword stuffed SEO sales copy'
OFF = 'Spam: off topic'

def read_disavow(path):
    doms, lines = [], open(path, encoding='utf-8').read().splitlines()
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('#'):
            continue
        doms.append(s)
    return doms

def main():
    ctx = build.build()
    rows = ctx['rows']; doms = sorted(rows.keys())
    aggs = {d: build.agg_domain(d, rows[d], ctx) for d in doms}
    fails = []; reviews = []; checks = 0
    def ck(cond, msg):
        nonlocal checks; checks += 1
        if not cond: fails.append(msg)

    disavow_set = {d for d in doms if rows[d]['status'] == SPAM_DISAVOW}

    # ---------- disavow-file integrity ----------
    money = os.path.join(OUT, f'disavow_{build.MONEY}.txt')
    files = {p: read_disavow(os.path.join(OUT, f'disavow_{p}.txt')) for p in build.PROPERTIES}
    for p, lines in files.items():
        seen = set()
        for ln in lines:
            ck(re.fullmatch(r'domain:[a-z0-9.\-]+', ln) is not None, f'{p}: bad line "{ln}"')
            ck(ln == ln.lower(), f'{p}: non-lowercase "{ln}"')
            ck('/' not in ln and 'http' not in ln, f'{p}: URL in line "{ln}"')
            ck(ln not in seen, f'{p}: duplicate "{ln}"')
            seen.add(ln)
            dom = ln.split(':',1)[1]
            ck(rows.get(dom, {}).get('status') == SPAM_DISAVOW, f'{p}: {dom} not Spam(Disavow)')
            ck(any(not L['nofollow'] for L in rows.get(dom,{}).get('links',[])),
               f'{p}: {dom} has no dofollow link')
        # redundant-child check
        sd = [l.split(':',1)[1] for l in lines]
        for d2 in sd:
            for d1 in sd:
                if d1 != d2 and d2.endswith('.'+d1):
                    fails.append(f'{p}: redundant child {d2} under {d1}');
        checks += 1

    money_doms = {l.split(':',1)[1] for l in files[build.MONEY]}
    ck(money_doms == {d for d in disavow_set}, 'money-site file != full union of Spam(Disavow)')
    # per-property = attribution set
    for p in build.REDIRECTS:
        attrib = set()
        for d in disavow_set:
            for L in rows[d]['links']:
                if link_property(L) == p: attrib.add(d)
        fdoms = {l.split(':',1)[1] for l in files[p]}
        ck(fdoms == attrib, f'{p} file != attribution set (file {len(fdoms)} vs attrib {len(attrib)})')
        ck(fdoms <= money_doms, f'{p} file not subset of money union')

    # ---------- no false positives (checked for ALL disavow domains) ----------
    for d in disavow_set:
        R = rows[d]
        ck(bool(R['evidence']) or 'host name' in R['reason'].lower() or 'template' in R['reason'].lower(),
           f'FALSE-POS: {d} disavowed with no visible evidence (reason={R["reason"]})')
        titles = ' '.join((L.get('source_title') or '') for L in R['links']).lower()
        names_client = 'bolton' in titles
        has_sales = classify._has(titles, classify.SALES_MARKERS) is not None
        if names_client and not has_sales:
            # allowed only if there is OTHER spam evidence (anchor/host/url)
            has_spam_anchor = any(classify_anchor(L['anchor'],L.get('target_url',''))[0] in (SALES,OFF)
                                  for L in R['links'])
            host_spam = classify._has(d, classify.SPAM_HOST_TOKENS) is not None
            ck(has_spam_anchor or host_spam,
               f'FALSE-POS?: {d} title names client w/o sales copy and weak evidence')
        # real traffic review (only where traffic known)
        tr = aggs[d]['traffic']
        if tr is not None and tr >= 50:
            reviews.append((d, tr, R['reason']))

    # ---------- no false negatives ----------
    for d in doms:
        st = rows[d]['status']
        if st == 'Keep':
            for L in rows[d]['links']:
                at,_ = classify_anchor(L['anchor'], L.get('target_url',''))
                if at in (SALES, OFF) and not L['nofollow']:
                    fails.append(f'FALSE-NEG: Keep {d} has dofollow spam anchor "{L["anchor"][:40]}"')
        if st in ('Spam (Nofollow, No Action)', 'Held (Nofollow, No Action)'):
            ck(all(L['nofollow'] for L in rows[d]['links']),
               f'FALSE-NEG: {st} {d} actually has a dofollow link')

    # ---------- workbook reconciliation ----------
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(OUT,'Bolton_Service_WNC_Backlinks_Audit.xlsx'))
    rd_rows = wb['Referring Domain Audit'].max_row - 1
    ab_rows = wb['All Backlinks'].max_row - 1
    dl_rows = wb['Disavow List'].max_row - 1
    pd_rows = wb['Pending Disavow Lines'].max_row - 1
    ck(rd_rows == len(doms), f'RD Audit rows {rd_rows} != domains {len(doms)}')
    total_links = sum(len(rows[d]['links']) for d in doms)
    ck(ab_rows == total_links, f'All Backlinks rows {ab_rows} != links {total_links}')
    ck(dl_rows == len(disavow_set), f'Disavow List rows {dl_rows} != disavow {len(disavow_set)}')
    ck(pd_rows == sum(1 for d in doms if rows[d]['status']=='Held (Pending Partner)'),
       f'Pending rows {pd_rows} != held-pending')

    # every Exact Match / decision row has a real example backlink
    emws = wb['Exact Match Anchors']
    for r in range(2, emws.max_row+1):
        dom = emws.cell(r,1).value; url = emws.cell(r,2).value
        if dom:
            ck(any(L['source_url']==url for L in rows.get(dom,{}).get('links',[])),
               f'Exact Match row {r}: example {url} not a real backlink of {dom}')

    print(f'Checks run: {checks} ; Failures: {len(fails)} ; Review items: {len(reviews)}')
    for f in fails[:80]:
        print('  FAIL:', f)
    if len(fails) > 80:
        print(f'  ... and {len(fails)-80} more')
    if reviews:
        print('  REVIEW (disavowed domains with organic traffic >=50 — confirm by hand):')
        for d, tr, rs in sorted(reviews, key=lambda x: -x[1]):
            print(f'    - {d}  traffic={tr:,}  reason={rs}')
    print('VERDICT:', 'PASS' if not fails else 'FAIL')
    return 0 if not fails else 1

if __name__ == '__main__':
    sys.exit(main())
