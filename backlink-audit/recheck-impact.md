# Independent Re-check: Traffic-Impact Claims, ngwindows.com

**Reviewer:** second-pass verification, independent of the analyst who produced
`impact-and-recovery-roadmap.md` and `FINAL-AUDIT.md`.
**Date:** 6 October 2026
**Method:** re-analysis of the audit's own evidence (`data/refdomains.csv` first_seen timestamps,
`data/anchors_observed.csv`, the 30-month Semrush series), plus external dating of Google
algorithm updates and the AI Overviews rollout. Ahrefs free Domain Rating endpoint used for
spot checks (zero units). **No new traffic data could be pulled** — Semrush units are at zero
and Ahrefs Site Explorer is locked until 25 Oct 2026. This is a review of reasoning, not a re-pull.

**Posture.** The audit's central message to the client is reassuring: *the frightening thing we
found is not what hurt you, and since it started you have actually gone up.* A reassuring
conclusion carries a higher burden of proof than an alarming one, because it is the conclusion
that ends the investigation. I have applied that higher burden throughout.

**Headline:** the audit's two load-bearing reassurances — **"the spam did not cause it"** and
**"+45% since the blast"** — are both weaker than presented. The first is contradicted by the
audit's own anchor-forensics table. The second is almost certainly seasonality. And the single
best-dated explanation of the collapse — **the June 2025 Google core update, which ran 30 Jun –
17 Jul 2025, precisely spanning the −36.5% break** — does not appear anywhere in the audit.

---

## 1. Claims that survive scrutiny

### 1.1 "Organic traffic has collapsed catastrophically" — SURVIVES (magnitude slightly over-stated)
Direction and order of magnitude are not in doubt. Every independent line in the series moves the
same way: Semrush Rank 55,310 → 331,548, positions 1–3 from 278 (Aug 2024) to 78 (Sep 2026),
organic keywords 6,668 → 4,180. A measurement artifact would not move all four coherently for
two years. **The business has lost roughly four-fifths of its organic traffic. That is real.**

The precise **−87.7%** is anchored on a suspicious peak (see §2.1). A more defensible framing is
**−79% to −81% against a 2024 trailing average (~26,000/mo)**. This does not change the
conversation, and the audit should not retreat from the severity — only from the decimal place.

### 1.2 "The blast itself has not yet produced measurable incremental damage" — SURVIVES, for now
This is correct but for a reason the audit under-weights rather than the one it gives. The
velocity table in `ngwindows-backlink-audit.md` §5 shows referring domains essentially **flat at
560–590 from Dec 2025 through Jun 2026**, then 849 (Sep) and 1,225 (Oct). The volumetric blast is
a **September–October 2026** event. Sep 2026 traffic data therefore *cannot* contain its effect —
Google's link-spam systems and core-update reprocessing operate on a lag of weeks to months.
"No damage yet" is a statement about **timing of measurement**, not about safety. The audit's own
Phase 3 says this; the executive summary does not, and the executive summary is what the client
reads. **Correct the summary.**

### 1.3 "ngwindows is ranking for its own name, not for its market" — SURVIVES, and is the strongest finding in the audit
Homepage + GBP variant = 60.6% of traffic; branded terms ~54% of visits; all four service-area
pages combined = 111 visits/month (2.3%); `window replacement atlanta` ($41.02 CPC) stranded at
position 15; `/windows` absent from the top 20 pages. This is internally consistent, is not
dependent on any contested baseline, and is commercially actionable regardless of what caused
the collapse. **This should be the lead of the client conversation, not §3 of a roadmap.**

### 1.4 "82.4% junk referring domains is not anomalous for this niche" — SURVIVES
74.9% (Window World Atlanta) and 80.4% (Davis) is a genuine control group. A 4–8 point deviation
is not a smoking gun. Good correction of the original audit; keep it.

### 1.5 "The anchor text is the real evidence, not the junk ratio" — SURVIVES
Agreed, and see §2.2 — it is stronger evidence than the audit realises, and it points the
opposite way from the audit's conclusion.

---

## 2. Claims that are artifacts, over-read, or contradicted by the audit's own data

