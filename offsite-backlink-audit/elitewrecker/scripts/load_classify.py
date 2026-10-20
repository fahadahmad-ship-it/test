#!/usr/bin/env python3
"""Load all sources, merge links, classify every referring domain (6 statuses),
and write intermediate CSVs the workbook builder consumes.

Sources:
  Semrush refdomains  data/rd/semrush_refdomains_*.csv   (; delimited)
  Semrush backlinks   data/fetch/semrush_backlinks_*.csv (; delimited, positional tail)
  Semrush AS bulk     data/metrics/as_*.csv              (; delimited)
  Semrush domain_rank data/metrics/rank_*.csv            (; delimited)
  Ahrefs refdomains   data/ahrefs_refdomains.tsv         (tab, quoted, UTF-8)
  Ahrefs backlinks    data/ahrefs_backlinks.tsv          (tab, quoted, UTF-8)

Principles (playbook s0): Semrush is the metric source; nothing disavowed on
score/TLD/vendor-flag alone (visible link evidence required); when in doubt, Keep/Hold.
"""
import csv, io, glob, json, html, re, sys
from collections import defaultdict, Counter
from datetime import datetime, timezone

BASE = "/home/user/test/offsite-backlink-audit/elitewrecker"
D = BASE + "/data"
OUT = BASE + "/out"

# ---------------- client constants (the only per-client section) ----------------
CLIENT_NAME = "Elite Service Recovery & Towing"
MONEY_SITE  = "elitewrecker.com"
OWNED       = {"elitewrecker.com", "elitewrecker.net"}   # .net 301s into .com
GEO = ["lake charles", "lafayette", "louisiana", "sulphur", "moss bluff", " la ", " la,", ", la", "la "]
GEO_STRICT = ["lake charles", "lafayette", "louisiana", "sulphur", "moss bluff"]
SERVICE = ["tow", "wrecker", "roadside", "recovery", "flatbed", "haul", "hauling",
           "heavy duty", "heavy-duty", "heavy equipment transport", "emergency road",
           "jump start", "lockout", "winch", "tire change", "car hauler", "dovetail",
           "vehicle recovery", "24 hour", "24/7", "24 hrs"]
PRESS_HOSTS = {"einpresswire.com","prnewswire.com","openpr.com","issuewire.com","pr.com",
               "newswire.com","prlog.org","pressreleasepoint.com","abnewswire.com"}
# ---------------------------------------------------------------------------------

def host_of(u):
    u = (u or "").strip()
    if "//" in u: u = u.split("//",1)[1]
    u = u.split("/",1)[0].split("?",1)[0].split("#",1)[0]
    if u.startswith("www."): u = u[4:]
    return u.lower().strip(".")

def path_of(u):
    u = (u or "").strip()
    if "//" in u: u = u.split("//",1)[1]
    p = "/" + u.split("/",1)[1] if "/" in u else "/"
    p = p.split("#",1)[0]
    return p.lower()

def canon(u):
    h = host_of(u); p = path_of(u).split("?",1)[0].rstrip("/")
    return h + p

