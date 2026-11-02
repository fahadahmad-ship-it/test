"""Recover backlinks_comparison rows from the killed subagent's transcript JSONL,
without loading the file into the orchestrator context. Dedupe by target,
validate against the canonical domain set, write comparison.csv."""
import re, sys, glob
sys.path.insert(0, "/home/user/test/ritter/scripts")
from load import canon_domain

TRANS = sys.argv[1]
OUT = "/home/user/test/ritter/data/metrics/comparison.csv"

doms = set(canon_domain(l.strip()) for l in open("/home/user/test/ritter/data/domains.txt") if l.strip())

text = open(TRANS, "r", encoding="utf-8", errors="replace").read()
# unescape JSON string escapes for newlines so CSV rows become real lines
text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace('\\"', '"')

# comparison data row: target;ascore;backlinks_num;domains_num;follows_num;nofollows_num
row_re = re.compile(r'^([A-Za-z0-9][A-Za-z0-9.\-]*\.[A-Za-z0-9\-]+);(\d+);(\d+);(\d+);(\d+);(\d+)$')
found = {}
for line in text.split("\n"):
    line = line.strip()
    m = row_re.match(line)
    if not m:
        continue
    target = m.group(1)
    key = canon_domain(target)
    if key in doms and key not in found:
        found[key] = (target, m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))

with open(OUT, "w") as fh:
    fh.write("target;ascore;backlinks_num;domains_num;follows_num;nofollows_num\n")
    for key in sorted(found):
        fh.write(";".join(found[key]) + "\n")

missing = doms - set(found)
print(f"recovered comparison rows: {len(found)} of {len(doms)}")
print(f"missing: {len(missing)}")
if missing:
    print("  e.g.:", sorted(missing)[:20])
