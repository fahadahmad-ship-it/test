# Adversarial verification — disavow-v2-ahrefs.txt, SECTION 6 (SEMRUSH-ONLY)

**Scope:** 117 domains / 147 links, lines 481–597 of `disavow-v2-ahrefs.txt`.
**Verified against:** `git show 6f5f407:backlink-audit/work/links_raw.tsv` (3,499 rows),
`data/refdomains.csv`, `data/ahrefs/ahrefs-refdomains.tsv`, `data/ahrefs/ahrefs-backlinks.tsv`,
Ahrefs free DR API (117 targets, 1 call), WebSearch.
**Date:** 2026-10-06. Disavow file was NOT edited.

---

## 1. How many of the 117 fully verify

**117 of 117. 147 of 147 links. Zero discrepancies.**

Matching rule applied exactly as specified: `(?<![a-z0-9.-])ngwindows\.com`, case-insensitive,
on the anchor column, with `nofollow == false`, restricted to rows whose `source_url` host is
the listed domain or a subdomain of it.

| Check | Result |
|---|---|
| Entries with ≥1 strict-matched dofollow row | **117 / 117** |
| Entries whose stated dofollow count equals the strict count | **117 / 117** |
| Sum of strict dofollow links | **147** (header claims 147 — exact) |
| Entries with no rows at all in `links_raw.tsv` | 0 |
| Entries absent from `refdomains.csv` | 0 |
| Duplicate entries within Section 6 | 0 |
| Duplicates against the other 343 entries in the file | 0 (460 `domain:` lines, 460 unique) |
| Quoted anchor in the comment is a true prefix of a verified anchor | **117 / 117** |

### The `performingwindows.com` trap — handled correctly

The literal string `ngwindows.com` occurs in the file 770 times; **353 of those are the tail of
`performingwindows.com`** and 417 are genuine. Restricted to `nofollow=false` rows the naive count
is 566 and the correct word-boundary count is **250** — a naive match would have inflated the
dofollow evidence by 2.26×.

**No Section 6 entry is a shell-named anchor misread as client-named.** Every one of the 147 rows
survives the lookbehind. 42 of the 117 domains *also* carry `performingwindows.com` rows, but those
rows are on different URLs and are not what the entry is evidenced on — the entry's own cited rows
are clean.

Other near-miss strings checked and excluded correctly: `ngawindows.com` (shell, 50+ rows),
`northgeorgiawindows.net`, `northgawindows.com`, `ngwindow.com` (singular — Group B),
`thermalastwindows.com`. None contaminates Section 6.

---

## 2. The Ahrefs-blindness claim — confirmed

**All 117 are genuinely absent from both Ahrefs files.**

- `ahrefs-refdomains.tsv` (1,357 domains): **0 of 117** present (exact match on normalised host).
- `ahrefs-backlinks.tsv` (2,665 links): **0 of 117** appear as the host, or as a subdomain host,
  of any source URL.

So no Section 6 entry belongs in a stronger section on Ahrefs evidence, and **no entry is
contradicted by Ahrefs evidence**. The section's own caveat — absence of coverage, not exoneration
— is accurate and is the honest framing.

---

## 3. False-positive hunt

### 3.1 DR sweep (all 117, one free call)

DR is reported here **only as a flag for manual review**, not as grounds. 92 of 117 return
DR ≤ 1.0; 80 return exactly 0.0. The non-trivial scores are:

| Band | Domains |
|---|---|
| DR 90+ | `ggmap.us.com` 92, `ggmap.co.com` 91, `daechul.co.com` 91 |
| DR 30–46 | `hotonlinegaming.com` 46, `bestonlinecasinogamescanada.online` 44, `casinopopular.online` 43, `bestirishcasinoonline.online` 42, `bestonlinecasinomexico.online` 42, `casinogamingsites.online` 40, `sidarma88gacor.shop` 40, `casinoonlinecrazytime.online` 39, `bigassstadiumtourmerch.store` 33, `agentbetting.online` 30 |
| DR 5–26 | `gumushaneescorton.shop` 26, `aloysionunes.com` 22, `bazerdaily.com` 13, `fittyfoody.com` 11, `missburrg.com` 11, `cmocheatsheets.com` 9, `onlineshoppingidea.com` 9, `cindylaup.com` 8, `perfectwebseo.com` 7, `seo-expert-1.com` 6 |

