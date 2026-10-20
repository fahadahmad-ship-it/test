#!/usr/bin/env python3
"""Adapt user-provided Semrush Bulk Analysis CSV exports into the as_recover.csv
format (semicolon; target;ascore;backlinks_num;domains_num;follows_num;nofollows_num)
that load_classify.py consumes. Pass the export CSV paths as arguments."""
import csv, io, sys, os
BASE="/home/user/test/offsite-backlink-audit/elitewrecker"
out=BASE+"/data/metrics/as_recover.csv"
rows={}
for path in sys.argv[1:]:
    with io.open(path,"r",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)  # comma-delimited, header row
        for d in r:
            tgt=(d.get("Target") or "").strip().lower()
            if not tgt: continue
            rows[tgt]=[tgt, d.get("Authority Score","").strip(), d.get("Backlinks","").strip(),
                       d.get("Domains","").strip(), d.get("Follow links","").strip(),
                       d.get("Nofollow links","").strip()]
with io.open(out,"w",encoding="utf-8",newline="") as f:
    f.write("target;ascore;backlinks_num;domains_num;follows_num;nofollows_num\n")
    for tgt in sorted(rows):
        f.write(";".join(rows[tgt])+"\n")
# coverage vs need_as.txt
need=set(l.strip() for l in open(BASE+"/data/metrics/need_as.txt") if l.strip())
got=set(rows.keys())
print(f"ingested {len(rows)} AS rows -> {out}")
print(f"need_as: {len(need)} | covered now: {len(need & got)} | still missing: {len(need - got)}")
miss=sorted(need-got)
if miss: print("  still-missing sample:", miss[:20])
