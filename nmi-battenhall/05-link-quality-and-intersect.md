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
link; an AS 50 domain with zero traffic usually is not. Ahrefs figures, live links:

| Segment | Count |
|---|---|
| Total referring domains | **4,164** |
| RDs with **22,637+** monthly organic traffic | **250** |
| RDs with **1,000–22,636** monthly organic traffic | **250+** (export capped) |
| **RDs with 1,000+ traffic — total** | **500+** ⚠️ true figure higher; API caps exports at 250 rows |

⚠️ **Methodology note:** the Ahrefs MCP export caps at 250 rows per query, so 500+ is a floor, not
a count. To quote an exact number in the deck we need paginated pulls — roughly 30 minutes of work.
**Do not put "500" in the deck as if it were precise.** Either quote it as "500+" or get the exact
figure first.

Top of the good-link segment is genuinely strong: Wikipedia, Google, Apple, Adobe, GitHub,
Forbes, Shopify, Salesforce, PCMag, Stack Overflow, Bloomberg, TechCrunch, Mastercard, Crunchbase,
PYMNTS, Fintech Futures, Fintech Magazine, Payments Dive.

**Read:** NMI's *good* links are good. There just are not many of them relative to the profile
size, and almost none point anywhere except the homepage (see `01-data-appendix.md` §C).

---

## 3. 🚩 Active spam link network — the significant finding

Filtering NMI's referring domains to Ahrefs' spam flag returns **250+ domains (export capped)**.
This is not historical noise. It is a live, ongoing network, and it validates exactly why score
alone cannot be the filter.

**The pattern:**

| Cluster | Examples | DR | Traffic |
|---|---|---|---|
| Explicit link-selling domains | `buybacklinks.agency`, `backlinker.shop`, `buyseobacklinks.shop`, `pbnseolinks.shop`, `authoritybacklinks.shop`, `rankrisebacklinks.shop` | 53–73 | **0** |
| "SEO Express" / "Link Baron" / "Outrank HQ" / "Rank Forge" `.store` network | `seoexpress-pbn-experts.store`, `master-rank-forge-pbn-league.store`, `link-baron-da-pa-luxury-directory.store`, `outrank-hq-dr-90-paramount-system.store` — **100+ domains** | 32 | **0** |
| Directory network | `topbilliondirectory.com`, `rankfastdirectory.com`, `worldzonedirectory.com`, `mostrankingdirectory.com` | 46–54 | **0** |

This connects directly to the Semrush anchor finding (`03-backlink-analysis-semrush.md` §4):
the anchor `telegram @seo_anomaly - seo backlinks, black-links, traffic boost, link indexing`
across 100 referring domains. **Same network.**

### Why this is the single best pitch asset

**Every one of these domains would pass a DR/AS filter. Almost none has any organic traffic.**
DR 32–74, traffic 0. If NMI or Battenhall are screening links on Authority Score alone, this
network is invisible to them — and it is currently pointing at nmi.com and growing.

That is a concrete, checkable demonstration of exactly the methodology point SUSO is selling:
**score plus traffic plus anchor, never score alone.**

### What we do and do not say
- **Do say:** it exists, roughly how large it is, that it is live, and that score-only screening
  misses it.
- **Do not say:** that it is causing a penalty, or that NMI needs an urgent disavow. We have not
  assessed impact, and over-claiming here is how the pitch loses credibility.
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
