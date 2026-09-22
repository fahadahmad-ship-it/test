#!/usr/bin/env python3
"""Build NFG Month-1 Foundation Audit 12-tab workbook from collected CSVs."""
import csv, os, glob, re
from datetime import datetime, timezone
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.comments import Comment
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.marker import DataPoint
from openpyxl.chart.shapes import GraphicalProperties

# ---------- static-value helpers (Excel-equivalent, computed in Python) ----------
def _median(vals):
    s = sorted(vals); n = len(s)
    if n == 0: return None
    return s[n//2] if n % 2 else (s[n//2 - 1] + s[n//2]) / 2
def _rank_desc(x, vals):
    return 1 + sum(1 for v in vals if v > x)
def _rank_asc(x, vals):
    return 1 + sum(1 for v in vals if v < x)
def _minmax(x, vals):
    lo, hi = min(vals), max(vals)
    return 0.0 if hi == lo else (x - lo) / (hi - lo)

BASE = "/home/user/test"
DATA = os.path.join(BASE, "data")
SNAP = "2026-09-22"
USD_GBP = 0.79  # FX applied to Semrush USD cost fields -> GBP
OUT = os.path.join(BASE, "NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx")
NFG = "nationalfosteringgroup.co.uk"

# ---------- palette (SUSO accent = deep magenta/purple; competitors neutral) ----------
FONT = "Arial"
CLR_HEADER = "3B1F5C"      # deep purple header band
CLR_HEADERTXT = "FFFFFF"
CLR_NFG = "E9D5FF"         # NFG accent highlight (light purple)
CLR_NFG_STRONG = "7C3AED"  # NFG accent strong
CLR_SUB = "EDE7F6"         # sub-header / summary block fill
CLR_CAVEAT = "FBF3E7"      # caveat box fill (soft warm tint)
# soft, low-saturation flag palette (muted sage / amber / rose) with accessible text
CLR_GREEN = "DCE7D6"; TXT_GREEN = "3F6B4E"   # muted sage
CLR_AMBER = "F2E7CE"; TXT_AMBER = "8A6A3B"   # soft amber
CLR_RED   = "EBD7D7"; TXT_RED   = "8F4B4B"   # soft rose
CLR_GREY = "F2F2F2"
# conditional-format colour-scale stops (muted, low-saturation)
SC_GOOD = "B7CDAC"   # sage  (favourable end)
SC_MID  = "EDE3C8"   # sand  (mid)
SC_BAD  = "E2B9BB"   # rose  (unfavourable end)
# soft data-bar accents
BAR_PURPLE = "B7A3D6"
BAR_BLUE   = "9DB8D2"
BAR_RED    = "D9A7A9"

TAB_EXEC = "B79A46"    # muted gold
TAB_ANALYST = "5B7EA6" # muted blue
TAB_ROLLUP = "5C8A5E"  # muted green
TAB_APPENDIX = "9AA0A6"# soft grey

thin = Side(style="thin", color="D9D9D9")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

def hfont(sz=10, bold=False, color="000000"):
    return Font(name=FONT, size=sz, bold=bold, color=color)

def read_csv(path, delim=None):
    with open(path, newline="", encoding="utf-8") as f:
        sample = f.read(2048); f.seek(0)
        if delim is None:
            delim = ";" if sample.count(";") >= sample.count(",") else ","
        return list(csv.DictReader(f, delimiter=delim))

def epoch_iso(v):
    try:
        return datetime.fromtimestamp(int(float(v)), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""

def num(v, default=None):
    try:
        if v in (None, "", "NA"): return default
        return float(v)
    except Exception:
        return default

def style_header_row(ws, row, ncols, fill=CLR_HEADER, txt=CLR_HEADERTXT):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.font = hfont(10, True, txt)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER

def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

def flag_cell(cell, level, text):
    fills = {"RED": (CLR_RED, TXT_RED), "AMBER": (CLR_AMBER, TXT_AMBER), "GREEN": (CLR_GREEN, TXT_GREEN)}
    fg, tx = fills[level]
    cell.value = text
    cell.fill = PatternFill("solid", fgColor=fg)
    cell.font = hfont(10, False, tx)

CLR_BAND = "F6F2FB"  # very light purple banding for alternate rows
def band_rows(ws, first, last, ncols, height=19, fill=CLR_BAND):
    """Light banding on alternate rows + a readable row height. Skips cells that
    already carry a solid fill (accent/flag cells) so they are not overwritten."""
    for row in range(first, last + 1):
        ws.row_dimensions[row].height = height
        if (row - first) % 2 == 1:
            for c in range(1, ncols + 1):
                cell = ws.cell(row=row, column=c)
                if cell.fill is None or cell.fill.patternType is None:
                    cell.fill = PatternFill("solid", fgColor=fill)

# ---------- punctuation sanitiser: strip em/en dashes, arrows and numeric-range
# hyphens from PROSE, while preserving hyphens inside domains, URLs, ISO dates and
# real data cells. Runs as a final pass over every string cell before save. ----------
_ISO   = re.compile(r"\d{4}-\d{2}-\d{2}")
_MONY  = re.compile(r"\b[A-Za-z]{3,9}-\d{4}\b")          # Feb-2026, January-2026
_YM    = re.compile(r"\b\d{4}-\d{2}\b")                   # 2026-02
_DOTTOK = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9-]+)+")  # domains, IPs, decimals
_SLASHTOK = re.compile(r"\S*/\S*")                        # tokens containing a slash (paths, a/b, gov/edu)
_NEGNUM = re.compile(r"-\d[\d,]*%?\Z")                    # a bare negative number token (keep the minus)
def _sanitize_text(s):
    if not isinstance(s, str) or not s:
        return s
    if "://" in s or s.startswith("www."):
        return s  # URL cell: leave hyphens/dashes untouched
    store = []
    def stash(m):
        store.append(m.group(0)); return "\x00%d\x00" % (len(store) - 1)
    # stash numeric dates, domains, decimals and slash/path tokens so their hyphens
    # survive. NOTE: _MONY (word-year, e.g. Feb-2026, early-2024) is deliberately NOT
    # stashed so month/year prose compounds de-hyphenate to "Feb 2026" / "early 2024".
    for rx in (_ISO, _YM, _DOTTOK, _SLASHTOK):
        s = rx.sub(stash, s)
    # em / en / horizontal-bar dashes -> comma
    for d in ("—", "–", "―", "‒", "−"):
        s = s.replace(" %s " % d, ", ").replace(d, ", ")
    # arrows -> the word "to"
    s = re.sub(r"\s*(?:->|→|⟶|=>)\s*", " to ", s)
    # >=N -> "at least N"
    s = re.sub(r">\s*=\s*(\d+)", r"at least \1", s)
    # numeric-range hyphens (0-10, 11-30, 50-75%) -> "to"
    s = re.sub(r"(?<=\d)\s*-\s*(?=\d)", " to ", s)
    # remaining hyphens are prose compounds (over-optimization, link-selling, top-anchor);
    # strip them token by token, preserving stashed tokens and bare negative numbers.
    parts = re.split(r"(\s+)", s)
    for i, tok in enumerate(parts):
        if not tok or tok.isspace():
            continue
        if "\x00" in tok or "." in tok or "/" in tok:
            continue
        if _NEGNUM.match(tok):
            continue
        if "-" in tok:
            parts[i] = tok.replace("-", " ")
    s = "".join(parts)
    # iterative unstash: a slash/path token can itself hold decimal placeholders
    for _ in range(len(store) + 2):
        if "\x00" not in s:
            break
        s = re.sub(r"\x00(\d+)\x00", lambda m: store[int(m.group(1))], s)
    s = re.sub(r" {2,}", " ", s).replace(" ,", ",").replace(" .", ".").strip()
    return s
def sanitize_workbook(wb):
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    nv = _sanitize_text(cell.value)
                    if nv != cell.value:
                        cell.value = nv

wb = openpyxl.Workbook()
wb.remove(wb.active)

# =====================================================================
# Load shared data
# =====================================================================
bench_bl = read_csv(f"{DATA}/backlinks/benchmark_backlinks.csv")
bench_kw = {r["Domain"]: r for r in read_csv(f"{DATA}/keywords/benchmark_keywords.csv")}
# toxic tail per domain from ascore files
ascore_files = {
    NFG: "ascore_NFG.csv", "thefca.co.uk": "ascore_thefca.csv",
    "thefosteringnetwork.org.uk": "ascore_fosteringnetwork.csv",
    "capstonefostercare.co.uk": "ascore_capstone.csv", "ispfostering.org.uk": "ascore_isp.csv",
    "fosterplus.co.uk": "ascore_fosterplus.csv", "fosteringpeople.co.uk": "ascore_fosteringpeople.csv",
    "swiisfostercare.com": "ascore_swiis.csv", "compassfostering.com": "ascore_compass.csv",
    "orangegrovefostercare.co.uk": "ascore_orangegrove.csv",
}
def toxic_tail(dom):
    rows = read_csv(f"{DATA}/backlinks/{ascore_files[dom]}")
    tot = sum(int(r["domains_num"]) for r in rows)
    tox = sum(int(r["domains_num"]) for r in rows if int(r["ascore"]) <= 10)
    return tox / tot if tot else 0
TOX = {d: toxic_tail(d) for d in ascore_files}

# Internal-only cohort split (never rendered as a column or label in any cell).
# Kept purely so weighting logic can tell the two informational bodies apart from the
# direct rivals; the public workbook lists every competitor by domain name only.
SEGMENT = {NFG: "client", "thefca.co.uk": "body",
        "thefosteringnetwork.org.uk": "body", "capstonefostercare.co.uk": "rival",
        "ispfostering.org.uk": "rival", "fosterplus.co.uk": "rival",
        "fosteringpeople.co.uk": "rival", "swiisfostercare.com": "rival",
        "compassfostering.com": "rival", "orangegrovefostercare.co.uk": "rival"}

print("shared data loaded")

# =====================================================================
# FULL client-side backlink audit data (live Semrush + Ahrefs widen)
#   Region UK, snapshot 2026-09-22. Reported metrics are Semrush only;
#   Ahrefs is used solely to widen the pooled link/domain list.
# =====================================================================
BLF = os.path.join(DATA, "backlinks_full")

# disavow domain set (ready-to-submit file prepared earlier)
DISAVOW_DOMS = set()
with open(f"{DATA}/disavow/disavow_nationalfosteringgroup.txt", encoding="utf-8") as _f:
    for _line in _f:
        _line = _line.strip()
        if _line.startswith("domain:"):
            DISAVOW_DOMS.add(_line.split(":", 1)[1].strip().lower())

# registrable-domain helper (eTLD+1, small public-suffix table)
_TWO_LEVEL = {"co.uk","org.uk","gov.uk","sch.uk","me.uk","ltd.uk","plc.uk","net.uk","ac.uk",
 "nhs.uk","com.au","net.au","org.au","com.bz","com.lc","co.za","co.in","org.in","co.com",
 "us.com","com.my","in.net","org.au"}
def src_host(url):
    h = re.sub(r"^https?://", "", (url or "").strip().lower()).split("/")[0].split(":")[0]
    return h[4:] if h.startswith("www.") else h
def reg_domain(url):
    h = src_host(url)
    parts = h.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in _TWO_LEVEL:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else h
def norm_url(u):
    return (u or "").strip().rstrip("/").lower()

# ---- link-level classification (Keep / Review / Disavow) ----
_DIS_ANCHOR = ["backlink","pbn","buy backlinks","premium pbn","seo service",
 "dofollow backlinks da","manual outreach backlinks","seo authority backlinks"]
_DIS_DOMKW = ["goooogla","factmags","kingranks","heavenarticle","seodomains","blinks"]
_PARK_TLD = (".monster",".sbs",".cfd",".homes",".shop")
_SHORT_TLD = (".top",".icu",".website",".party",".fyi",".world",".space",".mom",".store",".xyz",".cloud")
_DIR_MARK = ["papasearch","pagesearch","loginslink","ranksdirectory","directory","find-open",
 "companieshousemanager","fostercareagencies","fostercarecompare","safefostering","govspendbase",
 "companiesintheuk","wegetyoufound","bizzr","find-your-support","findsupportinfo","openobjects",
 "sponsoredjobs","hrninjas","yably","allthechildcare","websitescrawl","toparticlesdirectory",
 "webranksdirectory","huntukvisasponsors","indexaward"]
def classify_link(anchor, source_url, page_as, nofollow):
    a = (anchor or "").lower()
    host = src_host(source_url); root = reg_domain(source_url)
    if any(p in a for p in _DIS_ANCHOR):
        return "Disavow"
    if root in DISAVOW_DOMS or host in DISAVOW_DOMS:
        return "Disavow"
    if any(host.endswith(t) for t in _PARK_TLD):
        return "Disavow"
    if any(k in host for k in _DIS_DOMKW):
        return "Disavow"
    if "/domain/domain/part" in (source_url or "").lower():
        return "Disavow"
    if any(host.endswith(t) for t in _SHORT_TLD) and re.search(r"/(stats|share|report|domain)/", (source_url or "").lower()):
        return "Disavow"
    if page_as is not None and page_as <= 2 and any(m in host for m in _DIR_MARK):
        return "Review"
    if nofollow and page_as is not None and page_as <= 1 and any(m in host for m in _DIR_MARK):
        return "Review"
    return "Keep"

# ---- pooled backlinks: Semrush live + Ahrefs-only (deduped by source_url) ----
POOL = {}
for row in read_csv(f"{BLF}/backlinks_all.csv", delim=";"):
    key = norm_url(row["source_url"])
    if key in POOL:
        continue
    pa = num(row["page_ascore"], None)
    POOL[key] = {"source_url": row["source_url"], "anchor": (row["anchor"].strip() or "<EmptyAnchor>"),
        "target_url": row["target_url"], "page_as": int(pa) if pa is not None else None,
        "nofollow": (row["nofollow"].strip().lower() == "true"),
        "first_seen": epoch_iso(row["first_seen"]), "last_seen": epoch_iso(row["last_seen"])}
