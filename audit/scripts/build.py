import csv,collections,datetime,re
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils.cell import coordinate_to_tuple
D='/home/user/test/audit/data/'
OUT='/home/user/test/New_Image_Canopy_Backlinks_Audit.xlsx'
NAVY='FF1F3864'; F='Geist'; WHITE='FFFFFFFF'
INPUT='FF1F3864'; GREEN='FFC27BA0'          # the Keep fill, as Just Drive Media uses it
# Just Drive Media's palette only: FFEAD1DC, FFD5A6BD, FFC27BA0, FFA64D79, FF1F3864, FFFFFFFF.
# That sheet colours its four decided statuses and nothing else, so the four statuses it
# shares with this audit keep its exact fills and the six it does not have stay white,
# with the Status column carrying the meaning instead of a colour.
FILL={'Spam (Disavow)':'FFEAD1DC','Spam (Nofollow, No Action)':'FFD5A6BD','Keep':'FFC27BA0',
      'Own Site':'FFA64D79','Held (Pending Partner)':WHITE,'Held (Nofollow, No Action)':WHITE,
      'Held (Review)':WHITE,'Review (No Link Sample)':WHITE,'Review (Parent Unresolved)':WHITE,
      'Review (Host Artefact)':WHITE,'Review (Low Authority)':WHITE}
thin=Side(style='thin'); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)
def banner(ws,rng):
    """Style a merged full width note. openpyxl only styles the anchor cell, so the fill and
    border have to be written to every cell under the merge or the navy stops at column A."""
    a,b=rng.split(':')
    r1,c1=coordinate_to_tuple(a); r2,c2=coordinate_to_tuple(b)
    ws.merge_cells(rng)
    # Style after merging, never before: merge_cells resets the covered cells, so a fill
    # written first is thrown away and the navy stops at the first column. Styling the
    # covered cells afterwards does reach the file, even though openpyxl drops it again
    # when the file is read back, so check this in the sheet XML rather than with openpyxl.
    for rr in range(r1,r2+1):
        for cc in range(c1,c2+1):
            c=ws.cell(rr,cc)
            c.font=Font(name=F,sz=10,b=True,color=WHITE)
            c.fill=PatternFill('solid',fgColor=NAVY)
            c.alignment=Alignment(vertical='center',wrap_text=True)
            c.border=BORD
    ws.row_dimensions[int(re.findall(r'\d+',rng)[0])].height=31.5
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

AHR={r['domain']:r for r in csv.DictReader(open(D+'ahrefs/ah_refdomains.csv'),delimiter=';')}
SEMT={r['domain']:r for r in csv.DictReader(open(D+'semrush_traffic.csv'),delimiter=';')}
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
    if st=='Review (Host Artefact)': continue
    m=GEO.search(a)
    if st=='Keep': reco='Keep, genuine editorial placement, no confirmation needed'
    elif st=='Held (Nofollow, No Action)': reco='No action needed, nofollow passes no ranking value'
    elif st=='Held (Review)': reco='Review, mixes link scheme with exact match anchors'
    else: reco='Disavow after confirmation'
    emrows.append(dict(core=True,d=r['rd'],a=a,mk=MKT[m.group(1).lower()] if m else 'Non-geo',
        site=rec.get('sitetype','Low-quality web directory'),tool=r['tool'],
        link='Nofollow' if r['nofollow']=='true' else 'Dofollow',src=r['source_url'],
        title=r['source_title'],tgt=r['target_url'],tkind=tgt_kind(r['target_url']),
        fs=r['first_seen'],reco=reco,st=st,
        asc=rec.get('ascore',''),dr=rec.get('dr','')))
# Domains held on the strength of the linking page rather than the anchor still need a
# partner decision, so they belong on the decision tab too.
_seen_em={x['d'] for x in emrows}
for r in LNK:
    d=r['rd']; rec=AUDD.get(d,{})
    if d in _seen_em or not rec.get('status','').startswith('Held'): continue
    a=(r['anchor'] or '').strip() or '(no anchor text)'
    emrows.append(dict(core=False,d=d,a=a,mk='Non-geo',site=rec.get('sitetype','Low quality web directory'),
        tool=r['tool'],link='Nofollow' if r['nofollow']=='true' else 'Dofollow',src=r['source_url'],
        title=r['source_title'],tgt=r['target_url'],tkind=tgt_kind(r['target_url']),fs=r['first_seen'],
        reco='Disavow after confirmation',st=rec['status'],asc=rec.get('ascore',''),dr=rec.get('dr','')))
    _seen_em.add(d)
