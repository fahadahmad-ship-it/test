import csv,collections,datetime,re
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter

D='/home/user/test/audit/data/'
OUT='/home/user/test/New_Image_Canopy_Backlinks_Audit.xlsx'
NAVY='FF1F3864'; F='Geist'
FILL={'Spam (Disavow)':'FFEAD1DC','Spam (Nofollow, No Action)':'FFD5A6BD','Keep':'FFC27BA0',
      'Own Site':'FFA64D79','HELD - pending partner':'FFFFF2CC','HELD - review':'FFFFE599'}
BLUE='FFD9E2F3'; WHITE='FFFFFFFF'
thin=Side(style='thin'); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)

def hdr(ws,row=1,sz=9):
    for c in ws[row]:
        if c.value is None: continue
        c.font=Font(name=F,sz=sz,b=True,color='FFFFFFFF')
        c.fill=PatternFill('solid',fgColor=NAVY)
        c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        c.border=BORD
    ws.row_dimensions[row].height=31.5
def style(ws,r,fill,numfmts=None,centre=(),valign='center'):
    for c in ws[r]:
        c.font=Font(name=F,sz=9,color='FF000000')
        c.fill=PatternFill('solid',fgColor=fill)
        c.border=BORD
        c.alignment=Alignment(vertical=valign,horizontal='center' if c.column_letter in centre else None)
        if numfmts and c.column_letter in numfmts: c.number_format=numfmts[c.column_letter]
def widths(ws,m):
    for k,v in m.items(): ws.column_dimensions[k].width=v
def dt(ts):
    try: return datetime.datetime.utcfromtimestamp(int(ts)).date()
    except: return ''

AUD=list(csv.DictReader(open(D+'domain_audit.csv'),delimiter=';'))
BL =list(csv.DictReader(open(D+'backlinks_all.csv'),delimiter=';'))
def host(u):
    m=re.match(r'https?://([^/]+)',u or ''); 
    return re.sub(r'^www\.','',m.group(1).lower().split(':')[0]) if m else ''
AT={}
PBN  = re.compile(r'(seo authority|seo links|backlink|pbn|buy backlink|da 50|pa 40|rank first page|link building|dofollow|white hat seo|outreach backlinks|premium backlinks|sitetosocial|link profile|organic visibility|da and dr|safe link velocity|placement reporting)',re.I)
CANOPY=re.compile(r'(station canopy|gas canop|canopy light|canopy repair|canopy design|canopy construction|canopy solutions|canopy services|canopies|gas station imaging|gas pump canopy|fuel station|petrol station|canopy for sale|canopy installation|canopy manufacturers|commercial canopy|canopy in |canopy the purpose|purpose of a gas station canopy)',re.I)
GEO=re.compile(r'(austin|dallas|houston|tulsa|oklahoma city)',re.I)
BRAND=re.compile(r'(new ?image ?canopy|shady ?vent)',re.I); NAKED=re.compile(r'^(https?://|www\.)',re.I)
GENERIC=re.compile(r'^(visit website|website|click here|about|contact|services|project gallery|read more|check this source|here|link|visit site|icon - external link visit website|mistakes|6|,|\.)$',re.I)
def atype(a):
    a=(a or '').strip()
    if not a: return 'Empty or image'
    if PBN.search(a): return 'Spam: keyword stuffed SEO sales copy'
    if CANOPY.search(a): return 'Exact-match commercial (geo)' if GEO.search(a) else 'Exact-match commercial'
    if GENERIC.match(a): return 'Generic'
    if BRAND.search(a) and not NAKED.match(a): return 'Branded'
    if NAKED.match(a) or re.match(r'^[a-z0-9-]+\.(com|net|org|info)/?$',a,re.I): return 'Naked URL'
    return 'Contextual or other'
for r in BL: r['rd']=host(r['source_url']); r['atype']=atype(r['anchor'])
STAT={r['domain']:r['status'] for r in AUD}
TAB03=set(l.strip() for l in open(D+'tab03_named.txt') if l.strip())

