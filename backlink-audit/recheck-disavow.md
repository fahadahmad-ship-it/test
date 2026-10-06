# Re-check of disavow-ngwindows.txt — adversarial review
**Date:** 2026-10-06 · **Reviewer:** independent pass · **File under review:** `/home/user/test/backlink-audit/disavow-ngwindows.txt` (33 `domain:` lines)

## 0. Headline

Three structural errors, in order of consequence:

1. **The evidence base was never exhausted.** The prior pass states anchor/dofollow evidence
   "was retrievable for 73 of 1,232 referring domains (5.9%)" and builds the whole file around
   that scarcity. `links_raw.tsv` actually holds **3,499 anchor+nofollow rows covering 878
   distinct referring domains (71.3%)**. The scarcity premise is false, and every count derived
   from it is wrong.
   *(Note: the file is at `git show 6f5f407:backlink-audit/work/links_raw.tsv`, not `469162b` as briefed.)*
2. **Section 2 (28 entries) fails the file's own criterion-2 gate.** Every one of those entries
   is either **100% nofollow** in the raw data (14 entries) or **absent from the raw data
   entirely** (14 entries). Not one has a single dofollow link. The file declares "nofollow links
   are NEVER disavowed"; Section 2 violates that rule 28 times out of 28. **Remove all 28.**
3. **Section 1 is right but 17x too small.** The direct-target cluster
   `/dir/quality-authority-backlinks-148096` has **87 distinct dofollow domains**, not 5. The
   prior pass saw 5 because its single Semrush page only sampled 5. **Add 87 domains.**

**Recommended file: 92 entries** (5 kept + 87 added, 28 removed). The current 33-entry file is
**not submittable**: ~85% of its lines are unsupported and ~94% of the qualifying evidence is missing.

Internal arithmetic error, separately: the file's own footer says "TOTAL DISAVOW ENTRIES: 34"
and the inventory says 34, but the file contains **33** `domain:` lines. Section 2's header
claims "all 27 resolve to the SAME host" while only **26** such lines exist.

---

## 1. Per-entry verdict — all 33

Method: for each entry, every row in `links_raw.tsv` whose source host matches was extracted.
Column 3 is `nofollow`; `false` = dofollow. "Grounds hold" is judged against the file's own
stated criteria, not against authority.

### Section 1 — criterion 1 (5 entries)

| # | Domain | Rows | Dofollow | Slug fingerprint | Anchor | Verdict |
|---|---|---:|---:|---|---|---|
| 1 | backlinksseochecker.space | 4 | 4 | `/dir/quality-authority-backlinks-148096` | "Increase Google Visibility with High Quality Backlinks ngwindows.com" | **KEEP — fully verified** |
| 2 | dapaseochecker.online | 2 | 2 | same | same | **KEEP — fully verified** |
| 3 | onlinewebsitechecker.space | 2 | 2 | same | same | **KEEP — fully verified** |
| 4 | seostrengthchecker.online | 1 | 1 | same | same | **KEEP — fully verified** |
| 5 | siteseocheckerfree.store | 2 | 2 | same | same | **KEEP — fully verified** |

All five reproduce exactly as documented: dofollow, identical vendor sales-copy anchor naming
ngwindows.com, shared path slug with shared numeric id. Section 1 is sound. Their Ahrefs DR is
0.0 across the board — correctly irrelevant and correctly not cited as grounds.

### Section 2 — criterion 3 + co-hosting (28 entries)

