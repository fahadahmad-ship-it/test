# Scapers, LLC — backlink audit & disavow (scapersllc.com)

Prepared by Harbinger Marketing · 27 Oct 2026 · Harbinger backlink-audit format

## What's in this folder

| File | What it is |
|------|-----------|
| `disavow_scapersllc.com.txt` | **Submission-ready Google disavow file** — 4,212 `domain:` lines, grouped by reason, with a header. **Do not upload before reading the caveat below.** |
| `excluded_anchors.md` | The anchors/domains **deliberately held out of the file**, with the reason for each (the second deliverable). |
| `Scapers_LLC_Backlinks_Audit.xlsx` | Full 7-tab workbook (Summary, Referring Domain Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List). |
| `audit_summary.txt` | The headline counts. |

## The profile is far worse than the brief

The brief was a stale snapshot (17,457 links / 1,119 referring domains, ~July 2026). The **live** profile is
**28,089 backlinks across 4,983 referring domains** (Semrush), so this audit covers the full live profile, not the brief's list.

Two separate negative-SEO floods hit the site:
- **July 2026 — off-topic gambling flood.** ~13,300 links carrying Turkish-gambling anchors (`betsat`, `maxwin`,
  `sahabet`, `betwoon`) injected on a handful of hacked/compromised hosts — `piggington.com` alone carries 8,636.
- **Sep–Oct 2026 — link-selling / PBN flood.** ~3,600 fresh throwaway domains carrying sales-copy anchors that name
  the client and its sister brands ("… premium authority backlinks for better search visibility", "High Quality Dofollow
  Backlinks DA 50 PA 40 … buy backlinks online cheap", testimonial spam).

## What was decided

| Status | Domains | In the file? |
|--------|--------:|--------------|
| Spam (Disavow) | 4,212 | **Yes** |
| Spam (Nofollow, No Action) | 40 | No — nofollow, passes no value |
| Held (Pending Supplier) | 537 | **No — pending confirmation** |
| Keep (genuine / low-signal) | 194 | No |

At the client's instruction the low-volume (2-link) directory/listing spam is now included; the ~190 domains left as Keep are genuine citations or industry-relevant local sites, plus single-link mentions. Every disavowed domain rests on **visible evidence** (a gambling or PBN sales-copy anchor, a spam host-name
signature, or a naked-URL link-scheme pattern) — nothing is disavowed on score, TLD or IP alone. Verified both
directions: zero genuine citations in the file, zero gambling/PBN links left in Keep/Held.

## ⚠️ Before you upload — read this

1. **The 537 Held domains are NOT in the file.** They carry exact-match "dumpster rental &lt;Missouri city&gt;" anchors
   pointing at deep service pages and may be **commissioned placements**. Confirm with the **supplier (the previous SEO
   partner)** who ordered them before disavowing. The held lines are listed in the workbook (Pending Disavow Lines tab)
   and in `excluded_anchors.md`, ready to append if the supplier does not claim them.
2. **One property.** This file is for the `scapersllc.com` Search Console property. If a disavow file already exists
   there, uploading **replaces** it — merge rather than overwrite. If Search Console shows none, this is the first file.
3. **Sister brands.** Some flood links redirect toward `stldumpsters.com`, `stldumpster.com`, `stldumpsterental.com`,
   `renthisdumpster.com`, `stlrolloffs.com`, `farmingtondumpsters.com`. If the client controls those properties, each
   needs its own file.
4. We do **not** submit anything to Google Search Console on the client's behalf.

## Method & limits

Metrics are from Semrush (Authority Score, backlinks, referring domains); Ahrefs supplied link-level detail (anchors,
targets, live-page status, traffic) for ~2,100 of the domains. Where Semrush records a domain but Ahrefs does not, the
domain is classified on its Semrush anchor/host evidence. Per-domain organic traffic/keywords for brand-new spam
domains read as real zeros (no audience), consistent with the link-scheme fingerprint.
