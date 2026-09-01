#!/usr/bin/env python3
"""Simple review workbook + designed dashboard, with per-domain anchors joined in."""
import csv, collections, html, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import json
rows=list(csv.DictReader(open('merged_all_domains.csv')))
anch={r['domain']:r for r in csv.DictReader(open('anchor_by_domain.csv'))}
def root2(d):  # last two labels, for subdomain fallback matching
    p=d.split('.'); return '.'.join(p[-2:]) if len(p)>=2 else d
anch_root={root2(k):v for k,v in anch.items()}
def get_anchor(d):
    return anch.get(d) or anch.get(root2(d)) or anch_root.get(root2(d)) or {}
# actual backlink-level evidence from Semrush (source URL + anchor + follow)
BL=json.load(open('semrush_backlink_by_domain.json'))
def get_bl(d):
    return BL.get(d) or BL.get(root2(d)) or {}

WHY={
 'Link-selling / SEO-service PBN':'Paid-link / backlink-seller site',
 'Blogspot PBN / spam post':'Spam blog post (Blogspot PBN)',
 'Gambling / casino spam':'Gambling / casino spam',
 'Adult spam':'Adult spam',
 'URL-shortener / redirect link network':'Redirect / URL-shortener link network',
 'Expired-domain / auto network':'Expired-domain spam network',
 'Auto-generated stats / worth-checker':'Auto-generated stats / scraper page',
 'Low-quality directory / TLD list':'Spam directory listing',
 'Free-host throwaway page':'Throwaway free-host page',
 'Multi-signal spam':'Multiple spam signals (dead + farm-IP / spam-flag)',
 'Single-signal low-quality':'Low-quality / dead domain',
 'Window-company microsite cluster (verify OWNERSHIP)':'Possibly YOUR OWN microsite — verify before disavow',
 'Low-authority (needs review)':'Low authority — manual check',
 'Unclear':'Borderline — manual check',
 'LEGITIMATE / high-authority':'Legitimate / high-authority — keep',
}
for r in rows:
    a=get_anchor(r['domain']); b=get_bl(r['domain'])
    r['anchor_type']=a.get('anchor_type','')
    # example backlink: prefer Semrush source URL, else Ahrefs url_from
    r['backlink_url']=b.get('ex_url') or a.get('url_from','')
    r['example_anchor']=b.get('ex_anchor') or a.get('anchor','')
    r['follow']=b.get('ex_follow') or a.get('dofollow','')
    r['bl_count']=b.get('bl_count','')
    r['dofollow_n']=b.get('dofollow','')
    r['nofollow_n']=b.get('nofollow','')
    r['link_checked']='yes' if (b or a) else 'no (beyond sample)'
    r['why']=WHY.get(r['category'],r['category'])
    r['authority']=max(float(r['dr'] or 0), int(r['ascore'] or 0))

DIS=[r for r in rows if r['decision']=='DISAVOW']
REV=[r for r in rows if r['decision']=='REVIEW']
KEEP=[r for r in rows if r['decision']=='KEEP']
conf=collections.Counter(r['confidence'] for r in rows)

# ================= WORKBOOK =================
wb=openpyxl.Workbook()
HEAD=Font(bold=True,color='FFFFFF',size=11); HFILL=PatternFill('solid',fgColor='1F3864')
DEC_FILL={'DISAVOW':PatternFill('solid',fgColor='F8CBAD'),
          'REVIEW':PatternFill('solid',fgColor='FFE699'),
          'KEEP':PatternFill('solid',fgColor='C6E0B4')}
def build(ws,cols,data,widths,colorby='decision'):
    ws.append(cols)
    for i,c in enumerate(cols,1):
        cell=ws.cell(1,i); cell.font=HEAD; cell.fill=HFILL
        cell.alignment=Alignment(vertical='center',wrap_text=True,horizontal='left')
    for r in data:
        ws.append([r.get(k,'') for k in cols])
        if colorby and colorby in cols:
            c=ws.cell(ws.max_row, cols.index(colorby)+1)
            f=DEC_FILL.get(r.get(colorby));
            if f: c.fill=f
    ws.freeze_panes='A2'; ws.auto_filter.ref=f'A1:{get_column_letter(len(cols))}{ws.max_row}'
    for i,c in enumerate(cols,1): ws.column_dimensions[get_column_letter(i)].width=widths.get(c,14)
    ws.row_dimensions[1].height=26

