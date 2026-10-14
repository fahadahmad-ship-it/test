import csv,collections,datetime,re
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
D='/home/user/test/audit/data/'
OUT='/home/user/test/New_Image_Canopy_Backlinks_Audit.xlsx'
NAVY='FF1F3864'; F='Geist'; WHITE='FFFFFFFF'; BLUE='FFD9E2F3'; GREEN='FFE2EFDA'
FILL={'Spam (Disavow)':'FFEAD1DC','Spam (Nofollow, No Action)':'FFD5A6BD','Keep':'FFC27BA0',
      'Own Site':'FFA64D79','Held (Pending Partner)':'FFFFF2CC','Held (Nofollow, No Action)':'FFFCE4D6',
      'Held (Review)':'FFFFE599','Review (No Link Sample)':'FFF2F2F2','Review (Low Authority)':'FFF2F2F2'}
thin=Side(style='thin'); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)
def hdr(ws,row=1,sz=9):
    for c in ws[row]:
        if c.value is None: continue
        c.font=Font(name=F,sz=sz,b=True,color=WHITE); c.fill=PatternFill('solid',fgColor=NAVY)
        c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); c.border=BORD
    ws.row_dimensions[row].height=31.5
def style(ws,r,fill,numfmts=None,centre=(),valign='center'):
    for c in ws[r]:
        c.font=Font(name=F,sz=9,color='FF000000'); c.fill=PatternFill('solid',fgColor=fill); c.border=BORD
        c.alignment=Alignment(vertical=valign,horizontal='center' if c.column_letter in centre else None)
        if numfmts and c.column_letter in numfmts: c.number_format=numfmts[c.column_letter]
def widths(ws,m):
    for k,v in m.items(): ws.column_dimensions[k].width=v
def dt(ts):
    try: return datetime.datetime.fromtimestamp(int(ts),datetime.UTC).date()
    except: return ''

AUD=list(csv.DictReader(open(D+'domain_audit.csv'),delimiter=';'))
LNK=list(csv.DictReader(open(D+'links_all.csv'),delimiter=';'))
STAT={r['domain']:r['status'] for r in AUD}
AUDD={r['domain']:r for r in AUD}
TAB03=set(l.strip() for l in open(D+'tab03_named.txt') if l.strip())
GEO=re.compile(r'(austin|dallas|houston|tulsa|oklahoma city)',re.I)
MKT={'austin':'Austin, TX','dallas':'Dallas, TX','houston':'Houston, TX','tulsa':'Tulsa, OK','oklahoma city':'Oklahoma City, OK'}
def tgt_kind(u):
    if '/location/' in u or re.search(r'/gas-?station-canopy-construction-',u): return 'Geo landing page'
    if '/service/' in u: return 'Service page'
    if u.rstrip('/') in ('https://newimagecanopy.com','http://newimagecanopy.com'): return 'Homepage'
    return 'Other page (blog)'
def points_to(rs):
    hs={('shadyvent.com' if 'shadyvent' in x['target_url'] else 'newimagecanopy.com') for x in rs}
    if hs=={'shadyvent.com'}: return 'shadyvent.com (redirect)'
    if len(hs)>1: return 'newimagecanopy.com and shadyvent.com (redirect)'
    return 'newimagecanopy.com'

emrows=[]
for r in LNK:
    a=(r['anchor'] or '').strip()
    if not a or not r['atype'].startswith('Exact match'): continue
    rec=AUDD.get(r['rd'],{}); st=rec.get('status','')
    m=GEO.search(a)
    if st=='Keep': reco='Keep, genuine editorial placement, no confirmation needed'
    elif st=='Held (Nofollow, No Action)': reco='No action needed, nofollow passes no ranking value'
    elif st=='Held (Review)': reco='Review, mixes link scheme with exact match anchors'
    else: reco='Disavow after confirmation'
    emrows.append(dict(d=r['rd'],a=a,mk=MKT[m.group(1).lower()] if m else 'Non-geo',
        site=rec.get('sitetype','Low-quality web directory'),tool=r['tool'],
        link='Nofollow' if r['nofollow']=='true' else 'Dofollow',src=r['source_url'],
        title=r['source_title'],tgt=r['target_url'],tkind=tgt_kind(r['target_url']),
        fs=r['first_seen'],reco=reco,st=st,
        asc=rec.get('ascore',''),dr=rec.get('dr','')))