emrows.sort(key=lambda x:(x['d'],x['a']))
EM_CORE=[x for x in emrows if x.get('core')]
EM_CORE_DOMS=len({x['d'] for x in EM_CORE})
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
ws.append([f'Prepared {datetime.date.today().strftime("%-d %b %Y")} from Semrush and Ahrefs. Before you upload, confirm with the previous SEO '
           f'partner which of the {len(EM_HOLD)} held domains they commissioned. Nothing on the Exact Match Anchors tab is in disavow.txt.'])
ws.merge_cells('A2:E2')
ws['A2'].font=Font(name=F,sz=9); ws['A2'].alignment=Alignment(vertical='center',wrap_text=True)
ws.append([])
ws.append(['Status','Domains','Backlinks','Share of Domains','What it means'])
HDRROW=ws.max_row; hdr(ws,HDRROW,sz=10)
MEAN={'Review (Parent Unresolved)':'A subdomain whose parent domain could not be resolved either way. Never disavowed automatically.',
 'Review (Host Artefact)':'A nameserver or demo hostname, which is an artefact of its parent rather than a placement in its own right.',
 'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'Held (Pending Partner)':'Exact match commercial anchor or press release placement. May have been commissioned. Not in the disavow file until the previous SEO partner confirms.',
 'Held (Nofollow, No Action)':'Exact match commercial anchor, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
 'Held (Review)':'Carries both exact match commercial and link scheme anchors. Needs a judgement call.',
 'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Review (No Link Sample)':'Neither tool returned link level data, so dofollow cannot be confirmed. Never disavowed automatically.',
 'Review (Low Authority)':'Low authority site with no editorial signal. A judgement call, not a fact, so the client confirms.',
 'Keep':'Genuine or harmless link. Keep.','Own Site':'Client owned property or sister brand. Keep.'}
ORDER=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Held (Review)',
       'Spam (Nofollow, No Action)','Review (No Link Sample)','Review (Parent Unresolved)',
       'Review (Host Artefact)','Review (Low Authority)','Keep','Own Site']
first=ws.max_row+1
for s in ORDER:
    if not cnt[s]: continue
    ws.append([s,cnt[s],blc[s],cnt[s]/len(AUD),MEAN[s]])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'B':'#,##0','C':'#,##0','D':'0.0%'},centre=('B','C','D'))
    ws.cell(ws.max_row,5).alignment=Alignment(vertical='center',wrap_text=True)
last=ws.max_row
ws.append(['Total',len(AUD),sum(blc.values()),1.0,''])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0','D':'0.0%'},centre=('B','C','D'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)

def block(title,lines,sz=11):
    ws.append([]); ws.append([title]); r=ws.max_row
    ws.cell(r,1).font=Font(name=F,sz=sz,b=True,color=('FF000000' if sz==10 else NAVY))
    ws.cell(r,1).alignment=Alignment(vertical='center')
    for t in lines:
        ws.append([t]); rr=ws.max_row; ws.merge_cells(f'A{rr}:E{rr}')
        ws.cell(rr,1).font=Font(name=F,sz=9); ws.cell(rr,1).alignment=Alignment(vertical='center',wrap_text=True)

def _f(x):
    try: return float(x or 0)
    except: return 0.0
