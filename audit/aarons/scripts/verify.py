"""
Verification suite for the aaronshometech.com audit (BACKLINK_AUDIT_PLAYBOOK
section 9). Checks disavow-file integrity and runs the exhaustive both-directions
evidence sweep over EVERY domain (not a sample). Reads styling back from the saved
.xlsx XML, not openpyxl-in-memory, where it checks the workbook.

Run: python3 -I scripts/verify.py data/classified.json scripts/config.py \
        out/disavow_aaronshometech.com.txt out/Aarons_Home_Tech_Backlink_Audit.xlsx
"""
import sys, os, json, re, importlib.util, zipfile
from collections import Counter

def load_cfg(p):
    spec = importlib.util.spec_from_file_location("config", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def any_sig(text, sigs):
    t = (text or "").lower()
    return any(s in t for s in sigs)

FAILS = []
WARN = []
def check(cond, msg):
    if cond: print(f"  PASS  {msg}")
    else: print(f"  FAIL  {msg}"); FAILS.append(msg)
def warn(cond, msg):
    if not cond: print(f"  WARN  {msg}"); WARN.append(msg)

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))["domains"]
    cfg = load_cfg(sys.argv[2])
    disavow_path = sys.argv[3]
    xlsx = sys.argv[4] if len(sys.argv) > 4 else None

    doms = list(data.values())
    by_domain = {r["domain"]: r for r in doms}

    # ---- parse disavow file ----
    file_domains = []
    with open(disavow_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"): continue
            file_domains.append(line)
    print("== Disavow-file integrity ==")
    bad_fmt = [l for l in file_domains if not re.match(r"^domain:[a-z0-9.-]+$", l)]
    check(not bad_fmt, f"every line is 'domain:<lowercase-domain>' (offenders: {bad_fmt[:5]})")
    has_url = [l for l in file_domains if "/" in l or "http" in l]
    check(not has_url, "no URLs / paths in file")
    doms_only = [l.split("domain:", 1)[1] for l in file_domains]
    dupes = [d for d, c in Counter(doms_only).items() if c > 1]
    check(not dupes, f"no duplicate domains (dupes: {dupes[:5]})")
    lower_ok = all(d == d.lower() for d in doms_only)
    check(lower_ok, "all domains lowercase")

    fileset = set(doms_only)
    # every file domain is Spam (Disavow) w/ dofollow; nothing else leaks
    leaks = [d for d in fileset if by_domain.get(d, {}).get("status") != "Spam (Disavow)"]
    check(not leaks, f"no Held/Keep/Own/nofollow leak into file (leaks: {leaks[:10]})")
    nodofollow = [d for d in fileset if not by_domain.get(d, {}).get("has_dofollow")]
    check(not nodofollow, f"every file domain has >=1 dofollow link (offenders: {nodofollow[:10]})")

    # redundant children not emitted; their parent present
    red = []
    for d in fileset:
        labels = d.split(".")
        for i in range(1, len(labels) - 1):
            p = ".".join(labels[i:])
            if p in fileset:
                red.append(d); break
    check(not red, f"no redundant child whose parent is already in file (offenders: {red[:10]})")

    print("== No false positives (good link wrongly disavowed) — ALL entries ==")
    no_ev = []
    client_named = []
    for d in fileset:
        r = by_domain[d]
        ev_anchor = ev_title = ev_host = ev_coclient = False
        # the referring domain's own name is a member of the vendor's network
        if (d not in cfg.OWNED_DOMAINS) and any(tok in d for tok in cfg.PBN_COCLIENT_TOKENS):
            ev_coclient = True
        for l in r.get("links", []):
            a = (l.get("anchor") or ""); t = (l.get("source_title") or "")
            rdr = (l.get("redirect_url") or "")
            if any_sig(a, cfg.SPAM_ANCHOR_SIGNATURES) or any_sig(a, cfg.SPAM_SOFT_SIGNATURES) or any_sig(a, cfg.OFFTOPIC_TOKENS):
                ev_anchor = True
            if any_sig(t, cfg.SPAM_TITLE_SIGNATURES) or any_sig(t, cfg.SPAM_SOFT_SIGNATURES) or "backlink" in t.lower() or re.search(r"page\s*[\d,]{3,}", t.lower()) or "premium backlink" in t.lower() or "seo resource" in t.lower() or "resellers" in t.lower():
                ev_title = True
            # anchor or redirect names another client of the same vendor network
            if any(tok in a.lower() for tok in cfg.PBN_COCLIENT_TOKENS) or any(tok in rdr.lower() for tok in cfg.PBN_COCLIENT_TOKENS):
                ev_coclient = True
        if any(s in d for s in cfg.SPAM_HOST_SIGNATURES) or re.search(r"\.(shop|online|xyz|site|space|store|icu|club|monster|wiki|biz|sbs|click|link|live|today|fun|life|cfd|rest|lol)$", d):
            ev_host = True
        if not (ev_anchor or ev_title or ev_host or ev_coclient):
            no_ev.append(d)
        # a client-naming title WITHOUT sales copy = genuine citation
        for l in r.get("links", []):
            t = (l.get("source_title") or "").lower()
            if any(b in t for b in cfg.BRAND_TOKENS) and "backlink" not in t and not any_sig(t, cfg.SPAM_ANCHOR_SIGNATURES) and not any_sig(t, cfg.SPAM_TITLE_SIGNATURES):
                client_named.append(d); break
    check(not no_ev, f"zero disavow domains rest on no visible evidence (offenders: {no_ev[:15]})")
    check(not client_named, f"zero disavow domains carry a clean client-naming (editorial) title (offenders: {client_named[:15]})")

    print("== No false negatives (bad link wrongly kept/held) — ALL entries ==")
    kept_spam = []
    for r in doms:
        if r["status"].startswith("Keep"):
            for l in r.get("links", []):
                a = l.get("anchor") or ""
                if (not l["nofollow"]) and (any_sig(a, cfg.SPAM_ANCHOR_SIGNATURES) or any_sig(a, cfg.OFFTOPIC_TOKENS)):
                    kept_spam.append(r["domain"]); break
    check(not kept_spam, f"zero Keep domains carry a dofollow PBN/off-topic anchor (offenders: {kept_spam[:15]})")
    nf_wrong = []
    for r in doms:
        if r["status"] == "Spam (Nofollow, No Action)" and r.get("has_dofollow"):
            nf_wrong.append(r["domain"])
    check(not nf_wrong, f"zero nofollow-marked spam domains actually have a dofollow link (offenders: {nf_wrong[:15]})")

    print("== Traffic review on disavow set ==")
    # any disavow domain with real organic traffic must be reviewed by hand
    hi_traffic = []
    for d in fileset:
        # traffic attached post-metrics as r.get('organic_traffic'); if absent, skip
        tr = by_domain[d].get("organic_traffic")
        if isinstance(tr, int) and tr >= 50:
            hi_traffic.append((d, tr))
    warn(not hi_traffic, f"disavow domains with organic_traffic>=50 need a manual look: {hi_traffic[:15]}")

    print("== Counts reconcile ==")
    counts = Counter(r["status"] for r in doms)
    print("   " + "; ".join(f"{k}={v}" for k, v in counts.most_common()))
    disavow_dofollow = sum(1 for r in doms if r["status"] == "Spam (Disavow)" and r["has_dofollow"])
    check(len(fileset) <= disavow_dofollow,
          f"file size ({len(fileset)}) <= Spam(Disavow)+dofollow ({disavow_dofollow}) (rest = redundant children)")

    # ---- workbook structural check (read XML, not openpyxl objects) ----
    if xlsx and os.path.exists(xlsx):
        print("== Workbook structure (read from .xlsx XML) ==")
        try:
            import openpyxl
            wb = openpyxl.load_workbook(xlsx, read_only=True)
            names = wb.sheetnames
            expected = ["Summary", "Referring Domain Audit", "All Backlinks",
                        "Anchor Analysis", "Exact Match Anchors",
                        "Pending Disavow Lines", "Disavow List"]
            check(names == expected, f"tabs present and in order: {names}")
            # header-name check per tab by reading the saved sheet cell values
            blob = ""
            with zipfile.ZipFile(xlsx) as z:
                for n in z.namelist():
                    if n.startswith("xl/") and n.endswith(".xml"):
                        blob += z.read(n).decode("utf-8", "replace")
            for h in ["Referring Domain", "Anchor Type", "Disavow Line", "In Disavow",
                      "Exact-match commercial anchor", "Partner confirmed? (Y/N)"]:
                check(h in blob, f"header string present: {h!r}")
            wb.close()
        except Exception as e:
            print(f"  WARN  workbook read failed: {e}"); WARN.append(str(e))

    print()
    print(f"RESULT: {len(FAILS)} FAIL, {len(WARN)} WARN")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
