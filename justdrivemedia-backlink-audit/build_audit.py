"""Build the justdrivemedia.com backlink audit workbook + Google disavow file.

Inputs (raw/), all pulled 2026-09-29/30:
  ahrefs_p*.csv          Ahrefs live referring domains
  ahrefs_bl_p*.csv       Ahrefs live backlinks (anchor, page, snippet, outbound links)
  semrush_refdomains.csv Semrush referring domains
  semrush_bl_p*.csv      Semrush backlinks (anchor, page, nofollow, outbound links)

Every cell is written as a plain value (no formulas), so the file shows identical,
error-free numbers in Excel, Google Sheets, Numbers and LibreOffice.
"""
import glob
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
PULL_DATE = "2026-09-30"
SINCE = pd.Timestamp("2026-04-01")


def host(u):
    try:
        h = urlparse(str(u)).hostname or ""
    except ValueError:
        return ""
    return h.removeprefix("www.")


def clean(v):
    """Excel-safe scalar: no NaN, no control chars, and text can never be read as a formula."""
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if hasattr(v, "item"):  # numpy scalar -> python
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

# ---------------------------------------------------------------- anchor classification
GENERIC = {"website", "visit website", "go to website", "visit site", "click here", "here", "read more",
           "link", "source", "homepage", "this", "site", "web", "url", "more", "visit", "view website"}
# Strong terms: one hit is enough. Soft terms: need two different hits (sales-copy sentences).
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
CASINO_ANCHOR = re.compile(r"casino|\bslots?\b|poker|gambl|\bbet\b|kasino|nettikasino|togel|gacor|viagra|pharma|exam dumps?|pdfvce|jn0-\d+|certification exam", re.I)
THIRD_PARTY = re.compile(r"seoexpress|sitetosocial", re.I)
BRAND = re.compile(r"just ?drive ?media|mighty ?pr|^mighty$", re.I)
SPAMMY_ANCHORS = {"Spam – casino / pharma / exam-dump", "Spam – keyword-stuffed SEO sales copy"}


def anchor_type(a):
    if a is None or (isinstance(a, float) and pd.isna(a)) or not str(a).strip():
        return "Empty / image"
    t = " ".join(str(a).lower().split())
    if CASINO_ANCHOR.search(t):
        return "Spam – casino / pharma / exam-dump"
    soft = {m.group().lower() for m in SOFT_SPAM.finditer(t)}
    if len(t) > 25 and (STRONG_SPAM.search(t) or len(soft) >= 2):
        return "Spam – keyword-stuffed SEO sales copy"
    if THIRD_PARTY.search(t):
        return "Third-party brand (seoexpress / sitetosocial)"
    if re.fullmatch(r"(visit |go to )?(https?://)?(www\.)?(justdrivemedia|mightypr)\.com\S*( ↗)?", t):
        return "Naked URL"
    if BRAND.search(t) and len(t) <= 60:
        return "Branded"
    if t in GENERIC or re.fullmatch(r"\d+", t):
        return "Generic"
    if re.search(r"[а-яё]|[\u4e00-\u9fff]", t):
        return "Foreign-language text"
    if re.fullmatch(r"(https?://)?(www\.)?[\w.-]+\.[a-z]{2,}\S*", t):
        return "Other URL"
    if BRAND.search(t):
        return "Branded (long / contextual)"
    return "Contextual / other"


bl["Anchor Type"] = bl["Anchor Text"].map(anchor_type)

