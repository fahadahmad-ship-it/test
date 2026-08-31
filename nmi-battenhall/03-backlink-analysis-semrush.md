# NMI — Backlink Analysis (Semrush metrics)

**Internal working document.** Battenhall works in Semrush, so all client-facing numbers use
**Authority Score (AS)**, not Ahrefs DR. Data pulled 31 August 2026.

> ⚠️ The Ahrefs figures in `01-data-appendix.md` remain valid for the SERP and keyword analysis,
> but **do not put Ahrefs DR in front of Battenhall.** The two scales tell different stories —
> see §1.

---

## 1. The metric switch changes the narrative — in NMI's favour

| Domain | **Semrush AS** | Ahrefs DR | Referring domains | Total backlinks | Backlinks per domain |
|---|---|---|---|---|---|
| stripe.com | 79 | 95 | 696,910 | 146,428,354 | 210 |
| checkout.com | **52** | 80 | 11,610 | 817,121 | 70 |
| adyen.com | **49** | 88 | 59,017 | 1,434,387 | 24 |
| authorize.net | **48** | 90 | 39,946 | 33,079,406 | 828 |
| **nmi.com** | **46** | 77 | **4,968** | **22,878,932** | **4,605** |
| paysafe.com | 44 | 80 | 13,580 | 1,329,972 | 98 |
| finix.com | 37 | 66 | 2,330 | 14,369 | 6 |
| payrix.com | 27 | 66 | 1,005 | 5,512 | 5 |

**In Ahrefs, NMI looks 11–13 points behind Adyen and Authorize.Net. In Semrush, NMI is 2–3 points
behind them.** AS 46 vs 48 and 49. Checkout.com at 52 is the realistic ceiling for this programme;
Stripe at 79 is not a target.

This is a much stronger and still entirely honest pitch narrative: **NMI is inside touching
distance of its two named competitors on the metric the agency actually uses.** Lead with this.

---

## 2. The profile is concentrated, not earned

**NMI carries 4,605 backlinks per referring domain — 5.6x Authorize.Net and 192x Adyen.**

| Domain | Backlinks/domain | Nofollow % | Image links % |
|---|---|---|---|
| **nmi.com** | **4,605** | **0.17%** | **31.8%** |
| authorize.net | 828 | 26.2% | 55.1% |
| stripe.com | 210 | 28.8% | 7.1% |
| paysafe.com | 98 | 6.7% | 2.5% |
| checkout.com | 70 | 6.9% | 2.5% |
| adyen.com | 24 | 20.4% | 22.4% |

Two hard outliers:

1. **Nofollow at 0.17%.** A naturally earned profile runs 15–30% nofollow. NMI's is effectively
   zero. That is the signature of self-placed template links, not editorial coverage.
2. **Image links at 31.8%** (7.28m of 22.88m). The "powered by NMI" badge on merchant checkouts.
   Authorize.Net has the same pattern at 55% — it is the payment-gateway trust-seal footprint.

**Read:** NMI's headline backlink count is enormous and almost entirely inert. It is one asset
(the gateway integration) counted 22.8 million times. Adding more of the same moves nothing.

---

## 3. Quality distribution — how many links are actually good

Referring domains by Authority Score band, NMI vs Checkout.com (closest realistic benchmark):

| AS band | NMI domains | NMI % | Checkout.com domains | Checkout.com % |
|---|---|---|---|---|
| 0–9 | 2,753 | **57.4%** | 6,818 | 60.6% |
| 10–19 | 575 | 12.0% | 1,061 | 9.4% |
| 20–29 | 617 | 12.9% | 1,362 | 12.1% |
| 30–39 | 480 | 10.0% | 1,015 | 9.0% |
| 40–49 | 216 | 4.5% | 569 | 5.1% |
| 50–59 | 70 | 1.5% | 208 | 1.8% |
| 60–69 | 40 | 0.8% | 85 | 0.8% |
| 70–79 | 24 | 0.5% | 71 | 0.6% |
| 80–89 | 13 | 0.3% | 36 | 0.3% |
| 90–100 | 11 | 0.2% | 29 | 0.3% |
| **Total** | **4,799** | | **11,254** | |

**Headline numbers:**

| Threshold | NMI | Checkout.com | Gap |
|---|---|---|---|
| AS 40+ | **374** (7.8%) | 998 (8.9%) | **2.7x** |
| AS 50+ | **158** (3.3%) | 429 (3.8%) | 2.7x |
| AS 60+ | **88** (1.8%) | 221 (2.0%) | 2.5x |

