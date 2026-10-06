# Red-Team Review — ngwindows.com Backlink Audit

**Reviewer role:** adversarial QA / second opinion
**Review date:** 6 October 2026
**Under review:** `backlink-audit/ngwindows-backlink-audit.md` and `backlink-audit/disavow-ngwindows.txt`
**Method:** independent re-pull of Semrush `backlinks_overview`, `backlinks_anchors`, `backlinks_pages`,
`backlinks`, `backlinks_categories`, `backlinks_categories_profile`; Ahrefs free public Domain Rating
endpoint for spot-checks. Ahrefs Site Explorer remains unavailable (units exhausted to 25 Oct 2026).

**Bottom line up front:** the audit correctly identifies that a real, large, currently-active PBN
blast is hitting this domain. It then overstates the size of it by roughly 2x, builds its headline
"single operator" proof on a statistic that does not survive contact with the data, and recommends
submitting a disavow file built from a 9% sample before checking whether a disavow is warranted at
all. The single most valuable thing in the data — that the client is quietly **losing genuine
editorial links** while gaining spam — is absent from the audit entirely.

---

## 1. Claims that hold up

Stated once each, no elaboration needed.

- **There is a real, ongoing, automated link blast.** Confirmed. New links were landing within the
  hour of my pull (`first_seen` timestamps up to 1791298901 ≈ 6 Oct 2026).
- **The anchor text is literal SEO-vendor sales copy, including Telegram handles.** Confirmed verbatim.
- **The sister/competitor window domains used as anchor text are all Ahrefs DR 0.** Independently
  verified: `ngawindows.com`, `thermalprowindows.com`, `roiwindows.com`, `qualitypluswindows.com`,
  `northpointwindows.com`, `performingwindows.com`, `thermatrustwindows.com`,
  `northgeorgiawindows.net`, `e2windows.com`, `thermalastwindows.com`, `choiceviewwindows.com` —
  **every one DR 0.0**. The audit's "one vendor running one template across a scraped list of window
  companies" reading is correct and is the best inference in the document.
- **Networks A and B are correctly identified and correctly separated.** The domain lists are accurate.
- **The genuine (non-spam) anchor mix is healthy** — branded and naked-URL dominant, no organic
  over-optimisation. Correct.
- **Headline metrics match source.** My re-pull: AS 30, total 7,449, 1,227 ref domains, 1,141 IPs,
  428 class-C, 5,628 follow, 1,896 nofollow, 0 sponsored, 30 UGC, trust 30. The audit's figures are
  the same numbers 5 links earlier. No fabrication.
- **"Confirm with the client whether anyone bought links"** is the right first question and is
  correctly flagged as determining everything downstream.

---

## 2. Claims that are overstated or wrong — with corrections

### 2.1 🔴 The "~4,894 links / 66% spam" figure is not double-counted, but it is wrong anyway

I checked the arithmetic first, since that was the specific concern. **It does not double-count.**
The audit's clusters were built by summing `backlinks_num` across *distinct rows* of the Semrush
`backlinks_anchors` report, and anchor rows in that report are mutually exclusive by exact anchor
string. I reproduced every cluster:

- Cluster 1 (9 "High Quality Dofollow Backlinks DA 50 PA 40…" variants): 128+127+123+119+84+84+82+80+78 = **905** ✓
- Cluster 3 (14 bare sister-domain anchors): 319+303+290+278+277+272+263+261+66+57+51+51+46+46 = **2,580** ≈ 2,579 ✓

So the sum is sound. **The classification is not.** Cluster 3 — 2,579 links, **53% of the entire
claimed spam total** — is a fundamentally different animal from Clusters 1 and 2, and folding it into
one "active PBN blast" number is the audit's central analytical error:

| | Clusters 1+2 (SEO sales copy) | Cluster 3 (bare sister-domain anchors) |
|---|---|---|
| Links | 2,286 | 2,579 |
| First seen | Jun 2026 / Sep 2026 | **Jul 2025, continuous** |
| Source | Networks A + B (purpose-built PBN) | Network C scrapers + blogspot farms |
| Follow status (sampled n=100 each) | **100/100 dofollow** | **34/100 nofollow** |
| Audit's own risk rating of the source | 🔴 Critical | 🟡 Low |

