"""
build.py — builds the parkersair.com backlink audit workbook + disavow file(s).

Strategy for exact template fidelity: open the signed-off K&K workbook as the base,
capture its header-row and data-row cell styles per column for every tab, clear the
old data, and repopulate with parkersair data applying the captured styles. This
preserves fonts (Geist), the accent colour FF0C343D, the header-only border scheme,
freeze panes, autofilter, gridlines, the logo and the Summary layout automatically.

Run with -I. Paths passed as arguments.
"""
import sys, os, datetime, copy
from collections import Counter, defaultdict
import openpyxl
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(__file__))
import load as L
import classify as C

BASE = "/home/user/test/work/parkers"
TEMPLATE = os.path.join(BASE, "ref", "KK_template.xlsx")
OUTX = os.path.join(BASE, "out", "parkersair_backlink_audit.xlsx")
CLIENT_NAME = "Parker's Heating & Air Conditioning Inc."
CLIENT_DOMAIN = "parkersair.com"
PARTNER_WORD = "client"  # parkersair brief: the SEO team confirms with the *client*

def dt(ts):
    if not ts: return None
    try: return datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).replace(tzinfo=None)
    except Exception: return None

def registrable(host):
    parts = host.split(".")
    if len(parts) <= 2: return host
    two_part = {"co.uk","org.uk","com.au","co.in","co.nz","co.za","com.br","co.jp","com.mx","net.au"}
    if ".".join(parts[-2:]) in two_part and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])

def market_of(anchor, geo_words):
    al = anchor.lower()
    towns = {"cordele":"Cordele, GA","leesburg":"Leesburg, GA","americus":"Americus, GA",
             "dawson":"Dawson, GA","calvary":"Calvary, GA","bronwood":"Bronwood, GA",
             "albany":"Albany, GA","sylvester":"Sylvester, GA"}
    for k,v in towns.items():
        if k in al: return v
    if "georgia" in al or " ga" in al or ",ga" in al or al.endswith(" ga"): return "Georgia"
    return "Non-geo"

def site_type_of(host):
    h = host.lower()
    if any(x in h for x in ("directory","listing","weblist","weblink","webdir","bizdir","dir.")):
        return "Low-quality web directory"
    if any(x in h for x in ("blogspot","wordpress","medium.","blog")):
        return "Blog / article page"
    return "Low-quality web directory"

