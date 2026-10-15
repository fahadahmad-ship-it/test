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
# The referring domain's own referring-domain count, collected with the Authority
# Score pull. Used for the RD's column where refdomains.csv has nothing.
try:
    SRD={r['domain']:r for r in csv.DictReader(open(D+'semrush_rd.csv'),delimiter=';')}
except FileNotFoundError: SRD={}
SV={r['metric']:int(r['value']) for r in csv.DictReader(
    (l for l in open(D+'shadyvent_overview.csv') if not l.startswith('#')),delimiter=';')}
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
ws.append(['Status','Domains','Backlinks','Share of Domains','What it means'])
HDRROW=ws.max_row; hdr(ws,HDRROW,sz=10)
MEAN={'Review (Parent Unresolved)':'A subdomain whose parent domain could not be resolved either way. Never disavowed automatically.',
 'Spam (Disavow)':'Confirmed spam with at least one dofollow link. Included in the disavow file.',
 'Held (Pending Partner)':'Exact match commercial anchor or press release placement. May have been commissioned. Not in the disavow file until the previous SEO partner confirms.',
 'Held (Nofollow, No Action)':'Exact match commercial anchor, but every link is nofollow so it passes no ranking value. No disavow needed either way.',
 'Held (Review)':'Carries both exact match commercial and link scheme anchors. Needs a judgement call.',
 'Spam (Nofollow, No Action)':'Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.',
 'Review (No Link Sample)':'Neither tool returned link level data, so dofollow cannot be confirmed. Never disavowed automatically.',
 'Review (Low Authority)':'Low authority site with no editorial signal. A judgement call, not a fact, so the client confirms.',
 'Review (Conflicts With Parent)':'The parent domain is genuine but this subdomain serves a link scheme page, so the parent does not settle it. Never disavowed automatically.',
 'Keep':'Genuine or harmless link. Keep.','Own Site':'Client owned property or sister brand. Keep.'}
ORDER=['Spam (Disavow)','Held (Pending Partner)','Held (Nofollow, No Action)','Held (Review)',
       'Spam (Nofollow, No Action)','Review (No Link Sample)','Review (Parent Unresolved)',
       'Review (Conflicts With Parent)','Review (Low Authority)',
       'Keep','Own Site']
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
CLIENT_AS=9; COMP_FOLLOW=7959; COMP_RD=954
block('Key findings',sz=10,lines=[
 f"{spam:,} of the {len(AUD):,} referring domains are spam. {cnt['Spam (Disavow)']:,} have at least one dofollow link and go in the disavow file, the other {cnt['Spam (Nofollow, No Action)']:,} are nofollow only and need no action. All {len(TAB03)} domains named in Tab 03 are among them.",
 f"{EM_CORE_DOMS} referring domains carry {len(EM_CORE):,} exact match commercial placements. {len(EM_HOLD)} are held out of the disavow file until the previous SEO partner confirms what was commissioned. Do not upload before that.",
 f"{money:,} of the {len(EM_CORE):,} exact match links ({money/len(EM_CORE)*100:.0f}%) point at deep service and geo pages, while all {pbnl:,} link scheme links point at the homepage. Page level targeting is a paid campaign, not an attack.",
 f"The largest anchor, on {tn:,} referring domains, reuses the client's own brand and the client owned redirect shadyvent.com inside link selling sentences, which is a typical automated negative SEO template.",
 f"Held does not mean valuable. {_notraf} of the {_nq} held domains have no organic traffic at all and the whole set draws {_sumtraf:,.0f} visits a month between them, about one visit per site.",
 f"Authority Score is {CLIENT_AS} against a competitor set at 10 to 16. austinmohawk.com has {COMP_FOLLOW:,} follow links from {COMP_RD} domains, so the gap is link acquisition and the disavow file will not close it.",
 f"shadyvent.com is client owned, shares server IP 67.225.152.101, and carries {SV['referring_domains']:,} referring domains of its own, {SV['follow_links']:,} of them dofollow. It redirects into the client, so all of that passes through. None of it is in this audit.",
])
block('Anchor text profile (all backlinks)',[])
ws.append(['Anchor type','Backlinks','Share of Backlinks','Referring Domains','']); hdr(ws,ws.max_row)
_at=collections.Counter(); _ad=collections.defaultdict(set)
for r in LNK: _at[r['atype']]+=1; _ad[r['atype']].add(r['rd'])
for t,nbl in _at.most_common():
    ws.append([t,nbl,nbl/len(LNK),len(_ad[t]),''])
    style(ws,ws.max_row,FILL['Spam (Disavow)'] if t.startswith('Spam') else WHITE,
          {'A':'#,##0','B':'#,##0','C':'0.0%','D':'#,##0'},centre=('B','C','D'))
    # that sheet leaves the unused fifth column of this table unruled
    ws.cell(ws.max_row,5).border=Border(); ws.cell(ws.max_row,5).fill=PatternFill()