def ts_to_date(x):
    try:
        return datetime.fromtimestamp(int(str(x).strip()), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""

def ah_date(x):
    x = (x or "").strip()
    return x.split(" ")[0] if x else ""

# ---------------- referring-domain universe + reg-domain mapping ----------------
def load_semi(path, want):
    with io.open(path, "r", encoding="utf-8") as f:
        r = csv.reader(f, delimiter=";")
        hdr = next(r)
        idx = {}
        for w in want:
            for alias in want[w]:
                if alias in hdr: idx[w] = hdr.index(alias); break
        for row in r:
            if not row or all(not c for c in row): continue
            yield {k: (row[i] if i < len(row) else "") for k, i in idx.items()}

refmeta = {}  # domain -> dict
for p in sorted(glob.glob(D + "/rd/semrush_refdomains_*.csv")):
    for d in load_semi(p, {"domain":["domain"],"backlinks_num":["backlinks_num"],
                           "as":["domain_ascore","domain_authority_score","ascore"],
                           "ip":["ip"],"country":["country"],
                           "first_seen":["first_seen"],"last_seen":["last_seen"]}):
        dom = d["domain"].strip().lower()
        if not dom: continue
        refmeta.setdefault(dom, {})
        refmeta[dom].update({"ip": d.get("ip",""), "country": d.get("country",""),
                             "sem_first": ts_to_date(d.get("first_seen","")),
                             "sem_rd_backlinks": d.get("backlinks_num","")})

# Ahrefs refdomains (tab, quoted). Header has trailing spaces on some cols.
with io.open(D + "/ahrefs_refdomains.tsv", "r", encoding="utf-8-sig") as f:
    r = csv.reader(f, delimiter="\t", quotechar='"')
    hdr = [h.strip() for h in next(r)]
    gi = {h:i for i,h in enumerate(hdr)}
    for row in r:
        if len(row) <= gi["Domain"]: continue
        dom = row[gi["Domain"]].strip().lower()
        if not dom: continue
        m = refmeta.setdefault(dom, {})
        m["ahrefs_spam"] = row[gi["Is spam"]].strip().lower()=="true" if "Is spam" in gi else False
        m["ahrefs_dr"] = row[gi["DR"]].strip() if "DR" in gi else ""
        m["ahrefs_first"] = ah_date(row[gi["First seen"]]) if "First seen" in gi else ""

ALLDOMS = set(refmeta.keys())
_sorted = sorted(ALLDOMS, key=len, reverse=True)
_regcache = {}
def reg_domain(hostname):
    h = hostname
    if h in _regcache: return _regcache[h]
    out = None
    if h in ALLDOMS: out = h
    else:
        parts = h.split(".")
        for i in range(len(parts)-1):
            cand = ".".join(parts[i:])
            if cand in ALLDOMS: out = cand; break
        if out is None:
            out = ".".join(parts[-2:]) if len(parts) >= 2 else h
    _regcache[h] = out
    return out

# ---------------- Semrush AS bulk ----------------
as_data = {}  # domain -> dict(as, backlinks, rds, follows, nofollows)
for p in sorted(glob.glob(D + "/metrics/as_*.csv")):
    with io.open(p,"r",encoding="utf-8") as f:
        r = csv.reader(f, delimiter=";"); hdr = next(r)
        def col(*names):
            for n in names:
                if n in hdr: return hdr.index(n)
            return None
        it = col("target","domain"); ia = col("authority_score","ascore","domain_ascore")
        ib = col("backlinks_num"); idd = col("domains_num"); ifo = col("follows_num"); ino=col("nofollows_num")
        for row in r:
            if not row or it is None or len(row)<=it: continue
            dom = row[it].strip().lower()
            if not dom: continue
            def gv(i):
                return row[i].strip() if (i is not None and i < len(row)) else ""
            as_data[dom] = {"as": gv(ia), "backlinks": gv(ib), "rds": gv(idd),
                            "follows": gv(ifo), "nofollows": gv(ino)}

# ---------------- Semrush domain_rank ----------------
rank_data = {}  # domain -> dict(keywords, traffic)
for p in sorted(glob.glob(D + "/metrics/rank_*.csv")):
    with io.open(p,"r",encoding="utf-8") as f:
        r = csv.reader(f, delimiter=";"); hdr=next(r)
        for row in r:
            if not row: continue
            dom = row[0].strip().lower()
            if not dom or dom=="domain": continue
            def num(i):
                try: return int(float(row[i])) if i < len(row) and row[i] not in ("","ERR") else 0
                except: return 0
            rank_data[dom] = {"keywords": num(1), "traffic": num(2)}

# ---------------- anchor typing ----------------
URL_RE = re.compile(r"^(https?://|www\.)|^[a-z0-9-]+\.(com|net|org|io|co|info|biz|us|shop|store|online|site|xyz)(/|$)", re.I)
SPAM_ANCHOR_SIG = ["backlink","guest post","guest-post","pbn","dofollow","da 50","pa 40","da50","pa40",
    "high da","higher da","dr/da/tf","da/tf","link building","buy backlinks","premium authority",
    "authority backlinks","niche edit","darksidelinks","t.me/s/","join our telegram","complete seo for",
    "search engine authority for","google boost for","search visibility","sitetosocial","skylinkseo",
    "buybacklinks","seoexpress","fully automated","automation tools","saas tools","saas integrations",
    "rank elitewrecker","boost elitewrecker","scale elitewrecker","grow elitewrecker","strengthen elitewrecker",
    "take elitewrecker.com to page one","there was a time when","doubled my leads","filled my inbox",
    "increase in sales","secured us top","increased monthly traffic","tiered link","white hat seo links",
    "white-label","press release links","high-quality backlinks","high quality dofollow","citation flow"]
OFFTOPIC_SIG = ["casino","gambling","igaming","slot","poker","betting","crypto","pharma","viagra","cialis",
    "escort","porn","adult"]
GENERIC_SET = {"visit website","website","click here","read more","view website","visit site","learn more",
    "link","here","more","visit the website","website ↗","view site","visit","official website","homepage",
    "home page","read more »","visit site »","check it out"}
BRAND_SIG = ["elite service recovery","elite towing","elitewrecker","elite service recovery & towing",
    "elite service recovery and towing"]

def norm(a): return re.sub(r"\s+"," ",(a or "").strip().lower())

def is_naked_url(a):
    al = norm(a)
    if not al: return False
    if al.startswith("http") or al.startswith("www."): return True
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}(/.*)?$", al) and " " not in al: return True
    return False

