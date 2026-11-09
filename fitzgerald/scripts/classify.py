"""
classify.py - classify every referring domain for the Fitzgerald Plumbing audit.

Reads  data/processed/refdomains.json + links.jsonl  (from load.py)
Writes data/processed/domains.json + links_enriched.jsonl

Design notes:
  * anchor_type() reflects the ANCHOR TEXT ONLY (used for Tabs 3/4/5 + the anchor
    profile). Page titles/URLs/host are DOMAIN-level evidence, handled separately.
  * Verdict order follows the playbook (Section 6), first match wins, with the
    core principle: an exact-match commercial anchor (the clearest commissioned
    signal) sends a domain to HELD and takes precedence over weak spam signals
    (a 'directory' host token, off-topic content elsewhere on the host). Only
    spam evidence on the client's OWN links (sales-copy anchor, marketplace/SEO
    page title, spam URL, off-topic anchor) sends a domain to SPAM.
  * Nothing is disavowed without visible evidence. When in doubt -> Held, not disavow.
"""
import os, json, re, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "data", "processed")

MONEY = "fitzgeraldplumbing.com"
# owned/redirect properties detected from the Semrush redirect_url column
OWN_DOMAINS = {MONEY, "fitzgeraldandsonsplumbing.com", "fitzplumb.com"}
BRAND_SUBSTR = ["fitzgerald", "fitzplumb", "fitzgeraldandsons", "fitzgerald-and-sons",
                "fitzgerald and sons", "fitzgerald & sons", "fitzgerald sons"]

SERVICE_TERMS = [
    "plumber", "plumbers", "plumbing", "plumbing services", "plumbing service",
    "plumbing company", "plumbing companies", "plumbing contractor", "plumbing contractors",
    "plumbing construction", "construction plumbing", "plumbing repair", "local plumber",
    "local plumbers", "emergency plumber", "emergency plumbing", "commercial plumber",
    "commercial plumbing", "residential plumbing", "residential plumber", "licensed plumber",
    "licensed plumbing contractor", "drain cleaning", "clogged drain", "drain repair", "drain",
    "water heater", "water heater repair", "water heater installation", "water heater replacement",
    "tankless water heater", "hot water heater", "repipe", "repiping", "pipe repair",
    "pipe replacement", "burst pipe", "frozen pipe", "leak detection", "leak repair",
    "water leak", "slab leak", "sewer", "sewer line", "sewer repair", "sump pump",
    "garbage disposal", "faucet repair", "faucet installation", "faucet", "toilet repair",
    "toilet installation", "toilet", "gas line", "water line", "backflow", "hydro jetting",
    "hydrojetting", "bathroom plumbing", "kitchen plumbing", "water filtration",
    "water softener", "well pump", "fixture installation", "sewer camera", "trenchless",
    "septic", "drain unclogging", "rooter", "new construction plumbing", "service repair",
    "hot water tank", "water tank", "hot water tank installation", "water tank installation",
    "tank installation", "sump pump installation", "water heaters", "tankless water heaters",
]
# single-word service stems (matched plural-tolerant) to catch "toilets", "drains", "sewers" etc.
SERVICE_STEMS = ["plumber", "plumbing", "drain", "sewer", "toilet", "faucet", "repipe",
                 "hydrojetting", "rooter", "backflow", "septic"]
GEO_TERMS = [
    "georgia", "peachtree city", "newnan", "fayetteville", "fayette county", "fayette",
    "tyrone", "senoia", "sharpsburg", "brooks", "moreland", "grantville", "alvaton",
    "atlanta", "coweta", "griffin", "lagrange", "la grange", "carrollton", "douglasville",
    "palmetto", "turin", "haralson", "luthersville", "mcdonough", "stockbridge",
]

