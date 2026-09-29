"""Build the justdrivemedia.com backlink audit workbook + Google disavow file.

Inputs (raw/): Ahrefs live referring domains (ahrefs_p*.csv) and Semrush
referring domains (semrush_refdomains.csv), both pulled 2026-09-29.
"""
import glob
import re
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).parent
RAW = HERE / "raw"
PULL_DATE = "2026-09-29"
SINCE = pd.Timestamp("2026-04-01")

# ---------------------------------------------------------------- load
AH_COLS = ["domain", "dr", "first_seen", "links", "dofollow", "is_spam", "traffic", "kw"]
ah = pd.concat([pd.read_csv(f, header=0, names=AH_COLS)
                for f in sorted(glob.glob(str(RAW / "ahrefs_p*.csv")))])
ah["first_seen"] = pd.to_datetime(ah["first_seen"].str[:10]).dt.normalize()
ah = ah.drop_duplicates("domain").set_index("domain")

se = pd.read_csv(RAW / "semrush_refdomains.csv", sep=";")
se["first_seen"] = pd.to_datetime(se["first_seen"], unit="s").dt.normalize()
se["last_seen"] = pd.to_datetime(se["last_seen"], unit="s").dt.normalize()
se = se.drop_duplicates("domain").set_index("domain")

domains = sorted(set(ah.index) | set(se.index))

# ---------------------------------------------------------------- rules
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
    r"websiteworth|websitesworth|worthchecker|webworth|shorten|urls-|byteshort|buzzshrink",
    re.I,
)
SPAM_TLDS = (".shop", ".store", ".xyz", ".online", ".site", ".space", ".website", ".link",
             ".info", ".top", ".icu", ".cfd", ".sbs", ".monster", ".mom", ".click", ".cv",
             ".art", ".pro", ".lol", ".party", ".live", ".wiki", ".homes", ".forum", ".world",
             ".club", ".fyi", ".today", ".co.in", ".in", ".bz", ".lc", ".cc")
# Shared hosting IPs that serve dozens of the spam domains (from Semrush)
SPAM_IPS = {"104.207.79.34", "104.207.79.38", "203.161.54.114", "195.20.19.178",
            "118.139.181.85", "118.139.176.46", "118.139.161.199", "118.139.178.200",
            "118.139.177.45", "118.139.181.255", "184.168.115.60", "67.223.118.29"}


def cluster(d: str, ip: str | None) -> str:
    if re.fullmatch(r"\d+\.xyz", d):
        return "Numeric .xyz network"
    if re.search(r"seoexpress|link-baron|outrank-hq|rank-forge", d) or (
        d.endswith(".store") and d.count("-") >= 3):
        return "SEOExpress / Link-Baron / Outrank-HQ .store network"
    if re.search(r"checker|dapa|dadr|drur|tfchecker|pageauthority|backlinkanalys|backlinkaudit|"
                 r"backlinkreport|backlinkfinder|linkprofile|inboundlinks|finddomainbacklinks|"
                 r"checkbacklinks|findbacklinks|lookup", d):
        return "'SEO checker' tool-spam domains"
    if d.endswith(".shop") and re.search(r"boosthub|ranklab|linkpro|seolink|seohub|crawl|index|"
                                          r"serp|rank|seo|link|anchor|authority|search", d):
        return ".shop rank/boost link farm"
    if ip in {"203.161.54.114"}:
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
    return "Other spam"


