# Where the 7 links should go

Performance Lab · 2026-08-27 · full page inventory pulled from Ahrefs, joined
to per-page link and keyword data

---

## What the site actually looks like

Crawled inventory, `www.performancelab.com`, HTTP 200:

| Section | Notes |
|---|---|
| ~24 product pages | URL Rating 5–19 |
| ~14 collection pages | UR 17–19, the strongest non-home URLs |
| ~500+ blog articles | **UR 4.5–5.0 almost without exception** |
| Homepage | UR 19.5 |

**The first structural finding is in that table.** Product and collection pages
sit at UR 17–19; blog pages sit at 5. The blog is where 98% of the organic
traffic lands and it is receiving almost no internal authority. Every link
bought into a blog page is working against that, and fixing internal linking
costs nothing.

Two technical notes from the crawl, outside the scope of this plan but worth
handing to a developer:

- Dozens of `?a_aid=…` affiliate URLs are indexed as separate pages, several
  carrying their own URL Rating (`/products/mind-lab-pro?a_aid=68226e23cb8d9`
  at UR 9.6). Affiliate parameters should be canonicalised.
- A set of `wpm@…/sandbox/legacy/…` Shopify web-pixel URLs is indexed —
  machine-generated duplicates of real articles. These should be noindexed.

---

## How the pages were ranked

Four filters, applied in order. Most link plans stop at the first two.

1. **Headroom** — Ahrefs traffic potential for the parent topic, minus what the
   page already captures. A high-volume head term is not opportunity if the
   topic is already tapped.
2. **Link responsiveness** — referring domains the page already has. This is
   what decides whether links are the binding constraint.
3. **Realistic movement** — modelled position gain given (2), converted to
   traffic through a CTR curve.
4. **Commercial proximity** — CPC as a weight, applied last so a page can still
   surface on traffic and be judged on merit.

**The correction that mattered most.** The raw CTR model put
`dumbbell-rear-delt-fly` first at +5,880 visits — 84,000 search volume at
position 7 with only 14 referring domains. Applying the headroom ceiling cut
that to +2,502, because the whole topic tops out at 7,600 and the page already
takes 5,098 of it. A model that ignores the ceiling would have sent budget at a
page that has nearly finished growing.

---

## The ranking

Opportunity measured on each page's **head term** — the high-volume keyword it
ranks *poorly* for — not its top-traffic keyword.

| Rank | Page | Ref domains | Head term | Vol | Pos | Gain/mo | $/mo |
|---|---|---|---|---|---|---|---|
| **1** | `/blogs/sleep/best-magnesium-for-sleep` | **0** | best magnesium for sleep | 29,000 | 9 | **+1,959** | **546** |
| **2** | `/blogs/sleep/magnesium-bisglycinate-vs-glycinate` | 19 | magnesium bisglycinate | 26,000 | 13 | +468 | 234 |
| **3** | `/blogs/pre-lab-pro/creatine-before-…-take-it` | 3 | when to take creatine | 28,000 | 25 | +812 | 24 |
| **4** | `/blogs/magnesium/magnesium-malate-vs-glycinate` | 3 | magnesium malate benefits | 9,000 | 3 | +405 | 24 |
| 5 | `/blogs/magnesium/magnesium-taurate-vs-glycinate` | 7 | magnesium taurate benefits | 5,400 | 6 | +167 | 8 |
| — | `/blogs/fitness/dumbbell-rear-delt-fly` | 14 | rear delt fly | 84,000 | 7 | +2,502 | *(no intent)* |
| — | `/blogs/multi/best-multivitamin-for-men` | **237** | best multivitamin for men | 29,000 | 23 | **−5** | **−1** |

The multivitamin page returns a **negative** modelled gain. That is not a quirk
of the model — with 237 referring domains it is already past the point where
links move it, so the realistic-movement function correctly returns almost
nothing while its position stays where it is.

---

## Which page needs the links most

**`/blogs/sleep/best-magnesium-for-sleep`, without any real competition for the
title.** It ranks 9th for a 29,000-volume commercial term with **zero
backlinks** — confirmed twice, in Ahrefs' backlink index and independently in
the live SERP, which shows it at position 9 with `backlinks: 0, refdomains: 0`.

What is above it, and what those pages hold:

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

A DR-20 pharmacy blog with 12 referring domains holds position 5. Positions 8,
10 and 11 are held with one, four and one. Those pages rank on domain strength;
page strength is what a link buys, and Performance Lab has none of it here.
Three links puts it level with HealthCentral at #4 from a far stronger domain.

**The wider point: magnesium is the site's strongest topic and its least-linked
one.** Four magnesium pages carry **29 referring domains between them** and
produce **7,116 visits a month**. Nothing else on the site comes close to that
ratio, and it is why five of the seven links stay inside one cluster — topical
concentration is a benefit here, not a footprint.

---

## The allocation

