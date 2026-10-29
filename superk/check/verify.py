"""
verify.py — correctness suite for the superkexpress.com audit. Checks the disavow file
and workbook both directions, exhaustively (not a sample), per the playbook. Exit 0 only
if every check passes. Run: python3 -I superk/check/verify.py
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import load, classify, build
import openpyxl

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "out"))
WB = os.path.join(OUT, "SuperKExpress_Backlinks_Audit.xlsx")
DISAVOW = os.path.join(OUT, "disavow_superkexpress.com.txt")

FAIL = []
WARN = []
def check(cond, msg):
    if not cond: FAIL.append(msg)
def warn(cond, msg):
    if not cond: WARN.append(msg)

def visible_evidence(rec):
    """Does this domain have a VISIBLE spam signal (anchor, title, host, or URL)?"""
    dom = rec["domain"]; links = rec["links"]
    types = [classify.anchor_type(l.get("anchor",""), l.get("source_title","")) for l in links]
    if any(t in classify.SPAM_ANCHOR_TYPES for t in types):
        return True
    titles = [l.get("source_title","") for l in links]
    if any(classify._has(t, classify.PBN_TERMS) or classify._has(t, classify.GAMBLING_TERMS)
           or classify._has(t, classify.PHARMA_ADULT_TERMS) for t in titles):
        return True
    if classify._has(dom, classify.SPAM_HOST_SIGNATURES):
        return True
    from urllib.parse import urlsplit
    for l in links:
        p = classify._path(l.get("source_url",""))
        if re.search(r"/(domain|backlink|link-?placement|indexation|seo|pbn|dir/)", p.lower()):
            return True
    return False

def names_client_no_salescopy(rec):
    titles = [l.get("source_title","") for l in rec["links"]]
    names = any(("superkexpress" in (t or "").lower() or "super k express" in (t or "").lower()) for t in titles)
    sales = any(classify._has(t, classify.PBN_TERMS) or classify._has(t, classify.GAMBLING_TERMS) for t in titles)
    return names and not sales

def main():
    data = build.gather()
    recs = {r["domain"]: r for r in data["recs"]}
    doms = data["domains"]; cls = data["classification"]

    disavow = [r for r in data["recs"] if r["status"] == "Spam (Disavow)"]
    disavow_set = {r["domain"] for r in disavow}

    # ---------- A. disavow file integrity ----------
    with open(DISAVOW, encoding="utf-8") as fh:
        raw = fh.read().splitlines()
    file_domains = []
    for ln in raw:
        if ln.strip() == "" or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^domain:([a-z0-9.\-]+)$", ln)
        check(m is not None, f"disavow line not 'domain:<domain>' lowercase: {ln!r}")
        if m:
            file_domains.append(m.group(1))
    check(len(file_domains) == len(set(file_domains)), "duplicate domains in disavow file")
    # file set == spam(disavow) set (idna-encoded)
    disavow_idna = {build.idna(d) for d in disavow_set}
    check(set(file_domains) == disavow_idna,
          f"disavow file set != Spam(Disavow) set (file {len(set(file_domains))} vs {len(disavow_idna)})")
    # no held/keep/own/nofollow leak
    bad = [d for d in file_domains for dom in [d] if False]  # placeholder
    for d in file_domains:
        # map back: find a rec whose idna matches
        matches = [r for r in data["recs"] if build.idna(r["domain"]) == d]
        check(matches and matches[0]["status"] == "Spam (Disavow)",
              f"disavow file domain not Spam(Disavow): {d}")

    # ---------- B. every disavow domain: dofollow + visible evidence ----------
    for r in disavow:
        rec = doms[r["domain"]]
        check(rec.get("any_dofollow", False), f"disavow domain has no dofollow link: {r['domain']}")
        check(visible_evidence(rec), f"disavow domain rests on NO visible evidence: {r['domain']}")
        check(not names_client_no_salescopy(rec),
              f"disavow domain looks like a genuine citation (names client, no sales copy): {r['domain']}")
        if (r["traffic"] or 0) > 0:
            WARN.append(f"disavow domain has organic traffic {r['traffic']} (manual review): {r['domain']}")

    # ---------- C. no false negatives ----------
    for dom, rec in doms.items():
        st = cls[dom]["status"]
        types = [classify.anchor_type(l.get("anchor",""), l.get("source_title","")) for l in rec["links"]]
        has_dofollow_offtopic = any((t == "Spam: off topic") for t, l in zip(types, rec["links"]) if not l.get("nofollow"))
        if st in ("Keep",):
            check(not has_dofollow_offtopic, f"KEEP domain has a dofollow off-topic anchor (false negative?): {dom}")
        if st == "Spam (Nofollow, No Action)":
            check(not rec.get("any_dofollow", False),
                  f"nofollow-spam domain actually has a dofollow link: {dom}")

    # ---------- D. workbook reconciliation ----------
    wb = openpyxl.load_workbook(WB)
    rda = wb["Referring Domain Audit"]; dl = wb["Disavow List"]; pend = wb["Pending Disavow Lines"]
    allb = wb["All Backlinks"]; anch = wb["Anchor Analysis"]; em = wb["Exact Match Anchors"]
    check(rda.max_row - 1 == len(data["recs"]), f"RDA rows {rda.max_row-1} != domains {len(data['recs'])}")
    check(dl.max_row - 1 == len(disavow), f"Disavow List rows {dl.max_row-1} != disavow {len(disavow)}")
    held = [r for r in data["recs"] if r["status"].startswith("Held")]
    check(pend.max_row - 1 == len(held), f"Pending rows {pend.max_row-1} != held {len(held)}")
    # one disavow line per disavow domain in the tab
    dl_domains = [dl.cell(r,1).value for r in range(2, dl.max_row+1)]
    check(all(str(v).startswith("domain:") for v in dl_domains), "Disavow List col A not all 'domain:'")
    check(len(dl_domains) == len(set(dl_domains)), "duplicate lines in Disavow List tab")

    # ---------- D2. no blank cells where data exists ----------
    # First Seen (col 11) must be present for every domain that has any link with a date
    blanks = 0
    for i, r in enumerate(data["recs"], start=2):
        has_date = any(l.get("first_seen") for l in r["links"]) or doms[r["domain"]].get("first_seen")
        if has_date and rda.cell(i, 11).value in (None, ""):
            blanks += 1
    check(blanks == 0, f"{blanks} RDA rows have blank First Seen where a date exists")
    # Top Anchor / Example Page present for domains with links
    miss_anchor = sum(1 for i, r in enumerate(data["recs"], start=2)
                      if r["links"] and rda.cell(i,13).value in (None,""))
    check(miss_anchor == 0, f"{miss_anchor} RDA rows missing Example Linking Page though links exist")

    # ---------- E. Summary numbers re-derive ----------
    sm = wb["Summary"]
    # find the status table rows by scanning col A
    want = {r["status"] for r in data["recs"]}
    from collections import Counter
    cnt = Counter(r["status"] for r in data["recs"])
    found = {}
    for row in range(3, 12):
        a = sm.cell(row,1).value
        if a in cnt:
            found[a] = sm.cell(row,2).value
    for s, n in cnt.items():
        if s in found:
            check(found[s] == n, f"Summary domains for {s}: sheet {found[s]} != data {n}")

    # ---------- report ----------
    print(f"Spam(Disavow)={len(disavow)}  Held={len(held)}  domains={len(data['recs'])}  file_lines={len(file_domains)}")
    if WARN:
        print(f"\nWARNINGS ({len(WARN)}):")
        for w in WARN[:40]:
            print("  WARN:", w)
    if FAIL:
        print(f"\nFAILURES ({len(FAIL)}):")
        for f in FAIL[:60]:
            print("  FAIL:", f)
        sys.exit(1)
    print("\nALL VERIFY CHECKS PASSED")

if __name__ == "__main__":
    main()