dom_anchor = {}
for d, grp in bl.groupby("Referring Domain"):
    types = Counter(grp["Anchor Type"])
    spam = grp[grp["Anchor Type"].isin(SPAMMY_ANCHORS)]
    third = grp[grp["Anchor Type"] == "Third-party brand (seoexpress / sitetosocial)"]
    txt = grp["Anchor Text"].fillna("").astype(str).str.strip()
    txt = txt[txt != ""]
    ex = (spam if len(spam) else grp).iloc[0]
    outb = pd.to_numeric(grp["Outbound Links on Page"], errors="coerce")
    dom_anchor[d] = {
        "backlinks": len(grp),
        "anchors": int(txt.nunique()),
        "top_anchor": txt.value_counts().index[0] if len(txt) else "(empty / image link)",
        "anchor_mix": ", ".join(f"{k} ×{v}" for k, v in types.most_common()),
        "spam_anchors": len(spam),
        "third_party": len(third),
        "spam_example": spam["Anchor Text"].iloc[0] if len(spam) else None,
        "sample_url": ex["Linking Page URL"],
        "sample_title": ex["Linking Page Title"],
        "max_outbound": int(outb.max()) if outb.notna().any() else None,
        "category": next((c for c in grp["Page Category"] if isinstance(c, str) and c), ""),
        "dofollow": int((grp["Link Type"] == "Dofollow").sum()),
        "all_404": bool(grp["Linking Page Title"].fillna("").astype(str).str.contains("ERROR 404", case=False).all()),
    }

# ---------------------------------------------------------------- domain rules
OWN = {"justdrivemedia.notion.site", "justdrivemedia.vercel.app"}
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

CLUSTER_DESC = {
    "Numeric .xyz network": "throwaway numbered .xyz domain, mass-registered only to point links",
    "SEOExpress / Link-Baron / Outrank-HQ .store network": "keyword-named .store site from one link-selling network",
    "'SEO checker' tool-spam domains": "fake 'DA/PA/backlink checker' site that auto-generates a page for every domain",
    ".shop rank/boost link farm": "auto-generated .shop link-farm site (…ranklab / …boosthub / …linkpro family) created in bulk",
    "Paid-backlink seller network (203.161.54.114)": "backlink-selling site on 203.161.54.114 with dozens of sister sites",
    "Auto-generated site network (104.207.79.x)": "auto-generated content site on 104.207.79.x with dozens of sister sites",
    "Blogspot PBN / spam blogs": "throwaway Blogspot blog used as a private blog network",
    "Low-quality web directories": "mass-submission web directory with no editorial review",
    "Casino / pharma / adult spam": "casino, gambling or pharmacy spam site",
    "Website-info scraper network (shared IP)": "'website worth / domain info' scraper on a shared spam IP",
    ".link/.info SEO spam": "SEO-keyword .link/.info domain selling backlinks",
    "Hacked / thin sites carrying spam-copy links": "thin or hacked site used to host keyword-stuffed spam links",
    "Link-farm pages (500+ outbound links)": "page listing hundreds or thousands of unrelated outbound links (link farm)",
    "Other spam": "low-quality site with no genuine audience, used in the link-spam campaign",
}


def cluster(d, ip):
    if re.fullmatch(r"\d+\.xyz", d):
        return "Numeric .xyz network"
    if re.search(r"seoexpress|link-baron|outrank-hq|rank-forge", d) or (d.endswith(".store") and d.count("-") >= 3):
        return "SEOExpress / Link-Baron / Outrank-HQ .store network"
    if re.search(r"checker|dapa|dadr|drur|tfchecker|pageauthority|backlinkanalys|backlinkaudit|"
                 r"backlinkreport|backlinkfinder|linkprofile|inboundlinks|finddomainbacklinks|"
                 r"checkbacklinks|findbacklinks|lookup", d):
        return "'SEO checker' tool-spam domains"
    if d.endswith(".shop") and re.search(r"boosthub|ranklab|linkpro|seolink|seohub|crawl|index|serp|rank|seo|link|anchor|authority|search", d):
        return ".shop rank/boost link farm"
    if ip == "203.161.54.114":
        return "Paid-backlink seller network (203.161.54.114)"
    if ip in {"104.207.79.34", "104.207.79.38"}:
        return "Auto-generated site network (104.207.79.x)"
    if d.endswith(".blogspot.com"):
        return "Blogspot PBN / spam blogs"
    if re.search(r"directory|directoy", d):
        return "Low-quality web directories"
    if re.search(r"casino|gambl|poker|slot|gacor|ufabet|betwinner|doxycycline|erythromycin|psilocybin", d):
        return "Casino / pharma / adult spam"
    if ip in SPAM_IPS:
        return "Website-info scraper network (shared IP)"
    if re.search(r"\.link$|\.info$", d) and re.search(r"seo|backlink|rank", d):
        return ".link/.info SEO spam"
    an = dom_anchor.get(d)
    if an and an["spam_anchors"]:
        return "Hacked / thin sites carrying spam-copy links"
    if an and an["max_outbound"] is not None and an["max_outbound"] >= 500:
        return "Link-farm pages (500+ outbound links)"
    return "Other spam"


