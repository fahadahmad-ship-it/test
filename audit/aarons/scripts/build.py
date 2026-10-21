"""
Build the Harbinger-format workbook + disavow file(s) for the aaronshometech.com
audit. Follows AUDIT_FORMAT.md exactly (the signed-off format; where its styling
differs from older notes in the playbook, AUDIT_FORMAT.md wins). Seven tabs, in
order: Summary, Referring Domain Audit, All Backlinks, Anchor Analysis,
Exact Match Anchors, Pending Disavow Lines, Disavow List.

Run: python3 -I scripts/build.py data/classified.json scripts/config.py \
        data/anchors_0.csv out/Aarons_Home_Tech_Backlink_Audit.xlsx out/
"""
import sys, os, json, glob, csv, html, datetime, importlib.util, re
from collections import Counter, defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ACCENT = "FF0C343D"
WHITE = "FFFFFFFF"
FONT = "Geist"

def load_cfg(p):
    spec = importlib.util.spec_from_file_location("config", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def load_anchortype(p="scripts/anchortype.py"):
    spec = importlib.util.spec_from_file_location("anchortype", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

# ---------- styling ----------
THIN = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HDR_FONT = Font(name=FONT, size=9, bold=True, color=WHITE)
HDR_FILL = PatternFill("solid", fgColor=ACCENT)
HDR_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
DATA_FONT = Font(name=FONT, size=9, color="FF000000")
DATA_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=False)
DATA_ALIGN_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)
INPUT_FONT = Font(name=FONT, size=9, color=WHITE)
INPUT_FILL = PatternFill("solid", fgColor=ACCENT)

def ts_to_date(ts):
    try:
        ts = int(ts)
        if ts <= 0: return ""
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return ""

def write_header(ws, headers, row=1, start_col=2):
    for j, h in enumerate(headers):
        c = ws.cell(row=row, column=start_col + j, value=h)
        c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = HDR_ALIGN; c.border = BORDER
    ws.row_dimensions[row].height = 31.5

def write_row(ws, values, row, start_col=2, height=22.5, input_cols=()):
    for j, v in enumerate(values):
        c = ws.cell(row=row, column=start_col + j, value=v)
        if j in input_cols:
            c.font = INPUT_FONT; c.fill = INPUT_FILL
        else:
            c.font = DATA_FONT
        c.alignment = DATA_ALIGN; c.border = BORDER
    ws.row_dimensions[row].height = height

def finalize_data_tab(ws, nrows, ncols, start_col=2, header_row=1):
    first = get_column_letter(start_col)
    last = get_column_letter(start_col + ncols - 1)
    rng = f"{first}{header_row}:{last}{header_row + nrows}"
    ws.auto_filter.ref = rng
    ws.freeze_panes = f"{get_column_letter(start_col)}{header_row + 1}"
    ws.sheet_view.showGridLines = True
    ws.column_dimensions["A"].width = 2.5