| # | Domain | Rows in raw | Dofollow | Observed anchor | Verdict |
|---|---|---:|---:|---|---|
| 6 | 99backlinksbuy.com | 3 | **0** | `ngwindows.com` (bare) — all nofollow | **REMOVE — fails dofollow gate** |
| 7 | allbaclinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 8 | atozbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 9 | bestrankbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 10 | bestseobacklinkforsite.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 11 | bestsitesbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 12 | booastrankingwithbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 13 | buyfairbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 14 | buyrankbacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 15 | buytopqualitybacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 16 | clicktobuybacklinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 17 | eliteseobacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 18 | friendlybacklinksbuy.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 19 | goooogla.com | 26 | **0** | bare URL anchors, all nofollow | **REMOVE — see 2.1** |
| 20 | increasewebtrafficwithlinks.com | 3 | **0** | bare, nofollow | **REMOVE — fails dofollow gate** |
| 21 | quickseolinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 22 | rarebacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 23 | superbqualitybacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 24 | topratedbacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 25 | trafficboosterlinkseo.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 26 | viralbacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 27 | webbacklinkskbuy.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 28 | webrankingsolutionbacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 29 | welinkbacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 30 | worldtopbacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 31 | wowqualitybacklinks.com | **0** | 0 | none | **REMOVE — no evidence of any link** |
| 32 | best-seo-domains.com | 12 | **12** | see 2.2 | **REMOVE (qualified)** |
| 33 | backlinks-checker.com | 11 | **0** | all nofollow | **REMOVE — fails dofollow gate** |

**Answering the brief's question directly — "are those 28 actually linking to ngwindows.com at
all, and dofollow?"** Half of them (14) do not appear in the raw link data at all. The other
half do link, but **every single link is `rel=nofollow`**. Across all 28 entries there are
**78 observed link rows and zero dofollow rows** — except `best-seo-domains.com`, discussed below.

The file's own text says criterion 2 is a gate, not a ground: *"nofollow links are NEVER
disavowed — they pass no PageRank and cannot be the mechanism of a link penalty."* Section 2
is excluded by the file's own rule. The name-character criterion (3) cannot rescue it, because
criterion 3 was written to catch *"high-DR sellers that use benign bare-URL anchors"* — i.e. it
substitutes for the *anchor* test, never for the *dofollow* gate.

---

## 2. False positives to REMOVE

### 2.1 goooogla.com — remove; two of its three stated grounds are factually false

The file flags this as "CRITERION 4 (co-hosting)" and self-identifies it as weak. It is weaker
than stated:

- **Grounds 1 — co-hosting.** Not admissible under the user's standing constraint, and the file
  already concedes it.
- **Grounds 2 — "Ahrefs DR 60".** **False.** Live free-endpoint check returns **DR 29.0**. This
  also breaks the Section 2 header's central fingerprint claim of "a uniform DR block across 27
  unrelated registrations" — the block is not uniform, and the one domain the file admits is not
  a seller by name is also the one that is not DR 60. The "uniform DR" pattern was an artifact of
  not checking the outlier.
- **Grounds 3 — "35 links".** Raw data shows **26 rows, 100% nofollow**, anchors are bare URLs
  (`ngwindows.com`, `https://roiwindows.com/`, etc.) — i.e. the file's own "benign anchors
  observed / not disavowed" category.

Every independent ground fails. **REMOVE.**

### 2.2 best-seo-domains.com — remove, but this is the one judgement call

It is the only Section 2 entry with dofollow links (12/12 dofollow). However:

- Its grounds in the file are name-character + co-hosting + DR. DR is inadmissible; co-hosting is
  inadmissible; so only name-character remains.
- `best-seo-domains.com` is a **domain-marketplace / expired-domain** name, not a backlink-selling
  name. It does not match any of the enumerated patterns the file itself lists for criterion 3
  (`*backlink*`, `*buybacklinks*`, `*seolinks*`, `*dachecker*`, `*dapachecker*`, `*rankchecker*`).
  The file stretched its own criterion to fit it.
- Its 12 dofollow rows do **not** carry the shared-slug fingerprint, so criterion 1 is not met either.
  Their anchors are bare domain names (`ngwindows.com`, `roiwindows.com`, `thermatrustwindows.com` …)
  on paths of the form `/<8-char>-list/` — an expired-domain listing page. That is precisely the
  file's own **"NOT DISAVOWED — benign anchors observed"** category, which already exempts
  `domainsc.com`, `getonline.co.in` and `theface.in` on identical reasoning. Disavowing this one
  while exempting those three is internally inconsistent.

