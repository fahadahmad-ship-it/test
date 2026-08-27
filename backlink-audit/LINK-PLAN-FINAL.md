# Final link plan — after critical re-check

Performance Lab · 2026-08-27 · **supersedes LINK-PLAN.md**

I re-examined every figure looking for contradictions rather than confirmation.
Three real problems surfaced. **Two of my four recommendations change.**

> **Constraint:** the Ahrefs and Semrush connections dropped part-way through
> this re-check, so everything below is from data already pulled and I could not
> re-query to settle the conflicts. Each one is flagged with exactly what to
> check manually.

---

## What the re-check found

### Problem 1 — I recommended a link to a page that may already rank #1

`/blogs/magnesium/magnesium-malate-vs-glycinate`. The two tools disagree about
which URL even ranks:

| Source | Keyword | Volume | Position | URL it credits |
|---|---|---|---|---|
| Ahrefs | magnesium malate benefits | 7,600 | **#3** | `/Magnesium` |
| Semrush | magnesium malate benefits | 9,900 | **#1** | `/blogs/magnesium/magnesium-malate-vs-glycinate` |

If Semrush is right, the page is already first and there is no position to buy.
**Recommendation withdrawn.** Verify in Ahrefs Site Explorer → Organic keywords
for that exact URL before considering it again.

### Problem 2 — my traffic estimate for the bisglycinate page was inflated

Comparing each term's search volume against its topic traffic potential exposes
how much of the SERP's clicks never reach organic results at all:

| Keyword | Volume | Topic potential | Ratio | Reading |
|---|---|---|---|---|
| rear delt fly | 81,000 | 7,600 | **9%** | Clicks leak to features |
| **magnesium bisglycinate** | **26,000** | **3,400** | **13%** | **Clicks leak to features** |
| magnesium malate benefits | 9,000 | 2,800 | 31% | |
| creatine before or after workout | 21,000 | 10,000 | 48% | Healthy |
| magnesium taurate benefits | 5,400 | 4,900 | 91% | Healthy |
| magnesium bisglycinate **vs glycinate** | 2,800 | 3,600 | 129% | Healthy |
| when to take creatine | 28,000 | 41,000 | 146% | Healthy |
| **best magnesium for sleep** | **29,000** | **63,000** | **217%** | **Best in the set** |

A ratio far below 100% means the winning page captures only a fraction of the
stated volume — AI overviews, shopping units and People Also Ask absorb the
rest. At 13%, "magnesium bisglycinate" is a much smaller prize than 26,000
suggests, and my earlier +468/month estimate was too high.

**This cuts both ways, and mostly in favour of the top recommendation.** At
**217%**, "best magnesium for sleep" delivers *more* than its head-term volume,
because the page that wins it also picks up a wide long tail. That is the
strongest signal in the entire dataset and it makes recommendation 1 safer, not
weaker.

### Problem 3 — the two tools disagree on position by 2–3 places

| Keyword | Ahrefs | Semrush |
|---|---|---|
| best magnesium for sleep | #9 | #7 |
| which magnesium is best for sleep | #8 | #5 |
| magnesium bisglycinate | #16 | #13 |
| creatine before or after workout | #17 | #14 |
| when to take creatine | #24 | #25 |

Not large enough to reorder anything, but every traffic projection below should
be read as a range, not a number. My CTR curve is also a generic one — on SERPs
this feature-heavy, real click-through is likely **lower** than modelled.

---

## Revised allocation

| Links | Full URL | Change |
|---|---|---|
| **3** | `https://www.performancelab.com/blogs/sleep/best-magnesium-for-sleep` | Unchanged — strengthened |
| **2** | `https://www.performancelab.com/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it` | **Up from 1** |
| **1** | `https://www.performancelab.com/blogs/sleep/magnesium-bisglycinate-vs-glycinate` | **Down from 2** |
| **1** | `https://www.performancelab.com/blogs/magnesium/magnesium-taurate-vs-glycinate` | **New — replaces malate** |
| — | ~~`/blogs/magnesium/magnesium-malate-vs-glycinate`~~ | **Withdrawn** |
| — | `https://www.performancelab.com/blogs/multi/best-multivitamin-for-men` | Still zero |

---

## Page 1 — 3 links · the one I am most confident about

```
https://www.performancelab.com/blogs/sleep/best-magnesium-for-sleep
```

**Why:**

