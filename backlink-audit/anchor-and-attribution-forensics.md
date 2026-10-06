# Anchor-Text & Attribution Forensics — ngwindows.com

**Analysis date:** 6 October 2026
**Target:** ngwindows.com (North Georgia Replacement Windows / "NG Windows", Alpharetta GA)
**Primary source:** Semrush Backlink Analytics — full anchor list paginated to exhaustion
(503 anchors, 3 pages, `backlinks_anchors` sorted `domains_num_desc`), plus `backlinks`
(link-level, with `redirect_url` and `nofollow`), `backlinks_pages`, `backlinks_overview`,
`backlinks_historical`.
**Secondary source:** Ahrefs free public Domain Rating endpoint.

> **Constraint on this analysis.** Ahrefs Site Explorer was not queried (units exhausted to
> 25 Oct 2026). Separately, **outbound HTTP to ngwindows.com and to all 14 sister domains was
> blocked by this environment's egress proxy**, and `whois` is not installed. So every statement
> below about redirects and site content is inferred from **Semrush's crawl data**, not from a
> first-hand HTTP request. See §7 for exactly what that leaves unverified.
>
> **The Semrush API unit balance was exhausted during the §6A link-level pull** (500-row
> `backlinks` pages cost ~48,000 units each). §6A therefore rests on 878 of the 1,225 referring
> domains, with authority measured by Ahrefs DR rather than Semrush Authority Score; its limits
> are set out in §6A.1. Everything in §1–§6 was completed before the balance ran out and is
> unaffected.

---

## 1. Verdict

> ### The spam is not aimed at ngwindows.com. It is aimed at **14 content-free domains that 301-redirect into ngwindows.com** — and it arrives at the client through those redirects.
>
> **Attribution: a purchased / managed link campaign run on behalf of the ngwindows.com
> property — not a negative SEO attack, and not a vendor blasting a scraped list.**
>
> **Confidence: high (~85%).** The main residual doubt is registrant identity, which could not
> be checked from this environment (§7).

This reverses the working hypothesis in the existing draft audit
(`ngwindows-backlink-audit.md` §4.3), which read the sister-domain anchors as evidence of a
scraped list. The `redirect_url` field — not surfaced in that draft — shows the opposite.

---

## 2. The finding that settles it

### 2.1 The anchors are not anchors *about* other companies. They are the *link targets*.

Pulling `backlinks` at link level, filtered by anchor, exposes a column the anchor report hides:

| source_url (spam page) | target_url | **redirect_url** | anchor | nofollow |
|---|---|---|---|---|
| `seoanalysischecker.website/dir/backlink-seo-experts-211287` | `https://www.ngwindows.com/` | **`https://thermalprowindows.com/`** | Professional thermalprowindows.com SEO Backlinks… | false |
| `backlinkautomationtool.store/dir/authority-focused-backlinks-178285` | `https://ngwindows.com/` | **`https://roiwindows.com/`** | Premium Backlinks to Strengthen SEO Authority and Rankings roiwindows.com | false |
| `theface.in/page-7929cf…html` | `http://ngwindows.com/` | **`http://e2windows.com/`** | e2windows.com | false |

The spam page's `href` is **roiwindows.com** (or thermalprowindows.com, or e2windows.com).
Semrush follows the 301 and credits the link to **ngwindows.com**.

That is why the anchor text is a "competitor" domain name: **the anchor is simply the URL the
vendor was given.** There is no mystery and no third party. The vendor was handed a target list,
and that list is these 14 domains.

### 2.2 All 14 sister domains are content-free 301 shells

`backlinks_pages` for each domain returns **nothing but redirect responses** — no indexed content,
no title, zero outbound links, zero internal links:

| Domain | Pages Semrush has ever seen | Response | external / internal links | Ahrefs DR |
|---|---|---|---|---|
| roiwindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| thermalprowindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| ngawindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| qualitypluswindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| northpointwindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| performingwindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| thermatrustwindows.com | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| northgeorgiawindows.net | `https://` + `http://` root only | **301 / 301** | 0 / 0 | 0 |
| thermalastwindows.com | `http://` root only | **301** | 0 / 0 | 0 |
| e2windows.com | `http://` root only | **301** | 0 / 0 | 0 |
| choiceviewwindows.com | `http://` root only | **301** | 0 / 0 | 0 |
| ngwindow.com | `http://` root only | **301** | 0 / 0 | 0 |
| northgawindows.com | `http://` root only | **301** | 0 / 0 | 0 |
| northgeorgiawindow.com | `https://` (uncrawlable) + `http://` root | **301** | 0 / 0 | 0 |
| **ngwindows.com** | **full site**, 25+ indexed pages | **200**, title *"Energy-Efficient Windows & Doors \| NG Windows"* | 12 / 92 on homepage | **27** |

