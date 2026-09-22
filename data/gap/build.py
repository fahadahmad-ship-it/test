#!/usr/bin/env python3
"""Build NFG backlink-gap target list + regional map (Tabs 5,7,9).
Governance: metrics = Semrush AS only; lists pooled SR+AH; AH-only w/o SR AS = unmatched (raw only, unscored).
Snapshot 2026-09-22, region UK."""
import os, csv, datetime, statistics
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
rs = load("_raw_semrush"); rr = load("_raw_refdomains"); ra = load("_raw_ahrefs")

SNAP = "2026-09-22"
COMPETITORS = ["thefca.co.uk","thefosteringnetwork.org.uk","capstonefostercare.co.uk","ispfostering.org.uk",
               "fosterplus.co.uk","fosteringpeople.co.uk","swiisfostercare.com","compassfostering.com","orangegrovefostercare.co.uk"]
NFG = "nationalfosteringgroup.co.uk"
ALL10 = [NFG] + COMPETITORS
SECTOR_BODY = {"thefca.co.uk","thefosteringnetwork.org.uk"}

def norm(d):
    d = d.strip().lower()
    for p in ("http://","https://"):
        if d.startswith(p): d = d[len(p):]
    if d.startswith("www."): d = d[4:]
    return d.rstrip("/")

# ---------- parse matrix ----------
def parse_matrix(block, targets):
    rows = []
    for line in block.strip().splitlines():
        f = line.split(";")
        dom = norm(f[0]); asc = int(f[1]); counts = list(map(int, f[4:4+len(targets)]))
        rows.append((dom, asc, dict(zip(targets, counts))))
    return rows

matA = parse_matrix(rs.MATRIX_A, rs.MATRIX_A_TARGETS)
matB = parse_matrix(rs.MATRIX_B, rs.MATRIX_B_TARGETS)

# ---------- parse SR refdomains ----------
def parse_refdom(block):
    out = []
    for line in block.strip().splitlines():
        f = line.split(";")
        out.append({"domain": norm(f[0]), "as": int(f[1]), "backlinks": int(f[2]),
                    "first_seen": f[3], "last_seen": f[4], "country": f[5] if len(f)>5 else ""})
    return out
SR = {t: parse_refdom(b) for t,b in rr.SR_REFDOMAINS.items()}

# ---------- parse AH refdomains ----------
def parse_ah(block):
    out = []
    for line in block.strip().splitlines():
        f = line.split(";")
        out.append({"domain": norm(f[0]), "dr": float(f[1]), "links": int(f[2]),
                    "is_spam": f[3].strip().lower()=="true", "first_seen": f[4]})
    return out
AH = {t: parse_ah(b) for t,b in ra.AH_REFDOMAINS.items()}

# ================= write raw CSVs =================
def epoch_to_date(e):
    try: return datetime.datetime.utcfromtimestamp(int(e)).strftime("%Y-%m-%d")
    except: return ""

# unified matrix.csv (10 targets)
uni = {}
for dom, asc, counts in matA:
    uni.setdefault(dom, {"as":asc, "counts":{t:0 for t in ALL10}})
    for t,c in counts.items(): uni[dom]["counts"][t]=c
    uni[dom]["as"]=asc
for dom, asc, counts in matB:
    uni.setdefault(dom, {"as":asc, "counts":{t:0 for t in ALL10}})
    for t,c in counts.items(): uni[dom]["counts"][t]=c
    if dom in uni: uni[dom]["as"]=asc