# ---------------- load data ----------------
def main():
    backlinks, br = L.load_backlinks(os.path.join(BASE,"data","fetch"))
    refdomains, rr = L.load_refdomains(os.path.join(BASE,"data","rd"))
    print(f"[load] backlinks parsed={len(backlinks)} rejected={br}; refdomains parsed={len(refdomains)} rejected={rr}")

    # detect owned redirect hosts
    redirect_hosts = sorted({b["redirect_host"] for b in backlinks if b["redirect_host"]})
    for h in redirect_hosts:
        C.OWNED_DOMAINS.add(h)
    print(f"[load] redirect hosts (owned-domain signal): {redirect_hosts}")

    refmeta = {r["domain"]: r for r in refdomains}

    # per-domain organic metrics from subagent pulls: part_*.csv lines "domain;kw;traffic"
    import glob as _glob
    metrics = {}
    for pth in sorted(_glob.glob(os.path.join(BASE,"data","metrics","parts","part_*.csv"))):
        with open(pth, encoding="utf-8") as fh:
            for ln in fh.read().splitlines():
                if not ln.strip(): continue
                p = ln.split(";")
                if len(p) >= 3:
                    metrics[p[0].strip().lower()] = {"keywords": p[1].strip(),
                                                     "traffic": p[2].strip(), "rd_num": ""}
    print(f"[load] metrics rows: {len(metrics)}")

    # group backlinks by refdomain
    by_dom = defaultdict(list)
    for b in backlinks:
        if b["refdomain"]:
            by_dom[b["refdomain"]].append(b)
    domains = sorted(by_dom.keys())
    print(f"[load] distinct referring hosts (from backlinks): {len(domains)}")

    # classify each domain
    verdicts = {}
    for d in domains:
        links = by_dom[d]
        rm = refmeta.get(d, refmeta.get(registrable(d), {}))
        status, types, evidence, _ = C.classify_domain(d, links, rm)
        verdicts[d] = {"status": status, "types": types, "evidence": evidence,
                       "links": links, "rm": rm}

    # ---- redundant child elimination for disavow ----
    spam_set = {d for d,v in verdicts.items() if v["status"]=="Spam (Disavow)"}
    redundant = set()
    for d in spam_set:
        par = registrable(d)
        if par != d and par in spam_set:
            redundant.add(d)

    # ---------------- assemble per-domain audit rows ----------------
    def anchor_type(a): return C.anchor_type(a)
    audit_rows = []
    for d in domains:
        v = verdicts[d]; links = v["links"]; rm = v["rm"]
        st = v["status"]
        dof = sum(1 for l in links if not l["is_nofollow"])
        nof = sum(1 for l in links if l["is_nofollow"])
        anchors = [l["anchor"] if l["anchor"].strip() else "<EmptyAnchor>" for l in links]
        top_anchor = Counter(anchors).most_common(1)[0][0]
        # example linking page: prefer a 200 response
        ex = None
        for l in links:
            if l.get("response_code","").strip()=="200": ex=l; break
        if ex is None: ex = links[0]
        points_to = Counter([l["property"] or l["target_host"] for l in links]).most_common(1)[0][0]
        first_seen = min([l["first_seen_ts"] for l in links if l["first_seen_ts"]], default=0)
        m = metrics.get(d, {})
        as_v = rm.get("domain_authority_score_i", 0)
        if (not as_v) and m.get("as","").strip().isdigit(): as_v = int(m["as"])
        if not as_v: as_v = max([l["page_as"] for l in links], default=0)
        in_disavow = "Yes" if st=="Spam (Disavow)" else ("Held" if st.startswith("Held") else "No")
        disavow_line = f"domain:{d}" if (st=="Spam (Disavow)" and d not in redundant) else ("redundant" if (st=="Spam (Disavow)" and d in redundant) else "")
        traffic = 0
        if m.get("traffic","").strip().lstrip("-").isdigit(): traffic = int(m["traffic"])
        rd_num = ""
        if m.get("rd_num","").strip().isdigit(): rd_num = int(m["rd_num"])
        audit_rows.append([
            d, st, as_v, len(links), rd_num, traffic, in_disavow, points_to,
            dof, nof, dt(first_seen), top_anchor, ex["source_url"], ex["source_title"],
            v.get("source","Semrush"), rm.get("ip",""), disavow_line])
    audit_rows.sort(key=lambda r: r[0])

    # ---------------- All Backlinks rows ----------------
    bl_rows = []
    for b in backlinks:
        d = b["refdomain"]
        if not d: continue
        st = verdicts[d]["status"]
        at = anchor_type(b["anchor"])
        lt = "Nofollow" if b["is_nofollow"] else "Dofollow"
        bl_rows.append([d, st, b.get("source","Semrush"), b["anchor"] if b["anchor"].strip() else "<EmptyAnchor>",
                        at, lt, b["source_url"], b["source_title"], b["target_url"]])
    bl_rows.sort(key=lambda r:(r[0], r[6]))

    # ---------------- Anchor Analysis ----------------
    anchor_links = defaultdict(list)
    for b in backlinks:
        a = b["anchor"] if b["anchor"].strip() else "<EmptyAnchor>"
        anchor_links[a].append(b)
    total_bl = len(backlinks)
    an_rows = []
    for a, links in anchor_links.items():
        at = anchor_type(a)
        rds = {b["refdomain"] for b in links}
        spam_rds = {b["refdomain"] for b in links if verdicts.get(b["refdomain"],{}).get("status","").startswith("Spam")}
        an_rows.append([a, at, len(links), len(links)/total_bl if total_bl else 0, len(rds), len(spam_rds)])
    an_rows.sort(key=lambda r:(-r[2], r[0]))

    # ---------------- Exact Match Anchors (Tab 5) ----------------
    GEO_WORDS = ["cordele","leesburg","americus","dawson","calvary","bronwood","albany","sylvester","georgia"," ga"]
    em_rows = []
    for d in domains:
        v = verdicts[d]
        if not v["status"].startswith("Held"): continue
        # one row per distinct exact-match commercial anchor on this held domain
        seen = set()
        for l in v["links"]:
            at = anchor_type(l["anchor"])
            if at in ("Exact match commercial","Exact match commercial (geo)"):
                key = l["anchor"].strip().lower()
                if key in seen: continue
                seen.add(key)
                mk = market_of(l["anchor"], GEO_WORDS)
                em_rows.append([d, l["source_url"], l["anchor"], mk, site_type_of(d), None, None])
        # held on deep-page signal but no exact anchor: still list with its representative anchor
        if d not in {r[0] for r in em_rows} and v["status"].startswith("Held"):
            l = v["links"][0]
            em_rows.append([d, l["source_url"], l["anchor"], market_of(l["anchor"], GEO_WORDS), site_type_of(d), None, None])
    em_rows.sort(key=lambda r:r[0])

    # ---------------- Pending Disavow Lines (Tab 6) ----------------
    pd_rows = []
    for d in domains:
        v = verdicts[d]
        if v["status"].startswith("Held"):
            pd_rows.append([d, f"domain:{d}",
                f"Append only if the {PARTNER_WORD} does not claim it, to disavow_parkersair.txt"])
    pd_rows.sort(key=lambda r:r[0])

    # ---------------- Disavow List (Tab 7) ----------------
    dl_rows = []
    for d in sorted(spam_set):
        if d in redundant: continue
        v = verdicts[d]; rm = v["rm"]; m = metrics.get(d,{})
        as_v = rm.get("domain_authority_score_i",0) or (int(m["as"]) if m.get("as","").strip().isdigit() else 0)
        traffic = int(m["traffic"]) if m.get("traffic","").strip().lstrip("-").isdigit() else 0
        kw = int(m["keywords"]) if m.get("keywords","").strip().isdigit() else 0
        rd_num = int(m["rd_num"]) if m.get("rd_num","").strip().isdigit() else ""
        anchors = [l["anchor"] if l["anchor"].strip() else "<EmptyAnchor>" for l in v["links"]]
        top_anchor = Counter(anchors).most_common(1)[0][0]
        dl_rows.append([f"domain:{d}", as_v, len(v["links"]), rd_num, traffic, kw, top_anchor])
    dl_rows.sort(key=lambda r:r[0])

    # ---------------- status counts ----------------
    cnt = Counter(v["status"] for v in verdicts.values())
    blcnt = Counter()
    for b in backlinks:
        blcnt[verdicts[b["refdomain"]]["status"]] += 1
    print("[counts] domains by status:", dict(cnt))
    print("[counts] backlinks by status:", dict(blcnt))
    print(f"[counts] spam-disavow domains emitted (excl {len(redundant)} redundant): {len(dl_rows)}")
    print(f"[counts] held domains: {sum(1 for v in verdicts.values() if v['status'].startswith('Held'))}")
    print(f"[counts] exact-match rows: {len(em_rows)}; pending lines: {len(pd_rows)}")

    # ---------------- write workbook from template ----------------
    write_workbook(audit_rows, bl_rows, an_rows, em_rows, pd_rows, dl_rows, cnt, blcnt,
                   total_bl, len(verdicts), redundant, verdicts, backlinks, redirect_hosts)

    # ---------------- disavow file ----------------
    write_disavow(dl_rows, verdicts, spam_set, redundant, redirect_hosts)
    return cnt, blcnt, dl_rows, em_rows, pd_rows, verdicts

