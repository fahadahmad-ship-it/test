"""Build the Ritter workbook (7 tabs) + disavow file, matching the signed-off
Harbinger template (KandK_sample.xlsx) cell-for-cell. Change the format here,
never by hand in Excel. (AUDIT_FORMAT.md + BACKLINK_AUDIT_PLAYBOOK.md Section 8.)
"""
import glob
import os
import sys
import collections
import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils import get_column_letter

sys.path.insert(0, "/home/user/test/ritter/scripts")
import config as C
from load import read_semrush_csv, host_of, path_of, canon_domain, slash24
import classify

DATA = "/home/user/test/ritter/data"
OUT = "/home/user/test/ritter/out"
REF_LOGO = "/home/user/test/ritter/ref/image1.png"
DISAVOW_NAME = "disavow_ritterconsultingengineers.txt"

ACCENT = "FF0C343D"
WHITE = "FFFFFFFF"
BLACK = "FF000000"
FONT = "Geist"

thin = Side(style="thin")
BORDER_FULL = Border(left=thin, right=thin, top=thin, bottom=thin)
BORDER_HEADER = Border(left=thin, right=thin, top=thin)  # data-tab header: no bottom
NOBORDER = Border()

HEADER_FONT = Font(name=FONT, size=9, bold=True, color=WHITE)
HEADER_FILL = PatternFill("solid", fgColor=ACCENT)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
DATA_FONT = Font(name=FONT, size=9, color=BLACK)
WHITE_FILL = PatternFill("solid", fgColor=WHITE)
INPUT_FILL = PatternFill("solid", fgColor=ACCENT)     # partner-input cells
INPUT_FONT = Font(name=FONT, size=9, color=WHITE)


def ts_to_dt(ts):
    try:
        v = int(str(ts).strip())
        if v <= 0:
            return None
        return datetime.datetime.utcfromtimestamp(v)
    except (ValueError, TypeError):
        return None


def load_metrics():
    comp = {}
    cpath = os.path.join(DATA, "metrics/comparison.csv")
    if os.path.exists(cpath):
        rows, _, _ = read_semrush_csv([cpath], 6)
        for r in rows:
            comp[canon_domain(r["target"])] = {
                "authority_score": r.get("ascore", ""),
                "backlinks_num": r.get("backlinks_num", ""),
                "domains_num": r.get("domains_num", ""),
                "follows_num": r.get("follows_num", ""),
                "nofollows_num": r.get("nofollows_num", ""),
            }
    rank = {}
    for rp in sorted(glob.glob(os.path.join(DATA, "metrics/rank_*.csv"))):
        rows, _, _ = read_semrush_csv([rp], 3)
        for r in rows:
            rank[canon_domain(r["domain"])] = {
                "organic_keywords": r.get("organic_keywords", ""),
                "organic_traffic": r.get("organic_traffic", ""),
            }
    return comp, rank


def num(v, default=0):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return default


def site_type(domain, titles, AS):
    d = domain.lower()
    t = " ".join(titles).lower()
    blob = d + " " + t
    if "bookmark" in blob:
        return "Social bookmarking site"
    if any(k in d for k in ("director", "listing", "list", "local", "biz", "pages",
                            "find", "places", "yellow")):
        return "Low quality web directory"
    if any(k in d for k in ("article", "blog", "news", "post", "guest", "wiki", "mag")):
        return "Guest article or content farm"
    if AS >= C.KEEP_AS_THRESHOLD:
        return "Genuine site"
    if any(k in t for k in ("directory", "listing", "best 30", "yellow", "superpages")):
        return "Low quality web directory"
    return "Low quality web directory"


