#!/usr/bin/env python3
"""Build newgarden.com backlinks audit (SEMRUSH source) in the K&K template format.
Source: Semrush UI CSV exports (refdomains_full.csv, backlinks_full.csv).
Only Semrush metrics: AS = Semrush Authority Score (Domain ascore), Tool/Source = Semrush.
Semrush's referring-domains export has no per-domain RD count or organic traffic, so those two
template columns are left blank. Spam is derived from anchor patterns + link-farm TLDs
(Semrush has no spam flag). Anchor Analysis is aggregated from the full 8,086-backlink export."""
import csv, re, datetime, os
from urllib.parse import urlparse
from collections import defaultdict, Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

DATA="/home/user/test/data_semrush"
OUT="/home/user/test/NewGarden_Backlinks_Audit.xlsx"
TARGET="newgarden.com"
csv.field_size_limit(10_000_000)

def load(p):
    with open(p,newline="") as f: return list(csv.DictReader(f))
refdomains=load(f"{DATA}/refdomains_full.csv")      # Domain ascore,Domain,Backlinks,IP Address,Country,First seen,Last seen
backlinks =load(f"{DATA}/backlinks_full.csv")       # Page ascore,Source title,Source url,Target url,Anchor,External links,Internal links,Nofollow,Sponsored,Ugc,Text,Frame,Form,Image,Sitewide,First seen,Last seen,New link,Lost link

def num(v,cast=float,d=0):
    try:
        if v is None or str(v).strip()=="" : return d
        return cast(float(v))
    except Exception: return d
def asdate(s):
    try: return datetime.datetime.strptime(str(s)[:10],"%Y-%m-%d").date()
    except Exception: return s
def is_nofollow(b): return str(b.get("Nofollow","")).strip().lower()=="true"

# ---------- anchor-type classifier ----------
GEO=re.compile(r"\b(greensboro|winston[- ]?salem|high point|summerfield|kernersville|oak ridge|browns summit|north carolina|\bn\.?c\.?\b)\b",re.I)
SERVICE=re.compile(r"\b(landscap\w*|lawn|nursery|garden center|garden centre|hardscap\w*|irrigation|mulch\w*|patio|maintenance|tree service|plant(ing)? service|design (and|&) build)\b",re.I)
SPAMCOPY=re.compile(r"(back\s?link|\bseo\b|\bpbn\b|do[- ]?follow|dofollow|domain rating|\bdr[\s\-]?\d|\bda\b\s?\d|\btf\b|rank(ing|s)?\b|link[- ]build|guest post|niche edit|\bserp\b|index(ation|ing)|citation flow|trust flow|outrank|link velocity|anchor text|white[- ]hat|tier(ed|\s?1)|authority (backlink|link)|buy .{0,15}link|premium .{0,15}(backlink|link)|traffic (surge|boost)|web traffic|t\.me/|telegram|happygrannypies|darksidelinks|boost .{0,20}(rank|authority|traffic|dr|da))",re.I)
IMGSPAM=re.compile(r"ссылка на источник|источник изображени|image source",re.I)
URLISH=re.compile(r"^\s*(https?://|www\.)|^\s*[a-z0-9][a-z0-9.\-]*\.(com|org|net|info|io|co|us|store|shop|xyz|site|online|me|biz|ru)(/\S*)?\s*$",re.I)
BRAND=re.compile(r"new\s?garden",re.I)
GENERIC={"website","visit website","visit site","source","go now","more like this","click here","read more","learn more","here","link","more","view","this website","visit","website link","go","see more","website ↗"}
FARM_TLDS={"shop","xyz","store","online","site","space","click","link","buzz","top","fun","sbs","icu","cfd","lol","bond"}

def classify_anchor(a):
    if a is None: a=""
    a=a.strip()
    if a=="" or a=="<EmptyAnchor>": return "Empty or image"
    if SPAMCOPY.search(a) or IMGSPAM.search(a): return "Spam: keyword stuffed SEO sales copy"
    if URLISH.match(a) and " " not in a.strip(): return "Naked URL"
    if a.lower() in GENERIC: return "Generic"
    if BRAND.search(a): return "Branded"
    iss=bool(SERVICE.search(a)); isg=bool(GEO.search(a))
    pl=bool(re.search(r"\(([A-Z][a-z]+ [a-z]+|[A-Z][a-z]+ ')",a)) or "plants.newgarden" in a.lower() or re.search(r"camellia|magnolia|hydrangea|maple|yucca|boxwood|agave|pine|redwood|verbascum|gaura|sarcococca|ipomoea|stachys|cherry",a.lower())
    if iss and not pl: return "Exact match commercial (geo)" if isg else "Exact match commercial"
    if pl: return "Contextual or other"
    return "Contextual or other"
