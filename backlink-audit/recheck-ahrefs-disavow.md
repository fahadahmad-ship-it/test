# Re-check: disavow rebuilt on Ahrefs evidence

**Date:** 2026-10-06
**Inputs:** `data/ahrefs/ahrefs-backlinks.tsv` (2,665 live links), `data/ahrefs/ahrefs-refdomains.tsv`
(1,357 domains), `data/refdomains.csv` (Semrush, 1,232 domains), `work/links_raw.tsv` @ `6f5f407`
(3,499 anchor rows).
**Output:** `disavow-v2-ahrefs.txt` — **460 entries**.
**Not touched:** `disavow-ngwindows.txt`, `FINAL-AUDIT.md`.
**Live APIs:** none. Semrush `ERROR 132`; Ahrefs Site Explorer locked to 2026-10-25. Every statement
below is derived from the committed exports; nothing was re-fetched or rendered.

---

## 1. Headline

| | |
|---|---|
| Recommended final entry count | **460** |
| Ahrefs-evidenced | 343 |
| Semrush-only, independently evidenced | 117 |
| Prior file (5 entries) survival | **5 / 5** |
| Prior ~87 candidates survival | **87 / 87** (all pass a stricter re-test) |
| Ahrefs `Is spam` false-positive rate, dofollow slice | **3.0 %** (10 / 336 domains) |
| Ahrefs `Is spam` false-**negative** rate, keep-list | **10.6 %** (23 / 218 domains) |
| DR ≥ 30 entries in the final file | **3** of 343 Ahrefs-side |

The two most consequential findings are not in the entry count:

1. **Ahrefs' spam flag under-fires roughly as badly as it over-fires**, and it under-fires on
   *dofollow* links, which is the half that matters. Treating the flag as the filter would have
   missed 17 PageRank-passing links from a self-declared backlink marketplace.
2. **The 14-redirect-shell model has no support in Ahrefs' redirect-chain data.** Not one of the
   14 shells appears in any `Redirect Chain URLs` value across 2,665 links.

---

## 2. Method

Candidate set per brief: `Is spam = true` AND `Nofollow = false` → **809 links / 336 domains**.
That set was then (a) clustered by fingerprint, (b) hand-reviewed where no fingerprint applied,
(c) corrected for both classifier error directions, (d) unioned with independently evidenced
Semrush-only domains.

Every retained entry carries at least one of these **behavioural** grounds, quoted in the file:

- **(a)** manipulative anchor naming `ngwindows.com` inside link-vendor copy
- **(b)** observed dofollow
- **(c)** structural fingerprint — byte-identical path / campaign ID / page-ID across unrelated hosts
- **(d)** link-selling character stated in the referring page's own title
- **(e)** Ahrefs `Is spam` — corroboration only, never sole ground

No entry depends on DR, AS, traffic, thin content, TLD, country or hosting. The file says so in its
header and repeats it in the high-DR section.

### Word-boundary correction

A naive `ngwindows.com` substring test on anchors is wrong: `performi` + `ngwindows.com`,
`buildi` + `ngwindows.com`. The prior Semrush pass's vocabulary is full of anchors naming shells
(`performingwindows.com`, `thermalprowindows.com`). All matching here uses
`(?<![A-Za-z0-9-])(?:https?://)?(?:www\.)?ngwindows\.com`. Applying the naive test instead would
have inflated the Semrush-only candidate list from 117 to 227 — a 94 % over-count.

---

## 3. Does Ahrefs' spam flag over-fire? (Task 1)

### 3.1 Random sample of 25 flagged domains

Seeded sample (`seed=20261006`) of 25 from the 1,139 flagged domains:

- **24 unambiguous true positives** — 9 `*.xyz` hosts and 3 `*-seoexpress.store` hosts all serving
  the identical article *"After Years of Struggling with Low Engagement, I Discovered
  SEOExpress.org's Affordable Link-Building Services"*; 7 hosts on
  `/dir/quality-authority-backlinks-148096`; `cgpa2percentag.com` titled
  *"🏆🏆Boost your Google rankings with Premium PBN & Link Building🏆🏆"*; `plavo.shop`,
  `seostock.shop`, `swiftlinkpro.shop` all serving generated link-vendor sales copy.
- **1 borderline** — `bizscoreai.com`, an AI-generated Georgia business directory (16 nofollow links).
- **Random-sample FP rate: 0–4 %.**

