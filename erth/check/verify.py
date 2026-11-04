"""Correctness verification for the erthproducts.com audit — both directions,
exhaustive (not a sample). Mirrors the playbook Section 9 checklist."""
import re
import sys
import collections
import openpyxl

sys.path.insert(0, "erth/scripts")
import pipeline as P
import classify as C
import records as R
from load import host_of

FAILS = []
WARN = []


def fail(m):
    FAILS.append(m)


def warn(m):
    WARN.append(m)


def main():
    canon, links, by = P.run()
    recs, by2, covered = R.assemble()
    disavow_file = "erth/out/" + R.DISAVOW_FILE

    # ---------- disavow file integrity ----------
    lines = open(disavow_file).read().splitlines()
    dom_lines = [l for l in lines if l and not l.startswith("#")]
    file_domains = []
    for l in dom_lines:
        if not re.fullmatch(r"domain:[a-z0-9.\-]+", l):
            fail(f"disavow line not canonical: {l!r}")
        else:
            file_domains.append(l.split(":", 1)[1])
    if len(file_domains) != len(set(file_domains)):
        dup = [d for d, n in collections.Counter(file_domains).items() if n > 1]
        fail(f"duplicate disavow lines: {dup[:10]}")
    file_set = set(file_domains)

    # every file domain is Spam (Disavow); has >=1 dofollow; no held/keep/own leaks
    for d in file_domains:
        node = by.get(d)
        if not node:
            fail(f"disavow domain not in dataset: {d}")
            continue
        if node["status"] != "Spam (Disavow)":
            fail(f"disavow domain status != Spam(Disavow): {d} = {node['status']}")
        if not node["any_dofollow"]:
            fail(f"disavow domain has NO dofollow link: {d}")
    # reverse: every Spam(Disavow) not-covered is in the file
    for dom, d in by.items():
        if d["status"] == "Spam (Disavow)" and dom not in covered and dom not in file_set:
            fail(f"Spam(Disavow) missing from file: {dom}")
    # redundant children not emitted; parent present
    for child, parent in covered.items():
        if child in file_set:
            fail(f"redundant child emitted: {child} (parent {parent})")
        if parent not in file_set:
            fail(f"parent of covered child missing from file: {parent}")

    # ---------- no false positives ----------
    for dom, d in by.items():
        if d["status"] != "Spam (Disavow)":
            continue
        # must rest on visible evidence
        ev_ok = False
        for r in d["links"]:
            a, t, u = r["anchor"], r.get("title", ""), r.get("url_from", "")
            if C.is_pbn(a, t, u) or C.is_off_topic(a, t, host_of(u)):
                ev_ok = True
        if any(C.spam_host(h) for h in d["hosts"]):
            ev_ok = True
        if not ev_ok:
            fail(f"disavow domain rests on NO visible evidence: {dom}")
        # clean client citation must not be disavowed
        for r in d["links"]:
            tl = (r.get("title") or "").lower()
            if "erth" in tl and not C.is_pbn(r["anchor"], r.get("title", ""), r.get("url_from", "")) \
                    and not any(x in tl for x in C.SPAM_TITLE_TOKENS):
                fail(f"disavow domain has clean client-naming title: {dom} ({tl[:40]})")
                break

    # ---------- no false negatives ----------
    for dom, d in by.items():
        if d["status"] in ("Keep", "Held (Pending Partner)", "Held (Nofollow, No Action)", "Own Site"):
            for r in d["links"]:
                if not r["nofollow"] and (C.is_pbn(r["anchor"], r.get("title", ""), r.get("url_from", ""))
                                          or C.is_off_topic(r["anchor"], r.get("title", ""), host_of(r.get("url_from", "")))):
                    fail(f"{d['status']} domain carries a dofollow spam link: {dom}")
                    break
    # nofollow-marked spam must truly have no dofollow
    for dom, d in by.items():
        if d["status"] in ("Spam (Nofollow, No Action)", "Held (Nofollow, No Action)") and d["any_dofollow"]:
            fail(f"nofollow-marked status but has a dofollow link: {dom} = {d['status']}")

    # ---------- workbook counts reconcile ----------
    wb = openpyxl.load_workbook("erth/out/Erth_Products_Backlinks_Audit.xlsx")
    rda_n = wb["Referring Domain Audit"].max_row - 1
    abl_n = wb["All Backlinks"].max_row - 1
    dis_n = wb["Disavow List"].max_row - 1
    if rda_n != len(by):
        fail(f"RDA rows {rda_n} != domain count {len(by)}")
    if abl_n != len(links):
        fail(f"All Backlinks rows {abl_n} != link count {len(links)}")
    n_disavow = sum(1 for dom, d in by.items() if d["status"] == "Spam (Disavow)" and dom not in covered)
    if dis_n != n_disavow:
        fail(f"Disavow List rows {dis_n} != disavow count {n_disavow}")
    if dis_n != len(file_set):
        fail(f"Disavow List rows {dis_n} != file lines {len(file_set)}")

    # ---------- summary numbers re-derive ----------
    ws = wb["Summary"]
    tmpl_total = ws.cell(10, 2).value
    if tmpl_total != len(by):
        fail(f"Summary total domains {tmpl_total} != {len(by)}")

    # ---------- every decision-tab row has a real example backlink ----------
    ws = wb["Exact Match Anchors"]
    dom_links = collections.defaultdict(set)
    for dom, d in by.items():
        for r in d["links"]:
            dom_links[dom].add(r["url_from"])
    for row in range(2, ws.max_row + 1):
        dom = ws.cell(row, 1).value
        ex = ws.cell(row, 2).value
        if dom and ex and ex not in dom_links.get(dom, set()):
            fail(f"Exact Match row {row}: example {ex} not a real link of {dom}")

    # ---------- no blank First Seen where data exists ----------
    ws = wb["Referring Domain Audit"]
    blank_fs = 0
    for row in range(2, ws.max_row + 1):
        if ws.cell(row, 11).value in (None, ""):
            blank_fs += 1
    if blank_fs:
        warn(f"{blank_fs} rows with blank First Seen")

    print("=== VERIFY ===")
    print("domains:", len(by), "links:", len(links), "disavow lines:", len(file_set))
    print("FAILURES:", len(FAILS))
    for f in FAILS[:60]:
        print("  FAIL:", f)
    print("WARNINGS:", len(WARN))
    for w in WARN[:20]:
        print("  warn:", w)
    print("RESULT:", "PASS" if not FAILS else "FAIL")


if __name__ == "__main__":
    main()