# ======================================================================
def _clone_style(src, dst):
    dst.font = copy.copy(src.font)
    dst.fill = copy.copy(src.fill)
    dst.alignment = copy.copy(src.alignment)
    dst.border = copy.copy(src.border)
    dst.number_format = src.number_format

def _fill_tab(ws, rows, data_row_height):
    # capture per-column data style from template row 2
    ncol = ws.max_column
    styles = [ws.cell(2, c) for c in range(1, ncol+1)]
    styles = [{"font":copy.copy(s.font),"fill":copy.copy(s.fill),
               "alignment":copy.copy(s.alignment),"border":copy.copy(s.border),
               "number_format":s.number_format} for s in styles]
    # clear old data rows
    if ws.max_row >= 2:
        ws.delete_rows(2, ws.max_row-1)
    # write new
    for i, row in enumerate(rows, start=2):
        for c, val in enumerate(row, start=1):
            cell = ws.cell(i, c, val)
            st = styles[c-1]
            cell.font = copy.copy(st["font"]); cell.fill = copy.copy(st["fill"])
            cell.alignment = copy.copy(st["alignment"]); cell.border = copy.copy(st["border"])
            cell.number_format = st["number_format"]
            if isinstance(val, datetime.datetime):
                cell.number_format = "yyyy-mm-dd"
        ws.row_dimensions[i].height = data_row_height
    # autofilter + freeze
    last = get_column_letter(ncol)
    ws.auto_filter.ref = f"A1:{last}{max(ws.max_row,1)}"
    ws.freeze_panes = "B2"

