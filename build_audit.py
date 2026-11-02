#!/usr/bin/env python3
"""Build newgarden.com backlinks audit workbook in the K&K template format."""
import csv, json, re, datetime, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DATA = "/home/user/test/data"
OUT = "/home/user/test/NewGarden_Backlinks_Audit.xlsx"
TARGET = "newgarden.com"

# ---------- load ----------
def load_csv(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

refdomains = load_csv(f"{DATA}/refdomains.csv")
backlinks  = load_csv(f"{DATA}/backlinks.csv")
anchors    = json.load(open(f"{DATA}/anchors.json"))["anchors"]

def num(v, cast=float, default=0):
    try:
        if v is None or v == "" or str(v).lower()=="none": return default
        return cast(float(v))
    except Exception:
        return default
def bl(v):  # bool from csv/json
    return str(v).strip().lower() in ("true","1","yes")

# index one representative backlink per referring domain
bl_by_dom = {}
for b in backlinks:
    d = (b.get("root_name_source") or "").strip().lower()
    if d and d not in bl_by_dom:
        bl_by_dom[d] = b

# ---------- anchor-type classifier ----------
GEO = re.compile(r"\b(greensboro|winston[- ]?salem|high point|summerfield|kernersville|oak ridge|browns summit|north carolina|\bn\.?c\.?\b)\b", re.I)
SERVICE = re.compile(r"\b(landscap\w*|lawn|nursery|garden center|garden centre|hardscap\w*|irrigation|mulch\w*|patio|maintenance|tree service|plant(ing)? service|design (and|&) build)\b", re.I)
SPAMCOPY = re.compile(r"(back\s?link|\bseo\b|\bpbn\b|do[- ]?follow|dofollow|domain rating|\bdr[\s\-]?\d|\bda\b\s?\d|\btf\b|rank(ing|s)?\b|link[- ]build|guest post|niche edit|\bserp\b|index(ation|ing)|citation flow|trust flow|outrank|link velocity|anchor text|white[- ]hat|tier(ed|\s?1)|authority (backlink|link)|buy .{0,15}link|premium .{0,15}(backlink|link)|traffic (surge|boost)|web traffic|t\.me/|telegram|happygrannypies|darksidelinks|boost .{0,20}(rank|authority|traffic|dr|da))", re.I)
URLISH = re.compile(r"^\s*(https?://|www\.)|^\s*[a-z0-9][a-z0-9.\-]*\.(com|org|net|info|io|co|us|store|shop|xyz|site|online|me|biz)(/\S*)?\s*$", re.I)
BRAND = re.compile(r"new\s?garden", re.I)
GENERIC = {"website","visit website","visit site","source","go now","more like this","click here",
           "read more","learn more","here","link","more","view","this website","visit","website link","go","see more"}

def classify_anchor(a):
    if a is None: a = ""
    a = a.strip()
    if a == "" : return "Empty or image"
    low = a.lower()
    if SPAMCOPY.search(a): return "Spam: keyword stuffed SEO sales copy"
    # naked url / bare domain (no spaces, looks like a url) — but allow brand check first for plain brand
    if URLISH.match(a) and " " not in a.strip(): return "Naked URL"
    if low in GENERIC: return "Generic"
    # Branded FIRST: "New Garden ..." is the company name; the words landscaping/nursery in it
    # are part of the brand, not a commissioned money anchor.
    if BRAND.search(a): return "Branded"
    is_service = bool(SERVICE.search(a))
    is_geo = bool(GEO.search(a))
    # plant-catalogue / content style (latin binomials, plant names) -> contextual, not a money anchor
    plantish = bool(re.search(r"\(([A-Z][a-z]+ [a-z]+|[A-Z][a-z]+ ')", a)) or "plants.newgarden" in low or re.search(r"camellia|magnolia|hydrangea|maple|yucca|boxwood|agave|pine|redwood|verbascum|gaura|sarcococca|ipomoea|stachys", low)
    if is_service and not plantish:
        return "Exact match commercial (geo)" if is_geo else "Exact match commercial"
    if plantish: return "Contextual or other"
    return "Contextual or other"

COMMERCIAL = {"Exact match commercial","Exact match commercial (geo)"}

# ---------- per-domain status ----------
def host_of(url):
    m = re.match(r"https?://([^/]+)", url or "")
    return m.group(1).lower() if m else ""

rows = []   # enriched per referring domain
for r in refdomains:
    dom = (r.get("domain") or "").strip().lower()
    if not dom: continue
    spam = bl(r.get("is_spam"))
    df = int(num(r.get("dofollow_links"), int))
    links = int(num(r.get("links_to_target"), int))
    b = bl_by_dom.get(dom, {})
    anchor = (b.get("anchor") or "").strip()
    atype = classify_anchor(anchor)
    # An overt SEO-sales-copy anchor is spam even if Ahrefs' is_spam flag missed it.
    spam = spam or (atype == "Spam: keyword stuffed SEO sales copy")
    # status
    if spam and df > 0:            status = "Spam (Disavow)"
    elif spam and df == 0:         status = "Spam (Nofollow, No Action)"
    elif (not spam) and atype in COMMERCIAL and df > 0:   status = "Held (Pending Partner)"
    elif (not spam) and atype in COMMERCIAL and df == 0:  status = "Held (Nofollow, No Action)"
    else:                          status = "Keep"
    rows.append({
        "domain": dom, "status": status,
        "AS": num(r.get("domain_rating")), "Backlinks": links,
        "RDs": int(num(r.get("dofollow_refdomains"), int)),
        "Traffic": int(num(r.get("traffic_domain"), int)),
        "dofollow": df, "nofollow": max(links-df,0),
        "first_seen": (r.get("first_seen") or "")[:10],
        "anchor": anchor, "atype": atype,
        "url_from": b.get("url_from",""), "title": b.get("title",""),
        "url_to": b.get("url_to",""),
        "points_to": host_of(b.get("url_to","")) or TARGET,
        "ip": (r.get("ip_source") or "").strip() if (r.get("ip_source") or "").lower()!="none" else "",
        "orgkw": int(num(r.get("positions_source_domain"), int)),
        # link type of THIS representative backlink (fallback to domain-level if absent)
        "link_type": ("Dofollow" if bl(b.get("is_dofollow")) else "Nofollow") if b else ("Dofollow" if df>0 else "Nofollow"),
    })

# ---------- aggregates ----------
STATUS_ORDER = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
                "Spam (Nofollow, No Action)","Keep","Own Site"]
