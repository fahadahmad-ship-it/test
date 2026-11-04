#!/usr/bin/env python3
"""Classify farison.com referring domains per BACKLINK_AUDIT_PLAYBOOK and build the
7-tab workbook (AUDIT_FORMAT as written: 9pt accent title, bordered data cells) plus
per-property disavow files. Semrush = metrics; Ahrefs = is_spam cross-check only."""
import sys, glob, json, html, re, os, collections, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from urllib.parse import urlparse

BASE="/home/user/test/data/farison"; OUTDIR="/home/user/test/deliverables"
TODAY="2026-11-04"; ACCENT="FF0C343D"; WHITE="FFFFFFFF"; BLACK="FF000000"
OWNED={"farison.com","lawncare-louisvilleky.com"}
LOGO="/home/user/test/data/template_assets/Summary_img0.png"
GEO=["louisville","shelbyville","clarksville","mt washington","mount washington","new albany","prospect",
 "bardstown","kentucky","indiana"," ky"," in "," ky,"," in,","crestwood","jeffersontown","la grange","pewee valley","mt. washington"]
SERVICE=["lawn","mosquito","weed","flea","tick","tree","shrub","grub","fertiliz","mow","aeration",
 "landscap","irrigation","pest","mulch","seeding","sod","leaf","maintenance"]
SALES=["backlink","pbn","da 50","pa 40","da50","pa40"," seo ","premium seo","rank first","buy backlink",
 "dofollow backlinks","link building","trust flow","high authority","boost","niche edit","contextual link",
 "authority backlinks","ranking growth","increase organic","serp","web 2.0","aged domain","link profile",
 "outrank","premium backlinks","link placements","indexation","citation flow","rank higher","traffic focused",
 "grow your website","website authority","lasting authority"]
OFF=["casino","gambl","slot","poker","roulette","betting","porn","escort","viagra","cialis","pharma",
 "payday","loan","crypto","bitcoin","forex","adult"," sex ","telegram @","darkside","t.me/"]
HOSTSPAM=["backlink","pbn","-seo","seo-","dapa","rankchecker","ranktool","linkbuilding","buydomain",
 "ageddomain","domainanalysis","webtraffic","trafficbot","websitechecker","dacheck","pacheck"]
def host(u):
    try:
        h=urlparse((u or "").strip()).netloc.lower(); return h[4:] if h.startswith("www.") else h
    except: return ""
def reg(h):
    if not h: return ""
    p=h.split("."); two=("co.uk","org.uk","com.au","co.in","co.nz","com.br","gb.net","de.com")
    if len(p)>=3 and ".".join(p[-2:]) in two: return ".".join(p[-3:])
    return ".".join(p[-2:]) if len(p)>=2 else h
def hit(t,toks): tl=(t or "").lower(); return any(k in tl for k in toks)

# ---- load refdomains (Semrush: AS, ip, first_seen) ----
rd={}
for fp in glob.glob(f"{BASE}/rd/rd_*.csv"):
    with open(fp,encoding="utf-8",errors="replace") as f: lines=f.read().split("\n")
    start=1 if lines and lines[0].lower().startswith("domain;") else 0
    for ln in lines[start:]:
        if not ln.strip(): continue
        parts=html.unescape(ln).split(";")
        if len(parts)<8: continue
        dom=parts[0].strip().lower()
        def fnum(x):
            try: return float(x)
            except: return None
        rd[dom]=dict(as_=fnum(parts[2]), trust=fnum(parts[3]), ip=parts[4].strip(),
                     backlinks_num=fnum(parts[1]), first_seen=parts[6].strip(), last_seen=parts[7].strip())
print("refdomains loaded:",len(rd))

ah={}
try:
    ad=json.load(open(f"{BASE}/ahrefs_refdomains.json")); arr=ad.get("refdomains",ad) if isinstance(ad,dict) else ad
    for r in arr: ah[str(r.get("domain","")).lower()]=r
except Exception as e: print("ahrefs load warn:",e)
print("ahrefs loaded:",len(ah))

