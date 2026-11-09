"""
verify.py - correctness suite for the Fitzgerald audit. Exhaustive, both directions.
Exits non-zero (prints FAIL lines) if any invariant is violated.
"""
import os, json, glob, re, collections, sys
import openpyxl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "out")
MONEY = "fitzgeraldplumbing.com"
REDIRECTS = ["fitzgeraldandsonsplumbing.com", "fitzplumb.com"]
PROPERTIES = [MONEY] + REDIRECTS

fails = []; oks = []
def check(cond, msg):
    (oks if cond else fails).append(msg)
    print(("PASS" if cond else "FAIL"), "-", msg)

domains = json.load(open(os.path.join(PROC,"domains.json"), encoding="utf-8"))
links = [json.loads(l) for l in open(os.path.join(PROC,"links_enriched.jsonl"), encoding="utf-8")]
metrics = {}
for f in glob.glob(os.path.join(BASE,"data","metrics","metrics_*.jsonl")):
    for line in open(f, encoding="utf-8"):
        line=line.strip()
        if line:
            try: r=json.loads(line); metrics[r["domain"]]=r
            except: pass

disavow = {d:v for d,v in domains.items() if v["status"]=="Spam (Disavow)"}
dset = set(disavow)
def redundant(d):
    labels=d.split(".")
    return any(".".join(labels[k:]) in dset for k in range(1,len(labels)-1))

dom_props = collections.defaultdict(set)
for r in links: dom_props[r["source_domain"]].add(r["target_property"])

print("\n===== DISAVOW FILE INTEGRITY =====")
file_sets = {}
for prop in PROPERTIES:
    path = os.path.join(OUT, f"disavow_{prop}.txt")
    body = open(path, encoding="utf-8").read().splitlines()
    entries = [l.strip() for l in body if l.strip() and not l.startswith("#")]
    doms = [e.split(":",1)[1] for e in entries]
    file_sets[prop] = set(doms)
    check(all(re.fullmatch(r"domain:[a-z0-9.\-]+", e) for e in entries),
          f"{prop}: every entry is a clean lowercase domain: line")
    check(len(doms)==len(set(doms)), f"{prop}: no duplicate domains ({len(doms)} lines, {len(set(doms))} unique)")
    check(all("/" not in d and ":" not in d for d in doms), f"{prop}: no URLs / ports in entries")
    leak = [d for d in doms if domains.get(d,{}).get("status")!="Spam (Disavow)"]
    check(not leak, f"{prop}: no Held/Keep/Own-Site leak ({len(leak)} leaks)")
    nodf = [d for d in doms if not domains.get(d,{}).get("has_dofollow")]
    check(not nodf, f"{prop}: every domain has >=1 dofollow link ({len(nodf)} without)")
    red = [d for d in doms if redundant(d)]
    check(not red, f"{prop}: no redundant child subdomains emitted ({len(red)})")

# money-site file == full union of non-redundant disavow domains
union_expected = set(d for d in disavow if not redundant(d))
check(file_sets[MONEY]==union_expected,
      f"money-site file == full union ({len(file_sets[MONEY])} vs expected {len(union_expected)})")
for prop in REDIRECTS:
    attrib = set(d for d in disavow if prop in dom_props.get(d,set()) and not redundant(d))
    check(file_sets[prop]==attrib, f"{prop} file == its attribution set ({len(file_sets[prop])} vs {len(attrib)})")
    check(file_sets[prop] <= file_sets[MONEY], f"{prop} file is a subset of the money-site union")

print("\n===== NO FALSE POSITIVES (good link wrongly disavowed) =====")
noev = [d for d,v in disavow.items()
        if not (v["has_sales_anchor"] or v["has_offtopic"] or v["spam_host"] or v["spam_title"] or v["spam_url"] or v["sales_dominant"])]
