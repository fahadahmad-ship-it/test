import csv, re, json, html, copy, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from collections import Counter, defaultdict
DATA="/home/user/test/data"; CLIENT="blackwalnutconstruction.com"
SKELETON="/root/.claude/uploads/00899f38-e3d1-54d4-a148-a694f2eb9402/5011db2c-KandK_Manufacturing_Backlinks_Audit.xlsx"
OUT="/home/user/test/BlackWalnut_Backlinks_Audit.xlsx"
def host(u):
    s=html.unescape(str(u or "")).strip().lower(); s=re.sub(r'^https?://','',s).split('/')[0]; return re.sub(r'^www\.','',s)
def dt(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).date()
    except: return None

dj=json.load(open(f"{DATA}/domains.json")); status=dj["status"]; meta=dj["meta"]

# refdomains for metrics
rd={}
for fn in ["rd_p1.csv","rd_p2.csv"]:
    r=csv.reader(open(f"{DATA}/{fn}",encoding="utf-8"),delimiter=';'); next(r)
    for row in r:
        if len(row)<9: continue
        d=host(row[0])
        try: asc=int(row[2] or 0)
        except: asc=0
        try: bl=int(row[1] or 0)
        except: bl=0
        if d not in rd or bl>rd[d]["bl"]: rd[d]=dict(as_=asc,bl=bl,ip=row[5],first_seen=row[7])

# links (reparse for All Backlinks tab + anchor profile)
def parse_line(line):
    parts=line.split(';')
    if len(parts)<8: return None
    ni=None
    for i in range(len(parts)-1,-1,-1):
        if parts[i] in ('true','false'): ni=i;break
    if ni is None or ni<3: return None
    anchor=parts[ni-1]; src=parts[0]; left=parts[1:ni-1]
    ti=None
    for j in range(len(left)-1,-1,-1):
        if 'blackwalnutconstruction' in left[j]: ti=j;break
    target=left[ti] if ti is not None else (left[-1] if left else "")
    title=";".join(left[:ti]) if ti is not None else ""
    return dict(src=src,title=html.unescape(title),target=target,anchor=html.unescape(anchor),nofollow=parts[ni]=='true')
links=[]
for fn in ["bl_p1.csv","bl_p2.csv","bl_p3.csv"]:
    for line in open(f"{DATA}/{fn}",encoding="utf-8").read().splitlines()[1:]:
        if line.strip():
            p=parse_line(line)
            if p: links.append(p)

# anchor typing (same as classify)
GEO=re.compile(r'lexington|,?\s*sc\b|south carolina',re.I)
CONSTR=re.compile(r'construction|builder|contractor|home build|custom home|office|retail|residential|commercial|renovat|new house|homes build|house builder',re.I)
SALES=re.compile(r'premium authority backlink|buy backlink|backlinks online cheap|pbn|da 50|pa 40|guest post|white hat seo link|raise domain rating|dofollow backlink|premium backlink|rank first page|seo link building|outrank|guest posting|premium seo|authority backlink|visit site seo|links for blackwalnut|outshine competitors',re.I)
OFF=re.compile(r'casino|escort|porn|viagra|pharma|gambling|betting|slot|bonanza|\btoto|tokyopush|malatya|\bufa\b|sbobet',re.I)
GENERIC=re.compile(r'^(visit website|visit site|read more|click here|website|visit website\s*[→↗])\s*$',re.I)
NAKED=re.compile(r'^(https?://)?(www\.)?blackwalnutconstruction\.com',re.I)
BRAND=re.compile(r'black walnut construction',re.I)
def atype(a):
    al=(a or "").strip().lower()
    if al=="": return "Empty or image"
    if OFF.search(al): return "Spam: off topic"
    if SALES.search(al): return "Spam: keyword stuffed SEO sales copy"
    if CONSTR.search(al) and GEO.search(al): return "Exact match commercial (geo)"
    if CONSTR.search(al) and not NAKED.match(al): return "Exact match commercial"
    if BRAND.search(al): return "Branded"
    if NAKED.match(al): return "Naked URL"
    if GENERIC.match(al): return "Generic"
    if 'png' in al or 'banner' in al: return "Empty or image"
    return "Contextual or other"
