"""Merge per-domain Semrush metrics into merged.json.
Usage: python3 -I apply_metrics.py <merged.json> <metricsdir> <out.json>
AS: prefer backlinks_comparison (agrees with overview) over the refdomain report.
NOTHING FOUND from domain_rank = real zero.
"""
import sys, os, json, glob

MERGED, MDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(MERGED, encoding="utf-8"))

as_map = {}   # domain -> (ascore, domains_num)
for p in sorted(glob.glob(os.path.join(MDIR, "as_*.csv"))):
    with open(p, encoding="utf-8", errors="replace") as fh:
        head = fh.readline()
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 4:
                continue
            dom = parts[0].strip().lower()
            try:
                asc = int(float(parts[1]))
            except Exception:
                asc = None
            try:
                dn = int(float(parts[3]))
            except Exception:
                dn = None
            as_map[dom] = (asc, dn)

dr_map = {}   # domain -> (organic_keywords, organic_traffic)
for p in sorted(glob.glob(os.path.join(MDIR, "dr_*.csv"))):
    with open(p, encoding="utf-8", errors="replace") as fh:
        head = fh.readline()
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 3:
                continue
            dom = parts[0].strip().lower()
            try:
                kw = int(float(parts[1]))
            except Exception:
                kw = 0
            try:
                tr = int(float(parts[2]))
            except Exception:
                tr = 0
            dr_map[dom] = (kw, tr)

hit_as = hit_dr = 0
for r in data:
    d = r["domain"]
    if d in as_map:
        asc, dn = as_map[d]
        if asc is not None:
            r["as"] = asc          # prefer comparison AS
        r["rds"] = dn
        hit_as += 1
    else:
        r.setdefault("rds", None)
    if d in dr_map:
        kw, tr = dr_map[d]
        r["organic_keywords"] = kw
        r["traffic"] = tr
        hit_dr += 1
    else:
        r["organic_keywords"] = 0
        r["traffic"] = 0

json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print(f"applied metrics: AS/RDs for {hit_as}/{len(data)}, traffic/kw for {hit_dr}/{len(data)}")
missing_as = [r["domain"] for r in data if r.get("as") is None]
print(f"  domains with no AS at all: {len(missing_as)} {missing_as[:5]}")