### 2.1 🔴 The "−87.7% from a 40,569 peak" and the "−36.5% Jun→Jul 2025 break" both rest on two anomalous data points

Look at what the series says *around* each of the two anchor months:

| Month | Traffic | Organic KW | Pos 1–3 | Pos 4–10 |
|---|---|---|---|---|
| Jun 2024 | 27,546 | 6,886 | **307** | 412 |
| **Aug 2024** | **40,569** | 6,668 ↓ | **278 ↓** | 453 |
| Oct 2024 | 19,888 | 6,491 | 225 | 400 |
| Feb 2025 | 20,297 | 4,912 | 219 | 325 |
| Apr 2025 | 11,908 | 5,278 | 162 | 290 |
| **Jun 2025** | **24,194** | **7,507 (series max)** | 180 | **605 (series max)** |
| Jul 2025 | 15,372 | 6,578 | 173 | 465 |

- **Aug 2024 "peak":** traffic +47% over Jun 2024 while **organic keywords fell and positions 1–3
  fell**. Traffic cannot rise 47% on fewer keywords and fewer top-3 rankings unless a single
  high-volume term was re-estimated. This has the signature of a Semrush volume refresh, not a
  real 13,000-visit gain that then evaporated in eight weeks.
- **Jun 2025 "last strong month":** +103% over Apr 2025, against +15.5% for the same Apr→Jun step
  in 2024 — and it carries the **highest keyword count and highest position 4–10 count in the
  entire 30-month series**, both of which snap back the following month. Same signature.

**Consequence.** The audit's two most quoted numbers are each computed *from* a spike. Substitute
a seasonally normal Jun 2025 (~13,700) and the celebrated "sharpest break in the series,
Jun→Jul 2025 −36.5%" becomes **+12%** — it disappears entirely. On that reading the real step-change
is **Feb 2025 → Apr 2025 (20,297 → 11,908, −41%)**, which lands on the **March 2025 core update
(13–27 March)**.

Either reading points at a Google core update. But the audit built its exoneration timeline on
a single month it never stress-tested. **Any claim of the form "the break was precisely here"
should be withdrawn** until GSC — which measures clicks, not modelled visits — confirms it.

### 2.2 🔴 THE CRITICAL FAILURE: the causal exoneration is contradicted by the audit's own anchor table

The argument is: *first spam link = 29 Jun 2026; collapse ran Jun 2025 – May 2026; therefore
the spam did not cause the collapse.* The premise is false as stated. The audit's own
`ngwindows-backlink-audit.md` §4 anchor table contains two clusters:

| Anchor cluster | Links | First seen |
|---|---|---|
| "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN…" (Network A/B sales copy) | 905 | **29 Jun 2026** |
| **Bare sister/competitor domain names as anchor** (`ngawindows.com`, `roiwindows.com`, `thermalprowindows.com` +11 more) | **2,579** | **Jul 2025 → ongoing** |

**The 29 Jun 2026 date describes the smaller cluster. The larger cluster — 2,579 links, nearly
three times the size — is dated by the audit itself to July 2025: the exact month of the break
the audit says had no link event.** The exoneration is produced by quoting the later of two dates
in the audit's own table.

Three further confirmations from the raw `refdomains.csv`, which I re-parsed independently:

1. **Link-vendor-named domains are live in the collapse window.** Domains first seen Jul–Sep 2025
   include `backlinksolutions.info`, `rankvanceseo.info`, `rankvanceboost.info`, `jobsapp.info`,
   `sergechel.info`, `monetaryhistoryofworld.com`. These are not scraper farms that index every
   contractor; `backlinksolutions.info` and `rankvanceseo.info` are named after the service they
   sell. **Paid link activity was demonstrably live in July 2025, eleven months before the audit's
   claimed first spam link.**
2. **The sister-domain cluster itself predates the collapse.** `ngawindows.com`, `roiwindows.com`,
   `northpointwindows.com`, `qualitypluswindows.com`, `thermatrustwindows.com` (Jul 2024),
   `performingwindows.com` (Aug 2024), `thermalprowindows.com`, `northgeorgiawindows.net`
   (Sep 2024), `doorswindowscompany.com` (Nov 2024) — all AS 2, all DR 0 (confirmed via the free
   Ahrefs endpoint), all 3–6 links each. They arrive **at the Aug 2024 peak**, i.e. the moment the
   decline starts.
