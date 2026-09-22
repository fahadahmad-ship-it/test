# NFG Month-1 Off-Page Findings — Backlink Data Collection & Audit

**Target:** nationalfosteringgroup.co.uk (NFG) · **Snapshot:** 2026-09-22 · **Region:** UK
**Source firewall:** All metrics = **Semrush-only** (AS = Authority Score). Ahrefs not used here.
**Raw CSVs:** `/home/user/test/data/backlinks/` (benchmark + 5 reports × 10 domains + 3 NFG deep = 54 files).
No USD monetary fields were returned by these backlink reports (no cents→USD conversion needed).

---

## (a) 10-Domain Benchmark (Semrush `backlinks_comparison`, one call)

Follow% = follows ÷ (follows+nofollows) at backlink level. ToxTail% = ref domains AS 0–10 ÷ total (from `backlinks_ascore_profile`).

| Rank | Domain | Tag | AS | Ref Domains | Backlinks | Follow% | Ref IPs | BL/Domain | ToxTail% |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | thefosteringnetwork.org.uk | Sector Body | 39 | 1,892 | 18,972 | 72.8% | 1,939 | 10.0 | 45.5% |
| 2 | ★ **nationalfosteringgroup.co.uk** | **Target** | **36** | **420** | **1,743** | **79.3%** | **397** | **4.2** | **67.1%** |
| 3 | thefca.co.uk | Sector Body | 33 | 1,726 | 6,556 | 74.8% | 1,576 | 3.8 | 42.3% |
| 4 | capstonefostercare.co.uk | Commercial IFA | 29 | 813 | 127,526 | 30.0% | 825 | 156.9 | 77.1% |
| 5 | ispfostering.org.uk | Commercial IFA | 29 | 633 | 1,635 | 80.9% | 532 | 2.6 | 57.2% |
| 6 | compassfostering.com | Commercial IFA | 29 | 818 | 6,731 | 71.5% | 853 | 8.2 | 71.4% |
| 7 | fosteringpeople.co.uk | Commercial IFA | 28 | 847 | 5,210 | 89.6% | 789 | 6.2 | 49.4% |
| 8 | fosterplus.co.uk | Commercial IFA | 24 | 895 | 7,139 | 67.6% | 785 | 8.0 | 50.1% |
| 9 | orangegrovefostercare.co.uk | Commercial IFA | 24 | 825 | 1,150 | 75.6% | 733 | 1.4 | 49.8% |
| 10 | swiisfostercare.com | Commercial IFA | 23 | 300 | 1,270 | 66.1% | 259 | 4.2 | 78.0% |

**NFG position (framing numbers):**
- **Authority Score:** NFG 36 → **rank 2/10**, median 29, **gap-to-median +7**, gap-to-leader −3. Best of the 7 Commercial IFAs.
- **Referring Domains:** NFG 420 → **rank 9/10** (only swiis lower), median 821.5, **gap-to-median −401.5**. Field best 1,892.

**Read:** NFG's high AS sits on the smallest-but-one referring-domain base — a young, recently-inflated profile (see velocity). Off-site breadth is the primary constraint; the −401.5 ref-domain gap frames the Month-2+ deliverable.

*Capstone caveat:* 127,526 backlinks / 156.9-per-domain (30x cohort median) is a volume-inflation outlier — score on AS + ref domains, not raw backlink count.

---

## (b) NFG Critical Audit — issues with evidence

Evidence: E1 `historical_NFG.csv` · E2 `ascore_NFG.csv` · E3 `nfg_anchors.csv` · E4 `nfg_refips.csv` · E5 `nfg_refdomains_top100.csv` · E6 `categories_NFG.csv` · E7 `tld_NFG.csv` · E8 `benchmark_backlinks.csv`.

### ISSUE 1 — Severe velocity anomaly: entire profile ~8 months old [E1] (RED)
Flat at ~21 ref domains / AS 0–2 from early 2024 through Jan 2026, then: 2026-01 → 24 domains, AS 2; **2026-02 → 147 domains, +513% backlinks (28→486), AS 10**; 2026-06 → 296, AS 35; **2026-09 → 420, AS 36**. Net +399 ref domains in 8 months. Near-vertical velocity spike = bought/aggressive campaign signature. NFG's "rank-2 AS" is recency-inflated, not earned breadth.

### ISSUE 2 — Toxic tail: 67.1% of ref domains AS 0–10 [E2] (RED)
NFG toxic-tail 67.1% (AS-2 band alone = 127 domains) vs cohort median 53.6% → +13.5 pts, 2nd-worst of non-inflated peers. Distribution spikes at AS 0–6, not a healthy pyramid; trusted mid-band thin.