emrows.sort(key=lambda x:(x['d'],x['a']))
emdoms=collections.Counter(x['d'] for x in emrows)
EM_DOMS=len(emdoms); EM_LINKS=len(emrows); EM_ANCH=len({x['a'] for x in emrows})
EM_HOLD=sorted({x['d'] for x in emrows if x['st']=='Held (Pending Partner)' or x['st']=='Held (Review)'})
EM_NOFO=sorted({x['d'] for x in emrows if x['st']=='Held (Nofollow, No Action)'})
EM_KEEP=sorted({x['d'] for x in emrows if x['st']=='Keep'})
dis=[r for r in AUD if r['status']=='Spam (Disavow)' and r['redundant']!='Yes']
redun=[r for r in AUD if r['redundant']=='Yes']
cnt=collections.Counter(r['status'] for r in AUD)
blc=collections.Counter()
for r in LNK: blc[STAT.get(r['rd'],'')]+=1

wb=openpyxl.Workbook()
# ============ 01 Summary ============
ws=wb.active; ws.title='Summary'; ws.sheet_view.showGridLines=False
widths(ws,{'A':48,'B':16.29,'C':17.57,'D':18.71,'E':94})
ws['A1']='https://newimagecanopy.com/'; ws.merge_cells('A1:B1')
ws['A1'].font=Font(name=F,sz=16,b=True,color=NAVY); ws['A1'].alignment=Alignment(vertical='center')
ws.append(['Before you upload: confirm with the previous SEO vendor which of the '
           f'{len(EM_HOLD)} held domains they commissioned. Nothing on the Exact Match Anchors tab is in disavow.txt.'])
ws.merge_cells(f'A2:E2')
ws['A2'].font=Font(name=F,sz=10,b=True,color='FF9C0006'); ws['A2'].fill=PatternFill('solid',fgColor='FFFFC7CE')
ws['A2'].alignment=Alignment(vertical='center',wrap_text=True); ws['A2'].border=BORD
ws.append([])
ws.append(['Status','Domains','Backlinks','Share of Domains','What it means'])
HDRROW=ws.max_row; hdr(ws,HDRROW,sz=10)
MEAN={'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'Held (Pending Partner)':'Exact match commercial anchor or press release placement. May have been commissioned. Not in the disavow file until the previous SEO vendor confirms.',
 'Held (Nofollow, No Action)':'Exact match commercial anchor, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
 'Held (Review)':'Carries both exact match commercial and link scheme anchors. Needs a judgement call.',
 'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Review (No Link Sample)':'Neither tool returned link level data, so dofollow cannot be confirmed. Never disavowed automatically.',
 'Review (Low Authority)':'Low authority site with no editorial signal. A judgement call, not a fact, so the client confirms.',
 'Keep':'Genuine or harmless link. Keep.','Own Site':'Client owned property or sister brand. Keep.'}
ORDER=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Held (Review)',
       'Spam (Nofollow, No Action)','Review (No Link Sample)','Review (Low Authority)','Keep','Own Site']
first=ws.max_row+1
for s in ORDER:
    if not cnt[s]: continue
    ws.append([s,cnt[s],blc[s],cnt[s]/len(AUD),MEAN[s]])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'B':'#,##0','C':'#,##0','D':'0.0%'},centre=('B','C','D'))
    ws.cell(ws.max_row,5).alignment=Alignment(vertical='center',wrap_text=True)
last=ws.max_row
ws.append(['Total',f'=SUM(B{first}:B{last})',f'=SUM(C{first}:C{last})',f'=SUM(D{first}:D{last})',''])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0','D':'0.0%'},centre=('B','C','D'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)

def block(title,lines,sz=11):
    ws.append([]); ws.append([title]); r=ws.max_row
    ws.cell(r,1).font=Font(name=F,sz=sz,b=True,color=NAVY)
    for t in lines:
        ws.append([t]); rr=ws.max_row; ws.merge_cells(f'A{rr}:E{rr}')
        ws.cell(rr,1).font=Font(name=F,sz=9); ws.cell(rr,1).alignment=Alignment(vertical='center',wrap_text=True)

