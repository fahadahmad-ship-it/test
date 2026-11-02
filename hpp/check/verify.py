"""
Correctness checks for the High Priority Plumbing audit, both directions,
over the WHOLE set (not a sample). Prints PASS/FAIL per check.
"""
import json, os, re, sys
from collections import Counter, defaultdict
import openpyxl
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from load import canon_host

BASE = "/home/user/test/hpp"
MONEY = "highpriorityplumbing.com"
doms = json.load(open(os.path.join(BASE, "out/classified_domains.json")))
links = json.load(open(os.path.join(BASE, "out/classified_links.json")))
disavow_path = os.path.join(BASE, "out/disavow_highpriorityplumbing.txt")

links_by_dom = defaultdict(list)
for l in links:
    links_by_dom[l["refdomain"]].append(l)

fails = []
def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail and not ok else ""))
    if not ok: fails.append(name)

SPAM_ANCHOR_TYPES = {"Spam: keyword stuffed SEO sales copy", "Spam: messaging-app invitation", "Spam: off-topic"}
RE_HOSTSPAM = re.compile(r'(back ?link|linkbuilding|buybacklink|seobacklink|\bpbn\b|dofollow|guestpost|rankbuild|rankscal|toprank|nichelink|sponsoredlink|linkoutreach|page1boost|seoboost|linkjuice|offpage|editorlink|darksidelinks|quarterlinks|(^|[.-])seo([.-]|\d)|-seo\.|seo-)', re.I)

def has_evidence(dom):
    ls = links_by_dom[dom]
    if any(l["anchor_type"] in SPAM_ANCHOR_TYPES for l in ls): return True
    if RE_HOSTSPAM.search(dom): return True
    if any(re.search(r'(domain list page|aged domains|buy backlinks|where to buy|casino|viagra|escort)', (l["page_title"] or ""), re.I) for l in ls): return True
    return False

def names_client_clean(dom):
    return any(re.search(r'high ?priority ?plumbing', (l["page_title"] or ""), re.I) and
              not re.search(r'(backlink|seo|pbn|rank higher|authority|dofollow)', (l["page_title"] or ""), re.I)
              for l in links_by_dom[dom])

# ---- parse disavow file ----
dl_lines = []
for line in open(disavow_path):
    s = line.strip()
    if not s or s.startswith("#"): continue
    dl_lines.append(s)
dl_doms = [l.split("domain:", 1)[1] for l in dl_lines if l.startswith("domain:")]

# A. disavow-file integrity
check("every disavow line is 'domain:<host>' lowercase, no URL",
      all(re.fullmatch(r'domain:[a-z0-9.\-]+', l) for l in dl_lines),
      detail=str([l for l in dl_lines if not re.fullmatch(r'domain:[a-z0-9.\-]+', l)][:3]))
check("no duplicate disavow lines", len(dl_doms) == len(set(dl_doms)),
      detail=f"{len(dl_doms)} lines {len(set(dl_doms))} unique")
bad_status = [d for d in dl_doms if doms.get(d, {}).get("status") != "Spam (Disavow)"]
check("every disavow domain is Spam (Disavow)", not bad_status, detail=str(bad_status[:5]))
no_dofollow = [d for d in dl_doms if doms.get(d, {}).get("dofollow_links", 0) < 1]
check("every disavow domain has >=1 dofollow link", not no_dofollow, detail=str(no_dofollow[:5]))
# redundant children excluded
child_in_file = [d for d in dl_doms for p in dl_doms if p != d and d.endswith("."+p)]
check("no redundant child when parent present", not child_in_file, detail=str(child_in_file[:5]))
# file == full union of Spam(Disavow) minus redundant
disavow_all = [d for d,v in doms.items() if v["status"] == "Spam (Disavow)"]
redundant = set(d for d in disavow_all for p in disavow_all if p != d and d.endswith("."+p))
expected = set(disavow_all) - redundant
check("disavow file equals full union of non-redundant Spam(Disavow)", set(dl_doms) == expected,
      detail=f"file {len(dl_doms)} expected {len(expected)} missing {list(expected-set(dl_doms))[:3]} extra {list(set(dl_doms)-expected)[:3]}")

