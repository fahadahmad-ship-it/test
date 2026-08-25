# Performance Lab — Backlink Disavow Audit

Deterministic, rule-based toxic-link audit for `performancelab.com`.
No third-party toxicity score is consumed or trusted; every verdict is
derived from raw metrics in the export and is reproducible from source.

```bash
python3 audit.py           <backlinks.csv> <outdir>                 # link-level pass
python3 refdomain_audit.py <backlinks.csv> <refdomains.csv> <outdir> # full profile
python3 build_workbook.py  <outdir>                                  # single sheet
```

## Outputs

| File | Contents |
|---|---|
| `domain_audit.csv` | One row per referring domain — the primary deliverable. |
| `url_drilldown.csv` | Per-URL rows for every `DISAVOW` / `REVIEW_MANUALLY` domain. |
| `disavow.txt` | Google-format disavow file, grouped and commented by risk factor. |
| `SUMMARY.md` | Executive summary, equity exposure, priority targets, held-for-decision items. |
| `full_refdomain_audit.csv` | **All 2,928 referring domains** — the primary deliverable. |
| `disavow_full.txt` | Google-format disavow file for the full profile. |
| `performancelab_backlink_audit.xlsx` | **Consolidated single-sheet workbook** — all 2,928 domains and every drill-down URL on one surface, built by `build_workbook.py`. |

```bash
python3 build_workbook.py <outdir>          # after audit.py
```

The workbook puts domain rows (`Level=DOMAIN`) and their per-URL drill-down
(`Level=URL`) on one sheet, colour-coded by action, with an autofilter and a
dropdown on every Action cell. The summary block at the top uses live
`COUNTIFS`/`SUMIFS`, so as an analyst resolves `REVIEW_MANUALLY` rows to
`DISAVOW` or `KEEP` in place, the domain, backlink and follow-link totals
update with them.

## Coverage: why two exports are required

**The backlinks export alone cannot audit this profile.** It is capped at
50,000 rows — 3.67% of the 1,362,105-link profile — and it is *not* a random
sample: one domain (`hexcolor.co`) occupies 90.8% of it. Auditing it in
isolation reaches only **603 of 2,928 referring domains (20.6%)**, and misses
`wete.co` entirely — the second-largest referring domain at 209,306
backlinks.

The referring-domain export closes that gap. `refdomain_audit.py` evaluates
all 2,928 domains and merges in the richer link-level verdicts wherever the
sample covers them, so totals reconcile to Semrush exactly:

| | Semrush | This audit |
|---|---:|---:|
| Referring domains | 2,928 | 2,928 |
| Total backlinks | 1,362,105 | 1,362,105 |

Every row carries an **Evidence Level** naming what the verdict rests on:

- `Link-level (in 50k sample)` — 602 domains, full anchor/placement/OBL signal.
- `Link-level sample too thin (<1% of domain)` — the sample covers under 1%
  of the domain's real volume, so the thin verdict is replaced by the
  domain-level reading.
- `Domain-level only (outside sample)` — 2,325 domains judged on authority
  score, backlink volume, IP/C-block, TLD and naming alone. Thinner signal,
  so `DISAVOW` here requires a signature that cannot plausibly be innocent.

### What the domain-level pass caught

The referring-domain export carries `IP Address`, which makes the C-block
footprint analysis the brief asked for possible for the first time. Findings
absent from the sample entirely:

- **286 domains from one `seo-anomaly-*` / `seo-cartel-*` operation** —
  `seo-anomaly-top-1..89.xyz`, `seo-anomaly-{anchor,backlink,authority,…}`
  across `.online/.site/.space/.website`. The same operation whose Telegram
  handle appears in the anchors injected into three hacked institutional
  hosts, so this is a coordinated campaign, not organic spam.
- **89 domains on four concentrated C-blocks** (`118.139.181.0/24`,
  `203.161.54.0/24`, `68.178.238.0/24`, `118.139.176.0/24`) — near-zero
  authority clusters under single ownership.
- **147 link-vendor domains** named for what they sell (`backlinkhouse.com`,
  `bestseobacklinkforsite.com`, `a2zseoarticles.com`).

### C-block analysis requires a shared-hosting exclusion list

Co-location is only a footprint signal off shared platforms. Half the
profile (49.2%) sits behind Cloudflare, and the largest single C-block —
`23.227.38.0/24`, 81 domains — is **Shopify**, which hosts the client's own
brand estate. `192.0.78.0/24` is WordPress.com. A naive "many domains, one
C-block" rule would disavow Shopify and Automattic wholesale. Those ranges
are excluded by name in `SHARED_PLATFORM_CBLOCK`.