# ---- anchor-text spam signatures (whole-anchor heuristics) ----
SALES_PHRASES = [  # substring-safe (long, distinctive)
    "link building", "backlink", "back link", "dofollow", "do follow",
    "white hat seo", "white-hat seo", "tiered link", "high quality link",
    "high-quality link", "buy backlink", "buy link", "guest post", "link placement",
    "domain authority", "boost domain", "boost your ranking", "improve ranking",
    "higher google ranking", "google ranking", "citation flow", "trust flow",
    "premium seo", "authority backlink", "rank higher", "aged domain", "expired domain",
    "niche edit", "link juice", "off page seo", "off-page seo", "indexing service",
    "backlink indexer", "link farm", "blog network", "seo service", "seo services",
    "seo backlink", "professional seo", "affordable seo", "cheap seo", "best seo services",
    "search engine optimization service", "where to buy", "aged domains and backlinks",
]
SALES_WORDS = ["seo", "pbn", "gsa", "serp"]  # require word boundary
OFFTOPIC_PHRASES = [  # multi-word / distinctive -> substring safe
    "slot gacor", "binary option", "payday loan", "quick loan", "rolex replica",
    "replica watch", "write my essay", "essay writing", "term paper", "e-cigarette",
    "adult dating", "online casino", "sports betting",
]
OFFTOPIC_WORDS = [  # single words -> MUST be word-boundary (avoid 'cialis' in 'specialists' etc.)
    "casino", "gambling", "judi", "togel", "situs", "bandar", "poker", "roulette",
    "baccarat", "sportsbook", "viagra", "cialis", "pharmacy", "pills", "cannabis",
    "escort", "porn", "camgirl", "hookup", "bitcoin", "forex", "steroid",
    "bet", "slot", "xxx", "cbd", "sex", "vape", "weed", "loan", "casinos", "slots",
]

GENERIC = {"click here","visit website","visit site","read more","learn more","website",
           "this website","this site","homepage","home page","click","more info",
           "see more","view website","official website","check it out","here","link",
           "visit","go to website","website visit","company page visit website","website visit website"}

# ---- domain-level title/url/host spam signatures ----
SPAM_TITLE_PATTERNS = [
    "where to buy", "aged domain", "buy backlink", "buy aged domain", "link placement",
    "powerful pbn", "pbn backlink", "link building service", "backlink service",
    "seo backlink", "high quality backlink", "dofollow backlink", "citation flow",
    "high quality dofollow", "premium pbn", "domain for sale", "buy expired",
    "top domains", "domain list", "domains for sale", "website worth", "website stats",
    "web stats", "websiteworth", "buy backlinks", "aged domains and backlinks",
    "domain marketplace", "sell your domain", "domain appraisal", "estibot",
    # SEO/backlink-seller page titles (a genuine citation never uses this language)
    "backlink", "dofollow", "nofollow link", "niche edit", "guest post", "link building",
    "link-building", "link package", "seo resource", "seo service", "seo package",
    "powerful backlink", "premium backlink", "authority backlink", "boost organic traffic",
    "boost your ranking", "boost rankings", "higher da", "da and pa", "da/pa", "link juice",
    "tiered link", "web 2.0 link", "pbn", "rank higher", "increase your ranking",
]
SPAM_TITLE_REGEX = [re.compile(r"page\s*\d{3,}", re.I), re.compile(r"\bpage\s*\d{2,}\b.*domain", re.I)]
SPAM_URL_PATTERNS = [
    "/link-placement", "/pbn", "/buy-backlink", "/domain-list", "/aged-domain",
    "/seo-service", "/link-building", "/add-listing", "/submit-url", "/web-directory",
    "/domain/domain", "/backlinks/", "/buy-backlinks",
]
SPAM_HOST_TOKENS = [
    "backlink", "pbn", "dapa", "rankchecker", "rank-checker", "linkbuilding",
    "link-building", "buybacklink", "buylink", "dofollow", "linkfarm", "domainmarket",
    "aged-domain", "expireddomain", "domainlist", "directorysubmit", "submitdirectory",
    "freedirectory", "webdirectory", "linkdirectory", "seotool", "serptool", "indexer",
    "trafficboost", "massindex", "websiteslist", "websitelist", "websiteworth",
    "webstats", "getwebsiteworth", "bestwebstats", "dachecker", "pachecker",
    "seocheck", "domainsc", "allwebsitesdirectory", "worldbankingdirectory",
]
SPAM_HOST_WORDY = ["directory", "listing", "bookmark", "submit"]
PR_HOST_TOKENS = ["prnews", "pressrelease", "einnews", "openpr", "prlog", "issuewire",
                  "newswire", "prfree", "forpressrelease", "pr.com"]
