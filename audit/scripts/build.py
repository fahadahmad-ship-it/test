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
    emrows.append(dict(d=r['rd'],a=a,mk=MKT[m.group(1).lower()] if m else 'Non-geo',
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
    emrows.append(dict(d=d,a=a,mk='Non-geo',site=rec.get('sitetype','Low quality web directory'),
        tool=r['tool'],link='Nofollow' if r['nofollow']=='true' else 'Dofollow',src=r['source_url'],
        title=r['source_title'],tgt=r['target_url'],tkind=tgt_kind(r['target_url']),fs=r['first_seen'],
        reco='Disavow after confirmation',st=rec['status'],asc=rec.get('ascore',''),dr=rec.get('dr','')))
    _seen_em.add(d)
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
ws.append(['Before you upload: confirm with the previous SEO partner which of the '
           f'{len(EM_HOLD)} held domains they commissioned. Nothing on the Exact Match Anchors tab is in disavow.txt.'])
banner(ws,'A2:E2')
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
money=sum(1 for x in emrows if x['tkind'] in ('Service page','Geo landing page'))
block('Key findings',sz=10,lines=[
 f"{len(AUD):,} referring domains were assessed across both tools. {both:,} were found by Semrush and Ahrefs, {sem:,} by Semrush only and {ahr:,} by Ahrefs only. Semrush is the priority source for metrics and Ahrefs contributes additional sites and Domain Rating.",
 f"{spam:,} of the {len(AUD):,} referring domains are spam. {cnt['Spam (Disavow)']:,} have at least one dofollow link and go in the disavow file; {cnt['Spam (Nofollow, No Action)']:,} are nofollow only and need no action.",
 f"{EM_DOMS} referring domains carry {EM_LINKS:,} exact match commercial placements across {EM_ANCH} distinct anchors. {len(EM_HOLD)} are held out of the disavow file pending partner confirmation, {len(EM_NOFO)} are nofollow so need no decision, and {len(EM_KEEP)} are genuine editorial placements to keep.",
 f"The target URLs are the strongest evidence that the held set was commissioned. {money:,} of the {EM_LINKS:,} exact match links ({money/EM_LINKS*100:.1f}%) point at deep money pages such as /service/canopies/, /service/canopy-lighting/, /service/canopy-repairs/, /service/light-commercial/, /service/imaging/ and the five geo landing pages. {pbn_home:,} of the {pbnl:,} link scheme links ({pbn_home/pbnl*100:.0f}%) point at the homepage and nothing else. An automated attack does not build links to a lighting service page, so this level of page targeting is campaign behaviour.",
 "Ahrefs also revealed a paid press release campaign that Semrush did not index. EIN Presswire (Semrush AS 49) was syndicated to Nat Law Review (AS 60), WBOC (AS 51), XPR Media and a large lifestyle subdomain network, carrying the anchors 'New Image Canopy' and 'gas station canopy repair services'. Almost all of them are nofollow so they pass no ranking value, but they are clearly commissioned and must not be disavowed by mistake.",
 f"The largest single anchor, used on {tn:,} referring domains, is '{ta}'. The spam copy reuses the client's own brand names, New Image Canopy and the client owned redirect shadyvent.com, inside link selling sentences. That is the signature of an automated negative SEO template rather than anything the client bought.",
 "shadyvent.com is confirmed client owned because it shares server IP 67.225.152.101 with newimagecanopy.com.",
 f"{low:,} of the {semrows:,} domains Semrush scored sit at Authority Score 0 to 2 ({low/semrows*100:.1f}%). {tld:,} referring domains are on throwaway TLDs (.shop, .online, .website, .space, .store, .site).",
 f"All {len(TAB03)} referring domains named in the client's Tab 03 extract were found in the live index and independently classified as Spam (Disavow). They are flagged 'Yes' in the Tab 03 column of the Domain Audit tab.",
])
block('Complete breakdown, every domain and every link',[])
ws.append(['Status','Domains','Share of domains','Links','Share of links']); hdr(ws,ws.max_row)
_ldof=collections.Counter(); _lall=collections.Counter()
for _r in LNK:
    _s=STAT.get(_r['rd'],'')
    _lall[_s]+=1
    if _r['nofollow']=='false': _ldof[_s]+=1
for s in ORDER:
    if not cnt[s]: continue
    ws.append([s,cnt[s],cnt[s]/len(AUD),_lall[s],_lall[s]/len(LNK)])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'B':'#,##0','C':'0.0%','D':'#,##0','E':'0.0%'},centre=('B','C','D','E'))