COMMERCIAL={"Exact match commercial","Exact match commercial (geo)"}

# ---------- map backlinks to referring domains ----------
refset=set((r["Domain"] or "").strip().lower() for r in refdomains)
def root_of(host):
    host=(host or "").lower().strip()
    if host.startswith("www."): host=host[4:]
    if host in refset: return host
    labels=host.split(".")
    for n in (2,3):
        if len(labels)>=n and ".".join(labels[-n:]) in refset: return ".".join(labels[-n:])
    for d in refset:
        if host==d or host.endswith("."+d): return d
    return ".".join(labels[-2:]) if len(labels)>=2 else host

agg=defaultdict(lambda:{"df":0,"nf":0,"anchors":[],"rep":None,"rep_score":-1})
anchor_agg=defaultdict(lambda:{"bl":0,"doms":set()})
for b in backlinks:
    host=urlparse(b.get("Source url","")).netloc
    d=root_of(host)
    g=agg[d]
    if is_nofollow(b): g["nf"]+=1
    else:              g["df"]+=1
    an=(b.get("Anchor") or "").strip()
    g["anchors"].append(an)
    sc=num(b.get("Page ascore"))
    if sc>g["rep_score"]: g["rep_score"]=sc; g["rep"]=b
    anchor_agg[an]["bl"]+=1; anchor_agg[an]["doms"].add(d)

anchors=[{"anchor":a,"backlinks_num":v["bl"],"domains_num":len(v["doms"])} for a,v in anchor_agg.items()]

# ---------- per-domain rows ----------
def host_target(url):
    h=urlparse(url or "").netloc.lower(); return h or TARGET
rows=[]
for r in refdomains:
    d=(r["Domain"] or "").strip().lower()
    if not d: continue
    g=agg.get(d,{"df":0,"nf":0,"anchors":[],"rep":None})
    rep=g["rep"] or {}
    anchor=(rep.get("Anchor") or "").strip()
    atype=classify_anchor(anchor)
    tld=d.rsplit(".",1)[-1]
    as_score=int(num(r.get("Domain ascore"),int))
    anchors_spam=any(classify_anchor(a)=="Spam: keyword stuffed SEO sales copy" for a in g["anchors"])
    # A sales-copy anchor is spam at any authority. A link-farm TLD on its own only counts as
    # spam when Authority Score is low (<20); higher-AS farm-TLD domains need a spam anchor.
    spam = anchors_spam or (tld in FARM_TLDS and as_score < 20)
    bk=int(num(r.get("Backlinks"),int))
    df=g["df"]; nf=g["nf"]
    if df==0 and nf==0: df=bk
    if spam and df>0:            status="Spam (Disavow)"
    elif spam and df==0:         status="Spam (Nofollow, No Action)"
    elif (not spam) and atype in COMMERCIAL and df>0:  status="Held (Pending Partner)"
    elif (not spam) and atype in COMMERCIAL and df==0: status="Held (Nofollow, No Action)"
    else:                        status="Keep"
    rows.append({
        "domain":d,"status":status,"AS":as_score,"Backlinks":bk,
        "dofollow":df,"nofollow":nf,"first_seen":asdate(r.get("First seen")),
        "anchor":anchor,"atype":atype,
        "url_from":rep.get("Source url",""),"title":rep.get("Source title",""),"url_to":rep.get("Target url",""),
        "points_to":host_target(rep.get("Target url","")),"ip":(r.get("IP Address") or "").strip(),
        "link_type":"Dofollow" if (rep and not is_nofollow(rep)) else ("Nofollow" if rep else ("Dofollow" if df>0 else "Nofollow")),
    })

STATUS_ORDER=["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)","Spam (Nofollow, No Action)","Keep","Own Site"]
STATUS_MEANING={
 "Spam (Disavow)":"Spam referring domain (link-scheme anchor or link-farm TLD) with at least one dofollow link. Included in the disavow-ready file.",
 "Held (Pending Partner)":"Non-spam domain with an exact-match commercial / geo anchor that MAY have been a commissioned placement. Held out of the disavow file until the client / previous SEO partner confirms.",
 "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 "Spam (Nofollow, No Action)":"Spam domain, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 "Keep":"Genuine, branded or harmless link (incl. editorial citations and the plants.newgarden.com catalogue). Keep.",
 "Own Site":"Client-owned domain that redirects into the site.",
}
dom_count=Counter(); bl_count=Counter()
for r in rows: dom_count[r["status"]]+=1; bl_count[r["status"]]+=r["Backlinks"]
tot_dom=sum(dom_count.values()); tot_bl=sum(bl_count.values())
spam_dom=dom_count.get("Spam (Disavow)",0)+dom_count.get("Spam (Nofollow, No Action)",0)

