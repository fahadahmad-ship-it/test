# Backlink Audit — ngwindows.com (North Georgia Replacement Windows)

**Audit date:** 6 October 2026
**Target:** ngwindows.com (root domain)
**Data sources:** Semrush Backlink Analytics (full dataset, pulled 6 Oct 2026); Ahrefs free Domain Rating endpoint

> **Data-source note:** The Ahrefs Site Explorer API could **not** be queried for this audit — the
> workspace API unit allowance is fully consumed (800,068 / 800,000 used; resets **25 Oct 2026**).
> Every quantitative figure below therefore comes from **Semrush**. The only Ahrefs figure available
> was Domain Rating via the free public endpoint. Re-run the Ahrefs pulls after 25 Oct to
> cross-validate referring-domain counts and to use Ahrefs' link-level spam filters.

---

## 1. Verdict first

**ngwindows.com is sitting under an active, large-scale spam / PBN link blast.**

Roughly **two-thirds of the entire backlink profile (~4,900 of 7,444 links) is low-quality
link-vendor spam**, and almost all of it landed in the **last four months**. Referring domains grew
**+44% in September 2026 alone** (849 → 1,225). The anchor text is not just spammy — it is
*blatant*, consisting of literal SEO-vendor sales copy such as
*"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service … Buy Backlinks Online Cheap"*
and anchors containing **Telegram link-selling channel handles**.

This is either (a) a link vendor the client or a prior agency engaged, or (b) a **negative SEO
attack** — most likely the latter, or a vendor blasting a scraped list of window companies.

**Action required: build and submit a disavow file, and stop any active link-buying.**

---

## 2. Headline metrics

| Metric | Value |
|---|---|
| Semrush Authority Score | **30** |
| Ahrefs Domain Rating (free endpoint) | **27** |
| Total backlinks | **7,444** |
| Referring domains | **1,225** |
| Referring IPs | 1,141 |
| Referring class-C subnets | **428** |
| Follow links | 5,624 (75.6%) |
| Nofollow links | 1,896 (25.5%) |
| UGC links | 30 |
| Sponsored links | 0 (none declared — a problem, see §6) |
| Text links | 6,819 (91.6%) |
| Image links | 186 (2.5%) |
| Trust Score | 30 |

**Read on the ratios:**

- **1,141 IPs across only 428 class-C subnets** — an average of ~2.9 referring domains per subnet.
  Healthy organic profiles trend toward 1:1. This is a footprint of networked sites sharing hosting.
- **Authority Score 30 = Trust Score 30.** No trust premium at all. On a clean local-business
  profile you would expect Trust to sit at or above Authority.
- **Zero `rel="sponsored"` links** despite hundreds of obviously paid placements — the links are
  passing (or attempting to pass) PageRank, which is exactly what Google penalises.

---

## 3. Referring domain quality distribution

| Authority Score band | Referring domains | Share |
|---|---|---|
| **AS 0–5 (junk)** | **1,011** | **82.5%** |
| — of which **AS 2 exactly** | **886** | **72.3%** |
| AS 6–29 (weak/mid) | 149 | 12.2% |
| AS 30–49 (decent) | 54 | 4.4% |
| AS 50–79 (strong) | 8 | 0.7% |
| AS 80–100 (elite) | 4 | 0.3% |

**This is the single most damning chart in the audit.** 886 referring domains — nearly three
quarters of the entire profile — sit at exactly **Authority Score 2**. A tight cluster at one
identical score is the statistical signature of **machine-generated sites spun up from one template
by one operator**. Organic link profiles never look like this.

Only **65 referring domains (5.3%)** have an Authority Score of 30 or above. For a regional
home-improvement contractor, that small core is the *real* link profile — everything else is noise
or liability.

---

## 4. Anchor text analysis

### 4.1 The spam anchor clusters