def q(s, n=110):
    s = " ".join(str(s).split())
    return "“" + (s if len(s) <= n else s[:n].rstrip() + "…") + "”"


def assess(d):
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
        ev.append("Numbered throwaway .xyz domain with no real website behind it")
    if words:
        ev.append("Domain name is built from SEO / link-selling keywords")
    if spam_anchor:
        ev.append(f"Anchor text is keyword-stuffed SEO sales copy, e.g. {q(an['spam_example'])} "
                  f"({an['spam_anchors']} of {an['backlinks']} links)")
    if third:
        ev.append("Anchors promote unrelated third-party brands (seoexpress / sitetosocial) – a hallmark of automated link spam")
    if farm:
        ev.append(f"Linking page carries {an['max_outbound']:,} outbound links – a link farm, not an editorial page")
    if flagged:
        ev.append("Ahrefs classifies the domain as spam")
    if ip_net:
        ev.append(f"Hosted on {ip}, an IP shared by dozens of other spam domains linking to the site")
    if blogspot and (ascore or 0) <= 3:
        ev.append("Throwaway Blogspot blog with Semrush Authority Score ≤3")
    if an and an["all_404"]:
        ev.append("Linking pages have 'ERROR 404' titles – doorway / cloaked pages")
    if inflated_dr:
        ev.append(f"DR {dr:g} but zero organic traffic – authority is artificially inflated")
    if bad_tld and no_traffic:
        ev.append("Low-trust TLD commonly used for spam, with no organic traffic")

    metrics = []
    if a is not None:
        metrics.append(f"DR {dr:g}, {int(traffic):,} organic visits/mo, {int(a['kw']):,} ranking keywords")
    if s is not None:
        metrics.append(f"Semrush AS {int(ascore)}")
    metric_txt = "; ".join(metrics) or "no metrics reported"
    anchor_txt = f" Anchor used: {q(an['top_anchor'], 80)}." if an else ""

    if d in OWN:
        return "Own Property", f"Client-owned web property (Notion / Vercel).{anchor_txt} Action: keep.", ev

    if traffic is not None and traffic >= 1000 and not words and not spam_anchor:
        if flagged:
            return ("Review", f"Real, established site ({metric_txt}) that Ahrefs nevertheless flags as spam – most likely an "
                              f"auto-generated company/profile page, not an attack link.{anchor_txt} "
                              "Action: keep; disavow only if the page itself looks manipulative.", ev)
        return "Healthy", f"Genuine, established website ({metric_txt}).{anchor_txt} Action: keep.", ev
    if traffic is None and ascore is not None and ascore >= 35 and not spam_anchor:
        return "Healthy", f"Genuine, authoritative website ({metric_txt}).{anchor_txt} Action: keep.", ev

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
    if strong:
        cl = cluster(d, ip)
        text = (f"SPAM – {CLUSTER_DESC[cl]}. " + ". ".join(ev) + f". Metrics: {metric_txt}."
                + ("" if spam_anchor else anchor_txt) + " Action: disavow (domain-level).")
        return "Spam – Disavow", text, ev

    if traffic is not None and traffic >= 100 and not flagged and not spam_anchor:
        return "Healthy", f"Real website with organic visibility ({metric_txt}).{anchor_txt} Action: keep.", ev
    if flagged or words or spam_anchor or third:
        return ("Review", f"Mixed signals: {'. '.join(ev) or 'borderline signals'}. However, the domain also shows genuine "
                          f"quality ({metric_txt}).{anchor_txt} Action: open the linking page; disavow only if it is "
                          "clearly manipulative.", ev)
    if s is not None and a is None and (ascore or 0) <= 3 and s["first_seen"] >= pd.Timestamp("2026-06-01"):
        return ("Review", f"Zero-authority domain (Semrush AS {int(ascore)}, not indexed by Ahrefs) that first linked "
                          f"during the spam wave, but shows no hard spam signal.{anchor_txt} Action: check the page; "
                          "disavow if it is a thin / auto-generated site.", ev)
    return ("Low Value", f"Weak but harmless link – low authority and little traffic ({metric_txt}); no spam signals "
                         f"found.{anchor_txt} Action: leave as is.", ev)


