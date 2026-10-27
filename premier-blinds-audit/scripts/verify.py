"""Exhaustive, both-directions verification. Fails loudly. Checks the data,
the disavow files, and the saved workbook. Styling is read from the saved
.xlsx XML (not openpyxl) per the playbook."""
import os, sys, re, glob, zipfile
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
import load, classify, pipeline
OUT = os.path.join(os.path.dirname(__file__), "..", "out")
WB = os.path.join(OUT, "Premier_Blinds_and_Designs_Backlinks_Audit.xlsx")

fails=[]; warns=[]
def check(cond, msg):
    (print("  ok  "+msg) if cond else fails.append(msg))
def warn(cond,msg):
    if not cond: warns.append(msg)

def read_disavow(path):
    doms=[];
    for line in open(path,encoding="utf-8"):
        line=line.strip()
        if not line or line.startswith("#"): continue
        doms.append(line)
    return doms

def main():
    ds = pipeline.build()
    domains=ds["domains"]; links=ds["links"]
    emitted=set(ds["emitted"])
    print("=== DATA & CLASSIFICATION ===")
    NDOM=len(domains); NLINK=len(links)
    print("  domains=%d links=%d (Ahrefs merged: +%d new links)"%(NDOM,NLINK,ds.get("ahrefs_new",0)))
    check(NDOM>0 and NLINK>0, "dataset non-empty")

    # ---- disavow file integrity ----
    print("\n=== DISAVOW FILE INTEGRITY ===")
    f1=os.path.join(OUT,"disavow_premierblindsanddesigns.com.txt")
    f2=os.path.join(OUT,"disavow_thepremierdesigns.com.txt")
    u=read_disavow(f1); t=read_disavow(f2)
    check(all(re.fullmatch(r"domain:[a-z0-9.\-]+", x) for x in u), "union: every line is domain:<host> lowercase")
    check(all(re.fullmatch(r"domain:[a-z0-9.\-]+", x) for x in t), "redir: every line is domain:<host> lowercase")
    check(len(u)==len(set(u)), "union: no duplicate lines")
    check(len(t)==len(set(t)), "redir: no duplicate lines")
    udoms={x.split(":",1)[1] for x in u}; tdoms={x.split(":",1)[1] for x in t}
    # every file domain is Spam (Disavow)
    leak=[d for d in udoms if domains.get(d,{}).get("status")!="Spam (Disavow)"]
    check(not leak, "union: no non-Spam(Disavow) leak (%d)"%len(leak))
    leak2=[d for d in tdoms if domains.get(d,{}).get("status")!="Spam (Disavow)"]
    check(not leak2, "redir: no non-Spam(Disavow) leak (%d)"%len(leak2))
    # every file domain has >=1 dofollow
    nodof=[d for d in udoms if domains[d]["dofollow"]==0]
    check(not nodof, "union: every domain has >=1 dofollow link (%d fail)"%len(nodof))
    # redundant children not emitted
    check(all(not any(p!=d and d.endswith("."+p) for p in udoms) for d in udoms),
          "union: no redundant child whose parent is also listed")
    # union == full set of Spam(Disavow) emitted ; redir subset of union
    allspam={d for d,v in domains.items() if v["status"]=="Spam (Disavow)"}
    check(udoms==emitted, "union == full emitted Spam(Disavow) set")
    check(tdoms<=udoms, "redir file is a subset of the union")
    check(all("thepremierdesigns.com" in domains[d]["properties"] for d in tdoms),
          "redir: every domain actually points at thepremierdesigns.com")

    # ---- NO FALSE POSITIVES (good link wrongly disavowed) ----
    print("\n=== NO FALSE POSITIVES ===")
    EVIDENCE_REASONS={"PBN sales-copy anchor","Spam host name","Spam page title / URL template","Off-topic anchor"}
    noev=[d for d in udoms if domains[d]["reason"] not in EVIDENCE_REASONS]
    check(not noev, "every disavow domain rests on an evidence-based reason (%d fail: %s)"%(len(noev),noev[:5]))
    # benign-citation leak: a disavow domain whose linking title names client w/o sales copy and no PBN anchor
    bad=[]
    for d in udoms:
        for l in domains[d]["links"]:
            title=(l["source_title"] or "").lower()
            names=("premier blinds" in title or "premierblindsanddesigns" in title)
            if names and not classify._any(classify.SPAM_TITLE,title) and not classify._any(classify.PBN,(l["anchor"] or "").lower()):
                bad.append((d,l["source_title"])); break
    check(not bad, "no disavow domain is a genuine citation naming the client (%d fail)"%len(bad))
    for d,ti in bad[:10]: print("      LEAK",d,"|",ti[:60])
    # traffic hand-review: a disavow domain with real organic traffic is a
    # false-positive risk -> list for manual review and confirm it still rests on evidence
    traf=sorted(((domains[d]["traffic"] or 0, d) for d in udoms), reverse=True)
    withtraf=[(t,d) for t,d in traf if t>=100]
    print("  disavow domains with organic_traffic >= 100 (hand-review): %d" % len(withtraf))
    for t,d in withtraf[:15]:
        print("      traffic=%-6d %-28s reason=%s title=%s" % (t,d,domains[d]["reason"],(domains[d]["example_title"] or '')[:40]))
    check(all(domains[d]["reason"] in EVIDENCE_REASONS for _,d in withtraf),
          "every high-traffic disavow domain still rests on visible spam evidence")

    # ---- NO FALSE NEGATIVES (bad link wrongly kept) ----
    print("\n=== NO FALSE NEGATIVES ===")
    viol=[]
    for d,v in domains.items():
        if v["status"] in ("Spam (Disavow)","Spam (Nofollow, No Action)","Own Site"): continue
        for l in v["links"]:
            df=l["nofollow"].strip().lower()=="false"
            at=classify.anchor_type(l["anchor"])
            if df and at in classify.SPAM_ANCHOR_TYPES:
                viol.append((d,v["status"],at)); break
    check(not viol, "zero Keep/Held domains carry a dofollow spam/off-topic anchor (%d fail)"%len(viol))
    for x in viol[:10]: print("      VIOL",x)
    # nofollow-marked spam actually all nofollow
    badnf=[d for d,v in domains.items() if v["status"]=="Spam (Nofollow, No Action)" and v["dofollow"]>0]
    check(not badnf, "zero nofollow-spam domains actually have a dofollow link (%d fail)"%len(badnf))

    # ---- WORKBOOK RECONCILE (read saved xlsx) ----
    print("\n=== WORKBOOK RECONCILE (saved xlsx XML) ===")
    z=zipfile.ZipFile(WB)
    names=[n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$",n)]
    ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    def rowcount(sheetfile):
        root=ET.fromstring(z.read(sheetfile))
        return len(root.findall(ns+"sheetData/"+ns+"row"))
    # map sheet order
    wbxml=ET.fromstring(z.read("xl/workbook.xml"))
    sheet_names=[s.get("name") for s in wbxml.findall(ns+"sheets/"+ns+"sheet")]
    check(sheet_names==["Summary","Referring Domain Audit","All Backlinks","Anchor Analysis",
                        "Exact Match Anchors","Pending Disavow Lines","Disavow List"],
          "7 tabs in correct order: %s"%sheet_names)
    # rows: RDA = 3159+1 ; AllBacklinks = 4493+1 ; Disavow = 2603+1
    rc={}
    for i,sf in enumerate(sorted(names, key=lambda n:int(re.search(r"\d+",n.split('/')[-1]).group()))):
        rc[sheet_names[i]]=rowcount(sf)
    check(rc["Referring Domain Audit"]==NDOM+1, "RDA rows = domains+1 = %d (got %d)"%(NDOM+1,rc["Referring Domain Audit"]))
    check(rc["All Backlinks"]==NLINK+1, "All Backlinks rows = links+1 = %d (got %d)"%(NLINK+1,rc["All Backlinks"]))
    check(rc["Disavow List"]==len(emitted)+1, "Disavow List rows = %d (got %d)"%(len(emitted)+1,rc["Disavow List"]))
    # Pending Disavow == held pending partner count
    held_pp=sum(1 for v in domains.values() if v["status"]=="Held (Pending Partner)")
    check(rc["Pending Disavow Lines"]==held_pp+1, "Pending Disavow rows = held-pending %d (+1) got %d"%(held_pp,rc["Pending Disavow Lines"]))

    print("\n=== RESULT ===")
    if warns:
        print("WARNINGS:")
        for w in warns: print("  !",w)
    if fails:
        print("FAILURES (%d):"%len(fails))
        for f in fails: print("  X",f)
        sys.exit(1)
    print("ALL CHECKS PASSED")

if __name__=="__main__":
    main()
