#!/usr/bin/env python3
"""Build the 7-tab Harbinger workbook for elitewrecker.com, matching the signed
K&K template cell-for-cell (Geist, FF0C343D, header-only borders, logo), from the
intermediate CSVs produced by load_classify.py. Also writes disavow files.
All cells are literal values (the signed template uses literals, not formulas)."""
import csv, io, json, os, glob
from datetime import datetime
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D

BASE="/home/user/test/offsite-backlink-audit/elitewrecker"
OUT=BASE+"/out"
ACCENT="FF0C343D"
GEIST="Geist"
CLIENT_NAME="Elite Service Recovery & Towing"
MONEY_SITE="elitewrecker.com"

WHITE_FILL=PatternFill("solid",fgColor="FFFFFFFF")
ACC_FILL=PatternFill("solid",fgColor=ACCENT)
thin=Side(style="thin")
HDR_BORDER=Border(left=thin,right=thin,top=thin)       # no bottom (data tabs)
BOX=Border(left=thin,right=thin,top=thin,bottom=thin)  # summary small tables
NOBORDER=Border()

def hfont(sz=9): return Font(name=GEIST,size=sz,bold=True,color="FFFFFFFF")
def dfont(): return Font(name=GEIST,size=9,color="FF000000")
def wfont(): return Font(name=GEIST,size=9,color="FFFFFFFF")

def load_doms():
    rows=list(csv.DictReader(open(OUT+"/domains_classified.csv")))
    for r in rows:
        for k in ("traffic","keywords","dofollow","nofollow"):
            r[k]=int(r[k]) if r[k] not in ("",None) else 0
        r["as_n"]=None
        try: r["as_n"]=int(float(r["as"])) if r["as"] not in ("","None",None) else None
        except: r["as_n"]=None
        try: r["bl_n"]=int(float(r["backlinks"])) if r["backlinks"] not in ("",None) else 0
        except: r["bl_n"]=0
        try: r["rd_n"]=int(float(r["rds"])) if r["rds"] not in ("",None) else 0
        except: r["rd_n"]=0
    return rows

def d2date(s):
    s=(s or "").strip()
    if not s: return None
    try: return datetime.strptime(s[:10],"%Y-%m-%d")
    except: return None

def set_grid(ws,on=True): ws.sheet_view.showGridLines=on

def write_data_tab(wb,title,cols,rows,data_h):
    """cols: list of (header,width,align,numfmt,input_flag). rows: list of lists aligned to cols."""
    ws=wb.create_sheet(title)
    ncol=len(cols)
    for j,(hname,width,align,numfmt,inp) in enumerate(cols,1):
        c=ws.cell(row=1,column=j,value=hname)
        c.font=hfont(9); c.fill=ACC_FILL; c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
        c.border=HDR_BORDER
        ws.column_dimensions[get_column_letter(j)].width=width
    for i,rvals in enumerate(rows,2):
        for j,(hname,width,align,numfmt,inp) in enumerate(cols,1):
            v=rvals[j-1]
            c=ws.cell(row=i,column=j,value=v)
            if inp:
                c.font=wfont(); c.fill=ACC_FILL
            else:
                c.font=dfont(); c.fill=WHITE_FILL
            c.alignment=Alignment(horizontal=("center" if align=="c" else None),vertical="center")
            if numfmt: c.number_format=numfmt
            c.border=NOBORDER
    last=get_column_letter(ncol)
    nrow=len(rows)+1
    ws.freeze_panes="B2"
    ws.auto_filter.ref=f"A1:{last}{nrow}"
    set_grid(ws,True)
    ws.row_dimensions[1].height=31.5
    for i in range(2,nrow+1): ws.row_dimensions[i].height=data_h
    return ws

# ---------------- Site-type / market helpers for Exact Match Anchors ----------------
def market_of(anchor):
    al=(anchor or "").lower()
    for g in ("lake charles","lafayette","louisiana","sulphur","moss bluff"):
        if g in al: return g.title()
    return "Non-geo"
