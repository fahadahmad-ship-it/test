#!/usr/bin/env python3
"""Verification of the rebuilt NFG audit workbook (full backlink audit + reorder)."""
import re, openpyxl
OUT = "/home/user/test/NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx"
wb = openpyxl.load_workbook(OUT)

PROV = {"Seen_SR","Seen_AH","AS_source","Ahrefs_DR_evid","Source","DR","Ahrefs_DR"}
EMEN = "—–―‒−→←⟶"  # em en bar figure minus arrows
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}$|^[A-Za-z]{3,9}-\d{4}$")
NEG_RX  = re.compile(r"^-\d[\d,]*%?$")

def prose_hyphens(s):
    n = 0
    for tok in re.split(r"\s+", s):
        if not tok: continue
        if "." in tok or "/" in tok or ":" in tok: continue
        core = tok.strip(" \t.,;:!?()[]{}\"'•")
        if DATE_RX.match(core): continue
        if NEG_RX.match(core): continue
        n += tok.count("-")
    return n

def all_str_cells():
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    yield ws, c

EXPECTED = ["1 Executive Scorecard","2 Competitor Benchmark","3 NFG Referring Domains",
 "4 NFG Backlinks","5 Anchors & Toxicity","6 NFG Keyword Profile","7 Backlink Gap Targets",
 "8 Keyword Gap","9 Regional Whitespace Map","10 Competitor Link Detail",
 "11 Priority Target List","12 README & Methodology"]

print("=== 1. TAB LIST / ORDER ===")
titles = [ws.title for ws in wb.worksheets]
for t in titles: print("   -", t)
order_ok = titles == EXPECTED
print("  order matches expected 12-tab layout:", order_ok)
print("  tab count == 12:", len(titles) == 12)
print("  no Data Dictionary tab:", not any("Data Dictionary" in t for t in titles))
print("  methodology/README is LAST:", ("README" in titles[-1] or "Methodology" in titles[-1]))

print("\n=== 2. FREEZE HEADER-ONLY (every tab, freeze row <=5) ===")
fp_ok = True
for ws in wb.worksheets:
    fp = ws.freeze_panes
    rn = int(re.sub(r"[A-Z]+","",fp)) if fp else None
    low = rn is not None and rn <= 5
    if not low: fp_ok = False
    print(f"   {ws.title:28s} freeze={str(fp):5s} row={rn} ok={low}")
print("  ALL FREEZE LOW:", fp_ok)

print("\n=== 3. TAB 3 NFG Referring Domains: rows + AS + traffic ===")
ws3 = wb["3 NFG Referring Domains"]
h3 = [ws3.cell(row=3, column=j).value for j in range(1, ws3.max_column+1)]
print("  headers:", [h for h in h3 if h])
ci = {h: i+1 for i, h in enumerate(h3) if h}
as_c, tr_c, act_c = ci["Authority_Score"], ci["Organic_Traffic"], ci["Recommended_Action"]
rows3 = 0; missing_as = 0; missing_tr = 0; bad_act = 0
acts3 = set()
rr = 4
while ws3.cell(row=rr, column=1).value:
    rows3 += 1
    if ws3.cell(row=rr, column=as_c).value is None: missing_as += 1
    if ws3.cell(row=rr, column=tr_c).value is None: missing_tr += 1
    a = ws3.cell(row=rr, column=act_c).value
    if a not in ("Keep","Review","Disavow"): bad_act += 1
    else: acts3.add(a)
    rr += 1
print(f"  referring-domain rows: {rows3} (expect ~420)")
print(f"  rows missing Authority_Score: {missing_as}; missing Organic_Traffic: {missing_tr}")
print(f"  rows with bad/blank Recommended_Action: {bad_act}; actions seen: {sorted(acts3)}")
intro3 = " ".join(str(ws3.cell(row=n, column=1).value or "") for n in (1,2))
print("  intro mentions 'referring domains':", "referring domains" in intro3.lower())
print("  intro points to Backlinks tab:", "backlinks tab" in intro3.lower())

print("\n=== 4. TAB 4 NFG Backlinks: rows + anchor + action, sorted ===")
ws4 = wb["4 NFG Backlinks"]
h4 = [ws4.cell(row=3, column=j).value for j in range(1, ws4.max_column+1)]
print("  headers:", [h for h in h4 if h])
c4 = {h: i+1 for i, h in enumerate(h4) if h}
an_c, ac_c, pa_c = c4["Anchor"], c4["Recommended_Action"], c4["Page_Authority_Score"]
rows4 = 0; blank_anchor = 0; bad_act4 = 0
order_seq = []
rr = 4
while ws4.cell(row=rr, column=1).value:
    rows4 += 1
    av = ws4.cell(row=rr, column=an_c).value
    if av is None or str(av).strip() == "": blank_anchor += 1
    a = ws4.cell(row=rr, column=ac_c).value
    if a not in ("Keep","Review","Disavow"): bad_act4 += 1
    order_seq.append(a)
    rr += 1