sem=sum(1 for r in AUD if r['source']=='Semrush'); ahr=sum(1 for r in AUD if r['source']=='Ahrefs')
both=sum(1 for r in AUD if r['source']=='Both')
spam=cnt['Spam (Disavow)']+cnt['Spam (Nofollow, No Action)']
pbnl=sum(1 for r in LNK if r['atype']=='Spam: keyword stuffed SEO sales copy')
pbn_home=sum(1 for r in LNK if r['atype']=='Spam: keyword stuffed SEO sales copy' and tgt_kind(r['target_url'])=='Homepage')
topa=collections.Counter(); 
for r in LNK: topa[(r['anchor'] or '').strip()]+=1
topdom=collections.defaultdict(set)
for r in LNK: topdom[(r['anchor'] or '').strip()].add(r['rd'])
ta,tn=max(((a,len(s)) for a,s in topdom.items() if a),key=lambda x:x[1])
low=sum(1 for r in AUD if r['ascore']!='' and int(r['ascore'])<=2)
semrows=sum(1 for r in AUD if r['ascore']!='')
tld=sum(1 for r in AUD if re.search(r'\.(shop|online|website|space|store|site)$',r['domain'],re.I))
money=sum(1 for x in emrows if x['tkind'] in ('Service page','Geo landing page'))
block('Key findings',sz=10,lines=[
 f"{len(AUD):,} referring domains were assessed across both tools. {both:,} were found by Semrush and Ahrefs, {sem:,} by Semrush only and {ahr:,} by Ahrefs only. Semrush is the priority source for metrics and Ahrefs contributes additional sites and Domain Rating.",
 f"{spam:,} of the {len(AUD):,} referring domains are spam. {cnt['Spam (Disavow)']:,} have at least one dofollow link and go in the disavow file; {cnt['Spam (Nofollow, No Action)']:,} are nofollow only and need no action.",
 f"{EM_DOMS} referring domains carry {EM_LINKS:,} exact match commercial placements across {EM_ANCH} distinct anchors. {len(EM_HOLD)} are held out of the disavow file pending vendor confirmation, {len(EM_NOFO)} are nofollow so need no decision, and {len(EM_KEEP)} are genuine editorial placements to keep.",
 f"The target URLs are the strongest evidence that the held set was commissioned. {money:,} of the {EM_LINKS:,} exact match links ({money/EM_LINKS*100:.1f}%) point at deep money pages such as /service/canopies/, /service/canopy-lighting/, /service/canopy-repairs/, /service/light-commercial/, /service/imaging/ and the five geo landing pages. {pbn_home:,} of the {pbnl:,} link scheme links ({pbn_home/pbnl*100:.0f}%) point at the homepage and nothing else. An automated attack does not build links to a lighting service page, so this level of page targeting is campaign behaviour.",
 "Ahrefs also revealed a paid press release campaign that Semrush did not index. EIN Presswire (Semrush AS 49) was syndicated to Nat Law Review (AS 60), WBOC (AS 51), XPR Media and a large lifestyle subdomain network, carrying the anchors 'New Image Canopy' and 'gas station canopy repair services'. Almost all of them are nofollow so they pass no ranking value, but they are clearly commissioned and must not be disavowed by mistake.",
 f"The largest single anchor, used on {tn:,} referring domains, is '{ta}'. The spam copy reuses the client's own brand names (New Image Canopy and the client-owned redirect shadyvent.com / Shady Vent Construction, Inc.) inside link-selling sentences - the signature of an automated negative SEO template, not of anything the client bought.",
 "shadyvent.com is confirmed client owned because it shares server IP 67.225.152.101 with newimagecanopy.com.",
 f"{low:,} of the {semrows:,} domains Semrush scored sit at Authority Score 0 to 2 ({low/semrows*100:.1f}%). {tld:,} referring domains are on throwaway TLDs (.shop, .online, .website, .space, .store, .site).",
 f"All {len(TAB03)} referring domains named in the client's Tab 03 extract were found in the live index and independently classified as Spam (Disavow). They are flagged 'Yes' in the Tab 03 column of the Domain Audit tab.",
])
block('Authority Score vs competitor set',[])
ws.append(['Domain','Authority Score','Referring domains','Follow links','Note']); hdr(ws,ws.max_row)
for d,a,r_,f_,n in [('newimagecanopy.com (client)',9,2445,3589,'Most referring domains, lowest Authority Score'),
 ('austinmohawk.com',16,954,7959,'Named competitor with 2.2 times the follow links from a third of the domains'),
 ('tfccanopy.com',15,708,838,'Named competitor'),
 ('cscanopy.com',10,1376,1610,'Direct canopy competitor'),
 ('sheltersdirect.com',10,1519,2201,'Direct canopy competitor'),
 ('madisonind.com',10,1237,4172,'Direct canopy competitor'),
 ('shadyvent.com (client redirect)',2,1280,1312,'Client owned, hit by the same attack, needs its own audit')]:
    ws.append([d,a,r_,f_,n]); rr=ws.max_row
    style(ws,rr,'FFF2F2F2' if 'client' in d else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True)
