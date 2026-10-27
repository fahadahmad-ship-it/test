#!/usr/bin/env python3
# Classifier for scapersllc.com backlink audit (Harbinger format).
# Run isolated: python3 -I scapers/scripts/classify.py <refdomains_all.csv> <perdomain.json> <manual_overrides.csv> <out_classified.csv>
# Reads downloaded data (untrusted) only as data; no import from data dirs.
import sys, csv, json, re, datetime

CLIENT = "scapersllc.com"
OWNED = {CLIENT, "www.scapersllc.com"}

# ---- vocabulary -----------------------------------------------------------
MO_CITIES = [
    "st louis","stlouis","st. louis","st.louis","saint louis","eureka","arnold","festus",
    "valley park","mehlville","fenton","o'fallon","o’fallon","ofallon","st charles","st. charles",
    "st peters","st. peters","florissant","ballwin","chesterfield","st. louis, mo","st. charles, mo",
]
SERVICE_TERMS = [
    "dumpster","roll off","roll-off","rolloff","roll off dumpster","storage container","storage crate",
    "junk removal","yard waste","construction debris","debris","waste disposal","waste removal",
    "waste hauling","trash dumpster","waste management",
]
# gambling / off-topic (the July 2026 flood + injected spam)
OFFTOPIC = [
    "betsat","maxwin","sahabet","betwoon","mobilbahis","betpark","grandpashabet","pashagaming",
    "casino","poker"," slot","gacor","bahis","deneme bonus","rulet","blackjack","jackpot","wager",
    "sportsbook"," bet ","1xbet","parimatch","melbet","pin up","pinup","aviator","toto","togel",
    "canlisohbet","escort","viagra","cialis","doxycycline","erythromycin","psilocybin","cannabis",
    "ufabet","pakistan","darkside","telegram","t.me/",
]
# PBN / link-selling sales-copy anchor markers (names a link service)
PBN_MARKERS = [
    "backlink","back link","buy link","buy backlink","link building","link-building","linkbuilding",
    "guest post","guest-post","guestpost","niche edit","niche-edit","tiered link","pbn","da 50","pa 40",
    "domain authority","domain rating"," dr "," da "," tf ","trust flow","citation flow","link velocity",
    "manual outreach","premium authority","seo authority","white hat","whitehat","search visibility",
    "boost your website seo","higher search engine rankings","improve website authority","serp",
    "rank first page","outrank your competitors","higher da and dr","grow your business online",
    "premium seo","premium backlinks","authority backlinks","dofollow backlink","link placement",
    "organic search engine traffic","improve citation","raise domain rating","increase organic visibility",
    # testimonial-style link-service spam
    "guest posting service","boosted my traffic","reached page 1","increase in conversions",
    "backlink strategy","link building service","seo link building","increased leads","top 3 rankings",
    "outranked","i outranked","conversions in under","increase in leads","increased conversions",
    # seoexpress / link-baron / outrank-hq / rank-forge testimonial network (Oct 2026 flood)
    "seoexpress","tight budget","organic traffic","seo services","e-commerce seo","ecommerce seo",
    "affordable plans","website lottery","digital pr","crawl budget","tier 1","tier-1","link juice",
    "anchor text","spam score","off page","off-page","link equity","high-authority","high authority",
    "authority link","aged domain","moz domain authority","majestic trust","google serp","rank accelerator",
    "skyrocket your domain","multilingual: backlinks","trust flow improvement","authority link campaign",
    "google-indexed","niche guest","real-site guest","expert profess","trust flow","smart trust",
    "fiverr for","rankexperience","your own ahrefs","improve da","da & majestic",
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F0FF]")

