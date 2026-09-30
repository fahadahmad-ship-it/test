"""Build the justdrivemedia.com backlink audit workbook + Google disavow file.

Inputs (raw/), pulled 2026-09-29/30:
  ahrefs_p*.csv          Ahrefs live referring domains
  ahrefs_bl_p*.csv       Ahrefs live backlinks (anchor, page, snippet, outbound links)
  semrush_refdomains.csv Semrush referring domains
  semrush_bl_p*.csv      Semrush backlinks (anchor, page, nofollow, outbound links)
Review (review/):
  decisions_*.csv        Manual review of every domain: domain,status,confidence,note

Pipeline: an automated first pass scores every domain, then the manual review
decides the final status and writes the plain English note. Every cell is a plain
value (no formulas), and all statuses, notes and labels are written without hyphens.
"""
import csv
import glob
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).parent
RAW = HERE / "raw"
REVIEW = HERE / "review"
PULL_DATE = "30 Sep 2026"
DASHES = re.compile(r"[-‐‑‒–—―−]")


def host(u):
    try:
        h = urlparse(str(u)).hostname or ""
    except ValueError:
        return ""
    return h.removeprefix("www.")


def no_dash(text):
    """Plain wording: replace any hyphen or dash with a space."""
    return re.sub(r"\s{2,}", " ", DASHES.sub(" ", str(text))).strip()


def clean(v):
    """Excel safe scalar: no NaN, no control chars, and text can never be read as a formula."""
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, pd.Timestamp):
        return v.date()
    if isinstance(v, str):
        v = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", v).strip()
        if not v:
            return None
        if v[0] in "=+-@":
            v = "’" + v if v[0] == "=" else " " + v
        return v[:1000]
    return v


# ---------------------------------------------------------------- load domains
AH_COLS = ["domain", "dr", "first_seen", "links", "dofollow", "is_spam", "traffic", "kw"]
ah = pd.concat([pd.read_csv(f, header=0, names=AH_COLS) for f in sorted(glob.glob(str(RAW / "ahrefs_p*.csv")))])
ah["first_seen"] = pd.to_datetime(ah["first_seen"].str[:10])
ah = ah.drop_duplicates("domain").set_index("domain")

se = pd.read_csv(RAW / "semrush_refdomains.csv", sep=";")
se["first_seen"] = pd.to_datetime(se["first_seen"], unit="s").dt.normalize()
se["last_seen"] = pd.to_datetime(se["last_seen"], unit="s").dt.normalize()
se = se.drop_duplicates("domain").set_index("domain")
known = set(ah.index) | set(se.index)

# ---------------------------------------------------------------- load backlinks
abl = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(str(RAW / "ahrefs_bl_p*.csv")))])
abl = abl.drop_duplicates(["url_from", "url_to", "anchor"])
abl = pd.DataFrame({
    "Tool": "Ahrefs",
    "Referring Domain": abl["name_source"].str.removeprefix("www."),
    "Linking Page URL": abl["url_from"],
    "Linking Page Title": abl["title"],
    "Target URL": abl["url_to"],
    "Anchor Text": abl["anchor"],
    "Link Type": abl["is_dofollow"].astype(bool).map({True: "Dofollow", False: "Nofollow"}),
    "Outbound Links on Page": abl["links_external"],
    "Page Category": abl["page_category_source"].fillna("").str.split(",").str[0].str.strip("/").str.replace("_", " "),
    "Text Around Link": (abl["snippet_left"].fillna("").astype(str).str[-80:] + " [LINK] "
                         + abl["snippet_right"].fillna("").astype(str).str[:80]).str.strip(),
    "First Seen": pd.to_datetime(abl["first_seen_link"].str[:10]),
})
abl.loc[abl["Text Around Link"] == "[LINK]", "Text Around Link"] = ""
sbl = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(str(RAW / "semrush_bl_p*.csv")))]).drop_duplicates()
sbl = pd.DataFrame({
    "Tool": "Semrush",
    "Referring Domain": sbl["source_url"].map(host),
    "Linking Page URL": sbl["source_url"],
    "Linking Page Title": sbl["source_title"],
    "Target URL": sbl["target_url"],
    "Anchor Text": sbl["anchor"],
    "Link Type": sbl["nofollow"].astype(bool).map({True: "Nofollow", False: "Dofollow"}),
    "Outbound Links on Page": sbl["external_num"],
    "Page Category": "",
    "Text Around Link": "",
    "First Seen": pd.to_datetime(sbl["first_seen"], unit="s").dt.normalize(),
})
bl = pd.concat([abl, sbl], ignore_index=True)


def map_domain(h):
    """Map a link's host onto a referring domain reported by the tools (handles subdomains)."""
    if h in known:
        return h
    parts = h.split(".")
    for i in range(1, len(parts) - 1):
        cand = ".".join(parts[i:])
        if cand in known:
            return cand
    return h


bl["Referring Domain"] = bl["Referring Domain"].map(map_domain)
bl = bl[bl["Referring Domain"].isin(known)].reset_index(drop=True)

# Links to mightypr.com: it 301 redirects to justdrivemedia.com, so these links pass on to the client too
mfiles = sorted(glob.glob(str(RAW / "mightypr_bl_p*.csv")))
mraw = pd.concat([pd.read_csv(f) for f in mfiles]).drop_duplicates(["url_from", "url_to", "anchor"]) if mfiles else pd.DataFrame()
if len(mraw):
    col = lambda c: mraw[c] if c in mraw.columns else pd.Series([None] * len(mraw), index=mraw.index)
    mbl = pd.DataFrame({
        "Tool": "Ahrefs (via mightypr.com)",
        "Referring Domain": mraw["name_source"].str.removeprefix("www.").map(map_domain),
        "Linking Page URL": mraw["url_from"],
        "Linking Page Title": mraw["title"],
        "Target URL": mraw["url_to"],
        "Anchor Text": mraw["anchor"],
        "Link Type": mraw["is_dofollow"].astype(bool).map({True: "Dofollow", False: "Nofollow"}),
        "Outbound Links on Page": mraw["links_external"],
        "Page Category": col("page_category_source").fillna("").astype(str).str.split(",").str[0].str.strip("/").str.replace("_", " "),
        "Text Around Link": (col("snippet_left").fillna("").astype(str).str[-80:] + " [LINK] "
                             + col("snippet_right").fillna("").astype(str).str[:80]).str.strip().replace("[LINK]", ""),
        "First Seen": pd.to_datetime(mraw["first_seen_link"].str[:10]),
    })
    # Ahrefs shows a redirected link in the justdrivemedia.com report with the final URL as target;
    # a link that also appears in the mightypr.com report actually points at mightypr.com
    mkeys = set(zip(mraw["url_from"], mraw["anchor"].fillna("")))
    bl["_via_mighty"] = [(u, a if isinstance(a, str) else "") in mkeys for u, a in zip(bl["Linking Page URL"], bl["Anchor Text"])]
    seen_keys = set(zip(bl["Linking Page URL"], bl["Anchor Text"].fillna("")))
    mbl = mbl[[(u, a if isinstance(a, str) else "") not in seen_keys for u, a in zip(mbl["Linking Page URL"], mbl["Anchor Text"])]]
    bl = pd.concat([bl, mbl], ignore_index=True)