rows = []
for d in sorted(known):
    a = ah.loc[d] if d in ah.index else None
    s = se.loc[d] if d in se.index else None
    an = dom_anchor.get(d)
    label, reason, ev = assess(d)
    first = min(x for x in [a["first_seen"] if a is not None else None,
                            s["first_seen"] if s is not None else None] if x is not None)
    since = first >= SINCE
    score = 0 if label in ("Healthy", "Own Property") else min(100, 15 * len(ev) + (20 if label == "Spam – Disavow" else 0))
    rows.append({
        "Domain": d,
        "Verdict": label,
        "Spam Score (0-100)": score,
        "Why (evidence)": reason,
        "Spam Network / Cluster": cluster(d, s["ip"] if s is not None else None) if label == "Spam – Disavow" else "",
        "Signals Found": len(ev),
        "First Seen": first,
        "Added Since Apr 1 2026": "Yes" if since else "No",
        "In Disavow File": "Yes" if (label == "Spam – Disavow" and since) else "No",
        "Top Anchor Text": an["top_anchor"] if an else "No live backlink returned by either tool",
        "Anchor Mix": an["anchor_mix"] if an else "",
        "Spammy Anchors": an["spam_anchors"] if an else 0,
        "Distinct Anchors": an["anchors"] if an else 0,
        "Backlinks Analysed": an["backlinks"] if an else 0,
        "Example Linking Page": an["sample_url"] if an else "",
        "Linking Page Title": an["sample_title"] if an else "",
        "Max Outbound Links on Page": an["max_outbound"] if an else None,
        "Page Category": an["category"] if an else "",
        "Source": "Both" if (a is not None and s is not None) else ("Ahrefs" if a is not None else "Semrush"),
        "Ahrefs DR": float(a["dr"]) if a is not None else None,
        "Ahrefs Links": int(a["links"]) if a is not None else None,
        "Ahrefs Dofollow Links": int(a["dofollow"]) if a is not None else None,
        "Ahrefs Spam Flag": ("Yes" if int(a["is_spam"]) else "No") if a is not None else "",
        "Ahrefs Organic Traffic": int(a["traffic"]) if a is not None else None,
        "Ahrefs Ranking Keywords": int(a["kw"]) if a is not None else None,
        "Semrush Authority Score": int(s["domain_ascore"]) if s is not None else None,
        "Semrush Backlinks": int(s["backlinks_num"]) if s is not None else None,
        "Semrush Last Seen": s["last_seen"] if s is not None else None,
        "IP": s["ip"] if s is not None else "",
        "Country": (s["country"].upper() if isinstance(s["country"], str) else "") if s is not None else "",
    })

df = pd.DataFrame(rows)
ORDER = ["Spam – Disavow", "Review", "Low Value", "Healthy", "Own Property"]
df["_o"] = df["Verdict"].map(ORDER.index)
df = df.sort_values(["_o", "First Seen", "Domain"], ascending=[True, False, True]).drop(columns="_o").reset_index(drop=True)
bl["Domain Verdict"] = bl["Referring Domain"].map(dict(zip(df["Domain"], df["Verdict"])))
bl = bl.sort_values(["Referring Domain", "Tool", "First Seen"]).reset_index(drop=True)

