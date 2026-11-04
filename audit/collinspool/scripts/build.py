"""
Build the New Garden backlink audit workbook + disavow file.
Follows AUDIT_FORMAT.md (7 tabs, columns, statuses) and the playbook.

Data sources:
  Semrush backlinks   -> data/fetch/bl_*.csv
  Semrush refdomains  -> data/rd/rd_*.csv           (AS, ip, country, first_seen)
  Ahrefs refdomains   -> data/rd/ahrefs_refdomains.json   (is_spam, DR, discovery)
  Ahrefs backlinks    -> data/fetch/ahrefs_backlinks.json (http_code, discovery)

Per playbook principle 1, every METRIC (AS, backlinks) is Semrush. Ahrefs only
discovers missed links and corroborates (is_spam) + supplies http_code.

Note (documented deviations, no signed template/logo available):
  - Authority Score = Semrush refdomains domain_ascore (not backlinks_comparison).
  - Font Geist named but may not be installed in this environment.
  - No Harbinger logo asset supplied; Summary logo cell left as a text placeholder.
  - Border/title-size spec differs between AUDIT_FORMAT.md and the playbook; see
    BUILD_NOTES.md. Header-row borders + gridlines used (playbook section 8/12).
"""
import sys, os, json, datetime, re
from collections import Counter, defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from load import load_glob, truthy
import classify as C

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = "audit/collinspool"
OUT = f"{ROOT}/out"
ACCENT = "FF0C343D"
FONT = "Geist"
TODAY = datetime.date.today().isoformat()

# Tab-08 flagged domains (the brief's 76), if present, for the overlap finding.
try:
    TAB08 = [l.strip().lower() for l in open(f"{ROOT}/data/tab08.txt") if l.strip()]
except FileNotFoundError:
    TAB08 = []

# ------------------------------------------------------------------ helpers
def ts_to_date(v):
    try:
        return datetime.datetime.utcfromtimestamp(int(v)).strftime("%Y-%m-%d")
    except Exception:
        return ""

def canon(url):
    u = re.sub(r"^\w+://", "", (url or "").strip().lower())
    u = re.sub(r"^www\.", "", u)
    return u.rstrip("/")

def as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default

# ------------------------------------------------------------------ load
def load_all():
    _, bl, bl_rej = load_glob(f"{ROOT}/data/fetch/bl_*.csv")
    _, rd, rd_rej = load_glob(f"{ROOT}/data/rd/rd_*.csv")
    ah_rd = json.load(open(f"{ROOT}/data/rd/ahrefs_refdomains.json")).get("refdomains", [])
    try:
        ah_bl = json.load(open(f"{ROOT}/data/fetch/ahrefs_backlinks.json")).get("backlinks", [])
    except Exception:
        ah_bl = []
    return bl, rd, ah_rd, ah_bl, len(bl_rej), len(rd_rej)

