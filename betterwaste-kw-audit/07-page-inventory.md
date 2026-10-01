# Page inventory check — correction to the plan

**Date:** 1 October 2026 · **Source:** Ahrefs crawled-URL index (page existence and HTTP
status only — all keyword metrics elsewhere remain Semrush UK)

I could not crawl betterwaste.co.uk directly (the environment's network policy blocks
the host), so earlier documents inferred page existence from which URLs were ranking.
That under-counted the site badly. Pulling the full crawled-URL list corrects it.

---

## 1. Answering the direct question: do pages exist for the AVOID keywords?

**Yes — for two of the five AVOID groups, and that is a problem worth acting on.**

| AVOID group | SV | Page exists? | Which |
|---|---|---|---|
| **Clinical waste** | 6,400 | ✅ **Yes — two** | `/clinical-waste-disposal-clinical-waste-collection-companies/` and `/healthcare-waste/` |
| **Bin sizes** (1100/660/240/eurobin) | 2,290 | ✅ **Yes — seven** | `/bins/1100l-bin/`, `/bins/660l-bin/`, `/bins/240l-bin/`, `/bins/360l-bin/`, `/bins/fel-container/`, `/bins/rel-container/`, `/bins/roro/` |
| Hazardous waste | 3,200 | ❌ No | — |
| WEEE / electrical | 2,990 | ❌ No | — |
| Bulky / green waste | 11,200 | ❌ No | — |

**What this means:**

- **Clinical waste** — there are already two pages chasing this, and the head terms are
  household-intent council SERPs. They are not going to rank for `clinical waste
  collection`. Don't delete them: clinical/healthcare waste is a real commercial
  service with real demand, it just isn't expressed through those head terms. Re-point
  them at commercial entry terms (`clinical waste disposal companies`,
  `dental waste disposal`, `care home waste management`) and consolidate the two into
  one — right now they compete with each other.
- **Bin pages** — seven already exist, and `1100 litre bin` / `660 litre bin` etc. are
  retail SERPs full of bin shops. These pages won't win those terms. They are still
  useful as mid-funnel spec/reference pages; they just shouldn't carry a ranking
  target. The reachable term in this cluster is `commercial bin sizes` (210 SV), which
  wants one comparison page, not seven product pages.

---

## 2. The larger correction: pages I said CREATE that already exist

This affects **15 recommendations**. Each was costed as new-page work; most are
actually optimisation of something live.

| I recommended CREATE | Reality | Existing URL |
|---|---|---|
| `/commercial-waste-collection/` | ✅ **Already exists** | `/commercial-waste-collection/` |
| `/commercial-bins/` | ✅ Exists | `/commercial-bin-collections/` |
| `/office-waste-management/` | ✅ Exists | `/office-waste-management/` |
| `/retail-waste-management/` | ✅ Exists | `/retail-waste-management/` |
| `/school-waste-management/` | ✅ Exists | `/school-waste-management/` |
| Trade waste page | ✅ Exists | `/trade-waste-collections/` |
| Hotel sector page | ✅ Exists | `/hotel-waste-disposal/` |
| Commercial food waste page | ✅ Exists | `/commercial-food-waste-collections/` |
| `/areas-we-cover/bristol/` | ✅ Exists | same |
| `/areas-we-cover/nottingham/` | ✅ Exists | same |
| Bin spec pages ×6 | ✅ Exist under `/bins/` | `/bins/1100l-bin/` etc. |

**The single biggest one:** I made `/commercial-waste-collection/` the centrepiece of
the plan — "build the national money page". **It already exists.** The recommendation
is unchanged in substance (that page should own the Cluster A terms) but it is an
optimisation and internal-linking job, not a build. It also sharpens the
cannibalisation finding: `/commercial-waste-collection/`, `/commercial-waste-management/`,
`/business-waste-collections/` and `/trade-waste-collections/` are **four live pages**
targeting overlapping head terms.

Also undiscovered earlier, and worth noting: `/areas-we-cover/` has pages for
**Bradford, Coventry, Leeds, Leicester, Northampton, Nottingham, Sheffield and
Bristol** — eight cities, none of which appear in the keyword tracker.

---