- **Zero referring domains.** Verified twice — Ahrefs' backlink index returns
  0 live and 0 all-time, and the live SERP independently reports the ranking
  URL with `backlinks: 0, refdomains: 0`.
- **Ranks #7–9 for a 29,000-volume commercial term** with nothing pointing at it.
- **Topic potential 63,000 against 2,194 captured** — 217% of head-term volume,
  the healthiest ratio in the set.
- **The SERP is soft.** Position 5 is `coalgrovepharmacy.com`, DR **20**, on
  **12** referring domains. Positions 8, 10 and 11 (Amazon, MyPrivia, GNC) hold
  1, 4 and 1 respectively. Performance Lab is DR 62 with none.
- **Commercial:** CPC $0.35, feeds Performance Lab Sleep and Magnesium.

**Verify before ordering:** open the URL in Ahrefs Site Explorer, mode *Exact
URL*, and confirm Referring domains = 0. If it shows links, they are attributed
to a URL variant and the case weakens.

**Caveat I want on the record:** "0" means zero attributed to that exact string.
The crawl showed `?srsltid=…` variants of other articles holding their own
referring domains, so some equity may exist on a variant of this URL.

## Page 2 — 2 links · upgraded

```
https://www.performancelab.com/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it
```

**Why it moved up:** "when to take creatine" has a topic potential of **41,000
against 28,000 volume (146%)** and "creatine before or after workout" sits at
48% — both healthy SERPs where clicks actually reach organic results. The page
holds **3 referring domains** against 9,900–41,000 of potential, at KD 14–16
and competitive density 0.13, the softest cluster on the site.

**Two things to fix first — both free, both worth more than the links:**

**71 referring domains are stranded behind redirects:**

| URL | Ref domains | Status |
|---|---|---|
| `https://www.performancelab.com/blogs/pre/creatine-before-or-after-workout` | **55** | 301 |
| `https://www.performancelab.com/blogs/pre-workout/creatine-before-or-after-workout` | **16** | 301 |
| `https://www.performancelab.com/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it` | 3 | 200 |

**Four URLs compete for "when to take creatine" (28,000):**

| Position | URL |
|---|---|
| 25 | `/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it` |
| 42 | `/blogs/nutrition/how-often-should-i-take-creatine` |
| 65 | `/blogs/pre-workout/creatine-timing-when-is-the-best-time-to-take-it` |
| 93 | `/blogs/nutrition/when-to-take-creatine-and-protein-the-correct-whey` |

**Note the proposal's URL is truncated** — it says
`/blogs/pre-lab-pro/creatine-before-or-after-workout`, missing
`-when-should-you-take-it`. Confirm the live URL before any placement.

## Page 3 — 1 link · downgraded

```
https://www.performancelab.com/blogs/sleep/magnesium-bisglycinate-vs-glycinate
```

**Why it moved down:** the head term "magnesium bisglycinate" looked like the
prize at 26,000 volume, but only **13%** of that reaches organic. The page's own
comparison cluster is the healthy part — "magnesium bisglycinate vs glycinate"
runs at **129%** — and the page is already **#3–5** there.

So one link, and **aimed at the comparison intent, not the bare product term.**
19 referring domains already, so it is the least responsive of the four.

## Page 4 — 1 link · new

```
https://www.performancelab.com/blogs/magnesium/magnesium-taurate-vs-glycinate
```

**Why it replaces malate:** **7 referring domains**, KD **10**, ranking #4–6 for
"magnesium taurate benefits" (4,400–5,600) — and a **91%** potential-to-volume
ratio, so the clicks are really there. Unlike malate, there is no dispute about
which URL ranks or whether it is already first.

---

## What still gets nothing

```
https://www.performancelab.com/blogs/multi/best-multivitamin-for-men
```

**237 referring domains at position 23.** Men's Health ranks #2 with 279 — near
parity on links, 21 places lower. Ahrefs KD is **16**, so difficulty is not the
barrier either. The SERP is NYTimes Wirecutter, Fortune, Men's Health, Reddit
(×2), Quora, Amazon, GNC, CVS, Walgreens, US News — editorial, UGC, retail and
institutions, with no supplement brand ranking its own "best" listicle. This
needs digital PR that gets the brand *mentioned in* those pages.

```
https://www.performancelab.com/blogs/fitness/dumbbell-rear-delt-fly
```

5,098 visits/month on 14 referring domains at KD 0 — but only **9%** of the
81,000 volume reaches organic, and it already captures 5,098 of a 7,600 ceiling.
Near-maxed and no purchase intent. Use it as an internal-link donor to the Sleep
and Magnesium pages.