def build():
    bl, rd, ah_rd, ah_bl, bl_rej, rd_rej = load_all()
    os.makedirs(OUT, exist_ok=True)

    # refdomain metrics by root domain
    rdm = {}
    for r in rd:
        rdm[r["domain"].lower()] = r
    # ahrefs corroboration by root
    ah_spam, ah_dr = {}, {}
    for a in ah_rd:
        d = C.root_of(a["domain"].lower())
        ah_spam[d] = ah_spam.get(d, False) or bool(a.get("is_spam"))
        ah_dr[d] = max(ah_dr.get(d, 0.0), float(a.get("domain_rating") or 0))
    ah_http = {}
    ah_links_by_dom = defaultdict(list)
    for a in ah_bl:
        d = C.root_of(C.host_of(a.get("url_from")))
        ah_http[canon(a.get("url_from"))] = a.get("http_code")
        ah_links_by_dom[d].append(a)

    # ---- build link records, dedupe, group by referring root domain ----
    seen = set()
    by_dom = defaultdict(list)
    for r in bl:
        src = r["source_url"]; dom = C.root_of(C.host_of(src))
        key = (canon(src), canon(r["target_url"]), (r["anchor"] or "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        rec = dict(
            source_url=src, source_title=r.get("source_title", ""),
            target_url=r["target_url"], redirect_url=r.get("redirect_url", ""),
            anchor=r.get("anchor", ""), nofollow=r.get("nofollow", "false"),
            response_code=r.get("response_code", ""),
            first_seen=r.get("first_seen", ""),
            fsd=ts_to_date(r.get("first_seen")), tool="Semrush",
        )
        by_dom[dom].append(rec)
    # add Ahrefs-only links (discovery)
    ahrefs_only = 0
    for d, links in ah_links_by_dom.items():
        for a in links:
            key = (canon(a.get("url_from")), canon(a.get("url_to")),
                   (a.get("anchor") or "").strip().lower())
            if key in seen:
                continue
            seen.add(key); ahrefs_only += 1
            dom = C.root_of(C.host_of(a.get("url_from")))
            afs = (a.get("first_seen") or "")
            by_dom[dom].append(dict(
                source_url=a.get("url_from"), source_title="",
                target_url=a.get("url_to"), redirect_url="",
                anchor=a.get("anchor", ""),
                nofollow="false" if a.get("is_dofollow") else "true",
                response_code=a.get("http_code", ""),
                first_seen=afs, fsd=afs[:10], tool="Ahrefs",
            ))

    # Playbook section 6: a referring domain that carries no link of its own is
    # not a referring site. We only keep domains with >=1 captured link, so no
    # setdefault union here (refdomain metrics still attach via rdm lookup).

    # ip /24 groups for rule 11
    ip24 = Counter()
    for d, meta in rdm.items():
        ip = (meta.get("ip") or "")
        if ip.count(".") == 3:
            ip24["/".join(ip.split(".")[:3])] += 1
    CDN_IPS = ("104.21.", "172.67.", "172.64.", "104.16.", "104.18.")

    # ---- classify every domain ----
    domains = {}
    for d, links in by_dom.items():
        meta = rdm.get(d, {})
        try:
            asv = int(meta.get("domain_ascore")) if meta.get("domain_ascore") not in (None, "") else None
        except Exception:
            asv = None
        ip = meta.get("ip") or ""
        slash24 = "/".join(ip.split(".")[:3]) if ip.count(".") == 3 else ""
        grp = ip24.get(slash24, 0)
        cdn = any(ip.startswith(p) for p in CDN_IPS)
        res = C.classify_domain(d, links, asv if asv is not None else 0,
                                ip_group_size=grp, cdn_ip=cdn)
        # ahrefs is_spam corroboration only (never sole basis) -> already evidence-based
        domains[d] = dict(res=res, links=links, meta=meta, asv=asv,
                          ah_spam=ah_spam.get(d, False), ah_dr=ah_dr.get(d))
    return domains, dict(bl=len(bl), bl_rej=bl_rej, rd=len(rd), rd_rej=rd_rej,
                         ah_rd=len(ah_rd), ah_bl=len(ah_bl), ahrefs_only=ahrefs_only,
                         links_total=len(seen))

# ------------------------------------------------------------------ anchors
def market_of(anchor):
    al = (anchor or "").lower()
    if "alpharetta" in al: return "Alpharetta"
    if "marietta" in al: return "Marietta"
    if "atlanta" in al: return "Atlanta"
    for g in ["roswell","sandy springs","johns creek","kennesaw","smyrna","decatur"]:
        if g in al: return g.title()
    if " ga" in al or ", ga" in al or "georgia" in al: return "GA (other)"
    return "Non-geo"

# ------------------------------------------------------------------ styling
# Exact column widths read from the signed sample (NewGarden). Same column
# structure, so applied by letter to match the template cell-for-cell.
SAMPLE_WIDTHS = {
    "Summary": {"A":38.86,"B":16.29,"C":17.57,"D":18.71,"E":120.0},
    "Referring Domain Audit": {"A":36.0,"B":24.71,"C":9.57,"D":13.0,"E":9.43,"F":9.71,
        "G":12.43,"H":21.29,"I":14.0,"J":8.71,"K":12.0,"L":45.0,"M":8.71,"N":40.0,
        "O":14.0,"P":15.0,"Q":14.0},
    "All Backlinks": {"A":25.43,"B":27.14,"C":14.71,"D":55.0,"E":32.0,"F":10.0,
        "G":55.0,"H":53.14,"I":30.57},
    "Anchor Analysis": {"A":115.86,"B":37.71,"C":14.0,"D":8.71,"E":13.0,"F":20.29},
    "Exact Match Anchors": {"A":25.43,"B":59.0,"C":53.14,"D":16.0,"E":24.57,"F":15.43,"G":15.0},
    "Pending Disavow Lines": {"A":32.0,"B":44.0,"C":48.0},
    "Disavow List": {"A":44.0,"B":14.0,"C":15.57,"D":14.0,"E":11.14,"F":14.86,"G":98.86},
}

# Columns (1-indexed) the sample centres horizontally, per tab. All data cells
# are vertically centred; listed columns are also horizontally centred, the rest
# left-aligned (horizontal=None) - read from the signed sample.
CENTER_COLS = {
    "Referring Domain Audit": {3,4,5,6,7,8,9,10,11,15,16},
    "All Backlinks": {3,6},
    "Anchor Analysis": {3,4,5,6},
    "Exact Match Anchors": {4,6},
    "Pending Disavow Lines": set(),
    "Disavow List": {2,3,4,5,6},
}

def style_workbook(wb, data_tabs):
    thin = Side(style="thin", color="FFD9D9D9")
    hdr_fill = PatternFill("solid", fgColor=ACCENT)
    white_fill = PatternFill("solid", fgColor="FFFFFFFF")
    hdr_font = Font(name=FONT, size=9, bold=True, color="FFFFFFFF")
    data_font = Font(name=FONT, size=9, color="FF000000")
    hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ctr = Alignment(horizontal="center", vertical="center")
    lft = Alignment(vertical="center")
    for name, nrows, ncols, rowh in data_tabs:
        ws = wb[name]
        center = CENTER_COLS.get(name, set())
        # header row: accent fill, bold white, thin border all round, height 31.5
        for c in range(1, ncols + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = hdr_align
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws.row_dimensions[1].height = 31.5
        # data cells: Geist 9 black on white, per-column alignment, no border/height
        for rr in range(2, nrows + 1):
            for c in range(1, ncols + 1):
                cl = ws.cell(row=rr, column=c)
                cl.font = data_font; cl.fill = white_fill
                cl.alignment = ctr if c in center else lft
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = f"A1:{get_column_letter(ncols)}{max(nrows,1)}"
        # gridlines left at default (sample does not override) -> do not set
        for L, w in SAMPLE_WIDTHS.get(name, {}).items():
            ws.column_dimensions[L].width = w

# Number formats read from the signed sample, applied by column header.
NUMFMT = {
    "Referring Domain Audit": {"Backlinks":"#,##0","RD's":"#,##0","Traffic":"#,##0",
                                "First Seen":"d mmm yyyy"},
    "Anchor Analysis": {"Backlinks":"#,##0","Share of Backlinks":"0.00%"},
    "Disavow List": {"Backlinks":"#,##0","RD's":"#,##0","Traffic":"#,##0",
                      "Organic Keywords":"#,##0"},
}

def apply_numfmts(wb):
    for t, cols in NUMFMT.items():
        ws = wb[t]
        hdr = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column+1)]
        for name, fmt in cols.items():
            if name in hdr:
                ci = hdr.index(name) + 1
                for r in range(2, ws.max_row+1):
                    ws.cell(row=r, column=ci).number_format = fmt

