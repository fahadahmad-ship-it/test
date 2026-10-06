# Contradiction Recheck — ngwindows.com Backlink Audit Document Set

**Prepared:** 6 October 2026
**Scope:** All seven documents in `/home/user/test/backlink-audit/` plus `disavow-ngwindows.txt`
and the raw data in `data/`.
**Method:** Line-by-line cross-reading; arithmetic re-derived from
`data/refdomains.csv` (1,232 rows) and `data/anchors_observed.csv` (76 rows); disputed Ahrefs
Domain Ratings re-measured live on the free public DR endpoint (zero API cost).
Semrush and Ahrefs Site Explorer were **not** called — both exhausted.

**This document does not edit anything.** It adjudicates and lists the edits FINAL-AUDIT.md needs.

---

## 0. Independent ground truth established for this recheck

Everything below that is marked **verified** was recomputed here, not taken from any document.

| Quantity | Verified value | Source |
|---|---|---|
| Referring domains enumerated | **1,232** | `data/refdomains.csv`, row count |
| Backlinks summed across those domains | **7,547** | `refdomains.csv`, `sum(links)` |
| AS 0–5 referring domains | **1,015 = 82.39%** | `refdomains.csv` |
| Referring domains at AS exactly 2 | **888** (not 886) | `refdomains.csv` |
| Referring domains at AS ≥30 | **65** | `refdomains.csv` |
| Backlinks held by the AS 0–5 band | **6,078** | `refdomains.csv` |
| Domains on host `203.161.54.114` | **27** (incl. `factmags.com`, `goooogla.com`) | `refdomains.csv` |
| Anchor evidence available | **76 links / 73 domains** | `data/anchors_observed.csv` |
| `/dir/quality-authority-backlinks-148096` direct-target cluster | **exactly 5 domains** | `anchors_observed.csv` |
| `disavow-ngwindows.txt` actual `domain:` lines | **33** (Section 1 = 5, Section 2 = 28) | `grep -c '^domain:'` |

Live Ahrefs free-DR measurements taken for this recheck (6 Oct 2026):

| Domain | DR | Bearing |
|---|---|---|
| `factmags.com` | **75.0** | settles the "DR 60 vs DR 75" dispute |
| `csswinner.com` | **75.0** | confirms red-team and toxicity passes |
| `eurekster.com` | **53.0** | confirms red-team pass |
| `goooogla.com` | **29.0** | **refutes the "DR 60" annotation in the disavow file** |
| 25 of the other 26 domains on `203.161.54.114` | **59.0–60.0** | the uniform block is real — but it is 25 of 27, not 27 of 27 |
| `ngwindows.com` | 27.0 | confirms headline |
| `roiwindows.com`, `thermalprowindows.com`, `ngawindows.com`, `northgeorgiawindows.net` | 0.0 | confirms the shells |

---

## 1. Spam share: 66% vs 68.5% vs 30.7% vs "~2,321 dofollow links"

**Competing claims**

| Claim | Where |
|---|---|
| "~4,894 (66%)" spam links; "roughly two-thirds … ~4,900 of 7,444" | `ngwindows-backlink-audit.md:95`, `:19-20`, `:346` |
| "~2,286 links (30.7% of the profile)" is the dangerous share | `audit-review-and-gaps.md:71-72` |
| "— TOTAL SPAM — ~5,098 — ~68.5%" | `anchor-and-attribution-forensics.md:235` |
| "The dofollow vendor-sales-copy campaign — ~2,321 links … is the part that is unambiguously manipulative"; "'68.5% spam' overstates the *hostile* share" | `anchor-and-attribution-forensics.md:238-244` |
| "~4,894 spam links carrying commercial anchors" (still live) | `impact-and-recovery-roadmap.md:356` |

**Adjudication.** These are not four estimates of one quantity; they are two quantities, each
estimated twice, and the baseline figure is wrong on its own terms.

- **The baseline's 66% / ~4,894 is dead.** It was built by summing anchor clusters and folding the
  2,579-link bare-sister-domain cluster into a "🔴 Critical active PBN blast" total while the same
  document rates that cluster's source (Network C) 🟡 Low risk (`ngwindows-backlink-audit.md:240-256`
  vs `:346`). The red-team pass demonstrated the internal impossibility: the profile grew only
  +2,336 links between Jul 2026 and the audit date, which cannot accommodate 4,894 "recent" links
  (`audit-review-and-gaps.md:73-77`). Correct, and never rebutted.
- **~5,098 / 68.5% is the right number for "spam-associated links of all kinds"**, and it supersedes
  4,894 because it rests on all 503 anchors paginated to exhaustion rather than a partial cluster
  sum (`anchor-and-attribution-forensics.md:217-235`). It is a *superset* figure, including
  nofollow scraper bloat.
- **~2,300 links (~31%) is the right number for "unambiguously manipulative dofollow vendor
  spam."** The red team's 2,286 and the forensics pass's 2,321 are the same measurement computed
  off slightly different anchor totals; they agree to within 1.5%. Forensics' 2,321 is the better
  figure (fuller anchor coverage). The red team's label "30.7%" and forensics' implied 31.2% are
  the same claim.