| Anchor pattern | Ref. domains | Backlinks | First seen |
|---|---|---|---|
| `"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service <domain> Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap"` (9 rotating variants) | ~632 mentions | **905** | **29 Jun 2026** |
| `"<domain> Premium Link Building Experts…"` / `"Professional … SEO Backlinks…"` / `"Expert Backlink Building Services…"` (17 rotating variants) | ~1,282 mentions | **1,381** | **14 Sep 2026** |
| Bare competitor/sister domain names as anchor (`ngawindows.com`, `thermalprowindows.com`, `roiwindows.com`, `qualitypluswindows.com`, `northpointwindows.com`, `performingwindows.com`, `thermatrustwindows.com`, `northgeorgiawindows.net`, +6 more) | ~1,100 mentions | **2,579** | Jul 2025 → ongoing |
| `"Join our Telegram https://t.me/s/darksidelinks"` | 20 | 25 | Nov 2025 |
| `"Our Telegram chanel https://t.me/s/quarterlinks25"` | 4 | 4 | Jan 2026 |
| **Estimated spam total** | — | **~4,894 (66%)** | — |

### 4.2 The legitimate anchors

| Anchor | Ref. domains | Backlinks | Assessment |
|---|---|---|---|
| `ngwindows.com` | 201 | 496 | Naked URL — but heavily inflated by scraper sites |
| `north georgia replacement windows` | 31 | 41 | ✅ Branded, ideal |
| `<EmptyAnchor>` | 31 | 276 | Image/empty links, mostly scraper farms |
| `www.ngwindows.com` | 16 | 41 | ✅ Naked URL |
| `visit website` / `website` / `view website` | ~42 | ~117 | ✅ Generic, healthy |
| `ng windows` | 11 | 13 | ✅ Branded |
| `replacement windows` | 7 | 8 | ⚠️ Commercial exact-match |
| `window replacement company` | 5 | 14 | ⚠️ Commercial |
| `window replacement company atlanta` | 5 | 10 | ⚠️ Commercial, geo |
| `windows atlanta` | 5 | 7 | ⚠️ Commercial, geo |
| `vinyl windows atlanta` | 4 | 9 | ⚠️ Commercial, geo |
| `window replacement atlanta` | 2 | 6 | ⚠️ Commercial, geo |
| `window companies atlanta ga` | 2 | 2 | ⚠️ Commercial, geo |

### 4.3 Anchor verdict

Setting the spam aside, the **genuine** anchor mix is actually *fine*: it is dominated by branded
and naked-URL anchors, with only ~30 referring domains on commercial exact-match terms. There is
**no organic over-optimisation problem**. The problem is entirely external and injected.

**The most diagnostic finding in the whole audit:** the spam pages use **other window companies'
domain names as anchor text while linking to ngwindows.com**. All of those sister domains check out
at **Ahrefs DR 0** (`ngawindows.com`, `thermalprowindows.com`, `qualitypluswindows.com`,
`roiwindows.com`, `northpointwindows.com`, `performingwindows.com`, `thermatrustwindows.com`,
`northgeorgiawindows.net` — every one DR 0). That means a single vendor is running one template
across a scraped list of window-replacement companies and rotating the anchors randomly. ngwindows.com
is one name on that list, not necessarily the buyer.

**→ Confirm with the client whether they, or any agency they have used since June 2026, purchased
link-building services. The answer determines whether this is a cleanup or a defence.**

---

## 5. Link velocity — when it happened

| Month | Backlinks | Ref. domains | Δ domains |
|---|---|---|---|
| May 2024 | 2,573 | 379 | — |
| Dec 2025 | 3,906 | 572 | — |
| Jan 2026 | 3,154 | 560 | −12 |
| Feb 2026 | 3,243 | 535 | −25 |
| Mar 2026 | 3,932 | 562 | +27 |
| Apr 2026 | 4,435 | 575 | +13 |
| May 2026 | 4,827 | 585 | +10 |
| Jun 2026 | 4,921 | 590 | +5 |
| **Jul 2026** | 5,113 | 535 | −55 |
| **Aug 2026** | 5,561 | 583 | +48 |
| **Sep 2026** | 6,910 | **849** | **+266** |
| **Oct 2026** | **7,444** | **1,225** | **+376** |