Under "default to exclusion", **REMOVE**. Flag it for re-examination after 2026-10-25 — it is the
single entry in the file that could legitimately come back.

### 2.3 Any entry that is or could be a real site

None of the 33 is a real business. All are machine-generated SEO-tool or link-seller registrations.
There are **no false positives of the "destroyed a genuine site" kind in the current file** — the
file's failure mode is the opposite one: it disavows harmless nofollow links and misses the
harmful dofollow ones.

DR bulk-check on the Section 2 block confirmed DR 59–60 for 19 of them, DR 42 for
`backlinks-checker.com`, DR 29 for `goooogla.com`. Reported for completeness only — **DR is not
used as grounds anywhere in this review.**

---

## 3. False negatives to ADD — 87 domains

This is the file's largest defect. The prior pass identified `/dir/quality-authority-backlinks-148096`
as the one direct-target cluster and listed **5** members. The raw data shows the slug carries
**112 dofollow rows across 87 distinct referring domains**, every one with the byte-identical
anchor. Plus a second, entirely unnoticed source (§3.2).

### 3.1 Qualifying test applied

Strict criterion 1, no relaxation:
`nofollow == false` **AND** vendor sales-copy anchor naming **ngwindows.com itself** (not a
redirect shell) **AND** shared structural fingerprint (shared `/dir/` slug + numeric id, or a
shared Network-B selling-path segment + 6-hex id).

Result: **92 domains** qualify. 5 are already in the file. **87 are missing.**

All 87 were cross-checked and are present in `refdomains.csv`. None collides with the PROTECTED list.

### 3.2 Two slug clusters and one network the prior pass never found

Grepping `/dir/` slugs in the raw data returns **eight** clusters; the inventory documents **six**:

| Shared slug | Dofollow rows | Distinct domains | Anchor target | In prior audit? |
|---|---:|---:|---|---|
| /dir/professional-seo-links-148030 | 181 | 138 | ngawindows.com (shell) | yes (as 10 domains) |
| /dir/backlink-seo-experts-211287 | 156 | 127 | thermalprowindows.com (shell) | yes (as 15) |
| /dir/seo-ranking-links-170322 | 148 | 117 | qualitypluswindows.com (shell) | yes (as 10) |
| /dir/ethical-seo-backlinks-160633 | 147 | 116 | performingwindows.com (shell) | yes (as 9) |
| /dir/trusted-seo-backlinks-150104 | 138 | 96 | northpointwindows.com (shell) | yes (as 10) |
| **/dir/quality-authority-backlinks-148096** | **112** | **87** | **ngwindows.com — DIRECT** | yes (as **5**) |
| **/dir/authority-focused-backlinks-178285** | **88** | **63** | roiwindows.com (shell) | **NO — missed entirely** |
| **/dir/manual-link-building-services-211290** | **41** | **31** | thermatrustwindows.com (shell) | **NO — missed entirely** |

The two new clusters target shells, so they belong in the "delete the redirect" section, not the
disavow set — but their omission means the remediation section is also materially incomplete.

**Network B** is likewise understated: the inventory names 7 domains; the raw data shows
**43 distinct dofollow domains** across the eight selling-path segments, of which **5 name
ngwindows.com directly** and are included in the 87.

### 3.3 The 87 additions, each with its justifying raw-data line

Pattern for the 82 `/dir/` members — identical for all, differing only in host:

```
https://<DOMAIN>/dir/quality-authority-backlinks-148096	Increase Google Visibility with High Quality Backlinks ngwindows.com	false	0
```
e.g. `https://100ranking.com/dir/quality-authority-backlinks-148096 \t Increase Google Visibility with High Quality Backlinks ngwindows.com \t false \t 0`