- **"~4,894 spam links carrying commercial anchors"** in `impact-and-recovery-roadmap.md:356` is
  doubly wrong: the count is retracted, and the characterisation is contradicted by the same
  document set — exact-match commercial anchors are **3.2%** of the clean profile
  (`anchor-and-attribution-forensics.md:261-266`).

**Correct statement:** ~5,100 links (≈68.5%) are spam-associated; of those, ~2,320 (≈31%) are the
dofollow, purpose-built, vendor-sales-copy campaign; the remainder is largely nofollow scraper
bloat that predates the blast by a year. Retire 66% / 4,894 entirely.

**Does FINAL-AUDIT.md state it correctly?** **No — it does not state it at all.** FINAL-AUDIT
never gives a spam share. It uses the 68.5% basis implicitly and silently: "~4,815 toxic links"
(`FINAL-AUDIT.md:52`, `:215`) plus "~283 links hitting ngwindows.com directly" (`:225`) = 5,098,
i.e. the forensics total. So the client-facing document adopts the *larger* of the two framings
without naming it, without the percentage, and without the forensics pass's own refinement that
the hostile share is ~2,320. The single most quotable number in the engagement is missing, and
the one number FINAL does carry forward (4,815) is the one the source document partially walked
back. This is the most consequential omission in the file.

### 1a. A quantitative impossibility FINAL-AUDIT inherits

FINAL-AUDIT asserts both:
- "~4,815 toxic links" + "~283 direct" = 5,098 spam links (`FINAL-AUDIT.md:52`, `:225`); and
- "**Where the links land:** ~100% on the **homepage**" (`FINAL-AUDIT.md:107`).

But all four homepage variants combined hold only **~3,883 links**
(`audit-review-and-gaps.md:227-234`; same table at `anchor-and-attribution-forensics.md:174-177`).
5,098 spam links cannot all land on 3,883 link slots — the claim is short by ~1,215 links. The two
statements are reconcilable only under the ~2,320 figure. FINAL-AUDIT carries both and neither
source document noticed. **Flagged as new.**

---

## 2. Referring domains: 1,225 vs 1,227 vs 1,232

| Claim | Where |
|---|---|
| 1,225 | `ngwindows-backlink-audit.md:40`, `:320`; `anchor-and-attribution-forensics.md:18`; `impact-and-recovery-roadmap.md:71`, `:306`, `:429` |
| 1,227 | `audit-review-and-gaps.md:35`, `:155`, `:184`; `impact-and-recovery-roadmap.md:216`, `:233` |
| 1,232 | `toxic-domain-inventory.md:5`, `:67`; `FINAL-AUDIT.md:18`, `:64` |

**Adjudication: 1,232 is correct, and the other two are not errors — they are a different endpoint.**
1,225 and 1,227 are `backlinks_overview` snapshots taken hours apart on a live, growing profile.
1,232 is the full pagination of `backlinks_refdomains` and is independently **verified** here
(`data/refdomains.csv` = 1,232 rows). 1,232 is the only one usable as a denominator.

Two caveats nobody has stated cleanly: (a) 1,232 is **also not complete** — the toxicity pass found
two domains present in `backlinks` but absent from the 1,232-row list
(`toxic-domain-inventory.md:69-71`), confirmed here (`urlbacklinkschecker.space` and
`backlinkcheckerseo.space` are not in `refdomains.csv`); and (b) the same split affects total
backlinks — 7,444 (overview) vs 7,449 (re-pull) vs **7,547** (sum over refdomains, verified).

