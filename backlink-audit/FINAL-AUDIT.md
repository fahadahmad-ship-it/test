# Backlink Audit — ngwindows.com — FINAL

**Client:** ngwindows.com (North Georgia Replacement Windows), Atlanta / North Georgia metro
**Audit date:** 6 October 2026
**Status:** This document supersedes `ngwindows-backlink-audit.md`, which contains errors
corrected here. Read this one.

---

## Data sources and their limits — read before quoting any number

| Source | Status |
|---|---|
| Semrush Backlink Analytics | Used. **Unit balance hit zero mid-audit.** |
| Ahrefs Site Explorer | **Never available.** Workspace allowance exhausted on arrival; resets **25 Oct 2026**. |
| Ahrefs free DR endpoint | Used throughout at zero cost. |

**What this cost us.** Referring-domain enumeration is complete (1,232 domains). **Anchor-level
evidence is not**: the unit balance ran out after one 76-link page from the toxicity pass, and a
parallel pass covering 2,532 links / 878 domains (72%). No Ahrefs cross-check was possible at all,
and the two tools' crawlers find different links. Every figure below is Semrush-derived and
single-sourced.

**The practical consequence:** the disavow file is sized to what can be *individually evidenced*,
not to the probable size of the network. Those are different numbers and the gap is stated
explicitly in §4.

---

## 1. Executive summary

There is a real, large, ongoing link-spam campaign pointed at this property. But four findings
reverse the obvious reading of it:

1. **~94% of the spam does not point at ngwindows.com at all.** It points at **14 content-free
   301 redirect shells** that funnel into ngwindows.com. Semrush follows the redirect and credits
   the client. The "competitor domain names" in the anchor text are not anchors naming rivals —
   **they are the actual link targets.**
2. **This is therefore almost certainly a purchased campaign, not a negative SEO attack**
   (~85% confidence). The shells have per-target vendor campaign IDs, no content, no history, and
   climbed in lockstep from Nov 2024. **Registrant identity is unverified** — the proxy blocked
   WHOIS.
3. **The spam did not cause the client's traffic collapse.** Organic traffic fell **−87.7%**
   (40,569/mo Aug 2024 → 4,971/mo Sep 2026), and the collapse ran **Jun 2025 → May 2026** — the
   first PBN link is dated **29 Jun 2026**, twelve months later. Since the blast began, traffic is
   **+45%**.
4. **Links are not the competitive bottleneck.** ngwindows.com already holds more quality
   referring domains than its local rivals and gets the same traffic as Window World Atlanta from
   75% more referring domains.

**The single highest-value action is not a disavow.** It is deleting 14 redirect records, which
severs ~4,815 toxic links at source with no Google process involved — *if the client controls
those domains*. That question is unanswered and gates everything.

---

## 2. Profile metrics

| Metric | Value |
|---|---|
| Semrush Authority Score | 30 |
| Ahrefs Domain Rating | 27 |
| Total backlinks | 7,444–7,547 (drifts daily; blast is live) |
| Referring domains | **1,232** (full enumeration) |
| Follow / nofollow | 5,624 / 1,896 |
| Text / image links | 6,819 / 186 |
| Topical categories | Doors & Windows, Home Improvement, Construction — correctly classified |

**Two metrics from the earlier draft are withdrawn:**

- **Subnet clustering as stated is not evidence.** The "1,141 IPs across 428 class-C subnets" line
  was measuring **Cloudflare's address allocation** — 861 of 1,232 referring domains (**69.9%**)
  are Cloudflare-fronted, and the subnets they span are CDN artifacts. Struck.
  **Three real host clusters do exist** and are the version to cite: `118.139.181.85`
  (29 domains / 727 links, Singapore stats farms), `203.161.54.114` (27 domains, the DR 59–60
  link-seller block), `195.20.19.178` (19 domains, Moldova shortener network).
- **"886 domains at Authority Score 2" is withdrawn.** It is a rounding artifact of an integer
  score on a log scale; Ahrefs returns continuous DR 0.0–2.0 across the same band.

Replaced by a fingerprint that actually holds: **Network A sites share identical URL path slugs
with identical numeric IDs across 40+ registrable domains** (`/dir/seo-ranking-links-170322`,
`/dir/backlink-seo-experts-211287`). Same page, different domain. Not defeasible by binning.

---

## 3. What the spam is, and how it reaches the client

**The redirect mechanism.** Semrush's `redirect_url` column shows the spam pages' actual `href`:

| Spam page | Credited to | Real `href` |
|---|---|---|
| `seoanalysischecker.website/dir/backlink-seo-experts-211287` | ngwindows.com | **`thermalprowindows.com`** |
| `backlinkautomationtool.store/dir/authority-focused-backlinks-178285` | ngwindows.com | **`roiwindows.com`** |

All 14 shells return **301, zero internal links, zero external links, no title, no content**. The
vendor assigns a campaign ID per target; ngwindows.com has its own (`-148096`), added **Jun 2026**
— matching the escalation date exactly.

