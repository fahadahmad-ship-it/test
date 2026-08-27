# Which pages to push with links, which anchors, and why

Performance Lab · analysis 2026-08-27 · Ahrefs + Semrush, US

---

## Method

A page is only worth a paid link if it passes five tests. Most link plans test
one or two.

1. **Volume** — is there enough demand behind it?
2. **Striking distance** — is it close enough that a few links move it? Gains
   are largest from positions 4–15; below ~25 links rarely bridge the gap alone.
3. **Link responsiveness** — how many referring domains does the page *already*
   have? This is the test almost everyone skips, and it is the one that decides
   whether links are the binding constraint.
4. **SERP winnability** — what do the pages above it actually have? If they are
   editorial giants and UGC, authority is not the lever.
5. **Commercial proximity** — does the traffic end in a sale?

A page that fails test 3 or 4 cannot be fixed with budget. That distinction
drives everything below.

---

## The finding that reframes the whole plan

| Page | Position | Volume | **Referring domains** | Verdict |
|---|---|---|---|---|
| `/blogs/sleep/best-magnesium-for-sleep` | 7 | 22,200 | **0** | Maximum leverage |
| `/blogs/pre-lab-pro/creatine-before-…-take-it` | 14 | 18,100 | **3** | High leverage |
| `/blogs/magnesium/magnesium-taurate-vs-glycinate` | 4 | 5,400 | **7** | High leverage |
| `/blogs/fitness/dumbbell-rear-delt-fly` | 3 | 81,000 | **13** | Already winning |
| `/blogs/sleep/magnesium-bisglycinate-vs-glycinate` | 13 | 22,200 | **19** | Good leverage |
| `/blogs/multi/best-multivitamin-for-men` | 23 | 22,200 | **235** | **Saturated** |

`best-magnesium-for-sleep` ranks **7th for a 22,200-volume commercial term with
zero backlinks**. Confirmed twice: Ahrefs' backlink index returns 0 live and 0
all-time referring domains, and the live SERP shows it at position 9 with
`backlinks: 0, refdomains: 0`. It is ranking on domain authority and content
alone.

`best-multivitamin-for-men` has **235 referring domains** and sits at #23.

Those two facts point in opposite directions, and the proposal has it backwards:
it puts 3 links into the 235-domain page and 3 into the magnesium cluster
split across two pages.

---

## Recommended allocation

### 1. `/blogs/sleep/best-magnesium-for-sleep` — 3 links · **highest priority**

| Test | Evidence |
|---|---|
| Volume | 22,200 head term; cluster totals ~71,000/mo across 6 terms it already holds |
| Striking distance | #7 (Semrush) / #9 (Ahrefs) — the sweet spot |
| Link responsiveness | **0 referring domains.** Nothing to overcome; every link is the first |
| SERP winnability | See below — exceptionally soft |
| Commercial proximity | Feeds Sleep and Magnesium; CPC $0.35–0.46 |

**The SERP is the argument.** Who is above it and what they hold:

| Pos | Site | DR | Ref domains |
|---|---|---|---|
| 3 | Mayo Clinic Press | 92 | 240 |
| 4 | HealthCentral | 82 | **25** |
| 5 | **coalgrovepharmacy.com** | **20** | **12** |
| 6 | YouTube | 99 | 5 |
| 7 | Sleep Foundation | 90 | 1,009 |
| 8 | Amazon | 96 | **1** |
| **9** | **Performance Lab** | **62** | **0** |
| 10 | MyPrivia | 71 | 4 |
| 11 | GNC | 75 | 1 |

Position 5 is a **DR-20 pharmacy blog with 12 referring domains**. Performance
Lab is DR 62 with none. Three quality links puts this page at parity with
HealthCentral at #4, from a far stronger domain. Positions 8, 10 and 11 have
between 1 and 4 referring domains between them — they are held on domain
strength, not page strength, and page strength is exactly what a link buys.

**Expected movement:** #7 → #3–4 realistically. On 22,200 that is roughly 4% →
11% CTR, about **+1,500 visits/month on the head term alone**, plus movement
across the five sibling terms. Ahrefs puts the parent topic's traffic potential
at 63,000/month.

---

### 2. `/blogs/sleep/magnesium-bisglycinate-vs-glycinate` — 2 links

