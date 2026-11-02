#!/usr/bin/env python3
"""Build newgarden.com backlinks audit workbook in the K&K template format."""
import csv, json, re, datetime, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

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
def asdate(s):
    try: return datetime.datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except Exception: return s

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
WHITE_FILL = PatternFill("solid", fgColor="FFFFFFFF")
WHITE = "FFFFFFFF"; DARK="FF0C343D"
def headfont(sz=9): return Font(name="Geist", size=sz, bold=True, color=WHITE)
def cellfont(sz=9, bold=False, color="FF000000"): return Font(name="Geist", size=sz, bold=bold, color=color)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)   # header cells
CENV= Alignment(horizontal="center", vertical="center")                    # numeric / short data (vcenter)
LEFT= Alignment(vertical="center")                                         # text data: default horiz, vcenter, NO wrap (template style)
WRAP= Alignment(wrap_text=True, vertical="center")                         # summary 'meaning' / findings / notes (wrap)
thin = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=thin,right=thin,top=thin,bottom=thin)

# exact template column widths per tab
TPL_WIDTHS = {
 "Summary": {'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120.0},
 "Referring Domain Audit": {'A':36.0,'B':24.71,'C':9.57,'D':13.0,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14.0,'J':8.71,'K':12.0,'L':45.0,'M':8.71,'N':40.0,'O':14.0,'P':15.0,'Q':14.0},
 "All Backlinks": {'A':25.43,'B':27.14,'C':14.71,'D':55.0,'E':32.0,'F':10.0,'G':55.0,'H':53.14,'I':30.57},
 "Anchor Analysis": {'A':115.86,'B':37.71,'C':14.0,'D':8.71,'E':13.0,'F':20.29},
 "Exact Match Anchors": {'A':25.43,'B':59.0,'C':53.14,'D':16.0,'E':24.57,'F':15.43,'G':15.0},
 "Pending Disavow Lines": {'A':32.0,'B':44.0,'C':48.0},
 "Disavow List": {'A':44.0,'B':14.0,'C':15.57,'D':14.0,'E':11.14,'F':14.86,'G':98.86},
}
def apply_widths(ws):
    for L,w in TPL_WIDTHS.get(ws.title,{}).items():
        ws.column_dimensions[L].width = w

def style_header(ws, ncol, row=1, size=9):
    for c in range(1, ncol+1):
        cell = ws.cell(row, c)
        cell.font = headfont(size); cell.fill = HEAD_FILL; cell.alignment = CEN; cell.border = BORDER

def put(ws, r, c, v, bold=False, align=None, numfmt=None, color="FF000000", fill=False, border=False):
    cell = ws.cell(r, c, v)
    cell.font = cellfont(bold=bold, color=color)
    cell.alignment = align or LEFT
    if numfmt: cell.number_format = numfmt
    if fill: cell.fill = WHITE_FILL
    if border: cell.border = BORDER
    return cell

wb = openpyxl.Workbook()

# ===== 1. Summary =====
ws = wb.active; ws.title = "Summary"
apply_widths(ws)
# client name in B1 (same cell the template uses), left-aligned past the logo so it never overlaps it
t = ws.cell(1,2,"New Garden Landscaping & Nursery"); t.font=Font(name="Geist",size=21,bold=True,color=DARK)
t.alignment=Alignment(horizontal="left", vertical="center")
# agency logo at A1 (same image/size/position as template)
if os.path.exists("assets/harbinger_logo.png"):
    _lg=XLImage("assets/harbinger_logo.png"); _lg.width=196; _lg.height=58
    ws.add_image(_lg,"A1")
# status table (header row 3, matching template)
hdr_row=3
for c,h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"],1):
    ws.cell(hdr_row,c,h)
style_header(ws,5,hdr_row,size=10)
rr=hdr_row+1
for s in STATUS_ORDER:
    put(ws,rr,1,s,align=LEFT,fill=True,border=True)
    put(ws,rr,2,dom_count.get(s,0),align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,3,bl_count.get(s,0),align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,4,(dom_count.get(s,0)/tot_dom if tot_dom else 0),align=CENV,numfmt="0.0%",fill=True,border=True)
    put(ws,rr,5,STATUS_MEANING[s],align=WRAP,fill=True,border=True)
    rr+=1
put(ws,rr,1,"Total",bold=True,fill=True,border=True); put(ws,rr,2,tot_dom,bold=True,align=CENV,numfmt="#,##0",fill=True,border=True); put(ws,rr,3,tot_bl,bold=True,align=CENV,numfmt="#,##0",fill=True,border=True)
put(ws,rr,4,1.0,bold=True,align=CENV,numfmt="0.0%",fill=True,border=True); put(ws,rr,5,"",fill=True,border=True); rr+=2

spam_dom = dom_count.get("Spam (Disavow)",0)+dom_count.get("Spam (Nofollow, No Action)",0)
put(ws,rr,1,"Key findings",bold=True,color=DARK); rr+=1
dh = dom_count.get('Held (Pending Partner)',0)+dom_count.get('Held (Nofollow, No Action)',0)
findings = [
 f"{spam_dom:,} of {tot_dom:,} referring domains are spam. {dom_count.get('Spam (Disavow)',0):,} have a dofollow link and go in the disavow file; {dom_count.get('Spam (Nofollow, No Action)',0):,} are nofollow and can be ignored.",
 "The spam is recent - it jumped from about 470 domains in early 2026 to 1,780 by September.",
 "Most spam links use SEO sales-copy anchors that name the site. This is auto-generated spam, not links the client bought.",
 f"{dh:,} domains use local service anchors (e.g. \"Landscape Designers Winston-Salem NC\"). These may be a paid package - confirm in Tab 05.",
 "No manual action is visible here - check Google Search Console. The big traffic drop came before the spam, so the spam is likely not the cause.",
 "Disavow only if Search Console shows a manual action, or the client confirms buying links. Otherwise just monitor.",
 "A few top disavow domains (c99.nl, semanticjuice.com) are SEO tools, not attack sites.",
]
for fx in findings:
    c=put(ws,rr,1,fx,align=WRAP); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5); rr+=1