block('Note on these figures',[
 f"The competitor table above uses Semrush's own domain level counters, 2,445 referring domains for the client, so the comparison is like for like. The status table at the top counts {len(AUD):,} domains because it merges Semrush with Ahrefs, which contributes {ahr:,} sites that Semrush never indexed.",
])
block('Target URL split, attack against campaign',[])
ws.append(['Link population','Links','Homepage','Deep pages','Reading']); hdr(ws,ws.max_row)
for nm,tot_,deep_,note in [
  ('Link scheme and PBN self advertising',pbnl,pbnl-pbn_home,'Homepage only. Automated, with no page level targeting, so an attack.'),
  ('Exact match commercial',EM_LINKS,sum(1 for x in emrows if x['tkind']!='Homepage'),'Deep service and geo landing pages, which is deliberate targeting and therefore a campaign.')]:
    ws.append([nm,tot_,tot_-deep_,deep_,note]); rr=ws.max_row
    style(ws,rr,FILL['Held (Pending Partner)'] if 'Exact' in nm else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True)
ws.append([]); ws.append(['Target page','Exact match links','','',''])
hdr(ws,ws.max_row)
for u,n in collections.Counter(x['tgt'] for x in emrows).most_common(12):
    ws.append([u,n,'','','']); style(ws,ws.max_row,WHITE,{'B':'#,##0'},centre=('B',))
block('Anchor category and what happens to each',[])
ws.append(['Anchor category','In disavow.txt','Nofollow / no action','Action','']); hdr(ws,ws.max_row)
grp=collections.Counter()
for r in AUD:
    g=re.sub(r' \(covered by.*','',r['group'])
    grp[(g,r['status'])]+=1
ACT=[('Automated PBN and service advertising anchor network','Disavow'),
     ('Link network host (shared IP, templated page)','Disavow'),
     ('SEO tool and link selling network domain','Disavow'),
     ('Flagged spam by Ahrefs, low authority','Disavow'),
     ('Off topic casino or pharma anchor','Disavow'),
     ('Low authority directory or bookmark placement','Disavow')]
tot_in=tot_no=0
for g,act in ACT:
    a=grp[(g,'Spam (Disavow)')]; b=grp[(g,'Spam (Nofollow, No Action)')]
    if not(a or b): continue
    tot_in+=a; tot_no+=b
    ws.append([g,a,b,act,'']); style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
ws.append(['Exact match commercial and press release anchors',0,len(EM_NOFO),'Confirm who commissioned before disavowing',''])
style(ws,ws.max_row,FILL['Held (Pending Partner)'],{'B':'#,##0','C':'#,##0'},centre=('B','C'))
ws.append(['Brand, URL and natural anchors',0,0,'Retain','']); style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
ws.append(['Total domain: entries in disavow.txt',tot_in,tot_no,'',''])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)
block('Important caveats',[
 "Semrush Authority Score ignores the disavow file because it is a third party metric. Submitting this file will not move Authority Score from 9 to 15. Disavow is a safety action on the Google side. The gap to austinmohawk.com at AS 16 is a link acquisition problem, because they have 7,959 follow links from genuine industry sites. Those are two separate pieces of work.",
 f"Uploading replaces any existing disavow file and does not append to it. Download the current file from the Google Search Console disavow tool first and merge the two, or the previous list is lost. {len(redun)} subdomain lines were deliberately left out because the domain: directive already covers subdomains of a disavowed parent.",
 "shadyvent.com has its own 1,280 referring domains from the same network. Because it redirects into newimagecanopy.com those links pass through to the client, so it needs a parallel audit and its own disavow file. That is out of scope here and is the largest unaudited exposure in this engagement.",
 "Do not submit the disavow file to Google Search Console until the previous SEO vendor has confirmed which held domains were commissioned.",
])
block('Method',[
 f"Prepared {datetime.date.today():%d %b %Y}. {len(AUD):,} referring domains and {len(LNK):,} links assessed, merging Semrush (priority source for metrics) with Ahrefs (additional sites and Domain Rating).",
 "Status rules. Own Site is a client property. Keep is genuine or editorially harmless. Held means the domain carries an exact match commercial or press release anchor, so it may have been commissioned. Spam (Disavow) is a link scheme, casino or pharma, SEO tool network or low authority placement with at least one dofollow link. Spam (Nofollow, No Action) is the same but every link is nofollow. Review means there is not enough evidence to decide, and those are never disavowed automatically.",
])
for r in range(1,ws.max_row+1): ws.row_dimensions[r].height=22.5

