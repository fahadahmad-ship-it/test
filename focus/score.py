import csv,re,math,json
SRC='/root/.claude/uploads/d61293a7-0af2-5b41-b7a9-144ac89c2aa6/add7af2e-Reachgorilla_22_07_26_-_Guestposts.csv'
rows=list(csv.DictReader(open(SRC)))
built=set(x.strip().lower() for x in open('sheet_built.txt') if x.strip())
def num(s):
    s=str(s or '').replace(',','').replace('$','').strip()
    try: return float(s)
    except: return 0.0
NONENG=('Spanish','French','Italian','German','Portuguese','Ukrainian','Arabic','Romanian','Turkish','Greek','Dutch','Indonesian','Czech','Polish','Russian','Japanese','Korean','Chinese','Hindi','Hebrew','Thai','Vietnamese','Swedish','Danish','Norwegian','Finnish','Hungarian','Bulgarian','Serbian','Croatian','Slovak','Persian','Malay','Filipino','Catalan','Multilingual','Belarusian','talian')
EYE=r'\b(eye ?care|eyecare|optometry|optician|ophthalm|vision|optical|laser eye|lasik)\b'
MED=r'\b(health|healthcare|medical|medicine|clinic|surgery|wellness|wellbeing|cosmetic|aesthetic|dental|nhs|patient)\b'
UKRX=r'\b(uk|united kingdom|british|britain|england|scotland|wales|london|manchester|birmingham|glasgow|edinburgh|leeds|liverpool|bristol|yorkshire)\b'
LIFE=r'\b(lifestyle|magazine|beauty|fashion|women|men|culture|entertainment)\b'
NEWS=r'\b(news|local news|media|journalism)\b'
BAD=r'\b(casino|gambling|betting|poker|porn|adult|escort|crypto|bitcoin|forex|loan|payday|essay|dating|cbd|cannabis|vape|nicotine|gaming|anime|sports betting)\b'
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
    if re.search(EYE,c): rel+=75; tags.append('EYE')
    if re.search(MED,c): rel+=45; tags.append('health')
    if isuk: rel+=30; tags.append('UK')
    if re.search(LIFE,c): rel+=14; tags.append('lifestyle')
    if re.search(NEWS,c): rel+=8; tags.append('news')
    if rel<25: continue
    rd1k=round(rd/max(tr,1)*1000)
    qual=min(AS,100)*0.75+min(TF,80)*0.95+min(math.log10(max(tr,1))*11,55)+min(math.log10(max(rd,1))*7,30)
    out.append(dict(domain=dom,cat=cat,AS=int(AS),TF=int(TF),CF=int(CF),traffic=int(tr),rd=int(rd),price=int(pr),
        tags='+'.join(tags),uk=isuk,rd1k=rd1k,score=round(rel*1.3+qual,1)))
out.sort(key=lambda x:-x['score'])
json.dump(out,open('shortlist.json','w'))
print("candidates:",len(out))
print(" EYE:",sum(1 for x in out if 'EYE' in x['tags']),"| health:",sum(1 for x in out if 'health' in x['tags']),"| UK:",sum(1 for x in out if x['uk']))
print("\n--- health/UK under $500, best first ---")
UGC=r'(vocal\.media|medium\.com|\.kompass\.com|merchantcircle|beforeitsnews|storeboard|zupyak|writeupcafe|topsitenet|onesmablog|blogolize)'
c=[x for x in out if x['price']<=500 and x['rd1k']<=400 and not re.search(UGC,x['domain']) and ('health' in x['tags'] or 'EYE' in x['tags'])]
for x in c[:28]:
    print(f"{x['domain']:<32} ${x['price']:>4} AS{x['AS']:>3} TF{x['TF']:>3} tr{x['traffic']:>9,} rd/1k{x['rd1k']:>4} {'UK' if x['uk'] else '  '} | {x['cat'][:40]}")