bl=json.load(open(f"{BASE}/backlinks_parsed.json"))
def ts_to_date(x):
    try: return datetime.datetime.utcfromtimestamp(int(float(x))).strftime("%Y-%m-%d")
    except: return str(x)[:10] if x else ""
def anchor_type(a):
    al=(a or "").lower().strip()
    if hit(al,OFF): return "Spam: off topic"
    if hit(al,SALES): return "Spam: keyword stuffed SEO sales copy"
    if al in ("","-"): return "Empty or image"
    if al in ("farison.com","lawncare-louisvilleky.com") or al.startswith("http"): return "Naked URL"
    if al=="farison lawn care" or al=="farison": return "Branded"
    if hit(al,SERVICE) and hit(al,GEO): return "Exact match commercial (geo)"
    if hit(al,SERVICE): return "Exact match commercial"
    if al in ("visit website","website","google","read more","click here","visit site","homepage","more info","farison"): return "Generic"
    if "farison" in al and len(al)<28: return "Branded"
    return "Contextual or other"
def property_of(r):
    rh=host(r.get("redirect_url","")) if (r.get("redirect_url") or "").strip() else ""
    return reg(rh) if rh else reg(host(r.get("target_url","")))
def deep(r):
    return bool(urlparse(r.get("target_url","")).path.strip("/"))
def market_of(a):
    al=(a or "").lower()
    for city,label in [("new albany","New Albany IN"),("clarksville","Clarksville IN"),("mt washington","Mt Washington KY"),
        ("mount washington","Mt Washington KY"),("shelbyville","Shelbyville KY"),("louisville","Louisville KY"),
        ("prospect","Prospect KY"),("bardstown","Bardstown KY"),("crestwood","Crestwood KY"),("jeffersontown","Jeffersontown KY"),
        ("la grange","La Grange KY"),("pewee valley","Pewee Valley KY"),("sellersburg","Sellersburg IN"),
        ("charlestown","Charlestown IN"),("georgetown","Georgetown IN"),("floyds knobs","Floyds Knobs IN"),
        ("jeffersonville","Jeffersonville IN"),("new washington","New Washington IN"),("borden","Borden IN"),
        ("goshen","Goshen KY"),("simpsonville","Simpsonville KY"),("taylorsville","Taylorsville KY"),("fisherville","Fisherville KY"),
        (" ky","Kentucky (KY)"),(" in","Indiana (IN)")]:
        if city in al: return label
    return "Non-geo"

by=collections.defaultdict(list)
for r in bl:
    d=reg(host(r.get("source_url","")))
    if d: by[d].append(r)
print("referring domains (from backlinks):",len(by))