def has_geo(a):
    al = norm(a)
    return any(g.strip() in al for g in GEO_STRICT)

def is_commercial(a):
    al = norm(a)
    if is_naked_url(a): return False
    return any(s in al for s in SERVICE)

def is_spam_anchor(a):
    al = norm(a)
    return any(s in al for s in SPAM_ANCHOR_SIG)

def is_offtopic(a):
    al = norm(a)
    return any(s in al for s in OFFTOPIC_SIG)

def is_branded(a):
    al = norm(a)
    if is_naked_url(a): return False
    return any(s in al for s in BRAND_SIG)

def anchor_type(a):
    al = norm(a)
    if al == "" : return "Empty or image"
    if is_offtopic(a): return "Spam: off topic"
    if is_spam_anchor(a): return "Spam: keyword stuffed SEO sales copy"
    if is_commercial(a):
        return "Exact match commercial (geo)" if has_geo(a) else "Exact match commercial"
    if is_naked_url(a): return "Naked URL"
    if is_branded(a): return "Branded"
    if al in GENERIC_SET: return "Generic"
    return "Contextual or other"

# ---------------- spam host / title / url signals ----------------
SPAM_HOST_SIG = ["backlink","seo","pbn","dofollow","linkbuild","link-build","linkplacement","link-placement",
    "guestpost","guest-post","nicheedit","niche-edit","rankboost","rank-boost","rankpro","linkrank",
    "buybacklinks","authoritylink","dapa","da-pa","serp","outrank","indexer","trafficbot","linkfarm",
    "darkside","elitewrecker-","toplink","linkbaron","link-baron","rankforge","rank-forge"]
JUNK_TLD = {"shop","store","website","space","online","xyz","site","top","click","link","fun","cfd","sbs","rest"}
SPAM_URL_SIG = ["/link-placement","/link-building","/buy-backlink","link-placement-hub","/pbn","/seo-package",
    "/domain/","domain-list","aged-domains","/link-hub/"]
def spam_host_name(dom):
    name = dom.rsplit(".",1)[0]
    return any(s in dom for s in SPAM_HOST_SIG)
def junk_tld(dom):
    return dom.rsplit(".",1)[-1] in JUNK_TLD
def spam_title(t):
    tl = norm(t)
    return any(s in tl for s in ["backlink","pbn","buy backlinks","link building","guest post","dofollow",
        "seo authority","aged domain","premium authority","citation flow","white hat seo","tiered link"])
def spam_url(u):
    ul = (u or "").lower()
    return any(s in ul for s in SPAM_URL_SIG)

# ---------------- load + merge links ----------------
links = {}   # key -> link dict
def add_link(key, rec, tool):
    if key in links:
        if links[key]["tool"] != tool: links[key]["tool"] = "Both"
        # prefer a non-empty title/anchor
        for k in ("title","anchor"):
            if not links[key].get(k) and rec.get(k): links[key][k]=rec[k]
        if rec.get("http") and not links[key].get("http"): links[key]["http"]=rec["http"]
        return
    rec["tool"] = tool
    links[key] = rec

