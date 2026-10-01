# betterwaste.co.uk — KWR review & new keyword opportunities

**Date:** 1 October 2026 · **Market:** UK
**All keyword metrics (SV, KD, competitor Authority Score):** Semrush UK database. CPC is not included.
Ahrefs is used only for Domain Rating and indexed-URL evidence — no Ahrefs keyword difficulty is quoted.

---

## 1. Headline: the problem is not the keyword list, it's the pages

The mapping sheet is a reasonable list. But almost none of the pages it maps to are
actually competing — so adding more keywords to the same pages will not move revenue.

**betterwaste.co.uk, Semrush UK:**

| Metric | Value |
|---|---|
| Organic keywords | 341 |
| Est. organic traffic | 347/mo |
| Est. traffic value (Semrush) | $2,534/mo |
| Positions 1–3 | 3 |
| Positions 4–10 | 19 |
| Positions 11–20 | 26 |
| Positions 21–30 | 51 |
| Semrush Authority Score | 20 |

Where the sheet's own targets actually sit today (Semrush UK):

| Sheet keyword | Sheet SV | Semrush SV | Mapped page | Current position |
|---|---|---|---|---|
| dry mixed recycling | 2,400 | 2,400 | /dry-mixed-recycling-waste/ | **50** |
| dry mixed recycling bins | 320 | 1,000 | /dry-mixed-recycling-waste/ | **43** |
| commercial cardboard waste | 110 | 480 | /paper-and-cardboard-waste/ | **43** |
| commercial food waste disposal | 210 | 480 | /food-waste/ | **45** |
| commercial food waste | — | 390 | /food-waste/ | **60** |
| commercial glass waste | 210 | 210 | /glass-waste/ | **38** |
| commercial glass collection | not in sheet | 480 | /glass-waste/ | **30** |
| general waste management | 40 | 110 | /general-waste/ | **40** |
| business waste collection | — | 2,400 | /business-waste-collections/ | **26** |

Every waste-type page in the sheet is sitting in the 30–75 band. Those pages are
indexed but not competitive — thin content, no internal link equity, and (see §2)
in several cases competing against another page on the same site.

**Meanwhile the single biggest organic asset is a blog post, not a service page:**
`/top-10-commercial-waste-management-companies-in-the-uk/` ranks **4–8** for
`waste management companies` (1,300), `business waste management` (1,300),
`waste handling company` (720), `uk waste management companies` (210),
`commercial waste collection companies` (140) and ~15 more.
That page is a listicle that names competitors — it converts poorly and it is
currently doing the job a money page should be doing.

---

## 2. Structural problems found during the audit

These are worth more than any new keyword. Full list in `03-fix-list.csv`.

**a) The old Manchester page is still live and outranking the new one.**
`/areas-we-cover-old/manchester/` is ranking for the entire Manchester cluster —
`commercial waste collection manchester` (320) at **p20**,
`commercial rubbish collection near longsight manchester` (720) at p16,
`commercial waste manchester` (260) at p20, `business waste collection manchester`
(260) at p21, `manchester waste management` (170) at p26.
The sheet maps all of these to `/areas-we-cover/manchester/`, which is not ranking.
301 the `-old` URL to the new one. This alone should recover the Manchester cluster.

**b) www and non-www are both indexed.** Ahrefs sees two distinct URL sets:
`betterwaste.co.uk/polystyrene-and-recycling/` *and*
`www.betterwaste.co.uk/polystyrene-and-recycling`, same for
`/business-waste-collections`. Link equity and ranking signals are being split.
Fix canonicalisation.

**c) Cannibalisation on the core money term.** `business waste collection` (2,400) ranks with **both** `/business-waste-collections/` (p26) *and*
`/commercial-waste-management/` (p34). `commercial waste management companies`
ranks with both the blog (p7) and `/business-waste-collections/` (p90). Pick one
canonical money page per intent.

**d) `/areas-we-cover/` is absorbing national service terms it shouldn't own.**
It currently ranks for `business refuse collection` (590) at **p5**,
`waste collection for business` (320) p59, `commercial waste services` (260) p54, `industrial waste collection` (390) p83, `waste disposal companies`
(880) p63. A location hub is the wrong page for these — they need a national
commercial-waste service page.

**e) Mapping error in the sheet.** Rows 43–51 (the glass keywords) sit inside the
`/food-waste/` block. There is a live `/glass-waste/` page already ranking p30–38
for those terms. Re-map them.

---

## 3. Competitors — who is actually beating them, and on what