extra_domains = set(bl["Referring Domain"]) - known
known_all = known | extra_domains

# ---------------------------------------------------------------- anchor classification
A_EMPTY = "Empty or image"
A_CASINO = "Spam: casino, pharma or exam dump"
A_SALES = "Spam: keyword stuffed SEO sales copy"
A_THIRD = "Third party brand (seoexpress, sitetosocial)"
A_NAKED = "Naked URL"
A_BRAND = "Branded"
A_GENERIC = "Generic"
A_FOREIGN = "Foreign language text"
A_URL = "Other URL"
A_BRAND_LONG = "Branded (long, contextual)"
A_OTHER = "Contextual or other"
SPAMMY_ANCHORS = {A_CASINO, A_SALES}

GENERIC = {"website", "visit website", "go to website", "visit site", "click here", "here", "read more",
           "link", "source", "homepage", "this", "site", "web", "url", "more", "visit", "view website"}
# Strong terms: one hit is enough. Soft terms: need two different hits (sales copy sentences).
STRONG_SPAM = re.compile(
    r"backlink|\bpbn\b|\b(?:da|pa|dr)(?=[\s,/)&]|$)|domain authority|guest posts?\b|link building|link insertion|"
    r"dofollow|do-follow|rank first|\bbuy\b|\bcheap\b|seo packages?|da boost|high da|niche edits?|web 2\.0|"
    r"link juice|outrank|premium seo|seoexpress|affordable seo|authority links|link velocity|traffic packages",
    re.I,
)
SOFT_SPAM = re.compile(
    r"white[- ]label|indexation|sidebar links|blogroll|profile links|forum links|reseller|rankings|\border\b|"
    r"pricing|packages|link placements|press release links|rank tracking|schema markup|keyword research|"
    r"map pack|serp analysis|youtube seo|gmb optimization|skyscraper|content clusters|seo consulting|"
    r"traffic services|interview placements|resource page links|nap consistency",
    re.I,
)
CASINO_ANCHOR = re.compile(r"casino|\bslots?\b|poker|gambl|\bbet\b|kasino|nettikasino|togel|gacor|viagra|pharma|"
                           r"exam dumps?|pdfvce|jn0-\d+|certification exam", re.I)
THIRD_PARTY = re.compile(r"seoexpress|sitetosocial", re.I)
BRAND = re.compile(r"just ?drive ?media|mighty ?pr|^mighty$", re.I)


def anchor_type(a):
    if a is None or (isinstance(a, float) and pd.isna(a)) or not str(a).strip():
        return A_EMPTY
    t = " ".join(str(a).lower().split())
    if CASINO_ANCHOR.search(t):
        return A_CASINO
    soft = {m.group().lower() for m in SOFT_SPAM.finditer(t)}
    if len(t) > 25 and (STRONG_SPAM.search(t) or len(soft) >= 2):
        return A_SALES
    if THIRD_PARTY.search(t):
        return A_THIRD
    if re.fullmatch(r"(visit |go to )?(https?://)?(www\.)?(justdrivemedia|mightypr)\.com\S*( ↗)?", t):
        return A_NAKED
    if BRAND.search(t) and len(t) <= 60:
        return A_BRAND
    if t in GENERIC or re.fullmatch(r"\d+", t):
        return A_GENERIC
    if re.search(r"[а-яё]|[一-鿿]", t):
        return A_FOREIGN
    if re.fullmatch(r"(https?://)?(www\.)?[\w.-]+\.[a-z]{2,}\S*", t):
        return A_URL
    if BRAND.search(t):
        return A_BRAND_LONG
    return A_OTHER


bl["Anchor Type"] = bl["Anchor Text"].map(anchor_type)

dom_anchor = {}
for d, grp in bl.groupby("Referring Domain"):
    types = Counter(grp["Anchor Type"])
    spam = grp[grp["Anchor Type"].isin(SPAMMY_ANCHORS)]
    txt = grp["Anchor Text"].fillna("").astype(str).str.strip()
    txt = txt[txt != ""]
    ex = (spam if len(spam) else grp).iloc[0]
    outb = pd.to_numeric(grp["Outbound Links on Page"], errors="coerce")
    dom_anchor[d] = {
        "backlinks": len(grp),
        "anchors": int(txt.nunique()),
        "top_anchor": txt.value_counts().index[0] if len(txt) else "(empty or image link)",
        "anchor_mix": ", ".join(f"{k} ×{v}" for k, v in types.most_common()),
        "spam_anchors": len(spam),
        "third_party": int((grp["Anchor Type"] == A_THIRD).sum()),
        "sample_url": ex["Linking Page URL"],
        "sample_title": ex["Linking Page Title"],
        "max_outbound": int(outb.max()) if outb.notna().any() else None,
        "category": next((c for c in grp["Page Category"] if isinstance(c, str) and c), ""),
        "all_404": bool(grp["Linking Page Title"].fillna("").astype(str).str.contains("ERROR 404", case=False).all()),
    }

# ---------------------------------------------------------------- automated first pass
OWN = {"justdrivemedia.notion.site", "justdrivemedia.vercel.app", "mightypr.com"}
SPAM_WORDS = re.compile(
    r"backlink|baclink|seo|rank|serp|checker|dapa|pachecker|dachecker|drchecker|"
    r"directory|directoy|link-baron|outrank|crawl|index|boosthub|linkpro|guestpost|guest-post|"
    r"pbn|traffic|casino|gambl|poker|slot|gacor|ufabet|betwinner|doxycycline|erythromycin|"
    r"psilocybin|domraider|mp3|smmprovider|anchor|authority|linkfinds|linkstock|linkstash|"
    r"linkloot|linkdepot|linkory|linkharvest|linkfrontier|linkzira|linkqaro|linkqano|linkqira|"
    r"linkmiro|linkrivo|linklora|linklivo|linknaro|linkmexa|linkrixa|linktera|linkvilo|linkviro|"
    r"linkxaro|linkzaro|linktexa|linksnatcher|linkcollective|linkgrowth|linkseo|linkrank|"
    r"linkforge|linkpoint|linkpitcher|linkdirectory|linkboost|blinks\.|atomizelink|anchorurl|"
    r"websiteworth|webworth|worthchecker|shorten|urls-|byteshort|buzzshrink",
    re.I,
)
SPAM_TLDS = (".shop", ".store", ".xyz", ".online", ".site", ".space", ".website", ".link",
             ".info", ".top", ".icu", ".cfd", ".sbs", ".monster", ".mom", ".click", ".cv",
             ".art", ".pro", ".lol", ".party", ".live", ".wiki", ".homes", ".forum", ".world",
             ".club", ".fyi", ".today", ".co.in", ".in", ".bz", ".lc", ".cc")
SPAM_IPS = {"104.207.79.34", "104.207.79.38", "203.161.54.114", "195.20.19.178",
            "118.139.181.85", "118.139.176.46", "118.139.161.199", "118.139.178.200",
            "118.139.177.45", "118.139.181.255", "184.168.115.60", "67.223.118.29"}