# ============ 02 Domain Audit ============
ws=wb.create_sheet('Domain Audit')
ws.append(['Domain','Status','Group','Site Type (indicative)','Source','AS (Semrush)','RDs (Semrush)','DR (Ahrefs)','Backlinks',
  'Dofollow Links','Nofollow Links','First Seen','In Disavow','Named in Tab 03','Links Point To','Top Anchor Text',
  'Anchor Types','Example Linking Page','Linking Page Title','IP','Country','Disavow Line']); hdr(ws)
byd=collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
for r in AUD:
    rs=byd.get(r['domain'],[])
    ws.append([r['domain'],r['status'],r['group'],r['sitetype'],r['source'],
      int(r['ascore']) if r['ascore'] else '', int(r['semrush_rd']) if r.get('semrush_rd') else '',
      float(r['dr']) if r['dr'] else '',
      int(r['backlinks'] or 0),r['dofollow'],r['nofollow'],dt(r['first_seen']),
      'Yes' if (r['status']=='Spam (Disavow)' and r['redundant']!='Yes') else
      ('Covered by parent' if r['redundant']=='Yes' else ('Held' if r['status'].startswith('Held') else 'No')),
      r['tab03'],points_to(rs) if rs else '',r['top_anchor'],r['atypes'],r['example_page'],r['page_title'],
      r['ip'],r['country'],r['disavow_line'] if r['redundant']!='Yes' else ''])
    style(ws,ws.max_row,FILL.get(r['status'],WHITE),
      {'F':'#,##0','G':'#,##0','H':'0.0','I':'#,##0','J':'#,##0','K':'#,##0','L':'d mmm yyyy'},
      centre=('E','F','G','H','I','J','K','L','M','N','U'),valign='top')
widths(ws,{'A':34,'B':26,'C':46,'D':24,'E':10,'F':11,'G':13,'H':11,'I':10,'J':12,'K':12,'L':13,'M':14,'N':14,
           'O':34,'P':46,'Q':40,'R':52,'S':46,'T':16,'U':9,'V':30})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:V{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 03 Anchor Analysis ============
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Anchor Type','Links','Share of Links','Referring Domains','Spam Domains Using It',
           'Named in Tab 03','Target URL(s)','Target Page Type','Example Linking Page']); hdr(ws)
agg=collections.defaultdict(lambda:{'bl':0,'rd':set(),'spam':set(),'t3':set(),'type':'','tgt':set(),'src':''})
for r in LNK:
    a=(r['anchor'] or '').strip() or '<EmptyAnchor>'
    g=agg[a]; g['bl']+=1; g['rd'].add(r['rd']); g['type']=r['atype']; g['tgt'].add(r['target_url'])
    if not g['src']: g['src']=r['source_url']
    if STAT.get(r['rd'],'').startswith('Spam'): g['spam'].add(r['rd'])
    if r['rd'] in TAB03: g['t3'].add(r['rd'])