ws.append(['Total',len(AUD),1.0,len(LNK),1.0])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'0.0%','D':'#,##0','E':'0.0%'},centre=('B','C','D','E'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)
ws.append([])
ws.append(['Grouped','Domains','Share of domains','Links','Share of links']); hdr(ws,ws.max_row)
_G=[('Spam, in the disavow file',['Spam (Disavow)']),
    ('Spam, nofollow so no action needed',['Spam (Nofollow, No Action)']),
    ('Held for the partner to decide',['Held (Pending Partner)','Held (Review)']),
    ('Held but nofollow, no decision needed',['Held (Nofollow, No Action)']),
    ('Review, not enough evidence either way',['Review (No Link Sample)','Review (Parent Unresolved)','Review (Host Artefact)','Review (Low Authority)']),
    ('Keep, genuine links',['Keep','Own Site'])]
for nm,sts in _G:
    _d=sum(cnt[s] for s in sts); _l=sum(_lall[s] for s in sts)
    if not _d: continue
    ws.append([nm,_d,_d/len(AUD),_l,_l/len(LNK)])
    style(ws,ws.max_row,FILL.get(sts[0],WHITE),{'B':'#,##0','C':'0.0%','D':'#,##0','E':'0.0%'},centre=('B','C','D','E'))
_spamd=cnt['Spam (Disavow)']+cnt['Spam (Nofollow, No Action)']
_keepd=cnt['Keep']+cnt['Own Site']
_spaml=_lall['Spam (Disavow)']+_lall['Spam (Nofollow, No Action)']
_keepl=_lall['Keep']+_lall['Own Site']
block('The ratio',[
 f"Spam outnumbers genuine links by {_spamd/_keepd:.0f} to 1 on domains and {_spaml/_keepl:.0f} to 1 on links. {_spamd:,} of the {len(AUD):,} referring domains are spam and only {_keepd} are genuine.",
 f"{len(dis):,} domains go in the disavow file, which is {len(dis)/len(AUD)*100:.0f} per cent of the profile. The other {len(AUD)-len(dis):,} stay out of it: {cnt['Spam (Nofollow, No Action)']:,} are spam but nofollow so they pass no ranking value, {sum(cnt[s] for s in ('Held (Pending Partner)','Held (Nofollow, No Action)')):,} are held for the partner, {sum(cnt[s] for s in ORDER if s.startswith('Review')):,} lack the evidence to decide, and {_keepd} are genuine.",
 f"Of the {len(dis):,} in the file, {sum(1 for r in AUD if r['status']=='Spam (Disavow)' and r['redundant']!='Yes' and r['group'].startswith('Automated PBN')):,} are the single automated anchor network. That one network is {sum(1 for r in AUD if r['status']=='Spam (Disavow)' and r['redundant']!='Yes' and r['group'].startswith('Automated PBN'))/len(dis)*100:.0f} per cent of everything being disavowed.",
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
    style(ws,rr,FILL['Keep'] if 'client' in d else WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
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
    style(ws,rr,WHITE,{'B':'#,##0','C':'#,##0','D':'#,##0'},centre=('B','C','D'))
    ws.cell(rr,5).alignment=Alignment(vertical='center',wrap_text=True)
ws.append([]); ws.append(['Target page','Exact match links','','',''])
hdr(ws,ws.max_row)
for u,n in collections.Counter(x['tgt'] for x in emrows).most_common(12):
    ws.append([u,n,'','','']); style(ws,ws.max_row,WHITE,{'B':'#,##0'},centre=('B',))
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
ws.append(['Total domain: entries in disavow.txt',tot_in,tot_no,'',''])
style(ws,ws.max_row,WHITE,{'B':'#,##0','C':'#,##0'},centre=('B','C'))
for c in ws[ws.max_row]: c.font=Font(name=F,sz=9,b=True)
block('What the held domains are actually worth',[
 f"Held does not mean valuable. {_onip} of the {len(EM_HOLD)} domains held for partner confirmation sit on the same shared hosting ranges that this audit uses to disavow other link network hosts, and {_lowas} of them sit at Semrush Authority Score 2 or below.",
 f"Semrush organic traffic was queried for every one of the {_nheld} held domains. {_notraf} of them ({_notraf/_nq*100:.0f} per cent) have no organic traffic at all. {_noidx} are not indexed by Semrush on a single keyword, and a further {_idxnotraf} are indexed but still draw no traffic. The busiest site in the whole held set gets {_maxtraf:,.0f} visits a month.",
 f"Put together, all {_nheld} of these placements sit on sites drawing {_sumtraf:,.0f} visits a month between them, which is about one visit per site. Whoever was paid for this campaign bought links on sites that nobody reads.",
 f"Ahrefs reports most of these sites as having no keywords at all. Semrush disagrees and indexes {_nq-_noidx} of them, the largest on {max(int(_f(t['organic_keywords'])) for t in _q):,} keywords, so the Ahrefs spam flag and its traffic figures are not used anywhere in this audit. Semrush is the source for every metric shown.",
 "They are held for one reason only. They carry exact match commercial anchors pointing at specific service and geo pages, concentrated in identifiable bursts rather than spread evenly, which is what a paid campaign looks like. If the client paid for them, the client decides. If the partner does not claim them, they belong in the disavow file, because on quality alone almost none of them would survive.",
 "The Exact Match Anchors tab is sorted so the domains needing a decision come first, and every held row carries its Semrush keyword count and monthly traffic as sortable numbers.",
])
block('What to do next, in order',[
 "1. Send this workbook to the previous SEO partner and give them a deadline. The Exact Match Anchors tab is the only tab they need.",
 "2. They fill in four columns per domain: Partner confirmed (Y or N), Commissioned by, Your order or batch date, and Final decision. The Batch column groups the domains by the month they first appeared, so most of the answer is one decision per batch rather than one per domain.",
 "3. Treat no response by the deadline as not claimed.",
 "4. Filter the Exact Match Anchors tab on Final decision equals Disavow. Take those domains and copy their matching lines from column B of the Pending Disavow Lines tab.",
 "5. Download the current disavow file from the Google Search Console disavow tool first, because uploading replaces it rather than adding to it. Merge the old file with disavow.txt and the lines from step 4.",
 "6. Update the domain count in the comment header of disavow.txt so it matches, then upload the merged file to the correct Search Console property. http, https, www and non www are separate properties.",
 "7. Commission the shadyvent.com audit. It has 1,280 referring domains from the same network and redirects into the client, so those links pass through.",
])
block('Colour key',[
 "Pink rows are spam that is in the disavow file. Darker pink is spam where every link is nofollow, so no action is needed. Yellow marks the exact match anchor, which is the reason a domain is held. The pale orange block is held but nofollow. Grey is a Review status. Green is a genuine link to keep. The blue columns on the Exact Match Anchors tab are for the partner to fill in.",
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
ws=wb.create_sheet('Domain Audit')
ws.append(['Domain','Status','Group','Site Type (indicative)','Source','Found by','AS (Semrush)','RDs (Semrush)','DR (Ahrefs)','Links',
  'Dofollow Links','Nofollow Links','First Seen','In Disavow','Named in Tab 03','Links Point To','Top Anchor Text',
  'Anchor Types','Example Linking Page','Linking Page Title','IP','Country','Disavow Line']); hdr(ws)
byd=collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
for r in AUD:
    rs=byd.get(r['domain'],[])
    ws.append([r['domain'],r['status'],r['group'],r['sitetype'],r['source'],r['tool'],
      int(r['ascore']) if r['ascore'] else 'Not scored', int(r['semrush_rd']) if r.get('semrush_rd') else '',
      float(r['dr']) if r['dr'] else '',
      int(r['backlinks'] or 0),int(r['dofollow'] or 0) if r['dofollow'] else '',int(r['nofollow'] or 0) if r['nofollow'] else '',dt(r['first_seen']),
      'Yes' if (r['status']=='Spam (Disavow)' and r['redundant']!='Yes') else
      ('Covered by parent' if r['redundant']=='Yes' else ('Held' if r['status'].startswith('Held') else 'No')),
      r['tab03'],points_to(rs) if rs else '',r['top_anchor'],r['atypes'],r['example_page'],r['page_title'],
      r['ip'],r['country'],r['disavow_line'] if r['redundant']!='Yes' else ''])
    style(ws,ws.max_row,FILL.get(r['status'],WHITE),
      {'G':'#,##0','H':'#,##0','I':'0.0','J':'#,##0','K':'#,##0','L':'#,##0','M':'d mmm yyyy'},
      centre=('E','F','G','H','I','J','K','L','M','N','O','V'),valign='top')
widths(ws,{'A':34,'B':26,'C':46,'D':24,'E':10,'F':10,'G':12,'H':13,'I':11,'J':10,'K':12,'L':12,'M':13,'N':14,
           'O':14,'P':34,'Q':46,'R':40,'S':52,'T':46,'U':16,'V':9,'W':30})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:W{ws.max_row}'; ws.sheet_view.showGridLines=False

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
    ws.append([a if a!='<EmptyAnchor>' else '(no anchor text)',g['type'],g['bl'],g['bl']/len(LNK),len(g['rd']),len(g['spam']),len(g['t3']) or '',
               ' | '.join(tg)[:460],tgt_kind(tg[0]) if len(tg)==1 else 'Mixed',g['src']])
    style(ws,ws.max_row,WHITE,
      {'C':'#,##0','D':'0.00%','E':'#,##0','F':'#,##0'},centre=('C','D','E','F','G','I'))
widths(ws,{'A':104.57,'B':37.71,'C':14,'D':18,'E':20,'F':22,'G':16,'H':70,'I':20,'J':58})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ 04 Exact Match Anchors (the decision tab, one row per domain) ============
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
    t=SEMT.get(d); rec=AUDD[d]
    if not t: return 'Semrush traffic not queried for this domain'
    kw=fnum(t['organic_keywords']); tr=fnum(t['organic_traffic'])
    if kw==0 and tr==0: return 'Not indexed by Semrush, no keywords and no traffic'
    return (f"{kw:,.0f} keywords" if kw else "no keywords")+', '+ \
           (f"{tr:,.0f} visits a month" if tr else "no measurable traffic")
def has_life(d):
    """Semrush is the priority source. Ahrefs is not used to make this call."""
    t=SEMT.get(d)
    if not t: return None                      # not queried, so do not assert
    return fnum(t['organic_traffic'])>0 or fnum(t['organic_keywords'])>=100

ws=wb.create_sheet('Exact Match Anchors')
ws.append(['Held does not mean valuable. These sites carry exact match commercial anchors, which is why they are '
           'held out of the disavow file, but almost none of them has measurable traffic. Mark column Q for each '
           'domain. Anything you do not claim belongs in the disavow file.'])
banner(ws,'A1:T1')
ws.append(['Referring domain','Status','Placements','First seen','Last seen','Batch (first seen month)',
  'AS (Semrush)','Semrush keywords','Semrush traffic a month','What Semrush says the site is worth',
  'Markets','Site type (indicative)','Anchors used','Target pages hit','Indexed by (audit tool)','Recommendation',
  'Partner confirmed? (Y/N)','Commissioned by','Your order or batch date','Final decision']); hdr(ws,2)
dec=[]
for d in sorted(bd):
    rs=bd[d]; rec=AUDD[d]; st_=rec['status']
    places=len({(canon(x['src']),x['a']) for x in rs})
    mk=sorted({x['mk'] for x in rs if x['mk']!='Non-geo'})
    if st_=='Keep': reco='Keep, genuine editorial placement, no confirmation needed'
    elif st_.startswith('Review'): reco='Review, see Domain Audit tab'
    elif st_=='Held (Nofollow, No Action)': reco='No action needed, nofollow passes no ranking value'
    else:
        hl=has_life(d)
        if hl is True: reco='Hold for partner, Semrush shows this site is indexed and ranking'
        elif hl is False: reco='Disavow unless the partner confirms, Semrush shows almost nothing indexed'
        else: reco='Disavow unless the partner confirms they bought it'
    dec.append((reco,-places,d,rs,rec,places,mk,st_))
ORDER_R={'Hold for partner, Semrush shows this site is indexed and ranking':0,
         'Disavow unless the partner confirms they bought it':1,
         'Disavow unless the partner confirms, Semrush shows almost nothing indexed':2,
         'Review, see Domain Audit tab':3,
         'No action needed, nofollow passes no ranking value':4,
         'Keep, genuine editorial placement, no confirmation needed':5}
dec.sort(key=lambda t:(ORDER_R.get(t[0],9),t[1],t[2]))
for reco,_,d,rs,rec,places,mk,st_ in dec:
    fs=[int(x['fs']) for x in rs if x['fs']]
    t=SEMT.get(d)
    ws.append([d,st_,places,dt(min(fs)) if fs else '',dt(max(fs)) if fs else '',
      datetime.datetime.fromtimestamp(min(fs),datetime.UTC).strftime('%b %Y') if fs else 'Unknown',
      int(rec['ascore']) if rec['ascore'] else 'Not scored',
      int(fnum(t['organic_keywords'])) if t else 'Not queried',
      int(fnum(t['organic_traffic'])) if t else 'Not queried',
      quality(d),', '.join(mk) if mk else 'No market',rec['sitetype'],
      ' | '.join(sorted({x['a'] for x in rs}))[:460],
      ' | '.join(sorted({x['tgt'] for x in rs}))[:460],
      'Both' if len({x['tool'] for x in rs})>1 else list({x['tool'] for x in rs})[0],
      reco,'','','',''])
    r=ws.max_row
    base=GREEN if st_=='Keep' else WHITE
    style(ws,r,base,{'C':'#,##0','D':'d mmm yyyy','E':'d mmm yyyy','G':'#,##0','H':'#,##0','I':'#,##0'},
          centre=('C','D','E','F','G','H','I','K','O'))
    for col in ('Q','R','S','T'):
        _c=ws[f'{col}{r}']; _c.fill=PatternFill('solid',fgColor=INPUT)
        _c.font=Font(name=F,sz=9,color=WHITE)      # so what the partner types is readable
_lastheld=max((i for i,t in enumerate(dec,start=3) if t[7].startswith('Held') and t[7]!='Held (Nofollow, No Action)'),default=1)
dv=DataValidation(type='list',formula1='"Y,N"',allow_blank=True,showErrorMessage=True,
    errorTitle='Enter Y or N',error='Type Y if your agency commissioned this placement, or N if not.')
ws.add_data_validation(dv); dv.add(f'Q3:Q{_lastheld}')
dv2=DataValidation(type='list',formula1='"Keep,Disavow"',allow_blank=True,showErrorMessage=True,
    errorTitle='Choose Keep or Disavow',error='Only the domains awaiting confirmation can be set. Rows below this block are already decided.')
ws.add_data_validation(dv2); dv2.add(f'T3:T{_lastheld}')
widths(ws,{'A':32,'B':28,'C':12,'D':13,'E':13,'F':20,'G':13,'H':16,'I':20,'J':46,'K':22,'L':26,
           'M':70,'N':70,'O':20,'P':52,'Q':22,'R':24,'S':24,'T':20})
ws.freeze_panes='B3'; ws.auto_filter.ref=f'A2:T{ws.max_row}'; ws.sheet_view.showGridLines=False
EM_DECISION_ROWS=ws.max_row-2

# ============ 05 Exact Match Links (supporting evidence, one row per link) ============
ws=wb.create_sheet('Exact Match Links')
ws.append(['Referring domain','Exact match commercial anchor','Market','Link Type','Found by',
           'Linking Page URL','Linking Page Title','Target URL','Target Page Type','First Seen']); hdr(ws)
_emseen={}
for x in sorted(emrows,key=lambda y:(y['d'],y['a'])):
    k=(x['d'],canon(x['src']),x['a'])
    if k in _emseen:
        _emseen[k]['tool']='Both'; continue
    _emseen[k]=x
for x in _emseen.values():
    ws.append([x['d'],x['a'],x['mk'] if x['mk']!='Non-geo' else 'No market',x['link'],x['tool'],
               x['src'],x['title'],x['tgt'],x['tkind'],dt(x['fs'])])
    style(ws,ws.max_row,WHITE,{'J':'d mmm yyyy'},centre=('C','D','E','I','J'))
widths(ws,{'A':30,'B':64,'C':18,'D':11,'E':11,'F':62,'G':50,'H':62,'I':18,'J':13})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'; ws.sheet_view.showGridLines=False

# ============ Pending Disavow Lines ============
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Do not paste this whole column into disavow.txt. These lines are not approved for upload. '
           'Append only the domains the partner does not claim, after column T of the Exact Match Anchors tab is filled in.'])
banner(ws,'A1:J1')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)','Recommendation',
           'AS (Semrush)','DR (Ahrefs)','What Semrush says the site is worth','Site type','Placements',
           'Exact match anchors','Target pages hit']); hdr(ws,2)