**Not one of these is a real window company.** None has a homepage, a phone number, a service
page, or a single outbound link. They are DNS entries and a redirect rule. The "14 unrelated
window businesses on a scraped list" reading is dead: there are no businesses.

**Redirect direction is unambiguous.** ngwindows.com serves a 200 homepage with 92 internal
links and a real title; the 14 serve nothing but 301s with zero links; and queried from
ngwindows.com's side, Semrush records them as the *redirect hop*, with ngwindows.com as the
*destination*. A live 60-page business site does not redirect its homepage to 14 shells
simultaneously.

### 2.3 These domains have no history. They were built for this.

`backlinks_historical` for three of them, Nov 2024 → Oct 2026 (referring domains):

| Month | ngawindows.com | thermalprowindows.com | northgeorgiawindows.net |
|---|---|---|---|
| Nov 2024 | 7 | 6 | 3 |
| Dec 2024 | 9 | 10 | 4 |
| Feb 2025 | 17 | 15 | 17 |
| Jun 2025 | 56 | 53 | 59 |
| Dec 2025 | 92 | 95 | 96 |
| Jun 2026 | 121 | 120 | 130 |
| Aug 2026 | 270 | 235 | 225 |
| **Oct 2026** | **385** | **337** | **235** |

Three separate domains, three near-identical curves, all at Authority Score 2 the whole way,
all starting from ~0 in late 2024. **They are not expired authority domains that were bought —
they have no pre-existing equity at all.** They were registered or re-pointed around late 2024
and fed by one vendor on one schedule ever since.

### 2.4 The vendor assigns a campaign ID per target — and ngwindows.com has one

Network A's URL template is `<throwaway-domain>/dir/<campaign-slug>-<id>`. The id is constant
per *target*, and varies only across targets:

| Campaign ID | Target fed into it |
|---|---|
| `/dir/backlink-seo-experts-**211287**` | thermalprowindows.com |
| `/dir/authority-focused-backlinks-**178285**` | roiwindows.com |
| `/dir/quality-authority-backlinks-**148096**` | **ngwindows.com (direct, no redirect)** |

Hundreds of distinct throwaway domains (`seoanalysischecker.website`, `padacheckertools.shop`,
`trustflowchecker.space`, `dacheckeronline.store`, `onlinewebsitechecker.space`,
`seostrengthchecker.online`, …) each serve the *same* campaign-ID page. One operator, one
page-generation system, one order per target.

**ngwindows.com is itself order #148096.** The anchors
*"Increase Google Visibility with High Quality Backlinks ngwindows.com"* (102 ref domains) and
*"Trusted High DA Backlinks for ngwindows.com"* (46 ref domains) resolve with an **empty
`redirect_url`** — direct hits on the client domain, from the same network, through the same
ordering system, in the same week as the redirect-domain orders.

### 2.5 The negative evidence is as strong as the positive

If this were a vendor blasting a scraped list of Atlanta window companies, the anchor set would
contain window-company domains that have *nothing to do with* ngwindows.com.

**Across all 503 anchors, there are exactly zero.** Every single third-party domain named in an
anchor is either (a) one of the 14 that redirect to ngwindows.com, or (b) the vendor's own
self-promotion (`itxoft.com`, `sitetosocial.com`, the two Telegram handles). A scraped list
cannot produce that. The probability that an indiscriminate blast happens to hit 14 domains that
*all* funnel into one small Georgia contractor, and no others, is negligible.

---

## 3. Attribution: the three hypotheses, scored