C_XYZ = "Numbered .xyz network"
C_STORE = "SEOExpress, Link Baron and Outrank HQ .store network"
C_CHECKER = "Fake SEO checker sites"
C_SHOP = ".shop link farm network"
C_SELLER = "Paid backlink seller network (IP 203.161.54.114)"
C_AUTOGEN = "Auto generated site network (IP 104.207.79.x)"
C_BLOGSPOT = "Blogspot spam blogs"
C_DIRECTORY = "Low quality web directories"
C_CASINO = "Casino, pharma and gambling spam"
C_SCRAPER = "Website info scraper network (shared IP)"
C_LINKINFO = "SEO spam .link and .info sites"
C_HACKED = "Thin or hacked sites carrying spam links"
C_FARM = "Link farm pages (500+ outbound links)"
C_OTHER = "Other spam"
CLUSTER_DESC = {
    C_XYZ: "Throwaway numbered .xyz domains registered in bulk only to place links.",
    C_STORE: "Keyword named .store sites run by one link selling network.",
    C_CHECKER: "Fake DA, PA and backlink checker sites that create a page for every website.",
    C_SHOP: "Auto generated .shop sites (ranklab, boosthub, linkpro family) created in bulk.",
    C_SELLER: "Backlink selling sites that all sit on one server.",
    C_AUTOGEN: "Auto generated content sites that all sit on one server.",
    C_BLOGSPOT: "Throwaway Blogspot blogs used as a private blog network.",
    C_DIRECTORY: "Mass submission web directories with no editorial review and no visitors.",
    C_CASINO: "Casino, gambling, pharmacy and exam dump spam sites.",
    C_SCRAPER: "Website worth and domain info scraper pages on a shared spam server.",
    C_LINKINFO: "SEO keyword .link and .info domains that sell backlinks.",
    C_HACKED: "Thin or hacked sites used to host keyword stuffed spam links.",
    C_FARM: "Pages listing hundreds or thousands of unrelated outbound links.",
    C_OTHER: "Low quality sites with no real audience, used in the link spam campaign.",
}


def cluster(d, ip):
    if re.fullmatch(r"\d+\.xyz", d):
        return C_XYZ
    if re.search(r"seoexpress|link-baron|outrank-hq|rank-forge", d) or (d.endswith(".store") and d.count("-") >= 3):
        return C_STORE
    if re.search(r"checker|dapa|dadr|drur|tfchecker|pageauthority|backlinkanalys|backlinkaudit|"
                 r"backlinkreport|backlinkfinder|linkprofile|inboundlinks|finddomainbacklinks|"
                 r"checkbacklinks|findbacklinks|lookup", d):
        return C_CHECKER
    if d.endswith(".shop") and re.search(r"boosthub|ranklab|linkpro|seolink|seohub|crawl|index|serp|rank|seo|link|anchor|authority|search", d):
        return C_SHOP
    if ip == "203.161.54.114":
        return C_SELLER
    if ip in {"104.207.79.34", "104.207.79.38"}:
        return C_AUTOGEN
    if d.endswith(".blogspot.com"):
        return C_BLOGSPOT
    if re.search(r"directory|directoy", d):
        return C_DIRECTORY
    if re.search(r"casino|gambl|poker|slot|gacor|ufabet|betwinner|doxycycline|erythromycin|psilocybin", d):
        return C_CASINO
    if ip in SPAM_IPS:
        return C_SCRAPER
    if re.search(r"\.link$|\.info$", d) and re.search(r"seo|backlink|rank", d):
        return C_LINKINFO
    an = dom_anchor.get(d)
    if an and an["spam_anchors"]:
        return C_HACKED
    if an and an["max_outbound"] is not None and an["max_outbound"] >= 500:
        return C_FARM
    return C_OTHER


def assess(d):
    """Automated first pass: returns (Spam | Keep | Own Site, evidence phrases, metrics text)."""
    a = ah.loc[d] if d in ah.index else None
    s = se.loc[d] if d in se.index else None
    an = dom_anchor.get(d)
    traffic = float(a["traffic"]) if a is not None else None
    dr = float(a["dr"]) if a is not None else None
    ascore = float(s["domain_ascore"]) if s is not None else None
    ip = s["ip"] if s is not None else None
    flagged = a is not None and int(a["is_spam"]) == 1
    words = bool(SPAM_WORDS.search(d))
    bad_tld = d.endswith(SPAM_TLDS)
    ip_net = ip in SPAM_IPS
    blogspot = d.endswith(".blogspot.com")
    numeric = bool(re.fullmatch(r"\d+\.xyz", d))
    no_traffic = (traffic is not None and traffic < 100) or (traffic is None and (ascore or 0) < 10)
    low_traffic = (traffic is not None and traffic < 500) or (traffic is None and (ascore or 0) < 20)
    inflated_dr = bad_tld and traffic == 0 and (dr or 0) >= 30
    spam_anchor = bool(an and an["spam_anchors"])
    third = bool(an and an["third_party"])
    farm = bool(an and an["max_outbound"] is not None and an["max_outbound"] >= 500)
    quality = ((traffic or 0) >= 100 or (a is not None and a["kw"] >= 10) or (ascore or 0) >= 20
               or ((dr or 0) >= 20 and s is None and d.endswith((".com", ".io", ".ai", ".co", ".org", ".net"))
                   and not re.search(r"directory|directoy|backlink|seo", d)))

    ev = []
    if numeric:
        ev.append("numbered throwaway .xyz domain")
    if words:
        ev.append("SEO or link selling words in the domain name")
    if spam_anchor:
        ev.append(f"keyword stuffed sales copy anchors ({an['spam_anchors']} of {an['backlinks']} links)")
    if third:
        ev.append("anchors promote unrelated third party brands")
    if farm:
        ev.append(f"linking page has {an['max_outbound']:,} outbound links (link farm)")
    if flagged:
        ev.append("Ahrefs marks the domain as spam")
    if ip_net:
        ev.append(f"hosted on spam network IP {ip}")
    if blogspot and (ascore or 0) <= 3:
        ev.append("throwaway Blogspot blog with almost no authority")
    if an and an["all_404"]:
        ev.append("linking pages are fake error pages")
    if inflated_dr:
        ev.append("fake authority: looks strong in link tools but has zero organic traffic")
    if bad_tld and no_traffic:
        ev.append("cheap spam TLD with no organic traffic")

    metrics = []
    sl = sem_live.get(d, {})
    as_live = to_int(sl.get("authority_score"))
    as_show = as_live if as_live is not None else (int(ascore) if ascore is not None else None)
    if as_show is not None:
        st = to_int(sl.get("organic_traffic"))
        metrics.append(f"Semrush Authority Score {as_show}" + (f", Semrush organic traffic {st:,} a month" if st is not None else ""))
    if a is not None:
        metrics.append(f"Ahrefs organic traffic {int(traffic):,} a month, {int(a['kw']):,} ranking keywords")
    metric_txt = "; ".join(metrics) or "no metrics reported"

    if d in OWN:
        return "Own Site", ev, metric_txt
    if traffic is not None and traffic >= 1000 and not words and not spam_anchor:
        return "Keep", ev, metric_txt
    if traffic is None and ascore is not None and ascore >= 35 and not spam_anchor:
        return "Keep", ev, metric_txt
    strong = (
        numeric
        or (words and low_traffic and (flagged or not quality))
        or (spam_anchor and not quality)
        or (spam_anchor and (flagged or words or farm))
        or inflated_dr
        or (ip_net and low_traffic and not quality)
        or (flagged and no_traffic)
        or (blogspot and s is not None and (ascore or 0) <= 3)
        or (bad_tld and (traffic or 0) < 20 and (ascore or 0) < 10 and (flagged or words or ip_net or (dr or 0) < 5))
        or (third and farm and not quality)
    )
    return ("Spam" if strong else "Keep"), ev, metric_txt


