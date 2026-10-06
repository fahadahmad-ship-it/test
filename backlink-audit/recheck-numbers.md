# Re-check of Every Quantitative Claim — ngwindows.com Backlink Audit

**Auditor role:** independent data verification. Every figure below was re-derived from the raw
files with scripts written from scratch (`/home/user/scripts/lib.py`, `s1.py`–`s8.py`, run with
`python3 -I`). No existing script output was trusted.

**Evidence base actually used**

| File | Provenance | Shape |
|---|---|---|
| `backlink-audit/data/refdomains.csv` | working tree | **1,232** data rows, 1,232 unique domains, no blanks |
| `backlink-audit/data/anchors_observed.csv` | working tree | **76** rows, 73 distinct source domains |
| `backlink-audit/work/links_raw.tsv` | recovered from git commit **6f5f407** (deleted in 469162b — *not* present in 469162b as the brief stated) | **3,500** rows → **2,532** unique links, **878** distinct hosts → **829** registrable domains |
| `backlink-audit/work/anchors_multi.csv` | recovered from git commit **db9dcd8** | 87 multi-referring-domain anchors, `domains_num` sum 3,432, `backlinks_num` sum **6,336** |
| Ahrefs free DR endpoint | live, 2 bulk calls, 127 targets, 0 units | DR for all cluster + PROTECTED domains |

**One structural discovery drives several of the verdicts below.** `links_raw.tsv` is not one
pull. Rows 1–1,000 are a distinct block (all 1,000 unique; the first duplicate row in the file is
at index 1,000; mixed `page_authority_score` values, mean 0.49). Rows 1,001–3,500 are a second
block (2,500 rows, 1,896 unique, **every** row `page_authority_score = 0`). These correspond
exactly to the documents' "sample A" (1,000 links, `last_seen_desc`) and "sample B"
(`page_authority_score_asc`). **Sample B as reported — "2,532 unique links / 878 domains" — is the
deduplicated union of both blocks.** Sample A is a strict subset of sample B. This is the single
most important finding in this re-check and it invalidates the claim that the two estimates are
independent corroboration.

---

## 1. Claims CONFIRMED

### 1.1 Referring domains = 1,232 (enumerated file)
`refdomains.csv` holds exactly **1,232** data rows, **1,232 unique** domain strings, zero
duplicates, zero blank `ascore`. The `links` column sums to **7,547**. Confirmed. (The 1,225 /
1,227 variants are addressed in §2.1.)

### 1.2 The AS 0–5 band = 1,015 domains / 6,078 links
Re-derived: `ascore <= 5` → **1,015 domains**, **6,078 links**, **82.39%** of 1,232 domains.
`toxic-domain-inventory.md` is correct. Band is dominated by a single integer value: AS 2 alone
holds **888** domains (the documents say "886" — see §2.6).

### 1.3 "6.3% individually evidenced (64 of 1,015)"
Exactly reproduced from `anchors_observed.csv`: 76 links, 73 distinct source domains, 71 of which
appear in `refdomains.csv` (`urlbacklinkschecker.space` and `backlinkcheckerseo.space` do not —
the documents' note that Semrush's two endpoints disagree is confirmed), 70 of the 73 are AS 0–5,
and **64** carry a vendor sales-copy anchor on a dofollow link → **6.31%** of 1,015. Two further
domains carry vendor copy but are nofollow, matching the "2 failed the dofollow gate" line.
**Arithmetically confirmed — but see §2.4: this is the wrong evidence base to have used.**

### 1.4 Follow/nofollow split per anchor bucket (98% / 52%)
Re-derived link-level over all 2,532 unique links with my own classifier:

| Bucket | Links | Dofollow | Nofollow | % dofollow | Published |
|---|---:|---:|---:|---:|---|
| Vendor sales copy | 1,339 | **1,320** | 19 | **98.6%** | 1,342 / 1,320 / 22 → 98% ✅ |
| Bare sister-domain name | 751 | **391** | 360 | **52.1%** | 753 / 391 / 362 → 52% ✅ |
| Naked URL / brand | 222 | 79 | 143 | 35.6% | 239 → 38% ✅ |
| Empty / generic | 99 | 62 | 37 | 62.6% | 102 → 63% ✅ |
| Topical | 97 | 61 | 36 | 62.9% | 81 → 62% ✅ |
| Other | 24 | 17 | 7 | — | 15 → 93% ~ |