# ------------------------------------------------------------------ main
def main():
    domains, stats = build()

    rows = sorted(domains.items())
    status_of = {d: v["res"]["status"] for d, v in domains.items()}

    # status counts
    scount = Counter(v["res"]["status"] for v in domains.values())
    # backlink counts per status
    blcount = Counter()
    for d, v in domains.items():
        blcount[v["res"]["status"]] += len(v["links"])

    wb = openpyxl.Workbook()

    # ---------------- Referring Domain Audit ----------------
    ws = wb.active; ws.title = "Referring Domain Audit"
    RDA_COLS = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow",
                "Links Point To","Dofollow Links","Nofollow Links","First Seen",
                "Top Anchor Text","Example Linking Page","Linking Page Title",
                "Source","IP","Disavow Line"]
    ws.append(RDA_COLS)
    def pick_example(links):
        live = [l for l in links if str(l.get("response_code")) == "200"]
        pool = live or links
        return pool[0] if pool else None
    rda_sorted = sorted(domains.items(),
                        key=lambda kv: (kv[1]["res"]["status"], -len(kv[1]["links"])))
    for d, v in rda_sorted:
        links = v["links"]; res = v["res"]; meta = v["meta"]
        df = sum(1 for l in links if not truthy(l.get("nofollow")))
        nf = sum(1 for l in links if truthy(l.get("nofollow")))
        fs = [l.get("fsd") for l in links if l.get("fsd")]
        first_s = min(fs) if fs else (ts_to_date(meta.get("first_seen")) if meta.get("first_seen") else "")
        try:
            first = datetime.date.fromisoformat(first_s) if first_s else None
        except ValueError:
            first = None
        pts = Counter(C.host_of(l.get("redirect_url") or l.get("target_url")) for l in links)
        ex = pick_example(links)
        tool = "Semrush"
        tools = set(l.get("tool") for l in links)
        if "Ahrefs" in tools:
            tool = "Semrush, Ahrefs" if "Semrush" in tools else "Ahrefs"
        ws.append([
            d, res["status"], v["asv"], as_int(meta.get("backlinks_num"), len(links)),
            None, None, res["in_disavow"],
            (pts.most_common(1)[0][0] if pts else ""), df, nf, first,
            res["top_anchor"], (ex.get("source_url") if ex else ""),
            (ex.get("source_title") if ex else ""), tool, meta.get("ip", ""),
            res["res_line"] if False else (f"domain:{d}" if res["status"] == "Spam (Disavow)" else ""),
        ])

    # ---------------- All Backlinks ----------------
    ws2 = wb.create_sheet("All Backlinks")
    AB_COLS = ["Referring Domain","Status","Tool","Anchor Text","Anchor Type",
               "Link Type","Linking Page URL","Linking Page Title","Target URL"]
    ws2.append(AB_COLS)
    ab_n = 0
    for d, v in sorted(domains.items()):
        for l in v["links"]:
            at = C.anchor_type(l.get("anchor"), l.get("target_url"))
            lt = "Nofollow" if truthy(l.get("nofollow")) else "Dofollow"
            ws2.append([d, v["res"]["status"], l.get("tool", "Semrush"),
                        l.get("anchor", ""), at, lt, l.get("source_url", ""),
                        l.get("source_title", ""), l.get("target_url", "")])
            ab_n += 1

    # ---------------- Anchor Analysis ----------------
    ws3 = wb.create_sheet("Anchor Analysis")
    ws3.append(["Anchor Text","Anchor Type","Backlinks","Share of Backlinks",
                "Referring Domains","Spam Domains Using It"])
    anchor_bl = Counter(); anchor_doms = defaultdict(set); anchor_spamdoms = defaultdict(set)
    total_links = 0
    for d, v in domains.items():
        for l in v["links"]:
            a = l.get("anchor", "") or ""
            anchor_bl[a] += 1; anchor_doms[a].add(d); total_links += 1
            if v["res"]["status"].startswith("Spam"):
                anchor_spamdoms[a].add(d)
    for a, n in anchor_bl.most_common():
        ws3.append([a, C.anchor_type(a), n, (n/total_links if total_links else 0),
                    len(anchor_doms[a]), len(anchor_spamdoms[a])])

    # ---------------- Exact Match Anchors ----------------
    ws4 = wb.create_sheet("Exact Match Anchors")
    ws4.append(["Referring domain","Example backlink (linking page)",
                "Exact-match commercial anchor","Market","Site type (indicative)",
                "Partner confirmed? (Y/N)","Final decision"])
    em_n = 0
    for d, v in sorted(domains.items()):
        if not v["res"]["status"].startswith("Held"):
            continue
        # one row per (domain, exact-match anchor)
        seen_a = set()
        for l in v["links"]:
            at = C.anchor_type(l.get("anchor"), l.get("target_url"))
            if at.startswith("Exact match") and l.get("anchor") not in seen_a:
                seen_a.add(l.get("anchor"))
                ws4.append([d, l.get("source_url", ""), l.get("anchor", ""),
                            market_of(l.get("anchor")),
                            "Directory / blog (review source quality)", None, None])
                em_n += 1

    # ---------------- Pending Disavow Lines ----------------
    ws5 = wb.create_sheet("Pending Disavow Lines")
    ws5.append(["Referring domain",
                "Disavow line (append to disavow_collinspool.txt once confirmed)",
                "Recommendation"])
    pend_n = 0
    for d, v in sorted(domains.items()):
        if v["res"]["status"] == "Held (Pending Partner)":
            ws5.append([d, f"domain:{d}",
                        "Append ONLY if the previous SEO partner does not confirm "
                        "this was a commissioned placement."])
            pend_n += 1

    # ---------------- Disavow List ----------------
    ws6 = wb.create_sheet("Disavow List")
    ws6.append(["Disavow Line","AS","Backlinks","RD's","Traffic",
                "Organic Keywords","Top Anchor Text"])
    disavow_doms = []
    for d, v in sorted(domains.items(), key=lambda kv: -len(kv[1]["links"])):
        if v["res"]["status"] == "Spam (Disavow)":
            ws6.append([f"domain:{d}", v["asv"], as_int(v["meta"].get("backlinks_num"), len(v["links"])),
                        None, None, None, v["res"]["top_anchor"]])
            disavow_doms.append(d)

    # ---------------- Summary ----------------
    ws0 = wb.create_sheet("Summary", 0)
    total_dom = len(domains); total_bl = sum(len(v["links"]) for v in domains.values())
    ws0["B1"] = C.CLIENT_NAME
    order = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
             "Spam (Nofollow, No Action)","Keep","Own Site"]
    meaning = {
        "Spam (Disavow)":"Spam referring domain (link-scheme anchor, spam host/title, or off-topic) with at least one dofollow link. In the file.",
        "Held (Pending Partner)":"Non-spam domain with an exact-match commercial/geo anchor or a deep money-page link that MAY be a commissioned placement. Out of the file until the partner confirms.",
        "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
        "Spam (Nofollow, No Action)":"Spam domain, but every link is nofollow and passes no ranking value, so no disavow is needed.",
        "Keep":"Genuine, branded or harmless link (editorial citations, business profiles, directories with no manipulative anchor).",
        "Own Site":"Client-owned domain that redirects into the site.",
    }
    ws0.append([]); ws0.append([])
    ws0["A3"]="Status"; ws0["B3"]="Domains"; ws0["C3"]="Backlinks"; ws0["D3"]="Share of Domains"; ws0["E3"]="What it means"
    rr=4
    for s in order:
        ws0.cell(row=rr,column=1,value=s)
        ws0.cell(row=rr,column=2,value=scount.get(s,0))
        ws0.cell(row=rr,column=3,value=blcount.get(s,0))
        ws0.cell(row=rr,column=4,value=(scount.get(s,0)/total_dom if total_dom else 0))
        ws0.cell(row=rr,column=5,value=meaning[s]); rr+=1
    total_row=rr
    ws0.cell(row=rr,column=1,value="Total"); ws0.cell(row=rr,column=2,value=total_dom)
    ws0.cell(row=rr,column=3,value=total_bl); ws0.cell(row=rr,column=4,value=1); rr+=2

    spam_all = scount.get("Spam (Disavow)",0)+scount.get("Spam (Nofollow, No Action)",0)
    # anchor profile by type
    type_bl=Counter(); type_dom=defaultdict(set)
    for d,v in domains.items():
        for l in v["links"]:
            at=C.anchor_type(l.get("anchor"),l.get("target_url"))
            type_bl[at]+=1; type_dom[at].add(d)
    # biggest spam first-seen month (data-driven)
    month_spam=Counter()
    for d,v in domains.items():
        if v["res"]["status"].startswith("Spam"):
            fs=[l.get("fsd") for l in v["links"] if l.get("fsd")]
            if fs: month_spam[min(fs)[:7]]+=1
    top_month,top_month_n=(month_spam.most_common(1)[0] if month_spam else ("n/a",0))
    # top single source domain
    top_dom,top_dom_links=max(((d,len(v["links"])) for d,v in domains.items()),
                              key=lambda x:x[1], default=("n/a",0))
    # redirect properties
    red_hosts=Counter()
    for d,v in domains.items():
        for l in v["links"]:
            if l.get("redirect_url"): red_hosts[C.host_of(l["redirect_url"])]+=1
    red_note=(f"{sum(red_hosts.values())} links route via a redirect "
              f"({', '.join(h for h,_ in red_hosts.most_common(2))})" if red_hosts
              else "no redirect/owned-domain links detected")
    # Tab-08 flagged set overlap
    t08=TAB08
    t08_found=[d for d in t08 if d in domains]
    t08_dis=[d for d in t08_found if status_of.get(d)=="Spam (Disavow)"]
    t08_held=[d for d in t08_found if status_of.get(d,"").startswith("Held")]
    findings=[
        f"{spam_all} of {total_dom} referring domains are spam; {scount.get('Spam (Disavow)',0)} have a dofollow link and go in the disavow file.",
        f"The spam is concentrated in time: {top_month_n} spam domains were first seen in {top_month}.",
        f"Largest single source: {top_dom} ({top_dom_links} links).",
        "Two footprints: a link-scheme flood of SEO sales-copy anchors on throwaway TLDs, and exact-match commercial/geo directory & bookmark anchors held for the partner.",
        f"{scount.get('Held (Pending Partner)',0)} domains carry exact-match commercial/geo anchors and are held pending the partner who commissioned the directory/bookmark links.",
        f"Of the {len(t08)} Tab-08 flagged domains, {len(t08_found)} are in the live profile: {len(t08_dis)} disavowed, {len(t08_held)} held, {len(t08_found)-len(t08_dis)-len(t08_held)} other; {len(t08)-len(t08_found)} not found live.",
        f"One Search Console property ({C.MONEY_DOMAIN}); {red_note}. Held does not mean valuable - disavowing paid links without confirmation can hurt the client.",
    ]
    kf_head=rr
    ws0.cell(row=rr,column=1,value="Key findings"); rr+=1
    for f in findings:                      # unnumbered, as the sample
        ws0.cell(row=rr,column=1,value=f); rr+=1
    rr+=1
    ap_head=rr
    ws0.cell(row=rr,column=1,value="Anchor text profile (all backlinks)"); rr+=1
    at_head=rr
    ws0.cell(row=rr,column=1,value="Anchor type"); ws0.cell(row=rr,column=2,value="Backlinks")
    ws0.cell(row=rr,column=3,value="Share of Backlinks"); ws0.cell(row=rr,column=4,value="Referring Domains (distinct)"); rr+=1
    for at,n in type_bl.most_common():
        ws0.cell(row=rr,column=1,value=at); ws0.cell(row=rr,column=2,value=n)
        ws0.cell(row=rr,column=3,value=(n/total_bl if total_bl else 0))
        ws0.cell(row=rr,column=4,value=len(type_dom[at])); rr+=1
    rr+=1
    src_row=rr
    ws0.cell(row=rr,column=1,value=f"Source: Semrush Backlink Analytics + Ahrefs discovery, {TODAY} ({total_bl} backlinks / {total_dom} referring domains). Full Ahrefs merge pending client CSV (Ahrefs API 250-row cap).")

    # --- Summary styling to match the signed sample, element by element ---
    maxr=ws0.max_row
    reg=Font(name=FONT,size=9,color="FF000000")
    reg_b=Font(name=FONT,size=9,bold=True,color="FF000000")
    hdr10=Font(name=FONT,size=10,bold=True,color="FF000000")
    for r in range(1,maxr+1):
        ws0.row_dimensions[r].height=22.5                     # every row 22.5
        for c in range(1,6):
            cl=ws0.cell(row=r,column=c)
            if cl.value is not None:
                cl.font=reg                                   # default Geist 9 (blanks stay Calibri 11)
    ws0["B1"].font=Font(name=FONT,size=21,bold=True,color=ACCENT)   # title 21
    for c in range(1,6):
        ws0.cell(row=3,column=c).font=hdr10                   # status-table header 10 bold
        ws0.cell(row=at_head,column=c).font=hdr10             # anchor-type header 10 bold
    ws0.cell(row=total_row,column=1).font=reg_b               # Total bold
    ws0.cell(row=kf_head,column=1).font=reg_b                 # "Key findings" bold
    ws0.cell(row=ap_head,column=1).font=reg_b                 # "Anchor text profile" bold
    ws0.cell(row=src_row,column=1).font=Font(name=FONT,size=8,italic=True,color="FF000000")  # source 8 italic
    ws0.sheet_view.showGridLines=False
    for L,w in SAMPLE_WIDTHS["Summary"].items():
        ws0.column_dimensions[L].width=w
    # merge long single-column text rows (key findings + source) across A:E, as the sample does
    for r in range(1,maxr+1):
        a=ws0.cell(row=r,column=1).value
        if isinstance(a,str) and len(a)>55 and all(ws0.cell(row=r,column=c).value in (None,"") for c in range(2,6)):
            try: ws0.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5)
            except Exception: pass
    # embed the Harbinger agency logo (reused from the signed template; same for every client)
    logo_path=f"{ROOT}/ref/harbinger_logo.png"
    if os.path.exists(logo_path):
        from openpyxl.drawing.image import Image as _XLImage
        _img=_XLImage(logo_path); _img.width=196; _img.height=58
        ws0.add_image(_img,"A1")

    # styling for data tabs (header/data cells, freeze, filter, widths)
    style_workbook(wb, [
        ("Referring Domain Audit", ws.max_row, len(RDA_COLS), None),
        ("All Backlinks", ws2.max_row, len(AB_COLS), None),
        ("Anchor Analysis", ws3.max_row, 6, None),
        ("Exact Match Anchors", ws4.max_row, 7, None),
        ("Pending Disavow Lines", ws5.max_row, 3, None),
        ("Disavow List", ws6.max_row, 7, None),
    ])

    # number formats on data tabs (match the sample)
    apply_numfmts(wb)
    # number formats on the Summary tables
    statuses=set(order)|{"Total"}
    for r in range(1, ws0.max_row+1):
        a=ws0.cell(row=r,column=1).value
        cval=ws0.cell(row=r,column=3).value
        if a in statuses:                       # status table: Domains/Backlinks #,##0, Share 0.0%
            ws0.cell(row=r,column=2).number_format="#,##0"
            ws0.cell(row=r,column=3).number_format="#,##0"
            ws0.cell(row=r,column=4).number_format="0.0%"
        elif isinstance(ws0.cell(row=r,column=2).value,(int,float)) and isinstance(cval,float):
            ws0.cell(row=r,column=2).number_format="#,##0"   # anchor profile: Backlinks
            ws0.cell(row=r,column=3).number_format="0.0%"    # Share of Backlinks
            ws0.cell(row=r,column=4).number_format="#,##0"   # Referring Domains

    out_xlsx=f"{OUT}/CollinsPool_Backlinks_Audit.xlsx"
    wb.save(out_xlsx)

    # ---------------- disavow file ----------------
    reasons=defaultdict(list)
    for d in disavow_doms:
        cat=domains[d]["res"]["reason"].split("(")[0].strip()  # drop per-domain detail
        reasons[cat].append(d)
    with open(f"{OUT}/disavow_collinspool.txt","w") as f:
        f.write(f"# Disavow file - collinspoolmanagement.com ({C.CLIENT_NAME})\n")
        f.write(f"# Property: collinspoolmanagement.com (Google Search Console)\n")
        f.write(f"# Generated: {TODAY}\n")
        f.write(f"# Domains: {len(disavow_doms)} (Spam, with >=1 dofollow link)\n")
        f.write("# Held domains (exact-match/commissioned) are EXCLUDED pending the previous SEO partner's confirmation.\n")
        f.write("# DO NOT UPLOAD before that conversation. This file is the full union for the money site.\n")
        f.write("# Client must check Search Console: if a disavow file already exists on this property, uploading REPLACES it; if none exists, there is nothing to merge.\n")
        f.write("# Lines are domain: entries, grouped by reason.\n\n")
        for reason in sorted(reasons):
            f.write(f"# --- {reason} ({len(reasons[reason])}) ---\n")
            for d in sorted(reasons[reason]):
                f.write(f"domain:{d}\n")
            f.write("\n")

    # print verification counts
    print("=== BUILD COUNTS ===")
    print("stats:", stats)
    print("domains:", total_dom, "backlinks(links):", total_bl)
    for s in order:
        print(f"  {scount.get(s,0):5d} / {blcount.get(s,0):5d} bl  {s}")
    print("disavow domains:", len(disavow_doms))
    print("All Backlinks rows:", ab_n, "Exact-match rows:", em_n, "Pending:", pend_n)
    print("saved:", out_xlsx)

if __name__ == "__main__":
    main()
