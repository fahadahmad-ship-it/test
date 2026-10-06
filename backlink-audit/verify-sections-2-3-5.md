# Adversarial verification — disavow-v2-ahrefs.txt, Sections 2, 3 and 5
Client: ngwindows.com (North Georgia Replacement Windows, Alpharetta/Roswell GA)
Scope: 59 domains / 255 link rows. Verified 2026-10-06 against the committed exports.
Evidence base: `data/ahrefs/ahrefs-backlinks.tsv` (2,665 rows), `git show 6f5f407:backlink-audit/work/links_raw.tsv` (3,499 rows), Ahrefs free DR endpoint, WebSearch.
Nothing in the disavow file was edited.

---

## HEADLINE

| Section | As written | Verified | Verdict |
|---|---|---|---|
| 2 | 43 domains / 90 links | 43 / 90 — every claim holds | **KEEP in full** |
| 3 | 14 domains / 28 links | 14 / 28 — every claim holds | **KEEP in full** |
| 5 | 2 domains / 137 links | both entries fail the file's own grounds test | **REMOVE BOTH** |

**Is whosmypro.com safe to disavow? NO. Remove it.** It is a real, operating, multi-state business
directory. It is the single most damaging line in the file and it is a false positive.

Recommended final counts: S2 43/90 (unchanged) · S3 14/28 (unchanged) · S5 **0/0**.
File-wide effect of this review: 59 → 57 domains, 255 → 118 links.

---

## SECTION 2 — PBN service pages (43 domains / 90 links) — KEEP ALL 43

Every claimed element verified row-by-row for all 43 domains.

- **Anchor (a):** exactly **one** distinct anchor string across all 90 rows —
  `High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service ngwindows.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap`.
  The file quotes it truncated at "...Rank First Page Google"; the real string is longer, which only
  strengthens it. Cosmetic, no correction required.
- **Dofollow (b):** `Nofollow=false` on 90/90. Confirmed.
- **Titles (d):** vendor sales copy on 90/90. Both quoted examples exist:
  "Proven PBN Backlinks to Increase Trust Flow. Drive Qualified Visitors**, for Long Term SEO Results.**"
  (plavo.shop — file quotes it truncated) and "Trusted PBN Backlinks to Improve Citation Flow."
  (bramo/brilko/brinto/bripto.shop).
- **Ahrefs flag (e):** `Is spam=true` on 90/90. Confirmed.
- **Fingerprint (c) — the counts in the file are CORRECT:**
  - `🏆🏆Boost your Google rankings with Premium PBN & Link Building🏆🏆` — **exactly 22 hosts**. ✔
  - path `/all/2066/26.html` — **exactly 18 hosts**. ✔
  - Bonus the file missed: the other 4 trophy-title hosts (lawyerinjeddah.com, libyanatravel.com,
    m98ufa.com, plumeriamarketing.com) share a *second* byte-identical path `/all/947/16.html`.
    Ground (c) therefore covers **22 of 43**, not 18. The file understates its own case.
  - That trophy title appears on **zero** hosts outside Section 2 in the whole 2,665-row export — it
    is not a generic CMS string.
- **Independent corroboration:** 26 of the 43 also appear in the Semrush export (different crawler,
  different date), so these are not an Ahrefs artifact.
- **Liveness / targets:** 90/90 HTTP 200, `Lost status` empty, target host = ngwindows.com on 90/90.
  Last seen 2026-08-05 → 2026-09-25.
- **No collateral:** for every one of the 43 hosts, the spam rows are *all* the rows that host has in
  the export. A domain-level entry destroys no good link.

**False positives found: none.**

Nuance worth recording (does not change the verdict): several hosts look like real or formerly-real
sites carrying injected pages — betulcrime.com (DR 40), m98ufa.com (DR 50),
homesforsaleoldgreenwichct.com (DR 23), uncledspizza.com, plumeriamarketing.com, lawyerinjeddah.com,
libyanatravel.com. That is consistent with a compromised-host PBN. Since none of them links to the
client except through the vendor page, domain-level disavow is still the right instrument and costs
nothing.

---

## SECTION 3 — "High DA backlinks" vendor pages (14 domains / 28 links) — KEEP ALL 14

- **Anchor (a):** exactly **one** distinct anchor across all 28 rows, and the file quotes it
  **verbatim and in full** — `Trusted High DA Backlinks for ngwindows.com to Raise Domain Rating.
  Improve Google Rankings, Across Every Niche and Market.` ✔
- **Dofollow (b):** `Nofollow=false` 28/28. ✔
- **Titles (d):** both quoted examples verified — "Trusted White Hat SEO Links to Raise Domain
  Rating." (murvi.shop) and "Effective Niche Edit Links to Boost Domain Authority."
  (canlisohbethatlari.online). ✔
