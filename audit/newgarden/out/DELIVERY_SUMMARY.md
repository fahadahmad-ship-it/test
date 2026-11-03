# New Garden Landscaping & Nursery — backlink audit & disavow

**Prepared:** 2026-11-03 · **Site:** newgarden.com · **Format:** Harbinger signed audit format

## Files
- `NewGarden_Backlinks_Audit.xlsx` — the 7-tab workbook (Summary, Referring Domain
  Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines,
  Disavow List).
- `disavow_newgarden.txt` — the disavow file (1,719 `domain:` lines, grouped by reason).
- `BUILD_NOTES.md` — deviations, limitations, and the assets still needed.

> **Do not upload the disavow file yet.** It excludes 238 "held" domains pending the
> previous SEO partner's confirmation, and submission to Google Search Console is a
> manual step the client performs after that conversation.

## What the live profile looks like (re-pulled today, not from the brief)
- **2,724 referring domains / 7,189 unique links** (Semrush-complete; Ahrefs-sampled —
  see notes). Semrush's raw headline is 8,086 backlinks before de-duplication.
- **This is a large, recent negative-SEO / link-spam blast.** 1,464 of the spam domains
  were first seen in **October 2026** — Semrush's own history shows referring domains
  jumping from ~1,171 (Sep) to ~2,637 (Oct).

## Verdicts (one status per domain)

| Status | Domains | Links | In the file? |
|---|---:|---:|---|
| Spam (Disavow) | 1,719 | 1,752 | **Yes** |
| Held (Pending Partner) | 238 | 1,745 | No — partner confirms first |
| Held (Nofollow, No Action) | 60 | 179 | No |
| Spam (Nofollow, No Action) | 61 | 85 | No (nofollow, passes nothing) |
| Keep | 646 | 3,428 | No |
| Own Site | 0 | 0 | — |

**Every disavow line rests on visible evidence:** 1,640 on PBN/link-selling sales-copy
anchors, 56 on spam page titles/URLs, 17 on spam host names, 6 on directory/listing
hosts with corroboration. **Nothing is disavowed on Authority Score, TLD, or IP alone;
nothing with AS ≥ 20; nothing that names the client as a genuine citation.**

## The two campaigns
1. **Link-scheme flood (disavow):** throwaway-TLD domains (`.shop/.space/.site/.store/
   .online/.website`) carrying "premium backlinks / PBN / rank first page / buy
   backlinks" anchors, plus a wave of fake "SEO rank-checker" sites. Unsolicited.
2. **Exact-match local-service anchors (held):** 238 domains with anchors like
   "Landscape Maintenance Greensboro NC" / "Landscape Design Company Winston-Salem".
   These **may be commissioned placements** — they are held for the previous SEO partner
   to confirm. If the partner does not confirm, append the lines in **Pending Disavow
   Lines** to the file. Markets: mostly Winston-Salem and Greensboro.

## One property, one file
All links target newgarden.com (incl. the `plants.` catalogue and `estimate.`
subdomains). Only 15 links route through a redirect (`newgardenln.squarespace.com`, an
old site) and are folded into this single union file for the newgarden.com property.

## Before submitting
1. Partner fills `Partner confirmed?` / `Final decision` on the 344 Exact Match rows.
2. Check Search Console for a manual action, and whether a disavow file already exists
   on newgarden.com (uploading **replaces** it).
3. For complete coverage, supply the full Ahrefs backlink/refdomain CSV export — the
   Ahrefs API here is capped at 250 rows/call, so Ahrefs discovery was a sample.
