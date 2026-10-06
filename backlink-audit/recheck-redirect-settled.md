# Recheck: the redirect-attribution question, settled

**Date:** 2026-10-06
**Question:** Does the link-spam campaign point at ngwindows.com, or at 14 content-free
domains that 301-redirect into it?
**Status:** **Resolved in favour of reading (A)** — on evidence materially stronger than
the anchor-text inference it replaces. The operational recommendation that reading (A)
originally carried ("delete the redirects") is **still rejected**, for reasons set out in §4.

---

## 0. The one-paragraph answer

Ahrefs and Semrush both crawled 45 of the same Network A `/dir/` throwaway domains. On those
45 domains — where crawler coverage is *controlled by construction, because both tools
demonstrably fetched the host* — Semrush credits ngwindows.com with links from **eight**
vendor campaigns, only 17.2% of them the client's own. Ahrefs credits ngwindows.com with links
from **one** campaign, the client's own, **45 out of 45 domains, 100.0%**. The vendor stamps a
distinct campaign ID into every URL path and the campaign ID predicts the anchor brand with
**zero exceptions in 1,011 rows**. The only mechanism that produces this split is targeting:
the seven non-client campaigns do not point at ngwindows.com, and Semrush is following the 301
and crediting the client. Reading (B), crawler coverage, is not merely unsupported here — it is
excluded, because the coverage confound has been removed.

---

## 1. What the Ahrefs data **proves**

### 1.1 The four preliminary findings — all verified independently

| Claim | Verdict | Evidence |
|---|---|---|
| Zero of 2,665 rows have an anchor naming any of the 14 shells | **Confirmed** | Boundary-correct regex over all 36 fields. 1,908 rows name `ngwindows.com`; **0** name any shell |
| Zero have a shell in the redirect chain; all Target URLs are ngwindows.com | **Confirmed** | 2,665/2,665 Target URLs on ngwindows.com, across 90 distinct URLs |
| Chains present: ngwindows.com (833 hops), atlantabestmedia.com (22), bizhwy.com (5) | **Confirmed** | 812 rows carry a chain; 27 involve a third-party host |
| 297 of 351 `/dir/` domains absent from Ahrefs | **Directionally right, numbers restated** | Using the full `/dir/` set: 501 Semrush domains, 258 Ahrefs domains, 45 overlap. Ahrefs *also* sees **213 `/dir/` domains Semrush never saw** |

### 1.2 Ahrefs' redirect pipeline demonstrably works — so silence here is meaningful

This is the precondition for the whole argument and it is proven, not assumed. The export
contains 27 rows where a **third-party** domain sits in the redirect chain and Ahrefs
nonetheless credits ngwindows.com as Target URL:

```
atlantabestmedia.com/?post_id=12205&goto=EV0EC01... (303) -> http://ngwindows.com/ (301) -> https://ngwindows.com/
  Target URL: https://www.ngwindows.com/     Anchor: ngwindows.com
```

Ahrefs resolves multi-hop chains (`303, 301, 301`), through third-party hosts, and attributes
the link to the final destination. **If a shell-mediated spam link had been crawled, it would
appear in this export with the shell in `Redirect Chain URLs`** — exactly as atlantabestmedia.com
does. Zero do. This converts "Ahrefs doesn't show shells" from an absence into a constraint:
either the shell links were never crawled, or they do not resolve to ngwindows.com.

### 1.3 The vendor's campaign ID is a per-target key — 100% pure over 1,011 rows

Network A's URL template is `<throwaway-domain>/dir/<campaign-slug>-<id>`. Partitioning the
1,011 Semrush `/dir/` rows by that ID gives a **perfect** partition by anchor brand:

| Campaign slug + ID | Rows | Anchor brand | Purity |
|---|---|---|---|
| `professional-seo-links-148030` | 181 | ngawindows.com | 100% |
| `backlink-seo-experts-211287` | 156 | thermalprowindows.com | 100% |
| `seo-ranking-links-170322` | 148 | qualitypluswindows.com | 100% |
| `ethical-seo-backlinks-160633` | 147 | **performingwindows.com** | 100% |
| `trusted-seo-backlinks-150104` | 138 | northpointwindows.com | 100% |
| **`quality-authority-backlinks-148096`** | **112** | **ngwindows.com — the client** | **100%** |
| `authority-focused-backlinks-178285` | 88 | roiwindows.com | 100% |
| `manual-link-building-services-211290` | 41 | thermatrustwindows.com | 100% |

Not one row crosses. The campaign ID is a target key, and **one** of the eight keys is the
client's. 112 of 1,011 `/dir/` rows (11.1%) are the client's own campaign.

> **Correction to the prior audit.** `anchor-and-attribution-forensics.md:115-120` maps
> `160633` to the client. It belongs to **performingwindows.com**. The cause is a substring
> trap: `"performingwindows.com"` **contains** the literal string `"ngwindows.com"`
> (perfor-mi-**ngwindows.com**). Any `in`-style match counts it as a client mention. Across
> the Semrush corpus this inflates client-anchor rows from a true **385** to an apparent
> **762** — a **98% overstatement**, with 49.5% of apparent client mentions being
> performingwindows.com. Every anchor count in the existing documents that used substring
> matching needs re-deriving with a boundary-anchored pattern.

### 1.4 The controlled comparison — the coverage confound eliminated

Restrict to the **45 `/dir/` domains both tools crawled**. Ahrefs fetched these hosts; there is
no question of coverage.

| | Semrush, same 45 domains | Ahrefs, same 45 domains |
|---|---|---|
| `/dir/` links credited to ngwindows.com | 93 | 90 |
| ngawindows | 26 (28.0%) | 0 |
| performingwindows | 20 (21.5%) | 0 |
| **client (148096)** | **16 (17.2%)** | **90 (100.0%)** |
| qualitypluswindows | 11 (11.8%) | 0 |
| thermalprowindows | 7 (7.5%) | 0 |
| northpointwindows | 6 (6.5%) | 0 |
| thermatrustwindows | 4 (4.3%) | 0 |
| roiwindows | 3 (3.2%) | 0 |

Across the **entire** Ahrefs export there are 516 `/dir/` rows on 258 domains. **All 516 carry
campaign ID `148096`.** All 516 carry the single anchor
`"Increase Google Visibility with High Quality Backlinks ngwindows.com"`. All dofollow, all
flagged `Is spam = true`.

Under reading (B) — every campaign's href is ngwindows.com, Ahrefs just sampled fewer pages —
Ahrefs' crawl of these hosts should return the client campaign at roughly its population rate
of 17.2%. It returns it at 100%. Counting **domains** as the independent unit (the 90 rows are
45 domains × http/https target variants, so rows are not independent):

- p = 0.172^45 ≈ **4 × 10⁻³⁵**.
- Even assuming severe clustering and discounting to an *effective* 10 independent draws:
  p ≈ 0.172¹⁰ ≈ **2 × 10⁻⁸**.

Reading (B) does not survive at any defensible discount.

**And the sharpest form of it:** of those 45 overlap domains, **34 show no client campaign at
all in Semrush** — Semrush saw only shell-campaign pages there. Ahrefs reports a client-campaign
`/dir/` page on **every one of the 34**. Both tools crawled the same host, each found pages the
other missed, and the split falls exactly along the campaign-ID line rather than randomly.
Partial page coverage is real in both tools; it is **not** what separates what they report.

### 1.5 The DR-0 challenge — answered, and it does not refute (A)

The brief asks whether DR 0 on all 14 shells is consistent with them receiving thousands of
links. **It is**, and the control proves it. The 516 `/dir/` throwaway domains that Ahrefs has
indexed, and which demonstrably sit inside this network sending and receiving links, measure:

```
DR of the 516 /dir/ referring domains: min 0.0, max 0.6, mean 0.01, median 0.0  (514 of 516 round to 0)
```