## Input reality vs. brief

The brief specified ~1.4M backlinks across ~3,000 referring domains and a
column set including `Anchor Type`, `HTTP Status`, `Referring Domains
Count` and `Estimated Organic Traffic (Source)`.

The supplied export is a **Semrush backlinks export of 50,000 rows across
615 referring domains** — a ~3.6% sample of the stated profile — with a
different schema. Columns actually present:

`Page ascore, Source title, Source url, Target url, Anchor, External links,
Internal links, Nofollow, Sponsored, Ugc, Text, Frame, Form, Image,
Sitewide, First seen, Last seen, New link, Lost link`

Consequences, and how each was handled:

| Missing signal | Substitute used |
|---|---|
| `Referring Domain` | Derived from `Source url` (see *Domain keying*). |
| `Anchor Type` | Derived by classifier — Branded / URL / Exact-Commercial / CTA-Generic / Phrasing / Empty-Image. |
| `Estimated Organic Traffic` | `Page ascore` (Semrush page authority) as an authority proxy. **This is the weakest substitution** — a zero-traffic ghost domain can still carry a nonzero ascore. |
| `HTTP Status` | Unavailable. Dead-loop and parked-domain detection in the affiliate protocol **could not be executed**; affiliate gateways are retained on pattern match without a liveness check. |
| `Referring Domains Count` | Unavailable; no inbound-authority check on source domains. |
| `Link Type` (redirect) | Unavailable. Redirects are not distinguishable from direct links in this export. |

Verdicts are therefore sound for what the export contains, but the audit is
**not complete for the full 1.4M-link profile**. Re-run against a full
export with status codes and source traffic before filing the disavow.

## Evaluation unit — domain keying

Aggregation happens at the **registrable domain**, with two corrections that
materially change the disavow file:

1. **Shared publishing platforms** (`blogspot.com`, `substack.com`,
   `wordpress.com`, `medium.com`, …) key on the **full hostname**. Each
   account is an independent publisher. Keying these at the root would merge
   unrelated sites and emit `domain:blogspot.com` — a disavow line that
   discards every Blogspot link the brand will ever earn.
2. **Generic second-level labels under a ccTLD** (`edu.co`, `gov.mg`,
   `co.uk`, …) keep a third label. Three hacked institutional hosts appear
   in this dataset; `domain:edu.co` would disavow every Colombian
   university.

## Rule order

Protected assets resolve **before** any spam rule can fire.

**Tier 1 — protected (never disavowed)**
1. Opti-Nutra brand estate — `performancelab.com`, `mindlabpro.com`, `testolabpro.com`, `prelabpro.com`.
2. Affiliate / tracking infrastructure — known networks plus `go.`/`track.`/`offers.`-style tracker hosts.
3. Dedicated partner landing pages — all links resolve to one bespoke target path outside the standard site structure with brand-led anchors (e.g. `whatismoneypodcast.com` → `/breedlove`).
4. Search & AI answer surfaces — reported, excluded from the disavow file; they pass no manipulable equity.

**Tier 2 — spam (fires regardless of anchor profile)**

5. Hacked-site / link-vendor injection (anchor advertises a link vendor).
6. Vendor blog networks — free-blog hosts used only by link sellers.
7. Spun-content networks — the same article, near-verbatim, on 3+ other referring domains.
8. Synthetic affiliate doorway domains (geo-prefixed / doubled-hyphen patterns).
9. Throwaway auto-generated account subdomains.
10. Scraped aggregators, directory/link-scheme domains.
11. PBN / templated mass footprint — ≥20 auto-generated pages, ≤2 distinct anchors, no niche overlap.
12. Sitewide injection — one non-branded anchor on ≥80% of ≥8 pages.
13. Extreme outbound-link farms (≥1,500 avg external links).

### Cross-domain network detection

Rules 6–9 exist because per-domain analysis is structurally blind to
networks. A single link from `tkzblog.com` looks like an ordinary low-value
blog link; the pattern is only visible in aggregate. Before classification
the audit therefore builds a global index of normalised page titles and
flags any domain running an article that appears on **three or more other
referring domains**.

This caught 24 domains — carrying **follow** links — that per-domain rules
had cleared as topically relevant, because their spun articles were about
fish oil and nootropics and so passed the niche-relevance test. Relevance
had become the thing protecting them.