| Hypothesis | Supporting evidence | Contradicting evidence | Assessment |
|---|---|---|---|
| **A. Purchased / managed campaign on the client's behalf** (client, prior agency, freelancer, or an SEO who had DNS control) | 14 shells that *all* 301 to one target; the list grows ~monthly in a managed cadence (§4); lockstep growth curves; a per-target vendor order ID for ngwindows.com itself; 5 of the 14 are obvious defensive typo-variants of the real brand (`ngwindow.com`, `northgawindows.com`, `northgeorgiawindow.com`, `ngawindows.com`, `northgeorgiawindows.net`) — the kind of registration only the brand owner makes; **zero** unrelated window domains anywhere in the anchor set | Nothing in the data contradicts it. Registrant identity unverified (§7) | **~85% — the working conclusion** |
| **B. Negative SEO attack delivered via attacker-owned 301s** | 301-redirect negative SEO is a real, documented vector; an attacker *could* register lookalikes and point them at the victim | An attacker wanting to hurt ngwindows.com would blast ngwindows.com — it is 94% cheaper per link than maintaining 14 redirect domains for two years. The spend here (14 domain registrations + 24 months of renewals + a sustained vendor retainer) is grossly disproportionate to the payoff. And an attacker has no reason to register the client's *own* brand typos and hand them back as redirects. Growth is a steady managed ramp, not a burst | **~12%** |
| **C. Vendor blasting a scraped list** | Was the draft audit's reading; anchor text does rotate "other" window domains | Refuted. The "other companies" are not companies — they are the client's own redirect shells (§2.2), and no genuinely unrelated window domain appears anywhere in 503 anchors (§2.5) | **~3% — effectively ruled out** |

**The remediation strategy differs completely between A and B, but — usefully — the first and most
important action is identical in both cases: kill the redirects.** That makes the open registrant
question non-blocking.

---

## 4. Timeline: when each redirect domain started feeding ngwindows.com

First date Semrush saw a link whose anchor names each domain and whose target resolves to
ngwindows.com:

| First seen | Domain |
|---|---|
| Jul 2025 | northgeorgiawindows.net |
| Aug 2025 | thermalprowindows.com |
| Sep 2025 | thermatrustwindows.com |
| Oct 2025 | roiwindows.com · ngawindows.com |
| Nov 2025 | performingwindows.com |
| Dec 2025 | qualitypluswindows.com · northpointwindows.com |
| Feb 2026 | thermalastwindows.com |
| Mar 2026 | e2windows.com |
| Apr 2026 | choiceviewwindows.com · ngwindow.com · northgawindows.com |
| May 2026 | northgeorgiawindow.com |
| **Jun 2026** | **ngwindows.com itself** — first direct PBN anchor (`High Quality Dofollow Backlinks DA 50 PA 40 … ngwindows.com …`), matching the 29 Jun 2026 escalation date in the draft audit |
| **Sep 2026** | Second direct wave on ngwindows.com (`Increase Google Visibility…`, `Trusted High DA Backlinks for ngwindows.com`) + volume ramp across all 14 |

**Observation:** a new redirect domain is folded in roughly every 4–8 weeks for 12 months, then in
June 2026 the client domain is added to the rotation directly. **Inference:** this is an actively
managed programme with someone adding inventory, not a one-off event. It is still running —
links were landing within hours of this pull (latest `last_seen` 6 Oct 2026).

---

## 5. Which pages absorb it, and how

### 5.1 Target pages (`backlinks_pages`)

| Target page | Response | Backlinks | Ref. domains |
|---|---|---|---|
| `https://www.ngwindows.com/` | 200 | **1,604** | 292 |
| `https://ngwindows.com/` | 301 → www | **1,236** | 289 |
| `http://ngwindows.com/` | 301 → www | **1,009** | 172 |
| `http://www.ngwindows.com/` | 301 → https | 34 | 21 |
| every other page (blog, service areas, /contact, /specials) | 200 | ≤ 72 each | ≤ 9 each |

**100% of the spam lands on the homepage.** Not one deep page, service-area page or blog post is
targeted. Two consequences: (a) the money pages and the local service-area pages are clean, and
(b) all of the risk is concentrated on the single most important URL on the site.

### 5.2 Follow status

The vendor spam is **dofollow** (`nofollow: false`) almost without exception across every sample
pulled — Network A's `/dir/` pages, the fake-guest-post network, and the PBN sales-copy pages.
The only `nofollow: true` links in the spam are the low-risk scraper farms
(`anchorurl.cloud`, `blinks.sbs`, `knows.sbs`, blogspot). These links are actively attempting to
pass PageRank, and **zero** carry `rel="sponsored"`.

---

## 6. Anchor-text distribution

### 6.1 Method and basis

All 503 anchors were pulled. `backlinks_num` is used as the arithmetic basis because it is
additive and sums exactly to the 7,444 total (each link has exactly one anchor); `domains_num`
double-counts domains that use several anchors (it sums to 3,432 across the 87 multi-domain
anchors alone). The 87 anchors used by ≥2 referring domains cover **6,336 of 7,444 links (85.1%)**
and are classified **exactly**. The remaining **1,108 links** sit in ~416 single-referring-domain
anchors and are classified **by pattern inspection** — those figures carry roughly **±3pp**.
Measured and estimated figures are marked throughout.