def sitetype_of(dom,title):
    d=dom.lower(); t=(title or "").lower()
    if any(x in d for x in ("directory","listing","listings","biz","dir.","findus","local")): return "Low quality web directory"
    if any(x in d for x in ("article","blog","news","post","wiki","content")): return "Article / blog network"
    if any(x in d for x in ("bookmark",)): return "Bookmarking site"
    if "press" in d or "pr." in d or "newswire" in d: return "Press release syndication"
    return "Low quality web / blog"

def main():
    doms=load_doms()
    stats=json.load(open(OUT+"/stats.json"))
    links=list(csv.DictReader(open(OUT+"/links_classified.csv")))
    anchors=list(csv.DictReader(open(OUT+"/anchor_analysis.csv")))

    by_status=defaultdict(list)
    for r in doms: by_status[r["status"]].append(r)
    STAT_ORDER=["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
                "Spam (Nofollow, No Action)","Keep","Own Site"]
    bl_by_status=stats["backlinks_by_status"]
    tot_dom=len(doms)

    wb=Workbook(); wb.remove(wb.active)

    # ========== SUMMARY ==========
    ws=wb.create_sheet("Summary"); set_grid(ws,False)
    ws.column_dimensions["A"].width=38.86; ws.column_dimensions["B"].width=16.29
    ws.column_dimensions["C"].width=17.57; ws.column_dimensions["D"].width=18.71
    ws.column_dimensions["E"].width=120.0
    for r in range(1,40): ws.row_dimensions[r].height=22.5
    ws.merge_cells("B1:E2")
    t=ws["B1"]; t.value=CLIENT_NAME; t.font=Font(name=GEIST,size=21,bold=True,color=ACCENT)
    t.alignment=Alignment(horizontal="center",vertical="center")
    # logo
    try:
        img=XLImage(BASE+"/ref/harbinger_logo.png")
        mk=AnchorMarker(col=0,colOff=381000,row=0,rowOff=0)
        img.anchor=OneCellAnchor(_from=mk, ext=XDRPositiveSize2D(1866900,552450))
        ws.add_image(img)
    except Exception as e:
        print("logo warn:",e)
    # status table header row3
    sh=["Status","Domains","Backlinks","Share of Domains","What it means"]
    for j,h in enumerate(sh,1):
        c=ws.cell(row=3,column=j,value=h); c.font=hfont(10); c.fill=ACC_FILL
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.border=BOX
    means={"Spam (Disavow)":"Confirmed spam with at least one dofollow link. Included in the disavow file.",
      "Held (Pending Partner)":"Exact match commercial anchor, or a link aimed at a deep service or location page. May have been commissioned. Not in the disavow file until the previous supplier confirms.",
      "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
      "Spam (Nofollow, No Action)":"Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
      "Keep":"Genuine or harmless link. Keep.",
      "Own Site":"Client owned domain that redirects into the site."}
    r=4
    for st in STAT_ORDER:
        n=len(by_status.get(st,[])); bl=bl_by_status.get(st,0)
        vals=[st,n,bl,(n/tot_dom if tot_dom else 0),means[st]]
        fmts=[None,"#,##0","#,##0","0.0%",None]
        for j,(v,fm) in enumerate(zip(vals,fmts),1):
            c=ws.cell(row=r,column=j,value=v); c.font=dfont(); c.fill=WHITE_FILL; c.border=BOX
            c.alignment=Alignment(horizontal=("center" if j in(2,3,4) else None),vertical="center",wrap_text=(j==5))
            if fm: c.number_format=fm
        r+=1
    # total
    tbl=sum(bl_by_status.values())
    vals=["Total",tot_dom,tbl,1.0,None]; fmts=[None,"#,##0","#,##0","0.0%",None]
    for j,(v,fm) in enumerate(zip(vals,fmts),1):
        c=ws.cell(row=r,column=j,value=v); c.font=Font(name=GEIST,size=9,bold=True,color="FF000000"); c.fill=WHITE_FILL; c.border=BOX
        c.alignment=Alignment(horizontal=("center" if j in(2,3,4) else None),vertical="center")
        if fm and v is not None: c.number_format=fm
    r+=1
    # Key findings heading
    kf=ws.cell(row=r,column=1,value="Key findings"); kf.font=Font(name=GEIST,size=10,bold=True,color="FF000000")
    kf.alignment=Alignment(vertical="center"); kfrow=r; r+=1
    findings=build_findings(doms,by_status,stats,links,anchors)
    for fnd in findings:
        ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5)
        c=ws.cell(row=r,column=1,value=fnd); c.font=dfont(); c.alignment=Alignment(vertical="center",wrap_text=True)
        r+=1
    # Anchor profile heading
    ah=ws.cell(row=r,column=1,value="Anchor text profile (all backlinks)")
    ah.font=Font(name=GEIST,size=11,bold=True,color=ACCENT); ah.alignment=Alignment(vertical="center"); r+=1
    aph=["Anchor type","Backlinks","Share of Backlinks","Referring Domains"]
    for j,h in enumerate(aph,1):
        c=ws.cell(row=r,column=j,value=h); c.font=hfont(9); c.fill=ACC_FILL
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.border=BOX
    r+=1
    at=stats["anchor_types"]; totbl=sum(v["bl"] for v in at.values())
    for typ,info in sorted(at.items(), key=lambda kv:-kv[1]["bl"]):
        if info["bl"]==0: continue
        vals=[typ,info["bl"],(info["bl"]/totbl if totbl else 0),info["rd"]]; fmts=[None,"#,##0","0.0%","#,##0"]
        for j,(v,fm) in enumerate(zip(vals,fmts),1):
            c=ws.cell(row=r,column=j,value=v); c.font=dfont(); c.fill=WHITE_FILL; c.border=BOX
            c.alignment=Alignment(horizontal=("center" if j in(2,3,4) else None),vertical="center")
            if fm: c.number_format=fm
        r+=1

    # ========== REFERRING DOMAIN AUDIT ==========
    cols=[("Domain",36,"l",None,0),("Status",24.71,"l",None,0),("AS",9.57,"c",None,0),
          ("Backlinks",13,"c","#,##0",0),("RD's",9.43,"c","#,##0",0),("Traffic",9.71,"c","#,##0",0),
          ("In Disavow",12.43,"c",None,0),("Links Point To",21.29,"l",None,0),
          ("Dofollow Links",14,"c",None,0),("Nofollow Links",8.71,"c",None,0),
          ("First Seen",12,"c","d mmm yyyy",0),("Top Anchor Text",45,"l",None,0),
          ("Example Linking Page",8.71,"l",None,0),("Linking Page Title",40,"l",None,0),
          ("Source",14,"c",None,0),("IP",15,"c",None,0),("Disavow Line",14,"l",None,0)]
    def in_disavow(st):
        return "Yes" if st=="Spam (Disavow)" else ("Held" if st.startswith("Held") else "No")
    order={s:i for i,s in enumerate(STAT_ORDER)}
    rows=[]
    for d in sorted(doms,key=lambda x:(order.get(x["status"],9), -x["bl_n"], x["domain"])):
        dl = f"domain:{d['domain']}" if d["status"]=="Spam (Disavow)" else ""
        rows.append([d["domain"],d["status"],d["as_n"],d["bl_n"],d["rd_n"],d["traffic"],
                     in_disavow(d["status"]),d["links_point_to"],d["dofollow"],d["nofollow"],
                     d2date(d["first_seen"]),d["top_anchor"],d["example_page"],d["example_title"],
                     d["tool"],d["ip"],dl])
    write_data_tab(wb,"Referring Domain Audit",cols,rows,15.75)

    # ========== ALL BACKLINKS ==========
    cols=[("Referring Domain",25.43,"l",None,0),("Status",27.14,"l",None,0),("Tool",14.71,"l",None,0),
          ("Anchor Text",55,"l",None,0),("Anchor Type",32,"l",None,0),("Link Type",10,"c",None,0),
          ("Linking Page URL",55,"l",None,0),("Linking Page Title",53.14,"l",None,0),("Target URL",30.57,"l",None,0)]
    rows=[]
    for l in sorted(links,key=lambda x:x["referring_domain"]):
        rows.append([l["referring_domain"],l["status"],l["tool"],l["anchor"],l["anchor_type"],
                     l["link_type"],l["linking_page_url"],l["linking_page_title"],l["target_url"]])
    ws_ab=write_data_tab(wb,"All Backlinks",cols,rows,22.5)
    ws_ab["C1"].alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)  # template quirk

    # ========== ANCHOR ANALYSIS ==========
    cols=[("Anchor Text",115.86,"l",None,0),("Anchor Type",37.71,"l",None,0),("Backlinks",14,"c","#,##0",0),
          ("Share of Backlinks",8.71,"c","0.00%",0),("Referring Domains",13,"c","#,##0",0),
          ("Spam Domains Using It",20.29,"c","#,##0",0)]
    rows=[]
    for a in anchors:
        rows.append([a["anchor"],a["type"],int(float(a["backlinks"])),float(a["share"]),
                     int(float(a["refdomains"])),int(float(a["spam_domains"]))])
    ws_aa=write_data_tab(wb,"Anchor Analysis",cols,rows,22.5)
    ws_aa["A1"].alignment=Alignment(horizontal="center",vertical="center",wrap_text=False)  # template quirk

    # ========== EXACT MATCH ANCHORS ==========  (Held domains w/ commercial anchors)
    cols=[("Referring domain",25.43,"l",None,0),("Example backlink (linking page)",59,"l",None,0),
          ("Exact-match commercial anchor",53.14,"l",None,0),("Market",16,"c",None,0),
          ("Site type (indicative)",24.57,"l",None,0),("Partner confirmed? (Y/N)",15.43,"l",None,1),
          ("Final decision",15,"l",None,1)]
    # pick, per held domain, a commercial-anchor example link
    held={d["domain"] for d in doms if d["status"].startswith("Held")}
    link_by_dom=defaultdict(list)
    for l in links: link_by_dom[l["referring_domain"]].append(l)
    rows=[]
    for dom in sorted(held):
        ls=link_by_dom[dom]
        # one row per distinct exact-match commercial anchor (geo or not)
        seen={}
        for l in ls:
            if l["anchor_type"].startswith("Exact match"):
                a=l["anchor"]
                if a not in seen: seen[a]=l
        if not seen:
            # held via deep-page link w/ non-commercial anchor: one row w/ representative link
            l=ls[0] if ls else None
            a=l["anchor"] if l else ""
            seen[a]=l
        for a,l in sorted(seen.items()):
            page=l["linking_page_url"] if l else ""
            title=l["linking_page_title"] if l else ""
            rows.append([dom,page,a,market_of(a),sitetype_of(dom,title),"None","None"])
    write_data_tab(wb,"Exact Match Anchors",cols,rows,22.5)

    # ========== PENDING DISAVOW LINES ==========  (Held domains)
    cols=[("Referring domain",32,"l",None,0),
          ("Disavow line (append to disavow.txt once confirmed)",44,"l",None,0),
          ("Recommendation",48,"l",None,0)]
    rows=[]
    for d in sorted([x for x in doms if x["status"]=="Held (Pending Partner)"],key=lambda x:x["domain"]):
        rows.append([d["domain"],f"domain:{d['domain']}",
                     "Append only if the previous supplier/Harbinger does not claim this link as a commissioned placement."])
    write_data_tab(wb,"Pending Disavow Lines",cols,rows,22.5)

    # ========== DISAVOW LIST ==========  (Spam (Disavow))
    cols=[("Disavow Line",44,"l",None,0),("AS",14,"c",None,0),("Backlinks",15.57,"c","#,##0",0),
          ("RD's",14,"c","#,##0",0),("Traffic",11.14,"c","#,##0",0),("Organic Keywords",14.86,"c","#,##0",0),
          ("Top Anchor Text",98.86,"l",None,0)]
    rows=[]
    dis=sorted([x for x in doms if x["status"]=="Spam (Disavow)"],key=lambda x:x["domain"])
    for d in dis:
        rows.append([f"domain:{d['domain']}",d["as_n"],d["bl_n"],d["rd_n"],d["traffic"],d["keywords"],d["top_anchor"]])
    write_data_tab(wb,"Disavow List",cols,rows,22.5)

    outx=OUT+"/Elitewrecker_Backlinks_Audit.xlsx"
    wb.save(outx)
    print("wrote",outx)

    # ---- disavow.txt (.com union) ----
    write_disavow(dis, by_status)