The counter-check matters as much: one publisher syndicating its own
article across international editions (`thesun.co.uk` / `the-sun.com` /
`thesun.ie`) is not a network. Domains are collapsed to a brand core before
the count, so a single brand cannot trip the rule.

**Safety brake.** Past this point a profile that is ≥80% branded or bare-URL
anchors can only be downgraded to `REVIEW_MANUALLY`, never disavowed.
Circumstantial signals — topical irrelevance, elevated outbound-link counts —
are not sufficient grounds to discard a brand mention. High anchor diversity
(≥60% distinct) likewise blocks irrelevance-based disavowal, since editorial
variety is the opposite of a templated placement.

**Tier 3–4** — borderline signals route to `REVIEW_MANUALLY`; topically
relevant and brand-mention profiles are retained.

## Confidence gate

`DISAVOW` requires **High** confidence. Anything below it is routed to
`REVIEW_MANUALLY` instead, and the risk factor is suffixed
`[below disavow confidence bar]`. A filed disavow is slow and awkward to
unwind; a review queue is not.

Three domains are additionally held back by name in `MANUAL_REVIEW_OVERRIDE`
for an explicit client decision, each carrying the evidence that makes the
call a judgement rather than a rule — `hexcolor.co`, `currencyconverts.com`,
and `eastbayexpress.com`. See the summary for the reasoning.

## Remediation priority

Nofollow links pass no equity, so a nofollow-only footprint is hygiene, not
remediation. Every disavow row carries a priority:

- **P1** — follow links at volume (≥25)
- **P2** — follow links, low volume
- **P3** — nofollow only, no equity passed

This matters here: 98.1% of disavow-flagged backlinks in this export are
nofollow. Sequencing by priority prevents a headline row count from setting
the workload.

## Workbook formula validation

`recalc.py` could not be used in this environment: LibreOffice headless
hangs here even on a four-cell workbook, so both attempts timed out without
recalculating anything. The formulas were therefore validated directly
instead:

- every range spans exactly the data rows (`10:2154`), checked programmatically;
- the referenced columns resolve to the intended headers (`A`=Level,
  `F`=Action Recommendation, `K`=Backlinks, `L`=Follow (Equity) Links);
- expected results were computed independently from `domain_audit.csv`, and
  the TOTAL row reconciles to the raw export — 615 domains, 50,000
  backlinks, 3,431 follow links;
- only `COUNTIFS`, `SUMIFS` and `SUM` are used: all Excel-2007-era, so no
  `_xlfn.` prefix is needed and no spilling-array metadata is involved.

One consequence remains. openpyxl writes formulas with no cached values, and
nothing recalculated them, so those twelve summary cells read as empty to
anything relying on cached values (`pandas`, `load_workbook(data_only=True)`,
some previewers). Excel and LibreOffice compute them on open. The 2,145 data
rows are literal values and are unaffected.

## Coverage and residual risk

All 2,928 referring domains carry a verdict. "Audited" is not the same as
"settled", so the honest position:

| | Domains | Basis |
|---|---:|---|
| `DISAVOW` | 804 | High confidence only; every rule is a signature that cannot plausibly be innocent. |
| `REVIEW_MANUALLY` | 1,241 | Needs a human call. |
| `KEEP` | 883 | 395 High (link-level), 69 Medium, **419 Low**. |

### Residual triage

Parking 1,241 domains in a review queue is not an audit result, it is
deferred work. For the 957 domains outside the sample there is genuinely no
anchor, target or placement data — the export does not contain their links —
but exposure, authority, hosting and name shape remain. A domain with a
couple of links, ordinary authority and no spam marker does not merit a
human hour: disavowing gains nothing, retaining costs nothing.

`residual_triage()` resolves those, cutting the queue **1,241 → 682**. Rows
it moves are labelled `(Risk-Triaged)` and their evidence level is suffixed
`+ risk triage`, because this is a risk decision rather than a verification.
It fires only when every marker is absent: no hosting cluster, no spam TLD,
plausible name shape, under 25 backlinks, not held for a client decision.

Name shape is scored statistically (`nameshape.py` — vowel ratio, consonant
runs, digit and hyphen density, keyword stuffing), validated at **12/16 spam
caught with 0/18 false flags** on known-good domains. It is deliberately
**not** allowed to disavow on its own: it misreads initialisms
(`jsrproductions`, `hmscicomms`) as machine-generated, and the domains it
would have caught carry negligible exposure anyway.

