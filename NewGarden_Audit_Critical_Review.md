# New Garden Backlinks Audit — Critical Review

**Reviewed:** 2026-11-03
**File:** `NewGarden_Backlinks_Audit.xlsx` (7 sheets)
**Subject:** New Garden Landscaping & Nursery — newgarden.com
**Method:** Full internal reconciliation of every sheet + live cross-check against Semrush and Ahrefs.

---

## 1. Verdict up front

The workbook is **internally sound and faithfully reflects its source data.** Every
cross-sheet total reconciles to the row, the disavow list is well-formed, and the
spam targeting is conservative (nothing high-authority is being thrown away). It is
safe to proceed **with three caveats**, in order of importance:

1. **Single-source build.** Everything is a Semrush export. Ahrefs sees a materially
   different live profile, and Google (the only view that matters for disavow) is not
   represented at all. Merge Ahrefs + GSC before treating the list as complete.
2. **A real false-negative cluster.** At least 5 directory link-farms are marked
   **Keep** (≈1,217 dofollow links) because the classifier reads anchor text, not
   domain quality. They should be reviewed — they likely belong in the disavow.
3. **The partner-confirmation step has not happened.** All 133 "exact match" rows
   have `Partner confirmed?` and `Final decision` blank. The held bucket can't be
   finalised until that is filled in.

---

## 2. What the workbook contains

| Sheet | Rows | Purpose |
|---|---|---|
| Summary | — | Status buckets, key findings, anchor profile |
| Referring Domain Audit | 2,683 | One row per referring domain, with status + disavow line |
| All Backlinks | 8,086 | One row per backlink, with anchor-type classification |
| Anchor Analysis | 471 | Per-anchor-text rollup |
| Exact Match Anchors | 133 | Held domains awaiting partner sign-off |
| Pending Disavow Lines | 120 | Lines to append *only if* partner does not confirm |
| Disavow List | 1,646 | The actual disavow output (all `domain:` level) |

**Status buckets (domains / backlinks):**

| Status | Domains | Backlinks |
|---|---:|---:|
| Spam (Disavow) | 1,646 | 4,216 |
| Keep | 848 | 3,451 |
| Held (Pending Partner) | 120 | 285 |
| Spam (Nofollow, No Action) | 56 | 105 |
| Held (Nofollow, No Action) | 13 | 29 |
| **Total** | **2,683** | **8,086** |

Total spam = 1,702 domains (1,646 disavowed + 56 nofollow-only). 63.4% of the profile.

---

## 3. Internal consistency — PASS

Every check passed:

- 2,683 referring domains, **zero duplicates**.
- Summary bucket counts **match** the Referring Domain Audit status counts exactly.
- `In Disavow` flag is perfectly aligned with status (Spam→Yes, Keep→No, Held→Held).
- **Disavow List == Spam(Disavow) set, exactly** — 1,646 lines, no duplicates, every
  line well-formed (`domain:…`), none missing.
- **Pending Disavow Lines == Held(Pending Partner) set, exactly** (120).
- All Backlinks status totals (4,216 / 3,451 / 285 / 105 / 29) **match** the Summary.
- No domain carries conflicting statuses across its backlinks; no domain appears in one
  sheet but not the other.
- **Logic holds:** every "No Action (Nofollow)" domain genuinely has 0 dofollow links;
  every Spam(Disavow) domain genuinely has ≥1 dofollow link.
- First-seen dates all plausible (2023-04-11 → 2026-11-03, none in the future).

---

## 4. Live cross-check (critical)

| Metric | Workbook | Semrush (live) | Ahrefs (live) |
|---|---:|---:|---:|
| Backlinks | 8,086 | **8,086** | 3,573 live / 57,167 all-time |
| Referring domains | 2,683 | **2,683** | 1,694 live / 6,478 all-time |
| Dofollow / Nofollow | 7,293 / 793 | **7,293 / 793** | — |

- **Semrush matches the workbook to the digit** — it is a clean, current Semrush export.
- **Ahrefs disagrees by ~1,000 live domains** (1,694 vs 2,683) and shows a far bigger
  historical footprint (6,478 all-time refdomains, 57,167 all-time backlinks). Different
  crawlers see different webs — this is expected, but it means a Semrush-only disavow
  will **miss spam that only Ahrefs or GSC have indexed.**
- **Neither tool is Google.** Google only acts on links it has seen. Before submission,
  reconcile against the **GSC "links to your site" export** — that is the authoritative
  source for both coverage and for whether a manual action even exists.

**Recommendation:** merge the referring-domain lists from Semrush + Ahrefs + GSC, re-run
the same spam rules over the union, and disavow the combined set.

---

## 5. Classification quality