import re as _re
_SPAMIP=_re.compile(r'^(64\.182\.|69\.13\.|94\.46\.|118\.139\.|184\.168\.|185\.|188\.114\.|15\.204\.|51\.81\.)')
_hold=[AUDD[d] for d in EM_HOLD]
_allheld=[r for r in AUD if r['status'].startswith('Held')]
_q=[SEMT[r['domain']] for r in _allheld if r['domain'] in SEMT]
_nq=len(_q); _nheld=len(_allheld)
_maxtraf=max((_f(t['organic_traffic']) for t in _q),default=0)
_sumtraf=sum(_f(t['organic_traffic']) for t in _q)
_notraf=sum(1 for t in _q if _f(t['organic_traffic'])==0)
_noidx=sum(1 for t in _q if _f(t['organic_keywords'])==0)
_idxnotraf=sum(1 for t in _q if _f(t['organic_keywords'])>0 and _f(t['organic_traffic'])==0)
_onip=sum(1 for r in _hold if _SPAMIP.match(r['ip'] or ''))
_lowas=sum(1 for r in _hold if r['ascore'] and int(r['ascore'])<=2)
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
money=sum(1 for x in emrows if x['core'] and x['tkind'] in ('Service page','Geo landing page'))
block('Key findings',sz=10,lines=[
 f"{len(AUD):,} referring domains were assessed across both tools. {both:,} were found by Semrush and Ahrefs, {sem:,} by Semrush only and {ahr:,} by Ahrefs only. Semrush is the priority source for metrics and Ahrefs contributes additional sites and Domain Rating.",
 f"{spam:,} of the {len(AUD):,} referring domains are spam. {cnt['Spam (Disavow)']:,} have at least one dofollow link and go in the disavow file; {cnt['Spam (Nofollow, No Action)']:,} are nofollow only and need no action.",
 f"{EM_CORE_DOMS} referring domains carry {len(EM_CORE):,} exact match commercial placements across {EM_ANCH} distinct anchors. A further {EM_DOMS-EM_CORE_DOMS} directory domains are held on the strength of the linking page rather than the anchor, which makes {EM_DOMS} domains in total on the decision tab. {len(EM_HOLD)} are held out of the disavow file pending partner confirmation, {len(EM_NOFO)} are nofollow so need no decision, and {len(EM_KEEP)} are genuine editorial placements to keep.",
 f"The target URLs are the strongest evidence that the held set was commissioned. {money:,} of the {len(EM_CORE):,} exact match links ({money/len(EM_CORE)*100:.1f}%) point at deep money pages such as /service/canopies/, /service/canopy-lighting/, /service/canopy-repairs/, /service/light-commercial/, /service/imaging/ and the five geo landing pages. {pbn_home:,} of the {pbnl:,} link scheme links ({pbn_home/pbnl*100:.0f}%) point at the homepage and nothing else. An automated attack does not build links to a lighting service page, so this level of page targeting is campaign behaviour.",
 "Ahrefs also revealed a paid press release campaign that Semrush did not index. EIN Presswire (Semrush AS 49) was syndicated to Nat Law Review (AS 60), WBOC (AS 51), XPR Media and a large lifestyle subdomain network, carrying the anchors 'New Image Canopy' and 'gas station canopy repair services'. Almost all of them are nofollow so they pass no ranking value, but they are clearly commissioned and must not be disavowed by mistake.",
 f"The largest single anchor, used on {tn:,} referring domains, is '{ta}'. The spam copy reuses the client's own brand names, New Image Canopy and the client owned redirect shadyvent.com, inside link selling sentences. That is the signature of an automated negative SEO template rather than anything the client bought.",
 "shadyvent.com is confirmed client owned because it shares server IP 67.225.152.101 with newimagecanopy.com.",
 f"{low:,} of the {semrows:,} domains Semrush scored sit at Authority Score 0 to 2 ({low/semrows*100:.1f}%). {tld:,} referring domains are on throwaway TLDs (.shop, .online, .website, .space, .store, .site).",
 f"All {len(TAB03)} referring domains named in the client's Tab 03 extract were found in the live index and independently classified as Spam (Disavow). They are flagged 'Yes' in the Tab 03 column of the Domain Audit tab.",
])
# The status table at the top of this sheet already lists every status, so repeating it here
# would say the same thing twice. This section groups those statuses by what happens to them.
_lall=collections.Counter()
for _r in LNK: _lall[STAT.get(_r['rd'],'')]+=1
block('Anchor category and what happens to each',[])
ws.append(['Anchor category','In disavow.txt','Nofollow / no action','Action','']); hdr(ws,ws.max_row)
grp=collections.Counter()
for r in AUD:
    if r['redundant']=='Yes': continue      # folded into the parent, not a line in the file
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
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
ws.append(['Brand, URL and natural anchors',0,0,'Retain','']); style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
ws.append(['Total',tot_in,tot_no+len(EM_NOFO),'Column B is every domain: line in disavow.txt. Column C is every domain needing no action.',''])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)
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
    style(ws,rr,FILL['Keep'] if 'client' in d else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True)