def linktype(nf): return "Nofollow" if nf else "Dofollow"

wb=openpyxl.load_workbook(SKELETON)
def clone(dst,src): dst._style=copy.copy(src._style)
def rewrite(sheet, rows, ncol):
    ws=wb[sheet]
    tpl=[ws.cell(row=2,column=c) for c in range(1,ncol+1)]
    old=ws.max_row
    for i,rowvals in enumerate(rows):
        rr=2+i
        for c in range(1,ncol+1):
            cell=ws.cell(row=rr,column=c); cell.value=rowvals[c-1]; clone(cell,tpl[c-1])
    last=1+len(rows)
    if old>last: ws.delete_rows(last+1, old-last)
    ws.auto_filter.ref=f"A1:{openpyxl.utils.get_column_letter(ncol)}{last}"
    return ws

# ---------- Referring Domain Audit ----------
order_status=["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)","Spam (Nofollow, No Action)","Keep","Own Site"]
rda_rows=[]
for d in sorted(status, key=lambda x:(-(meta[x]["bl"]),x)):
    m=meta[d]; s=m["status"]
    rda_rows.append([d, s, m["as_"], m["bl"], None, None, "Yes" if s=="Spam (Disavow)" else "No",
        m["points"], m["dofollow"], m["nofollow"], dt(m["first_seen"]), m["top"],
        m["ex_url"], m["ex_title"], "Semrush", m["ip"], f"domain:{d}" if s=="Spam (Disavow)" else ""])
rewrite("Referring Domain Audit", rda_rows, 17)

# ---------- All Backlinks ----------
ab_rows=[]
for L in links:
    d=host(L["src"])
    # map to root present in status
    root=d
    if d not in status:
        for k in sorted(status,key=len,reverse=True):
            if d==k or d.endswith("."+k): root=k;break
    ab_rows.append([root, status.get(root,"Keep"), "Semrush", L["anchor"], atype(L["anchor"]),
        linktype(L["nofollow"]), L["src"], L["title"], L["target"]])
rewrite("All Backlinks", ab_rows, 9)

# ---------- Anchor Analysis ----------
anchor_dom=defaultdict(set); anchor_spamdom=defaultdict(set)
for L in links:
    d=host(L["src"]); root=d
    if d not in status:
        for k in sorted(status,key=len,reverse=True):
            if d==k or d.endswith("."+k): root=k;break
    anchor_dom[L["anchor"]].add(root)
    if status.get(root,"").startswith("Spam"): anchor_spamdom[L["anchor"]].add(root)
an_rows=[]
total_bl_anchor=0
anchors_csv=list(csv.reader(open(f"{DATA}/anchors.csv",encoding="utf-8"),delimiter=';'))[1:]
for row in anchors_csv:
    if len(row)<3: continue
    anc=row[0]; dnum=int(row[1]); blnum=int(row[2]); total_bl_anchor+=blnum
for row in anchors_csv:
    if len(row)<3: continue
    anc=row[0]; dnum=int(row[1]); blnum=int(row[2])
    an_rows.append([anc, atype(anc), blnum, blnum/ (total_bl_anchor or 1), dnum, len(anchor_spamdom.get(anc,[]))])
an_rows.sort(key=lambda r:-r[2])
rewrite("Anchor Analysis", an_rows, 6)

# ---------- Exact Match Anchors (Tab 05) ----------
held=[d for d,s in status.items() if s.startswith("Held")]
em_rows=[]
for d in sorted(held):
    m=meta[d]
    anc=m["ex_anchor"] if atype(m["ex_anchor"]).startswith("Exact match") else (m["top"] if atype(m["top"]).startswith("Exact match") else m["ex_anchor"])
    em_rows.append([d, m["ex_url"], anc, m["market"], "Directory / blog (review source quality)", None, None])
