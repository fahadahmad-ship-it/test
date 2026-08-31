# NMI — Link Quality Benchmark & Ahrefs Link Intersect

**Internal working document.** Data pulled 31 August 2026.
Quality thresholds per SUSO's definition: **AS 30+** for authority, **1,000+ monthly organic
traffic** for "good", with spam judged on **anchors and zero-traffic domains**, not score alone.

---

## 1. AS 30+ benchmark

| Domain | **AS 30+ RDs** | Total RDs | % of profile | NMI's gap |
|---|---|---|---|---|
| adyen.com | **4,547** | 57,741 | 7.9% | **5.3x** |
| authorize.net | **3,940** | 38,233 | 10.3% | **4.6x** |
| checkout.com | **2,013** | 11,254 | 17.9% | **2.4x** |
| **nmi.com** | **854** | **4,799** | **17.8%** | — |

**The finding that should lead the pitch:**

> NMI's profile is *proportionally cleaner* than Adyen's and Authorize.Net's. 17.8% of NMI's
> referring domains are AS 30+, against 7.9% for Adyen and 10.3% for Authorize.Net. NMI is not
> carrying a quality problem. It is carrying a **scale** problem at the top of the profile.

That is a genuinely good story and it is true. NMI needs roughly **4.6x more AS 30+ referring
domains to match Authorize.Net** and **5.3x to match Adyen** — but the composition of what they
already have is better than both. The programme is about volume of good links, not remediation.