### ISSUE 3 — Explicit PBN / link-selling anchor footprint [E3] (RED)
Overt paid-scheme fingerprints against NFG and sister nfa.co.uk: "high quality dofollow backlinks da 50 pa 40 premium pbn network service … buy backlinks online cheap" (52+7 domains); "professional manual outreach backlinks for nationalfosteringgroup.co.uk … safe link velocity" (18); "professional seo authority backlinks for nfa.co.uk" (7). ~84 domain-hits (~21% of top-50 anchor sample). Live PBN/link-buying (or negative-SEO) — leading toxicity signal and disavow driver.

### ISSUE 4 — IP / subnet concentration (PBN signature) [E4] (RED)
25 ref domains on one IP 159.198.75.134 (US); 17 on 195.20.19.178 (Moldova) → 42 domains (~10%) on 2 IPs. Singapore 118.139.x subnet cluster = 23 domains across 5 IPs. Textbook PBN signatures, time-aligned with the Feb-2026 spike.

### CLEARED — money-anchor over-optimization NOT present [E3] (GREEN)
Money/exact-match commercial anchors ~1.9% of backlinks / 3.3% of anchor domain-hits — far below 10–15% single / 35% top-5 thresholds. Mix dominated by branded (nfa.co.uk 100 domains), naked URLs (~41% of domain-hits), generic ("website","here"), and empty anchors. Anchor risk is spam-tail, not commercial over-optimization.

### ISSUE 5 — Follow ratio high but not alarming alone [E8] (AMBER)
79.3% follow (backlink level) vs median 73.8%. Upper edge of healthy 50–75%, below the >90% manipulation line — fine alone, but with Issues 1–4 reads as engineered. DATA GAP: referring-domain-level follow% not returned by `backlinks_overview`; Tab 2 `Follow_RefDomains_%` needs a per-domain follow pull.

### ISSUE 6 — Topical relevance mediocre / diluted [E6] (AMBER)
NFG categories led by generic buckets (Business & Industrial 58, Arts & Entertainment 43, Internet & Telecom 41); fostering-core present but not dominant (Family 18, Social Issues 17). Contrast FosteringNetwork: People & Society 513, Law & Gov 480, Adoption 173, Social Services 141. NFG topical concentration thin, diluted by generic/spam tail.

### Positive signals — geo/TLD trust markers [E5, E7] (GREEN)
.gov.uk cluster: sandwell, wolverhampton, luton, havering, buckinghamshire (AS 44–50). Fostering/charity .org.uk: corambaaf (33), nff.org.uk (34), aff.org.uk (37), staf.scot, torbayfamilyhub. UK news: liverpoolecho (73), walesonline (72), leicestermercury (61), lancs.live, cheshire-live (supports NW strength). TLD: 74 .uk (17.6%) vs 221 .com (52.6%); .uk share modest for a UK-only business; .com majority + spam gTLD tail (.shop .online .top .sbs .monster .cfd) reflects PBN injection.

### Single-domain inflation [E5] (AMBER)
buzzsprout.com 193 backlinks (podcast host), nfa.co.uk 350 (sister brand), prnewslink.net 14 — each one ref domain, so no domain-count inflation, but read backlink totals per-domain.

---

## (c) Spam outliers (hu17.net-style patterns)

- **Not in NFG's profile.** The Appendix-A hu17.net→Capstone archetype does not appear against NFG; NFG's worst offenders are the PBN anchor/IP clusters (Issues 3–4).
- **Capstone confirms the archetype:** 127,526 backlinks / 813 domains = 156.9 per domain (30x median), 70% nofollow; tld_capstone shows .net = 31,592 backlinks from 18 domains and .eu = 18,402 from 6 — single-source injection consistent with hu17.net widget spam. Flag Capstone's backlink count as inflated.
- **Cohort:** swiis (78.0%) and compass (71.4%) also carry heavy toxic tails; FosteringNetwork (45.5%) and theFCA (42.3%) are cleanest/most topical.

---

## Data / method notes
- All 10 domains pulled at one snapshot via a single `backlinks_comparison` call (Tab 2 backbone).
- Semrush backlink reports are global (not region-filtered); UK framing is interpretive.
- Out of assigned pull scope: `Follow_RefDomains_%`, per-domain 12m new/lost split, `backlinks_geo` — flag as follow-ups if Tab 2/3 need those cells.
- Toxic-tail % from `backlinks_ascore_profile` domain counts; minor differences vs `backlinks_comparison` totals are expected (different aggregations).