# ---------------------------------------------------------------- disavow file
dis = df[df["In Disavow File"] == "Yes"].sort_values("Domain")
lines = [
    "# Disavow file for justdrivemedia.com",
    f"# Prepared {PULL_DATE} from Ahrefs + Semrush referring-domain and backlink exports",
    "# Scope: spam referring domains first seen on or after 2026-04-01",
    f"# {len(dis)} domains",
    "# Upload at https://search.google.com/search-console/disavow-links (Domain property).",
    "# NOTE: uploading REPLACES any existing disavow file - merge with the current one first.",
    "",
] + [f"domain:{d}" for d in dis["Domain"]]
(HERE / "justdrivemedia-disavow.txt").write_text("\n".join(lines) + "\n")

# ---------------------------------------------------------------- workbook helpers
FONT = "Arial"
FILL = {"Spam – Disavow": "F4C7C3", "Review": "FCE8B2", "Low Value": "EDEDED",
        "Healthy": "B7E1CD", "Own Property": "C9DAF8"}
INK = {"Spam – Disavow": "9C0006", "Review": "7F6000", "Low Value": "434343",
       "Healthy": "274E13", "Own Property": "1C4587"}
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
NUM, DATE, PCT = "#,##0", "yyyy-mm-dd", "0.0%"


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


wb = Workbook()

# ---------------------------------------------------------------- Summary
sm = wb.active
sm.title = "Summary"
since_df = df[df["Added Since Apr 1 2026"] == "Yes"]
spam_since = int((since_df.Verdict == "Spam – Disavow").sum())
sm["A1"] = "justdrivemedia.com – Backlink Audit"
sm["A1"].font = TITLE
sm["A2"] = (f"Data pulled {PULL_DATE} from Ahrefs and Semrush: {len(df):,} unique referring domains and "
            f"{len(bl):,} backlinks analysed (anchor text, linking page, outbound links, hosting, authority, traffic).")
sm["A2"].font = Font(name=FONT, size=10, italic=True, color="595959")