# Semrush backlinks: positional-tail parse (title/anchor may contain ';')
for p in sorted(glob.glob(D + "/fetch/semrush_backlinks_*.csv")):
    with io.open(p,"r",encoding="utf-8") as f:
        first = f.readline()  # header
        for line in f:
            line = line.rstrip("\n")
            if not line: continue
            line = html.unescape(line)
            fx = line.split(";")
            if len(fx) < 10: continue
            source_url = fx[0]
            tail = fx[-6:]  # nofollow, first_seen, last_seen, response_code, redirect_url, page_ascore
            middle = fx[1:-6]
            # locate target_url in middle
            tj = None
            for j,v in enumerate(middle):
                if "elitewrecker" in v.lower() and (v.lower().startswith("http") or v.lower().startswith("www")):
                    tj = j
            if tj is None:
                # fallback: assume [title, target, anchor]
                tj = 1 if len(middle)>=3 else len(middle)-1
            title = ";".join(middle[:tj])
            target_url = middle[tj] if tj < len(middle) else ""
            anchor = ";".join(middle[tj+1:]) if tj+1 <= len(middle) else ""
            nofollow = tail[0].strip().lower()=="true"
            fseen = ts_to_date(tail[1]); lseen = ts_to_date(tail[2])
            http = tail[3].strip(); redirect = tail[4].strip()
            shost = host_of(source_url); rd = reg_domain(shost)
            prop = host_of(redirect) if redirect else host_of(target_url)
            key = (canon(source_url), canon(target_url), norm(anchor))
            add_link(key, {"rd":rd, "src":source_url, "title":title, "target":target_url,
                           "prop":prop, "anchor":anchor, "nofollow":nofollow,
                           "first":fseen, "last":lseen, "http":http}, "Semrush")

# Ahrefs backlinks (tab, quoted)
with io.open(D + "/ahrefs_backlinks.tsv","r",encoding="utf-8-sig") as f:
    r = csv.reader(f, delimiter="\t", quotechar='"')
    hdr=[h.strip() for h in next(r)]; gi={h:i for i,h in enumerate(hdr)}
    def g(row,name):
        i=gi.get(name); return row[i] if (i is not None and i<len(row)) else ""
    for row in r:
        if len(row) < 5: continue
        source_url=g(row,"Referring page URL"); title=g(row,"Referring page title")
        target_url=g(row,"Target URL"); anchor=g(row,"Anchor")
        nofollow = g(row,"Nofollow").strip().lower()=="true"
        http = g(row,"Referring page HTTP code").strip()
        fseen = ah_date(g(row,"First seen")); lseen=ah_date(g(row,"Last seen"))
        rchain = g(row,"Redirect Chain URLs")
        shost=host_of(source_url); rd=reg_domain(shost)
        prop = host_of(target_url)
        key=(canon(source_url),canon(target_url),norm(anchor))
        add_link(key, {"rd":rd,"src":source_url,"title":title,"target":target_url,"prop":prop,
                       "anchor":anchor,"nofollow":nofollow,"first":fseen,"last":lseen,"http":http}, "Ahrefs")

# ---------------- aggregate per domain ----------------
dom_links = defaultdict(list)
for k,v in links.items():
    dom_links[v["rd"]].append(v)
# ensure every refdomain present
for d in ALLDOMS: dom_links.setdefault(d, [])

def is_home(prop_path):
    return prop_path in ("", "/", "")