STATUS_MEANING = {
 "Spam (Disavow)":"Confirmed spam referring domain with at least one dofollow link. Included in the disavow-ready file.",
 "Held (Pending Partner)":"Non-spam domain with an exact-match commercial anchor that MAY have been a commissioned/paid placement. Held out of the disavow file until the client / previous SEO partner confirms whether it was paid for.",
 "Held (Nofollow, No Action)":"Same as above, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)":"Spam domain, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep":"Genuine, branded, or harmless link (incl. editorial citations and the plants.newgarden.com catalogue). Keep.",
 "Own Site":"Client-owned domain that redirects into the site.",
}
from collections import defaultdict
dom_count = defaultdict(int); bl_count = defaultdict(int)
for r in rows:
    dom_count[r["status"]] += 1
    bl_count[r["status"]]  += r["Backlinks"]
tot_dom = sum(dom_count.values()); tot_bl = sum(bl_count.values())

# anchor-type profile (from anchors report, top-N coverage)
at_bl = defaultdict(int); at_rd = defaultdict(int)
tot_anchor_bl = sum(int(a["links_to_target"]) for a in anchors)
for a in anchors:
    t = classify_anchor(a["anchor"])
    at_bl[t] += int(a["links_to_target"]); at_rd[t] += int(a["refdomains"])