**Read:** the *shape* of NMI's profile is normal for the vertical — the percentages track
Checkout.com almost exactly. The problem is **absolute volume at the top**. NMI has 374
authority-grade referring domains where Checkout.com has 998. The gap is consistently ~2.7x at
every quality threshold, which makes it a clean, defensible target to quote.

⚠️ **Do not present the AS 0–9 concentration as a spam finding.** Checkout.com has the same
spike (4,348 domains at AS 2, 38.6% of profile). It is characteristic of payments — merchant
directories, parked domains and small e-commerce sites. Calling it spam would be wrong and
Battenhall could check it in thirty seconds.

---

## 4. Flagged anchors

Top anchors by referring domain count:

| Anchor | Ref. domains | Backlinks | Assessment |
|---|---|---|---|
| `nmi` | 637 | 30,342 | Branded — healthy |
| `nmi.com` | 489 | 1,828 | Branded — healthy |
| *(empty anchor)* | 445 | **7,311,007** | Image/badge links — the footprint |
| `usaepay.com` | 320 | 763 | Acquired brand |
| `iriscrm.com` | 315 | 1,138 | Acquired brand |
| `usaepay` | 208 | 1,831 | Acquired brand |
| `usaepay.info` | 191 | 313 | Acquired brand |
| `https://www.nmi.com/legal/privacy-policy/` | 190 | 1,087 | Naked URL to a duplicate policy page |
| `https://www.nmi.com/privacy-policy` | 186 | 208 | Naked URL to a duplicate policy page |
| `agreementexpress.com` | 169 | 1,034 | Acquired brand |
| `learn more` | 138 | 11,428 | Generic |
| **`telegram @seo_anomaly - seo backlinks, black-links, traffic boost, link indexing`** | **100** | **100** | 🚩 **Spam / third-party link network** |

### 🚩 Flag 1 — Third-party spam anchor
An anchor advertising a Telegram black-hat link service appears across **100 referring domains**,
first seen October 2025 and still active. NMI did not place this. It is either a spam network
using NMI as a trust-signal or an unsolicited negative-SEO footprint. **Low severity at this
volume, but it should be looked at.** This is the single best "we found something" item for the
pitch — concrete, verifiable in Semrush in one click, and it demonstrates value without giving
away an audit.

### 🚩 Flag 2 — Typo-domain anchor cluster
A tight cluster of misspelled variants of NMI's acquired brands appears with near-identical
volumes (92–107 referring domains, ~150 backlinks each), all first seen 2024–2026:

`uasepay.com` · `usaaepay.com` · `naepay.com` · `us-epay.com` · `usaecart.com` ·
`networkmerchant.com` · `networkmerchantinc.com` · `networkmerchantsinc.com` · `epaypad.com` ·
`payvisa.com` · `bestcardonline.com` · `paysaberclip.com` · `integratedreportingissimple.com`

The uniformity is the tell — organic anchor distributions do not cluster this tightly.
**Two readings:** defensive typo-domain registrations NMI owns and redirects (benign), or a link
network (not benign). **We cannot tell which without checking ownership — do not assert spam.**
Present it as "requires investigation", which is honest and still lands.

### Flag 3 — Naked URLs to duplicate privacy pages
376 referring domains use a raw privacy-policy URL as anchor text, split across two different
duplicate paths. Reinforces the consolidation recommendation in `00-plan-of-attack.md` §F2.

### Anchor headroom
Branded + acquired-brand + naked URL + generic accounts for the overwhelming majority of the
profile. **There is effectively no exact-match commercial anchor presence at all.** That means
unusually wide headroom for partial and exact-match anchors — a real advantage, and it revises
the provisional framework in `02-scope-and-target-map.md` §5 upward on partial match.

---

## 5. Link intersect — domains linking to competitors but not NMI

Method: Semrush `backlinks_matrix` across nmi.com, adyen.com, authorize.net, checkout.com,
paysafe.com; filtered to domains with **zero** links to nmi.com; sorted by number of competitors
matched. All 50 rows returned link to **all four** competitors. Stripe deliberately excluded —
its profile is so large it swamps the consensus signal.

### 5a. Genuinely actionable prospects