---

## Anchors

### The principle

Google's own guidance is that anchor text should be descriptive, reasonable in
length, and useful to a reader. What gets sites into trouble is not commercial
anchors as such — it is **repeated, bare, keyword-string anchors arriving from
paid placements**, which is a pattern no editorial writer produces.

So every anchor below is a phrase that reads as part of a sentence. Several
happen to match a real query, which is fine and expected — natural language and
search language overlap. What matters is that none is a bare keyword string
dropped into copy, and that no two are alike.

Context also matters independently of the anchor. **Give the publisher the
surrounding sentence**, not just the anchor — the words around a link carry
relevance signal on their own, and it stops the writer inventing something
worse.

### The seven

**`/blogs/sleep/best-magnesium-for-sleep`** — 3 links

| # | Anchor | Suggested sentence |
|---|---|---|
| 1 | `which magnesium is best for sleep` | "If you're not sure **which magnesium is best for sleep**, this comparison of glycinate, citrate and threonate is a sensible starting point." |
| 2 | `the best magnesium for sleep` | "Performance Lab's guide to **the best magnesium for sleep** sets out the forms side by side, with dosing and timing." |
| 3 | `magnesium and sleep quality` | "There's a readable summary of the research on **magnesium and sleep quality** that covers what the trials actually measured." |

**`/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it`** — 2 links

| # | Anchor | Suggested sentence |
|---|---|---|
| 4 | `when to take creatine` | "The evidence on **when to take creatine** is less settled than most training advice suggests." |
| 5 | `whether to take creatine before or after a workout` | "This review of **whether to take creatine before or after a workout** works through the timing studies rather than the folklore." |

**`/blogs/sleep/magnesium-bisglycinate-vs-glycinate`** — 1 link

| # | Anchor | Suggested sentence |
|---|---|---|
| 6 | `magnesium bisglycinate vs glycinate` | "The distinction between **magnesium bisglycinate vs glycinate** is largely a naming convention, explained clearly here." |

**`/blogs/magnesium/magnesium-taurate-vs-glycinate`** — 1 link

| # | Anchor | Suggested sentence |
|---|---|---|
| 7 | `magnesium taurate benefits` | "**Magnesium taurate benefits** are less familiar than glycinate's, particularly around cardiovascular support." |

### Why this set is safe

- **Zero bare commercial keyword strings.** Every anchor is a natural phrase.
- **Seven distinct anchors, no repetition**, across four URLs.
- **No page exceeds three anchors**, and each page's three differ in form —
  question, descriptive, topical.
- **Domain-level exposure is nil**: the existing profile is **>80% branded,
  bare-URL or generic** across ~2,830 referring domains, with
  `performancelab.com` alone on 781. Seven anchors is 0.25% of the profile.

### Conditions to put in writing

- Anchor sits in **editorial body copy** — not an author bio, resource box,
  footer or sidebar.
- **No placement uses `performancelab.com` as the anchor.** 781 referring
  domains already do; another adds nothing.
- **Publisher list approved in advance.** This profile already carries 221
  referring domains of spun `SEOExpress.org` testimonials and 234 with
  `TELEGRAM @SEO_ANOMALY` anchors — someone has sold this site links before.
- **Submit the disavow first.** 1,183 toxic referring domains are still live.

### Fallbacks

If a publisher refuses a given anchor, supply one of these rather than letting
them write their own:

`research from Performance Lab` · `this breakdown of magnesium forms` ·
`Performance Lab's comparison of magnesium types` · `a guide to creatine timing`

---

## Honest confidence

| Recommendation | Confidence | Why |
|---|---|---|
| best-magnesium-for-sleep, 3 links | **High** | Zero links verified twice, softest SERP, best potential ratio |
| creatine page, 2 links | **Medium-high** | Strong metrics, but conditional on fixing cannibalisation and redirects |
| bisglycinate, 1 link | **Medium** | Real but smaller than first estimated; 19 links already |
| taurate, 1 link | **Medium** | Good ratio and low KD, small absolute prize |
| multivitamin, 0 links | **High** | 237 domains at #23 with KD 16 is conclusive |
| Traffic projections | **Low-medium** | Generic CTR curve, feature-heavy SERPs, 2–3 place tool disagreement |

Treat the page and anchor choices as solid and the traffic numbers as
directional.
