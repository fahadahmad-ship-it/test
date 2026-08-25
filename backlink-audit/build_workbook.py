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
from openpyxl.worksheet.datavalidation import DataValidation

COLS = [
    ("Level", 9), ("Referring Domain / URL", 46), ("Target URL", 42),
    ("Anchor Text", 38), ("Anchor Type", 15), ("Action Recommendation", 23),
    ("Primary Risk Factor", 44), ("Confidence Score", 11),
    ("Remediation Priority", 26), ("Disavow Entry", 30),
    ("Backlinks", 10), ("Follow (Equity) Links", 12), ("Linking Pages", 11),
    ("Unique Anchors", 11), ("Top Anchor Share", 11),
    ("Exact-Match Anchor %", 12), ("Branded/URL Anchor %", 12),
    ("Median Page AScore", 11), ("Max Page AScore", 11),
    ("Avg External Links", 11), ("Nofollow %", 10), ("Sponsored", 10),
    ("Sitewide", 9), ("Lost Link", 9), ("Topically Relevant", 11),
    ("Distinct Targets", 11), ("Lost %", 9),
    ("First Seen", 12), ("Last Seen", 12), ("Rationale", 90),
]
FONT = "Arial"
ACTION_FILL = {
    "DISAVOW":               PatternFill("solid", fgColor="F8CBAD"),
    "REVIEW_MANUALLY":       PatternFill("solid", fgColor="FFE699"),
    "KEEP_AFFILIATE_RETAIN": PatternFill("solid", fgColor="C6E0B4"),
}
NUMERIC = {"Backlinks", "Follow (Equity) Links", "Linking Pages",
           "Unique Anchors", "Max Page AScore", "Median Page AScore",
           "Avg External Links", "Distinct Targets"}


def main(outdir):
    dom = list(csv.DictReader(open(f"{outdir}/domain_audit.csv", encoding="utf-8")))
    url = list(csv.DictReader(open(f"{outdir}/url_drilldown.csv", encoding="utf-8")))
    order = {"DISAVOW": 0, "REVIEW_MANUALLY": 1, "KEEP_AFFILIATE_RETAIN": 2}
    dom.sort(key=lambda r: (order[r["Action Recommendation"]], -int(r["Backlinks"])))

    by_domain = {}
    for r in url:
        by_domain.setdefault(r["Referring Domain"], []).append(r)

    rows = []
    for d in dom:
        key = d["Referring Domain / URL"]
        rows.append({**d, "Level": "DOMAIN", "Anchor Type": "",
                     "Sitewide": "", "Lost Link": "",
                     "Disavow Entry": (f"domain:{key}"
                                       if d["Action Recommendation"] == "DISAVOW" else "")})
        for u in by_domain.get(key, []):
            rows.append({
                "Level": "URL",
                "Referring Domain / URL": u["Referring Domain / URL"],
                "Target URL": u["Target URL"], "Anchor Text": u["Anchor Text"],
                "Anchor Type": u["Anchor Type"],
                "Action Recommendation": u["Action Recommendation"],
                "Primary Risk Factor": u["Primary Risk Factor"],
                "Confidence Score": u["Confidence Score"],
                "Median Page AScore": u["Page AScore"],
                "Avg External Links": u["External Links"],
                "Nofollow %": "100%" if u["Nofollow"] == "true" else "0%",
                "Sponsored": u["Sponsored"], "Sitewide": u["Sitewide"],
                "Lost Link": u["Lost Link"], "First Seen": u["First Seen"],
                "Last Seen": u["Last Seen"],
            })

    wb = Workbook()
    ws = wb.active
    ws.title = "Backlink Audit"
    HDR = 9
    first, last = HDR + 1, HDR + len(rows)
    act, lvl = f"$F${first}:$F${last}", f"$A${first}:$A${last}"
    bl, fol = f"$K${first}:$K${last}", f"$L${first}:$L${last}"

    ws["A1"] = "Performance Lab - Backlink Disavow Audit"
    ws["A1"].font = Font(name=FONT, size=15, bold=True)
    ws["A2"] = ("One row per referring domain (Level=DOMAIN), plus the per-URL drill-down "
                "for every flagged domain (Level=URL). Action cells are dropdowns; the "
                "counts below are live formulas and update as you resolve REVIEW rows.")
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color="595959")

    for col, head in zip("ABCD", ["Action", "Domains", "Backlinks", "Follow (equity) links"]):
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
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    for i, (name, width) in enumerate(COLS, start=1):
        c = ws.cell(row=HDR, column=i, value=name)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = hdr_fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = width
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
        ws.cell(row=ri, column=6).fill = ACTION_FILL[row["Action Recommendation"]]
        if is_dom:
            ws.cell(row=ri, column=1).fill = DOM_FILL

    ws.auto_filter.ref = f"A{HDR}:{get_column_letter(len(COLS))}{last}"
    ws.freeze_panes = f"C{first}"
    dv = DataValidation(type="list",
                        formula1='"DISAVOW,REVIEW_MANUALLY,KEEP_AFFILIATE_RETAIN"',
                        allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"F{first}:F{last}")

    path = f"{outdir}/performancelab_backlink_audit.xlsx"
    wb.save(path)
    print(f"{len(rows):,} rows -> {path}")
    print(f"  DOMAIN rows: {sum(1 for r in rows if r['Level']=='DOMAIN'):,}")
    print(f"  URL rows   : {sum(1 for r in rows if r['Level']=='URL'):,}")


if __name__ == "__main__":
    main(sys.argv[1])