ANCHOR_ORDER = sorted(at_bl, key=lambda k:-at_bl[k])

# ---------- styling ----------
HEAD_FILL = PatternFill("solid", fgColor="FF0C343D")
WHITE = "FFFFFFFF"; DARK="FF0C343D"
def headfont(sz=9): return Font(name="Geist", size=sz, bold=True, color=WHITE)
def cellfont(sz=9, bold=False, color="FF000000"): return Font(name="Geist", size=sz, bold=bold, color=color)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
CENV= Alignment(horizontal="center", vertical="center")
WRAP= Alignment(wrap_text=True, vertical="top")
LEFT= Alignment(horizontal="left", vertical="top")
thin = Side(style="thin", color="FFD9D9D9")
BORDER = Border(left=thin,right=thin,top=thin,bottom=thin)

def style_header(ws, ncol, row=1):
    for c in range(1, ncol+1):
        cell = ws.cell(row, c)
        cell.font = headfont(); cell.fill = HEAD_FILL; cell.alignment = CEN; cell.border = BORDER

def put(ws, r, c, v, bold=False, align=None, numfmt=None, color="FF000000"):
    cell = ws.cell(r, c, v)
    cell.font = cellfont(bold=bold, color=color)
    cell.alignment = align or LEFT
    if numfmt: cell.number_format = numfmt
    return cell

wb = openpyxl.Workbook()

# ===== 1. Summary =====
ws = wb.active; ws.title = "Summary"
ws.column_dimensions["A"].width=40; ws.column_dimensions["B"].width=16
ws.column_dimensions["C"].width=17; ws.column_dimensions["D"].width=18; ws.column_dimensions["E"].width=120
t = ws.cell(1,2,"New Garden Landscaping & Nursery  —  newgarden.com"); t.font=Font(name="Geist",size=18,bold=True,color=DARK); t.alignment=CENV
sub = ws.cell(2,2,f"Live referring-domain & backlink audit  ·  {datetime.date.today().isoformat()}"); sub.font=Font(name="Geist",size=10,italic=True,color=DARK)
# status table
hdr_row=4
for c,h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"],1):
    ws.cell(hdr_row,c,h)
style_header(ws,5,hdr_row)
rr=hdr_row+1
for s in STATUS_ORDER:
    put(ws,rr,1,s,bold=True)
    put(ws,rr,2,dom_count.get(s,0),align=CENV)
    put(ws,rr,3,bl_count.get(s,0),align=CENV)
    put(ws,rr,4,(dom_count.get(s,0)/tot_dom if tot_dom else 0),align=CENV,numfmt="0.0%")
    put(ws,rr,5,STATUS_MEANING[s],align=WRAP)
    rr+=1
put(ws,rr,1,"Total",bold=True); put(ws,rr,2,tot_dom,bold=True,align=CENV); put(ws,rr,3,tot_bl,bold=True,align=CENV)
put(ws,rr,4,1.0,bold=True,align=CENV,numfmt="0.0%"); rr+=2