block('Note on these figures',[
 f"The competitor table above uses Semrush's own domain level counters, 2,445 referring domains for the client, so the comparison is like for like. The status table at the top counts {len(AUD):,} domains because it merges Semrush with Ahrefs, which contributes {ahr:,} sites that Semrush never indexed.",
])
block('What to do next, in order',[
 "1. Send this workbook to the previous SEO partner and give them a deadline. The Exact Match Anchors tab is the only tab they need.",
 "2. They fill in the four shaded columns: Partner confirmed (column F), Commissioned by (column G), Final decision (column H) and Your order or batch date (column U). The Batch column groups the domains by the month they first appeared, so most of the answer is one decision per batch rather than one per domain.",
 "3. Treat no response by the deadline as not claimed.",
 "4. Filter the Exact Match Anchors tab on Final decision (column H) equals Disavow. Take those domains and copy their matching lines from column B of the Pending Disavow Lines tab.",
 "5. Download the current disavow file from the Google Search Console disavow tool first, because uploading replaces it rather than adding to it. Merge the old file with disavow.txt and the lines from step 4.",
 "6. Update the domain count in the comment header of disavow.txt so it matches, then upload the merged file to the correct Search Console property. http, https, www and non www are separate properties.",
 "7. Commission the shadyvent.com audit. It has 1,280 referring domains from the same network and redirects into the client, so those links pass through.",
])
block('Important caveats',[
 "Semrush Authority Score ignores the disavow file because it is a third party metric. Submitting this file will not move Authority Score from 9 to 15. Disavow is a safety action on the Google side. The gap to austinmohawk.com at AS 16 is a link acquisition problem, because they have 7,959 follow links from genuine industry sites. Those are two separate pieces of work.",
 f"Uploading replaces any existing disavow file and does not append to it. Download the current file from the Google Search Console disavow tool first and merge the two, or the previous list is lost. {len(redun)} subdomain lines were deliberately left out because the domain: directive already covers subdomains of a disavowed parent.",
 "shadyvent.com has its own 1,280 referring domains from the same network. Because it redirects into newimagecanopy.com those links pass through to the client, so it needs a parallel audit and its own disavow file. That is out of scope here and is the largest unaudited exposure in this engagement.",
 "Do not submit the disavow file to Google Search Console until the previous SEO partner has confirmed which held domains were commissioned.",
])
block('Method',[
 f"Version 1. Prepared {datetime.date.today():%d %b %Y}. {len(AUD):,} referring domains and {len(LNK):,} links assessed, merging Semrush (priority source for metrics) with Ahrefs (additional sites and Domain Rating).",
 "Status rules. Own Site is a client property. Keep is genuine or editorially harmless. Held means the domain carries an exact match commercial or press release anchor, so it may have been commissioned. Spam (Disavow) is a link scheme, casino or pharma, SEO tool network or low authority placement with at least one dofollow link. Spam (Nofollow, No Action) is the same but every link is nofollow. Review means there is not enough evidence to decide, and those are never disavowed automatically.",
])
for r in range(1,ws.max_row+1): ws.row_dimensions[r].height=22.5

# ============ 02 Domain Audit ============
# ============ 02 Domain Audit ============
# Just Drive Media's seventeen columns, in its order and under its names. The columns this
# audit adds that it has no counterpart for follow to the right of them.
ws=wb.create_sheet('Domain Audit')
ws.append(['Domain','Status','AS','Backlinks',"RD's",'Traffic','In Disavow','Links Point To',
  'Dofollow Links','Nofollow Links','First Seen','Top Anchor Text','Example Linking Page',
  'Linking Page Title','Source','IP','Disavow Line',
  'Organic Keywords','DR (Ahrefs)','Group','Site Type (indicative)','Anchor Types',
  'Named in Tab 03','Country']); hdr(ws)
byd=collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
def _tr(d,f):
    t=SEMT.get(d)
    return int(float(t[f] or 0)) if t else ''
