# Super K Express — backlink audit & disavow file

**Client:** https://superkexpress.com/ · **Prepared:** 2026-10-29 · Signed Harbinger audit format.

## Deliverables (in this folder)
- `SuperKExpress_Backlinks_Audit.xlsx` — the 7-tab workbook (Summary, Referring Domain
  Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines,
  Disavow List). Matches the signed K&K template cell-for-cell (zero structural
  differences).
- `disavow_superkexpress.com.txt` — the Google disavow file. **One file**, for the
  `superkexpress.com` Search Console property (no owned/redirect domains exist).

## Headline
Semrush shows **61,239 backlinks from 1,644 referring domains**, Authority Score 10,
99.8% dofollow — a textbook spam link profile, grown from **336 referring domains (Nov
2024) to ~1,620 (Oct 2026)**. Across the full Semrush + Ahrefs union (2,222 domains):

| Status | Domains | In file? |
|---|---|---|
| Spam (Disavow) | **1,663** | Yes |
| Spam (Nofollow, No Action) | 68 | No (passes no value) |
| Held (Pending Partner) | 403 | **No — awaiting partner** |
| Held (Nofollow, No Action) | 1 | No |
| Keep | 87 | No |
| Own Site | 0 | — |

## Three campaigns, cleanly separated by target page
1. **Gambling injection** — anchor `jogjatoto` (Indonesian gambling brand) pointed at
   `/resources/`; **bisicon.com alone = 58,903 links**, 15 domains total. Off-topic spam.
2. **PBN link-blast** — keyword-stuffed SEO sales-copy anchors ("Build Powerful Website
   Authority with Premium SEO Backlinks…") pointed at the **home page**, ~1,500 domains.
3. **Commissioned-looking exact-match campaign** — the client's own trucking service +
   geography anchors (`dry van trucking kansas city mo`, `cross docking company newnan ga`,
   …) pointed at **deep `/services/` and `/locations/` pages**. These are **HELD** for the
   previous SEO partner to confirm, never auto-disavowed.

## ⚠️ Required before submitting the file
Per the brief: **confirm with the partner who commissioned the exact-match commercial
anchors before the file is submitted.** The 404 held domains are **excluded** from the
disavow file pending that conversation, because they may be placements the client paid for
— disavowing a paid link hurts the site. Tab 5 (Exact Match Anchors) and Tab 6 (Pending
Disavow Lines) list them with partner-input cells. Once the partner confirms which were
**not** commissioned, append those `domain:` lines to the file.

Also: **uploading a disavow file replaces any file already on the property** — confirm with
the client whether one exists first. Held does not mean valuable: 381 of the 404 held
domains have no organic traffic.

## Method & disclosures (deviations from the playbook, forced by the available API)
- **Metrics are Semrush; link-level discovery adds Ahrefs** (live-page `http_code`,
  `is_spam` corroboration, recovered dates). Authority Score, backlinks and
  referring-domain **counts are all Semrush**.
- **Semrush link pull.** Semrush `backlinks` costs ~40 units/row, so pulling all 61,239
  links (~2.45M units) was infeasible. Since `bisicon.com` holds 58,903 of them, we pulled
  **every other domain's links in full** (2,337 rows) plus a bisicon sample — complete
  per-domain anchor/target/title evidence for the whole long tail.
- **Traffic / Organic Keywords / RD's columns are Ahrefs-sourced.** The available Semrush
  API exposes per-domain traffic/keywords only one-domain-per-call (no bulk report), so a
  1,644-domain Semrush pull was not feasible. In this spam profile almost every domain has
  **zero** organic traffic, so Ahrefs metrics ordered by traffic/keywords desc capture
  every non-zero domain; the rest are genuinely 0.
- **Ahrefs 250-row API cap.** A small number of Ahrefs-only fringe domains lacked
  retrievable link-level detail; they were classified conservatively on host-name + Ahrefs
  spam signals and **never disavowed without a visible signal**.
- **The file is the full union (Semrush + Ahrefs).** Of the 1,663 disavowed domains, 1,172
  are in Semrush's live profile and **491 are Ahrefs-discovered** spam the live
  referring-domain report doesn't list (e.g. a sequential `NNNNNNNN.xyz` farm, recent
  `.shop`/`.space` PBN sites). Each still rests on a visible spam anchor/title/host and has
  a dofollow link. Per the playbook the money-site file carries the complete union, and
  listing a domain that no longer links is harmless — so the file is intentionally broader
  than Semrush's 1,644.
- **Authority Score is blank for 580 Ahrefs-only domains.** Semrush AS is only retrievable
  in bulk via `backlinks_comparison`, which this MCP does not expose; per-domain AS at that
  scale is infeasible. Those domains are classified on anchor/title/host evidence (AS plays
  no part in their verdict), so the blank does not weaken any decision.
- **Anchor counts are Semrush-authoritative.** The Anchor Analysis tab and the Summary
  anchor-profile table use Semrush `backlinks_anchors` counts (e.g. `jogjatoto` = 59,168
  backlinks), not the link-level sample.
- **Blog/site platforms** (blogspot, weebly, typepad, tripod, livedoor, …) are disavowed at
  the **subdomain** level (`domain:spamblog.blogspot.com`), never the platform root.
  Path-based free hosts (angelfire.com, tripod.com) are kept out of the file — the specific
  spam URL should be disavowed manually, not the whole platform.
- **7 disavow domains carry residual organic traffic** and are flagged for your manual
  review: 360east.com, akcorp.jp, blogulluicatalina.com, caparvo.co.jp, ektype.in,
  sakuranko.com, seobacklinkschecker.online. Each is a genuine site hosting a spam-injection
  link to superkexpress (gambling or the `rankexperience.com => massive linkbuilding` PBN
  anchor) — correctly disavowed, but worth a final human glance.

Do not submit anything to Google Search Console on the client's behalf.

## Reproducing
`superk/scripts/{load,classify,build}.py` build everything from the raw pulls in
`superk/data/`; `superk/check/{verify,compare}.py` prove disavow integrity (both
directions, exhaustively) and a zero-difference match to the signed template. Run with
`python3 -I`.