records={}
for d in set(by)|set(rd):
    links=by.get(d,[]); info=rd.get(d,{}); as_=info.get("as_"); ahrow=ah.get(d,{})
    types=[anchor_type(r.get("anchor","")) for r in links]
    nd=sum(1 for r in links if r.get("nofollow")=="false"); nf=sum(1 for r in links if r.get("nofollow")=="true")
    props=set(property_of(r) for r in links if property_of(r))
    has_exact=any(t.startswith("Exact match") for t in types)
    has_sales=any(t=="Spam: keyword stuffed SEO sales copy" for t in types)
    has_off=any(t=="Spam: off topic" for t in types)
    anydeep=any(deep(r) for r in links)
    titles=" ".join(str(r.get("source_title","")) for r in links)
    names_client=("farison" in titles.lower()) and not hit(titles,SALES)
    host_spam=hit(d,HOSTSPAM); title_spam=hit(titles,SALES) or hit(titles,OFF)
    tld=d.rsplit(".",1)[-1]; throwaway=tld in ("store","site","shop","online","space","website","cfd","sbs","icu","top","click","live")
    allnofollow=(nd==0 and nf>0)
    if d in OWNED: status="Own Site"
    elif as_ is not None and as_>=20 and not has_sales and not has_off: status="Keep"
    elif has_exact and has_sales: status="Held (Pending Partner)"
    elif has_exact or (anydeep and not has_sales and not has_off and not host_spam and not throwaway): status="Held (Pending Partner)"
    elif names_client and not (has_sales or has_off or host_spam): status="Keep"
    elif has_off or has_sales or host_spam or title_spam: status="Spam (Disavow)"
    elif throwaway and nd>0: status="Spam (Disavow)"
    else: status="Keep"
    if status=="Spam (Disavow)" and allnofollow: status="Spam (Nofollow, No Action)"
    if status=="Held (Pending Partner)" and allnofollow: status="Held (Nofollow, No Action)"
    if status=="Spam (Disavow)" and nd==0: status="Keep"  # no dofollow evidence in our data -> cannot disavow
    anc_counts=collections.Counter(r.get("anchor","") for r in links)
    top_anchor=anc_counts.most_common(1)[0][0] if links else ""
    ema_anchor=next((r.get("anchor","") for r in links if anchor_type(r.get("anchor","")).startswith("Exact match")), top_anchor)
    ex=next((r for r in links if r.get("response_code")=="200"), links[0] if links else None)
    in_dis="Yes" if status=="Spam (Disavow)" else ("Held" if status.startswith("Held") else "No")
    lc_attr=any("lawncare-louisvilleky" in (property_of(l) or "") for l in links)
    fa_attr=any(property_of(l)=="farison.com" for l in links)
    records[d]=dict(domain=d,status=status,as_=as_,backlinks=(len(links) if links else int(info.get("backlinks_num") or 0)),
        in_dis=in_dis,props="; ".join(sorted(p for p in props if p)) or "farison.com",nd=nd,nf=nf,
        first_seen=(ts_to_date(info.get("first_seen")) or (ts_to_date(ex.get("first_seen")) if ex else "")),
        top_anchor=top_anchor,example=(ex.get("source_url","") if ex else ""),title=(ex.get("source_title","") if ex else ""),
        ip=info.get("ip",""),ahrefs_spam=ahrow.get("is_spam"),dr=ahrow.get("domain_rating"),
        has_exact=has_exact,disavow_line=(f"domain:{d}" if status=="Spam (Disavow)" else ""),
        lc_attr=lc_attr,fa_attr=fa_attr,ema_anchor=ema_anchor)

sc=collections.Counter(r["status"] for r in records.values())
print("\nStatus distribution:"); [print(f"  {k}: {v}") for k,v in sc.most_common()]
TAB08=["gotolistings.org","getzzby.com","findzy.net","listingspace.net","showyourbizz.com","directoryhop.com",
 "premiumlistings.co","downtownlists.com","b-listings.com","prolocalbusinesssearch.com","boblistings.org","smallbizdir.com","local-business-center.com"]
print("\nTab08 statuses:")
for d in TAB08:
    r=records.get(d); print(f"  {d}: {(r['status']+' exact='+str(r['has_exact'])+' as='+str(r['as_'])) if r else 'NOT FOUND'}")

if "--build" not in sys.argv:
    print("\n(diagnostic only; pass --build to write workbook)"); sys.exit(0)

# ================= BUILD =================
os.makedirs(OUTDIR,exist_ok=True)
STATUS_ORDER=["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)","Spam (Nofollow, No Action)","Keep","Own Site"]
MEANS={"Spam (Disavow)":"Confirmed spam (PBN/link-service sales-copy anchor, spam host, or throwaway TLD) with at least one dofollow link. In the disavow file.",
 "Held (Pending Partner)":"Exact-match commercial/geo anchor or a link to a deep money page - may be a commissioned placement. Held until Harbinger and the commissioning partner confirm.",
 "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no value. No disavow needed.",
 "Spam (Nofollow, No Action)":"Spam, but every link is nofollow and passes no value, so no disavow is needed.",
 "Keep":"Genuine, branded or harmless (editorial citation, genuine directory/aggregator AS>=20, nofollow listing). Keep.",
 "Own Site":"Client-owned property or a domain that redirects into the site (farison.com, lawncare-louisvilleky.com)."}
def anchor_type2(a): return anchor_type(a)
# all backlinks rows
abl_rows=[]
for r in bl:
    d=reg(host(r.get("source_url","")))
    rec=records.get(d,{})
    abl_rows.append([d, rec.get("status","Keep"), "Semrush", r.get("anchor",""), anchor_type2(r.get("anchor","")),
                     ("Nofollow" if r.get("nofollow")=="true" else "Dofollow"), r.get("source_url",""),
                     r.get("source_title",""), r.get("target_url","")])