for r in AUD:
    d=r['domain']; rs=byd.get(d,[])
    ws.append([d,r['status'],int(r['ascore']) if r['ascore'] else 'Not scored',
      int(r['backlinks'] or 0),
      int(r['semrush_rd']) if r.get('semrush_rd') else '',
      _tr(d,'organic_traffic'),
      'Yes' if (r['status']=='Spam (Disavow)' and r['redundant']!='Yes') else
      ('Covered by parent' if r['redundant']=='Yes' else ('Held' if r['status'].startswith('Held') else 'No')),
      points_to(rs) if rs else '',
      int(r['dofollow'] or 0) if r['dofollow'] else '',
      int(r['nofollow'] or 0) if r['nofollow'] else '',
      dt(r['first_seen']),r['top_anchor'],r['example_page'],r['page_title'],r['tool'],r['ip'],
      r['disavow_line'] if r['redundant']!='Yes' else '',
      _tr(d,'organic_keywords'),float(r['dr']) if r['dr'] else '',
      r['group'],r['sitetype'],r['atypes'],r['tab03'],r['country']])
    style(ws,ws.max_row,FILL.get(r['status'],WHITE),
      {'C':'#,##0','D':'#,##0','E':'#,##0','F':'#,##0','I':'#,##0','J':'#,##0','K':'d mmm yyyy',
       'R':'#,##0','S':'0.0'},
      centre=('C','D','E','F','G','I','J','K','O','R','S','W','X'),valign='top')