MKT={'austin':'Austin, TX','dallas':'Dallas, TX','houston':'Houston, TX','tulsa':'Tulsa, OK','oklahoma city':'Oklahoma City, OK'}
AUDD={r['domain']:r for r in AUD}
def tgt_kind(u):
    if '/location/' in u or re.search(r'/gas-?station-canopy-construction-',u): return 'Geo landing page'
    if '/service/' in u: return 'Service page'
    if u.rstrip('/')=='https://newimagecanopy.com': return 'Homepage'
    return 'Other page'
emrows=[]
for r in BL:
    a=(r['anchor'] or '').strip()
    if not a or not r['atype'].startswith('Exact-match'): continue
    d=r['rd']; rec=AUDD.get(d,{}); st=rec.get('status','')
    m=GEO.search(a)
    emrows.append(dict(d=d,a=a,mk=MKT[m.group(1).lower()] if m else 'Non-geo',
        site=rec.get('sitetype','Low-quality web directory'),
        link='Nofollow' if r['nofollow']=='true' else 'Dofollow',
        src=r['source_url'],title=r['source_title'],tgt=r['target_url'],
        tkind=tgt_kind(r['target_url']),fs=r['first_seen'],
        reco='Keep - genuine editorial placement, no confirmation needed' if st=='Keep' else 'Disavow after confirmation',
        st=st))
emrows.sort(key=lambda x:(x['d'],x['a']))
em={r['d'] for r in emrows}
EM_ROWS=len(emrows); EM_DOMS=len(em); EM_PAIRS=len({(r['d'],r['a']) for r in emrows})
EM_HOLD=sorted({r['d'] for r in emrows if r['st']!='Keep'})
EM_KEEP=sorted({r['d'] for r in emrows if r['st']=='Keep'})
EM_DEEP=sum(1 for r in emrows if r['tkind']!='Homepage')

dis_pre=[r for r in AUD if r['status']=='Spam (Disavow)']
wb=openpyxl.Workbook(); 

# ---------------- 01 Summary ----------------
ws=wb.active; ws.title='Summary'; ws.sheet_view.showGridLines=False
widths(ws,{'A':48,'B':16.29,'C':17.57,'D':18.71,'E':94})
ws['A1']='https://newimagecanopy.com/'; ws.merge_cells('A1:B1')
ws['A1'].font=Font(name=F,sz=16,b=True,color=NAVY); ws['A1'].alignment=Alignment(vertical='center')
ws.append(['Status','Domains','Backlinks','Share of Domains','What it means'])
SUMMARY_HDR_SZ=10
cnt=collections.Counter(r['status'] for r in AUD)
blc=collections.Counter(); 
for r in AUD: blc[r['status']]+=int(r['backlinks'] or 0)
tot=sum(cnt.values())
MEAN={'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'HELD - pending partner':'Exact-match commercial anchor. May have been commissioned. NOT in the disavow file until the previous SEO vendor confirms.',
 'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Keep':'Genuine or harmless link. Keep.','Own Site':'Client owned property or sister brand. Keep.'}
for s in ['Spam (Disavow)','HELD - pending partner','Spam (Nofollow, No Action)','Keep','Own Site']:
    ws.append([s,cnt[s],blc[s],cnt[s]/tot,MEAN[s]])
ws.append(['Total',tot,sum(blc.values()),1.0,''])
for r in range(2,ws.max_row+1):
    ws.row_dimensions[r].height=22.5
    if r==2: hdr(ws,2,sz=10)
    else:
        s=ws.cell(r,1).value
        style(ws,r,FILL.get(s,WHITE) if s!='Total' else WHITE,{'B':'#,##0','C':'#,##0','D':'0.00%'},centre=('B','C','D'))
        ws.cell(r,5).alignment=Alignment(vertical='center',wrap_text=True)
        if s=='Total':
            for c in ws[r]: c.font=Font(name=F,sz=9,b=True)

def block(title,lines,sz=11):
    ws.append([]); ws.append([title])
    r=ws.max_row; ws.cell(r,1).font=Font(name=F,sz=sz,b=True,color=NAVY); ws.row_dimensions[r].height=22.5
    for t in lines:
        ws.append([t]); rr=ws.max_row; ws.merge_cells(f'A{rr}:E{rr}')
        ws.cell(rr,1).font=Font(name=F,sz=9); ws.cell(rr,1).alignment=Alignment(vertical='center',wrap_text=True)
        ws.row_dimensions[rr].height=22.5

