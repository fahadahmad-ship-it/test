"""Exhaustive correctness checks (both directions) on the audit outputs.
Usage: python3 -I verify.py <classified.json> <workbook.xlsx> <disavow.txt>
Fails loudly on any integrity / false-positive / false-negative problem.
"""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from openpyxl import load_workbook

data = json.load(open(sys.argv[1], encoding="utf-8"))
wb = load_workbook(sys.argv[2])
disavow_path = sys.argv[3]
fails = []
warns = []
def fail(m): fails.append(m)
def warn(m): warns.append(m)

byd = {r["domain"]: r for r in data}
disav = [r for r in data if r["status"] == "Spam (Disavow)"]
disav_set = {r["domain"] for r in disav}

# ---------- disavow file integrity ----------
lines = open(disavow_path, encoding="utf-8").read().splitlines()
file_doms = []
for ln in lines:
    s = ln.strip()
    if not s or s.startswith("#"):
        continue
    if not re.fullmatch(r"domain:[a-z0-9.\-]+", s):
        fail(f"disavow line malformed: {ln!r}")
        continue
    if s != s.lower():
        fail(f"disavow line not lowercase: {ln!r}")
    file_doms.append(s[len("domain:"):])
if len(file_doms) != len(set(file_doms)):
    dup = [d for d, c in collections.Counter(file_doms).items() if c > 1]
    fail(f"duplicate disavow lines: {dup[:5]}")
file_set = set(file_doms)

# every file domain is Spam (Disavow); no Held/Keep/Own leaks
for d in file_set:
    r = byd.get(d)
    if r is None:
        fail(f"disavow domain not in dataset: {d}")
    elif r["status"] != "Spam (Disavow)":
        fail(f"non-disavow status in file: {d} = {r['status']}")
# every file domain has >=1 dofollow
for d in file_set:
    if byd.get(d) and byd[d]["dofollow"] < 1:
        fail(f"disavow domain with no dofollow link: {d}")
# money-site file == full union of Spam(Disavow)
if file_set != disav_set:
    miss = disav_set - file_set; extra = file_set - disav_set
    fail(f"disavow file != Spam(Disavow) union. missing {len(miss)} {list(miss)[:5]}, extra {len(extra)} {list(extra)[:5]}")

# ---------- no false positives (good link wrongly disavowed) ----------
for r in disav:
    ev = r["evidence"]
    has_ev = any([ev["pbn"], ev["offtopic"], ev["spam_host"], ev["spam_title"],
                  ev["throwaway"], ev["numeric_host"], ev["network_host"]])
    if not has_ev:
        fail(f"disavow domain with NO visible evidence: {r['domain']}")
    if r.get("traffic", 0) and r["traffic"] >= 500:
        warn(f"disavow domain with real organic traffic (review by hand): {r['domain']} traffic={r['traffic']}")

# ---------- no false negatives (bad link wrongly kept out) ----------
for r in data:
    if r["status"].startswith(("Keep", "Held")):
        # dofollow off-topic anchor must not hide in Keep/Held
        for l in r["links"]:
            if (not l["nofollow"]) and l.get("anchor_type") == "Spam: off topic":
                fail(f"{r['status']} domain has dofollow OFF-TOPIC anchor: {r['domain']}")
                break
    if r["status"] == "Spam (Nofollow, No Action)":
        if r["dofollow"] > 0:
            fail(f"nofollow-spam domain actually has {r['dofollow']} dofollow links: {r['domain']}")

# Keep with a dofollow PBN sales-copy anchor (strict: Keep must be clean)
for r in data:
    if r["status"] == "Keep":
        for l in r["links"]:
            if (not l["nofollow"]) and l.get("anchor_type") == "Spam: keyword stuffed SEO sales copy":
                fail(f"Keep domain has dofollow PBN anchor: {r['domain']}")
                break

# ---------- workbook reconciliation ----------
by_status = collections.Counter(r["status"] for r in data)
ws = wb["Referring Domain Audit"]
rda_rows = ws.max_row - 1
if rda_rows != len(data):
    fail(f"Referring Domain Audit rows {rda_rows} != domains {len(data)}")
ws = wb["Disavow List"]
dl_rows = ws.max_row - 1
if dl_rows != len(disav):
    fail(f"Disavow List rows {dl_rows} != Spam(Disavow) {len(disav)}")
ws = wb["Pending Disavow Lines"]
pend = ws.max_row - 1
held_pp = by_status.get("Held (Pending Partner)", 0)
if pend != held_pp:
    fail(f"Pending Disavow rows {pend} != Held(Pending Partner) {held_pp}")

# Summary numbers re-derive
ws = wb["Summary"]
# status table rows 4-9
sm = {}
for r in range(4, 10):
    s = ws.cell(row=r, column=1).value
    dom = ws.cell(row=r, column=2).value
    if s:
        sm[s] = dom
for s, cnt in by_status.items():
    if s in sm and sm[s] != cnt:
        fail(f"Summary count mismatch {s}: sheet {sm[s]} vs data {cnt}")
tot = ws.cell(row=10, column=2).value
if tot != len(data):
    fail(f"Summary total {tot} != {len(data)}")

# every decision-tab row has a real example backlink (Disavow List top anchor present)
ws = wb["Referring Domain Audit"]
blank_fs = 0
for r in range(2, ws.max_row+1):
    dom = ws.cell(row=r, column=1).value
    rec = byd.get(dom)
    fs = ws.cell(row=r, column=11).value
    if rec and rec.get("first_seen") and fs in (None, ""):
        blank_fs += 1
if blank_fs:
    fail(f"{blank_fs} rows have blank First Seen where data exists")

# Exact Match Anchors rows all have an example linking page
ws = wb["Exact Match Anchors"]
for r in range(2, ws.max_row+1):
    if ws.cell(row=r,column=1).value and not ws.cell(row=r,column=2).value:
        fail(f"Exact Match Anchors row {r} missing example backlink")
        break

print(f"=== VERIFY: {len(fails)} failures, {len(warns)} warnings ===")
for f in fails:
    print("  FAIL:", f)
for w in warns[:20]:
    print("  warn:", w)
if warns and len(warns) > 20:
    print(f"  ... and {len(warns)-20} more warnings")
sys.exit(1 if fails else 0)