**The DR 90+ trio is an artifact, not authority.** `co.com` and `us.com` are commercial
third-level registries; Ahrefs' free DR endpoint is returning the registry's own rating, not the
sub-registrant's. Treat 91/92 as meaningless here. (Harmless for the disavow: `domain:ggmap.co.com`
scopes to that host and its subdomains only, not to `co.com`.)

The DR 30–46 band is entirely gambling/casino spam plus one merch store — high DR from spam
network cross-linking, not editorial.

### 3.2 Manual review of the 28 domains whose *name* could belong to a real business

Pulled the actual `source_url` for every strict-matched row on these. **Every single one is a
link-vendor directory path.** Examples:

- `expresskitchendesigns.com/tiered-link-archive/professional-guest-post-service-…`
- `gladeflowers.com/pbn-directory/effective-white-hat-seo-links-…`
- `daechul.co.com/niche-relevance-hub/powerful-manual-outreach-backlinks-…`
- `coruzants.com/all/2066/26.html`, `marinasone.com/all/2066/26.html`

WebSearch corroboration (live, today):

| Domain | Finding | Verdict |
|---|---|---|
| `expresskitchendesigns.com` | Homepage title is literally **"Boost your Google rankings with Premium PBN & Link Building"** | Not a kitchen company. Ground (d) satisfied live. |
| `daechul.co.com` | Same homepage title, verbatim | Vendor host |
| `ggmap.us.com` | Same homepage title, verbatim | Vendor host |
| `cmocheatsheets.com` | Openly listed for sale as a paid guest-post placement ("do-follow and permanent backlinks") on a broker site | Vendor host |
| `coruzants.com` | **Typosquat of the real `coruzant.com`** tech magazine. `coruzants.com` itself is DR 0 with a `/all/2066/26.html` vendor index. | Not the real publisher. Keep. |
| `marinasone.com` | Generic "Blog Travel & News", registered 2025-03-05, low trust, carries the shared vendor index path | Recycled/parked shell |
| `gladeflowers.com` | A dormant Pinterest gardening presence exists, but the domain is DR 0.1 and serves `/pbn-directory/` | Expired-domain reuse |
| `fittyfoody.com` | Domain registered ~2 months old per third-party scan | Churn-and-burn |
| `breachviews.com`, `missburrg.com`, `onlineshoppingidea.com`, `clifflisting.com`, `fletcherrld.com`, `cindylaup.com`, `rjcentinc.com`, `chordmp3.net`, `techbumppy.com`, `bazerdaily.com`, `aloysionunes.com` | No independent presence; all serve only vendor directory paths | Keep |

**Result: zero confirmed false positives.** No entry is a news site, a genuine directory, a real
business site linking editorially, or a blog with its own audience. The closest calls
(`gladeflowers.com`, `marinasone.com`, `coruzants.com`, `expresskitchendesigns.com`) are all
either lookalikes or repurposed expired domains now wholly serving link-vendor inventory — and in
three of those four the site's *own current homepage title* advertises PBN link selling.

### 3.3 The one residual risk class

If any of these is a *hacked* legitimate site rather than a repurposed one, a `domain:` directive
disavows the whole host rather than the injected directory. That is over-broad in principle.
In practice it is costless: none of the 117 is a link the client would want to keep, and a
disavow has no punitive effect on the referring site.

---

## 4. Distinct-anchor breakdown

Only **three** distinct anchor strings account for all 147 dofollow links across the 117 domains.
All three are unambiguous link-vendor sales copy. None could be an ordinary editorial mention —
each one is an advertisement *for backlink services*, with the client's domain interpolated as the
product being sold.

