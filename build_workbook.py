#!/usr/bin/env python3
"""Build NFG Month-1 Foundation Audit 12-tab workbook from collected CSVs."""
import csv, os, glob
from datetime import datetime, timezone
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.comments import Comment

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
CLR_CAVEAT = "FFF4E5"      # caveat box fill
CLR_GREEN = "C6EFCE"; TXT_GREEN = "006100"
CLR_AMBER = "FFEB9C"; TXT_AMBER = "9C6500"
CLR_RED = "FFC7CE"; TXT_RED = "9C0006"
CLR_GREY = "F2F2F2"

TAB_EXEC = "C9A227"    # gold
TAB_ANALYST = "2E6DA4" # blue
TAB_ROLLUP = "2E7D32"  # green
TAB_APPENDIX = "757575"# grey

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

TAGS = {NFG: "NFG (Target)", "thefca.co.uk": "Sector Body",
        "thefosteringnetwork.org.uk": "Sector Body", "capstonefostercare.co.uk": "Commercial IFA",
        "ispfostering.org.uk": "Commercial IFA", "fosterplus.co.uk": "Commercial IFA",
        "fosteringpeople.co.uk": "Commercial IFA", "swiisfostercare.com": "Commercial IFA",
        "compassfostering.com": "Commercial IFA", "orangegrovefostercare.co.uk": "Commercial IFA"}

print("shared data loaded")

# =====================================================================
# TAB 0 — README & Methodology
# =====================================================================
ws0 = wb.create_sheet("0 README & Methodology")
ws0.sheet_properties.tabColor = TAB_EXEC
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
r = kv(ws0, r, "Client (target)", "National Fostering Group — nationalfosteringgroup.co.uk (NFG)")
r = kv(ws0, r, "Agency", "SUSO Digital")
r = kv(ws0, r, "Snapshot date", SNAP + "  (single dated window; referenced by every tab header)")
r = kv(ws0, r, "Database / region", "UK")
r = kv(ws0, r, "Month-1 scope", "Foundation only — diagnostic + target map. No link placements or content shipped this month; Month 2+ outreach executes against Tabs 5, 6, 7 and 10.")
r = kv(ws0, r, "Deliverable file", "NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx (12 tabs)")
r += 1
h = ws0.cell(row=r, column=1, value="Governance — the two rules that bind every cell"); h.font = hfont(12, True, CLR_HEADER); r += 1
r = kv(ws0, r, "1. Metric firewall (Semrush-only)", "Every reported metric — Authority Score (AS), follow split, search volume, KD, traffic, CPC — is Semrush-sourced. Ahrefs DR/UR/traffic never appear in a client-facing metric cell.")
r = kv(ws0, r, "2. Lists may be pooled", "Raw backlink/refdomain LISTS pooled Semrush + Ahrefs to widen coverage, but every row is re-scored against Semrush AS before ranking. Ahrefs-only rows flagged AS_source=unmatched, kept in Raw, never scored. AS and DR never mixed in one column.")
r += 1
h = ws0.cell(row=r, column=1, value="Competitor set (9)"); h.font = hfont(12, True, CLR_HEADER); r += 1
r = kv(ws0, r, "Sector Body (weighted separately)", "thefca.co.uk · thefosteringnetwork.org.uk — high-authority, informational")
r = kv(ws0, r, "Commercial IFA (direct rivals)", "capstonefostercare.co.uk · ispfostering.org.uk · fosterplus.co.uk · fosteringpeople.co.uk · swiisfostercare.com · compassfostering.com · orangegrovefostercare.co.uk")
r += 1
h = ws0.cell(row=r, column=1, value="Metric definitions"); h.font = hfont(12, True, CLR_HEADER); r += 1
defs = [
 ("Authority Score (AS)", "Semrush 0-100 domain authority. NFG-reported metric. Not comparable to Ahrefs DR."),
 ("Referring Domain", "A unique root domain (eTLD+1, normalised) with >=1 link to the target."),
 ("Toxic tail %", "Share of referring domains scoring AS 0-10 (from backlinks_ascore_profile). Healthy profiles are pyramid-shaped."),
 ("Follow %", "follows / (follows + nofollows) at backlink level. Healthy ~50-75%; >90% = manipulation smell."),
 ("Gap (backlink)", "Referring domain links to >=1 competitor but NOT to NFG (pure gap after subtracting NFG's own set)."),
 ("Whitespace (regional)", "UK region with strong local demand where NFG is weak/absent and competitors are present."),
 ("Consensus target", "Referring domain linked by >=4 of 9 competitors (proven-relevant near-certain miss)."),
 ("Target_Quality", "Analyst classification separating genuine editorial/relevant targets from generic directories & blog/PR farms."),
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
 "Sector bodies (theFCA, FosteringNetwork) distort the set — benchmarked but tagged/weighted separately.",
 "Keyword export in Tab 4 is the top 1,000 of NFG's 4,028 organic keywords (Semrush cap); summary counts use full-profile totals.",
]
for cav in caveats:
    cell = ws0.cell(row=r, column=1, value="• " + cav); cell.font = hfont(9); cell.alignment = Alignment(wrap_text=True, vertical="top")
    cell.fill = PatternFill("solid", fgColor=CLR_CAVEAT)
    ws0.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    ws0.row_dimensions[r].height = 28; r += 1
r += 1
r = kv(ws0, r, "SUSO contact & sign-off", "Prepared by SUSO Digital SEO team · fahad.ahmad@susodigital.com · Sign-off: ____________  Date: __________")
r = kv(ws0, r, "Legend", "NFG rows/columns carry the purple accent. Flags are RED/AMBER/GREEN paired with text. SR=Semrush, AH=Ahrefs, Pooled=AH+SR list SR-scored.")
print("tab0 done")

# =====================================================================
# TAB 2 — Competitor Benchmark (10 rows) — built before Tab1 (Tab1 refs it)
# =====================================================================
ws2 = wb.create_sheet("2 Competitor Benchmark")
ws2.sheet_properties.tabColor = TAB_ANALYST
cols2 = ["Domain","Tag","Is_NFG","Authority_Score","Total_Backlinks","Referring_Domains",
         "Referring_IPs","Follow_%","Backlinks_per_RefDomain","Toxic_Tail_%","Organic_Keywords_UK",
         "Est_Organic_Traffic_UK","Est_Traffic_Cost_GBP","Pos_1_3","Pos_11_30_QuickWin","SemrushRank",
         "Index_AS","Index_RefDomains","Rank_AS","Rank_RefDomains","Composite_Strength","Snapshot_Date"]
title = ws2.cell(row=1, column=1, value=f"Competitor Benchmark — 10 domains, one Semrush snapshot {SNAP} (UK). Source: backlinks_comparison + benchmark_keywords. NFG row = purple accent.")
title.font = hfont(10, True, CLR_HEADER); ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(cols2))
for j, c in enumerate(cols2, 1):
    ws2.cell(row=2, column=j, value=c)