Dofollow counts match the published table to the unit (1,320 and 391). **§6A.2 of
`anchor-and-attribution-forensics.md` is the most reliable table in the document set.** The
98% / 52% contrast — and therefore the conclusion that the vendor campaign and the bare-domain
scraper cluster are two separate events — holds.

### 1.5 Host clusters 118.139.181.85, 203.161.54.114, 195.20.19.178
Counted directly off the `ip` column of `refdomains.csv`:

| IP | Claimed | Re-derived | Verdict |
|---|---|---|---|
| 118.139.181.85 | 29 domains / 727 links | **29 / 727** | ✅ exact |
| 203.161.54.114 | 27 domains / 186 links | **27 / 186** | ✅ exact |
| 195.20.19.178 | 19 domains / 263 links | **19 / 263** | ✅ exact |

These are also the top three IPs in the file by domain count, in that order. Confirmed.

### 1.6 Anchor-export arithmetic behind the spam volume (§6.2)
Every "measured" cell of `anchor-and-attribution-forensics.md` §6.2 reproduces exactly from
`anchors_multi.csv` under explicit rules (§2.5 below for the rules):

| Bucket | Re-derived links | Re-derived `domains_num` | Published |
|---|---:|---:|---|
| Bare redirect-shell anchors | **2,757** | **1,049** | 2,757 / 1,049 ✅ |
| Vendor copy naming a shell | **2,058** | **1,701** | 2,058 / 1,701 ✅ |
| Vendor copy naming ngwindows.com + Telegram | **263** | **243** | 263 / 243 ✅ |
| Redirect-borne total | **4,815** | — | ~4,815 ✅ |
| All spam, measured | **5,078** (+~20 estimated tail = 5,098) | — | ~5,098 ✅ |
| Vendor sales copy, all | **2,321** | — | ~2,321 ✅ |
| 87 anchors cover | **6,336 of 7,444 (85.1%)** | — | 6,336 / 85.1% ✅ |

### 1.7 The DR 59–60 seller block is real (mostly) — and the PROTECTED list is accurate
Bulk-verified live on the free endpoint, zero units:

- **25 of the 27** domains on 203.161.54.114 return **DR 59.0–60.0** (24 at exactly 60.0,
  `99backlinksbuy.com` at 59.0). A uniform DR 60.0 block across 24 unrelated registrations on one
  IP is a genuine authority-inflation signature. The qualitative finding stands.
- All **15 PROTECTED** domains verified and every published DR is correct:
  `forsythcounty.com` 3.6, `georgiashutters.com` 2.2, `1stcallglasscare.com` 2.9 (published "3"),
  `alpharettatoprated.com` 10, `lombardohomegroup.com` 13, `windowdigest.com` 15,
  `homerenoworld.com` 16, `athomepros.com` 18, `koalatyremodel.com` 27,
  `roswell365.com` 39, `atlantahomeimprovement.com` 45, `members.williamsonchamber.com` 49,
  `eurekster.com` 53, `csswinner.com` 75, `factmags.com` 75.
- All **14 redirect shells** return **DR 0.0**. `ngwindows.com` returns **DR 27**.
  `seonix.agency` **DR 65**, `best-seo-domains.com` **DR 59**. All as published.

**The "authority is anti-correlated with manipulation" thesis survives and is strengthened.**
Two further bulk checks I ran that the documents never did: the 29-domain Singapore farm on
118.139.181.85 runs **DR 0.0–2.5** (one outlier at 9), while the 19-domain Moldova shortener
network on 195.20.19.178 runs **DR 36–54** (mean ~41, also a tight block). A 40-domain sample of
Network A `/dir/` sites runs **DR 0.0–1.7**. So tight DR blocks are a *hosting-cluster* artifact
appearing at three different levels in this profile, not something unique to the 60s.

### 1.8 Disavow file size = 33 entries
`disavow-ngwindows.txt` contains exactly **33** `domain:` lines (5 in Section 1, 28 in Section 2).
`FINAL-AUDIT.md` is right.

---

## 2. Claims REFUTED