spam_dom = dom_count.get("Spam (Disavow)",0)+dom_count.get("Spam (Nofollow, No Action)",0)
put(ws,rr,1,"Key findings",bold=True,color=DARK); rr+=1
findings = [
 f"{spam_dom:,} of the {tot_dom:,} live referring domains are spam. {dom_count.get('Spam (Disavow)',0):,} carry at least one dofollow link and are compiled into the disavow-ready list (Tab 07); the other {dom_count.get('Spam (Nofollow, No Action)',0):,} are nofollow and need no action.",
 "The spam is a recent injection: referring domains were flat at ~450-530 through early 2026, then spiked to ~1,780 by Sep 2026 (a ~4x jump). A single automated burst on 28-29 Sep 2026 created dozens of same-day .shop / .xyz / .store link-farm domains (DR 0, zero traffic, one link each).",
 "The dominant spam anchors are keyword-stuffed SEO sales copy that NAME the client's own domain (e.g. 'Premium SEO Backlinks newgarden.com', 'PBN Network Service', 'Niche Edit Links'). This is the fingerprint of auto-generated spam / negative SEO, not a paid campaign the client would have bought.",
 f"PAID-ANCHOR QUESTION: {dom_count.get('Held (Pending Partner)',0)+dom_count.get('Held (Nofollow, No Action)',0):,} non-spam domains carry exact-match commercial / geo money anchors (e.g. 'Expert Landscape Designers Winston-Salem NC', 'Best Nursery in Greensboro NC'), many on a cluster of social-bookmarking sites (atozbookmarks.net, sharedbookmark.net, instabookmarking.com, bookmarkhaven.com ...). That footprint is consistent with a COMMISSIONED/paid bookmarking link package. The link data cannot prove it was commissioned - confirm with the client and any previous SEO agency. All are held in Tab 05 (of these, only the {dom_count.get('Held (Pending Partner)',0):,} dofollow ones could pass value; the {dom_count.get('Held (Nofollow, No Action)',0):,} nofollow ones are inert).",
 "MANUAL ACTION: cannot be confirmed from Ahrefs or any tool used here. A Google manual action appears ONLY in Google Search Console > Security & Manual Actions > Manual actions. It must be read directly in GSC. The traffic curve argues AGAINST a link penalty tied to this spam: the biggest organic decline (peak ~15.9k/mo May 2025 to ~1.8k by Jan 2026) PRE-DATES the spam, which points to an algorithmic/core-update or on-site cause.",
 "DISAVOW RECOMMENDATION: not warranted yet. File the Tab 07 disavow ONLY if (A) GSC shows a manual action for unnatural links, OR (B) the client/agency confirms the links were bought. Otherwise monitor; Google already discounts this kind of junk algorithmically, and a reflexive disavow risks dropping value from legitimate links.",
 "REVIEW BEFORE UPLOAD: the Tab 07 list is built mechanically (Ahrefs spam flag + at least one dofollow link). A few high-volume entries (c99.nl, semanticjuice.com, whosmypro.com) are SEO/recon TOOL scans, not link-farm attacks - harmless to disavow but they are NOT evidence of an attack. The genuine attack is the single-link .shop / .xyz / .store cluster.",
]
for fx in findings:
    c=put(ws,rr,1,fx,align=WRAP); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5); rr+=1
rr+=1
# anchor type profile
put(ws,rr,1,"Anchor text profile (top anchors by link volume)",bold=True,color=DARK); rr+=1
for c,h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains"],1):
    ws.cell(rr,c,h)
style_header(ws,4,rr); rr+=1
for t_ in ANCHOR_ORDER:
    put(ws,rr,1,t_)
    put(ws,rr,2,at_bl[t_],align=CENV)
    put(ws,rr,3,(at_bl[t_]/tot_anchor_bl if tot_anchor_bl else 0),align=CENV,numfmt="0.0%")
    put(ws,rr,4,at_rd[t_],align=CENV); rr+=1
note=put(ws,rr,1,"Notes: 'AS' column throughout = Ahrefs Domain Rating (DR, 0-100). 'Traffic' = estimated monthly organic visits. 'RD's' = referring domains linking to that domain. Source: Ahrefs live backlinks index, "+datetime.date.today().isoformat()+". Anchor-type profile above covers the top 250 anchors by link volume (long tail of single-use anchors excluded); status counts cover the FULL live referring-domain profile (1,693 domains). To action: in Tab 05 fill column F (Y/N) and column G (Keep/Disavow).",align=WRAP)
note.font=Font(name="Geist",size=8,italic=True,color="FF666666"); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5)