MEANING = {
    "Spam – Disavow": "Manipulative / negative-SEO link source. All first seen since Apr 1 2026 are in the disavow file.",
    "Review": "Mixed signals – check the linking page by hand. Not in the disavow file.",
    "Low Value": "Weak but harmless (tiny blogs, small directories). Leave as is.",
    "Healthy": "Genuine, authoritative or relevant site. Keep.",
    "Own Property": "Client-owned property. Keep.",
}
r = 4
hdr(sm, r, ["Verdict", "All Domains", "Added Since Apr 1 2026", "In Disavow File", "What it means / action"])
for lab in ORDER:
    r += 1
    vals = [lab, int((df.Verdict == lab).sum()), int((since_df.Verdict == lab).sum()),
            int(((df.Verdict == lab) & (df["In Disavow File"] == "Yes")).sum()), MEANING[lab]]
    for c, v in enumerate(vals, 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.fill, cell.font, cell.border = FILLS[lab], BODY, BORDER
        if c in (2, 3, 4):
            cell.number_format = NUM
    sm.cell(row=r, column=1).font = Font(name=FONT, size=10, bold=True, color=INK[lab])
r += 1
for c, v in enumerate(["Total", len(df), len(since_df), len(dis), ""], 1):
    cell = sm.cell(row=r, column=c, value=v)
    cell.font, cell.border = BOLD, BORDER
    if c in (2, 3, 4):
        cell.number_format = NUM

r += 2
sm.cell(row=r, column=1, value="Key findings").font = H2
spam_bl = bl[bl["Anchor Type"].isin(SPAMMY_ANCHORS)]
sep_new = int((df["First Seen"].dt.strftime("%Y-%m") == "2026-09").sum())
healthy_n = int((df.Verdict == "Healthy").sum())
findings = [
    f"justdrivemedia.com is the target of a large negative-SEO link attack: {spam_since:,} of the {len(since_df):,} "
    f"referring domains added since April 1 2026 ({spam_since / len(since_df):.0%}) are spam.",
    f"The attack accelerated sharply in September 2026 – {sep_new:,} new referring domains that month alone, almost all "
    "auto-generated .shop, .xyz, .store and fake 'SEO checker' sites.",
    f"{len(spam_bl):,} of {len(bl):,} backlinks ({len(spam_bl) / len(bl):.0%}) use keyword-stuffed sales copy as anchor text "
    "(e.g. “high quality pbn backlinks for justdrivemedia.com…”, “justdrivemedia.com delivers da boost packages…”), "
    "framing the brand as a link seller – a pattern Google's spam systems penalise.",
    "The spam copy reuses the client's own brand names (justdrivemedia.com and sister brand Mighty PR / mightypr.com) "
    "inside link-selling sentences, plus fake reviews naming seoexpress.org – an automated negative-SEO template.",
    f"Spam linking pages carry a median of {int(pd.to_numeric(spam_bl['Outbound Links on Page'], errors='coerce').median()):,} "
    "outbound links each – classic link farms with no editorial value.",
    f"The genuine profile is intact: {healthy_n} healthy sites (e.g. crunchbase.com, inc.com, prweb.com, msu.edu, g2.com, "
    "squarespace.com, pr.com) link naturally with branded anchors and must NOT be disavowed.",
]
for f in findings:
    r += 1
    c = sm.cell(row=r, column=1, value="•  " + f)
    c.font, c.alignment = BODY, WRAP
    sm.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    sm.row_dimensions[r].height = 30

r += 2
sm.cell(row=r, column=1, value="Spam networks in the disavow file").font = H2
r += 1
hdr(sm, r, ["Network / cluster", "Domains", "Description"])
for cl, n in dis["Spam Network / Cluster"].value_counts().items():
    r += 1
    for c, v in enumerate([cl, int(n), CLUSTER_DESC[cl]], 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.font, cell.border = BODY, BORDER
    sm.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)

r += 2
sm.cell(row=r, column=1, value="Anchor text profile (all backlinks)").font = H2
r += 1
hdr(sm, r, ["Anchor type", "Backlinks", "Share of backlinks", "Referring domains"])
at = bl.groupby("Anchor Type").agg(n=("Anchor Type", "size"), d=("Referring Domain", "nunique")).sort_values("n", ascending=False)
for t, rec in at.iterrows():
    r += 1
    for c, v in enumerate([t, int(rec.n), float(rec.n) / len(bl), int(rec.d)], 1):
        cell = sm.cell(row=r, column=c, value=v)
        cell.font, cell.border = BODY, BORDER
        cell.number_format = PCT if c == 3 else NUM
        if t in SPAMMY_ANCHORS:
            cell.fill = FILLS["Spam – Disavow"]

r += 2
sm.cell(row=r, column=1, value="Next steps").font = H2
steps = [
    "1. Download the current disavow file from Google Search Console (if one exists) and merge it with justdrivemedia-disavow.txt.",
    "2. Upload the merged file at search.google.com/search-console/disavow-links for the justdrivemedia.com property.",
    "3. Manually check the 'Review' domains (filter Verdict on the Domain Audit tab) and add any clearly manipulative ones.",
    "4. Optional: also disavow the pre-April spam domains (Verdict = Spam, Added Since Apr 1 2026 = No) for a full clean-up.",
    "5. Re-run this audit monthly while the attack continues – new spam domains are still appearing daily.",
]
for sline in steps:
    r += 1
    sm.cell(row=r, column=1, value=sline).font = BODY
    sm.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)