The audit rates Network C as "low risk — Google generally ignores these" in §7, then counts its
output inside the 🔴 Critical "~4,894 spam links" line in §10. **It cannot be both.**

**Correction:** the dangerous, dofollow, recently-injected, purpose-built PBN spam is
**~2,286 links (30.7% of the profile)**, not 4,894 / 66%. The remaining ~2,600 is long-running
scraper bloat that predates the blast by a year and is partly nofollowed.

This also resolves an internal contradiction the audit never noticed: §1 says "almost all of it
landed in the last four months", but §5's own table shows the profile only grew from 5,113 (Jul 2026)
to 7,449 — **+2,336 links**, which matches Clusters 1+2 almost exactly and cannot accommodate 4,894.
The audit's two headline numbers contradict each other.

### 2.2 🔴 "886 referring domains at Authority Score exactly 2" is not diagnostic of anything. Drop it.

The audit calls this "the single most damning chart in the audit" and "the statistical signature of
machine-generated sites spun up from one template by one operator." **This claim does not hold, and
it should be removed rather than softened.** Four reasons:

1. **It is a rounding artifact.** Semrush Authority Score is an integer on a log-compressed 0–100
   scale; the bottom of that scale is where the overwhelming majority of the indexed web lives. For
   the same tier of domain, Ahrefs returns *continuous* values — I pulled DR 0.0, 0.2, 0.3, 0.9, 1.5,
   2.0 for six of these sites. Every one of those would round into Semrush's 0–2 band. A large mass
   at a single low integer is what you get from **any** large set of thin domains, related or not.
2. **The audit's own data refutes it.** §7 describes Network C as "all AS 2–4" — and Network C is
   explicitly a *different operator* from Network A. So at minimum two unrelated operations, plus the
   blogspot farms, plus ordinary web junk, all occupy the AS 0–5 band. One score, many operators.
3. **The arithmetic doesn't fit.** The audit names ~81 domains across Networks A, B and C combined.
   886 is an order of magnitude larger than any single network it was able to identify.
4. **AS isn't a pure link metric.** Semrush AS blends link signals, organic traffic and spam signals.
   A domain registered last month with no traffic has no path to a high score regardless of who
   registered it.

**What to use instead — and it is much stronger.** In my `backlinks` pull, the Network A sites share
**identical URL path slugs including identical numeric IDs** across 40+ distinct registrable domains:

```
/dir/seo-ranking-links-170322          /dir/backlink-seo-experts-211287
/dir/professional-seo-links-148030     /dir/ethical-seo-backlinks-160633
/dir/trusted-seo-backlinks-150104      /dir/quality-authority-backlinks-148096
```

`dacheckertoolonline.site/dir/seo-ranking-links-170322` and
`dapafreechecker.website/dir/seo-ranking-links-170322` and
`linkaudit.space/dir/seo-ranking-links-170322` are the same page on different domains. That is
**deterministic** proof of one operator — a shared database and a shared template — and it is
immune to the "that's just how the metric bins" objection. Rebuild §3's argument on this.

### 2.3 🟠 "Zero rel=sponsored across hundreds of paid placements — exactly what Google penalises"

This is a logic error, not an overstatement. **`rel="sponsored"` can only be set by the linking site.**
The client has no ability to add it to a third party's PBN page, and a spam network will obviously
never add it. Scoring the client for its absence is meaningless, and listing it as a 🟠 Medium risk
in §10 ("Paid links not disclosed") implies client culpability that the audit elsewhere says it has
not established. Also: 0 sponsored tags is the norm across essentially the whole web — the attribute
has very low adoption. Delete this risk row.

### 2.4 🟠 "Authority Score 30 = Trust Score 30 — no trust premium at all"

Semrush Trust Score equalling Authority Score is **extremely common** and is not in itself a signal.
The audit then compounds this by setting "Trust Score rising above Authority Score" as a §9 success
metric — that is an arbitrary target with no basis, and the client will be measured against something
that may never move. Remove it from the KPI list.

### 2.5 🟠 "1,141 IPs across 428 class-C subnets… healthy profiles trend toward 1:1"

