"""
Classifier for the highpriorityplumbing.com backlink audit.

Client constants
----------------
MONEY_SITE   = highpriorityplumbing.com  (single Search Console property; client can upload)
OWNED        = highpriorityplumbing.com + its own subdomains. No redirect/owned domains
               (only redirect_url seen is ift.tt = IFTTT sharing, not owned).
PARTNER word = "partner" (default; the brief names no other role).
VOCAB        = plumbing / septic / drain / sewer / water-heater etc. + GA geography.

Six statuses, no Review buckets. Evidence-based: every Spam rests on a visible anchor,
host-name, title, or off-topic signal -- never on Authority Score or TLD alone.
"""
import re, glob, os, json, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import parse_backlinks, parse_refdomains, canon_host

BASE = "/home/user/test/hpp"
MONEY = "highpriorityplumbing.com"

# ---------- anchor pattern vocabulary ----------
RE_SALES = re.compile(
    r'(premium seo authority backlinks|high quality (dofollow|white hat) '
    r'|white hat seo links|dofollow backlinks da ?\d+|pbn network service'
    r'|i will increase your domain|as a small business owner.*(seo|overwhelmed)'
    r'|tiered link building|buy back ?links|cheap back ?links|link building service'
    r'|boost (your )?(domain authority|da|dr)|rank higher|authority backlinks'
    r'|increase your (domain authority|da|dr)|whatsapp us on)', re.I)
RE_MSG = re.compile(r'(join our telegram|our telegram chanel|t\.me/|\btelegram\b|join our whatsapp (channel|group)|whatsapp channel)', re.I)
RE_OFFTOPIC = re.compile(r'(\bcasino\b|\bpoker\b|gambling|\bslots?\b|\bbetting\b|viagra|cialis|pharmacy|\bescort\b|\bporn\b|\bxxx\b|animal sex|\bsex\b|adult dating)', re.I)
RE_NAKED = re.compile(r'^(https?://|www\.)', re.I)
RE_SERVICE = re.compile(r'(plumb|septic|drain|sewer|water ?(heater|line|service|shut|pressure)|faucet|gas ?(line|pipe)|garbage disposal|sump ?pump|repipe|leak detection|hydro ?jet|sewer (jet|line)|boiler|toilet|water valve)', re.I)
RE_GEO = re.compile(r'(conyers|eatonton|columbus|acworth|savannah|\bgeorgia\b|\bga\b)', re.I)
RE_BRAND = re.compile(r'(high ?priority ?plumbing)', re.I)
RE_GENERIC = re.compile(r'^(visit (the )?(provider )?website\.?|open (the )?website|go to website|view website|website|click here\.?\.?|read more|learn more|here\.?|this website|more|button|link|external[- ]link.*|view provider website|🌐 ?visit website|via website|apply now)$', re.I)
RE_EMPTY_IMG = re.compile(r'(\.gif|\.png|\.jpe?g|\bimage\b|\blogo\b|\bicon\b|screenshot|home\.gif)', re.I)

# host-name link-SELLER signatures (conservative: clear link/seo seller vocab only;
# NOT bare "directory"/"listing" which also name genuine citation sites)
RE_HOSTSPAM = re.compile(
    r'(back ?link|linkbuilding|link-building|buybacklink|seobacklink|seo-?back'
    r'|\bpbn\b|dofollow|guestpost|guest-post|rankbuild|rankscal|ranklink|toprank'
    r'|nichelink|sponsoredlink|linkoutreach|page1boost|seoboost|linkjuice'
    r'|offpage|off-page|editorlink|linkplacement|link-placement|darksidelinks|quarterlinks'
    r'|(^|[.-])seo([.-]|\d)|-seo\.|seo-)', re.I)
RE_HOSTSPAM2 = re.compile(r'(dapa|rankchecker|domainauthority)', re.I)

# off-topic host
RE_HOSTOFF = re.compile(r'(casino|poker|gambl|betting|\bslot|porn|\bxxx\b|escort|pharма|viagra)', re.I)


def anchor_type(anchor):
    a = anchor.strip()
    if a == "" or RE_EMPTY_IMG.search(a):
        return "Empty or image"
    if RE_SALES.search(a):
        return "Spam: keyword stuffed SEO sales copy"
    if RE_MSG.search(a):
        return "Spam: messaging-app invitation"
    if RE_OFFTOPIC.search(a):
        return "Spam: off-topic"
    if RE_NAKED.search(a) or a.lower().startswith(MONEY) or a.lower() in ("www."+MONEY, MONEY):
        # bare url / bare domain
        return "Naked URL"
    # brand vs commercial: a service term that survives removing the brand phrase is a
    # genuine commercial anchor; a service term only inside the brand name ("...plumbing")
    # is Branded, not commercial.
    brand_present = bool(RE_BRAND.search(a))
    stripped = RE_BRAND.sub(" ", a)
    if RE_SERVICE.search(stripped):
        return "Exact match commercial (geo)" if RE_GEO.search(a) else "Exact match commercial"
    if brand_present:
        return "Branded"
    if RE_SERVICE.search(a):  # service term with no brand at all
        return "Exact match commercial (geo)" if RE_GEO.search(a) else "Exact match commercial"
    if RE_GENERIC.search(a):
        return "Generic"
    return "Contextual or other"