_ah_added = 0
for a in read_csv(f"{BLF}/ahrefs_backlinks.csv", delim=","):
    key = norm_url(a["url_from"])
    if key in POOL:
        continue
    _ah_added += 1
    fs = (a.get("first_seen") or "")[:10]
    POOL[key] = {"source_url": a["url_from"], "anchor": (a.get("anchor","").strip() or "<EmptyAnchor>"),
        "target_url": a.get("url_to",""), "page_as": None,
        "nofollow": (str(a.get("is_dofollow","1")).strip() == "0"),
        "first_seen": fs, "last_seen": ""}
POOLED = list(POOL.values())
for p in POOLED:
    p["ref_domain"] = reg_domain(p["source_url"])
    p["action"] = classify_link(p["anchor"], p["source_url"], p["page_as"], p["nofollow"])
# link-action counts per referring domain (feeds the domain-level action)
DOM_LINKS = defaultdict(lambda: [0,0,0])  # domain -> [disavow, review, keep]
for p in POOLED:
    idx = {"Disavow":0,"Review":1,"Keep":2}[p["action"]]
    DOM_LINKS[p["ref_domain"]][idx] += 1

def classify_domain(domain, as_val):
    d = domain.lower()
    if d in DISAVOW_DOMS:
        return "Disavow"
    if any(d.endswith(t) for t in _PARK_TLD):
        return "Disavow"
    if any(k in d for k in _DIS_DOMKW):
        return "Disavow"
    dis, rev, keep = DOM_LINKS.get(d, [0,0,0])
    tot = dis + rev + keep
    if dis > 0 and (dis >= keep or tot <= 2):
        return "Disavow"
    if rev > 0:
        return "Review"
    if as_val is not None and as_val <= 2 and any(m in d for m in _DIR_MARK):
        return "Review"
    if dis > 0:
        return "Review"
    return "Keep"

# referring-domain traffic (Semrush domain_rank; AS>=12 genuine, tail set 0)
REF_TRAFFIC = {r["domain"].lower(): int(float(r["organic_traffic"])) for r in read_csv(f"{BLF}/refdomain_traffic.csv", delim=",")}
print("full backlink audit loaded:", len(POOLED), "pooled backlinks (", _ah_added, "Ahrefs-only );",
      len(REF_TRAFFIC), "traffic rows")

# =====================================================================
# TAB 0 — README & Methodology
# =====================================================================
ws0 = wb.create_sheet("12 README & Methodology")
ws0.sheet_properties.tabColor = TAB_APPENDIX
ws0.column_dimensions["A"].width = 34
ws0.column_dimensions["B"].width = 95
r = 1
def kv(ws, row, k, v, kfill=CLR_SUB, kbold=True):
    a = ws.cell(row=row, column=1, value=k); a.font = hfont(10, kbold); a.fill = PatternFill("solid", fgColor=kfill)
    a.alignment = Alignment(vertical="top", wrap_text=True); a.border = BORDER
    b = ws.cell(row=row, column=2, value=v); b.font = hfont(10); b.alignment = Alignment(vertical="top", wrap_text=True); b.border = BORDER
    return row + 1
t = ws0.cell(row=r, column=1, value="NFG Month-1 Foundation Audit — README & Methodology"); t.font = hfont(15, True, CLR_HEADER); r += 1
ws0.cell(row=r, column=1, value="Off-site competitor analysis · Backlink-gap target list · Keyword analysis").font = hfont(10, False, "666666"); r += 2
r = kv(ws0, r, "Client", "National Fostering Group, nationalfosteringgroup.co.uk (NFG)")
r = kv(ws0, r, "Agency", "SUSO Digital")
r = kv(ws0, r, "Snapshot date", SNAP + "  (single dated window; referenced by every tab header)")
r = kv(ws0, r, "Database / region", "UK")
r = kv(ws0, r, "Month-1 scope", "Foundation only — diagnostic + target map. No link placements or content shipped this month; Month 2+ outreach executes against Tabs 7, 8, 9 and 10.")
r = kv(ws0, r, "Deliverable file", "NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx (12 tabs)")
r += 1
h = ws0.cell(row=r, column=1, value="Governance — the two rules that bind every cell"); h.font = hfont(12, True, CLR_HEADER); r += 1
r = kv(ws0, r, "1. Metric firewall (Semrush-only)", "Every reported metric — Authority Score (AS), follow split, search volume, KD, traffic, CPC — is Semrush-sourced. Ahrefs DR/UR/traffic never appear in a client-facing metric cell.")
r = kv(ws0, r, "2. Lists may be pooled", "Raw backlink/refdomain LISTS pooled Semrush + Ahrefs to widen coverage, but every row is re-scored against Semrush AS before ranking. Ahrefs-only rows flagged AS_source=unmatched, kept in Raw, never scored. AS and DR never mixed in one column.")
r += 1
h = ws0.cell(row=r, column=1, value="Competitor set (9)"); h.font = hfont(12, True, CLR_HEADER); r += 1
r = kv(ws0, r, "Competitors (by domain)", "thefca.co.uk · thefosteringnetwork.org.uk · capstonefostercare.co.uk · ispfostering.org.uk · fosterplus.co.uk · fosteringpeople.co.uk · swiisfostercare.com · compassfostering.com · orangegrovefostercare.co.uk")
r += 1
r = kv(ws0, r, "How targets were prioritised", "No invented composite scores are used. Backlink targets are ranked by Semrush Authority Score and competitor consensus (how many of the nine competitors link the domain). Keyword targets are ranked by search volume and difficulty (KD). Every reported metric stays Semrush sourced.")
r += 1
h = ws0.cell(row=r, column=1, value="Metric definitions"); h.font = hfont(12, True, CLR_HEADER); r += 1
defs = [
 ("Authority Score (AS)", "Semrush 0-100 domain authority. NFG-reported metric. Not comparable to Ahrefs DR."),
 ("Referring Domain", "A unique root domain (eTLD+1, normalised) with >=1 link to the analysed domain."),
 ("Toxic tail %", "Share of referring domains scoring AS 0-10 (from backlinks_ascore_profile). Healthy profiles are pyramid-shaped."),
 ("Follow %", "follows / (follows + nofollows) at backlink level. Healthy ~50-75%; >90% = manipulation smell."),
 ("Gap (backlink)", "Referring domain links to >=1 competitor but NOT to NFG (pure gap after subtracting NFG's own set)."),
 ("Whitespace (regional)", "UK region with strong local demand where NFG is weak/absent and competitors are present."),
 ("Consensus target", "Referring domain linked by >=4 of 9 competitors (proven-relevant near-certain miss)."),
 ("Target_Quality", "Analyst classification separating genuine editorial/relevant targets from generic directories & blog/PR farms."),
 ("PBN", "Private Blog Network — a link scheme of sites built to pass artificial link equity."),
 ("EHCP", "Education, Health and Care Plan — UK statutory SEND document."),
 ("SEND", "Special Educational Needs and Disabilities."),
 ("FASD", "Fetal Alcohol Spectrum Disorder."),
 ("KD", "Keyword Difficulty (Semrush 0-100)."),
 ("CPC", "Cost Per Click."),
 ("IFA", "Independent Fostering Agency."),
]
for k, v in defs:
    r = kv(ws0, r, k, v, kfill=CLR_GREY, kbold=False)
r += 1
h = ws0.cell(row=r, column=1, value="CAVEATS BOX"); h.font = hfont(12, True, TXT_RED); h.fill = PatternFill("solid", fgColor=CLR_CAVEAT); r += 1
caveats = [
 "Semrush metrics are third-party ESTIMATES (volume, KD, position, traffic modelled — not Google-truth); directional, snapshot-dated.",
 "Index coverage: neither engine indexes the whole web; absence of a link is not proof it does not exist.",
 "Ahrefs-only domains without a Semrush AS are excluded from scored ranking (Raw only). AS != DR, never compared in one cell.",
 "Regional classification is MANUAL & inferential (IP-geo unreliable via CDNs); Region_Confidence flags uncertainty; some domains stay Unknown by design.",
 "Top-100 refdomain cut for the regional map is a comparable strong-links sample, not a full profile.",
 "Spam/toxicity is rules-based judgment, not a certified verdict; thresholds are tunable priors.",
 "TARGET-QUALITY CAVEAT: many high-#competitor 'consensus' gap domains are generic directories (yell, thomsonlocal) or SEO/PR/mommy-blog farms competitors used as link schemes. These are separated from genuine editorial targets and must NOT be presented as top recommendations.",
 "Gap != guaranteed win (domains may be unreachable/paid/closed); tiering encodes acquisition realism, not outcomes.",
 "The two informational bodies (theFCA, FosteringNetwork) distort the set — benchmarked but weighted separately behind the scenes; no segment label is shown on any tab.",
 "Keyword export in Tab 6 is the top 1,000 of NFG's 4,028 organic keywords (Semrush cap); summary counts use full-profile totals.",
 "swiisfostercare.com's regional counts (Tab 9) are under-populated: it has only ~300 total referring domains, so its top-100 cut is thin — a source characteristic, not an error.",
]
for cav in caveats:
    cell = ws0.cell(row=r, column=1, value="• " + cav); cell.font = hfont(9); cell.alignment = Alignment(wrap_text=True, vertical="top")
    cell.fill = PatternFill("solid", fgColor=CLR_CAVEAT)
    ws0.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    ws0.row_dimensions[r].height = 28; r += 1
r += 1
r = kv(ws0, r, "SUSO contact & sign-off", "Prepared by SUSO Digital SEO team · fahad.ahmad@susodigital.com · Sign-off: ____________  Date: __________")
r = kv(ws0, r, "Legend", "NFG (Client) rows/columns carry the purple accent. Flags are RED/AMBER/GREEN paired with text. All reported metrics are Semrush; Ahrefs is used only to widen the pooled lists behind the scenes and is not exposed as a column.")
ws0.freeze_panes = "A2"
print("tab0 done")

# =====================================================================
# TAB 2 — Competitor Benchmark (10 rows) — built before Tab1 (Tab1 refs it)
# =====================================================================
ws2 = wb.create_sheet("2 Competitor Benchmark")
ws2.sheet_properties.tabColor = TAB_ANALYST
# FIX: Organic Traffic (UK) promoted to an early column beside Authority Score and
# Referring Domains; analyst-plumbing (Index_*/Rank_*/Composite) moved to the far right;
# "Is_NFG" replaced by a plain-English "Role" (Client / Competitor).
cols2 = ["Domain","Authority_Score","Referring_Domains","Est_Organic_Traffic_UK",
         "Organic_Keywords_UK","Est_Traffic_Cost_GBP","Total_Backlinks","Referring_IPs","Follow_%",
         "Backlinks_per_RefDomain","Toxic_Tail_%","Pos_1_3","Pos_11_30_QuickWin","SemrushRank",
         "Rank_AS","Rank_RefDomains","Snapshot_Date"]
DISP2 = {"Domain":"Domain","Authority_Score":"Authority Score (Semrush)",
 "Referring_Domains":"Referring Domains","Est_Organic_Traffic_UK":"Organic Traffic (UK)",
 "Organic_Keywords_UK":"Organic Keywords (UK)","Est_Traffic_Cost_GBP":"Est Traffic Cost (GBP)",
 "Total_Backlinks":"Total Backlinks","Referring_IPs":"Referring IPs","Follow_%":"Follow %",
 "Backlinks_per_RefDomain":"Backlinks per Ref Domain","Toxic_Tail_%":"Toxic Tail %",
 "Pos_1_3":"Positions 1 to 3","Pos_11_30_QuickWin":"Positions 11 to 30 (quick win)","SemrushRank":"Semrush Rank",
 "Rank_AS":"NFG position out of 10 (by Authority Score)","Rank_RefDomains":"NFG position out of 10 (by Referring Domains)",
 "Snapshot_Date":"Snapshot Date"}
title = ws2.cell(row=1, column=1, value=f"Competitor Benchmark: NFG (the Client) and 9 competitors on one Semrush snapshot ({SNAP}, UK). The Client row carries the purple accent.")
title.font = hfont(10, True, CLR_HEADER); ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols2))
for j, c in enumerate(cols2, 1):
    ws2.cell(row=2, column=j, value=DISP2.get(c, c))
