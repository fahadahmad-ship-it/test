#!/usr/bin/env python3
"""Verification of the rebuilt NFG audit workbook (post-polish)."""
import re, openpyxl
OUT = "/home/user/test/NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx"
wb = openpyxl.load_workbook(OUT)

PROV = {"Seen_SR","Seen_AH","AS_source","Ahrefs_DR_evid","Source"}
FORBIDDEN_SCORE = {"Opportunity_Score","Priority_Score","Tier","Unified_Priority_Score"}
EMEN = "—–―‒−→←⟶"  # em en bar figure minus arrows
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}$|^[A-Za-z]{3,9}-\d{4}$")
NEG_RX  = re.compile(r"^-\d[\d,]*%?$")

def prose_hyphens(s):
    n = 0
    for tok in re.split(r"\s+", s):
        if not tok: continue
        if "." in tok or "/" in tok: continue
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

print("=== 1. FREEZE PANES (prove header-only / low row) ===")
fp_ok = True
for ws in wb.worksheets:
    fp = ws.freeze_panes
    rownum = int(re.sub(r"[A-Z]+","",fp)) if fp else None
    low = (rownum is not None and rownum <= 5)
    if not low: fp_ok = False
    print(f"  {ws.title:34s} freeze={str(fp):6s} row={rownum} low(<=5)={low}")
print("  ALL FREEZE LOW:", fp_ok)

print("\n=== 2. NO PROVENANCE HEADER CELLS (Seen_SR/Seen_AH/AS_source/Ahrefs_DR/Source) ===")
prov_hits = [(ws.title, c.coordinate, c.value) for ws, c in all_str_cells() if c.value.strip() in PROV]
print("  provenance header/cell hits:", len(prov_hits))
for h in prov_hits: print("   ", h)

print("\n=== 3. NO INVENTED-SCORE HEADER/CELL (Opportunity_Score/Priority_Score/Tier/Unified_Priority_Score) ===")
score_hits = [(ws.title, c.coordinate, c.value) for ws, c in all_str_cells() if c.value.strip() in FORBIDDEN_SCORE]
print("  invented-score cell hits:", len(score_hits))
for h in score_hits: print("   ", h)

print("\n=== 4. SEGMENT LABELS 'Sector Body' / 'Commercial IFA' APPEAR NOWHERE ===")
seg_hits = [(ws.title, c.coordinate, c.value[:60]) for ws, c in all_str_cells()
            if "Sector Body" in c.value or "Commercial IFA" in c.value]
print("  segment-label hits:", len(seg_hits))
for h in seg_hits: print("   ", h)

print("\n=== 5. DASH / HYPHEN SCAN (every cell) ===")
emen = 0; prose = 0; prose_examples = []
for ws, c in all_str_cells():
    emen += sum(c.value.count(ch) for ch in EMEN)
    ph = prose_hyphens(c.value)
    if ph:
        prose += ph
        if len(prose_examples) < 12: prose_examples.append((ws.title, c.coordinate, c.value[:80]))
print("  em/en/bar/arrow dash characters:", emen, "(must be 0)")
print("  prose hyphens (token without . or /, not date/neg):", prose, "(must be 0)")
for e in prose_examples: print("   ", e)

print("\n=== 6. METHODOLOGY / README IS THE LAST SHEET ===")
last = wb.worksheets[-1].title
readme_last = ("README" in last) or ("Methodology" in last)
print("  last sheet:", last, "-> is methodology/README:", readme_last)

print("\n=== 7. TAB 2 HEADER ORDER (Client not Target; traffic early; no segment/role col) ===")
ws2 = wb["2 Competitor Benchmark"]
hdr2 = [ws2.cell(row=2, column=j).value for j in range(1, ws2.max_column+1)]
print("  first 6 headers:", hdr2[:6])
ti = next((i for i,h in enumerate(hdr2) if h and "Organic Traffic" in str(h)), None)
ai = next((i for i,h in enumerate(hdr2) if h and "Authority Score" in str(h)), None)
ri = next((i for i,h in enumerate(hdr2) if h and "Referring Domains" in str(h)), None)
no_seg = not any(h in ("Segment","Tag","Role") for h in hdr2)
traffic_early = ti is not None and ai < ti and ri < ti and ti <= 5
print(f"  idx AuthorityScore={ai} RefDomains={ri} OrganicTraffic={ti}  traffic_early={traffic_early}  no segment/role col={no_seg}")

