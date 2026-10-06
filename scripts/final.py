import csv, sys, collections, re, json, datetime
def rd(p,d='\t'):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=d, quotechar='"'))
BL,RDM,SEM,LRAW=sys.argv[1:5]
bl=rd(BL); rdm=rd(RDM); sem=rd(SEM,';')
raw=[l.rstrip('\n').split('\t') for l in open(LRAW,encoding='utf-8',errors='replace') if l.strip()]
def host(u):
    m=re.match(r'https?://([^/]+)', u or '')
    h=m.group(1).lower() if m else ''
    return h[4:] if h.startswith('www.') else h
for r in bl: r['_h']=host(r['Referring page URL'])
drmap={r['Domain'].lower():(r['DR'] or '0') for r in rdm}
ahr_all={r['Domain'].lower() for r in rdm}
spamdom={r['Domain'].lower() for r in rdm if r['Is spam']=='true'}
byd=collections.defaultdict(list)
for r in bl: byd[r['_h']].append(r)
cand={r['_h'] for r in bl if r['Is spam']=='true' and r['Nofollow']=='false'}
FP={'brandfetch.com':'brand-asset directory, auto-indexes every domain; editorial-neutral aggregator',
 'prospeo.io':'B2B email-format lookup, auto-indexes every company',
 'clientsbee.com':'tech-stack lookup page, auto-generated for every domain',
 'prosgrade.com':'consumer reviews aggregator with correct Alpharetta GA geography',
 'missfrugalmommy.com':'genuine editorial how-to article (Article > How-to), in-copy citation',
 'hghomeclub.com':'podcast episode page featuring the business by name',
 '100xrecruiting.com':'jobs/company profile listing',
 'nearmelisting.com':'local reviews listing, correct Decatur GA geography',
 'struvia.co':'subcontractor profile carrying the real phone number (770) 888-1604',
 'robuta.com':'search-engine SERP mirror for "marietta georgia"'}
# ---- tiers
T1=sorted({r['_h'] for r in bl if 'quality-authority-backlinks-148096' in r['Referring page URL'] and r['Nofollow']=='false'})
T2=sorted({r['_h'] for r in bl if 'Premium PBN Network Service' in r['Anchor'] and r['Nofollow']=='false'})
T3=sorted({r['_h'] for r in bl if r['Anchor'].startswith('Trusted High DA Backlinks for ngwindows.com') and r['Nofollow']=='false'})
AGED=[r for r in bl if ('aged domains and backlinks' in r['Referring page title'].lower() or re.search(r'Top Domains . Page 168196', r['Referring page title'])) and r['Nofollow']=='false']
T4=sorted({r['_h'] for r in AGED})
T5=['whosmypro.com','homeownerideas.com']
for s in (T1,T2,T3,T4): assert not (set(s)&set(FP))
used=set(T1)|set(T2)|set(T3)|set(T4)|set(T5)
# Semrush-only strict
NG=re.compile(r'(?<![A-Za-z0-9-])(?:https?://)?(?:www\.)?ngwindows\.com', re.I)
VEND=re.compile(r'backlink|pbn|dofollow|domain rating|domain authority|guest post|niche edit|seo|google visibility|rankings?', re.I)
rawd=collections.defaultdict(list)
for row in raw:
    if len(row)>=4: rawd[host(row[0])].append(row)
semd={r['domain'].lower() for r in sem}
T6={}
for d in sorted(semd-ahr_all):
    s=[r for r in rawd.get(d,[]) if r[2]=='false' and NG.search(r[1]) and VEND.search(r[1])]
    if s: T6[d]=s
def ev(h):
    rows=byd.get(h,[]) or byd.get('www.'+h,[])
    df=[r for r in rows if r['Nofollow']=='false']
    return (df or rows)[0], len(df)