r += 2
sm.cell(row=r, column=1, value="Colour legend").font = H2
for lab in ORDER:
    r += 1
    cell = sm.cell(row=r, column=1, value=lab)
    cell.fill, cell.border = FILLS[lab], BORDER
    cell.font = Font(name=FONT, size=10, bold=True, color=INK[lab])
    sm.cell(row=r, column=2, value=MEANING[lab]).font = BODY
    sm.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
for col, w in zip("ABCDE", (46, 14, 22, 16, 84)):
    sm.column_dimensions[col].width = w

# ---------------------------------------------------------------- Domain Audit
wd = wb.create_sheet("Domain Audit")
write_table(
    wd, df,
    widths={"Domain": 36, "Verdict": 15, "Spam Score (0-100)": 10, "Why (evidence)": 95, "Spam Network / Cluster": 32,
            "Signals Found": 9, "First Seen": 12, "Top Anchor Text": 45, "Anchor Mix": 42, "Example Linking Page": 45,
            "Linking Page Title": 40, "Page Category": 30, "IP": 15},
    color_col="Verdict", wrap_cols=("Why (evidence)",),
    fmt={"First Seen": DATE, "Semrush Last Seen": DATE, "Ahrefs Organic Traffic": NUM,
         "Ahrefs Ranking Keywords": NUM, "Max Outbound Links on Page": NUM, "Semrush Backlinks": NUM},
)

# ---------------------------------------------------------------- Anchor Analysis
aa = (bl.assign(_a=bl["Anchor Text"].fillna("").astype(str).str.strip().replace("", "(empty / image link)"))
        .groupby("_a")
        .agg(**{"Anchor Type": ("Anchor Type", "first"),
                "Backlinks": ("_a", "size"),
                "Referring Domains": ("Referring Domain", "nunique"),
                "Spam Domains Using It": ("Referring Domain",
                                          lambda v: int(bl.loc[v.index, "Domain Verdict"].eq("Spam – Disavow")
                                                        .groupby(v).any().sum())),
                "Example Referring Domain": ("Referring Domain", "first")})
        .reset_index().rename(columns={"_a": "Anchor Text"})
        .sort_values(["Backlinks", "Anchor Text"], ascending=[False, True]))
aa["Share of Backlinks"] = aa["Backlinks"] / len(bl)
aa["Verdict"] = aa["Anchor Type"].map(lambda t: "Spam – Disavow" if t in SPAMMY_ANCHORS
                                      else ("Review" if t.startswith("Third-party") else "Healthy"))
aa = aa[["Anchor Text", "Anchor Type", "Verdict", "Backlinks", "Share of Backlinks", "Referring Domains",
         "Spam Domains Using It", "Example Referring Domain"]]
wa = wb.create_sheet("Anchor Analysis")
write_table(wa, aa, widths={"Anchor Text": 90, "Anchor Type": 36, "Verdict": 15, "Example Referring Domain": 34},
            color_col="Verdict", wrap_cols=("Anchor Text",), fmt={"Share of Backlinks": "0.00%", "Backlinks": NUM})

# ---------------------------------------------------------------- All Backlinks
bcols = ["Referring Domain", "Domain Verdict", "Tool", "Anchor Text", "Anchor Type", "Link Type", "Linking Page URL",
         "Linking Page Title", "Target URL", "Outbound Links on Page", "Page Category", "Text Around Link", "First Seen"]
wbl = wb.create_sheet("All Backlinks")
write_table(wbl, bl[bcols],
            widths={"Referring Domain": 32, "Domain Verdict": 15, "Tool": 9, "Anchor Text": 55, "Anchor Type": 30,
                    "Link Type": 10, "Linking Page URL": 55, "Linking Page Title": 45, "Target URL": 38,
                    "Page Category": 30, "Text Around Link": 60},
            color_col="Domain Verdict", fmt={"First Seen": DATE, "Outbound Links on Page": NUM})

# ---------------------------------------------------------------- Disavow List
dl = dis.assign(**{"Disavow Line": "domain:" + dis["Domain"]})[
    ["Disavow Line", "Domain", "Verdict", "First Seen", "Spam Network / Cluster", "Top Anchor Text", "Why (evidence)"]]