for r in range(1,ws.max_row+1): ws.row_dimensions[r].height=22.5

# ============ 02 Domain Audit ============
# ============ 02 Domain Audit ============
# Just Drive Media's seventeen columns, in its order and under its names. The columns this
# audit adds that it has no counterpart for follow to the right of them.
ws=wb.create_sheet('Domain Audit')
ws.append(['Domain','Status','AS','Backlinks',"RD's",'Traffic','In Disavow','Links Point To',
  'Dofollow Links','Nofollow Links','First Seen','Top Anchor Text','Example Linking Page',
  'Linking Page Title','Source','IP','Disavow Line']); hdr(ws)
byd=collections.defaultdict(list)
for r in LNK: byd[r['rd']].append(r)
def _tr(d,f):
    t=SEMT.get(d)
    return int(float(t[f] or 0)) if t else ''
for r in AUD:
    d=r['domain']; rs=byd.get(d,[])
    ws.append([d,r['status'],int(r['ascore']) if r['ascore'] else 'Not scored',
      int(r['backlinks'] or 0),
      int(r['semrush_rd']) if r.get('semrush_rd') else
        (int(SRD[d]['own_refdomains']) if d in SRD else ''),
      _tr(d,'organic_traffic'),
      'Yes' if (r['status']=='Spam (Disavow)' and r['redundant']!='Yes') else
      ('Covered by parent' if r['redundant']=='Yes' else ('Held' if r['status'].startswith('Held') else 'No')),
      points_to(rs) if rs else '',
      int(r['dofollow'] or 0) if r['dofollow'] else '',
      int(r['nofollow'] or 0) if r['nofollow'] else '',
      dt(r['first_seen']),r['top_anchor'],r['example_page'],r['page_title'],r['tool'],r['ip'],
      r['disavow_line'] if r['redundant']!='Yes' else ''])
    style(ws,ws.max_row,FILL.get(r['status'],WHITE),
      {'D':'#,##0','E':'#,##0','F':'#,##0','K':'d mmm yyyy'},
      centre=('C','D','E','F','G','I','J','K','O','P'),valign='top')
widths(ws,{'A':36,'B':20,'C':9.57,'D':13,'E':9.43,'F':9.71,'G':12.43,'H':21.29,'I':14,
           'K':12,'L':45,'N':40,'O':14,'P':15,'Q':14})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:Q{ws.max_row}'

# ============ 03 Anchor Analysis ============
# Just Drive Media's six columns first, this audit's additions to the right of them.
ws=wb.create_sheet('Anchor Analysis')
ws.append(['Anchor Text','Anchor Type','Backlinks','Share of Backlinks','Referring Domains',
           'Spam Domains Using It']); hdr(ws)
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
               len(g['rd']),len(g['spam'])])
    # Just Drive Media fills the spam anchor rows and leaves everything else white.
    style(ws,ws.max_row,FILL['Spam (Disavow)'] if g['type'].startswith('Spam') else WHITE,
      {'C':'#,##0','D':'0.00%'},centre=('C','D','E','F'))
ws['A1'].alignment=Alignment(horizontal='center',vertical='center',wrap_text=False)
widths(ws,{'A':104.57,'B':37.71,'C':14,'F':20.29})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:F{ws.max_row}'

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
  'Example backlink (linking page)']); hdr(ws)
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
    mk=sorted({x['mk'] for x in xs if x['mk']!='Non-geo'})
    ws.append([d,a,', '.join(mk) if mk else 'No market',rec['sitetype'],reco_for(d,st_),'','','',
      ex['src']])
    r=ws.max_row
    style(ws,r,GREEN if st_=='Keep' else WHITE,centre=('C',))
    for col in ('F','G','H'):
        _c=ws[f'{col}{r}']; _c.fill=PatternFill('solid',fgColor=INPUT)
        _c.font=Font(name=F,sz=9,color=WHITE)      # so what the partner types is readable
    if st_.startswith('Held') and st_!='Held (Nofollow, No Action)': _held_rows.append(r)
