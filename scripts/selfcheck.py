import json, csv, io, re, sys
D=json.load(open('audit/data/classified_domains.json'))
BRIEF=["listique.org","topbizdir.com","zynatee.com","theinfosynth.com","onepluslisting.com","true-listings.com","lookuplists.com","getdirectory.org","localstudio.info","honestdir.com","localbusinessfinder.co","listingcenter.org","thelistingmatrix.com","directoryology.com","myreallistings.com","selectbusinesszone.com","thedirectopia.com","ackoona.org","listingsspot.com","premiuminc.org","businesslistingforall.com","5starlocalcenter.com","bestlocalcenter.com","ideal-listings.com","ultimatesites.info","thelistingcloud.net","directoryninja.org","weblistings.info","yourpremium.org","godigitalbusinesshub.com","directorycentered.com","findbusinesses.org","rozzbee.com","busineessupdir.com","topincitylocal.com","probusinessworld.com","findlocalcenter.com","getzzby.com","businessinfoseek.com","a-zbusinesses.com","easybusinessdirect.com","woorivo.com","localbusinessesdir.com","showmelocalpro.com","localbusinessguide.org","populardirectory.co","directorist.net","snapsearch.org","seekbump.org","yellowmarketplaces.com","directoryview.com","localdirectory247.com","atozweb.org","localpagesdirectory.com","searchknock.com","getlistedahead.com"]
# 1. all 56 held?
bad=[(d,D[d]['status']) for d in BRIEF if d in D and not D[d]['status'].startswith('Held')]
missing=[d for d in BRIEF if d not in D]
print("56 brief domains NOT Held:", bad or "none")
print("56 brief domains missing from classification:", missing or "none")
# 2. false negatives: Keep/Held domains with a dofollow PBN/offtopic anchor
PBN=re.compile(r'premium seo backlink|buy backlink|dofollow backlink|pbn network|da ?\d{2}|increase your domain|whatsapp us|high quality .*backlink|link building|higher google ranking', re.I)
rows=list(csv.reader(io.StringIO(open('audit/data/classified_links.csv').read())))
h={c:i for i,c in enumerate(rows[0])}
fn=[]
for r in rows[1:]:
    st=r[h['status']]; nf=r[h['nofollow']]=='True'; a=r[h['anchor']]
    if st.startswith(('Keep','Held')) and (not nf) and PBN.search(a or ''):
        fn.append((r[h['referring_domain']], st, a[:50]))
print("FALSE-NEGATIVE candidates (Keep/Held + dofollow PBN anchor):", len(fn))
for x in fn[:15]: print("   ", x)
# 3. Spam(Disavow) with no dofollow (should be 0) and evidence present
dis=[d for d,v in D.items() if v['status']=='Spam (Disavow)']
nodof=[d for d in dis if D[d]['dofollow']==0]
print("Spam(Disavow) with 0 dofollow links (must be 0):", len(nodof), nodof[:10])
# 4. Keep domains that are spam-flagged (review list size)
keepspam=[d for d,v in D.items() if v['status']=='Keep' and v['spam_flag']]
print("Keep but Ahrefs-spam-flagged (needs human eyeball):", len(keepspam))
print("   examples:", keepspam[:20])