### 2.1 🔴 "1,225 / 1,227 / 1,232 referring domains" — 1,232 is the only defensible figure, and the other two are not interchangeable
The enumerated file contains 1,232 unique domains and that is the number to use. The other two are
**Semrush aggregate-counter readings taken at different moments**, not alternative counts of the
same list: `audit-review-and-gaps.md` reports 1,227 alongside a total-backlinks figure of 7,449,
`ngwindows-backlink-audit.md` reports 1,225 alongside 7,444, and the enumerated file sums to
7,547. All three move together, which is the signature of a live, growing profile sampled on
different days — consistent with the documents' own statement that the newest link is dated
6 Oct 2026 15:01 UTC (confirmed: that is exactly the max `first_seen` in the file; min is
2023-05-20).

**Why this matters more than it looks:** several published percentages divide a count taken from
the 1,232-row file by a denominator of 1,225 or 1,227. That is a real, if small, error, and it is
the direct cause of the 1,011/1,015 discrepancy (§2.2).

**Use 1,232. Never mix denominators within one calculation.**

### 2.2 🔴 "1,011 AS 0–5 domains" is wrong — it is 1,015
`ngwindows-backlink-audit.md` (1,011 = 82.5%), `impact-and-recovery-roadmap.md` (1,011 = 82.4%)
and `anchor-and-attribution-forensics.md` §6A ("~1,011") all carry the stale figure.
**Correct: 1,015 domains, 82.39% of 1,232, 6,078 backlinks.** The 1,011 came from the earlier
1,225-domain enumeration and was never refreshed when the list was re-paginated to 1,232.
`toxic-domain-inventory.md` has it right.

### 2.3 🔴🔴 "84.3% (sample A) and ~84% (sample B) agree" — the agreement is an artifact. The samples are not independent, and 84.3% is not reproducible.

Three separate failures, in increasing order of severity.

**(a) 84.3% does not reproduce. The correct sample-A figure is 87.4%.**
I replicated the published method exactly — including a byte-for-byte reimplementation of
`anchor-band-analysis.py`'s own regexes and registrable-domain resolution — against block A of
`links_raw.tsv`. Every cell of the published link-level table reproduces within 0–2 links
(bare sister-domain dofollow: 93 published vs **93** mine; empty/image: 1/1 vs **1/1**; brand
dofollow: 20 vs **20**) **except the vendor row**, which is published at 584 dofollow / 7 nofollow
against my **716 / 9**. Correspondingly 998 of block A's 1,000 links resolve to a scored referring
domain, against the published "855 of 1,000", and block A touches **620** distinct AS 0–5
registrable domains, against the published **485**.