3. **AS 0–5 inflow ramped from October 2025, not June 2026.** Monthly new AS 0–5 referring domains
   from first_seen: Sep 2025 = 5, **Oct 2025 = 13, Dec 2025 = 21, Jan 2026 = 21, Feb 2026 = 23,
   Mar 2026 = 55, Apr 2026 = 33**, then Jun 2026 = 21 → Sep 2026 = 273 → Oct 2026 = 411. The
   low-quality inflow was already running at 20–55/month throughout the second half of the
   collapse. The June 2026 "start" is visible in the chart only because the Sep/Oct spike
   compresses everything before it.

**A fourth, structural problem the audit never flags:** `refdomains.csv` is a snapshot of
*currently live* referring domains. **Links that arrived and were removed before 6 Oct 2026 do
not appear in it at all.** You therefore *cannot* establish a "first spam link" date from this
file in either direction. The audit treats absence of 2024/2025 spam in a live-links snapshot as
evidence of absence. It is not.

**Verdict: the exoneration does not hold.** I am not asserting the spam caused the collapse —
I doubt it is the main driver (see §3). I am asserting that **the audit has not established that
it didn't**, and has told the client it has. That is the most serious defect in the document.

### 2.3 🔴 "+45.4% since the blast began" is a seasonal pattern, not a recovery

This is a window-replacement contractor in Georgia. Index each year's Jun→Sep run to Jun = 100:

| | Jun | Jul | Aug | Sep |
|---|---|---|---|---|
| **2024** | 100 (27,546) | — | **147** (40,569) | — |
| **2025** | 100 (24,194) | 64 | 53 | 42 |
| **2026** | 100 (3,420) | 104 | **150** (5,139) | 145 (4,971) |

**2024 and 2026 produce an essentially identical Jun→Aug index: 147 and 150.** Two independent
years of the same company show the same ~+50% summer lift. 2025 is the exception, and 2025 is the
year a core update landed on 30 June. The audit's "+45.4%" is **the ordinary summer shape of this
business**, measured from the month that happens to be the seasonal floor.

Two further points that dissolve the claim:
- **Jun 2026 is also the month immediately after the May 2026 core update** (21 May – 2 Jun 2026).
  The trough has an algorithmic cause and a seasonal cause; it needs no link-related cause at all.
- **Traffic has already turned down again**: Aug 5,139 → Sep 4,971 (−3.3%), and Aug→Sep fell in
  2025 too (−20%). The "+45%" is already rolling over.

**This claim should be struck from the client-facing summary entirely.** Presenting a normal
summer lift as evidence that a spam attack is harmless is the single most misleading sentence in
the audit. If the client acts on it and defers the disavow, and the Sep/Oct volumetric blast
(+266, +376 domains) does score, they will have been talked out of the one defensive action
available to them, on the strength of the weather.

### 2.4 ⚠️ The AI Overview hypothesis is plausible but its stated evidence does not support it

Each of the three cited data points fails as evidence:

- **"907 keywords, 225 visits is a classic ranks-broadly-earns-nothing profile."** It is a classic
  *long-tail* profile. Semrush attributes keywords down to position 100; a page holding positions
  40–90 on 700 near-zero-volume terms earns zero from all of them, with or without AI Overviews.
  The audit's own table contains a tighter anomaly it did not notice — `/service-areas/marietta-ga`
  holds **159 keywords for 55 visits (0.35/kw)** versus standard-door-sizes' 0.25/kw. The ratios
  are the same order of magnitude. **907/225 is not anomalous; it is arithmetic.**
- **"The informational cluster is 22% of traffic."** This is a *share* statistic. It tells you the
  blog matters; it tells you nothing about whether the blog is the thing that fell. If anything,
  it cuts the other way: **60.6% of traffic is branded homepage/GBP**, so at most 22% of current
  traffic is exposed to AIO — and the site lost ~80%. Killing the entire informational cluster
  cannot produce an 80% decline.