rr+=1
# anchor type profile
put(ws,rr,1,"Anchor text profile (top anchors by link volume)",bold=True,color=DARK); rr+=1
for c,h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains"],1):
    ws.cell(rr,c,h)
style_header(ws,4,rr,size=10); rr+=1
for t_ in ANCHOR_ORDER:
    put(ws,rr,1,t_,fill=True,border=True)
    put(ws,rr,2,at_bl[t_],align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,3,(at_bl[t_]/tot_anchor_bl if tot_anchor_bl else 0),align=CENV,numfmt="0.0%",fill=True,border=True)
    put(ws,rr,4,at_rd[t_],align=CENV,numfmt="#,##0",fill=True,border=True); rr+=1
note=put(ws,rr,1,"Notes: 'AS' column throughout = Ahrefs Domain Rating (DR, 0-100). 'Traffic' = estimated monthly organic visits. 'RD's' = referring domains linking to that domain. Source: Ahrefs live backlinks index, "+datetime.date.today().isoformat()+". Anchor-type profile above covers the top 250 anchors by link volume (long tail of single-use anchors excluded); status counts cover the FULL live referring-domain profile (1,693 domains). Tab 03 (All Backlinks) shows the top representative link per referring domain; per-domain link counts are in Tab 02. To action Tab 05: fill column F (Y/N = was it a paid placement) and column G (Keep or Disavow).",align=WRAP)
note.font=Font(name="Geist",size=8,italic=True,color="FF666666"); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5)

# ===== 2. Referring Domain Audit =====
ws = wb.create_sheet("Referring Domain Audit")
cols = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page","Linking Page Title","Source","IP","Disavow Line"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
indisavow={"Spam (Disavow)":"Yes","Held (Pending Partner)":"Held","Held (Nofollow, No Action)":"Held"}
order_rank={s:i for i,s in enumerate(STATUS_ORDER)}
rows_sorted=sorted(rows,key=lambda r:(order_rank.get(r["status"],9),-r["Backlinks"]))
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"])
    put(ws,i,3,round(r["AS"],1),align=CENV); put(ws,i,4,r["Backlinks"],align=CENV,numfmt="#,##0")
    put(ws,i,5,r["RDs"],align=CENV,numfmt="#,##0"); put(ws,i,6,r["Traffic"],align=CENV,numfmt="#,##0")
    put(ws,i,7,indisavow.get(r["status"],"No"),align=CENV); put(ws,i,8,r["points_to"],align=CENV)
    put(ws,i,9,r["dofollow"],align=CENV); put(ws,i,10,r["nofollow"],align=CENV)
    put(ws,i,11,asdate(r["first_seen"]),align=CENV,numfmt="d mmm yyyy")
    put(ws,i,12,r["anchor"],align=LEFT); put(ws,i,13,r["url_from"],align=LEFT); put(ws,i,14,r["title"],align=LEFT)
    put(ws,i,15,"Ahrefs",align=CENV); put(ws,i,16,r["ip"],align=CENV)
    put(ws,i,17,("domain:"+r["domain"]) if r["status"]=="Spam (Disavow)" else "")