out=[]
W=out.append
today='2026-10-06'
W(f"""# ==========================================================================
# DISAVOW v2 - ngwindows.com   (REBUILD ON AHREFS EVIDENCE)
# Built {today}. Supersedes nothing automatically - for reconciliation only.
# DO NOT UPLOAD until reconciled against disavow-ngwindows.txt / FINAL-AUDIT.md.
# ==========================================================================
#
# EVIDENCE BASE
#   Ahrefs live backlinks export : 2,665 links / 1,357 referring domains
#   Semrush refdomains + links_raw: 1,232 domains / 3,499 anchor rows (commit 6f5f407)
#   Tool overlap: 338 domains. Semrush-only 894. Ahrefs-only 1,019.
#   APIs unavailable (Semrush ERROR 132; Ahrefs Site Explorer locked to 2026-10-25),
#   so NOTHING below was re-fetched live. All evidence is from the committed exports.
#
# DISAVOW GROUNDS USED (per the standing constraint, NO authority-based grounds):
#   (a) observed manipulative anchor text naming ngwindows.com in link-vendor copy
#   (b) observed dofollow (PageRank-passing) status on that link
#   (c) structural fingerprint: byte-identical page path / campaign ID / page-ID
#       replicated across otherwise unrelated hosts
#   (d) link-selling domain character stated in the referring page's own title
#   (e) Ahrefs' own `Is spam` classification - corroborating only, NEVER the sole ground
#
# EXPLICITLY NOT USED AS GROUNDS ANYWHERE IN THIS FILE:
#   Domain Rating, Authority Score, traffic, thin content, TLD, country, hosting IP,
#   subnet clustering. No entry below depends on any of them.
#
# COVERAGE AND WHAT IS UNVERIFIED
#   VERIFIED: every entry has at least one quoted anchor/title/path from a committed
#     export, and dofollow status read from that export's own Nofollow column.
#   UNVERIFIED: no page was fetched or rendered at build time; link liveness is as of
#     each export's Last-seen date, not today. Semrush rows carry no target_url column,
#     so Semrush-side entries are evidenced by anchor text naming ngwindows.com only.
#   NOT COVERED: 894 Semrush-only domains minus the {len(T6)} listed here have no anchor
#     evidence naming ngwindows.com and are deliberately excluded (default-to-exclusion).
#
# TOTAL ENTRIES: {len(T1)+len(T2)+len(T3)+len(T4)+len(T5)+len(T6)}
# ==========================================================================
""")
def sec(title, body): W(title); W(body)
# T1
r0=byd[T1[0]][0]
W(f"""
# ==========================================================================
# SECTION 1 - STRONGEST. Vendor campaign 148096, direct-named, dofollow.
# {len(T1)} domains / 516 links.
# Grounds (a)+(b)+(c)+(e), all four present on every entry.
#   (a) anchor, byte-identical on all 516 links:
#       "Increase Google Visibility with High Quality Backlinks ngwindows.com"
#   (b) Nofollow=false on all 516.
#   (c) path, byte-identical on all 516 across 258 unrelated hosts:
#       /dir/quality-authority-backlinks-148096
#       (1 unique path, 1 unique page title across the whole cluster - a single
#        vendor campaign ID mirrored onto 258 throwaway hosts)
#   (d) referring page title states the business: "High Quality SEO Link Building
#       Experts Helping Websites Gain Powerful Backlinks..."
#   (e) Ahrefs Is spam=true on 258/258.
# This is the same cluster the prior Semrush pass found; Ahrefs independently
# confirms it and raises the domain count from 87 to 258.
# ==========================================================================
""")
for h in T1: W(f"domain:{h}")
# T2
W(f"""
# ==========================================================================
# SECTION 2 - PBN service pages, direct-named, dofollow. {len(T2)} domains / 90 links.
# Grounds (a)+(b)+(d)+(e).
#   (a) anchor: "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network
#       Service ngwindows.com Rank First Page Google" - the anchor itself advertises
#       a PBN and names the target.
#   (b) Nofollow=false on all 90.
#   (d) page titles are link-vendor sales copy, e.g.
#       "Proven PBN Backlinks to Increase Trust Flow. Drive Qualified Visitors."
#       "Trusted PBN Backlinks to Improve Citation Flow."
#       and the recurring literal title: "Boost your Google rankings with Premium
#       PBN & Link Building" (22 hosts share this exact title; 18 share the exact
#       path /all/2066/26.html - structural fingerprint (c) on that subset).
#   (e) Ahrefs Is spam=true on all.
# ==========================================================================
""")
for h in T2: W(f"domain:{h}")
W(f"""
# ==========================================================================
# SECTION 3 - "High DA backlinks" vendor pages, direct-named, dofollow.
# {len(T3)} domains / 28 links. Grounds (a)+(b)+(d)+(e).
#   (a) anchor: "Trusted High DA Backlinks for ngwindows.com to Raise Domain
#       Rating. Improve Google Rankings, Across Every Niche and Market."
#   (b) Nofollow=false on all 28.
#   (d) titles are the same generated vendor-copy family as Section 2, e.g.
#       "Trusted White Hat SEO Links to Raise Domain Rating."
#       "Effective Niche Edit Links to Boost Domain Authority."
#   (e) Ahrefs Is spam=true on all.
# ==========================================================================
""")
for h in T3: W(f"domain:{h}")
W(f"""
# ==========================================================================
# SECTION 4 - Aged-domain / backlink marketplace listings, dofollow.
# {len(T4)} domains / {len(AGED)} dofollow links.
# Grounds (b)+(c)+(d). AHREFS' FLAG IS NOT THE GROUND HERE - it flagged only
# 9 of these 26; the other 17 are included on (c)+(d) alone, independently of it.
#   (d) the referring page's own title states it sells links:
#       "Where to buy aged domains and backlinks" / "Top Domains - Page 168196"
#   (c) two page-IDs are replicated byte-for-byte across unrelated hosts:
#         /page-34962c4ce6e04e66bc6683ce26dd6c07.html  (ID 3496-2460, 16 hosts)
#         /61a37460a2eed245244c9bc59896bc7b-l/         (ID 6137-4602, 8 hosts)
#       Left/right context shows ngwindows.com sitting inside a scraped
#       alphabetical domain list: "ngwind.com ngwindow.com | ngwindows.com |
#       ngwindsong.com ngwindsongk.com" - an inventory listing, not a citation.
#   (b) Nofollow=false on every link counted here.
# NOTE FOR THE REVIEWER: this is a weaker-MOTIVE tier (the operator is selling
# domains, not necessarily boosting ngwindows.com) but the behavioural evidence
# is strong. It is the cleanest section to drop wholesale if you want to.
# ==========================================================================
""")
for h in T4: W(f"domain:{h}  # DR={drmap.get(h,'?')} Ahrefs-spam={'yes' if h in spamdom else 'NO (included on fingerprint+title only)'}")
W(f"""
# ==========================================================================
# SECTION 5 - Auto-generated directory injection, dofollow. 2 domains / 137 links.
# Grounds (b)+(c)+(e). These two are individually argued; read both before acting.
# ==========================================================================
domain:whosmypro.com
#   133 dofollow links from one DR-0.4 host. (c) structural fingerprint: 133
#   near-identical "Doors & Windows Near <CITY>, GA" pages (Druid Hills, Peachtree,
#   Acworth, Austell, ...) each carrying the same anchor "- Go to company website"
#   to the same target. City-permutation doorway pages, not 133 editorial mentions.
#   Page type "Listing collection > Business". (e) Ahrefs Is spam=true.
#   CHALLENGEABLE: legitimate local directories also build city pages. The
#   distinguishing facts are the volume (133 dofollow to one business) and that
#   every page is a permutation of one template.
domain:homeownerideas.com
#   4 dofollow links. (c) fabricated geography: the page title is "North Georgia
#   Replacement Windows Roswell NEW MEXICO - Home Owner Ideas Directory" for a
#   Georgia company. A directory that invents a location is generating listings
#   programmatically, not recording a real business. Anchor is the bare URL
#   "https://www.ngwindows.com/". (e) Ahrefs Is spam=true.
""")
W(f"""
# ==========================================================================
# SECTION 6 - SEMRUSH-ONLY. {len(T6)} domains Ahrefs has never crawled.
# Grounds (a)+(b) from links_raw.tsv (commit 6f5f407), which carries anchor and
# nofollow but NO target_url column. Each entry below has at least one row where
#   nofollow=false  AND  the anchor names ngwindows.com (word-boundary matched,
#   so "performingwindows.com" does NOT count) inside link-vendor copy.
# These cannot be corroborated by Ahrefs because Ahrefs does not list the domain
# at all - absence of Ahrefs evidence here is absence of coverage, not exoneration.
# Format: domain  # <dofollow rows> | <quoted anchor>
# ==========================================================================
""")
for d in sorted(T6):
    a=T6[d][0][1].replace('\t',' ')[:96]
    W(f'domain:{d}  # {len(T6[d])} dofollow | "{a}"')
