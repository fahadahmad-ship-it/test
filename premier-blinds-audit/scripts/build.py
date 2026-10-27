"""Build the Premier Blinds & Designs backlink audit workbook + disavow files,
in the signed-off Harbinger format (styling read from the K&K signed template).
Change the format here, never by hand in Excel."""
import os, sys, glob
from collections import Counter, defaultdict
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
import load, classify, pipeline
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CLIENT = "Premier Blinds & Designs"
ACCENT = "FF0C343D"; WHITE = "FFFFFFFF"
GEIST = "Geist"

thin = Side(style="thin", color="FF000000")
BORDER_HEADER = Border(left=thin, right=thin, top=thin)          # data-tab header: no bottom
BORDER_FULL = Border(left=thin, right=thin, top=thin, bottom=thin)
NOBORDER = Border()
accent_fill = PatternFill("solid", fgColor=ACCENT)
white_fill = PatternFill("solid", fgColor=WHITE)

def F(sz, bold=False, color="FF000000"): return Font(name=GEIST, size=sz, bold=bold, color=color)

# cell helpers -----------------------------------------------------------------
def hdr_cell(c, text):
    c.value = text; c.font = F(9, True, WHITE); c.fill = accent_fill
    c.border = BORDER_HEADER; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def data_cell(c, val, numfmt=None, align="left"):
    c.value = val; c.font = F(9); c.fill = white_fill; c.border = NOBORDER
    c.alignment = Alignment(horizontal=align, vertical="center")
    if numfmt: c.number_format = numfmt

def input_cell(c, val=""):
    c.value = val; c.font = F(9, False, WHITE); c.fill = accent_fill; c.border = NOBORDER
    c.alignment = Alignment(horizontal="center", vertical="center")

def write_table(ws, headers, rows, widths, data_h, numfmts=None, aligns=None, input_cols=()):
    numfmts = numfmts or {}; aligns = aligns or {}
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for j, h in enumerate(headers, 1):
        hdr_cell(ws.cell(row=1, column=j), h)
    ws.row_dimensions[1].height = 31.5
    for r, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            if (j-1) in input_cols:
                input_cell(ws.cell(row=r, column=j), val)
            else:
                data_cell(ws.cell(row=r, column=j), val,
                          numfmt=numfmts.get(j-1), align=aligns.get(j-1, "left"))
        ws.row_dimensions[r].height = data_h
    ws.freeze_panes = "B2"
    last = get_column_letter(len(headers))
    ws.auto_filter.ref = "A1:%s%d" % (last, max(1, len(rows)+1))
    ws.sheet_view.showGridLines = True

# ------------------------------------------------------------------ site type
def site_type(dom, v):
    h = dom.lower()
    if classify._any([r"listing", r"directory", r"\bdir\b"], h): return "Low quality web directory"
    if classify._any(classify.PRESS, h): return "Press-release syndication"
    if classify._any(classify.SPAM_HOST, h): return "Link network / PBN host"
    if v["ascore"] >= 20: return "Established site"
    return "Unknown / low quality"

def market(anchor):
    a = anchor.lower()
    if "peachtree" in a: return "Peachtree City GA"
    if "atlanta" in a: return "Atlanta GA"
    if classify.has_geo(a): return "Georgia"
    return "Non-geo"