Semrush organic competitors (UK), sorted by relevance to betterwaste:

| Domain | Relevance | Common KWs | Organic KWs | Organic traffic | Authority Score |
|---|---|---|---|---|---|
| **businesswaste.co.uk** | 0.02 | 27 | 8,718 | 19,353 | 41 |
| **wastemanaged.co.uk** | 0.02 | 13 | 6,291 | 9,074 | 37 |
| **thefirstmile.co.uk** | 0.02 | 19 | 5,434 | 20,361 | 39 |
| **direct365.co.uk** | 0.01 | 14 | 7,369 | 12,827 | 32 |
| biffa.co.uk | 0.01 | 32 | 11,238 | 83,402 | 46 |
| suez.co.uk | 0.01 | 17 | 6,331 | 39,492 | 40 |
| veolia.co.uk | 0.00 | 26 | 34,744 | 176,463 | 48 |
| kennywastemanagement.co.uk | **0.13** | 11 | 451 | 4,920 | 27 |
| sensawaste.com | 0.09 | 14 | 1,285 | 1,319 | 24 |
| ashwasteservices.co.uk | 0.08 | 14 | 1,183 | 8,203 | 26 |
| bandmwaste.com | 0.07 | 12 | 1,299 | 6,929 | 29 |

**The realistic benchmark is businesswaste.co.uk and wastemanaged.co.uk**, not Biffa
or Veolia. Both are broker/aggregator models like Better Waste, both sit at
5,000–9,000 keywords vs Better Waste's 341. Biffa/Veolia/Suez are AS 40–48 asset
operators — not winnable head-on at AS 20.

**What businesswaste.co.uk ranks top-10 for that Better Waste has no page for at all:**

`commercial waste disposal` p5 (3,600) · `commercial waste collection` p5 (3,600) · `commercial waste management` p3 (2,400) · `commercial waste`
p6 (1,900) · `business waste disposal` p2 (1,300) · `commercial waste bins`
p8 (1,000) · `small business waste collection` p4 (880) ·
`commercial waste removal` p7 (590) · `clinical waste disposal` p6 (2,400) ·
`sanitary waste disposal` p3 (1,600) · `sanitary waste collection` p4 (1,300) ·
`hazardous waste` p8 (1,300) · `confidential waste bags` p7 (1,000) ·
`industrial waste management` p1 (1,000) · `industrial waste disposal` p2 (880) ·
`liquid waste management` p2 (590) · `construction waste removal` p5 (590) ·
`weee waste collection` p10 (1,000) · `waste carriers licence` p7 (1,600).

**What wastemanaged.co.uk ranks top-10 for in the same gap:**
`waste management` p1 (9,900) · `commercial food waste collection` p7 (720) ·
`construction waste management` p3 (720) · `care home waste management` p10 (480) ·
`dental waste` p9 (320) · `butchers waste collection` p4 (260) ·
`industrial waste disposal` p9 (880).

**The pattern is clear and repeatable.** Both competitors win on two axes
Better Waste has almost entirely skipped:

1. **Waste-stream pages beyond the five Better Waste has.** Clinical, hazardous,
 confidential, sanitary/hygiene, WEEE, industrial, construction, liquid.
2. **A city/borough page per location** (`/locations/waste-management-york/`,
 `/locations/dundee-waste-management/`, `/locations/waste-management-tewkesbury/`).
 Better Waste has ~8 location pages; businesswaste.co.uk has dozens, and they rank
 top-5 on high-value commercial terms.

---

## 4. New keyword opportunities not in the current sheet

Full list with metrics in `02-new-keywords.csv`. Summary by cluster, ranked by ROI.

### Cluster A — Core commercial service head terms (highest value, entirely absent from the sheet)

The sheet has **no row at all** for the terms that define this market. These are the
most commercially valuable terms in the vertical.

| Keyword | SV | KD |
|---|---|---|
| commercial waste collection | 3,600 | 25 |
| commercial waste disposal | 3,600 | 34 |
| commercial waste management | 2,900 | 33 |
| commercial waste | 1,600 | 26 |
| business waste disposal | 1,300 | 37 |
| trade waste | 1,300 | 26 |
| commercial waste bins | 880 | 44 |
| commercial recycling | 880 | 41 |
| small business waste collection | 720 | 34 |
| commercial bin collection | 720 | 33 |
| commercial waste removal | 590 | 29 |
| trade waste collection | 480 | 22 |
| office waste collection | 390 | 34 |
| commercial rubbish removal | 320 | 18 |
| business bin collection | 260 | 31 |
| commercial waste services | 260 | 52 |
| commercial bin hire | 170 | 28 |