That number is however **not informative**, because the flagged population is ~96 % mass network.
A random sample mostly re-samples the same three clusters.

### 3.2 Stratified review — where the errors actually are

Partitioning all 1,139 flagged domains by whether any title/anchor/URL carries explicit
SEO-link-vendor vocabulary:

| stratum | domains | verdict |
|---|---|---|
| Carries vendor vocabulary | 1,089 (95.6 %) | true positive by construction — the page *says* it sells links |
| Heterogeneous tail | 50 (4.4 %) | hand-reviewed, one by one |

Hand review of all 50:

- **24 true positives.** Three further networks, each with a clean fingerprint:
  11 hosts titled `👲 Domain Report 👲` / `✅ Website Stats 📊` sharing paths `/report/97119-20`,
  `/stats/97119-20`; 3 hosts (`allinone.co.in`, `findit.co.in`, `topbillion.net`) sharing
  `/domains/192447/<hash>/`; the scraped domain-list family (`domaindexer.com`, `itsyourgold.com`,
  `domains.com.bz`). Plus five **topically impossible injections** — anchor *"Window Replacement
  Company Atlanta"* on `intermeritocracy.com`'s *"Thriving Economy of China"*, anchor *"Windows
  Atlanta"* on `monetaryhistoryofworld.com`'s *"Part III – 1154-1470"*, plus
  `worldbusinesspromote.com` (*"Makita: A Global Leader in Power Tools"*), `marketingexperts.click`
  (*"Artie Lange: Laughter, Pain..."*) and a `dreamscometroup.com` comment page. And
  `whosmypro.com` / `homeownerideas.com`, below.