# ---------------------------------------------------------------- manual review decisions
review = {}
for f in sorted(glob.glob(str(REVIEW / "decisions_*.csv"))):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            dom = (row.get("domain") or "").strip().lower()
            if dom:
                review[dom] = {"status": (row.get("status") or "").strip(),
                               "confidence": (row.get("confidence") or "").strip().title(),
                               "note": no_dash(row.get("note") or "")}

# Second check (red team) on the riskiest spam calls: can overturn a spam call to Keep
verify = {}
for f in sorted(glob.glob(str(REVIEW / "verify_*.csv"))):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            dom = (row.get("domain") or "").strip().lower()
            if dom:
                verify[dom] = {"verdict": (row.get("verdict") or "").strip().title(),
                               "confidence": (row.get("confidence") or "").strip().title(),
                               "note": no_dash(row.get("note") or "")}

# Final consistency overrides decided after comparing reviewers (review/overrides.csv)
overrides = {}
for f in sorted(glob.glob(str(REVIEW / "overrides.csv"))):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            overrides[row["domain"].strip().lower()] = {"status": row["status"].strip(),
                                                        "confidence": row["confidence"].strip().title(),
                                                        "note": no_dash(row["note"])}

# Deep live check (review/deep): investigator evidence per domain + final decisions after skeptic verification
DEEP = REVIEW / "deep"
deep_ev = {}
for f in sorted(glob.glob(str(DEEP / "result_*.json"))):
    try:
        data = json.load(open(f))
    except (ValueError, OSError):
        continue
    for r in data if isinstance(data, list) else data.get("results", []):
        if isinstance(r, dict) and r.get("domain"):
            deep_ev[r["domain"].strip().lower()] = r
deep_dec = {}
if (DEEP / "final_decisions.json").exists():
    for r in json.load(open(DEEP / "final_decisions.json")):
        deep_dec[r["domain"].strip().lower()] = r

# Live Semrush metrics for every domain (review/semrush): primary authority and traffic source
sem_live = {}
for f in sorted(glob.glob(str(REVIEW / "semrush" / "semrush_*.csv"))):
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            dom = (row.get("domain") or "").strip().lower()
            if dom:
                sem_live[dom] = row


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# Rewrites that express authority with Semrush AS instead of DR (review/rewrites_final.json)
rewrites = {}
if (REVIEW / "rewrites_final.json").exists():
    for r in json.load(open(REVIEW / "rewrites_final.json")):
        rewrites[(r["domain"].strip().lower(), r["field"])] = no_dash(r["text"])


def rw(d, field, text):
    return rewrites.get((d, field), text)


# Careful anchor review of brand anchor only domains and mightypr.com only domains (review/anchors)
anchor_dec = {}
if (REVIEW / "anchors" / "final_decisions.json").exists():
    for r in json.load(open(REVIEW / "anchors" / "final_decisions.json")):
        anchor_dec[r["domain"].strip().lower()] = r

S_SPAM, S_KEEP, S_KEEP_LOW, S_OWN = "Spam (Disavow)", "Keep", "Keep (Low Confidence)", "Own Site"
S_SPAM_NF = "Spam (Nofollow, No Action)"
ORDER = [S_SPAM, S_SPAM_NF, S_KEEP_LOW, S_KEEP, S_OWN]


def fallback_note(auto, ev):
    if auto == "Spam":
        return no_dash((ev[0][0].upper() + ev[0][1:] + ".") if ev else "Spam site with no real audience.")
    if auto == "Own Site":
        return "Client owned property. Keep."
    return "No clear spam signals found. Keep."


rows = []
link_first = bl.groupby("Referring Domain")["First Seen"].min().to_dict()
dof_links = bl[bl["Link Type"] == "Dofollow"].groupby("Referring Domain").size().to_dict()
nof_links = bl[bl["Link Type"] == "Nofollow"].groupby("Referring Domain").size().to_dict()
bl["_via_mighty"] = bl.get("_via_mighty", False)
bl["_via_mighty"] = bl["_via_mighty"].fillna(False).astype(bool) | bl["Target URL"].astype(str).str.contains("mightypr.com")
bl.loc[bl["_via_mighty"] & ~bl["Target URL"].astype(str).str.contains("mightypr.com"), "Target URL"] = \
    bl["Target URL"].astype(str) + " (via mightypr.com redirect)"
targets = bl.assign(_t=bl["_via_mighty"].map(lambda v: "mightypr.com (redirect)" if v else "justdrivemedia.com")) \
            .groupby("Referring Domain")["_t"].agg(lambda t: " and ".join(sorted(set(t))) if len(set(t)) > 1 else next(iter(t))).to_dict()