**The remaining queue is not 682 units of work either:**

| Tier | Domains | Backlinks |
|---|---:|---:|
| ≥1,000 backlinks | 3 | 1,334,482 |
| 100–999 | 11 | 3,105 |
| 25–99 | 25 | 1,373 |
| 10–24 | 98 | 1,494 |
| <10 | 545 | 1,302 |

Deciding `hexcolor.co`, `wete.co` and `appsrankings.com` settles **98.5% of
the entire link profile**. The 545-domain tail carries 1,302 links between
them and can be worked opportunistically or left.

### Where false negatives most likely remain

**419 Low-confidence KEEPs** — 291 retained because the domain name matches
the health/performance lexicon, 128 because authority score ≥20. Both are
thin: a PBN can register a niche-sounding domain, and authority score is not
editorial quality. These sit outside the 50k sample, so no anchor or
placement signal exists to test them against. This is the most likely home
of anything still missed.

Successive review passes each found real spam in exactly this bucket — a
24-domain spun-content blog network, then 274 directory-submission domains,
then 52 throwaway free-host subdomains — every one previously protected by
niche relevance or authority score. The pattern is that generated networks
adopt legitimate-looking surface features; only cross-domain evidence
(shared titles, shared C-blocks, shared naming generators) exposes them.

**What would close the gap:** a full backlinks export rather than a 50k
sample, which would give anchor, placement and outbound-link signal for the
2,325 domains currently judged on domain metrics alone.

## Known limitations

- No liveness check on redirects or affiliate gateways (no `HTTP Status`).
- `Page ascore` is a weak proxy for organic traffic; a genuinely
  zero-traffic domain with a nonzero ascore may be under-flagged.
- Topical relevance is lexicon-based over domain names and page titles, not
  page-body content — non-English sources are under-detected.
- The URL drill-down caps at 250 rows per domain for templated footprints;
  the cap is disclosed in `SUMMARY.md`, never silent.

## Critical review pass (2026-08-25)

A full adversarial re-read of every rule against the raw data. Seven defects
found and fixed; one rule withdrawn.

**1. Hacked institutional hosts were disavowed at the root.** `uba.ar` is the
University of Buenos Aires at authority 68 and the injection sits on
`quantitativemarxism.economicas.uba.ar` alone. A `domain:uba.ar` line would
discard every future academic citation. Now scoped to the compromised host —
also `cecar.edu.co`, `alazharcilacap.sch.id`, `spottedcow.media`,
`digitalatto.io`, `capetownthing.co.za`, `seomuda.id`.

**2. The affiliate guard was shielding the directory-spam network.** The
protection added for `ebylife.com` retained 196 directory domains as "Tracked
Affiliate Partner"; the Directory Submission Spam Network collapsed from 274
condemned to 14. A structural override now lets a name-based spam signature
outrank a link-level affiliate label. I had claimed this guard could not shield
structural spam — that claim was wrong.

**3. Outbound-link volume was condemning on its own, for the third time.**
After `benchchem.com` (a bibliography) and `sitelike.org` (an aggregator), it
caught `duckduckgo.github.io` — DuckDuckGo's Tracker Radar Wiki, a privacy
research dataset that lists every site embedding a given tracker —
`smolecule.com` (numbered citations in a product reference list),
`whoacceptsamex.co.uk` (a factual merchant directory) and two personal
"favourite sites" pages. The discriminator was in the data all along: the
genuine dumps have machine-generated paths (`/list-<hash>`, `/report/49117`,
`/domain-list-456`, `-links-list`) and the false positives have human ones
(`/favorite-sites/`, `/companies/performance-lab/14323/`, `/products/s541135`).
High OBL now requires `autogen_page_share >= 0.50`; without it the domain goes
to review, not to the disavow file.

**4. A shared link-template rule was missing.** 52 domains link from the
byte-identical path `/domain-list-456` with ~1,000 outbound links each, and 100
from `/czechia_farm-13-08-2025/seo-anomaly-czechia_farm-10`. Identical paths
across unrelated domains are one operator's script. Excluded: paths naming the
client's products (29 domains publish `/performance-lab-mind` independently)
and on-niche topical slugs (`/review/best-vitamin-d-supplements` is shared by
15 domains, one of them `bbcgoodfood.com`).

