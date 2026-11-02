# Ritter Consulting Engineers — Backlink Audit & Disavow

Referring-domain audit and Google disavow file for **ritterconsultingengineers.com**,
in the signed-off Harbinger 7-tab format. Built to `AUDIT_FORMAT.md` +
`BACKLINK_AUDIT_PLAYBOOK.md`, verified cell-for-cell against the template.

## Deliverables (`out/`)
- `Ritter_Backlinks_Audit.xlsx` — 7 tabs: Summary, Referring Domain Audit, All
  Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List.
- `disavow_ritterconsultingengineers.txt` — 957 `domain:` lines, grouped by reason.
  **Do not upload before the previous SEO supplier confirms which held placements
  they commissioned.** It is the only file to submit (single Search Console
  property; no redirect domains).

## Headline numbers
- Live profile: **1,423 referring domains / 2,389 links** (Semrush), Authority Score 7.
  Brief said ~150 — the profile has grown ~9× (Aug→Sep 2026 flood).
- **957 Spam (Disavow)** · 97 Spam (Nofollow) · 331 Held (Pending Supplier) ·
  10 Held (Nofollow) · 28 Keep · 0 Own Site.
- Two campaigns: a home-page PBN flood (1,601 home-page links; dominant anchor
  "Premium Link Building Experts … ritterconsultingengineers.com" on 706 domains)
  and a commissioned directory campaign (deep service-page links, service + "Louisiana"
  anchors) → held for the supplier.

## Method (fixed)
- **Semrush** is the source for every metric (AS, backlinks, RD's, traffic, keywords).
  Authority Score from the bulk comparison report. **Ahrefs** checked for coverage
  (1,221 live refdomains < Semrush's 1,423 — nothing material missed); live-page
  status rests on Semrush `response_code`.
- Nothing disavowed on Authority Score, TLD or shared IP alone — every line rests on
  a spam anchor, a spam page title/URL, or a known link-network host.
- Held ≠ disavow: exact-match commercial (service + geo) and deep-money-page links
  are held for the supplier, never auto-disavowed.

## Pipeline (`scripts/`)
1. `load.py` — Semrush CSV reader (HTML-entity / `;`-delimiter safe).
2. `classify.py` — six-status classifier (playbook verdict order).
3. `build.py` — workbook + disavow builder (template-exact styling).
4. `verify.py` — both-directions correctness sweep (run after build).
5. `compare.py` — structural match vs the signed-off template (reports zero diffs).
6. `config.py` — the only per-client constants (vocabulary, geo, domain).

Regenerate: re-pull `data/` from Semrush, then
`python3 -I scripts/build.py && python3 -I scripts/verify.py && python3 -I scripts/compare.py`.

## Verification status
`verify.py` PASSED both directions · `compare.py` zero structural differences ·
0 false positives · 0 disavow lines without visible evidence · 0 dofollow spam kept out ·
12 trafficked disavow domains hand-reviewed (all confirmed spam, ≤12 visits).