for d in EM_HOLD:
    rs=bd[d]; rec=AUDD[d]
    places=len({(canon(x['src']),x['a']) for x in rs})
    ws.append([d,'domain:'+d,'Append only if the partner does not claim it',
      int(rec['ascore']) if rec['ascore'] else 'Not scored',
      round(fnum(rec['dr']),1) if rec['dr'] else 'Not scored',quality(d),rec['sitetype'],places,
      ' | '.join(sorted({x['a'] for x in rs}))[:460],' | '.join(sorted({x['tgt'] for x in rs}))[:460]])
    style(ws,ws.max_row,WHITE,{'D':'#,##0','E':'0.0','H':'#,##0'},centre=('D','E','H'))
widths(ws,{'A':32,'B':52,'C':42,'D':13,'E':12,'F':52,'G':26,'H':12,'I':68,'J':68})
ws.freeze_panes='B3'; ws.auto_filter.ref=f'A2:J{ws.max_row}'; ws.sheet_view.showGridLines=False

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
ws.append(['Disavow Line','Source','AS (Semrush)','RDs (Semrush)','DR (Ahrefs)','Links','Dofollow Links',
           'First Seen','Group','Top Anchor Text','Named in Tab 03']); hdr(ws)
for r in sorted(dis,key=lambda x:x['domain']):
    ws.append([r['disavow_line'],r['source'],int(r['ascore']) if r['ascore'] else '',
      int(r['semrush_rd']) if r.get('semrush_rd') else '',float(r['dr']) if r['dr'] else '',
      int(r['backlinks'] or 0),int(r['dofollow'] or 0) if r['dofollow'] else '',dt(r['first_seen']),
      r['group'],r['top_anchor'],r['tab03']])
    style(ws,ws.max_row,FILL['Spam (Disavow)'],
      {'C':'#,##0','D':'#,##0','E':'0.0','F':'#,##0','G':'#,##0','H':'d mmm yyyy'},
      centre=('B','C','D','E','F','G','H','K'))