Free-endpoint spot checks: `dapacheckerfree.site` 0.0, `multipledapachecker.store` 0.0,
`bulkdrcheckerfree.website` 0.0, `24rankings.link` 0.1, `backlinkschecker.site` 0.5 — against
`ngwindows.com` 27.0 and `atlantabestmedia.com` 46.0.

DR is a log-scaled function of dofollow referring domains **weighted by the linkers' own DR**.
A domain receiving ~300 links exclusively from DR-0.0 sources is expected to measure ~0. DR 0 on
the shells is therefore the predicted observation under **both** readings and carries almost no
likelihood ratio. The intuition in the brief — "shouldn't they have substantial profiles?" —
assumes link *count* drives DR; in a population where every source is DR 0, it does not.

This is a case where the sceptical argument, properly calibrated, dissolves. It should not be
cited either way.

### 1.6 Incidental findings

- **A 15th domain variant: `ngwind.com`** (DR 0.0), surfaced in scraper-page sidebars. Not
  previously on any list. Ownership unverified.
- **The 53 `ngwindow.com` mentions are an artefact, not evidence.** They occur only in
  `Left context` on alphabetised expired-domain listicles
  (`"ngwind.com ngwindow.com [ngwindows.com] ngwindsong.com ngwindsongk.com"`). Alphabetical
  neighbours, not links. Anyone grepping for shells will hit these; they mean nothing.
- **A live client-side bug.** 72 backlinks point at
  `https://www.ngwindows.com/%3Futm_source%3Dgoogle%26utm_medium%3Dorganic%26utm_campaign%3Dgbp`
  — the client's own Google Business Profile URL with `?` and `&` percent-encoded, so the query
  string is parsed as a path. It 301s to the homepage, so equity is largely preserved, but the
  GBP link is malformed at source and should be fixed. Unrelated to this question; worth a ticket.
- **Spam is homepage-only; the overall profile is not.** Of 1,938 spam-flagged rows, 1,860 hit
  `/` and 72 hit the malformed homepage URL — **99.7% homepage** once the encoding artefact is
  folded in. Non-spam rows are 79.0% homepage. The earlier "~100% homepage" claim is correct
  **for the spam specifically**, which is the claim that matters; it was being tested against
  whole-profile figures.

---

## 2. What the data only **suggests**

Scoping discipline matters here, because this is where the previous over-claim happened.

1. **The proof covers Network A `/dir/` links. It does not directly cover the whole profile.**
   §1.4 is airtight for the `/dir/` network. Extension to the remaining spam rests on an
   anchor-brand tally, which is weaker evidence of the same kind that was over-read before.
   Boundary-corrected, Semrush's 3,500 sampled rows name: roiwindows 410, qualityplus 399,
   **client 385**, northpoint 355, ngawindows 354, performingwindows 350, thermalpro 349,
   thermatrust 197, northgeorgiawindows.net 173, and a tail — **client = 12.1% of the 3,178
   brand-naming rows**. That the `/dir/` subset independently yields 11.1% client by campaign ID
   is a strong consistency check, but the two measures are not independent evidence of the
   non-`/dir/` spam's targeting.

2. **The "~94% / 4,815 links" magnitude is plausible but not established to the same standard.**
   The mechanism is proven; the exact share is an extrapolation from a 46.4%-complete Semrush
   pull. Treat 88–94% as a range, not a figure, and do not put it in a client deliverable as a
   point estimate.

3. **The 297 (properly: 456) missing `/dir/` domains prove nothing on their own.** Both readings
   predict their absence — (A) because they target shells, (B) because Ahrefs didn't crawl them.
   The likelihood ratio is ~1. **This was the weakest item in the preliminary findings and it
   should be dropped from the argument entirely.** Ahrefs independently sees 213 `/dir/` domains
   Semrush misses, which shows both tools' coverage is patchy in both directions. The 45-domain
   overlap carries the entire inferential load, and it is sufficient.

4. **Shell ownership is inferred, not documented.** The one-campaign-per-domain structure and the
   301s into ngwindows.com strongly imply a common buyer, and `justgotlive.com/es/site/
   qualitypluswindows.com` renders with the title *"Energy-Efficient Windows & Doors | NG Windows"* —
   a third-party scraper resolving the shell to client content, which independently confirms the
   redirect is live. None of that is a registration record.