- **"The timing (Jun–Jul 2025) aligns with AI Overview rollout."** It does not. **AI Overviews
  launched to all US users on 13–14 May 2024** — three months *before* this site's all-time peak,
  and twelve months before the claimed break. By Jun 2025 AIO had been live in the US for over a
  year. The May 2025 I/O expansion was mostly international. **The stated timing argument is
  backwards.**

AIO click erosion is real (Pew: 8% vs 15% click rate; a randomised field experiment measured −38%
on affected queries) and is near-certainly *a* contributor here. But it is a slow, continuous
pressure, and the audit is using it to explain a **step change** — which is the one shape it does
not produce.

### 2.5 ⚠️ The competitive benchmark does not support "links are not the bottleneck"

The comparison is not like-for-like in three ways the audit does not mention:

1. **Window World Atlanta is a franchisee of windowworld.com, which I measured at Ahrefs DR 61.**
   It inherits national brand demand, a national entity, and internal link equity from a domain
   three times its own authority. Comparing it to an independent contractor on *referring domain
   count* is comparing a franchise outlet's marketing to a standalone's.
2. **The two sites are being compared at the moment a crashing line crosses a flat one.** ngwindows
   is at 4,971 *on the way down from 40,569*. At its peak it beat WWA roughly **8.5 to 1** on
   traffic, with a broadly similar link profile. That fact is fatal to the audit's framing in both
   directions: ngwindows' traffic was *never* link-driven (it was blog volume), so a link-based
   comparison was never going to diagnose its loss — and equally, "we have more links and the same
   traffic" is not a finding about links, it is a finding about a collapse the benchmark cannot see.
3. **"65 AS≥30 domains vs 34" counts domains, not value.** A profile where ~820 of 1,232 referring
   domains arrived in the last twelve months, overwhelmingly AS 0–5, and where Authority Score
   **fell 33 → 30 while the link count tripled**, is not a stronger profile than a smaller clean
   one. The audit reports the AS decline in §5 of the backlink audit and then asserts link
   superiority in §4.3 of the roadmap without reconciling the two.

Of the three readings available — *(a) links are not the bottleneck, (b) ngwindows' links are
lower-value per domain, (c) ngwindows is being algorithmically suppressed relative to its link
profile* — the audit selects (a), the only one that requires no further investigation. (b) is
directly supported by the AS 33→30 drift; (c) is consistent with a core-update demotion. **(a) is
the least-supported of the three, not the best-supported.**

### 2.6 ⚠️ The audit contradicts itself on whether links matter
§2.3 of the roadmap: *"no amount of link building will fix it."* §3.3, one page later: positions
15–20 is *"exactly what a clean, local, topically-relevant link campaign fixes… the single best
argument for the rebuild programme."* §4.3: *"not losing locally because of a link deficit."*
These cannot all be true. A client reading the document cannot tell what is being recommended or
why. (They are reconcilable — links won't restore *blog* traffic but may move *commercial* terms —
but the document never says so.)

### 2.7 ✅ One finding the audit itself buries, which I confirm and would promote
`audit-review-and-gaps.md` §4.3: the site is **losing genuine links while gaining spam** —
`gnpmilton.com` (DR 26, confirmed, a local podcast episode about the principal by name),
`atlantahomeimprovement.com` (**DR 45**, confirmed, local, on-topic, linking since 2023),
`atlantaunitedsoccer.com`, `csswinner.com` (DR 75, ×4). I verified the two key DRs independently.
This is small relative to an 80% collapse, but it is the cheapest item on the board and it is
absent from the 12-point action plan.

---

## 3. My ranked explanation of the collapse, with confidence

The audit considers essentially one hypothesis and labels it unconfirmed. Here is a ranked field.
**I could not fetch ngwindows.com or archive.org from this environment — the network egress proxy
blocks both — so hypotheses 5 and 6 are untested, not excluded.** That is a real gap and it is
flagged as such below.

### #1 — Sequential Google core and spam updates. Confidence: HIGH (~60–65%)
Not mentioned anywhere in the audit. Dating the confirmed updates against the series:

| Google update (confirmed dates) | Next reported month | Traffic move |
|---|---|---|
| **March 2025 core** (13–27 Mar 2025) | Apr 2025 | 20,297 → **11,908 (−41%)** |
| **June 2025 core** (30 Jun – 17 Jul 2025) | Jul 2025 | 24,194 → **15,372 (−36.5%)** |
| **August 2025 spam update** | Aug–Sep 2025 | 15,372 → 12,839 → **10,231** |
| **December 2025 core** (11–29 Dec 2025) | Dec 25 / Feb 26 | 8,375 → 7,225 → **6,026** |
| **March 2026 spam (24–25 Mar) + March 2026 core (27 Mar – 8 Apr)** | Apr 2026 | 7,188 → **6,014** |
| **May 2026 core** (21 May – 2 Jun 2026) | May–Jun 2026 | 6,014 → 4,360 → **3,420 (trough)** |

**Every single step-down month in the thirty-month series falls in the month of, or the month
after, a confirmed Google core or spam update.** The June 2025 core update ran **30 June to
17 July 2025** — it does not merely "align with" the Jun→Jul break, it *is* the Jun→Jul window.
A site that is ~80% thin informational blog content with a weak commercial core is precisely the
profile the 2025 core updates demoted. This explanation also accounts for what AIO cannot: the
**step** shape, and the **Jan 2026 partial rebound** (8,692, a classic post-update re-shuffle).

I withhold the remaining ~35% because the match is correlational, the pre-Jun-2025 series is
bi-monthly (so I cannot resolve within-month timing), and I could not inspect the site.

### #2 — AI Overviews / zero-click erosion of the informational cluster. Confidence: MEDIUM (~40–45%) as a *contributing* factor; LOW (<10%) as the *primary* cause
Real and well-evidenced as a phenomenon. But it is gradual, it had been live in the US since
May 2024 (before the peak), and it can only touch the ~22% of traffic that is informational.
It plausibly explains why the site never recovered between core updates. It cannot explain a −80%
step sequence on its own. **Concurrent with #1, not an alternative to it** — the June 2025 core
update and AIO expansion both hit thin informational content, which is exactly why they are hard
to separate without GSC.

### #3 — Measurement artifact inflating the headline. Confidence: MEDIUM-HIGH (~55%) that it accounts for 10–20 points of the quoted −87.7%
See §2.1. Does not change that a severe decline happened; does change the numbers in the deck.

### #4 — Link-related demotion. Confidence: LOW-MEDIUM (~20–25%) for the 2025 phase; MATERIAL AND UNMEASURED for the Sep/Oct 2026 phase
Downgraded, not dismissed. For the 2025 collapse: a 2,579-link bare-domain anchor cluster dated
**Jul 2025** (the break month), vendor-named `.info` domains live from Jul 2025, AS 0–5 inflow
at 20–55/month from Oct 2025, and Authority Score drifting 33 → 30 while links tripled. Google's
link systems typically *neutralise* rather than demote, which is why I keep this below #1 — but
the August 2025 spam update, which sits mid-collapse, is specifically a demotion mechanism.
**Separately: the Sep–Oct 2026 blast (+266, +376 domains, 1,225 total) is not yet in any traffic
data and must be treated as a live, unquantified risk.**

### #5 — Site migration, redesign, or technical breakage in the Jun 2025 window. Confidence: UNKNOWN — NOT TESTED
**This is the most important untested hypothesis and the audit does not raise it at all.** A
CMS migration, URL restructure, or robots/canonical error in June 2025 would produce exactly the
observed shape — a one-month step with keyword counts holding and traffic falling. The pattern
`/windows` ranking #11 for "infinity windows" yet earning **zero** traffic, and being absent from
the top 20 pages entirely, is also consistent with a page that was broken, noindexed, or
re-pathed. **This must be checked before any causal statement is made to the client.** It is a
ten-minute check with GSC access and an archive.org comparison of May vs August 2025 snapshots.

### #6 — Google Business Profile suspension. Confidence: LOW (~5%)
Largely excluded by the data already present: the GBP-tagged homepage variant still delivers
**777 visits/month (16.1%)**. A suspension would have zeroed it. Worth a one-line confirmation,
no more.