CDN_IP_PREFIXES = ("172.67.", "104.21.", "104.16.", "104.17.", "104.18.", "104.19.",
                   "104.20.", "104.22.", "104.23.", "104.24.", "104.25.", "104.26.",
                   "104.27.", "104.28.", "172.64.", "172.65.", "172.66.", "172.68.",
                   "172.69.", "172.70.", "172.71.", "162.159.", "188.114.", "190.93.",
                   "197.234.", "198.41.", "108.162.")

def low(s): return (s or "").lower().strip()
def has_word(text, word):
    return re.search(r'(?<![a-z0-9])' + re.escape(word) + r'(?![a-z0-9])', text) is not None

def host_of(url):
    if not url: return ""
    u = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', url.strip())
    u = u.split('/')[0].split('?')[0].split('#')[0].split('@')[-1].split(':')[0].lower().strip('.')
    return u[4:] if u.startswith('www.') else u

def path_of(url):
    if not url: return "/"
    u = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', url.strip())
    i = u.find('/')
    if i < 0: return "/"
    return (u[i:].split('?')[0].split('#')[0]) or "/"

def is_home(url):
    return path_of(url).rstrip('/') in ("", "/index.html", "/home", "/index.php")

def is_brand(a):
    return any(b in a for b in BRAND_SUBSTR)

def looks_url(a):
    return bool(re.match(r'^(https?://)?[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(/\S*)?$', a)) and ' ' not in a

def anchor_type(anchor):
    """Classify by ANCHOR TEXT ONLY."""
    a = low(anchor)
    if a == "":
        return "Empty or image"
    # off-topic anchor text
    if any(p in a for p in OFFTOPIC_PHRASES) or any(has_word(a, w) for w in OFFTOPIC_WORDS):
        return "Spam: off topic"
    # SEO/backlink sales copy anchor text
    if any(p in a for p in SALES_PHRASES) or any(has_word(a, w) for w in SALES_WORDS):
        return "Spam: keyword stuffed SEO sales copy"
    # branded
    if is_brand(a):
        return "Branded"
    # naked url / domain
    if looks_url(a):
        return "Naked URL"
    # exact-match commercial (service vocabulary), plural-tolerant
    def _svc(a):
        for t in SERVICE_TERMS:
            if ' ' in t:
                if t in a: return True
            elif re.search(r'(?<![a-z])'+re.escape(t)+r's?(?![a-z])', a):
                return True
        for stem in SERVICE_STEMS:
            if re.search(r'(?<![a-z])'+re.escape(stem)+r's?(?![a-z])', a):
                return True
        return False
    has_service = _svc(a)
    has_geo = any(g in a for g in GEO_TERMS)
    if has_service:
        return "Exact match commercial (geo)" if has_geo else "Exact match commercial"
    # generic
    if a in GENERIC or (len(a) <= 22 and any(g == a for g in GENERIC)):
        return "Generic"
    if len(a) <= 22 and any(g in a for g in ("website","click","visit","here","more","link")):
        return "Generic"
    return "Contextual or other"

def host_is_spam(host):
    h = host.lower()
    core = h.rsplit('.', 1)[0] if '.' in h else h
    for tok in SPAM_HOST_TOKENS:
        if tok in h:
            return True, f"spam host token '{tok}'"
    for tok in SPAM_HOST_WORDY:
        if tok in core:
            return True, f"directory/listing host '{tok}'"
    return False, ""

def title_is_spam(title):
    t = low(title)
    for p in SPAM_TITLE_PATTERNS:
        if p in t:
            return True, f"spam page title ('{p}')"
    for rx in SPAM_TITLE_REGEX:
        if rx.search(t):
            return True, "domain-list page title"
    return False, ""

