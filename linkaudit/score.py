import csv,re,json

SRC='/root/.claude/uploads/d61293a7-0af2-5b41-b7a9-144ac89c2aa6/add7af2e-Reachgorilla_22_07_26_-_Guestposts.csv'
rows=list(csv.DictReader(open(SRC)))
built=set(x.strip().lower() for x in open('built_all.txt') if x.strip())

def num(s):
    s=str(s or '').replace(',','').replace('$','').strip()
    try: return float(s)
    except: return 0.0

NONENG=('Spanish','French','Italian','German','Portuguese','Ukrainian','Arabic','Romanian','Turkish','Greek','Dutch','Indonesian','Czech','Polish','Russian','Japanese','Korean','Chinese','Hindi','Hebrew','Thai','Vietnamese','Swedish','Danish','Norwegian','Finnish','Hungarian','Bulgarian','Serbian','Croatian','Slovak','Slovenian','Lithuanian','Latvian','Estonian','Persian','Farsi','Urdu','Bengali','Tamil','Malay','Filipino','Catalan','Galician','Albanian','Macedonian','Georgian','Armenian','Azerbaijani','Kazakh','Mongolian','Nepali','Sinhala','Burmese','Khmer','Lao','Afrikaans','Swahili','Icelandic','Irish','Welsh','Basque','Bosnian','Belarusian','Latin','Multilingual')

FOOD=r'\b(food|cooking|cook|recipe|baking|bake|dessert|sweets|pastry|culinary|restaurant|cuisine|kitchen|gastronom|foodie|chef|dining|drink|beverage|cocktail|bartend|wine|spirits|coffee|cafe|catering|grocer|nutrition|vegan|vegetarian|bbq|barbecue|brunch)\b'
PARTY=r'\b(part(y|ies)|event|wedding|entertaining|nightlife|festival|celebration|hospitality|bar\b|clubbing)'
HOMEL=r'\b(home|lifestyle|interior|living|decor|household|garden|diy)\b'
PARENT=r'\b(mom|mum|parent|family|mother|kids|children)\b'
LIFE=r'\b(lifestyle|magazine|culture|entertainment|travel|news|health|wellness|fashion|beauty)\b'
AURX=r'\b(australia|australian|aussie|sydney|melbourne|brisbane|perth|adelaide|gold coast|canberra|queensland|victoria|nsw|tasmania)\b'
BAD=r'\b(casino|gambling|betting|poker|slots|porn|adult|escort|xxx|crypto|bitcoin|forex|trading|loan|payday|insurance|pharma|pharmacy|cbd|weed|cannabis|marijuana|essay|dating|gun|firearm|islam|church|astrolog|sports betting)\b'

out=[]
for r in rows:
    dom=r['Website'].strip().lower().removeprefix('www.')
    cat=(r['Category'] or '')
    m=re.match(r'\s*([A-Za-z]+)\s*:',cat)
    lang=m.group(1) if m else ''
    if lang in NONENG: continue
    if dom in built: continue
    AS,TF,CF=num(r['AS']),num(r['TF']),num(r['CF'])
    tr,rd,price=num(r['Traffic']),num(r['RD']),num(r['Price ($)'])
    c=cat.lower()
    if re.search(BAD,c): continue
    # quality gates
    if TF<12 or AS<20 or tr<1500 or price<=0: continue
    if CF>0 and TF/CF<0.55: continue   # trust/citation ratio spam filter

    rel=0; tags=[]
    if re.search(FOOD,c): rel+=50; tags.append('food')
    if re.search(PARTY,c): rel+=22; tags.append('party')
    if re.search(HOMEL,c): rel+=14; tags.append('home')
    if re.search(PARENT,c): rel+=10; tags.append('parent')
    if re.search(LIFE,c): rel+=6; tags.append('lifestyle')
    isau = bool(re.search(AURX,c)) or dom.endswith('.au')
    if isau: rel+=45; tags.append('AU')
    if rel<20: continue

    import math
    qual = min(AS,100)*0.7 + min(TF,80)*0.9 + min(math.log10(max(tr,1))*11,55) + min(math.log10(max(rd,1))*7,30)
    score = rel*1.25 + qual
    value = score/ (price**0.55) if price>0 else 0
    out.append(dict(domain=dom,cat=cat,AS=int(AS),TF=int(TF),CF=int(CF),traffic=int(tr),rd=int(rd),
                    price=int(price),rel=rel,tags='+'.join(tags),au=isau,score=round(score,1),value=round(value,2)))

out.sort(key=lambda x:-x['score'])
json.dump(out,open('shortlist.json','w'),indent=1)
print("candidates passing filters:",len(out))
print("AU among them:",sum(1 for x in out if x['au']))
print("food among them:",sum(1 for x in out if 'food' in x['tags']))