held=cnt['HELD - pending partner']; spam=cnt['Spam (Disavow)']+cnt['Spam (Nofollow, No Action)']
block('Key findings',sz=10,lines=[
 f"{spam:,} of the {tot:,} referring domains are spam. {cnt['Spam (Disavow)']:,} have at least one dofollow link and go in the disavow file; the other {cnt['Spam (Nofollow, No Action)']} are nofollow only and need no action.",
 f"{held} referring domains carry exact-match commercial anchors (gas station canopy services, and geo variants for Austin TX, Dallas TX, Houston TX, Tulsa OK and Oklahoma City OK). These look commissioned, are HELD OUT of the disavow file, and must be confirmed with the previous SEO vendor before any are submitted.",
 "newimagecanopy.com is the target of a large automated link attack that accelerated sharply in October 2026: referring domains went from 925 to 2,445 in a single month (+1,520).",
 "2,178 of 3,821 backlinks (57%) use keyword-stuffed SEO sales copy as anchor text, which makes the brand look like a link seller. The single largest anchor, on 994 referring domains, is 'build strong seo authority with high quality links from shadyvent.com'.",
 "The spam copy reuses the client's own brand names (New Image Canopy and the client-owned redirect domain shadyvent.com / Shady Vent Construction, Inc.) inside link-selling sentences - the signature of an automated negative SEO template, not of anything the client bought.",
 "shadyvent.com is confirmed client-owned: it shares server IP 67.225.152.101 with newimagecanopy.com and is the single largest referring domain (18 links).",
 "93.3% of referring domains sit at Semrush Authority Score 0-2, and only 26 are above AS 10. 1,512 of them are on throwaway TLDs (.shop, .online, .website, .space, .store, .site).",
 f"{cnt['Keep']} domains are genuine and are kept (Yellow Pages AS69, Grokipedia AS69, Birdeye AS66, Scam-Detector AS58, Accio AS54, Superpages AS47, Owler AS41, PEI.org AS40, RoofingCalculator AS39, DexKnows AS37). None of them are in the disavow file.",
 "All 18 referring domains named in the client's Tab 03 extract were found in the live Semrush index and independently classified as Spam (Disavow). They are flagged 'Yes' in the Tab 03 column of the Domain Audit tab.",
])
block('Authority Score vs competitor set',[])
ws.append(['Domain','Authority Score','Referring domains','Follow links','Note']); hdr(ws,ws.max_row)
COMP=[('newimagecanopy.com (client)',9,2445,3589,'Most referring domains, lowest Authority Score'),
 ('austinmohawk.com',16,954,7959,'Named competitor - 2.6x the follow links from a third of the domains'),
 ('tfccanopy.com',15,708,838,'Named competitor'),
 ('cscanopy.com',10,1376,1610,'Direct canopy competitor'),
 ('sheltersdirect.com',10,1519,2201,'Direct canopy competitor'),
 ('madisonind.com',10,1237,4172,'Direct canopy competitor'),
 ('shadyvent.com (client redirect)',2,1280,1312,'Client-owned, hit by the same attack - needs its own audit')]
for d,a,r_,f_,n in COMP:
    ws.append([d,a,r_,f_,n]); rr=ws.max_row
    style(ws,rr,'FFF2F2F2' if 'client' in d else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True); ws.row_dimensions[rr].height=22.5

block('Anchor text profile (all backlinks)',[])
ws.append(['Anchor type','Backlinks','Share of Backlinks','Referring Domains','']); hdr(ws,ws.max_row)
at=collections.Counter(r['atype'] for r in BL)
ad=collections.defaultdict(set)
for r in BL: ad[r['atype']].add(r['rd'])
for k,v in at.most_common():
    ws.append([k,v,v/len(BL),len(ad[k]),'']); rr=ws.max_row
    style(ws,rr,WHITE,{'B':'#,##0','C':'0.00%','D':'#,##0'},centre=('B','C','D')); ws.row_dimensions[rr].height=22.5