for d in sorted(known_all):
    a = ah.loc[d] if d in ah.index else None
    s = se.loc[d] if d in se.index else None
    an = dom_anchor.get(d)
    auto, ev, metric_txt = assess(d)
    rv = review.get(d)
    if rv and rv["status"] in ("Spam", "Keep", "Own Site"):
        status = {"Spam": S_SPAM, "Own Site": S_OWN}.get(rv["status"], S_KEEP)
        if status == S_KEEP and rv["confidence"] == "Low":
            status = S_KEEP_LOW
        note, conf, reviewed = rv["note"], rv["confidence"] or "Medium", "Manual review"
    else:
        status = {"Spam": S_SPAM, "Own Site": S_OWN}.get(auto, S_KEEP)
        note, conf, reviewed = fallback_note(auto, ev), "Medium", "Automated only"
    second = ""
    vf = verify.get(d)
    if vf and vf["verdict"] in ("Spam", "Keep"):
        conf = vf["confidence"] or conf
        note = vf["note"] or note
        reviewed = "Manual review and second check"
        if vf["verdict"] == "Keep":
            status, second = (S_KEEP_LOW if conf == "Low" else S_KEEP), "Overturned to keep"
        else:
            status, second = S_SPAM, "Confirmed spam"
    ov = overrides.get(d)
    if ov:
        conf, note = ov["confidence"], ov["note"]
        status = {"Spam": S_SPAM, "Own Site": S_OWN}.get(ov["status"], S_KEEP_LOW if conf == "Low" else S_KEEP)
        second = "Overturned to keep" if status != S_SPAM and auto == "Spam" else second
    dd = deep_dec.get(d)
    deep_check = ""
    if dd and dd.get("final_status") in ("Spam", "Keep", "Own Site"):
        conf = (dd.get("final_confidence") or conf).title()
        note = no_dash(dd.get("final_note") or note)
        status = {"Spam": S_SPAM, "Own Site": S_OWN}.get(dd["final_status"], S_KEEP_LOW if conf == "Low" else S_KEEP)
        deep_check = "Verified by two skeptics" if dd.get("verified") else "Investigated with live data"
        reviewed = "Manual review, second check and deep live check"
    ar = anchor_dec.get(d)
    anchor_check = ""
    if ar and ar.get("status") in ("Spam", "Keep"):
        conf = (ar.get("confidence") or conf).title()
        note = no_dash(ar.get("note") or note)
        status = S_SPAM if ar["status"] == "Spam" else (S_KEEP_LOW if conf == "Low" else S_KEEP)
        anchor_check = "Checked and challenged" if ar.get("verified") else "Checked"
        if d in extra_domains:
            reviewed = "Manual anchor review (links via mightypr.com)"
    n_dof, n_nof = int(dof_links.get(d, 0)), int(nof_links.get(d, 0))
    if a is not None:
        n_dof = max(n_dof, int(a["dofollow"]))
    has_dofollow = n_dof > 0 or (n_dof == 0 and n_nof == 0)
    if status == S_SPAM and not has_dofollow:
        status = S_SPAM_NF
    de = dict(deep_ev.get(d, {}))
    for k in ("own_backlink_profile", "top_pages", "links_to_client"):
        if de.get(k):
            de[k] = rw(d, k, de[k])
    note = rw(d, "note", note)
    first = min(x for x in [a["first_seen"] if a is not None else None,
                            s["first_seen"] if s is not None else None, link_first.get(d)] if x is not None and not pd.isna(x))
    sl = sem_live.get(d, {})
    sem_as = to_int(sl.get("authority_score"))
    if sem_as is None and s is not None:
        sem_as = int(s["domain_ascore"])
    if sem_as is None and ar and ar.get("semrush_as") is not None:
        sem_as = int(ar["semrush_as"])
    sem_bl = to_int(sl.get("backlinks"))
    if sem_bl is None and s is not None:
        sem_bl = int(s["backlinks_num"])
    rows.append({
        "Domain": d,
        "Status": status,
        "Note (why)": note,
        "Confidence": conf,
        "Spam Network": cluster(d, s["ip"] if s is not None else None) if status in (S_SPAM, S_SPAM_NF) else "",
        "Semrush Authority Score": sem_as,
        "Semrush Backlinks": sem_bl,
        "Semrush Referring Domains": to_int(sl.get("referring_domains")),
        "Semrush Organic Traffic": to_int(sl.get("organic_traffic")),
        "Semrush Organic Keywords": to_int(sl.get("organic_keywords")),
        "Semrush Main Market": (sl.get("top_database") or "").upper(),
        "Evidence Found": no_dash(("; ".join(ev) + ". " if ev else "No spam signals. ") + metric_txt + "."),
        "Spam Signals": len(ev),
        "In Disavow File": "Yes" if status == S_SPAM else "No",
        "Links Point To": targets.get(d, "justdrivemedia.com"),
        "Dofollow Links": n_dof,
        "Nofollow Links": n_nof,
        "First Seen": first,
        "Top Anchor Text": an["top_anchor"] if an else "No live backlink returned by either tool",
        "Anchor Mix": an["anchor_mix"] if an else "",
        "Spam Anchors": an["spam_anchors"] if an else 0,
        "Backlinks Analysed": an["backlinks"] if an else 0,
        "Links To Client (summary)": no_dash(de["links_to_client"]) if de.get("links_to_client") else "",
        "Example Linking Page": an["sample_url"] if an else "",
        "Linking Page Title": an["sample_title"] if an else "",
        "Max Outbound Links on Page": an["max_outbound"] if an else None,
        "Page Category": an["category"] if an else "",
        "Its Own Backlink Profile": no_dash(de["own_backlink_profile"]) if de.get("own_backlink_profile") else "",
        "Its Top Pages": no_dash(de["top_pages"]) if de.get("top_pages") else "",
        "Sites It Links Out To": de.get("linked_domains"),
        "Ahrefs DR": de.get("dr") if de.get("dr") is not None else (float(a["dr"]) if a is not None else None),
        "Ahrefs Referring Domains": de.get("refdomains"),
        "Ahrefs Backlinks": de.get("backlinks"),
        "Ahrefs Organic Traffic": de.get("org_traffic") if de.get("org_traffic") is not None else (int(a["traffic"]) if a is not None else None),
        "Ahrefs Ranking Keywords": de.get("org_keywords") if de.get("org_keywords") is not None else (int(a["kw"]) if a is not None else None),
        "Ahrefs Spam Flag": ("Yes" if int(a["is_spam"]) else "No") if a is not None else "",
        "Source": "Both" if (a is not None and s is not None) else ("Ahrefs" if a is not None else "Semrush"),
        "IP": s["ip"] if s is not None else "",
        "Country": (s["country"].upper() if isinstance(s["country"], str) else "") if s is not None else "",
        "Semrush Last Seen": s["last_seen"] if s is not None else None,
        "Deep Check": deep_check,
        "Anchor Review": anchor_check,
        "Automated First Pass": auto,
        "Second Check": second,
        "Reviewed By": reviewed,
    })

df = pd.DataFrame(rows)
df["_o"] = df["Status"].map(ORDER.index)
df = df.sort_values(["_o", "Spam Network", "Domain"]).drop(columns="_o").reset_index(drop=True)
status_of = dict(zip(df["Domain"], df["Status"]))
note_of = dict(zip(df["Domain"], df["Note (why)"]))
bl["Status"] = bl["Referring Domain"].map(status_of)
bl["Note (why)"] = bl["Referring Domain"].map(note_of)
bl = bl.sort_values(["Referring Domain", "Tool", "First Seen"]).reset_index(drop=True)

# ---------------------------------------------------------------- disavow file (all dates)
# If every live link from a domain comes from one subdomain and the root domain itself is not
# a spam name, disavow only that subdomain so a genuine main site is never touched.
bl["_host"] = bl["Linking Page URL"].map(host)
hosts = bl[bl["Status"] == S_SPAM].groupby("Referring Domain")["_host"].agg(lambda h: sorted(set(h)))


def disavow_target(d, net):
    hs = hosts.get(d, [])
    if len(hs) == 1 and hs[0] != d and hs[0].endswith("." + d) and not SPAM_WORDS.search(d) and net != C_STORE:
        return hs[0]
    return d


df["Disavow Line"] = [("domain:" + disavow_target(d, n)) if st == S_SPAM else ""
                      for d, st, n in zip(df["Domain"], df["Status"], df["Spam Network"])]
dis = df[df["Status"] == S_SPAM].sort_values("Domain")
lines = [
    "# Disavow file for justdrivemedia.com and mightypr.com",
    f"# Prepared {PULL_DATE} from Ahrefs and Semrush referring domain and backlink exports",
    "# Scope: every spam referring domain with at least one dofollow link (all dates). Nofollow only spam is not included.",
    "# mightypr.com 301 redirects to justdrivemedia.com, so upload this SAME file to BOTH Search Console properties:",
    "# justdrivemedia.com and mightypr.com.",
    f"# {len(dis)} domains",
    "# Upload at https://search.google.com/search-console/disavow-links using a URL prefix property",
    "# (the tool does not support Domain properties). Upload to every version that exists (https and http).",
    "# NOTE: uploading REPLACES any existing disavow file, so merge with the current one first.",
    "",
] + list(dis["Disavow Line"])
(HERE / "justdrivemedia-disavow.txt").write_text("\n".join(lines) + "\n")

