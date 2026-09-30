import csv,re,math,json
SRC='/root/.claude/uploads/d61293a7-0af2-5b41-b7a9-144ac89c2aa6/add7af2e-Reachgorilla_22_07_26_-_Guestposts.csv'
rows=list(csv.DictReader(open(SRC)))
built=set(x.strip().lower() for x in open('sheet_built.txt') if x.strip())
def num(s):
    s=str(s or '').replace(',','').replace('$','').strip()
    try: return float(s)
    except: return 0.0
NONENG=('Spanish','French','Italian','German','Portuguese','Ukrainian','Arabic','Romanian','Turkish','Greek','Dutch','Indonesian','Czech','Polish','Russian','Japanese','Korean','Chinese','Hindi','Hebrew','Thai','Vietnamese','Swedish','Danish','Norwegian','Finnish','Hungarian','Bulgarian','Serbian','Croatian','Slovak','Persian','Malay','Filipino','Catalan','Multilingual','Belarusian','talian','Kannada','Tamil')
PRIV=r'\b(privacy|data protection|identity|personal data|gdpr|surveillance|anonymity|data broker)\b'
CYBER=r'\b(cyber ?security|cybersecurity|infosec|information security|network security|it security|data security|penetration testing|pentest|hacking|malware|ransomware|vpn|encryption|vulnerability|fraud|scam|phishing)\b'
TECH=r'\b(technology|tech|software|saas|it\b|enterprise|cloud|data|ai\b|artificial intelligence|iot|startup|b2b|internet|digital)\b'
BIZ=r'\b(business|entrepreneur|finance|management|leadership|marketing|industry|legal|law)\b'
NEWS=r'\b(news|media|journalism|magazine)\b'
BAD=r'\b(casino|gambling|betting|porn|adult|escort|crypto|bitcoin|forex|loan|payday|essay|dating|cbd|cannabis|vape|nicotine|food|recipe|travel|fashion|beauty|wedding|pets|sports|gaming|anime|music|movie|parenting|kids|religion)\b'
EXCL=r'(vocal\.media|medium\.com|\.kompass\.com|merchantcircle|beforeitsnews|storeboard|zupyak|writeupcafe|topsitenet|onesmablog|blogolize|\.edu$|genius\.com|msn\.com|bignewsnetwork|selfgrowth|newsbreak|prlog|openpr|einpresswire|globenewswire|prnewswire|directory|listing)'
out=[]
for r in rows:
    dom=r['Website'].strip().lower().removeprefix('www.')
    if dom in built or re.search(EXCL,dom): continue
    cat=r['Category'] or ''
    m=re.match(r'\s*([A-Za-z]+)\s*:',cat); lang=m.group(1) if m else ''
    if lang in NONENG: continue
    c=cat.lower()
    if re.search(BAD,c): continue
    AS,TF,CF=num(r['AS']),num(r['TF']),num(r['CF'])
    tr,rd,pr=num(r['Traffic']),num(r['RD']),num(r['Price ($)'])
    if TF<18 or AS<28 or tr<5000 or pr<=0: continue
    if CF>0 and TF/CF<0.58: continue
    rel=0; tags=[]
    if re.search(PRIV,c): rel+=75; tags.append('PRIVACY')
    if re.search(CYBER,c): rel+=65; tags.append('CYBER')
    if re.search(TECH,c): rel+=30; tags.append('tech')
    if re.search(BIZ,c): rel+=12; tags.append('biz')
    if re.search(NEWS,c): rel+=8; tags.append('news')
    if rel<25: continue
    rd1k=round(rd/max(tr,1)*1000)
    qual=min(AS,100)*0.75+min(TF,80)*0.95+min(math.log10(max(tr,1))*11,55)+min(math.log10(max(rd,1))*7,30)
    out.append(dict(domain=dom,cat=cat,AS=int(AS),TF=int(TF),CF=int(CF),traffic=int(tr),rd=int(rd),price=int(pr),
        tags='+'.join(tags),rd1k=rd1k,score=round(rel*1.3+qual,1)))
out.sort(key=lambda x:-x['score'])
json.dump(out,open('shortlist.json','w'))
print("candidates:",len(out))
print(" PRIVACY:",sum(1 for x in out if 'PRIVACY' in x['tags']),"| CYBER:",sum(1 for x in out if 'CYBER' in x['tags']))
print("\n--- PRIVACY / CYBER tagged, clean ratio ---")
for x in [y for y in out if ('PRIVACY' in y['tags'] or 'CYBER' in y['tags']) and y['rd1k']<=350][:26]:
    print(f"{x['domain']:<31} ${x['price']:>5} AS{x['AS']:>3} TF{x['TF']:>3} tr{x['traffic']:>9,} rd/1k{x['rd1k']:>4} | {x['cat'][:38]}")