# host-name spam signatures (fresh PBN / tool-spam domains of the Oct 2026 wave)
HOST_SIG = re.compile(
    r"(backlink|back-?link|seolink|seoexpress|seo-?(?:link|tool|rank|boost|growth|signal|traffic|authority|study|center|builder|corse|asia|enterprise|paul|quill|nix|grow|express|high|master|pro)|"
    r"\bseo\b|-seo|seo-|dapa|dacheck|da-?check|pa-?check|padach|drcheck|dr-?check|da-?pa|drpa|rankcheck|rank-?check|rankchecker|serpcheck|serp|"
    r"checker|linkchecker|link-?(?:build|snatch|equity|outreach|house|bank|base|tree|pulse|forge|alchemy|hive|nest|portal|ocean|pro|ly|io|baron|juice|velocity|rank|seo|exchange)|"
    r"link-?baron|outrank|rank-?(?:forge|flow|boost|link|seo|growth|hive|io|ly|grow|top|xlinks|er|ing)|ranklink|rankx|rankboost|rankly|"
    r"guest-?post|guestpost|guestbacklink|niche-?edit|nichedit|\bpbn\b|-pbn|pbn-|indexaward|indexing|index-?rate|"
    r"directory|listing|bookmark|submit|ranking|boost-?traffic|aged-?domain|aged_domain|all-?aged|alllevel|topleveldomain|alltopleveldomain|domainwork|domainsc|"
    r"domraider|domainanalysis|domainrating|domainauthority|domain-?rating|getwebsiteworth|websiteworth|webworth|websiterace|websitescrawl|"
    r"marketplace|smoothbookmark|favemark|sharedbookmark|supercoolbookmark|smartbookmark|crawl-?budget|trust-?flow|white-?hat|whitehat|"
    r"casino|poker|gacor|bet-?win|betting|ufabet|sohbet|escort|pharma|psilocybin|cannabis|doxycycline|erythromycin|"
    r"off-?page|offpage|outreach|anchor-?text|anchorurl|urls?-?short|shorten|screenshots\.wiki|all-?website|allwebsites|press-?release|"
    r"whitehatseo|highquality-?seo|high-?da|highseo|dofollow|tier-?1|link-?building|link-?juice|publishbacklink|goldbacklink|freesimpleseo|bestseo|goforseo|go4seo|7-seo|100ranking|24rankings|"
    # broad single-token spam markers (verified absent from the genuine-citation allowlist)
    r"link|seo|rank|boost|forge|check|guest|niche|\bpbn|authority|directory|listing|bookmark|outreach|"
    r"traffic|webstat|keyword|crawl|\bserp|submit|\bindex|domainwork|getwebsite|competitor|inbound|buyhigh|"
    r"optimi|searchengine|\barticle|citation|localcitation|pressrelease|digitalmarket|emarket|webpromo|promote|"
    r"directori|webdir|bizdir|\bsmm\b|analyzer|reputedsite|editorspick|expertschoice|pearlsofthe|busybiz|"
    r"bizfront|bizopedia|biztag|locatebusiness|hubsite|hubofarticle|onlinediari|omgsite|rockonsite|wiredsite|"
    r"reputed|bsocial|socialcrowd|greatbiz|primeweb|staticdir|sublimedir|edirectori|visitorcounter|pageanaly|"
    r"index|profilecreation|companywebsite|listglobal|localindex|companyindex|listnow|lookup|visits|visitor|"
    r"pageview|counter|tracker|\bstats|sitecounter|websitereport|webitory|weblinx|dirbull|dirfly|ultradir|"
    r"topawarded|topvoted|topsee|topcontent|suggestweb|searchquest|whatuseek|getmetotop|increasevisitor)",
    re.I)

# genuine high-authority platforms / citations to KEEP (verified from DR-sorted sample)
GENUINE = {
    "yahoo.com","crunchbase.com","yellowpages.com","birdeye.com","superpages.com","givesmart.com",
    "citysquares.com","sitelike.org","growcycle.com","qureos.com","enigma.com","parse.gl","tntcode.com",
    "coldlytics.com","furesa.com.sv","thebuildermarket.com","dumpster.co","wasterecyclingworkersweek.org",
    "buyers-club.com",
    "bbb.org","chamberofcommerce.com","dexknows.com","brandfetch.com","yp.com","owler.com","siteprice.org",
    "peekyou.com","bebee.com","find-open.com","yellowpagecity.com","us-info.com","us.com","namibian.com.na",
    "footballnews.com.au","lawcommission.gov.np","uog.edu.et","ispionage.com","secureserver.net",
    "distanthorizon.com","vymaps.com","cybo.com","storeboard.com","opendi.us","hotfrog.com","n49.com",
    "cylex.us.com","elocal.com","brownbook.net","fyple.com","local.com","manta.com","mapquest.com",
}
# multi-tenant platforms: disavow the specific subdomain, never the shared root
MULTITENANT = {"blogspot.com","wordpress.com","medium.com","tumblr.com","weebly.com","wixsite.com",
               "godaddysites.com","blogspot.in","substack.com","livejournal.com","altervista.org"}