def classify(d: str):
    a = ah.loc[d] if d in ah.index else None
    s = se.loc[d] if d in se.index else None
    traffic = float(a["traffic"]) if a is not None else None
    dr = float(a["dr"]) if a is not None else None
    ascore = float(s["domain_ascore"]) if s is not None else None
    ip = s["ip"] if s is not None else None
    flagged = a is not None and int(a["is_spam"]) == 1
    words = bool(SPAM_WORDS.search(d))
    bad_tld = d.endswith(SPAM_TLDS)
    ip_net = ip in SPAM_IPS
    blogspot = d.endswith(".blogspot.com")

    if d in OWN:
        return "Own Property", "Client-owned web property (Notion / Vercel) – keep"

    # Established sites with real organic traffic are kept even if Ahrefs flags them
    if traffic is not None and traffic >= 1000 and not words:
        if flagged:
            return "Review", f"Ahrefs spam flag, but real site ({int(traffic):,} organic visits/mo) – don't disavow"
        return "Healthy", f"Authoritative site – DR {dr:g}, {int(traffic):,} organic visits/mo"
    if traffic is None and ascore is not None and ascore >= 35:
        return "Healthy", f"Authoritative site (Semrush AS {ascore:g})"

    reasons = []
    if re.fullmatch(r"\d+\.xyz", d):
        reasons.append("numeric .xyz throwaway domain")
    if words:
        reasons.append("spam keywords in domain name")
    if flagged:
        reasons.append("Ahrefs flags domain as spam")
    if ip_net:
        reasons.append(f"hosted on spam-network IP {ip}")
    if blogspot and s is not None and ascore <= 3:
        reasons.append("blogspot spam blog (AS ≤3)")
    no_traffic = (traffic is not None and traffic < 100) or (traffic is None and (ascore or 0) < 10)
    if bad_tld and no_traffic:
        reasons.append("low-trust TLD with no organic traffic")

    low_traffic = (traffic is not None and traffic < 500) or (traffic is None and (ascore or 0) < 20)
    inflated_dr = bad_tld and traffic == 0 and (dr or 0) >= 30
    if inflated_dr:
        reasons.append(f"inflated DR {dr:g} with zero organic traffic")
    # Some genuine quality signal: real traffic, ranking keywords or decent Semrush AS
    quality = ((traffic or 0) >= 100 or (a is not None and a["kw"] >= 10) or (ascore or 0) >= 20
               or (dr or 0) >= 20 and s is None and d.endswith((".com", ".io", ".ai", ".co", ".org", ".net"))
               and not re.search(r"directory|directoy|backlink|seo", d))
    strong = (
        re.fullmatch(r"\d+\.xyz", d)
        or (words and low_traffic and (flagged or not quality))
        or inflated_dr
        or (ip_net and low_traffic and not quality)
        or (flagged and no_traffic)
        or (blogspot and s is not None and ascore <= 3)
        or (bad_tld and (traffic or 0) < 20 and (ascore or 0) < 10 and (flagged or words or ip_net or (dr or 0) < 5))
    )
    if strong:
        return "Spam – Disavow", "; ".join(reasons).capitalize()

    if traffic is not None and traffic >= 100:
        if flagged:
            return "Review", f"Ahrefs spam flag but has {int(traffic):,} organic visits/mo – manual check"
        return "Healthy", f"Real site – DR {dr:g}, {int(traffic):,} organic visits/mo"
    wave = s is not None and a is None and ascore <= 3 and s["first_seen"] >= pd.Timestamp("2026-06-01")
    if wave:
        return "Review", "Zero-authority domain (Semrush AS ≤3, Semrush-only) first seen during the spam wave – likely spam, verify before disavowing"
    if flagged or words:
        return "Review", ("; ".join(reasons) or "Borderline signals").capitalize() + " – manual check"
    return "Low Value", "Low authority / little traffic, but no spam signals – leave as is"