def main():
    os.makedirs(OUT, exist_ok=True)
    backlinks, bl_rej, _ = read_semrush_csv(
        sorted(glob.glob(os.path.join(DATA, "fetch/backlinks_p*.csv"))), 10)
    refdomains, rd_rej, _ = read_semrush_csv(
        sorted(glob.glob(os.path.join(DATA, "rd/refdomains_p*.csv"))), 9)
    comp, rank = load_metrics()
    records, ip24 = classify.build_domain_records(backlinks, refdomains, comp, rank)

    # classify each domain
    rows = []
    for d in sorted(records):
        rec = records[d]
        status, reason, atypes = classify.classify_domain(rec, ip24)
        rec["status"] = status
        rec["reason"] = reason
        rec["atypes"] = atypes
        rows.append(rec)

    # ---- redundancy: a Spam(Disavow) child whose parent is also Spam(Disavow) ----
    spam_set = set(r["domain"] for r in rows if r["status"] == "Spam (Disavow)")
    for r in rows:
        r["redundant"] = False
        if r["status"] == "Spam (Disavow)":
            d = r["domain"]
            for p in spam_set:
                if p != d and d.endswith("." + p):
                    r["redundant"] = True
                    break

    # ---- per-link rows (All Backlinks) + anchor aggregates ----
    def link_rows_for(rec):
        out = []
        for l in rec["links"]:
            a = l.get("anchor", "")
            atype = classify.anchor_type(a, l.get("source_title", ""))
            nf = l.get("nofollow", "").lower() == "true"
            out.append({
                "refdom": rec["domain"], "status": rec["status"], "tool": "Semrush",
                "anchor": a, "atype": atype,
                "linktype": "Nofollow" if nf else "Dofollow",
                "page_url": l.get("source_url", ""), "page_title": l.get("source_title", ""),
                "target": l.get("target_url", ""), "nofollow": nf,
            })
        return out

    all_links = []
    for r in rows:
        all_links.extend(link_rows_for(r))

    # ---- build workbook ----
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # helper to lay a data tab
    def data_tab(name, headers, data, widths, row_height, col_align, col_numfmt,
                 input_cols=(), header_align_overrides=None):
        header_align_overrides = header_align_overrides or {}
        ws = wb.create_sheet(name)
        # leave showGridLines unset (default = on) to match the template exactly
        for i, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=i, value=h)
            c.font = HEADER_FONT
            c.fill = HEADER_FILL
            c.border = BORDER_HEADER
            if i in header_align_overrides:
                c.alignment = Alignment(horizontal=header_align_overrides[i],
                                        vertical="center", wrap_text=True)
            else:
                c.alignment = HEADER_ALIGN
        ws.row_dimensions[1].height = 31.5
        for ri, rowvals in enumerate(data, 2):
            for ci, val in enumerate(rowvals, 1):
                c = ws.cell(row=ri, column=ci, value=val)
                c.font = DATA_FONT
                c.fill = WHITE_FILL
                al = col_align.get(ci, "L")
                c.alignment = Alignment(
                    horizontal=None if al == "L" else al, vertical="center")
                if ci in col_numfmt:
                    c.number_format = col_numfmt[ci]
                c.border = NOBORDER
            ws.row_dimensions[ri].height = row_height
        # input cells (accent fill) across all data rows
        for ci in input_cols:
            for ri in range(2, len(data) + 2):
                c = ws.cell(row=ri, column=ci)
                c.fill = INPUT_FILL
                c.font = INPUT_FONT
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        last = f"{get_column_letter(len(headers))}{max(len(data)+1,1)}"
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = f"A1:{last}"
        return ws

    # ============ TAB 2: Referring Domain Audit ============
    rda_headers = ["Domain", "Status", "AS", "Backlinks", "RD's", "Traffic",
                   "In Disavow", "Links Point To", "Dofollow Links", "Nofollow Links",
                   "First Seen", "Top Anchor Text", "Example Linking Page",
                   "Linking Page Title", "Source", "IP", "Disavow Line"]
    rda_data = []
    for r in rows:
        links = r["links"]
        dofollow = sum(1 for l in links if l.get("nofollow", "").lower() != "true")
        nofollow = len(links) - dofollow
        anchors = [l.get("anchor", "") for l in links]
        top_anchor = collections.Counter(a for a in anchors if a).most_common(1)
        top_anchor = top_anchor[0][0] if top_anchor else ""
        # example page: prefer a live 200 page
        ex = None
        for l in links:
            if l.get("response_code", "") == "200":
                ex = l
                break
        if ex is None:
            ex = links[0] if links else {}
        points_to = collections.Counter(host_of(l.get("target_url", "")) for l in links).most_common(1)
        points_to = points_to[0][0] if points_to else C.MONEY_DOMAIN
        first_seens = [ts_to_dt(l.get("first_seen", "")) for l in links]
        first_seens = [x for x in first_seens if x]
        fs = min(first_seens) if first_seens else ts_to_dt(r.get("rd_first_seen", ""))
        status = r["status"]
        if status == "Spam (Disavow)":
            indis = "Covered by parent" if r["redundant"] else "Yes"
        elif status.startswith("Held"):
            indis = "Held"
        else:
            indis = "No"
        dis_line = ("domain:" + r["domain"]) if (status == "Spam (Disavow)" and not r["redundant"]) else ""
        rda_data.append([
            r["domain"], status, num(r["AS"]), len(links), num(r["own_rds"]),
            num(r["traffic"]), indis, points_to, dofollow, nofollow, fs,
            top_anchor, ex.get("source_url", ""), ex.get("source_title", ""),
            "Semrush", r["ip"], dis_line,
        ])
    rda_widths = [36, 24.71, 9.57, 13, 9.43, 9.71, 12.43, 21.29, 14, 8.71, 12, 45,
                  8.71, 40, 14, 15, 14]
    data_tab("Referring Domain Audit", rda_headers, rda_data, rda_widths, 15.75,
             {3: "center", 4: "center", 5: "center", 6: "center", 7: "center",
              9: "center", 10: "center", 11: "center", 15: "center", 16: "center"},
             {4: "#,##0", 5: "#,##0", 6: "#,##0", 11: "d mmm yyyy"})

    # ============ TAB 3: All Backlinks ============
    ab_headers = ["Referring Domain", "Status", "Tool", "Anchor Text", "Anchor Type",
                  "Link Type", "Linking Page URL", "Linking Page Title", "Target URL"]
    ab_data = [[l["refdom"], l["status"], l["tool"], l["anchor"], l["atype"],
                l["linktype"], l["page_url"], l["page_title"], l["target"]] for l in all_links]
    data_tab("All Backlinks", ab_headers, ab_data,
             [25.43, 27.14, 14.71, 55, 32, 10, 55, 53.14, 30.57], 22.5,
             {3: "left", 6: "center"}, {}, header_align_overrides={3: "left"})

    # ============ TAB 4: Anchor Analysis ============
    total_links = len(all_links)
    by_anchor = collections.defaultdict(lambda: {"bl": 0, "doms": set(), "spam_doms": set(), "atype": ""})
    for l in all_links:
        a = l["anchor"]
        e = by_anchor[a]
        e["bl"] += 1
        e["doms"].add(l["refdom"])
        e["atype"] = l["atype"]
        if l["status"] in ("Spam (Disavow)", "Spam (Nofollow, No Action)"):
            e["spam_doms"].add(l["refdom"])
    aa_data = []
    for a, e in sorted(by_anchor.items(), key=lambda kv: kv[1]["bl"], reverse=True):
        aa_data.append([a, e["atype"], e["bl"], e["bl"] / total_links if total_links else 0,
                        len(e["doms"]), len(e["spam_doms"])])
    data_tab("Anchor Analysis", ["Anchor Text", "Anchor Type", "Backlinks",
             "Share of Backlinks", "Referring Domains", "Spam Domains Using It"],
             aa_data, [115.86, 37.71, 14, 8.71, 13, 20.29], 22.5,
             {3: "center", 4: "center", 5: "center", 6: "center"},
             {3: "#,##0", 4: "0.00%"})

    # ============ TAB 5: Exact Match Anchors ============
    em_data = []
    seen_pairs = set()
    for r in rows:
        AS = num(r["AS"])
        titles = [l.get("source_title", "") for l in r["links"]]
        for l in r["links"]:
            a = l.get("anchor", "")
            at = classify.anchor_type(a, l.get("source_title", ""))
            if at in (classify.ANCHOR_EXACT, classify.ANCHOR_EXACT_GEO):
                key = (r["domain"], a.lower())
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                market = C.GEO_TERMS[0].title() if at == classify.ANCHOR_EXACT_GEO else "Non-geo"
                em_data.append([r["domain"], l.get("source_url", ""), a, market,
                                site_type(r["domain"], titles, AS), "", ""])
    data_tab("Exact Match Anchors", ["Referring domain", "Example backlink (linking page)",
             "Exact-match commercial anchor", "Market", "Site type (indicative)",
             "Partner confirmed? (Y/N)", "Final decision"], em_data,
             [25.43, 59, 53.14, 16, 24.57, 15.43, 15], 22.5,
             {3: "center", 4: "center"}, {}, input_cols=(6, 7))

    # ============ TAB 6: Pending Disavow Lines ============
    pend = [r for r in rows if r["status"] == "Held (Pending Partner)"]
    rec_text = f"Append only if the partner does not claim it, to {DISAVOW_NAME}"
    pd_data = [[r["domain"], "domain:" + r["domain"], rec_text] for r in sorted(pend, key=lambda r: r["domain"])]
    data_tab("Pending Disavow Lines", ["Referring domain",
             "Disavow line (append to disavow.txt once confirmed)", "Recommendation"],
             pd_data, [32, 44, 48], 22.5, {}, {})

    # ============ TAB 7: Disavow List ============
    disavow_rows = [r for r in rows if r["status"] == "Spam (Disavow)" and not r["redundant"]]
    disavow_rows.sort(key=lambda r: r["domain"])
    dl_data = []
    for r in disavow_rows:
        top = collections.Counter(l.get("anchor", "") for l in r["links"] if l.get("anchor")).most_common(1)
        top = top[0][0] if top else ""
        dl_data.append(["domain:" + r["domain"], num(r["AS"]), num(r["own_backlinks"]),
                        num(r["own_rds"]), num(r["traffic"]), num(r["organic_keywords"]), top])
    data_tab("Disavow List", ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic",
             "Organic Keywords", "Top Anchor Text"], dl_data,
             [44, 14, 15.57, 14, 11.14, 14.86, 98.86], 22.5,
             {2: "center", 3: "center", 4: "center", 5: "center", 6: "center"},
             {3: "#,##0", 4: "#,##0", 5: "#,##0", 6: "#,##0"})

    # ============ TAB 1: Summary (insert first) ============
    build_summary(wb, rows, all_links, records)
    wb.move_sheet("Summary", -(len(wb.sheetnames) - 1))

    # ---- save ----
    out_xlsx = os.path.join(OUT, "Ritter_Backlinks_Audit.xlsx")
    wb.save(out_xlsx)

    # ---- disavow.txt ----
    write_disavow(disavow_rows, rows)

    # ---- counts ----
    counts = collections.Counter(r["status"] for r in rows)
    print("=== STATUS COUNTS (domains) ===")
    for s in ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
              "Spam (Nofollow, No Action)", "Keep", "Own Site"]:
        print(f"  {s:32} {counts.get(s,0)}")
    print(f"  {'TOTAL':32} {len(rows)}")
    print(f"disavow lines emitted: {len(disavow_rows)}  (redundant children: {sum(1 for r in rows if r.get('redundant'))})")
    print(f"pending (held) lines : {len(pend)}")
    print(f"total links          : {len(all_links)}")
    print(f"workbook: {out_xlsx}")