Not true. Real link profiles are dominated by shared hosting — Wix, Squarespace, Shopify, GoDaddy,
Cloudflare-fronted ranges — and routinely show far more than 2.9 domains per class-C. 1:1 is not the
healthy baseline; it is close to unachievable. 2.9:1 is unremarkable on its own and should be dropped
to 🟢, or dropped entirely. Likewise "class-C-to-domain ratio approaching 1:1" as a §9 success metric
is unachievable and should be removed.

### 2.6 🟠 "Authority Score drifted down from 33 to 30 — more links, less authority"

AS is a normalised, relative metric that also incorporates traffic and keyword signals, and the whole
scale shifts as Semrush's index grows. A 3-point drift over two years is noise. Presenting it as
causal evidence that "the new links are carrying negative or zero value" is not supportable from this
data. If you want to evidence harm, use Search Console clicks/impressions — which this audit never
looked at.

### 2.7 🟡 Velocity figures are mislabelled

§1 says "Referring domains grew +44% in September 2026 alone (849 → 1,225)". §5's table shows 849 is
the **September** value and 1,225 the **October** value — so the +44% and the +376 are the
**September→October** change, not September's. §5 then labels the same +376 as October. Minor, but it
is the number the client will quote, and it is currently attributed to the wrong month in §1 and §10.

### 2.8 🟡 "Topical relevance is sound… the foundation is fine" (§8) quotes counts without denominators

§8 cites "Doors & Windows (38)" as evidence of a healthy topical base. Against **1,227 referring
domains that is 3.1%**. My `backlinks_categories_profile` pull shows **Arts & Entertainment (62) ties
Home & Garden (62) and beats Doors & Windows (38)**, and the SEO/web-tools neighbourhood —
Internet & Telecom (50) + SEO & Marketing (16) + Web Stats & Analytics (13) + Web Design (13) —
is one of the largest blocs in the profile. The conclusion ("the right neighbourhood, the foundation
is fine") is true of the ~200-domain genuine core but is not what the numbers as presented say. State
the denominator.

### 2.9 🟡 "Most likely a negative SEO attack" is the weaker of the two readings, and it's alarmist

The audit's own §4.3 reasoning defeats it. In a negative-SEO attack on ngwindows.com you would expect
anchors targeting **ngwindows.com**. What the data actually shows is anchors naming *other* window
companies pointing at ngwindows.com, and (per the audit) ngwindows.com used as anchor text pointing
elsewhere. Anchor and target are being drawn independently from the same scraped list. ngwindows.com
is **filler in a vendor's auto-generated inventory**, not a target. That is the third option the audit
raises and then drops in favour of the scarier one. It should be the primary hypothesis, and it
materially lowers urgency: nobody is attacking this client.

### 2.10 🟡 A methodological note the audit should have caught

Semrush's own overview returns follow 5,628 + nofollow 1,896 = **7,524 against a stated total of
7,449**. The buckets are not additive. The audit reported these as 75.6% and 25.5% — summing to
101.1% — without flagging it. That is exactly the kind of non-additivity that should have prompted a
check before building a headline number by summation.

---

## 3. False-positive risk in the draft disavow

The file is **109 domains built from a sample of ~110 of 1,227 referring domains (9%)**, yet §9 item 3
instructs the client to submit it. A sample-based disavow is the worst of both worlds: it carries the
full downside of every false positive while covering a minority of the spam. If a disavow happens at
all, it must come from a full export.

**Confirmed or probable false positives — remove before any submission:**

| Line | Domain | Ahrefs DR | Finding |
|---|---|---|---|
| 109 | `eurekster.com` | **53.0** | **Appears nowhere in the audit body.** An unsourced entry — there is no analysis anywhere supporting it. The actual link is a *deep* link to `/entry-doors` carrying the client's own real page title ("Entry Doors \| North Georgia Replacement Windows"). It is a search-widget aggregator: worthless, but not toxic, and already `lostlink=true`. **Remove.** |
| 108 | `factmags.com` | **75.0** | Classified in §7 as a Network C "auto-generated scraper, AS 2–4". DR 75 is not an auto-generated scraper profile. Either the classification is wrong or the domain is a hijacked legitimate site. **Do not disavow without manual inspection.** |
| §7 only | `csswinner.com` | **75.0** | Listed in §7's Network C disavow list but correctly excluded from the file's active section. **The audit and the file contradict each other.** csswinner.com is a long-running web-design award directory; the links are nomination/listing pages (`/nominees/361`, `/nominees/363`) and are nofollow and already lost. **Keep. Fix §7.** |

**Resolved open questions from the file's "REVIEW MANUALLY" block:**

- `derchidoor.com` (DR 18, 134 links) — **resolved: do not disavow.** This is the single referring
  domain behind `backlinks_pages`' anomalous entry *"/blog/the-benefits-of-casement-windows… — 188
  backlinks, 1 referring domain"*. It is a machine-translated content scraper (anchor text in
  Assamese: *"বায়ুৰ লিকেজ হ্ৰাস কৰে"*), the links are **nofollow**, and they are already
  `lostlink=true`. No action required.