domains = {}
for dom, ls in dom_links.items():
    meta = refmeta.get(dom, {})
    a = as_data.get(dom, {})
    rk = rank_data.get(dom, {})
    as_val = a.get("as","")
    try: as_num = float(as_val) if as_val not in ("", None) else None
    except: as_num = None
    dofollow = sum(1 for l in ls if not l["nofollow"])
    nofollow = sum(1 for l in ls if l["nofollow"])
    anchors = [l["anchor"] for l in ls]
    types = Counter(anchor_type(x) for x in anchors)
    has_spam = any(is_spam_anchor(x) or is_offtopic(x) for x in anchors)
    has_off = any(is_offtopic(x) for x in anchors)
    has_comm = any(is_commercial(x) for x in anchors)
    # deep money-page target?
    def deep(l):
        pp = path_of(l["target"]);
        if l.get("prop") and l["prop"] not in OWNED: pass
        return pp not in ("","/", "/contact","/contact/","/contact-us","/contact-us/") and (
            "/service" in pp or "/tow" in pp or "/heavy" in pp or "/recovery" in pp or "/wrecker" in pp
            or "/roadside" in pp or len(pp.strip("/").split("/"))>=2 or pp.strip("/") not in ("",))
    points_deep = any(l["target"] and path_of(l["target"]) not in ("","/") and
                      path_of(l["target"]) not in ("/contact","/contact/","/contact-us","/contact-us/")
                      for l in ls)
    deep_commercial = any((is_commercial(l["anchor"]) or True) and
                          path_of(l["target"]).startswith(("/service","/tow","/heavy","/recovery","/wrecker","/roadside","/service-area"))
                          for l in ls)
    # top anchor (by frequency, prefer dofollow)
    top_anchor = Counter(anchors).most_common(1)[0][0] if anchors else ""
    # example linking page: prefer a dofollow, http200, with a title
    ex = None
    for l in sorted(ls, key=lambda x:(x["nofollow"], x.get("http","")!="200")):
        ex = l; break
    first_seens = [l["first"] for l in ls if l["first"]] + ([meta.get("sem_first")] if meta.get("sem_first") else []) + ([meta.get("ahrefs_first")] if meta.get("ahrefs_first") else [])
    first_seen = min(first_seens) if first_seens else ""
    prop = Counter(l["prop"] for l in ls if l.get("prop")).most_common(1)
    links_point_to = prop[0][0] if prop else MONEY_SITE
    tool = "—"
    ts = set(l["tool"] for l in ls)
    tool = "Both" if ts=={"Both"} or len(ts)>1 or "Both" in ts else (list(ts)[0] if ts else "Semrush")
    domains[dom] = {
        "domain":dom, "as":as_num, "as_raw":as_val,
        "backlinks": a.get("backlinks") or str(len(ls)),
        "rds": a.get("rds",""), "traffic": rk.get("traffic",0), "keywords": rk.get("keywords",0),
        "dofollow":dofollow, "nofollow":nofollow, "nlinks":len(ls),
        "first_seen":first_seen, "top_anchor":top_anchor,
        "ex_page": ex["src"] if ex else "", "ex_title": ex["title"] if ex else "",
        "links_point_to":links_point_to, "ip":meta.get("ip",""), "country":meta.get("country",""),
        "tool":tool, "has_spam":has_spam, "has_off":has_off, "has_comm":has_comm,
        "points_deep":points_deep, "deep_commercial":deep_commercial,
        "ahrefs_spam":meta.get("ahrefs_spam",False), "types":dict(types),
        "titles":[l["title"] for l in ls],
    }

# ---------------- IP /24 network counts ----------------
net24 = Counter()
for d,info in domains.items():
    ip = info["ip"]
    if ip and ip.count(".")==3:
        net24["/".join(ip.split(".")[:3])] += 1

# ---------------- classify (verdict order, first match wins) ----------------
def title_names_client(info):
    for t in info["titles"]:
        tl = norm(t)
        if ("elite" in tl and ("tow" in tl or "wrecker" in tl or "recovery" in tl)) or "elitewrecker" in tl:
            return True
    return False

def classify(info):
    dom = info["domain"]; as_num = info["as"]
    dofollow = info["dofollow"]; nofollow = info["nofollow"]
    anchors_spam = info["has_spam"]; off = info["has_off"]; comm = info["has_comm"]
    deep = info["deep_commercial"]
    # 1 owned
    if dom in OWNED: return "Own Site"
    # 2 AS>=20 genuine
    if as_num is not None and as_num >= 20: return "Keep"
    # 3 exact-commercial AND pbn spam on same domain -> Held
    if comm and anchors_spam:
        return "Held (Nofollow, No Action)" if dofollow==0 else "Held (Pending Partner)"
    # 4 exact commercial OR deep money-page link -> Held
    if comm or deep:
        return "Held (Nofollow, No Action)" if dofollow==0 else "Held (Pending Partner)"
    # 5 press release host -> Held
    if dom in PRESS_HOSTS:
        return "Held (Nofollow, No Action)" if dofollow==0 else "Held (Pending Partner)"
    # 6 title names client without SEO sales copy -> Keep
    if title_names_client(info) and not anchors_spam:
        return "Keep"
    # 7 off-topic -> Spam
    if off:
        return "Spam (Disavow)" if dofollow>0 else "Spam (Nofollow, No Action)"
    # 8 PBN sales-copy anchor -> Spam
    if anchors_spam:
        return "Spam (Disavow)" if dofollow>0 else "Spam (Nofollow, No Action)"
    # 9 spam host name -> Spam
    if spam_host_name(dom):
        return "Spam (Disavow)" if dofollow>0 else "Spam (Nofollow, No Action)"
    # 10 spam page title / url template -> Spam
    if any(spam_title(t) for t in info["titles"]) or any(spam_url(l) for l in [info["ex_page"]]):
        return "Spam (Disavow)" if dofollow>0 else "Spam (Nofollow, No Action)"
    # 11 junk TLD + naked/empty-only anchors + low AS + points home => corroborated spam
    only_cheap = all(anchor_type(x) in ("Naked URL","Empty or image","Generic") for x in [l["anchor"] for l in dom_links[dom]]) if dom_links[dom] else False
    net = info["ip"] and net24.get("/".join(info["ip"].split(".")[:3]),0) >= 5
    if junk_tld(dom) and only_cheap and (as_num is None or as_num < 5) and (net or nofollow>0 or dofollow>0):
        return "Spam (Disavow)" if dofollow>0 else "Spam (Nofollow, No Action)"
    # 12 else Keep
    return "Keep"