block('Exact-match anchors - held for client decision',[
 f"{EM_DOMS} referring domains carry {EM_PAIRS} distinct exact-match commercial anchors. Every one of them is listed on the 'Exact-Match Anchors' tab so the client can decide domain by domain. None are in disavow.txt.",
 f"{len(EM_HOLD)} of those domains are recommended for disavow once the previous SEO vendor confirms they were not commissioned. Their ready-made disavow lines are on the 'Pending Disavow Lines' tab - append them to disavow.txt only after confirmation.",
 f"{len(EM_KEEP)} are genuine editorial placements that should be kept regardless of who commissioned them ({', '.join(EM_KEEP)}).",
 f"EVIDENCE THEY WERE COMMISSIONED: {EM_DEEP} of the {EM_ROWS} exact-match links ({EM_DEEP/EM_ROWS*100:.1f}%) point at deep money pages - /service/canopies/, /service/canopy-lighting/, /service/canopy-repairs/, /service/light-commercial/, /service/imaging/ and the five geo landing pages. By contrast ALL 2,178 PBN self-advertising links point at the homepage and nothing else. An automated attack does not build links to /service/canopy-lighting/; deliberate page-level targeting is campaign behaviour. This is the strongest reason not to disavow this set until the vendor has been asked.",
 "Every exact-match link is listed individually on the 'Exact-Match Anchors' tab with its linking page URL, linking page title, target URL, target page type, link type and first-seen date, so each one can be opened and verified.",
 "Fill the blue columns on the 'Exact-Match Anchors' tab (Partner confirmed? / Commissioned by / Final decision) with the vendor.",
])
ws.append(['Anchor category','Ref. domains','Action','Status','']); hdr(ws,ws.max_row)
ACT=[('Link-scheme / PBN service-advertising anchors',1705,'Disavow','In disavow.txt'),
     ('Low-authority directory / bookmark placements',131,'Disavow','In disavow.txt'),
     ('Off-topic casino / pharma anchors',27,'Disavow','In disavow.txt'),
     ('SEO-tool / link-selling network domains',30,'Disavow','In disavow.txt'),
     ('Exact-match commercial anchors',len(EM_HOLD),'Confirm who commissioned before disavowing','HELD - pending partner'),
     ('Exact-match on genuine editorial sites',len(EM_KEEP),'Retain','Not in file'),
     ('Brand, URL and natural anchors','Remainder','Retain','Not in file'),
     ('Total domain: entries in disavow.txt',len(dis_pre),'','')]
for a,b_,c_,d_ in ACT:
    ws.append([a,b_,c_,d_,'']); rr=ws.max_row
    style(ws,rr,FILL['HELD - pending partner'] if 'HELD' in str(d_) else WHITE,{'B':'#,##0'},centre=('B',))
    ws.row_dimensions[rr].height=22.5

block('Target URL split - attack vs campaign',[])
ws.append(['Link population','Backlinks','Homepage','Deep pages','Reading']); hdr(ws,ws.max_row)
_pbn=[r for r in BL if r['atype']=='Spam: keyword stuffed SEO sales copy']
_pbn_deep=sum(1 for r in _pbn if r['target_url'].rstrip('/')!='https://newimagecanopy.com')
for nm,tot_,deep_,note in [
  ('PBN self-advertising anchors',len(_pbn),_pbn_deep,'100% homepage only. Automated, no page-level targeting - an attack.'),
  ('Exact-match commercial anchors',EM_ROWS,EM_DEEP,'97.2% deep service and geo landing pages - deliberate targeting, i.e. a campaign.')]:
    ws.append([nm,tot_,tot_-deep_,deep_,note]); rr=ws.max_row
    style(ws,rr,FILL['HELD - pending partner'] if 'Exact' in nm else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True); ws.row_dimensions[rr].height=22.5
ws.append([]); ws.append(['Target page','Exact-match links','','','']); hdr(ws,ws.max_row)
_t=collections.Counter(r['tgt'] for r in emrows)
for u,n in _t.most_common(12):
    ws.append([u,n,'','','']); rr=ws.max_row
    style(ws,rr,WHITE,{'B':'#,##0'},centre=('B',)); ws.row_dimensions[rr].height=22.5