### Strengths
- **TLD targeting is textbook.** The disavow set is dominated by throwaway gTLDs:
  `.shop` (297), `.space` (246), `.website` (237), `.site` (236), `.store` (219),
  `.online` (212); only 115 `.com`. This is a classic PBN/spam-blast fingerprint.
- **Conservative on authority.** Of 1,646 disavowed domains, only **2** have Authority
  Score ≥10 (`jazminsbeautysalon.be` AS18 with a Telegram link-spam anchor; `rosih.ru`
  AS10). Mean AS of the disavow set is 1.8. Essentially no risk of nuking a valuable link.
- **No anchor-based false positives in Keep** — no kept backlink carries a spam anchor type.

### Weakness — false negatives (the main finding)
The classifier is **anchor-text-centric**, so a link-farm that uses a plain naked-URL
anchor ("newgarden.com") instead of keyword-stuffed sales copy slips into **Keep**.
Confirmed examples, all **Keep**, all AS2, all auto-generated business directories
(`/detail/NNNNN/…` pages spanning unrelated services and random US cities):

| Domain | Status | Dofollow links | Reality |
|---|---|---:|---|
| webmash.org | Keep | 373 | Directory farm |
| mysmallbiz.net | Keep | 274 | Directory farm |
| directoryplus.biz | Keep | 270 | Directory farm |
| fixx.co | Keep | 207 | Directory farm |
| powerbizdirectory.com | Keep | 93 | Directory farm |

≈**1,217 dofollow links** across these 5 alone. `1000.co.in` (Keep, 1 link) is even more
blatant — its page title is literally *"Where to buy aged domains and backlinks."*
**These should be manually reviewed and almost certainly moved to disavow (or Held).**
Suggested addendum lines are in Section 7.

### Label noise (cosmetic, not decision-affecting)
- `rosih.ru` — one Russian domain supplying **2,536 dofollow links = 60% of all
  disavowed backlinks** (31% of the entire profile). Its anchor
  "(Ссылка на источник изображения)" = "(image source link)" is mislabelled
  "keyword-stuffed SEO sales copy." The disavow call is right (irrelevant foreign
  image-scraper), but the single-domain concentration is worth knowing.
- `eurekster.com` (Keep, 450 "backlinks") is one defunct search-widget param page
  (`p.eurekster.com/?...`) — syndication junk, not 450 editorial links. Harmless to
  keep, but it inflates the Keep backlink count.

### Judgment calls worth a conscious decision
- **56 Spam(Nofollow) domains are excluded from disavow.** Defensible (nofollow passes
  no value), but disavowing at `domain:` level is free insurance and would also catch any
  link that later flips to dofollow. Cheap to include; your call.
- **Anchor profile "Referring Domains" column double-counts.** The per-anchor-type domain
  figures in the Summary (e.g. geo exact-match = 324) are *sums of per-anchor-text* counts,
  so domains using several anchors are counted more than once. True distinct figures are
  lower (geo exact-match = 235 distinct). Backlink counts are correct; only that one
  column overstates.

---

## 6. Concentration & timing

- **1,478 of the 1,702 spam domains were first seen in October 2026** — a single
  large, recent spam/PBN blast (negative-SEO-style). This is the dominant event in the
  profile and should anchor the GSC manual-action check.
- `rosih.ru` concentration (above): 60% of disavowed backlinks from one domain.

---

## 7. The disavow file

As produced, the Disavow List is **valid and submission-ready in format**: 1,646 unique
`domain:` entries, correctly scoped to whole domains (right choice for link-farm spam).

**Suggested review-and-add before finalising** (false-negative directory farms from §5):

```
domain:webmash.org
domain:mysmallbiz.net
domain:directoryplus.biz
domain:fixx.co
domain:powerbizdirectory.com
domain:1000.co.in
```

Hold the 120 Pending lines until the partner responds (per the workbook's own rule).

---

## 8. Outstanding actions

1. **Fill in partner confirmation** for the 133 exact-match held domains (currently all
   blank). Markets: Winston-Salem 70, Greensboro 51, Non-geo 12. Only after this can the
   held / pending-disavow split be finalised.
2. **Check Google Search Console** for a manual action, and export GSC links — the audit
   itself flags that no manual action is visible in Semrush data (it wouldn't be).
   Disavow is only warranted if GSC shows a manual action or the client confirms buying links.
3. **Merge Ahrefs + GSC sources** and re-run the spam rules over the union (§4).
4. **Review the 5–6 false-negative directory farms** (§5/§7).
5. Decide the nofollow-spam inclusion question (§5).

## 9. Bottom line

Mechanically excellent, faithful to Semrush, and conservatively targeted — a solid
disavow you could defend. The gaps are **coverage** (one tool, no GSC), a **systematic
blind spot** for naked-URL directory farms, and the **unfinished partner sign-off** — none
fatal, all fixable before submission.