**5. Nine shared hosting platforms were missing from `PLATFORM_HOSTS`.**
`icylv5.azurewebsites.net` keyed to `azurewebsites.net`, merging every Azure
app into one row until four link-vendor advertisement anchors were diluted
into a retain. Same defect as the original `blogspot.com` keying, on
`pages.dev`, `workers.dev`, `web.app`, `firebaseapp.com`, `glitch.me`,
`repl.co`, `onrender.com`, `surge.sh` and `000webhostapp.com`.

**6. The link-vendor anchor regex missed a whole vendor.** `@SEO_CARTEL IN
TELEGRAM – SEO BACKLINKS, BULK LINK POSTING` was not matched, so
`academia.edu.gt` and `equipetrol.com.ec` fell through to the outbound-volume
rule and never reached the hacked-host scoping. Broadened; 8 distinct vendor
anchors over 1,022 links now match, with no false positives in the corpus.

**7. A backlink-sales page was retained.** `rankvanceauthority.info` served
2,008 follow links from `/order-quality-backlinks-online-with-rankvance-
today-251/` and sat in the negligible-exposure tier. A path advertising
backlink sales is self-declaring and is now read as one.

**Withdrawn: the generated-doorway-URL rule.** 19 `*.pages.dev` subdomains link
from URLs like `/rhbiu-top-nootropics-2025-fwnbr` — no publisher writes those
by hand. But two implementations each misclassified higher-authority domains
than they caught: letter-shape scoring flagged
`health-is-wealth-...-health` and `alpha-lipoic-acid-...-research`, because
ordinary English words contain three-consonant runs; corpus document frequency
fixed those and then flagged `trendencias.com` (authority 59), `gymbeam.it`,
`healthview.gr` and `dr-muscu.fr`, because Spanish, Italian, Greek and French
words are rare in an English corpus. Rare is not generated. The pattern governs
28 backlinks out of 1,362,105, so it is reported in `SUMMARY.md` under
"Observed but not automated" for a human to act on, and those domains resolve
on exposure like any other single-link authority-2 referrer.

Also fixed: the `Disavow Entry` column showed `domain:uba.ar` while the file
correctly narrowed to the subdomain — the sheet is what the client reads.

Net effect: DISAVOW 961 -> 1,081, REVIEW 139 -> 88. Both moves are evidence,
not threshold changes.

## Review-queue pass (2026-08-25)

Every domain in the review queue read individually against its actual
placements, not its domain metrics. This surfaced a large injected-spam
network I had been *retaining*, which is the more expensive kind of error.

**The injected-doorway network — 15 domains, 19 of them previously KEEP.**
Working the queue by hand turned up two URL signatures with no benign
reading:

- A root URL whose whole query is one letter and a long id:
  `porras.ch/?p=89451313`, `politicsofsport.com/?p=89451313`,
  `pro-one-trans.com/?p=89451313`, `jvnps.com/?j=83596013`,
  `saintsebastianelitecollege.com/?s=83596013`. **The ids repeat across
  unrelated domains** — 89451313 on three, 83596013 on two, and
  `csir-sari.org`/`thejeera.com` one digit apart carrying the same anchor.
  Fifteen domains span seven different single-letter parameters (b, c, d, j,
  p, s, t); no CMS uses seven conventions. Anchors are e-commerce modifiers
  machine-dropped into health phrases: "Best omega 3 hotsell supplement for
  dogs", "Crunching sound in cheap knee", "Belly fat deals burner without
  exercise".
- A content page served from a CMS admin directory:
  `robo.dev.nologostudio.ru/bitrix/admin/tzut/the-star-newspaper-obituaries.html`
  and `avtoburo-bitrix.sk-its.ru/bitrix/admin/hqfyj1m/burthey-funeral-home-durham-obituaries.html`,
  anchors "wlces" and "kjwjx". Nobody links out from `/bitrix/admin/`.

`servicio-online.net` (authority 30) and `csir-sari.org` (21) are compromised
hosts, not bad actors, so the disavow narrows to the injected subdomain where
one exists. An anchor-based version of this rule was tried and dropped twice:
keying on the commerce wording caught the client's own `mindlabpro.com`
("Shop Performance Lab® Omega-3") and every real affiliate, and requiring the
anchor to omit the brand let two through, because these injections often
carry a scraped article title that names it. The URL carries the signature
alone.