widths(ws,{'A':36,'B':20,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,
           'K':12,'L':45,'N':40,'O':14,'P':15,'Q':14,
           'R':15,'S':11,'T':46,'U':24,'V':40,'W':14,'X':9})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:X{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 03 Anchor Analysis ============
# Just Drive Media's six columns first, this audit's additions to the right of them.
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains',
           'Spam Domains Using It',
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
    ws.append([a if a!='<EmptyAnchor>' else '(no anchor text)',g['type'],g['bl'],g['bl']/len(LNK),
               len(g['rd']),len(g['spam']),len(g['t3']) or '',
               ' | '.join(tg)[:460],tgt_kind(tg[0]) if len(tg)==1 else 'Mixed',g['src']])
    # Just Drive Media fills the spam anchor rows and leaves everything else white.
    style(ws,ws.max_row,FILL['Spam (Disavow)'] if g['type'].startswith('Spam') else WHITE,
      {'C':'#,##0','D':'0.00%','E':'#,##0','F':'#,##0'},centre=('C','D','E','F','G','I'))
widths(ws,{'A':104.57,'B':37.71,'C':14,'F':20.29,'G':16,'H':70,'I':20,'J':58})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 04 Exact Match Anchors (the decision tab) ============
def fnum(x):
    try: return float(x or 0)
    except: return 0.0
def canon(u):
    u=(u or '').strip().lower().split('#')[0]
    return re.sub(r'^www\.','',re.sub(r'^https?://','',u)).rstrip('/')
bd=collections.defaultdict(list)
for x in emrows: bd[x['d']].append(x)

def quality(d):
    """What the linking site is worth, measured by Semrush."""
    t=SEMT.get(d)
    if not t: return 'Semrush traffic not queried for this domain'
    kw=fnum(t['organic_keywords']); tr=fnum(t['organic_traffic'])
    if kw==0 and tr==0: return 'Not indexed by Semrush, no keywords and no traffic'
    return (f"{kw:,.0f} keywords" if kw else "no keywords")+', '+ \
           (f"{tr:,.0f} visits a month" if tr else "no measurable traffic")
def has_life(d):
    """Semrush is the priority source. Ahrefs is not used to make this call."""
    t=SEMT.get(d)
    if not t: return None
    return fnum(t['organic_traffic'])>0 or fnum(t['organic_keywords'])>=100
def reco_for(d,st_):
    if st_=='Keep': return 'Keep, genuine editorial placement, no confirmation needed'
    if st_.startswith('Review'): return 'Review, see Domain Audit tab'
    if st_=='Held (Nofollow, No Action)': return 'No action needed, nofollow passes no ranking value'
    hl=has_life(d)
    if hl is True: return 'Hold for partner, Semrush shows this site is indexed and ranking'
    if hl is False: return 'Disavow unless the partner confirms, Semrush shows almost nothing indexed'
    return 'Disavow unless the partner confirms they bought it'
ORDER_R={'Hold for partner, Semrush shows this site is indexed and ranking':0,
         'Disavow unless the partner confirms they bought it':1,
         'Disavow unless the partner confirms, Semrush shows almost nothing indexed':2,
         'Review, see Domain Audit tab':3,
         'No action needed, nofollow passes no ranking value':4,
         'Keep, genuine editorial placement, no confirmation needed':5}

# Super K Express's eight columns, in its order and under its names, plus the example backlink.
# The Semrush evidence this audit adds follows to the right of them.
ws=wb.create_sheet('Exact Match Anchors')
ws.append(['Referring domain','Exact-match commercial anchor','Market','Site type (indicative)',
  'Recommendation','Partner confirmed? (Y/N)','Commissioned by','Final decision',
  'Example backlink (linking page)','Link type','Target of that backlink','Status',
  'AS (Semrush)','Semrush keywords','Semrush traffic a month','What Semrush says the site is worth',
  'Placements','First seen','Batch (first seen month)','Found by','Your order or batch date']); hdr(ws)
pairs=collections.defaultdict(list)
for x in emrows: pairs[(x['d'],x['a'])].append(x)
prow=[]
for (d,a),xs in pairs.items():
    rec=AUDD[d]; st_=rec['status']; prow.append((ORDER_R.get(reco_for(d,st_),9),d,a,xs,rec,st_))
prow.sort(key=lambda t:(t[0],t[1],t[2]))
_held_rows=[]
for _,d,a,xs,rec,st_ in prow:
    # One real, checkable backlink for this domain and anchor. Prefer a dofollow link on a
    # money page, so the example is the strongest placement rather than an arbitrary one.
    ex=sorted(xs,key=lambda x:(x['link']!='Dofollow',
              x['tkind'] not in ('Service page','Geo landing page'),x['src']))[0]
    fs=[int(x['fs']) for x in xs if x['fs']]
    t=SEMT.get(d); mk=sorted({x['mk'] for x in xs if x['mk']!='Non-geo'})
    ws.append([d,a,', '.join(mk) if mk else 'No market',rec['sitetype'],reco_for(d,st_),'','','',
      ex['src'],ex['link'],ex['tgt'],st_,
      int(rec['ascore']) if rec['ascore'] else 'Not scored',
      int(fnum(t['organic_keywords'])) if t else 'Not queried',
      int(fnum(t['organic_traffic'])) if t else 'Not queried',
      quality(d),len({(canon(x['src']),x['a']) for x in xs}),dt(min(fs)) if fs else '',
      datetime.datetime.fromtimestamp(min(fs),datetime.UTC).strftime('%b %Y') if fs else 'Unknown',
      'Both' if len({x['tool'] for x in xs})>1 else list({x['tool'] for x in xs})[0],''])
    r=ws.max_row
    style(ws,r,GREEN if st_=='Keep' else WHITE,
      {'M':'#,##0','N':'#,##0','O':'#,##0','Q':'#,##0','R':'d mmm yyyy'},
      centre=('C','J','L','M','N','O','Q','R','S','T'))
    for col in ('F','G','H','U'):
        _c=ws[f'{col}{r}']; _c.fill=PatternFill('solid',fgColor=INPUT)
        _c.font=Font(name=F,sz=9,color=WHITE)      # so what the partner types is readable
    if st_.startswith('Held') and st_!='Held (Nofollow, No Action)': _held_rows.append(r)
if _held_rows:
    dv=DataValidation(type='list',formula1='"Y,N"',allow_blank=True,showErrorMessage=True,
        errorTitle='Enter Y or N',error='Type Y if your agency commissioned this placement, or N if not.')
    ws.add_data_validation(dv); dv.add(f'F{min(_held_rows)}:F{max(_held_rows)}')
    dv2=DataValidation(type='list',formula1='"Keep,Disavow"',allow_blank=True,showErrorMessage=True,
        errorTitle='Choose Keep or Disavow',error='Only the domains awaiting confirmation can be set.')
    ws.add_data_validation(dv2); dv2.add(f'H{min(_held_rows)}:H{max(_held_rows)}')
widths(ws,{'A':24.43,'B':54,'C':16,'D':24.57,'E':30.71,'F':15.43,'G':17.57,'H':15,
           'I':62,'J':11,'K':52,'L':26,'M':13,'N':16,'O':20,'P':46,'Q':12,'R':13,'S':20,'T':11,'U':22})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:U{ws.max_row}'; ws.sheet_view.showGridLines=False
EM_DECISION_ROWS=len(_held_rows)

# ============ 05 Pending Disavow Lines ============
# Super K Express's three columns, then this audit's supporting evidence.
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation',
           'AS (Semrush)','DR (Ahrefs)','What Semrush says the site is worth','Site type','Placements',
           'Exact match anchors','Target pages hit']); hdr(ws)
