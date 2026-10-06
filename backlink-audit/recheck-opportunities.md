# Link-Opportunity Recheck — ngwindows.com

**Date:** 2026-10-06
**Scope:** Independent verification of every named link-building target and both "lost links" in the backlink audit.
**Client:** North Georgia Replacement Windows / **NG Windows** (rebranded — see Note A), 11460 Maxwell Rd, Alpharetta GA 30009. ngwindows.com **DR 27**.

## Method & limits (read this first)

- **DR figures below are real**, pulled today from the free Ahrefs Domain Rating endpoint. Every DR in this document was measured, not copied from the audit.
- **Semrush and Ahrefs Site Explorer were unavailable** (zero units / blocked until 2026-10-25). "Already linking?" is therefore judged against `data/refdomains.csv` (1,232 referring domains, crawl window ending **2026-10-06**) plus live SERP evidence — not a fresh backlink pull.
- **The network egress proxy blocked direct fetches** of gnfcc.com, gnpmilton.com, marvin.com, trustdale.com, guildquality.com, appenmedia.com, buzzsprout.com, podcasts.apple.com and archive.org (403 at CONNECT). Those targets were verified via search-index evidence instead. **Where that left a question genuinely open, it is marked UNVERIFIED below rather than assumed.**
- Note the CSV `ascore` column is **Semrush Authority Score, not Ahrefs DR** — they are different scales. Several discrepancies between this document and the original audit come from that conflation.

---

## 1. Verified target table

### Primary targets

| Target | Claimed DR | **Real DR** | Exists | Already linking? | How to obtain | Difficulty |
|---|---|---|---|---|---|---|
| gnfcc.com | 44 | **44** ✅ | Yes — Greater North Fulton Chamber, 1,200+ members, EIN 58-1157316 | **No** (absent from refdomains.csv) | Paid membership → member directory listing. Covers Alpharetta/Roswell/Milton/Johns Creek as claimed. **Dues not published** — tiered, quote by phone | Low (money, not outreach) |
| guildquality.com | 75 | **75** ✅ | Yes | **Profile already exists — see Note B** | Already a member since ≥2013. Not an acquisition task | N/A — reclassify |
| trustdale.com | 62 | **62** ✅ | Yes, active | **No** | Paid "Certified Partner" — in-person meeting + 7-point vetting + application. Fee partially evidenced at $275 (split); full schedule not public | Medium (vetting gate + cost) |
| marvin.com | 76 | **76** ✅ | Yes | **No — and correctly so. See Note C** | Not realistically claimable | **STRIKE** |
| infinitywindows.com | 54 | **54** ✅ | Yes | **YES — already linking.** `infinitywindows.com/find-a-dealer/a1k0w00000bueuvuaf/...` live; CSV: 1 link, first seen 2026-02-08, last 2026-09-06 | Already held | Redundant |
| appenmedia.com | 61 | **61** ✅ | Yes — Appen Media Group, 319 N Main St Alpharetta. Publishes Alpharetta-Roswell Herald, Forsyth Herald, Johns Creek Herald, **Milton Herald**, Sandy Springs Crier, Dunwoody Crier; 105k homes/wk | **No** | Editorial pitch or sponsored content. Perfect geo overlap | **Low–Medium — best unexploited target in the plan** |

### Secondary targets

| Target | Claimed | **Real DR** | Exists | Already linking? | Assessment |
|---|---|---|---|---|---|
| atlantamagazine.com | 78 | **78** ✅ | Yes | No | Real but editorially hard; no contractor path |
| businessradiox.com | 71 | **71** ✅ | Yes — **North Fulton studio, inside Renasant Bank, Alpharetta** | No | **Explicitly "no pay to play"** — free guest slot. Strong geo + topical fit. **Upgrade this** |
| exploregeorgia.org | 77 | **77** ✅ | Yes | No | **STRIKE — tourism businesses only** (accommodations, F&B, attractions, tours). A window contractor is ineligible for the free listing |
| todayshomeowner.com | 80 | **80** ✅ | Yes | No | Real. National editorial/"best of" roundups; largely paid placement in practice. Low odds, keep as stretch |
| citylifestyle.com | 80 | **80** ✅ | Yes — **both `/alpharetta` and `/johnscreek` editions live** | No | Paid advertorial partnership w/ local publisher. Legit hyperlocal, but it is advertising, label it as such |
| modernluxury.com | 85 | **85** ✅ | Yes | No | Real but no realistic contractor route. Low priority |
| cobbchamber.org | 55 | **55** ✅ | Yes | No | Real — but **Cobb County is outside the client's named service area**. Geo-irrelevant |
| ecohome.net | 62 | **62** ✅ | Yes, active (acquired 2024 by Raiiz Innovations) | No | **Canada-focused** green-building publisher. No Atlanta relevance. Low value |
| cobbemc.com | "AS 41" | **DR 55** | Yes | No | **Claim used the wrong metric.** Serves Cobb/Bartow/Cherokee/Paulding + *small* parts of Fulton — not the Alpharetta/Roswell/Milton/Johns Creek core. Weak fit |