**The 14 shells:** ngawindows.com · roiwindows.com · thermalprowindows.com · qualitypluswindows.com ·
northpointwindows.com · performingwindows.com · thermatrustwindows.com · northgeorgiawindows.net ·
thermalastwindows.com · e2windows.com · choiceviewwindows.com · ngwindow.com · northgawindows.com ·
northgeorgiawindow.com

They cluster on **three shared IPs** (15.197.225.128, 15.197.142.173, 3.33.251.168) and several are
near-exact brand variants of the client. All are **Ahrefs DR 0**.

**Where the links land:** ~100% on the **homepage**, much of it on `http://`/non-`www` variants that
301 again. Every service page, service-area page and blog post is clean. This materially lowers
severity — the money pages were never touched.

**Anchor character:** the vendor spam is **98% dofollow**, with literal sales copy —
*"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service … Buy Backlinks Online
Cheap"* — and anchors containing Telegram link-selling handles (`t.me/s/darksidelinks`,
`t.me/s/quarterlinks25`).

---

## 4. Low-authority domains: what the evidence actually supports

**Operative rule, applied throughout: no link is disavowed for being low authority. Ever.**
The grounds must be cited anchor text plus dofollow status, or link-selling domain character.

Three measurements of the AS 0–5 band, which must not be conflated:

| Measurement | Finding | Basis |
|---|---|---|
| Independent sample A | 84.3% vendor sales copy, 15.7% benign | 485 domains, 1,000 links |
| Independent sample B | ~84% vendor sales copy, 98% dofollow | 878 domains, 2,532 links |
| **Individually evidenced** | **6.3%** (64 of 1,015 domains) | 73 domains, 76 links |

The first two agree closely and are the honest *estimate*: roughly five in six low-authority
referring domains carry vendor sales copy. **But only 6.3% can be documented domain-by-domain**,
because the API ran dry. Those are different claims and the disavow file is built to the second,
stricter one.

**The finding that matters most: neither test is safe alone.**

- **High-authority spam that a benign-anchor rule lets through** — commercial link sellers using a
  plain bare `ngwindows.com` anchor: `allbaclinks.com` (DR 60), `atozbacklinks.com` (60),
  `bestsitesbacklinks.com` (60), `friendlybacklinksbuy.com` (60), `99backlinksbuy.com` (59),
  `best-seo-domains.com` (59). An authority rule also lets them through — they're DR 59–60.
  `factmags.com` (DR 75) is co-hosted with 27 domains literally named `buyfairbacklinks.com`,
  `clicktobuybacklinks.com`.
- **Legitimate sites an authority sweep would destroy** — `forsythcounty.com` (DR 3.6),
  `georgiashutters.com` (2.2), `1stcallglasscare.com` (3), `alpharettatoprated.com` (10),
  `lombardohomegroup.com` (13), `windowdigest.com` (15), `homerenoworld.com` (16),
  `athomepros.com` (18), `koalatyremodel.com` (27).

**Authority is anti-correlated with manipulation in this profile.** Any DR or AS threshold would
produce false positives one way and miss DR 65+ vendors the other.

**The delivered disavow file contains 33 domains**, and they are not of equal strength:

| | Entries | Grounds | Strength |
|---|---|---|---|
| **Section 1 — criterion 1** | **5** | Vendor anchor **observed** + dofollow **observed** + shared slug, **and points at ngwindows.com directly** | Fully evidenced |
| Section 2 — criterion 3 | 28 | Link-selling domain name + shared host `203.161.54.114` + uniform DR 59–60 | Anchors and routing **unverified** |

**For a strictly defensible submission, Section 2 can be dropped, leaving 5 lines.** That is
flagged in the file itself. The uniform DR 59–60 across 27 co-hosted sellers is itself an
authority-inflation signature, which is why name character was admitted as a criterion at all.

**1,159 domains are excluded by design** as insufficient evidence — including 360 carrying Network
A's naming convention, 284 of which first appeared in the 14 days to 6 Oct. Likely the same
network; likely is not evidence, so they are out.

Removed as false positives: `csswinner.com` (DR 75), `eurekster.com` (DR 53), and `factmags.com`
(grounds were co-hosting rather than its own anchor, and two passes disagree on its authority —
DR 60 vs DR 75; conflicting evidence excludes by default).

**Anchor-verified coverage: 73 of 1,232 referring domains (5.9%). 94.1% is unverified.**

---

## 5. Business impact — the spam is not the client's problem

| Period | Organic traffic | Note |
|---|---|---|
| Aug 2024 | **40,569** | peak |
| Jun 2025 → May 2026 | 24,194 → 4,360 | **−82% collapse** |
| **Jun 2026** | **3,420** | trough — *blast begins* |
| Sep 2026 | **4,971** | **+45% since the blast started** |

The decline **pre-dates the spam by twelve months**. Keywords are flat; Semrush Rank improved
23.5%. The Sep/Oct escalation is too recent to have been scored, so remediation is justified as
**preventive risk management, not emergency triage**.