# ---- Tab 1: How to use ----
ws=wb.active; ws.title='① Read me'
info=[
 ['ngwindows.com — Backlink Disavow Review',''],
 ['Generated',str(datetime.date.today())],
 ['',''],
 ['WHAT TO DO','—'],
 ['1','Open “② Review list”. Rows are colour-coded: RED = disavow, YELLOW = manual review, and the KEEP list is on its own tab.'],
 ['2','Skim the “Why” and “Anchor” columns. Untick (delete the row) anything you recognise as a real/own site.'],
 ['3','The “③ Disavow file” tab is the exact text to upload to Google Search Console → Disavow Tool (or use disavow.txt).'],
 ['4','“④ Keep” = do NOT disavow. “⑤ Full data” = every signal if you want the detail.'],
 ['',''],
 ['NUMBERS','—'],
 ['Total referring domains',len(rows)],
 ['Disavow (HIGH+MEDIUM)',len(DIS)],
 ['   • HIGH confidence',conf['HIGH']],
 ['   • MEDIUM confidence',conf['MEDIUM']],
 ['Manual review',len(REV)],
 ['Keep (protected)',len(KEEP)],
 ['',''],
 ['ACTUAL BACKLINKS CHECKED','—'],
 ['Pulled 5,000+ individual backlink records (source page URL, anchor, follow) from Semrush + Ahrefs.',''],
 ['Each flagged row shows a real example link in “backlink_url” + “example_anchor”; “link_checked” = yes/beyond-sample.',''],
 ['Sample toxic anchors found across 200+ domains:',''],
 ['  •','“…SEOExpress.org and their backlink building service worked wonders… traffic +400%”'],
 ['  •','“High Quality Dofollow Backlinks DA50 PA40 Premium PBN … Buy Backlinks Online Cheap”'],
 ['  •','“JOIN OUR TELEGRAM https://t.me/s/darksidelinks”'],
 ['Blogspot PBNs (innocyscx / burnersgamershitasd) link using your microsite names (qualitypluswindows.com, roiwindows.com) as anchors.',''],
 ['Most spam links are nofollow (pass no equity — lower priority); the follow column flags the dofollow ones that matter most.',''],
 ['',''],
 ['⚠ OWNERSHIP','15 window-brand microsites (ngawindows.com, ngwindow.com, roiwindows.com …) may be YOUR OWN sites — they are in REVIEW, not disavow. Confirm before acting.'],
]
for r in info: ws.append(r)
ws.column_dimensions['A'].width=30; ws.column_dimensions['B'].width=100
ws['A1'].font=Font(bold=True,size=14,color='1F3864')
for rr in range(1,ws.max_row+1):
    if ws.cell(rr,2).value=='—': ws.cell(rr,1).font=Font(bold=True,color='C00000')

SIMPLE=['domain','decision','confidence','why','follow','example_anchor','backlink_url','authority','traffic','link_checked']
SW={'domain':28,'decision':11,'confidence':11,'why':34,'follow':9,'example_anchor':34,'backlink_url':50,
    'authority':10,'traffic':9,'link_checked':16}
build(wb.create_sheet('② Review list'),SIMPLE,DIS+REV,SW)
build(wb.create_sheet('④ Keep (do NOT disavow)'),SIMPLE,KEEP,SW)

# Tab 3: disavow file text
ws=wb.create_sheet('③ Disavow file')
ws.append(['Paste into Google Search Console → Disavow Tool (or use disavow.txt)'])
ws['A1'].font=Font(bold=True,color='1F3864')
ws.append([f'# ngwindows.com disavow — {datetime.date.today()} — {len(DIS)} domains'])
for r in sorted(DIS,key=lambda x:(x['confidence'],x['domain'])):
    ws.append([f"domain:{r['domain']}"])
ws.column_dimensions['A'].width=45

# Tab 5: full data
FULL=['domain','decision','confidence','category','why','anchor_type','example_anchor','backlink_url',
      'follow','bl_count','dofollow_n','nofollow_n','link_checked','dr','ascore','authority','traffic',
      'positions','is_spam','links','ip','country','evidence','qa_note']
FW={'domain':30,'category':26,'why':34,'example_anchor':40,'backlink_url':50,'evidence':55,'qa_note':60,'ip':15}
build(wb.create_sheet('⑤ Full data'),FULL,DIS+REV+KEEP,{**SW,**FW})

wb.save('ngwindows_disavow_review.xlsx')
print('workbook:',wb.sheetnames)

# ================= DASHBOARD =================
P={'disavow':'#e34948','review':'#eda100','keep':'#008300','ink':'#0b0b0b','ink2':'#52514e',
   'surf':'#ffffff','panel':'#fbfbfa','line':'#e6e6e2','accent':'#2a78d6'}
cat_counts=collections.Counter(r['why'] for r in DIS)
top_cats=cat_counts.most_common(9)
anchor_counts=collections.Counter(r['anchor_type'] for r in rows if r['anchor_type']!='n/a (Semrush-only)')
follow_counts=collections.Counter(r['follow'] for r in rows if r['follow'])
# link networks (recompute from ip among disavow/review)
ipc=collections.Counter(r['ip'] for r in rows if r['ip'] and r['decision']!='KEEP')
FARM={'203.161.54.114','118.139.181.85','118.139.176.46','118.139.178.200','118.139.161.199',
 '118.139.181.255','184.168.115.60','195.20.19.178','67.223.118.29','188.40.17.96','92.249.46.138','191.101.14.187'}