def build_summary(wb, rows, all_links, records):
    ws = wb.create_sheet("Summary")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 38.86
    ws.column_dimensions["B"].width = 16.29
    ws.column_dimensions["C"].width = 17.57
    ws.column_dimensions["D"].width = 18.71
    ws.column_dimensions["E"].width = 120
    for r in range(1, 29):
        ws.row_dimensions[r].height = 22.5

    # logo
    if os.path.exists(REF_LOGO):
        img = XLImage(REF_LOGO)
        marker = AnchorMarker(col=0, colOff=381000, row=0, rowOff=0)
        size = XDRPositiveSize2D(cx=1866900, cy=552450)
        img.anchor = OneCellAnchor(_from=marker, ext=size)
        ws.add_image(img)

    # title B1:E2
    ws.merge_cells("B1:E2")
    t = ws["B1"]
    t.value = C.CLIENT_NAME
    t.font = Font(name=FONT, size=21, bold=True, color=ACCENT)
    t.alignment = Alignment(horizontal="center", vertical="center")

    counts = collections.Counter(r["status"] for r in rows)
    bl_by_status = collections.Counter(l["status"] for l in all_links)
    total_dom = len(rows)
    total_bl = len(all_links)

    # status table header row 3
    hdr = ["Status", "Domains", "Backlinks", "Share of Domains", "What it means"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(row=3, column=i, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color=WHITE)
        c.fill = HEADER_FILL
        c.border = BORDER_FULL
        c.alignment = HEADER_ALIGN
    meanings = {
        "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
        "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a service, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
        "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
        "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
        "Keep": "Genuine or harmless link. Keep.",
        "Own Site": "Client owned domain that redirects into the site.",
    }
    order = ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
             "Spam (Nofollow, No Action)", "Keep", "Own Site"]
    row = 4
    for s in order:
        dn = counts.get(s, 0)
        bn = bl_by_status.get(s, 0)
        vals = [s, dn, bn, (dn / total_dom if total_dom else 0), meanings[s]]
        for i, v in enumerate(vals, 1):
            c = ws.cell(row=row, column=i, value=v)
            c.font = DATA_FONT
            c.fill = WHITE_FILL
            c.border = BORDER_FULL
            if i in (2, 3):
                c.number_format = "#,##0"
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif i == 4:
                c.number_format = "0.0%"
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif i == 5:
                c.alignment = Alignment(vertical="center", wrap_text=True)
            else:
                c.alignment = Alignment(vertical="center")
        row += 1
    # total row
    tv = ["Total", total_dom, total_bl, 1.0, None]
    for i, v in enumerate(tv, 1):
        if v is None:
            continue
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(name=FONT, size=9, bold=True)
        c.fill = WHITE_FILL
        c.border = BORDER_FULL
        if i in (2, 3):
            c.number_format = "#,##0"
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif i == 4:
            c.number_format = "0.0%"
            c.alignment = Alignment(horizontal="center", vertical="center")
        else:
            c.alignment = Alignment(vertical="center")
    total_row = row

    # Key findings heading
    kf_row = total_row + 1
    kc = ws.cell(row=kf_row, column=1, value="Key findings")
    kc.font = Font(name=FONT, size=10, bold=True, color=BLACK)
    kc.alignment = Alignment(vertical="center")

    findings = compute_findings(rows, all_links, counts, bl_by_status)
    fr = kf_row + 1
    for f in findings:
        ws.merge_cells(start_row=fr, start_column=1, end_row=fr, end_column=5)
        c = ws.cell(row=fr, column=1, value=f)
        c.font = DATA_FONT
        c.alignment = Alignment(vertical="center", wrap_text=True)
        fr += 1

    # Anchor profile heading
    ap_row = fr
    ac = ws.cell(row=ap_row, column=1, value="Anchor text profile (all backlinks)")
    ac.font = Font(name=FONT, size=11, bold=True, color=ACCENT)
    ac.alignment = Alignment(vertical="center")
    # anchor profile header
    aphdr_row = ap_row + 1
    for i, h in enumerate(["Anchor type", "Backlinks", "Share of Backlinks", "Referring Domains"], 1):
        c = ws.cell(row=aphdr_row, column=i, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.border = BORDER_FULL
        c.alignment = HEADER_ALIGN
    by_type_bl = collections.Counter(l["atype"] for l in all_links)
    by_type_dom = collections.defaultdict(set)
    for l in all_links:
        by_type_dom[l["atype"]].add(l["refdom"])
    apr = aphdr_row + 1
    for atype, bl in by_type_bl.most_common():
        vals = [atype, bl, (bl / total_bl if total_bl else 0), len(by_type_dom[atype])]
        for i, v in enumerate(vals, 1):
            c = ws.cell(row=apr, column=i, value=v)
            c.font = DATA_FONT
            c.fill = WHITE_FILL
            c.border = BORDER_FULL
            if i == 1:
                c.number_format = "#,##0"
                c.alignment = Alignment(vertical="center")
            elif i == 3:
                c.number_format = "0.0%"
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.number_format = "#,##0"
                c.alignment = Alignment(horizontal="center", vertical="center")
        apr += 1


def compute_findings(rows, all_links, counts, bl_by_status):
    total_dom = len(rows)
    spam_d = counts.get("Spam (Disavow)", 0)
    spam_nf = counts.get("Spam (Nofollow, No Action)", 0)
    held = counts.get("Held (Pending Partner)", 0)
    held_nf = counts.get("Held (Nofollow, No Action)", 0)
    keep = counts.get("Keep", 0)
    all_spam = spam_d + spam_nf
    # home vs deep
    home = sum(1 for l in all_links if path_of(l["target"]) in classify.HOME_PATHS)
    deep = len(all_links) - home
    # dominant anchor
    anc = collections.Counter(l["anchor"] for l in all_links if l["anchor"])
    top_anchor, top_anchor_n = anc.most_common(1)[0] if anc else ("", 0)
    top_anchor_doms = len(set(l["refdom"] for l in all_links if l["anchor"] == top_anchor))
    # held traffic zero
    held_rows = [r for r in rows if r["status"].startswith("Held")]
    held_zero = sum(1 for r in held_rows if num_safe(r.get("traffic")) == 0)
    # directory-campaign signature among the held-pending set
    pending_rows = [r for r in rows if r["status"] == "Held (Pending Partner)"]
    diry = sum(1 for r in pending_rows if any(k in r["domain"] for k in
              ("director", "listing", "list", "local", "biz", "bookmark", "pages", "find")))
    f = []
    f.append(f"{all_spam:,} of the {total_dom:,} referring domains are spam. {spam_d:,} have a dofollow link and go in the disavow file. The other {spam_nf:,} are nofollow and need no action.")
    f.append(f"The profile is far bigger than the brief said. The brief listed about 150 referring domains. The live profile now has {total_dom:,}. We audited all of them, not just the 150.")
    f.append(f"Only one disavow file is needed, for {C.MONEY_DOMAIN}. No other domain redirects into the site, so this one file covers everything.")
    f.append(f"There are two clear patterns. {home:,} of the {len(all_links):,} links point at the home page. The {deep:,} that point at deep service pages carry the commercial anchors. The home page links are the spam attack.")
    f.append(f'The most common anchor is backlink sales copy. It appears on {top_anchor_doms:,} domains and reads "{top_anchor}".')
    f.append(f"{held:,} domains are held for the previous supplier to confirm, in case they were paid placements. {diry:,} of them are directory or listing sites. They all use the same service plus Louisiana anchor, which looks like one commissioned local campaign.")
    f.append(f"Held does not mean valuable. {held_zero:,} of the {held + held_nf:,} held domains have no organic traffic at all.")
    return f[:7]


def num_safe(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 0


def write_disavow(disavow_rows, rows):
    path = os.path.join(OUT, DISAVOW_NAME)
    # group by reason
    groups = collections.OrderedDict([
        ("Keyword-stuffed SEO sales-copy anchors (PBN / link-service networks)", []),
        ("Spam host-name / domain-marketplace signatures", []),
        ("Off-topic (casino / pharma / adult) links", []),
        ("Other confirmed spam with a dofollow link", []),
    ])
    for r in disavow_rows:
        reason = r.get("reason", "")
        if "sales-copy" in reason or "PBN" in reason:
            groups["Keyword-stuffed SEO sales-copy anchors (PBN / link-service networks)"].append(r["domain"])
        elif "host-name" in reason or "marketplace" in reason or "page title" in reason:
            groups["Spam host-name / domain-marketplace signatures"].append(r["domain"])
        elif "Off-topic" in reason:
            groups["Off-topic (casino / pharma / adult) links"].append(r["domain"])
        else:
            groups["Other confirmed spam with a dofollow link"].append(r["domain"])
    total = len(disavow_rows)
    held = sum(1 for r in rows if r["status"] == "Held (Pending Partner)")
    lines = []
    lines.append(f"# Google disavow file for {C.MONEY_DOMAIN}")
    lines.append(f"# Generated {datetime.date.today().isoformat()} by Harbinger Marketing")
    lines.append(f"#")
    lines.append(f"# {total} domains, all confirmed spam with at least one dofollow link.")
    lines.append(f"# This is the ONLY file to submit: {C.MONEY_DOMAIN} is the single Search")
    lines.append(f"#   Console property and no other domain redirects into the site.")
    lines.append(f"# {held} further domains are HELD and are NOT in this file. They carry")
    lines.append(f"#   exact-match commercial (service + Louisiana) anchors that the previous")
    lines.append(f"#   SEO supplier may have ordered. In this audit \"supplier\" = the \"partner\"")
    lines.append(f"#   named on the workbook. DO NOT submit this file until that supplier has")
    lines.append(f"#   confirmed which of the held placements, if any, they commissioned.")
    lines.append(f"# Nothing here is disavowed on Authority Score, TLD or shared IP alone:")
    lines.append(f"#   every line rests on a spam anchor, a spam page title/URL, or a known")
    lines.append(f"#   link-network host.")
    lines.append(f"# Check Search Console first: if a disavow file already exists on this")
    lines.append(f"#   property, uploading REPLACES it; merge rather than overwrite.")
    lines.append("")
    for reason, doms in groups.items():
        if not doms:
            continue
        lines.append(f"# --- {reason} ({len(doms)}) ---")
        for d in sorted(doms):
            lines.append(f"domain:{d}")
        lines.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"disavow file: {path}")


if __name__ == "__main__":
    main()