# B. no false positives
noevidence = [d for d in dl_doms if not has_evidence(d)]
check("zero disavow domains rest on NO visible evidence", not noevidence, detail=f"{len(noevidence)}: {noevidence[:8]}")
cleanname = [d for d in dl_doms if names_client_clean(d)]
check("zero disavow domains are clean client citations", not cleanname, detail=f"{len(cleanname)}: {cleanname[:8]}")

# C. no false negatives
keptheld = [d for d,v in doms.items() if v["status"] in ("Keep","Held (Pending Partner)","Held (Nofollow, No Action)")]
leak = [d for d in keptheld if any((l["link_type"]=="Dofollow" and l["anchor_type"] in ("Spam: keyword stuffed SEO sales copy","Spam: off-topic")) for l in links_by_dom[d])]
check("zero Keep/Held domains carry a dofollow sales-copy/off-topic anchor", not leak, detail=f"{len(leak)}: {leak[:8]}")
nf_wrong = [d for d,v in doms.items() if v["status"].startswith("Spam (Nofollow") and v["dofollow_links"]>0]
check("zero nofollow-spam domains actually have a dofollow link", not nf_wrong, detail=str(nf_wrong[:8]))
heldnf_wrong = [d for d,v in doms.items() if v["status"]=="Held (Nofollow, No Action)" and v["dofollow_links"]>0]
check("zero held-nofollow domains actually have a dofollow link", not heldnf_wrong, detail=str(heldnf_wrong[:8]))

# D. workbook reconciliation
xlsx = os.path.join(BASE, "out/HighPriorityPlumbing_Backlinks_Audit.xlsx")
wb = openpyxl.load_workbook(xlsx)
rda = wb["Referring Domain Audit"]; ab = wb["All Backlinks"]; dl = wb["Disavow List"]
check("RDA has one row per referring domain", rda.max_row-1 == len(doms), detail=f"{rda.max_row-1} vs {len(doms)}")
check("All Backlinks has one row per link", ab.max_row-1 == len(links), detail=f"{ab.max_row-1} vs {len(links)}")
check("Disavow List has one row per emitted disavow domain", dl.max_row-1 == len(expected), detail=f"{dl.max_row-1} vs {len(expected)}")
# Summary status counts reconcile
summ = wb["Summary"]
stat_tbl = {}
for r in range(4, 10):
    stat_tbl[summ.cell(row=r,column=1).value] = summ.cell(row=r,column=2).value
cnt = Counter(v["status"] for v in doms.values())
recon = all(stat_tbl.get(s,0) == cnt.get(s,0) for s in cnt)
check("Summary status-table counts re-derive from data", recon, detail=str({s:(stat_tbl.get(s),cnt.get(s)) for s in cnt}))
total_cell = summ.cell(row=10,column=2).value
check("Summary total = number of domains", total_cell == len(doms), detail=f"{total_cell} vs {len(doms)}")

# E. every decision-tab (Disavow List) row has a real example backlink that exists
missing_ex = [d for d in expected if not doms[d]["example_page"]]
check("every disavow domain has a real example backlink", not missing_ex, detail=str(missing_ex[:8]))

# F. no blank example cells in RDA where links exist
blank_rows = 0
for r in range(2, rda.max_row+1):
    dom = rda.cell(row=r, column=1).value
    if dom and not rda.cell(row=r, column=13).value and links_by_dom.get(dom):  # Example Linking Page col 13
        blank_rows += 1
check("no blank Example-Linking-Page where links exist", blank_rows == 0, detail=f"{blank_rows} blanks")

print(f"\n{'ALL CHECKS PASSED' if not fails else str(len(fails))+' CHECKS FAILED: '+str(fails)}")