| Domain | AS | Type | Note |
|---|---|---|---|
| visa.com | 70 | Industry body | 33 links to authorize.net |
| gocardless.com | 58 | Competitor content | Links to all 4 — outreach/citation target |
| seeklogo.com | 59 | Logo/brand directory | Trivial win |
| retaildive.com | 55 | Trade press | **222 links to authorize.net** |
| indiehackers.com | 54 | Developer community | Direct ICP match |
| altexsoft.com | 51 | Tech content | |
| iubenda.com | 48 | Compliance tooling | 199 links to adyen |
| ecommercefastlane.com | 48 | E-commerce media | |
| cocoapods.org | 46 | **Developer package registry** | 52 links to adyen |
| geekflare.com | 46 | Software reviews | |
| financemagnates.com | 43 | **Fintech trade press** | |
| wappalyzer.com | 42 | Tech profiling | Listing opportunity |
| hexdocs.pm | 42 | **Developer docs registry** | |
| splitit.com | 42 | Payments peer | |
| recurly.com | 40 | Payments peer | 139 links to adyen |
| hex.pm | 34 | **Developer package registry** | |
| lendsqr.com | 34 | Fintech | |
| paymentsindustryintelligence.com | 33 | **Niche trade press** | 67 links to authorize.net |
| faisalkhan.com | 31 | Payments consultant/blog | |
| merchantmachine.co.uk | 29 | **Comparison site** | Links to all 4 |

### 5b. Excluded as non-actionable
`microsoft.com` · `uol.com.br` · `udn.com` · `amazonaws.com` · `telegram.me` · `entireweb.com` ·
`isdown.app` · `sg-host.com` · `mybluehost.me` · `ghost.io` · `raindrop.io` · `cnblogs.com` ·
`habr.com` · `podcasts-online.org` · `iconlogovector.com` · `osmarks.net` · `paperblog.com` ·
`zoolatech.com` — hosting artefacts, status-page scrapers, aggregators and non-target-market sites.

### 5c. The finding that matters most

**Every competitor has developer-ecosystem links that NMI does not.** CocoaPods (AS 46), Hex.pm
(AS 34), HexDocs (AS 42), Wappalyzer (AS 42), IndieHackers (AS 54) all link to Adyen,
Authorize.Net, Checkout.com and Paysafe — and to **none** of them to NMI.

NMI's positioning is **embedded payments for US developers**. Their competitors are present in the
developer ecosystem and they are not. This is a whole link category that is missing, maps exactly
onto their ICP, is mostly free to acquire (SDK listings, integration directories, package
registries, tech profiles), and produces qualified referral traffic as well as authority.

**This should be a headline slide in the pitch.** It is the most differentiated insight in the
entire analysis and it is not something a generic link proposal would surface.

---

## 6. Recommended backlink mix

Derived from §3 (need ~2.7x more AS 40+ domains), §4 (anchor headroom is wide open) and §5
(developer ecosystem is the unexploited category).

| # | Link type | Target AS | Why | Share |
|---|---|---|---|---|
| 1 | **Fintech & payments trade press** — RetailDive, Finance Magnates, Payments Industry Intelligence, PYMNTS-tier | 30–60 | Closes the AS 40+ gap with topical relevance. Directly what the SERPs reward. | Largest |
| 2 | **Developer ecosystem & integration listings** — package registries, SDK/integration directories, tech-profiling sites, dev communities | 30–55 | §5c. ICP match, competitors have them, low cost, referral traffic. | Significant |
| 3 | **Comparison, review & software directories** — Merchant Machine, Geekflare tier | 25–50 | Commercial intent, converts as well as ranks. | Moderate |
| 4 | **Data-led digital PR** — original survey data | 50+ | Proven for this brand: the generative-AI post earned 143 RDs, the consumer survey 42. Gives Battenhall a PR cycle. | Quarterly asset |

**Explicitly deprioritise:**
- More badge / footer / template placements. NMI has 22.8m of these. Zero marginal value.
- Low-AS directory submissions. The 0–9 band is already 57% of the profile.
- Anything that adds backlink *count* without adding a **new referring domain at AS 30+**.

**Quality floor to propose: AS 30 minimum, AS 40+ for the majority.** Below AS 30 the link does
not move the metric Battenhall reports on.

---

## 7. What goes to Battenhall vs what stays internal

A full audit is a **paid product**. The pitch shows enough to prove capability and create urgency,
and no more. See `04-pitch-extract.md` for the client-facing cut.

| Include in pitch | Withhold |
|---|---|
| AS comparison table (§1) — it flatters NMI and is the hook | Full AS distribution tables |
| Referring domain counts vs the three named competitors | Backlinks-per-domain and nofollow analysis (§2) — this is the diagnostic core |
| Headline "374 of 4,968 domains are AS 40+" (§3) | Band-by-band breakdown and the Checkout.com benchmark |
| **The Telegram spam anchor** (§4 Flag 1) — named, one line | The typo-domain cluster (§4 Flag 2) — unresolved, and the better hook for paid audit work |
| **The developer-ecosystem gap** (§5c) as a strategic finding | The named 20-domain prospect list (§5a) — this *is* the product |
| 3–4 sample prospect domains, no more | The other 46 |
| Recommended link mix at category level (§6) | Per-category volumes, targeting logic, outreach angles |
