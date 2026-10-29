#!/usr/bin/env python3
"""
verify.py — correctness checks (both directions) + structural template compare.
Reads styling back from the saved .xlsx XML, not openpyxl in memory.

Run: python3 -I scripts/verify.py
"""
import json, os, re, sys, zipfile, csv
import xml.etree.ElementTree as ET
import openpyxl
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
TEMPLATE = os.path.join(BASE, "ref", "KK_template.xlsx")
WB = os.path.join(OUT, "Jaco_Contracting_Backlinks_Audit.xlsx")
DISAVOW = os.path.join(OUT, "disavow_jacocontracting.txt")
CLIENT = "jacocontracting.com"

fails = []
warns = []
def check(cond, msg):
    if not cond:
        fails.append(msg)
def warn(cond, msg):
    if not cond:
        warns.append(msg)

def main():
    domains = json.load(open(os.path.join(DATA, "domains_classified.json")))
    links = [json.loads(l) for l in open(os.path.join(DATA, "links_classified.jsonl"))]
    by_dom = defaultdict(list)
    for L in links:
        by_dom[L["refdomain"]].append(L)

    # ---- disavow file integrity ----
    dlines = [l.strip() for l in open(DISAVOW) if l.strip() and not l.startswith("#")]
    file_doms = []
    for l in dlines:
        check(re.fullmatch(r"domain:[a-z0-9.\-]+", l) is not None, f"bad disavow line: {l!r}")
        check("/" not in l and "http" not in l, f"disavow line has URL: {l!r}")
        file_doms.append(l[len("domain:"):])
    check(len(file_doms) == len(set(file_doms)), "duplicate domains in disavow file")
    file_set = set(file_doms)

    # every file domain is Spam (Disavow) with >=1 dofollow
    for d in file_set:
        v = domains.get(d)
        check(v is not None, f"disavow domain not in dataset: {d}")
        if v:
            check(v["status"] == "Spam (Disavow)", f"disavow domain not Spam(Disavow): {d} = {v['status']}")
            check(v["dofollow"] >= 1, f"disavow domain has no dofollow link: {d}")

    # disavow set == Spam(Disavow) set
    spam_disavow = {d for d, v in domains.items() if v["status"] == "Spam (Disavow)"}
    check(file_set == spam_disavow, f"disavow file != Spam(Disavow) set (file {len(file_set)} vs {len(spam_disavow)}; "
          f"missing {len(spam_disavow-file_set)}, extra {len(file_set-spam_disavow)})")

    # no Held/Keep/Own Site leaks
    for d in file_set:
        st = domains[d]["status"]
        check(not (st.startswith("Held") or st in ("Keep", "Own Site")), f"non-spam leaked into file: {d} {st}")

    # ---- no false positives: every disavow domain rests on visible evidence ----
    for d, v in domains.items():
        if v["status"] == "Spam (Disavow)":
            ls = by_dom.get(d, [])
            ev = (any(L["anchor_type"] in ("Spam: keyword stuffed SEO sales copy", "Spam: off topic") for L in ls)
                  or any(k in d for k in ["backlink","seo","pbn","dapa","rank","directory","listing","bookmark","buy","index","dofollow","guestpost","marketplace","aged"])
                  or bool(v.get("reason")))
            check(ev, f"disavow domain with no visible evidence: {d}")

    # ---- no false negatives: Keep/Held must not carry a dofollow off-topic anchor ----
    for d, v in domains.items():
        ls = by_dom.get(d, [])
        if v["status"] in ("Keep", "Own Site") or v["status"].startswith("Held"):
            dof_offtopic = any(L["anchor_type"] == "Spam: off topic" and not L["nofollow"] for L in ls)
            check(not dof_offtopic, f"{v['status']} domain carries a dofollow off-topic anchor: {d}")
        if v["status"] in ("Keep", "Own Site"):
            dof_sales = any(L["anchor_type"] == "Spam: keyword stuffed SEO sales copy" and not L["nofollow"] for L in ls)
            check(not dof_sales, f"Keep domain carries a dofollow sales-copy anchor: {d}")

    # nofollow-marked spam actually all nofollow
    for d, v in domains.items():
        if v["status"] in ("Spam (Nofollow, No Action)", "Held (Nofollow, No Action)"):
            check(v["dofollow"] == 0, f"{v['status']} domain {d} actually has {v['dofollow']} dofollow links")

    # ---- workbook structure vs template (XML) ----
    wb = openpyxl.load_workbook(WB)
    tb = openpyxl.load_workbook(TEMPLATE)
    check(wb.sheetnames == tb.sheetnames, f"sheet names/order differ: {wb.sheetnames} vs {tb.sheetnames}")
    for name in tb.sheetnames:
        ws, ts = wb[name], tb[name]
        # header row values
        tcols = ts.max_column
        for c in range(1, tcols + 1):
            tv = ts.cell(row=1, column=c).value
            wv = ws.cell(row=1, column=c).value
            if name != "Summary":
                check(tv == wv, f"[{name}] header col {c} differs: {wv!r} vs template {tv!r}")
        # freeze / gridlines / autofilter presence
        if name != "Summary":
            check(ws.freeze_panes == "B2", f"[{name}] freeze panes {ws.freeze_panes} != B2")
            check(ws.sheet_view.showGridLines == ts.sheet_view.showGridLines,
                  f"[{name}] gridlines differ")
            check(bool(ws.auto_filter.ref), f"[{name}] missing autofilter")

    # ---- row counts reconcile ----
    rda = wb["Referring Domain Audit"]
    check(rda.max_row - 1 == len(domains), f"Referring Domain Audit rows {rda.max_row-1} != domains {len(domains)}")
    allb = wb["All Backlinks"]
    check(allb.max_row - 1 == len(links), f"All Backlinks rows {allb.max_row-1} != links {len(links)}")
    dl = wb["Disavow List"]
    check(dl.max_row - 1 == len(spam_disavow), f"Disavow List rows {dl.max_row-1} != spam {len(spam_disavow)}")
    pend = wb["Pending Disavow Lines"]
    held = {d for d, v in domains.items() if v["status"].startswith("Held")}
    check(pend.max_row - 1 == len(held), f"Pending rows {pend.max_row-1} != held {len(held)}")

    # ---- Summary numbers re-derive ----
    ws = wb["Summary"]
    sc = Counter(v["status"] for v in domains.values())
    row_for = {ws.cell(row=r, column=1).value: r for r in range(4, 11)}
    for s, cnt in sc.items():
        r = row_for.get(s)
        if r:
            check(ws.cell(row=r, column=2).value == cnt, f"Summary {s} domains {ws.cell(row=r,column=2).value} != {cnt}")
    check(ws.cell(row=10, column=2).value == len(domains), "Summary total domains mismatch")

    # ---- example backlinks exist; no blank first seen where links exist ----
    blank_fs = 0
    for d, v in domains.items():
        ls = by_dom.get(d, [])
        if ls:
            check(bool(v.get("example_url")), f"domain {d} has links but no example url")
            if not v.get("first_seen"):
                blank_fs += 1
    warn(blank_fs == 0, f"{blank_fs} domains have links but blank First Seen")

    # logo present
    z = zipfile.ZipFile(WB)
    check("xl/media/image1.png" in z.namelist(), "logo image missing from workbook")

    # ---- report ----
    print(f"domains={len(domains)} links={len(links)} disavow={len(spam_disavow)} held={len(held)}")
    print(f"status: {dict(sc)}")
    if warns:
        print("\nWARNINGS:")
        for w in warns:
            print("  ! " + w)
    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for f in fails[:60]:
            print("  ✗ " + f)
        sys.exit(1)
    print("\nALL CHECKS PASSED ✓")

if __name__ == "__main__":
    main()