if _held_rows:
    dv=DataValidation(type='list',formula1='"Y,N"',allow_blank=True,showErrorMessage=True,
        errorTitle='Enter Y or N',error='Type Y if your agency commissioned this placement, or N if not.')
    ws.add_data_validation(dv); dv.add(f'F{min(_held_rows)}:F{max(_held_rows)}')  # noqa
    dv2=DataValidation(type='list',formula1='"Keep,Disavow"',allow_blank=True,showErrorMessage=True,
        errorTitle='Choose Keep or Disavow',error='Only the domains awaiting confirmation can be set.')
    ws.add_data_validation(dv2); dv2.add(f'H{min(_held_rows)}:H{max(_held_rows)}')
widths(ws,{'A':24.43,'B':54,'C':16,'D':24.57,'E':30.71,'F':15.43,'G':17.57,'H':15,'I':62})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:I{ws.max_row}'
EM_DECISION_ROWS=len(_held_rows)

# ============ 05 Pending Disavow Lines ============
# Super K Express's three columns, then this audit's supporting evidence.
ws=wb.create_sheet('Pending Disavow Lines')
ws.append(['Referring domain','Disavow line (append to disavow.txt once confirmed)',
           'Recommendation']); hdr(ws)
for d in EM_HOLD:
    ws.append([d,'domain:'+d,'Append only if the partner does not claim it'])
    style(ws,ws.max_row,WHITE)
widths(ws,{'A':32,'B':44,'C':48})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:C{ws.max_row}'

# ============ 06 All Backlinks ============
ws=wb.create_sheet('All Backlinks')
ws.append(['Referring Domain','Status','Tool','Anchor Text','Anchor Type','Link Type','Linking Page URL',
           'Linking Page Title','Target URL','First Seen']); hdr(ws)
for r in LNK:
    s=STAT.get(r['rd'],'')
    ws.append([r['rd'],s,r['tool'],r['anchor'],r['atype'],'Nofollow' if r['nofollow']=='true' else 'Dofollow',
               r['source_url'],r['source_title'],r['target_url'],dt(r['first_seen'])])
    style(ws,ws.max_row,FILL.get(s,WHITE),{'J':'d mmm yyyy'},centre=('F','J'))
for _r in range(1,ws.max_row+1):
    _c=ws.cell(_r,3); _c.alignment=Alignment(horizontal='left',vertical='center',
                                             wrap_text=(_r==1))
widths(ws,{'A':25.43,'B':27.14,'C':14.71,'D':55,'E':32,'F':10,'G':55,'H':53.14,'I':38,'J':14})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:J{ws.max_row}'

# ============ 07 Disavow List ============
# Just Drive Media's seven columns, then this audit's additions.
ws=wb.create_sheet('Disavow List')
ws.append(['Disavow Line','AS','Backlinks',"RD's",'Traffic','Organic Keywords','Top Anchor Text'])
hdr(ws,sz=10)   # Just Drive Media sets this one header a point larger than the rest
for r in sorted(dis,key=lambda x:x['domain']):
    d=r['domain']
    ws.append([r['disavow_line'],int(r['ascore']) if r['ascore'] else '',
      int(r['backlinks'] or 0),
      int(r['semrush_rd']) if r.get('semrush_rd') else
        (int(SRD[d]['own_refdomains']) if d in SRD else ''),
      _tr(d,'organic_traffic'),_tr(d,'organic_keywords'),r['top_anchor']])
    style(ws,ws.max_row,FILL['Spam (Disavow)'],
      {'C':'#,##0','D':'#,##0','E':'#,##0','F':'#,##0'},centre=('B','C','D','E','F'))
widths(ws,{'A':44,'B':14,'C':15.57,'D':14,'G':71.57})
ws.freeze_panes='B2'; ws.auto_filter.ref=f'A1:G{ws.max_row}'

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
        f.write(f"\n# --- {g} ({len(bg[g]):,} domain{'' if len(bg[g])==1 else 's'}) ---\n")
        for ln in sorted(bg[g]): f.write(ln+'\n')

print("workbook:",OUT); print("tabs:",wb.sheetnames)
print(f"domains {len(AUD):,} | links {len(LNK):,} | disavow {len(dis):,} (+{len(redun)} redundant child lines omitted)")
print(f"exact-match: {EM_DOMS} domains, {EM_LINKS} links, {EM_ANCH} anchors | hold {len(EM_HOLD)} nofollow {len(EM_NOFO)} keep {len(EM_KEEP)}")
