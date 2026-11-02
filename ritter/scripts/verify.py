"""Correctness suite — both directions, exhaustive (not a sample).
Re-derives classification from the data and cross-checks the generated workbook
and disavow file. Exit non-zero on any failure. (Playbook Section 9.)
"""
import glob
import sys
import collections
import openpyxl

sys.path.insert(0, "/home/user/test/ritter/scripts")
import config as C
from load import read_semrush_csv, host_of, path_of, canon_domain
import classify
from build import load_metrics, num

OUT_XLSX = "/home/user/test/ritter/out/Ritter_Backlinks_Audit.xlsx"
DISAVOW = "/home/user/test/ritter/out/disavow_ritterconsultingengineers.txt"

fails = []
warns = []


def fail(m):
    fails.append(m)


def warn(m):
    warns.append(m)


def main():
    bl, blrej, _ = read_semrush_csv(sorted(glob.glob("/home/user/test/ritter/data/fetch/backlinks_p*.csv")), 10)
    rd, rdrej, _ = read_semrush_csv(sorted(glob.glob("/home/user/test/ritter/data/rd/refdomains_p*.csv")), 9)
    if blrej:
        fail(f"{len(blrej)} malformed backlink rows")
    if rdrej:
        fail(f"{len(rdrej)} malformed refdomain rows")
    comp, rank = load_metrics()
    records, ip24 = classify.build_domain_records(bl, rd, comp, rank)
    rows = {}
    for dcan in records:
        rec = records[dcan]
        st, why, at = classify.classify_domain(rec, ip24)
        rec["status"] = st
        rows[dcan] = rec

    spam_set = set(d for d, r in rows.items() if r["status"] == "Spam (Disavow)")

    def redundant(d):
        return any(p != d and d.endswith("." + p) for p in spam_set)

    emitted = set(d for d in spam_set if not redundant(d))

    # ---------- disavow file integrity ----------
    with open(DISAVOW) as fh:
        lines = fh.read().split("\n")
    file_domains = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if not ln.startswith("domain:"):
            fail(f"disavow: non-domain line {ln!r}")
            continue
        dom = ln[len("domain:"):]
        if dom != dom.lower():
            fail(f"disavow: not lowercase {dom!r}")
        if "/" in dom or ":" in dom or " " in dom:
            fail(f"disavow: looks like a URL/invalid {dom!r}")
        file_domains.append(dom)
    if len(file_domains) != len(set(file_domains)):
        dup = [x for x, n in collections.Counter(file_domains).items() if n > 1]
        fail(f"disavow: {len(dup)} duplicate lines e.g. {dup[:5]}")
    fdset = set(file_domains)

    # every file domain: Spam(Disavow), has >=1 dofollow, not redundant, has evidence
    for dom in fdset:
        rec = rows.get(canon_domain(dom))
        if rec is None:
            fail(f"disavow domain not in dataset: {dom}")
            continue
        if rec["status"] != "Spam (Disavow)":
            fail(f"disavow domain is {rec['status']!r}, not Spam (Disavow): {dom}")
        dof = sum(1 for l in rec["links"] if l.get("nofollow", "").lower() != "true")
        if dof < 1:
            fail(f"disavow domain has no dofollow link: {dom}")
        if redundant(dom):
            fail(f"redundant child emitted: {dom}")
        # visible evidence
        titles = [l.get("source_title", "") for l in rec["links"]]
        anchors = [l.get("anchor", "") for l in rec["links"]]
        atset = set(classify.anchor_type(a, t) for a, t in zip(anchors, titles))
        ev = (classify.ANCHOR_SPAM_SALESCOPY in atset or classify.ANCHOR_SPAM_OFFTOPIC in atset
              or classify.host_is_spam(dom) or any(classify.title_is_spam(t) for t in titles)
              or any(dom == h or dom.endswith("." + h) for h in C.FREE_BLOG_PBN_HOSTS))
        if not ev:
            fail(f"disavow domain rests on NO visible evidence: {dom}")
        # genuine-citation guard
        if any(classify.title_names_client(t) and not classify.title_is_spam(t) for t in titles):
            # allowed only if also carries spam anchor; else false positive
            if not (classify.ANCHOR_SPAM_SALESCOPY in atset or classify.ANCHOR_SPAM_OFFTOPIC in atset):
                warn(f"disavow domain has a client-naming title (review): {dom}")

    # file equals emitted set (money-site single file = full union)
    if fdset != set(canon_domain(d) for d in emitted):
        miss = set(canon_domain(d) for d in emitted) - fdset
        extra = fdset - set(canon_domain(d) for d in emitted)
        if miss:
            fail(f"disavow missing {len(miss)} emitted spam domains e.g. {list(miss)[:5]}")
        if extra:
            fail(f"disavow has {len(extra)} domains not in emitted set e.g. {list(extra)[:5]}")

    # ---------- no false negatives ----------
    for d, rec in rows.items():
        if rec["status"] in ("Keep", "Held (Pending Partner)", "Held (Nofollow, No Action)"):
            for l in rec["links"]:
                nf = l.get("nofollow", "").lower() == "true"
                at = classify.anchor_type(l.get("anchor", ""), l.get("source_title", ""))
                if (not nf) and at in (classify.ANCHOR_SPAM_SALESCOPY, classify.ANCHOR_SPAM_OFFTOPIC):
                    fail(f"dofollow spam anchor kept out ({rec['status']}): {d}")
                    break
        if rec["status"] == "Spam (Nofollow, No Action)":
            if any(l.get("nofollow", "").lower() != "true" for l in rec["links"]):
                fail(f"nofollow-spam domain actually has a dofollow link: {d}")

    # ---------- workbook cross-check ----------
    wb = openpyxl.load_workbook(OUT_XLSX)
    if wb.sheetnames != ["Summary", "Referring Domain Audit", "All Backlinks",
                         "Anchor Analysis", "Exact Match Anchors", "Pending Disavow Lines",
                         "Disavow List"]:
        fail(f"tab names/order wrong: {wb.sheetnames}")
    rda = wb["Referring Domain Audit"]
    n_rda = rda.max_row - 1
    if n_rda != len(rows):
        fail(f"Referring Domain Audit rows {n_rda} != domains {len(rows)}")
    # one row per domain, unique
    seen = set()
    blank_fs = 0
    for r in range(2, rda.max_row + 1):
        dom = rda.cell(row=r, column=1).value
        if dom in seen:
            fail(f"RDA duplicate domain row: {dom}")
        seen.add(dom)
        if rda.cell(row=r, column=11).value in (None, ""):
            blank_fs += 1
    if blank_fs:
        fail(f"{blank_fs} blank First Seen cells in Referring Domain Audit")
    # All Backlinks rows == total links
    ab = wb["All Backlinks"]
    if ab.max_row - 1 != len(bl):
        warn(f"All Backlinks rows {ab.max_row-1} != backlinks {len(bl)}")
    # Disavow List rows == emitted
    dl = wb["Disavow List"]
    if dl.max_row - 1 != len(emitted):
        fail(f"Disavow List rows {dl.max_row-1} != emitted {len(emitted)}")
    # Pending Disavow Lines == Held (Pending Partner)
    pend = sum(1 for r in rows.values() if r["status"] == "Held (Pending Partner)")
    pdl = wb["Pending Disavow Lines"]
    if pdl.max_row - 1 != pend:
        fail(f"Pending Disavow Lines rows {pdl.max_row-1} != held-pending {pend}")
    # every Disavow List / Pending / Exact-Match row has an example or line that exists
    em = wb["Exact Match Anchors"]
    for r in range(2, em.max_row + 1):
        dom = em.cell(row=r, column=1).value
        ex = em.cell(row=r, column=2).value
        if not ex or not str(ex).startswith("http"):
            fail(f"Exact Match row without a real example backlink: {dom}")
            break

    # ---------- summary numbers re-derive ----------
    counts = collections.Counter(r["status"] for r in rows.values())
    sm = wb["Summary"]
    # read status table (rows 4-9): col A label, col B domains
    tbl = {}
    for r in range(4, 10):
        lab = sm.cell(row=r, column=1).value
        val = sm.cell(row=r, column=2).value
        if lab:
            tbl[lab] = val
    for s, n in counts.items():
        if s in tbl and int(tbl[s]) != n:
            fail(f"Summary count mismatch {s}: sheet={tbl[s]} data={n}")
    total_sheet = sm.cell(row=10, column=2).value
    if total_sheet is not None and int(total_sheet) != len(rows):
        fail(f"Summary total {total_sheet} != {len(rows)}")

    # ---------- report ----------
    print("STATUS COUNTS:", dict(counts))
    print(f"disavow lines: {len(file_domains)}  emitted(expected): {len(emitted)}  held-pending: {pend}")
    if warns:
        print(f"\nWARNINGS ({len(warns)}):")
        for w in warns[:40]:
            print("  !", w)
    if fails:
        print(f"\nFAILURES ({len(fails)}):")
        for f in fails[:80]:
            print("  X", f)
        sys.exit(1)
    print("\nVERIFY PASSED: all checks green, both directions.")


if __name__ == "__main__":
    main()
