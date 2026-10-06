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
2. **The infrastructure is one operator's; the attribution is not settled.** All 14 shells share
   the identical GoDaddy nameserver pair (`ns23`/`ns24.domaincontrol.com`) across both IP groups
   and both registration waves, on GoDaddy Domain Forwarding — a feature only the registrant can
   configure. A control domain at the same registrar gets a different pair, so this is **one
   registrar account (~92%)**. **But who holds that account is unknown:** client-commissioned ~45%,
   an SEO vendor or lead-gen partner the client cannot control ~30%, negative SEO via
   attacker-owned 301s ~15%, domain monetiser ~10%. Property-side ≈75%, **not 85%** — and only
   the ~45% branch supports deleting anything.
3. **The spam did not cause the client's traffic collapse.** Organic traffic fell **−87.7%**
   (40,569/mo Aug 2024 → 4,971/mo Sep 2026), and the collapse ran **Jun 2025 → May 2026** — the
   first PBN link is dated **29 Jun 2026**, twelve months later. Since the blast began, traffic is
   **+45%**.
4. **Links are not the competitive bottleneck.** ngwindows.com already holds more quality
   referring domains than its local rivals and gets the same traffic as Window World Atlanta from
   75% more referring domains.

**The highest-value action is a question, not a change.** Ask the client **who owns the GoDaddy
account holding all 14 domains.** It takes minutes and resolves every branch above.

**Do not delete the redirects as a first step.** Two reasons. First, the claim that the spam
*targets the shells* rests on **anchor text alone** — the committed export has no `target_url`
column, and vendor anchors interpolate whichever domain the campaign was ordered under. If the
links point at ngwindows.com directly, deleting the redirects severs **zero** toxic links and is
pure downside. Second, 5 of the 14 are brand variants for a company trading since 2003 with live
legacy citations (Houzz, BBB, GuildQuality, Therma-Tru dealer directory); deleting them breaks
real referral paths and is hard to reverse.

**The cheapest decisive test — 30 seconds, no API units, needs only an unrestricted machine:**
fetch a spam source page and read the `href`.
`curl -sL https://urlbacklinkschecker.space/dir/seo-ranking-links-170322 | grep -o 'href="[^"]*windows[^"]*"'`
If it returns `qualitypluswindows.com`, the redirect model is confirmed. If it returns
`ngwindows.com`, **this entire finding collapses.**

---

## 2. Profile metrics

| Metric | Value |
|---|---|
| Semrush Authority Score | 30 |
| Ahrefs Domain Rating | 27 |
| Total backlinks | 7,444–7,547 (drifts daily; blast is live) |
| Referring domains | **1,232** (full enumeration; 1,225 / 1,227 elsewhere are same-metric counter reads on other days) |
| Follow / nofollow | 5,624 / 1,896 |
| Text / image links | 6,819 / 186 |
| Topical categories | Doors & Windows, Home Improvement, Construction — correctly classified |

**Two metrics from the earlier draft are withdrawn:**

- **Subnet clustering as stated is not evidence.** The "1,141 IPs across 428 class-C subnets" line
  was measuring **Cloudflare's address allocation** — 861 of 1,232 referring domains (**69.9%**)
  are Cloudflare-fronted, and the subnets they span are CDN artifacts. Struck.
  **Three real host clusters do exist** and are the version to cite: `118.139.181.85`
  (29 domains / 727 links, Singapore stats farms — note a **fourth** shell IP, `3.33.152.147`,
  hosts `choiceviewwindows.com` and is named in no earlier document), `203.161.54.114` (27 domains, a link-seller
  block — **note: the "uniform DR 59–60" fingerprint is false**; 25 of 27 measure 59–60,
  `factmags.com` is 75 and `goooogla.com` is 29), `195.20.19.178` (19 domains, Moldova shorteners).
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

**Both of the earlier readings of this band were wrong, in opposite directions.**

An earlier draft reported "two independent samples agreeing at ~84%". **They were not
independent** — sample A is a strict *subset* of sample B, supplying 620 of its 805 AS 0–5
domains. Agreement between a set and its own superset is not corroboration. Sample A's own figure
also fails to reproduce: re-running its script gives **87.4%**, not 84.3%, because its input was
missing ~143 links.