---

## 4. What the client should actually be told about cause

Replace the current framing. The honest version:

> **Your organic traffic is down roughly 80% from its 2024 level.** That is real, it is severe,
> and it happened over about eighteen months, not overnight.
>
> **We do not yet know the cause with confidence, and anyone who tells you otherwise is guessing.**
> What we can say is that **every major drop in your traffic lands in the month of, or the month
> after, a confirmed Google algorithm update** — March 2025, June–July 2025, August 2025,
> December 2025, March 2026, May 2026. The most likely explanation is that Google re-weighted
> against the kind of content that was carrying most of your traffic: general informational blog
> posts, on which you ranked broadly and earned little. The parallel rise of AI answers in search
> results pushes in the same direction. Those two forces are hard to separate without your
> Search Console data, which we have not yet seen.
>
> **On the spam links: we are not able to clear them, and we should not pretend to.** An earlier
> read of this data concluded the spam arrived after the decline and was therefore blameless. On
> re-examination that is not supportable: our own anchor analysis dates a **2,579-link** cluster
> to **July 2025** — the exact month of the sharpest drop — and link-vendor domains were attaching
> to your site from mid-2025. The spam is probably **not** the main cause. But "probably not the
> main cause" is where the evidence stops, and it is not the same as "not a factor."
>
> **The recent uptick is summer.** Traffic rose 45% from June to September 2026. It also rose 47%
> across the same months in 2024. You are a window company in Georgia; summer is your season.
> Please do not read that number as recovery — it has already turned down again (August 5,139 →
> September 4,971).
>
> **The genuinely urgent item is the thing nobody has measured yet.** Your referring domains went
> from 590 in June to **1,225 in October** — they doubled in sixty days, almost entirely from
> junk, with other companies' names used as the link text. **None of that is in any traffic data
> we have seen**, because it is too recent. Disavow it now, as insurance, while we establish cause.
>
> **And here is the finding that will make you money regardless of cause:** 61% of your organic
> traffic is people searching for *you by name*. Your four service-area pages earn 111 visits a
> month between them. `window replacement atlanta` — $41 a click — sits at position 15, and your
> `/windows` page does not rank at all. **You are not competing for your market.** That is fixable,
> and it is fixable without first winning the argument about what happened in 2025.

---

## 5. The specific checks that would settle it

Ordered by decisiveness per unit of effort. Items 1–4 need only Google Search Console and
Google Analytics access — both free, both the client's own data, neither blocked by the API outage.

**Tier 1 — do these before any further analysis (together they settle cause, cost ≈ 2 hours)**