**~20,000 SV.** Needs one strong national money page —
`/commercial-waste-collection/` — with `/commercial-waste-management/` consolidated
into it, internal links from the top-10 blog post, and the location hub de-optimised
for these terms.

### Cluster B — Missing waste streams (biggest competitive gap)

Better Waste covers general / DMR / paper & cardboard / food / glass. Competitors
cover 8–12 streams. Each missing stream is a page that converts.

| Keyword | SV | KD |
|---|---|---|
| confidential waste disposal | 3,600 | 25 |
| clinical waste disposal | 2,900 | 22 |
| weee recycling | 2,400 | 41 |
| clinical waste collection | 1,900 | 22 |
| hazardous waste disposal | 1,900 | 35 |
| clinical waste | 1,600 | 30 |
| sanitary waste disposal | 1,300 | **10** |
| sanitary waste collection | 1,300 | 17 |
| hazardous waste collection | 1,300 | 23 |
| confidential waste collection | 1,000 | **13** |
| confidential shredding | 1,000 | 16 |
| industrial waste disposal | 720 | 28 |
| construction waste disposal | 590 | 28 |
| electrical waste disposal | 590 | 24 |
| it equipment disposal | 590 | 37 |
| industrial waste collection | 390 | 41 |
| wood waste collection | 390 | **9** |
| used cooking oil collection | 320 | 15 |
| construction waste collection | 260 | 27 |
| metal waste collection | 260 | 24 |
| coffee cup recycling | 260 | 16 |

**~26,000 SV.** `sanitary waste collection` (KD 17) and
`confidential waste collection` (KD 13) are the standout ROI plays — low difficulty,
high commercial value, and Better Waste has no page.

> ⚠️ **One exclusion:** `bulky waste collection` (9,900, KD 21) looks tempting but the
> SERP is dominated by council pages and the intent is residential/free-council-collection
> — the ranking pages for `free bulky waste collection` are all local authorities.
> **Do not target.** Noted in the CSV as excluded with reason.

### Cluster C — Bin specification terms (fastest wins on the whole site)

`/binpedia/` already half-ranks here (`waste container` 1,900 at p39, `bin sizes`
590 at p49, `waste bin dimensions` 90 at p52). Breaking it into individual bin-size
pages is near-free traffic — every term is KD < 12.

| Keyword | SV | KD |
|---|---|---|
| 1100 litre bin | 720 | **8** |
| 660 litre bin | 720 | **8** |
| 240 litre bin | 590 | 11 |
| commercial wheelie bin | 320 | **8** |
| wheelie bin hire | 320 | 11 |
| eurobin | 260 | **9** |
| commercial bin sizes | 210 | **7** |
| 1100 litre bin dimensions | 90 | **6** |

**~3,200 SV at KD ≤ 11.** These are also strong mid-funnel assist pages — people
checking bin dimensions are shortlisting a supplier.

### Cluster D — Compliance & legislation (lead-gen + natural link bait)

| Keyword | SV | KD | Note |
|---|---|---|---|
| waste carriers licence | 4,400 | 38 | businesswaste ranks p7 |
| extended producer responsibility | 3,600 | 46 | |
| waste transfer note | 1,900 | 16 | low KD, high relevance |
| simpler recycling | 1,000 | 22 | **already p14 — quick win** |
| epr packaging | 320 | 34 | |
| duty of care waste transfer note | 320 | 20 | |
| waste duty of care | 170 | 29 | — | |
| simpler recycling regulations | 140 | 22 | |

`simpler recycling` at p14 on an existing page is the single cheapest win in this
document — a content refresh should take it top-10.

### Cluster E — Sector pages

Better Waste already has sector pages that are ranking p13–25 and just need pushing:

| Existing page | Keyword | SV | Current pos |
|---|---|---|---|
| /takeaway-waste-management/ | takeaway waste collection | 170 | 15 |
| /pub-waste-management/ | pub waste management | 140 | 13 |
| /cafe-waste-management/ | café waste collection | 210 | 19 |
| /hair-salon-waste-management/ | salon waste management | 260 | 21 |
| /bakery-waste-management/ | bakery waste management | 210 | 25 |
| /restaurant-waste-management/ | restaurant waste disposal | 170 | 27 |

Sectors with **no page**, all low difficulty (competitors rank for these):