def is_home(target_url):
    m = re.sub(r'^https?://[^/]+', '', (target_url or "").lower()).strip('/')
    m = m.split('?')[0]
    return m in ("", "index.html", "home")


def main():
    bl, bl_rej = parse_backlinks(glob.glob(os.path.join(BASE, "data/fetch/bl_*.csv")))
    rd, rd_rej = parse_refdomains(glob.glob(os.path.join(BASE, "data/rd/rd_*.csv")))
    # metrics (optional): domain;organic_keywords;organic_traffic
    metrics = {}
    mpath = os.path.join(BASE, "data/metrics/metrics.csv")
    if os.path.exists(mpath):
        with open(mpath) as fh:
            for line in fh:
                p = line.rstrip("\n").split(";")
                if len(p) >= 3 and not line.lower().startswith("domain;"):
                    d = canon_host(p[0])
                    try: metrics[d] = (int(float(p[1])), int(float(p[2])))
                    except: metrics[d] = (0, 0)

    # dedupe links
    seen = set(); links = []
    for r in bl:
        k = (r["source_url"].rstrip("/").lower(), r["target_url"].rstrip("/").lower(), r["anchor"])
        if k in seen: continue
        seen.add(k); links.append(r)

    # refdomain index
    rdidx = {}
    for d in rd:
        dom = canon_host(d["domain"])
        if dom in rdidx:  # keep the one with more backlinks
            try:
                if int(d["backlinks_num"]) <= int(rdidx[dom]["backlinks_num"]): continue
            except: pass
        rdidx[dom] = d
    rd_domains = sorted(rdidx.keys())

    # map each link to a referring domain (longest suffix match into rd set, else own host)
    rd_sorted_bylen = sorted(rd_domains, key=len, reverse=True)
    rd_set = set(rd_domains)
    def refdomain_of(host):
        if host in rd_set: return host
        for d in rd_sorted_bylen:
            if host.endswith("." + d): return d
        return host  # Semrush-unlisted subdomain -> its own row

    dom_links = defaultdict(list)
    for r in links:
        h = canon_host(r["source_url"])
        rdom = refdomain_of(h)
        dom_links[rdom].append(r)

    # ensure every refdomain has a row even if 0 mapped links (shouldn't happen, but safe)
    for d in rd_domains:
        dom_links.setdefault(d, [])

    # ---------- classify each referring domain ----------
    def classify(dom, rs):
        info = rdidx.get(dom, {})
        try: asc = int(info.get("domain_ascore", "0") or 0)
        except: asc = 0
        types = [anchor_type(r["anchor"]) for r in rs]
        has_dofollow = any(not r["nofollow"] for r in rs)
        has_sales = any(t == "Spam: keyword stuffed SEO sales copy" for t in types)
        has_msg = any(t == "Spam: messaging-app invitation" for t in types)
        has_off = any(t == "Spam: off-topic" for t in types)
        has_exact = any(t.startswith("Exact match commercial") for t in types)
        names_client_clean = any(
            (RE_BRAND.search(r["source_title"] or "") and not RE_SALES.search(r["source_title"] or ""))
            for r in rs)
        host_spam = bool(RE_HOSTSPAM.search(dom) or RE_HOSTSPAM2.search(dom))
        host_off = bool(RE_HOSTOFF.search(dom))
        deep_commercial = any((not is_home(r["target_url"])) and
                              anchor_type(r["anchor"]).startswith("Exact match") for r in rs)

        # ----- verdict order (first match wins) -----
        if dom == MONEY or dom.endswith("." + MONEY):
            verdict = "Own Site"
        elif has_exact and has_sales:
            verdict = "Held"                      # mixed: possibly commissioned + spammed -> partner
        elif has_off or host_off:
            verdict = "Spam"
        elif has_sales:
            verdict = "Spam"
        elif has_msg:
            verdict = "Spam"
        elif host_spam:
            verdict = "Spam"
        elif asc >= 20:
            verdict = "Keep"                      # genuine authority site, no spam evidence
        elif has_exact or deep_commercial:
            verdict = "Held"
        elif names_client_clean:
            verdict = "Keep"                      # genuine citation / editorial mention
        else:
            verdict = "Keep"

        # ----- genuine-parent guard -----
        # If a Spam verdict rests only on nofollow spam links that came from a *subdomain*
        # folded into this root, and the root itself is a genuine authority site (AS>=20),
        # keep the parent's standing (playbook: a subdomain's link-scheme page keeps its own
        # verdict; the genuine parent is not spam). These are nofollow => no action anyway.
        if verdict == "Spam" and not has_dofollow and asc >= 20:
            spam_srcs = [r for r in rs if anchor_type(r["anchor"]) in
                         ("Spam: keyword stuffed SEO sales copy", "Spam: messaging-app invitation", "Spam: off-topic")]
            if spam_srcs and all(canon_host(r["source_url"]) != dom for r in spam_srcs) and not host_spam and not host_off:
                verdict = "Keep"

        # ----- nofollow / dofollow modifier -----
        if verdict == "Spam":
            status = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
        elif verdict == "Held":
            status = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
        elif verdict == "Own Site":
            status = "Own Site"
        else:
            status = "Keep"
        return status, asc, types, has_dofollow

    out = {}
    for dom in sorted(dom_links.keys()):
        rs = dom_links[dom]
        status, asc, types, has_dofollow = classify(dom, rs)
        info = rdidx.get(dom, {})
        # example backlink: prefer a live (200) link, prefer dofollow, prefer one carrying the top anchor
        def score_ex(r):
            s = 0
            if r["response_code"] == "200": s += 2
            if not r["nofollow"]: s += 1
            return s
        ex = max(rs, key=score_ex) if rs else None
        # top anchor by frequency among this domain's links
        anchors_here = Counter(r["anchor"] for r in rs)
        top_anchor = anchors_here.most_common(1)[0][0] if anchors_here else ""
        kw, tr = metrics.get(dom, (None, None))
        out[dom] = {
            "domain": dom,
            "status": status,
            "as": asc,
            "backlinks_num": info.get("backlinks_num", str(len(rs))),
            "rds": info.get("domain_trust_score", ""),  # placeholder; RD's per domain not pulled
            "traffic": tr,
            "organic_keywords": kw,
            "ip": info.get("ip", ""),
            "country": info.get("country", ""),
            "first_seen": info.get("first_seen", min((r["first_seen"] for r in rs), default="")),
            "dofollow_links": sum(1 for r in rs if not r["nofollow"]),
            "nofollow_links": sum(1 for r in rs if r["nofollow"]),
            "links_point_to": "highpriorityplumbing.com",
            "top_anchor": top_anchor,
            "example_page": ex["source_url"] if ex else "",
            "example_title": ex["source_title"] if ex else "",
            "example_target": (ex["redirect_url"] or ex["target_url"]) if ex else "",
            "source": "Semrush",
            "n_links": len(rs),
            "has_exact": any(t.startswith("Exact match") for t in types),
        }

    # status counts
    cnt = Counter(v["status"] for v in out.values())
    print("=== STATUS COUNTS (referring domains) ===")
    for s in ["Spam (Disavow)", "Spam (Nofollow, No Action)", "Held (Pending Partner)",
              "Held (Nofollow, No Action)", "Keep", "Own Site"]:
        print(f"  {s:32s} {cnt.get(s,0)}")
    print(f"  {'TOTAL':32s} {sum(cnt.values())}")
    print(f"backlinks parsed {len(bl)} unique {len(links)} rejected {bl_rej}; refdomains {len(rdidx)} (rej {rd_rej})")
    print(f"metrics loaded for {len(metrics)} domains")

    os.makedirs(os.path.join(BASE, "out"), exist_ok=True)
    with open(os.path.join(BASE, "out/classified_domains.json"), "w") as fh:
        json.dump(out, fh)
    # also persist per-link classification for All Backlinks / Anchor Analysis
    linkrows = []
    for dom in sorted(dom_links.keys()):
        st = out[dom]["status"]
        for r in dom_links[dom]:
            linkrows.append({
                "refdomain": dom, "status": st, "tool": "Semrush",
                "anchor": r["anchor"], "anchor_type": anchor_type(r["anchor"]),
                "link_type": "Nofollow" if r["nofollow"] else "Dofollow",
                "page_url": r["source_url"], "page_title": r["source_title"],
                "target_url": r["redirect_url"] or r["target_url"],
            })
    with open(os.path.join(BASE, "out/classified_links.json"), "w") as fh:
        json.dump(linkrows, fh)
    print(f"wrote {len(out)} domains, {len(linkrows)} links")


if __name__ == "__main__":
    main()