### 6.2 Full profile — including the spam

| Bucket | Ref. domains | Backlinks | % of 7,444 | Basis |
|---|---|---|---|---|
| **Third-party-domain-name — bare redirect-domain anchors** (`roiwindows.com`, `performingwindows.com`, `ngawindows.com`, `https://roiwindows.com/` …) | 1,049 | **2,757** | **37.0%** | measured |
| **SPAM-vendor copy naming a redirect domain** (`High Quality Dofollow Backlinks DA 50 PA 40 … roiwindows.com …`, `Professional thermalprowindows.com SEO Backlinks…`, 26 rotating templates) | 1,701 | **2,058** | **27.6%** | measured |
| **SPAM-vendor copy naming ngwindows.com directly** + Telegram handles | 243 | **263** | **3.5%** | measured |
| Spam in the long tail (`itxoft.com links for northgeorgiawindows.net`, `visit performingwindows.com for latest info`, fake testimonials, `quality contextual backlinks`) | ~15 | ~20 | ~0.3% | estimated |
| **— TOTAL SPAM —** | — | **~5,098** | **~68.5%** | — |

> **Refinement from §6A.** Counting all 2,757 bare-sister-domain links as "spam" is too blunt.
> At link level that bucket is **52% dofollow / 48% nofollow**, and the nofollow half is
> stats-farm scraping (`knows.sbs`, `takes.sbs`, `seol.store`, `blinks.monster`) that indexed the
> shell domains — background noise, not an attack. It is also a *separate and earlier* event:
> the bare-domain cluster first appears Jul 2025, a year before the PBN blast of 29 Jun 2026.
> The two should not be conflated. Either way these links are removed at source by cutting the
> redirects, so the remediation is unchanged; but "68.5% spam" overstates the *hostile* share.
> The dofollow vendor-sales-copy campaign — ~2,321 links, buckets (a)+(c) above — is the part
> that is unambiguously manipulative.
| Naked URL (ngwindows.com in all casings/paths) | ~258 | ~789 | 10.6% | mostly measured |
| Page-title / editorial-context anchors | — | ~378 | 5.1% | estimated |
| Generic CTA / navigational (`read more`, `contact us now`, `visit website`, `\|`, bare digits) | — | ~370 | 5.0% | mostly measured |
| Empty / image / logo | 31 | ~281 | 3.8% | measured |
| Branded (`north georgia replacement windows`, `ng windows`) | ~51 | ~120 | 1.6% | mostly measured |
| Machine-translated fragments (one multilingual scraper, ~90 languages of *"reduces air leakage"*) | ~90 | ~95 | 1.3% | estimated |
| Partial-match commercial | ~40 | ~92 | 1.2% | estimated |
| Client's own newsletter promo copy (`constantcontact.com` archive) | ~2 | ~90 | 1.2% | estimated |
| **Exact-match commercial** | **~50** | **~75** | **1.0%** | mostly measured |
| Image-search scraper anchors (`photos of…`, `pictures of…`) | — | ~45 | 0.6% | estimated |
| Misc / nonsense | — | ~11 | 0.1% | estimated |

### 6.3 The clean profile — spam excluded (**this is the number that matters**)

Clean base = 7,444 − ~5,098 = **~2,346 links** across roughly **375 referring domains**.

| Bucket | Backlinks | **% of clean profile** | Healthy? |
|---|---|---|---|
| **Naked URL** | ~789 | **33.6%** | ⚠️ High, but normal for a citation/directory-heavy local contractor |
| Page-title / editorial context | ~378 | **16.1%** | ✅ Genuine editorial mentions |
| **Generic** (CTA, navigational, punctuation) | ~370 | **15.8%** | ✅ Healthy |
| Empty / image / logo | ~281 | **12.0%** | ✅ Normal |
| **Branded** | ~120 | **5.1%** | 🟠 **Too low — see below** |
| Machine-translated fragments | ~95 | 4.0% | 🟡 Scraper noise, harmless |
| **Partial-match commercial** | ~92 | **3.9%** | ✅ Healthy |
| Own-newsletter promo copy | ~90 | 3.8% | 🟡 Self-generated, neutral |
| **Exact-match commercial** | ~75 | **3.2%** | ✅ Well within safe limits |
| Image-search scraper anchors | ~45 | 1.9% | 🟡 Harmless |
| Misc / nonsense | ~11 | 0.5% | — |

**Consolidated clean mix:**