# ===== 2. Referring Domain Audit =====
ws = wb.create_sheet("Referring Domain Audit")
cols = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page","Linking Page Title","Source","IP","Disavow Line"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
widths=[36,24,7,10,9,10,11,20,9,9,12,45,40,40,9,15,28]
for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
indisavow={"Spam (Disavow)":"Yes","Held (Pending Partner)":"Held","Held (Nofollow, No Action)":"Held"}
order_rank={s:i for i,s in enumerate(STATUS_ORDER)}
rows_sorted=sorted(rows,key=lambda r:(order_rank.get(r["status"],9),-r["Backlinks"]))
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"])
    put(ws,i,3,round(r["AS"],1),align=CENV); put(ws,i,4,r["Backlinks"],align=CENV)
    put(ws,i,5,r["RDs"],align=CENV); put(ws,i,6,r["Traffic"],align=CENV)
    put(ws,i,7,indisavow.get(r["status"],"No"),align=CENV); put(ws,i,8,r["points_to"],align=CENV)
    put(ws,i,9,r["dofollow"],align=CENV); put(ws,i,10,r["nofollow"],align=CENV)
    put(ws,i,11,r["first_seen"],align=CENV)
    put(ws,i,12,r["anchor"],align=WRAP); put(ws,i,13,r["url_from"],align=WRAP); put(ws,i,14,r["title"],align=WRAP)
    put(ws,i,15,"Ahrefs",align=CENV); put(ws,i,16,r["ip"],align=CENV)
    put(ws,i,17,("domain:"+r["domain"]) if r["status"]=="Spam (Disavow)" else "")