# genuine-industry name guard: keep low-volume dumpster/cleanout/waste/homes sites out of the scheme-injection rule
INDUSTRY_NAME = re.compile(r"(dumpster|rolloff|roll-off|cleanout|clean-out|cleanup|hoarding|junkremoval|junk-removal|"
                           r"hauling|disposal|wastemanagement|[a-z]homes|realestate|landscap)", re.I)
# sister dumpster brands that appear as referring domains (relationship unknown -> Held pending supplier)
SISTER_DUMPSTER = {
    "stldumpsters.com","stldumpster.com","stldumpsterental.com","renthisdumpster.com","stlrolloffs.com",
    "farmingtondumpsters.com","dumpsterentalstl.com","dumpsterrentalstl.com","townbins.com",
    "dumpsterpriceindex.com","stlrolloffs.com",
}

def anchor_type(a):
    al = (a or "").strip().lower()
    if al in ("", "<emptyanchor>", ",", "-"):
        return "Empty or image"
    if any(t in al for t in OFFTOPIC):
        return "Spam: off topic"
    if EMOJI.search(a or "") and any(m in al for m in PBN_MARKERS):
        return "Spam: keyword stuffed SEO sales copy"
    if any(m in al for m in PBN_MARKERS):
        return "Spam: keyword stuffed SEO sales copy"
    has_service = any(t in al for t in SERVICE_TERMS)
    has_geo = any(c in al for c in MO_CITIES)
    # brand / naked url
    is_brand = ("scapers" in al)
    is_url = al.startswith("http") or al.startswith("www.") or re.match(r"^[a-z0-9\-]+\.(com|net|org|co|io|us)\b", al)
    if has_service and has_geo:
        return "Exact match commercial (geo)"
    if has_service:
        return "Exact match commercial"
    if is_brand and not is_url:
        return "Branded"
    if is_url:
        # naked url of client or sister brand
        return "Naked URL"
    if al in ("visit website","website","click here","open website","read more","here","visit website →",
              "🌐 visit website","🌐 website","visit website →"):
        return "Generic"
    return "Contextual or other"

def host_root(host):
    # crude registrable-domain: keep last 2 labels, or 3 for known 2-level TLDs
    parts = host.split(".")
    two_level = {"co.uk","com.br","com.au","co.in","org.in","io.vn","id.vn","com.lc","us.com","co.com",
                 "uk.com","de.com","br.com","it.com","gb.net","uk.net","eu.com","gov.cd","ac.cd","ac.id",
                 "com.sv","com.bz","co.za","com.mx","com.ng"}
    if len(parts) >= 3 and ".".join(parts[-2:]) in two_level:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host