style_header_row(ws2, 2, len(cols2))
# order: NFG first then by AS desc
blmap = {r["target"]: r for r in bench_bl}
order = [NFG] + sorted([d for d in blmap if d != NFG], key=lambda d: -int(blmap[d]["ascore"]))
row = 3
first_data, last_data = 3, 3 + len(order) - 1
bench_num = []  # FIX 2: collect numeric values per row to compute STATIC derived cells
for dom in order:
    b = blmap[dom]; k = bench_kw.get(dom, {})
    follows = int(b["follows_num"]); nofollows = int(b["nofollows_num"])
    cost_usd = num(k.get("OrganicTrafficCost_USD"))
    vals = {
        "Domain": dom,
        "Authority_Score": int(b["ascore"]), "Total_Backlinks": int(b["backlinks_num"]),
        "Referring_Domains": int(b["domains_num"]), "Referring_IPs": int(b["ips_num"]),
        "Backlinks_per_RefDomain": round(int(b["backlinks_num"]) / max(int(b["domains_num"]),1), 1),
        "Toxic_Tail_%": round(TOX[dom], 3),
        "Organic_Keywords_UK": int(k["OrganicKeywords"]) if k.get("OrganicKeywords") not in (None,"NA") else None,
        "Est_Organic_Traffic_UK": int(k["OrganicTraffic"]) if k.get("OrganicTraffic") not in (None,"NA") else None,
        # FIX 1: competitor OrganicTrafficCost_USD is mis-scaled ~100x too small vs NFG's
        # domain_rank value; multiply by 100 before the USD->GBP conversion so every domain
        # lands on a consistent per-visit basis (~£2-4/visit). NFG uses its hard-coded path below.
        "Est_Traffic_Cost_GBP": round(cost_usd * 100 * USD_GBP, 2) if cost_usd is not None else None,
        "Pos_1_3": int(k["Pos_1_3"]) if k.get("Pos_1_3") not in (None,"NA") else None,
        "Pos_11_30_QuickWin": (int(k["Pos_11_20"])+int(k["Pos_21_30"])) if k.get("Pos_11_20") not in (None,"NA") else None,
        "SemrushRank": int(k["SemrushRank"]) if k.get("SemrushRank") not in (None,"NA") else None,
        "Snapshot_Date": SNAP,
    }
    # NFG keyword metrics come from the direct domain_rank pull (not in the competitor benchmark_keywords.csv),
    # so populate its real UK values here instead of leaving the cells blank.
    if dom == NFG:
        vals.update({
            "Organic_Keywords_UK": 4028,
            "Est_Organic_Traffic_UK": 15906,
            "Est_Traffic_Cost_GBP": round(47868 * USD_GBP, 2),
            "Pos_1_3": 471,
            "Pos_11_30_QuickWin": 351 + 326,  # pos 11-20 (351) + 21-30 (326) = 677
            "SemrushRank": 32673,
        })
    cL = {c: get_column_letter(cols2.index(c)+1) for c in cols2}
    for c in cols2:
        cell = ws2.cell(row=row, column=cols2.index(c)+1)
        if c in vals: cell.value = vals[c]
    # follow %
    ws2[f'{cL["Follow_%"]}{row}'] = f'={cL["Total_Backlinks"]}{row}/({int(follows)+int(nofollows)})' if False else follows/(follows+nofollows)
    ws2[f'{cL["Follow_%"]}{row}'].value = round(follows/(follows+nofollows), 3)
    bench_num.append({
        "dom": dom, "row": row, "is_nfg": dom == NFG,
        "AS": vals["Authority_Score"], "RD": vals["Referring_Domains"],
        "TB": vals["Total_Backlinks"], "KW": vals["Organic_Keywords_UK"],
        "TR": vals["Est_Organic_Traffic_UK"],
        "FU": round(follows/(follows+nofollows), 3), "TT": round(TOX[dom], 3),
    })
    row += 1
# rank columns: Rank_AS, Rank_RefDomains (Index_* and Composite_Strength removed per client —
# the client considers the normalised index/composite formulas unhelpful).
AScol=cL["Authority_Score"]; RDcol=cL["Referring_Domains"]; KWcol=cL["Organic_Keywords_UK"]; TRcol=cL["Est_Organic_Traffic_UK"]
RAcol=cL["Rank_AS"]; RRcol=cL["Rank_RefDomains"]
FUcol=cL["Follow_%"]; TTcol=cL["Toxic_Tail_%"]
tr_rng=f"{TRcol}{first_data}:{TRcol}{last_data}"
# compute Rank_AS / Rank_RefDomains as STATIC numeric values so they render everywhere
# (PDF/preview/pandas), not just inside Excel.
as_list = [b["AS"] for b in bench_num]; rd_list = [b["RD"] for b in bench_num]
for b in bench_num:
    row = b["row"]
    ws2[f"{RAcol}{row}"] = _rank_desc(b["AS"], as_list)
    ws2[f"{RRcol}{row}"] = _rank_desc(b["RD"], rd_list)
# formatting
for row in range(first_data, last_data+1):
    for j, c in enumerate(cols2, 1):
        cell = ws2.cell(row=row, column=j); cell.font = hfont(9); cell.border = BORDER
        if c in ("Total_Backlinks","Referring_Domains","Referring_IPs","Organic_Keywords_UK","Est_Organic_Traffic_UK","SemrushRank","Pos_1_3","Pos_11_30_QuickWin"):
            cell.number_format = "#,##0"
        if c == "Est_Traffic_Cost_GBP": cell.number_format = '£#,##0.00'
        if c in ("Follow_%","Toxic_Tail_%"): cell.number_format = "0.0%"
    if ws2.cell(row=row, column=1).value == NFG:
        for j in range(1, len(cols2)+1):
            ws2.cell(row=row, column=j).fill = PatternFill("solid", fgColor=CLR_NFG)
            ws2.cell(row=row, column=j).font = hfont(9, True)
# conditional colour scale on AS; data bars on refdomains & traffic
ws2.conditional_formatting.add(f"{AScol}{first_data}:{AScol}{last_data}",
    ColorScaleRule(start_type="min", start_color=SC_BAD, mid_type="percentile", mid_value=50, mid_color=SC_MID, end_type="max", end_color=SC_GOOD))
ws2.conditional_formatting.add(f"{RDcol}{first_data}:{RDcol}{last_data}", DataBarRule(start_type="min", end_type="max", color=BAR_PURPLE))
ws2.conditional_formatting.add(f"{tr_rng}", DataBarRule(start_type="min", end_type="max", color=BAR_BLUE))
# toxic tail: reversed scale (high=unfavourable)
ws2.conditional_formatting.add(f"{TTcol}{first_data}:{TTcol}{last_data}",
    ColorScaleRule(start_type="min", start_color=SC_GOOD, mid_type="percentile", mid_value=50, mid_color=SC_MID, end_type="max", end_color=SC_BAD))
# gap note row
gnr = last_data + 2
ws2.cell(row=gnr, column=1, value="Framing numbers:").font = hfont(10, True, CLR_HEADER)
ws2.cell(row=gnr+1, column=1, value=f"AS: NFG 36 = rank 2/10, median 29, gap-to-median +7, gap-to-leader -3 (highest of the direct rivals, but recency-inflated, see Tab 3).").font = hfont(9)
ws2.cell(row=gnr+2, column=1, value=f"Referring Domains: NFG 420 = rank 9/10, median 821.5, gap-to-median -401.5, competitor best 1,892. This -401.5 frames the Month-2+ deliverable.").font = hfont(9)
ws2.cell(row=gnr+3, column=1, value="Capstone caveat: 127,526 backlinks / 156.9-per-domain (~30x cohort median) is a volume-inflation outlier — score on AS + ref domains, not raw backlink count.").font = hfont(9, False, TXT_AMBER)
ws2.merge_cells(start_row=gnr+1, start_column=1, end_row=gnr+1, end_column=len(cols2))
ws2.merge_cells(start_row=gnr+2, start_column=1, end_row=gnr+2, end_column=len(cols2))
ws2.merge_cells(start_row=gnr+3, start_column=1, end_row=gnr+3, end_column=len(cols2))
band_rows(ws2, first_data, last_data, len(cols2))
ws2.freeze_panes = "B3"
ws2.auto_filter.ref = f"A2:{get_column_letter(len(cols2))}{last_data}"
W2 = {"Domain":34,"Authority_Score":16,"Referring_Domains":15,"Est_Organic_Traffic_UK":16,
 "Organic_Keywords_UK":16,"Est_Traffic_Cost_GBP":16,"Total_Backlinks":14,"Referring_IPs":12,"Follow_%":10,
 "Backlinks_per_RefDomain":16,"Toxic_Tail_%":12,"Pos_1_3":12,"Pos_11_30_QuickWin":16,"SemrushRank":12,
 "Rank_AS":20,"Rank_RefDomains":22,"Snapshot_Date":13}
autosize(ws2, {cL[c]: W2[c] for c in cols2})
BENCH = {"sheet":"2 Competitor Benchmark","AScol":AScol,"RDcol":RDcol,"TBcol":cL["Total_Backlinks"],
         "KWcol":KWcol,"TRcol":TRcol,"FUcol":FUcol,"TTcol":TTcol,"first":first_data,"last":last_data,
         "nfg_row":first_data}
print("tab2 done")

# =====================================================================
# TAB 1 — Executive Scorecard (references Tab 2)
# =====================================================================
ws1 = wb.create_sheet("1 Executive Scorecard")
ws1.sheet_properties.tabColor = TAB_EXEC
KPI = {k: [b[k] for b in bench_num] for k in ("AS","RD","TB","KW","TR","FU","TT")}
nfg_b = next(b for b in bench_num if b["is_nfg"])
# ---- consistent dashboard type hierarchy & muted card styling ----
HAIR = Side(style="thin", color="E6DFF0")
CARD_BORDER = Border(left=HAIR, right=HAIR, top=HAIR, bottom=HAIR)
TILE_FILL = "F7F4FB"
def _ord(n):
    n = int(n)
    suf = "th" if 10 <= n % 100 <= 20 else {1:"st",2:"nd",3:"rd"}.get(n % 10, "th")
    return f"{n}{suf}"
def _fmt(x, kind):
    if kind == "pct": return f"{x*100:.1f}%"
    if kind == "comma": return f"{x:,.0f}" if float(x) == int(x) else f"{x:,.1f}"
    return f"{int(round(x))}"
def section_label(row, text):
    c = ws1.cell(row=row, column=1, value=text); c.font = hfont(11, True, CLR_HEADER)
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws1.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
# widths: eight even columns carry both the tile band and the card band
for col in "ABCDEFGH":
    ws1.column_dimensions[col].width = 17
# ---- title band ----
t = ws1.cell(row=1, column=1, value="Executive Scorecard")
t.font = hfont(16, True, CLR_HEADER); t.alignment = Alignment(vertical="center")
ws1.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8); ws1.row_dimensions[1].height = 26
sub = ws1.cell(row=2, column=1, value=f"Semrush snapshot {SNAP}, UK, estimates (see caveats). Authority Score 36, referring domains 9th of 10 (gap to median minus 401.5), toxic tail 67 percent, and a February 2026 spike.")
sub.font = hfont(9, False, "6E6E6E"); sub.alignment = Alignment(vertical="center", wrap_text=True)
ws1.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8); ws1.row_dimensions[2].height = 24
ws1.row_dimensions[3].height = 6
# ---- KPI TILE BAND ----
section_label(4, "KEY METRICS — NFG value, with competitor median, best and NFG's position of ten")
def tile(r0, c0, name, key, kind, higher_better=True):
    vals = KPI[key]; nfgv = nfg_b[key]
    med = _median(vals); best = max(vals) if higher_better else min(vals)
    rank = _rank_desc(nfgv, vals) if higher_better else _rank_asc(nfgv, vals)
    for rr in range(r0, r0+4):
        for cc in (c0, c0+1):
            cell = ws1.cell(row=rr, column=cc)
            cell.fill = PatternFill("solid", fgColor=TILE_FILL); cell.border = CARD_BORDER
    n = ws1.cell(row=r0, column=c0, value=name); n.font = hfont(9, True, "6E6E6E")
    n.alignment = Alignment(horizontal="left", vertical="center")
    ws1.merge_cells(start_row=r0, start_column=c0, end_row=r0, end_column=c0+1)
    v = ws1.cell(row=r0+1, column=c0, value=_fmt(nfgv, kind)); v.font = hfont(24, True, CLR_HEADER)
    v.alignment = Alignment(horizontal="left", vertical="center")
    ws1.merge_cells(start_row=r0+1, start_column=c0, end_row=r0+2, end_column=c0+1)
    s = ws1.cell(row=r0+3, column=c0,
                 value=f"competitor median {_fmt(med, kind)}  ·  competitor best {_fmt(best, kind)}  ·  NFG is {_ord(rank)} of ten")
    s.font = hfont(8, False, "7C7C7C"); s.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws1.merge_cells(start_row=r0+3, start_column=c0, end_row=r0+3, end_column=c0+1)
tiles_def = [
    ("Authority Score (0 to 100)", "AS", "int", True),
    ("Referring Domains", "RD", "comma", True),
    ("Organic Traffic (UK) / mo", "TR", "comma", True),
    ("Organic Keywords (UK)", "KW", "comma", True),
    ("Follow % (backlink level)", "FU", "pct", True),
    ("Toxic Tail % (lower is better)", "TT", "pct", False),
]
for i, (name, key, kind, hb_) in enumerate(tiles_def):
    band = i // 4; slot = i % 4
    r0 = 5 if band == 0 else 10
    c0 = 1 + slot*2
    tile(r0, c0, name, key, kind, hb_)
for r0 in (5, 10):
    ws1.row_dimensions[r0].height = 16
    ws1.row_dimensions[r0+1].height = 20; ws1.row_dimensions[r0+2].height = 20
    ws1.row_dimensions[r0+3].height = 30
ws1.row_dimensions[9].height = 8; ws1.row_dimensions[14].height = 10
ws1.cell(row=10, column=7).comment = Comment("Ref-domain gap-to-median -401.5 = the number that frames the deliverable.","SUSO")
# ---- CHARTS (breathing room; rows 16-49 left clear for the two floating charts) ----
section_label(15, "COMPETITOR COMPARISON CHARTS")
# ---- HEADLINE FINDINGS (clean cards below the charts) ----
find = 50
section_label(find, "Headline opportunity counts"); find += 1
counts = [
 ("Backlink gap domains found", "866"),
 ("Consensus targets (linked by 4 or more competitors)", "69"),
 ("Keyword opportunities", "35"),
 ("Quick win keywords (positions 11 to 30)", "22"),
 ("Regional whitespace regions", "2 (Yorkshire & Humber, North East)"),
 ("Toxic or PBN domains to review", "about 84"),
]
for i, (lab, val) in enumerate(counts):
    a = ws1.cell(row=find, column=1, value=lab); a.font = hfont(10, lab[0] != " "); a.border = CARD_BORDER
    a.alignment = Alignment(vertical="center", wrap_text=True)
    ws1.merge_cells(start_row=find, start_column=1, end_row=find, end_column=4)
    b = ws1.cell(row=find, column=5, value=val); b.font = hfont(10, True, CLR_HEADER); b.border = CARD_BORDER
    b.alignment = Alignment(vertical="center", wrap_text=True)
    ws1.merge_cells(start_row=find, start_column=5, end_row=find, end_column=8)
    if i % 2 == 1:
        for cc in range(1, 9): ws1.cell(row=find, column=cc).fill = PatternFill("solid", fgColor=CLR_GREY)
    find += 1