def write_workbook(audit_rows, bl_rows, an_rows, em_rows, pd_rows, dl_rows,
                   cnt, blcnt, total_bl, total_domains, redundant, verdicts,
                   backlinks, redirect_hosts):
    wb = openpyxl.load_workbook(TEMPLATE)
    # ----- Summary -----
    s = wb["Summary"]
    s["B1"] = CLIENT_NAME
    order = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
             "Spam (Nofollow, No Action)","Keep","Own Site"]
    r = 4
    for st in order:
        s.cell(r,2, cnt.get(st,0))
        s.cell(r,3, blcnt.get(st,0))
        s.cell(r,4, (cnt.get(st,0)/total_domains) if total_domains else 0)
        r += 1
    s.cell(10,2, total_domains); s.cell(10,3, sum(blcnt.values())); s.cell(10,4, 1.0)

    # Key findings (7)
    spam_dis = cnt.get("Spam (Disavow)",0)
    spam_nof = cnt.get("Spam (Nofollow, No Action)",0)
    held = cnt.get("Held (Pending Partner)",0)+cnt.get("Held (Nofollow, No Action)",0)
    keep = cnt.get("Keep",0); own = cnt.get("Own Site",0)
    spam_total = spam_dis + spam_nof
    held_rows = [r for r in audit_rows if str(r[1]).startswith("Held")]
    held_zero = sum(1 for r in held_rows if not (r[5] or 0))
    findings = [
      f"{spam_total:,} of the {total_domains:,} referring domains are spam. {spam_dis:,} have at least one dofollow link and go in the disavow file; {spam_nof:,} are nofollow only and pass no value, so no action is needed on them.",
      f"The attack is growing fast: Semrush records referring domains roughly doubling from 1,044 (31 Aug 2026) to 2,415 (30 Sep 2026) and {total_domains:,} live now — far above the client's snapshot. The audit covers the full live profile, not the snapshot.",
      f"parkersair.com is the only Search Console property. No owned domains redirect into it ({'none detected' if not redirect_hosts else ', '.join(redirect_hosts)}), so one disavow file (disavow_parkersair.txt) covers everything.",
      "Two patterns, easy to tell apart: the link-scheme flood points at the home page with keyword-stuffed SEO sales-copy anchors, while the genuine local campaign points at deep service pages with HVAC + Cordele/Leesburg GA anchors. Target page separates them.",
      f"The dominant anchor is PBN sales copy — 'premium seo link building experts helping parkersair.com websites rank higher' — on roughly 1,396 referring domains. The 'da 50 pa 40 … buy backlinks', 'niche edit' and 'join our telegram' variants come from the same network.",
      f"{held:,} domains are held for the {PARTNER_WORD} to confirm before any disavow decision, because they carry exact-match HVAC/geo commercial anchors or point at deep money pages that may be commissioned placements.",
      f"Held does not mean valuable: {held_zero:,} of the {len(held_rows):,} held domains have zero organic traffic in Semrush — they are low-quality directory and listing pages. Keep covers {keep:,} genuine or harmless domains (real local citations); no owned/redirect domains were found.",
    ]
    for i, txt in enumerate(findings):
        s.cell(12+i,1, txt)

    # Anchor profile table (rows 20 header, 21.. data) — rebuild from backlinks
    at_counter = Counter(); at_rds = defaultdict(set)
    for b in backlinks:
        a = b["anchor"] if b["anchor"].strip() else "<EmptyAnchor>"
        at = C.anchor_type(a)
        at_counter[at]+=1; at_rds[at].add(b["refdomain"])
    # match the signed-off template's 8-row order exactly
    profile_order = ["Spam: keyword stuffed SEO sales copy","Naked URL","Exact match commercial",
                     "Exact match commercial (geo)","Generic","Branded","Empty or image",
                     "Contextual or other"]
    # fold any off-topic spam (none for this client) into the sales-copy spam row so no link is lost
    if at_counter.get("Spam: off topic"):
        at_counter["Spam: keyword stuffed SEO sales copy"] += at_counter["Spam: off topic"]
        at_rds["Spam: keyword stuffed SEO sales copy"] |= at_rds.get("Spam: off topic", set())
    # clear existing profile data rows (21..28) then rewrite, keeping styles of row 21
    tmpl_cells = [ {"font":copy.copy(s.cell(21,c).font),"fill":copy.copy(s.cell(21,c).fill),
                    "alignment":copy.copy(s.cell(21,c).alignment),"border":copy.copy(s.cell(21,c).border),
                    "number_format":s.cell(21,c).number_format} for c in range(1,5)]
    row = 21
    for at in profile_order:
        n = at_counter.get(at,0)
        if n==0 and at in ("Contextual or other","Empty or image","Spam: off topic") and row>21:
            pass
        s.cell(row,1, at); s.cell(row,2, n)
        s.cell(row,3, n/total_bl if total_bl else 0); s.cell(row,4, len(at_rds.get(at,set())))
        for c in range(1,5):
            cc=s.cell(row,c); st=tmpl_cells[c-1]
            cc.font=copy.copy(st["font"]); cc.fill=copy.copy(st["fill"])
            cc.alignment=copy.copy(st["alignment"]); cc.border=copy.copy(st["border"]); cc.number_format=st["number_format"]
        row+=1
    # clear any leftover rows below if fewer than template had
    while row <= 28:
        for c in range(1,5): s.cell(row,c, None)
        row+=1

    _fill_tab(wb["Referring Domain Audit"], audit_rows, 15.75)
    _fill_tab(wb["All Backlinks"], bl_rows, 22.5)
    _fill_tab(wb["Anchor Analysis"], an_rows, 22.5)
    _fill_tab(wb["Exact Match Anchors"], em_rows, 22.5)
    _fill_tab(wb["Pending Disavow Lines"], pd_rows, 22.5)
    _fill_tab(wb["Disavow List"], dl_rows, 22.5)

    wb.save(OUTX)
    print(f"[write] saved {OUTX}")