| Test | Evidence |
|---|---|
| Volume | 26,000 on "magnesium bisglycinate"; **CPC $0.50–0.69**, the highest commercial signal in the magnesium set |
| Striking distance | #13 on the head term |
| Link responsiveness | 19 referring domains — modest, room to move |
| Position asymmetry | Already **#3–#5 on every "vs" variant** (bisglycinate vs glycinate, glycinate vs bisglycinate, etc.) but #13 on the bare head term |
| Commercial proximity | Bisglycinate is what Performance Lab Sleep contains |

That asymmetry is the whole case. Google already trusts this page for the
comparison intent; it has not yet accepted it for the broad product term. That
is the classic profile of a page held back by page-level authority rather than
relevance.

**Expected movement:** #13 → #6–8. On 26,000, roughly 1.5% → 4%, about **+650
visits/month**, on the highest-CPC term in the cluster.

---

### 3. `/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it` — 1 link, **after a fix**

| Test | Evidence |
|---|---|
| Volume | Cluster ~88,000/mo: when to take creatine 27,100 · best time to take creatine 18,100 · creatine before or after workout 18,100 · when should you take creatine 14,800 · when to creatine 9,900 |
| Striking distance | #14 / #20 / #25 across those terms |
| Link responsiveness | **3 referring domains** |
| Difficulty | KD 14–16, competitive density 0.13 — the softest cluster on the site |
| Commercial proximity | Pre Lab Pro |

**But fix the cannibalisation first — it is free and probably worth more than
the link.** Four URLs compete for "when to take creatine":

| Position | URL |
|---|---|
| 25 | `/blogs/pre-lab-pro/creatine-before-or-after-workout-when-should-you-take-it` |
| 42 | `/blogs/nutrition/how-often-should-i-take-creatine` |
| 65 | `/blogs/pre-workout/creatine-timing-when-is-the-best-time-to-take-it` |
| 93 | `/blogs/nutrition/when-to-take-creatine-and-protein-the-correct-whey` |

**And recover 71 wasted referring domains.** Two old URLs 301-redirect to this
content and carry links that are being diluted by the hop:

- `/blogs/pre/creatine-before-or-after-workout` — **55 referring domains**
- `/blogs/pre-workout/creatine-before-or-after-workout` — **16 referring domains**

The page has 3 direct referring domains while 71 sit behind redirects. Auditing
those redirect chains is worth more than the $550 link.

---

## What not to link, and why

### `/blogs/multi/best-multivitamin-for-men` — the proposal's 3 links here are the biggest misallocation

The proposal calls positions 13–21 "credible to Google but under-supported —
precisely the situation that authority solves". The data says otherwise on three
counts.

**It is not under-supported.** 235 referring domains. For comparison, Men's
Health ranks #2 with 279. It has near-parity in links and sits 21 places lower.

**Difficulty is not the barrier.** Ahrefs KD is **16** — low. A KD-16 term that a
235-domain page cannot crack is not a link problem by definition.

**The SERP has decided what it wants, and it is not a supplement brand:**

| Pos | Result |
|---|---|
| 1 | NYTimes Wirecutter, Fortune (×2) |
| 2 | Men's Health (DR 87, 279 RDs) |
| 4 | Reddit (×2), Quora |
| 5 | Amazon best-sellers |
| 6 | University of Utah Health |
| 7–9 | GNC, CVS, Walgreens |
| 10 | US News |

Editorial giants, UGC, retailers and institutions. Performance Lab is trying to
rank its *own* "best multivitamin" listicle in a set where every other result is
a third party. That is an intent and trust mismatch, and no realistic number of
$550 links resolves it. Three links is 43% of the budget into the least
responsive page on the list.

If the multivitamin range matters commercially — and it should, NutriGenesis
Multi Men is the **strongest** product page at 201 visits/mo — the route is
digital PR that gets Performance Lab *mentioned in* those third-party listicles,
not links into a competing one.

### `/blogs/fitness/dumbbell-rear-delt-fly` — don't link it, mine it

13 referring domains, **#3 for an 81,000-volume term, 5,098 visits/month** — more
than double any other page, about $905/month in equivalent traffic value, at
KD 0. Ahrefs puts remaining traffic potential at 7,600, so it is close to
maxed out.

The proposal dismisses it because "there is no product at the end of that
search". Correct on intent, wrong on conclusion. It is the largest internal
authority source on the site and it costs nothing to route its internal links
into the Sleep and Magnesium pages. Free, and larger than anything $4,000 buys.

---

## Anchor text

### Why the risk here is close to zero

Present profile, by referring domains:

| Anchor | Ref domains | Type |
|---|---|---|
| `performancelab.com` | 781 | URL |
| *(empty / image)* | 392 | None |
| `Performance Lab` | 273 | Branded |
| `performancelab` | 247 | Branded |
| `www.performancelab.com` | 88 | URL |
| `here` / `website` / `click here` / `read more` / `check here` | 350 | Generic |

Over **80% of the profile is branded, bare-URL or generic. Exact-match
commercial anchors are effectively absent.** Seven new anchors against ~2,830
referring domains is 0.25% of the profile — statistically invisible at domain
level.

The real constraint is *page*-level. `best-magnesium-for-sleep` has zero links,
so three identical anchors would make it 100% exact-match on that page, which is
a footprint. So vary at page level, not domain level.

### The seven anchors

| # | Target page | Anchor | Type | Why this one |
|---|---|---|---|---|
| 1 | best-magnesium-for-sleep | `best magnesium for sleep` | Exact | Primary term, 22,200, page is #7 |
| 2 | best-magnesium-for-sleep | `which type of magnesium is best for sleep` | Partial | Covers the #2/#3 sibling terms; reads naturally in copy |
| 3 | best-magnesium-for-sleep | `Performance Lab's guide to magnesium and sleep` | Branded + topic | Keeps the page's own anchor mix natural |
| 4 | magnesium-bisglycinate-vs-glycinate | `magnesium bisglycinate` | Exact | The precise gap — #13 on the head term while #3–5 on every variant |
| 5 | magnesium-bisglycinate-vs-glycinate | `magnesium bisglycinate vs glycinate` | Partial | Reinforces existing strength, supports the head term |
| 6 | creatine-…-when-should-you-take-it | `when to take creatine` | Exact | Highest volume in the cluster (27,100) and where the page is weakest (#25) |
| 7 | creatine-…-when-should-you-take-it | `creatine before or after a workout` | Partial | Natural phrasing of the 18,100 term |

**Mix: 3 exact, 3 partial, 1 branded.** No page exceeds 50% exact-match at page
level. Nothing repeats verbatim across placements.

**Fallbacks** if a publisher refuses a commercial anchor — hand these over
rather than letting them invent one:

- `research from Performance Lab`
- `Performance Lab's magnesium comparison`
- `this breakdown of magnesium types`
- `creatine timing guide`

**Two instructions to give the vendor in writing:** the anchor must be inside
editorial body copy, not an author bio or footer; and no placement may use
`performancelab.com` as the anchor — the profile has 781 domains doing that
already and another adds nothing.

---

## Risk review

| Risk | Assessment |
|---|---|
| Over-optimisation | Negligible. 7 anchors on a 2,830-domain profile that is >80% branded |
| Page-level footprint | Managed by the mix above; no page above 50% exact |
| Wasted spend on a dead URL | **Real.** The proposal's creatine URL is truncated and two known variants 301-redirect. Confirm the live URL first |
| Links diluted by redirects | **Real.** 71 referring domains sit on redirecting creatine URLs |
| Building onto a toxic profile | **Real.** 1,183 toxic referring domains identified; submit the disavow first |
| Vendor quality | Unproven. This profile already carries 221 domains of spun `SEOExpress.org` testimonials and 234 carrying `TELEGRAM @SEO_ANOMALY`. Approve the publisher list in advance |
| Affiliate leak | Separate but larger. Affiliate ID `68990cbe508aa` appears on **368 referring domains with 1,017 dofollow links** to a single tracking URL |

---

## Summary

| Priority | Page | Links | Ref domains now | Rationale in one line |
|---|---|---|---|---|
| 1 | `best-magnesium-for-sleep` | 3 | **0** | #7 on 22,200 with no links, on a SERP where a DR-20 blog holds #5 |
| 2 | `magnesium-bisglycinate-vs-glycinate` | 2 | 19 | #3–5 on every variant but #13 on the highest-CPC head term |
| 3 | `creatine-…-when-should-you-take-it` | 1 | 3 | Softest cluster on the site — but fix 4-way cannibalisation and 71 redirect-trapped domains first |
| — | `best-multivitamin-for-men` | **0** | 235 | Saturated. KD 16 with 235 domains at #23 is not a link problem |
| — | `dumbbell-rear-delt-fly` | **0** | 13 | Already #3 at KD 0. Use as an internal-link donor, not a target |

Same seven links, same $3,850 — reallocated from the page that cannot respond
to the page that has nothing to overcome.