for a,g in sorted(agg.items(),key=lambda x:-x[1]['bl']):
    tg=sorted(g['tgt'])
    ws.append([a,g['type'],g['bl'],g['bl']/len(LNK),len(g['rd']),len(g['spam']),len(g['t3']) or '',
               ' | '.join(tg)[:460],tgt_kind(tg[0]) if len(tg)==1 else 'Mixed',g['src']])
    style(ws,ws.max_row,FILL['Held (Pending Partner)'] if g['type'].startswith('Exact match') else WHITE,
      {'C':'#,##0','D':'0.00%','E':'#,##0','F':'#,##0'},centre=('C','D','E','F','G','I'))
widths(ws,{'A':104.57,'B':37.71,'C':14,'D':18,'E':20,'F':22,'G':16,'H':70,'I':20,'J':58})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 04 Exact Match Anchors ============
ws=wb.create_sheet('Exact Match Anchors')
ws.append(['Referring domain','Links from this domain','AS (Semrush)','DR (Ahrefs)','Exact match commercial anchor',
  'Market','Site type (indicative)','Tool','Link Type','Linking Page URL','Linking Page Title','Target URL',
  'Target Page Type','First Seen','Recommendation','Partner confirmed? (Y/N)','Commissioned by','Final decision']); hdr(ws)
for x in emrows:
    ws.append([x['d'],emdoms[x['d']],int(x['asc']) if x['asc'] else '',float(x['dr']) if x['dr'] else '',
      x['a'],x['mk'],x['site'],x['tool'],x['link'],x['src'],x['title'],x['tgt'],x['tkind'],dt(x['fs']),
      x['reco'],'','',''])
    r=ws.max_row
    base=GREEN if x['st']=='Keep' else (FILL['Held (Nofollow, No Action)'] if x['st']=='Held (Nofollow, No Action)' else WHITE)
    style(ws,r,base,{'B':'#,##0','C':'#,##0','D':'0.0','N':'d mmm yyyy'},centre=('B','C','D','F','H','I','M','N'))
    ws.cell(r,5).fill=PatternFill('solid',fgColor=FILL['Held (Pending Partner)'])   # highlight the ANCHOR only
    for col in ('P','Q','R'): ws[f'{col}{r}'].fill=PatternFill('solid',fgColor=BLUE)
dv=DataValidation(type='list',formula1='"Y,N"',allow_blank=True,showDropDown=False)
ws.add_data_validation(dv); dv.add(f'P2:P{ws.max_row}')
dv2=DataValidation(type='list',formula1='"Keep,Disavow,Undecided"',allow_blank=True,showDropDown=False)
ws.add_data_validation(dv2); dv2.add(f'R2:R{ws.max_row}')
widths(ws,{'A':30,'B':11,'C':11,'D':11,'E':62,'F':18,'G':26,'H':10,'I':11,'J':62,'K':50,'L':62,'M':18,'N':13,
           'O':46,'P':22,'Q':24,'R':20})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:R{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 05 Pending Disavow Lines ============
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation',
           'AS (Semrush)','DR (Ahrefs)','Site type','Links','Exact match anchors','Target pages hit']); hdr(ws)
bd=collections.defaultdict(list)
for x in emrows: bd[x['d']].append(x)
for d in EM_HOLD:
    rs=bd[d]; rec=AUDD[d]
    ws.append([d,'domain:'+d,'Disavow after confirmation',
      int(rec['ascore']) if rec['ascore'] else '',float(rec['dr']) if rec['dr'] else '',rec['sitetype'],len(rs),
      ' | '.join(sorted({x['a'] for x in rs}))[:460],' | '.join(sorted({x['tgt'] for x in rs}))[:460]])
    style(ws,ws.max_row,FILL['Held (Pending Partner)'],{'D':'#,##0','E':'0.0','G':'#,##0'},centre=('D','E','G'))
widths(ws,{'A':32,'B':52,'C':30,'D':11,'E':11,'F':26,'G':8,'H':68,'I':68})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:I{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 06 All Backlinks ============
ws=wb.create_sheet('All Backlinks')
ws.append(['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL',
           'Linking Page Title','Target URL','First Seen']); hdr(ws)
for r in LNK:
    s=STAT.get(r['rd'],'')
    ws.append([r['rd'],s,r['tool'],r['anchor'],r['atype'],'Nofollow' if r['nofollow']=='true' else 'Dofollow',
               r['source_url'],r['source_title'],r['target_url'],dt(r['first_seen'])])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'J':'d mmm yyyy'},centre=('C','F','J'))