---

## 2. Targets to STRIKE

1. **marvin.com dealer locator** — the claim rests on a misunderstanding. See Note C. Chasing this wastes outreach on something that cannot be granted.
2. **exploregeorgia.org** — eligibility is restricted to tourism businesses. A window installer does not qualify. Unobtainable, not merely hard.
3. **guildquality.com (as an acquisition target)** — already held, and the "held by competitor Window World Atlanta" framing is wrong. See Note B.
4. **infinitywindows.com** — already linking. Redundant recommendation; the audit itself conceded this but still listed it as a target.
5. **cobbchamber.org** and **cobbemc.com** — both real, both outside the stated service area. Paying Cobb County dues to serve North Fulton is poor value.
6. **ecohome.net** — Canadian editorial focus. Geographically and commercially irrelevant.
7. **modernluxury.com / atlantamagazine.com** — real and high-DR, but no identified acquisition path for a contractor. Keep as aspirational PR, not as a link plan line item.

---

## 3. Targets to ADD (analyst missed these — and four were wrongly excluded)

### 3a. The "not viable" exclusions were almost all wrong — they tested the wrong domains

**This is the most serious error in the audit.** Five of the six exclusions were justified by a DR reading taken from a misspelled or non-existent domain. The real organisations are live and respectable:

| Audit excluded | Audit DR | The organisation's **actual** domain | **Real DR** | Verdict |
|---|---|---|---|---|
| `georgiachamber.com` | 0.5 | **`gachamber.com`** — Georgia Chamber of Commerce, founded 1911, largest business advocacy org in GA | **62** | ❌ **Wrongly excluded** |
| `gachamber.org` | 2.8 | same as above (wrong TLD) | **62** | ❌ **Wrongly excluded — duplicate of the same error** |
| `atlantanari.org` | 0 | **`nariatlanta.org`** — NARI Atlanta Chapter, 250+ member cos., Peachtree Corners | **39** | ❌ **Wrongly excluded** |
| `cherokeetribuneledger.com` | 0 | **`tribuneledgernews.com`** — Cherokee Tribune & Ledger-News | **60** | ❌ **Wrongly excluded** |
| `jamesharditepros.com` | 0 | **`jameshardiepros.com`** (note: audit typed "hardite") | **51** | Exclusion stands, but on *relevance* — client does windows/doors, not siding. Reason given was wrong |
| `okna.com` | 4.2 | Okna is a competing window brand | — | **Exclusion correct.** Client is Infinity-by-Marvin **exclusive**; an Okna link is off-brand. Right call, wrong reasoning |

**Two concrete additions fall straight out of this:**

- **`gachamber.com` (DR 62)** — and there is a free route: GNFCC is a **Georgia Chamber Federation Partner**, and Federation local-chamber members with **20 or fewer full-time employees** receive complimentary Georgia Chamber membership. ⚠️ *Caveat: NG Windows installs 10,000+ windows/yr and likely exceeds 20 FTE, so the complimentary route may not apply — confirm headcount before promising this.* Either way, one GNFCC transaction may buy two directory links.
- **`nariatlanta.org` (DR 39)** — Atlanta Chapter of NARI. Membership is open: **$760 application fee, applied as year-one dues ($475 chapter + $285 national)**, requires 1 year trading and Code of Ethics agreement. The client qualifies comfortably. Transparent pricing, directly relevant trade body, member directory.

### 3b. Genuine citation gaps in refdomains.csv