widths(ws,{'A':40,'B':10,'C':12,'D':13,'E':12,'F':10,'G':14,'H':13,'I':46,'J':52,'K':16})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:K{ws.max_row}'; ws.sheet_view.showGridLines=False

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
# ---------------------------------------------------------------------------
# Column widths taken from Just Drive Media, matched by what the column holds.
# Where that sheet leaves a column at the default width, this one leaves it too.
# Columns this audit adds, which that sheet has no counterpart for, keep the
# widths set when their tab was built.
JDM_W={
 'Domain Audit':{'Domain':36.0,'Status':20.0,'AS (Semrush)':9.57,'Links':13.0,
   'RDs (Semrush)':9.43,'In Disavow':12.43,'Links Point To':21.29,'Dofollow Links':14.0,
   'Nofollow Links':None,'First Seen':12.0,'Top Anchor Text':45.0,'Example Linking Page':None,
   'Linking Page Title':40.0,'Source':14.0,'IP':15.0,'Disavow Line':14.0},
 'Anchor Analysis':{'Anchor Text':104.57,'Anchor Type':37.71,'Links':14.0,
   'Share of Links':None,'Referring Domains':None,'Spam Domains Using It':20.29},
 'All Backlinks':{'Referring Domain':25.43,'Status':27.14,'Tool':14.71,'Anchor Text':55.0,
   'Anchor Type':32.0,'Link Type':10.0,'Linking Page URL':55.0,'Linking Page Title':53.14,
   'Target URL':38.0,'First Seen':14.0},
 'Disavow List':{'Disavow Line':44.0,'AS (Semrush)':14.0,'Links':15.57,
   'RDs (Semrush)':14.0,'Top Anchor Text':71.57},
}
for _t,_m in JDM_W.items():
    _ws=wb[_t]
    _heads={c.value:c.column_letter for c in _ws[1]}
    for _name,_w in _m.items():
        _col=_heads.get(_name)
        if not _col: continue
        if _w is None: _ws.column_dimensions.pop(_col,None)
        else: _ws.column_dimensions[_col].width=_w

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