5. **Nothing here establishes what Google does.** Ahrefs' and Semrush's attribution rules are
   their own. Google's handling of a 301 from a content-free domain is a separate question on
   which this dataset is silent. See §5.

---

## 3. Probability for (A) vs (B)

**P(A) ≈ 0.95 for the mechanism, over the Network A `/dir/` network.**
**P(A) ≈ 0.85 for the mechanism generalising to the bulk of the spam profile.**
**P(the "~94% of 4,815 links" magnitude being accurate to ±5pp) ≈ 0.6.**

Reasoning, explicitly:

**Driving P(A) up:**
- The controlled 45-domain comparison (§1.4) removes the coverage confound rather than arguing
  around it. p ≈ 4×10⁻³⁵ at face value, ≈2×10⁻⁸ under severe clustering discount.
- 34 domains where Semrush saw only shell campaigns and Ahrefs saw only the client campaign —
  the complementary pattern a targeting split predicts and a coverage story does not.
- 516/516 Ahrefs `/dir/` rows on one campaign ID with one anchor string. Not a tendency; a
  constant.
- The campaign ID → brand mapping is 100% pure across 1,011 rows and 8 campaigns.
- Ahrefs' redirect machinery is proven live in this very export (§1.2), so its silence on shells
  is informative rather than vacuous.

**Holding P(A) below ~0.97:**
- A residual mechanism survives: the vendor could resolve the buyer's 301 at page-build time,
  writing `href=ngwindows.com` while keeping the ordered brand in the anchor. That would produce
  shell-named anchors on genuinely client-targeted links. It is defeated by §1.4 — under it,
  Ahrefs would see *all* eight campaigns pointing at ngwindows.com, and it sees one — but it is
  not defeated by anchor evidence alone, and it is why the anchor-only argument was correctly
  withdrawn.
- Ahrefs' `/dir/` rows all first-seen 17–29 Sep 2026. Semrush's `/dir/` domains first-seen Sep
  (130) / Oct (369). The windows overlap and the 45 shared domains are concurrently live in
  both, so a "different wave" explanation is largely excluded — but Ahrefs' snapshot is
  narrower, and I cannot fully rule out that the September cohort was disproportionately client
  campaign. This is the strongest surviving objection and it is a modest one.

**Holding the generalisation at 0.85:** the non-`/dir/` spam (fake guest posts, PBN sales-copy
pages) has not had the campaign-ID test applied, because those networks do not stamp an ID into
the path. Its targeting is inferred from anchors and from belonging to the same blast.

**Why not higher, given how clean §1.4 is.** The statistic is clean; the inference chain is not
single-link. It depends on the campaign ID genuinely being a target key (very well evidenced,
but inferred from the data it explains), on Semrush's `/dir/` sample being representative of
the campaign mix, and on Ahrefs' September snapshot not being cohort-skewed. Each is likely;
their conjunction is not 0.99. The previous 85% was asserted on anchor text alone; this 95% is
asserted on a controlled comparison with a stated p-value **and** a named surviving objection.
Those are different epistemic objects even where the numbers are close.

---

## 4. Can "delete the redirects" now be recommended?

**No. Do not delete the redirects.** The finding that justified the proposal is now confirmed,
and it argues *against* the action rather than for it. Specifically:

1. **It would not remove a single spam link.** If the links target the shells, the links continue
   to exist and continue to point at the shells. Deleting the 301s converts them into links to
   dead domains. Nothing is disavowed, nothing is cleaned.

2. **It severs the one thing of value.** These are brand-variant and legacy domains. Whatever
   legitimate historical equity and type-in traffic they carry flows through those 301s. The
   proposal destroys the real asset and leaves the liability untouched — the exact inversion of
   what was intended.