**Five other rules the queue produced.** A 6-domain template network found via
mixed-case opaque paths — `/10/EmzwpDHARN` on both `businessvocal.com` and
`thecloudherald.com`, `/01/arnVoAQycp` on `global-rank.pages.dev` and
`top-websites-directory.pages.dev`. Only 35 such paths exist in the corpus, so
two owners is decisive where two owners of a readable slug would not be — and
it finally gave real placement evidence for three `pages.dev` domains an
earlier pass could not separate. Klaviyo's click wrapper
(`ctrk.klclick2.com`) was being read as an affiliate gateway with link-farm
traits; it is the brand's own newsletter. Seven blogspot hosts averaging
13,500 outbound links a page with URLs like `/1u58.vip%20rel=nofollow` are
scraped templates, not blogs. A vendor's three domains
(`rankvance.website`, `rankvanceseo.info`, `rankvanceauthority.info`) phrase
their sales path three ways, so the backlink-sales pattern now allows
intervening words. And a name-based structural signature now breaks an
unresolved REVIEW tie, not just an affiliate mislabel — while still never
overruling a KEEP earned on an observed redirect or affiliate parameter.

**Two bugs found while wiring those up.** `_registrable()` collapses every
blogspot subdomain to `blogspot.com`, so a `.endswith(".blogspot.com")` test
silently never matched — the blogspot rule is keyed on the full hostname
instead. And an `/(?:[a-z]+-)*list[-_]?\d+` path pattern first written as
`[a-z-]*list` matched any word ending in "list", which would have flagged
`checklist-2024` and `playlist-99`.

**The remaining 70 are each hand-decided.** `review_decisions.py` carries a
recommendation and the evidence behind it for every row — 26 DISAVOW, 43 KEEP,
1 for the client to settle. They render as two colour-coded columns in the
sheet's Review Queue tab next to the decision dropdown, so the call is made
with the evidence in view rather than from the metrics.

`dtcx.com` is the one I cannot settle: it links with image anchors
"Performance Lab Logo" and "Nutropic Logo", which reads like an owned or
partner property, but it is also promoted *by* several of the spam networks in
this audit ("visit dtcx.com for latest info", "Premium PBN Network Service
dtcx.com Rank First"). Either it is yours, or a link seller is riding the
brand. That needs an answer before any action.

DISAVOW 1,081 -> 1,120, REVIEW 88 -> 70.

## Workbook reorganised for working (2026-08-25)

The sheet held the right data in the wrong shape: it opened on a 7,904-row
reference table with no indication of where to start, and the Review Queue put
my recommendation in column 16, so you scrolled past fifteen columns to reach
the thing you were being asked to confirm.

Five tabs now, in the order you work them.

**Start here** — what the audit found, how to work the other tabs, the one
question I could not settle, and where the confidence actually sits (2,354
domains judged on observed placements, 362 on domain metrics alone, 352 keeps
retained on negligible exposure rather than verified merit).

**Networks** — the work surface. 1,120 disavowed domains are **25 decisions**,
not 1,120 judgements: 139 of those rows are `seo-anomaly-s1.xyz` through
`s139.xyz`, one operator, one call. Each row gives the network, its domain and
backlink counts, its follow links, its highest-authority member, why it is
flagged and an example domain, with one Approve dropdown. Ordered by impact:
equity-passing networks first, nofollow-only last.

**Disavow** — the members of each network, grouped contiguously under it with a
rule between groups and in the same order as the Networks tab. Use it to
spot-check before approving, or to pull one domain out of a network. Where a
`Disavow Entry` names a subdomain, that is deliberate: the host is compromised
rather than hostile, and `domain:quantitativemarxism.economicas.uba.ar` keeps
the University of Buenos Aires' other 4 million pages out of the file.

**Review Queue** — recommendation in column B, the evidence for it in column C,
sorted so the open question comes first, then the 26 disavows, then the 43
keeps.

**Full audit** — all 2,928 domains and the per-URL drill-down, moved to last.
Reference, not a worklist.

Two defects found while rebuilding it. The resolution pass rewrites verdicts
after `Remediation Priority` has already been computed, so 92 domains that
`_set()` flipped to DISAVOW kept the `"-"` priority they had as keeps — which
sorted a network carrying 158 follow links *below* the nofollow-only work.
Priority is now a function both paths call. And a blank Follow column means the
domain sits outside the link sample, so the count is unknown, not zero;
totalling it printed `0` against 139 domains, which reads as "passes no equity"
when it means "we cannot see". Those cells now say `not sampled` or
`593 (+4 unsampled)`.