def build_findings(doms,by_status,stats,links,anchors):
    from collections import Counter
    n=len(doms)
    spam_dis=len(by_status.get("Spam (Disavow)",[]))
    spam_nf=len(by_status.get("Spam (Nofollow, No Action)",[]))
    held_pp=len(by_status.get("Held (Pending Partner)",[]))
    spam_total=spam_dis+spam_nf
    # single biggest spam anchor (by referring domains), like K&K
    spam_anc=[a for a in anchors if a["type"].startswith("Spam")]
    top_anc=max(spam_anc,key=lambda a:int(float(a["refdomains"]))) if spam_anc else None
    top_anc_rd=int(float(top_anc["refdomains"])) if top_anc else 0
    # held IP concentration (/16)
    net16=Counter()
    for d in by_status.get("Held (Pending Partner)",[]):
        ip=d["ip"]
        if ip and ip.count(".")==3: net16[".".join(ip.split(".")[:2])]+=1
    ip3=sum(c for _,c in net16.most_common(3))
    top3=", ".join(f"{k}.x" for k,_ in net16.most_common(3))
    held_notraffic=sum(1 for d in by_status.get("Held (Pending Partner)",[]) if int(d["traffic"])==0)
    f=[]
    f.append(f"{spam_total:,} of the {n:,} referring domains are spam. {spam_dis:,} have a dofollow link and go in the disavow file; the other {spam_nf:,} are nofollow and need no action.")
    f.append(f"The attack has more than tripled since the brief: Semrush showed 762 referring domains in the brief's April snapshot and 2,142 now; the full live Semrush+Ahrefs profile we audited is {n:,}. We audited the full live profile, not the brief's 762.")
    f.append(f"You can upload a disavow file for {MONEY_SITE} only. That one file covers every bad domain, including the links that reach the site through the elitewrecker.net 301 redirect.")
    f.append("Two patterns, easy to tell apart: the link-scheme flood points only at the home page, while the commercial-anchor links point at deep /services location pages. The home-page flood is the attack.")
    f.append(f"The biggest single spam anchor is backlink sales copy naming the client's own domain (“elitewrecker.com Premium Authority Backlinks for Better Search Visibility”), on {top_anc_rd:,} referring domains.")
    f.append(f"{held_pp:,} domains are held for the previous supplier/Harbinger to confirm, in case any were paid placements. {ip3:,} of them sit in three hosting ranges ({top3}), so they are one directory/article network, not {held_pp:,} separate sites.")
    f.append(f"Held does not mean good: {held_notraffic:,} of the {held_pp:,} held (pending) domains have no organic traffic at all. The paid-link / PBN and Telegram clusters named in the brief are all confirmed spam.")
    return f

