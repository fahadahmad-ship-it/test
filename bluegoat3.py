import csv, sys
built=set(l.strip().lower() for l in open('built-bluegoat.txt') if l.strip())
def n(s):
    try: return float(str(s).replace(',','').strip() or 0)
    except: return 0.0
UGC=('codepen','dev.to','crunchbase','wufoo','clickup','vocal.media','gitbook','strikingly','indiehackers',
'cargo.site','rapidapi','protocols.io','openprocessing','pitchero','schoology','webcampus','minecraftforum',
'boosty','wistia','pocketcasts','ruby-doc','hackmd','.edu','behance','slideshare','quora','reddit','medium.com',
'substack','canva','figma','trello','atlassian','zendesk','hubspot','shopify','wix.com','weebly','jimdo',
'zohosites','scrapbox','selar','.io/','blogspot','wordpress.com','tumblr','issuu','linktr','opencart')
TECH={'technology','software','ai','saas','cybersecurity','security','tech news','software development',
      'data','it','engineering','science','telecom','internet'}
HEALTH={'health & fitness','health and medicine','mental health','wellness','medicine','healthcare','pharma'}
rows=[]
for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')):
    d=(r.get('Website') or '').strip().lower()
    if not d or d in built or any(u in d for u in UGC): continue
    if (r.get('Language') or '').strip().lower()!='english': continue
    cats={c.strip().lower() for c in (r.get('Category') or '').split(',')}
    AS,TF,CF=n(r.get('AS')),n(r.get('TF')),n(r.get('CF'))
    tr,pr,rd=n(r.get('Traffic')),n(r.get('Price ($)')),n(r.get('RD'))
    if pr<=0 or pr>=320 or AS<35 or TF<28: continue
    if tr<2000 or rd<150: continue
    if TF<CF*0.5: continue
    tech=bool(cats&TECH); health=bool(cats&HEALTH)
    if not (tech or health): continue
    rows.append((AS+TF,d,'Health' if health and not tech else 'Tech',r.get('Category'),AS,TF,CF,tr,rd,pr))
rows.sort(key=lambda x:-x[0])
seen=set(open('bluegoat-candidates.csv').read())
print(f"{len(rows)} candidates (widened floors)\n")
print(f"{'Domain':36}{'B':6}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>7}{'Price$':>8}  Category")
print('-'*124)
for s,d,b,c,A,T,C,tr,rd,p in rows[:50]:
    print(f"{d:36}{b:6}{A:4.0f}{T:4.0f}{C:4.0f}{tr:10,.0f}{rd:7,.0f}{p:8,.0f}  {c[:36]}")