# ---------- metrics ----------
def load_metrics(base):
    cmp_map, rank_map = {}, {}
    for p in glob.glob(os.path.join(base, "metrics", "*cmp*.csv")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = html.unescape(line.strip())
                if not line or line.startswith("target;"): continue
                parts = line.split(";")
                if len(parts) < 4: continue
                d = parts[0].strip().lower()
                try:
                    cmp_map[d] = {"as": int(parts[1]), "backlinks": int(parts[2]),
                                  "rds": int(parts[3])}
                except ValueError:
                    continue
    for p in glob.glob(os.path.join(base, "metrics", "*rank*.csv")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = html.unescape(line.strip())
                if not line or line.lower().startswith("domain;"): continue
                parts = line.split(";")
                if len(parts) < 4: continue
                d = parts[0].strip().lower()
                # domain;rank;organic_keywords;organic_traffic;...
                try:
                    rank_map[d] = {"organic_keywords": int(parts[2]),
                                   "organic_traffic": int(parts[3])}
                except (ValueError, IndexError):
                    continue
    return cmp_map, rank_map

# ---------- disavow set / redundancy ----------
def build_disavow_set(domains, cfg):
    spam = {d: r for d, r in domains.items()
            if r["status"] == "Spam (Disavow)" and r["has_dofollow"]}
    # drop redundant children (parent also in set covers subdomains)
    keys = set(spam.keys())
    redundant = set()
    for d in spam:
        labels = d.split(".")
        for i in range(1, len(labels) - 1):
            parent = ".".join(labels[i:])
            if parent in keys:
                redundant.add(d); break
    final = {d: r for d, r in spam.items() if d not in redundant}
    return final, redundant

# ---------- main build ----------
def main():
    classified = sys.argv[1]; cfg = load_cfg(sys.argv[2])
    anchors_csv = sys.argv[3]; out_xlsx = sys.argv[4]
    out_dir = sys.argv[5] if len(sys.argv) > 5 else "out"
    base = os.path.dirname(os.path.dirname(anchors_csv)) or "."
    base = "data"
    AT = load_anchortype()

    data = json.load(open(classified, encoding="utf-8"))["domains"]
    cmp_map, rank_map = load_metrics(base)
    doms = list(data.values())

    def as_of(r):
        d = r["domain"]
        return cmp_map.get(d, {}).get("as", r.get("domain_ascore", 0))
    def own_backlinks(r):
        return cmp_map.get(r["domain"], {}).get("backlinks", "")
    def own_rds(r):
        return cmp_map.get(r["domain"], {}).get("rds", "")
    def traffic(r):
        return rank_map.get(r["domain"], {}).get("organic_traffic", "")
    def okw(r):
        return rank_map.get(r["domain"], {}).get("organic_keywords", "")

    disavow, redundant = build_disavow_set(data, cfg)
    disavow_domains = set(disavow.keys())

    wb = openpyxl.Workbook()

    # ============ TAB 1: SUMMARY ============
    ws = wb.active; ws.title = "Summary"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2.5
    for col, w in zip("BCDE", (34, 18, 20, 22)):
        ws.column_dimensions[col].width = w
    ws.merge_cells("B1:E2")
    t = ws.cell(row=1, column=2, value=cfg.CLIENT_NAME + " — Backlink Audit & Disavow Review")
    t.font = Font(name=FONT, size=9, bold=True, color=ACCENT)
    t.alignment = Alignment(horizontal="left", vertical="center")
    ws.cell(row=3, column=2, value="Prepared by Harbinger Marketing").font = Font(name=FONT, size=9, color=ACCENT)
    ws.cell(row=4, column=2, value="Date: " + datetime.date.today().strftime("%Y-%m-%d")).font = Font(name=FONT, size=9, color="FF000000")
    ws.cell(row=5, column=2, value="Money site: " + cfg.MONEY_SITE).font = Font(name=FONT, size=9, color="FF000000")

    # status table
    counts = Counter(r["status"] for r in doms)
    order = ["Spam (Disavow)", "Spam (Nofollow, No Action)", "Held (Pending Partner)",
             "Held (Nofollow, No Action)", "Keep", "Own Site"]
    hr = 7
    for j, h in enumerate(["Status", "Referring domains", "In disavow file"]):
        c = ws.cell(row=hr, column=2 + j, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color=WHITE); c.fill = HDR_FILL
        c.alignment = HDR_ALIGN; c.border = BORDER
    ws.row_dimensions[hr].height = 22.5
    rr = hr
    for st in order:
        rr += 1
        n = counts.get(st, 0)
        indis = len(disavow) if st == "Spam (Disavow)" else 0
        for j, v in enumerate([st, n, (indis if st == "Spam (Disavow)" else "")]):
            c = ws.cell(row=rr, column=2 + j, value=v)
            c.font = DATA_FONT; c.alignment = DATA_ALIGN; c.border = BORDER
        ws.row_dimensions[rr].height = 22.5
    rr += 1
    for j, v in enumerate(["Total referring domains", len(doms), len(disavow)]):
        c = ws.cell(row=rr, column=2 + j, value=v)
        c.font = Font(name=FONT, size=9, bold=True); c.alignment = DATA_ALIGN; c.border = BORDER
    ws.row_dimensions[rr].height = 22.5

    # key findings
    kf_row = rr + 2
    kc = ws.cell(row=kf_row, column=2, value="Key findings")
    kc.font = Font(name=FONT, size=10, bold=True, color=ACCENT)
    findings = compute_findings(doms, data, disavow, cmp_map, rank_map, cfg, counts)
    for i, f in enumerate(findings, 1):
        c = ws.cell(row=kf_row + i, column=2, value=f"{i}. {f}")
        c.font = Font(name=FONT, size=9, color="FF000000")
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.merge_cells(start_row=kf_row + i, start_column=2, end_row=kf_row + i, end_column=5)
        ws.row_dimensions[kf_row + i].height = 30
    for r in range(1, kf_row + len(findings) + 2):
        if ws.row_dimensions[r].height is None:
            ws.row_dimensions[r].height = 22.5

    # ============ TAB 2: REFERRING DOMAIN AUDIT ============
    ws = wb.create_sheet("Referring Domain Audit")
    hdrs = ["Domain", "Status", "AS", "Backlinks", "RD's", "Traffic", "In Disavow",
            "Links Point To", "Dofollow Links", "Nofollow Links", "First Seen",
            "Top Anchor Text", "Example Linking Page", "Linking Page Title",
            "Source", "IP", "Disavow Line"]
    write_header(ws, hdrs)
    rank_sort = {"Spam (Disavow)": 0, "Held (Pending Partner)": 1,
                 "Held (Nofollow, No Action)": 2, "Spam (Nofollow, No Action)": 3,
                 "Keep": 4, "Own Site": 5}
    doms_sorted = sorted(doms, key=lambda r: (rank_sort.get(r["status"], 9),
                                              -as_of(r), r["domain"]))
    for i, r in enumerate(doms_sorted, start=2):
        links = r.get("links", [])
        df = sum(1 for l in links if not l["nofollow"])
        nf = sum(1 for l in links if l["nofollow"])
        ex = r.get("example", {}) or {}
        indis = "Yes" if r["domain"] in disavow_domains else ("Redundant" if r["domain"] in redundant else "No")
        line = f"domain:{r['domain']}" if r["domain"] in disavow_domains else ""
        write_row(ws, [
            r["domain"], r["status"], as_of(r), own_backlinks(r), own_rds(r), traffic(r),
            indis, r.get("points_to", ""), df, nf, ts_to_date(r.get("first_seen")),
            (r.get("top_anchor", "") or "")[:200],
            (ex.get("source_url", "") or "")[:200],
            (ex.get("source_title", "") or "")[:200],
            "Semrush", r.get("ip", ""), line,
        ], i, height=15.75)
    finalize_data_tab(ws, len(doms_sorted), len(hdrs))
    for col, w in zip("BCDEFGHIJKLMNOPQR",
                      (30, 24, 5, 10, 8, 9, 10, 16, 11, 11, 12, 34, 44, 40, 9, 15, 26)):
        ws.column_dimensions[col].width = w

    # ============ TAB 3: ALL BACKLINKS ============
    ws = wb.create_sheet("All Backlinks")
    hdrs = ["Referring Domain", "Status", "Tool", "Anchor Text", "Anchor Type",
            "Link Type", "Linking Page URL", "Linking Page Title", "Target URL"]
    write_header(ws, hdrs)
    row = 2
    all_links = []
    for r in doms_sorted:
        for l in r.get("links", []):
            all_links.append((r, l))
    for r, l in all_links:
        write_row(ws, [
            r["domain"], r["status"], "Semrush",
            (l.get("anchor", "") or "")[:300],
            AT.anchor_type(l.get("anchor", ""), cfg, l.get("target_url", "")),
            "Nofollow" if l["nofollow"] else "Dofollow",
            (l.get("source_url", "") or "")[:300],
            (l.get("source_title", "") or "")[:300],
            (l.get("target_url", "") or "")[:300],
        ], row, height=22.5)
        row += 1
    finalize_data_tab(ws, len(all_links), len(hdrs))
    for col, w in zip("BCDEFGHIJ", (28, 22, 9, 40, 22, 10, 46, 42, 40)):
        ws.column_dimensions[col].width = w

    # ============ TAB 4: ANCHOR ANALYSIS ============
    ws = wb.create_sheet("Anchor Analysis")
    hdrs = ["Anchor Text", "Anchor Type", "Backlinks", "Share of Backlinks",
            "Referring Domains", "Spam Domains Using It"]
    write_header(ws, hdrs)
    anchors = read_anchor_csv(anchors_csv)
    total_bl = sum(a["backlinks_num"] for a in anchors) or 1
    # spam-domains-using-anchor from evidence
    anchor_spam = defaultdict(set)
    anchor_any = defaultdict(set)
    for r in doms:
        is_spam = r["status"].startswith("Spam")
        for l in r.get("links", []):
            a = (l.get("anchor", "") or "").strip().lower()
            anchor_any[a].add(r["domain"])
            if is_spam:
                anchor_spam[a].add(r["domain"])
    anchors.sort(key=lambda a: -a["backlinks_num"])
    for i, a in enumerate(anchors, start=2):
        key = a["anchor"].strip().lower()
        spam_using = len(anchor_spam.get(key, set()))
        write_row(ws, [
            a["anchor"][:300], AT.anchor_type(a["anchor"], cfg),
            a["backlinks_num"], round(a["backlinks_num"] / total_bl, 4),
            a["domains_num"], spam_using if spam_using else "",
        ], i, height=22.5)
    finalize_data_tab(ws, len(anchors), len(hdrs))
    for col, w in zip("BCDEFG", (60, 24, 11, 15, 16, 18)):
        ws.column_dimensions[col].width = w
    # share-of-backlinks as percent
    for i in range(2, len(anchors) + 2):
        ws.cell(row=i, column=5).number_format = "0.00%"

    # ============ TAB 5: EXACT MATCH ANCHORS ============
    ws = wb.create_sheet("Exact Match Anchors")
    hdrs = ["Referring domain", "Example backlink (linking page)",
            "Exact-match commercial anchor", "Market", "Site type (indicative)",
            "Partner confirmed? (Y/N)", "Final decision"]
    write_header(ws, hdrs)
    em_rows = build_exact_match_rows(doms, cfg, AT)
    for i, em in enumerate(em_rows, start=2):
        write_row(ws, em, i, height=22.5, input_cols=(5, 6))
    finalize_data_tab(ws, len(em_rows), len(hdrs))
    for col, w in zip("BCDEFGH", (28, 46, 40, 18, 22, 18, 24)):
        ws.column_dimensions[col].width = w

    # ============ TAB 6: PENDING DISAVOW LINES ============
    ws = wb.create_sheet("Pending Disavow Lines")
    hdrs = ["Referring domain", "Disavow line (append to disavow.txt once confirmed)",
            "Recommendation"]
    write_header(ws, hdrs)
    held = [r for r in doms_sorted if r["status"] == "Held (Pending Partner)"]
    for i, r in enumerate(held, start=2):
        rec = ("Hold — exact-match commercial/deep-page link; confirm with the previous "
               "supplier (partner) whether commissioned. Disavow only if not commissioned.")
        write_row(ws, [r["domain"], f"domain:{r['domain']}", rec], i, height=22.5)
    finalize_data_tab(ws, len(held), len(hdrs))
    for col, w in zip("BCD", (30, 42, 80)):
        ws.column_dimensions[col].width = w

    # ============ TAB 7: DISAVOW LIST ============
    ws = wb.create_sheet("Disavow List")
    hdrs = ["Disavow Line", "AS", "Backlinks", "RD's", "Traffic",
            "Organic Keywords", "Top Anchor Text"]
    write_header(ws, hdrs)
    dis_sorted = sorted(disavow.values(), key=lambda r: (-as_of(r), r["domain"]))
    for i, r in enumerate(dis_sorted, start=2):
        write_row(ws, [
            f"domain:{r['domain']}", as_of(r), own_backlinks(r), own_rds(r),
            traffic(r), okw(r), (r.get("top_anchor", "") or "")[:200],
        ], i, height=22.5)
    finalize_data_tab(ws, len(dis_sorted), len(hdrs))
    for col, w in zip("BCDEFGH", (40, 6, 11, 8, 9, 15, 44)):
        ws.column_dimensions[col].width = w

    os.makedirs(os.path.dirname(out_xlsx), exist_ok=True)
    wb.save(out_xlsx)
    sys.stderr.write(f"[build] wrote {out_xlsx}\n")

    # ============ DISAVOW FILE(S) ============
    write_disavow_file(os.path.join(out_dir, "disavow_aaronshometech.com.txt"),
                       disavow, as_of, cfg)

    # counts for the operator
    sys.stderr.write(f"[build] referring domains={len(doms)} "
                     f"disavow(lines)={len(disavow)} redundant={len(redundant)} "
                     f"held={len(held)} all_backlink_rows={len(all_links)} "
                     f"anchors={len(anchors)} exact_match_rows={len(em_rows)}\n")


def read_anchor_csv(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            line = html.unescape(line.rstrip("\n").rstrip("\r"))
            if not line: continue
            parts = line.split(";")
            if i == 0 and parts[0] == "anchor": continue
            if len(parts) != 5: continue
            try:
                out.append({"anchor": parts[0], "domains_num": int(parts[1]),
                            "backlinks_num": int(parts[2])})
            except ValueError:
                continue
    return out


def _market(anchor, cfg):
    a = anchor.lower()
    cities = {"atlanta": "Atlanta, GA", "greensboro": "Greensboro, GA",
              "senoia": "Senoia, GA", "roswell": "Roswell, GA", "decatur": "Decatur, GA",
              "marietta": "Marietta, GA", "johns creek": "Johns Creek, GA",
              "smyrna": "Smyrna, GA", "sandy springs": "Sandy Springs, GA",
              "vinings": "Vinings, GA", "brookhaven": "Brookhaven, GA",
              "peachtree city": "Peachtree City, GA", "eatonton": "Eatonton, GA",
              "chattahoochee hills": "Chattahoochee Hills, GA",
              "fayetteville": "Fayetteville, GA", "highlands": "Highlands, NC"}
    for k, v in cities.items():
        if k in a: return v
    return "GA (metro Atlanta)"

def _site_type(domain, title):
    d = domain.lower(); t = (title or "").lower()
    if any(x in d for x in ("directory", "listing", "listings", "local", "biz")): return "Business directory"
    if any(x in d or x in t for x in ("press", "pr ", "news", "einpresswire", "newswire")): return "Press release"
    if any(x in d for x in ("blog", "article", "articles")): return "Blog / article"
    return "Directory / blog (indicative)"

def build_exact_match_rows(doms, cfg, AT):
    rows = []
    for r in doms:
        # list exact-match commercial anchors on this domain (dedup)
        seen = set()
        for l in r.get("links", []):
            a = (l.get("anchor", "") or "").strip()
            t = AT.anchor_type(a, cfg, l.get("target_url", ""))
            if t.startswith("Exact-match commercial") and a.lower() not in seen:
                seen.add(a.lower())
                rows.append([r["domain"], (l.get("source_url", "") or "")[:200], a[:200],
                             _market(a, cfg), _site_type(r["domain"], l.get("source_title", "")),
                             "", ""])
    rows.sort(key=lambda x: x[0])
    return rows


def compute_findings(doms, data, disavow, cmp_map, rank_map, cfg, counts):
    n = len(doms)
    spam_dis = counts.get("Spam (Disavow)", 0)
    spam_nf = counts.get("Spam (Nofollow, No Action)", 0)
    held = counts.get("Held (Pending Partner)", 0) + counts.get("Held (Nofollow, No Action)", 0)
    keep = counts.get("Keep", 0)
    own = counts.get("Own Site", 0)
    # dofollow/nofollow among analyzed links
    df = nf = 0
    home = deep = 0
    for r in doms:
        for l in r.get("links", []):
            if l["nofollow"]: nf += 1
            else: df += 1
            tu = (l.get("target_url", "") or "").lower()
            tu2 = re.sub(r"^https?://(www\.)?", "", tu)
            if tu2.rstrip("/") == "aaronshometech.com": home += 1
            elif tu2.startswith("aaronshometech.com/"): deep += 1
    f = []
    f.append(f"The profile holds {n:,} referring domains. {len(disavow):,} are confirmed spam with at "
             f"least one dofollow link and go in the disavow file; a further {spam_nf:,} are spam but "
             f"link only via nofollow, so they pass nothing and need no action.")
    f.append("This is an active negative-SEO / link-seller flood: Semrush shows referring domains rising "
             "from ~900 a year ago to 1,699 last month to 5,399 now, while Authority Score fell from 28 "
             "(2022) to 10. No client brief figure was supplied, so the full live profile was audited.")
    f.append("One disavow file is prepared, for the aaronshometech.com Search Console property, and it "
             "carries the full union of bad domains. aaronssystems.com and aaronssecurity.com redirect "
             "into the profile and are pending the client's confirmation of ownership and upload access.")
    f.append(f"Two campaigns are visible by target page: the spam flood points almost entirely at the home "
             f"page ({home:,} of analyzed links), while a smaller, older, commissioned-looking set points "
             f"at deep /services/ and /location/ money pages ({deep:,}).")
    f.append("The dominant anchors are a single link vendor's PBN sales copy — 'premium pbn backlinks', "
             "'high quality dofollow backlinks DA 50 PA 40 … buy backlinks online cheap', niche-edit and "
             "emoji testimonial text — the same network also selling links to unrelated businesses.")
    f.append(f"{held:,} domains are held for the previous supplier (partner) to confirm: these carry exact-match "
             f"commercial (geo) anchors or links to deep money pages and may be commissioned placements. They "
             f"are kept out of the disavow file until confirmed.")
    f.append("Held does not mean valuable. It means the link may have been paid for and must be confirmed "
             "before removal; many held domains are themselves low-authority and may still be disavowed once "
             "the supplier conversation rules out a commission.")
    return f[:7]


def write_disavow_file(path, disavow, as_of, cfg):
    # group by reason
    groups = defaultdict(list)
    for d, r in disavow.items():
        g = r.get("spam_group") or "pbn"
        groups[g].append(d)
    total = len(disavow)
    label = {"pbn": "PBN / link-service sales-copy spam (dofollow)",
             "off_topic": "Off-topic spam (dofollow)",
             "host": "Link-farm / directory host signature (dofollow)"}
    lines = []
    lines.append(f"# Disavow file for {cfg.MONEY_SITE} (Google Search Console property)")
    lines.append(f"# Prepared by Harbinger Marketing — {datetime.date.today().isoformat()}")
    lines.append(f"# {total} domains. One domain: line each; a domain: line also covers its subdomains.")
    lines.append("# SCOPE: this file is the full UNION of bad domains for the money site. Owned domains")
    lines.append("#   aaronssystems.com and aaronssecurity.com 301 into this profile; their bad links are")
    lines.append("#   folded in here (one file). If the client has Search Console access to those")
    lines.append("#   properties, separate per-property files can be produced on request.")
    lines.append("# HELD links are NOT in this file. Exact-match commercial and deep-money-page links that")
    lines.append("#   may be commissioned are held for the previous SEO supplier (the 'partner' on the")
    lines.append("#   sheet; the client's brief calls this role the 'supplier') to confirm first.")
    lines.append("# DO NOT UPLOAD before that supplier conversation. Uploading REPLACES any existing")
    lines.append("#   disavow file on the property — confirm with the client whether one already exists")
    lines.append("#   (none was supplied for this audit).")
    lines.append("")
    for g in ("pbn", "off_topic", "host"):
        if not groups.get(g): continue
        lines.append(f"# --- {label[g]}: {len(groups[g])} domains ---")
        for d in sorted(groups[g]):
            lines.append(f"domain:{d}")
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    sys.stderr.write(f"[build] wrote {path} ({total} domain lines)\n")


if __name__ == "__main__":
    main()