The pattern is unambiguous: the input file fed to `anchor-band-analysis.py` was missing ~143 of
the 1,000 links, and **~133 of the 135 missing domains were vendor-anchor domains**. I could not
determine the loss mechanism (no semicolons, quotes, embedded newlines or pipes appear in block
A's anchors; only 6 rows contain any non-ASCII character), so the mechanism is unverifiable — but
the effect is not. Sample A's domain-level table should read:

| Classification | Published | **Re-derived** |
|---|---:|---:|
| Vendor sales copy | 409 (84.3%) | **542 (87.4%)** |
| Bare sister-domain only | 50 (10.3%) | **50 (8.1%)** |
| Topical only | 12 (2.5%) | **12 (1.9%)** |
| Brand / naked URL only | 12 (2.5%) | **14 (2.3%)** |
| Empty / image only | 2 (0.4%) | **2 (0.3%)** |
| **Base** | **485** | **620** |

The published sample-A coverage claim — "485 of ~1,011, 48%" — should read **620 of 1,015, 61%**.
The direction of the error is to *understate* vendor share.

**(b) The two samples share 100% of sample A. "Independent" is false.**
- Sample A's 1,000 links are **all** inside sample B's 2,532 (sample B is defined as the dedupe of
  A+B blocks).
- Of sample A's 1,000 links, **364 (36.4%)** also appear verbatim in the second block.
- At domain level the dependence is near-total: sample A contributes **663 of sample B's 875**
  registrable domains — **75.8%**. In the AS 0–5 band specifically, sample A supplies **620 of
  sample B's 805** — **77.0%**.

Two estimates computed over populations that are 76% the same observations are not corroboration.
They are one estimate reported twice. **The documents' framing — "the first two agree closely and
are the honest estimate" (`FINAL-AUDIT.md` §4) — must be struck.**

**(c) Once the shared observations are removed, the estimate collapses from ~84% to 47%.**
This is the test the documents never ran. Restricting to the **185 AS 0–5 domains that appear only
in the second block** — i.e. the genuinely new observations the `page_authority_score_asc` pull
added:

| Dominant anchor bucket | Domains | Share |
|---|---:|---:|
| **Vendor sales copy** | **87** | **47.0%** |
| Bare sister-domain | 30 | 16.2% |
| Naked URL / brand | 27 | 14.6% |
| Topical | 24 | 13.0% |
| Empty / generic | 16 | 8.6% |
| Other | 1 | 0.5% |

**47.0%, not 84%.** Vendor share nearly halves the moment the recency-sorted block stops
contributing. Sample B's headline "~84%" is sample A's 87% diluted by a tail that is only 47%
vendor — it lands at 78.1% over the full 805-domain union under my classifier, and the published
~84% is an extrapolation on top of that.

**Where the recency sort inflates the number, stated explicitly.** Block A was pulled
`last_seen_desc`. The campaign is live — the file's newest `first_seen` is the audit date itself,
and the documents' own §6 records 284 new Network-A-styled domains in the 14 days to 6 Oct. A
recency sort therefore returns, preferentially, the links of whichever campaign is firing *today*,
which is precisely the vendor campaign. Every percentage computed on block A — and, because of the
contamination in (b), every percentage computed on the union — is biased upward by this. The
`as0-5-anchor-evidence.md` caveat ("these numbers are an upper bound on toxicity, not a lower one")
is correct in direction and badly understated in magnitude: the gap between the biased and
unbiased estimates is **40 percentage points**, not a few.

**Defensible replacement.** Of the 1,015 AS 0–5 domains, **805 (79.3%)** have at least one
observed anchor in `links_raw.tsv`; **629 of those 805 (78.1%)** carry vendor sales copy as their
worst anchor. The **210 domains with no observation at all** are, by the sampling design, the least
recently active and least sampled — the subpopulation measured at 47%, not 84%. The band-wide
vendor share is therefore bounded:

> **Floor 62.0%** (629 / 1,015, assuming every unobserved domain is benign)
> **Ceiling 82.7%** (839 / 1,015, assuming every unobserved domain is vendor)
> **Best estimate ~66%** (629 observed + 47% of the 210 unobserved)

Report the band as **"roughly two in three, bounded 62–83%"**, not "five in six".

### 2.4 🔴🔴 The "6.3% individually evidenced" figure is arithmetically right and methodologically indefensible — the real figure is 60.8%
`toxic-domain-inventory.md` builds the entire disavow file on the premise that only 64 of 1,015
AS 0–5 domains "can currently be shown to be manipulative", because "the API ran dry" after one
76-link page. **That premise is false.** `links_raw.tsv` — 2,532 individually attributed links with
per-link anchor and per-link `nofollow`, sitting in this repository's own git history and
explicitly cited by `anchor-and-attribution-forensics.md` — contains, by the documents' own
criterion-1 standard (observed vendor sales-copy anchor **+** observed dofollow):

> **617 AS 0–5 referring domains — 60.8% of the band — individually evidenced.**
> (623 domains across all authority bands; 621 of them present in `refdomains.csv`.)

That is a **9.6×** understatement. The "73 domains / 76 links" evidence base is not the extent of
the anchor data that was retrieved; it is one page of it. Every downstream statement built on the
6.3% figure — "93% of the AS 0–5 band has no anchor evidence either way", "anchor-verified
coverage 73 of 1,232 (5.9%)", "1,159 domains excluded as insufficient evidence", and the decision
to cap the disavow file at 33 lines — inherits the error.

Related: `links_raw.tsv` shows **501 distinct domains serving `/dir/` template paths** (499 of them
in `refdomains.csv`, 498 of them AS 0–5). The documents size Network A at **59** evidenced domains
and treat the other ~360 similarly-named domains as "likely, and likely is not evidence". They are
evidenced — the evidence was in the file.

**This does not mean disavow 617 domains.** It means the stated reason for not doing so (no data)
is wrong, and the decision must be re-taken on its merits with the real coverage figure in view.
The separate and still-valid argument against disavowing most of them is the redirect-scope rule:
the overwhelming majority target shell domains, not ngwindows.com.

### 2.5 🟠 Spam volume: 5,098 and 4,815 are right; 4,894, 2,286 and 2,579 are undercounts of the same quantities
All four published figures are the same measurement at different levels of completeness. My
bucketing rules, applied to `anchors_multi.csv` (`backlinks_num`, additive, mutually exclusive by
exact anchor string — the documents' choice of basis is correct and I adopt it):

> **V-shell** — anchor matches a link-vendor lexicon (`backlink`, `dofollow`, `pbn`, `seo link`,
> `link building`, `guest post`, `niche edit`, `da NN`, `t.me/`, `white hat`, `domain authority`,
> `outreach`, `serp`, `premium/quality link`, `HQDF`) **and** names one of the 14 shell domains.
> **V-direct** — same lexicon, names `ngwindows.com` (or a Telegram handle) instead.
> **S-bare** — anchor is *only* a shell domain name or a bare `https://shell/` URL.
> **Clean** — everything else (naked client URL, brand, empty/image, generic CTA, topical).

| | Links | % of 7,444 |
|---|---:|---:|
| S-bare (shell-name anchors) | **2,757** | 37.0% |
| V-shell | **2,058** | 27.6% |
| V-direct | **263** | 3.5% |
| **Total measured spam** | **5,078** | **68.2%** |
| Clean | 1,258 | 16.9% |
| (unclassified single-domain anchor tail) | 1,108 | 14.9% |

Reconciling the four published numbers:

- **5,098** = 5,078 measured + ~20 estimated long tail. ✅ sound.
- **4,815** redirect-borne = 2,757 + 2,058. ✅ exact. **283 direct** = 263 + ~20. ✅ sound.
- **2,321** vendor sales copy = 2,058 + 263. ✅ exact (and the 263 decomposes exactly as
  104 + 46 + 84 + 25 + 4).
- **2,579** (red-team "Cluster 3") ❌ **undercount**. It sums the 14 bare shell-*name* anchors but
  omits the 5 bare shell-*URL* anchors (`https://roiwindows.com/` 120, `https://northpointwindows.com/`
  18, `https://thermalprowindows.com/` 16, `https://thermatrustwindows.com/` 15,
  `https://ngawindows.com/` 8 = **177**). 2,580 + 177 = **2,757**.
- **2,286** (red-team "Clusters 1+2", the recommended replacement headline) ❌ **undercount by 35**.
  Correct figure for the same bucket is **2,321**.
- **4,894** (draft) ❌ = 2,286 + 2,579 + 29 Telegram. Same quantity as 5,098, computed over an
  incomplete anchor set. Not double-counted — the red team was right about that — just short.

**The defensible figures to publish:**

| Measure | Figure | Status |
|---|---:|---|
| Links carrying explicit vendor sales copy | **2,321 (31.2%)** | measured, ~98.6% dofollow → ~2,289 dofollow |
| Bare shell-domain anchors | **2,757 (37.0%)** | measured, 52.1% dofollow → ~1,436 dofollow |
| **All spam** | **5,078 measured / ~5,098 incl. tail (68.2–68.5%)** | measured |
| **Unambiguously hostile dofollow core** | **~2,289** | the number to lead with |
| Redirect-borne / direct split | **4,815 / ~283** | measured |

The red team's substantive point survives intact and should be kept: counting the 2,757 bare-anchor
links as hostile is wrong, because **48% of them are nofollow** and they predate the blast by a
year. "68.5% spam" is an honest *volume* figure and a misleading *risk* figure.

### 2.6 🟠 "886 domains at Authority Score 2" — it is 888
Minor, and the line is already withdrawn on sound methodological grounds. Noted for completeness:
the AS histogram is 0→12, 1→2, **2→888**, 3→33, 4→52, 5→28.

### 2.7 🟠 Cloudflare: 861 is right only under the narrow range list; the correct figure is 866 (70.3%)
Testing the `ip` column against the four ranges named in the brief (104.16–104.31.x, 172.64–172.71.x,
162.158.x, 198.41.x) returns **exactly 861** — so the published figure is reproducible and was
computed honestly. But 162.158.x matches **zero** rows and 198.41.x matches zero; the real
composition is 104.16.0.0/12 → 413 and 172.64.0.0/13 → 448. Testing against Cloudflare's **complete**
published IPv4 list adds 5 domains on 162.159.x: **866 of 1,232 = 70.3%**.

**A far more important fact is buried here, and no document states it.** Of the 1,232 rows,
**860 have an empty `country` field — and all 860 are Cloudflare-fronted.** Cloudflare's anycast
front door destroys the geo attribution. So only **372 of 1,232 domains (30.2%) have any country
data at all**. This is load-bearing for §2.8.

### 2.8 🔴 Singapore: 69 domains / 2,107 links / 27.9% — not 70 / 2,133 / 29%
Direct count on `country == 'sg'`: **69 domains**, **2,107 links** = **27.9%** of 7,547
(28.3% of 7,444). All three published components are wrong, though only slightly.

**The framing is the bigger problem.** "29% of the profile" is reported as a geographic risk
signal, but per §2.7 the country field is null for 70% of the profile. The honest statement is:
*of the 372 domains for which country is known, 69 (18.5%) are Singapore and they carry 2,107
links* — concentrated on three stats-farm IPs (118.139.181.85 → 29, 184.168.115.60 → 9,
118.139.176.46 → 9). It is a hosting-cluster finding, not a geographic one, and it cannot be
expressed as a share of the whole profile.

### 2.9 🟠 "27 link sellers on 203.161.54.114, all at DR 59–60" — 25 of 27
The IP carries 27 referring domains, of which:
- **25** are seller-branded and return **DR 59.0–60.0** ✅
- **`factmags.com`** — **DR 75.0**, not a seller name (correctly PROTECTED)
- **`goooogla.com`** — **DR 29.0**, and it **is in Section 2 of the disavow file**

So the sentence "all 27 return DR 59–60" is false two ways: `factmags.com` is one of the 27 and is
DR 75, and `goooogla.com` is DR 29. There is also an internal contradiction the documents never
caught — `toxic-domain-inventory.md` says factmags is "co-hosted with 27 domains" *and* that there
are "27 sellers", which would require 28 domains on the IP. There are 27 in total.

Section 2 of the disavow file likewise is **not** "27 domains sharing host 203.161.54.114 at
uniform DR 59–60". Its 28 entries are: **26** from that IP (25 at DR 59–60 + `goooogla.com` at
DR 29), plus `best-seo-domains.com` (DR 59, different host) and `backlinks-checker.com`
(**DR 42**, and it is on **195.20.19.178** — the Moldova shortener cluster, not the seller block).
**Two of the 28 Section-2 entries do not meet the stated criterion.**

### 2.10 🟠 Disavow entry count: `toxic-domain-inventory.md` says 34 (5 + 29); the file has 33 (5 + 28)
`FINAL-AUDIT.md` (33) and the file agree; the inventory is one entry ahead of the delivered file in
both the Section-2 count and the total. Its §7 "**34** `domain:` entries" is wrong.

### 2.11 🟠 "Anchor-verified coverage: 73 of 1,232 (5.9%)"
Two of the 73 (`urlbacklinkschecker.space`, `backlinkcheckerseo.space`) are not among the 1,232, so
the ratio mixes populations: it is **71 / 1,232 = 5.8%**. Superseded anyway by §2.4 — true
anchor-verified coverage from `links_raw.tsv` is **818 registrable domains / 1,232 = 66.4%**.

### 2.12 🟠 Minor cluster error: 3.33.251.168 is 3 domains / 15 links, not 7 / 17
From `refdomains.csv`. The other two shell-hosting IPs are correct (15.197.225.128 → 5 / 26;
15.197.142.173 → 5 / 13). The shell-hosting claim as a whole still holds — all 14 shells are DR 0,
all 14 are present in `refdomains.csv`, and all 14 sit at Authority Score 2 — but only **13** of the
14 sit on the three named IPs. **`choiceviewwindows.com` is on `3.33.152.147`, a fourth AWS Global
Accelerator address no document names.** "They cluster on three shared IPs" should read four.

---

## 3. Claims UNVERIFIABLE from the available data

| Claim | Why it cannot be checked |
|---|---|
| **Total backlinks 7,444 / 7,449 / 7,547**; follow-nofollow 5,624/1,896; text/image 6,819/186 | These are Semrush `backlinks_overview` aggregates. No overview export exists in the repo or in git history. The only internally derivable total is the `links` column sum, **7,547**. Note that §6.1 uses 7,444 as its denominator for percentages while the enumerated file sums to 7,547 — a 1.4% denominator inconsistency running through every percentage in §6.2/§6.3. |
| **"~94% of spam reaches the client via 301 redirects"** | Rests entirely on Semrush's `redirect_url` column, which is in no preserved file. The 4,815/283 split is reproducible as *arithmetic over anchor buckets* (§2.5) but the premise that shell-naming anchors imply shell-targeting links is not independently testable here. The documents are candid that outbound HTTP and WHOIS were blocked. |
| **Registrant identity of the 14 shells; whether the client controls them** | Correctly flagged as unknown. Unchanged. |
| **Sample B's DR-extrapolation chain (§6A.3: 206 domains sampled → ~721 DR 0–5 → ~84%)** | The per-bucket DR sample (which 206 domains, which DR values) was never preserved. The chain cannot be re-derived. Given §2.3, it should not be relied on in any case: it extrapolates from a population that is 76% sample A. |
| **The 1,108-link single-referring-domain anchor tail (14.9% of the profile), "classified by pattern inspection, ±3pp"** | The 416 single-domain anchors were never exported; only the 87 multi-domain anchors survive. Every "estimated" row of §6.2/§6.3 — editorial context ~378, generic ~370, machine-translated ~95, partial-match ~92, exact-match ~75 — is unverifiable. Treat the §6.3 "clean profile" table as indicative only. |
| **Traffic figures, keyword counts, competitor AS 0–5 shares, Semrush Rank movement** | All from Semrush Domain Overview / Organic Research. No export preserved; API returns `ERROR 132 :: API UNITS BALANCE IS ZERO`. The −87.7% collapse / +45% recovery narrative and the entire competitive benchmark table are single-sourced and unchecked. |
| **"284 of 360 Network-A-styled domains first appeared in the 14 days to 6 Oct"** | `first_seen` is present in `refdomains.csv` and the max value does confirm 2026-10-06 15:01:41, but the "360 Network-A-styled" set is never enumerated, so the 284 cannot be reproduced against a defined population. (The comparable figure I *can* produce: 501 domains serving `/dir/` paths — see §2.4.) |
| **Why ~143 links vanished from the sample-A input** | Confirmed to have happened (§2.3a); mechanism unknown. No semicolon, quote, newline or pipe characters appear in block A's anchors. |

---

## 4. Corrected numbers table — use these downstream

| # | Quantity | **Corrected figure** | Basis | Replaces |
|---|---|---|---|---|
| 1 | Referring domains (enumerated) | **1,232** | refdomains.csv, unique | 1,225 / 1,227 |
| 2 | Total links, enumerated-file basis | **7,547** | `links` column sum | use consistently; do not mix with 7,444 |
| 3 | AS 0–5 domains | **1,015 (82.4% of 1,232)** | ascore ≤ 5 | 1,011 |
| 4 | AS 0–5 backlinks | **6,078** | ascore ≤ 5 | — |
| 5 | Domains at AS exactly 2 | **888** | histogram | 886 (line withdrawn anyway) |
| 6 | Sample A — AS 0–5 domains observed | **620 (61% of band)** | block A, 1,000 links | 485 / 48% |
| 7 | Sample A — vendor-copy share | **87.4%** | 542 / 620 | 84.3% |
| 8 | Sample A ∩ Sample B | **sample A ⊂ sample B**; 76% of B's domains come from A | dedupe analysis | "two independent samples" |
| 9 | **Independent increment — vendor share** | **47.0%** (87 / 185 domains) | block-B-only AS 0–5 domains | the ~84% corroboration |
| 10 | **AS 0–5 vendor share, band-wide** | **~66%, bounded 62–83%** | 629 observed + 47% of 210 unobserved | "~84% / five in six" |
| 11 | AS 0–5 domains with any anchor observation | **805 (79.3%)** | links_raw.tsv | "70 of 1,015 / 93% no data" |
| 12 | **AS 0–5 domains individually evidenced (vendor copy + dofollow)** | **617 (60.8%)** | links_raw.tsv, criterion 1 | **64 / 6.3%** |
| 13 | Anchor-verified coverage of the profile | **818 / 1,232 = 66.4%** | links_raw.tsv registrable domains | 73 / 1,232 = 5.9% |
| 14 | Network A `/dir/` domains evidenced | **501 (499 in refdomains, 498 AS 0–5)** | links_raw.tsv URL paths | 59 evidenced / ~360 "likely" |
| 15 | Vendor-copy links, dofollow rate | **98.6%** (1,320 / 1,339) | 2,532 unique links | 98% ✅ |
| 16 | Bare shell-anchor links, dofollow rate | **52.1%** (391 / 751) | 2,532 unique links | 52% ✅ |
| 17 | Vendor sales-copy links | **2,321 (31.2% of 7,444)** | anchors_multi.csv | 2,286 |
| 18 | Bare shell-domain anchor links | **2,757 (37.0%)** | anchors_multi.csv | 2,579 |
| 19 | **Total spam links** | **5,078 measured (~5,098 incl. est. tail), 68.2%** | anchors_multi.csv | 4,894 / 66% |
| 20 | **Hostile dofollow core** | **~2,289 links** | 2,321 × 98.6% | 2,286 (close, but derived wrongly) |
| 21 | Redirect-borne / direct | **4,815 / ~283** | anchors_multi.csv | ✅ confirmed |
| 22 | Cloudflare-fronted domains | **866 (70.3%)** | full CF IPv4 list | 861 (69.9%) |
| 23 | Domains with usable country data | **372 (30.2%)** — 860 are null, all Cloudflare | refdomains.csv | never stated |
| 24 | Singapore | **69 domains / 2,107 links**; **18.5% of geo-known domains**, 27.9% of all links | country column | 70 / 2,133 / 29% |
| 25 | Cluster 118.139.181.85 | **29 domains / 727 links** | ✅ | ✅ |
| 26 | Cluster 203.161.54.114 | **27 domains / 186 links**; **25** at DR 59–60, +factmags DR 75, +goooogla DR 29 | ✅ count / ❌ "all 27" | "27 sellers all DR 59–60" |
| 27 | Cluster 195.20.19.178 | **19 domains / 263 links**, DR 36–54 (mean ~41) | ✅ | ✅ |
| 28 | Cluster 3.33.251.168 | **3 domains / 15 links** | refdomains.csv | 7 / 17 |
| 28b | Shell-hosting IPs | **four**: 15.197.225.128 (5), 15.197.142.173 (5), 3.33.251.168 (3), **3.33.152.147 (1)** | refdomains.csv | "three shared IPs" |
| 29 | Disavow file size | **33 entries (5 + 28)** | file | 34 (5 + 29) |
| 30 | Section-2 entries meeting the stated criterion | **26 of 28** (`backlinks-checker.com` DR 42 on the MD cluster; `goooogla.com` DR 29) | DR endpoint + IP column | implied 28/28 |
| 31 | 14 redirect shells, DR | **all 0.0** | DR endpoint ✅ | ✅ |
| 32 | 15 PROTECTED domains, DR | **all verified correct** | DR endpoint ✅ | ✅ |
| 33 | ngwindows.com DR | **27.0** | DR endpoint ✅ | ✅ |

### The three corrections that change a decision, not just a digit

1. **№12 — the evidence base was ~10× larger than the audit believed.** The disavow file was
   capped at 33 lines on the explicit grounds that only 64 domains could be individually
   evidenced. 617 can. The scoping decision must be re-taken.
2. **№9/10 — "five in six low-authority domains are vendor spam" is not supported.** It is ~two in
   three, and the apparent corroboration between the two samples was a recency-sorted sample
   counted twice.
3. **№23/24 — the geographic risk signal is an artifact of missing data.** Country is null for 70%
   of the profile, and every null is Cloudflare. "29% of links from Singapore" cannot be stated as
   a share of the profile.
