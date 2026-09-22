#!/usr/bin/env python3
"""Verification of the rebuilt NFG audit workbook."""
import re, openpyxl
OUT = "/home/user/test/NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx"
wb = openpyxl.load_workbook(OUT)

PROV = {"Seen_SR","Seen_AH","AS_source","Ahrefs_DR_evid","Source"}
EMEN = "—–―‒−→←⟶"  # em en bar figure minus arrows
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}$|^[A-Za-z]{3,9}-\d{4}$")
NEG_RX  = re.compile(r"^-\d[\d,]*%?$")

def prose_hyphens(s):
    # count hyphens in whitespace tokens that are NOT dot/slash tokens (domains, URLs,
    # paths), NOT numeric date timestamps (YYYY-MM-DD / YYYY-MM, which are data and must
    # not be corrupted), and NOT negative numbers. Anything left is a prose compound hyphen.
    n = 0
    for tok in re.split(r"\s+", s):
        if not tok: continue
        if "." in tok or "/" in tok: continue
        core = tok.strip(" \t.,;:!?()[]{}\"'•")
        if DATE_RX.match(core): continue
        if NEG_RX.match(core): continue
        n += tok.count("-")
    return n

print("=== 1. FREEZE PANES (prove header-only / low row) ===")
fp_ok = True
for ws in wb.worksheets:
    fp = ws.freeze_panes
    rownum = int(re.sub(r"[A-Z]+","",fp)) if fp else None
    low = (rownum is not None and rownum <= 5)
    if not low: fp_ok = False
    print(f"  {ws.title:34s} freeze={str(fp):6s} row={rownum} low(<=5)={low}")
print("  ALL FREEZE LOW:", fp_ok)

print("\n=== 2. NO PROVENANCE HEADER CELLS (Seen_SR/Seen_AH/AS_source/Ahrefs_DR_evid/Source) ===")
prov_hits = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.strip() in PROV:
                prov_hits.append((ws.title, c.coordinate, c.value))
print("  provenance header/cell hits:", len(prov_hits))
for h in prov_hits: print("   ", h)

print("\n=== 3. DASH / HYPHEN SCAN (every cell) ===")
emen = 0; prose = 0; prose_examples = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str):
                emen += sum(c.value.count(ch) for ch in EMEN)
                ph = prose_hyphens(c.value)
                if ph:
                    prose += ph
                    if len(prose_examples) < 12:
                        prose_examples.append((ws.title, c.coordinate, c.value[:80]))
print("  em/en/bar/arrow dash characters:", emen, "(must be 0)")
print("  prose hyphens (token without . or /, not date/neg):", prose, "(must be 0)")
for e in prose_examples: print("   ", e)

print("\n=== 4. TAB 2 HEADER ORDER (Organic Traffic among first metrics) ===")
ws2 = wb["2 Competitor Benchmark"]
hdr2 = [ws2.cell(row=2, column=j).value for j in range(1, ws2.max_column+1)]
print("  first 8 headers:", hdr2[:8])
ti = next((i for i,h in enumerate(hdr2) if h and "Organic Traffic" in str(h)), None)
ai = next((i for i,h in enumerate(hdr2) if h and "Authority Score" in str(h)), None)
ri = next((i for i,h in enumerate(hdr2) if h and "Referring Domains" in str(h)), None)
print(f"  idx AuthorityScore={ai} RefDomains={ri} OrganicTraffic={ti}")
print("  traffic right after AS+RefDomains and early:", ti is not None and ai < ti and ri < ti and ti <= 6)

print("\n=== 5. NO '8 month old' / arrows / NFG-as-Target ===")
bad8 = []; arrows = []; targ = []; eight_month_any = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str):
                v = c.value
                low = v.lower()
                if "8 month old" in low or "month-old" in low or "month old profile" in low:
                    bad8.append((ws.title, c.coordinate, v[:60]))
                if "->" in v or "→" in v:
                    arrows.append((ws.title, c.coordinate, v[:60]))
                if "8 month" in low:
                    eight_month_any.append((ws.title, c.coordinate, v[:90]))
                for pat in ("nfg (target", "nfg the target", "nfg is the target", "as the target", "target (nfg", "the target)"):
                    if pat in low:
                        targ.append((ws.title, c.coordinate, v[:80]))
print("  '8 month old' style defect cells:", len(bad8), bad8)
print("  arrow ('->'/→) cells:", len(arrows), arrows[:5])
print("  NFG-called-Target cells:", len(targ), targ)
print("  (info) cells containing bare '8 month' (should only be the mandated 'last 8 months' sentence):")
for e in eight_month_any: print("    ", e)

print("\n=== 6. STRUCTURE: tabs / row counts / charts ===")
print("  sheet count:", len(wb.worksheets), "(expect 12)")
for ws in wb.worksheets: print("   -", ws.title)
ws5 = wb["5 Backlink Gap Targets"]
gap_rows = sum(1 for rr in range(3, ws5.max_row+1) if ws5.cell(row=rr, column=1).value)
print("  Tab 5 gap data rows (col A non-empty from row 3):", gap_rows, "(expect 866)")
ws9 = wb["9 Competitor Link Detail"]
link_rows = sum(1 for rr in range(3, ws9.max_row+1) if ws9.cell(row=rr, column=1).value)
print("  Tab 9 link data rows (col A non-empty from row 3):", link_rows, "(expect ~1453)")
ws1 = wb["1 Executive Scorecard"]
print("  Tab 1 charts:", len(ws1._charts), "(expect 2)")

print("\n=== 7. MANDATED BACKLINK-AGE WORDING PRESENT ===")
found = []
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and "were acquired in the last 8 months" in c.value:
                found.append((ws.title, c.coordinate))
print("  cells with mandated sentence:", found)

print("\n=== SUMMARY ===")
checks = {
  "freeze all low": fp_ok,
  "no provenance cells": len(prov_hits)==0,
  "em/en dashes == 0": emen==0,
  "prose hyphens == 0": prose==0,
  "tab2 traffic early": (ti is not None and ai<ti and ri<ti and ti<=6),
  "no '8 month old' defect": len(bad8)==0,
  "no arrows": len(arrows)==0,
  "no NFG-as-Target": len(targ)==0,
  "12 tabs": len(wb.worksheets)==12,
  "tab5==866": gap_rows==866,
  "tab9~1453": abs(link_rows-1453)<=3,
  "tab1 2 charts": len(ws1._charts)==2,
  "mandated wording present": len(found)>=1,
}
for k,v in checks.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
print("ALL PASS:", all(checks.values()))