style_header_row(ws2, 2, len(cols2))
# order: NFG first then by AS desc
blmap = {r["target"]: r for r in bench_bl}
order = [NFG] + sorted([d for d in blmap if d != NFG], key=lambda d: -int(blmap[d]["ascore"]))
row = 3
first_data, last_data = 3, 3 + len(order) - 1
for dom in order:
    b = blmap[dom]; k = bench_kw.get(dom, {})
    follows = int(b["follows_num"]); nofollows = int(b["nofollows_num"])
    cost_usd = num(k.get("OrganicTrafficCost_USD"))
    vals = {
        "Domain": dom, "Tag": TAGS[dom], "Is_NFG": "YES" if dom == NFG else "no",
        "Authority_Score": int(b["ascore"]), "Total_Backlinks": int(b["backlinks_num"]),
        "Referring_Domains": int(b["domains_num"]), "Referring_IPs": int(b["ips_num"]),
        "Backlinks_per_RefDomain": round(int(b["backlinks_num"]) / max(int(b["domains_num"]),1), 1),
        "Toxic_Tail_%": round(TOX[dom], 3),
        "Organic_Keywords_UK": int(k["OrganicKeywords"]) if k.get("OrganicKeywords") not in (None,"NA") else None,
        "Est_Organic_Traffic_UK": int(k["OrganicTraffic"]) if k.get("OrganicTraffic") not in (None,"NA") else None,
        "Est_Traffic_Cost_GBP": round(cost_usd * USD_GBP, 2) if cost_usd is not None else None,
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
    row += 1
# formula columns: Index_AS, Index_RefDomains, Rank_AS, Rank_RefDomains, Composite_Strength
AScol=cL["Authority_Score"]; RDcol=cL["Referring_Domains"]; KWcol=cL["Organic_Keywords_UK"]; TRcol=cL["Est_Organic_Traffic_UK"]
IAcol=cL["Index_AS"]; IRcol=cL["Index_RefDomains"]; RAcol=cL["Rank_AS"]; RRcol=cL["Rank_RefDomains"]; CScol=cL["Composite_Strength"]
FUcol=cL["Follow_%"]; TTcol=cL["Toxic_Tail_%"]
as_rng=f"{AScol}{first_data}:{AScol}{last_data}"; rd_rng=f"{RDcol}{first_data}:{RDcol}{last_data}"
kw_rng=f"{KWcol}{first_data}:{KWcol}{last_data}"; tr_rng=f"{TRcol}{first_data}:{TRcol}{last_data}"
for row in range(first_data, last_data+1):
    ws2[f"{IAcol}{row}"] = f"=ROUND({AScol}{row}/MEDIAN({as_rng})*100,0)"
    ws2[f"{IRcol}{row}"] = f"=ROUND({RDcol}{row}/MEDIAN({rd_rng})*100,0)"
    ws2[f"{RAcol}{row}"] = f"=RANK({AScol}{row},{as_rng})"
    ws2[f"{RRcol}{row}"] = f"=RANK({RDcol}{row},{rd_rng})"
    # composite = mean of min-max normalized AS, RD, KW, TR
    ws2[f"{CScol}{row}"] = (
        f"=ROUND((({AScol}{row}-MIN({as_rng}))/(MAX({as_rng})-MIN({as_rng}))"
        f"+({RDcol}{row}-MIN({rd_rng}))/(MAX({rd_rng})-MIN({rd_rng}))"
        f"+({KWcol}{row}-MIN({kw_rng}))/(MAX({kw_rng})-MIN({kw_rng}))"
        f"+({TRcol}{row}-MIN({tr_rng}))/(MAX({tr_rng})-MIN({tr_rng})))/4,3)")
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
# conditional colour scale on Composite + AS; data bars on refdomains & traffic
ws2.conditional_formatting.add(f"{CScol}{first_data}:{CScol}{last_data}",
    ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50, mid_color="FFEB84", end_type="max", end_color="63BE7B"))
ws2.conditional_formatting.add(f"{AScol}{first_data}:{AScol}{last_data}",
    ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50, mid_color="FFEB84", end_type="max", end_color="63BE7B"))
ws2.conditional_formatting.add(f"{RDcol}{first_data}:{RDcol}{last_data}", DataBarRule(start_type="min", end_type="max", color="7C3AED"))
ws2.conditional_formatting.add(f"{tr_rng}", DataBarRule(start_type="min", end_type="max", color="2E6DA4"))
# toxic tail: red scale (high=bad) reversed
ws2.conditional_formatting.add(f"{TTcol}{first_data}:{TTcol}{last_data}",
    ColorScaleRule(start_type="min", start_color="63BE7B", mid_type="percentile", mid_value=50, mid_color="FFEB84", end_type="max", end_color="F8696B"))
# gap note row
gnr = last_data + 2
ws2.cell(row=gnr, column=1, value="Framing numbers:").font = hfont(10, True, CLR_HEADER)
ws2.cell(row=gnr+1, column=1, value=f"AS: NFG 36 = rank 2/10, median 29, gap-to-median +7, gap-to-leader -3 (best of 7 Commercial IFAs — but recency-inflated, see Tab 3).").font = hfont(9)
ws2.cell(row=gnr+2, column=1, value=f"Referring Domains: NFG 420 = rank 9/10, median 821.5, gap-to-median -401.5, field best 1,892. This -401.5 frames the Month-2+ deliverable.").font = hfont(9)
ws2.cell(row=gnr+3, column=1, value="Capstone caveat: 127,526 backlinks / 156.9-per-domain (~30x cohort median) is a volume-inflation outlier — score on AS + ref domains, not raw backlink count.").font = hfont(9, False, TXT_AMBER)
ws2.merge_cells(start_row=gnr+1, start_column=1, end_row=gnr+1, end_column=len(cols2))
ws2.merge_cells(start_row=gnr+2, start_column=1, end_row=gnr+2, end_column=len(cols2))
ws2.merge_cells(start_row=gnr+3, start_column=1, end_row=gnr+3, end_column=len(cols2))
ws2.freeze_panes = "B3"
ws2.auto_filter.ref = f"A2:{get_column_letter(len(cols2))}{last_data}"
autosize(ws2, {"A":30,"B":15,"C":8,"D":9,"E":13,"F":11,"G":11,"H":9,"I":12,"J":11,"K":13,"L":14,"M":13,"N":8,"O":13,"P":12,"Q":9,"R":11,"S":9,"T":11,"U":12,"V":12})
BENCH = {"sheet":"2 Competitor Benchmark","AScol":AScol,"RDcol":RDcol,"TBcol":cL["Total_Backlinks"],
         "KWcol":KWcol,"TRcol":TRcol,"FUcol":FUcol,"TTcol":TTcol,"first":first_data,"last":last_data,
         "nfg_row":first_data}
print("tab2 done")

# =====================================================================
# TAB 1 — Executive Scorecard (references Tab 2)
# =====================================================================
ws1 = wb.create_sheet("1 Executive Scorecard")
ws1.sheet_properties.tabColor = TAB_EXEC
S = f"'{BENCH['sheet']}'"; fd, ld = BENCH["first"], BENCH["last"]; nr = BENCH["nfg_row"]
t = ws1.cell(row=1, column=1, value="Executive Scorecard — NFG vs the field (9 competitors)"); t.font = hfont(15, True, CLR_HEADER)
ws1.cell(row=2, column=1, value=f"Semrush snapshot {SNAP} · UK · estimates, see caveats").font = hfont(9, False, "666666")
# KPI grid
hdr = ["Metric","NFG Value","Field Median","Field Best","NFG Rank /10","Gap to Median","Percentile /100"]
hrow = 4
for j, c in enumerate(hdr, 1): ws1.cell(row=hrow, column=j, value=c)
style_header_row(ws1, hrow, len(hdr))
def kpi(row, label, col, fmt="#,##0", higher_better=True, value_is_pct=False):
    rng = f"{S}!{col}{fd}:{col}{ld}"; nfgref = f"{S}!{col}{nr}"
    ws1.cell(row=row, column=1, value=label).font = hfont(10, True)
    ws1.cell(row=row, column=2, value=f"={nfgref}")
    ws1.cell(row=row, column=3, value=f"=MEDIAN({rng})")
    ws1.cell(row=row, column=4, value=(f"=MAX({rng})" if higher_better else f"=MIN({rng})"))
    ws1.cell(row=row, column=5, value=(f"=RANK({nfgref},{rng},0)" if higher_better else f"=RANK({nfgref},{rng},1)"))
    ws1.cell(row=row, column=6, value=f"={nfgref}-MEDIAN({rng})")
    # percentile: for lower-is-better metrics (e.g. toxic tail) invert so a high percentile always reads "good"
    pct = (f"=ROUND(({nfgref}-MIN({rng}))/(MAX({rng})-MIN({rng}))*100,0)" if higher_better
           else f"=ROUND((MAX({rng})-{nfgref})/(MAX({rng})-MIN({rng}))*100,0)")
    ws1.cell(row=row, column=7, value=pct)
    for j in range(2, 8):
        cell = ws1.cell(row=row, column=j); cell.font = hfont(10); cell.border = BORDER
        if j in (2,3,4,6): cell.number_format = fmt
    return row + 1