For roughly two years the profile sat flat at 350–590 referring domains — normal for a local
contractor. Then **referring domains more than doubled in 60 days**. A +44% month-over-month jump
with zero corresponding PR, campaign, or content push is the exact pattern Google's link-spam
systems are built to detect.

Note also the Authority Score has **drifted down from 33 (Jun 2024) to 30** across the same period
the link count tripled. More links, less authority — the new links are carrying negative or zero value.

---

## 6. Geographic & TLD footprint

### Referring domains by country

| Country | Domains | Backlinks | Links per domain |
|---|---|---|---|
| **Singapore** | 70 | **2,133** | **30.5** 🚩 |
| United States | 246 | 1,391 | 5.7 |
| **Moldova** | 19 | 263 | 13.8 🚩 |
| France | 15 | 66 | 4.4 |
| Germany | 8 | 12 | 1.5 |
| Canada | 7 | 9 | 1.3 |
| India | 5 | 12 | 2.4 |
| United Kingdom | 5 | 8 | 1.6 |

**70 Singaporean domains are responsible for 2,133 backlinks** — 29% of the entire profile from
0.06% of the world. A domestic Atlanta-area window installer has no legitimate reason for this. These
are the auto-generated "website worth / domain stats" scraper farms (`domainanalysis.org`,
`getwebsiteworth.com`, `bestwebstats.com`, `websiterace.com`, `webworthchecker.cv`, `wallpapers.pro`,
`allwebsitesdirectory.com`, …), all AS 2–4, all Singapore-hosted, 30–64 links each.

### Referring domains by TLD

| TLD | Domains | Backlinks |
|---|---|---|
| .com | 494 | 3,980 |
| **.shop** | 118 | 368 |
| **.online** | 84 | 229 |
| .info | 77 | 374 |
| **.space** | 66 | 139 |
| **.site** | 64 | 124 |
| **.link** | 60 | 171 |
| **.store** | 58 | 120 |
| **.website** | 57 | 119 |
| .org | 19 | 256 |
| .net | 16 | 170 |
| .in | 15 | 342 |
| .top / .cv / .sbs / .monster / .art / .pro | 21 | 610 |

**584 referring domains (47.7%) sit on throwaway TLDs** — `.shop`, `.online`, `.space`, `.site`,
`.link`, `.store`, `.website`, `.sbs`, `.monster`, `.cv`, `.top`. These registrations cost $1–3 and
exist almost exclusively for link spam. No real Atlanta-area business links to a window installer
from a `.monster`.

---

## 7. The toxic networks, named

Three distinct operations are visible in the data.

### Network A — "DA/PA checker" PBN directory (highest risk 🔴)
Hundreds of template sites on cheap TLDs, all serving pages under a `/dir/` path, all **dofollow**,
all with SEO-vendor sales-copy anchors. Examples seen in the newest-links pull:

`dacheckertoolonline.site` · `rankwebsitechecker.website` · `onlinewebsitechecker.space` ·
`padacheckertools.shop` · `onlinedapachecker.site` · `backlinkrankchecker.shop` ·
`dapafreechecker.website` · `padachecker.site` · `goodbacklinkchecker.space` ·
`seoblogchecker.store` · `freesiterankchecker.online` · `linkaudit.space` ·
`trustflowchecker.space` · `bestseochecker.shop` · `big-easy-seo.com` · `seostrengthchecker.online` ·
`dacheckerbulkfree.online` · `backlinkscheckerbulk.space` · `domainmetricschecker.store` ·
`highdachecker.space` · `blogseochecker.online` · `bulkbacklinkanalysis.website` ·
`backlinkcheckers.online` · `backlinkcheckerseo.online` · `livebacklinkchecker.online` ·
`dapacheckermultiple.website` · `dapacheckerfree.site` · `bulkpachecker.online` ·
`dabacklinks.website` · `siteseocheckerfree.shop` · `dacheckeronline.store` ·
`whatisdapachecker.space`