| Domains | Links | Anchor (verbatim) |
|---|---|---|
| **76** | 96 | `Increase Google Visibility with High Quality Backlinks ngwindows.com` |
| **24** | 27 | `High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service ngwindows.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap` |
| **19** | 24 | `Trusted High DA Backlinks for ngwindows.com to Raise Domain Rating. Improve Google Rankings, Across Every Niche and Market.` |

(76 + 24 + 19 = 119 > 117 because `ggmap.co.com` and `ggmap.us.com` each carry two of the three.)

Anchors #1 and #2 are byte-identical to the anchors already cited as grounds for **Section 1**
(campaign 148096) and **Section 2** (the PBN cluster) respectively, both of which Ahrefs
independently confirms. Section 6 is the Semrush-visible tail of clusters Ahrefs has already
corroborated at their core — the generator is the same, only the hosts are new.

**Nofollow rows naming ngwindows.com on these 117 hosts: 0.** There is no mixed-attribution
ambiguity; every named row on every one of these hosts is dofollow.

---

## 5. The strategic question — routing, and whether to submit now

### 5.1 New evidence that substantially resolves the routing doubt

The brief states that routing rests on anchor text alone. That is true of the *column set*, but
two structural facts in the same export narrow it much further.

**(a) 76 of the 117 carry the client's own campaign ID in the URL path.**
Splitting Section 6 by the path of its cited rows:

| Tier | Domains | Evidence beyond the anchor |
|---|---|---|
| **A** | **76** (96 links) | Path is `/dir/quality-authority-backlinks-148096` — campaign **148096**, which `REDIRECT-TEST-RESULTS.md` establishes is the one campaign aimed at **ngwindows.com directly**, not at any Group-A redirect shell. |
| **B** | **16** (24 links) | Path is the shared vendor index `/all/2066/26.html` or `/all/947/16.html`, replicated byte-identically across unrelated hosts (ground (c)). |
| **C** | **25** (27 links) | Unique per-host vendor path; anchor text only. |

For Tier A the routing inference does not depend on the anchor at all. The campaign ID is a
structural fingerprint that the redirect test already tied to ngwindows.com, 8/8 and 6/6 with no
exceptions. These 76 are as well-evidenced as Section 1.

**(b) Every vendor page is single-target.**
Of the 125 distinct source URLs in Section 6 that carry a strict `ngwindows.com` anchor, **125 of
125 name ngwindows.com and no other target domain anywhere on the page.** Not one page mixes
ngwindows.com with `performingwindows.com`, `ngawindows.com`, `roiwindows.com` or any other shell.
The same 117 hosts *do* serve pages for the other seven shells — but always on separate URLs with
separate paths. The vendor's generator emits one page per (host × target) pair.

That closes the main failure mode. The worry behind "routing is inferred" is that a dofollow link
sitting on a page whose copy names ngwindows.com might actually point at a shell. On a page whose
entire generated copy names exactly one target, and where the vendor demonstrably builds a
separate page when the target is a shell, there is no mechanism by which that would happen.

### 5.2 The case for waiting until 2026-10-25

- `target_url` is genuinely absent. Everything above is inference, however tight, and on
  2026-10-25 Ahrefs Site Explorer returns and the question can be answered rather than argued.
- A disavow filed against ngwindows.com has **no effect whatsoever** on links aimed at the Group-A
  shells — those pass equity through a 301 and are only neutralisable from the shell's own
  property (which the client does not control). So every Tier-C entry that is actually shell-aimed
  is a line that does nothing.
- Ahrefs has never crawled these 117, so there is no second opinion on whether the links are even
  still live. The Semrush export's last-seen dates are the only liveness signal.
- The file's own header says **"DO NOT UPLOAD until reconciled"**. Section 6 is 25% of the entries
  and 100% of the single-sourced ones; submitting it is the one decision that cannot be
  reconciled later with better data.

### 5.3 The case for submitting now

- **The cost of a wrong inclusion here is close to zero, and asymmetric.** A disavow line against a
  domain whose link actually aimed at a shell is simply inert — it does not harm the client, does
  not harm the site, and is removable. A disavow line against a *genuine* link would be costly, but
  §3 found none: all 117 are vendor inventory, three of them advertising link selling in their own
  live homepage title.