- `atlantahomeimprovement.com` (DR 45) — correctly kept, and now more important than the file
  realises: see §4.3, the link is **lost**.
- `constantcontact.com` — correctly kept.

**Low-FP-risk but zero-upside entries.** `domainanalysis.org` (DR 1.5), `procycling.org` (DR 0.9),
`wallpapers.pro` (DR 2.0) and the rest of Network C are genuinely junk — I am not claiming they are
good links. The objection is different: disavowing them buys nothing (see §5) while every line added
is another chance to catch a `csswinner.com` or an `eurekster.com`. **Network C is where all the
false-positive risk in this file lives and none of the benefit.**

**One systemic risk the file does not state.** Every classification in it rests on **Semrush AS from a
single source**. My spot-checks found AS and DR diverging violently on exactly the disputed entries —
csswinner.com AS 29 / DR 75, factmags.com in an "AS 2–4" bucket / DR 75. Single-source AS is not a
safe criterion for permanently discarding a link.

---

## 4. New findings the audit missed

### 4.1 The spam is ~100% homepage-targeted. The money pages are clean. (Good news, and it's load-bearing.)

`backlinks_pages` was never run. It should have been first.

| Target page | Backlinks | Ref. domains |
|---|---|---|
| `https://www.ngwindows.com/` | 1,604 | 292 |
| `https://ngwindows.com/` (301) | 1,236 | 289 |
| `http://ngwindows.com/` (301) | 1,009 | 172 |
| `http://www.ngwindows.com/` (301) | 34 | 21 |
| **Homepage variants, total** | **~3,883 (52% of profile)** | — |
| `/blog/the-benefits-of-casement-windows…` | 188 | **1** (= derchidoor.com, nofollow, lost) |
| `/contact` | 72 | 5 |
| `/specials` | 70 | 3 |
| every other page | ≤ 38 each | mostly 1–5 |

**Every single Network A and Network B link in my pulls targets a homepage variant.** Not one touched
a service page, a product page, or a service-area page. `/windows` has 7 links from 4 domains;
`/service-areas/replacement-windows-and-doors-roswell-ga` has 3 from 2. The pages that actually earn
revenue are **untouched** by the blast.

Two consequences the audit's risk framing gets wrong:
1. There is **no page-level over-optimisation vector**. The spam is not trying to rank a commercial
   URL for a commercial term; it is dumping homepage links.
2. A large share of it points at `http://` and non-`www` variants that **301 to the canonical** —
   diluting whatever signal it carries before it arrives.

This should move the overall severity down and is the strongest argument against urgent action.

### 4.2 Follow/nofollow split **of the spam specifically** — the two clusters are opposites

The audit only had the sitewide split (75.6% / 25.5%), which tells you nothing about the spam. I
sampled n=100 per cluster:

- **"Premium PBN network service…" sales-copy cluster: 100 / 100 dofollow. Zero nofollow.**
  Networks A and B pass link equity by design. Spot-checks across the newest-links pull agree —
  every `/dir/` link is `nofollow:false`.
- **Bare sister-domain anchor cluster: 34 / 100 nofollow (~34%).**