```
domain:100ranking.com
domain:100ranking.link
domain:1seoservices.com
domain:1seoservices.info
domain:7-seo.com
domain:7-seo.link
domain:advanced-seo.com
domain:backlinkanalyzer.site
domain:backlinkcheckersite.store
domain:backlinkfindertool.shop
domain:backlinkfreeseo.com
domain:backlinkfreeseo.link
domain:backlinkgenerator.org
domain:backlinkindia.link
domain:backlinkmaker.info
domain:backlinkmaker.link
domain:backlinkocean.info
domain:backlinksboost.com
domain:backlinksboost.info
domain:backlinkscheckersite.space
domain:backlinksindia.com
domain:backlinksindia.info
domain:backlinksindia.link
domain:backlinkspace.info
domain:backlinkspace.link
domain:backlinkspulse.com
domain:backlinkspulse.info
domain:bestseosuite.com
domain:blog-backlinks.com
domain:blogdachecker.website
domain:bulkbacklinkreport.space
domain:competitorchecker.store
domain:daandpacheckerfree.shop
domain:dacheckeronline.shop
domain:dacheckerseo.store
domain:dadpchecker.online
domain:dadpchecker.site
domain:darankingchecker.site
domain:diversifiedseo.com
domain:domainauthority.website
domain:domainlinkprofile.site
domain:drchecker.site
domain:drchecker.store
domain:findbacklinks.website
domain:freebulkdachecker.shop
domain:freerankcheckertool.shop
domain:geobacklinks.link
domain:getseotips.link
domain:go4seo.com
domain:go4seo.info
domain:gofreebacklinks.info
domain:goldbacklinks.com
domain:goldbacklinks.info
domain:goodbacklinkchecker.website
domain:liveserpchecker.website
domain:marketsseo.com
domain:massdachecker.website
domain:onlineseochecker.website
domain:perfectwebseo.com
domain:proseobacklinks.link
domain:rankcheckerseo.online
domain:rankingschecker.site
domain:seo-asia.link
domain:seo-enterprise.com
domain:seo-expert-1.com
domain:seocheckerforfree.site
domain:seocheckerrank.site
domain:seofastranks.com
domain:seorankingschecker.online
domain:seostrengthchecker.site
domain:seotoolslike.com
domain:seowebsitechecker.site
domain:seozens.com
domain:serprankingchecker.site
domain:stormbacklink.com
domain:technicalseochecker.space
domain:thebulkdachecker.website
domain:urlbacklinkchecker.store
domain:websiteauditchecker.space
domain:websitepageschecker.space
domain:websiterankchecker.space
domain:websiterankchecker.website
```

The remaining 5 are Network B, each with its own raw line:

```
domain:daechul.co.com
  https://daechul.co.com/niche-relevance-hub/powerful-manual-outreach-backlinks-to-raise-domain-rating-...-388dd7.html	Trusted High DA Backlinks for ngwindows.com to Raise Domain Rating. Improve Google Rankings, Across Every Niche and Market.	false	0
domain:drobo.shop
  https://drobo.shop/guest-post-network/professional-tiered-link-building-to-raise-domain-rating-...-80e33e.html	Trusted High DA Backlinks for ngwindows.com to Raise Domain Rating. ...	false	0
domain:fittyfoody.com
  https://fittyfoody.com/link-building-hub/effective-manual-outreach-backlinks-for-higher-da-and-dr-scores-...-371323.html	High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service ngwindows.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap	false	0
domain:ggmap.us.com
  https://ggmap.us.com/guest-post-network/proven-guest-post-service-designed-to-improve-da-dr-and-tf-...-91e10d.html	Trusted High DA Backlinks for ngwindows.com to Raise Domain Rating. ...	false	0
domain:s-tribe.net
  https://s-tribe.net/crawl-index-network/effective-dofollow-link-building-for-higher-da-and-dr-scores-...-8eddff.html	High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service ngwindows.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap	false	0
```