def build():
    ds = pipeline.build()
    domains = ds["domains"]; links = ds["links"]
    os.makedirs(OUT, exist_ok=True)
    wb = Workbook(); wb.remove(wb.active)

    # ===== derive summary numbers =====
    order = ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)",
             "Spam (Nofollow, No Action)","Keep","Own Site"]
    meaning = {
        "Spam (Disavow)":"Confirmed spam with at least one dofollow link. Included in the disavow file.",
        "Held (Pending Partner)":"Exact-match commercial anchor, or a link aimed at a product/service page. May have been commissioned. Not in the disavow file until the previous partner confirms.",
        "Held (Nofollow, No Action)":"Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
        "Spam (Nofollow, No Action)":"Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
        "Keep":"Genuine or harmless link. Keep.",
        "Own Site":"Client-owned domain that redirects into the site.",
    }
    dom_count = Counter(v["status"] for v in domains.values())
    bl_count = Counter();
    for v in domains.values(): bl_count[v["status"]] += v["backlinks"]
    tot_dom = len(domains); tot_bl = sum(v["backlinks"] for v in domains.values())

    # anchor profile
    at_bl = Counter(); at_dom = defaultdict(set)
    for lo in links:
        at_bl[lo["anchor_type"]] += 1; at_dom[lo["anchor_type"]].add(lo["refdomain"])
    atype_order = ["Spam: keyword stuffed SEO sales copy","Naked URL","Exact match commercial",
                   "Exact match commercial (geo)","Generic","Branded","Empty or image",
                   "Spam: off topic","Contextual or other"]

    # home vs deep
    home_links = sum(1 for lo in links if not classify.is_deep_page(lo["target_url"]))
    deep_links = len(links) - home_links
    # dominant anchor
    top_anchor, top_anchor_n = Counter(lo["anchor"].strip() for lo in links).most_common(1)[0]
    top_anchor_doms = len({lo["refdomain"] for lo in links if lo["anchor"].strip()==top_anchor})
    # held IP concentration (/24)
    held = [v for v in domains.values() if v["status"].startswith("Held")]
    def net24(ip):
        p = ip.split("."); return ".".join(p[:3]) if len(p)==4 else ip
    held_nets = Counter(net24(v["ip"]) for v in held if v["ip"])
    top3 = held_nets.most_common(3)
    top3_share = sum(n for _,n in top3)
    held_lowas = sum(1 for v in held if v["ascore"] <= 2)
    spam_dof = dom_count["Spam (Disavow)"]; spam_nof = dom_count["Spam (Nofollow, No Action)"]
    spam_total = spam_dof + spam_nof

    key_findings = [
        "%d of the %d referring domains are spam. %d have a dofollow link and go in the disavow file; the other %d are nofollow and need no action." % (spam_total, tot_dom, spam_dof, spam_nof),
        "The attack exploded in the last month: 782 referring domains in September 2026, %d now. We audited the full live profile." % tot_dom,
        "The client owns two Search Console properties: premierblindsanddesigns.com and thepremierdesigns.com, which 301s into it. A disavow file is provided for each; the money-site file carries the full union of every bad domain.",
        "Two patterns, easy to tell apart. %d links hit the home page (the link-scheme flood); the other %d hit deep product/service pages (the commissioned-looking campaign). The home-page flood is the attack." % (home_links, deep_links),
        "The biggest anchor, on %d domains, is backlink sales copy naming the client's own domain: \"%s\"." % (top_anchor_doms, top_anchor[:70]),
        "%d domains are held for the previous SEO provider (the \"partner\") to confirm, in case any were paid placements. Unlike the home-page flood, they are NOT one IP network - they scatter across many hosts and /24 ranges (the three largest hold only %d between them). Most are low-quality web directories and listing sites carrying exact-match geo anchors to deep product pages." % (len(held), top3_share),
        "Held does not mean valuable: %d of the %d held domains sit at Authority Score 2 or below and none above 19. Per-domain organic traffic was not pulled (see delivery note); Authority Score is the authority signal used here." % (held_lowas, len(held)),
    ]

    # ===== Tab 1 Summary =====
    ws = wb.create_sheet("Summary")
    ws.sheet_view.showGridLines = False
    for col, w in zip("ABCDE", [38.86,16.29,17.57,18.71,120.0]):
        ws.column_dimensions[col].width = w
    ws.merge_cells("B1:E2")
    t = ws["B1"]; t.value = CLIENT; t.font = F(21, True, ACCENT)
    t.alignment = Alignment(horizontal="center", vertical="center")
    # status table header row3
    for j, h in enumerate(["Status","Domains","Backlinks","Share of Domains","What it means"],1):
        c = ws.cell(row=3, column=j); c.value=h; c.font=F(10,True,WHITE); c.fill=accent_fill
        c.border=BORDER_FULL; c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    r = 4
    for st in order:
        if dom_count.get(st,0)==0 and st not in ("Held (Nofollow, No Action)","Own Site"):
            pass
        vals = [st, dom_count.get(st,0), bl_count.get(st,0), (dom_count.get(st,0)/tot_dom if tot_dom else 0), meaning[st]]
        for j,val in enumerate(vals,1):
            c=ws.cell(row=r,column=j); c.font=F(9); c.fill=white_fill; c.border=BORDER_FULL
            if j==1: c.alignment=Alignment(horizontal="left",vertical="center"); c.value=val
            elif j in (2,3): c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="#,##0"
            elif j==4: c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="0.0%"
            else: c.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True); c.value=val
        r+=1
    # total row
    for j,val in enumerate(["Total",tot_dom,tot_bl,1.0,""],1):
        c=ws.cell(row=r,column=j); c.font=F(9,True); c.fill=white_fill; c.border=BORDER_FULL
        if j==1: c.alignment=Alignment(horizontal="left",vertical="center"); c.value=val
        elif j in (2,3): c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="#,##0"
        elif j==4: c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="0.0%"
    kf_start = r+2
    kc = ws.cell(row=kf_start, column=1); kc.value="Key findings"; kc.font=F(10,True,"FF000000")
    for i, kf in enumerate(key_findings):
        rr = kf_start+1+i
        ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=5)
        c = ws.cell(row=rr,column=1); c.value=kf; c.font=F(9,color=ACCENT)
        c.alignment=Alignment(horizontal="left",vertical="center",wrap_text=True)
    ap_head = kf_start+1+len(key_findings)+1
    ws.cell(row=ap_head,column=1).value="Anchor text profile (all backlinks)"
    ws.cell(row=ap_head,column=1).font=F(11,True,ACCENT)
    for j,h in enumerate(["Anchor type","Backlinks","Share of Backlinks","Referring Domains"],1):
        c=ws.cell(row=ap_head+1,column=j); c.value=h; c.font=F(9,True,WHITE); c.fill=accent_fill
        c.border=BORDER_FULL; c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    rr = ap_head+2
    for at in atype_order:
        if at_bl.get(at,0)==0: continue
        vals=[at, at_bl[at], at_bl[at]/len(links), len(at_dom[at])]
        for j,val in enumerate(vals,1):
            c=ws.cell(row=rr,column=j); c.font=F(9); c.fill=white_fill; c.border=BORDER_FULL
            if j==1: c.alignment=Alignment(horizontal="left",vertical="center"); c.value=val
            elif j==3: c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="0.0%"
            else: c.alignment=Alignment(horizontal="center",vertical="center"); c.value=val; c.number_format="#,##0"
        rr+=1
    for ridx in range(1, rr+1):
        ws.row_dimensions[ridx].height = 22.5
    logo = os.path.join(DATA,"harbinger_logo.png")
    if os.path.exists(logo):
        img = XLImage(logo); img.anchor = "A1"
        ws.add_image(img, "A1")

    # ===== Tab 2 Referring Domain Audit =====
    ws = wb.create_sheet("Referring Domain Audit")
    H2 = ["Domain","Status","AS","Backlinks","RD's","Traffic","In Disavow","Links Point To",
          "Dofollow Links","Nofollow Links","First Seen","Top Anchor Text","Example Linking Page",
          "Linking Page Title","Source","IP","Disavow Line"]
    W2 = [36,24.71,9.57,13,9.43,9.71,12.43,21.29,14,8.71,12,45,8.71,40,14,15,14]
    rows2=[]
    for d in sorted(domains):
        v=domains[d]
        rows2.append([v["domain"],v["status"],v["ascore"],v["backlinks"],
                      "" if v["rds"] is None else v["rds"], v["traffic"], v["in_disavow"],
                      v["points_to"], v["dofollow"], v["nofollow"], v["first_seen"],
                      v["top_anchor"], v["example_page"], v["example_title"], "Semrush",
                      v["ip"], v["disavow_line"]])
    write_table(ws,H2,rows2,W2,15.75,
                numfmts={2:"0.0",3:"#,##0",5:"#,##0",8:"#,##0",9:"#,##0",10:"d mmm yyyy"},
                aligns={2:"center",3:"center",4:"center",5:"center",6:"center",8:"center",9:"center",10:"center"})

    # ===== Tab 3 All Backlinks =====
    ws = wb.create_sheet("All Backlinks")
    H3=["Referring Domain","Status","Tool","Anchor Text","Anchor Type","Link Type",
        "Linking Page URL","Linking Page Title","Target URL"]
    W3=[25.43,27.14,14.71,55,32,10,55,53.14,30.57]
    rows3=[[lo["refdomain"],lo["status"],lo["tool"],lo["anchor"],lo["anchor_type"],
            lo["link_type"],lo["page_url"],lo["page_title"],lo["target_url"]] for lo in links]
    write_table(ws,H3,rows3,W3,22.5,aligns={5:"center"})

    # ===== Tab 4 Anchor Analysis =====
    ws = wb.create_sheet("Anchor Analysis")
    H4=["Anchor Text","Anchor Type","Backlinks","Share of Backlinks","Referring Domains","Spam Domains Using It"]
    W4=[115.86,37.71,14,8.71,8.71,20.29]
    arows=[]
    for a,rec in ds["anchors"].items():
        arows.append([a,rec["type"],rec["bl"],rec["bl"]/ds["total_links"],len(rec["doms"]),len(rec["spamdoms"])])
    arows.sort(key=lambda x:-x[2])
    write_table(ws,H4,arows,W4,22.5,
                numfmts={2:"#,##0",3:"0.0%",4:"#,##0",5:"#,##0"},
                aligns={2:"center",3:"center",4:"center",5:"center"})

    # ===== Tab 5 Exact Match Anchors =====
    ws = wb.create_sheet("Exact Match Anchors")
    H5=["Referring domain","Example backlink (linking page)","Exact-match commercial anchor",
        "Market","Site type (indicative)","Partner confirmed? (Y/N)","Final decision"]
    W5=[25.43,59,53.14,16,24.57,15.43,15]
    rows5=[]
    for d in sorted(domains):
        v=domains[d]
        if not v["status"].startswith("Held"): continue
        seen=set()
        for l in v["links"]:
            at=classify.anchor_type(l["anchor"])
            if at in classify.EXACT_TYPES:
                a=l["anchor"].strip()
                if a in seen: continue
                seen.add(a)
                rows5.append([d,l["source_url"],a,market(a),site_type(d,v),"",""])
    rows5.sort(key=lambda x:x[0])
    write_table(ws,H5,rows5,W5,22.5,input_cols=(5,6))

    # ===== Tab 6 Pending Disavow Lines =====
    ws = wb.create_sheet("Pending Disavow Lines")
    H6=["Referring domain","Disavow line (append to disavow.txt once confirmed)","Recommendation"]
    W6=[32,44,48]
    rows6=[]
    for d in sorted(domains):
        v=domains[d]
        if v["status"]!="Held (Pending Partner)": continue
        rows6.append([d,"domain:"+d,"Append only if the previous SEO provider does not claim this link as a commissioned placement."])
    write_table(ws,H6,rows6,W6,22.5)

    # ===== Tab 7 Disavow List =====
    ws = wb.create_sheet("Disavow List")
    H7=["Disavow Line","AS","Backlinks","RD's","Traffic","Organic Keywords","Top Anchor Text"]
    W7=[44,14,15.57,14,11.14,14.86,98.86]
    rows7=[]
    for d in ds["emitted"]:
        v=domains[d]
        rows7.append(["domain:"+d, v["ascore"], v["backlinks"], "", v["traffic"], v["orgkw"], v["top_anchor"]])
    write_table(ws,H7,rows7,W7,22.5,
                numfmts={1:"0.0",2:"#,##0",4:"#,##0",5:"#,##0"},
                aligns={1:"center",2:"center",3:"center",4:"center",5:"center"})

    path = os.path.join(OUT, "Premier_Blinds_and_Designs_Backlinks_Audit.xlsx")
    wb.save(path)
    print("wrote", path)
    print("summary: domains=%d backlinks=%d disavow lines=%d held=%d keep=%d" %
          (tot_dom, tot_bl, len(ds["emitted"]), len(held), dom_count["Keep"]))
    return ds

if __name__ == "__main__":
    build()