r = hrow + 1
r = kpi(r, "Authority Score (0-100)", BENCH["AScol"], "0")
r = kpi(r, "Referring Domains", BENCH["RDcol"], "#,##0")
r = kpi(r, "Total Backlinks", BENCH["TBcol"], "#,##0")
r = kpi(r, "Organic Keywords (UK)", BENCH["KWcol"], "#,##0")
r = kpi(r, "Est. Organic Traffic (UK)", BENCH["TRcol"], "#,##0")
r = kpi(r, "Follow % (backlink level)", BENCH["FUcol"], "0.0%")
r = kpi(r, "Toxic Tail % (lower better)", BENCH["TTcol"], "0.0%", higher_better=False)
for rr in range(hrow+1, r):
    ws1.cell(row=rr, column=1).fill = PatternFill("solid", fgColor=CLR_SUB)
# highlight the two framing rows
ws1.cell(row=hrow+2, column=1).comment = Comment("Ref-domain gap-to-median -401.5 = the number that frames the deliverable.","SUSO")
# headline counts block
hc = r + 1
ws1.cell(row=hc, column=1, value="Headline opportunity counts").font = hfont(12, True, CLR_HEADER); hc += 1
counts = [
 ("Backlink-gap referring domains found (pooled, link >=1 competitor, not NFG)", "866"),
 ("  of which Semrush-scored (matched, non-hard-spam)", "712"),
 ("  Ahrefs-only unscored (AS_source=unmatched, raw only)", "149"),
 ("  hard-spam excluded from ranking (kept in raw)", "49"),
 ("Consensus targets (linked by >=4 of 9 competitors)", "69 non-spam"),
 ("Keyword-gap opportunities (competitor ranks, NFG absent/weak)", "35 scored"),
 ("  cluster split", "SEND/EHCP, FASD, kinship, therapeutic — overwhelmingly INFORMATIONAL"),
 ("Quick-win keywords (NFG pos 11-30, commercial)", "22"),
 ("Regional whitespace regions flagged HIGH", "2 (Yorkshire & Humber, North East)"),
 ("Toxic-anchor / PBN exposure", "~84 domain-hits (~21% of top-50 anchors) = live PBN/link-buying"),
]
for lab, val in counts:
    a = ws1.cell(row=hc, column=1, value=lab); a.font = hfont(10, lab[0] != " "); a.border = BORDER
    b = ws1.cell(row=hc, column=2, value=val); b.font = hfont(10, True, CLR_HEADER); b.border = BORDER
    ws1.merge_cells(start_row=hc, start_column=2, end_row=hc, end_column=7)
    hc += 1