find += 1
tk = find
ws1.cell(row=tk, column=1, value="The five Month-1 takeaways (corrected — earlier hypotheses disproven by data)").font = hfont(11, True, CLR_HEADER)
ws1.merge_cells(start_row=tk, start_column=1, end_row=tk, end_column=8); tk += 1
takeaways = [
 ("1. BACKLINK TOXICITY is the real story", "RED",
  "The Client's backlink profile was negligible, about 24 referring domains, until February 2026, then it spiked. Roughly 94 percent of its 420 referring domains were acquired in the last 8 months. In February 2026 referring domains went from 24 to 147, a rise of 512 percent, then backlinks went from 28 to 486, a rise of 1,636 percent, then AS went from 2 to 10 in one month. Toxic tail is 67 percent (AS 0 to 10), with live PBN and link selling anchors ('buy backlinks online cheap ... premium pbn network') and an IP cluster footprint (42 domains on 2 IPs). Needs a disavow review. The 'AS 36, rank 2 of 10' is recency inflated, not earned breadth."),
 ("2. GENUINE AUTHORITY DEFICIT", "RED",
  "Referring domains rank 9/10, -401.5 below the cohort median (420 vs 821.5). Off-site breadth — not on-site — is the primary constraint. This -401.5 is the number that frames the Month-2+ deliverable."),
 ("3. KEYWORD GAP is INFORMATIONAL, not money terms", "AMBER",
  "The gap is SEND/EHCP (~34k/mo, ISP owns, KD 20-43 winnable), FASD (~29k), kinship care (~12k), therapeutic parenting. NFG already OWNS the money terms (fostering agencies p4, foster carer salary p5, become a foster carer p9). Do not chase what NFG already ranks for."),
 ("4. REGIONAL WHITESPACE = Yorkshire & North East", "AMBER",
  "NFG has zero/near-zero links in Yorkshire & Humber and North East, both proven attainable by theFCA/FosteringNetwork and both inside NFG's real service geography (NFA North = Yorkshire/Lincs; Reach Out Care = North East/Cumbria). Highest-leverage regional play."),
 ("5. TARGET-QUALITY CAVEAT", "AMBER",
  "Many high-#competitor 'consensus' gap domains are generic directories (yell.com, thomsonlocal) or SEO/mommy-blog/PR farms competitors used as link schemes. These are separated from GENUINE editorial targets (regional councils/universities/local news, fostering charities) via a Target_Quality column. Directory/farm spam is NOT presented as a top recommendation."),
]
for lab, lvl, txt in takeaways:
    a = ws1.cell(row=tk, column=1, value=lab)
    fg = {"RED":CLR_RED,"AMBER":CLR_AMBER,"GREEN":CLR_GREEN}[lvl]
    tx = {"RED":TXT_RED,"AMBER":TXT_AMBER,"GREEN":TXT_GREEN}[lvl]
    a.font = hfont(10, True, tx); a.fill = PatternFill("solid", fgColor=fg); a.alignment = Alignment(vertical="top", wrap_text=True); a.border = CARD_BORDER
    b = ws1.cell(row=tk, column=3, value=txt); b.font = hfont(10); b.alignment = Alignment(vertical="top", wrap_text=True); b.border = CARD_BORDER
    ws1.merge_cells(start_row=tk, start_column=1, end_row=tk, end_column=2)
    ws1.merge_cells(start_row=tk, start_column=3, end_row=tk, end_column=8)
    ws1.row_dimensions[tk].height = 74; tk += 1
# caveats box
cb = tk + 1
cc = ws1.cell(row=cb, column=1, value="CAVEATS: Semrush estimates (modelled, not Google-truth); single snapshot 2026-09-22; regional classification is manual/inferential; target-quality is analyst judgment — see the README & Methodology tab for the full box.")
cc.font = hfont(9, False, TXT_AMBER); cc.fill = PatternFill("solid", fgColor=CLR_CAVEAT); cc.alignment = Alignment(wrap_text=True, vertical="top")
ws1.merge_cells(start_row=cb, start_column=1, end_row=cb+1, end_column=8)
ws1.freeze_panes = "A3"

# Exec Scorecard visuals: two clean comparison bar charts (no index/composite numbers).
# Each compares all ten domains on a real Semrush metric, sorted descending, NFG highlighted.
def _short_dom(d):
    return "NFG (Client)" if d == NFG else d.replace(".co.uk", "").replace(".org.uk", "").replace(".com", "")
# helper tables live far-right (cols T onward), well clear of the tiles (A-H) and the charts.
HCHDR = 4  # helper header row; values start on HCHDR+1
def _chart_table(col, header, sorted_rows):
    ws1.cell(row=HCHDR, column=col, value="Domain").font = hfont(9, True)
    ws1.cell(row=HCHDR, column=col+1, value=header).font = hfont(9, True)
    for i, (lab, val) in enumerate(sorted_rows):
        ws1.cell(row=HCHDR+1+i, column=col, value=lab).font = hfont(9)
        ws1.cell(row=HCHDR+1+i, column=col+1, value=val).font = hfont(9)
def _comparison_chart(col, header, title, x_axis, sorted_rows):
    n = len(sorted_rows)
    _chart_table(col, header, sorted_rows)
    ch = BarChart(); ch.type = "bar"; ch.legend = None; ch.title = title
    ch.y_axis.title = None; ch.x_axis.title = x_axis
    data = Reference(ws1, min_col=col+1, min_row=HCHDR, max_row=HCHDR+n)
    cats = Reference(ws1, min_col=col, min_row=HCHDR+1, max_row=HCHDR+n)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    pts = []
    for i, (lab, _v) in enumerate(sorted_rows):
        color = CLR_NFG_STRONG if lab == "NFG (Client)" else "C9C9CE"
        pts.append(DataPoint(idx=i, spPr=GraphicalProperties(solidFill=color)))
    ch.series[0].data_points = pts
    ch.y_axis.scaling.orientation = "maxMin"  # largest bar at the top
    ch.height = 8; ch.width = 18
    return ch
# (a) Authority Score across all ten domains, descending
as_rows = sorted(((b["dom"], b["AS"]) for b in bench_num), key=lambda x: -x[1])
as_rows = [(_short_dom(d), v) for d, v in as_rows]
ch_as = _comparison_chart(20, "Authority Score", "Authority Score by domain, all 10 (Semrush, NFG highlighted)", "Authority Score", as_rows)
ws1.add_chart(ch_as, "A16")
# (b) Organic Traffic (UK) across all ten domains, descending
tr_rows = sorted(((b["dom"], b["TR"] or 0) for b in bench_num), key=lambda x: -x[1])
tr_rows = [(_short_dom(d), v) for d, v in tr_rows]
ch_tr = _comparison_chart(23, "Organic Traffic (UK)", "Organic Traffic (UK) by domain, all 10 (Semrush, NFG highlighted)", "Organic Traffic (UK) / mo", tr_rows)
ws1.add_chart(ch_tr, "A33")
print("tab1 done")

# =====================================================================
# TAB 3 — NFG Referring Domains (ALL referring domains, live Semrush + traffic)
# =====================================================================
ws3 = wb.create_sheet("3 NFG Referring Domains")
ws3.sheet_properties.tabColor = TAB_ANALYST
ov = read_csv(f"{DATA}/backlinks/overview_NFG.csv")[0]
ws3.cell(row=1, column=1, value="NFG Referring Domains: every site that links to the Client (Semrush, 2026-09-22)").font = hfont(13, True, CLR_HEADER)
ws3.cell(row=2, column=1, value="These are referring domains, the external websites that link to the Client, not the individual links. The individual links, each with its own anchor text, are on the NFG Backlinks tab. Backlinks from domain is how many links that site sends. Organic Traffic is the Semrush estimated monthly UK organic traffic of that referring site (the low authority tail, Authority Score under 12, is spam with negligible traffic and is shown as 0). Recommended Action is the analyst call (Keep, Review or Disavow); Your Decision is yours to fill in. Summary and the AS band distribution are in the labelled panel to the right, from column L onward.").font = hfont(9, False, "6E6E6E")

# ---- DATA TABLE at top-left; ALL referring domains from the live pull ----
rd = read_csv(f"{BLF}/refdomains_all.csv", delim=";")
# Client-friendly order: by how many links each domain sends (desc), then Authority Score (desc),
# so incidental single-link high-authority domains (apple.com, google.com) do not dominate the top.
rd.sort(key=lambda x: (-int(x["backlinks_num"]), -int(x["domain_ascore"])))
rdcols = ["Referring_Domain","Authority_Score","Domain_Trust","Organic_Traffic",
          "Backlinks_From_Domain","Country","First_Seen","Last_Seen","Recommended_Action","Your_Decision"]
hrow3 = 3
for j,c in enumerate(rdcols,1): ws3.cell(row=hrow3, column=j, value=c)
style_header_row(ws3, hrow3, len(rdcols))
rd_start = hrow3 + 1
r = rd_start
_act_fill = {"Disavow":(CLR_RED,TXT_RED),"Review":(CLR_AMBER,TXT_AMBER),"Keep":(CLR_GREEN,TXT_GREEN)}
for row in rd:
    dom = row["domain"]; as_val = int(row["domain_ascore"])
    trf = REF_TRAFFIC.get(dom.lower(), 0) if as_val >= 12 else 0
    act = classify_domain(dom, as_val)
    ws3.cell(row=r, column=1, value=dom)
    ws3.cell(row=r, column=2, value=as_val)
    ws3.cell(row=r, column=3, value=int(row["domain_trust_score"]) if row["domain_trust_score"] else 0)
    ws3.cell(row=r, column=4, value=trf)
    ws3.cell(row=r, column=5, value=int(row["backlinks_num"]))
    ws3.cell(row=r, column=6, value=row["country"])
    ws3.cell(row=r, column=7, value=epoch_iso(row["first_seen"]))
    ws3.cell(row=r, column=8, value=epoch_iso(row["last_seen"]))
    ac = ws3.cell(row=r, column=9, value=act)
    ws3.cell(row=r, column=10, value="")
    for j in range(1,len(rdcols)+1):
        cell=ws3.cell(row=r,column=j); cell.font=hfont(9); cell.border=BORDER
        if j in (4,5): cell.number_format="#,##0"
    fg,tx=_act_fill[act]; ac.fill=PatternFill("solid",fgColor=fg); ac.font=hfont(9,True,tx)
    ws3.cell(row=r,column=10).fill=PatternFill("solid",fgColor="FBF3D9")
    r += 1
rd_end = r - 1
ws3.conditional_formatting.add(f"B{rd_start}:B{rd_end}", ColorScaleRule(start_type="min",start_color=SC_BAD,mid_type="percentile",mid_value=50,mid_color=SC_MID,end_type="max",end_color=SC_GOOD))
band_rows(ws3, rd_start, rd_end, len(rdcols))
ws3.column_dimensions["K"].width = 3  # clean gutter between the table and the summary panel
ws3.freeze_panes = f"A{hrow3+1}"
ws3.auto_filter.ref = f"A{hrow3}:{get_column_letter(len(rdcols))}{rd_end}"

# ---- RIGHT PANEL (columns L onward): summary, critical flags, AS band distribution ----
PC = 12  # column L
pr = 3
ws3.cell(row=pr, column=PC, value="SUMMARY BLOCK").font = hfont(11, True, CLR_HEADER); pr += 1
summ = [
 ("Authority Score", "36"), ("Total backlinks", f'{int(ov["total"]):,}'),
 ("Referring domains", f'{int(ov["domains_num"]):,}'), ("Referring IPs", f'{int(ov["ips_num"]):,}'),
 ("Class-C subnets", f'{int(ov["ipclassc_num"]):,}'),
 ("Follow % (backlink level)", f'{int(ov["follows_num"])/(int(ov["follows_num"])+int(ov["nofollows_num"])):.1%}'),
 ("Toxic tail % (AS 0-10 ref domains)", f'{TOX[NFG]:.1%}'),
 ("Profile age", "The Client's backlink profile was negligible, about 24 referring domains, until February 2026, then it spiked. Roughly 94 percent of its 420 referring domains were acquired in the last 8 months."),
 ("12-mo velocity", "Referring domains grew by 399 over the period. In February 2026 alone referring domains went from 24 to 147, a rise of 512 percent, then backlinks went from 28 to 486, a rise of 1,636 percent."),
 ("New in last 90 days", "Referring domains moved to 296 in June, then to 358, then to 420. Backlinks moved to 1,390, then to 1,843, then to 1,743."),
]
for k, v in summ:
    a = ws3.cell(row=pr, column=PC, value=k); a.font=hfont(10,True); a.fill=PatternFill("solid",fgColor=CLR_SUB); a.alignment=Alignment(vertical="top",wrap_text=True); a.border=BORDER
    b = ws3.cell(row=pr, column=PC+1, value=v); b.font=hfont(10); b.alignment=Alignment(vertical="top",wrap_text=True); b.border=BORDER
    ws3.merge_cells(start_row=pr, start_column=PC+1, end_row=pr, end_column=PC+5)
    pr += 1