Checkout.com is the closest structural comparison (17.9% vs NMI's 17.8% — near-identical shape)
and the realistic 12–24 month target at **2.4x**.

---

## 2. Traffic-based quality — "good" = 1,000+ monthly organic traffic

Score alone does not settle whether a link is good. An AS 15 domain with real traffic is a real
link; an AS 50 domain with zero traffic usually is not. Ahrefs figures, live links, **exact counts
via paginated banding** (the API caps any single export at 250 rows):

| Traffic band | Referring domains |
|---|---|
| 22,637+ | 250 |
| 4,516 – 22,636 | 250 |
| 1,202 – 4,515 | 250 |
| 1,000 – 1,201 | 33 |
| **Total with 1,000+ traffic** | **783** |
| Total referring domains | 4,164 |
| **Good-link rate** | **18.8%** |

**783 of NMI's 4,164 referring domains carry 1,000+ monthly organic traffic.** Figure is exact.

Top of the segment is genuinely strong: Wikipedia, Google, Apple, Adobe, GitHub, Forbes, Shopify,
Salesforce, PCMag, Stack Overflow, Bloomberg, TechCrunch, Mastercard, Crunchbase, PYMNTS,
Fintech Futures, Fintech Magazine, Payments Dive.

**Read:** NMI's *good* links are good. There just are not many of them relative to profile size,
and almost none point anywhere except the homepage (see `01-data-appendix.md` §C).

---

## 3. 🚩 Active spam link network — the significant finding

Filtering NMI's referring domains to Ahrefs' spam flag, banded by DR for exact counts:

| DR band | Spam-flagged RDs |
|---|---|
| 40+ | 95 |
| 33 – 39 | 27 |
| 30 – 32 | 205 |
| **DR 30+ subtotal** | **327** |
| 20 – 29 | 97 |
| 10 – 19 | 88 |
| 5 – 9 | 89 |
| Under 5 | 250+ (tail, still capped) |
| **Total** | **851+** |

This is not historical noise. It is a live, growing network.

**The pattern:**

| Cluster | Examples | DR | Traffic |
|---|---|---|---|
| Explicit link-selling domains | `buybacklinks.agency`, `backlinker.shop`, `buyseobacklinks.shop`, `pbnseolinks.shop`, `authoritybacklinks.shop` | 53–73 | **0** |
| "SEO Express" / "Link Baron" / "Outrank HQ" / "Rank Forge" `.store` network | `seoexpress-pbn-experts.store`, `master-rank-forge-pbn-league.store`, `outrank-hq-dr-90-paramount-system.store` — **100+ domains** | 32 | **0** |
| Directory network | `topbilliondirectory.com`, `rankfastdirectory.com`, `worldzonedirectory.com` | 46–54 | **0** |

Connects directly to the Semrush anchor finding (`03` §4): the anchor
`telegram @seo_anomaly - seo backlinks, black-links, traffic boost, link indexing` across 100
referring domains. **Same network.**

### 3a. The proof that score-only screening fails

Of the **327 spam-flagged domains at DR 30+**:

| | Count |
|---|---|
| Would pass a **DR 30+ filter** | **327** |
| Of those, with **1,000+ monthly traffic** | **12** |
| Of those 12, actually legitimate on inspection | ~8 (`pages.dev`, `web.app`, `brandfetch.com`, `prospeo.io` — hosting subdomains and real SaaS tools, i.e. false positives on the spam flag) |
| **Removed by adding a traffic filter** | **315 (96%)** |

> **A DR/AS 30+ filter passes all 327 of these domains. Adding "1,000+ organic traffic" removes
> 315 of them.** That is the entire methodology argument, proven on the client's own data, in one
> table.

This is the strongest asset in the pitch. It is concrete, checkable in either tool in under a
minute, and it demonstrates precisely why SUSO's screening model is not the same as a DR filter.

### What we do and do not say
- **Do say:** it exists, that it is 327 domains at DR 30+, that it is live, and that score-only
  screening cannot see it.
- **Do not say:** that it is causing a penalty or that NMI needs an urgent disavow. We have not
  assessed impact, and over-claiming is how the pitch loses credibility.
- **Do not** hand over the domain list. That is the audit.

---

## 4. Ahrefs link intersect

**Method.** Ahrefs referring domains for adyen.com and authorize.net, filtered to
**dofollow + in-content + 20,000+ monthly organic traffic**, top 250 each by traffic. Diffed
against NMI's referring domains. NMI's export is complete down to 22,637 traffic, so the
comparison is valid above that floor. Platform, CDN, hosting and consumer-retail domains excluded
by hand.

**Result: 123 qualified prospect domains** that link to at least one competitor and **not** to NMI.

### 4a. Linking to *both* Adyen and Authorize.Net (highest confidence)

| Domain | Traffic /mo |
|---|---|
| zoho.com | 9,611,494 |
| cnet.com | 7,808,966 |
| hubspot.com | 4,398,346 |
| **visa.com** | 1,417,846 |
| odoo.com | 934,390 |
| elementor.com | 699,739 |
| toptal.com | 503,662 |

Overlap statistics: of 37 domains shared by both competitors in the sample, **NMI has only 12.**

### 4b. Developer ecosystem — 35 prospects, and the strategic headline

| Domain | Traffic /mo | Links to |
|---|---|---|
| docker.com | 3,595,382 | Adyen |
| jetbrains.com | 2,432,608 | Adyen |
| okta.com | 1,440,607 | Adyen |
| redhat.com | 1,404,975 | Adyen |
| postman.com | 971,218 | Adyen |
| ycombinator.com | 941,914 | AuthNet |
| pydata.org | 552,816 | Adyen |
| postgresql.org | 534,658 | Adyen |
| php.net | 483,990 | AuthNet |
| codepen.io | 383,161 | AuthNet |
| w3.org | 262,309 | AuthNet |
| indiehackers.com | 110,122 | AuthNet |
| gitbook.io | 106,193 | AuthNet |
| shopify.dev | 96,875 | AuthNet |
| apidog.com | 90,749 | AuthNet |
| sitepoint.com | 79,808 | AuthNet |
| curl.se | 72,138 | AuthNet |
| oreilly.com | 71,459 | AuthNet |
| codesandbox.io | 68,870 | AuthNet |

*(plus unity3d.com, optimizely.com, softpedia.com, tutsplus.com, velog.io, mulesoft.com,
alteryx.com, sitecore.com, jitterbit.com, c-sharpcorner.com, telerik.com, computerhope.com,
getharvest.com, elegantthemes.com, systeme.io, dynamics.com)*

**NMI sells embedded payments to US developers and holds none of these.** Both Semrush and Ahrefs
independently produce this finding. It is the most differentiated insight in the analysis.

### 4c. Payments & fintech peers — 36 prospects
PayPal, Chase, Intuit, Stripe, Xero, Remitly, MercadoPago, Cash App, SumUp, Razorpay, **Visa**,
Afterpay, Gusto, Affirm, PagBank, InfinitePay, PhonePe, Wave, Klaviyo, **GoCardless**, Bill.com,
Paddle, Lightspeed, Shippo, Podium, Sendcloud, Zendrop, Nayax, Intacct, Omnisend, Spocket, Zeffy,
SimplyBook, Pilot, LeadSquared, Block Advisors.

### 4d. Marketing / SEO media — 10 prospects
HubSpot (both), Buffer, Moz, Neil Patel, Skillshare, HubSpot ES, Search Engine Journal,
ScreenPal, Beehiiv, Docebo.

### 4e. Media & trade — 19 prospects
Il Sole 24 Ore, **FT**, CoinDesk, Statista, Newsweek, The Points Guy, WEF, KPMG, Science News,
Engadget, Gambling.com, Grand View Research, MobileAppDaily, Awin, Computerworld, AltexSoft,
Iubenda, SEO.ai, Venture Harbour.

---

## 5. Cross-check: Ahrefs vs Semrush intersect

Both tools were run independently and **converge on the same conclusion.**

| | Semrush `backlinks_matrix` | Ahrefs referring-domain diff |
|---|---|---|
| Competitors | Adyen, Authorize.Net, Checkout, Paysafe | Adyen, Authorize.Net |
| Filter | Links to all 4, none to NMI | Dofollow + in-content + 20k traffic |
| Qualified prospects | 50 (20 actionable) | 123 |
| Developer-ecosystem gap | **Found** (CocoaPods, Hex.pm, HexDocs, Wappalyzer, IndieHackers) | **Found** (Docker, JetBrains, Postman, PostgreSQL, php.net, CodePen, W3C, IndieHackers) |
| Trade press gap | **Found** (RetailDive, Finance Magnates) | **Found** (FT, CoinDesk, Computerworld, Engadget) |

Two independent datasets reaching the same answer is worth stating in the pitch. It is the
difference between an observation and a finding.

**Combined qualified prospect pool: ~140 unique domains**, before any manual relevance vetting.