block('Important caveats',[
 "Semrush Authority Score ignores the disavow file - it is a third-party metric. Submitting this file will NOT move Authority Score from 9 to 15. Disavow is a Google-side safety action. The Authority Score gap to austinmohawk.com (AS 16) is a link-acquisition problem: they have 7,959 follow links from genuine industry sites. Those are two separate pieces of work.",
 "Data source is Semrush only. Ahrefs API units for this workspace were exhausted (800,068 of 800,000 used, resetting 25 Oct 2026), so unlike a two-source audit every row here is Semrush-sourced.",
 "shadyvent.com has its own 1,280 referring domains from the same network. Because it redirects into newimagecanopy.com those links pass through to the client, so it needs a parallel audit and its own disavow file. That is not covered by this workbook.",
 "Do not submit the disavow file to Google Search Console until the previous SEO vendor has confirmed which of the 544 HELD domains were commissioned.",
])
block('Method',[
 f"Prepared {datetime.date.today():%d %b %Y} from the Semrush live index. {len(AUD):,} referring domains and {len(BL):,} backlinks assessed.",
 "Status rules: Own Site = client property. Keep = genuine or editorially harmless. HELD = carries an exact-match commercial anchor, so it may have been commissioned. Spam (Disavow) = link-scheme, casino/pharma, SEO-tool-network or low-authority directory placement with at least one dofollow link. Spam (Nofollow, No Action) = the same, but every link is nofollow.",
])

# ---------------- 02 Domain Audit ----------------
ws=wb.create_sheet('Domain Audit')
COLS=['Domain','Status','Group','Site Type (indicative)','AS','Backlinks','Dofollow Links','Nofollow Links',
      'First Seen','In Disavow','Named in Tab 03','Top Anchor Text','Anchor Types','Example Linking Page',
      'Linking Page Title','Source','IP','Country','Disavow Line']
ws.append(COLS); hdr(ws)
for r in AUD:
    ws.append([r['domain'],r['status'],r['group'],r['sitetype'],int(r['ascore'] or 0),int(r['backlinks'] or 0),
      r['dofollow'],r['nofollow'],dt(r['first_seen']),
      'Yes' if r['status'].startswith('Spam (Disavow)') else ('HELD' if r['status'].startswith('HELD') else 'No'),
      r['tab03'],r['top_anchor'],r['atypes'],r['example_page'],r['page_title'],'Semrush',r['ip'],r['country'],
      r['disavow_line'] if r['status']=='Spam (Disavow)' else ''])
    style(ws,ws.max_row,FILL.get(r['status'],WHITE),
      {'E':'#,##0','F':'#,##0','G':'#,##0','H':'#,##0','I':'d mmm yyyy'},centre=('E','F','G','H','I','J','K','P','R'),valign='top')