Restricting to the **185 AS 0–5 domains observed only in the second block** — the genuinely new
observations — vendor share is **47.0%**.

| Measurement | Finding |
|---|---|
| Sample A (re-derived; subset of B) | 87.4% vendor |
| New observations only (185 domains) | **47.0%** vendor |
| **Defensible band-wide estimate** | **~66%, bounded 62–83%** |

**"Five in six low-authority domains are spam" must not be used.** The defensible claim is roughly
two-thirds, with a wide interval.

**And the opposite error was larger.** The disavow file was capped at 5 entries on the explicit
grounds that only "6.3% (64 of 1,015)" could be individually evidenced. **That premise is false.**
`links_raw.tsv` — already in this repo's git history — individually evidences **617 AS 0–5 domains
(60.8% of the band)** by the audit's own criterion 1. A **9.6× understatement**. Network A is
**501 `/dir/` domains**, not "59 evidenced + 360 likely".

The scoping decision therefore needs re-taking on the real evidence. (The separate argument — that
redirect-borne links should be fixed at the redirect rather than disavowed — still stands, and is
why the file was not simply expanded to ~620 lines.)

**The most reliable table in the entire document set** is the follow/nofollow split, which
re-derived to the unit: vendor spam **1,320 dofollow / 19 nofollow = 98.6%**; bare sister-domain
cluster **391 / 360 = 52.1%**. Two genuinely different populations.

**The finding that matters most: neither test is safe alone.**

- **High-authority spam that a benign-anchor rule lets through** — commercial link sellers using a
  plain bare `ngwindows.com` anchor: `allbaclinks.com` (DR 60), `atozbacklinks.com` (60),
  `bestsitesbacklinks.com` (60), `friendlybacklinksbuy.com` (60), `99backlinksbuy.com` (59),
  `best-seo-domains.com` (59). An authority rule also lets them through — they're DR 59–60.
  **However**, verification showed every one of these links to this client is `rel=nofollow`, so
  none of them was disavowable in the first place (see §4).
- **Legitimate sites an authority sweep would destroy** — `forsythcounty.com` (DR 3.6),
  `georgiashutters.com` (2.2), `1stcallglasscare.com` (3), `alpharettatoprated.com` (10),
  `lombardohomegroup.com` (13), `windowdigest.com` (15), `homerenoworld.com` (16),
  `athomepros.com` (18), `koalatyremodel.com` (27).

**Authority is anti-correlated with manipulation in this profile.** Any DR or AS threshold would
produce false positives one way and miss DR 65+ vendors the other.

**The delivered disavow file now contains 5 domains.** It briefly held 33; the other 28 have been
**withdrawn in full** after verification against data that was already in the repo.

The withdrawal matters because it exposes a process failure, not just a bad call. The earlier pass
reported anchor evidence for only "73 of 1,232 domains (5.9%)" and sized everything to that
scarcity. The committed export actually holds **3,499 link rows covering 878 domains (71.3%)**.
Against the real data:

- **14 of the 28 have zero link rows to this client at all.**
- **The other 14 are 100% `rel=nofollow`** — excluded by the file's own stated criterion.
- The **"uniform DR 59–60 block" fingerprint is false** (25 of 27; `factmags.com` 75,
  `goooogla.com` 29).
- `goooogla.com` had been admitted under a **co-hosting criterion this file's own evidence
  standard forbids**. Shared hosting turned out to have *negative* predictive value here: it
  selected exclusively for nofollow links. Criterion struck.

**A separate pass identifies ~87 further domains that do meet criterion 1** (dofollow + vendor
sales-copy anchor naming ngwindows.com + shared slug). They are **not added yet**: routing is
inferred from anchor text, for the same missing-`target_url` reason as §1. Confirm that field
after 2026-10-25, then extend. The honest range for a final file is **5 to ~92 entries**, and
which end depends on one unread HTML attribute.