pr += 1
ws3.cell(row=pr, column=PC, value="CRITICAL FLAGS (evidence backed)").font = hfont(11, True, TXT_RED); pr += 1
flags = [
 ("RED","ISSUE 1 — Severe velocity anomaly","Flat ~21 domains / AS 0-2 from early-2024 to Jan-2026, then 2026-02: 147 domains (referring domains +512%, 24->147; backlinks +1,636%, 28->486), AS 10; 2026-06: 296, AS 35; 2026-09: 420, AS 36. Near-vertical spike = bought/aggressive campaign signature. 'Rank-2 AS' is recency-inflated. [historical_NFG.csv]"),
 ("RED","ISSUE 2 — Toxic tail 67.1%","67.1% of ref domains AS 0-10 (AS-2 band alone = 127 domains) vs cohort median 53.6% (+13.5 pts). Spikes at AS 0-6, not a healthy pyramid; trusted mid-band thin. [ascore_NFG.csv]"),
 ("RED","ISSUE 3 — PBN / link-selling anchors","Overt paid-scheme fingerprints: 'high quality dofollow backlinks da 50 pa 40 premium pbn network service ... buy backlinks online cheap' (52+7 domains); 'professional manual outreach backlinks ... safe link velocity' (18); ~84 domain-hits (~21% of top-50 anchors). Live PBN/link-buying or negative-SEO. [nfg_anchors.csv]"),
 ("RED","ISSUE 4 — IP / subnet concentration","25 ref domains on 159.198.75.134 (US); 17 on 195.20.19.178 (Moldova) = 42 domains (~10%) on 2 IPs. Singapore 118.139.x cluster = 23 domains across 5 IPs. Textbook PBN, time-aligned with the Feb-2026 spike. [nfg_refips.csv]"),
 ("GREEN","CLEARED — money-anchor over-optimization NOT present","Money/exact-match anchors ~1.9% of backlinks / 3.3% of anchor domain-hits — far below the 10-15% single / 35% top-5 thresholds. Anchor risk is spam-tail, not commercial over-optimization."),
 ("AMBER","ISSUE 5 — Follow ratio high but not alarming alone","79.3% follow vs median 73.8% — upper edge of healthy 50-75%, below the >90% line. With Issues 1-4 reads as engineered. DATA GAP: refdomain-level follow% not returned by backlinks_overview."),
 ("AMBER","ISSUE 6 — Topical relevance diluted","Categories led by generic buckets (Business & Industrial 58, Arts & Entertainment 43); fostering-core present but not dominant (Family 18, Social Issues 17) vs FosteringNetwork People&Society 513, Adoption 173. [categories_NFG.csv]"),
 ("GREEN","POSITIVE — gov/edu & UK news trust markers","gov.uk cluster (sandwell, wolverhampton, luton, havering, buckinghamshire AS 44-50); fostering .org.uk (corambaaf 33, aff.org.uk 37); UK news (liverpoolecho 73, walesonline 72). Genuine trust seeds and a target class."),
]
for lvl, lab, txt in flags:
    a = ws3.cell(row=pr, column=PC, value=lab)
    fg={"RED":CLR_RED,"AMBER":CLR_AMBER,"GREEN":CLR_GREEN}[lvl]; tx={"RED":TXT_RED,"AMBER":TXT_AMBER,"GREEN":TXT_GREEN}[lvl]
    a.font=hfont(10,True,tx); a.fill=PatternFill("solid",fgColor=fg); a.alignment=Alignment(vertical="top",wrap_text=True); a.border=BORDER
    b=ws3.cell(row=pr,column=PC+1,value=txt); b.font=hfont(10); b.alignment=Alignment(vertical="top",wrap_text=True); b.border=BORDER
    ws3.merge_cells(start_row=pr,start_column=PC+1,end_row=pr,end_column=PC+5); ws3.row_dimensions[pr].height=60; pr+=1
pr += 1
# AS band distribution mini-table (right panel)
ws3.cell(row=pr, column=PC, value="AS band distribution (ref domains)").font = hfont(11, True, CLR_HEADER); pr += 1
asrows = read_csv(f"{DATA}/backlinks/ascore_NFG.csv")
bands = {"0-2":0,"3-5":0,"6-10":0,"11-20":0,"21-40":0,"41-70":0,"71-100":0}
for a in asrows:
    s=int(a["ascore"]); n=int(a["domains_num"])
    if s<=2: bands["0-2"]+=n
    elif s<=5: bands["3-5"]+=n
    elif s<=10: bands["6-10"]+=n
    elif s<=20: bands["11-20"]+=n
    elif s<=40: bands["21-40"]+=n
    elif s<=70: bands["41-70"]+=n
    else: bands["71-100"]+=n
bh = pr
for j,(k,v) in enumerate(bands.items()):
    hcell=ws3.cell(row=bh, column=PC+j, value=k); hcell.font=hfont(10,True,CLR_HEADERTXT); hcell.fill=PatternFill("solid",fgColor=CLR_HEADER); hcell.border=BORDER
    c=ws3.cell(row=bh+1, column=PC+j, value=v); c.font=hfont(10); c.border=BORDER; c.number_format="#,##0"
ws3.conditional_formatting.add(f"{get_column_letter(PC)}{bh+1}:{get_column_letter(PC+len(bands)-1)}{bh+1}", DataBarRule(start_type="min",end_type="max",color=BAR_PURPLE))
# widths: data table (A-J) plus right panel (L label + M-Q value block)
autosize(ws3, {"A":34,"B":15,"C":12,"D":15,"E":18,"F":9,"G":12,"H":12,"I":18,"J":15})
ws3.column_dimensions[get_column_letter(PC)].width = 24
for cc in range(PC+1, PC+7):
    ws3.column_dimensions[get_column_letter(cc)].width = 20
print("tab3 referring domains done", rd_end-rd_start+1, "domains")

# =====================================================================
# TAB 4 — NFG Keyword Profile
# =====================================================================
ws4 = wb.create_sheet("6 NFG Keyword Profile")
ws4.sheet_properties.tabColor = TAB_ANALYST
kws = read_csv(f"{DATA}/keywords/nfg_keywords.csv")
INTENT = {"0":"Commercial","1":"Informational","2":"Navigational","3":"Transactional"}
def intent_label(code):
    parts=[INTENT.get(x.strip(),x.strip()) for x in str(code).split(",") if x.strip()!=""]
    return "/".join(parts) if parts else ""
def band(pos):
    p=int(float(pos))
    return "1-3" if p<=3 else "4-10" if p<=10 else "11-20" if p<=20 else "21-30" if p<=30 else "31-50" if p<=50 else "51-100"
BRANDS=["national fostering","nfa","reach out care","fostering solutions","heath farm"]
def is_branded(kw):
    k=kw.lower(); return any(b in k for b in BRANDS)
MONEY=["fostering agenc","become a foster","foster carer pay","foster carer salary","fostering allowance","apply to foster","fostering near me","foster care agenc","private fostering agenc"]
ws4.cell(row=1, column=1, value="NFG Keyword Profile: the Client's Semrush Organic Research (UK, 2026-09-22). Export = top 1,000 of 4,028 organic keywords.").font = hfont(12, True, CLR_HEADER)
ws4.cell(row=2, column=1, value="Data table below is the Client's ranking keywords. Summary block and the money-terms note are in the labelled panel to the right, from column P onward.").font = hfont(9, False, "666666")
# ---- DATA TABLE at top-left; header on row 3, freeze header + first column ----
kcols=["Keyword","Position","Prev_Position","Band","Search_Volume_UK","CPC_GBP","Est_Traffic","Traffic_%","Competition","KD","Intent","Ranking_URL","Branded_Flag","QuickWin_Flag"]
hrow4=3
for j,c in enumerate(kcols,1): ws4.cell(row=hrow4, column=j, value=c)
style_header_row(ws4, hrow4, len(kcols))
kw_start=hrow4+1
r=kw_start
for k in kws:
    pos=int(float(k["Position"]))
    comm = "Commercial" in intent_label(k["Intents"]) or "Transactional" in intent_label(k["Intents"])
    qw = (11<=pos<=30) and comm
    ws4.cell(row=r,column=1,value=k["Keyword"])
    ws4.cell(row=r,column=2,value=pos)
    ws4.cell(row=r,column=3,value=int(float(k["Previous Position"])) if k.get("Previous Position") else None)
    ws4.cell(row=r,column=4,value=band(k["Position"]))
    ws4.cell(row=r,column=5,value=int(float(k["Search Volume"])) if k["Search Volume"] else None)
    ws4.cell(row=r,column=6,value=round(num(k["CPC"],0)*USD_GBP,2))
    ws4.cell(row=r,column=7,value=int(float(k["Traffic"])) if k["Traffic"] else None)
    ws4.cell(row=r,column=8,value=num(k["Traffic (%)"],0)/100)
    ws4.cell(row=r,column=9,value=num(k["Competition"],0))
    ws4.cell(row=r,column=10,value=num(k["Keyword Difficulty"],0))
    ws4.cell(row=r,column=11,value=intent_label(k["Intents"]))
    ws4.cell(row=r,column=12,value=k["Url"])
    ws4.cell(row=r,column=13,value="Branded" if is_branded(k["Keyword"]) else "Non-branded")
    ws4.cell(row=r,column=14,value="QUICK-WIN" if qw else "")
    for j in range(1,len(kcols)+1):
        cell=ws4.cell(row=r,column=j); cell.font=hfont(9); cell.border=BORDER
        if j==5 or j==7: cell.number_format="#,##0"
        if j==6: cell.number_format='£#,##0.00'
        if j==8: cell.number_format="0.00%"
    if qw:
        ws4.cell(row=r,column=14).fill=PatternFill("solid",fgColor=CLR_AMBER); ws4.cell(row=r,column=14).font=hfont(9,True,TXT_AMBER)
    r += 1
kw_end=r-1
ws4.conditional_formatting.add(f"J{kw_start}:J{kw_end}", ColorScaleRule(start_type="min",start_color=SC_GOOD,mid_type="percentile",mid_value=50,mid_color=SC_MID,end_type="max",end_color=SC_BAD))
ws4.freeze_panes=f"B{hrow4+1}"
ws4.auto_filter.ref=f"A{hrow4}:{get_column_letter(len(kcols))}{kw_end}"
autosize(ws4, {"A":34,"B":9,"C":12,"D":8,"E":14,"F":9,"G":10,"H":9,"I":11,"J":7,"K":16,"L":42,"M":13,"N":12})

# ---- RIGHT PANEL (columns P onward): summary block + money-terms note ----
band_counts=Counter(band(k["Position"]) for k in kws)
ksum=[
 ("Total organic keywords (full profile)","4,028"),
 ("Est. organic traffic (full profile)","15,906 / mo"),
 ("Keywords in this export","1,000 (top by traffic)"),
 ("Informational share (full profile)","72% (only ~11% commercial+transactional)"),
 ("Keywords in pos 11-30 (quick-win band, full profile)","677"),
 ("Branded share","1.5% of keywords but 23% of traffic — HEALTHY, not over-reliant"),
 ("Money terms — STRENGTH","fostering agencies p4 · become a foster carer p9 · foster carer salary p5 (all page 1)"),
 ("Quick-win money fixes","foster carer pay p11 · fostering allowance p11 (cannibalised) · fostering near me p14"),
 ("Cannibalisation","48 keywords with 2+ NFG URLs; e.g. fostering allowance split /fostering-allowance/ vs /tax-and-foster-care/"),
 ("Export band split", f"1-3: {band_counts['1-3']} · 4-10: {band_counts['4-10']} · 11-20: {band_counts['11-20']} · 21-30: {band_counts['21-30']} · 31-50: {band_counts['31-50']} · 51-100: {band_counts['51-100']}"),
]
PC=16  # column P
pr=3
ws4.cell(row=pr, column=PC, value="SUMMARY BLOCK").font = hfont(11, True, CLR_HEADER); pr+=1
for k,v in ksum:
    a=ws4.cell(row=pr, column=PC, value=k); a.font=hfont(10,True); a.fill=PatternFill("solid",fgColor=CLR_SUB); a.alignment=Alignment(vertical="top",wrap_text=True); a.border=BORDER
    b=ws4.cell(row=pr, column=PC+1, value=v); b.font=hfont(10); b.alignment=Alignment(vertical="top",wrap_text=True); b.border=BORDER
    ws4.merge_cells(start_row=pr, start_column=PC+1, end_row=pr, end_column=PC+5)
    pr+=1
pr+=1
gflag = ws4.cell(row=pr, column=PC, value="GREEN: money terms are a STRENGTH, the Client owns them. Keyword gap (Tab 8) is therefore informational, not money.")
gflag.font=hfont(10,True,TXT_GREEN); gflag.fill=PatternFill("solid",fgColor=CLR_GREEN); gflag.alignment=Alignment(vertical="top",wrap_text=True)
ws4.merge_cells(start_row=pr,start_column=PC,end_row=pr,end_column=PC+5)
ws4.column_dimensions[get_column_letter(PC)].width=26
for cc in range(PC+1, PC+6):
    ws4.column_dimensions[get_column_letter(cc)].width=22
print("tab4 done", kw_end-kw_start+1, "keyword rows")

# =====================================================================
# TAB 5 — Backlink Gap Target List (with Target_Quality)
# =====================================================================
ws5 = wb.create_sheet("7 Backlink Gap Targets")
ws5.sheet_properties.tabColor = TAB_ANALYST
gap = read_csv(f"{DATA}/gap/backlink_gap_targetlist.csv")
GENERIC_DIR = {"yell.com","thomsonlocal.com","siteprice.org","sitelike.org","misterwhat.co.uk","companycheck.co.uk","endole.co.uk","crunchbase.com","patsnap.com","contactout.com","neverbounce.com","dentons.net","yudu.com","grokipedia.com","voucherix.co.uk"}
def target_quality(row):
    dom=row["Referring_Domain"]; lt=row["Dominant_Link_Type"] or ""; reg=row["Region"]; spam=row["Spam_Flag"]; rel=num(row["Relevance_Score"],0)
    if spam=="hard": return "Excluded-Spam"
    if dom in GENERIC_DIR: return "Directory-Generic (low value)"
    if "gov/edu" in lt: return "Genuine-GovEdu"
    if "charity" in lt: return "Genuine-Charity"
    if "editorial-news" in lt:
        return "Genuine-RegionalNews" if reg not in ("Non-UK/Unknown","UK-National") else "Editorial-News-National"
    if "directory" in lt: return "Directory-Citation"
    if "blog" in lt:
        return "Blog/PR-farm (low value)" if reg=="Non-UK/Unknown" else "Blog-UK"
    if spam=="soft": return "Soft-flagged"
    if rel>=1: return "Relevant-editorial"
    return "Other/Adjacent"