**Does FINAL-AUDIT state it correctly?** **Yes for the domain count** (1,232, labelled "full
enumeration"). **Partly for backlinks:** "7,444–7,547 (drifts daily; blast is live)"
(`FINAL-AUDIT.md:63`) presents an endpoint disagreement as temporal drift. Some of the gap is
drift; ~100 links of it is methodological. Minor, but it should say so.

**One inherited error FINAL-AUDIT does not catch:** `FINAL-AUDIT.md:65` reports "Follow / nofollow
5,624 / 1,896" — the *baseline's* numbers, not the red team's corrected re-pull of 5,628
(`audit-review-and-gaps.md:35`). Worse, the red team specifically flagged that these buckets are
non-additive (5,628 + 1,896 = 7,524 against a stated total of 7,449; the baseline rendered them as
75.6% + 25.5% = 101.1% without comment — `audit-review-and-gaps.md:173-178`). FINAL-AUDIT
reproduces the uncorrected figures and omits the flag.

---

## 3. AS 0–5 toxicity: "84%" twice vs "6.3% evidenced" — is FINAL-AUDIT's reconciliation honest?

**Competing claims**

| Claim | Where |
|---|---|
| "(a) Vendor sales-copy … **~84%**"; benign buckets "~16%" — 878 domains / 2,532 links | `anchor-and-attribution-forensics.md:380`, `:385`, `:343-372` |
| "Vendor sales copy — 409 domains — **84.3%**" — 485 domains / 1,000 links | `as0-5-anchor-evidence.md:40` |
| "only **64 of 1,015** AS 0–5 domains (**6.3%**) can currently be shown to be manipulative" | `toxic-domain-inventory.md:96-98`, table at `:83-92` |
| FINAL's reconciliation: "Three measurements of the AS 0–5 band, which must not be conflated" | `FINAL-AUDIT.md:123-134` |

**Adjudication: FINAL-AUDIT's framing is dishonest in the opposite direction from the one
suspected. It manufactures a disagreement that does not exist.**

The 6.3% is not a third measurement of toxicity. It is a **coverage** statistic. Look at the
toxicity pass's own table (`toxic-domain-inventory.md:83-92`): of the 1,015 AS 0–5 domains, only
**70** had any anchor data at all — 945 are "no anchor data retrievable" (93.1%). Within the 70
that were observed: 64 vendor sales-copy dofollow + 2 vendor nofollow + 4 bare-domain =
**64/70 = 91% carrying vendor sales copy**. That *agrees* with 84.3% and ~84%; it does not
contradict them. The 6.3% is simply 64 divided by the wrong denominator — the whole band rather
than the observed subset. The toxicity pass is explicit about this ("This is the honest answer and
it is mostly a gap", `:94`), but FINAL-AUDIT strips that context and tabulates 6.3% in the same
column as 84.3% and ~84%, under the shared heading "Finding".

A reader of `FINAL-AUDIT.md:125-134` is left believing a careful pass found the band to be
one-thirteenth as toxic as two earlier passes claimed. No pass found that. Nothing in the repo
supports a toxicity estimate below ~84%.

**The real weakness FINAL-AUDIT misses — and it cuts the other way.** FINAL calls the two 84%
figures "Independent sample A" and "Independent sample B" and says "the first two agree closely"
(`FINAL-AUDIT.md:127-131`). They are not independent in the sense that matters:

- Sample A sorted `last_seen_desc`, which front-loads the live campaign. Its own document says so
  and draws the conclusion FINAL-AUDIT deletes: *"These numbers are an **upper bound** on toxicity,
  not a lower one"* (`as0-5-anchor-evidence.md:14-17`).
- Sample B sorted `page_authority_score_asc`, which front-loads the low-authority band, and admits
  72% coverage weighted toward the band, per-bucket samples of 12–44, and a substituted authority
  metric (`anchor-and-attribution-forensics.md:327-341`).

Two samples biased the same direction agreeing with each other is weak corroboration, not strong.
FINAL-AUDIT presents their agreement as the reason to trust them and drops both caveats.

**Does FINAL-AUDIT state it correctly? No.** The prose partially rescues it ("only 6.3% can be
documented domain-by-domain, because the API ran dry", `:132-133`), but the table that the client
will read is wrong in structure, and the suppressed upper-bound caveat is a material omission.

---

## 4. Attribution: negative SEO vs purchased campaign vs "inference flagged as such"

| Claim | Where |
|---|---|
| "either (a) a link vendor the client … engaged, or (b) a **negative SEO attack** — most likely the latter"; "ngwindows.com is one name on that list, not necessarily the buyer" | `ngwindows-backlink-audit.md:26-27`, `:121-127`; risk row `:347` |
| "most likely a negative SEO attack is the weaker of the two readings, and it's alarmist" | `audit-review-and-gaps.md:163-171` |
| "purchased / managed link campaign … **Confidence: high (~85%)**"; B (negative SEO) ~12%; C (scraped list) ~3% | `anchor-and-attribution-forensics.md:29-32`, `:152-154` |
| "This **reads as** a purchased or managed campaign … The residual uncertainty is registrant identity … put it to the client directly" | `toxic-domain-inventory.md:196-199` |
| "**almost certainly a purchased campaign**, not a negative SEO attack (~85% confidence)" | `FINAL-AUDIT.md:39-42` |

**Adjudication: the purchased-campaign reading is correct; the baseline is refuted; the stated
confidence is defensible but the wording overstates it.**

The evidence is strong and is not disputed by any later document: 14 content-free 301 shells all
funnelling into one target, five of them defensive typo-variants of the client's own brand, a
per-target vendor campaign ID for ngwindows.com itself, lockstep growth curves, and zero unrelated
window domains across 503 anchors. The baseline's negative-SEO reading is dead and its own §4.3
reasoning defeats it.

But "~85%" and "almost certainly" are not the same register. 85% leaves a ~1-in-7 chance, and the
forensics pass put a specific **~12%** on the negative-SEO branch — a branch that, if it fires,
inverts the entire remediation plan and makes this a live security incident. FINAL-AUDIT quotes the
85% but never surfaces the 12%, and the only trace of the alternative is the conditional in the
action plan (`FINAL-AUDIT.md:217-218`). It also silently upgrades the toxicity pass's softer
formulation ("reads as", "inference, flagged as such") to "almost certainly".

In FINAL's favour: it *does* say "Registrant identity is unverified — the proxy blocked WHOIS"
(`:41-42`), repeats it as the first unknown (`:255`), and makes the WHOIS check action 1 gating
everything (`:211-213`). The substance is honest. The adjective is not.

**Does FINAL-AUDIT state it correctly? Substantially yes, verbally no.** Fix: "likely a purchased
campaign (~85%); negative SEO remains at ~12% and is not excluded until WHOIS is run."

---

## 5. Disavow entry count: 84 → 66 → 34 → 33

**The chain as it actually appears in the repo** is 109 → 66 → 34 → 33. No document anywhere
contains an "84-entry" disavow file; the red-team pass counted the original at **109**
(`audit-review-and-gaps.md:184`, `:265`, and its line-109/line-108 citations at `:191-195`). If 84
was a real intermediate, it left no trace.

**Verified current state of the deliverable:** `disavow-ngwindows.txt` contains **33** `domain:`
lines (Section 1 = 5, Section 2 = 28).

**Does every document reflect 33? No. Three places are stale, and one of them is the deliverable
itself.**

| Document | States | Status |
|---|---|---|
| `disavow-ngwindows.txt:120` | "**TOTAL DISAVOW ENTRIES: 34**" | ❌ wrong — the file holds 33 |
| `disavow-ngwindows.txt:306` | "Those **29** entries rest on domain-name character" | ❌ wrong — Section 2 holds 28 |
| `disavow-ngwindows.txt:53` | "all **27** resolve to the SAME host" | ✔ true of the host cluster, ✘ misleading as a description of Section 2 (28 entries, 27 on that host) |
| `toxic-domain-inventory.md:60`, `:73`, `:255` | "34" and "criterion 3 → **29**" | ❌ stale by one |
| `impact-and-recovery-roadmap.md:306` | "Submit the domain-level disavow … Export the full **1,225**-domain referring list" | ❌ stale count *and* stale sequencing (see §9) |
| `ngwindows-backlink-audit.md:308-311` | submit disavow (item 3) before manual-action check (item 4) | ❌ retracted ordering, uncorrected |
| `FINAL-AUDIT.md:152`, `:156-157`, `:226` | 33 = 5 + 28 | ✔ **correct** |

So FINAL-AUDIT is the *only* document with the right number, and the file it points the client at
contradicts it on its own face. A client who opens the deliverable reads "34".

### 5a. An entry no stated criterion admits — `goooogla.com` (new finding)

`disavow-ngwindows.txt:85-88` disavows `goooogla.com` under "**CRITERION 4 (co-hosting), NOT a
link-selling name**". There is no criterion 4. The file's own evidence standard lists criteria 1,
2 (gate) and 3 (`:16-27`) and explicitly says "**NOT grounds** for any entry in this file: … shared
IP alone" (`:29-30`). The toxicity pass says the same: "**None of the clusters above are in the
disavow file** — co-hosting is not per-domain evidence" (`toxic-domain-inventory.md:169-171`) —
which is now false, because one is.

It gets worse on two counts:

1. **The annotation is factually wrong.** The file records "Ahrefs DR 60" for `goooogla.com`
   (`:87`). **Measured live for this recheck: DR 29.0.** So the single supporting fingerprint
   claimed for it — membership of a uniform DR 59–60 block — is not present.
2. **It is irreconcilable with the exclusion of `factmags.com`.** FINAL-AUDIT excludes factmags
   because "grounds were co-hosting rather than its own anchor" (`FINAL-AUDIT.md:167-169`).
   `goooogla.com` is on the *same host*, with the *same* (absent) anchor evidence, and is kept.
   The audit applies opposite rules to two domains in the same cluster.

FINAL-AUDIT does not mention `goooogla.com` at all and describes Section 2 as "Link-selling domain
name + shared host + uniform DR 59–60" (`:157`) — a description 27 of the 28 entries satisfy and
one does not.

### 5b. "All 27 return DR 59–60" is false (new finding)

`toxic-domain-inventory.md:40-42`, `disavow-ngwindows.txt:51-54` and `FINAL-AUDIT.md:160-161`
("The uniform DR 59–60 across 27 co-hosted sellers is itself an authority-inflation signature")
all assert a uniform DR block across all 27 domains on `203.161.54.114`.

**Measured live, all 27:** 25 return DR 59–60. `factmags.com` returns **75.0** and `goooogla.com`
returns **29.0**. The signature is real and still probative — but it is 25/27, and the two
exceptions are precisely the two domains the audit argues about. Since the uniform-DR block is the
*only* supporting fingerprint offered for Section 2, the claim has to be stated accurately.

---

## 6. "886 domains at AS 2"

| Claim | Where |
|---|---|
| "886 … at exactly Authority Score 2 … the single most damning chart in the audit" | `ngwindows-backlink-audit.md:67`, `:73-76`, `:349` |
| "not diagnostic of anything. **Drop it.**" — rounding artifact of an integer log-scale metric | `audit-review-and-gaps.md:79-112` |
| "The draft's §2, **§3**, §5, §6, §7 and §8 … are unaffected and **remain accurate**" | `anchor-and-attribution-forensics.md:560-561` |
| competitors show "the same AS-2 mega-cluster (431 and 553 domains)"; the ratio is a 4–8pp deviation, not an outlier | `impact-and-recovery-roadmap.md:230`, `:237-242` |
| "'886 domains at Authority Score 2' is withdrawn" | `FINAL-AUDIT.md:77-82` |

**Adjudication: withdrawal is correct, on two independent grounds, and FINAL-AUDIT states it
correctly** — including the replacement fingerprint (shared `/dir/` path slugs with identical
numeric IDs), which is genuinely deterministic and which I confirmed in
`data/anchors_observed.csv`: six slugs, each reused verbatim across 5–15 unrelated registrable
domains with one fixed anchor each.

**But the withdrawal is not propagated, and one document re-endorses it.**

- `anchor-and-attribution-forensics.md:560-561` explicitly certifies the baseline's **§3** — the
  AS-2 chart — as "unaffected and remain accurate". That is a direct, uncorrected contradiction of
  the red-team retraction, sitting in a 561-line document a reader may well treat as the most
  thorough pass. **This is the single most dangerous live contradiction in the set**, because it
  reinstates a withdrawn claim by name.
- `ngwindows-backlink-audit.md` itself is untouched: §3's "single most damning chart" and §10's
  risk row both still stand.
- The count is also wrong on its own terms: **verified 888**, not 886 (`data/refdomains.csv`).
  Immaterial to the argument, but it shows no one re-derived it.
- The two rebuttals are different and both valid, and FINAL-AUDIT uses only one. The red team's
  ground is *metric binning*; the roadmap's ground is *peer parity* (Window World Atlanta 74.9%,
  Davis 80.4% — `impact-and-recovery-roadmap.md:230`). FINAL-AUDIT takes the binning argument at
  `:77-78` and separately deploys the peer-parity data at `:193-199` without connecting them. The
  peer comparison is the more persuasive one for a client and deserves to be named as the second
  reason the AS-2 cluster proves nothing.

---

## 7. Subnet / Cloudflare evidence

| Claim | Where |
|---|---|
| "1,141 IPs across only 428 class-C subnets … Healthy organic profiles trend toward 1:1" | `ngwindows-backlink-audit.md:53-55`, `:353`; KPI at `:338` |
| "Not true … 1:1 is not the healthy baseline; it is close to unachievable … should be dropped" | `audit-review-and-gaps.md:130-136` |
| "861 of 1,232 (69.9%) resolve to Cloudflare anycast … uninformative in both directions … should be **struck from the client-facing report**" | `toxic-domain-inventory.md:142-148`, `:205-209` |
| "Subnet clustering as stated is not evidence … **Struck.**" | `FINAL-AUDIT.md:71-76` |

**Adjudication: struck, correctly, and FINAL-AUDIT states it correctly** — including the right
replacement (the three real non-Cloudflare host clusters).

**But it still stands uncorrected in two places:**

- `ngwindows-backlink-audit.md:53-55`, `:353` — the original claim, and `:338`, which sets
  "class-C-to-domain ratio approaching 1:1" as a 90-day success metric.
- **`impact-and-recovery-roadmap.md:394`** — the live KPI table still carries
  "Referring class-C subnets per domain | 2.9 | <2.2 | <1.6". This is the retracted metric
  converted into a *contractual client target*. It is the worst surviving instance, because an SEO
  will be measured against a number that is measuring Cloudflare's address allocation.

---

## 8. `factmags.com`, `csswinner.com`, `eurekster.com`

| Domain | Baseline | Red team | Toxicity pass | Disavow file | FINAL-AUDIT | Verified DR |
|---|---|---|---|---|---|---|
| `factmags.com` | Network C "auto-generated scraper, AS 2–4" (`:251`), in draft disavow line 108 | "DR 75 is not a scraper profile … do not disavow without manual inspection" (`:194`) | DR 75, "High DR, highly suspicious company. No anchor evidence → excluded" (`:218-220`) | **PROTECTED** list (`:241-242`) + "REMOVED … two passes disagree (DR 60 vs DR 75)" (`:255-260`) | "Removed as false positive … DR 60 vs DR 75; conflicting evidence excludes by default" (`:167-169`) — **and simultaneously cited as high-authority spam** (`:142-143`) | **75.0** |
| `csswinner.com` | Network C, listed for disavow (`:251`) | "Keep. **Fix §7.**" DR 75, nofollow, already lost (`:195`, `:284`) | "No anchor evidence of manipulation → removed" (`:221-222`) | PROTECTED (`:241`) + review note (`:262`) | Removed as FP ✔ (`:167`) | **75.0** |
| `eurekster.com` | **absent from the body entirely**, but present in the draft disavow at line 109 | "An unsourced entry … **Remove.**" DR 53, deep link with the client's real page title, already lost (`:193`) | removed (`:223`) | PROTECTED (`:243`) | Removed as FP ✔ (`:167`) | **53.0** |

**Adjudication**

- **`csswinner.com` and `eurekster.com`: settled and correct.** Both out of the disavow, both
  verified at the DRs claimed. FINAL-AUDIT states both correctly. The only residue is the baseline,
  where `csswinner.com` still sits in the Network C disavow list (`ngwindows-backlink-audit.md:251`)
  — the red team asked for §7 to be fixed and it never was.
- **`factmags.com`: not settled, and FINAL-AUDIT gets it wrong twice.**
  1. **The stated rationale is unfounded.** "Two passes disagree on its authority — DR 60 vs DR 75"
     (`FINAL-AUDIT.md:168-169`). No pass ever measured factmags at DR 60. The toxicity pass says
     DR 75 (`:218`); the red team says DR 75.0 (`:194`). The "DR 60" is an artifact of the blanket
     "all 27 on that host are DR 59–60" assertion — which §5b above shows is itself the error.
     **Measured live: 75.0, unambiguously.** There is no conflicting evidence; the correct reason
     to exclude factmags is simply that no anchor evidence exists for it.
  2. **FINAL-AUDIT asserts both sides.** `:142-143` lists factmags under "**High-authority spam**
     that a benign-anchor rule lets through", citing its co-hosting with 26 link sellers; `:167-169`
     lists it under "**Removed as false positives**". Both in the same section, 25 lines apart.
  3. **"PROTECTED" is the wrong bucket.** `disavow-ngwindows.txt:231-237` heads that list
     "**DO NOT DISAVOW UNDER ANY SWEEP** — Legitimate local / trade / industry sites", then places
     factmags among `forsythcounty.com` and `georgiashutters.com` while conceding in the next
     breath that it "genuinely warrants a human look" (`:245-248`). A domain co-hosted with 26
     named backlink sellers belongs on a watchlist, not on a permanent exclusion list.

---

## 9. Further contradictions found (not on the brief)

**9.1 — Trust Score > Authority Score: a refuted metric, reinstated by FINAL-AUDIT.**
The red team: Trust = Authority is "extremely common and is not in itself a signal"; setting
"Trust Score rising above Authority Score" as a success metric is "an arbitrary target with no
basis … **Remove it from the KPI list**" (`audit-review-and-gaps.md:123-128`). Nothing anywhere
rebuts this. Yet it survives in `anchor-and-attribution-forensics.md:544`, is promoted in
`impact-and-recovery-roadmap.md:392` and `:397-398` to "**the single best signal** … Watch this one
above all others" and becomes escalation trigger #5 (`:440`) — and FINAL-AUDIT reinstates it as
the **"Key healing signal"** (`FINAL-AUDIT.md:265-266`). FINAL-AUDIT is the document that is
supposed to carry the corrections, and on this point it carries the error instead.

**9.2 — Action ordering: fixed in FINAL-AUDIT, still inverted in two live documents.**
The red team's central procedural correction was that the GSC manual-action check gates the
disavow, not the reverse (`audit-review-and-gaps.md:327-329`, `:382-392`). FINAL-AUDIT gets this
right (`:211-228`: WHOIS → manual action → disavow only if). But
`impact-and-recovery-roadmap.md:306` still instructs "Submit the domain-level disavow" as Day-1
item 1, with no manual-action gate, and `ngwindows-backlink-audit.md:308-311` still has submit
before check. Both uncorrected.

**9.3 — Lost-link reclamation is truncated.** The red team identified four-plus lost genuine links:
`gnpmilton.com`, `atlantahomeimprovement.com`, `atlantaunitedsoccer.com`, `vuink.com`
(`audit-review-and-gaps.md:276-286`), calling reclamation "highest expected value per hour of
anything in either document". FINAL-AUDIT §6 action 4 carries only the first two
(`FINAL-AUDIT.md:230-234`). The other two are dropped without explanation.

**9.4 — "100% of the spam lands on the homepage" is stated with false precision.** Forensics asserts
100% (`anchor-and-attribution-forensics.md:201`); the red team's narrower claim was "every single
Network A and Network B link **in my pulls**" (`audit-review-and-gaps.md:239-240`). FINAL-AUDIT
says "~100%" (`:107`). Given the arithmetic in §1a above, the honest statement is "all spam
observed at link level targeted a homepage variant" — a sampling result, not a census.

**9.5 — Defensive typo-variants: 4 or 5?** `anchor-and-attribution-forensics.md:152` and
`FINAL-AUDIT.md:215` say **5**; `toxic-domain-inventory.md:190` says "**Four** of the fourteen are
near-exact brand variants". Trivial, but it is an instruction to the client about which domains to
keep registered.

**9.6 — When the shells first appeared: three answers.** "first appeared **Jul 2024 – Jul 2025**"
(`toxic-domain-inventory.md:191-192`); "registered or re-pointed around **late 2024**", with
referring-domain history starting Nov 2024 (`anchor-and-attribution-forensics.md:95-110`); the
feed-in timeline runs **Jul 2025 → May 2026** (`anchor-and-attribution-forensics.md:146-159`).
FINAL-AUDIT says "climbed in lockstep from **Nov 2024**" (`:41`), which matches the strongest
source. Fine as stated, but the roadmap's Jul 2024 start is unsourced and should not survive.

**9.7 — Network B membership changed silently.** Baseline Network B = 10 domains including
`backlinkhouse.com`, `backlinkstree.com`, `seodomains.website`, `goooogla.com`, `seonix.agency`
(`ngwindows-backlink-audit.md:232-233`). The toxicity pass's Network B = 7 different domains
(`toxic-domain-inventory.md:124-127`), adding `mervi.shop`/`nimbra.shop` and dropping four. No
document explains the reclassification; `backlinkstree.com` meanwhile appears on the
*behaviourally harmless* list in `as0-5-anchor-evidence.md:54`. Low stakes — none of them are in
the disavow file except `goooogla.com` — but it is an unexplained change of a named finding.

**9.8 — Velocity is still misattributed in the baseline.** "+44% in September 2026 alone
(849 → 1,225)" (`ngwindows-backlink-audit.md:19-21`) is the September→October change, as the
baseline's own table shows (`:148-149`) and the red team noted (`:146-151`). FINAL-AUDIT sensibly
omits velocity percentages entirely; `impact-and-recovery-roadmap.md:451` gets it right
("+376 referring domains in October"). Baseline uncorrected.

---

## 10. The critical question: does FINAL-AUDIT.md adequately supersede the baseline?

**No. The supersession is one-directional and therefore ineffective.**

`FINAL-AUDIT.md:5-6` says "This document supersedes `ngwindows-backlink-audit.md`, which contains
errors corrected here. Read this one." That notice is only visible to someone who has already
opened the right file. `ngwindows-backlink-audit.md` carries **no status marker of any kind** — it
opens as "# Backlink Audit — ngwindows.com (North Georgia Replacement Windows)", dated the same
day, with a confident §1 "Verdict first". It is also the most obviously-named file in the
directory and the one a client searching for "the backlink audit" will open first.

What that reader would come away with, all of it retracted elsewhere and none of it marked:

- "**most likely** a **negative SEO attack**" (`:26-27`) and a 🔴 Critical risk row for it (`:347`)
  — refuted; the evidence points to a purchased campaign on the client's own behalf.
- "**two-thirds of the entire backlink profile (~4,900 of 7,444)**" (`:19-20`) — withdrawn.
- "**886 referring domains … the single most damning chart in the audit**" (`:67`, `:73`) —
  withdrawn, and the true count is 888.
- "**Submit a disavow file**" as immediate action 3, *ahead of* the manual-action check (`:308-311`)
  — the ordering was explicitly reversed, and current guidance is not to submit at all absent a
  manual action.
- `csswinner.com` and `factmags.com` named for disavowal (`:251`) — both now excluded.
- The class-C subnet argument (`:53-55`) — struck.
- "Paid links not disclosed" as a client-culpability risk row (`:350`) — the red team showed
  `rel="sponsored"` can only be set by the linking site (`audit-review-and-gaps.md:114-121`).

A client acting on that document would brief a negative-SEO narrative, quote a 66% spam figure,
submit a 109-line disavow without checking for a manual action, and disavow two DR-75 legitimate
directories. Every one of those is a client-visible error, and two of them (the attack narrative
and the unsupervised disavow) are actively harmful.

**Recommendation — strongest to weakest:**

1. **Preferred: move it out of the working directory** to `archive/` (or `superseded/`) with a
   `README` stating what it is. This removes the find-the-wrong-file risk entirely rather than
   mitigating it.
2. **If it must stay in place:** rename to `ngwindows-backlink-audit.SUPERSEDED.md` **and** prepend
   a blocking banner as the first lines of the file — `> ⛔ SUPERSEDED 6 Oct 2026. DO NOT SEND TO
   THE CLIENT. DO NOT QUOTE. Replaced by FINAL-AUDIT.md.` — followed by the six-bullet retraction
   list above. A banner alone, without the rename, is weaker: the filename is what gets picked.
3. **Do not simply delete it.** It is the provenance record for the disavow file's evolution and
   the red-team pass is written as a commentary on it; deleting it orphans the review chain. Archive
   with a pointer.

**The same problem applies, less acutely, to the three interim passes.** None of
`audit-review-and-gaps.md`, `anchor-and-attribution-forensics.md` or
`impact-and-recovery-roadmap.md` carries a status header, and each contains at least one claim that
a later pass retracted — the forensics pass re-certifies the withdrawn AS-2 chart (§6 above), the
roadmap carries two retracted KPIs and a retracted disavow-first instruction (§7, §9.1, §9.2), and
the roadmap still quotes the 4,894 figure. Only `as0-5-anchor-evidence.md` handles this properly,
with a self-labelled "**This finding is now partly superseded**" closing section (`:71-74`) — that
is the pattern the other three should follow.

**FINAL-AUDIT.md also lacks a document index.** It names the baseline as superseded but says
nothing about the status of the other five files, so a reader cannot tell which are live working
papers and which are history.

---

## 11. Prioritised edits FINAL-AUDIT.md needs

### P0 — client-visible errors or safety

1. **§4, lines 123–134 — rebuild the "Three measurements" table.** It is not three measurements of
   one thing. Present two estimates (84.3% and ~84%, both marked as **upper bounds** because of
   their sort-order bias) plus one **coverage** figure. State the correct comparable: of the 70
   AS 0–5 domains with any anchor data, **64 (91%) carry vendor sales copy** — which agrees with
   the estimates. Replace the "6.3%" row label "Individually evidenced / Finding" with
   "Documented domain-by-domain / **coverage**, 64 of 1,015 band members, 945 untestable".
   Restore the `as0-5-anchor-evidence.md:14-17` upper-bound caveat and drop the word
   "Independent" from samples A and B.
2. **§4, line 168 — delete "two passes disagree on its authority — DR 60 vs DR 75".** It is
   unfounded; `factmags.com` is DR **75.0**, re-verified today, and no pass ever said 60. Replace
   the exclusion rationale with "no anchor evidence retrievable; co-hosting alone is not grounds".
   Then **resolve the self-contradiction** between line 142 (factmags cited as high-authority spam)
   and line 167 (factmags listed as a removed false positive) — pick one, and recommend moving it
   from the disavow file's PROTECTED list to an explicit watchlist.
3. **§4, line 157 and line 160 — correct the Section 2 description.** (a) "uniform DR 59–60 across
   27 co-hosted sellers" is **25 of 27**; `factmags.com` is DR 75 and `goooogla.com` is DR 29
   (both measured today). (b) Disclose `goooogla.com`: it is in Section 2 on co-hosting alone, under
   an invented "criterion 4" the file's own evidence standard forbids, with a DR annotation that is
   wrong by 31 points. Recommend dropping it — which also makes the file 32 entries and removes the
   inconsistency with the factmags exclusion.
4. **§8, lines 265–266 — remove "Trust Score crossing above Authority Score" as the key healing
   signal.** Explicitly retracted at `audit-review-and-gaps.md:123-128` and never rebutted.
   Replace with signals that are actually diagnostic: new referring domains per week returning to
   the ~400–600 pre-campaign baseline, and the disappearance of the `/dir/` slug fingerprint.
5. **Add a one-line pointer on the disavow-file discrepancy** at §4 line 152 / §6 line 226: the
   delivered file's own header still reads "TOTAL DISAVOW ENTRIES: 34" and "those 29 entries"
   against an actual 33 / 28. FINAL-AUDIT is right and the deliverable is wrong; until the file is
   corrected, say so rather than letting the client find it.

### P1 — accuracy and completeness

6. **§1 / §3 — state the spam share explicitly, in both forms.** "~5,100 links (≈68.5%) are
   spam-associated; of those, ~2,320 (≈31%) are the dofollow vendor-sales-copy campaign that is
   unambiguously manipulative; the balance is largely nofollow scraper bloat predating the blast
   by a year." Add one line retiring "66% / ~4,894" by name, since it is still live in two
   documents and is the figure the client may already have heard.
7. **Reconcile §1 line 52 / §3 line 107.** 5,098 spam links cannot all land on ~3,883 homepage
   links. Either quote the ~2,320 figure alongside, or soften to "all spam observed at link level
   targeted a homepage variant (sampled, not a census)".
8. **§1 line 39 — change "almost certainly" to "likely (~85%)" and surface the ~12%
   negative-SEO branch** from `anchor-and-attribution-forensics.md:153`. The substance is already
   honest; the adjective is not, and the 12% branch is the one that changes the whole engagement.
9. **§2 line 65 — fix follow/nofollow and flag the non-additivity.** Use the red team's re-pull
   (5,628 / 1,896) and note that the buckets sum above the stated total, so neither should be
   quoted as a percentage. Also soften line 63: part of the 7,444–7,547 spread is endpoint
   disagreement, not daily drift.
10. **§2 lines 77–82 — add the second reason the AS-2 cluster proves nothing:** peer parity.
    Window World Atlanta 74.9% and Davis 80.4% at AS 0–5, with their own AS-2 clusters of 431 and
    553 (`impact-and-recovery-roadmap.md:230`, `:237-242`). FINAL already has this data at
    lines 193–199 but never connects it to the withdrawal. Also note the verified count is 888,
    not 886.
11. **§6 action 4 — restore the two dropped reclamation targets**, `atlantaunitedsoccer.com` and
    the `vuink.com` deep link (`audit-review-and-gaps.md:282-283`).

### P2 — document hygiene (this is the part that actually protects the client)

12. **Upgrade the supersession from a note to a structural fix.** FINAL-AUDIT's header
    (lines 5–6) cannot protect a reader who never opens FINAL-AUDIT. Archive
    `ngwindows-backlink-audit.md` out of the working directory, or at minimum rename it
    `*.SUPERSEDED.md` and prepend a blocking do-not-send banner with the six-item retraction list
    in §10 above.
13. **Add a document index to FINAL-AUDIT** stating the status of all seven files: which are
    client-deliverable (FINAL-AUDIT + the disavow file), which are internal working papers, and
    which is superseded. Right now a reader cannot tell.
14. **Flag the three interim passes' surviving retracted claims** so they are not quoted from:
    `anchor-and-attribution-forensics.md:560-561` (re-certifies the withdrawn AS-2 chart by name —
    the most dangerous single line in the set); `impact-and-recovery-roadmap.md:394` (class-C KPI),
    `:392`/`:397-398`/`:440` (Trust>Authority KPI), `:306` (disavow-first, stale 1,225),
    `:356` (the 4,894 figure). Follow the pattern `as0-5-anchor-evidence.md:71-74` already sets.
15. **Record the two referring-domain endpoint disagreements** as a data caveat:
    `urlbacklinkschecker.space` and `backlinkcheckerseo.space` appear in `backlinks` but not in the
    1,232-row `backlinks_refdomains` list (`toxic-domain-inventory.md:69-71`, confirmed against
    `data/refdomains.csv`). The "full enumeration" is complete to the endpoint, not to the profile.

---

## Appendix — what FINAL-AUDIT already gets right

Worth recording, so the edit list is not read as a verdict on the document:

- Referring domains **1,232** as the denominator — correct and verified.
- AS 0–5 **82.4%**, AS ≥30 **65** — both verified against raw data.
- Disavow **33 = 5 + 28** — the only document with the right count.
- The redirect-shell mechanism, the campaign-ID fingerprint, and the shared `/dir/` slug
  fingerprint — all confirmed in `data/anchors_observed.csv` (six slugs, 5–15 domains each,
  one fixed anchor per slug; the five Section 1 domains match the
  `/dir/quality-authority-backlinks-148096` cluster exactly).
- Action ordering (WHOIS → manual action → disavow only if) — correctly implements the red-team
  correction that two other documents still ignore.
- "No link is disavowed for being low authority. Ever." — correct, consistently applied, and the
  single best decision in the whole engagement.
- The traffic-impact separation (collapse pre-dates the blast by 12 months; +45% since) — internally
  consistent with the roadmap throughout.
- `csswinner.com` and `eurekster.com` exclusions — correct, and DRs verified today.
