import csv, collections, re, json
from urllib.parse import urlparse
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
def host(u):
    h=urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h
w=[r for r in rows if host(r['Referring page URL'])=='whosmypro.com']
urls=collections.Counter(r['Referring page URL'] for r in w)
print("links",len(w),"distinct URLs",len(urls))
print("dup counts:",collections.Counter(urls.values()))
print("distinct targets:",collections.Counter(r['Target URL'] for r in w))
print("\nsample redirect chain:",[ (r['Redirect Chain URLs'],r['Redirect Chain status codes']) for r in w if r['Redirect Chain URLs'].strip()][:2])
cities=sorted(set(urlparse(u).path for u in urls))
print("\npaths",len(cities)); print(cities)
print("\nExternal links / Linked domains stats:",collections.Counter((r['External links'],r['Linked domains']) for r in w).most_common(6))
print("Domain traffic:",set(r['Domain traffic'] for r in w),"page traffic:",collections.Counter(r['Page traffic'] for r in w).most_common(3))
print("Keywords:",collections.Counter(r['Keywords'] for r in w).most_common(3))
print("Refdomains col:",collections.Counter(r['Referring domains'] for r in w).most_common(3))
print("\nLeft/Right context samples:")
for r in w[:4]: print("  L:",r['Left context'][:120],"| R:",r['Right context'][:120])
print("firstseen range:",min(r['First seen'] for r in w),max(r['First seen'] for r in w))
print("lastseen range:",min(r['Last seen'] for r in w),max(r['Last seen'] for r in w))
print("Type:",collections.Counter(r['Type'] for r in w), "Content:",collections.Counter(r['Content'] for r in w))
h=[r for r in rows if host(r['Referring page URL'])=='homeownerideas.com']
print("\n--- homeownerideas",len(h))
for r in h: print("  ",r['Referring page URL'],"|",r['Referring page title'],"| L:",r['Left context'][:80],"| R:",r['Right context'][:80],"| tgt",r['Target URL'],"| pt",r['Page type'],"| cat",r['Page category'][:60],"| DR",r['Domain rating'],"| traf",r['Domain traffic'],"| first",r['First seen'])