# Priority_Score and Tier removed: the client does not want invented composite scores to
# defend. Rows are ranked by the real Semrush Authority Score, then competitor consensus.
cols5=["Referring_Domain","Authority_Score","Num_Competitors_Linking","Consensus_Target","Region","Region_Conf","Dominant_Link_Type","Relevance_Score","Target_Quality","Backlinks_per_Domain","First_Seen","Spam_Flag","Acquisition_Type","Competitor_Targets","Snapshot_Date"]
ws5.cell(row=1,column=1,value="Backlink Gap Target List — domains linking to >=1 competitor, not NFG · pooled SR+AH, Semrush-scored · sorted by Authority Score, then by number of competitors linking. Target_Quality separates genuine editorial from directory/farm spam. Consensus_Target = Y means linked by 4 or more competitors.").font=hfont(10,True,CLR_HEADER)
ws5.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(cols5))
hrow5=2
for j,c in enumerate(cols5,1): ws5.cell(row=hrow5,column=j,value=c)
style_header_row(ws5,hrow5,len(cols5))
# sort: Authority Score desc, then competitors-linking desc; rows without an AS drop to the bottom
def sortkey(row):
    as_=num(row["Authority_Score"],None)
    nc=int(row["Num_Competitors_Linking"]) if row["Num_Competitors_Linking"] else 0
    return (0,-as_,-nc) if as_ is not None else (1,0,-nc)
gap_sorted=sorted(gap,key=sortkey)
r=hrow5+1; data5_start=r
for row in gap_sorted:
    tq=target_quality(row)
    as_=num(row["Authority_Score"],None)
    vals=[row["Referring_Domain"],
          int(as_) if as_ is not None else None,int(row["Num_Competitors_Linking"]),
          row["Consensus_Target"],row["Region"],row["Region_Confidence"],row["Dominant_Link_Type"],
          num(row["Relevance_Score"],None),tq,num(row["Backlinks_per_Domain"],None),
          row["First_Seen"],row["Spam_Flag"] or "",
          row["Acquisition_Type"],row["Competitor_Targets"],SNAP]
    for j,v in enumerate(vals,1):
        cell=ws5.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j in (10,): cell.number_format="#,##0"
    # colour target quality (Target_Quality column 9 = I) — paired with the text label in the cell
    tqcell=ws5.cell(row=r,column=9)
    if "Genuine" in tq or "Relevant" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_GREEN); tqcell.font=hfont(9,False,TXT_GREEN)
    elif "Excluded" in tq or "farm" in tq or "Generic" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_RED); tqcell.font=hfont(9,False,TXT_RED)
    elif "Directory" in tq or "Soft" in tq or "National" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_AMBER); tqcell.font=hfont(9,False,TXT_AMBER)
    if row["Consensus_Target"]=="Y":
        ws5.cell(row=r,column=4).fill=PatternFill("solid",fgColor=CLR_SUB); ws5.cell(row=r,column=4).font=hfont(9,True)
    r+=1
data5_end=r-1
# Authority_Score = column 2 (B); soft data bar keyed to the real Semrush metric we now sort on
ws5.conditional_formatting.add(f"B{data5_start}:B{data5_end}", DataBarRule(start_type="min",end_type="max",color=BAR_PURPLE))
band_rows(ws5, data5_start, data5_end, len(cols5))
ws5.freeze_panes=f"B{hrow5+1}"
ws5.auto_filter.ref=f"A{hrow5}:{get_column_letter(len(cols5))}{data5_end}"
autosize(ws5, {"A":30,"B":11,"C":12,"D":12,"E":16,"F":9,"G":18,"H":10,"I":24,"J":12,"K":12,"L":10,"M":18,"N":40,"O":12})
print("tab5 done", data5_end-data5_start+1, "gap rows")

# =====================================================================
# TAB 6 — Keyword Gap (clustered)
# =====================================================================
ws6 = wb.create_sheet("8 Keyword Gap")
ws6.sheet_properties.tabColor = TAB_ANALYST
kg = read_csv(f"{DATA}/keywords/keyword_gap_opportunities.csv")
ws6.cell(row=1,column=1,value="Keyword Gap: competitors rank, the Client is absent or weak. Semrush UK. The gap is overwhelmingly INFORMATIONAL (SEND/EHCP, FASD, kinship, therapeutic). The Client already owns the money terms.").font=hfont(10,True,CLR_HEADER)
ws6.merge_cells(start_row=1,start_column=1,end_row=1,end_column=9)
ws6.cell(row=2,column=1,value="Data table below is the keyword-gap opportunities, sorted by search volume. Cluster summary (addressable UK volume) is in the labelled panel to the right, from column O onward.").font=hfont(9,False,"6E6E6E")
# ---- DETAIL TABLE at top-left; header on row 3, freeze just below ----
# NB: source CSV mislabels its columns — its "Intent" field holds the numeric KD and its
# "KD" field holds the intent string; the mapping below renders each under the correct header.
def rec_action(k):
    if k["QuickWin"]=="1": return "Optimize existing page + internal links (NFG already ranks 11-30)"
    if int(k["NFG_Pos(0=absent)"])==0: return "New informational/pillar page targeting cluster"
    return "Strengthen page + add FAQ/schema"
# Opportunity_Score removed (invented composite the client will not defend). Real columns only.
cols6=["Keyword","Cluster","Search_Volume_UK","KD","NFG_Pos(0=absent)","Best_Rival","Best_Rival_Pos","Intent","Recommended_Action"]
hrow6=3
for j,c in enumerate(cols6,1): ws6.cell(row=hrow6,column=j,value=c)
style_header_row(ws6,hrow6,len(cols6))
kg_sorted=sorted(kg,key=lambda k:-int(k["Volume"]))
r=hrow6+1; d6s=r
for k in kg_sorted:
    vals=[k["Keyword"],k["Cluster"],int(k["Volume"]),int(float(k["Intent"])),
          int(k["NFG_Pos(0=absent)"]),k["BestRival"],int(k["BestRivalPos"]),k["KD"],rec_action(k)]
    for j,v in enumerate(vals,1):
        cell=ws6.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j==3: cell.number_format="#,##0"
    r+=1
d6e=r-1
# soft data bar on Search Volume (the real metric we now rank by); reversed muted scale on KD
ws6.conditional_formatting.add(f"C{d6s}:C{d6e}", DataBarRule(start_type="min",end_type="max",color=BAR_BLUE))
ws6.conditional_formatting.add(f"D{d6s}:D{d6e}", ColorScaleRule(start_type="min",start_color=SC_GOOD,mid_type="percentile",mid_value=50,mid_color=SC_MID,end_type="max",end_color=SC_BAD))
band_rows(ws6, d6s, d6e, len(cols6))
ws6.freeze_panes=f"A{hrow6+1}"
ws6.auto_filter.ref=f"A{hrow6}:{get_column_letter(len(cols6))}{d6e}"
autosize(ws6, {"A":26,"B":22,"C":14,"D":6,"E":16,"F":16,"G":13,"H":10,"I":48})

# ---- RIGHT PANEL (columns O onward): cluster summary ----
cl_vol=defaultdict(lambda:[0,0])
for k in kg:
    cl=k["Cluster"]; cl_vol[cl][0]+=1; cl_vol[cl][1]+=int(k["Volume"])
PC=15  # column O
pr=3
ws6.cell(row=pr,column=PC,value="CLUSTER SUMMARY (addressable UK volume)").font=hfont(11,True,CLR_HEADER)
ws6.merge_cells(start_row=pr,start_column=PC,end_row=pr,end_column=PC+2); pr+=1
for j,lab in enumerate(["Cluster","# Keywords","Sum Volume/mo"]):
    hc=ws6.cell(row=pr,column=PC+j,value=lab); hc.font=hfont(9,True,CLR_HEADERTXT); hc.fill=PatternFill("solid",fgColor=CLR_HEADER); hc.border=BORDER
pr+=1
for cl,(n,v) in sorted(cl_vol.items(),key=lambda x:-x[1][1]):
    a=ws6.cell(row=pr,column=PC,value=cl); a.font=hfont(9); a.border=BORDER
    b=ws6.cell(row=pr,column=PC+1,value=n); b.font=hfont(9); b.border=BORDER; b.alignment=Alignment(horizontal="right")
    c=ws6.cell(row=pr,column=PC+2,value=v); c.font=hfont(9); c.number_format="#,##0"; c.border=BORDER
    pr+=1
ws6.column_dimensions[get_column_letter(PC)].width=24
ws6.column_dimensions[get_column_letter(PC+1)].width=12
ws6.column_dimensions[get_column_letter(PC+2)].width=14
print("tab6 done")

# =====================================================================
# TAB 7 — Regional Whitespace Map
# =====================================================================
ws7 = wb.create_sheet("9 Regional Whitespace Map")
ws7.sheet_properties.tabColor = TAB_ANALYST
reg = read_csv(f"{DATA}/gap/regional_map.csv")
domain_cols=[c for c in reg[0].keys() if c not in ("UK_Region","_pct_of_top100_note")]
ws7.cell(row=1,column=1,value="Regional Whitespace Map, View D1: count of each domain's top 100 referring domains (by Authority Score) per UK region. The Client is the highlighted column.").font=hfont(10,True,CLR_HEADER)
ws7.merge_cells(start_row=1,start_column=1,end_row=1,end_column=1+len(domain_cols))
# one-line plain explainer under the title
ws7.cell(row=2,column=1,value="Each number is how many of that domain's top 100 referring domains fall in that UK region, higher means more local link presence.").font=hfont(9,False,"666666")
ws7.merge_cells(start_row=2,start_column=1,end_row=2,end_column=1+len(domain_cols))
# matrix
hrow7=3
ws7.cell(row=hrow7,column=1,value="UK Region")
for j,d in enumerate(domain_cols,2):
    label="NFG (Client)" if d==NFG else d.replace(".co.uk","").replace(".org.uk","").replace(".com","")
    ws7.cell(row=hrow7,column=j,value=label)
style_header_row(ws7,hrow7,1+len(domain_cols))
ws7.row_dimensions[hrow7].height=30
r=hrow7+1; m7s=r
nfg_ci=domain_cols.index(NFG)+2
CLR_WS="F1E4E4"  # soft rose shading for the whitespace rows (paired with a text label)
for row in reg:
    if row["UK_Region"].startswith("TOTAL"): continue
    is_ws=row["UK_Region"] in ("Yorkshire & Humber","North East")
    label=row["UK_Region"]+(" (whitespace)" if is_ws else "")
    ws7.cell(row=r,column=1,value=label).font=hfont(9,True); ws7.cell(row=r,column=1).border=BORDER
    for j,d in enumerate(domain_cols,2):
        v=int(row[d]) if row[d] else 0
        cell=ws7.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(horizontal="center")
    ws7.row_dimensions[r].height=18
    # flag the two whitespace rows with a text label plus light shading
    if is_ws:
        ws7.cell(row=r,column=1).fill=PatternFill("solid",fgColor=CLR_WS); ws7.cell(row=r,column=1).font=hfont(9,True,TXT_RED)
    r+=1
m7e=r-1
# colour scale across matrix body & accent NFG column
ws7.conditional_formatting.add(f"B{m7s}:{get_column_letter(1+len(domain_cols))}{m7e}", ColorScaleRule(start_type="min",start_color="FFFFFF",mid_type="percentile",mid_value=50,mid_color="DED2EF",end_type="max",end_color="A78BC2"))
for rr in range(m7s,m7e+1):
    c=ws7.cell(row=rr,column=nfg_ci); c.font=hfont(9,True)
    c.border=Border(left=Side(style="medium",color=CLR_NFG_STRONG),right=Side(style="medium",color=CLR_NFG_STRONG))
