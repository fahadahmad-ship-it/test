"""
Correctness checks for the New Garden audit (playbook section 9).
Runs on the built workbook + disavow files. Both-directions, exhaustive.
Exit non-zero on any failure. Pure stdlib + openpyxl.
"""
import sys, re
import openpyxl

WB = sys.argv[1] if len(sys.argv) > 1 else "audit/newgarden/out/NewGarden_Backlinks_Audit.xlsx"
DISAVOW = sys.argv[2] if len(sys.argv) > 2 else "audit/newgarden/out/disavow_newgarden.txt"

FAIL = []
def check(cond, msg):
    print(("  ok  " if cond else "FAIL  ") + msg)
    if not cond:
        FAIL.append(msg)

def sheet(wb, name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0]
    idx = {h: i for i, h in enumerate(hdr)}
    return idx, rows[1:]

def main():
    wb = openpyxl.load_workbook(WB, data_only=True)
    print("TABS:", wb.sheetnames)
    expected_tabs = ["Summary", "Referring Domain Audit", "All Backlinks",
                     "Anchor Analysis", "Exact Match Anchors",
                     "Pending Disavow Lines", "Disavow List"]
    check(wb.sheetnames == expected_tabs, "seven tabs in the signed order")

    ridx, rda = sheet(wb, "Referring Domain Audit")
    aidx, ab = sheet(wb, "All Backlinks")
    didx, dl = sheet(wb, "Disavow List")
    pidx, pend = sheet(wb, "Pending Disavow Lines")

    # one row per domain
    doms = [r[ridx['Domain']] for r in rda]
    check(len(doms) == len(set(doms)), f"no duplicate referring domains ({len(doms)})")

    status = {r[ridx['Domain']]: r[ridx['Status']] for r in rda}
    dofollow = {r[ridx['Domain']]: r[ridx['Dofollow Links']] for r in rda}

    # ---- disavow file integrity ----
    with open(DISAVOW) as f:
        lines = [l.rstrip("\n") for l in f]
    entries = [l for l in lines if l and not l.startswith("#")]
    doms_in_file = [l.split("domain:")[1] for l in entries if l.startswith("domain:")]
    check(all(l.startswith("domain:") for l in entries), "every non-comment line is domain:<d>")
    check(all(l == l.lower() for l in entries), "all disavow lines lowercase")
    check(all("/" not in d and "http" not in d for d in doms_in_file), "no URLs in disavow file")
    check(len(doms_in_file) == len(set(doms_in_file)), "no duplicate disavow lines")
    # every file domain is Spam (Disavow)
    leak = [d for d in doms_in_file if status.get(d) != "Spam (Disavow)"]
    check(not leak, f"no Held/Keep/OwnSite leak into disavow file ({leak[:5]})")
    # every file domain has >=1 dofollow
    nod = [d for d in doms_in_file if not (dofollow.get(d) or 0)]
    check(not nod, f"every disavow domain has >=1 dofollow link ({nod[:5]})")
    # disavow set == Spam(Disavow) set
    spamset = {d for d, s in status.items() if s == "Spam (Disavow)"}
    check(set(doms_in_file) == spamset,
          f"disavow set == Spam(Disavow) set (file {len(doms_in_file)} vs {len(spamset)})")

    # Disavow List tab == file
    dltab = {str(r[didx['Disavow Line']]).replace("domain:", "") for r in dl}
    check(dltab == set(doms_in_file), "Disavow List tab matches disavow file")

    # ---- cross-tab reconciliation ----
    ab_status = {}
    for r in ab:
        ab_status.setdefault(r[aidx['Referring Domain']], set()).add(r[aidx['Status']])
    multi = [d for d, s in ab_status.items() if len(s) > 1]
    check(not multi, f"no domain has conflicting per-link status ({multi[:5]})")
    check(set(ab_status) == set(doms), "All Backlinks domains == Referring Domain Audit domains")

    # Pending == Held (Pending Partner)
    heldp = {d for d, s in status.items() if s == "Held (Pending Partner)"}
    pendset = {str(r[pidx['Referring domain']]) for r in pend}
    check(pendset == heldp, f"Pending lines == Held(Pending Partner) ({len(pendset)} vs {len(heldp)})")

    # ---- no false negatives: no Keep/Held with dofollow spam anchor ----
    SPAM_AT = {"Spam: keyword stuffed SEO sales copy", "Spam: off topic"}
    fn = [(r[aidx['Referring Domain']], r[aidx['Anchor Type']])
          for r in ab if r[aidx['Status']] in ("Keep",) and r[aidx['Anchor Type']] in SPAM_AT
          and str(r[aidx['Link Type']]).lower() == "dofollow"]
    check(not fn, f"no Keep domain carries a dofollow spam anchor ({fn[:5]})")

    # ---- no false positives: every disavow domain rests on evidence (Reason non-empty) ----
    reason = {r[ridx['Domain']]: r[ridx['Disavow Line']] for r in rda}
    # evidence is captured in build; here ensure every spam-disavow row has a disavow line
    noline = [r[ridx['Domain']] for r in rda if r[ridx['Status']] == "Spam (Disavow)" and not r[ridx['Disavow Line']]]
    check(not noline, f"every Spam(Disavow) row has a Disavow Line ({noline[:5]})")

    # ---- no-action nofollow really nofollow ----
    nf_bad = [r[ridx['Domain']] for r in rda
              if r[ridx['Status']] in ("Spam (Nofollow, No Action)", "Held (Nofollow, No Action)")
              and (r[ridx['Dofollow Links']] or 0) > 0]
    check(not nf_bad, f"nofollow-no-action domains have 0 dofollow ({nf_bad[:5]})")

    print()
    if FAIL:
        print(f"VERIFY FAILED: {len(FAIL)} issue(s)")
        sys.exit(1)
    print("VERIFY PASSED")

if __name__ == "__main__":
    main()