def main():
    rd = json.load(open(os.path.join(OUT, "refdomains.json"), encoding="utf-8"))
    links = [json.loads(l) for l in open(os.path.join(OUT, "links.jsonl"), encoding="utf-8")]

    by_dom = collections.defaultdict(list)
    for r in links:
        r["anchor_type"] = anchor_type(r.get("anchor",""))
        r["link_type"] = "Nofollow" if r.get("nofollow") else "Dofollow"
        tgt = r.get("redirect_url") or r.get("target_url")
        r["target_property"] = host_of(tgt) or MONEY
        r["target_is_home"] = is_home(r.get("target_url",""))
        d = r.get("source_domain") or host_of(r.get("source_url",""))
        r["source_domain"] = d
        by_dom[d].append(r)

    # /24 network detection (non-CDN)
    net24 = collections.Counter(); dom_net = {}
    for d, meta in rd.items():
        ip = meta.get("ip","")
        if ip and ip.count('.')==3 and not ip.startswith(CDN_IP_PREFIXES):
            net = ip.rsplit('.',1)[0] + ".0/24"; net24[net]+=1; dom_net[d]=net
    big_nets = {n for n,c in net24.items() if c>=5}

    domains = {}
    all_doms = set(rd.keys()) | set(by_dom.keys())
    for d in all_doms:
        dl = by_dom.get(d, [])
        meta = rd.get(d, {})
        ascore = meta.get("ascore", 0) or 0
        ip = meta.get("ip","")
        n_df = sum(1 for r in dl if not r.get("nofollow"))
        n_nf = sum(1 for r in dl if r.get("nofollow"))
        has_dofollow = n_df > 0
        atypes = [r["anchor_type"] for r in dl]
        titles = [r.get("source_title","") for r in dl]
        n_home = sum(1 for r in dl if r.get("target_is_home"))
        n_deep = sum(1 for r in dl if not r.get("target_is_home"))

        # client-link evidence
        has_exact = any(t in ("Exact match commercial","Exact match commercial (geo)") for t in atypes)
        n_sales_anchor = sum(1 for t in atypes if t=="Spam: keyword stuffed SEO sales copy")
        has_sales_anchor = n_sales_anchor > 0
        has_offtopic_anchor = any(t=="Spam: off topic" for t in atypes)
        # spam title/url on the client's own linking pages
        spam_title = False; title_reason=""
        for tt in titles:
            ok,why = title_is_spam(tt)
            if ok: spam_title=True; title_reason=why; break
        spam_url = any(any(p in low(r.get("source_url","")) for p in SPAM_URL_PATTERNS) for r in dl)
        spam_host, host_reason = host_is_spam(d)
        title_names_client = any(any(b in low(tt) for b in BRAND_SUBSTR) for tt in titles)
        deep_commercial = any((not r.get("target_is_home")) and
                              r["anchor_type"] in ("Exact match commercial","Exact match commercial (geo)")
                              for r in dl)
        pr_host = any(tok in d for tok in PR_HOST_TOKENS)
        in_big_net = d in dom_net and dom_net[d] in big_nets

        # aggregate "sales/marketplace" evidence on the client's own links
        sales_evidence = has_sales_anchor or spam_title or spam_url
        sales_dominant = (len(dl) > 0 and n_sales_anchor >= max(1, 0.5*len(dl)))

        evidence = []
        if has_sales_anchor: evidence.append("SEO/backlink sales-copy anchor")
        if has_offtopic_anchor: evidence.append("off-topic (casino/pharma/etc.) anchor")
        if spam_title: evidence.append(title_reason)
        if spam_url: evidence.append("spam URL template")
        if spam_host: evidence.append(host_reason)

        # ---------------- verdict order (first match wins) ----------------
        status = reason = ""
        if d in OWN_DOMAINS:
            status, reason = "Own Site", "client-owned / redirect domain"
        elif has_offtopic_anchor:                       # off-topic anchor on a client link = clear spam
            status = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
            reason = "; ".join(evidence)
        elif has_exact and has_sales_anchor:            # exact-match + PBN sales copy together -> review-level hold
            status = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
            reason = "exact-match commercial anchor AND SEO sales-copy on the same domain (review)"
        elif sales_dominant:                            # the home-page flood: mostly sales-copy anchors
            status = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
            reason = "; ".join(evidence) or "SEO sales-copy anchors dominate"
        elif has_exact or deep_commercial:              # commissioned-looking -> HOLD for partner
            status = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
            reason = "exact-match commercial anchor / deep money-page link; may be commissioned"
        elif ascore >= 20 and not sales_evidence:       # genuine site
            status, reason = "Keep", f"genuine site (Authority Score {ascore})"
        elif pr_host and not sales_evidence:
            status = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
            reason = "press-release syndication host"
        elif title_names_client and not sales_evidence:
            # playbook rule 6: a page that names the client without SEO sales copy is a
            # citation/business listing -> Keep, even on a directory host. Never disavow a citation.
            status, reason = "Keep", "linking page names the client without SEO sales copy (citation/editorial)"
        elif sales_evidence:                            # marketplace/SEO page or sales anchor
            status = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
            reason = "; ".join(evidence)
        elif spam_host:                                 # spam host name
            status = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
            reason = host_reason
        else:
            status, reason = "Keep", "no spam evidence"

        disavow_line = f"domain:{d}" if status == "Spam (Disavow)" else ""

        # top anchor (most common non-empty anchor text)
        ac = collections.Counter(r.get("anchor","") for r in dl if r.get("anchor","").strip())
        top_anchor = ac.most_common(1)[0][0] if ac else ""
        def ex_score(r):
            s=0
            if r.get("response_code")==200: s+=2
            if not r.get("nofollow"): s+=1
            if not r.get("target_is_home"): s+=0  # prefer any live dofollow
            return s
        example = max(dl, key=ex_score) if dl else None
        first_seen = min([r.get("first_seen",0) for r in dl if r.get("first_seen")],
                         default=meta.get("first_seen",0))
        props = collections.Counter(r["target_property"] for r in dl)

        domains[d] = {
            "domain": d, "status": status, "reason": reason,
            "ascore": ascore, "trust": meta.get("trust",0),
            "backlinks": len(dl), "rd_backlinks_num": meta.get("backlinks_num",0),
            "ip": ip, "country": meta.get("country",""),
            "dofollow": n_df, "nofollow": n_nf, "has_dofollow": has_dofollow,
            "first_seen": first_seen, "top_anchor": top_anchor,
            "target_properties": dict(props), "n_home": n_home, "n_deep": n_deep,
            "example_url": example.get("source_url","") if example else "",
            "example_title": example.get("source_title","") if example else "",
            "example_target": example.get("target_url","") if example else "",
            "example_anchor": example.get("anchor","") if example else "",
            "source_tool": ("Ahrefs" if (dl and all(r.get("tool")=="Ahrefs" for r in dl)) else
                            ("Semrush+Ahrefs" if any(r.get("tool")=="Semrush+Ahrefs" for r in dl) else "Semrush")),
            "has_exact": has_exact, "has_sales_anchor": has_sales_anchor,
            "has_offtopic": has_offtopic_anchor, "spam_title": spam_title,
            "spam_url": spam_url, "spam_host": spam_host,
            "title_names_client": title_names_client, "deep_commercial": deep_commercial,
            "sales_dominant": sales_dominant, "in_big_net": in_big_net, "net24": dom_net.get(d,""),
            "metrics_missing": meta.get("metrics_missing", False),
            "disavow_line": disavow_line,
            "links": dl,
        }

    with open(os.path.join(OUT, "domains.json"), "w", encoding="utf-8") as fh:
        json.dump(domains, fh)
    with open(os.path.join(OUT, "links_enriched.jsonl"), "w", encoding="utf-8") as fh:
        for r in links:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    sc = collections.Counter(v["status"] for v in domains.values())
    print("=== classification summary ===")
    for s in ["Spam (Disavow)","Spam (Nofollow, No Action)","Held (Pending Partner)",
              "Held (Nofollow, No Action)","Keep","Own Site"]:
        print(f"  {s}: {sc.get(s,0)}")
    print("  TOTAL domains:", len(domains))
    disq = [v for v in domains.values() if v["status"]=="Spam (Disavow)"]
    noev = [v for v in disq if not (v["has_sales_anchor"] or v["has_offtopic"] or v["spam_host"] or v["spam_title"] or v["spam_url"] or v["sales_dominant"])]
    print("  disavow domains:", len(disq), " | without visible evidence (MUST be 0):", len(noev))
    nf_bad = [v for v in disq if not v["has_dofollow"]]
    print("  disavow domains with no dofollow (MUST be 0):", len(nf_bad))
    print("  big /24 networks (>=5, non-CDN):", len(big_nets))

if __name__ == "__main__":
    main()