rewrite("Exact Match Anchors", em_rows, 7)

# ---------- Pending Disavow Lines ----------
rec="Append ONLY if the previous SEO partner does not confirm this was a commissioned placement."
pend=[d for d,s in status.items() if s=="Held (Pending Partner)"]
pend_rows=[[d, f"domain:{d}", rec] for d in sorted(pend)]
rewrite("Pending Disavow Lines", pend_rows, 3)

# ---------- Disavow List ----------
dis=[d for d,s in status.items() if s=="Spam (Disavow)"]
dis_rows=[]
for d in sorted(dis, key=lambda x:(-(meta[x]["bl"]),x)):
    m=meta[d]; dis_rows.append([f"domain:{d}", m["as_"], m["bl"], None, None, None, m["top"]])
rewrite("Disavow List", dis_rows, 7)

# ---------- Summary ----------
sm=wb["Summary"]
sm["B1"].value="Black Walnut Construction, LLC"
cnt=Counter(status.values()); blby=defaultdict(int)
for d,s in status.items(): blby[s]+=meta[d]["bl"]
tot_d=sum(cnt.values()); tot_b=sum(blby.values())
desc={
 'Spam (Disavow)':"Confirmed spam with at least one dofollow link. Included in the disavow file.",
 'Held (Pending Partner)':"Exact-match commercial (Lexington SC) anchor, or a link aimed at a deep /...-construction-services money page. MAY be a commissioned placement. Out of the disavow file until the previous SEO supplier (the 'partner') confirms.",
 'Held (Nofollow, No Action)':"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
 'Spam (Nofollow, No Action)':"Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
 'Keep':"Genuine, branded or harmless link (incl. the agency's own site and higher-authority citations). Keep.",
 'Own Site':"Client-owned domain that redirects into the site.",
}
for i,s in enumerate(order_status):
    r=4+i
    sm.cell(row=r,column=1).value=s; sm.cell(row=r,column=2).value=cnt.get(s,0)
    sm.cell(row=r,column=3).value=blby.get(s,0); sm.cell(row=r,column=4).value=(cnt.get(s,0)/tot_d if tot_d else 0)
    sm.cell(row=r,column=5).value=desc[s]
sm.cell(row=10,column=1).value="Total"; sm.cell(row=10,column=2).value=tot_d
sm.cell(row=10,column=3).value=tot_b; sm.cell(row=10,column=4).value=1
for mr in list(sm.merged_cells.ranges):
    if mr.min_row>=11 or mr.min_row==1: sm.unmerge_cells(str(mr))
spam_tot=cnt['Spam (Disavow)']+cnt['Spam (Nofollow, No Action)']; held_tot=cnt['Held (Pending Partner)']+cnt['Held (Nofollow, No Action)']
# anchor-type profile from links
tcnt=Counter(); tdom=defaultdict(set)
for L in links:
    t=atype(L["anchor"]); tcnt[t]+=1
    d=host(L["src"]); root=d
    if d not in status:
        for k in sorted(status,key=len,reverse=True):
            if d==k or d.endswith("."+k): root=k;break
    tdom[t].add(root)
