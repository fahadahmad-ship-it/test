"""Critical self-review of the classification: hunt false positives (genuine
citations in the disavow set) and false negatives (dofollow spam kept out)."""
import glob, sys, collections
sys.path.insert(0, "/home/user/test/ritter/scripts")
import config as C
from load import read_semrush_csv, host_of, path_of, canon_domain
import classify

bl,_,_ = read_semrush_csv(sorted(glob.glob("/home/user/test/ritter/data/fetch/backlinks_p*.csv")),10)
rd,_,_ = read_semrush_csv(sorted(glob.glob("/home/user/test/ritter/data/rd/refdomains_p*.csv")),9)
from build import load_metrics, num
comp, rank = load_metrics()
records, ip24 = classify.build_domain_records(bl, rd, comp, rank)
rows=[]
for d in sorted(records):
    rec=records[d]; st,why,at=classify.classify_domain(rec,ip24)
    rec["status"]=st; rec["why"]=why; rows.append(rec)

bystatus=collections.Counter(r["status"] for r in rows)
print("STATUS:",dict(bystatus))

# Genuine-citation signatures that must NOT be in any spam bucket
GENUINE=["superpages","yellowpages","yelp","manta","bbb.org","mapquest","chamber",
 "angi.com","houzz","thomasnet","dnb.com","bizapedia","buzzfile","zoominfo","crunchbase",
 "facebook","linkedin","indeed","glassdoor","eianet","acadiana","seamless.ai","true-naics",
 ".gov",".edu","opencorporates","bbb","foursquare","alignable"]
print("\n--- Possible FALSE POSITIVES: genuine-looking hosts/titles in a SPAM bucket ---")
fp=0
for r in rows:
    if r["status"].startswith("Spam"):
        titles=" ".join(l.get("source_title","") for l in r["links"]).lower()
        if any(g in r["domain"] for g in GENUINE) or any(g in titles for g in GENUINE):
            print(f"  [{r['status']}] {r['domain']}  AS={num(r['AS'])}  why={r['why']}")
            print(f"       title: {r['links'][0].get('source_title','')[:80]!r}")
            fp+=1
print(f"  total flagged: {fp}")

# Disavow entries with NO visible evidence (should be zero)
print("\n--- Disavow entries resting on NO visible evidence (must be 0) ---")
ne=0
for r in rows:
    if r["status"]=="Spam (Disavow)":
        links=r["links"]
        anchors=[l.get("anchor","") for l in links]; titles=[l.get("source_title","") for l in links]
        atset=set(classify.anchor_type(a,t) for a,t in zip(anchors,titles))
        ev = (classify.ANCHOR_SPAM_SALESCOPY in atset or classify.ANCHOR_SPAM_OFFTOPIC in atset
              or classify.host_is_spam(r["domain"]) or any(classify.title_is_spam(t) for t in titles))
        if not ev:
            print(f"  NO-EV {r['domain']} AS={num(r['AS'])} why={r['why']} anchors={list(atset)} title={titles[0][:60]!r}")
            ne+=1
print(f"  total no-evidence disavow: {ne}")

# Dofollow spam kept out (Keep/Held with a dofollow PBN/offtopic anchor) -> false negatives
print("\n--- Possible FALSE NEGATIVES: Keep/Held with a dofollow spam anchor ---")
fn=0
for r in rows:
    if r["status"] in ("Keep","Held (Pending Partner)","Held (Nofollow, No Action)"):
        for l in r["links"]:
            nf=l.get("nofollow","").lower()=="true"
            at=classify.anchor_type(l.get("anchor",""),l.get("source_title",""))
            if (not nf) and at in (classify.ANCHOR_SPAM_SALESCOPY,classify.ANCHOR_SPAM_OFFTOPIC):
                print(f"  [{r['status']}] {r['domain']} AS={num(r['AS'])} anchor={l.get('anchor','')[:50]!r}")
                fn+=1; break
print(f"  total flagged: {fn}")

# The Keep set — show all with AS + a title, to eyeball genuineness
print("\n--- KEEP set (all), AS / reason / example title ---")
for r in sorted([r for r in rows if r["status"]=="Keep"], key=lambda r:-num(r["AS"])):
    print(f"  AS={num(r['AS']):3} {r['domain']:34} {r['why'][:40]:40} {r['links'][0].get('source_title','')[:46]!r}")