Checked the full 1,232-domain file. What the client **has**: bbb.org (2 links, A+ accredited since 2005), nextdoor.com (3), porch.com (1), yellowpages.com (5), superpages.com (15), dexknows.com (9), expertise.com (2), threebestrated.com (1), chamberofcommerce.com (3).

**Genuinely missing, and competitors will hold them:**

| Gap | DR | Note |
|---|---|---|
| **angi.com** | 90 | Absent. No profile found. Real gap |
| **homeadvisor.com** | 91 | Absent. Real gap |
| **thumbtack.com** | 90 | Absent. Real gap |
| **modernize.com** | 76 | Absent |
| **networx.com** | 76 | Absent |
| **buildzoom.com** | 82 | Absent |

⚠️ **Important nuance the audit would have missed:** **yelp.com (DR 94) and houzz.com (DR 92) are absent from refdomains.csv but the client DOES have live profiles on both** — `yelp.com/biz/ng-windows-alpharetta-3` (172 photos, 17 reviews) and `houzz.com/professionals/.../ng-windows-pfvwus-pf~1669593390` (4.2★). They do not appear as referring domains because **those links are nofollow**. Do not report Yelp/Houzz as missing citations; report them as *present but non-passing*. The same caveat likely applies to Angi/Thumbtack — treat these as **local-pack and conversion assets, not link assets**, and budget effort accordingly.

### 3c. Local media the analyst didn't name (verified live, strong geo fit)

| Target | **DR** | Why |
|---|---|---|
| **tribuneledgernews.com** | **60** | Cherokee Tribune & Ledger-News — the paper the audit wrote off at DR 0 |
| **forsythnews.com** | **61** | Forsyth County News — Forsyth/Cumming is named service area, **not in refdomains.csv** |
| **atlantahomesmag.com** | **71** | Atlanta Homes & Lifestyles — directly on-topic, local, not in CSV |
| **qualifiedremodeler.com** | **71** | Already ran a feature on the client (`/infinity-from-marvin-by-north-georgia-replacement-windows/`) — **relationship exists, link not in CSV. Easy reclaim/ask** |
| **accessnorthga.com** | **53** | North Georgia regional news |
| **wsbtv.com** | **81** | Client's principals have already appeared on WSB-TV discussing the Window Wisdom podcast — **warm relationship, no link in CSV** |
| **nfrc.org** (77) / **energystar.gov** (91) / **dsireusa.org** (83) | high | Energy-efficiency authority/rebate directories — natural fit for a replacement-window specialist. Not in CSV |

---

## 4. Verdict on the two "lost links"

### 4a. `atlantahomeimprovement.com` — **CLAIM IS FALSE. THE LINK IS NOT LOST.**

This is the audit's biggest factual error.

Evidence from `data/refdomains.csv`:

```
atlantahomeimprovement.com;24;90;;104.17.46.19;1684564744;1791266962
```

- `links` = **90**
- `first_seen` = 1684564744 = **2023-05-20** (matches "linking since 2023" ✅)
- `last_seen` = 1791266962 = **2026-10-06** — which is **the maximum last_seen value in the entire file**. The domain was seen on the final day of the crawl window.

A domain cannot be "lost" and simultaneously be the most recently observed referring domain in the dataset. Live corroboration: two active pages were found in the index — the editorial feature `atlantahomeimprovement.com/north-georgia-windows/` and the directory entry `atlantahomeimprovement.com/local-resources/north-georgia-replacement-windows/`.