widths(ws,{'A':25.43,'B':24,'C':11,'D':55,'E':32,'F':11,'G':55,'H':53.14,'I':38,'J':14})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 07 Disavow List ============
ws=wb.create_sheet('Disavow List')
ws.append(['Disavow Line','Source','AS (Semrush)','RDs (Semrush)','DR (Ahrefs)','Backlinks','Dofollow Links','First Seen',
           'Group','Top Anchor Text','Named in Tab 03']); hdr(ws)
for r in sorted(dis,key=lambda x:x['domain']):
    ws.append([r['disavow_line'],r['source'],int(r['ascore']) if r['ascore'] else '',
      float(r['dr']) if r['dr'] else '',int(r['backlinks'] or 0),r['dofollow'],dt(r['first_seen']),
      r['group'],r['top_anchor'],r['tab03']])
    style(ws,ws.max_row,FILL['Spam (Disavow)'],
      {'C':'#,##0','D':'0.0','E':'#,##0','F':'#,##0','G':'d mmm yyyy'},centre=('B','C','D','E','F','G','J'))
widths(ws,{'A':40,'B':10,'C':11,'D':11,'E':12,'F':14,'G':13,'H':46,'I':52,'J':16})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ---- typography pass, sizes read from Just Drive Media ----
for name in wb.sheetnames:
    w=wb[name]
    for row in w.iter_rows():
        for c in row:
            fo=c.font
            if fo.name!=F or fo.sz not in (9,10,11,16):
                sz=fo.sz if fo.sz in (9,10,11,16) else 9
                try: col=fo.color.rgb if (fo.color and isinstance(fo.color.rgb,str)) else None
                except Exception: col=None
                c.font=Font(name=F,sz=sz,b=fo.b,i=fo.i,color=col)
    if name!='Summary':
        w.row_dimensions[1].height=31.5
        h=15.75 if name=='Domain Audit' else 22.5
        for r in range(2,w.max_row+1): w.row_dimensions[r].height=h
    w.sheet_format.defaultRowHeight=15.0
bad=collections.Counter()
for name in wb.sheetnames:
    for row in wb[name].iter_rows():
        for c in row:
            if c.value is not None and (c.font.name!=F or c.font.sz not in (9,10,11,16)): bad[(name,c.font.name,c.font.sz)]+=1
print("non-conforming cells:",dict(bad) if bad else "none")
wb.save(OUT)

with open('/home/user/test/disavow.txt','w') as f:
    f.write("# New Image Canopy (newimagecanopy.com) disavow file\n")
    f.write(f"# Generated {datetime.date.today():%d %b %Y} from Semrush (priority) merged with Ahrefs.\n")
    f.write(f"# {len(dis):,} domains. Source: New_Image_Canopy_Backlinks_Audit.xlsx, 'Disavow List' tab.\n#\n")
    f.write(f"# Excluded: {EM_DOMS} referring domains carrying exact match commercial or press release\n")
    f.write(f"# anchors are held out of this file. {len(EM_HOLD)} need vendor confirmation (see the\n")
    f.write(f"# 'Exact Match Anchors' and 'Pending Disavow Lines' tabs); {len(EM_NOFO)} are nofollow and\n")
    f.write(f"# need no decision; {len(EM_KEEP)} are genuine editorial placements to keep.\n#\n")
    f.write("# Do not submit to Google Search Console until that confirmation is complete.\n")
    f.write("# Uploading replaces any existing disavow file. Download and merge the current one first.\n#\n")
    bg=collections.defaultdict(list)
    for r in dis: bg[re.sub(r' \(covered by.*','',r['group'])].append(r['disavow_line'])
    for g in sorted(bg,key=lambda k:-len(bg[k])):
        f.write(f"\n# --- {g} ({len(bg[g]):,} domains) ---\n")
        for ln in sorted(bg[g]): f.write(ln+'\n')

print("workbook:",OUT); print("tabs:",wb.sheetnames)
print(f"domains {len(AUD):,} | links {len(LNK):,} | disavow {len(dis):,} (+{len(redun)} redundant child lines omitted)")
print(f"exact-match: {EM_DOMS} domains, {EM_LINKS} links, {EM_ANCH} anchors | hold {len(EM_HOLD)} nofollow {len(EM_NOFO)} keep {len(EM_KEEP)}")