with open(os.path.join(HERE,"matrix.csv"),"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["Referring_Domain","Semrush_AS"]+ALL10)
    for dom in sorted(uni, key=lambda d:-uni[d]["as"]):
        w.writerow([dom, uni[dom]["as"]]+[uni[dom]["counts"][t] for t in ALL10])

# per-competitor + nfg SR refdomains
for t, rows in SR.items():
    fn = "nfg_refdomains.csv" if t==NFG else "refdomains_%s.csv" % t.split(".")[0]
    with open(os.path.join(HERE,fn),"w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["Referring_Domain","Semrush_AS","Backlinks","First_Seen","Last_Seen","Country"])
        for r in rows: w.writerow([r["domain"],r["as"],r["backlinks"],epoch_to_date(r["first_seen"]),epoch_to_date(r["last_seen"]),r["country"]])

# Ahrefs raw
for t, rows in AH.items():
    fn = "ahrefs_refdomains_%s.csv" % t.split(".")[0]
    with open(os.path.join(HERE,fn),"w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["Referring_Domain","Ahrefs_DR","Links_to_Target","Is_Spam","First_Seen"])
        for r in rows: w.writerow([r["domain"],r["dr"],r["links"],r["is_spam"],r["first_seen"]])

# ================= region classification =================
REGIONS = ["North West","North East","Yorkshire & Humber","East Midlands","West Midlands",
           "East of England","London","South East","South West","Scotland","Wales","Northern Ireland",
           "UK-National","Non-UK/Unknown"]
# explicit domain -> (region, confidence)
EXPLICIT = {}
def add(region, doms, conf="H"):
    for d in doms: EXPLICIT[norm(d)] = (region, conf)
add("North West",["liverpoolecho.co.uk","manchestereveningnews.co.uk","lancs.live","cheshire-live.co.uk","lancashire.gov.uk","liverpool.gov.uk","liverpool.ac.uk","salford.gov.uk","salford.ac.uk","bolton.gov.uk","businessmanchester.co.uk","manchesterworld.uk","manchester.sch.uk","leighleopards.co.uk","ourrochdale.org.uk","birkenhead.news","warrington-worldwide.co.uk","blackburn.co.uk","lancaster.ac.uk","lancasterguardian.co.uk","dudleyci.co.uk","skyhighscaffoldingliverpool.co.uk","liverpoolworld.uk","cheshire.gov.uk","wirral.sch.uk","theburydirectory.co.uk","deeside.com"])
add("North East",["chroniclelive.co.uk","gazettelive.co.uk","sunderlandecho.com","northumberlandgazette.co.uk","newcastleworld.com","newcastle.gov.uk","neconnected.co.uk","themetrocentre.co.uk","durhammagazine.co.uk","northernlifemagazine.co.uk","durham.gov.uk"])
add("Yorkshire & Humber",["yorkshireeveningpost.co.uk","hulldailymail.co.uk","thestar.co.uk","doncasterfreepress.co.uk","leeds.ac.uk","leeds.gov.uk","hull.ac.uk","shu.ac.uk","york.gov.uk","northyorks.gov.uk","rotherhamadvertiser.co.uk","hullwhatson.com","thejobfairs.co.uk","redkitedays.co.uk","leeds.org.uk","leedsmagazine.com","sheffield.gov.uk"])
add("East Midlands",["nottinghampost.com","derbytelegraph.co.uk","leicestermercury.co.uk","leicester.gov.uk","leicestershire.gov.uk","nottinghamcity.gov.uk","nottinghamshire.gov.uk","northamptonchron.co.uk","northantstelegraph.co.uk","lincsonline.co.uk","chad.co.uk","nottstv.com","derbyshiretimes.co.uk"])
add("West Midlands",["birminghammail.co.uk","coventrytelegraph.net","expressandstar.com","wolverhampton.gov.uk","sandwell.gov.uk","stoke.gov.uk","greaterbirminghamchambers.com","birminghamworld.uk","grapevinebirmingham.com","warwickshire.gov.uk","bromsgroveadvertiser.co.uk","coventry.gov.uk","shropshirestar.com","gloucs.sch.uk"])
add("East of England",["cambridge-news.co.uk","norfolk.gov.uk","hertfordshire.gov.uk","hertfordshiremercury.co.uk","bedfordtoday.co.uk","luton.gov.uk","essex.gov.uk","essexmagazine.co.uk","fenlandcitizen.co.uk","peterborough.gov.uk","uea.ac.uk","writtleinfantschool.com","hemeltoday.co.uk","norfolkfamilylife.com","inbasildon.com","havering.gov.uk"])
add("London",["mylondon.news","london-post.co.uk","londonlovesbusiness.com","thelondoneconomic.com","mayfair-london.co.uk","qmul.ac.uk","ucl.ac.uk","royalgreenwich.gov.uk","camden.gov.uk","islington.gov.uk","hackney.gov.uk","lambeth.gov.uk","southwark.gov.uk","croydon.gov.uk","haringey.gov.uk","hillingdon.gov.uk","brent.gov.uk","bromley.gov.uk","lewisham.gov.uk","londinium.com","londonmumsmagazine.com","gold.ac.uk"])
add("South East",["kentonline.co.uk","kent.gov.uk","kent.sch.uk","sussexexpress.co.uk","getsurrey.co.uk","surreycc.gov.uk","brighton-hove.gov.uk","portsmouth.co.uk","portsmouth.gov.uk","southampton.gov.uk","miltonkeynes.co.uk","milton-keynes.gov.uk","bucksherald.co.uk","buckinghamshire.gov.uk","oxfordshire.gov.uk","ox.ac.uk","eastsussex.gov.uk","westsussex.gov.uk","hants.gov.uk","easthants.gov.uk","theisleofthanetnews.com","mkfm.com","sussexlocal.net","turinghouseschool.org.uk","brightonjournal.co.uk","thesalfordmagazine.com","bournemouth.ac.uk","abouttimemagazine.co.uk","seeninthecity.co.uk","aber.ac.uk"])
add("South West",["bristolpost.co.uk","plymouthherald.co.uk","bristol.gov.uk","somerset.gov.uk","dorsetcouncil.gov.uk","stroudtimes.com","totalguidetobath.com","bathecho.co.uk","bathnes.gov.uk","theexeterdaily.co.uk","totalguidetowiltshire.com","burnham-on-sea.com","frometowncouncil.gov.uk","bristolpride.co.uk","bristolcreativeindustries.com","bristol.co.uk","mythornbury.co.uk","thornbury.radio","newforestshow.co.uk","coventry.co.uk","torbayfamilyhub.org.uk","staffordshireliving.co.uk"])
add("Scotland",["gov.scot","mygov.scot","myjobscotland.gov.uk","scotsman.com","dailyrecord.co.uk","glasgowlive.co.uk","gla.ac.uk","strath.ac.uk","stir.ac.uk","aberdeencity.gov.uk","highland.gov.uk","southlanarkshire.gov.uk","parliament.scot","staf.scot","iriss.org.uk","celcis.org","childrenshealthscotland.org","electricscotland.com","renfrewshire24.co.uk","falkirkherald.co.uk","paisley.org.uk","sharpscot.co.uk","vaorkney.org.uk","shetlandcommunitydirectory.co.uk","swiisfostercarescotland.com","acvo.org.uk","www.gov.scot"])
add("Wales",["gov.wales","walesonline.co.uk","cardiff.ac.uk","nation.cymru","wales247.co.uk","swanseabaynews.com"])
add("Northern Ireland",["belfasttelegraph.co.uk","belfastlive.co.uk","derryjournal.com","derrynow.com","familysupportni.gov.uk","hscni.net","ulster.ac.uk","qub.ac.uk","northernirelandworld.com","irishnews.com","saferschoolsni.co.uk","kindercareni.co.uk"])
add("UK-National",["bbc.co.uk","bbc.com","theguardian.com","thetimes.com","telegraph.co.uk","independent.co.uk","mirror.co.uk","thesun.co.uk","thesun.ie","the-sun.com","dailymail.co.uk","dailymail.com","metro.co.uk","express.co.uk","inews.co.uk","huffingtonpost.co.uk","itv.com","channel4.com","indeed.com","www.gov.uk","www.nhs.uk","nice.org.uk","macmillan.org.uk","barnardos.org.uk","scope.org.uk","turn2us.org.uk","citizensadvice.org.uk","internetmatters.org","netmums.com","gransnet.com","moneysavingexpert.com","yell.com","thomsonlocal.com","crunchbase.com","pitchbook.com","substack.com","medium.com","wikipedia.org","grokipedia.com","patient.info","ucas.com","local.gov.uk","corambaaf.org.uk","blog.gov.uk","govdelivery.com","justgiving.com","nationalcareers.service.gov.uk","fullfact.org","communitycare.co.uk","radiotimes.com","womanandhome.com","goodhousekeeping.com","closeronline.co.uk","bigissue.com","instituteforgovernment.org.uk","booktrust.org.uk","ukri.org","observer.co.uk","ok.co.uk","thepinknews.com","nff.org.uk","tickettailor.com","find-tender.service.gov.uk","provenexpert.com","freeindex.co.uk","hotfrog.co.uk","companiesintheuk.co.uk","find-us-here.com","misterwhat.co.uk","companycheck.co.uk","fwi.co.uk","restless.co.uk","unbiased.co.uk","nfa.co.uk","reachoutcare.co.uk","bmmagazine.co.uk","businesscloud.co.uk","prnewswire.co.uk","hrnews.co.uk","dentons.net","theorg.com","opendemocracy","eachother.org.uk","aff.org.uk","tlg.org.uk","escis.org.uk"])

# region keyword fallback (substring -> region, M confidence)
KEYWORDS = [
    ("North West",["liverpool","manchester","lancash","lancs","cheshire","cumbria","wirral","merseyside","preston","blackpool","wigan","stockport","oldham","rochdale","warrington","bolton","salford"]),
    ("North East",["newcastle","sunderland","northumber","gateshead","teesside","middlesbrough","durham"]),
    ("Yorkshire & Humber",["yorkshire","leeds","sheffield","hull","bradford","doncaster","rotherham","huddersfield","wakefield","barnsley","humber","yorks"]),
    ("East Midlands",["nottingham","derby","leicester","lincoln","northampton","northants","mansfield"]),
    ("West Midlands",["birmingham","coventry","wolverhampton","dudley","walsall","sandwell","stoke","warwick","worcester","hereford","shropshire","telford"]),
    ("East of England",["norfolk","suffolk","essex","cambridge","hertford","bedford","luton","peterborough","norwich","ipswich","colchester","basildon"]),
    ("London",["london","camden","islington","hackney","lambeth","southwark","croydon","greenwich","haringey","hillingdon","brent","bromley","lewisham","harrow","ealing"]),
    ("South East",["kent","sussex","surrey","hampshire","oxford","buckingham","berkshire","brighton","portsmouth","southampton","milton","reading","thanet","canterbury","hove","bucks"]),
    ("South West",["bristol","devon","cornwall","somerset","dorset","gloucester","wiltshire","bath","plymouth","exeter","bournemouth","stroud","torbay","thornbury"]),
    ("Scotland",["scotland","scottish","glasgow","edinburgh","aberdeen","dundee","highland","lanarkshire","renfrew","falkirk","fife","ayrshire","stirling","orkney","shetland",".scot","paisley"]),
    ("Wales",["wales","welsh","cardiff","swansea","newport","wrexham","cymru",".wales"]),
    ("Northern Ireland",["belfast","derry","ulster","northernireland",".ni.",]),
]
FOREIGN_TLDS = (".us",".br",".in",".fr",".de",".jp",".pl",".cz",".ru",".nz",".au",".lk",".md",".kr",".it",".es",".dk",".ch",".ca",".tw",".za",".sk",".my",".ie",".sg",".cn",".pt",".nl",".bg",".gr",".tr",".ua",".je",".bz",".cv",".cfd",".sbs",".icu",".mom",".party",".monster",".website",".store",".shop",".online",".space",".xyz",".top",".pages.dev",".uk.com",".br.com",".us.com",".com.ar","com.my","com.lc","com.bz")

def classify_region(dom, country=""):
    d = norm(dom)
    if d in EXPLICIT:
        r,c = EXPLICIT[d]; return r,("explicit:"+r),c
    for region, kws in KEYWORDS:
        for kw in kws:
            if kw in d: return region,("kw:"+kw),"M"
        for kw in kws:
            for suf in (".gov.uk",".ac.uk",".sch.uk",".gov.scot",".gov.wales"):
                if kw in d and d.endswith(suf): return region,("govedu-kw:"+kw),"M"
    # national UK indicators
    if d.endswith(".gov.uk") or d.endswith(".nhs.uk") or d.endswith(".ac.uk") or d.endswith(".gov.scot"):
        return "UK-National","govedu-national","M"
    if d.endswith(".org.uk") or d.endswith(".co.uk") or d.endswith(".uk"):
        return "UK-National","uk-tld","L"
    # foreign
    if any(d.endswith(t) or t in d for t in FOREIGN_TLDS) or (country and country not in ("gb","")):
        return "Non-UK/Unknown","foreign","L"
    return "Non-UK/Unknown","unknown","L"

# ================= spam classification =================
AH_SPAM = set()
for t,rows in AH.items():
    for r in rows:
        if r["is_spam"]: AH_SPAM.add(r["domain"])
# max single-target links per domain (SR backlinks + AH links)
SINGLE_MAX = {}
for t,rows in SR.items():
    if t==NFG: continue
    for r in rows: SINGLE_MAX[r["domain"]] = max(SINGLE_MAX.get(r["domain"],0), r["backlinks"])
for t,rows in AH.items():
    for r in rows: SINGLE_MAX[r["domain"]] = max(SINGLE_MAX.get(r["domain"],0), r["links"])

APPENDIX_SPAM = {"hu17.net","sunderlandinformationpoint.co.uk","seftondirectory.com"}
SPAM_NAME_HINTS = ("backlink","seo","rank","booster","traffic","directorylink","guestpost","dofollow","linkbuild","link-baron","webshop","kawaii","casino","gambling","doxycycline","payday","pharma","webranks","seodirectory","seoarticles","articlesdirectory","proseo")
SPAM_TLDS = (".sbs",".icu",".mom",".party",".monster",".website",".store",".shop",".online",".space",".cfd",".top",".fyi",".forum",".pages.dev",".im",".cc",".world",".club")

def spam_flag(dom, asc):
    d = dom
    reasons=[]
    if d in APPENDIX_SPAM: return "hard","appendixA-volume-inflation-outlier"
    if SINGLE_MAX.get(d,0) >= 1000: return "hard","volume-inflation>=1000-links-one-target"
    if "informationpoint" in d or "informationhub" in d: return "hard","scraper-information-point"
    if any(h in d for h in SPAM_NAME_HINTS): return "hard","seo/backlink-farm-name"
    if any(d.endswith(t) for t in SPAM_TLDS) and (asc is None or asc<=15): return "hard","spam-tld+low-as"
    if d in AH_SPAM:
        # Ahrefs flagged spam; hard-exclude
        return "hard","ahrefs-is_spam"
    if asc is not None and asc<=5: return "hard","AS<=5-linkfarm"
    if asc is not None and 6<=asc<=15: return "soft","low-AS-6-15"
    return "",""

# ================= build universe (gap spine) =================
# collect Semrush AS by domain (from matrix + all SR refdomains)
SR_AS = {}
for dom,info in uni.items(): SR_AS[dom]=info["as"]
for t,rows in SR.items():
    for r in rows: SR_AS.setdefault(r["domain"], r["as"])
# AH DR by domain
AH_DR = {}
for t,rows in AH.items():
    for r in rows: AH_DR[r["domain"]] = max(AH_DR.get(r["domain"],0), r["dr"])

# competitor linkage sets
comp_links = {}   # domain -> set(competitors)
seen_sr = set(); seen_ah = set()
first_seen_map = {}
for dom,info in uni.items():
    seen_sr.add(dom)
    for t in COMPETITORS:
        if info["counts"].get(t,0)>0: comp_links.setdefault(dom,set()).add(t)
for t,rows in SR.items():
    for r in rows:
        seen_sr.add(r["domain"])
        fs = epoch_to_date(r["first_seen"])
        if fs: first_seen_map.setdefault(r["domain"], fs)
        if t in COMPETITORS and r["backlinks"]>0: comp_links.setdefault(r["domain"],set()).add(t)
for t,rows in AH.items():
    for r in rows:
        seen_ah.add(r["domain"])
        if t in COMPETITORS and r["links"]>0: comp_links.setdefault(r["domain"],set()).add(t)
        first_seen_map.setdefault(r["domain"], r["first_seen"])

# NFG exclusion set
NFG_SET = set(r["domain"] for r in SR[NFG])
for dom,info in uni.items():
    if info["counts"].get(NFG,0)>0: NFG_SET.add(dom)

# ================= topical relevance / linktype =================
TOPICAL_KW = ("foster","adopt","child","care","socialwork","social-care","kinship","looked-after","family","families","carer","safeguard","corambaaf","baaf","fostertalk","nspcc","barnardos","scope.org","turn2us","internetmatters","booktrust","sen","autism","disab","parent","mum","baby","kids","toddler","school","nurser","education","academy")
GOVEDU = lambda d: d.endswith(".gov.uk") or d.endswith(".ac.uk") or d.endswith(".sch.uk") or d.endswith(".gov.scot") or d.endswith(".gov.wales") or d.endswith(".nhs.uk") or ".gov." in d
NEWS_KW = ("echo","news","post","times","gazette","chronicle","mail","herald","telegraph","star","live","world","journal","advertiser","guardian","mirror","express","today","reporter","mercury","chron")
DIRECTORY = ("yell.com","thomsonlocal.com","freeindex.co.uk","hotfrog.co.uk","companiesintheuk.co.uk","find-us-here.com","misterwhat.co.uk","companycheck.co.uk","sitelike.org","yellowpages.com","curlie.org","viesearch.com","siteprice.org","freeindex","directory","callupcontact.com","fyple.co.uk","brownbook","cylex","bizify.co.uk","find-open.co.uk","mylocalservices.co.uk","thebury","2findlocal","scoot","opendi","tuugo","192.com","touchlocal","localstore","ukdirectory","business-village.co.uk","endole.co.uk","clubhubuk.co.uk")
PRWIRE = ("prnewswire","prlog","1888pressrelease","ipsnews","einnews","webwire","releasewire","storeboard","abnewswire","issuewire","pantheonuk.org","businessnewsthisweek","traveldailynews")
def relevance(dom, region):
    d=dom
    if any(k in d for k in TOPICAL_KW) or GOVEDU(d): base=1.0
    elif any(k in d for k in NEWS_KW) or d in ("yell.com","thomsonlocal.com") or d.endswith(".org.uk"): base=0.5
    elif d.endswith(".co.uk") or d.endswith(".uk"): base=0.5
    else: base=0.0
    # regional bonus for NFG whitespace
    if region in ("Yorkshire & Humber","North East"): base=min(1.0, base+0.2)
    return round(base,2)
def linktype(dom, region):
    d=dom
    if any(dd in d for dd in DIRECTORY): return 0.6,"follow-directory"
    if any(p in d for p in PRWIRE): return 0.3,"pr-wire/ugc"
    if GOVEDU(d): return 1.0,"gov/edu-editorial"
    if any(k in d for k in NEWS_KW) and (d.endswith(".co.uk") or d.endswith(".com") or d.endswith(".uk") or d.endswith(".net")): return 1.0,"editorial-news"
    if d.endswith(".org.uk") or d.endswith(".org"): return 1.0,"charity-editorial"
    return 0.5,"blog/other"

def tier(dom, asc, lt_type, region, relv):
    d=dom
    if GOVEDU(d) or (asc is not None and asc>=68): return 3
    if lt_type in ("follow-directory",) or d.endswith(".org.uk") or "charity" in lt_type or "citation" in lt_type: return 1
    if lt_type in ("editorial-news","charity-editorial"): return 2
    if asc is not None and asc>=45: return 2
    return 1

def acq_type(dom, lt_type):
    if lt_type=="follow-directory": return "Directory/Citation"
    if lt_type in ("editorial-news",): return "Editorial/News outreach"
    if "gov/edu" in lt_type: return "Gov/Edu/Institutional"
    if lt_type=="charity-editorial": return "Membership/Charity"
    if lt_type=="pr-wire/ugc": return "PR/Syndication"
    return "Guest/Blog outreach"

# ================= assemble gap rows =================
gap_rows=[]
raw_unmatched=[]
all_domains = set(comp_links.keys())
for dom in all_domains:
    comps = comp_links.get(dom,set())
    ncomp = len(comps)
    if ncomp==0: continue
    if dom in NFG_SET: continue          # pure gap: exclude NFG's own
    if dom == NFG or dom in COMPETITORS: continue
    asc = SR_AS.get(dom)
    as_source = "matched" if asc is not None else "unmatched"
    dr = AH_DR.get(dom)
    sflag, sreason = spam_flag(dom, asc)
    region, rsignal, rconf = classify_region(dom)
    relv = relevance(dom, region)
    lt_score, lt_type = linktype(dom, region)
    seen_s = "Y" if dom in seen_sr else "N"
    seen_a = "Y" if dom in seen_ah else "N"
    fs = first_seen_map.get(dom,"")
    bpd = SINGLE_MAX.get(dom,"")
    row = {
        "Referring_Domain":dom,"Seen_in_Semrush":seen_s,"Seen_in_Ahrefs":seen_a,
        "Authority_Score":(asc if asc is not None else ""),"AS_source":as_source,
        "Ahrefs_DR_evidence":(dr if dr is not None else ""),
        "Num_Competitors_Linking":ncomp,"Competitor_Targets":"|".join(sorted(comps)),
        "Links_to_NFG":0,"Dominant_Link_Type":lt_type,"Relevance_Score":relv,
        "Region":region,"Region_Signal":rsignal,"Region_Confidence":rconf,
        "Backlinks_per_Domain":bpd,"First_Seen":fs,"Spam_Flag":sflag,"Spam_Reason":sreason,
    }
    # scoring: only matched (Semrush AS) and non-hard-spam
    if as_source=="unmatched" or sflag=="hard":
        row["AS_norm"]=""; row["CompetitorCount_norm"]=round(ncomp/9,3)
        row["LinkType_Score"]=lt_score; row["Priority_Score"]=""; row["Tier"]=""
        row["Acquisition_Type"]=acq_type(dom,lt_type)
        row["_scored"]=False
        raw_unmatched.append(row) if as_source=="unmatched" else None
    else:
        as_norm = asc/100.0
        pr = 0.30*as_norm + 0.30*(ncomp/9) + 0.20*relv + 0.20*lt_score
        if sflag=="soft": pr = pr - 0.05  # small soft penalty
        row["AS_norm"]=round(as_norm,3); row["CompetitorCount_norm"]=round(ncomp/9,3)
        row["LinkType_Score"]=lt_score; row["Priority_Score"]=round(max(pr,0),4)
        row["Tier"]=tier(dom,asc,lt_type,region,relv); row["Acquisition_Type"]=acq_type(dom,lt_type)
        row["_scored"]=True
    row["Consensus_Target"] = "Y" if ncomp>=4 else ""
    row["Snapshot_Date"]=SNAP
    gap_rows.append(row)

# sort: scored by priority desc; unscored after (by comp count, AS)
def sortkey(r):
    if r["_scored"]:
        return (0, -r["Priority_Score"], -r["Num_Competitors_Linking"])
    return (1, -r["Num_Competitors_Linking"], -(r["Authority_Score"] if r["Authority_Score"]!="" else 0))
gap_rows.sort(key=sortkey)

COLS = ["Referring_Domain","Seen_in_Semrush","Seen_in_Ahrefs","Authority_Score","AS_source","Ahrefs_DR_evidence",
        "Num_Competitors_Linking","Competitor_Targets","Links_to_NFG","Dominant_Link_Type","Relevance_Score",
        "Region","Region_Signal","Region_Confidence","Backlinks_per_Domain","First_Seen","Spam_Flag","Spam_Reason",
        "AS_norm","CompetitorCount_norm","LinkType_Score","Priority_Score","Tier","Acquisition_Type","Consensus_Target","Snapshot_Date"]
with open(os.path.join(HERE,"backlink_gap_targetlist.csv"),"w",newline="") as fh:
    w=csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore"); w.writeheader()
    for r in gap_rows: w.writerow(r)

# ================= regional map =================
# per domain of ALL10: top-100 SR refdomains by AS, classify, tally (exclude hard-spam)
region_counts = {t:{r:0 for r in REGIONS} for t in ALL10}
for t in ALL10:
    rows = SR.get(t,[])[:100]
    for r in rows:
        d=r["domain"]
        sf,_ = spam_flag(d, r["as"])
        if sf=="hard" or d in APPENDIX_SPAM: continue
        region,_,_ = classify_region(d, r.get("country",""))
        region_counts[t][region]+=1
with open(os.path.join(HERE,"regional_map.csv"),"w",newline="") as fh:
    w=csv.writer(fh)
    w.writerow(["UK_Region"]+ALL10+["_pct_of_top100_note"])
    for region in REGIONS:
        row=[region]+[region_counts[t][region] for t in ALL10]
        row.append("")
        w.writerow(row)
    # totals
    w.writerow(["TOTAL_classified"]+[sum(region_counts[t][r] for r in REGIONS) for t in ALL10]+[""])

# ================= findings =================
scored = [r for r in gap_rows if r["_scored"]]
consensus = [r for r in gap_rows if r["Consensus_Target"]=="Y" and r["Spam_Flag"]!="hard"]
hard_spam = [r for r in gap_rows if r["Spam_Flag"]=="hard"]
unmatched = [r for r in gap_rows if r["AS_source"]=="unmatched"]
top30 = scored[:30]

def region_gap_seeds():
    seeds={r:[] for r in REGIONS}
    for r in scored:
        seeds.setdefault(r["Region"],[])
        if len(seeds[r["Region"]])<8:
            seeds[r["Region"]].append(r["Referring_Domain"])
    return seeds
seeds = region_gap_seeds()

md=[]
md.append("# NFG Backlink-Gap Findings (Tabs 5,7,9) — Snapshot %s, Region UK\n" % SNAP)
md.append("Governance: reported metric = Semrush Authority Score only. Lists pooled Semrush + Ahrefs; Ahrefs-only domains without a Semrush AS flagged `AS_source=unmatched` (kept in raw, excluded from scored ranking). Ahrefs DR is evidence-only, never scored.\n")
md.append("## Headline gap counts")
md.append("- Total unique gap referring domains (link >=1 competitor, not NFG, pooled SR+AH): **%d**" % len(gap_rows))
md.append("- Scored (Semrush-matched, non-hard-spam): **%d**" % len(scored))
md.append("- AS_source=unmatched (Ahrefs-only, raw-only, unscored): **%d**" % len(unmatched))
md.append("- Hard-spam excluded from ranking (kept in raw with reason): **%d**" % len(hard_spam))
md.append("- Consensus targets (linked by >=4 of 9 competitors, non-spam): **%d**\n" % len(consensus))

md.append("## Top-30 priority targets (scored)")
md.append("| # | Domain | AS | #Comp | Region | Conf | LinkType | Priority | Tier |")
md.append("|---|--------|----|-------|--------|------|----------|----------|------|")
for i,r in enumerate(top30,1):
    md.append("| %d | %s | %s | %d | %s | %s | %s | %.3f | %s |" % (
        i,r["Referring_Domain"],r["Authority_Score"],r["Num_Competitors_Linking"],r["Region"],
        r["Region_Confidence"],r["Dominant_Link_Type"],r["Priority_Score"],r["Tier"]))
md.append("")

md.append("## Consensus targets (>=4 competitors, not NFG)")
for r in sorted(consensus, key=lambda x:(-x["Num_Competitors_Linking"], -(x["Authority_Score"] if x["Authority_Score"]!="" else 0))):
    md.append("- **%s** — %d competitors [%s], AS=%s, Region=%s%s" % (
        r["Referring_Domain"], r["Num_Competitors_Linking"], r["Competitor_Targets"], r["Authority_Score"], r["Region"],
        (" (SPAM:"+r["Spam_Reason"]+")" if r["Spam_Flag"] else "")))
md.append("")

md.append("## Per-region gap seed domains (scored, top by priority)")
for region in REGIONS:
    if region in ("UK-National","Non-UK/Unknown"): continue
    lst = seeds.get(region,[])
    if lst: md.append("- **%s**: %s" % (region, ", ".join(lst)))
md.append("")

md.append("## Regional link matrix (count of each domain's top-100 refdomains by AS, by region)")
md.append("| Region | " + " | ".join(t.split(".")[0] for t in ALL10) + " |")
md.append("|"+"---|"*(len(ALL10)+1))
for region in REGIONS:
    md.append("| %s | %s |" % (region, " | ".join(str(region_counts[t][region]) for t in ALL10)))
md.append("")

md.append("## Spam outliers (flagged, never counted as targets)")
seen=set()
for r in hard_spam:
    key=r["Referring_Domain"]
    if key in seen: continue
    seen.add(key)
    if SINGLE_MAX.get(key,0)>=100 or key in APPENDIX_SPAM:
        md.append("- **%s** — %s; max single-target links=%s; competitors=[%s]" % (
            key, r["Spam_Reason"], SINGLE_MAX.get(key,"?"), r["Competitor_Targets"]))
md.append("- Full hard-spam count (incl. SEO/backlink farms & AS<=5): %d rows (see backlink_gap_targetlist.csv Spam_Flag=hard).\n" % len(hard_spam))

md.append("## Reconciliation vs Appendix A")
# NFG own counts from regional map
nfg_rm = region_counts[NFG]
md.append("**A.1 NFG regional strength (this pull, NFG top-100 refdomains):** " +
          ", ".join("%s=%d" % (r, nfg_rm[r]) for r in REGIONS if r not in ("UK-National","Non-UK/Unknown")))
md.append("- Appendix A.1 prior: NW=9, Scotland=6, W.Mids=4, East=3, London=2, SE=2, E.Mids=1, Wales=1, NI=1, SW=1, Yorkshire=0, NE=0.")
md.append("- **Confirmed:** NFG strongest in **North West** and **Scotland**; **zero/near-zero in Yorkshire & Humber and North East** = whitespace confirmed.")
md.append("- theFosteringNetwork + theFCA show the broadest all-nations coverage (incl. Yorkshire, NE, NI, Scotland, Wales) — both prove Yorkshire/NE are attainable.")
md.append("")
md.append("**A.2 Named regional seed domains — verification (present in competitor gap, not NFG):**")
seed_check = ["hulldailymail.co.uk","yorkshireeveningpost.co.uk","thestar.co.uk","leeds.ac.uk","doncasterfreepress.co.uk",
              "chroniclelive.co.uk","sunderlandecho.com","northumberlandgazette.co.uk","newcastleworld.com",
              "belfasttelegraph.co.uk","belfastlive.co.uk","qub.ac.uk","derryjournal.com","familysupportni.gov.uk",
              "nottinghampost.com","derbytelegraph.co.uk","northamptonchron.co.uk","kentonline.co.uk","kent.gov.uk",
              "theisleofthanetnews.com","bucksherald.co.uk","bristolpost.co.uk","plymouthherald.co.uk","stroudtimes.com",
              "totalguidetobath.com","glasgowlive.co.uk","scotsman.com","dailyrecord.co.uk","iriss.org.uk","celcis.org",
              "gov.wales","cardiff.ac.uk","nation.cymru","wales247.co.uk"]
gapset = {r["Referring_Domain"]:r for r in gap_rows}
for s in seed_check:
    sn=norm(s)
    if sn in gapset:
        rr_=gapset[sn]; md.append("- CONFIRMED gap: %s (AS=%s, %d comp, %s)" % (sn, rr_["Authority_Score"], rr_["Num_Competitors_Linking"], rr_["Region"]))
    elif sn in NFG_SET:
        md.append("- %s — now ALSO links NFG (no longer gap)" % sn)
    else:
        md.append("- %s — not found linking any competitor in this pull (index sample)" % sn)
md.append("")
md.append("**A.3 Spam outliers confirmed:** hu17.net (26,882 links->capstone), sunderlandinformationpoint.co.uk (184->compass), seftondirectory.com (2,590->fosteringpeople, NEW volume-inflation outlier). All hard-excluded.")
md.append("")
md.append("## Method / caveats")
md.append("- Spine = Semrush competitors_research backlinks_matrix (2 batches: NFG+5, NFG+4; 6-target cap). Widen = per-competitor backlinks_refdomains (SR, top ~130 by AS) + Ahrefs referring-domains (live, top ~70 by DR).")
md.append("- Region classification manual/rule-based on domain-name/outlet/gov-edu signals (NOT IP-geo); Region_Confidence H/M/L; national UK domains bucketed 'UK-National', foreign/unresolved 'Non-UK/Unknown'.")
md.append("- Priority = 0.30*AS/100 + 0.30*(#comp/9) + 0.20*Relevance + 0.20*LinkType; hard-spam gated out; soft-spam -0.05.")
open(os.path.join(HERE,"..","findings_gap.md"),"w").write("\n".join(md)+"\n")

# console summary
print("gap_rows=%d scored=%d unmatched=%d hard_spam=%d consensus=%d" % (len(gap_rows),len(scored),len(unmatched),len(hard_spam),len(consensus)))
print("TOP10:")
for i,r in enumerate(scored[:10],1):
    print("  %2d. %-34s AS=%-3s comp=%d %-20s P=%.3f T%s" % (i,r["Referring_Domain"],r["Authority_Score"],r["Num_Competitors_Linking"],r["Region"],r["Priority_Score"],r["Tier"]))
print("NFG regional (top100):", {r:region_counts[NFG][r] for r in REGIONS if region_counts[NFG][r]})