tot_links=sum(tcnt.values())
findings=[
 f"{spam_tot:,} of {tot_d:,} referring domains are spam. {cnt['Spam (Disavow)']:,} carry a dofollow link and go in the disavow file; {cnt['Spam (Nofollow, No Action)']} are nofollow and need no action.",
 f"The brief is stale. It cited 368 referring domains; the live profile (Semrush, 2026-11-04) is {tot_d:,} domains / {tot_b:,} backlinks. Referring domains sat near 60-90 through 2025, then exploded from ~206 (Jan 2026) to ~1,575 (Oct). The full live profile was audited, not the brief's list.",
 "One disavow file covers blackwalnutconstruction.com. No client-owned redirect domains were found (Own Site = 0); a domain-level property covers any subdomains, so a single file is enough.",
 "Two patterns, cleanly separable. All 1,395 link-scheme / PBN sales-copy links hit the home page; the commissioned-looking geo campaign hits the four deep /commercial-, /office-, /residential- and /retail-construction-services pages.",
 "The biggest single anchor, on 1,151 domains, is SEO sales copy ('blackwalnutconstruction.com premium authority backlinks for better search visibility'). A separate PBN anchor ('...DA 50 PA 40 Premium PBN... buy backlinks online cheap') spans 95 domains. This is auto-generated spam, not links the client bought.",
 f"{held_tot} domains are held for the previous SEO supplier to confirm, in case any were paid placements ({cnt['Held (Pending Partner)']} dofollow in the pending file, {cnt['Held (Nofollow, No Action)']} nofollow = no action). They are one directory/bookmark network using Lexington-SC service anchors.",
 "Held does not mean valuable: almost all referring domains sit at Authority Score 2-3 with no traffic, on a few shared hosts. Disavow only if Search Console shows a manual action or the supplier confirms buying links; otherwise monitor.",
]
sm.cell(row=11,column=1).value="Key findings"; sm.cell(row=11,column=1).font=Font(name="Geist",size=10,bold=True,color="FF000000")
for i,f in enumerate(findings):
    r=12+i; c=sm.cell(row=r,column=1); c.value=f
    c.font=Font(name="Geist",size=9,color="FF000000"); c.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)
    sm.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5); sm.row_dimensions[r].height=22.5
sm.cell(row=19,column=1).value="Anchor text profile (all backlinks)"; sm.cell(row=19,column=1).font=Font(name="Geist",size=11,bold=True,color="FF0C343D")
accent=PatternFill("solid",fgColor="FF0C343D"); white=PatternFill("solid",fgColor="FFFFFFFF")
hdr=["Anchor type","Backlinks","Share of Backlinks","Referring Domains"]
for c in range(1,5):
    cell=sm.cell(row=20,column=c); cell.value=hdr[c-1]; cell.font=Font(name="Geist",size=9,bold=True,color="FFFFFFFF"); cell.fill=accent; cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
rank=["Spam: keyword stuffed SEO sales copy","Naked URL","Exact match commercial (geo)","Exact match commercial","Generic","Branded","Empty or image","Spam: off topic","Contextual or other"]
rr=21
for t in rank:
    if tcnt.get(t,0)==0: continue
    for c,(val) in enumerate([t,tcnt[t],tcnt[t]/(tot_links or 1),len(tdom[t])],start=1):
        cell=sm.cell(row=rr,column=c); cell.value=val; cell.font=Font(name="Geist",size=9,color="FF000000"); cell.fill=white
    rr+=1
srow=rr+1
src=sm.cell(row=srow,column=1)
src.value=("Source: Semrush Backlink Analytics export, 2026-11-04 ({:,} backlinks / {:,} referring domains); cross-checked against Ahrefs. "
           "AS = Semrush Authority Score (0-100). RD/Traffic columns blank (not in Semrush refdomains export). Tab 05: supplier fills columns F (Y/N) and G.").format(tot_b,tot_d)
src.font=Font(name="Geist",size=8,color="FF666666"); src.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)
sm.merge_cells(start_row=srow,start_column=1,end_row=srow,end_column=5)
for _r in range(1, srow+1):
    sm.row_dimensions[_r].height=22.5
sm.merge_cells("B1:E2")
wb.save(OUT)
print("SAVED",OUT)
print("status:",dict(cnt)," tot_d",tot_d,"tot_b",tot_b)
print("tabs rows: RDA",len(rda_rows),"AllBL",len(ab_rows),"Anchors",len(an_rows),"Tab05",len(em_rows),"Pending",len(pend_rows),"Disavow",len(dis_rows))