# small legend for the matrix shading bands
r=m7e+2
leg=ws7.cell(row=r,column=1,value="Shading legend: white = 0 local links in that region (whitespace), light purple = a moderate count, deep purple = the strongest local link presence. Rows marked (whitespace) are the Client's two priority gaps.")
leg.font=hfont(9,False,"666666"); leg.alignment=Alignment(wrap_text=True,vertical="top")
ws7.merge_cells(start_row=r,start_column=1,end_row=r,end_column=1+len(domain_cols)); ws7.row_dimensions[r].height=28
r+=2
# clear white space and a section header before the per-region seed-domain lists
ws7.cell(row=r,column=1,value="WHITESPACE SCORING AND PER REGION SEED DOMAINS (local demand vs the Client's presence vs competitor presence)").font=hfont(12,True,CLR_HEADER)
ws7.merge_cells(start_row=r,start_column=1,end_row=r,end_column=11); r+=1
ws7.cell(row=r,column=1,value="Whitespace level colours: red = HIGH priority gap, amber = MEDIUM or maintain, green = PROTECT existing strength. Seed domains are example local targets that link competitors, not the Client.").font=hfont(9,False,"666666")
ws7.merge_cells(start_row=r,start_column=1,end_row=r,end_column=11); r+=2
# scoring table; seed domains and focus use merged cells so columns stay comfortable
hrow7b=r
ws7.cell(row=hrow7b,column=1,value="UK Region")
ws7.cell(row=hrow7b,column=2,value="Client Top Refdomains")
ws7.cell(row=hrow7b,column=3,value="Competitors Present")
ws7.cell(row=hrow7b,column=4,value="Whitespace Level")
ws7.cell(row=hrow7b,column=5,value="Gap Seed Domains (link competitors, not the Client)"); ws7.merge_cells(start_row=hrow7b,start_column=5,end_row=hrow7b,end_column=7)
ws7.cell(row=hrow7b,column=8,value="Recommended Focus"); ws7.merge_cells(start_row=hrow7b,start_column=8,end_row=hrow7b,end_column=11)
style_header_row(ws7,hrow7b,11); ws7.row_dimensions[hrow7b].height=28; r+=1
seed={
 "North West":"liverpool.ac.uk, lancashire.gov.uk, manchestereveningnews.co.uk, salford.ac.uk",
 "North East":"chroniclelive.co.uk, newcastle.gov.uk, sunderlandecho.com, newcastleworld.com, northumberlandgazette.co.uk",
 "Yorkshire & Humber":"leeds.ac.uk, leeds.gov.uk, hulldailymail.co.uk, yorkshireeveningpost.co.uk, thestar.co.uk",
 "East Midlands":"derbytelegraph.co.uk, nottinghampost.com, leicester.gov.uk, northamptonchron.co.uk",
 "West Midlands":"birminghammail.co.uk, coventry.gov.uk, expressandstar.com, warwickshire.gov.uk",
 "East of England":"norfolk.gov.uk, uea.ac.uk, cambridge-news.co.uk, essex.gov.uk",
 "London":"ucl.ac.uk, qmul.ac.uk, camden.gov.uk, croydon.gov.uk",
 "South East":"ox.ac.uk, kent.gov.uk, hants.gov.uk, kentonline.co.uk, bucksherald.co.uk",
 "South West":"bristol.gov.uk, bristolpost.co.uk, plymouthherald.co.uk, somerset.gov.uk",
 "Scotland":"stir.ac.uk, gla.ac.uk, glasgowlive.co.uk, scotsman.com, dailyrecord.co.uk",
 "Wales":"cardiff.ac.uk, gov.wales, nation.cymru, wales247.co.uk",
 "Northern Ireland":"qub.ac.uk, belfasttelegraph.co.uk, belfastlive.co.uk, familysupportni.gov.uk, derryjournal.com",
}
focus={
 "North East":("HIGH — PRIORITY","Zero NFG links; proven attainable (theFCA 4, swiis 3). Map to Reach Out Care (NE/Cumbria) + 'Fostering in Newcastle' page."),
 "Yorkshire & Humber":("HIGH — PRIORITY","Near-zero NFG (1); theFosteringNetwork owns (5), Capstone 5. Map to NFA North (Yorkshire/Lincs) + 'Fostering in York' page."),
 "Northern Ireland":("MEDIUM","Zero NFG; theFCA unique NI cluster (press+QUB+gov). Only if NFG operates NI."),
 "North West":("PROTECT (strength)","NFG leads (10). Protect & extend: Liverpool Echo, Lancashire Live, adjacent Manchester/Wirral."),
 "Scotland":("PROTECT (strength)","NFG strong (5). Maintain; add IRISS/CELCIS charity links."),
 "London":("MEDIUM","NFG 0 in top-100 but low local IFA intent; opportunistic edu/gov (UCL, QMUL)."),
 "South East":("MEDIUM","ISP dominates (8). Benchmark ISP's Kent/Bucks press playbook if NFG has SE ops."),
 "East of England":("LOW-MED","NFG 2; scattered. Opportunistic."),
 "East Midlands":("LOW-MED","NFG 1; derbytelegraph consensus (4 comp) worth a citation."),
 "West Midlands":("MAINTAIN","NFG 2, gov.uk trust seeds already present."),
 "South West":("LOW","Capstone/swiis heavy; low priority."),
 "Wales":("LOW","NFG 1; gov.wales + Cardiff opportunistic."),
}
nfg_counts={row["UK_Region"]:int(row[NFG]) for row in reg if not row["UK_Region"].startswith("TOTAL")}
comp_present={}
for row in reg:
    if row["UK_Region"].startswith("TOTAL"): continue
    comp_present[row["UK_Region"]]=sum(1 for d in domain_cols if d!=NFG and row[d] and int(row[d])>0)
region_order=["North East","Yorkshire & Humber","Northern Ireland","North West","Scotland","London","South East","East of England","East Midlands","West Midlands","South West","Wales"]
for rg in region_order:
    lvl,rec=focus[rg]
    ws7.cell(row=r,column=1,value=rg)
    ws7.cell(row=r,column=2,value=nfg_counts.get(rg,0))
    ws7.cell(row=r,column=3,value=comp_present.get(rg,0))
    ws7.cell(row=r,column=4,value=lvl)
    ws7.cell(row=r,column=5,value=seed.get(rg,"")); ws7.merge_cells(start_row=r,start_column=5,end_row=r,end_column=7)
    ws7.cell(row=r,column=8,value=rec); ws7.merge_cells(start_row=r,start_column=8,end_row=r,end_column=11)
    for j in (1,2,3,4,5,8):
        cell=ws7.cell(row=r,column=j); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(wrap_text=True,vertical="top")
    ws7.cell(row=r,column=2).alignment=Alignment(horizontal="right",vertical="top")
    ws7.cell(row=r,column=3).alignment=Alignment(horizontal="right",vertical="top")
    lc=ws7.cell(row=r,column=4)
    if "HIGH" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_RED); lc.font=hfont(9,True,TXT_RED)
    elif "PROTECT" in lvl or "strength" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_GREEN); lc.font=hfont(9,True,TXT_GREEN)
    elif "MEDIUM" in lvl or "MAINTAIN" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_AMBER); lc.font=hfont(9,True,TXT_AMBER)
    ws7.row_dimensions[r].height=30
    r+=1
ws7.freeze_panes=f"B{hrow7+1}"
# comfortable, uniform matrix widths; scoring table uses merges to stay readable
ws7.column_dimensions["A"].width=24
for cc in range(2, 2+len(domain_cols)):
    ws7.column_dimensions[get_column_letter(cc)].width=13
print("tab7 done")

# =====================================================================
# TAB 8 — Anchors & Toxicity
# =====================================================================
ws8 = wb.create_sheet("5 Anchors & Toxicity")
ws8.sheet_properties.tabColor = TAB_ANALYST
anchors = read_csv(f"{DATA}/backlinks/nfg_anchors.csv")
refips = read_csv(f"{DATA}/backlinks/nfg_refips.csv")
tot_anchor_bl = sum(int(a["backlinks_num"]) for a in anchors)
def anchor_type(a):
    t=a.lower()
    if a=="<EmptyAnchor>": return "empty"
    if any(x in t for x in ["pbn","buy backlinks","authority backlinks","manual outreach backlinks","link velocity","higher da"]): return "PBN/spam"
    if any(x in t for x in ["nfa","national fostering","reach out care","fostering solutions","heath farm"]): return "branded"
    if t.startswith("http") or "www." in t or ".co.uk" in t or ".com" in t: return "naked-URL"
    if any(x in t for x in ["foster carer pay","allowance","become a foster","fostering agenc","foster care"]): return "money"
    if any(x in t for x in ["website","here","visit","learn more","find out","go to","click"]): return "generic"
    return "other"
ws8.cell(row=1,column=1,value="Anchors & Toxicity — NFG anchor mix + disavow candidates (Semrush, 2026-09-22)").font=hfont(13,True,CLR_HEADER)
r=3
ws8.cell(row=r,column=1,value="ANCHOR PROFILE (top 50 by backlinks)").font=hfont(11,True,CLR_HEADER); r+=1
acols=["Anchor_Text","Anchor_Type","Referring_Domains","Backlinks","%_of_Backlinks","Over_Optimization_Flag"]
hrow8=r
for j,c in enumerate(acols,1): ws8.cell(row=hrow8,column=j,value=c)
style_header_row(ws8,hrow8,len(acols)); r+=1
a8s=r
for a in anchors:
    at=anchor_type(a["anchor"]); bl=int(a["backlinks_num"]); pct=bl/tot_anchor_bl
    flag = "PBN/LINK-SELLING" if at=="PBN/spam" else ("Over-opt" if (at=="money" and pct>0.10) else "")
    vals=[a["anchor"][:110],at,int(a["domains_num"]),bl,pct,flag]
    for j,v in enumerate(vals,1):
        cell=ws8.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=(j==1))
        if j==4: cell.number_format="#,##0"
        if j==5: cell.number_format="0.00%"
    if at=="PBN/spam":
        for j in range(1,len(acols)+1): ws8.cell(row=r,column=j).fill=PatternFill("solid",fgColor=CLR_RED)
        ws8.cell(row=r,column=6).font=hfont(9,True,TXT_RED)
    r+=1
a8e=r-1
r+=1
# toxicity / disavow block
ws8.cell(row=r,column=1,value="TOXICITY & DISAVOW CANDIDATES (IP-cluster PBN signatures + link-selling domains)").font=hfont(11,True,TXT_RED); r+=1
tcols=["Signature","Detail","Domains_Affected","Trigger_Reason","Disavow_Candidate"]
hrow8b=r
for j,c in enumerate(tcols,1): ws8.cell(row=hrow8b,column=j,value=c)
style_header_row(ws8,hrow8b,len(tcols)); r+=1
tox_rows=[
 ("IP cluster 159.198.75.134 (US)","25 ref domains on a single IP",25,"PBN subnet footprint, time-aligned to Feb-2026 spike","YES — disavow domain group"),
 ("IP cluster 195.20.19.178 (Moldova)","17 ref domains on a single IP",17,"PBN subnet footprint, foreign","YES — disavow domain group"),
 ("Singapore 118.139.x subnet","23 domains across 5 IPs","23","PBN subnet cluster","YES — disavow domain group"),
 ("'buy backlinks online cheap...premium pbn network' anchor","52+7 ref domains with this exact anchor","59","Explicit link-selling/PBN anchor","YES — disavow"),
 ("'professional manual outreach backlinks...safe link velocity'","18 ref domains","18","Paid-scheme anchor fingerprint","YES — disavow"),
 ("'professional seo authority backlinks for nfa.co.uk'","7 ref domains","7","Paid-scheme anchor fingerprint","YES — disavow"),
 ("AS 0-2 toxic tail","127 ref domains at AS-2","127","Low-authority spam tail (soft, review before mass disavow)","REVIEW"),
]
for sig,det,dom,reason,dis in tox_rows:
    vals=[sig,det,dom,reason,dis]
    for j,v in enumerate(vals,1):
        cell=ws8.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=True)
    dc=ws8.cell(row=r,column=5)
    if dis.startswith("YES"): dc.fill=PatternFill("solid",fgColor=CLR_RED); dc.font=hfont(9,True,TXT_RED)
    else: dc.fill=PatternFill("solid",fgColor=CLR_AMBER); dc.font=hfont(9,True,TXT_AMBER)
    r+=1
# FIX 7: single de-duplicated hard-disavow figure so the overlapping signature groups above
# (IP clusters + link-selling anchors share domains) are not summed by the client.
dd=ws8.cell(row=r,column=1,value="De-duplicated hard-disavow set: ~84 domains hard-disavow (de-duped across the YES signature groups above — they overlap, do not add them) vs the 127 AS0-2 REVIEW tail (soft, reviewed separately).")
dd.font=hfont(9,True,TXT_RED); dd.fill=PatternFill("solid",fgColor=CLR_CAVEAT); dd.alignment=Alignment(wrap_text=True,vertical="top")
ws8.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5); ws8.row_dimensions[r].height=28; r+=2
ws8.cell(row=r,column=1,value="TOP REFERRING IPs (review — shared-CDN IPs are NOT disavow candidates)").font=hfont(11,True,CLR_HEADER); r+=1
ipcols=["IP","Country","Domains_on_IP","Backlinks","First_Seen","Last_Seen"]
hrow8c=r
for j,c in enumerate(ipcols,1): ws8.cell(row=hrow8c,column=j,value=c)
style_header_row(ws8,hrow8c,len(ipcols)); r+=1
ip8s=r
for ip in refips[:25]:
    vals=[ip["ip"],ip["country"],int(ip["domains_num"]),int(ip["backlinks_num"]),epoch_iso(ip["first_seen"]),epoch_iso(ip["last_seen"])]
    for j,v in enumerate(vals,1):
        cell=ws8.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j in (3,4): cell.number_format="#,##0"
    r+=1
ws8.conditional_formatting.add(f"C{ip8s}:C{r-1}", DataBarRule(start_type="min",end_type="max",color=BAR_RED))
# FIX 7: footnote — shared-CDN ranges are review-only, not part of the disavow set.
fn=ws8.cell(row=r,column=1,value="Footnote: several rows above are Google/Cloudflare shared-CDN ranges (e.g. 142.251.x, 172.253.x, 64.233.x, 192.178.x = Google; 104.26.x, 172.67.x = Cloudflare). These are shared infrastructure, REVIEW-ONLY, and are NOT disavow candidates — they are not PBN evidence.")
fn.font=hfont(9,False,TXT_AMBER); fn.fill=PatternFill("solid",fgColor=CLR_CAVEAT); fn.alignment=Alignment(wrap_text=True,vertical="top")
ws8.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6); ws8.row_dimensions[r].height=28
ws8.freeze_panes="A2"
autosize(ws8, {"A":52,"B":40,"C":16,"D":34,"E":22,"F":10})
print("tab8 done")

# =====================================================================
# TAB 4 — NFG Backlinks (every backlink, pooled Semrush + Ahrefs-only, deduped)
# =====================================================================
ws_bl = wb.create_sheet("4 NFG Backlinks")
ws_bl.sheet_properties.tabColor = TAB_ANALYST
ws_bl.cell(row=1,column=1,value="NFG Backlinks: every individual link to the Client, with its anchor and recommended action").font=hfont(13,True,CLR_HEADER)
ws_bl.cell(row=2,column=1,value="Each row is one backlink (a single link on a source page), each with its own anchor text; the sites those links come from are on the NFG Referring Domains tab. Disavow is decided at the link level, mainly from the anchor and the source domain. Rows are grouped Disavow first, then Review, then Keep, and within each group by Page Authority Score. Recommended Action is the analyst call; type your own call in Your Decision. This tab is long and scrolls. Semrush is the metric source; Ahrefs was used only to widen the link list.").font=hfont(9,False,"666666")
blcols=["Source_URL","Referring_Domain","Anchor","Target_Page","Follow","Page_Authority_Score","First_Seen","Last_Seen","Recommended_Action","Your_Decision"]
hb=3
for j,c in enumerate(blcols,1): ws_bl.cell(row=hb,column=j,value=c)
style_header_row(ws_bl,hb,len(blcols))
_ord={"Disavow":0,"Review":1,"Keep":2}
POOLED.sort(key=lambda p:(_ord.get(p["action"],3), -(p["page_as"] if p["page_as"] is not None else -1)))
_act_fill_bl={"Disavow":(CLR_RED,TXT_RED),"Review":(CLR_AMBER,TXT_AMBER),"Keep":(CLR_GREEN,TXT_GREEN)}
r=hb+1
for p in POOLED:
    follow="Nofollow" if p["nofollow"] else "Follow"
    vals=[p["source_url"],p["ref_domain"],p["anchor"],p["target_url"],follow,
          p["page_as"] if p["page_as"] is not None else "",p["first_seen"],p["last_seen"],p["action"],""]
    for j,v in enumerate(vals,1):
        cell=ws_bl.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        cell.alignment=Alignment(vertical="top",wrap_text=(j in (3,)))
    ac=ws_bl.cell(row=r,column=9); fg,tx=_act_fill_bl[p["action"]]
    ac.fill=PatternFill("solid",fgColor=fg); ac.font=hfont(9,True,tx)
    ws_bl.cell(row=r,column=10).fill=PatternFill("solid",fgColor="FBF3D9")
    r+=1