# Five corrected takeaways
tk = hc + 1
ws1.cell(row=tk, column=1, value="The five Month-1 takeaways (corrected — earlier hypotheses disproven by data)").font = hfont(12, True, CLR_HEADER)
ws1.merge_cells(start_row=tk, start_column=1, end_row=tk, end_column=7); tk += 1
takeaways = [
 ("1. BACKLINK TOXICITY is the real story", "RED",
  "NFG's link profile is ~8 months old with a Feb-2026 spike (referring domains +512%: 24->147; backlinks +1,636%: 28->486; AS 2->10 in one month). 67% toxic tail (AS 0-10), live PBN/link-selling anchors ('buy backlinks online cheap...premium pbn network') and an IP-cluster footprint (42 domains on 2 IPs). Needs a disavow review. The 'AS 36 / rank 2-of-10' is recency-INFLATED, not earned breadth."),
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
    a.font = hfont(10, True, tx); a.fill = PatternFill("solid", fgColor=fg); a.alignment = Alignment(vertical="top", wrap_text=True); a.border = BORDER
    b = ws1.cell(row=tk, column=2, value=txt); b.font = hfont(10); b.alignment = Alignment(vertical="top", wrap_text=True); b.border = BORDER
    ws1.merge_cells(start_row=tk, start_column=2, end_row=tk, end_column=7)
    ws1.row_dimensions[tk].height = 70; tk += 1
# caveats box
cb = tk + 1
cc = ws1.cell(row=cb, column=1, value="CAVEATS: Semrush estimates (modelled, not Google-truth); single snapshot 2026-09-22; regional classification is manual/inferential; target-quality is analyst judgment — see README tab 0 for the full box.")
cc.font = hfont(9, False, TXT_AMBER); cc.fill = PatternFill("solid", fgColor=CLR_CAVEAT); cc.alignment = Alignment(wrap_text=True)
ws1.merge_cells(start_row=cb, start_column=1, end_row=cb+1, end_column=7)
autosize(ws1, {"A":44,"B":18,"C":14,"D":13,"E":13,"F":14,"G":14})
ws1.freeze_panes = "A5"
print("tab1 done")

# =====================================================================
# TAB 3 — NFG Backlink Profile
# =====================================================================
ws3 = wb.create_sheet("3 NFG Backlink Profile")
ws3.sheet_properties.tabColor = TAB_ANALYST
ov = read_csv(f"{DATA}/backlinks/overview_NFG.csv")[0]
ws3.cell(row=1, column=1, value="NFG Backlink Profile — critical off-site audit (Semrush, 2026-09-22)").font = hfont(14, True, CLR_HEADER)
r = 3
ws3.cell(row=r, column=1, value="SUMMARY BLOCK").font = hfont(11, True, CLR_HEADER); r += 1
summ = [
 ("Authority Score", "36"), ("Total backlinks", f'{int(ov["total"]):,}'),
 ("Referring domains", f'{int(ov["domains_num"]):,}'), ("Referring IPs", f'{int(ov["ips_num"]):,}'),
 ("Class-C subnets", f'{int(ov["ipclassc_num"]):,}'),
 ("Follow % (backlink level)", f'{int(ov["follows_num"])/(int(ov["follows_num"])+int(ov["nofollows_num"])):.1%}'),
 ("Toxic tail % (AS 0-10 ref domains)", f'{TOX[NFG]:.1%}'),
 ("Profile age", "~8 months of real growth (flat ~21 domains 2024->Jan-2026, then vertical)"),
 ("12-mo velocity", "+399 ref domains in 8 months; referring domains +512% in Feb-2026 alone (24->147; backlinks +1,636%, 28->486)"),
 ("New/last 90d", "296 (Jun) -> 358 -> 420 domains; backlinks 1,390 -> 1,843 -> 1,743"),
]
for k, v in summ:
    r = kv(ws3, r, k, v, kfill=CLR_SUB)
r += 1
# RED flags
ws3.cell(row=r, column=1, value="CRITICAL FLAGS (evidence-backed)").font = hfont(11, True, TXT_RED); r += 1
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
    a = ws3.cell(row=r, column=1, value=lab)
    fg={"RED":CLR_RED,"AMBER":CLR_AMBER,"GREEN":CLR_GREEN}[lvl]; tx={"RED":TXT_RED,"AMBER":TXT_AMBER,"GREEN":TXT_GREEN}[lvl]
    a.font=hfont(10,True,tx); a.fill=PatternFill("solid",fgColor=fg); a.alignment=Alignment(vertical="top",wrap_text=True); a.border=BORDER
    b=ws3.cell(row=r,column=2,value=txt); b.font=hfont(9); b.alignment=Alignment(vertical="top",wrap_text=True); b.border=BORDER
    ws3.merge_cells(start_row=r,start_column=2,end_row=r,end_column=8); ws3.row_dimensions[r].height=58; r+=1
r += 1
# AS-band distribution mini-table
ws3.cell(row=r, column=1, value="AS-band distribution (ref domains)").font = hfont(11, True, CLR_HEADER); r += 1
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
bh = r
for j,(k,v) in enumerate(bands.items()):
    ws3.cell(row=bh, column=1+j, value=k).font=hfont(9,True,CLR_HEADERTXT)
    ws3.cell(row=bh, column=1+j).fill=PatternFill("solid",fgColor=CLR_HEADER)
    c=ws3.cell(row=bh+1, column=1+j, value=v); c.font=hfont(9); c.border=BORDER; c.number_format="#,##0"
ws3.conditional_formatting.add(f"A{bh+1}:{get_column_letter(len(bands))}{bh+1}", DataBarRule(start_type="min",end_type="max",color="7C3AED"))
r = bh + 3
# refdomains table (top 100)
ws3.cell(row=r, column=1, value="TOP REFERRING DOMAINS (top ~100 by AS — evidence rows)").font = hfont(11, True, CLR_HEADER); r += 1
rd = read_csv(f"{DATA}/backlinks/nfg_refdomains_top100.csv")
rdcols = ["Referring_Domain","Domain_AS","Backlinks_from_Domain","Domain_Trust","IP","Country","First_Seen","Last_Seen"]
hrow3 = r
for j,c in enumerate(rdcols,1): ws3.cell(row=hrow3, column=j, value=c)
style_header_row(ws3, hrow3, len(rdcols)); r += 1
rd_start = r
for row in rd:
    ws3.cell(row=r, column=1, value=row["domain"])
    ws3.cell(row=r, column=2, value=int(row["domain_ascore"]))
    ws3.cell(row=r, column=3, value=int(row["backlinks_num"]))
    ws3.cell(row=r, column=4, value=int(row["domain_trust_score"]) if row["domain_trust_score"] else None)
    ws3.cell(row=r, column=5, value=row["ip"])
    ws3.cell(row=r, column=6, value=row["country"])
    ws3.cell(row=r, column=7, value=epoch_iso(row["first_seen"]))
    ws3.cell(row=r, column=8, value=epoch_iso(row["last_seen"]))
    for j in range(1,9):
        cell=ws3.cell(row=r,column=j); cell.font=hfont(9); cell.border=BORDER
        if j in (3,): cell.number_format="#,##0"
    r += 1
ws3.conditional_formatting.add(f"B{rd_start}:B{r-1}", ColorScaleRule(start_type="min",start_color="F8696B",mid_type="percentile",mid_value=50,mid_color="FFEB84",end_type="max",end_color="63BE7B"))
ws3.freeze_panes = f"A{hrow3+1}"
ws3.auto_filter.ref = f"A{hrow3}:{get_column_letter(len(rdcols))}{r-1}"
autosize(ws3, {"A":34,"B":10,"C":10,"D":11,"E":16,"F":9,"G":12,"H":12})
print("tab3 done")

# =====================================================================
# TAB 4 — NFG Keyword Profile
# =====================================================================
ws4 = wb.create_sheet("4 NFG Keyword Profile")
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
ws4.cell(row=1, column=1, value="NFG Keyword Profile — Semrush Organic Research (UK, 2026-09-22). Export = top 1,000 of 4,028 organic keywords.").font = hfont(12, True, CLR_HEADER)
r = 3
ws4.cell(row=r, column=1, value="SUMMARY BLOCK").font = hfont(11, True, CLR_HEADER); r += 1
# compute summary from export
tot_exp=len(kws)
branded=[k for k in kws if is_branded(k["Keyword"])]
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
for k,v in ksum: r=kv(ws4,r,k,v,kfill=CLR_SUB)
r += 1
gflag = ws4.cell(row=r, column=1, value="GREEN: money terms are a STRENGTH — NFG owns them. Keyword gap (Tab 6) is therefore informational, not money.")
gflag.font=hfont(10,True,TXT_GREEN); gflag.fill=PatternFill("solid",fgColor=CLR_GREEN); ws4.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6); r+=2
# keyword table
kcols=["Keyword","Position","Prev_Position","Band","Search_Volume_UK","CPC_GBP","Est_Traffic","Traffic_%","Competition","KD","Intent","Ranking_URL","Branded_Flag","QuickWin_Flag"]
hrow4=r
for j,c in enumerate(kcols,1): ws4.cell(row=hrow4, column=j, value=c)
style_header_row(ws4, hrow4, len(kcols)); r+=1
kw_start=r
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
ws4.conditional_formatting.add(f"J{kw_start}:J{r-1}", ColorScaleRule(start_type="min",start_color="63BE7B",mid_type="percentile",mid_value=50,mid_color="FFEB84",end_type="max",end_color="F8696B"))
ws4.freeze_panes=f"B{hrow4+1}"
ws4.auto_filter.ref=f"A{hrow4}:{get_column_letter(len(kcols))}{r-1}"
autosize(ws4, {"A":34,"B":9,"C":12,"D":8,"E":14,"F":9,"G":10,"H":9,"I":11,"J":7,"K":16,"L":42,"M":13,"N":12})
print("tab4 done", r-kw_start, "keyword rows")

# =====================================================================
# TAB 5 — Backlink Gap Target List (with Target_Quality)
# =====================================================================
ws5 = wb.create_sheet("5 Backlink Gap Targets")
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
cols5=["Referring_Domain","Seen_SR","Seen_AH","Authority_Score","AS_source","Ahrefs_DR_evid","Num_Competitors_Linking","Consensus_Target","Region","Region_Conf","Dominant_Link_Type","Relevance_Score","Target_Quality","Backlinks_per_Domain","First_Seen","Spam_Flag","Priority_Score","Tier","Acquisition_Type","Competitor_Targets","Snapshot_Date"]
ws5.cell(row=1,column=1,value="Backlink Gap Target List — domains linking to >=1 competitor, not NFG · pooled SR+AH, Semrush-scored · sorted by Priority. Target_Quality separates genuine editorial from directory/farm spam.").font=hfont(10,True,CLR_HEADER)
ws5.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(cols5))
hrow5=2
for j,c in enumerate(cols5,1): ws5.cell(row=hrow5,column=j,value=c)
style_header_row(ws5,hrow5,len(cols5))
# sort: scored (has priority) desc, then spam/unmatched at bottom
def sortkey(row):
    p=num(row["Priority_Score"],None)
    return (0,-p) if p is not None else (1,0)
gap_sorted=sorted(gap,key=sortkey)
r=hrow5+1; data5_start=r
for row in gap_sorted:
    tq=target_quality(row)
    as_=num(row["Authority_Score"],None)
    vals=[row["Referring_Domain"],row["Seen_in_Semrush"],row["Seen_in_Ahrefs"],
          int(as_) if as_ is not None else None,row["AS_source"],
          num(row["Ahrefs_DR_evidence"],None),int(row["Num_Competitors_Linking"]),
          row["Consensus_Target"],row["Region"],row["Region_Confidence"],row["Dominant_Link_Type"],
          num(row["Relevance_Score"],None),tq,num(row["Backlinks_per_Domain"],None),
          row["First_Seen"],row["Spam_Flag"] or "",num(row["Priority_Score"],None),
          row["Tier"],row["Acquisition_Type"],row["Competitor_Targets"][:120],SNAP]
    for j,v in enumerate(vals,1):
        cell=ws5.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j in (14,): cell.number_format="#,##0"
    # colour target quality
    tqcell=ws5.cell(row=r,column=13)
    if "Genuine" in tq or "Relevant" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_GREEN); tqcell.font=hfont(9,False,TXT_GREEN)
    elif "Excluded" in tq or "farm" in tq or "Generic" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_RED); tqcell.font=hfont(9,False,TXT_RED)
    elif "Directory" in tq or "Soft" in tq or "National" in tq: tqcell.fill=PatternFill("solid",fgColor=CLR_AMBER); tqcell.font=hfont(9,False,TXT_AMBER)
    if row["Consensus_Target"]=="Y":
        ws5.cell(row=r,column=8).fill=PatternFill("solid",fgColor=CLR_SUB); ws5.cell(row=r,column=8).font=hfont(9,True)
    r+=1