- **23 false positives.** Ordinary aggregators and one genuine article: `brandfetch.com` (DR 73,
  brand-asset directory), `prospeo.io` (DR 73, email-format lookup), `clientsbee.com` (tech-stack
  lookup), `prosgrade.com`, `nearmelisting.com`, `struvia.co` (carries the real phone number
  `(770) 888-1604`), `robuta.com` and `gnomit.com` (SERP mirrors), `ssreteam.com` (a real estate
  team's genuine *"Our Preferred Vendors"* page), `alpharettatoprated.com`,
  `chattanoogatoprated.com`, `atlantatoprated.com`, `cityvetted.com`, `findlocalexperts.com`,
  `bestaround.com`, `revaliew.com`, `repairhomeexperts.com`, `localshutters.net`, `mailbat.com`,
  `bizscoreai.com`, `100xrecruiting.com`, `hghomeclub.com` (a podcast episode about the business),
  and **`missfrugalmommy.com` — a genuine `Article > How-to`, *"How To Secure Your Family Home"*,
  dofollow in-copy citation.** Flagging that one is a plain classifier error.
- **3 unassessable** (no live link row): `jake.eu`, `spottedcow.media`,
  `review-link-system-link-baron.store` (the last is self-evidently the vendor network by name).

### 3.3 Measured rates

- **Tail FP rate: 23 / 47 assessable ≈ 49 %.**
- **Overall FP rate: 23 / 1,136 ≈ 2.0 %.**
- **FP rate on the slice that governs the disavow (spam ∧ dofollow): 10 / 336 = 3.0 %.**
  All 10 are excluded from the file and listed by name in its NOT-DISAVOWED section.

**Conclusion:** the flag is reliable on mass networks and unreliable on individual aggregator pages.
It is safe as a *clustering* signal and unsafe as a *decision* signal. Used here as (e) only.

### 3.4 The flag also under-fires — and that is the worse error

Sanity-checking the 218 `Is spam = false` domains (Task 6) surfaced **23 carrying SEO-vendor
vocabulary**:

- **17 dofollow** domains on the *"Where to buy 🚀 aged domains and backlinks 🔥"* network —
  the same two page-IDs (`3496-2460`, `6137-4602`) that Ahrefs *did* flag on 9 sibling hosts.
  **Ahrefs flagged 9 of 26 members of one network: a 65 % miss rate.** The 17 are in Section 4 of
  the file, included on **(c) + (d) alone**, explicitly annotated `Ahrefs did NOT flag it`.
- **6 nofollow** vendor pages (`seo-high-ranking.shop` DR 52, `kawaiishop.shop`,
  `thehighseoranking.shop`, `verified-digital-firm-seoexpress.store`, plus `revan-me.com` and
  `sblmerchant.com` titled *"🛸 Dark Side Links – Dark/White Hat Link Building Services"*).
  Excluded — nofollow.

**Keep-list false-negative rate: 23 / 218 = 10.6 %.** This is why the keep-list was not simply
adopted as written.

Keep-list spot checks that **passed**: `bizlistusa.com` / `businesslistus.com` share the exact path
`/business/5067660.htm` across 3 hosts and are dofollow — a shared-path fingerprint — but the
geography is correct (Roswell, GA), the subdomain structure is an ordinary city index, and the link
is an image link with an empty anchor. **Kept.** Also kept: `bbb.org`, `crunchbase.com`,
`glassdoor.com`, `yellowpages.com`, `expertise.com`, `fixr.com`, `qualifiedremodeler.com`,
`housedigest.com`, `moneytalksnews.com`.

---

## 4. Semrush ↔ Ahrefs reconciliation (Task 2)

Overlap 338; Semrush-only 894; Ahrefs-only 1,019. Largely disjoint views, as established.

### 4.1 The current 5-entry file — all 5 survive

| domain | in Ahrefs | Ahrefs spam | dofollow cand | verdict |
|---|---|---|---|---|
| `backlinksseochecker.space` | yes | true | yes | KEEP (Section 1) |
| `onlinewebsitechecker.space` | yes | true | yes | KEEP (Section 1) |
| `dapaseochecker.online` | no | – | – | KEEP (Section 6, Semrush anchor) |
| `seostrengthchecker.online` | no | – | – | KEEP (Section 6, Semrush anchor) |
| `siteseocheckerfree.store` | no | – | – | KEEP (Section 6, Semrush anchor) |

### 4.2 The ~87 earlier candidates — all 87 survive, but mostly unconfirmable

- **87 / 87** pass the stricter word-boundary re-test on `links_raw.tsv`: dofollow row whose anchor
  names `ngwindows.com` in vendor copy. The prior pass's criterion holds under tightening.
- **Only 10 of the 87 appear in Ahrefs' refdomains at all.** Of those 10, **10/10** are
  `Is spam = true` **and** in the dofollow candidate set.
- Across *all* Semrush domains passing the strict test, **31 also exist in Ahrefs — and 31/31 are
  Ahrefs spam ∧ dofollow. 100 % agreement wherever both tools see the domain.**

That is the reconciliation result worth quoting to a reviewer: the two tools never disagree on this
class; they simply crawl different hosts. So the 77 Semrush-only members of the 87 are **retained**
— Ahrefs' silence on them is absence of coverage, not exoneration.

### 4.3 The prior pass also *under*-counted, in both directions

- **Ahrefs side:** campaign `148096` is not 87 domains, it is **258** (516 dofollow links, one
  unique path, one unique title). Section 1.
- **Semrush side:** the strict test finds **117** Semrush-only domains, i.e. **40 the prior pass
  missed** — including three of its own five file entries, plus a block of casino/escort/misc hosts
  (`bestirishcasinoonline.online`, `casinooftheking.com`, `gumushaneescorton.shop`,
  `sidarma88gacor.shop`, `betwinnermirror.com`, …) carrying the Section 2 and Section 3 anchors.
  Section 6.

### 4.4 777 Semrush-only domains deliberately excluded

They carry no dofollow anchor naming `ngwindows.com`. Many carry vendor anchors naming a **shell**
(`ngawindows.com`, `roiwindows.com`, `performingwindows.com`, …). Under default-to-exclusion they
stay out — and see §6, which removes their evidentiary basis anyway.

---

## 5. How the spam is actually placed (Task 3 — new capability)

`Left context` / `Right context` are **empty on 516 of 516** Section 1 links and on essentially the
whole vendor population. There is no surrounding sentence. That is itself the finding: these are not
in-copy citations, they are **bare list items on generated listing pages**.

Corroborated by `Page type` across the 809 candidate links:

| Page type | links |
|---|---|
| Listing > Business | 404 |
| Listing > Service | 112 |
| Listing > Product | 60 |
| Listing collection > Service | 49 |
| Listing collection > Business | 46 |
| Article > * (all kinds) | 26 |
| everything else (blank 97, Site page > Home 7, Landing > Service 4, misc 4) | 112 |

**671 of 809 are listing pages.** `Page category` is *"Internet > Web services > SEO and marketing;
Business > Marketing > Marketing"* on 544. `Platform` is blank on 788/809 — bespoke generated sites,
not CMS installs. 21 are WordPress.

Placement taxonomy, with counts:

| mechanism | links | domains | evidence |
|---|---|---|---|
| **Directory injection into a mirrored vendor catalogue** | 516 | 258 | one path `/dir/quality-authority-backlinks-148096`, one title, one anchor, 258 hosts |
| **Auto-generated vendor sales page** | 118 | 57 | generated title grammar — `{Trusted\|Proven\|Powerful\|Effective\|Reliable} + {PBN Backlinks\|Niche Edit Links\|Manual Outreach Backlinks\|White Hat SEO Links} + to {Raise Domain Rating\|Improve Citation Flow\|Increase Trust Flow}`; `Page type` mislabelled `Article > Guide` on 26 of them |
| **Marketplace inventory listing** | 53 | 26 | ngwindows.com inside a scraped alphabetical run: `ngwind.com ngwindow.com │ **ngwindows.com** │ ngwindsong.com ngwindsongk.com` |
| **City-permutation doorway directory** | 133 | 1 | `whosmypro.com`, 133 `Doors & Windows Near <CITY>, GA` pages, anchor `↗ Go to company website` |
| **Fabricated-geography directory** | 4 | 1 | `homeownerideas.com`, *"North Georgia Replacement Windows **Roswell New Mexico**"* |
| **Topical injection into unrelated articles** | 24 | 4 | *China's economy* → "Window Replacement Company Atlanta"; *Monetary History of the World 1154-1470* → "Windows Atlanta"; *Makita power tools*; *Artie Lange*; comment spam counted separately below |
| **Comment spam** | 1 | 1 | `dreamscometroup.com/bio/1428-2/comment-page-41` |

Note the last two rows are **all nofollow** and therefore excluded. The behaviourally most damning
evidence in the whole dataset attaches to links that pass no PageRank.

---

## 6. Redirect chains — every third-party redirect in the export (Task 4)

812 of 2,665 links carry a redirect chain. Exhaustive extraction of every host in every chain that
is not `ngwindows.com` yields **exactly two hosts**:

**`atlantabestmedia.com` — 22 links. KEEP.**
```
https://atlantabestmedia.com/?post_id=12205&goto=EV0EC01MTBhNDAsSBBgeLXgzCzw
  → 303 → http://ngwindows.com/ → 301 → https://ngwindows.com/
```
Referring page `my-woodstock-canton-best-of-2025`, anchor `ngwindows.com`, `Is spam = false`,
dofollow. This is a local awards/press site using a **click-tracking redirect** on an outbound
editorial link — the `?post_id=&goto=` pattern is standard outbound-click instrumentation, and the
303 is the tracker's own hop. Not a cloaking shell.

**`bizhwy.com` — 5 links. KEEP.**
```
https://www.bizhwy.com/visit.php?biz=7329&state=Georgia → 302
```
Business-directory **interstitial**, anchor *"Visit the North Georgia Replacement Windows, Inc.
website"*, `Is spam = false`, and **`Nofollow = true`** — it passes nothing. Disavowing it would be
pointless as well as unjustified.

**The remaining 785 chains are ngwindows.com's own canonicalisation** — 759 a single `301`, 26 a
`301, 301` (http→https then non-www→www). No third party involved.

### 6.1 The 14 shells do not appear

`ngawindows.com` · `roiwindows.com` · `thermalprowindows.com` · `qualitypluswindows.com` ·
`northpointwindows.com` · `performingwindows.com` · `thermatrustwindows.com` ·
`northgeorgiawindows.net` · `thermalastwindows.com` · `e2windows.com` · `choiceviewwindows.com` ·
`ngwindow.com` · `northgawindows.com` · `northgeorgiawindow.com`

**Zero occurrences in any `Redirect Chain URLs` value.** Raw string matches across the whole file:
12 of the 14 return 0. `ngwindow.com` returns 49, all of which are alphabetical domain-list context
on the Section 4 marketplace pages. `qualitypluswindows.com` returns 1, a URL *path segment* on
`justgotlive.com/es/site/qualitypluswindows.com`.

**Consequence.** `FINAL-AUDIT.md` §5 and `recheck-disavow.md` §3.2 rest on Semrush crediting
shell-borne links to `ngwindows.com` via 301. Ahrefs resolves redirect chains and publishes them,
and credits **none**. Either the shells do not redirect into `ngwindows.com`, or Ahrefs does not
follow them for attribution. Both readings are consistent with this export; it cannot distinguish
them. Either way the prior pass's **"~279 redirect-borne dofollow domains"** and the
**"delete the redirects"** recommendation have **no corroboration in the better dataset**. Flagged
as unresolved in the file; nothing has been acted on.

---

## 7. High-DR spam (Task 5)

632 flagged domains are DR ≥ 30 — but **only 7 of those 632 have any dofollow link at all**. The
high-authority spam is almost entirely nofollow (the 577-host `SEOExpress.org` network sits at
DR 44–52 and passes nothing). After excluding nofollow and false positives, **3 of the 343
Ahrefs-side entries are DR ≥ 30**:

| domain | DR | links | quoted evidence |
|---|---|---|---|
| `m98ufa.com` | 50 | 2 dofollow | page `/all/947/16.html`; anchor *"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service **ngwindows.com** Rank First Page Google"*; the anchor advertises a PBN and names the target |
| `tokyopush188.online` | 42 | 2 dofollow | page `/backlink-network/powerful-tiered-link-building-to-raise-domain-rating-...`; anchor *"Trusted High DA Backlinks for **ngwindows.com** to Raise Domain Rating"*; URL path contains `backlink-network` |
| `betulcrime.com` | 40 | 2 dofollow | page `/all/2066/26.html` — **a path shared byte-for-byte with 17 other hosts**; title *"🏆🏆Boost your Google rankings with Premium PBN & Link Building🏆🏆"*; same PBN anchor |

Highest-DR Section 4 entry is `domains.com.bz` (DR 28), on the `/page/168196/` fingerprint it shares
with `itsyourgold.com` (DR 0) — same page, two hosts, which is the point.

**In none of these three is DR a ground.** Each is listed on anchor + dofollow + title, and
`betulcrime.com` additionally on an 18-host shared path. The file reproduces this table verbatim so
a reviewer meets the strongest evidence first.

---

## 8. Final file structure and recommendation

| section | basis | entries |
|---|---|---|
| 1 — campaign `148096` | (a)+(b)+(c)+(e) | 258 |
| 2 — PBN vendor pages | (a)+(b)+(d)+(e) | 43 |
| 3 — "High DA backlinks" vendor pages | (a)+(b)+(d)+(e) | 14 |
| 4 — aged-domain marketplace | (b)+(c)+(d) — **17 of 26 without Ahrefs' flag** | 26 |
| 5 — auto-generated directory injection | (b)+(c)+(e) | 2 |
| 6 — Semrush-only, independently evidenced | (a)+(b) from `links_raw.tsv` | 117 |
| **total** | | **460** |

**Recommended final entry count: 460.**

Fallback positions, in order of conservatism, should the reviewer want to trim:

- **434** — drop Section 4 wholesale. It is the weakest *motive* tier (the operator sells domains;
  the link to ngwindows.com is inventory, not promotion) even though the behavioural evidence is
  solid. It is deliberately built to detach cleanly.
- **432** — also drop Section 5. `whosmypro.com` is the single most challengeable entry in the file:
  133 dofollow links from city-permutation pages is a doorway pattern, but legitimate local
  directories do build city pages, and nothing beyond volume and templating distinguishes it.
- **343** — Ahrefs-evidenced only, dropping all 117 Semrush-only entries. Defensible if the reviewer
  decides `links_raw.tsv`'s missing `target_url` column makes anchor-only evidence insufficient.
  I do **not** recommend this: 31/31 agreement wherever both tools overlap (§4.2) is strong
  corroboration that the Semrush anchor test identifies the same population.

### Carried-forward open items

1. The redirect-shell model (§6.1) is unresolved and cannot be resolved from committed data.
   Re-run after 2026-10-25 with Site Explorer, or fetch the 14 shells directly and record the
   `Location:` header.
2. No page was fetched at build time. Liveness is as of each export's last-seen date.
3. `missfrugalmommy.com` is proof the classifier mislabels genuine editorial content. If any
   Section 1–3 entry is ever challenged individually, re-read its own quoted anchor before
   defending it on the flag.