So the ~2,286-link core PBN is **100% dofollow** — materially worse than the sitewide ratio implied,
and the correct basis for a disavow decision if one is made. The 2,579-link cluster the audit used to
inflate its headline is a third nofollowed and sourced from scrapers. Risk is **concentrated**, not
diffuse: the right response is a surgical ~45-domain action, not a 109-line one.

One addendum: `seonix.agency` — the "fake testimonial" site the audit singles out — is **DR 65**, and
its links are **nofollow**. It is a low-priority target despite being the audit's most quotable find.

### 4.3 🔴 The client is losing genuine links while gaining spam. The audit missed this entirely.

This is the finding I would lead a client conversation with. Sorting `backlinks` by `last_seen_asc`
with the `lostlink` column exposes a clean and ugly pattern: **the links arriving are 100% spam; the
links leaving are disproportionately real.**

Confirmed `lostlink=true`:

| Lost link | DR | Why it mattered |
|---|---|---|
| `gnpmilton.com/c/podcasts/b/ep-37-north-georgia-replacement-windows-with-ted-kirk` | 26 | A **local podcast episode about the client by name, featuring their principal**. Dofollow, hyperlocal, perfectly on-topic. The single best editorial link in the profile. **Gone.** |
| `atlantahomeimprovement.com` | **45** | Local, on-topic, linking since 2023 — the file itself says "almost certainly GENUINE. KEEP". It is already **lost**. |
| `atlantaunitedsoccer.com` | — | Local sponsorship/community link. Lost. |
| `vuink.com/post/…` → `/impact-of-windows-on-home-design` | — | Deep link to a content page. Lost. |
| `csswinner.com` (×4 URLs) | **75** | Award-directory listings. Lost — and simultaneously on the disavow shortlist. |
| `derchidoor.com`, `eurekster.com` | 18 / 53 | Lost. Both on the disavow shortlist. |

**This is a separate and quieter problem than the spam, and arguably a more tractable one.**
Reclaiming the `gnpmilton.com` podcast link and the `atlantahomeimprovement.com` link is a two-email
job with a near-certain success rate, and is worth more to this client than the entire disavow
exercise. Nothing in the audit's 12-point action plan addresses link reclamation. Add it as item 1.

### 4.4 Topical mismatch, quantified properly

`backlinks_categories` (what ngwindows.com *is*) returns high-confidence, tightly clustered:
Locks & Locksmiths 0.945, **Doors & Windows 0.930**, Roofing 0.917, Home Improvement 0.867,
Building Materials 0.858. The site is unambiguously classified correctly.

`backlinks_categories_profile` (what links to it) is where the mismatch shows, and it is **not** the
mismatch the audit described:

- **Doors & Windows: 38 domains = 3.1% of 1,227.**
- **Arts & Entertainment: 62 — more than Doors & Windows, and with no conceivable relationship to
  window replacement.**
- The SEO/web-tools bloc — Internet & Telecom (50), SEO & Marketing (16), Web Stats & Analytics (13),
  Web Design & Development (13) — is ~50+ domains. **A window installer has no organic reason to
  attract a single link from an SEO-tools site.** This bloc *is* Networks A and C, and it is the
  cleanest category-level fingerprint of the spam available.

So the real topical finding is the inverse of the audit's: the client's on-topic link base is **thin
in absolute terms (38 domains)** and is now outnumbered by SEO-tool spam and by Arts & Entertainment
junk. That is the number to show the client — not the reassuring "the foundation is fine".

---

## 5. Independent recommendation: should they disavow at all?

### Short answer: **No — not now.** Do not submit this file.

Google's position on the disavow tool has moved decisively and the audit does not reflect it. Google
Search Central's own documentation states that in most cases Google can assess which links to trust
without additional guidance, and Google's search relations team (Mueller, Illyes) has stated
repeatedly and consistently that the tool exists for **manual actions** and for links **you are
responsible for** — and that for algorithmically-detected link spam, SpamBrain simply ignores the
links and a disavow file changes nothing. Unsolicited spam blasts are the textbook case of what the
tool was explicitly *not* kept around for.