| | Share of clean profile |
|---|---|
| Branded + naked URL + generic + empty | **66.5%** |
| Editorial / page-title / promo / translated / scraper noise | **25.8%** |
| **Commercial anchors of any kind (exact + partial)** | **7.1%** |
| — of which **exact-match** | **3.2%** |

### 6.4 Reading of the clean mix

**There is no anchor over-optimisation problem, and there never was.** At **3.2% exact-match**
(~50 referring domains) the profile sits far below the ~10–15% band where exact-match anchor
ratios start drawing algorithmic attention. The commercial anchors that do exist are the right
ones and are naturally distributed across geos — `window replacement company atlanta` (5 domains),
`windows atlanta` (5), `vinyl windows atlanta` (4), `replacement windows` (7),
`window replacement atlanta` (2), `window companies atlanta ga` (2), plus singletons for
Johns Creek, Marietta, Roswell, Savannah and Alpharetta. That is what an organically-earned local
contractor profile looks like.

**The one real weakness is the opposite of over-optimisation: branded anchors are too thin.**
At ~5.1% of the clean profile (~51 referring domains), brand mentions are dwarfed by naked URLs
at 33.6%. A healthy local-service profile runs **40–55% branded**. The business also appears to be
mid-rebrand — "North Georgia Replacement Windows" → "NG Windows" — and the anchor data shows the
split (`north georgia replacement windows` 31 domains vs. `ng windows` 11). Link acquisition
should deliberately push brand-name anchors in the new form.

**Caveat on the naked-URL share:** a meaningful slice of those ~789 links comes from auto-generated
domain-stats scraper farms (Network C in the draft audit), not from genuine citations. The *real*
naked-URL share from legitimate directories and citations is lower, and the branded deficit
correspondingly starker.

---

## 6A. The low-authority band: what are those anchors actually saying?

Requested follow-up. The client does not want anything disavowed merely for being low-authority —
correctly. So the question is what the ~1,011 Authority-Score-0–5 referring domains are *doing*.

### 6A.1 Method, and its limits

Link-level data was pulled with `backlinks` sorted `page_authority_score_asc`, which front-loads
the low-authority band. **2,532 unique links across 878 distinct referring domains** were
retrieved and classified. Each domain was assigned its *dominant* anchor bucket.

Authority was then measured with the **Ahrefs free DR endpoint** on a stratified random sample of
**206 of those 878 domains** (~45 per bucket), and the per-bucket DR 0–5 rate extrapolated to the
full 878.

Four honest caveats, all of which widen the error bars:

1. **Coverage is 878 of 1,225 referring domains (72%).** Pagination stopped early because
   **the Semrush API unit balance hit zero** during this pull (500-row link pages cost ~48,000
   units each). Two pages also failed on a malformed row. The missing ~347 domains are, by the
   sort order, weighted toward *higher* authority — so the low-authority band is better covered
   than 72%, but coverage is not complete and the exact figure is unknown.
2. **The authority metric is substituted.** The band was defined by Semrush Authority Score;
   I measured **Ahrefs DR** because Semrush units were gone. DR 0–5 and AS 0–5 are conceptually
   equivalent but not identical, and the two tools disagree on individual domains.
3. **Per-bucket DR rates come from samples of 12–44 domains.** Bucket (e) in particular rests on
   12 usable observations. Treat its figure as indicative only.
4. **Hosted subdomains were excluded from the DR calculation.** The free endpoint returns the
   *platform root* DR for `*.blogspot.com` (95), `*.wordpress.com` (96) and `*.pages.dev` (93).
   Those are artifacts, not site authority — and many of those subdomains
   (`glassreplacementkaev.blogspot.com`, `carwindowreplacementznali.blogspot.com`,
   `fiberglassdoorpantai.blogspot.com` …) are auto-generated spam blogs.

### 6A.2 Anchor buckets across the 878 sampled referring domains, by follow status

Link-level, all 2,532 classified links:

| Bucket | Links | Dofollow | Nofollow | % dofollow |
|---|---|---|---|---|
| **(a) Vendor sales-copy** (`High Quality Dofollow Backlinks DA 50 PA 40…`, `Premium White Hat SEO Links for…`, Telegram handles) | **1,342** | **1,320** | 22 | **98%** |
| **(b) Bare sister-domain name** (`roiwindows.com`, `performingwindows.com`, `https://thermalprowindows.com/`) | 753 | 391 | 362 | **52%** |
| **(c) Naked URL / brand** (`ngwindows.com`, `www.ngwindows.com`, `north georgia replacement windows`) | 239 | 91 | 148 | 38% |
| **(d) Empty / image / generic** (`<EmptyAnchor>`, `visit website`, `read more`) | 102 | 64 | 38 | 63% |
| **(e) Genuinely topical** (`replacement windows`, `window replacement atlanta`, `windows and doors`) | 81 | 50 | 31 | 62% |
| (f) Other / unclassifiable | 15 | 14 | 1 | 93% |