TOTAL_BL=len(abl_rows); TOTAL_DOM=len(records)
bl_by=collections.Counter(row[1] for row in abl_rows)
dom_by=collections.Counter(r["status"] for r in records.values())
# anchor profile
type_bl=collections.Counter(row[4] for row in abl_rows); type_rd=collections.defaultdict(set)
for row in abl_rows: type_rd[row[4]].add(row[0])
anchor_profile=sorted(type_bl.items(),key=lambda x:-x[1])
# anchor analysis
anc_bl=collections.Counter(); anc_rd=collections.defaultdict(set); anc_spam=collections.defaultdict(set); anc_type={}
for row in abl_rows:
    a=row[3]; anc_bl[a]+=1; anc_rd[a].add(row[0]); anc_type.setdefault(a,row[4])
    if row[1].startswith("Spam"): anc_spam[a].add(row[0])
anchor_rows=[[a,anc_type[a],c,c/TOTAL_BL,len(anc_rd[a]),len(anc_spam[a])] for a,c in sorted(anc_bl.items(),key=lambda x:-x[1])]
# RDA rows
RDA_H=["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To","Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page","Linking Page Title","Source","IP","Disavow Line"]
rda_rows=[]
for d,r in sorted(records.items(), key=lambda kv:-kv[1]["backlinks"]):
    rda_rows.append([r["domain"],r["status"],r["as_"],r["backlinks"],None,None,r["in_dis"],r["props"],r["nd"],r["nf"],
                     r["first_seen"],r["top_anchor"],r["example"],r["title"],"Semrush",r["ip"],r["disavow_line"]])
# exact match tab (held + has_exact)
ema_rows=[]
for d,r in sorted(records.items()):
    if r["status"].startswith("Held") and r["has_exact"]:
        ema_rows.append([d,r["example"],r["ema_anchor"],market_of(r["ema_anchor"]),"Directory / blog (review source quality)","",""])
# pending tab (held pending partner)
pend_rows=[[d,f"domain:{d}","Append ONLY if Harbinger and the commissioning partner do not confirm this was a commissioned placement."]
           for d,r in sorted(records.items()) if r["status"]=="Held (Pending Partner)"]
# disavow list (spam disavow)
dis=[r for d,r in sorted(records.items(), key=lambda kv:-kv[1]["backlinks"]) if r["status"]=="Spam (Disavow)"]
dis_rows=[[r["disavow_line"],r["as_"],r["backlinks"],None,None,None,r["top_anchor"]] for r in dis]

# ---- disavow files (per property) ----
def reason(r):
    d=r["domain"]; t=(r["top_anchor"]+" "+r["title"]).lower()
    if hit(t,OFF): return "Off-topic (gambling / pharma / adult)"
    if hit(d,["backlink","dacheck","pacheck","dapa","rankchecker","seochecker","checker","indexer","baclink"]): return "SEO-tool / backlink-checker link-farm host"
    if hit(d,["buybacklink","buydofollow","buypbn","buyhigh","buycheap","pbn","buylinks","buyingbacklinks"]): return "Buy-backlinks / PBN-for-sale host"
    if hit(d,["seo","directory","listing","traffic","webtraffic","domainanalysis","linkbuilding"]): return "Spam host name (SEO / directory / traffic)"
    if hit(t,SALES): return "PBN / link-service sales-copy anchor"
    return "Throwaway-TLD / spam page evidence"
def write_disavow(path, domains, header_lines):
    groups=collections.OrderedDict()
    for r in domains: groups.setdefault(reason(r),[]).append(r["domain"])
    with open(path,"w") as f:
        for h in header_lines: f.write("# "+h+"\n")
        for g,doms in groups.items():
            f.write(f"\n# --- {g} ({len(set(doms))}) ---\n")
            for dd in sorted(set(doms)): f.write(f"domain:{dd}\n")
    return sum(len(set(v)) for v in groups.values())
