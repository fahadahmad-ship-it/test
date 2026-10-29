#!/usr/bin/env python3
"""
build.py — build the Jaco Contracting backlink audit workbook by cloning the
signed-off K&K template and replacing its data, so styling matches cell-for-cell.
Also writes the disavow file.

Run: python3 -I scripts/build.py
"""
import json, os, csv, datetime, copy, re
import openpyxl
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
TEMPLATE = os.path.join(BASE, "ref", "KK_template.xlsx")
CLIENT_NAME = "Jaco Contracting"
CLIENT = "jacocontracting.com"
DISAVOW_FILE = "disavow_jacocontracting.txt"

STATUS_ORDER = [
    "Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
    "Spam (Nofollow, No Action)", "Keep", "Own Site",
]
STATUS_MEANING = {
    "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
    "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
    "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
    "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
    "Keep": "Genuine or harmless link. Keep.",
    "Own Site": "Client owned domain that redirects into the site.",
}

def load():
    domains = json.load(open(os.path.join(DATA, "domains_classified.json")))
    links = [json.loads(l) for l in open(os.path.join(DATA, "links_classified.jsonl"))]
    return domains, links

def dt(unix):
    if not unix:
        return None
    try:
        return datetime.datetime.utcfromtimestamp(int(unix))
    except Exception:
        return None

def market_of(anchor):
    a = (anchor or "").lower()
    tn = any(x in a for x in ["chattanooga", "tennessee", " tn", "tn ", ",tn", ", tn"])
    ga = any(x in a for x in ["covington", "atlanta", "macon", "conyers", "newnan", "georgia", " ga", "ga ", ",ga", ", ga"])
    if tn and ga:
        return "Georgia / Tennessee"
    if tn:
        return "Tennessee"
    if ga:
        return "Georgia"
    return "Non-geo"

def site_type(domain, title):
    d = domain.lower(); t = (title or "").lower()
    if any(x in d for x in ["directory", "listing", "list", "local", "biz", "find", "bookmark", "yp", "places", "citysquares", "catalog"]):
        return "Low quality web directory"
    if any(x in d for x in ["article", "news", "blog", "wiki", "post", "press", "media", "mag", "journal"]):
        return "Article / blog network"
    return "Low quality web directory"

def capture_styles(ws, ncols):
    """Return (header_styles, data_styles) as copies, plus heights."""
    hdr = [copy.copy(ws.cell(row=1, column=c)._style) for c in range(1, ncols + 1)]
    data = [copy.copy(ws.cell(row=2, column=c)._style) for c in range(1, ncols + 1)]
    hh = ws.row_dimensions[1].height
    dh = ws.row_dimensions[2].height
    return hdr, data, hh, dh

def clear_data(ws):
    if ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)

def write_rows(ws, rows, data_styles, dh, ncols):
    for i, row in enumerate(rows):
        r = i + 2
        for c in range(1, ncols + 1):
            cell = ws.cell(row=r, column=c)
            cell.value = row[c - 1]
            cell._style = copy.copy(data_styles[c - 1])
        if dh:
            ws.row_dimensions[r].height = dh
    last = len(rows) + 1
    lastcol = get_column_letter(ncols)
    ws.auto_filter.ref = f"A1:{lastcol}{last}"
    ws.freeze_panes = "B2"

def in_disavow_label(status):
    if status == "Spam (Disavow)":
        return "Yes"
    if status.startswith("Held"):
        return "Held"
    return "No"