## 3. ⚠️ The Manchester finding was backwards — correct this before acting

My fix list said: *301 `/areas-we-cover-old/manchester/` → `/areas-we-cover/manchester/`.*

The crawl data says the opposite is happening:

| URL | HTTP status |
|---|---|
| `/areas-we-cover-old/manchester/` | **200** (live) |
| `/areas-we-cover-old/london/` | **200** (live) |
| `/areas-we-cover-old/birmingham/` | **200** (live) |
| `/areas-we-cover/manchester/` | **301** (redirecting) |
| `/areas-we-cover/london/` | **301** (redirecting) |
| `/areas-we-cover/birmingham/` | **301** (redirecting) |

The "new" URLs are the ones redirecting; the "-old" URLs serve 200. That explains
cleanly why Google ranks the `-old` pages — they are the only ones actually resolving.

**This does not change the diagnosis** (Manchester, London and Birmingham rankings sit
on URLs that look deprecated) **but it does change the fix.** Before touching
anything, establish where those three 301s point. Two possibilities:

1. The new URLs redirect *to* the `-old` ones — in which case the naming is simply
   misleading and the `-old` URLs are the canonical pages. Rename, don't redirect.
2. They redirect somewhere else (the hub, or a loop) — in which case the redirect is
   the bug.

I cannot resolve this without fetching the URLs, which the network policy prevents.
**Verify before implementing.** The previous instruction, followed literally, could
have created a redirect loop.

---

## 4. Still genuinely missing — the CREATE list is now this

These have no page and remain real build work:

| Page | Grade | SV |
|---|---|---|
| `/confidential-waste/` | 🟢 EASY | 5,600 |
| `/sanitary-waste/` | 🟢 EASY | 2,600 |
| `/industrial-waste/` | 🟡 MEDIUM | 1,110 |
| `/construction-waste/` | 🟡 MEDIUM | 850 |
| `/care-home-waste-management/` | 🟡 MEDIUM | 480 |
| `/dental-waste-disposal/` | 🟡 MEDIUM | 480 |
| `/wood-waste/` | 🟢 EASY | 390 |
| `/cooking-oil-collection/` | 🟢 EASY | 320 |
| `/butchers-waste-collection/` | 🟢 EASY | 260 |
| `/metal-waste/` | 🟢 EASY (check service fit) | 260 |
| `/areas-we-cover/liverpool/` | 🟢 EASY | 260 |
| `/areas-we-cover/glasgow/` | 🟢 EASY | 70 |

**12 genuine new pages, not the 63 originally scored.** The rest of the plan is
optimisation of pages that already exist — which is cheaper, faster, and lower risk.

---

## 5. Other things the crawl surfaced

- **Index bloat.** Live 200-status pages include `/222-2/`, `/test-2/`, `/home/`,
  `/thank-you/`, `/thank-you-2/`, `/quote2-old/`, `/quote-commercial-waste-old/`,
  `/quote-waste-services-old/`, `/trial-form/`, `/demos/`, plus `/quote2/` with six
  indexable `?slink=` parameter variants. Worth a crawl-control pass.
- **Duplicate trailing-slash URLs** serving 200 on both forms: `/about` and `/about/`,
  `/binpedia` and `/binpedia/`, `/contact-us` and `/contact-us/`, `/blog` and `/blog/`,
  `/faqs` and `/faqs/`, `/how-to-be-green` and `/how-to-be-green/`. Compounds the
  www / non-www duplication already flagged.
- **Four live 404s that were previously real pages** and may hold links:
  `/better-waste-solutions-birmingham/`, `/better-waste-solutions-london/`,
  `/better-waste-solutions-manchester/`, `/business-waste-management-yorkshire/`.
- **Eleven sector pages confirmed**, matching the Better Waste document: barber, cafe,
  convenience shop, hair salon, hotel, office, pub, restaurant, retail, school,
  takeaway — plus bakery. The document was right and my inference was wrong.

---

## Method note

Page existence and HTTP status come from the Ahrefs crawled-URL index. It reflects
Ahrefs' last crawl, not a live fetch, so status codes may lag recent changes —
particularly relevant to the three 301s in §3. Treat §3 as something to verify, not
something established.
