import csv,re,math,json
SRC='/root/.claude/uploads/d61293a7-0af2-5b41-b7a9-144ac89c2aa6/add7af2e-Reachgorilla_22_07_26_-_Guestposts.csv'
rows=list(csv.DictReader(open(SRC)))
built=set(x.strip().lower() for x in open('built_partial.txt') if x.strip())
def num(s):
    s=str(s or '').replace(',','').replace('$','').strip()
    try: return float(s)
    except: return 0.0
NONENG=('Spanish','French','Italian','German','Portuguese','Ukrainian','Arabic','Romanian','Turkish','Greek','Dutch','Indonesian','Czech','Polish','Russian','Japanese','Korean','Chinese','Hindi','Hebrew','Thai','Vietnamese','Swedish','Danish','Norwegian','Finnish','Hungarian','Bulgarian','Serbian','Croatian','Slovak','Persian','Malay','Filipino','Catalan','Multilingual','Belarusian','talian')
MEDTECH=r'\b(medical device|medtech|med-tech|health ?tech|healthcare technology|health ?it|clinical engineering|biomedical|medical technology|digital health|health informatics|telemedicine|telehealth|life sciences|pharma tech)\b'
CYBER=r'\b(cyber ?security|cybersecurity|infosec|information security|network security|it security|data security|penetration testing|pentest|ethical hacking|hacking|malware|ransomware|privacy|compliance|grc|data protection|vulnerability)\b'
HEALTH=r'\b(health|healthcare|medical|medicine|clinical|hospital|physician|doctor|nursing|patient|surgery|diagnostic)\b'
B2BTECH=r'\b(technology|tech|software|saas|it\b|enterprise|cloud|devops|engineering|electronics|data|ai\b|artificial intelligence|iot|automation|innovation|startup|b2b)\b'
BIZ=r'\b(business|entrepreneur|finance|management|leadership|marketing|industry|news)\b'
BAD=r'\b(casino|gambling|betting|poker|porn|adult|escort|crypto|bitcoin|forex|loan|payday|essay|dating|cbd|cannabis|vape|food|recipe|travel|fashion|beauty|wedding|pets|sports|gaming|anime|music|movie)\b'
out=[]
for r in rows:
    dom=r['Website'].strip().lower().removeprefix('www.')
    if dom in built: continue
    cat=r['Category'] or ''
    m=re.match(r'\s*([A-Za-z]+)\s*:',cat); lang=m.group(1) if m else ''
    if lang in NONENG: continue
    c=cat.lower()
    AS,TF,CF=num(r['AS']),num(r['TF']),num(r['CF'])
    tr,rd,pr=num(r['Traffic']),num(r['RD']),num(r['Price ($)'])
    if TF<15 or AS<25 or tr<3000 or pr<=0: continue
    if CF>0 and TF/CF<0.55: continue
    rel=0; tags=[]
    if re.search(MEDTECH,c): rel+=70; tags.append('MEDTECH')
    if re.search(CYBER,c):   rel+=55; tags.append('CYBER')
    if re.search(HEALTH,c):  rel+=28; tags.append('health')
    if re.search(B2BTECH,c): rel+=20; tags.append('tech')
    if re.search(BIZ,c):     rel+=8;  tags.append('biz')
    if rel<20: continue
    # penalise consumer-junk categories unless medtech/cyber present
    if re.search(BAD,c) and not re.search(MEDTECH+'|'+CYBER,c): rel-=25
    if rel<20: continue
    qual=min(AS,100)*0.75+min(TF,80)*0.95+min(math.log10(max(tr,1))*11,55)+min(math.log10(max(rd,1))*7,30)
    score=rel*1.3+qual
    out.append(dict(domain=dom,cat=cat,AS=int(AS),TF=int(TF),CF=int(CF),traffic=int(tr),rd=int(rd),price=int(pr),
                    tags='+'.join(tags),rel=rel,score=round(score,1),value=round(score/(pr**0.55),2)))
out.sort(key=lambda x:-x['score'])
json.dump(out,open('shortlist.json','w'))
print("candidates:",len(out))
for t in ('MEDTECH','CYBER','health','tech'):
    print(" ",t,sum(1 for x in out if t in x['tags']))