farison_union=dis  # money-site file = full union
lc_set=[r for r in dis if r["lc_attr"]]
hdr_fa=[f"Disavow file - farison.com (Google Search Console)",
 f"Generated: {TODAY} | Domains: {len(dis)}",
 "This is the MONEY-SITE file: it carries the FULL UNION of every spam domain, because",
 "lawncare-louisvilleky.com 301-redirects into farison.com and Google forwards disavow",
 "signals across redirects imperfectly. Listing a domain that does not link to farison",
 "directly is harmless.",
 "'Partner' = the SEO partner who commissioned the exact-match directory links.",
 "HELD exact-match domains (incl. the 13 Tab 08 domains) are EXCLUDED pending confirmation",
 "from Harbinger and that partner. DO NOT UPLOAD before that conversation and a GSC",
 "manual-action check. Uploading REPLACES any existing file - confirm with the client",
 "whether one already exists (unknown here)."]
hdr_lc=[f"Disavow file - lawncare-louisvilleky.com (owned redirect domain)",
 f"Generated: {TODAY} | Domains: {len(lc_set)}",
 "Attribution set: spam domains whose links point at lawncare-louisvilleky.com (which 301s",
 "into farison.com). Upload this ONLY to the lawncare-louisvilleky.com Search Console",
 "property. If the client only controls the farison.com property, this file is REFERENCE",
 "ONLY and its domains are already covered by the farison.com union file.",
 "Confirm lawncare-louisvilleky.com is client-owned before using."]
n_fa=write_disavow(f"{OUTDIR}/disavow_farison.com.txt", farison_union, hdr_fa)
n_lc=write_disavow(f"{OUTDIR}/disavow_lawncare-louisvilleky.com.txt", lc_set, hdr_lc)
print(f"\ndisavow_farison.com.txt: {n_fa} | disavow_lawncare: {n_lc}")

# ---- workbook (match the signed NewGarden sample exactly) ----
wb=openpyxl.Workbook(); wb.remove(wb.active)
sthin=Side(style="thin"); box=Border(left=sthin,right=sthin,top=sthin,bottom=sthin)
def F(size=9,bold=False,color=BLACK): return Font(name="Geist",size=size,bold=bold,color=color)
fill_accent=PatternFill("solid",fgColor=ACCENT); fill_white=PatternFill("solid",fgColor=WHITE)
hdr_al=Alignment(horizontal="center",vertical="center",wrap_text=True)
WIDTHS={'Referring Domain Audit':{'A':36,'B':24.71,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,'J':8.71,'K':12,'L':45,'M':8.71,'N':40,'O':14,'P':15,'Q':14},
 'All Backlinks':{'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':30.57},
 'Anchor Analysis':{'A':115.86,'B':37.71,'C':14,'D':8.71,'E':13,'F':20.29},
 'Exact Match Anchors':{'A':25.43,'B':59,'C':53.14,'D':16,'E':24.57,'F':15.43,'G':15},
 'Pending Disavow Lines':{'A':32,'B':44,'C':48},
 'Disavow List':{'A':44,'B':14,'C':15.57,'D':14,'E':11.14,'F':14.86,'G':98.86}}
LEFT={"Domain","Referring Domain","Referring domain","Anchor Text","Anchor Type","Top Anchor Text","Example Linking Page",
 "Linking Page Title","Linking Page URL","Target URL","Disavow Line","Links Point To","Recommendation",
 "Exact-match commercial anchor","Example backlink (linking page)","Site type (indicative)",
 "Disavow line (append to disavow_farison.com.txt once confirmed)"}