rows = []
for d in domains:
    a = ah.loc[d] if d in ah.index else None
    s = se.loc[d] if d in se.index else None
    label, reason = classify(d)
    fs = [x for x in [a["first_seen"] if a is not None else None,
                      s["first_seen"] if s is not None else None] if x is not None]
    first = min(fs)
    since = first >= SINCE
    rows.append({
        "Domain": d,
        "Label": label,
        "Reason": reason,
        "Spam Cluster": cluster(d, s["ip"] if s is not None else None) if label == "Spam – Disavow" else "",
        "Source": "Both" if (a is not None and s is not None) else ("Ahrefs" if a is not None else "Semrush"),
        "First Seen (earliest)": first.date(),
        "Added Since Apr 1 2026": "Yes" if since else "No",
        "In Disavow File": "Yes" if (label == "Spam – Disavow" and since) else "No",
        "Ahrefs DR": float(a["dr"]) if a is not None else None,
        "Ahrefs Links": int(a["links"]) if a is not None else None,
        "Ahrefs Dofollow": int(a["dofollow"]) if a is not None else None,
        "Ahrefs Spam Flag": ("Yes" if int(a["is_spam"]) else "No") if a is not None else None,
        "Ahrefs Organic Traffic": int(a["traffic"]) if a is not None else None,
        "Ahrefs Organic Keywords": int(a["kw"]) if a is not None else None,
        "Ahrefs First Seen": a["first_seen"].date() if a is not None else None,
        "Semrush AS": int(s["domain_ascore"]) if s is not None else None,
        "Semrush Backlinks": int(s["backlinks_num"]) if s is not None else None,
        "Semrush First Seen": s["first_seen"].date() if s is not None else None,
        "Semrush Last Seen": s["last_seen"].date() if s is not None else None,
        "IP": s["ip"] if s is not None else None,
        "Country": (s["country"].upper() if isinstance(s["country"], str) else None) if s is not None else None,
    })

df = pd.DataFrame(rows)
order = {"Spam – Disavow": 0, "Review": 1, "Low Value": 2, "Healthy": 3, "Own Property": 4}
df = df.sort_values(["Label", "First Seen (earliest)"], key=lambda c: c.map(order) if c.name == "Label" else c,
                    ascending=[True, False]).reset_index(drop=True)

# ---------------------------------------------------------------- disavow
dis = df[df["In Disavow File"] == "Yes"].sort_values("Domain")
lines = [
    "# Disavow file for justdrivemedia.com",
    f"# Prepared {PULL_DATE} from Ahrefs + Semrush referring-domain exports",
    "# Scope: spam referring domains first seen on or after 2026-04-01",
    f"# {len(dis)} domains",
    "# Upload at https://search.google.com/search-console/disavow-links (Domain property).",
    "# NOTE: uploading REPLACES any existing disavow file - merge with the current one first.",
    "",
] + [f"domain:{d}" for d in dis["Domain"]]
(HERE / "justdrivemedia-disavow.txt").write_text("\n".join(lines) + "\n")

# ---------------------------------------------------------------- workbook
FONT = "Arial"
FILL = {
    "Spam – Disavow": "F4C7C3",
    "Review": "FCE8B2",
    "Low Value": "EDEDED",
    "Healthy": "B7E1CD",
    "Own Property": "C9DAF8",
}
LABEL_FONT = {
    "Spam – Disavow": "9C0006",
    "Review": "7F6000",
    "Low Value": "434343",
    "Healthy": "274E13",
    "Own Property": "1C4587",
}
HDR_FILL = PatternFill("solid", start_color="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY = Font(name=FONT, size=10)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# --- All domains sheet
ws = wb.active
ws.title = "All Referring Domains"
cols = list(df.columns)
ws.append(cols)
for c in range(1, len(cols) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for r in df.itertuples(index=False):
    ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in r])
for i, lab in enumerate(df["Label"], start=2):
    fill = PatternFill("solid", start_color=FILL[lab])
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=i, column=c)
        cell.fill, cell.font, cell.border = fill, BODY, BORDER
    ws.cell(row=i, column=2).font = Font(name=FONT, size=10, bold=True, color=LABEL_FONT[lab])
widths = {"Domain": 44, "Label": 16, "Reason": 58, "Spam Cluster": 40, "Source": 9}
for c, name in enumerate(cols, start=1):
    ws.column_dimensions[get_column_letter(c)].width = widths.get(name, 13)
    if "Seen" in name:
        for rr in range(2, len(df) + 2):
            ws.cell(row=rr, column=c).number_format = "yyyy-mm-dd"
    if name in ("Ahrefs Organic Traffic", "Ahrefs Organic Keywords"):
        for rr in range(2, len(df) + 2):
            ws.cell(row=rr, column=c).number_format = "#,##0"
