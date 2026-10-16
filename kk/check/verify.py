"""Check the finished workbook and disavow files against the audit data.

Reads the saved .xlsx rather than the in-memory workbook, and reads the styling out of
the sheet XML, because openpyxl drops the styling of merged cells when it reads a file
back and would report a pass that is not there.
"""
import csv, collections, glob, re, sys, zipfile
import openpyxl

D = '/home/user/test/kk/data/'
XL = '/home/user/test/KandK_Manufacturing_Backlinks_Audit.xlsx'
fails = []
def ck(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)

AUD = list(csv.DictReader(open(D + 'domain_audit.csv'), delimiter='\t'))
LNK = list(csv.DictReader(open(D + 'links_all.csv'), delimiter='\t'))
ST = {r['domain']: r['status'] for r in AUD}
cnt = collections.Counter(r['status'] for r in AUD)

print('\n== disavow files ==')
allfile = set()
for p in sorted(glob.glob('/home/user/test/disavow_*.txt')):
    lines = [l.strip() for l in open(p) if l.strip() and not l.startswith('#')]
    doms = {l.split(':', 1)[1] for l in lines}
    allfile |= doms
    ck(all(l.startswith('domain:') for l in lines), f'{p.split("/")[-1]}: every line is a domain: directive')
    ck(len(doms) == len(lines), f'{p.split("/")[-1]}: no duplicate lines ({len(lines):,})')
    bad = sorted(d for d in doms if ST.get(d) != 'Spam (Disavow)')
    ck(not bad, f'{p.split("/")[-1]}: nothing but Spam (Disavow) in the file' + (f' -> {bad[:5]}' if bad else ''))

held = {r['domain'] for r in AUD if r['status'].startswith('Held')}
keep = {r['domain'] for r in AUD if r['status'] in ('Keep', 'Own Site')}
nofo = {r['domain'] for r in AUD if r['status'] == 'Spam (Nofollow, No Action)'}
ck(not (allfile & held), f'no Held domain reaches a file ({len(allfile & held)} found)')
ck(not (allfile & keep), f'no Keep or Own Site domain reaches a file ({len(allfile & keep)} found)')
ck(not (allfile & nofo), f'no nofollow-only domain reaches a file ({len(allfile & nofo)} found)')
expect = {r['domain'] for r in AUD if r['status'] == 'Spam (Disavow)' and r['redundant'] != 'Yes'}
ck(allfile == expect, f'the three files together carry exactly the {len(expect):,} disavow domains '
                      f'(files {len(allfile):,})')

print('\n== every disavow line rests on evidence, not on a score ==')
byd = collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
noev = [d for d in expect if not byd.get(d)]
ck(not noev, f'every disavowed domain has at least one link row ({len(noev)} without)')
nodof = [d for d in expect if not any(x['nofollow'] == 'false' for x in byd[d])]
ck(not nodof, f'every disavowed domain has at least one dofollow link ({len(nodof)} without)')
named = [d for d in expect if any(re.search(r'k ?& ?k|kandkmfg|kandkmanufacturing|gaworktrucks',
         (x['source_title'] or ''), re.I) and not re.search(r'backlink|seo|pbn|dofollow|premium|authority',
         (x['source_title'] or ''), re.I) for x in byd[d])]
ck(not named, f'no page whose title names the client without sales copy is in the file ({len(named)} found)')

print('\n== workbook ==')
wb = openpyxl.load_workbook(XL, read_only=True)
want = ['Summary', 'Referring Domain Audit', 'All Backlinks', 'Anchor Analysis',
        'Exact Match Anchors', 'Pending Disavow Lines', 'Disavow List']
ck(wb.sheetnames == want, f'seven tabs in the signed-off order: {wb.sheetnames}')
rows = {n: wb[n].max_row for n in wb.sheetnames}
ck(rows['Referring Domain Audit'] == len(AUD) + 1, f"Referring Domain Audit has one row per domain ({rows['Referring Domain Audit'] - 1:,} vs {len(AUD):,})")
ck(rows['All Backlinks'] == len(LNK) + 1, f"All Backlinks has one row per link ({rows['All Backlinks'] - 1:,} vs {len(LNK):,})")
ck(rows['Disavow List'] == len(expect) + 1, f"Disavow List has one row per disavow line ({rows['Disavow List'] - 1:,} vs {len(expect):,})")