at_bl=defaultdict(int); at_rd=defaultdict(int)
tot_anchor_bl=sum(a["backlinks_num"] for a in anchors) or 1
for a in anchors:
    t=classify_anchor(a["anchor"]); at_bl[t]+=a["backlinks_num"]; at_rd[t]+=a["domains_num"]
ANCHOR_ORDER=sorted(at_bl,key=lambda k:-at_bl[k])

# ======================= styling =======================
HEAD_FILL=PatternFill("solid",fgColor="FF0C343D"); WHITE_FILL=PatternFill("solid",fgColor="FFFFFFFF")
WHITE="FFFFFFFF"; DARK="FF0C343D"
def headfont(sz=9): return Font(name="Geist",size=sz,bold=True,color=WHITE)
def cellfont(sz=9,bold=False,color="FF000000"): return Font(name="Geist",size=sz,bold=bold,color=color)
CEN=Alignment(horizontal="center",vertical="center",wrap_text=True); CENV=Alignment(horizontal="center",vertical="center")
LEFT=Alignment(vertical="center"); WRAP=Alignment(wrap_text=True,vertical="center")
thin=Side(style="thin",color="FFBFBFBF"); BORDER=Border(left=thin,right=thin,top=thin,bottom=thin)
TPL_WIDTHS={
 "Summary":{'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120.0},
 "Referring Domain Audit":{'A':36.0,'B':24.71,'C':9.57,'D':13.0,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14.0,'J':8.71,'K':12.0,'L':45.0,'M':8.71,'N':40.0,'O':14.0,'P':15.0,'Q':14.0},
 "All Backlinks":{'A':25.43,'B':27.14,'C':14.71,'D':55.0,'E':32.0,'F':10.0,'G':55.0,'H':53.14,'I':30.57},
 "Anchor Analysis":{'A':115.86,'B':37.71,'C':14.0,'D':8.71,'E':13.0,'F':20.29},
 "Exact Match Anchors":{'A':25.43,'B':59.0,'C':53.14,'D':16.0,'E':24.57,'F':15.43,'G':15.0},
 "Pending Disavow Lines":{'A':32.0,'B':44.0,'C':48.0},
 "Disavow List":{'A':44.0,'B':14.0,'C':15.57,'D':14.0,'E':11.14,'F':14.86,'G':98.86},
}
def apply_widths(ws):
    for L,w in TPL_WIDTHS.get(ws.title,{}).items(): ws.column_dimensions[L].width=w
def style_header(ws,ncol,row=1,size=9):
    for c in range(1,ncol+1):
        cell=ws.cell(row,c); cell.font=headfont(size); cell.fill=HEAD_FILL; cell.alignment=CEN; cell.border=BORDER
def put(ws,r,c,v,bold=False,align=None,numfmt=None,color="FF000000",fill=False,border=False):
    cell=ws.cell(r,c,v); cell.font=cellfont(bold=bold,color=color); cell.alignment=align or LEFT
    if numfmt: cell.number_format=numfmt
    if fill: cell.fill=WHITE_FILL
    if border: cell.border=BORDER
    return cell

wb=openpyxl.Workbook()

# ===== Summary =====
ws=wb.active; ws.title="Summary"; apply_widths(ws)
t=ws.cell(1,2,"New Garden Landscaping & Nursery"); t.font=Font(name="Geist",size=21,bold=True,color=DARK); t.alignment=Alignment(horizontal="left",vertical="center")
if os.path.exists("assets/harbinger_logo.png"):
    _lg=XLImage("assets/harbinger_logo.png"); _lg.width=196; _lg.height=58; ws.add_image(_lg,"A1")
hdr_row=3
for c,h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"],1): ws.cell(hdr_row,c,h)
style_header(ws,5,hdr_row,size=10)
rr=hdr_row+1
for s in STATUS_ORDER:
    put(ws,rr,1,s,align=LEFT,fill=True,border=True)
    put(ws,rr,2,dom_count.get(s,0),align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,3,bl_count.get(s,0),align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,4,(dom_count.get(s,0)/tot_dom if tot_dom else 0),align=CENV,numfmt="0.0%",fill=True,border=True)
    put(ws,rr,5,STATUS_MEANING[s],align=WRAP,fill=True,border=True); rr+=1
put(ws,rr,1,"Total",bold=True,fill=True,border=True); put(ws,rr,2,tot_dom,bold=True,align=CENV,numfmt="#,##0",fill=True,border=True)
put(ws,rr,3,tot_bl,bold=True,align=CENV,numfmt="#,##0",fill=True,border=True); put(ws,rr,4,1.0,bold=True,align=CENV,numfmt="0.0%",fill=True,border=True); put(ws,rr,5,"",fill=True,border=True); rr+=2

put(ws,rr,1,"Key findings",bold=True,color=DARK); rr+=1
dh=dom_count.get('Held (Pending Partner)',0)+dom_count.get('Held (Nofollow, No Action)',0)
findings=[
 f"{spam_dom:,} of {tot_dom:,} referring domains are spam. {dom_count.get('Spam (Disavow)',0):,} have a dofollow link and go in the disavow file; {dom_count.get('Spam (Nofollow, No Action)',0):,} are nofollow and can be ignored.",
 "The spam is recent and large. One campaign anchor, \"build powerful website authority with premium seo backlinks newgarden.com\", appears on over 1,400 domains alone.",
 "Most spam links use SEO sales-copy anchors that name the site, or sit on throwaway link-farm domains. This is auto-generated spam, not links the client bought.",
 f"{dh:,} domains use local service anchors (e.g. \"Landscape Maintenance Services Greensboro NC\"). These may be a paid package - confirm in Tab 05.",
 "No manual action is visible in this data - check Google Search Console. Review the disavow list before uploading.",
 "Disavow only if Search Console shows a manual action, or the client confirms buying links. Otherwise just monitor.",
]
for fx in findings:
    put(ws,rr,1,fx,align=WRAP); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5); rr+=1