- **Real DR: 45** — the claimed 45 was correct (the audit's own CSV shows AS 24; again DR ≠ AS).
- **Verdict: STRIKE from the reclamation plan.** This is the client's single strongest and most durable referring domain by link count. Recommending outreach to "reclaim" it would have the client emailing a publisher to ask for a link they already have 90 of — an avoidable credibility hit. **It should be protected, not reclaimed.**

### 4b. `gnpmilton.com` — **LINK LOSS IS REAL AND CORROBORATED. Episode number UNVERIFIED.**

Evidence from `data/refdomains.csv`:

```
gnpmilton.com;11;2;us;34.68.234.4;1741489909;1778080111
```

- `first_seen` = **2025-03-09**, `last_seen` = **2026-05-06** — i.e. last observed **five months before** the crawl window closed, while 1,200 other domains kept being seen. **This is a genuine loss, not a crawl artefact.**

What was independently confirmed:
- `gnpmilton.com` is **Good Neighbor Podcast: Milton & More**, host **Stacey Poehler**, covering Milton / Crabapple / Hickory Flat. Buzzsprout show 2214217. **Site is live** — `/home`, `/blog`, `/about`, `/book-your-interview` all currently indexed.
- The show's episode-page URL pattern is `gnpmilton.com/b/ep-NNN-<slug>` (e.g. a live `EP #143` page), and the catalogue runs to ~248 episodes — so an **Ep 37** is entirely plausible in range.
- Ted Kirk (founder, 2003/2005) and NG Windows are documented Milton-area business figures; the show's format is exactly local-business interviews.

What could **not** be verified (egress proxy blocked gnpmilton.com, Buzzsprout, Apple Podcasts **and archive.org**):
- ❌ That the episode is specifically numbered **37**.
- ❌ That the link was **dofollow**.
- ❌ A Wayback snapshot of the original page.
- A domain-restricted search of gnpmilton.com for Ted Kirk returned the show's generic pages but **no Ted Kirk episode page** — weak-to-moderate corroboration that the episode page itself is gone or de-indexed, consistent with the May 2026 loss date.

- **Real DR: 26** (the audit did not state one; CSV AS is 11). This is a **modest** link, not a high-value one.
- ⚠️ **Material caveat the audit omitted:** the Good Neighbor Podcast network operates a **paid "Book Your Interview"** model. The original placement was most likely **bought, not earned**, and "reclaiming" it probably means **paying again**.
- **Verdict:** loss is real; **value was overstated**. At DR 26, 2 links, on a likely pay-to-feature local podcast, the claim that these two lost links are "worth more than the entire disavow exercise" does not survive contact with the data — especially since the other half of that claim (4a) is simply false. Worth a single friendly email to Stacey Poehler. Not worth a budget line.

---

## 5. Honest top 5, reordered by value-per-effort

| # | Target | DR | Why it ranks here |
|---|---|---|---|
| **1** | **businessradiox.com** — North Fulton studio | **71** | **Free** ("no pay to play", confirmed), studio is physically in Alpharetta, format is built for exactly this guest, contact published (moreinfo@businessradiox.com / 770-369-9199). Highest DR obtainable at zero cost. One email |
| **2** | **appenmedia.com** | **61** | Publishes the Alpharetta-Roswell, Milton, Johns Creek **and** Forsyth Heralds — a 1:1 match with the service area, 105k homes/wk. One relationship, multiple mastheads. Local-newsroom pitch or modest sponsored spend |
| **3** | **gnfcc.com** (+ possible **gachamber.com** DR 62 bundled) | **44** | Fixes the verified zero-Georgia-chamber problem (§6) in one transaction, covers all four core cities, and the Federation Partner route may add a DR 62 link. Cost is money, not effort. **Get the dues quote before committing** |
| **4** | **nariatlanta.org** | **39** | The audit's wrongly-excluded target. Transparent **$760** entry, directly relevant trade body, client clears eligibility easily, member directory link. Predictable and fast |
| **5** | **qualifiedremodeler.com** + **wsbtv.com** (warm-relationship reclaim) | **71 / 81** | Both have **already published about the client** but neither appears in refdomains.csv. Asking an outlet that already covered you to add a link is the cheapest high-DR win available — far better value than the gnpmilton chase |

**Dropped from any top 5:** trustdale.com (real, but paid + in-person vetting gate for DR 62 — fine later, poor value-per-effort now) and both "lost links" (one isn't lost; the other is DR 26 and probably pay-to-feature).

---

## 6. Answers to the specific questions asked

### "ZERO Georgia chamber of commerce links, only link is williamsonchamber.com (Williamson County, TENNESSEE)" — **TRUE, and worse than stated**

Full scan of all 1,232 domains for chamber/association/local-government patterns. Chamber-type domains present:

```
williamsonchamber.com;33;6;us;...;first 2026-08-21;last 2026-10-06
chamberofcommerce.com;48;3;...;first 2026-04-19;last 2026-09-09
```

- ✅ **Confirmed: not a single Georgia chamber of commerce** appears in the file. Not gnfcc.com, not cobbchamber.org, not gwinnettchamber.org, not forsythchamber.org, not johnscreekchamber.com, not cherokeechamber.com, not gachamber.com.
- ✅ **Confirmed: `williamsonchamber.com` is the only true chamber link** — and it is **Williamson County, Tennessee**, ~250 miles outside the service area, acquired 2026-08-21. (`chamberofcommerce.com` is a generic national directory, not a chamber.)
- **Additional finding the audit missed:** there are also **no Georgia municipal or county government links** — no alpharetta.ga.us (DR 68), roswellgov.com (DR 70), cityofmiltonga.us (DR 44) or johnscreekga.gov (DR 69). For a hyperlocal contractor these are the most trust-dense local links available and the gap is total. `forsythcounty.com` (AS 17) is a commercial site, not the county government.
- **The geographic signal problem is sharper than "a gap."** The only chamber link the client holds actively points search engines at **Tennessee**. Recommend acquiring a Georgia chamber link before, or at minimum alongside, any further link work.

### Named targets already in refdomains.csv (recommendation redundant)

- **infinitywindows.com** — 1 link. Already held. ✅ (audit acknowledged this)
- **atlantahomeimprovement.com** — 90 links, live as of 2026-10-06. Already held and **wrongly listed as lost**. ❌
- **gnpmilton.com** — 2 links, genuinely lapsed 2026-05-06. ✅
- All other named targets are confirmed absent from the file.

---

## Notes

**Note A — the client has rebranded.** The company now trades as **"NG Windows"** (formerly North Georgia Replacement Windows); third-party profiles appear under both names, and a `prelaunch.ngwindows.com` subdomain is indexed alongside the live site. Any outreach, citation cleanup or reclamation must handle **both** trading names, or listings will fragment. The audit does not mention this anywhere. Separately, an unrelated franchise competitor, **Wallaby Windows of North Georgia** (Cumming, GA), ranks for the client's old brand phrase — a brand-confusion risk worth flagging to the client, though not a link issue.

**Note B — GuildQuality is already held, and the competitor claim is wrong.** NG Windows has a long-standing GuildQuality presence: `guildquality.com/pro/north-georgia-replacement-windows` and `/pro/ng-windows-formerly-north-georgia-replacement-windows`, with ~8,670 survey responses from 4,748 respondents, 3,661 reviews, 98% recommend rate, and **Guildmaster Awards with Highest Distinction in 2013, 2015, 2017–2022, 2025 and 2026**. The audit's framing — that the DR 75 opportunity is "held by competitor Window World Atlanta" — is incorrect; the client has one of the deeper profiles on the platform. guildquality.com does not appear in refdomains.csv, which most likely means the profile link is **nofollow or uncrawled**, not that it is missing. **Correct action: audit the existing profile's outbound link attribute and ensure the award pages point at ngwindows.com — not "acquire a GuildQuality link."**

**Note C — the Marvin locator claim rests on a product-line confusion.** Marvin runs **two separate dealer networks**. `marvin.com/find-a-dealer` lists Marvin new-construction/architectural dealers — for Alpharetta those are **Architectural Visions Inc** and **AVI (Marvin Design Gallery)**. Replacement-window contractors live on the **Infinity** network at `infinitywindows.com/find-a-dealer`, where NG Windows is already listed and is described as **Infinity by Marvin's exclusive Georgia contractor** and a **President's Circle partner**. The marvin.com locator entry is not "unclaimed" — NG Windows is in the network it belongs to, and is not eligible for the other. **No outreach will produce this link.**

**Note D — DR vs Authority Score.** Several of the audit's numbers appear to mix Ahrefs DR with Semrush Authority Score (the `ascore` column in refdomains.csv). Examples: cobbemc.com given as "AS 41" when its **DR is 55**; atlantahomeimprovement.com given as DR 45 (correct) while the CSV shows AS 24; gnpmilton.com AS 11 vs **DR 26**. These are different scales and should not be presented interchangeably in a client deliverable.

**Note E — what remains unverified.** In order of how much it would change a recommendation: (1) GNFCC's actual membership cost — not published, must be obtained by phone before §5 rank 3 is committed; (2) whether the gnpmilton episode is specifically Ep 37 and whether its link was dofollow; (3) TrustDALE's full fee schedule beyond the partial $275 reference; (4) whether NG Windows is under 20 FTE for the free Georgia Chamber Federation route. None of these were assumed in the client's favour.