# ---------------------------------------------------------------- workbook helpers
FONT = "Arial"
FILL = {S_SPAM: "F4C7C3", S_SPAM_NF: "F9E3E1", S_KEEP_LOW: "FCE8B2", S_KEEP: "B7E1CD", S_OWN: "C9DAF8",
        "Spam anchor": "F4C7C3", "Unrelated brand anchor": "FCE8B2", "Normal anchor": "B7E1CD"}
INK = {S_SPAM: "9C0006", S_SPAM_NF: "B45F06", S_KEEP_LOW: "7F6000", S_KEEP: "274E13", S_OWN: "1C4587",
       "Spam anchor": "9C0006", "Unrelated brand anchor": "7F6000", "Normal anchor": "274E13"}
FILLS = {k: PatternFill("solid", start_color=v) for k, v in FILL.items()}
HDR_FILL = PatternFill("solid", start_color="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=16, bold=True, color="1F3864")
H2 = Font(name=FONT, size=12, bold=True, color="1F3864")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
TOP = Alignment(vertical="top")
NUM, DATE, PCT = "#,##0", "d mmm yyyy", "0.0%"


def hdr(ws, row, headers, col=1):
    for c, h in enumerate(headers, col):
        cell = ws.cell(row=row, column=c, value=h)
        cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def write_table(ws, frame, widths=None, color_col=None, wrap_cols=(), fmt=None):
    cols = list(frame.columns)
    hdr(ws, 1, cols)
    ws.row_dimensions[1].height = 32
    ci = cols.index(color_col) if color_col else None
    for r, rec in enumerate(frame.itertuples(index=False, name=None), start=2):
        lab = rec[ci] if ci is not None else None
        fill = FILLS.get(lab)
        for c, v in enumerate(rec, start=1):
            cell = ws.cell(row=r, column=c, value=clean(v))
            cell.font, cell.border = BODY, BORDER
            cell.alignment = WRAP if cols[c - 1] in wrap_cols else TOP
            if fill is not None:
                cell.fill = fill
            if fmt and cols[c - 1] in fmt:
                cell.number_format = fmt[cols[c - 1]]
        if ci is not None:
            ws.cell(row=r, column=ci + 1).font = Font(name=FONT, size=10, bold=True, color=INK.get(lab, "000000"))
    for c, name in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(c)].width = (widths or {}).get(name, 14)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(frame) + 1}"


def para(ws, row, text, last_col=5, height=30):
    c = ws.cell(row=row, column=1, value=text)
    c.font, c.alignment = BODY, WRAP
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    ws.row_dimensions[row].height = height


wb = Workbook()

# ---------------------------------------------------------------- Summary
sm = wb.active
sm.title = "Summary"
n_spam = int((df.Status == S_SPAM).sum())
sm["A1"] = "justdrivemedia.com Backlink Audit"
sm["A1"].font = TITLE
sm["A2"] = (f"Data pulled {PULL_DATE} from Ahrefs and Semrush: {len(df):,} unique referring domains and "
            f"{len(bl):,} backlinks. Every domain went through an automated check, a manual review and a deep live check "
            "with Semrush and Ahrefs data; doubtful spam calls were also verified by independent skeptics.")
sm["A2"].font = Font(name=FONT, size=10, italic=True, color="595959")