- **The evidence standard here is the same one Sections 1–2 already clear.** The anchors are
  byte-identical to anchors Ahrefs independently confirms elsewhere. Section 6 is not a weaker
  *kind* of evidence, it is the same evidence from a tool with different crawl coverage.
- **Tier A is not actually single-sourced in the way the label implies.** 76 of 117 carry campaign
  148096 in the path — corroborated by the redirect test, which is independent of both Semrush and
  Ahrefs.
- Waiting 19 days means 19 more days of the client's profile carrying 147 dofollow PBN links.
  Against an active, still-running vendor campaign, that is not a free option.

### 5.4 Recommendation — **submit a subset now (Tiers A + B, 92 domains / 120 links); hold Tier C (25 domains / 27 links) until 25 October**

**Submit now — Tier A (76 domains).** Campaign ID `148096` in the path is structural evidence tying
these to ngwindows.com directly, independent of the anchor and independent of Semrush. Routing is
not inferred for these; it is fingerprinted. They meet the file's own grounds (a)+(b)+(c).

**Submit now — Tier B (16 domains).** The byte-identical `/all/2066/26.html` and `/all/947/16.html`
paths across unrelated hosts are ground (c) on their own terms, and the single-target finding in
§5.1(b) applies. Evidence is one notch below Tier A but clearly above anchor-alone.

**Hold Tier C (25 domains).** These rest on anchor text and nothing else: a unique vendor path per
host, no shared campaign ID, no cross-host fingerprint, no Ahrefs record. The single-target finding
makes them *probably* client-aimed, but "probably" is exactly the standard the brief says to
default against. They are also the least urgent: 27 links, and the band is dominated by churn
gambling domains (`casinopopular.online`, `hotonlinegaming.com`, `sidarma88gacor.shop`, the
`.shop` cluster) that are likely to be deindexed or dead by 25 October anyway. Nineteen days buys a
definitive `target_url` for all of them at zero cost.

**On 2026-10-25**, when Site Explorer returns: re-query the 25 Tier-C domains plus all 117 for
`target_url`, and file a supplementary disavow. If `target_url` confirms Tier C, add it; if it
shows shell routing, the entries were correctly withheld and the inference method itself gets a
validation check that should be applied back to Tiers A and B.

**Do not submit all 117 as a block, and do not withhold all 117.** The section is not uniform —
it bundles 76 entries with campaign-ID corroboration together with 25 that have none, under a
single "weakest tier" label that undersells the former and oversells the latter.

### 5.5 One thing that should be said in the covering note

A disavow filed for ngwindows.com cannot reach the ~2,587 anchor rows aimed at the seven Group-A
redirect shells, which continue to pass equity through live 301s. Submitting Section 6 — or the
whole 460-line file — addresses only campaign 148096. The shell exposure is a separate remediation
track (shell takedown, or redirect removal) and no disavow file will substitute for it.

---

## Appendix — entries to REMOVE

**From the file on evidence grounds: none.** All 117 verify at the stated standard.

**Deferred to the 25 October pass (Tier C, 25 domains, anchor-only routing):**

```
adcreativevideo.com                   agentbetting.online
bazerdaily.com                        bestirishcasinoonline.online
bestonlinecasinogamescanada.online    bestonlinecasinomexico.online
bigassstadiumtourmerch.store          burpio.shop
casinogamingsites.online              casinoonlinecrazytime.online
casinopopular.online                  chordmp3.net
cindylaup.com                         cmocheatsheets.com
daechul.co.com                        drobo.shop
expresskitchendesigns.com             fioro.shop
fittyfoody.com                        gumushaneescorton.shop
mertio.shop                           ninko.shop
plendo.shop                           rjcentinc.com
sidarma88gacor.shop
```

This is a sequencing decision, not a finding of error. Every one of the 25 verifies against
`links_raw.tsv` exactly as the file claims.