This **confirms the red-team pass's separation of the two events.** Bucket (a) is 98% dofollow —
a deliberate PageRank-passing campaign. Bucket (b) is 52% dofollow / 48% nofollow, a mixed
population consistent with stats-farm scrapers (`knows.sbs`, `takes.sbs`, `seol.store`,
`blinks.monster` — all nofollow) sitting alongside dofollow directory spam. They are not the same
operation and should not be conflated.

### 6A.3 Cross-cut by authority (DR sample, hosted subdomains excluded)

| Bucket | Domains (of 878) | DR sampled | of which DR 0–5 | DR 0–5 rate | Est. DR 0–5 domains |
|---|---|---|---|---|---|
| **(a) Vendor sales-copy** | 633 | 44 | 42 | **95%** | **~604** |
| (b) Bare sister-domain | 100 | 38 | 25 | 66% | ~66 |
| (c) Naked URL / brand | 74 | 33 | 7 | **21%** | ~16 |
| (d) Empty / generic | 34 | 32 | 18 | 56% | ~19 |
| (e) Topical | 33 | 12 | 5 | 42% | ~14 |
| (f) Other | 4 | 3 | 2 | — | ~3 |
| | | | | | **~721** |

### 6A.4 Answer: the low-authority band is **not** mostly benign

> **Estimated composition of the low-authority band (~721 domains in the sampled 878):**
>
> | | Share |
> |---|---|
> | **(a) Vendor sales-copy — manipulative on its face, 98% dofollow** | **~84%** |
> | (b) Bare sister-domain name | ~9% |
> | (d) Empty / generic | ~3% |
> | (c) Naked URL / brand | ~2% |
> | (e) Genuinely topical | ~2% |
> | **Benign buckets (b)+(c)+(d)+(e) combined** | **~16%** |

**This does not support the working suspicion, and I am reporting it as measured.** The hypothesis
was that the AS 0–5 band would be mostly (b)+(c)+(d) background noise with a minority of (a).
The data says the reverse by a wide margin: roughly **five out of six low-authority referring
domains are carrying explicit link-vendor sales copy on a dofollow link.** That is the defining
characteristic of the band, not an edge case within it.

The reason is structural: the June–October 2026 blast added ~640 referring domains in two months
(draft audit §5), and essentially all of them are Network A `/dir/` template sites. They swamp the
pre-existing low-authority population. The benign low-authority domains the client rightly wants
protected do exist — there are roughly **115 of them in the sample** — but they are now a minority
of the band.

### 6A.5 The finding that matters more: **neither test alone is safe**

The strategic premise — *don't disavow on authority, disavow on behaviour* — is right. But the
data shows the anchor-behaviour test has serious false negatives in **both** directions:

**False negatives (spam that looks benign).** Bucket (c) — "naked URL / brand", the bucket the
client most wants left alone — contains a cluster of **high-DR commercial link sellers** linking
with an innocuous bare `ngwindows.com` anchor:

`allbaclinks.com` (DR 60) · `atozbacklinks.com` (DR 60) · `bestsitesbacklinks.com` (DR 60) ·
`booastrankingwithbacklinks.com` (DR 60) · `friendlybacklinksbuy.com` (DR 60) ·
`increasewebtrafficwithlinks.com` (DR 60) · `99backlinksbuy.com` (DR 59) ·
`bestrankbacklinks.com` (DR 59) · `buytopqualitybacklinks.com` (DR 59) ·
`best-seo-domains.com` (DR 59) · `backlinks-checker.com` (DR 42)

A rule of "benign anchor → leave alone" lets all of these through. A rule of "low authority →
disavow" *also* lets them through, because they are DR 59–60.

**False positives (legitimate sites that look disposable).** Conversely, buckets (c), (d) and (e)
contain genuinely good links that an authority-threshold sweep would destroy:

`castbox.fm` (DR 87) · `barbend.com` (DR 75) · `brightside.me` (DR 75) · `csswinner.com` (DR 75) ·
`moneytalksnews.com` (DR 74) · `bizhwy.com` (DR 71) · `members.williamsonchamber.com` (DR 49) ·
`disgustingmen.com` (DR 46) · `atlantahomeimprovement.com` (DR 45) · `nerdymamma.com` (DR 45) ·
`contractorsnearme.ai` (DR 44) · `roswell365.com` (DR 39) · `jeffslist.com` (DR 38) ·
`acraftedpassion.com` (DR 34) · `disunplugged.com` (DR 34) · `houseandhomeonline.com` (DR 32) ·
`atlantaglow.org` (DR 30)