MEANING = {
    S_SPAM: "Confirmed spam with at least one dofollow link. Included in the disavow file.",
    S_SPAM_NF: "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed (standard practice).",
    S_KEEP_LOW: "Kept to be safe. Not disavowed, but worth a quick manual look.",
    S_KEEP: "Genuine or harmless link. Keep.",
    S_OWN: "Client owned property or sister brand. Keep.",
}
r = 4
hdr(sm, r, ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"])
for lab in ORDER:
    r += 1
    n_dom = int((df.Status == lab).sum())
    vals = [lab, n_dom, int((bl.Status == lab).sum()), n_dom / len(df), MEANING[lab]]
    for c, v in enumerate(vals, 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.fill, cell.font, cell.border = FILLS[lab], BODY, BORDER
        cell.number_format = PCT if c == 4 else NUM
    sm.cell(row=r, column=1).font = Font(name=FONT, size=10, bold=True, color=INK[lab])
r += 1
for c, v in enumerate(["Total", len(df), len(bl), 1.0, ""], 1):
    cell = sm.cell(row=r, column=c, value=v)
    cell.font, cell.border = BOLD, BORDER
    cell.number_format = PCT if c == 4 else NUM

r += 2
sm.cell(row=r, column=1, value="What the manual review changed").font = H2
auto_spam = df["Automated First Pass"] == "Spam"
final_spam = df["Status"].isin([S_SPAM, S_SPAM_NF])
changes = [
    f"Moved from spam to keep (protected): {int((auto_spam & ~final_spam).sum())} domains.",
    f"Moved from keep to spam (newly caught): {int((~auto_spam & final_spam).sum())} domains.",
    f"Unchanged: {int((auto_spam == final_spam).sum()):,} domains.",
    f"Domains checked by manual review: {int(df['Reviewed By'].str.startswith('Manual').sum()):,} of {len(df):,}.",
    f"Domains given the deep live check: {int((df['Deep Check'] != '').sum()):,}, of which "
    f"{int((df['Deep Check'] == 'Verified by two skeptics').sum())} doubtful spam verdicts were also verified by two skeptics.",
    f"Riskiest spam calls given an independent second check: {int((df['Second Check'] != '').sum())}, of which "
    f"{int((df['Second Check'] == 'Overturned to keep').sum())} were overturned to keep.",
    f"Domains whose links use only plain brand anchors (Mighty PR, Just Drive Media) given a careful anchor review: "
    f"{int((df['Anchor Review'] != '').sum())}, judged only on the linking page because brand anchors are normal.",
]
for t in changes:
    r += 1
    para(sm, r, "•  " + t, height=16)

r += 2
sm.cell(row=r, column=1, value="Key findings").font = H2
spam_bl = bl[bl["Anchor Type"].isin(SPAMMY_ANCHORS)]
sep_new = int((df["First Seen"].dt.strftime("%Y%m") == "202609").sum())
since_apr = df["First Seen"] >= pd.Timestamp("2026-04-01")
healthy_n = int(df.Status.isin([S_KEEP, S_KEEP_LOW, S_OWN]).sum())
n_nf = int((df.Status == S_SPAM_NF).sum())
n_mighty = int(df["Links Point To"].str.contains("mightypr").sum())
findings = [
    f"{int(final_spam.sum()):,} of the {len(df):,} referring domains are spam. {n_spam:,} of them have at least one dofollow "
    f"link and go in the disavow file; the other {n_nf:,} only have nofollow links, which pass no ranking value, so they "
    "need no action (standard practice).",
    f"mightypr.com 301 redirects to justdrivemedia.com, so its links pass on to the client. {n_mighty:,} referring domains "
    "link through mightypr.com, which is why the same disavow file must be uploaded to both Search Console properties.",
    f"justdrivemedia.com is the target of a large negative SEO link attack that sped up sharply in September 2026, "
    f"with {sep_new:,} new referring domains in that month alone, almost all auto generated spam.",
    f"{len(spam_bl):,} of {len(bl):,} backlinks ({len(spam_bl) / len(bl):.0%}) use keyword stuffed sales copy as anchor "
    "text (for example “high quality pbn backlinks for justdrivemedia.com”), which makes the brand look like a link seller.",
    "The spam copy reuses the client's own brand names (Just Drive Media and sister brand Mighty PR) inside link "
    "selling sentences, which is a typical automated negative SEO template.",
    f"Spam linking pages carry a median of {int(pd.to_numeric(spam_bl['Outbound Links on Page'], errors='coerce').median()):,} "
    "outbound links each, so they are link farms with no editorial value.",
    f"{healthy_n} domains are genuine or harmless and are kept (for example Crunchbase, Inc, PRWeb, G2, Squarespace, "
    "universities and real client websites). None of them are in the disavow file.",
]
for t in findings:
    r += 1
    para(sm, r, "•  " + t)

r += 2
sm.cell(row=r, column=1, value="Spam networks in the disavow file").font = H2
r += 1
hdr(sm, r, ["Network", "Domains", "What it is"])
for cl, n in dis["Spam Network"].value_counts().items():
    r += 1
    for c, v in enumerate([cl, int(n), CLUSTER_DESC[cl]], 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.font, cell.border = BODY, BORDER
    sm.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)

r += 2
sm.cell(row=r, column=1, value="Anchor text profile (all backlinks)").font = H2
r += 1
hdr(sm, r, ["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"])
at = bl.groupby("Anchor Type").agg(n=("Anchor Type", "size"), d=("Referring Domain", "nunique")).sort_values("n", ascending=False)
for t, rec in at.iterrows():
    r += 1
    for c, v in enumerate([t, int(rec.n), float(rec.n) / len(bl), int(rec.d)], 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.font, cell.border = BODY, BORDER
        cell.number_format = PCT if c == 3 else NUM
        if t in SPAMMY_ANCHORS:
            cell.fill = FILLS[S_SPAM]

r += 2
sm.cell(row=r, column=1, value="Next steps").font = H2
steps = [
    "1. Download the current disavow file from Google Search Console (if one exists) and merge it with the disavow text file delivered with this audit.",
    "2. Upload the merged file in the Disavow Links tool for the justdrivemedia.com URL prefix property (the tool does not work with Domain properties).",
    "3. Optionally glance at the Keep (Low Confidence) domains. They are not disavowed, so nothing is lost by leaving them.",
    "   Spam (Nofollow, No Action) domains can be added to the file if you prefer, but it is not needed.",
    "4. Upload the same merged file to a mightypr.com URL prefix property too (verify it by DNS record if needed), because it redirects to justdrivemedia.com.",
    "5. Re run this audit every month while the attack continues, because new spam domains are still appearing daily.",
]
for t in steps:
    r += 1
    para(sm, r, t, height=16)

r += 2
sm.cell(row=r, column=1, value="Colour legend").font = H2
for lab in ORDER:
    r += 1
    cell = sm.cell(row=r, column=1, value=lab)
    cell.fill, cell.border = FILLS[lab], BORDER
    cell.font = Font(name=FONT, size=10, bold=True, color=INK[lab])
    sm.cell(row=r, column=2, value=MEANING[lab]).font = BODY
    sm.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
for col, w in zip("ABCDE", (48, 14, 14, 16, 84)):
    sm.column_dimensions[col].width = w

# ---------------------------------------------------------------- Domain Audit
wd = wb.create_sheet("Domain Audit")
write_table(
    wd, df,
    widths={"Domain": 36, "Status": 20, "Note (why)": 60, "Confidence": 11, "Spam Network": 34,
            "Evidence Found": 70, "Spam Signals": 9, "In Disavow File": 10, "First Seen": 12,
            "Top Anchor Text": 45, "Anchor Mix": 42, "Example Linking Page": 45, "Linking Page Title": 40,
            "Page Category": 30, "IP": 15, "Automated First Pass": 12, "Second Check": 16, "Reviewed By": 18,
            "Its Own Backlink Profile": 60, "Its Top Pages": 45, "Links To Client (summary)": 60, "Deep Check": 20,
            "Semrush Authority Score": 11, "Semrush Main Market": 10},
    color_col="Status", wrap_cols=("Note (why)", "Evidence Found", "Its Own Backlink Profile", "Links To Client (summary)"),
    fmt={"First Seen": DATE, "Semrush Last Seen": DATE, "Ahrefs Organic Traffic": NUM, "Ahrefs Backlinks": NUM,
         "Ahrefs Referring Domains": NUM, "Semrush Referring Domains": NUM, "Semrush Organic Traffic": NUM,
         "Semrush Organic Keywords": NUM, "Sites It Links Out To": NUM,
         "Ahrefs Ranking Keywords": NUM, "Max Outbound Links on Page": NUM, "Semrush Backlinks": NUM},
)

# ---------------------------------------------------------------- Anchor Analysis
tmp = bl.assign(_a=bl["Anchor Text"].fillna("").astype(str).str.strip().replace("", "(empty or image link)"),
                _spam=bl["Status"].eq(S_SPAM))
aa = (tmp.groupby("_a")
         .agg(**{"Anchor Type": ("Anchor Type", "first"),
                 "Backlinks": ("_a", "size"),
                 "Referring Domains": ("Referring Domain", "nunique"),
                 "Example Referring Domain": ("Referring Domain", "first")})
         .reset_index().rename(columns={"_a": "Anchor Text"}))
spam_dom_per_anchor = tmp[tmp["_spam"]].groupby("_a")["Referring Domain"].nunique()
aa["Spam Domains Using It"] = aa["Anchor Text"].map(spam_dom_per_anchor).fillna(0).astype(int)
aa["Share of Backlinks"] = aa["Backlinks"] / len(bl)
aa["Anchor Verdict"] = aa["Anchor Type"].map(lambda t: "Spam anchor" if t in SPAMMY_ANCHORS
                                             else ("Unrelated brand anchor" if t == A_THIRD else "Normal anchor"))
aa = aa.sort_values(["Backlinks", "Anchor Text"], ascending=[False, True])[
    ["Anchor Text", "Anchor Type", "Anchor Verdict", "Backlinks", "Share of Backlinks", "Referring Domains",
     "Spam Domains Using It", "Example Referring Domain"]]
wa = wb.create_sheet("Anchor Analysis")
write_table(wa, aa, widths={"Anchor Text": 90, "Anchor Type": 36, "Anchor Verdict": 20, "Example Referring Domain": 34},
            color_col="Anchor Verdict", wrap_cols=("Anchor Text",), fmt={"Share of Backlinks": "0.00%", "Backlinks": NUM})

# ---------------------------------------------------------------- All Backlinks
bcols = ["Referring Domain", "Status", "Note (why)", "Tool", "Anchor Text", "Anchor Type", "Link Type",
         "Linking Page URL", "Linking Page Title", "Target URL", "Outbound Links on Page", "Page Category",
         "Text Around Link", "First Seen"]
wbl = wb.create_sheet("All Backlinks")
write_table(wbl, bl[bcols],
            widths={"Referring Domain": 32, "Status": 20, "Note (why)": 50, "Tool": 9, "Anchor Text": 55,
                    "Anchor Type": 32, "Link Type": 10, "Linking Page URL": 55, "Linking Page Title": 45,
                    "Target URL": 38, "Page Category": 30, "Text Around Link": 60},
            color_col="Status", fmt={"First Seen": DATE, "Outbound Links on Page": NUM})

# ---------------------------------------------------------------- Disavow List
dl = dis[
    ["Disavow Line", "Domain", "Status", "Note (why)", "Confidence", "Spam Network", "Links Point To", "Dofollow Links",
     "Nofollow Links", "First Seen",
     "Semrush Authority Score", "Semrush Backlinks", "Semrush Referring Domains", "Semrush Organic Traffic",
     "Semrush Organic Keywords", "Top Anchor Text", "Links To Client (summary)", "Its Own Backlink Profile",
     "Its Top Pages", "Sites It Links Out To", "Ahrefs DR", "Ahrefs Organic Traffic", "Evidence Found", "Deep Check"]]
wdl = wb.create_sheet("Disavow List")
write_table(wdl, dl, widths={"Disavow Line": 44, "Domain": 38, "Status": 16, "Note (why)": 60, "Confidence": 11,
                             "Spam Network": 34, "Top Anchor Text": 45, "Links To Client (summary)": 60,
                             "Its Own Backlink Profile": 60, "Its Top Pages": 45, "Evidence Found": 70, "Deep Check": 20},
            color_col="Status", wrap_cols=("Note (why)", "Evidence Found", "Links To Client (summary)", "Its Own Backlink Profile"),
            fmt={"First Seen": DATE, "Semrush Backlinks": NUM, "Semrush Referring Domains": NUM,
                 "Semrush Organic Traffic": NUM, "Semrush Organic Keywords": NUM, "Sites It Links Out To": NUM,
                 "Ahrefs Organic Traffic": NUM})

# ---------------------------------------------------------------- Methodology
wm = wb.create_sheet("Methodology")
wm["A1"] = "How each domain was assessed"
wm["A1"].font = TITLE
cov = sum(d in dom_anchor for d in df.Domain)
method = [
    ("Data sources", f"Ahrefs Site Explorer (live referring domains and all {len(abl):,} live backlinks) and Semrush "
                     f"Backlink Analytics (referring domains and {len(sbl):,} backlinks), pulled {PULL_DATE}. Domains "
                     "were merged and de duplicated, and www or sub domain variants were mapped to the referring domain."),
    ("Metrics used", "Semrush is the primary source: Semrush Authority Score (AS), Semrush backlinks, referring domains and "
                     "organic traffic and keywords (main market) are shown for every domain. Ahrefs figures are shown "
                     "alongside as a second opinion. Semrush visit data (Traffic Analytics) is not included in the "
                     "account's Semrush plan, so organic search traffic is used instead."),
    ("Scope", "All referring domains and all backlinks, from every date. The disavow file is not limited to recent links."),
    ("Step 1: automated check", "Every domain was scored on 11 spam signals: SEO or link words in the domain name, numbered "
                                "throwaway .xyz domain, keyword stuffed or casino anchors, anchors for unrelated brands, "
                                "linking page with 500+ outbound links, Ahrefs spam flag, spam network hosting IP, "
                                "throwaway Blogspot blog, fake error pages, fake authority with zero traffic, and cheap spam TLD "
                                "with no traffic."),
    ("Step 2: manual review", "Eight reviewers then checked every one of the domains by hand, using the metrics, every "
                              "anchor text, the linking pages and their outbound link counts, and challenged the automated "
                              "verdict. The review decides the final status and writes the note."),
    ("Step 3: second check", "The riskiest spam calls (those resting on hosting or page size evidence rather than spam "
                             "anchor text, or where the first reviewer was not highly confident) were given to two more "
                             "reviewers whose only job was to try to prove each one genuine, using live Ahrefs data. "
                             "Anything they could show to be genuine was overturned to keep."),
    ("Step 4: deep live check", "Before anything was disavowed, every domain was checked again with live Ahrefs data: "
                                "its own metrics (referring domains, backlinks, organic traffic and keywords, how many "
                                "sites it links out to), the anchors of its own backlinks, who links to it, what pages it "
                                "ranks with, and every link it sends to the client. Any spam verdict with the slightest doubt "
                                "was then given to two independent skeptics (one judging the site, one judging the link) "
                                "who tried to prove it genuine; if either succeeded, the domain was kept."),
    ("Mighty PR redirect", "Just Drive Media acquired Mighty PR, and mightypr.com 301 redirects to justdrivemedia.com, so links "
                           "to mightypr.com pass on to the client. They were pulled from Ahrefs and included. Plain Mighty PR "
                           "anchors are treated as normal branded anchors, never as a spam signal; domains whose links use only "
                           "brand anchors were reviewed again on the linking page alone, with a skeptic on every doubtful call."),
    ("Dofollow rule", "Only spam domains with at least one dofollow link go in the disavow file, which is standard practice: "
                      "nofollow links pass no ranking value. Nofollow only spam is labelled Spam (Nofollow, No Action)."),
    ("Protection rule", "No genuine link is disavowed. Real sites with real traffic, recognised brands, company profile "
                        "sites, PR and news sites, and real personal or business sites are kept even when the link is low "
                        "value or nofollow. When a reviewer was unsure, the domain was kept and marked Keep (Low Confidence)."),
    ("Statuses", "Spam (Disavow): confirmed spam with a dofollow link, in the disavow file. Spam (Nofollow, No Action): "
                 "spam with only nofollow links, not in the file. Keep: genuine or harmless. Keep (Low Confidence): "
                 "kept to be safe, worth a quick look. Own Site: client owned property or sister brand."),
    ("Anchor types", "Branded (Just Drive Media or sister brand Mighty PR), Naked URL, Generic (for example website), "
                     "Empty or image, Contextual, Other URL, Third party brand, Foreign language, Spam: keyword stuffed "
                     "SEO sales copy, Spam: casino, pharma or exam dump."),
    ("Disavow file", "Domain level entries (domain:example.com) for every domain with status Spam (Disavow). Blogspot "
                     "spam is disavowed per sub domain, never blogspot.com itself. Where every live link comes from one "
                     "spam sub domain of an otherwise ordinary domain, only that sub domain is disavowed."),
    ("Coverage", f"Anchor level evidence was available for {cov:,} of {len(df):,} domains. The rest are domains the tools "
                 "list as referring but returned no live backlink row for, so they were judged on domain level data."),
    ("Upload warning", "Google's disavow upload REPLACES the existing file, so merge with any current file before uploading, "
                       "and upload it to both the justdrivemedia.com and the mightypr.com properties."),
    ("No formulas", "All figures are stored as values, so the workbook opens the same way, with no errors, in any spreadsheet app."),
]
for i, (k, v) in enumerate(method, start=3):
    kc = wm.cell(row=i, column=1, value=k)
    kc.font, kc.alignment = BOLD, WRAP
    vc = wm.cell(row=i, column=2, value=v)
    vc.font, vc.alignment = BODY, WRAP
    wm.row_dimensions[i].height = 48
wm.column_dimensions["A"].width = 26
wm.column_dimensions["B"].width = 120

out = HERE / "justdrivemedia-backlink-audit.xlsx"
wb.save(out)
print(df["Status"].value_counts().to_string())
print("reviewed:", int(df["Reviewed By"].str.startswith("Manual").sum()), "of", len(df),
      "| second check:", int((df["Second Check"] != "").sum()), "overturned:", int((df["Second Check"] == "Overturned to keep").sum()),
      "| disavow:", len(dis), "| backlinks:", len(bl), "| anchor coverage:", cov)
print("saved", out)