ws = wb['Exact Match Anchors']
miss = blank = 0
doms_on_tab = set()
for r in ws.iter_rows(min_row=2, max_col=3, values_only=True):
    doms_on_tab.add(r[0])
    if not r[1]: miss += 1
    if not r[2]: blank += 1
ck(miss == 0, f'every decision row carries an example backlink ({miss} blank)')
ck(blank == 0, f'every decision row carries an anchor ({blank} blank)')
ck(held <= doms_on_tab, f'every Held domain appears on the decision tab '
                        f'({len(held - doms_on_tab)} missing)')

print('\n== Tab 05, the nine domains the client named ==')
t5 = sorted(r['domain'] for r in AUD if r['tab05'] == 'Yes')
ck(len(t5) == 9, f'all nine resolved: {len(t5)}')
for d in t5: print(f'       {d:28s} {ST[d]}')

print('\n== summary figures ==')
ws = wb['Summary']
vals = {}
for r in ws.iter_rows(min_row=1, max_col=2, values_only=True):
    if r[0] in cnt or r[0] == 'Total': vals[r[0]] = r[1]
for s, n in cnt.items():
    ck(vals.get(s) == n, f'Summary row "{s}" says {vals.get(s)}, data says {n}')
ck(vals.get('Total') == len(AUD), f'Summary total {vals.get("Total")} vs {len(AUD)}')

print('\n== styling, read from the sheet XML ==')
z = zipfile.ZipFile(XL)
wbxml = z.read('xl/workbook.xml').decode()
styles = z.read('xl/styles.xml').decode()
fonts = re.findall(r'<font>.*?</font>', styles, re.S)
# Font 0 is the workbook default Excel requires; openpyxl always writes Calibri there and
# it only ever reaches empty cells. The signed-off New Image Canopy file carries the same
# entry, so the test is that nothing BEYOND it is off-brand, plus the populated-cell check
# below.
badf = [f for f in fonts[1:] if 'Geist' not in f]
ck(not badf, f'every font beyond the workbook default is Geist ({len(badf)} others)')
offbrand = 0
for n in wb.sheetnames:
    for row in openpyxl.load_workbook(XL)[n].iter_rows():
        for c in row:
            if c.value is not None and (c.font.name != 'Geist' or c.font.sz not in (9, 10, 11)):
                offbrand += 1
ck(offbrand == 0, f'no populated cell uses anything but Geist at 9, 10 or 11 ({offbrand} do)')
szs = sorted({float(m) for m in re.findall(r'<sz val="([\d.]+)"/>', styles)})
ck(set(szs) <= {9.0, 10.0, 11.0}, f'font sizes used: {szs}')
ck('FF0C343D' in styles, 'the accent colour FF0C343D is in the palette')
names = [n for n in wb.sheetnames]
for i, n in enumerate(names, 1):
    sx = z.read(f'xl/worksheets/sheet{i}.xml').decode(errors='ignore')[:4000]
    grid = 'showGridLines="0"' not in sx
    if n == 'Summary':
        ck(not grid, 'Summary has gridlines off')
    else:
        ck(grid, f'{n} has gridlines on')
        ck('<pane ' in sx and 'B2' in sx, f'{n} is frozen at B2')
z2 = zipfile.ZipFile(XL)
for i, n in enumerate(names, 1):
    sx = z2.read(f'xl/worksheets/sheet{i}.xml').decode(errors='ignore')
    if n != 'Summary':
        ck('<autoFilter' in sx, f'{n} has an autofilter')

print('\n' + ('ALL CHECKS PASS' if not fails else f'{len(fails)} CHECK(S) FAILED'))
sys.exit(1 if fails else 0)