**Disavow at domain level. This is the priority target.**

### Network B — Fake guest-post / "niche edit" network (high risk 🔴)
Dofollow links from long auto-generated URLs with SEO-service anchors:

`ggmap.co.com` · `newearthsummit.org` · `nivira.shop` · `mertio.shop` · `bestseoquill.site` ·
`seonix.agency` · `backlinkhouse.com` · `backlinkstree.com` · `seodomains.website` · `goooogla.com`

Note `seonix.agency` is publishing fake testimonials ("*After hiring northgeorgiawindows.net for
niche edits, my sales doubled within 1 month 💰*") — a clear link-vendor shill network.

**Disavow at domain level.**

### Network C — Auto-generated domain-stats scrapers (low risk 🟡)
Singapore-hosted "what is this website worth" scrapers. Google generally ignores these, so they are
unlikely to cause harm, but they bloat the profile and distort every metric:

`domainanalysis.org` · `allwebsitesdirectory.com` · `domainsc.com` · `wallpapers.pro` ·
`bestwebstats.com` · `domain.com.lc` · `linksnatcher.com` · `getwebsiteworth.com` ·
`globalecommerce.org` · `websiterace.com` · `webworthchecker.cv` · `indexaward.com` ·
`pagesearch.net` · `egyptiandirectory.com` · `alljobs.info` · `tunca.org` · `way2check.cv` ·
`way2check.art` · `pudhe.com` · `wonvision.com` · `ycm.info` · `read.org.in` · `procycling.org` ·
`taxies.biz` · `theface.in` · `tyres.pro` · `homefinance.co.in` · `preparation.co.in` ·
`indians.cc` · `takes.sbs` · `knows.sbs` · `knows.monster` · `blinks.monster` · `wants.cfd` ·
`seol.store` · `takes.homes` · `bizscoreai.com` · `factmags.com` · `csswinner.com`

Plus blogspot spam: `burnersgamershitasd.blogspot.com` (110 links) ·
`oozeas.blogspot.com` (104) · `innocyscx.blogspot.com` (38).

**Disavow — second priority.** Optional but recommended for profile hygiene.

---

## 8. The assets worth protecting

The genuine link profile underneath the spam is small but respectable for a local contractor:

| Domain | AS | Links | Type |
|---|---|---|---|
| apple.com | 100 | 2 | Maps / business data |
| pinterest.com | 100 | 4 | Social |
| yahoo.com | 100 | 4 | Directory |
| bing.com | 96 | 1 | Business listing |
| **bbb.org** | 78 | 2 | ✅ Trust signal |
| **nextdoor.com** | 73 | 3 | ✅ Local |
| zoominfo.com | 70 | 1 | Business data |
| **yellowpages.com** | 69 | 5 | ✅ Citation |
| barbend.com | 56 | 1 | Editorial |
| brightside.me | 50 | 1 | Editorial |
| re-thinkingthefuture.com | 49 | 1 | ✅ Architecture — on-topic |
| **chamberofcommerce.com** | 48 | 3 | ✅ Local trust |
| housedigest.com | 48 | 1 | ✅ Home & garden |
| constantcontact.com | 47 | 394 | Own newsletter archive |
| **expertise.com** | 47 | 2 | ✅ Vetted local directory |
| superpages.com | 47 | 15 | ✅ Citation |
| **diamondcertified.org** | 38 | 2 | ✅ Contractor trust |
| **qualifiedremodeler.com** | 36 | 1 | ✅ Trade publication |
| porch.com | 36 | 1 | ✅ Home services |
| fixr.com | 41 | 1 | ✅ Home services |
| **glass.com** | 31 | 1 | ✅ Industry-relevant |
| williamsonchamber.com | 33 | 6 | ✅ Local chamber |
| roswell365.com | 32 | 2 | ✅ Hyperlocal |
| threebestrated.com | 32 | 1 | ✅ Local directory |
| dexknows.com | 37 | 9 | ✅ Citation |
| 24-7pressrelease.com | 40 | 11 | ⚠️ Paid PR — low value |

**Topical relevance is sound.** The referring-domain category profile shows Business & Industrial
(86), Home & Garden (62), Home Improvement (56), **Doors & Windows (38)**, Construction &
Maintenance (41), Building Materials (34). The *real* links are from the right neighbourhood — the
foundation is fine.

---

## 9. Recommended action plan

### Immediate (this week)

1. **Ask the client the direct question:** has anyone — the client, a prior agency, a freelancer,
   a Fiverr/Telegram vendor — bought links or "SEO packages" since June 2026? This determines
   whether you are cleaning up a mistake or defending against an attack.
2. **If links were bought: stop immediately** and request removal from the vendor.
3. **Submit a disavow file** to Google Search Console. A draft is provided at
   `backlink-audit/disavow-ngwindows.txt` in this repo. Disavow at **domain level** (`domain:`),
   never URL level, for networks this large.
4. **Check Search Console** for a manual action under Security & Manual Actions. If one exists, the
   disavow must be paired with a reconsideration request.
5. **Baseline the organic traffic and rankings now** so the recovery curve is measurable.

### Short term (2–6 weeks)

6. **Re-run the Ahrefs pulls after 25 October 2026** when API units reset. Cross-reference Ahrefs'
   referring domains against the Semrush list — each tool's crawler finds links the other misses,
   and the disavow should cover the union, not just the Semrush set.
7. **Paginate the full Semrush referring-domain list** (1,225 domains; this audit sampled the top
   110 by authority and by link volume). Build the complete disavow from the full export.
8. **Audit the `constantcontact.com` 394 links** — confirm these are the client's own newsletter
   archive and not a compromised account.
9. **Set up weekly new-referring-domain monitoring.** If the blast is ongoing (and the data says it
   is — links are landing hourly as of the audit date), the disavow file needs refreshing monthly
   until it stops.

### Medium term (2–6 months)

10. **Rebuild the real profile** against the asset list in §8: local chambers (Alpharetta, Roswell,
    Cumming, Forsyth County), Georgia home-builder and remodeler associations, Atlanta home &
    garden press, manufacturer dealer-locator pages, and genuine Home Improvement /
    Doors & Windows editorial.
11. **Target a healthy anchor mix** as new links come in: ~50% branded, ~25% naked URL, ~15%
    generic, ~10% partial-match. Avoid exact-match commercial anchors entirely until the profile
    has recovered.
12. **Re-audit in 90 days.** Success metrics: Trust Score rising above Authority Score;
    AS 0–5 band falling below 50% of referring domains; class-C-to-domain ratio approaching 1:1.

---

## 10. Risk summary

| Risk | Severity | Evidence |
|---|---|---|
| Active link-spam / PBN blast | 🔴 **Critical** | ~4,894 spam links (66%); +376 ref. domains in one month |
| Possible negative SEO attack | 🔴 **Critical** | Anchors naming 14 other DR-0 window-company domains |
| Unnatural link velocity | 🔴 **High** | Ref. domains +44% MoM, Sep→Oct 2026 |
| Junk-tier referring domains | 🔴 **High** | 82.5% at AS 0–5; 886 domains at AS 2 exactly |
| Paid links not disclosed | 🟠 **Medium** | 0 sponsored tags across hundreds of paid placements |
| Geographic mismatch | 🟠 **Medium** | 29% of links from 70 Singapore domains |
| Cheap-TLD concentration | 🟠 **Medium** | 47.7% of ref. domains on throwaway TLDs |
| Subnet clustering | 🟠 **Medium** | 1,141 IPs across only 428 class-C subnets |
| Organic anchor over-optimisation | 🟢 **Low** | Genuine anchors are branded/naked-URL dominant |
| Topical relevance of real links | 🟢 **Low** | Home Improvement / Doors & Windows categories strong |