**1,159 domains are excluded by design** as insufficient evidence — including 360 carrying Network
A's naming convention, 284 of which first appeared in the 14 days to 6 Oct. Likely the same
network; likely is not evidence, so they are out.

Removed as false positives: `csswinner.com` (DR 75) and `eurekster.com` (DR 53). `factmags.com`
is also out, but the earlier stated reason here was wrong: there was no DR conflict — it measures
**DR 75** and no pass ever said 60. It is excluded because **all 76 of its links are nofollow**.

**Anchor-verified coverage: 73 of 1,232 referring domains (5.9%). 94.1% is unverified.**

---

## 5. Business impact — the spam is not the client's problem

| Period | Organic traffic | Note |
|---|---|---|
| Aug 2024 | **40,569** | peak |
| Jun 2025 → May 2026 | 24,194 → 4,360 | **−82% collapse** |
| **Jun 2026** | **3,420** | trough — *blast begins* |
| Sep 2026 | **4,971** | **+45% since the blast started** |

**Both reassurances in that table failed verification and are withdrawn.**

- **The exoneration does not hold.** "First spam link 29 Jun 2026" quoted the later of two dates
  in the audit's own anchor table. The bare sister-domain cluster is **2,579 links dated Jul 2025
  onward** — ~3× larger, and landing in the exact break month. Vendor-named domains
  (`backlinksolutions.info`, `rankvanceseo.info`) appear Jul–Sep 2025, and AS 0–5 inflow ramps
  from Oct 2025. `refdomains.csv` is also a **live-links snapshot** — removed links are absent —
  so it cannot date a "first" link in either direction.
- **"+45% since the blast" is seasonality.** Indexing Jun→Aug at Jun=100: **2024 = 147,
  2026 = 150**. Same company, same summer lift, two independent years. It is already rolling over
  (Aug 5,139 → Sep 4,971). Strike it from any client summary.

**The best-dated explanation is one nobody had considered: Google core and spam updates.** Every
step-down month lands in or just after a confirmed update — March 2025 core → Apr −41%;
**June 2025 core (30 Jun – 17 Jul), which literally spans the −36.5% break**; Aug 2025 spam;
Dec 2025 core; Mar 2026 spam+core; **May 2026 core (21 May – 2 Jun) → the Jun 2026 trough**.
Ranked primary at **60–65%**.

**The AI Overview hypothesis is demoted to a contributing factor (~40%, not primary).** Its stated
timing evidence was backwards: AIO launched to all US users **13–14 May 2024, three months before
this site's all-time peak**. And 907 keywords / 225 visits is ordinary long-tail distribution, not
an anomaly.

**Untested, not excluded:** a 2025 site migration, redesign or technical break. Both the live site
and archive.org were proxy-blocked here. **Diffing May vs August 2025 Wayback snapshots is the
highest-priority outstanding check** and takes ten minutes on an unrestricted browser.

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

**Caveat the earlier draft omitted:** this is not like-for-like. Window World Atlanta is a
franchisee of `windowworld.com` (**DR 61**) and inherits national brand demand. The comparison is
also taken at the moment a falling line crosses a flat one — at peak, ngwindows beat WWA ~8.5:1 on
traffic with a similar link profile, which is itself evidence its traffic was never link-driven.
The "links are not the bottleneck" reading is still the most likely, but it was the most
reassuring of three available readings and was adopted without testing the others.

**The gap is commercial, not authority:** homepage + GBP = 60.6%
of organic traffic, almost all branded; `/windows` doesn't crack the top 20 pages; and
**`window replacement atlanta` (720/mo, $41.02 CPC) sits at position 15** — the page-two band where
targeted links do pay.

---

## 6. Action plan, in priority order

**1. Read one `href`, and ask one question. Neither changes anything, and together they decide
everything else.**
- **The href test** (30 seconds, unrestricted machine):
  `curl -sL https://urlbacklinkschecker.space/dir/seo-ranking-links-170322 | grep -o 'href="[^"]*windows[^"]*"'`
  Returns a shell domain → the redirect model holds. Returns `ngwindows.com` → the model collapses
  and the ~87 candidate domains all become directly disavowable.