rr+=1
put(ws,rr,1,"Anchor text profile (all backlinks)",bold=True,color=DARK); rr+=1
for c,h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains"],1): ws.cell(rr,c,h)
style_header(ws,4,rr,size=10); rr+=1
for t_ in ANCHOR_ORDER:
    put(ws,rr,1,t_,fill=True,border=True)
    put(ws,rr,2,at_bl[t_],align=CENV,numfmt="#,##0",fill=True,border=True)
    put(ws,rr,3,(at_bl[t_]/tot_anchor_bl),align=CENV,numfmt="0.0%",fill=True,border=True)
    put(ws,rr,4,at_rd[t_],align=CENV,numfmt="#,##0",fill=True,border=True); rr+=1
note=put(ws,rr,1,"Source: Semrush Backlink Analytics export, "+datetime.date.today().isoformat()+" ("+format(len(backlinks),",")+" backlinks / "+format(tot_dom,",")+" referring domains). 'AS' = Semrush Authority Score (0-100). Semrush's referring-domains export has no per-domain referring-domain count or organic traffic, so the \"RD's\" and \"Traffic\" columns in Tab 02 are left blank. Anchor-type profile covers all backlinks; status counts cover the full profile. Tab 05: fill column F (Y/N) and column G (Keep/Disavow).",align=WRAP)
note.font=Font(name="Geist",size=8,italic=True,color="FF666666"); ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5)

order_rank={s:i for i,s in enumerate(STATUS_ORDER)}
rows_sorted=sorted(rows,key=lambda r:(order_rank.get(r["status"],9),-r["Backlinks"]))

