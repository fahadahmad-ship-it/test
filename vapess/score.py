import csv,re,math,json
SRC='/root/.claude/uploads/d61293a7-0af2-5b41-b7a9-144ac89c2aa6/add7af2e-Reachgorilla_22_07_26_-_Guestposts.csv'
rows=list(csv.DictReader(open(SRC)))
built=set(x.strip().lower() for x in open('sheet_built.txt') if x.strip())
def num(s):
    s=str(s or '').replace(',','').replace('$','').strip()
    try: return float(s)
    except: return 0.0
NONENG=('Spanish','French','Italian','German','Portuguese','Ukrainian','Arabic','Romanian','Turkish','Greek','Dutch','Indonesian','Czech','Polish','Russian','Japanese','Korean','Chinese','Hindi','Hebrew','Thai','Vietnamese','Swedish','Danish','Norwegian','Finnish','Hungarian','Bulgarian','Serbian','Croatian','Slovak','Persian','Malay','Filipino','Catalan','Multilingual','Belarusian','talian')
VAPE=r'\b(vap(e|ing)|e-?cig|e-?liquid|smoking|tobacco|nicotine|cbd|cannabis|hemp|smoke shop|headshop)\b'
UKRX=r'\b(uk|united kingdom|british|britain|england|scotland|wales|london|manchester|birmingham|glasgow|edinburgh|leeds|liverpool|bristol|yorkshire|essex|kent|devon|cornwall)\b'
LIFE=r'\b(lifestyle|magazine|culture|entertainment|men|music|fashion|nightlife|events|celebrity|arts)\b'
NEWS=r'\b(news|local news|media|journalism|newspaper|current affairs)\b'
BIZ=r'\b(business|retail|ecommerce|e-commerce|entrepreneur|marketing|industry|finance)\b'
HEALTH=r'\b(health|wellness|wellbeing)\b'
BAD=r'\b(casino|gambling|betting|poker|slots|porn|adult|escort|crypto|bitcoin|forex|loan|payday|essay|dating|kids|children|parenting|school|religion|church)\b'
out=[]
for r in rows:
    dom=r['Website'].strip().lower().removeprefix('www.')
    if dom in built: continue
    cat=r['Category'] or ''
    m=re.match(r'\s*([A-Za-z]+)\s*:',cat); lang=m.group(1) if m else ''
    if lang in NONENG: continue
    c=cat.lower()
    if re.search(BAD,c): continue
    AS,TF,CF=num(r['AS']),num(r['TF']),num(r['CF'])
    tr,rd,pr=num(r['Traffic']),num(r['RD']),num(r['Price ($)'])
    if TF<15 or AS<25 or tr<3000 or pr<=0: continue
    if CF>0 and TF/CF<0.55: continue
    isuk = dom.endswith('.co.uk') or dom.endswith('.uk') or bool(re.search(UKRX,c))
    rel=0; tags=[]
    if re.search(VAPE,c): rel+=70; tags.append('VAPE')
    if isuk: rel+=40; tags.append('UK')
    if re.search(LIFE,c): rel+=18; tags.append('lifestyle')
    if re.search(NEWS,c): rel+=12; tags.append('news')
    if re.search(BIZ,c): rel+=10; tags.append('biz')
    if re.search(HEALTH,c): rel+=8; tags.append('health')
    if rel<20: continue
    rd1k=round(rd/max(tr,1)*1000)
    qual=min(AS,100)*0.75+min(TF,80)*0.95+min(math.log10(max(tr,1))*11,55)+min(math.log10(max(rd,1))*7,30)
    out.append(dict(domain=dom,cat=cat,AS=int(AS),TF=int(TF),CF=int(CF),traffic=int(tr),rd=int(rd),price=int(pr),
        tags='+'.join(tags),uk=isuk,rd1k=rd1k,score=round(rel*1.3+qual,1)))
out.sort(key=lambda x:-x['score'])
json.dump(out,open('shortlist.json','w'))
print("candidates:",len(out))
print(" VAPE-tagged:",sum(1 for x in out if 'VAPE' in x['tags']))
print(" UK:",sum(1 for x in out if x['uk']))