— plus real low-DR local sites that are perfectly legitimate and must be kept:
`forsythcounty.com` (DR 3.6), `georgiashutters.com` (DR 2.2), `alpharettatoprated.com` (DR 10),
`chattanoogatoprated.com` (DR 10), `windowdigest.com` (DR 15), `homerenoworld.com` (DR 16),
`athomepros.com` (DR 18), `fairviewwindows.co.uk` (DR 20), `koalatyremodel.com` (DR 27),
`gnpmilton.com` (DR 26), `lombardohomegroup.com` (DR 13), `thehomefixitpage.com` (DR 13),
`crowdyhome.com` (DR 12), `1stcallglasscare.com` (DR 3).

**Conclusion: build the disavow on domain character — what the site is — using anchor behaviour as
the primary screen and authority as no more than a tiebreaker.** The clean decision rule the data
supports:

| Signal | Action |
|---|---|
| Vendor sales-copy anchor (bucket a), dofollow | **Disavow.** ~604 domains, 95% of them DR 0–5, zero legitimate sites found in the sample |
| Domain name is itself a link-selling brand (`*backlinks*`, `*seo*`, `*dachecker*`, `*rankchecker*`) **regardless of anchor or DR** | **Disavow.** Catches the DR 59–60 vendors bucket (a) misses |
| Bare sister-domain anchor (bucket b) | **Do not disavow — remove the redirect instead.** These disappear at source (§8, Action 1) |
| Naked URL / brand / generic / topical anchor from a site that is a real publisher, directory, chamber or local business | **Leave alone**, at any DR. ~115 such domains in the low-authority band alone |

### 6A.6 Does this shrink the remediation scope?

**Yes — but through the redirects, not through the low-authority band.** The band is mostly
genuine spam, so a behaviour-based disavow there is still large. What shrinks the scope is §8
Action 1: ~94% of the spam arrives through the 14 redirects, and the redirect-borne bucket (b)
population never needs disavowing at all. The two findings are complementary, not alternatives.

---

## 7. What is NOT established — stated plainly

Being explicit about the limits of this analysis:

1. **Registrant identity is unverified.** Outbound HTTP to all 15 domains was blocked by this
   environment's egress proxy and `whois` is unavailable. We have **not** confirmed who owns the
   14 redirect domains. The attribution verdict rests on behavioural and structural evidence
   (§2, §3), not on a registration record. **This is the single highest-value next check and it
   takes five minutes:** run WHOIS / a historical-WHOIS lookup on all 14 and compare registrant,
   registrar, creation date and nameservers against ngwindows.com. If they share a registrar
   account or nameserver set with ngwindows.com, confidence in Hypothesis A goes to ~99%.
2. **The redirects are inferred from Semrush's crawler, not observed first-hand.** The evidence is
   strong and internally consistent (301 response codes, `redirect_url` values, zero content on
   14 domains, a live 200 site on the fifteenth), but a direct `curl -I` on each domain should be
   run to confirm the destination and the status code.
3. **Long-tail anchor buckets are estimates.** 85.1% of links are classified exactly; the ~1,108
   single-domain-anchor links are bucketed by inspection, ±3pp. The strategic conclusions
   (exact-match is low, branded is too thin) hold comfortably across that band.
4. **The Ahrefs cross-check is still outstanding.** DR 0 on all 14 redirect domains is consistent
   with Ahrefs collapsing them into the redirect target, but Ahrefs' own link graph may attribute
   these links differently from Semrush's. Re-run after 25 Oct 2026 before finalising any disavow.
5. **Whether Google is currently following these 301s is unknown.** Google may already be
   discounting them. This does not change the recommended action — the redirects carry no upside
   and unbounded downside.

---

## 8. Remediation — reprioritised

The draft audit's plan led with a disavow file. **That is now the second action, not the first.**

### Action 1 — Remove the 14 redirects. This is the whole ballgame.

Spam reaching ngwindows.com **via a 301** = buckets in §6.2 rows 1–2 = **~4,815 links**.
Spam hitting ngwindows.com **directly** = **~283 links**.