def main():
    domains, links = load()
    doms = list(domains.values())
    total_domains = len(doms)
    total_links = len(links)

    status_priority = {s: i for i, s in enumerate(STATUS_ORDER)}
    def dkey(v):
        return (status_priority.get(v["status"], 99), -v["backlinks"], v["domain"])

    wb = openpyxl.load_workbook(TEMPLATE)

    # ---------- Tab 2: Referring Domain Audit ----------
    ws = wb["Referring Domain Audit"]; NC = 17
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    rows = []
    for v in sorted(doms, key=dkey):
        rows.append([
            v["domain"], v["status"], v.get("AS", 0), v["backlinks"], v.get("RDs"),
            v.get("organic_traffic", 0), in_disavow_label(v["status"]),
            v.get("links_point_to", CLIENT), v["dofollow"], v["nofollow"],
            dt(v.get("first_seen")), v.get("top_anchor", ""), v.get("example_url", ""),
            v.get("example_title", ""), v.get("source", "Semrush"), v.get("ip", ""),
            ("domain:" + v["domain"]) if v["status"] == "Spam (Disavow)" else "",
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 3: All Backlinks ----------
    ws = wb["All Backlinks"]; NC = 9
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    def lkey(L):
        return (L["refdomain"], L["anchor"] or "")
    rows = []
    for L in sorted(links, key=lkey):
        st = domains.get(L["refdomain"], {}).get("status", "Keep")
        tool = "Semrush" if "Semrush" in L.get("sources", []) else "Ahrefs"
        rows.append([
            L["refdomain"], st, tool, L["anchor"], L["anchor_type"],
            "Nofollow" if L["nofollow"] else "Dofollow",
            L["source_url"], L.get("source_title", ""), L["target_url"],
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 4: Anchor Analysis ----------
    ws = wb["Anchor Analysis"]; NC = 6
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    from collections import defaultdict
    a_links = defaultdict(int); a_type = {}; a_doms = defaultdict(set); a_spamdoms = defaultdict(set)
    for L in links:
        a = L["anchor"] or ""
        a_links[a] += 1
        a_type[a] = L["anchor_type"]
        a_doms[a].add(L["refdomain"])
        if domains.get(L["refdomain"], {}).get("status", "").startswith("Spam"):
            a_spamdoms[a].add(L["refdomain"])
    rows = []
    for a in sorted(a_links, key=lambda x: -a_links[x]):
        rows.append([
            a, a_type[a], a_links[a], a_links[a] / total_links,
            len(a_doms[a]), len(a_spamdoms[a]),
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 5: Exact Match Anchors ----------
    ws = wb["Exact Match Anchors"]; NC = 7
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    seen = {}
    for L in links:
        if L["anchor_type"] in ("Exact match commercial", "Exact match commercial (geo)"):
            key = (L["refdomain"], (L["anchor"] or "").strip())
            if key not in seen:
                seen[key] = L
    rows = []
    for (d, anchor), L in sorted(seen.items(), key=lambda x: (x[0][0], x[0][1])):
        rows.append([
            d, L["source_url"], anchor, market_of(anchor),
            site_type(d, L.get("source_title", "")), None, None,  # input cells left blank
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 6: Pending Disavow Lines ----------
    ws = wb["Pending Disavow Lines"]; NC = 3
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    held = [v for v in doms if v["status"].startswith("Held")]
    rows = []
    for v in sorted(held, key=lambda v: v["domain"]):
        rows.append([
            v["domain"], "domain:" + v["domain"],
            f"Append only if the partner does not claim it, to {DISAVOW_FILE}",
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 7: Disavow List ----------
    ws = wb["Disavow List"]; NC = 7
    hdr, dsty, hh, dh = capture_styles(ws, NC)
    clear_data(ws)
    disavow = [v for v in doms if v["status"] == "Spam (Disavow)"]
    rows = []
    for v in sorted(disavow, key=lambda v: v["domain"]):
        rows.append([
            "domain:" + v["domain"], v.get("AS", 0), v["backlinks"], v.get("RDs"),
            v.get("organic_traffic", 0), v.get("organic_keywords", 0), v.get("top_anchor", ""),
        ])
    write_rows(ws, rows, dsty, dh, NC)

    # ---------- Tab 1: Summary (value edits, keep styles + logo) ----------
    ws = wb["Summary"]
    ws["B1"] = CLIENT_NAME
    # status table rows 4-10
    from collections import Counter
    sc = Counter(v["status"] for v in doms)
    bc = Counter()
    for v in doms:
        bc[v["status"]] += v["backlinks"]
    r = 4
    for s in STATUS_ORDER:
        ws.cell(row=r, column=1).value = s
        ws.cell(row=r, column=2).value = sc.get(s, 0)
        ws.cell(row=r, column=3).value = bc.get(s, 0)
        ws.cell(row=r, column=4).value = (sc.get(s, 0) / total_domains) if total_domains else 0
        ws.cell(row=r, column=5).value = STATUS_MEANING[s]
        r += 1
    ws.cell(row=10, column=1).value = "Total"
    ws.cell(row=10, column=2).value = total_domains
    ws.cell(row=10, column=3).value = total_links
    ws.cell(row=10, column=4).value = 1.0

    # key findings rows 12-18 (7)
    spam_dof = sc.get("Spam (Disavow)", 0)
    spam_nof = sc.get("Spam (Nofollow, No Action)", 0)
    spam_total = spam_dof + spam_nof
    held_total = sc.get("Held (Pending Partner)", 0) + sc.get("Held (Nofollow, No Action)", 0)
    # home vs deep — count the link-scheme flood vs commercial-anchor campaign
    SCHEME = ("Spam: keyword stuffed SEO sales copy", "Spam: off topic", "Naked URL")
    COMM = ("Exact match commercial", "Exact match commercial (geo)")
    scheme_home = sum(1 for L in links if L["anchor_type"] in SCHEME and not _deep(L["target_url"]))
    commercial_deep = sum(1 for L in links if L["anchor_type"] in COMM and _deep(L["target_url"]))
    commercial_total = sum(1 for L in links if L["anchor_type"] in COMM)
    # dominant salescopy anchor domains
    sales_doms = len({L["refdomain"] for L in links if L["anchor_type"] == "Spam: keyword stuffed SEO sales copy"})
    # top salescopy anchor
    from collections import Counter as C2
    sales_anchor_counter = C2(L["anchor"] for L in links if L["anchor_type"] == "Spam: keyword stuffed SEO sales copy")
    top_sales = sales_anchor_counter.most_common(1)[0] if sales_anchor_counter else ("", 0)
    top_sales_doms = len({L["refdomain"] for L in links if L["anchor"] == top_sales[0]}) if top_sales[0] else 0
    held_zero_traffic = sum(1 for v in doms if v["status"].startswith("Held") and (v.get("organic_traffic", 0) or 0) == 0)
    # aug vs now from history
    aug_rd, now_rd = 406, total_domains
    findings = [
        f"{spam_total:,} of the {total_domains:,} referring domains are spam. {spam_dof:,} have a dofollow link and go in the disavow file; the other {spam_nof:,} are nofollow and need no action.",
        f"The attack has roughly tripled since mid-2026: 406 referring domains in August 2026, {now_rd:,} now. We audited the full live profile, not an older snapshot.",
        f"You can upload one disavow file, for {CLIENT}. No owned domains redirect into the site, so a single file ({DISAVOW_FILE}) covers every bad domain.",
        f"Two patterns, easy to tell apart. {home_links:,} link-scheme links hit the home page; the commercial-anchor links hit deep location and service pages. The home-page flood is the attack.",
        f"The biggest single anchor, on {top_sales_doms:,} domains, is backlink sales copy that names the client's own domain.",
        f"{held_total:,} domains are held for the previous partner to confirm, in case any were paid placements.",
        f"Held does not mean good: {held_zero_traffic:,} of the {held_total:,} held domains have no organic traffic at all.",
    ]
    for i, f in enumerate(findings):
        ws.cell(row=12 + i, column=1).value = f

    # anchor profile table rows 21+
    at_links = Counter(); at_doms = defaultdict(set)
    for L in links:
        at_links[L["anchor_type"]] += 1
        at_doms[L["anchor_type"]].add(L["refdomain"])
    ordered = sorted(at_links, key=lambda x: -at_links[x])
    # capture style of row 21 (data) to clone for any extra rows
    base_style = [copy.copy(ws.cell(row=21, column=c)._style) for c in range(1, 5)]
    base_h = ws.row_dimensions[21].height
    # clear existing anchor rows 21..28
    for rr in range(21, 40):
        for c in range(1, 6):
            ws.cell(row=rr, column=c).value = None
    for i, t in enumerate(ordered):
        rr = 21 + i
        vals = [t, at_links[t], at_links[t] / total_links, len(at_doms[t])]
        for c in range(1, 5):
            cell = ws.cell(row=rr, column=c)
            cell.value = vals[c - 1]
            cell._style = copy.copy(base_style[c - 1])
        if base_h:
            ws.row_dimensions[rr].height = base_h

    os.makedirs(OUT, exist_ok=True)
    outpath = os.path.join(OUT, "Jaco_Contracting_Backlinks_Audit.xlsx")
    wb.save(outpath)

    # ---------- disavow file ----------
    write_disavow(disavow)

    print("wrote", outpath)
    print("domains:", total_domains, "links:", total_links)
    print("status counts:", dict(sc))
    print("disavow domains:", len(disavow), "held:", held_total)
    return domains, links, disavow, held


def write_disavow(disavow):
    """Write disavow_jacocontracting.txt grouped by reason, with a header."""
    from collections import defaultdict
    groups = defaultdict(list)
    group_label = {
        "off-topic (gambling/pharma/adult/telegram) spam anchor": "Off-topic spam (gambling / pharma / adult / malicious)",
        "keyword-stuffed SEO/PBN sales-copy anchor": "PBN / link-scheme sales-copy anchors",
        "link-network / directory / backlink-marketplace host name": "Link-network / directory / backlink-marketplace hosts",
        "spam page title (backlink marketplace / domain list / PBN template)": "Backlink-marketplace / domain-list page templates",
    }
    for v in disavow:
        lbl = group_label.get(v.get("reason", ""), "Other confirmed spam (link evidence)")
        groups[lbl].append(v["domain"])
    total = len(disavow)
    lines = []
    lines.append(f"# Disavow file for {CLIENT} (Google Search Console property: {CLIENT})")
    lines.append(f"# Generated {datetime.date.today().isoformat()} — {total} domains, all confirmed spam with at least one dofollow link.")
    lines.append("#")
    lines.append("# IMPORTANT — DO NOT UPLOAD until the previous SEO partner has confirmed the Held set.")
    lines.append("#   Held (Pending Partner) domains are NOT in this file. They carry exact-match")
    lines.append("#   commercial anchors or deep-page links that may have been commissioned. Confirm")
    lines.append("#   with the business/partner first; append any the partner does not claim from")
    lines.append("#   the 'Pending Disavow Lines' tab.")
    lines.append("#")
    lines.append("# This is the only disavow file for this client: no owned domains 301-redirect into")
    lines.append(f"#   {CLIENT}, so one file for the {CLIENT} property covers the whole profile.")
    lines.append("#")
    lines.append("# NOTE: Confirm with the client whether a disavow file already exists on this Search")
    lines.append("#   Console property. If one exists, uploading REPLACES it — merge first. If the")
    lines.append("#   client has checked and there is none, this is the first file.")
    lines.append("#")
    lines.append("# Each line disavows the referring (source) domain; domain: covers its subdomains.")
    lines.append("")
    for lbl in sorted(groups):
        ds = sorted(set(groups[lbl]))
        lines.append(f"# --- {lbl} ({len(ds)}) ---")
        for d in ds:
            lines.append(f"domain:{d}")
        lines.append("")
    path = os.path.join(OUT, DISAVOW_FILE)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip("\n") + "\n")
    print("wrote", path, "(", total, "domains )")


def _deep(target_url):
    u = (target_url or "").lower().split("//", 1)[-1].replace("www.", "").rstrip("/")
    if not u.startswith(CLIENT):
        return False
    return u[len(CLIENT):] not in ("", "/")


if __name__ == "__main__":
    main()