data5_end=r-1
ws5.conditional_formatting.add(f"Q{data5_start}:Q{data5_end}", ColorScaleRule(start_type="min",start_color="F8696B",mid_type="percentile",mid_value=50,mid_color="FFEB84",end_type="max",end_color="63BE7B"))
ws5.conditional_formatting.add(f"D{data5_start}:D{data5_end}", DataBarRule(start_type="min",end_type="max",color="7C3AED"))
ws5.freeze_panes=f"B{hrow5+1}"
ws5.auto_filter.ref=f"A{hrow5}:{get_column_letter(len(cols5))}{data5_end}"
autosize(ws5, {"A":30,"B":8,"C":8,"D":9,"E":11,"F":11,"G":10,"H":10,"I":16,"J":9,"K":18,"L":10,"M":24,"N":10,"O":12,"P":9,"Q":10,"R":6,"S":18,"T":40,"U":12})
print("tab5 done", data5_end-data5_start+1, "gap rows")

# =====================================================================
# TAB 6 — Keyword Gap (clustered)
# =====================================================================
ws6 = wb.create_sheet("6 Keyword Gap")
ws6.sheet_properties.tabColor = TAB_ANALYST
kg = read_csv(f"{DATA}/keywords/keyword_gap_opportunities.csv")
ws6.cell(row=1,column=1,value="Keyword Gap — competitors rank, NFG absent/weak · Semrush UK · clustered. The gap is overwhelmingly INFORMATIONAL (SEND/EHCP, FASD, kinship, therapeutic) — NFG already owns the money terms.").font=hfont(10,True,CLR_HEADER)
ws6.merge_cells(start_row=1,start_column=1,end_row=1,end_column=13)
# cluster summary
r=3
ws6.cell(row=r,column=1,value="CLUSTER SUMMARY (addressable UK volume)").font=hfont(11,True,CLR_HEADER); r+=1
cl_vol=defaultdict(lambda:[0,0])
for k in kg:
    cl=k["Cluster"]; cl_vol[cl][0]+=1; cl_vol[cl][1]+=int(k["Volume"])
ws6.cell(row=r,column=1,value="Cluster").font=hfont(9,True,CLR_HEADERTXT); ws6.cell(row=r,column=1).fill=PatternFill("solid",fgColor=CLR_HEADER)
ws6.cell(row=r,column=2,value="# Keywords").font=hfont(9,True,CLR_HEADERTXT); ws6.cell(row=r,column=2).fill=PatternFill("solid",fgColor=CLR_HEADER)
ws6.cell(row=r,column=3,value="Sum Volume/mo").font=hfont(9,True,CLR_HEADERTXT); ws6.cell(row=r,column=3).fill=PatternFill("solid",fgColor=CLR_HEADER)
r+=1
for cl,(n,v) in sorted(cl_vol.items(),key=lambda x:-x[1][1]):
    ws6.cell(row=r,column=1,value=cl).font=hfont(9); ws6.cell(row=r,column=1).border=BORDER
    ws6.cell(row=r,column=2,value=n).font=hfont(9); ws6.cell(row=r,column=2).border=BORDER
    c=ws6.cell(row=r,column=3,value=v); c.font=hfont(9); c.number_format="#,##0"; c.border=BORDER
    r+=1
r+=1
# detail table clustered
cols6=["Rank","Opportunity_Score","Keyword","Cluster","Search_Volume_UK","KD","Intent","NFG_Pos(0=absent)","Best_Rival","Best_Rival_Pos","Rival_Density","Quick_Win","Recommended_Action"]
hrow6=r
for j,c in enumerate(cols6,1): ws6.cell(row=hrow6,column=j,value=c)
style_header_row(ws6,hrow6,len(cols6)); r+=1
def rec_action(k):
    if k["QuickWin"]=="1": return "Optimize existing page + internal links (NFG already ranks 11-30)"
    if int(k["NFG_Pos(0=absent)"])==0: return "New informational/pillar page targeting cluster"
    return "Strengthen page + add FAQ/schema"
kg_sorted=sorted(kg,key=lambda k:(k["Cluster"],-float(k["OpportunityScore"])))
d6s=r
for k in kg_sorted:
    vals=[int(k["Rank"]),float(k["OpportunityScore"]),k["Keyword"],k["Cluster"],int(k["Volume"]),
          int(float(k["Intent"])),k["KD"],int(k["NFG_Pos(0=absent)"]),k["BestRival"],int(k["BestRivalPos"]),
          int(k["RivalDensity"]),"QUICK-WIN" if k["QuickWin"]=="1" else "",rec_action(k)]
    for j,v in enumerate(vals,1):
        cell=ws6.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j==5: cell.number_format="#,##0"
        if j==2: cell.number_format="0.000"
    if k["QuickWin"]=="1":
        ws6.cell(row=r,column=12).fill=PatternFill("solid",fgColor=CLR_AMBER); ws6.cell(row=r,column=12).font=hfont(9,True,TXT_AMBER)
    r+=1
ws6.conditional_formatting.add(f"B{d6s}:B{r-1}", ColorScaleRule(start_type="min",start_color="FFEB84",mid_type="percentile",mid_value=50,mid_color="A9D08E",end_type="max",end_color="63BE7B"))
ws6.conditional_formatting.add(f"F{d6s}:F{r-1}", ColorScaleRule(start_type="min",start_color="63BE7B",mid_type="percentile",mid_value=50,mid_color="FFEB84",end_type="max",end_color="F8696B"))
ws6.freeze_panes=f"A{hrow6+1}"
ws6.auto_filter.ref=f"A{hrow6}:{get_column_letter(len(cols6))}{r-1}"
autosize(ws6, {"A":6,"B":15,"C":26,"D":22,"E":14,"F":6,"G":8,"H":16,"I":16,"J":13,"K":12,"L":11,"M":48})
print("tab6 done")

# =====================================================================
# TAB 7 — Regional Whitespace Map
# =====================================================================
ws7 = wb.create_sheet("7 Regional Whitespace Map")
ws7.sheet_properties.tabColor = TAB_ANALYST
reg = read_csv(f"{DATA}/gap/regional_map.csv")
domain_cols=[c for c in reg[0].keys() if c not in ("UK_Region","_pct_of_top100_note")]
ws7.cell(row=1,column=1,value="Regional Whitespace Map — View D1: count of each domain's top-100 referring domains (by AS) per UK region. NFG column = purple accent.").font=hfont(10,True,CLR_HEADER)
ws7.merge_cells(start_row=1,start_column=1,end_row=1,end_column=1+len(domain_cols))
# matrix
hrow7=3
ws7.cell(row=hrow7,column=1,value="UK_Region")
for j,d in enumerate(domain_cols,2): ws7.cell(row=hrow7,column=j,value=d.replace(".co.uk","").replace(".org.uk","").replace(".com",""))
style_header_row(ws7,hrow7,1+len(domain_cols))
r=hrow7+1; m7s=r
nfg_ci=domain_cols.index(NFG)+2
for row in reg:
    if row["UK_Region"].startswith("TOTAL"): continue
    ws7.cell(row=r,column=1,value=row["UK_Region"]).font=hfont(9,True); ws7.cell(row=r,column=1).border=BORDER
    for j,d in enumerate(domain_cols,2):
        v=int(row[d]) if row[d] else 0
        cell=ws7.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
    # highlight NFG whitespace regions
    if row["UK_Region"] in ("Yorkshire & Humber","North East"):
        ws7.cell(row=r,column=1).fill=PatternFill("solid",fgColor=CLR_RED); ws7.cell(row=r,column=1).font=hfont(9,True,TXT_RED)
    r+=1