> **94.4% of the entire spam problem is delivered through 14 DNS/redirect records the operator
> controls. Deleting them — or returning 410/404 — severs ~4,815 toxic links instantly, with no
> disavow file, no reconsideration request, and no waiting on Google.**

For each of `ngawindows.com`, `thermalprowindows.com`, `qualitypluswindows.com`, `roiwindows.com`,
`northpointwindows.com`, `performingwindows.com`, `thermatrustwindows.com`,
`northgeorgiawindows.net`, `thermalastwindows.com`, `e2windows.com`, `choiceviewwindows.com`,
`ngwindow.com`, `northgawindows.com`, `northgeorgiawindow.com`: **drop the redirect to
ngwindows.com.** Do not simply let them expire — an expiring domain gets re-registered and the
redirect can be re-pointed by someone else. Keep the defensive typo-variants registered
(`ngwindow.com`, `northgawindows.com`, `northgeorgiawindow.com`, `ngawindows.com`,
`northgeorgiawindows.net`) but park them on a holding page, not a redirect into the money site.

Before deleting, **record everything**: WHOIS, DNS, current redirect target, and a screenshot of
each domain's Semrush/Ahrefs profile. If this turns out to be Hypothesis B, that is the evidence
file for a Google reconsideration request or legal action.

### Action 2 — Establish who set this up

Put the question to the client directly, and name the domains. The single most informative thing
you can ask: *"Do you own, or have you ever owned, these fourteen domains, and who has access to
your DNS?"* The answer resolves Hypothesis A vs. B in one sentence. If the client has no idea what
these domains are, escalate immediately — that is a live negative SEO incident and a possible DNS
compromise.

### Action 3 — Disavow on domain character, not on authority

Once the redirects are gone, the residual direct problem is the Network A
`/dir/quality-authority-backlinks-148096` campaign and the Telegram-handle links that point
straight at ngwindows.com. Disavow at **domain level**, using the §6A.5 decision rule:

- **Disavow** any domain whose dominant anchor is vendor sales-copy on a dofollow link
  (bucket a — 95% of these are DR 0–5, and no legitimate site appeared among 44 sampled).
- **Also disavow** domains whose *name* is a link-selling brand (`*backlinks*`, `*seo*`,
  `*dachecker*`, `*rankchecker*`) **even at DR 59–60** — §6A.5 lists eleven that a benign-anchor
  rule or a low-authority rule would both miss.
- **Do not disavow** bucket (b) bare-sister-domain links. They vanish when the redirects go.
- **Do not disavow on low authority alone.** ~115 legitimate domains in the sampled
  low-authority band — local chambers, directories, real publishers and small contractors —
  would be destroyed by an authority threshold. §6A.5 names them.

The Network C scraper farms are optional hygiene and carry no urgency.

### Action 4 — Rebuild branded anchors

The clean profile's real defect (§6.4) is a branded share of ~5% against a naked-URL share of
~34%. New link acquisition should target **40–55% branded**, favouring the current trading name
"NG Windows", and should leave exact-match commercial anchors alone entirely — at 3.2% they are
already in good shape and there is no upside in pushing them.

### Action 5 — Monitor

New referring domains were still landing hourly on the audit date. After the redirects are cut,
re-pull `backlinks_overview` weekly for 8 weeks. Expected signature of success: referring domains
fall back toward the ~400–600 pre-campaign baseline, the AS 0–5 band collapses, and Trust Score
rises above Authority Score. If referring domains keep climbing *after* the redirects are
removed, the attack is direct and ongoing — revisit Hypothesis B.

---

## 9. Corrections to the existing draft audit

`ngwindows-backlink-audit.md` should be amended on three points:

| Section | Current claim | Correction |
|---|---|---|
| §1 Verdict, §4.3, §10 | The sister-domain anchors indicate "a vendor blasting a scraped list of window companies" and ngwindows.com "is one name on that list, not necessarily the buyer" | Refuted. The 14 are not window companies — they are content-free 301 shells pointing at ngwindows.com. The spam reaches the client *through* them |
| §10 Risk table | "Possible negative SEO attack — 🔴 Critical — anchors naming 14 other DR-0 window-company domains" | Downgrade to 🟠 Medium pending WHOIS. The named domains are not "other companies"; the redirect architecture points to a managed campaign |
| §9 Action plan | Leads with "submit a disavow file" | Reorder: removing the 14 redirects eliminates ~94% of the spam and must come first. Disavow handles the ~6% remainder |

The draft's §2, §3, §5, §6, §7 and §8 (metrics, AS distribution, velocity, geography, named
networks, asset list) are unaffected and remain accurate.