def write_disavow(dis, by_status):
    lines=[]
    lines.append("# Google disavow file — elitewrecker.com")
    lines.append("# Prepared by Harbinger Marketing. Generated 2026-10-20 from the full live")
    lines.append("# Semrush + Ahrefs referring-domain profile (subdomains scope).")
    lines.append("#")
    lines.append(f"# Domains in this file: {len(dis)} (Status = Spam (Disavow): confirmed spam with >=1 dofollow link).")
    lines.append("# This file is for the elitewrecker.com Search Console property and is the FULL UNION")
    lines.append("# of every bad domain, including links that reach the site via the elitewrecker.net 301.")
    lines.append("# elitewrecker.net is client-owned and redirects in; disavow is uploaded to elitewrecker.com only.")
    lines.append("#")
    lines.append("# DO NOT UPLOAD until the previous SEO supplier and Harbinger have confirmed which")
    lines.append("#   links were commissioned. Held (Pending Partner) domains are NOT in this file;")
    lines.append("#   see the 'Pending Disavow Lines' tab and append any the supplier does not claim.")
    lines.append("# NOTE: confirm with the client whether a disavow file already exists on the property.")
    lines.append("#   If one exists, uploading REPLACES it; if the client has confirmed none exists, this is the first.")
    lines.append("#")
    for d in sorted(dis,key=lambda x:x["domain"]):
        lines.append(f"domain:{d['domain']}")
    open(OUT+"/disavow_elitewrecker.com.txt","w").write("\n".join(lines)+"\n")
    print("wrote disavow_elitewrecker.com.txt with",len(dis),"domains")

if __name__=="__main__":
    main()