m7e=r-1
# colour scale across matrix body & accent NFG column
ws7.conditional_formatting.add(f"B{m7s}:{get_column_letter(1+len(domain_cols))}{m7e}", ColorScaleRule(start_type="min",start_color="FFFFFF",mid_type="percentile",mid_value=50,mid_color="C9B3E8",end_type="max",end_color="7C3AED"))
for rr in range(m7s,m7e+1):
    c=ws7.cell(row=rr,column=nfg_ci); c.font=hfont(9,True)
    c.border=Border(left=Side(style="medium",color=CLR_NFG_STRONG),right=Side(style="medium",color=CLR_NFG_STRONG))
r=m7e+2
# classified whitespace table
ws7.cell(row=r,column=1,value="WHITESPACE SCORING — local demand vs NFG presence vs competitor presence").font=hfont(11,True,CLR_HEADER); r+=1
wcols=["UK_Region","NFG_TopRefdomains","Competitors_Present","Whitespace_Level","Gap_Seed_Domains (link competitors, not NFG)","Recommended_Focus"]
hrow7b=r
for j,c in enumerate(wcols,1): ws7.cell(row=hrow7b,column=j,value=c)
style_header_row(ws7,hrow7b,len(wcols)); r+=1
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
    vals=[rg,nfg_counts.get(rg,0),comp_present.get(rg,0),lvl,seed.get(rg,""),rec]
    for j,v in enumerate(vals,1):
        cell=ws7.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(wrap_text=True,vertical="top")
    lc=ws7.cell(row=r,column=4)
    if "HIGH" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_RED); lc.font=hfont(9,True,TXT_RED)
    elif "PROTECT" in lvl or "strength" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_GREEN); lc.font=hfont(9,True,TXT_GREEN)
    elif "MEDIUM" in lvl or "MAINTAIN" in lvl: lc.fill=PatternFill("solid",fgColor=CLR_AMBER); lc.font=hfont(9,True,TXT_AMBER)
    r+=1
ws7.freeze_panes=f"B{hrow7+1}"
autosize(ws7, {"A":20,"B":13,"C":13,"D":18,"E":52,"F":60})
for col in "BCDEFGHIJK": 
    if ws7.column_dimensions[col].width is None: ws7.column_dimensions[col].width=9
print("tab7 done")

# =====================================================================
# TAB 8 — Anchors & Toxicity
# =====================================================================
ws8 = wb.create_sheet("8 Anchors & Toxicity")
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
r+=1
ws8.cell(row=r,column=1,value="TOP REFERRING IPs (PBN evidence — count of domains per IP)").font=hfont(11,True,CLR_HEADER); r+=1
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
ws8.conditional_formatting.add(f"C{ip8s}:C{r-1}", DataBarRule(start_type="min",end_type="max",color="C00000"))
ws8.freeze_panes="A2"
autosize(ws8, {"A":52,"B":40,"C":16,"D":34,"E":22,"F":10})
print("tab8 done")

# =====================================================================
# TAB 9 — Competitor Link Detail (per-competitor refdomains, long format)
# =====================================================================
ws9 = wb.create_sheet("9 Competitor Link Detail")
ws9.sheet_properties.tabColor = TAB_ANALYST
COMPS = {"capstonefostercare.co.uk":"capstonefostercare","compassfostering.com":"compassfostering",
 "fosteringpeople.co.uk":"fosteringpeople","fosterplus.co.uk":"fosterplus","ispfostering.org.uk":"ispfostering",
 "orangegrovefostercare.co.uk":"orangegrovefostercare","swiisfostercare.com":"swiisfostercare",
 "thefca.co.uk":"thefca","thefosteringnetwork.org.uk":"thefosteringnetwork"}
# NFG own refdomains set for Also_Links_to_NFG
nfg_own=set(r["Referring_Domain"].lower() for r in read_csv(f"{DATA}/gap/nfg_refdomains.csv"))
ws9.cell(row=1,column=1,value="Competitor Link Detail — per-competitor referring domains (Semrush SR + Ahrefs AH evidence, pooled). Raw evidence feeding Tabs 5 & 7. AS=Semrush; DR=Ahrefs evidence-only.").font=hfont(10,True,CLR_HEADER)
ws9.merge_cells(start_row=1,start_column=1,end_row=1,end_column=9)
cols9=["Competitor","Referring_Domain","Semrush_AS","Ahrefs_DR_evid","Backlinks","First_Seen","Last_Seen","Country","Source","Also_Links_to_NFG"]
hrow9=2
for j,c in enumerate(cols9,1): ws9.cell(row=hrow9,column=j,value=c)
style_header_row(ws9,hrow9,len(cols9))
r=hrow9+1; d9s=r
for dom,slug in COMPS.items():
    # SR
    srrows=read_csv(f"{DATA}/gap/refdomains_{slug}.csv")
    ah={a["Referring_Domain"].lower():a for a in read_csv(f"{DATA}/gap/ahrefs_refdomains_{slug}.csv")}
    for row in srrows:
        rd=row["Referring_Domain"]; dr=ah.get(rd.lower(),{}).get("Ahrefs_DR","")
        src="SR+AH" if rd.lower() in ah else "SR"
        vals=[dom,rd,int(row["Semrush_AS"]) if row["Semrush_AS"] else None,num(dr,None),int(row["Backlinks"]) if row["Backlinks"] else None,row["First_Seen"],row["Last_Seen"],row["Country"],src,"YES" if rd.lower() in nfg_own else ""]
        for j,v in enumerate(vals,1):
            cell=ws9.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
            if j==5: cell.number_format="#,##0"
        if rd.lower() in nfg_own: ws9.cell(row=r,column=10).font=hfont(9,True,TXT_GREEN)
        r+=1
    # AH-only rows (not in SR)
    sr_set=set(x["Referring_Domain"].lower() for x in srrows)
    for rd_l,a in ah.items():
        if rd_l not in sr_set:
            vals=[dom,a["Referring_Domain"],None,num(a["Ahrefs_DR"],None),num(a["Links_to_Target"],None),a.get("First_Seen",""),"","","AH","YES" if rd_l in nfg_own else ""]
            for j,v in enumerate(vals,1):
                cell=ws9.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
            r+=1
d9e=r-1
ws9.conditional_formatting.add(f"C{d9s}:C{d9e}", ColorScaleRule(start_type="min",start_color="F8696B",mid_type="percentile",mid_value=50,mid_color="FFEB84",end_type="max",end_color="63BE7B"))
ws9.freeze_panes=f"C{hrow9+1}"
ws9.auto_filter.ref=f"A{hrow9}:{get_column_letter(len(cols9))}{d9e}"
autosize(ws9, {"A":28,"B":32,"C":10,"D":12,"E":10,"F":12,"G":12,"H":9,"I":8,"J":16})
print("tab9 done", d9e-d9s+1, "link rows")