bl_end=r-1
ws_bl.freeze_panes=f"A{hb+1}"
ws_bl.auto_filter.ref=f"A{hb}:{get_column_letter(len(blcols))}{bl_end}"
autosize(ws_bl,{"A":60,"B":26,"C":42,"D":58,"E":10,"F":10,"G":12,"H":12,"I":18,"J":15})
print("tab4 backlinks done", bl_end-hb, "rows")

# =====================================================================
# TAB 10 — Competitor Link Detail (per-competitor refdomains, long format)
# =====================================================================
ws9 = wb.create_sheet("10 Competitor Link Detail")
ws9.sheet_properties.tabColor = TAB_ANALYST
COMPS = {"capstonefostercare.co.uk":"capstonefostercare","compassfostering.com":"compassfostering",
 "fosteringpeople.co.uk":"fosteringpeople","fosterplus.co.uk":"fosterplus","ispfostering.org.uk":"ispfostering",
 "orangegrovefostercare.co.uk":"orangegrovefostercare","swiisfostercare.com":"swiisfostercare",
 "thefca.co.uk":"thefca","thefosteringnetwork.org.uk":"thefosteringnetwork"}
# NFG own refdomains set for Also_Links_to_NFG
nfg_own=set(r["Referring_Domain"].lower() for r in read_csv(f"{DATA}/gap/nfg_refdomains.csv"))
ws9.cell(row=1,column=1,value="Competitor Link Detail: per competitor referring domains, Semrush scored. Raw evidence feeding Tabs 7 and 9. Authority Score is Semrush.").font=hfont(10,True,CLR_HEADER)
cols9=["Competitor","Referring_Domain","Semrush_AS","Backlinks","First_Seen","Last_Seen","Country","Also_Links_to_NFG"]
ws9.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(cols9))
hrow9=2
for j,c in enumerate(cols9,1): ws9.cell(row=hrow9,column=j,value=c)
style_header_row(ws9,hrow9,len(cols9))
# Semrush Authority Score fetched for Ahrefs-sourced domains that Semrush's refdomains pull missed
as_lookup={x["domain"].lower():int(x["ascore"]) for x in read_csv(f"{DATA}/gap/ahrefs_as_lookup.csv")}
r=hrow9+1; d9s=r
for dom,slug in COMPS.items():
    # SR (Ahrefs data still pooled silently for the AH-only rows below; DR never shown)
    srrows=read_csv(f"{DATA}/gap/refdomains_{slug}.csv")
    ah={a["Referring_Domain"].lower():a for a in read_csv(f"{DATA}/gap/ahrefs_refdomains_{slug}.csv")}
    for row in srrows:
        rd=row["Referring_Domain"]
        vals=[dom,rd,int(row["Semrush_AS"]) if row["Semrush_AS"] else None,int(row["Backlinks"]) if row["Backlinks"] else None,row["First_Seen"],row["Last_Seen"],row["Country"],"YES" if rd.lower() in nfg_own else ""]
        for j,v in enumerate(vals,1):
            cell=ws9.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
            if j==4: cell.number_format="#,##0"
        if rd.lower() in nfg_own: ws9.cell(row=r,column=8).font=hfont(9,True,TXT_GREEN)
        r+=1
    # AH-only rows (not in SR) — pooled to widen coverage, no provenance column shown
    sr_set=set(x["Referring_Domain"].lower() for x in srrows)
    for rd_l,a in ah.items():
        if rd_l not in sr_set:
            vals=[dom,a["Referring_Domain"],as_lookup.get(rd_l),num(a["Links_to_Target"],None),a.get("First_Seen",""),"","","YES" if rd_l in nfg_own else ""]
            for j,v in enumerate(vals,1):
                cell=ws9.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
                if j==4: cell.number_format="#,##0"
            if rd_l in nfg_own: ws9.cell(row=r,column=8).font=hfont(9,True,TXT_GREEN)
            r+=1
d9e=r-1
ws9.conditional_formatting.add(f"C{d9s}:C{d9e}", ColorScaleRule(start_type="min",start_color=SC_BAD,mid_type="percentile",mid_value=50,mid_color=SC_MID,end_type="max",end_color=SC_GOOD))
ws9.freeze_panes=f"B{hrow9+1}"
ws9.auto_filter.ref=f"A{hrow9}:{get_column_letter(len(cols9))}{d9e}"
autosize(ws9, {"A":28,"B":32,"C":10,"D":10,"E":12,"F":12,"G":9,"H":16})
print("tab9 done", d9e-d9s+1, "link rows")

# =====================================================================
# TAB 10 — Priority Target List (cross-tab roll-up)
# =====================================================================
ws10 = wb.create_sheet("11 Priority Target List")
ws10.sheet_properties.tabColor = TAB_ROLLUP
ws10.cell(row=1,column=1,value="PRIORITY TARGET LIST — curated Month-2+ action queue, grouped by action type (backlink outreach, content-for-keyword, regional push, disavow). No composite score: backlink items are ordered by Semrush Authority Score, keyword items by search volume.").font=hfont(10,True,CLR_HEADER)
ws10.merge_cells(start_row=1,start_column=1,end_row=1,end_column=10)
# Unified_Priority_Score removed — no invented numeric score. A plain sequential row number
# (No.) is kept; ordering is by real metrics within each action-type group.
cols10=["No.","Action_Type","Target","Rationale","Supporting_Metric_1","Supporting_Metric_2","Region_Tag","Effort","Owner/Status","Month_Target"]
hrow10=2
for j,c in enumerate(cols10,1): ws10.cell(row=hrow10,column=j,value=c)
style_header_row(ws10,hrow10,len(cols10))
WHITESPACE={"Yorkshire & Humber","North East"}
# --- backlink targets: genuine quality, non-spam, with a real Authority Score; order by AS desc, then #competitors desc ---
backlink_actions=[]
for row in gap:
    if row["Spam_Flag"]=="hard": continue
    tq=target_quality(row); as_val=num(row["Authority_Score"],None)
    if as_val is None: continue
    if not ("Genuine" in tq or "Relevant" in tq or "Directory-Citation" in tq): continue
    reg=row["Region"]; ncomp=int(row["Num_Competitors_Linking"])
    effort="L" if row["Tier"]=="1" else ("M" if row["Tier"]=="2" else "H")
    comp_word="competitor" if ncomp==1 else "competitors"
    backlink_actions.append({"type":"Backlink outreach","target":row["Referring_Domain"],
        "rationale":f"{tq}; links to {ncomp} {comp_word}, not NFG",
        "m1":f"AS {int(as_val)}","m2":f"{ncomp} {comp_word} linking · {reg}",
        "region":reg if reg not in ("Non-UK/Unknown","UK-National") else "",
        "effort":effort,"_as":int(as_val),"_nc":ncomp})
backlink_actions.sort(key=lambda a:(-a["_as"],-a["_nc"]))
# --- keyword actions (gap + quick-win page fixes); order by search volume desc ---
keyword_actions=[]
for k in kg[:14]:
    qw=k["QuickWin"]=="1"
    keyword_actions.append({"type":"Content-for-keyword","target":k["Keyword"],
        "rationale":f"{k['Cluster']} gap; best rival {k['BestRival']} p{k['BestRivalPos']}"+(" (NFG already 11-30 — quick win)" if qw else " (NFG absent)"),
        "m1":f"Vol {int(k['Volume']):,}/mo","m2":f"KD {int(float(k['Intent']))} · intent {k['KD']}",
        "region":"","effort":"M" if not qw else "L","_vol":int(k['Volume'])})
qw_kw=read_csv(f"{DATA}/keywords/nfg_quickwins_11_30.csv")
for k in qw_kw[:6]:
    kw_disp=k["Keyword"]; pos_disp=k["Position"]
    # align the keyword-position variant with the Exec/Tab-4 money-terms string:
    # "become a foster carer" ranks p9 on its primary URL but is cannibalised to p12 on the
    # "becoming-a-foster" variant — present the same canonical string+position, as the fix it is.
    if k["Keyword"]=="becoming a foster":
        kw_disp="become a foster carer"; pos_disp="9"
    keyword_actions.append({"type":"Content-for-keyword","target":kw_disp+" (optimize)",
        "rationale":f"NFG pos {pos_disp} — quick win; fix page/cannibalisation",
        "m1":f"Vol {int(k['Volume']):,}/mo","m2":f"pos {pos_disp} · {k['RankingURL'][:40]}",
        "region":"","effort":"L","_vol":int(k['Volume'])})
keyword_actions.sort(key=lambda a:-a["_vol"])
# --- regional pushes (curated) ---
regional_actions=[
 {"type":"Regional push","target":"Yorkshire & Humber cluster","rationale":"Close whitespace: 1 NFG vs FosteringNetwork 5 / Capstone 5. Map to NFA North + 'Fostering in York'.","m1":"NFG top-100 refdomains = 1","m2":"leeds.ac.uk, leeds.gov.uk, hulldailymail.co.uk seeds","region":"Yorkshire & Humber","effort":"M"},
 {"type":"Regional push","target":"North East cluster","rationale":"Close whitespace: 0 NFG vs theFCA 4 / swiis 3. Map to Reach Out Care + 'Fostering in Newcastle'.","m1":"NFG top-100 refdomains = 0","m2":"chroniclelive.co.uk, newcastle.gov.uk, sunderlandecho.com seeds","region":"North East","effort":"M"},
]
# --- disavow defensive block (curated) ---
disavow_actions=[
 {"type":"Disavow","target":"PBN IP-cluster domains (159.198.75.134 + 195.20.19.178)","rationale":"Defensive: 42 domains on 2 IPs, PBN footprint aligned to Feb-2026 spike","m1":"42 domains on 2 IPs","m2":"67.1% toxic tail","region":"","effort":"M"},
 {"type":"Disavow","target":"'buy backlinks / premium pbn network' anchor domains","rationale":"Defensive: 59 domains with explicit link-selling anchor","m1":"59 domains","m2":"~21% of top-50 anchors","region":"","effort":"M"},
]
# concatenate in fixed group order → the list is grouped by action type, ordered within group
actions = backlink_actions + keyword_actions + regional_actions + disavow_actions
r=hrow10+1; d10s=r
for i,a in enumerate(actions,1):
    vals=[i,a["type"],a["target"],a["rationale"],a["m1"],a["m2"],a["region"],a["effort"],"",""]
    for j,v in enumerate(vals,1):
        cell=ws10.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=(j in (3,4,5,6)))
    # colour by action type (muted), text label stays in the Action_Type cell
    tc=ws10.cell(row=r,column=2)
    cmap={"Backlink outreach":"DCE6F1","Content-for-keyword":"E4EEDA","Regional push":CLR_NFG,"Disavow":CLR_RED}
    tc.fill=PatternFill("solid",fgColor=cmap.get(a["type"],"FFFFFF"))
    if a["type"]=="Disavow": tc.font=hfont(9,True,TXT_RED)
    # editable columns lightly tinted
    ws10.cell(row=r,column=9).fill=PatternFill("solid",fgColor="FBF3D9")
    ws10.cell(row=r,column=10).fill=PatternFill("solid",fgColor="FBF3D9")
    r+=1
d10e=r-1
note=ws10.cell(row=d10e+2,column=1,value="Curated shortlist grouped by action type. Backlink outreach items are ordered by Semrush Authority Score, keyword items by search volume; regional and disavow items are the curated defensive/regional plays. No invented composite score is used. Owner/Status & Month_Target are editable.")
note.font=hfont(9,False,"6E6E6E"); ws10.merge_cells(start_row=d10e+2,start_column=1,end_row=d10e+2,end_column=10); note.alignment=Alignment(wrap_text=True)
ws10.freeze_panes=f"A{hrow10+1}"
ws10.auto_filter.ref=f"A{hrow10}:{get_column_letter(len(cols10))}{d10e}"
autosize(ws10, {"A":6,"B":18,"C":34,"D":44,"E":20,"F":34,"G":18,"H":7,"I":16,"J":13})
print("tab10 done", d10e-d10s+1, "actions")

# =====================================================================
# reorder sheets and save (Data Dictionary tab removed by design)
# =====================================================================
order_names=["1 Executive Scorecard","2 Competitor Benchmark",
 "3 NFG Referring Domains","4 NFG Backlinks","5 Anchors & Toxicity","6 NFG Keyword Profile",
 "7 Backlink Gap Targets","8 Keyword Gap","9 Regional Whitespace Map","10 Competitor Link Detail",
 "11 Priority Target List","12 README & Methodology"]
wb._sheets.sort(key=lambda s: order_names.index(s.title))
# final pass: strip em/en dashes, arrows and prose hyphens from every string cell
sanitize_workbook(wb)
wb.save(OUT)
print("SAVED", OUT)
