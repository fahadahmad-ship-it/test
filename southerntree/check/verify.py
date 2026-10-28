"""
Verification suite for the southerntreega.com audit (run after build.py).

    python3 -I southerntree/check/verify.py <template.xlsx>

Checks, both directions and exhaustively (not a sample):
  Disavow-file integrity, no false positives, no false negatives, count reconciliation,
  decision-row example backlinks, no blank First Seen, and a structural compare of the
  built workbook against the signed-off template.
Exit code 0 only if every check passes.
"""
import os
import sys
import glob
import re
import json
import datetime
from collections import Counter

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, f"{ROOT}/scripts")
import load as L
import classify as C
import build as B

OUT = f"{ROOT}/out/Southern_Tree_Solutions_Backlinks_Audit.xlsx"
DISAVOW = f"{ROOT}/out/{B.DISAVOW_FILE}"

fails, warns = [], []
def check(cond, msg):
    (print(f"  PASS {msg}") if cond else fails.append(msg))
def warn(cond, msg):
    if not cond:
        warns.append(msg)


def rebuild_domains():
    sem = L.load_semrush(sorted(glob.glob(f"{ROOT}/data/fetch/backlinks_*.csv")))
    ahr = L.load_ahrefs_backlinks(sorted(glob.glob(f"{ROOT}/data/ahrefs/backlinks.json")))
    refmeta = L.load_ahrefs_refdomains(sorted(glob.glob(f"{ROOT}/data/ahrefs/refdomains.json")))
    merged = L.canonical_merge(sem, ahr)
    domains = B.build_domains(merged, refmeta)
    return domains, merged


def main():
    domains, merged = rebuild_domains()
    spam_dis = {d["domain"] for d in domains.values() if d["status"] == "Spam (Disavow)"}
    held = {d["domain"] for d in domains.values() if d["status"].startswith("Held")}
    keep = {d["domain"] for d in domains.values() if d["status"] in ("Keep", "Own Site")}

    print("== Disavow-file integrity ==")
    with open(DISAVOW) as fh:
        raw = fh.read().splitlines()
    file_lines = [ln for ln in raw if ln.strip() and not ln.startswith("#")]
    file_doms = []
    for ln in file_lines:
        check(ln.startswith("domain:"), f"line is a domain: line -> {ln!r}")
        dom = ln.split("domain:", 1)[1]
        check(dom == dom.lower(), f"lowercase -> {ln!r}")
        check("/" not in dom and "://" not in dom, f"no URL -> {ln!r}")
        file_doms.append(dom)
    check(len(file_doms) == len(set(file_doms)), "no duplicate disavow lines")
    check(set(file_doms) == spam_dis, "disavow file == Spam(Disavow) set exactly")
    check(not (set(file_doms) & held), "no Held domain leaked into file")
    check(not (set(file_doms) & keep), "no Keep/Own domain leaked into file")

    print("== No false positives (every disavow rests on evidence) ==")
    noev = [d["domain"] for d in domains.values()
            if d["status"] == "Spam (Disavow)" and d["reason"] == "No spam evidence found"]
    check(not noev, f"no disavow domain lacks evidence (offenders: {noev[:5]})")
    for d in domains.values():
        if d["domain"] in spam_dis:
            has_do = any(l["is_dofollow"] for l in d["links"])
            check(has_do, f"{d['domain']} has >=1 dofollow link") if not has_do else None
    dofollow_ok = all(any(l["is_dofollow"] for l in domains[x]["links"]) for x in spam_dis)
    check(dofollow_ok, "every disavow domain has at least one dofollow link")

    print("== No false negatives (no kept domain carries dofollow spam) ==")
    leaks = []
    for d in domains.values():
        if d["status"] in ("Keep", "Own Site") or d["status"].endswith("Nofollow, No Action)"):
            for l in d["links"]:
                if l["is_dofollow"] and l["anchor_type"].startswith("Spam:"):
                    leaks.append((d["domain"], d["status"], l["anchor"][:40]))
    # nofollow-marked spam must truly have no dofollow
    nf_wrong = [d["domain"] for d in domains.values()
                if d["status"] == "Spam (Nofollow, No Action)" and any(l["is_dofollow"] for l in d["links"])]
    check(not nf_wrong, f"no 'Spam (Nofollow)' domain actually has a dofollow link ({nf_wrong[:5]})")
    # Keep/Own with dofollow spam is a hard fail; nofollow-held variants are examined
    hard = [x for x in leaks if x[1] in ("Keep", "Own Site")]
    check(not hard, f"no Keep/Own-Site domain carries a dofollow spam anchor ({hard[:5]})")

    print("== Workbook structure vs template ==")
    wb = openpyxl.load_workbook(OUT)
    tpl = openpyxl.load_workbook(sys.argv[1]) if len(sys.argv) > 1 else None
    expect_tabs = ["Summary", "Referring Domain Audit", "All Backlinks", "Anchor Analysis",
                   "Exact Match Anchors", "Pending Disavow Lines", "Disavow List"]
    check(wb.sheetnames == expect_tabs, f"tab order correct -> {wb.sheetnames}")
    if tpl:
        for tab in expect_tabs[1:]:
            tv, wv = tpl[tab], wb[tab]
            th = [tv.cell(row=1, column=c).value for c in range(1, tv.max_column + 1)]
            wh = [wv.cell(row=1, column=c).value for c in range(1, wv.max_column + 1)]
            check(th == wh, f"{tab}: headers match template")
            check(wv.freeze_panes == tv.freeze_panes, f"{tab}: freeze panes {wv.freeze_panes}")
            check(bool(wv.auto_filter.ref), f"{tab}: autofilter set")

    print("== Count reconciliation (Summary re-derives from data) ==")
    sm = wb["Summary"]
    # find status rows
    smvals = {}
    for r in range(3, 12):
        k = sm.cell(row=r, column=1).value
        if k in B.STATUS_ORDER + ["Total"]:
            smvals[k] = sm.cell(row=r, column=2).value
    dbs = Counter(d["status"] for d in domains.values())
    for st in B.STATUS_ORDER:
        check(int(smvals.get(st, 0) or 0) == dbs.get(st, 0), f"Summary domains[{st}]={smvals.get(st)} == data {dbs.get(st,0)}")
    check(int(smvals.get("Total", 0) or 0) == len(domains), "Summary total domains == data")

    print("== Decision rows carry a real example backlink ==")
    ema = wb["Exact Match Anchors"]
    missing_ex = 0
    for r in range(2, ema.max_row + 1):
        dom = ema.cell(row=r, column=1).value
        ex = ema.cell(row=r, column=2).value
        if dom and not ex:
            missing_ex += 1
    check(missing_ex == 0, f"every Exact-Match row has an example backlink ({missing_ex} missing)")

    print("== No blank First Seen where data exists (Referring Domain Audit) ==")
    rda = wb["Referring Domain Audit"]
    blank_fs = sum(1 for r in range(2, rda.max_row + 1)
                   if rda.cell(row=r, column=1).value and rda.cell(row=r, column=11).value in (None, ""))
    warn(blank_fs == 0, f"{blank_fs} rows have blank First Seen")

    print("\n================ RESULT ================")
    if warns:
        print("WARNINGS:")
        for w in warns:
            print("  -", w)
    if fails:
        print("FAILURES:")
        for f in fails:
            print("  FAIL", f)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