# ===== 3. All Backlinks (one representative link per referring domain) =====
ws = wb.create_sheet("All Backlinks")
cols=["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type","Linking Page URL","Linking Page Title","Target URL"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
for i,w in enumerate([25,27,10,55,32,10,55,53,40],1): ws.column_dimensions[get_column_letter(i)].width=w
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"]); put(ws,i,3,"Ahrefs",align=CENV)
    put(ws,i,4,r["anchor"],align=WRAP); put(ws,i,5,r["atype"]); put(ws,i,6,r["link_type"],align=CENV)
    put(ws,i,7,r["url_from"],align=WRAP); put(ws,i,8,r["title"],align=WRAP); put(ws,i,9,r["url_to"],align=WRAP)
nrow=len(rows_sorted)+3
n=put(ws,nrow,1,"Note: shows the top representative backlink per referring domain (Ahrefs '1 per domain'). A domain may have additional links; per-domain link counts are in the Referring Domain Audit tab.",align=WRAP)
n.font=Font(name="Geist",size=8,italic=True,color="FF666666"); ws.merge_cells(start_row=nrow,start_column=1,end_row=nrow,end_column=9)

# ===== 4. Anchor Analysis =====
ws = wb.create_sheet("Anchor Analysis")
cols=["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
for i,w in enumerate([115,38,12,16,16,20],1): ws.column_dimensions[get_column_letter(i)].width=w
an_sorted=sorted(anchors,key=lambda a:-int(a["links_to_target"]))
for i,a in enumerate(an_sorted,2):
    put(ws,i,1,a["anchor"],align=WRAP); put(ws,i,2,classify_anchor(a["anchor"]))
    put(ws,i,3,int(a["links_to_target"]),align=CENV)
    put(ws,i,4,(int(a["links_to_target"])/tot_anchor_bl if tot_anchor_bl else 0),align=CENV,numfmt="0.0%")
    put(ws,i,5,int(a["refdomains"]),align=CENV)
    put(ws,i,6,int(a["refdomains"]) if bl(a.get("is_spam")) else 0,align=CENV)

# ===== 5. Exact Match Anchors (held / possibly commissioned) =====
ws = wb.create_sheet("Exact Match Anchors")
cols=["Referring domain","Example backlink (linking page)","Exact-match commercial anchor","Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
for i,w in enumerate([25,59,53,16,25,22,16],1): ws.column_dimensions[get_column_letter(i)].width=w
held=[r for r in rows if r["status"] in ("Held (Pending Partner)","Held (Nofollow, No Action)")]
held.sort(key=lambda r:(-r["dofollow"],-r["Backlinks"]))
for i,r in enumerate(held,2):
    m=GEO.search(r["anchor"]); market=m.group(0).title() if m else "Non-geo"
    put(ws,i,1,r["domain"]); put(ws,i,2,r["url_from"],align=WRAP); put(ws,i,3,r["anchor"],align=WRAP)
    put(ws,i,4,market,align=CENV); put(ws,i,5,"Directory / blog (review source quality)")
    put(ws,i,6,"",align=CENV); put(ws,i,7,"")
if not held:
    put(ws,2,1,"(none)");
nrow=len(held)+3
n=put(ws,nrow,1,"HOW TO USE: these carry exact-match commercial anchors and may be commissioned placements. Ask the client / previous SEO partner whether each was paid for. Fill column F with Y or N, and column G with Keep (partner claims it / legitimate) or Disavow (unclaimed + low quality). Nofollow rows pass no value and need no action regardless of answer.",align=WRAP)
n.font=Font(name="Geist",size=8,italic=True,color="FF666666"); ws.merge_cells(start_row=nrow,start_column=1,end_row=nrow,end_column=7)

# ===== 6. Pending Disavow Lines =====
ws = wb.create_sheet("Pending Disavow Lines")
cols=["Referring domain","Disavow line (append to disavow_newgarden.txt once confirmed)","Recommendation"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
for i,w in enumerate([32,52,60],1): ws.column_dimensions[get_column_letter(i)].width=w
held_follow=[r for r in rows if r["status"]=="Held (Pending Partner)"]
held_follow.sort(key=lambda r:r["domain"])
for i,r in enumerate(held_follow,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,"domain:"+r["domain"])
    put(ws,i,3,"Append ONLY if the previous SEO partner does not confirm this was a commissioned placement.",align=WRAP)
if not held_follow: put(ws,2,1,"(none)")

# ===== 7. Disavow List =====
ws = wb.create_sheet("Disavow List")
cols=["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"
for i,w in enumerate([44,10,12,12,11,15,90],1): ws.column_dimensions[get_column_letter(i)].width=w
disavow=[r for r in rows if r["status"]=="Spam (Disavow)"]
disavow.sort(key=lambda r:-r["Backlinks"])
# header comment lines (2 info rows then data) -> keep simple: data from row2
for i,r in enumerate(disavow,2):
    put(ws,i,1,"domain:"+r["domain"]); put(ws,i,2,round(r["AS"],1),align=CENV)
    put(ws,i,3,r["Backlinks"],align=CENV); put(ws,i,4,r["RDs"],align=CENV)
    put(ws,i,5,r["Traffic"],align=CENV); put(ws,i,6,r["orgkw"],align=CENV)
    put(ws,i,7,r["anchor"],align=WRAP)
if not disavow: put(ws,2,1,"(none)")

wb.save(OUT)
print("SAVED", OUT)
print("domains:",tot_dom,"backlinks(sum):",tot_bl)
for s in STATUS_ORDER: print(f"  {s}: {dom_count.get(s,0)} dom / {bl_count.get(s,0)} bl")
print("disavow-list rows:",len(disavow),"| held rows:",len(held),"| pending-follow:",len(held_follow))

# also write the ready-to-upload disavow txt
with open("/home/user/test/disavow_newgarden.txt","w") as f:
    f.write("# Disavow file for newgarden.com - DRAFT / conditional\n")
    f.write(f"# Generated {datetime.date.today().isoformat()} from Ahrefs live referring domains flagged spam with >=1 dofollow link.\n")
    f.write("# DO NOT UPLOAD unless GSC shows a manual action for unnatural links, or bought links are confirmed. See Summary tab.\n")
    for r in disavow:
        f.write("domain:"+r["domain"]+"\n")
print("wrote disavow_newgarden.txt")
