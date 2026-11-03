# Backlink Disavow Assessment — collinspoolmanagement.com

**Prepared:** 2026-11-03
**Target:** https://collinspoolmanagement.com/
**Input:** Tab 08 — 76 flagged referring domains (two footprints)
**Deliverables:** `disavow.txt` (annotated), `disavow-clean.txt` (minimal), this memo

> **STATUS: DRAFT — NOT SUBMITTED.** The file must be signed off by **Harbinger**
> (whole file) and by **the partner who commissioned the directory/bookmark links**
> (Section 2) *before* it is uploaded to Google Search Console. I have prepared the
> file only; I have not submitted it and cannot contact those approvers from here.

---

## 1. What was asked

Assess the 76 referring domains in Tab 08 against the wider referring-domain profile,
produce the disavow file, and confirm with Harbinger and the commissioning partner
before submission.

## 2. Method / tools used

The 76 domains were cross-checked against the live profile rather than taken on trust:

- **Ahrefs** Site Explorer — backlink stats, and a targeted referring-domains pull for
  all 76 domains (mode=subdomains, history=all_time): Domain Rating, first-seen,
  last-seen, spam flag, link counts.
- **Semrush** Backlink Analytics — backlinks overview (referring-domain total).

## 3. Verification findings (read these before submitting)

**3a. The "592-domain profile" figure does not reconcile with either live tool.**

| Source | Referring domains |
|---|---|
| Task description ("wider 592-domain profile") | 592 |
| Ahrefs | 1,054 live / 1,702 all-time |
| Semrush | 2,003 |

The 592 count matches neither Ahrefs nor Semrush. It most likely comes from a different
source (e.g. a Google Search Console "top linking sites" export, or a dated snapshot).
**Action for reviewers:** confirm which source Tab 08 was built from so the 76/592
ratio is being read correctly; the live third-party picture is a much larger profile.

**3b. Only 29 of the 76 flagged domains are present in Ahrefs' index; 47 are not.**

This is expected for brand-new throwaway spam domains and does not change the disavow
recommendation (disavow is preventative and covers links Google may see even when a
third-party crawler has not indexed them yet). It is listed here as a data point, not a
reason to drop any domain. The 47 not in Ahrefs are annotated as such in `disavow.txt`.

**3c. First-seen dates in Ahrefs diverge from Tab 08, materially for Section 2.**

Examples (Tab 08 → Ahrefs):
- `atozbookmarks.net`: 2026-01-17 → **2024-12-11**
- `instabookmarking.com`: 2026-01-14 → **2025-05-31**
- `articles4all.org`: 2026-01-07 → **2025-07-07**

Several directory/bookmark links are older in Ahrefs than Tab 08 states (by up to a
year). The spam-network dates are closer (within days/weeks). This reinforces that
Tab 08's "first seen" column is from a different data source than Ahrefs.

**3d. Of the 29 Ahrefs-known domains, 23 carry Ahrefs' `is_spam` flag; 6 do not**
(`atozbookmarks.net`, `instabookmarking.com`, `articles4all.org`, `bookmarkingbuddy.com`,
`bookmarkhaven.com`, `ideailluminator.com` — all Section 2 directory/bookmark sites,
all DR ≤ 0.5). Low DR + exact-match commercial anchors still make them valid disavow
candidates; they are simply not auto-flagged as spam.

**3e. Three Section 1 domains have inflated Domain Rating** — `betulcrime.com` (DR 40),
`onlyhealthydeals.com` (DR 27), `homesforsaleoldgreenwichct.com` (DR 23) — consistent
with hijacked/expired domains repurposed for a PBN. Correctly in scope.

## 4. Assessment & recommendation

**Section 1 — Spam / PBN link-selling network (43 domains).** Unambiguous link spam:
boilerplate link-selling anchors ("High Quality Dofollow Backlinks DA 50 PA 40 Premium
PBN Network Service …" and "Professional Link Building Services Helping …"), first seen
Jul–Sep 2026, unsolicited. **Recommend: disavow at domain level.** No partner sign-off
needed beyond Harbinger — these were never commissioned.

**Section 2 — Directory / bookmark / article listings (33 domains).** Exact-match
commercial anchors ("Commercial Pool Services Atlanta GA", "Lifeguard Certification
Atlanta GA", etc.) on low-quality directory/bookmark/article sites, first seen Dec 2025
– Aug 2026. These were **commissioned by a partner**. They are manipulative exact-match
anchor links and are reasonable disavow candidates, **but disavowing them reverses paid
link-building work** — so this section specifically needs the commissioning partner's
confirmation before it goes in the submitted file.

All 76 are disavowed at **domain** level (`domain:`) rather than per-URL, because the
intent is to neutralise the whole source in each case.

## 5. Blockers / things the requester should know

1. **Approvals outstanding — do not submit.** Harbinger (whole file) and the
   commissioning partner (Section 2) must sign off first. I cannot reach them from this
   session.
2. **Deadline has passed.** Tab 08 set "by end of October 2026"; today is 2026-11-03.
   The production step is late — flag to Harbinger.
3. **Source-of-truth mismatch (592 vs 1,054 vs 2,003).** Resolve which tool Tab 08 came
   from before the file is treated as final.
4. **Submission is a separate manual step** in Google Search Console's disavow tool, on
   the correct property — not performed here.

## 6. Files

- `disavow.txt` — annotated (per-domain Ahrefs DR / first-seen / spam flag, or
  "not present in Ahrefs index"), two labelled sections. Human-review copy.
- `disavow-clean.txt` — same 76 `domain:` entries, minimal comments. Upload copy.