**Likely actual cause (hypothesis, needs GSC confirmation):** AI Overviews absorbing informational
blog traffic. `/blog/standard-door-sizes` holds **907 ranking keywords and earns 225 visits**. The
informational cluster is 22% of traffic and consists of queries like "how tall is an average door".
Timing matches the AI Overview rollout, not any link event. **Verify with GSC impressions vs clicks.**

**Competitive benchmark — the 82% junk ratio is the niche norm, not an anomaly:**

| | ngwindows | WindowWorld ATL | Davis |
|---|---|---|---|
| AS 0–5 share | 82.4% | 74.9% | 80.4% |
| **AS ≥30 domains** | **65** | **34** | **51** |
| Organic traffic | 4,971 | 4,758 | 2,932 |

ngwindows leads its peer group on quality links and gets the same traffic as Window World Atlanta
from 75% more referring domains. **The gap is commercial, not authority:** homepage + GBP = 60.6%
of organic traffic, almost all branded; `/windows` doesn't crack the top 20 pages; and
**`window replacement atlanta` (720/mo, $41.02 CPC) sits at position 15** — the page-two band where
targeted links do pay.

---

## 6. Action plan, in priority order

**1. Ask the client who controls the 14 redirect domains.** Run WHOIS and compare nameservers
against ngwindows.com. This gates everything and takes five minutes. *(Blocked here — proxy
denied outbound WHOIS/HTTP.)*
- **Client controls them →** delete the 301s. ~4,815 toxic links vanish at source. Preserve
  WHOIS/DNS/Semrush snapshots first. Park the 5 defensive typo-variants on a holding page rather
  than letting them expire and be re-registered.
- **Client does not →** this is an attack; the snapshots become the evidence file and the
  negative-SEO hypothesis returns.

**2. Check Google Search Console for a manual action.** Free, 90 seconds, and it determines
whether a disavow is warranted at all. Google's current guidance limits the tool to manual actions
and links you are responsible for.

**3. Disavow — only if step 2 shows a manual action, or step 1 confirms links were bought.**
Scope: the **~283 links hitting ngwindows.com directly**. Everything redirect-borne is resolved by
step 1 and must not be disavowed. Use the 33-domain evidenced file as-is — or its 5-line Section 1
alone if you want only fully-evidenced entries; extend it after
**25 Oct 2026** per the procedure documented in the file header.

**4. Reclaim two lost links — worth more than the entire disavow exercise.**
- **`gnpmilton.com`** — local podcast, *"Ep 37 North Georgia Replacement Windows with Ted Kirk"*.
  Dofollow, hyperlocal, on-topic. The best editorial link the profile ever had. **Lost.**
- **`atlantahomeimprovement.com`** (DR 45) — local, on-topic, linking since 2023. **Lost.**
Two emails.

**5. Fix the zero-Georgia-chamber problem.** The only chamber citation is Williamson County,
**Tennessee**. Named, competitor-proven targets: `gnfcc.com` (Greater North Fulton Chamber, DR 44 —
covers Alpharetta, Roswell, Milton, Johns Creek exactly), `guildquality.com` (DR 75,
Atlanta-headquartered), `trustdale.com` (DR 62), the **Marvin (DR 76) and Infinity (DR 54) dealer
locators** — the dealership is live but the locator link is unclaimed — and `appenmedia.com`
(DR 61, publishes the Alpharetta-Roswell and Forsyth Heralds).

**6. Put the budget into commercial pages, not link volume.** There is nothing to catch up to
locally. `/windows` and the service-area pages are the gap.

**7. Anchor policy for new links:** push **branded** anchors in the current brand form. Branded
sits at ~5% against naked URLs at ~34%, where a healthy local-service profile runs 40–55% branded.
Exact-match commercial is 3.2% — far below any risk band. **Leave commercial anchors alone for
6+ months.**

---

## 7. What remains unknown

- **Registrant of the 14 redirect domains.** The central question. Unverified.
- **Anchor evidence for 1,159 referring domains** (94% of the profile). API exhausted.
- **No Ahrefs cross-check of any kind.** Resets 25 Oct 2026.
- **Whether the Sep/Oct escalation has cost rankings.** October data does not exist yet.
- **The campaign is still running.** Newest spam link first seen **6 Oct 2026 15:01 UTC** — the
  audit date. Any disavow built today is a snapshot of a moving target.
- **Whether AI Overviews explain the 2025 collapse.** Needs GSC impressions-vs-clicks.

## 8. Monitoring

Re-run after 25 Oct 2026 against both tools and extend the disavow to the union. Key healing
signal: **Trust Score crossing above Authority Score** (currently tied at 30/30). Escalation
trigger: **if branded queries start sliding, that is site-level demotion** and the posture changes.
If referring domains keep climbing *after* the redirects are cut, the spam is direct and ongoing —
revisit the negative-SEO hypothesis.
