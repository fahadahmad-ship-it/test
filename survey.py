import csv, sys, collections
path = sys.argv[1]
built = set(l.strip().lower() for l in open('built.txt') if l.strip())
rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
print("total rows:", len(rows))
cats = collections.Counter()
for r in rows:
    for c in (r.get('Category') or '').split(','):
        c = c.strip()
        if c: cats[c] += 1
print("\ntop 45 categories:")
for c, n in cats.most_common(45):
    print(f"  {n:6d}  {c}")
doms = set((r.get('Website') or '').strip().lower() for r in rows)
print("\noverlap with already-built:", len(doms & built))