NUMCOMMA={"Backlinks","RD's","Traffic","Dofollow Links","Nofollow Links","Referring Domains","Spam Domains Using It","Organic Keywords"}
def col_fmt(h): return "#,##0" if h in NUMCOMMA else ("0.00%" if h=="Share of Backlinks" else None)
def col_align(h): return Alignment(horizontal=(None if h in LEFT else "center"), vertical="center")
def write_tab(name,header,rows):
    ws=wb.create_sheet(name); ws.sheet_format.defaultRowHeight=15.75
    for c,h in enumerate(header,1):
        cell=ws.cell(1,c,h); cell.font=F(9,True,WHITE); cell.fill=fill_accent; cell.alignment=hdr_al; cell.border=box
    ws.row_dimensions[1].height=31.5
    aligns=[col_align(h) for h in header]; fmts=[col_fmt(h) for h in header]
    for ri,row in enumerate(rows,2):
        for c,v in enumerate(row,1):
            cell=ws.cell(ri,c,v); cell.font=F(9); cell.fill=fill_white; cell.alignment=aligns[c-1]
            if fmts[c-1]: cell.number_format=fmts[c-1]
    ncol=len(header); nrow=len(rows)+1
    for col,w in WIDTHS.get(name,{}).items(): ws.column_dimensions[col].width=w
    ws.freeze_panes="B2"; ws.auto_filter.ref=f"A1:{get_column_letter(ncol)}{nrow}"
    return ws
# Summary (own small tables are bordered; gridlines off; title 21pt unmerged; source note 8pt gray)
ws=wb.create_sheet("Summary"); ws.sheet_view.showGridLines=False; ws.sheet_format.defaultRowHeight=15.0
for col,w in {'A':38.86,'B':16.29,'C':17.57,'D':18.71,'E':120}.items(): ws.column_dimensions[col].width=w
try:
    img=XLImage(LOGO); img.width=196; img.height=58; ws.add_image(img,"A1")
except Exception as e: print("logo warn:",e)
t=ws.cell(1,2,"Farison Lawn Care"); t.font=F(21,True,ACCENT); t.alignment=Alignment(horizontal="left",vertical="center")
ws.row_dimensions[1].height=22.5; ws.row_dimensions[2].height=22.5
for c,h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"],1):
    cell=ws.cell(3,c,h); cell.font=F(10,True,WHITE); cell.fill=fill_accent; cell.alignment=hdr_al; cell.border=box
rr=4
def sumcell(cell,c,total=False):
    cell.font=F(9,total); cell.fill=fill_white; cell.border=box
    if c in (2,3): cell.number_format="#,##0"; cell.alignment=Alignment(horizontal="center",vertical="center")
    elif c==4: cell.number_format="0.0%"; cell.alignment=Alignment(horizontal="center",vertical="center")
    elif c==5: cell.alignment=Alignment(vertical="center",wrap_text=True)
    else: cell.alignment=Alignment(vertical="center")
for st in STATUS_ORDER:
    for c,v in enumerate([st,dom_by.get(st,0),bl_by.get(st,0),(dom_by.get(st,0)/TOTAL_DOM if TOTAL_DOM else 0),MEANS[st]],1):
        sumcell(ws.cell(rr,c,v),c)
    rr+=1
for c,v in enumerate(["Total",TOTAL_DOM,TOTAL_BL,1,""],1):
    sumcell(ws.cell(rr,c,v),c,total=True)
for r_ in range(3,rr+1): ws.row_dimensions[r_].height=22.5
kf=rr+2; ws.cell(kf,1,"Key findings").font=F(9,True,ACCENT); ws.row_dimensions[kf].height=22.5
spam_dom=dom_by["Spam (Disavow)"]+dom_by["Spam (Nofollow, No Action)"]
findings=[
 f"{spam_dom:,} of {TOTAL_DOM:,} referring domains are spam. {dom_by['Spam (Disavow)']:,} have a dofollow link and go in the disavow file; {dom_by['Spam (Nofollow, No Action)']} are nofollow and pass nothing.",
 "Referring domains roughly tripled from ~1,326 (Sep 2026) to 3,566 (Oct 2026) - a single recent PBN flood. Semrush Authority Score stayed ~14, so the spam is not moving the profile.",
 "Most spam uses SEO sales-copy anchors (\"Premium SEO Authority Backlinks to Help farison.com...\", \"DA 50 PA 40 Premium PBN Network\") on throwaway .store/.site/.shop domains. Auto-generated, not links the client bought.",
 "farison.com has an owned redirect domain, lawncare-louisvilleky.com: ~1,312 spam links point at it and 301 into farison. It needs its own disavow file; the farison.com file carries the full union.",
 f"{dom_by['Held (Pending Partner)']} domains carry exact-match commercial/geo anchors (incl. the 13 Tab 08 domains, the 69.13.x.x directory network). These may be a commissioned package - HELD for Harbinger + the partner to confirm (Tab 05/06).",
 "Cross-checked against Ahrefs: genuine directories (siteprice, dexknows, yp.com, superpages) are kept; the OVH 15.204.x bookmarking network and 69.13.x.x directory network are the two spam clusters. Metrics are Semrush.",
 "No manual action is visible in this data - check Search Console. Disavow only on a manual action or confirmed paid links; the Tab 08 held set must be confirmed with the partner first. Deadline in the brief (end Oct 2026) has passed."]