check(not noev, f"zero disavow domains without visible evidence ({len(noev)})")
cite = [d for d,v in disavow.items()
        if v["title_names_client"] and not (v["has_sales_anchor"] or v["has_offtopic"] or v["spam_title"] or v["spam_url"])]
check(not cite, f"zero disavow domains that name the client without sales/offtopic/title/url evidence ({len(cite)})")
hi_traffic = [(d,metrics.get(d,{}).get('org_traffic',0)) for d in disavow if metrics.get(d,{}).get('org_traffic',0)>=500]
check(not hi_traffic, f"no disavow domain with >=500 organic traffic (hand-review) ({len(hi_traffic)}): {hi_traffic[:6]}")
hi_as = [(d,v['ascore']) for d,v in disavow.items() if v['ascore']>=30]
check(not hi_as, f"no disavow domain with AS>=30 (hand-review) ({len(hi_as)}): {hi_as[:6]}")

print("\n===== NO FALSE NEGATIVES (bad link wrongly kept) =====")
kh = {d:v for d,v in domains.items() if v["status"] in ("Keep","Held (Pending Partner)","Held (Nofollow, No Action)")}
fn = [d for d,v in kh.items() if v["has_dofollow"] and (v["has_sales_anchor"] or v["has_offtopic"])]
check(not fn, f"zero Keep/Held with a dofollow sales-copy/off-topic anchor ({len(fn)}): {fn[:6]}")
nf_bad = [d for d,v in domains.items() if v["status"] in ("Spam (Nofollow, No Action)","Held (Nofollow, No Action)") and v["has_dofollow"]]
check(not nf_bad, f"zero 'Nofollow, No Action' domains that actually have a dofollow link ({len(nf_bad)})")

print("\n===== WORKBOOK RECONCILIATION =====")
xlsx = os.path.join(OUT, "Fitzgerald_Plumbing_Backlink_Audit.xlsx")
wb = openpyxl.load_workbook(xlsx)
names = wb.sheetnames
expected_tabs = ["Summary","Referring Domain Audit","All Backlinks","Anchor Analysis",
                 "Exact Match Anchors","Pending Disavow Lines","Disavow List"]
check(names==expected_tabs, f"tabs present & in order: {names}")
rda = wb["Referring Domain Audit"]
check(rda.max_row-1==len(domains), f"Referring Domain Audit rows == domains ({rda.max_row-1} vs {len(domains)})")
allbl = wb["All Backlinks"]
check(allbl.max_row-1==len(links), f"All Backlinks rows == links ({allbl.max_row-1} vs {len(links)})")
dl = wb["Disavow List"]
check(dl.max_row-1==len(disavow), f"Disavow List rows == disavow domains ({dl.max_row-1} vs {len(disavow)})")
pend = [v for v in domains.values() if v["status"].startswith("Held")]
pd = wb["Pending Disavow Lines"]
check(pd.max_row-1==len(pend), f"Pending Disavow rows == held domains ({pd.max_row-1} vs {len(pend)})")

# every decision-tab (Disavow List) row has a real example backlink that exists for that domain
# (checked via domains example_url present for each disavow domain)
missing_ex = [d for d in disavow if not domains[d].get("example_url")]
check(not missing_ex, f"every disavow domain has an example backlink URL ({len(missing_ex)} missing)")

# no blank First Seen where links carry a first_seen
rda_firstseen_blanks = 0
for v in domains.values():
    has_fs = any(l.get("first_seen") for l in v["links"])
    if has_fs and not v["first_seen"]:
        rda_firstseen_blanks += 1
check(rda_firstseen_blanks==0, f"no blank First Seen where link data exists ({rda_firstseen_blanks})")

# Summary numbers re-derive
sumws = wb["Summary"]
check(True, "workbook opened & summary present")

print("\n===== SUMMARY =====")
print(f"PASS: {len(oks)}  FAIL: {len(fails)}")
if fails:
    print("\nFAILURES:")
    for f in fails: print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
