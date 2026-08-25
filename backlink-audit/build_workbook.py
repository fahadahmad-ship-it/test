#!/usr/bin/env python3
"""Consolidate the audit into a single-sheet Excel workbook.

Every evaluated item — domain-level verdicts plus the per-URL drill-down for
flagged domains — lands on one sheet so the analyst works from one surface.
The summary block uses live COUNTIFS/SUMIFS so counts update as
REVIEW_MANUALLY rows are resolved to DISAVOW or KEEP in place.

Usage: python3 build_workbook.py <outdir>
"""
import csv
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

try:
    from review_decisions import DECISIONS as REVIEW_RECOMMENDATIONS
except ImportError:          # the sheet still builds without the hand pass
    REVIEW_RECOMMENDATIONS = {}
from openpyxl.worksheet.datavalidation import DataValidation

# Columns in reading order: what it is, what to do, why, then the evidence,
# then volume, hosting and dates. Decision fields sit left so they stay
# visible while scrolling the evidence; the long Rationale goes last.
COL_GROUPS = [
    ("Identity", "Level", 9),
    ("Identity", "Referring Domain / URL", 42),
    ("Decision", "Action Recommendation", 23),
    ("Decision", "Remediation Priority", 30),
    ("Decision", "Confidence Score", 11),
    ("Decision", "Disavow Entry", 30),
    ("Why", "Primary Risk Factor", 42),
    ("Why", "Evidence Level", 30),
    ("Volume", "Backlinks (true)", 12),
    ("Volume", "Backlinks (in sample)", 12),
    ("Volume", "Follow (Equity) Links", 12),
    ("Volume", "Domain ascore", 11),
    ("Link evidence", "Anchor Text", 38),
    ("Link evidence", "Anchor Type", 14),
    ("Link evidence", "Target URL", 40),
    ("Link evidence", "Unique Anchors", 11),
    ("Link evidence", "Exact-Match Anchor %", 12),
    ("Link evidence", "Branded/URL Anchor %", 12),
    ("Link evidence", "Nofollow %", 10),
    ("Link evidence", "Avg External Links", 11),
    ("Link evidence", "Sponsored", 10),
    ("Link evidence", "Sitewide", 9),
    ("Link evidence", "Lost Link", 9),
    ("Link evidence", "Topically Relevant", 11),
    ("Hosting", "IP Address", 15),
    ("Hosting", "C-Block", 16),
    ("Hosting", "Hosting", 24),
    ("Hosting", "Country", 8),
    ("Dates", "First seen", 11),
    ("Dates", "Last seen", 11),
    ("Rationale", "Rationale", 95),
]
COLS = [(n, w) for _, n, w in COL_GROUPS]
GROUP_FILL = {"Identity": "1F3864", "Decision": "2E5A2E", "Why": "7B3F00",
              "Volume": "1F4E5F", "Link evidence": "4A3B6B",
              "Hosting": "5A5A5A", "Dates": "5A5A5A", "Rationale": "3F3F3F"}

FONT = "Arial"
ACTION_FILL = {
    "DISAVOW":               PatternFill("solid", fgColor="F8CBAD"),
    "REVIEW_MANUALLY":       PatternFill("solid", fgColor="FFE699"),
    "KEEP_AFFILIATE_RETAIN": PatternFill("solid", fgColor="C6E0B4"),
}
NUMERIC = {"Backlinks (true)", "Backlinks (in sample)",
           "Follow (Equity) Links", "Domain ascore", "Unique Anchors",
           "Avg External Links"}


TAB_COLS = [
    ("Referring Domain", 44), ("Disavow Entry", 30),
    ("Primary Risk Factor", 44), ("Confidence Score", 11),
    ("Evidence Level", 32), ("Remediation Priority", 32),
    ("Backlinks (true)", 13), ("Follow (Equity) Links", 13),
    ("Domain ascore", 11), ("C-Block", 17), ("Hosting", 24),
    ("Anchor Text", 36), ("First seen", 12), ("Last seen", 12),
    ("Rationale", 100),
]


