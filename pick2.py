import csv, sys
path = sys.argv[1]
built = set(l.strip().lower() for l in open('built.txt') if l.strip())
def num(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0

# UGC / profile / directory platforms - not editorial placements
BAD = ('houzz','vocal.media','ko-fi','evite','medium.com','linktr','issuu','behance','niadd',
       'storymirror','gardenweb','findaspring','digitaljournal','appsgeyser','wowdeals',
       'spellingbee','quotebless','shayari','dreammeaniing','blessingtide','dotmovie',
       'thefilmgordon','xxbrits','windstream','noodle-magazine','mehndistan','readwritetips')
FOOD = {'food & drink','cooking','recipes'}
HOME = {'home','parenting','family','events','wellness'}

rows=[]
for r in csv.DictReader(open(path, encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built: continue
    if any(b in d for b in BAD): continue
    if (r.get('Language') or '').strip().lower()!='english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    AS,TF,CF=num(r.get('AS')),num(r.get('TF')),num(r.get('CF'))
    tr,pr,rd=num(r.get('Traffic')),num(r.get('Price ($)')),num(r.get('RD'))
    if pr<=0 or AS<25 or TF<20 or tr<3000 or rd<150: continue
    if TF<CF*0.5: continue
    au=d.endswith(('.com.au','.au','.co.nz','.net.au','.org.au'))
    food=bool(cats&FOOD); home=bool(cats&HOME)
    lifes='lifestyle' in cats
    if not (food or home or lifes or au): continue
    rows.append(dict(d=d,c=r.get('Category'),AS=AS,TF=TF,CF=CF,tr=tr,rd=rd,pr=pr,
                     au=au,food=food,home=home,cpm=pr/(tr/1000)))

def show(title, sel, n=18, key=None):
    sel=sorted(sel,key=key or (lambda x:-(x['AS']+x['TF'])))[:n]
    print(f"\n=== {title}  ({len(sel)} shown) ===")
    print(f"{'Domain':34}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>9}   Category")
    print('-'*118)
    for x in sel:
        print(f"{x['d']:34}{x['AS']:4.0f}{x['TF']:4.0f}{x['CF']:4.0f}{x['tr']:10,.0f}{x['rd']:8,.0f}{x['pr']:9,.0f}   {x['c'][:42]}")

show("A. AUSTRALIA / NZ GEO MATCH", [r for r in rows if r['au']], 20)
show("B. FOOD & DRINK core", [r for r in rows if r['food'] and not r['au']], 20)
show("C. HOME / PARENTING / FAMILY / EVENTS core", [r for r in rows if r['home'] and not r['food'] and not r['au']], 20)
show("D. BEST VALUE - lifestyle, under $80, traffic 20k+",
     [r for r in rows if r['pr']<80 and r['tr']>20000 and not r['au']], 20,
     key=lambda x: x['cpm'])

with open('nangwizard-reachgorilla-shortlist.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Domain','Category','AS','TF','CF','Traffic','RD','Price_USD','Bucket'])
    for x in sorted(rows,key=lambda y:-(y['AS']+y['TF'])):
        b='AU/NZ' if x['au'] else ('Food' if x['food'] else ('Home/Family' if x['home'] else 'Lifestyle'))
        w.writerow([x['d'],x['c'],int(x['AS']),int(x['TF']),int(x['CF']),int(x['tr']),int(x['rd']),round(x['pr'],2),b])
print(f"\n-> nangwizard-reachgorilla-shortlist.csv  ({len(rows)} qualified sites, all unbuilt)")