- **Ahrefs flag (e):** `Is spam=true` 28/28. ✔
- **Liveness / targets:** 28/28 HTTP 200, not lost, target host = ngwindows.com. Last seen
  2026-09-12 → 2026-09-29 (the freshest tier in the file).
- 8 of 14 corroborated in the Semrush export.
- No collateral: these 28 rows are the entirety of each host's presence in the export.

**False positives found: none.** The three non-`.shop` hosts (bitproperty.online DR 26,
canlisohbethatlari.online DR 20, tokyopush188.online DR 42) are higher-DR but their only link to the
client is the vendor page; nothing about them reads as a real business serving this niche.

Presentational note: Sections 2 and 3 are the *same* vendor network — shared `.shop` host pool,
shared title grammar ("<Adjective> <Service> to <Benefit>. <Benefit>, <Qualifier>."), shared page
architecture. Splitting them is fine for the reviewer but the grounds are identical.

---

## SECTION 5 — REMOVE BOTH ENTRIES (137 links back)

### whosmypro.com — **REMOVE. NOT safe to disavow.** (133 links)

This is a genuine business directory and the entry is a false positive. Evidence:

1. **Real operating company.** "Who's My Pro?", operated by **Whos My Pro LLC**, with published
   Terms of Service, Privacy Policy, Disclaimer, FAQ and Contact pages, and a documented listing
   correction/removal process (support@whosmypro.com, business name + city/state + URL + requested
   change). Link farms do not publish a removal SLA.
2. **Nationwide and multi-category — not built around this client.** Live sections include
   `/plumbing/flanders-nj/`, `/doors-windows/albertville-al/`, `/doors-windows/hartselle-al/`.
   The GA window pages are one slice of a US-wide plumbing/electrical/HVAC/doors directory.
3. **The pages are real multi-business comparison pages.** `/doors-windows/alpharetta-ga/` lists
   NG Windows **alongside** North Fulton Window Experts (5.0★, 14 reviews), Apex Energy Solutions
   (4.8★, 438 reviews) and Window Comfort (4.9★, 207 reviews), with star ratings and review counts.
   Ahrefs' own columns agree: each page carries **211–222 external links to ~80 external domains**.
   ngwindows is 1 of ~80 businesses on the page, not the page's reason to exist.
4. **The anchor is a UI control, not anchor text.** `↗ Go to company website` — zero keyword
   optimisation, no client name. The file correctly does not claim ground (a); it *cannot*.
5. **The link is a scraped Google Business Profile citation.** 72 of the 133 rows target
   `https://www.ngwindows.com/?utm_source=google&utm_medium=organic&utm_campaign=gbp` — the
   client's **own GBP website URL, with the client's own UTM tags**. Who's My Pro states listings
   are "sourced from public business profile data." This is an unsolicited third-party citation
   built from Google's own data, outside the client's control and not placed by any vendor. That is
   the textbook case for *not* disavowing.
6. **The geography is correct, not permuted.** All 72 paths are real Georgia municipalities
   (Atlanta, Marietta, Roswell, Alpharetta, Sandy Springs, Dalton, Rome, Athens, Toccoa, Gainesville…).
   The client publicly states it serves **the entire state of Georgia** (ngwindows.com/service-areas;
   "over 10,000 windows and doors per year in Atlanta, Alpharetta, Roswell and surrounding areas").
   A statewide directory footprint matches a statewide service area. The "city-permutation doorway"
   reading does not survive that.

**Four factual errors in the entry as written:**

| # | File says | Export says |
|---|---|---|
| 1 | "**133** near-identical pages" | **72** distinct referring pages. 61 of them carry two links each (bare homepage + UTM URL) = 133 *link rows*. The central structural claim is overstated by 85%. |
| 2 | "each carrying the same anchor … **to the same target**" | **Two** distinct targets: `https://www.ngwindows.com/` (61 rows) and the GBP UTM URL (72 rows). |
| 3 | Page type "Listing collection > Business" | Only **35** of 133 rows. 95 rows have Page type **blank**; 3 are "Listing > Business". |
| 4 | anchor `- Go to company website` | actual anchor is `↗ Go to company website` (arrow glyph). Cosmetic. |

With (c) collapsed to 72 accurate-geography pages on a real multi-business directory, the only
surviving ground is **(e) Ahrefs `Is spam=true`** — which the file's own preamble declares
"corroborating only, NEVER the sole ground." The entry fails the file's own rules.

**Cost if shipped:** 133 links across 72 live local-citation pages in exactly the client's service
area — the largest single-line kill in the document, aimed at a directory the client would normally
want to be in.

### homeownerideas.com — **REMOVE (evidence far weaker than claimed).** (4 links)