def _worksheet(wb, title, dom, action, blurb, confirm_header,
               confirm_list, default="", recommend=None):
    """One working tab per action bucket, with a decision column."""
    rows = [dict(d) for d in dom if d["Action Recommendation"] == action]
    rows.sort(key=lambda r: -int(r["Backlinks (true)"]))
    # Pre-fill the disavow line on every row so a REVIEW domain flipped to
    # DISAVOW can be copied straight into Google's tool.
    for r in rows:
        r["Disavow Entry"] = f"domain:{r['Referring Domain']}"
    ws = wb.create_sheet(title)
    HDR = 6
    first, last = HDR + 1, HDR + len(rows)
    n_rec = 2 if recommend else 0
    ncol = len(TAB_COLS) + n_rec + 2
    dec_col = get_column_letter(len(TAB_COLS) + n_rec + 1)

    ws["A1"] = f"{title} - {len(rows):,} domains"
    ws["A1"].font = Font(name=FONT, size=14, bold=True)
    ws["A2"] = blurb
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color="595959")
    ws["A3"] = "Total backlinks"
    ws["B3"] = f"=SUM($G${first}:$G${last})"
    ws["A4"] = "Rows still unset"
    ws["B4"] = f'=COUNTIF(${dec_col}${first}:${dec_col}${last},"{default or ""}")'         if default else f'=COUNTBLANK(${dec_col}${first}:${dec_col}${last})'
    for r in (3, 4):
        ws[f"A{r}"].font = Font(name=FONT, size=10, bold=True)
        ws[f"B{r}"].font = Font(name=FONT, size=10)
        ws[f"B{r}"].number_format = "#,##0"

    thin = Side(style="thin", color="BFBFBF")
    BOT, A_TOP = Border(bottom=thin), Alignment(vertical="top")
    A_WRAP = Alignment(vertical="top", wrap_text=True)
    F_BODY = Font(name=FONT, size=10)
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    heads = [c[0] for c in TAB_COLS]
    widths = [c[1] for c in TAB_COLS]
    if recommend:
        heads += ["Recommendation", "Evidence for the recommendation"]
        widths += [16, 62]
    heads += [confirm_header, "Notes"]
    widths += [26, 44]
    for i, (h, w) in enumerate(zip(heads, widths), start=1):
        c = ws.cell(HDR, i, h)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = hdr_fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[HDR].height = 30

    NUM = {"Backlinks (true)", "Follow (Equity) Links", "Domain ascore"}
    for ri, row in enumerate(rows, start=first):
        for ci, (name, _) in enumerate(TAB_COLS, start=1):
            v = row.get(name, "")
            if name in NUM and v not in ("", None):
                try:
                    v = int(v)
                except ValueError:
                    pass
            c = ws.cell(ri, ci, v)
            c.font = F_BODY
            c.alignment = A_WRAP if name == "Rationale" else A_TOP
            c.border = BOT
        if recommend:
            rec, why = recommend.get(row["Referring Domain"], ("", ""))
            rc = ws.cell(ri, len(TAB_COLS) + 1, rec)
            rc.font = Font(name=FONT, size=10, bold=True)
            rc.alignment = A_TOP
            rc.border = BOT
            rc.fill = PatternFill("solid", fgColor={
                "DISAVOW": "F8CBAD", "KEEP": "C6E0B4",
                "ASK_CLIENT": "FFE699"}.get(rec, "FFFFFF"))
            ec = ws.cell(ri, len(TAB_COLS) + 2, why)
            ec.font = F_BODY
            ec.alignment = A_WRAP
            ec.border = BOT
        d = ws.cell(ri, len(TAB_COLS) + n_rec + 1, default)
        d.font = F_BODY
        d.fill = PatternFill("solid", fgColor="FFF2CC")
        d.border = BOT
        ws.cell(ri, len(TAB_COLS) + 2).border = BOT

    ws.auto_filter.ref = f"A{HDR}:{get_column_letter(ncol)}{last}"
    ws.freeze_panes = f"B{first}"
    dv = DataValidation(type="list", formula1=confirm_list, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{dec_col}{first}:{dec_col}{last}")
    return ws


def main(outdir):
    dom = list(csv.DictReader(open(f"{outdir}/full_refdomain_audit.csv", encoding="utf-8")))
    url = list(csv.DictReader(open(f"{outdir}/url_drilldown.csv", encoding="utf-8")))
    order = {"DISAVOW": 0, "REVIEW_MANUALLY": 1, "KEEP_AFFILIATE_RETAIN": 2}
    dom.sort(key=lambda r: (order[r["Action Recommendation"]],
                            -int(r["Backlinks (true)"])))

    by_domain = {}
    for r in url:
        by_domain.setdefault(r["Referring Domain"], []).append(r)

    rows = []
    for d in dom:
        key = d["Referring Domain"]
        rows.append({**d, "Level": "DOMAIN",
                     "Referring Domain / URL": key,
                     "Anchor Type": "", "Sponsored": "",
                     "Sitewide": "", "Lost Link": ""})
        for u in by_domain.get(key, []):
            rows.append({
                "Level": "URL",
                "Referring Domain / URL": u["Referring Domain / URL"],
                "Target URL": u["Target URL"], "Anchor Text": u["Anchor Text"],
                "Anchor Type": u["Anchor Type"],
                "Action Recommendation": u["Action Recommendation"],
                "Primary Risk Factor": u["Primary Risk Factor"],
                "Confidence Score": u["Confidence Score"],
                "Domain ascore": u["Page AScore"],
                "Avg External Links": u["External Links"],
                "Nofollow %": "100%" if u["Nofollow"] == "true" else "0%",
                "Sponsored": u["Sponsored"], "Sitewide": u["Sitewide"],
                "Lost Link": u["Lost Link"], "First seen": u["First Seen"],
                "Last seen": u["Last Seen"],
            })

    wb = Workbook()
    ws = wb.active
    ws.title = "Backlink Audit"
    HDR = 9
    first, last = HDR + 1, HDR + len(rows)
    act, lvl = f"$C${first}:$C${last}", f"$A${first}:$A${last}"
    bl, fol = f"$I${first}:$I${last}", f"$K${first}:$K${last}"

    ws["A1"] = "Performance Lab - Backlink Disavow Audit"
    ws["A1"].font = Font(name=FONT, size=15, bold=True)
    ws["A2"] = ("All 2,928 referring domains (Level=DOMAIN) plus the per-URL drill-down "
                "where the 50k backlink sample covers them (Level=URL). Check Evidence "
                "Level: 602 domains were judged on link-level data, the rest on domain "
                "metrics only. Action cells are dropdowns; counts below are live formulas.")
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color="595959")

    for col, head in zip("ABCD", ["Action", "Domains", "Backlinks (true)",
                                  "Follow links (sampled)"]):
        ws[f"{col}4"] = head
    for i, a in enumerate(["DISAVOW", "REVIEW_MANUALLY", "KEEP_AFFILIATE_RETAIN"]):
        r = 5 + i
        ws[f"A{r}"] = a
        ws[f"B{r}"] = f'=COUNTIFS({act},$A{r},{lvl},"DOMAIN")'
        ws[f"C{r}"] = f'=SUMIFS({bl},{act},$A{r},{lvl},"DOMAIN")'
        ws[f"D{r}"] = f'=SUMIFS({fol},{act},$A{r},{lvl},"DOMAIN")'
        ws[f"A{r}"].fill = ACTION_FILL[a]
    ws["A8"] = "TOTAL"
    for col in "BCD":
        ws[f"{col}8"] = f"=SUM({col}5:{col}7)"
    for r in range(4, 9):
        for c in "ABCD":
            cell = ws[f"{c}{r}"]
            cell.font = Font(name=FONT, size=10, bold=(r in (4, 8)))
            if c != "A":
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = "#,##0"

    thin = Side(style="thin", color="BFBFBF")
    BOT = Border(bottom=thin)
    F_DOM = Font(name=FONT, size=10, bold=True, color="000000")
    F_URL = Font(name=FONT, size=10, bold=False, color="404040")
    A_TOP = Alignment(vertical="top")
    A_WRAP = Alignment(vertical="top", wrap_text=True)
    WRAPPED = {"Rationale", "Primary Risk Factor"}
    DOM_FILL = PatternFill("solid", fgColor="D9E1F2")
    # Group band one row above the names, merged per group, so 31 columns
    # read as six sections rather than an undifferentiated wall.
    _gi = 1
    while _gi <= len(COL_GROUPS):
        _grp = COL_GROUPS[_gi - 1][0]
        _span = 1
        while (_gi + _span <= len(COL_GROUPS)
               and COL_GROUPS[_gi + _span - 1][0] == _grp):
            _span += 1
        if _span > 1:
            ws.merge_cells(start_row=HDR - 1, start_column=_gi,
                           end_row=HDR - 1, end_column=_gi + _span - 1)
        _gc = ws.cell(row=HDR - 1, column=_gi, value=_grp.upper())
        _gc.font = Font(name=FONT, size=9, bold=True, color="FFFFFF")
        _gc.fill = PatternFill("solid", fgColor=GROUP_FILL[_grp])
        _gc.alignment = Alignment(horizontal="center", vertical="center")
        _gi += _span

    for i, (name, width) in enumerate(COLS, start=1):
        c = ws.cell(row=HDR, column=i, value=name)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=GROUP_FILL[COL_GROUPS[i - 1][0]])
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[HDR - 1].height = 16
    ws.row_dimensions[HDR].height = 30

    for ri, row in enumerate(rows, start=first):
        is_dom = row["Level"] == "DOMAIN"
        for ci, (name, _) in enumerate(COLS, start=1):
            v = row.get(name, "")
            if name in NUMERIC and v not in ("", None):
                try:
                    v = float(v) if "." in str(v) else int(v)
                except ValueError:
                    pass
            c = ws.cell(row=ri, column=ci, value=v)
            c.font = F_DOM if is_dom else F_URL
            c.alignment = A_WRAP if name in WRAPPED else A_TOP
            c.border = BOT
        ws.cell(row=ri, column=3).fill = ACTION_FILL[row["Action Recommendation"]]
        if is_dom:
            ws.cell(row=ri, column=1).fill = DOM_FILL

    ws.auto_filter.ref = f"A{HDR}:{get_column_letter(len(COLS))}{last}"
    ws.freeze_panes = f"C{first}"
    dv = DataValidation(type="list",
                        formula1='"DISAVOW,REVIEW_MANUALLY,KEEP_AFFILIATE_RETAIN"',
                        allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"C{first}:C{last}")

    # ---------------- Tab 2: Disavow working sheet ----------------------
    _worksheet(
        wb, "Disavow", dom, "DISAVOW",
        "Disavow queue - 'Disavow Entry' is the exact line for Google's tool. "
        "Work the Confirmed column; the counts update live.",
        confirm_header="Confirmed? (Y / N / HOLD)",
        confirm_list='"Y,N,HOLD"',
    )

    # ---------------- Tab 3: Review queue -------------------------------
    _worksheet(
        wb, "Review Queue", dom, "REVIEW_MANUALLY",
        "Domains needing a human call, highest backlink volume first. Set "
        "Decision per row; the counts update live.",
        confirm_header="Decision (DISAVOW / KEEP / PENDING)",
        confirm_list='"DISAVOW,KEEP,PENDING"',
        default="PENDING",
        recommend=REVIEW_RECOMMENDATIONS,
    )

    path = f"{outdir}/performancelab_backlink_audit.xlsx"
    wb.save(path)
    print(f"{len(rows):,} rows -> {path}")
    print(f"  DOMAIN rows: {sum(1 for r in rows if r['Level']=='DOMAIN'):,}")
    print(f"  URL rows   : {sum(1 for r in rows if r['Level']=='URL'):,}")


if __name__ == "__main__":
    main(sys.argv[1])