print("\n=== 8. RANK LABEL WORDING ('NFG position out of 10') ===")
rank_labels = [ws2.cell(row=2, column=j).value for j in range(1, ws2.max_column+1)
               if ws2.cell(row=2, column=j).value and "position out of 10" in str(ws2.cell(row=2, column=j).value)]
bad_rank = [(ws.title, c.coordinate, c.value) for ws, c in all_str_cells()
            if c.value.strip() in ("Rank","NFG Rank /10","NFG rank out of 10")]
print("  benchmark 'position out of 10' headers:", rank_labels)
print("  leftover bare 'Rank' / 'NFG Rank /10' headers:", len(bad_rank), bad_rank)

print("\n=== 9. KEYWORD GAP SORTED BY SEARCH VOLUME DESC (Tab 6) ===")
ws6 = wb["6 Keyword Gap"]
h6 = [ws6.cell(row=3, column=j).value for j in range(1, ws6.max_column+1)]
vcol = h6.index("Search_Volume_UK") + 1
vols = []
rr = 4
while ws6.cell(row=rr, column=1).value:
    vols.append(ws6.cell(row=rr, column=vcol).value); rr += 1
kw_sorted = all(vols[i] >= vols[i+1] for i in range(len(vols)-1))
print(f"  {len(vols)} rows; volume descending:", kw_sorted, " first 6:", vols[:6])

print("\n=== 10. BACKLINK GAP SORTED BY AUTHORITY SCORE DESC + every row has AS (Tab 5) ===")
ws5 = wb["5 Backlink Gap Targets"]
h5 = [ws5.cell(row=2, column=j).value for j in range(1, ws5.max_column+1)]
ascol = h5.index("Authority_Score") + 1
as_vals = []
rr = 3
while ws5.cell(row=rr, column=1).value:
    as_vals.append(ws5.cell(row=rr, column=ascol).value); rr += 1
gap_rows = len(as_vals)
every_as = all(v is not None for v in as_vals)
as_sorted = all(as_vals[i] >= as_vals[i+1] for i in range(len(as_vals)-1) if as_vals[i] is not None and as_vals[i+1] is not None)
print(f"  Tab5 rows={gap_rows} (expect 866); every row has AS={every_as}; AS descending={as_sorted}; first 6 AS={as_vals[:6]}")

print("\n=== 11. STRUCTURE: tabs / row counts / charts ===")
print("  sheet count:", len(wb.worksheets), "(expect 12)")
for ws in wb.worksheets: print("   -", ws.title)
ws9 = wb["9 Competitor Link Detail"]
link_rows = sum(1 for rr in range(3, ws9.max_row+1) if ws9.cell(row=rr, column=1).value)
print("  Tab 9 link data rows:", link_rows, "(expect ~1453)")
ws1 = wb["1 Executive Scorecard"]
print("  Tab 1 (Exec Scorecard) charts:", len(ws1._charts), "(expect 2)")
chart_sheets = [ws.title for ws in wb.worksheets if len(ws._charts) > 0]
print("  sheets carrying charts:", chart_sheets, "(expect only Exec Scorecard)")

print("\n=== 12. MANDATED BACKLINK-AGE WORDING PRESENT ===")
found = [(ws.title, c.coordinate) for ws, c in all_str_cells() if "were acquired in the last 8 months" in c.value]
print("  cells with mandated sentence:", found)

print("\n=== SUMMARY ===")
checks = {
  "freeze all low": fp_ok,
  "no provenance cells": len(prov_hits)==0,
  "no invented-score cells": len(score_hits)==0,
  "no 'Sector Body'/'Commercial IFA'": len(seg_hits)==0,
  "em/en dashes == 0": emen==0,
  "prose hyphens == 0": prose==0,
  "methodology/README is last sheet": readme_last,
  "tab2 traffic early + no seg/role col": traffic_early and no_seg,
  "rank labels renamed": len(rank_labels)==2 and len(bad_rank)==0,
  "keyword gap sorted by volume desc": kw_sorted,
  "backlink gap sorted by AS desc": as_sorted,
  "tab5 every row has AS": every_as,
  "tab5==866": gap_rows==866,
  "tab9~1453": abs(link_rows-1453)<=3,
  "exec scorecard 2 charts": len(ws1._charts)==2,
  "charts only on exec scorecard": chart_sheets==["1 Executive Scorecard"],
  "12 tabs": len(wb.worksheets)==12,
  "mandated wording present": len(found)>=1,
}
for k,v in checks.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
print("ALL PASS:", all(checks.values()))