Against that, this audit's §9 orders the actions **backwards**: item 3 is "Submit a disavow file",
item 4 is "Check Search Console for a manual action." That ordering must be reversed. The manual
action check is free, takes ninety seconds, and **determines whether item 3 should happen at all.**

### The decision tree I would give the client

**Step 1 — Check GSC → Security & Manual Actions. This gates everything.**

- **Manual action present ("Unnatural links to your site"):** disavow **immediately**, domain-level,
  **Networks A + B only** (~45 domains), built from a **full** 1,227-domain export, paired with a
  reconsideration request that documents the attempted removals. In this scenario the disavow is
  mandatory and the file's existence is justified.
- **No manual action + client/agency confirms they bought links:** disavow the purchased inventory.
  Not because it will move rankings, but because it is the documented good-faith record you want on
  file if a manual action ever lands later. Stop the spend first.
- **No manual action + nobody bought anything** — which the §4.3 "filler in a vendor's scraped list"
  reading makes the most likely outcome: **do not submit a disavow.** Monitor. Specifically:
  - Baseline GSC clicks/impressions **now** (the audit says this, correctly, and it is its best
    recommendation).
  - If organic performance is flat or rising, there is nothing to fix and a disavow has no mechanism
    by which to help.
  - Revisit only if a manual action appears or if performance degrades in a way that correlates with
    the Sep/Oct link curve.

**Step 2 — if and only if a disavow is submitted, scope it as follows.**

| Scope | Verdict |
|---|---|
| **Network A** (~32 domains, `/dir/` PBN, 100% dofollow, shared path slugs) | **Include.** Deterministically identified, zero FP risk, zero collateral value. |
| **Network B** (~10 domains, fake guest-post) | **Include.** Same reasoning. |
| **Network C** (39 scraper domains) | **Exclude. No.** |
| Blogspot subdomains (3) | Optional, harmless either way. They are nofollow. |
| `eurekster.com`, `factmags.com`, `csswinner.com` | **Exclude.** See §3. |

**On Network C specifically — the downside clearly exceeds the upside.** The upside is explicitly
nil by the audit's own assessment ("Google generally ignores these"); "profile hygiene" is not a
benefit, because Semrush's rendering of the profile is not a ranking input and no one at Google
looks at it. The downside is real and asymmetric: this is where `csswinner.com` (DR 75),
`factmags.com` (DR 75) and `eurekster.com` (DR 53) got swept up — three probable or confirmed errors
in a 39-domain list, an error rate near 8%, in the one section that cannot possibly help. Scraper
links are noise; disavowing noise is itself noise, with a tail risk attached.

### What I would actually do with the client's next ten hours

1. **Check GSC for a manual action.** Ninety seconds. Gates everything above.
2. **Ask the direct question about purchased links.** The audit has this right.
3. **Baseline GSC clicks/impressions/positions**, and chart them against the Sep–Oct link curve. The
   audit asserts harm without ever looking at performance data. Establish whether harm exists before
   treating it.
4. **Reclaim the lost links** (§4.3) — `gnpmilton.com`, `atlantahomeimprovement.com`,
   `atlantaunitedsoccer.com`. Highest expected value per hour of anything in either document.
5. **Monitor new referring domains weekly.** Correct in the audit, keep it.
6. **Hold the disavow file as a prepared, unsubmitted asset**, trimmed to Networks A + B and rebuilt
   from a full export when Ahrefs units reset on 25 Oct. Ready to fire if a manual action lands.

### Corrections to carry back into the audit document

- §4.1: replace "~4,894 (66%)" with **~2,286 dofollow PBN links (30.7%)**, with the scraper cluster
  broken out separately and rated 🟡.
- §3: delete the AS-2 argument; replace with the shared `/dir/` path-slug fingerprint.
- §9: swap items 3 and 4. The manual-action check gates the disavow, not the reverse.
- §10: delete the "Paid links not disclosed" row; downgrade "Subnet clustering" to 🟢; re-rate
  "Active link-spam blast" from 🔴 Critical to 🟠 High on the basis of §4.1 (homepage-only targeting,
  money pages clean, no manual action known).
- §10: **add a new row — "Attrition of genuine editorial links — 🟠 Medium"**, which is currently
  absent and is the one problem here with a guaranteed-positive fix.