**Caveat on these 5, stated plainly.** `daechul.co.com` (DR 91) and `ggmap.us.com` (DR 92) sit on
the shared `co.com` / `us.com` registry suffixes, so their DR is inherited from the registry parent
and means nothing about the host. `fittyfoody.com` (DR 10) and `s-tribe.net` (DR 3.2) may be real
sites carrying an injected or sold placement. In all five cases the *link* is evidenced vendor
sales copy at dofollow, so criterion 1 is satisfied and domain-level disavow is defensible — but
if you want to be surgical, these five are the candidates for page-level (`http://...`) rather than
`domain:` lines. The other 82 are pure vendor registrations with no such ambiguity.

### 3.4 Answering "360 carry the naming convention — for how many can you now find anchor evidence?"

Anchor evidence now exists for **878 of 1,232 referring domains (71.3%)**, not 73. Of the
previously "unverified" population, **366 distinct domains** are now shown to carry a shared-slug
vendor anchor at dofollow. 87 of them name ngwindows.com directly (→ disavow); the remaining
~279 name a redirect shell (→ delete the redirect). The "1,159 excluded for insufficient
evidence" figure should be restated as roughly **354 genuinely unevidenced**.

---

## 4. PROTECTED list corrections

### 4.1 All 15 existing entries verified — keep every one

Each was checked against its actual anchor in the raw data. All are benign, and none carries a
vendor fingerprint:

| Domain | Observed anchor | Follow | Verdict |
|---|---|---|---|
| forsythcounty.com | "Visit website" | dofollow | genuine — **KEEP PROTECTED** |
| georgiashutters.com | "Vinyl Windows Atlanta" | nofollow | genuine local trade — **KEEP** |
| 1stcallglasscare.com | bare shell domains | dofollow | genuine glass trade — **KEEP** |
| alpharettatoprated.com | "Visit website" / "Website" | nofollow | genuine directory — **KEEP** |
| lombardohomegroup.com | "energy-efficient" | dofollow | genuine editorial — **KEEP** |
| windowdigest.com | full blog URL on ngwindows.com | dofollow | genuine industry — **KEEP** |
| homerenoworld.com | "North Georgia Replacement Windows" | dofollow | brand anchor — **KEEP** |
| athomepros.com | "https://www.ngwindows.com" | nofollow | genuine — **KEEP** |
| koalatyremodel.com | "North Georgia Replacement Windows" | dofollow | brand anchor — **KEEP** |
| atlantahomeimprovement.com | "ngwindows.com" / "www.ngwindows.com" | dofollow | genuine, DR 45 — **KEEP** |
| roswell365.com | "North Georgia Replacement Windows" | dofollow | hyperlocal — **KEEP** |
| members.williamsonchamber.com | "Visit Website" | dofollow | chamber — **KEEP** (note: not in `refdomains.csv`; it is a subdomain, the parent is the listed refdomain) |
| csswinner.com | empty anchor | nofollow | award directory, nofollow — **KEEP** |
| eurekster.com | no rows in raw data | — | no evidence either way — **KEEP** |
| factmags.com | see 4.2 | nofollow | **KEEP — and the open question is now closed** |

### 4.2 factmags.com — the open question is resolved, and not in its favour

The file protects it while flagging it as "the one protected entry that genuinely warrants a human
look", citing conflicting DR (60 vs 75) as the reason to exclude. Both halves of that reasoning
should be replaced:

- Live DR is **75.0**. There is no conflict; the DR-60 reading was wrong.
- Its 76 links sit on paths of the form `factmags.com/<6-char>seo/<brand>-best-seo-service/` —
  that **is** a selling fingerprint, and it is far stronger evidence than the co-hosting the prior
  pass relied on. Its anchors are bare shell URLs (`https://ngwindows.com/`, `https://roiwindows.com/`,
  `https://thermalprowindows.com/` …).
- **But every one of the 76 is `rel=nofollow`.**

