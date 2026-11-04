#!/usr/bin/env python3
import sys, collections, re, json
import openpyxl

SRC = sys.argv[1]
OUT = sys.argv[2]
wb = openpyxl.load_workbook(SRC, data_only=True)
def read(tab):
    ws=wb[tab]; rr=list(ws.iter_rows(values_only=True))
    h=[("" if c is None else str(c)).strip() for c in rr[0]]
    return h,[list(r) for r in rr[1:] if any(c is not None and str(c).strip()!="" for c in r)]
rh,rda=read('Referring Domain Audit'); ci={n:i for i,n in enumerate(rh)}
ah,abl=read('All Backlinks'); ai={n:i for i,n in enumerate(ah)}
eh,ema=read('Exact Match Anchors'); ei={n:i for i,n in enumerate(eh)}
ph,pend=read('Pending Disavow Lines')

SALES=["backlink","seo","pbn","dofollow"," da "," pa ","da50","pa40","da 50","pa 40","rank","premium",
 "niche edit","link building","link-building","buy ","guest post","authority","boost","high quality",
 "aged domain","telegram","serp","web 2.0"," moz","domain authority","link velocity","link service",
 "powerful","traffic to","websites grow","dapa","indexing","do follow","white hat"]
OFF=["casino","gambl","slot","poker","roulette","betting"," bet ","porn","escort","viagra","cialis",
 "pharma","payday","loan","crypto","bitcoin","forex","adult","sex "]
HOST=["backlink","seo","pbn","directory","listing","-dir","dir.","bookmark","submit","rank","dapa",
 "domainlist","buydomain","ageddomain","marketplace","catalog","weblink","linkz","linx"]
MKT=["where to buy","aged domains","domain list","domains for sale","buy backlinks","for sale"]

def hit(text, toks):
    t=(text or "").lower()
    return [k for k in toks if k in t]

# group all backlinks by domain
by_dom=collections.defaultdict(list)
for r in abl:
    by_dom[str(r[ai['Referring Domain']]).lower()].append(r)

status={str(r[ci['Domain']]).lower():str(r[ci['Status']]) for r in rda}
dofo={str(r[ci['Domain']]).lower():(r[ci['Dofollow Links']] or 0) for r in rda}
rda_dom=[str(r[ci['Domain']]).lower() for r in rda]

disavow=[d for d in rda_dom if status[d]=="Spam (Disavow)"]
keep=[d for d in rda_dom if status[d]=="Keep"]
held=[d for d in rda_dom if status[d].startswith("Held")]

def evidence_for(dom):
    """Return dict of evidence found across ALL of a domain's backlinks + host."""
    ev={"sales":set(),"off":set(),"host":set(),"mkt":set(),"spam_type":0,"client_no_sales":[]}
    ev["host"].update(hit(dom, HOST))
    for r in by_dom.get(dom,[]):
        anc=str(r[ai['Anchor Text']] or ""); title=str(r[ai['Linking Page Title']] or "")
        url=str(r[ai['Linking Page URL']] or ""); atype=str(r[ai['Anchor Type']] or "")
        if atype.startswith("Spam"): ev["spam_type"]+=1
        for field in (anc,title,url):
            ev["sales"].update(hit(field,SALES)); ev["off"].update(hit(field,OFF)); ev["mkt"].update(hit(field,MKT))
        ev["host"].update(hit(url,HOST))
        # client named without sales copy
        tl=title.lower()
        if ("new garden" in tl or "newgarden" in tl) and not (hit(title,SALES) or hit(anc,SALES)):
            ev["client_no_sales"].append(title[:60])
    return ev

flags=collections.defaultdict(list)
for d in disavow:
    ev=evidence_for(d)
    has_ev = ev["spam_type"] or ev["sales"] or ev["off"] or ev["host"] or ev["mkt"]
    if not has_ev:
        flags["FP_no_visible_evidence"].append(d)
    if ev["client_no_sales"] and not (ev["sales"] or ev["off"] or ev["spam_type"]>0):
        flags["FP_client_cited_no_salescopy"].append((d, ev["client_no_sales"][0]))

# disavow domains whose anchor types are ALL benign (no spam-type anchor on any link)
for d in disavow:
    atypes=set(str(r[ai['Anchor Type']] or "") for r in by_dom.get(d,[]))
    if not any(a.startswith("Spam") for a in atypes):
        ev=evidence_for(d)
        basis=[]
        if ev["host"]: basis.append("host:"+",".join(sorted(ev["host"])))
        if ev["sales"]: basis.append("sales-in-title/url")
        if ev["off"]: basis.append("off-topic")
        if ev["mkt"]: basis.append("marketplace-title")
        flags["disavow_benign_anchor_only"].append((d, "|".join(sorted(atypes)), (";".join(basis) or "NO-BASIS")))