# =====================================================================
# TAB 10 — Priority Target List (cross-tab roll-up)
# =====================================================================
ws10 = wb.create_sheet("10 Priority Target List")
ws10.sheet_properties.tabColor = TAB_ROLLUP
ws10.cell(row=1,column=1,value="★ PRIORITY TARGET LIST — unified Month-2+ action queue (backlink outreach + content-for-keyword + regional push + disavow). Sorted by unified score; quick-wins float up. Top 25 = Month-2 shortlist.").font=hfont(10,True,CLR_HEADER)
ws10.merge_cells(start_row=1,start_column=1,end_row=1,end_column=11)
cols10=["Rank","Action_Type","Target","Rationale","Supporting_Metric_1","Supporting_Metric_2","Region_Tag","Effort","Unified_Priority_Score","Owner/Status","Month_Target"]
hrow10=2
for j,c in enumerate(cols10,1): ws10.cell(row=hrow10,column=j,value=c)
style_header_row(ws10,hrow10,len(cols10))
WHITESPACE={"Yorkshire & Humber","North East"}
# Build candidate actions
actions=[]
# --- backlink targets: genuine quality, non-spam, scored ---
for row in gap:
    if row["Spam_Flag"]=="hard": continue
    tq=target_quality(row); p=num(row["Priority_Score"],None)
    if p is None: continue
    if not ("Genuine" in tq or "Relevant" in tq or "Directory-Citation" in tq): continue
    genuine_bonus=1.0 if "Genuine" in tq else 0.6
    reg=row["Region"]; ws_mult=1.15 if reg in WHITESPACE else 1.0
    ncomp=int(row["Num_Competitors_Linking"])
    effort="L" if row["Tier"]=="1" else ("M" if row["Tier"]=="2" else "H")
    eff_v={"L":0.2,"M":0.5,"H":0.8}[effort]
    src=p  # 0-1 native
    unified=(0.45*src + 0.20*min(ncomp/9,1) + 0.20*(0.9 if reg in WHITESPACE else 0.3) + 0.15*(1-eff_v))*100*ws_mult*genuine_bonus
    actions.append({"type":"Backlink outreach","target":row["Referring_Domain"],
        "rationale":f"{tq}; links to {ncomp} competitor(s), not NFG",
        "m1":f"AS {int(num(row['Authority_Score'],0))}","m2":f"{ncomp} competitors linking · {reg}",
        "region":reg if reg not in ("Non-UK/Unknown","UK-National") else "",
        "effort":effort,"score":unified,"qw":row["Tier"]=="1"})
# --- keyword actions from gap opportunities ---
for k in kg[:14]:
    qw=k["QuickWin"]=="1"
    unified=(0.45*min(float(k["OpportunityScore"])/1.6,1)+0.20*(min(int(k["RivalDensity"])/4,1))+0.20*0.4+0.15*(0.8 if qw else 0.4))*100
    if qw: unified+=8
    actions.append({"type":"Content-for-keyword","target":k["Keyword"],
        "rationale":f"{k['Cluster']} gap; best rival {k['BestRival']} p{k['BestRivalPos']}"+(" (NFG already 11-30 — quick win)" if qw else " (NFG absent)"),
        "m1":f"Vol {int(k['Volume']):,}/mo","m2":f"KD {int(float(k['Intent']))} · intent {k['KD']}",
        "region":"","effort":"M" if not qw else "L","score":unified,"qw":qw})
# --- quick-win keyword page fixes ---
qw_kw=read_csv(f"{DATA}/keywords/nfg_quickwins_11_30.csv")
for k in qw_kw[:6]:
    unified=68+ (5 if k["Intent"] in ("comm","trans") else 0)
    actions.append({"type":"Content-for-keyword","target":k["Keyword"]+" (optimize)",
        "rationale":f"NFG pos {k['Position']} — quick win; fix page/cannibalisation",
        "m1":f"Vol {int(k['Volume']):,}/mo","m2":f"pos {k['Position']} · {k['RankingURL'][:40]}",
        "region":"","effort":"L","score":unified,"qw":True})
# --- regional pushes ---
regional=[
 ("Regional push","Yorkshire & Humber cluster","Close whitespace: 1 NFG vs FosteringNetwork 5 / Capstone 5. Map to NFA North + 'Fostering in York'.","NFG top-100 refdomains = 1","leeds.ac.uk, leeds.gov.uk, hulldailymail.co.uk seeds","Yorkshire & Humber","M",92,True),
 ("Regional push","North East cluster","Close whitespace: 0 NFG vs theFCA 4 / swiis 3. Map to Reach Out Care + 'Fostering in Newcastle'.","NFG top-100 refdomains = 0","chroniclelive.co.uk, newcastle.gov.uk, sunderlandecho.com seeds","North East","M",94,True),
]
for a in regional:
    actions.append({"type":a[0],"target":a[1],"rationale":a[2],"m1":a[3],"m2":a[4],"region":a[5],"effort":a[6],"score":a[7],"qw":a[8]})
# --- disavow defensive block ---
disavow=[
 ("Disavow","PBN IP-cluster domains (159.198.75.134 + 195.20.19.178)","Defensive: 42 domains on 2 IPs, PBN footprint aligned to Feb-2026 spike","42 domains on 2 IPs","67.1% toxic tail","","M",60),
 ("Disavow","'buy backlinks / premium pbn network' anchor domains","Defensive: 59 domains with explicit link-selling anchor","59 domains","~21% of top-50 anchors","","M",58),
]
for a in disavow:
    actions.append({"type":a[0],"target":a[1],"rationale":a[2],"m1":a[3],"m2":a[4],"region":a[5],"effort":a[6],"score":a[7],"qw":False})
# sort: score desc, quick-wins float (effort asc as tiebreak)
eff_rank={"L":0,"M":1,"H":2}
actions.sort(key=lambda a:(-a["score"], eff_rank[a["effort"]]))
r=hrow10+1; d10s=r
for i,a in enumerate(actions,1):
    vals=[i,a["type"],a["target"],a["rationale"],a["m1"],a["m2"],a["region"],a["effort"],round(a["score"],1),"",""]
    for j,v in enumerate(vals,1):
        cell=ws10.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=(j in (3,4,5,6)))
    # colour by action type
    tc=ws10.cell(row=r,column=2)
    cmap={"Backlink outreach":"D9E1F2","Content-for-keyword":"E2EFDA","Regional push":CLR_NFG,"Disavow":CLR_RED}
    tc.fill=PatternFill("solid",fgColor=cmap.get(a["type"],"FFFFFF"))
    if a["type"]=="Disavow": tc.font=hfont(9,True,TXT_RED)
    # editable columns highlighted yellow
    ws10.cell(row=r,column=10).fill=PatternFill("solid",fgColor="FFF2CC")
    ws10.cell(row=r,column=11).fill=PatternFill("solid",fgColor="FFF2CC")
    r+=1
d10e=r-1
ws10.conditional_formatting.add(f"I{d10s}:I{d10e}", ColorScaleRule(start_type="min",start_color="FFEB84",mid_type="percentile",mid_value=50,mid_color="A9D08E",end_type="max",end_color="2E7D32"))
# shade top 25 shortlist
for rr in range(d10s, min(d10s+25,d10e+1)):
    ws10.cell(row=rr,column=1).fill=PatternFill("solid",fgColor="FCE4D6"); ws10.cell(row=rr,column=1).font=hfont(9,True)
note=ws10.cell(row=d10e+2,column=1,value="Unified score = (0.45·source_score + 0.20·competitor-consensus + 0.20·regional-whitespace + 0.15·(1−effort)) ×100, whitespace-multiplied, quality-weighted. Rows 1-25 (shaded) = Month-2 shortlist. Owner/Status & Month_Target are editable (yellow).")
note.font=hfont(9,False,"666666"); ws10.merge_cells(start_row=d10e+2,start_column=1,end_row=d10e+2,end_column=11); note.alignment=Alignment(wrap_text=True)
ws10.freeze_panes=f"A{hrow10+1}"
ws10.auto_filter.ref=f"A{hrow10}:{get_column_letter(len(cols10))}{d10e}"
autosize(ws10, {"A":6,"B":18,"C":34,"D":44,"E":20,"F":34,"G":18,"H":7,"I":13,"J":16,"K":13})
print("tab10 done", d10e-d10s+1, "actions")