for d in EM_HOLD:
    rs=bd[d]; rec=AUDD[d]
    places=len({(canon(x['src']),x['a']) for x in rs})
    ws.append([d,'domain:'+d,'Append only if the partner does not claim it',
      int(rec['ascore']) if rec['ascore'] else 'Not scored',
      round(fnum(rec['dr']),1) if rec['dr'] else 'Not scored',quality(d),rec['sitetype'],places,
      ' | '.join(sorted({x['a'] for x in rs}))[:460],' | '.join(sorted({x['tgt'] for x in rs}))[:460]])
    style(ws,ws.max_row,WHITE,{'D':'#,##0','E':'0.0','H':'#,##0'},centre=('D','E','H'))
widths(ws,{'A':32,'B':44,'C':48,'D':13,'E':12,'F':52,'G':26,'H':12,'I':68,'J':68})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 06 All Backlinks ============
ws=wb.create_sheet('All Backlinks')
ws.append(['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL',
           'Linking Page Title','Target URL','First Seen']); hdr(ws)
for r in LNK:
    s=STAT.get(r['rd'],'')
    ws.append([r['rd'],s,r['tool'],r['anchor'],r['atype'],'Nofollow' if r['nofollow']=='true' else 'Dofollow',
               r['source_url'],r['source_title'],r['target_url'],dt(r['first_seen'])])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'J':'d mmm yyyy'},centre=('C','F','J'))
widths(ws,{'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':38,'J':14})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 07 Disavow List ============
# Just Drive Media's seven columns, then this audit's additions.
ws=wb.create_sheet('Disavow List')
ws.append(['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text',
           'Source','DR (Ahrefs)','Dofollow Links','First Seen','Group','Named in Tab 03']); hdr(ws)
for r in sorted(dis,key=lambda x:x['domain']):
    d=r['domain']
    ws.append([r['disavow_line'],int(r['ascore']) if r['ascore'] else '',
      int(r['backlinks'] or 0),int(r['semrush_rd']) if r.get('semrush_rd') else '',
      _tr(d,'organic_traffic'),_tr(d,'organic_keywords'),r['top_anchor'],
      r['source'],float(r['dr']) if r['dr'] else '',
      int(r['dofollow'] or 0) if r['dofollow'] else '',dt(r['first_seen']),r['group'],r['tab03']])
    style(ws,ws.max_row,FILL['Spam (Disavow)'],
      {'B':'#,##0','C':'#,##0','D':'#,##0','E':'#,##0','F':'#,##0','I':'0.0','J':'#,##0','K':'d mmm yyyy'},
      centre=('B','C','D','E','F','H','I','J','K','M'))
widths(ws,{'A':44,'B':14,'C':15.57,'D':14,'G':71.57,'H':10,'I':12,'J':14,'K':13,'L':46,'M':16})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:M{ws.max_row}'; ws.sheet_view.showGridLines=False

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
# Column widths are set on each tab as it is built, using Just Drive Media's own values
# for the tabs it has and Super K Express's for the decision tabs.
wb.save(OUT)

with open('/home/user/test/disavow.txt','w') as f:
    f.write("# New Image Canopy (newimagecanopy.com) disavow file\n")
    f.write(f"# Generated {datetime.date.today():%d %b %Y} from Semrush (priority) merged with Ahrefs.\n")
    f.write(f"# {len(dis):,} domains. Source: New_Image_Canopy_Backlinks_Audit.xlsx, 'Disavow List' tab.\n#\n")
    f.write(f"# Excluded: {EM_DOMS} referring domains carrying exact match commercial or press release\n")
    f.write(f"# anchors are held out of this file. {len(EM_HOLD)} need partner confirmation (see the\n")
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