3. **The premise of urgency is now weaker, not stronger.** The reason the deletion looked urgent
   was that ~4,815 spam links appeared to be reaching ngwindows.com. The evidence says the major
   third-party index that *can* see redirect chains does not attribute them to ngwindows.com at
   all. The exposure being defended against may be substantially a reporting artefact in Semrush.

4. **Disavow is the correct instrument, and its scoping changes.** Google's disavow file is
   per-property. Links pointing at shell domains are not addressed by a disavow filed on
   ngwindows.com. If the shells are client-owned and the risk is judged real, they must be
   verified as separate GSC properties and disavowed there. If they are not client-owned, there
   is no action available and probably no exposure. **Establishing ownership of the 15 domains is
   now the top-priority action item** — it determines whether there is anything to do at all.

5. **What to do on ngwindows.com itself.** Only the client's own campaign `148096` is evidenced
   as pointing at ngwindows.com: 258 referring domains in Ahrefs, 516 links, all dofollow, all
   spam-flagged, all aimed at the homepage. That is the real, verified, directly-attributable
   exposure — and it is an order of magnitude smaller than the headline figure. Disavow those
   258 domains at `domain:` level on ngwindows.com. That recommendation is supported by both
   tools and by the redirect column, and it is safe.

6. **Note the direction of the correction.** This recheck does not shrink the problem to nothing;
   it relocates it. The client's own property has a real, smaller, cleanly-identified spam
   problem. The larger number was mostly other people's domains — or the client's own shells,
   which is a different remediation with a different owner.

---

## 5. What still cannot be answered

Blocked until the Semrush unit reset (**25 Oct 2026**) or an unrestricted machine:

1. **Direct per-link `target_url` / `redirect_url` from Semrush.** The single clean confirmation.
   Everything above is an inference from which links each tool reports; this would show the href
   itself. **First pull on reset**, filtered to shell-brand anchors.

2. **Ahrefs Site Explorer on the 14+1 shells.** The decisive test, and it is cheap: pull
   `site-explorer-all-backlinks` or `backlinks-stats` for `thermalprowindows.com`. Under (A) it
   should show a `/dir/` campaign `211287` profile of roughly 150+ links from DR-0 throwaways.
   Under (B) it should show nothing. The free DR endpoint cannot distinguish these, because
   §1.5 shows DR 0 is the predicted value under both. **This is the highest-value single query
   available and it resolves the residual 5% directly.** Site Explorer is dead until reset.

3. **Whether Google follows these 301s and attributes the links.** Not answerable from any
   third-party index. Requires GSC link data for ngwindows.com — which is free, available now,
   and nobody in this audit has pulled it. **It should be pulled before any disavow is filed.**
   If the Network A domains are absent from GSC's referring-domain list, the case for action
   collapses further.

4. **Registration/ownership of the 15 variant domains.** WHOIS, registrar records, or simply
   asking the client. Per §4.4 this gates the entire remediation decision and needs no API units.

5. **The ~4,048 Semrush links never retrieved (53.6%).** The campaign-ID test can be run over
   them once pulled, which would move the §3 generalisation figure from 0.85 toward the 0.95 the
   `/dir/` subset supports. Budget first: 500-row pages cost ~48,000 units.

6. **Whether Ahrefs' September `/dir/` snapshot is cohort-skewed** (§3, the surviving objection).
   Needs `site-explorer-refdomains-history` on ngwindows.com, or a second Ahrefs pull after the
   October cohort is indexed.

---

## Reproduction

All figures derive from `data/ahrefs/ahrefs-backlinks.tsv`, `data/ahrefs/ahrefs-refdomains.tsv`,
`data/refdomains.csv`, and `git show 6f5f407:backlink-audit/work/links_raw.tsv`. The controlled
comparison in §1.4 is the load-bearing analysis: join the two corpora on referring **domain**,
restrict to domains appearing in both with a `/dir/` path, extract `/dir/<slug>-(\d+)` as the
campaign key, and cross-tabulate. Use boundary-anchored anchor matching
(`(?<![a-z0-9.-])ngwindows\.com`) — plain substring matching is wrong by a factor of two (§1.3).
