#!/usr/bin/env python3
"""Verification suite for the Controlled Comfort audit (playbook §9, both directions).
Usage: verify.py <data_dir> <out_dir>
"""
import sys, os, json, csv, re
from collections import Counter
from openpyxl import load_workbook

DATA, OUT = sys.argv[1], sys.argv[2]
D = json.load(open(os.path.join(DATA, 'classified_domains.json')))
LINKS = list(csv.DictReader(open(os.path.join(DATA, 'classified_links.csv'))))
disavow = open(os.path.join(OUT, 'disavow_controlledcomfort.txt')).read().splitlines()
wb = load_workbook(os.path.join(OUT, 'controlled_comfort_backlink_audit.xlsx'))

fails, warns = [], []
def check(cond, msg):
    (fails if not cond else None)
    if not cond: fails.append(msg)

file_domains = [l.split(':', 1)[1] for l in disavow if l and not l.startswith('#')]

# 1. disavow line format
for dom in file_domains:
    check(re.match(r'^[a-z0-9.-]+$', dom) is not None, f"bad disavow line: {dom}")
    check('/' not in dom and 'http' not in dom, f"URL in disavow line: {dom}")
    check(dom == dom.lower(), f"non-lowercase disavow line: {dom}")
# 2. no duplicates
dups = [d for d, c in Counter(file_domains).items() if c > 1]
check(not dups, f"duplicate disavow lines: {dups}")
# 3. every file domain is Spam (Disavow)
leak = [d for d in file_domains if D.get(d, {}).get('status') != 'Spam (Disavow)']
check(not leak, f"non-Spam(Disavow) domains leaked into file: {leak[:10]}")
# 4. every file domain has >=1 dofollow link
nodof = [d for d in file_domains if D.get(d, {}).get('dofollow', 0) < 1]
check(not nodof, f"disavow domains with no dofollow link: {nodof[:10]}")
# 5. redundant child not emitted while parent present
fset = set(file_domains)
redun = [d for d in file_domains if any(d != p and d.endswith('.' + p) for p in fset)]
check(not redun, f"redundant child lines emitted: {redun[:10]}")
# 6. count reconciliation vs workbook
rda = wb['Referring Domain Audit']; allbl = wb['All Backlinks']; dl = wb['Disavow List']
check(rda.max_row - 1 == len(D), f"RDA rows {rda.max_row-1} != domains {len(D)}")
check(allbl.max_row - 1 == len(LINKS), f"All Backlinks rows {allbl.max_row-1} != links {len(LINKS)}")
# disavow list tab == emitted active lines (after redundancy)
emitted = [d for d in sorted(x for x, v in D.items() if v['status'] == 'Spam (Disavow)')
           if not any(d != p and d.endswith('.' + p) for p in {x for x, v in D.items() if v['status'] == 'Spam (Disavow)'})]
check(dl.max_row - 1 == len(emitted), f"Disavow List rows {dl.max_row-1} != emitted {len(emitted)}")
check(len(file_domains) == len(emitted), f"file lines {len(file_domains)} != emitted {len(emitted)}")
# 7. no Held/Keep in file; held count sanity
held = [d for d, v in D.items() if v['status'].startswith('Held')]
check(not (set(held) & fset), "a Held domain is in the disavow file")
# 8. both-directions evidence sweep
PBN = re.compile(r'premium seo backlink|buy backlink|dofollow backlink|pbn network|da ?\d{2}|pa ?\d{2}|'
                 r'increase your domain|whatsapp us|high quality .*backlink|link building|higher google ranking|'
                 r'if you had told me last year|ranking in europe is not the same', re.I)
OFF = re.compile(r'casino|gambling|pharma|viagra|cialis|escort|porn|erythromycin', re.I)
HOSTBAD = re.compile(r'\.store$|\.shop$|^\d+\.xyz$|buybacklink|backlink|seoexpress|rankforge|linkbaron|'
                     r'outrank|dapachecker|99backlink|worldtopbacklink|rankboost', re.I)
# false positives: every disavow domain must have visible evidence (host OR anchor OR offtopic title)
links_by = {}
for l in LINKS:
    links_by.setdefault(l['referring_domain'], []).append(l)
noevidence = []
for d in file_domains:
    ls = links_by.get(d, [])
    host_ev = bool(HOSTBAD.search(d))
    anchor_ev = any(PBN.search(l['anchor'] or '') or OFF.search((l['anchor'] or '') + ' ' + (l['title'] or '')) for l in ls)
    if not (host_ev or anchor_ev):
        noevidence.append(d)
check(not noevidence, f"disavow domains with NO visible evidence: {len(noevidence)} e.g. {noevidence[:12]}")
# false negatives: no Keep/Held domain has a dofollow PBN/offtopic anchor
fneg = []
for d, v in D.items():
    if v['status'].startswith(('Keep', 'Held')):
        for l in links_by.get(d, []):
            if l['nofollow'] == 'False' and (PBN.search(l['anchor'] or '') or OFF.search((l['anchor'] or ''))):
                fneg.append(d); break
check(not fneg, f"Keep/Held domains with dofollow spam anchor (false negatives): {fneg[:12]}")
# 9. no blank First Seen where refdomain data exists
blankfs = [d for d, v in D.items() if not str(v['first_seen']).strip()]
if blankfs: warns.append(f"blank First Seen: {len(blankfs)} domains")

print("=== VERIFY ===")
print(f"domains: {len(D)} | links: {len(LINKS)} | active disavow: {len(file_domains)} | held excluded: {len(held)}")
print(f"RDA rows: {rda.max_row-1} | All Backlinks rows: {allbl.max_row-1} | Disavow List rows: {dl.max_row-1}")
if warns: print("WARN:", *warns, sep='\n  - ')
if fails:
    print(f"\nFAILURES ({len(fails)}):")
    for f in fails: print("  ✗", f)
    sys.exit(1)
print("\nALL CHECKS PASSED ✓")