# ===== Referring Domain Audit =====
ws=wb.create_sheet("Referring Domain Audit")
cols=["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page","Linking Page Title","Source","IP","Disavow Line"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
indisavow={"Spam (Disavow)":"Yes","Held (Pending Partner)":"Held","Held (Nofollow, No Action)":"Held"}
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"]); put(ws,i,3,r["AS"],align=CENV)
    put(ws,i,4,r["Backlinks"],align=CENV,numfmt="#,##0"); put(ws,i,5,"",align=CENV,numfmt="#,##0"); put(ws,i,6,"",align=CENV,numfmt="#,##0")
    put(ws,i,7,indisavow.get(r["status"],"No"),align=CENV); put(ws,i,8,r["points_to"],align=CENV)
    put(ws,i,9,r["dofollow"],align=CENV); put(ws,i,10,r["nofollow"],align=CENV)
    put(ws,i,11,r["first_seen"],align=CENV,numfmt="d mmm yyyy")
    put(ws,i,12,r["anchor"],align=LEFT); put(ws,i,13,r["url_from"],align=LEFT); put(ws,i,14,r["title"],align=LEFT)
    put(ws,i,15,"Semrush",align=CENV); put(ws,i,16,r["ip"],align=CENV)
    put(ws,i,17,("domain:"+r["domain"]) if r["status"]=="Spam (Disavow)" else "")

# ===== All Backlinks (top representative link per referring domain) =====
ws=wb.create_sheet("All Backlinks")
cols=["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type","Linking Page URL","Linking Page Title","Target URL"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
for i,r in enumerate(rows_sorted,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,r["status"]); put(ws,i,3,"Semrush",align=CENV)
    put(ws,i,4,r["anchor"],align=LEFT); put(ws,i,5,r["atype"]); put(ws,i,6,r["link_type"],align=CENV)
    put(ws,i,7,r["url_from"],align=LEFT); put(ws,i,8,r["title"],align=LEFT); put(ws,i,9,r["url_to"],align=LEFT)

# ===== Anchor Analysis =====
ws=wb.create_sheet("Anchor Analysis")
cols=["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
an_sorted=sorted(anchors,key=lambda a:-a["backlinks_num"])
for i,a in enumerate(an_sorted,2):
    at=classify_anchor(a["anchor"])
    put(ws,i,1,a["anchor"],align=LEFT); put(ws,i,2,at)
    put(ws,i,3,a["backlinks_num"],align=CENV,numfmt="#,##0")
    put(ws,i,4,(a["backlinks_num"]/tot_anchor_bl),align=CENV,numfmt="0.00%")
    put(ws,i,5,a["domains_num"],align=CENV)
    put(ws,i,6,a["domains_num"] if at=="Spam: keyword stuffed SEO sales copy" else 0,align=CENV)

# ===== Exact Match Anchors =====
ws=wb.create_sheet("Exact Match Anchors")
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
if not held: put(ws,2,1,"(none)")

# ===== Pending Disavow Lines =====
ws=wb.create_sheet("Pending Disavow Lines")
cols=["Referring domain","Disavow line (append to disavow_newgarden.txt once confirmed)","Recommendation"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
held_follow=[r for r in rows if r["status"]=="Held (Pending Partner)"]; held_follow.sort(key=lambda r:r["domain"])
for i,r in enumerate(held_follow,2):
    put(ws,i,1,r["domain"]); put(ws,i,2,"domain:"+r["domain"])
    put(ws,i,3,"Append ONLY if the previous SEO partner does not confirm this was a commissioned placement.",align=LEFT)
if not held_follow: put(ws,2,1,"(none)")

# ===== Disavow List =====
ws=wb.create_sheet("Disavow List")
cols=["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
for c,h in enumerate(cols,1): ws.cell(1,c,h)
style_header(ws,len(cols)); ws.freeze_panes="B2"; apply_widths(ws)
disavow=[r for r in rows if r["status"]=="Spam (Disavow)"]; disavow.sort(key=lambda r:-r["Backlinks"])
for i,r in enumerate(disavow,2):
    put(ws,i,1,"domain:"+r["domain"]); put(ws,i,2,r["AS"],align=CENV)
    put(ws,i,3,r["Backlinks"],align=CENV,numfmt="#,##0"); put(ws,i,4,"",align=CENV,numfmt="#,##0"); put(ws,i,5,"",align=CENV,numfmt="#,##0")
    put(ws,i,6,"",align=CENV,numfmt="#,##0"); put(ws,i,7,r["anchor"],align=LEFT)
if not disavow: put(ws,2,1,"(none)")

for ws in wb.worksheets:
    if ws.title=="Summary":
        ws.sheet_view.showGridLines=False
        for r in range(1,ws.max_row+1): ws.row_dimensions[r].height=22.5
    else:
        ncol=ws.max_column
        for r in range(2,ws.max_row+1):
            for c in range(1,ncol+1):
                cell=ws.cell(r,c)
                if not (cell.fill and cell.fill.patternType): cell.fill=WHITE_FILL
        ws.auto_filter.ref=f"A1:{get_column_letter(ncol)}{ws.max_row}"
        ws.row_dimensions[1].height=31.5
        ws.sheet_format.defaultRowHeight=15.75; ws.sheet_format.customHeight=True

wb.save(OUT)
print("SAVED",OUT,"| domains:",tot_dom,"| backlinks(sum):",tot_bl)
for s in STATUS_ORDER: print(f"  {s}: {dom_count.get(s,0)} dom / {bl_count.get(s,0)} bl")
with open("/home/user/test/disavow_newgarden.txt","w") as f:
    f.write("# Disavow file for newgarden.com - DRAFT / conditional (source: Semrush)\n")
    f.write(f"# Generated {datetime.date.today().isoformat()}. Spam referring domains with >=1 dofollow link.\n")
    f.write("# DO NOT UPLOAD unless GSC shows a manual action, or bought links are confirmed. See Summary tab.\n")
    for r in disavow: f.write("domain:"+r["domain"]+"\n")
print("disavow lines:",len(disavow),"| held:",len(held))