# ---------- NOT DISAVOWED ----------
hi=[(h,drmap.get(h,'0')) for h in (T1+T2+T3+T4+T5) if float(drmap.get(h,'0') or 0)>=30]
W(f"""
# ==========================================================================
# NOT DISAVOWED - deliberate exclusions, with counts and reasons
# ==========================================================================
#
# [1] 1,129 Ahrefs links that are Is spam=true but Nofollow=TRUE.
#     Reason: nofollow passes no PageRank. Disavowing them changes nothing and
#     inflates the file. This is where nearly all the high-authority spam lives:
#     of 632 spam-flagged domains at DR>=30, only 7 have ANY dofollow link.
#     Largest excluded nofollow networks, each with a clean fingerprint:
#       577 hosts sharing the path /after-years-of-struggling-with-low-engagement-
#            i-found-seoexpresscom-... (the "SEOExpress.org" testimonial network,
#            DR 44-52, anchor "There was a time when ngwindows.com struggled...")
#        65 hosts sharing /ysh5qk2-what-29-campaigns-built-local-citations-...
#        24 hosts titled "Directory Pages Index"
#        19 hosts sharing /bibiacseo/ ; 15 /buytfnseo/ ; 15 /ashgeoseo/
#        11 hosts titled "Domain Report" / "Website Stats" (/report/97119-20,
#            /stats/97119-20) ; 3 hosts "Dark Side Links - Dark/White Hat Link
#            Building Services"
#     Topically impossible injections also excluded here BECAUSE they are nofollow:
#       intermeritocracy.com  "Thriving Economy of China" -> anchor "Window
#                             Replacement Company Atlanta" (6 links)
#       monetaryhistoryofworld.com  "Monetary History of the World, 1154-1470"
#                             -> anchor "Windows Atlanta" (12 links)
#       worldbusinesspromote.com  "Makita: A Global Leader in Power Tools" (4)
#       marketingexperts.click  "Artie Lange: Laughter, Pain..." (2)
#       dreamscometroup.com   blog comment page 41 (1)
#     If you later want a belt-and-braces file, these five are the first additions:
#     their evidence is behaviourally the strongest in the whole dataset.
#
# [2] 10 Ahrefs-flagged DOFOLLOW domains judged FALSE POSITIVES of Ahrefs'
#     classifier. Excluded because no manipulative behaviour is observable:""")
for d,why in sorted(FP.items()): W(f"#       {d:22s} - {why}")
W(f"""#
# [3] 218 domains with Ahrefs Is spam=false (the keep-list), incl. bbb.org,
#     crunchbase.com, glassdoor.com, yellowpages.com, expertise.com, fixr.com,
#     qualifiedremodeler.com, housedigest.com, moneytalksnews.com, dexknows.com.
#     Sanity-checked: 23 of them carry SEO-vendor vocabulary. 17 of those are the
#     aged-domain marketplace and WERE PROMOTED into Section 4 above. The other 6
#     (seo-high-ranking.shop, kawaiishop.shop, thehighseoranking.shop,
#      verified-digital-firm-seoexpress.store, revan-me.com, sblmerchant.com) are
#     link-vendor pages but every link is nofollow -> excluded under [1].
#     bizlistusa.com / businesslistus.com (shared path /business/5067660.htm,
#     3 hosts, dofollow) were checked and KEPT: correct Roswell GA geography,
#     ordinary subdomain city structure, image link with empty anchor.
#
# [4] 777 Semrush-only domains with no dofollow anchor naming ngwindows.com.
#     Excluded under default-to-exclusion. Many carry vendor anchors naming a
#     DIFFERENT target (ngawindows.com, roiwindows.com, performingwindows.com,
#     qualitypluswindows.com, thermalprowindows.com, northpointwindows.com,
#     thermatrustwindows.com). Those are not evidence against ngwindows.com
#     unless the redirect model holds - and see [5].
#
# [5] THE 14 REDIRECT SHELLS - NOT DISAVOWED, AND THE MODEL IS NOT CONFIRMED.
#     Ahrefs' export has a Redirect Chain URLs column. Across all 2,665 links it
#     contains exactly TWO third-party hosts, and NEITHER is a shell:
#       atlantabestmedia.com (22 links) - a local Atlanta awards/press site using
#         an outbound CLICK-TRACKER: https://atlantabestmedia.com/?post_id=12205
#         &goto=<token> -> 303 -> http://ngwindows.com/ -> 301 -> https://.
#         Is spam=false, dofollow, anchor "ngwindows.com", page "my-woodstock-
#         canton-best-of-2025". This is a tracked editorial link. KEEP.
#       bizhwy.com (5 links) - business directory interstitial:
#         https://www.bizhwy.com/visit.php?biz=7329&state=Georgia -> 302.
#         Is spam=false and NOFOLLOW. Passes nothing. KEEP.
#     The remaining 785 chains are ngwindows.com's OWN canonicalisation
#     (http->https, non-www->www; 759 are a single 301).
#     NONE of ngawindows.com, roiwindows.com, thermalprowindows.com,
#     qualitypluswindows.com, northpointwindows.com, performingwindows.com,
#     thermatrustwindows.com, northgeorgiawindows.net, thermalastwindows.com,
#     e2windows.com, choiceviewwindows.com, ngwindow.com, northgawindows.com or
#     northgeorgiawindow.com appears in ANY redirect chain in the Ahrefs export.
#     (ngwindow.com's 49 raw string hits are all alphabetical domain-list context
#     on the Section 4 marketplace pages; qualitypluswindows.com's single hit is
#     a URL path segment on justgotlive.com.)
#     => The prior pass's "279 redirect-borne dofollow domains" has NO support in
#     Ahrefs data. Either the shells do not 301 into ngwindows.com, or Ahrefs does
#     not credit shell-borne links to it. Unresolved; do not act on it from here.
#
# ==========================================================================
# HIGH-DR SPAM - the entries a reviewer will challenge hardest
# Only {len(hi)} of the {len(T1)+len(T2)+len(T3)+len(T4)+len(T5)} Ahrefs-side entries are DR>=30. DR is NOT the reason any
# of them is listed; they are listed on the quoted evidence below. Stated here
# only so the reviewer is not ambushed.
# ==========================================================================""")
for h,d in sorted(hi,key=lambda x:-float(x[1])):
    r,n=ev(h)
    W(f"#   {h} (DR {d}) - {n} dofollow link(s)")
    W(f"#     page : {r['Referring page URL'][:100]}")
    W(f"#     title: \"{r['Referring page title'][:92]}\"")
    W(f"#     anchor: \"{r['Anchor'][:100]}\"")
    W(f"#     ground: (a) anchor names ngwindows.com in PBN/link-vendor copy; (b) dofollow;")
    W(f"#             (d) page title is vendor sales copy; (e) Ahrefs Is spam=true. Not DR.")
W("""#
#   Also note: domains.com.bz (DR 28) in Section 4 is the highest-DR entry there;
#   its ground is the shared page-ID fingerprint and the title "Top Domains -
#   Page 168196", identical to itsyourgold.com (DR 0). Same page, two hosts.
#
# END OF FILE
""")
open('/home/user/test/backlink-audit/disavow-v2-ahrefs.txt','w').write('\n'.join(out)+'\n')
print("sections:",len(T1),len(T2),len(T3),len(T4),len(T5),len(T6),"TOTAL",len(T1)+len(T2)+len(T3)+len(T4)+len(T5)+len(T6))
print("highDR:",hi)
json.dump(dict(T1=T1,T2=T2,T3=T3,T4=T4,T5=T5,T6=sorted(T6)),open('/home/user/test/backlink-audit/work-v2/final_tiers.json','w'),indent=0)