nets=[(ip,n) for ip,n in ipc.most_common(20) if n>=4 and ip in FARM][:8]
anchors=[('…SEOExpress.org and their backlink building service worked wonders… traffic +400%',222),
 ('Complete SEO for ngwindows.com: premium guest posts, contextual backlinks…',44),
 ('High Quality Dofollow Backlinks DA50 PA40 Premium PBN … Buy Backlinks Online Cheap',21),
 ('JOIN OUR TELEGRAM https://t.me/s/darksidelinks',10),
 ('tLvtiPx5V2OVDzj (random gibberish anchor)',11)]

def hbars(data,color,unit='',w=580,rowh=30,pad=190):
    if not data: return ''
    mx=max(v for _,v in data) or 1
    bw=w-pad-70; H=len(data)*rowh+10; out=[f'<svg viewBox="0 0 {w} {H}" width="100%" role="img">']
    for i,(lab,v) in enumerate(data):
        y=i*rowh+8; bl=max(6,bw*v/mx)
        lab_s=html.escape(str(lab))
        if len(lab_s)>28: lab_s=lab_s[:27]+'…'
        out.append(f'<text x="{pad-8}" y="{y+15}" text-anchor="end" font-size="12.5" fill="{P["ink2"]}">{lab_s}</text>')
        out.append(f'<rect x="{pad}" y="{y+3}" width="{bl:.1f}" height="16" rx="4" fill="{color}"/>')
        out.append(f'<text x="{pad+bl+7}" y="{y+15}" font-size="12" font-weight="600" fill="{P["ink"]}">{v}{unit}</text>')
    out.append('</svg>'); return ''.join(out)