So: keep it out of the disavow file, but **record the correct reason — it fails the dofollow gate**,
not "conflicting authority data". It should be moved from PROTECTED (which implies legitimacy) to
the existing **"NOT DISAVOWED — failed the dofollow gate"** section alongside `seo-rank-boost.shop`
and `seonix.agency`. It is not a legitimate site; it is a seller whose links happen to be harmless.
Nothing further is needed after 2026-10-25.

### 4.3 Genuine sites MISSING from PROTECTED — add 20

These all link to ngwindows.com with genuine editorial, brand or bare-URL anchors and carry no
vendor fingerprint. Several are exactly the DR 0–13 local businesses an authority sweep would
destroy — which is the stated purpose of the list. **The current PROTECTED list is less than half
the size it should be.**

| Domain | DR | Anchor | Character |
|---|---:|---|---|
| threebestrated.com | 80 | "ngwindows.com" | directory listing |
| fixr.com | 78 | "(ngwindows.com)" | home-services marketplace |
| brightside.me | 75 | "curtains" | editorial |
| moneytalksnews.com | 74 | "NG Windows" | editorial, brand anchor |
| qualifiedremodeler.com | 71 | "www.ngwindows.com" | **trade publication** |
| sitelike.org | 63 | "ngwindows.com" | similar-sites directory |
| **windowanddoor.com** | **62** | "North Georgia Replacement Windows Inc." | **industry trade publication — the single most on-topic link in the profile** |
| nerdymamma.com | 45 | "window replacement Nashville" | editorial |
| jeffslist.com | 38 | "View Website" | local directory |
| idyllicpursuit.com | 38 | "North Georgia Replacement Windows" | brand anchor |
| acraftedpassion.com | 34 | "casement window installation" | on-topic editorial |
| atlantaglow.org | 30 | "ngwindows-logo.png" | local, image link |
| angelaricardo.com | 28 | "window company, North Georgia Replacement Windows" | editorial |
| gnpmilton.com | 26 | "https://www.ngwindows.com/" | hyperlocal (Milton GA) |
| fairviewwindows.co.uk | 20 | full blog URL | industry peer |
| thehomefixitpage.com | 13 | "ngwindows.com/" | home improvement |
| fixthehome.com | 7 | "www.ngwindows.com/" | home improvement |
| candidmama.com | 4 | "new windows for your home" | editorial |
| crystalclearfl.com | 2.3 | "compare the best bids before hiring the right expert" | trade |
| hghomeclub.com | 0.1 | "North Georgia Replacement Windows" | local, brand anchor |

Also worth protecting on the same basis: `athomeinthefutureblog.com`, `crowdyhome.com`,
`disunplugged.com`, `contractorsnearme.ai`, `roswellartfestival.com` (DR 12, hyperlocal — same
class as the already-protected `roswell365.com`).

### 4.4 derchidoor.com — carried-forward note can be closed

The file asks to verify it (134 links, DR 18). It has **zero rows in `links_raw.tsv`** — no anchor
evidence either way. Under default-to-exclusion it stays out of the disavow file; there is nothing
further to verify from this dataset. DR confirmed at 18.0.

---

## 5. The 14-domain "DO NOT DISAVOW — delete the redirect" section

**Correct, and complete.** Verified two ways:

1. Extracting every `*window*.com|.net|.org` string appearing in any anchor across all 3,499 rows
   returns exactly 15 window-domain targets: ngwindows.com plus **the 14 listed shells**, and
   nothing else (the only other hits are `windowdigest.com`, `windowanddoor.com` and a
   `windowdoor-test.com` string, none of them shells). **There is no 15th shell.**
2. All 14 appear in `refdomains.csv` as referring domains in their own right, consistent with the
   301-shell reading. Link volumes by shell are heavily skewed — roiwindows.com (413 anchor
   mentions) and qualitypluswindows.com (401) down to northgawindows.com (33) — matching the
   cluster sizes.

The strategic call is right: these are operator-controlled assets, deleting the 301s severs the
links at source, and they should not be disavowed.

**Two corrections to the surrounding text:**

