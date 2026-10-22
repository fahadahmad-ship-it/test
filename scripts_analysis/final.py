import json, csv, re
from collections import defaultdict, Counter
with open("/home/user/test/audit/data/classified_domains.json", encoding="utf-8") as f:
    dom = json.load(f)
links=[]
with open("/home/user/test/audit/data/classified_links.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f): links.append(r)
dlinks=defaultdict(list)
for r in links: dlinks[r["referring_domain"]].append(r)

# Visible spam-copy: PBN/backlink-sales/SEO-ranking-sales/pharma/casino/porn.
# Require a clear commercial-SEO-spam or illicit-vertical phrase.
SPAM = re.compile(r"("
    r"buy[\s\w]{0,20}back ?links?|back ?links?[\s\w]{0,15}for sale|aged domains?(\s*(and|&)\s*back ?links?)?|"
    r"pbn back ?links?|\bpbn\b|manual outreach back ?links?|tiered link building|"
    r"seo authority back ?links?|dofollow link building|dofollow (seo )?back ?links?|"
    r"link building (service|to)|higher da and dr|da\d+\s*pa\d+|\bda\s?\d{2}\b|"
    r"raise domain rating|increase (trust|citation) flow|citation flow|trust flow|"
    r"improve (google )?rankings?|google rankings?|rank on 1st page|boost[\s\w]{0,15}(ranking|backlink)|"
    r"guest posts?|increase (your )?domain authority|unbeatable[\s\w]{0,15}(seo|ranking)|"
    r"casino|slot(s| gacor| online)?|judi|togel|poker|baccarat|sportsbook|betting|"
    r"viagra|cialis|tadalafil|sildenafil|canadian pharmacy|erythromycin|"
    r"escort|\bporn\b|\bxxx\b|replica (watch|rolex)|payday loan|forex trading"
    r")", re.I)

def scan(*texts):
    for t in texts:
        if not t: continue
        m = SPAM.search(str(t))
        if m: return m.group(0)
    return None

keepheld = {k:v for k,v in dom.items() if v.get("status","").startswith(("Keep","Held"))}

disavow=[]; nofollow_na=[]; held_leave=[]
for d,v in keepheld.items():
    status=v["status"]
    # gather evidence across domain fields + all link rows (+ host)
    ev=None; ev_src=None
    host_hit = SPAM.search(d)
    dofollow_spam=False; nofollow_spam=False; exact_commercial=False
    best_quote=None
    for r in dlinks.get(d,[]):
        hit = scan(r.get("anchor"), r.get("title"))
        at=(r.get("anchor_type") or "").lower()
        if ("exact" in at) or ("commercial" in at) or ("money" in at):
            exact_commercial=True
        if hit:
            nf=str(r.get("nofollow","")).strip().lower()
            isdo = nf in ("false","0","","no")
            q = (r.get("title") or r.get("anchor") or "")[:85]
            if isdo:
                dofollow_spam=True; best_quote=best_quote or q
            else:
                nofollow_spam=True; best_quote=best_quote or q
    dom_hit = scan(v.get("top_anchor"), v.get("example_title"), v.get("example_url"))
    if host_hit and not best_quote:
        best_quote = d+" (host)"
    if dom_hit and not best_quote:
        best_quote = str(v.get("example_title") or v.get("top_anchor"))[:85]

    has_spam = dofollow_spam or nofollow_spam or host_hit or dom_hit
    if not has_spam:
        continue
    rec = {"domain":d,"status":status,"do":v.get("dofollow"),"nf":v.get("nofollow"),
           "flag":v.get("spam_flag"),"quote":best_quote,"exact":exact_commercial}
    if exact_commercial:
        held_leave.append(rec)
    elif dofollow_spam or (int(v.get("dofollow") or 0)>0 and (host_hit or dom_hit)):
        disavow.append(rec)
    else:
        nofollow_na.append(rec)

def pr(title, lst):
    print(f"\n===== {title}: {len(lst)} =====")
    for r in sorted(lst, key=lambda x:(-int(x['do'] or 0))):
        print(f"{r['domain']} | {r['status']} | do={r['do']} nf={r['nf']} flag={r['flag']} | {r['quote']!r}")
pr("-> Spam (Disavow)  [dofollow + visible spam]", disavow)
pr("-> Spam (Nofollow, No Action)  [all nofollow]", nofollow_na)
pr("-> LEAVE HELD (exact-match commercial anchor)", held_leave)
print("\nTOTAL reclassifications:", len(disavow)+len(nofollow_na))