def donut(parts):  # [(label,val,color)]
    tot=sum(v for _,v,_ in parts) or 1; import math
    cx,cy,r,sw=90,90,66,26; a=-math.pi/2; seg=[]
    for lab,v,col in parts:
        frac=v/tot; a2=a+frac*2*math.pi
        x1,y1=cx+r*math.cos(a),cy+r*math.sin(a); x2,y2=cx+r*math.cos(a2),cy+r*math.sin(a2)
        large=1 if frac>0.5 else 0
        seg.append(f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        a=a2
    return (f'<svg viewBox="0 0 180 180" width="180" height="180" role="img">{"".join(seg)}'
            f'<text x="90" y="86" text-anchor="middle" font-size="26" font-weight="700" fill="{P["ink"]}">{tot}</text>'
            f'<text x="90" y="106" text-anchor="middle" font-size="12" fill="{P["ink2"]}">domains</text></svg>')

def kpi(v,l,c):
    return (f'<div class="kpi"><div class="kpi-v" style="color:{c}">{v}</div><div class="kpi-l">{l}</div></div>')

toxic_pct=round(100*len(DIS)/len(rows))
net_rows=''.join(f'<tr><td class="mono">{html.escape(ip)}</td><td style="text-align:right">{n}</td></tr>' for ip,n in nets)
anc_rows=''.join(f'<tr><td>{html.escape(a)}</td><td style="text-align:right">{n}</td></tr>' for a,n in anchors)
legend=''.join(f'<span class="lg"><i style="background:{c}"></i>{l} — {v}</span>' for l,v,c in
    [('Disavow',len(DIS),P['disavow']),('Review',len(REV),P['review']),('Keep',len(KEEP),P['keep'])])

HTML=f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ngwindows.com — Backlink Disavow Dashboard</title>
<style>
 :root{{--surf:{P['surf']};--panel:{P['panel']};--ink:{P['ink']};--ink2:{P['ink2']};--line:{P['line']}}}
 *{{box-sizing:border-box}} body{{margin:0;font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  background:#f2f2ef;color:var(--ink);padding:26px}}
 .wrap{{max-width:1120px;margin:0 auto}}
 h1{{font-size:22px;margin:0 0 2px}} .sub{{color:var(--ink2);margin-bottom:20px;font-size:13px}}
 .grid{{display:grid;gap:16px}} .k5{{grid-template-columns:repeat(5,1fr)}}
 .two{{grid-template-columns:1.15fr .85fr}} .two2{{grid-template-columns:1fr 1fr}}
 @media(max-width:820px){{.k5,.two,.two2{{grid-template-columns:1fr}}}}
 .card{{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:18px 18px 14px}}
 .card h2{{font-size:13px;letter-spacing:.02em;text-transform:uppercase;color:var(--ink2);margin:0 0 14px;font-weight:700}}
 .kpi{{background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:16px 14px;text-align:center}}
 .kpi-v{{font-size:30px;font-weight:800;line-height:1}} .kpi-l{{font-size:12px;color:var(--ink2);margin-top:6px}}
 .lg{{display:inline-flex;align-items:center;gap:6px;margin-right:16px;font-size:12.5px;color:var(--ink2)}}
 .lg i{{width:11px;height:11px;border-radius:3px;display:inline-block}}
 .donutrow{{display:flex;align-items:center;gap:18px;flex-wrap:wrap}}
 table{{width:100%;border-collapse:collapse;font-size:12.5px}}
 td{{padding:6px 8px;border-bottom:1px solid var(--line)}} .mono{{font-family:ui-monospace,Menlo,Consolas,monospace}}
 .warn{{background:#fff4e5;border:1px solid #f0c98a;border-left:4px solid {P['review']};border-radius:10px;padding:14px 16px;margin-top:16px}}
 .warn b{{color:#9a5b00}}
 .banner{{background:#fdecec;border:1px solid #f2b8b8;border-left:4px solid {P['disavow']};border-radius:10px;padding:14px 16px;margin-bottom:18px;font-size:13.5px}}
 .foot{{color:var(--ink2);font-size:11.5px;margin-top:22px;text-align:center}}
</style>
<div class="wrap">
 <h1>ngwindows.com — Backlink Disavow Dashboard</h1>
 <div class="sub">Ahrefs + Semrush referring-domain audit · {datetime.date.today()} · anchors, follow-status &amp; {sum(1 for r in (DIS+REV) if r.get('backlink_url'))}/{len(DIS)+len(REV)} flagged domains checked at the actual-backlink level</div>

 <div class="banner"><b>Profile verdict: heavily manipulated (paid-PBN) link profile.</b>
  {toxic_pct}% of referring domains are toxic and staged for disavow. The scheme is self-evident in the anchor text
  (“Buy Backlinks Online Cheap”, “Premium PBN Network Service”, Telegram spam).</div>

 <div class="grid k5" style="margin-bottom:16px">
  {kpi(len(rows),'Referring domains',P['ink'])}
  {kpi(len(DIS),'Flag to disavow',P['disavow'])}
  {kpi(len(REV),'Manual review',P['review'])}
  {kpi(len(KEEP),'Keep (protected)',P['keep'])}
  {kpi(str(toxic_pct)+'%','Toxic share',P['disavow'])}
 </div>

 <div class="grid two" style="margin-bottom:16px">
  <div class="card"><h2>Why domains are flagged (disavow reasons)</h2>{hbars(top_cats,P['disavow'])}</div>
  <div class="card"><h2>Decision split</h2>
   <div class="donutrow">{donut([('Disavow',len(DIS),P['disavow']),('Review',len(REV),P['review']),('Keep',len(KEEP),P['keep'])])}
    <div>{legend.replace('<span','<div style="margin:6px 0" ').replace('</span>','</div>')}</div></div></div>
 </div>

 <div class="grid two2" style="margin-bottom:16px">
  <div class="card"><h2>Anchor-text type (Ahrefs, one per domain)</h2>{hbars(anchor_counts.most_common(),P['accent'])}
   <div style="font-size:12px;color:var(--ink2);margin-top:10px">Follow status:
   <b style="color:{P['disavow']}">{follow_counts.get('nofollow',0)} nofollow</b> · {follow_counts.get('dofollow',0)} dofollow
   — nofollow links pass no equity, so they are lower disavow priority.</div></div>
  <div class="card"><h2>Largest link networks (shared farm IP)</h2>
   <table><tr><td><b>IP</b></td><td style="text-align:right"><b>domains</b></td></tr>{net_rows}</table></div>
 </div>

 <div class="card"><h2>Smoking-gun spam anchors</h2>
  <table><tr><td><b>Anchor text (verbatim)</b></td><td style="text-align:right"><b>ref. domains</b></td></tr>{anc_rows}</table></div>

 <div class="warn"><b>⚠ Verify ownership before disavowing:</b> 15 near-identical window-brand microsites
  (ngawindows.com, ngwindow.com, northgawindows.com, roiwindows.com, thermalprowindows.com, performingwindows.com …)
  sit on shared AWS IPs and are likely <b>your own sites or a self-built PBN</b>. They are held in <b>Manual review</b>,
  not disavow — redirect/consolidate your own sites rather than disavow them.</div>

 <div class="foot">Nothing is submitted to Google automatically. Review the workbook, then upload disavow.txt yourself.</div>
</div></html>"""
open('dashboard.html','w').write(HTML)
print('dashboard.html bytes:',len(HTML))
print('disavow',len(DIS),'review',len(REV),'keep',len(KEEP),'toxic%',toxic_pct)
print('top cats:',top_cats[:5])
print('nets:',nets)