| Keyword | SV | KD |
|---|---|---|
| care home waste management | 480 | **9** |
| dental waste disposal | 480 | 13 |
| office waste management | 390 | 13 |
| hotel waste management | 320 | 16 |
| school waste management | 260 | **10** | — |
| retail waste management | 260 | 17 | — |
| butchers waste collection | 260 | **7** |

### Cluster F — Location expansion

The sheet covers Birmingham, London and Manchester only. Low SV but the most
commercially valuable terms on the site — these convert.

| Keyword | SV | KD | Page status |
|---|---|---|---|
| commercial waste collection london | 720 | 31 | exists |
| commercial waste collection manchester | 320 | 13 | **ranks on the -old URL** |
| commercial waste collection leeds | 260 | 17 | exists |
| commercial waste collection liverpool | 260 | 18 | no page |
| commercial waste collection birmingham | 140 | 20 | exists |
| commercial waste collection sheffield | 110 | 15 | exists |
| commercial waste collection bristol | 90 | 22 | no page |
| commercial waste collection nottingham | 90 | 16 | no page |
| commercial waste collection glasgow | 70 | — | no page |
| commercial waste collection leicester | 50 | — | exists |
| commercial waste collection near me | 260 | 25 | — |
| business waste collection near me | 170 | 31 | — |

Also worth noting: Better Waste already ranks p11–28 for a long tail of
`commercial rubbish collection near [area]` queries with 320–720 SV each
(Longsight, Fallowfield, Handsworth, Peckham, Alum Rock, Stratford Rd). These are
odd-looking but real SERPs, and the pages ranking are the generic hub or the old
Manchester page. Proper borough-level pages would take them.

---

## 5. Prioritised roadmap

**Phase 1 — fix what's already working (weeks 1–2, no new content)**
1. 301 `/areas-we-cover-old/manchester/` → `/areas-we-cover/manchester/`
2. Fix www / non-www canonicalisation
3. Resolve `business waste collection` cannibalisation — one canonical money page
4. Refresh `/simpler-recycling-legislation.../` — p14 → top 10
5. Re-map glass keywords in the sheet to `/glass-waste/`

**Phase 2 — the money page (weeks 2–5)**
Build `/commercial-waste-collection/` targeting Cluster A. Consolidate
`/commercial-waste-management/` and `/business-waste-collections/` into it.
Internal-link from `/top-10-commercial-waste-management-companies-in-the-uk/`
(the site's strongest page) and de-optimise `/areas-we-cover/` for national terms.

**Phase 3 — waste-stream expansion (weeks 4–12)**
In ROI order: sanitary/hygiene → confidential/shredding → clinical → hazardous →
WEEE/IT → industrial → construction → wood & cooking oil.
Start with sanitary and confidential: lowest KD, highest commercial value, competitors already
prove the model.

**Phase 4 — low-KD volume (weeks 6–12, run in parallel)**
Split `/binpedia/` into individual bin-size pages (Cluster C). Add the seven missing
sector pages (Cluster E). Both are KD < 17 across the board.

**Phase 5 — location scale-out (ongoing)**
Fix the existing eight pages first (thin, and the Manchester one is broken), then
expand on the businesswaste.co.uk model: Liverpool, Glasgow, Bristol, Nottingham,
then borough-level for London/Birmingham/Manchester.

**Phase 6 — simultaneously, authority**
At AS 20 vs businesswaste.co.uk's AS 41, content alone caps out. Cluster D
(compliance/legislation) is the natural link target — `waste transfer note` and
`waste carriers licence` pages earn links in this vertical.

---

## 6. Notes on data

- All SV / KD / Authority Score in the tables and CSVs are **Semrush UK**. CPC is not
  included, and no Ahrefs keyword difficulty is quoted anywhere in this pack.
- Ahrefs was used only for the indexed-URL evidence behind the
 www / non-www duplication finding.
- Several keywords in your sheet have materially different Semrush volumes than
 listed (`dry mixed recycling bins` 320 → 1,000; `commercial cardboard waste`
 110 → 480; `commercial food waste disposal` 210 → 480). Worth refreshing the sheet.
- I could not crawl betterwaste.co.uk directly from this environment — the network
 policy blocked the host, so the page inventory and on-page read are inferred from
 Semrush/Ahrefs indexed-URL data rather than a live crawl. If you want an on-page
 content audit (H1s, word counts, internal linking) to sit alongside this, allow
 `betterwaste.co.uk` in the environment's network settings and I'll add it.