wdl = wb.create_sheet("Disavow List")
write_table(wdl, dl, widths={"Disavow Line": 44, "Domain": 38, "Verdict": 15, "Spam Network / Cluster": 32,
                             "Top Anchor Text": 45, "Why (evidence)": 95},
            color_col="Verdict", wrap_cols=("Why (evidence)",), fmt={"First Seen": DATE})

# ---------------------------------------------------------------- Methodology
wm = wb.create_sheet("Methodology")
wm["A1"] = "How each domain was assessed"
wm["A1"].font = TITLE
cov = sum(d in dom_anchor for d in df.Domain)
method = [
    ("Data sources", f"Ahrefs Site Explorer (live referring domains + all {len(abl):,} live backlinks) and Semrush Backlink "
                     f"Analytics (referring domains + {len(sbl):,} backlinks), pulled {PULL_DATE}. Domains were merged and "
                     "de-duplicated; www / sub-domain variants were mapped to the referring domain."),
    ("First Seen", "Earliest first-seen date reported by either tool. 'Added Since Apr 1 2026' uses this date."),
    ("Spam signals checked", "1) Domain name made of SEO/link keywords  2) Numbered throwaway .xyz domain  "
                             "3) Keyword-stuffed or casino/pharma anchor text  4) Anchors promoting unrelated third-party brands  "
                             "5) Linking page with 500+ outbound links (link farm)  6) Ahrefs spam classification  "
                             "7) Hosting IP shared by a spam network  8) Blogspot blog with AS ≤3  "
                             "9) 'ERROR 404' doorway pages  10) Inflated DR with zero traffic  11) Low-trust TLD with no traffic."),
    ("Protection rule", "A site with ≥1,000 organic visits/mo (Ahrefs) or Semrush AS ≥35 is never auto-disavowed unless its "
                        "anchor text is itself spam; flagged-but-real sites go to 'Review'."),
    ("Spam Score", "15 points per spam signal found, +20 when the verdict is Spam, capped at 100. Healthy / own sites score 0."),
    ("Anchor types", "Branded (Just Drive Media / sister brand Mighty PR), Naked URL, Generic (e.g. 'website'), Empty/image, Contextual, Other URL, Third-party brand, "
                     "Foreign-language, Spam – keyword-stuffed SEO sales copy, Spam – casino/pharma/exam-dump."),
    ("Disavow file", "Domain-level entries (domain:example.com) for every Spam domain first seen on/after 2026-04-01. "
                     "Blogspot spam is disavowed per sub-domain, never blogspot.com itself."),
    ("Coverage", f"Anchor-level evidence was available for {cov:,} of {len(df):,} domains. The remaining "
                 f"{len(df) - cov:,} are domains the tools list as referring but returned no live backlink row for; they "
                 "were assessed on domain-level metrics and name / IP / TLD signals."),
    ("Brief vs data", "The brief quoted 439 new referring domains since April. Live data on the pull date shows far more, "
                      "because the spam wave accelerated heavily in September 2026."),
    ("Upload warning", "Google's disavow upload REPLACES the existing file – merge with any current file before uploading."),
    ("No formulas", "All figures are stored as values so the workbook opens identically, with no errors, in any spreadsheet app."),
]
for i, (k, v) in enumerate(method, start=3):
    kc = wm.cell(row=i, column=1, value=k)
    kc.font, kc.alignment = BOLD, WRAP
    vc = wm.cell(row=i, column=2, value=v)
    vc.font, vc.alignment = BODY, WRAP
    wm.row_dimensions[i].height = 48
wm.column_dimensions["A"].width = 24
wm.column_dimensions["B"].width = 120

out = HERE / "justdrivemedia-backlink-audit.xlsx"
wb.save(out)
print(df["Verdict"].value_counts().to_string())
print("since-April:", len(since_df), "disavow:", len(dis), "backlinks:", len(bl), "anchor coverage:", cov)
print("saved", out)