rank = {"Disavow":0,"Review":1,"Keep":2}
grouped_ok = all(rank.get(order_seq[i],9) <= rank.get(order_seq[i+1],9) for i in range(len(order_seq)-1))
from collections import Counter
print(f"  backlink rows: {rows4} (expect ~1700+)")
print(f"  rows with blank anchor: {blank_anchor}; bad/blank action: {bad_act4}")
print(f"  action distribution: {dict(Counter(order_seq))}")
print(f"  grouped Disavow->Review->Keep:", grouped_ok)

print("\n=== 5. DASH / HYPHEN SCAN (every cell) ===")
emen = 0; prose = 0; ex = []
for ws, c in all_str_cells():
    emen += sum(c.value.count(ch) for ch in EMEN)
    ph = prose_hyphens(c.value)
    if ph:
        prose += ph
        if len(ex) < 10: ex.append((ws.title, c.coordinate, c.value[:70]))
print("  em/en/bar/arrow dash characters:", emen, "(must be 0)")
print("  prose hyphens:", prose, "(must be 0)")
for e in ex: print("    ", e)

print("\n=== 6. NO PROVENANCE COLUMNS / CELLS ===")
prov = [(ws.title, c.coordinate, c.value) for ws, c in all_str_cells() if c.value.strip() in PROV]
print("  provenance header/cell hits:", len(prov), prov[:6])

print("\n=== 7. CLIENT NOT TARGET (NFG never labelled 'Target') ===")
# The Priority tab's 'Target' column is a legitimate outreach-target header, so we only flag
# cells that label the CLIENT (NFG) as a Target / Is_NFG-style provenance column.
bad_target = [(ws.title, c.coordinate, c.value) for ws, c in all_str_cells()
              if c.value.strip() in ("Is_NFG","Is_Target","NFG (Target)","Target Domain","Target_Domain")]
has_client = any("client" in c.value.lower() for _, c in all_str_cells())
print("  NFG-labelled-as-Target cells:", len(bad_target), bad_target[:4])
print("  'Client' terminology present in workbook:", has_client)

print("\n=== 8. EXISTING TABS STILL POPULATED ===")
def datarows(title, hdr_row):
    ws = wb[title]
    n = 0; rr = hdr_row+1
    while ws.cell(row=rr, column=1).value not in (None, ""):
        n += 1; rr += 1
    return n
for t, hr, exp in [("2 Competitor Benchmark",2,10),("5 Anchors & Toxicity",5,10),
                   ("6 NFG Keyword Profile",3,900),("7 Backlink Gap Targets",2,866),
                   ("8 Keyword Gap",3,10),("9 Regional Whitespace Map",3,5),
                   ("10 Competitor Link Detail",2,1400),("11 Priority Target List",2,50)]:
    n = datarows(t, hr)
    print(f"   {t:28s} data rows={n}")

print("\n=== 9. CHARTS ONLY ON EXEC SCORECARD ===")
chart_sheets = [ws.title for ws in wb.worksheets if len(ws._charts) > 0]
print("  sheets carrying charts:", chart_sheets)
print("  exec scorecard chart count:", len(wb["1 Executive Scorecard"]._charts))
print("  charts only on Exec Scorecard:", chart_sheets == ["1 Executive Scorecard"])

print("\n=== 10. MANDATED AGE WORDING PRESENT ===")
found = [(ws.title, c.coordinate) for ws, c in all_str_cells() if "were acquired in the last 8 months" in c.value]
print("  cells with mandated sentence:", found)

print("\n=== SUMMARY ===")
checks = {
  "12 tabs in exact order": order_ok and len(titles)==12,
  "no Data Dictionary tab": not any("Data Dictionary" in t for t in titles),
  "methodology/README last": ("README" in titles[-1] or "Methodology" in titles[-1]),
  "freeze header-only all tabs": fp_ok,
  "Tab3 ~420 ref-domain rows": abs(rows3-420) <= 20,
  "Tab3 every row has AS": missing_as == 0,
  "Tab3 every row has traffic value": missing_tr == 0,
  "Tab3 every row has action": bad_act == 0,
  "Tab3 intro says referring domains": "referring domains" in intro3.lower(),
  "Tab4 >=1700 backlink rows": rows4 >= 1700,
  "Tab4 every row has anchor": blank_anchor == 0,
  "Tab4 every row has action": bad_act4 == 0,
  "Tab4 grouped Disavow/Review/Keep": grouped_ok,
  "0 em/en dashes": emen == 0,
  "0 prose hyphens": prose == 0,
  "no provenance columns": len(prov) == 0,
  "Client not Target": len(bad_target) == 0 and has_client,
  "charts only on Exec Scorecard": chart_sheets == ["1 Executive Scorecard"],
  "mandated age wording present": len(found) >= 1,
}
for k, v in checks.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
print("ALL PASS:", all(checks.values()))