r_=kf+1
for fnd in findings:
    ws.merge_cells(f"A{r_}:E{r_}"); cell=ws.cell(r_,1,fnd); cell.font=F(9); cell.alignment=Alignment(vertical="center",wrap_text=True); ws.row_dimensions[r_].height=22.5; r_+=1
ap=r_+1; hh=ws.cell(ap,1,"Anchor text profile (all backlinks)"); hh.font=F(9,True,ACCENT); ws.row_dimensions[ap].height=22.5
for c,h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains"],1):
    cell=ws.cell(ap+1,c,h); cell.font=F(10,True,WHITE); cell.fill=fill_accent; cell.alignment=hdr_al; cell.border=box
ws.row_dimensions[ap+1].height=22.5
rr2=ap+2
for atype,cnt in anchor_profile:
    for cc,v in enumerate([atype,cnt,cnt/TOTAL_BL,len(type_rd[atype])],1):
        cell=ws.cell(rr2,cc,v); cell.font=F(9); cell.fill=fill_white; cell.border=box
        if cc==2: cell.number_format="#,##0"; cell.alignment=Alignment(horizontal="center",vertical="center")
        elif cc==3: cell.number_format="0.00%"; cell.alignment=Alignment(horizontal="center",vertical="center")
        elif cc==4: cell.number_format="#,##0"; cell.alignment=Alignment(horizontal="center",vertical="center")
        else: cell.alignment=Alignment(vertical="center")
    ws.row_dimensions[rr2].height=22.5; rr2+=1
srow=rr2+1; ws.merge_cells(f"A{srow}:E{srow}")
note=(f"Source: Semrush Backlink Analytics, {TODAY} ({TOTAL_BL:,} backlinks / {TOTAL_DOM:,} referring domains), cross-checked "
 "against Ahrefs. 'AS' = Semrush Authority Score. Per the signed format RD's and Traffic are left blank (Semrush's "
 "referring-domains export omits them). Two properties: farison.com + the owned redirect lawncare-louisvilleky.com; "
 "see the two disavow files. Tab 05: fill F (Y/N) and G (Keep/Disavow). The brief's '345-domain profile' does not match "
 "either tool (Ahrefs ~1,296 live / Semrush 3,667).")
cell=ws.cell(srow,1,note); cell.font=F(8,False,"FF666666"); cell.alignment=Alignment(vertical="center",wrap_text=True); ws.row_dimensions[srow].height=72
# data tabs
write_tab('Referring Domain Audit',RDA_H,rda_rows)
write_tab('All Backlinks',["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type","Linking Page URL","Linking Page Title","Target URL"],abl_rows)
write_tab('Anchor Analysis',["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"],anchor_rows)
write_tab('Exact Match Anchors',["Referring domain","Example backlink (linking page)","Exact-match commercial anchor","Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"],ema_rows)
write_tab('Pending Disavow Lines',["Referring domain","Disavow line (append to disavow_farison.com.txt once confirmed)","Recommendation"],pend_rows)
write_tab('Disavow List',["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"],dis_rows)
wb.move_sheet("Summary",-(len(wb.sheetnames)-1))
OUT=f"{OUTDIR}/Farison_Backlinks_Audit.xlsx"; wb.save(OUT)
print("saved",OUT,"| sheets:",wb.sheetnames)
print("Summary counts:",dict(dom_by),"| EMA rows:",len(ema_rows),"| pending:",len(pend_rows),"| disavow:",len(dis_rows))