widths(ws,{'A':34,'B':22,'C':44,'D':24,'E':7,'F':10,'G':12,'H':12,'I':13,'J':11,'K':14,'L':46,'M':40,'N':52,'O':46,'P':10,'Q':16,'R':9,'S':30})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:S{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---------------- 03 Anchor Analysis ----------------
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains','Spam Domains Using It','Named in Tab 03','Target URL(s)','Target Page Type','Example Linking Page']); hdr(ws)
agg=collections.defaultdict(lambda:{'bl':0,'rd':set(),'spam':set(),'t3':set(),'type':''})
for r in BL:
    a=(r['anchor'] or '').strip() or '<EmptyAnchor>'
    g=agg[a]; g['bl']+=1; g['rd'].add(r['rd']); g['type']=r['atype']
    g.setdefault('tgt',set()).add(r['target_url']); g.setdefault('src','') or g.__setitem__('src',r['source_url'])
    if STAT.get(r['rd'],'').startswith('Spam'): g['spam'].add(r['rd'])
    if r['rd'] in TAB03: g['t3'].add(r['rd'])
for a,g in sorted(agg.items(),key=lambda x:-x[1]['bl']):
    tg=sorted(g.get('tgt',set()))
    ws.append([a,g['type'],g['bl'],g['bl']/len(BL),len(g['rd']),len(g['spam']),len(g['t3']) or '',
               ' | '.join(tg)[:460], tgt_kind(tg[0]) if len(tg)==1 else ('Mixed' if len(tg)>1 else ''),
               g.get('src','')])
    style(ws,ws.max_row,FILL['HELD - pending partner'] if g['type'].startswith('Exact-match') else WHITE,
      {'C':'#,##0','D':'0.00%','E':'#,##0','F':'#,##0'},centre=('C','D','E','F','G'))
widths(ws,{'A':104.57,'B':37.71,'C':14,'D':18,'E':20,'F':22,'G':16,'H':70,'I':20,'J':58})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---------------- 04 Exact-Match Anchors (ALL) ----------------
# Every referring domain carrying an exact-match commercial anchor, regardless of
# how the domain itself was classified. Nothing commissioned can be missed here.
ws=wb.create_sheet('Exact-Match Anchors')
ws.append(['Referring domain','Exact-match commercial anchor','Market','Site type (indicative)','Link Type',
           'Linking Page URL','Linking Page Title','Target URL','Target Page Type','First Seen','Recommendation',
           'Partner confirmed? (Y/N)','Commissioned by','Final decision']); hdr(ws)
for r in emrows:
    ws.append([r['d'],r['a'],r['mk'],r['site'],r['link'],r['src'],r['title'],r['tgt'],r['tkind'],dt(r['fs']),
               r['reco'],'','',''])
    style(ws,ws.max_row,'FFE2EFDA' if r['st']=='Keep' else FILL['HELD - pending partner'],
          {'J':'d mmm yyyy'},centre=('C','E','I','J'))
    for col in ('L','M','N'):
        ws[f'{col}{ws.max_row}'].fill=PatternFill('solid',fgColor=BLUE)
widths(ws,{'A':30,'B':62,'C':18,'D':26,'E':11,'F':62,'G':50,'H':62,'I':18,'J':13,'K':46,'L':22,'M':24,'N':20})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:N{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---------------- 05 Pending Disavow Lines ----------------
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation',
           'Exact-match anchors','Target pages hit','Links']); hdr(ws)
byd=collections.defaultdict(list)
for r in emrows: byd[r['d']].append(r)
for d in EM_HOLD:
    rs=byd[d]
    ws.append([d,'domain:'+d,'Disavow after confirmation',
               ' | '.join(sorted({x['a'] for x in rs}))[:460],
               ' | '.join(sorted({x['tgt'] for x in rs}))[:460], len(rs)])
    style(ws,ws.max_row,FILL['HELD - pending partner'],{'F':'#,##0'},centre=('F',))
widths(ws,{'A':32,'B':52,'C':30,'D':70,'E':70,'F':9})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:F{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---------------- 05 All Backlinks ----------------
ws=wb.create_sheet('All Backlinks')
ws.append(['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL','Linking Page Title','Target URL','First Seen']); hdr(ws)
for r in sorted(BL,key=lambda x:(x['rd'],x['anchor'] or '')):
    s=STAT.get(r['rd'],'')
    ws.append([r['rd'],s,'Semrush',r['anchor'],r['atype'],'Nofollow' if r['nofollow']=='true' else 'Dofollow',
               r['source_url'],r['source_title'],r['target_url'],dt(r['first_seen'])])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'J':'d mmm yyyy'},centre=('C','F','J'))
widths(ws,{'A':25.43,'B':24,'C':11,'D':55,'E':32,'F':11,'G':55,'H':53.14,'I':38,'J':14})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---------------- 06 Disavow List ----------------
ws=wb.create_sheet('Disavow List')
ws.append(['Disavow Line','AS','Backlinks','Dofollow Links','First Seen','Group','Top Anchor Text','Named in Tab 03']); hdr(ws)
dis=[r for r in AUD if r['status']=='Spam (Disavow)']
dis.sort(key=lambda r:r['domain'])
for r in dis:
    ws.append([r['disavow_line'],int(r['ascore'] or 0),int(r['backlinks'] or 0),r['dofollow'],dt(r['first_seen']),r['group'],r['top_anchor'],r['tab03']])
    style(ws,ws.max_row,FILL['Spam (Disavow)'],{'B':'#,##0','C':'#,##0','D':'#,##0','E':'d mmm yyyy'},centre=('B','C','D','E','H'))