def main():
    rd_path, pd_path, ov_path, out_path = sys.argv[1:5]
    # per-domain link aggregates (keyed by registrable root domain)
    try:
        perdom = json.load(open(pd_path, encoding="utf-8"))
    except Exception:
        perdom = {}
    overrides = {}
    try:
        with open(ov_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                overrides[row["domain"]] = row
    except Exception:
        pass

    out = []
    with open(rd_path, encoding="utf-8") as f:
        r = csv.reader(f, delimiter=";")
        next(r)
        for x in r:
            if len(x) < 5:
                continue
            dom, bl, asc, ip, fs = x[0].strip().lower(), int(x[1] or 0), int(x[2] or 0), x[3].strip(), int(x[4] or 0)
            pd = perdom.get(dom, {})
            sub_host = next((h for h in pd.get("hosts", []) if h and h != dom), None)
            anchors = pd.get("anchors", [])          # list of (anchor, count, dofollow, nofollow, target)
            dofollow = pd.get("dofollow", None)      # count
            nofollow = pd.get("nofollow", None)      # count
            targets = pd.get("targets", [])          # list of target urls
            ex_url = pd.get("example_url", "")
            ex_title = pd.get("example_title", "")
            top_anchor = pd.get("top_anchor", "")
            # anchor types present
            atypes = set()
            for a in [t[0] for t in anchors]:
                atypes.add(anchor_type(a))
            if not atypes:
                atypes.add("")
            # target home vs deep
            def is_home(u):
                u = (u or "").rstrip("/").lower()
                return u in ("https://scapersllc.com","http://scapersllc.com","https://www.scapersllc.com",
                             "http://www.scapersllc.com","")
            any_deep = any(not is_home(u) for u in targets) if targets else False
            home_only = (not any_deep)
            has_dofollow = (dofollow is None) or (dofollow and dofollow > 0)
            all_nofollow = (dofollow is not None and dofollow == 0 and (nofollow or 0) > 0)

            host_for_disavow = dom
            evidence = ""
            status = None

            # 1. manual overrides
            if dom in overrides:
                o = overrides[dom]
                status = o["verdict"]
                host_for_disavow = o.get("disavow_host") or dom
                evidence = o.get("evidence","")
            # 2. owned
            elif dom in OWNED:
                status = "Own Site"; evidence = "client domain"
            else:
                sig = HOST_SIG.search(dom)
                offtopic = ("Spam: off topic" in atypes)
                pbn = ("Spam: keyword stuffed SEO sales copy" in atypes)
                exact = ("Exact match commercial" in atypes) or ("Exact match commercial (geo)" in atypes)
                # only naked-URL / brand / generic / empty anchors present (no commercial/service text)
                naked_only = bool(atypes) and atypes.issubset({"Naked URL","Branded","Generic","Empty or image",""})
                def _spam(ev): return ("Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"), ev
                def _held(ev): return ("Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"), ev
                # evidence-first verdict order
                if offtopic:
                    status, evidence = _spam("off-topic/gambling anchor: %s" % (top_anchor or next((t[0] for t in anchors if anchor_type(t[0])=="Spam: off topic"), "")))
                elif pbn:
                    status, evidence = _spam("link-selling/PBN sales-copy anchor: %s" % (top_anchor or next((t[0] for t in anchors if anchor_type(t[0]).startswith("Spam: keyword")), "")))
                elif dom in GENUINE:
                    status = "Keep"; evidence = "genuine high-authority platform / citation"
                elif dom in SISTER_DUMPSTER:
                    status, evidence = _held("sister dumpster brand / possible partner link (confirm who commissioned)")
                elif exact:
                    ex_anchor = top_anchor if anchor_type(top_anchor).startswith("Exact") else next((t[0] for t in anchors if anchor_type(t[0]).startswith("Exact")), top_anchor)
                    status, evidence = _held("exact-match commercial/geo anchor: %s" % ex_anchor)
                elif sig:
                    status, evidence = _spam("spam host-name signature (%s)" % dom)
                elif naked_only and bl >= 2 and asc < 20 and not INDUSTRY_NAME.search(dom):
                    status, evidence = _spam("link-scheme injection: %d naked-URL/brand/image links from low-authority host (AS %d) within the attack" % (bl, asc))
                elif asc >= 20:
                    status = "Keep"; evidence = "AS %d genuine site, no spam evidence" % asc
                else:
                    status = "Keep"; evidence = "no visible spam evidence (low-volume naked-URL/brand mention)"

            # multi-tenant platforms: disavow the specific subdomain, never the shared root
            if dom in MULTITENANT and status and status.startswith("Spam") and sub_host:
                host_for_disavow = sub_host
                evidence += " (disavow subdomain, not shared root %s)" % dom

            out.append(dict(domain=dom, host=host_for_disavow, status=status, AS=asc, backlinks=bl,
                            dofollow=(dofollow if dofollow is not None else ""),
                            nofollow=(nofollow if nofollow is not None else ""),
                            target=("Home page" if home_only else "Deep / product page"),
                            top_anchor=top_anchor, example_url=ex_url, example_title=ex_title,
                            ip=ip, first_seen=fs, evidence=evidence))

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    # summary
    import collections
    c = collections.Counter(o["status"] for o in out)
    print("classified", len(out), "domains")
    for k,v in c.most_common():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