- **`domainlinkprofile.site` is misfiled.** It is listed under the 61 redirect-borne domains
  (`/dir/professional-seo-links-148030`, targeting the ngawindows.com shell) and therefore excluded
  from disavow. But it *also* carries a **direct dofollow link on
  `/dir/quality-authority-backlinks-148096` naming ngwindows.com**. Deleting the redirect will not
  remove that link. **Move it into the disavow set** (it is included in the 87 above). This is a
  general warning: redirect-borne and direct-borne are not mutually exclusive per domain, and the
  prior pass assumed they were.
- **The "61 redirect-borne domains" figure is a large undercount.** With the full raw data the
  redirect-borne population is roughly **279 distinct dofollow domains** across seven shell-targeted
  slugs — including the two clusters (`/dir/authority-focused-backlinks-178285` → roiwindows.com,
  63 domains; `/dir/manual-link-building-services-211290` → thermatrustwindows.com, 31 domains)
  that the prior pass never found at all. This does not change the remediation action — delete the
  redirects — but it does mean the client-facing impact estimate is understated by roughly 4.5x.

---

## 6. Recommended final file

| Action | Entries |
|---|---:|
| Current file | 33 |
| **REMOVE** — all of Section 2 (28 entries: 14 with zero dofollow links, 14 with no observed link at all) | −28 |
| **KEEP** — Section 1, fully verified | 5 |
| **ADD** — criterion 1 direct-target, each with a citable raw-data line | +87 |
| **Recommended total** | **92** |

Every one of the 92 rests on criterion 1 alone: observed vendor sales-copy anchor **+** observed
dofollow **+** shared structural fingerprint **+** anchor names ngwindows.com directly. **No entry
in the recommended file depends on Authority Score, Domain Rating, thin content, TLD, country,
hosting, or co-hosting.** The co-hosting criterion the prior pass smuggled in is not merely weak —
with anchor data in hand it turns out to select *exclusively* for nofollow links, i.e. it has
negative predictive value here. It should be struck from the methodology, not just de-weighted.

### Is the file submittable?

**No — do not submit the current file.** Submitting it would disavow 28 domains whose links are
all nofollow (no effect, but a documented departure from the file's own stated standard) while
leaving **87 evidenced dofollow PageRank-passing vendor links pointing straight at ngwindows.com
untouched**. It would be the wrong file in both directions.

After applying §2 and §3 the 92-entry file **is submittable** and every line is defensible from
`links_raw.tsv` without reference to any authority metric.

### Also fix before submission

1. Section 2's header claim "all 27 resolve to the SAME host … all return DR 59–60" — **both halves
   are wrong**: 26 lines, and goooogla.com is DR 29. Moot once Section 2 is deleted, but the same
   claim is repeated in `toxic-domain-inventory.md` §1 and §4 and should be corrected there.
2. The file footer and the inventory both say 34 entries; the file has 33.
3. The coverage statement ("5.9% anchor-verified, 94.1% unverified") is wrong and should read
   **71.3% anchor-verified (878 of 1,232)**. The "TO COMPLETE after 2026-10-25" section is largely
   moot — the data was already in the repository.
4. Expand the remediation section from 61 to ~279 redirect-borne domains and add the two missing
   slug clusters.
5. Move `factmags.com` from PROTECTED to "failed the dofollow gate" (§4.2).
6. Add the 20+ genuine sites in §4.3 to PROTECTED.

### Residual uncertainty, stated honestly

`links_raw.tsv` has no `target_url` / `redirect_url` column. Direct-vs-shell routing is inferred
from **which domain the anchor text names** — the same inference the prior pass used, and it is
consistent and unambiguous across all 112 rows of the direct cluster (one slug, one fixed anchor,
one named target). It is nonetheless an inference. Re-confirm with `redirect_url` after 2026-10-25.
If it turns out `/dir/quality-authority-backlinks-148096` also routes through a shell, those 87
move to the remediation section and the disavow file collapses to 5 — so **confirm this one field
before submitting** if you can wait until 25 October.