- **The ownership question:** who holds the GoDaddy account for the 14 domains? All share
  nameservers `ns23`/`ns24.domaincontrol.com`, so it is one account.
- Only if **both** come back "client-controlled shells" should deleting the redirects be
  considered — and then preserve DNS/WHOIS/Semrush snapshots first, and park the 5 brand variants
  on a holding page rather than letting them lapse and be re-registered. **Deleting them is not
  the default and must not be done on the current evidence.**

**2. Check Google Search Console for a manual action.** Free, 90 seconds, and it determines
whether a disavow is warranted at all. Google's current guidance limits the tool to manual actions
and links you are responsible for.

**3. Disavow — only if step 2 shows a manual action, or step 1 confirms links were bought.**
Scope: the **~283 links hitting ngwindows.com directly**. Everything redirect-borne is resolved by
step 1 and must not be disavowed. Use the 33-domain evidenced file as-is — or its 5-line Section 1
alone if you want only fully-evidenced entries; extend it after
**25 Oct 2026** per the procedure documented in the file header.

**4. Lost links — one is real, one was a false alarm.**
- **`atlantahomeimprovement.com` is NOT lost.** It has **90 links** and the **highest `last_seen`
  value in the entire 1,232-domain file** — seen on the final day of the crawl. It is the client's
  strongest referring domain by link count. Emailing to "reclaim" it would have been embarrassing.
- **`gnpmilton.com` is genuinely lost** (last seen 2026-05-06 while 1,200 other domains kept being
  seen) — but it is **DR 26, 2 links**, on a podcast network that runs a paid "Book Your Interview"
  model. The original placement was likely bought, so reclaiming it means paying again. Worth
  doing, not worth leading with.

**5. Fix the zero-Georgia-chamber problem — confirmed true, and worse than first stated.** There
is no Georgia chamber anywhere in the profile; the only chamber link is Williamson County,
**Tennessee**, ~250 miles away. There are also **no Georgia municipal or county government links
at all** (`alpharetta.ga.us` DR 68, `roswellgov.com` 70, `johnscreekga.gov` 69,
`cityofmiltonga.us` 44 — all absent).

**Verified targets, reordered by value-per-effort:**
1. **`businessradiox.com`** (DR 71) — North Fulton studio physically in Alpharetta, confirmed
   **"no pay to play"**. Best ratio available.
2. **`gachamber.com`** (DR 62) — the *real* Georgia Chamber. An earlier draft excluded it after
   measuring `georgiachamber.com` / `gachamber.org`, which are different domains.
3. **`nariatlanta.org`** (DR 39) — real NARI Atlanta chapter, open membership, transparent $760.
4. **`tribuneledgernews.com`** (DR 60) and **`forsythnews.com`** (61) — local press.
5. **Warm reclaims:** `qualifiedremodeler.com` (71) and `wsbtv.com` (81) have **already published
   about this client** but neither appears in the referring-domain file.

**Struck from the earlier plan:** `guildquality.com` — **already held** (8,670 survey responses,
Guildmaster Awards; absent from the file only because the profile link is nofollow, so audit the
attribute rather than chase the link). `marvin.com` — **unobtainable**; Marvin runs separate
networks and replacement contractors sit on `infinitywindows.com`, where this client is already
Infinity's exclusive Georgia contractor. `gnfcc.com` dues are unpublished — **phone before
committing**.

**Two things nobody had flagged:** the company has **rebranded to "NG Windows"**, so outreach and
citation cleanup must cover both trading names or listings will fragment. And **Yelp and Houzz are
absent from the referring-domain file but have live profiles** — they are nofollow, so reporting
them as missing citations would be wrong.

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
signal: movement in the AS ≥30 referring-domain count (currently 65). **Note:** an earlier draft
set "Trust Score above Authority Score" as the healing KPI. That was retracted in review — the two
being equal is the norm, not a defect — and it should not appear in any client-facing plan.
Escalation
trigger: **if branded queries start sliding, that is site-level demotion** and the posture changes.
If referring domains keep climbing *after* the redirects are cut, the spam is direct and ongoing —
revisit the negative-SEO hypothesis.