# FALSE NEGATIVES: Keep/Held with a dofollow spam/off-topic link
for d in keep+held:
    for r in by_dom.get(d,[]):
        atype=str(r[ai['Anchor Type']] or ""); lt=str(r[ai['Link Type']] or "")
        anc=str(r[ai['Anchor Text']] or ""); title=str(r[ai['Linking Page Title']] or "")
        if lt=="Dofollow" and (atype.startswith("Spam") or hit(anc,OFF) or hit(title,OFF)):
            flags["FN_keep_held_dofollow_spam"].append((d,status[d],atype,anc[:40]))
            break

# AS distribution in disavow + top AS disavow domains
as_vals=[(d, next((r[ci['AS']] for r in rda if str(r[ci['Domain']]).lower()==d), None)) for d in disavow]
as_num=[(d,float(a)) for d,a in as_vals if a not in (None,"") and str(a).replace('.','',1).isdigit()]
as_num.sort(key=lambda x:-x[1])
flags["top_AS_in_disavow"]=as_num[:15]

# subdomain/parent redundancy within disavow set
dset=set(disavow)
def registrable(d):
    parts=d.split(".");
    # naive: handle a few two-level TLDs
    two=("co.uk","org.uk","com.au","co.in","co.nz","com.br")
    if len(parts)>=3 and ".".join(parts[-2:]) in two: return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts)>=2 else d
for d in disavow:
    if d!=registrable(d) and registrable(d) in dset:
        flags["redundant_subdomain_with_parent"].append((d, registrable(d)))

# target host / property check across ALL backlinks
tgt_hosts=collections.Counter()
for r in abl:
    u=str(r[ai['Target URL']] or "")
    m=re.match(r'https?://([^/]+)', u)
    if m: tgt_hosts[m.group(1).lower()]+=1
flags["target_hosts"]=tgt_hosts.most_common(15)

# blank First Seen in RDA
blank_fs=[str(r[ci['Domain']]) for r in rda if r[ci['First Seen']] in (None,"")]
flags["blank_first_seen_count"]=len(blank_fs)
flags["blank_first_seen_sample"]=blank_fs[:10]

# domains in RDA but with zero backlinks in All Backlinks (and vice versa)
abl_doms=set(by_dom.keys()); rda_set=set(rda_dom)
flags["rda_not_in_allbacklinks"]=sorted(rda_set-abl_doms)[:20]
flags["allbacklinks_not_in_rda"]=sorted(abl_doms-rda_set)[:20]
flags["rda_not_in_abl_count"]=len(rda_set-abl_doms)
flags["abl_not_in_rda_count"]=len(abl_doms-rda_set)

# dup domains in RDA
dup=[d for d,c in collections.Counter(rda_dom).items() if c>1]
flags["duplicate_rda_domains"]=dup[:20]; flags["duplicate_rda_count"]=len(dup)

# Exact Match tab: every row has an example backlink URL? and market sanity
ema_missing_ex=[r[ei['Referring domain']] for r in ema if not r[ei['Example backlink (linking page)']]]
flags["ema_missing_example"]=ema_missing_ex[:10]
# held count reconcile: EMA rows vs Held buckets
flags["ema_rows"]=len(ema)
flags["held_pending"]=sum(1 for d in rda_dom if status[d]=="Held (Pending Partner)")
flags["held_nofollow"]=sum(1 for d in rda_dom if status[d]=="Held (Nofollow, No Action)")

# summarize
summary={}
for k,v in flags.items():
    if isinstance(v,list): summary[k]=len(v)
    else: summary[k]=v
print("=== DEEP CHECK SUMMARY ===")
print(json.dumps(summary, indent=1, default=str))
print("\n=== KEY SAMPLES ===")
for k in ["FP_no_visible_evidence","FP_client_cited_no_salescopy","disavow_benign_anchor_only",
          "FN_keep_held_dofollow_spam","redundant_subdomain_with_parent","top_AS_in_disavow","target_hosts"]:
    print(f"\n-- {k} --")
    for item in (flags[k][:25] if isinstance(flags[k],list) else [flags[k]]):
        print("  ", item)

json.dump({k:(v if not isinstance(v,list) else v) for k,v in flags.items()}, open(OUT,"w"), indent=1, default=str)
print("\nfull flags ->", OUT)
