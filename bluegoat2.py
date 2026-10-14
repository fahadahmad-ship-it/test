import csv
UGC=('codepen.io','dev.to','crunchbase','opencart','wufoo','clickup','vocal.media','gitbook','strikingly',
'indiehackers','cargo.site','rapidapi','protocols.io','openprocessing','musicglue','pitchero','schoology',
'webcampus','minecraftforum','boosty','wistia','pocketcasts','cyberpanel','ruby-doc','hackmd','.unr.edu',
'caringbridge','beyondblue','behance','slideshare','quora','reddit','medium.com','substack','notion.site',
'canva','figma','trello','atlassian','zendesk','hubspot','shopify','wix.com','weebly','jimdo','sites.google')
OFFTOPIC=('minecraft','gaming','gmauthority','automotive','psu.com','cgmagonline','tuaw','everythingusb',
'findyourfate','suziethefoodie','onestep4ward','spacedaily','factsanddetails','thedailyaztec','kongotech',
'ibtimes','musicglue')
rows=[]
for r in csv.DictReader(open('bluegoat-candidates.csv')):
    d=r['Domain']
    if any(u in d for u in UGC) or any(o in d for o in OFFTOPIC): continue
    rows.append((int(r['AS'])+int(r['TF']),r))
rows.sort(key=lambda t: -t[0])
print(f"{len(rows)} editorial candidates (UGC + off-topic removed)\n")
print(f"{'Domain':36}{'AS':>4}{'TF':>4}{'CF':>4}{'Traffic':>10}{'RD':>8}{'Price$':>8}  Category")
print('-'*126)
for s,r in rows[:38]:
    print(f"{r['Domain']:36}{r['AS']:>4}{r['TF']:>4}{r['CF']:>4}{int(r['Traffic']):10,}{int(r['RD']):8,}{float(r['Price_USD']):8,.0f}  {r['Category'][:40]}")