ws.row_dimensions[1].height = 30
ws.freeze_panes = "B2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(df) + 1}"
last = len(df) + 1

# --- Disavow sheet
wd = wb.create_sheet("Disavow List")
wd.append(["Disavow Line", "Domain", "First Seen", "Spam Cluster", "Reason"])
for c in range(1, 6):
    cell = wd.cell(row=1, column=c)
    cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
for r in dis.itertuples(index=False):
    wd.append([f"domain:{r.Domain}", r.Domain, r._5, r._3, r.Reason])
for rr in range(2, len(dis) + 2):
    for c in range(1, 6):
        cell = wd.cell(row=rr, column=c)
        cell.font, cell.border = BODY, BORDER
        cell.fill = PatternFill("solid", start_color=FILL["Spam – Disavow"])
    wd.cell(row=rr, column=3).number_format = "yyyy-mm-dd"
for c, w in zip("ABCDE", (52, 46, 12, 44, 60)):
    wd.column_dimensions[c].width = w
wd.freeze_panes = "A2"
wd.auto_filter.ref = f"A1:E{len(dis) + 1}"

# --- Summary sheet (formulas reference the data sheet)
sm = wb.create_sheet("Summary", 0)
REF = "'All Referring Domains'"
B = lambda **k: Font(name=FONT, **k)
sm["A1"] = "justdrivemedia.com – Backlink Audit"
sm["A1"].font = B(size=16, bold=True, color="1F3864")
sm["A2"] = f"Data pulled {PULL_DATE} from Ahrefs (live referring domains) and Semrush (referring domains, root domain)."
sm["A2"].font = B(size=10, italic=True, color="595959")

sm["A4"] = "Label"; sm["B4"] = "All Domains"; sm["C4"] = "Added Since Apr 1 2026"; sm["D4"] = "Meaning / Action"
for c in "ABCD":
    sm[f"{c}4"].fill, sm[f"{c}4"].font, sm[f"{c}4"].border = HDR_FILL, HDR_FONT, BORDER
meaning = {
    "Spam – Disavow": "Toxic / manipulative link source. Since-April ones are in the disavow file.",
    "Review": "Mixed signals (e.g. Ahrefs spam flag on a site with real traffic). Check manually; not disavowed.",
    "Low Value": "Weak but harmless (tiny blogs, small directories). Leave as is.",
    "Healthy": "Genuine, authoritative or relevant sites. Keep.",
    "Own Property": "Client-owned properties. Keep.",
}
r0 = 5
for i, lab in enumerate(order):
    r = r0 + i
    sm[f"A{r}"] = lab
    sm[f"B{r}"] = f'=COUNTIF({REF}!$B$2:$B${last},A{r})'
    sm[f"C{r}"] = f'=COUNTIFS({REF}!$B$2:$B${last},A{r},{REF}!$G$2:$G${last},"Yes")'
    sm[f"D{r}"] = meaning[lab]
    for c in "ABCD":
        sm[f"{c}{r}"].fill = PatternFill("solid", start_color=FILL[lab])
        sm[f"{c}{r}"].font, sm[f"{c}{r}"].border = BODY, BORDER
    sm[f"A{r}"].font = B(size=10, bold=True, color=LABEL_FONT[lab])
rt = r0 + len(order)
sm[f"A{rt}"] = "Total"
sm[f"B{rt}"] = f"=SUM(B{r0}:B{rt - 1})"
sm[f"C{rt}"] = f"=SUM(C{r0}:C{rt - 1})"
for c in "ABCD":
    sm[f"{c}{rt}"].font, sm[f"{c}{rt}"].border = B(size=10, bold=True), BORDER

