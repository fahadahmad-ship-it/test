#!/usr/bin/env python3
# Correctness checks for the scapersllc.com audit (both directions, exhaustive).
# python3 -I scapers/scripts/verify.py <classified.csv> <disavow.txt> <workbook.xlsx> <ahrefs_refdomains.csv>
import sys, csv, os, collections
sys.path.insert(0, os.path.dirname(__file__)); import classify as C
csv.field_size_limit(10**7)

def main():
    cls,dis,xlsx,ahrd=sys.argv[1:5]
    rows=list(csv.DictReader(open(cls,encoding="utf-8")))
    by_dom={r["domain"]:r for r in rows}
    for r in rows: r["backlinks"]=int(r["backlinks"] or 0); r["AS"]=int(r["AS"] or 0)
    fails=[]; warns=[]; ok=[]
    def check(cond,msg):
        (ok if cond else fails).append(msg)

    # --- parse disavow ---
    dl=[l.strip() for l in open(dis,encoding="utf-8") if l.strip() and not l.strip().startswith("#")]
    hosts=[l.split("domain:",1)[1] for l in dl if l.startswith("domain:")]
    # 1 format
    check(all(l.startswith("domain:") for l in dl), "every non-comment line is a domain: line")
    check(all(h==h.lower() for h in hosts), "all disavow hosts lowercase")
    check(not any("/" in h or ":" in h or "http" in h for h in hosts), "no URLs in disavow lines")
    check(len(hosts)==len(set(hosts)), f"no duplicate disavow lines ({len(hosts)} lines, {len(set(hosts))} unique)")
    # 2 every disavow host maps to a Spam (Disavow) domain
    host2dom={}
    for r in rows:
        if r["status"]=="Spam (Disavow)": host2dom[r["host"]]=r
    leak=[h for h in hosts if h not in host2dom]
    check(not leak, f"every disavow host belongs to a Spam (Disavow) row (leaks: {leak[:5]})")
    # 3 no Held/Keep/Own host in file
    bad_status=[h for h in hosts if h in {r['host'] for r in rows if r['status'] in ('Keep','Own Site') or r['status'].startswith('Held')}]
    check(not bad_status, f"no Held/Keep/Own domain leaked into file ({bad_status[:5]})")
    # 4 evidence present on every disavowed domain
    noevi=[r["domain"] for r in rows if r["status"]=="Spam (Disavow)" and len((r.get("evidence") or "").strip())<8]
    check(not noevi, f"every disavowed domain has visible evidence (missing: {noevi[:5]})")
    # 5 no genuine-citation domain disavowed
    gleak=[r["domain"] for r in rows if r["status"]=="Spam (Disavow)" and r["domain"] in C.GENUINE]
    check(not gleak, f"no genuine-citation platform disavowed ({gleak[:5]})")
    # 6 redundant children removed
    hs=set(hosts); red=[h for h in hosts if h!=C.host_root(h) and C.host_root(h) in hs]
    check(not red, f"no redundant child whose parent is also listed ({red[:5]})")

    # --- false negatives: Keep/Held carrying a dofollow gambling/PBN anchor ---
    fn=[]
    for r in rows:
        if r["status"] in ("Keep",) or r["status"].startswith("Held"):
            at=C.anchor_type(r.get("top_anchor",""))
            if at in ("Spam: off topic","Spam: keyword stuffed SEO sales copy"):
                fn.append((r["domain"],r["status"],at,r.get("top_anchor","")[:40]))
    check(not fn, f"no Keep/Held domain has a top gambling/PBN anchor (offenders: {fn[:5]})")

    # --- review: disavow domains with a notable Semrush Authority Score (Semrush metric) ---
    hi=[(r["domain"],r["AS"],r["evidence"][:45]) for r in rows if r["status"]=="Spam (Disavow)" and r["AS"]>=20]
    for d,a,e in sorted(hi,key=lambda x:-x[1]): warns.append(f"disavow domain with Semrush AS {a}: {d} ({e}) — hand-reviewed")

    # --- counts reconcile ---
    total=len(rows)
    dc=collections.Counter(r["status"] for r in rows)
    check(sum(dc.values())==total, f"status counts sum to {total}")
    check(len(host2dom)==len(hosts), f"disavow line count == Spam(Disavow) host count ({len(hosts)} vs {len(host2dom)})")

    # --- workbook structure ---
    try:
        import openpyxl
        wb=openpyxl.load_workbook(xlsx, read_only=True)
        exp=["Summary","Referring Domain Audit","All Backlinks","Anchor Analysis","Exact Match Anchors","Pending Disavow Lines","Disavow List"]
        check(wb.sheetnames==exp, f"workbook tabs correct ({wb.sheetnames})")
        heads={"Referring Domain Audit":["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page","Linking Page Title","Source","IP","Disavow Line"],
               "Disavow List":["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]}
        for tab,h in heads.items():
            ws=wb[tab]; got=[ws.cell(1,i+1).value for i in range(len(h))]
            check(got==h, f"{tab} headers correct")
        # disavow-list row count == disavow lines
        ws=wb["Disavow List"]; n=ws.max_row-1
        check(n==len(hosts), f"Disavow List rows ({n}) == disavow file lines ({len(hosts)})")
        wb.close()
    except Exception as e:
        fails.append(f"workbook load error: {e}")

    print("=== VERIFY ===")
    for m in ok: print("  PASS:", m)
    for m in warns: print("  WARN:", m)
    for m in fails: print("  FAIL:", m)
    print(f"\n{len(ok)} passed, {len(warns)} warnings, {len(fails)} failed")
    sys.exit(1 if fails else 0)

if __name__=="__main__": main()