# ===== 3. All Backlinks (one representative link per referring domain) =====
ws = wb.create_sheet("All Backlinks")
cols=["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type","Linking Page URL","Linking Page Title","Target URL"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"]); put(ws,i,3,"Ahrefs",align=CENV)
    put(ws,i,4,r["anchor"],align=LEFT); put(ws,i,5,r["atype"]); put(ws,i,6,r["link_type"],align=CENV)
    put(ws,i,7,r["url_from"],align=LEFT); put(ws,i,8,r["title"],align=LEFT); put(ws,i,9,r["url_to"],align=LEFT)

# ===== 4. Anchor Analysis =====
ws = wb.create_sheet("Anchor Analysis")
cols=["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
an_sorted=sorted(anchors,key=lambda a:-int(a["links_to_target"]))
for i,a in enumerate(an_sorted,2):
    put(ws,i,1,a["anchor"],align=LEFT); put(ws,i,2,classify_anchor(a["anchor"]))
    put(ws,i,3,int(a["links_to_target"]),align=CENV,numfmt="#,##0")
    put(ws,i,4,(int(a["links_to_target"])/tot_anchor_bl if tot_anchor_bl else 0),align=CENV,numfmt="0.00%")
    put(ws,i,5,int(a["refdomains"]),align=CENV)
    put(ws,i,6,int(a["refdomains"]) if bl(a.get("is_spam")) else 0,align=CENV)

# ===== 5. Exact Match Anchors (held / possibly commissioned) =====
ws = wb.create_sheet("Exact Match Anchors")
cols=["Referring domain","Example backlink (linking page)","Exact-match commercial anchor","Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
held=[r for r in rows if r["status"] in ("Held (Pending Partner)","Held (Nofollow, No Action)")]
held.sort(key=lambda r:(-r["dofollow"],-r["Backlinks"]))
for i,r in enumerate(held,2):
    m=GEO.search(r["anchor"]); market=m.group(0).title() if m else "Non-geo"
    put(ws,i,1,r["domain"]); put(ws,i,2,r["url_from"],align=LEFT); put(ws,i,3,r["anchor"],align=LEFT)
    put(ws,i,4,market,align=CENV); put(ws,i,5,"Directory / blog (review source quality)")
    put(ws,i,6,"",align=CENV); put(ws,i,7,"")
if not held:
    put(ws,2,1,"(none)")

# ===== 6. Pending Disavow Lines =====
ws = wb.create_sheet("Pending Disavow Lines")
cols=["Referring domain","Disavow line (append to disavow_newgarden.txt once confirmed)","Recommendation"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
held_follow=[r for r in rows if r["status"]=="Held (Pending Partner)"]
held_follow.sort(key=lambda r:r["domain"])
for i,r in enumerate(held_follow,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,"domain:"+r["domain"])
    put(ws,i,3,"Append ONLY if the previous SEO partner does not confirm this was a commissioned placement.",align=LEFT)
if not held_follow: put(ws,2,1,"(none)")

# ===== 7. Disavow List =====
ws = wb.create_sheet("Disavow List")
cols=["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
disavow=[r for r in rows if r["status"]=="Spam (Disavow)"]
disavow.sort(key=lambda r:-r["Backlinks"])
for i,r in enumerate(disavow,2):
    put(ws,i,1,"domain:"+r["domain"]); put(ws,i,2,round(r["AS"],1),align=CENV)
    put(ws,i,3,r["Backlinks"],align=CENV,numfmt="#,##0"); put(ws,i,4,r["RDs"],align=CENV,numfmt="#,##0")
    put(ws,i,5,r["Traffic"],align=CENV,numfmt="#,##0"); put(ws,i,6,r["orgkw"],align=CENV,numfmt="#,##0")
    put(ws,i,7,r["anchor"],align=LEFT)
if not disavow: put(ws,2,1,"(none)")

# Match template sheet-level styling:
for ws in wb.worksheets:
    if ws.title == "Summary":
        ws.sheet_view.showGridLines = False          # template hides gridlines on Summary only
        for r in range(1, ws.max_row+1):
            ws.row_dimensions[r].height = 22.5        # template Summary row height
    else:
        # white fill on every data cell (headers keep the dark fill)
        ncol = ws.max_column
        for r in range(2, ws.max_row+1):
            for c in range(1, ncol+1):
                cell = ws.cell(r, c)
                if not (cell.fill and cell.fill.patternType):
                    cell.fill = WHITE_FILL
        # autofilter across the full header+data range (template has this on every data tab)
        ws.auto_filter.ref = f"A1:{get_column_letter(ncol)}{ws.max_row}"
        ws.row_dimensions[1].height = 31.5            # taller header row, per template
        ws.sheet_format.defaultRowHeight = 15.75      # data rows, per template
        ws.sheet_format.customHeight = True

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