r = rt + 2
sm[f"A{r}"] = "Key figures"; sm[f"A{r}"].font = B(size=12, bold=True, color="1F3864")
kf = [
    ("Domains in disavow file", f'=COUNTIF({REF}!$H$2:$H${last},"Yes")'),
    ("Spam share of since-April domains", f"=IFERROR(C{r0}/C{rt},0)"),
    ("Domains seen by Ahrefs", f'=COUNTIF({REF}!$E$2:$E${last},"Ahrefs")+COUNTIF({REF}!$E$2:$E${last},"Both")'),
    ("Domains seen by Semrush", f'=COUNTIF({REF}!$E$2:$E${last},"Semrush")+COUNTIF({REF}!$E$2:$E${last},"Both")'),
    ("Seen by both tools", f'=COUNTIF({REF}!$E$2:$E${last},"Both")'),
    ("Pre-April spam (not in disavow – optional add)", f'=B{r0}-C{r0}'),
]
for j, (k, f) in enumerate(kf, start=1):
    sm[f"A{r + j}"] = k; sm[f"B{r + j}"] = f
    sm[f"A{r + j}"].font = sm[f"B{r + j}"].font = BODY
    sm[f"A{r + j}"].border = sm[f"B{r + j}"].border = BORDER
sm[f"B{r + 2}"].number_format = "0.0%"

r = r + len(kf) + 2
sm[f"A{r}"] = "Spam clusters (since Apr 1 2026)"; sm[f"A{r}"].font = B(size=12, bold=True, color="1F3864")
sm[f"A{r + 1}"] = "Cluster"; sm[f"B{r + 1}"] = "Domains"
for c in "AB":
    sm[f"{c}{r + 1}"].fill, sm[f"{c}{r + 1}"].font, sm[f"{c}{r + 1}"].border = HDR_FILL, HDR_FONT, BORDER
clusters = df.loc[df["In Disavow File"] == "Yes", "Spam Cluster"].value_counts().index
for j, cl in enumerate(clusters, start=2):
    sm[f"A{r + j}"] = cl
    sm[f"B{r + j}"] = f'=COUNTIFS({REF}!$D$2:$D${last},A{r + j},{REF}!$H$2:$H${last},"Yes")'
    sm[f"A{r + j}"].font = sm[f"B{r + j}"].font = BODY
    sm[f"A{r + j}"].border = sm[f"B{r + j}"].border = BORDER

r = r + len(clusters) + 3
sm[f"A{r}"] = "Method"; sm[f"A{r}"].font = B(size=12, bold=True, color="1F3864")
notes = [
    "1. Exported every live referring domain from Ahrefs (1,443) and Semrush (520 of 533 reported) and merged them on domain.",
    "2. 'First Seen (earliest)' is the earlier of the two tools' first-seen dates; 'Added Since Apr 1 2026' uses that date.",
    "3. Spam = any of: numeric .xyz throwaway domain; SEO/backlink/checker/casino keywords in the domain with no organic "
    "traffic; Ahrefs spam flag with <100 visits/mo; hosted on a known spam-network IP; blogspot spam blog; low-trust TLD with no traffic.",
    "4. Sites with ≥1,000 organic visits/mo (Ahrefs) or Semrush AS ≥35 are never auto-disavowed, even if flagged – they go to Review.",
    "5. The disavow file uses domain-level entries (domain:example.com) only for spam first seen on/after 2026-04-01.",
    "6. Google's upload REPLACES the existing disavow file – merge with any file already in Search Console before uploading.",
    "7. The brief quoted 439 new referring domains since April; live tool data on 2026-09-29 shows many more because the spam "
    "wave (mostly .shop/.xyz/.store networks) accelerated heavily in September.",
]
for j, n in enumerate(notes, start=1):
    sm[f"A{r + j}"] = n
    sm[f"A{r + j}"].font = BODY
    sm[f"A{r + j}"].alignment = Alignment(wrap_text=True, vertical="top")
    sm.merge_cells(f"A{r + j}:D{r + j}")
    sm.row_dimensions[r + j].height = 28

sm.column_dimensions["A"].width = 46
sm.column_dimensions["B"].width = 14
sm.column_dimensions["C"].width = 22
sm.column_dimensions["D"].width = 90

out = HERE / "justdrivemedia-backlink-audit.xlsx"
wb.save(out)
print(df["Label"].value_counts().to_string())
print("since-April:", (df["Added Since Apr 1 2026"] == "Yes").sum(), "disavow:", len(dis))
print("saved", out)