| Links | Page | Why this page |
|---|---|---|
| **3** | `best-magnesium-for-sleep` | Zero links, 60,000 of unclaimed headroom, softest SERP on the list, highest CPC in the cluster |
| **2** | `magnesium-bisglycinate-vs-glycinate` | Already #3–5 on every "vs" variant but #13 on the 26,000-volume head term at $0.50 CPC — relevance is proven, page authority is the gap |
| **1** | `creatine-before-…-take-it` | 3 referring domains against 9,900 headroom, KD 14, the softest cluster on the site |
| **1** | `magnesium-malate-vs-glycinate` | 3 referring domains, already #3; parent topic "different types of magnesium" holds 37,000 potential against 1,629 captured |

**Swap option:** if the creatine redirects (below) are not fixed first, move
that link to `magnesium-taurate-vs-glycinate` — 7 referring domains, KD 10,
#6 → #4. Smaller prize, no dependencies.

---

## The anchors

The profile is **>80% branded, bare-URL or generic** across ~2,830 referring
domains — `performancelab.com` alone accounts for 781. Seven commercial anchors
is 0.25% of the profile and carries no domain-level risk. The real constraint is
page level: three identical anchors at a page with zero links would be 100%
exact-match on that URL, which *is* a footprint.

| # | Page | Anchor | Type |
|---|---|---|---|
| 1 | best-magnesium-for-sleep | `best magnesium for sleep` | Exact |
| 2 | best-magnesium-for-sleep | `which type of magnesium is best for sleep` | Partial |
| 3 | best-magnesium-for-sleep | `Performance Lab's guide to magnesium and sleep` | Branded |
| 4 | magnesium-bisglycinate-vs-glycinate | `magnesium bisglycinate` | Exact |
| 5 | magnesium-bisglycinate-vs-glycinate | `bisglycinate vs glycinate` | Partial |
| 6 | creatine-before-…-take-it | `when to take creatine` | Exact |
| 7 | magnesium-malate-vs-glycinate | `magnesium malate vs glycinate` | Partial |

3 exact, 3 partial, 1 branded. No page above 50% exact-match. Nothing repeats
verbatim.

**On anchor 7:** the page's biggest term is "magnesium malate benefits" (9,000)
but that keyword carries **KD 63** — much harder than anything else here. The
anchor deliberately targets "magnesium malate vs glycinate" (2,900, **KD 4**),
where the page sits at #6 and can actually move.

**Fallbacks** if a publisher refuses a commercial anchor — supply these rather
than letting them invent one:
`research from Performance Lab` · `this breakdown of magnesium types` ·
`Performance Lab's magnesium comparison` · `creatine timing guide`

**Two conditions to put in writing:** the anchor sits in editorial body copy,
not an author bio or footer; and no placement uses `performancelab.com` as the
anchor — 781 referring domains already do.

---

## What not to link, and why

**`/blogs/multi/best-multivitamin-for-men` — 0 links.** 237 referring domains at
position 23. Men's Health ranks #2 with 279, so this page is at near-parity on
links and 21 places lower. Ahrefs KD is **16** — low — so difficulty is not the
barrier either. The SERP is NYTimes Wirecutter, Fortune, Men's Health, Reddit
(×2), Quora, Amazon, GNC, CVS, Walgreens and US News: editorial, UGC, retail and
institutions, with no supplement brand ranking its own "best" listicle. That is
an intent mismatch, and the route in is digital PR that gets Performance Lab
*mentioned in* those listicles.

**`/blogs/fitness/dumbbell-rear-delt-fly` — 0 links, but do not ignore it.**
5,098 visits/month at KD 0, the site's largest page by more than double, on just
14 referring domains. Headroom is only ~2,500 and there is no purchase intent
behind "rear delt fly". It is the biggest internal authority source on the site
and should be routed into the Sleep and Magnesium pages — free, and larger than
anything the budget buys.

---

## Fix these first — both free, both worth more than a link

**71 referring domains are stranded behind redirects.** Two old URLs 301 to the
creatine article while it holds only 3 directly:

| URL | Ref domains | Status |
|---|---|---|
| `/blogs/pre/creatine-before-or-after-workout` | **55** | 301 |
| `/blogs/pre-workout/creatine-before-or-after-workout` | **16** | 301 |
| `/blogs/pre-lab-pro/creatine-before-…-take-it` | 3 | 200 (live) |

**Four URLs compete for "when to take creatine"** (28,000): positions 25, 42, 65
and 93. Buying a link into one of four self-competing pages treats the symptom.

---

## Expected outcome

| Page | Links | Now | Expected | Gain/mo |
|---|---|---|---|---|
| best-magnesium-for-sleep | 3 | #9 | #4–5 | +1,959 |
| magnesium-bisglycinate-vs-glycinate | 2 | #13 | #8 | +468 |
| creatine-before-…-take-it | 1 | #25 | #12–15 | +812 |
| magnesium-malate-vs-glycinate | 1 | #6 | #4 | +405 |
| | | | **Total** | **≈ +3,600/mo** |

Against ~3,900 current monthly visits across those four pages — roughly a
doubling of the cluster, on a $3,850 spend, with the largest single share going
to the one page on the site that ranks top-10 on a 29,000-volume commercial term
with nothing pointing at it.
