# Collins Pool Management — backlink audit & disavow

**Prepared:** 2026-11-04 · **Site:** collinspoolmanagement.com · **Format:** Harbinger signed audit format

## Files
- `CollinsPool_Backlinks_Audit.xlsx` — the 7-tab workbook (Summary, Referring Domain
  Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines,
  Disavow List).
- `disavow_collinspool.txt` — the disavow file (1,593 `domain:` lines, grouped by reason).
- `BUILD_NOTES.md` — deviations, limitations, assets still needed.

> **Do not upload the disavow file yet.** Per the brief, confirm with **Harbinger** and
> the **partner who commissioned the directory/bookmark links** first. The 273 held
> domains are excluded pending that confirmation. Submission to GSC is a manual step.

## The 76 Tab-08 domains, assessed against the wider profile (the brief's core ask)

| Outcome | Count |
|---|---:|
| In the live profile | 74 / 76 |
| → **Spam (Disavow)** — the PBN / link-selling footprint | 42 |
| → **Held (Pending Partner)** — directory/bookmark, exact-match anchors | 32 |
| Not found in the live profile | 2 |

This reproduces the brief's two footprints almost exactly (Section 1 PBN = 43, Section 2
directory/bookmark = 33). **2 flagged domains are not in the live Semrush profile:**
`daechul.co.com` (a Section-1 PBN domain) and `articles4all.org` (a Section-2 directory;
Ahrefs shows its link was lost 2026-10-28). Because a disavow is preventative, the team
should **manually add `daechul.co.com` to the disavow** and **hold `articles4all.org`**
if the original Tab-08 source still shows them — they were omitted from the generated
file only because there is no live link evidence for them now (playbook: evidence-based).

Assessing against the wider profile also surfaced **more** of the same bookmark/directory
network beyond the 76 (e.g. `sharedbookmark.net`, `supercoolbookmarks.com`,
`smoothbookmarks.com`, `socialcrowd.biz`) — all held for the same partner conversation.

## ⚠ The brief's "592-domain profile" does not match the live data
Re-pulled today: **Semrush 2,003 referring domains / 5,803 backlinks**; **Ahrefs 1,054
live / 1,702 all-time**. 592 matches neither — likely a Google Search Console
"top linking sites" export or a dated snapshot. The audit assessed the 76 against the
**real ~2,003-domain profile**, which is much larger than the brief states. Confirm the
source of the 592 figure.

## Verdicts (one status per domain)

| Status | Domains | Links | In the file? |
|---|---:|---:|---|
| Spam (Disavow) | 1,593 | 4,421 | **Yes** |
| Held (Pending Partner) | 241 | 854 | No — partner confirms first |
| Held (Nofollow, No Action) | 27 | 90 | No |
| Spam (Nofollow, No Action) | 104 | 141 | No (nofollow) |
| Keep | 122 | 270 | No |
| Own Site | 0 | 0 | — |
| **Total** | **2,087** | **5,776** | |

Spam is ~81% of the profile — this site was hit by a large link-selling/PBN campaign.
**Every disavow line rests on visible evidence:** 1,528 PBN/link-selling anchors, 57 spam
page titles/URLs, 8 spam host names. **Nothing disavowed on Authority Score, TLD or IP
alone; nothing at AS ≥ 20; nothing that names the client as a genuine citation.**

## The two footprints
1. **Link-scheme flood (disavow):** dominant anchors "Expert Guest Post Service for
   collinspoolmanagement.com" (2,894 links / 103 domains) and "Professional Link Building
   Services Helping collinspoolmanagement.com Grow" (1,340 domains), plus the Tab-08
   "High Quality Dofollow Backlinks DA 50 PA 40 …" template. Unsolicited.
2. **Exact-match commercial anchors (held):** 268 bookmark/directory/article domains with
   anchors like "Commercial Pool Services Atlanta GA", "Lifeguard Certification Atlanta
   GA". These **may be commissioned** — held for the partner. If unconfirmed, append the
   **Pending Disavow Lines** to the file. Markets: Atlanta and Alpharetta GA.

## One property
All 5,801 links target collinspoolmanagement.com; no owned/redirect domains detected →
one disavow file for the one Search Console property.

## Before submitting
1. **Confirm with Harbinger and the commissioning partner** (the brief's requirement).
2. Partner fills `Partner confirmed?` / `Final decision` on the 381 Exact Match rows.
3. Check GSC for a manual action and whether a disavow file already exists (uploading
   **replaces** it).
4. Decide on the 2 not-found Tab-08 domains (above).
5. **Note:** the brief's deadline was end of October 2026; today is 2026-11-04 — overdue.