- **It is a real directory.** homeownerideas.com is a nationwide home-improvement **contractor
  directory plus blog**, with per-state and per-category sections across all 50 states
  (`/directory/region/florida/`, `/directory/dir-cat/residential-contractor/`, `/local-looks/`,
  `/online-quote/`), free listing submission, operator traceable to Leads Online Marketing. DR 23.
  No page sells links; no title advertises link-selling. It is a standard local-citation site of the
  kind that appears on published construction-citation lists.
- **Ground (c) "fabricated geography" does not hold.** "North Georgia Replacement Windows **Roswell
  New Mexico**" is a **Roswell, GA → Roswell, NM city/state disambiguation bug** — the single most
  famous US city-name collision, and the client really is in Roswell, GA. A geo-matching bug is
  evidence of sloppy automation; it is *not* "a directory that invents a location," and it is not
  evidence of a link scheme. The claim as drafted misdescribes the data.
- **The anchor argues against manipulation.** All 4 rows use the bare URL
  `https://www.ngwindows.com/` — the least optimised anchor that exists. A link vendor uses keyword
  anchors. The file correctly does not claim ground (a) here either.
- **What is left:** (b) dofollow — not a ground on its own — plus (e) the Ahrefs flag, again
  forbidden as a sole ground. The entry fails the file's own rules.
- **The one real weakness,** and it is not a disavow-grade one: three duplicate listing pages for the
  same business (`/directory/north-georgia-replacement-windows/`, `-2`, `-3`) plus the region page.
  That is duplicate-submission hygiene. Remedy is a removal request to the directory, not a disavow.

**Section 5 recommended final count: 0 domains / 0 links.** If the reviewer insists on keeping one,
homeownerideas is the only arguable entry (4 links, DR 23) — but **whosmypro must come out regardless.**

---

## Cross-cutting checks

**The `performingwindows.com` trap — clean in these sections.**
`performingwindows` appears **0 times** anywhere in the Ahrefs export (anchor, target URL or
referring URL), so it cannot have contaminated Sections 2, 3 or 5, which are Ahrefs-sourced.
Word-boundary matching `(?<![a-z0-9-])ngwindows\.com` vs naive substring `ngwindows.com` returns
**identical counts in all three sections** (S2 90 = 90, S3 28 = 28, S5 4 = 4, mismatch 0). Every
anchor claimed to name the client is a genuine word-boundary match.

> **Warning for work outside this review's scope:** the trap is very real in the **Semrush** export.
> Of 762 anchor hits on the substring `ngwindows.com` there, **350 are `performingwindows.com`** —
> 46% misattribution. Any Semrush-evidenced entry (Section 6, 117 domains) must be re-checked with
> word-boundary matching before upload. Not verified here.

**Liveness and targets — all clean.** Across all 255 rows in S2/S3/S5:
HTTP code 200 on 255/255 · `Lost status` empty on 255/255 · target host = `ngwindows.com` on
255/255 · no third-party redirect shell anywhere. The populated "redirect chain" values are the
client's own 301 normalisation of its homepage/UTM URL, not an intermediary.
Last seen: S2 2026-08-05→2026-09-25 · S3 2026-09-12→2026-09-29 · whosmypro 2026-08-20→**2026-10-02**
(still being crawled four days before the file was built) · homeownerideas 2026-09-07→2026-09-28.

**A non-signal, checked and discarded.** `Rendered=false` on all 255 rows looks alarming, but it is
true of **2,593 of the export's 2,665 rows** — an export-wide crawl artifact, not a property of
these links. Do not use it as a ground.

**Hygiene.** No duplicate domains within any section and no domain appearing in two sections.
Section 2 contains exactly 43 unique domains totalling exactly 90 rows; Section 3 exactly 14 / 28;
Section 5 exactly 2 / 137. All stated counts reconcile.

**Nothing flagged as missing evidence.** Every one of the 59 domains was located in the Ahrefs
export with its claimed rows present.

---

## Action list

1. **Delete `domain:whosmypro.com` from Section 5.** Real directory, scraped-GBP citation, 72 (not
   133) accurate-geography pages, ~80 businesses listed per page, CTA anchor. False positive.
2. **Delete `domain:homeownerideas.com` from Section 5.** Real nationwide contractor directory; the
   "fabricated geography" ground is a Roswell GA/NM disambiguation bug; bare-URL anchor; only the
   forbidden sole ground (e) remains.
3. **Delete the Section 5 header** or mark the section void — recommended final count 0/0.
4. **Ship Sections 2 and 3 as written** (43/90 and 14/28). Optionally correct ground (c) in Section 2
   upward from 18 to 22 hosts (second shared path `/all/947/16.html`, 4 hosts) and extend the two
   truncated quotes.
5. **Before upload, re-run the word-boundary anchor test over Section 6** (Semrush-only, 117
   domains). 46% of Semrush's `ngwindows.com` anchor hits are `performingwindows.com`.