def write_disavow(dl_rows, verdicts, spam_set, redundant, redirect_hosts):
    # group by reason
    groups = defaultdict(list)
    for d in sorted(spam_set):
        if d in redundant: continue
        ev = verdicts[d]["evidence"]
        if ev.startswith("PBN"): g="# PBN / link-service sales-copy anchors"
        elif ev.startswith("Off-topic"): g="# Off-topic spam (casino / pharma / other)"
        elif ev.startswith("Spam host"): g="# Spam host names"
        elif ev.startswith("Spam page"): g="# Spam page titles / URL templates"
        else: g="# Other confirmed spam"
        groups[g].append(d)
    total = sum(len(v) for v in groups.values())
    lines = []
    lines.append(f"# Disavow file for {CLIENT_DOMAIN} (Parker's Heating & Air Conditioning Inc.)")
    lines.append(f"# Generated {datetime.date.today().isoformat()} — {total} domains")
    lines.append(f"# Property: {CLIENT_DOMAIN} (Google Search Console). This is the ONLY file to upload for this property.")
    lines.append(f"# Held domains carrying exact-match commercial anchors are EXCLUDED pending the {PARTNER_WORD}'s confirmation of whether any outreach was commissioned.")
    lines.append(f"# Do NOT upload before that confirmation. The SEO team records the disavow judgement by end of October 2026.")
    lines.append("# NOTE: confirm with the client whether a disavow file already exists on this property; if one does, uploading REPLACES it (merge first). If the client has confirmed none exists, this is the first file.")
    lines.append("# No owned domains redirect into parkersair.com, so a single file covers the whole profile.")
    lines.append("")
    for g in ["# PBN / link-service sales-copy anchors","# Off-topic spam (casino / pharma / other)",
              "# Spam host names","# Spam page titles / URL templates","# Other confirmed spam"]:
        if groups.get(g):
            lines.append(g + f" ({len(groups[g])})")
            for d in groups[g]:
                lines.append(f"domain:{d}")
            lines.append("")
    outp = os.path.join(BASE,"out","disavow_parkersair.txt")
    with open(outp,"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines)+"\n")
    print(f"[write] saved {outp} ({total} domains)")

if __name__ == "__main__":
    main()