# =====================================================================
# TAB 11 — Data Dictionary & Raw Exports
# =====================================================================
ws11 = wb.create_sheet("11 Data Dictionary & Raw")
ws11.sheet_properties.tabColor = TAB_APPENDIX
ws11.cell(row=1,column=1,value="Data Dictionary & Raw Exports — column definitions, source attribution, file index, changelog").font=hfont(13,True,CLR_HEADER)
r=3
ws11.cell(row=r,column=1,value="A — COLUMN DICTIONARY (key columns)").font=hfont(11,True,CLR_HEADER); r+=1
dcols=["Column","Tab","Definition","Source","Units/Format"]
for j,c in enumerate(dcols,1): ws11.cell(row=r,column=j,value=c)
style_header_row(ws11,r,len(dcols)); r+=1
dict_rows=[
 ("Authority_Score","1,2,3,5,8,9","Semrush domain authority 0-100","SR backlinks_comparison / refdomains","integer 0-100"),
 ("Toxic_Tail_%","1,2,3","Share of ref domains AS 0-10","SR backlinks_ascore_profile","percent"),
 ("Follow_%","1,2,3","follows/(follows+nofollows) at backlink level","SR backlinks_overview","percent"),
 ("Composite_Strength","2","Min-max normalised mean of AS, ref domains, keywords, traffic","Derived (formula)","0-1"),
 ("Index_AS / Index_RefDomains","2","value ÷ cohort median ×100","Derived (formula)","index (100=median)"),
 ("Organic_Keywords_UK / Traffic","1,2,4","Semrush organic keyword count & est. monthly traffic","SR organic_research / domain_rank","count"),
 ("CPC_GBP","4","Semrush CPC converted USD→GBP @0.79","SR organic_research","GBP"),
 ("Priority_Score","5","0.30·AS_norm+0.30·#comp/9+0.20·Relevance+0.20·LinkType − spam gate","Derived","0-1"),
 ("Target_Quality","5,10","Analyst class: Genuine-GovEdu/Charity/RegionalNews vs Directory/Farm/Spam","Derived (analyst)","label"),
 ("Consensus_Target","1,5","Linked by >=4 of 9 competitors","Derived","Y/blank"),
 ("Opportunity_Score","6","(norm Volume × Intent multiplier) ÷ KD band, rival/quick-win adj","Derived","score"),
 ("Whitespace_Level","7","Region link deficit × local demand judgment","Derived (manual)","HIGH/MED/LOW"),
 ("Region / Region_Confidence","5,7,9","Manual domain/brand/outlet classification (NOT IP-geo)","Derived (manual)","UK region + H/M/L"),
 ("Ahrefs_DR_evid","5,9","Ahrefs Domain Rating — EVIDENCE ONLY, never scored, never mixed with AS","AH","0-100"),
 ("Unified_Priority_Score","10","0.45·source+0.20·consensus+0.20·whitespace+0.15·(1−effort)","Derived","0-100"),
]
for row in dict_rows:
    for j,v in enumerate(row,1):
        cell=ws11.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=True)
    r+=1
r+=1
ws11.cell(row=r,column=1,value="B — RAW EXPORT INDEX (files on disk under /home/user/test/data/)").font=hfont(11,True,CLR_HEADER); r+=1
fcols=["File","Engine","Report","Pull_Date","Region_Filter","Row_Count"]
for j,c in enumerate(fcols,1): ws11.cell(row=r,column=j,value=c)
style_header_row(ws11,r,len(fcols)); r+=1
def engine_report(fn):
    if fn.startswith("ahrefs_"): return ("Ahrefs","referring-domains")
    if fn.startswith("benchmark_backlinks"): return ("Semrush","backlinks_comparison")
    if fn.startswith("benchmark_keywords"): return ("Semrush","domain_rank/organic")
    if fn.startswith("nfg_keywords") or fn.startswith("gap_batch"): return ("Semrush","organic/domain_domains")
    if fn.startswith("nfg_anchors"): return ("Semrush","backlinks_anchors")
    if fn.startswith("nfg_refips"): return ("Semrush","backlinks_refips")
    if fn.startswith("nfg_refdomains") or fn.startswith("refdomains_"): return ("Semrush","backlinks_refdomains")
    if fn.startswith("ascore"): return ("Semrush","backlinks_ascore_profile")
    if fn.startswith("historical"): return ("Semrush","backlinks_historical")
    if fn.startswith("categories"): return ("Semrush","backlinks_categories")
    if fn.startswith("tld"): return ("Semrush","backlinks_tld")
    if fn.startswith("overview"): return ("Semrush","backlinks_overview")
    if fn.startswith("backlink_gap_targetlist") or fn=="matrix.csv": return ("Pooled SR+AH","backlinks_matrix/derived")
    if fn.startswith("keyword_gap") or fn.startswith("organic_competitors") or fn.startswith("nfg_quickwins") or fn.startswith("ifa_footprints"): return ("Semrush","domain_domains/organic")
    if fn=="regional_map.csv": return ("Pooled SR+AH","derived regional matrix")
    return ("Semrush","-")
files=[]
for d in ("backlinks","keywords","gap"):
    for p in sorted(glob.glob(f"{DATA}/{d}/*.csv")):
        fn=os.path.basename(p)
        try: n=sum(1 for _ in open(p))-1
        except: n=0
        eng,rep=engine_report(fn)
        files.append((f"{d}/{fn}",eng,rep,SNAP,"UK",n))
for row in files:
    for j,v in enumerate(row,1):
        cell=ws11.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER
        if j==6: cell.number_format="#,##0"
    r+=1
r+=1
ws11.cell(row=r,column=1,value="C — SNAPSHOT & API NOTES").font=hfont(11,True,CLR_HEADER); r+=1
notes=[
 ("Snapshot date","2026-09-22 (single dated window, referenced by every tab)"),
 ("Region","UK (Semrush backlink reports are global; UK framing interpretive)"),
 ("Approx. API units consumed","~200,000 Semrush units across benchmark + 10-domain deep pulls + gap batches + Ahrefs pooling"),
 ("Firewall","All reported metrics Semrush-only; Ahrefs DR evidence-only; AS and DR never in one column"),
 ("Gap pooling","866 unique gap domains: 712 SR-scored, 149 AH-only unmatched, 49 hard-spam excluded"),
]
for k,v in notes: r=kv(ws11,r,k,v,kfill=CLR_SUB)
r+=1
ws11.cell(row=r,column=1,value="D — CHANGELOG").font=hfont(11,True,CLR_HEADER); r+=1
for j,c in enumerate(["Version","Date","Editor","Change"],1): ws11.cell(row=r,column=j,value=c)
style_header_row(ws11,r,4); r+=1
ch=("v1","2026-09-22","SUSO SEO","Initial Month-1 foundation audit build — 12 tabs from Semrush+Ahrefs pulls; corrected narrative (backlink toxicity + authority deficit primary; informational keyword gap; Yorkshire/NE whitespace; target-quality tiering).")
for j,v in enumerate(ch,1):
    cell=ws11.cell(row=r,column=j,value=v); cell.font=hfont(9); cell.border=BORDER; cell.alignment=Alignment(vertical="top",wrap_text=True)
autosize(ws11, {"A":34,"B":14,"C":40,"D":30,"E":16,"F":11})
print("tab11 done", len(files), "files indexed")

# =====================================================================
# reorder sheets 0..11 and save
# =====================================================================
order_names=["0 README & Methodology","1 Executive Scorecard","2 Competitor Benchmark",
 "3 NFG Backlink Profile","4 NFG Keyword Profile","5 Backlink Gap Targets","6 Keyword Gap",
 "7 Regional Whitespace Map","8 Anchors & Toxicity","9 Competitor Link Detail",
 "10 Priority Target List","11 Data Dictionary & Raw"]
wb._sheets.sort(key=lambda s: order_names.index(s.title))
wb.save(OUT)
print("SAVED", OUT)