widths(ws,{'A':40,'B':8,'C':12,'D':14,'E':13,'F':44,'G':52,'H':16})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:H{ws.max_row}'; ws.sheet_view.showGridLines=False

wb.move_sheet('All Backlinks',offset=0); wb.move_sheet('Disavow List',offset=0)

# =========================================================================
# Final typography pass. Sizes and row heights taken verbatim from
# Just Drive Media: Summary title 16, Summary status header 10,
# 'Key findings' 10, section headings 11, everything else 9. Geist only.
# Row heights: Summary 22.5 | data headers 31.5 | Domain Audit rows 15.75
# | all other data rows 22.5.
# (JDM's own Disavow List header is Arial 10 - a slip in their file, not
#  replicated: Geist 9 is used there, matching their other three tabs.)
# =========================================================================
DATA_ROW_H={'Domain Audit':15.75}
for name in wb.sheetnames:
    ws=wb[name]
    is_summary = (name=='Summary')
    for row in ws.iter_rows():
        for c in row:
            fo=c.font
            if fo.name!=F or fo.sz not in (9,10,11,16):
                sz=fo.sz if fo.sz in (9,10,11,16) else 9
                try: col=fo.color.rgb if (fo.color and isinstance(fo.color.rgb,str)) else None
                except Exception: col=None
                c.font=Font(name=F,sz=sz,b=fo.b,i=fo.i,color=col)
            elif fo.name!=F:
                c.font=Font(name=F,sz=9,b=fo.b,color=None)
    if is_summary:
        for r in range(1,ws.max_row+1): ws.row_dimensions[r].height=22.5
    else:
        ws.row_dimensions[1].height=31.5
        h=DATA_ROW_H.get(name,22.5)
        for r in range(2,ws.max_row+1): ws.row_dimensions[r].height=h
    ws.sheet_format.defaultRowHeight=15.0

# verify no stray font/size survived
import collections as _c
bad=_c.Counter()
for name in wb.sheetnames:
    for row in wb[name].iter_rows():
        for c in row:
            if c.value is None: continue
            if c.font.name!=F or c.font.sz not in (9,10,11,16): bad[(name,c.font.name,c.font.sz)]+=1
print("non-conforming cells:",dict(bad) if bad else "none")

wb.save(OUT)

# ---------------- disavow.txt ----------------
with open('/home/user/test/disavow.txt','w') as f:
    f.write(f"# New Image Canopy (newimagecanopy.com) - disavow file\n")
    f.write(f"# Generated {datetime.date.today():%d %b %Y} from the Semrush live index.\n")
    f.write(f"# {len(dis):,} domains. Source: New_Image_Canopy_Backlinks_Audit.xlsx, 'Disavow List' tab.\n#\n")
    f.write(f"# EXCLUDED: {EM_DOMS} referring domains carrying exact-match commercial anchors are HELD OUT\n")
    f.write(f"# of this file pending confirmation from the previous SEO vendor. See the 'Exact-Match Anchors' tab;\n")
    f.write(f"# ready-made lines for the {len(EM_HOLD)} disavow candidates are on the 'Pending Disavow Lines' tab.\n")
    f.write(f"# Do NOT submit to Google Search Console until that confirmation is complete.\n#\n")
    bygrp={}
    for r in dis: bygrp.setdefault(r['group'],[]).append(r['disavow_line'])
    for g in sorted(bygrp,key=lambda k:-len(bygrp[k])):
        f.write(f"\n# --- {g} ({len(bygrp[g]):,} domains) ---\n")
        for ln in sorted(bygrp[g]): f.write(ln+'\n')

print("workbook:",OUT)
print("tabs:",wb.sheetnames)
print("disavow domains:",len(dis))
print("exact-match domains:",EM_DOMS,"| pairs:",EM_PAIRS,"| pending-disavow:",len(EM_HOLD),"| keep:",len(EM_KEEP))