1. **GSC → Performance → Compare, 16-month window, Clicks *and* Impressions, filtered to `/blog/`.**
   The decisive test, and it separates #1 from #2 cleanly:
   - Impressions flat, clicks down → **AI Overviews / zero-click**. Link building will not fix it.
   - Impressions *and* clicks both down, in a step → **core-update demotion**. Content quality and
     site-level signals are the lever.
   - Impressions down but *average position* flat → **indexation or technical loss** (hypothesis #5).
2. **GSC daily clicks, 20 June – 31 July 2025, day by day.** The June 2025 core update ran
   30 Jun – 17 Jul 2025. If the fall begins on 30 June or 1 July and completes by mid-month, the
   core-update explanation moves from ~60% to near-certain. If it begins earlier or elsewhere in
   the month, #1 drops sharply and #5 rises. **This single chart is worth more than everything
   else on this list.**
3. **GSC → Pages, and GA4 landing-page report, May 2025 vs August 2025.** Did a set of URLs
   *disappear* (migration/redesign — hypothesis #5) or did surviving URLs merely lose clicks
   (algorithmic)? Cross-check against **GSC → Indexing → Pages** for a crawl/index drop in that
   window, and ask the client directly: *"did you change, rebuild, or re-platform the website at
   any point in 2025, and who did it?"* No tool answers this faster than the question does.
4. **GSC → Links → Top linking sites, and the Manual Actions and Security Issues panels.**
   Manual Actions is a yes/no on penalty — it takes five seconds and the audit never cites it.
   The linking-sites list is also the only source that shows links Google *knows about*, including
   ones Semrush and Ahrefs dropped from their live snapshots.

**Tier 2 — closing the gaps I could not close here**

5. **Fetch ngwindows.com and `/windows` directly, and pull archive.org snapshots for
   May / June / July / August 2025.** I was blocked by the network egress proxy on both
   `ngwindows.com` and `web.archive.org`. A redesign visible between the May and August 2025
   captures would be decisive for hypothesis #5 and would reorder this entire list. **Anyone with
   an unrestricted browser can do this in ten minutes — do it first.**
6. **Technical crawl of `/windows`** — status code, canonical, robots, `noindex`, internal link
   count. A commercial page ranking #11 on a 1,600/mo term and earning zero traffic is a specific,
   checkable anomaly, not a content problem.
7. **Re-run Ahrefs Site Explorer after 25 Oct 2026** with `history` on referring domains, and pull
   the **lost-links** report for Jun 2024 – Dec 2025. This is the only way to recover links that
   arrived and were removed, and it is the only way to test the "first spam link" date properly.
   Disavow the **union** of Ahrefs and Semrush domains, not the intersection.
8. **Pull the traffic *trend* for windowworldatlanta.com and daviswin.com**, not just their current
   level. If both are flat or rising while ngwindows fell 80%, the cause is site-specific
   (→ #1, #4, #5). If the whole local set fell together, it is SERP-level (→ #2). The audit
   benchmarked a single frozen moment; the trend is where the answer is.

**Tier 3 — ongoing**

9. **Weekly new-referring-domain count** while the blast is live. The Sep/Oct 2026 escalation is
   the one risk that is both unmeasured and still growing.
10. **Monthly GSC positions 1–3 count.** If it falls below 60 (from 78) in any single month after
    the blast, link demotion is scoring and the picture changes.

---

## 6. Summary scorecard

| # | Claim | Verdict |
|---|---|---|
| 1 | −87.7%, 40,569 → 4,971 | **Directionally sound; magnitude over-stated.** Peak is likely a Semrush artifact. Use −79–81% vs a 2024 average. |
| 2 | Collapse Jun 2025 – May 2026, sharpest break Jun→Jul 2025 (−36.5%) | **Over-read.** Computed from an anomalous Jun 2025 (series-max keywords and pos 4–10). Collapse is real; the precise break month is not established. |
| 3 | First spam link 29 Jun 2026 → spam didn't cause it | **🔴 FAILS.** The audit's own anchor table dates a 2,579-link cluster to **Jul 2025**. Vendor `.info` domains live from Jul 2025. AS 0–5 inflow ramping from Oct 2025. And a live-links snapshot cannot date a *first* link in either direction. |
| 4 | +45.4% since the blast; Jun 2026 is the trough | **🔴 SEASONAL ARTIFACT.** Jun→Aug index is 147 (2024) and 150 (2026) — the same summer lift. Jun 2026 also follows the May 2026 core update. Already rolling over (Aug → Sep, −3.3%). Strike from the summary. |
| 5 | AI Overviews ate the blog traffic | **Plausible contributor, badly evidenced.** 907/225 is normal long-tail, not an anomaly. 22% share cannot explain an 80% loss. AIO launched May 2024 — *before* the peak — so the timing argument is backwards. |
| 6 | 65 AS≥30 vs 34 → "links are not the bottleneck" | **Over-read.** WWA is a franchisee of a DR 61 national brand. Comparison taken at the moment a falling line crosses a flat one. AS fell 33 → 30 as links tripled. The most reassuring of three readings was chosen, not the best-supported. |
| 7 | `window replacement atlanta` pos 15; `/windows` absent; homepage+GBP 60.6% | **✅ SURVIVES — and is the most valuable finding in the audit.** Promote it to the lead. |

**The one sentence I would want changed above all others:** the audit tells the client the spam
"did not cause it." The evidence supports, at most, *"the spam is probably not the main cause of
the 2025–26 decline, and its largest phase is too recent to have been measured at all."*
The difference between those two sentences is whether the client disavows this month or next year.