for d,info in domains.items():
    info["status"] = classify(info)

# ---------------- write outputs ----------------
import os; os.makedirs(OUT, exist_ok=True)

# domains_classified.csv
with io.open(OUT+"/domains_classified.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f)
    w.writerow(["domain","status","as","backlinks","rds","traffic","keywords","dofollow","nofollow",
                "first_seen","top_anchor","example_page","example_title","links_point_to","tool","ip",
                "ahrefs_spam","points_deep","deep_commercial","has_spam","has_comm"])
    for d in sorted(domains):
        i=domains[d]
        w.writerow([d,i["status"],i["as_raw"],i["backlinks"],i["rds"],i["traffic"],i["keywords"],
                    i["dofollow"],i["nofollow"],i["first_seen"],i["top_anchor"],i["ex_page"],i["ex_title"],
                    i["links_point_to"],i["tool"],i["ip"],i["ahrefs_spam"],i["points_deep"],
                    i["deep_commercial"],i["has_spam"],i["has_comm"]])

# links_classified.csv
with io.open(OUT+"/links_classified.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f)
    w.writerow(["referring_domain","status","tool","anchor","anchor_type","link_type",
                "linking_page_url","linking_page_title","target_url"])
    for k,l in links.items():
        st = domains.get(l["rd"],{}).get("status","Keep")
        w.writerow([l["rd"],st,l["tool"],l["anchor"],anchor_type(l["anchor"]),
                    "Nofollow" if l["nofollow"] else "Dofollow",
                    l["src"],l["title"],l["target"]])

# anchor_analysis.csv (per distinct anchor)
anc = defaultdict(lambda:{"bl":0,"rds":set(),"spamrds":set(),"type":None})
for k,l in links.items():
    a=l["anchor"]; t=anchor_type(a)
    e=anc[a]; e["bl"]+=1; e["type"]=t; e["rds"].add(l["rd"])
    if domains.get(l["rd"],{}).get("status","").startswith("Spam"): e["spamrds"].add(l["rd"])
tot_bl=sum(e["bl"] for e in anc.values())
with io.open(OUT+"/anchor_analysis.csv","w",encoding="utf-8",newline="") as f:
    w=csv.writer(f); w.writerow(["anchor","type","backlinks","share","refdomains","spam_domains"])
    for a,e in sorted(anc.items(), key=lambda kv:-kv[1]["bl"]):
        w.writerow([a,e["type"],e["bl"], e["bl"]/tot_bl if tot_bl else 0, len(e["rds"]), len(e["spamrds"])])

# stats.json
statuses = Counter(i["status"] for i in domains.values())
bl_by_status = Counter()
for k,l in links.items():
    bl_by_status[domains.get(l["rd"],{}).get("status","Keep")] += 1
type_bl=Counter(); type_rd=defaultdict(set)
for k,l in links.items():
    t=anchor_type(l["anchor"]); type_bl[t]+=1; type_rd[t].add(l["rd"])
stats={"n_domains":len(domains),"n_links":len(links),
       "statuses":dict(statuses),"backlinks_by_status":dict(bl_by_status),
       "anchor_types":{t:{"bl":type_bl[t],"rd":len(type_rd[t])} for t in type_bl},
       "home_vs_deep":None}
open(OUT+"/stats.json","w").write(json.dumps(stats,indent=2))

print("domains:",len(domains)," links:",len(links))
print("statuses:",dict(statuses))
print("backlinks_by_status:",dict(bl_by_status))
print("anchor_type backlinks:",dict(type_bl))
dis=[d for d,i in domains.items() if i["status"]=="Spam (Disavow)"]
print("DISAVOW domains:",len(dis))
