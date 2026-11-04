# Erth Products — Backlink Audit & Disavow: method, sources, and notes

Date: 2026-11-04 · Property: erthproducts.com · Format: Harbinger signed-off (K&K template, matched cell-for-cell)

## What was produced
- `Erth_Products_Backlinks_Audit.xlsx` — 7 tabs: Summary, Referring Domain Audit, All Backlinks,
  Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List.
- `disavow_erthproducts.txt` — Google disavow file, `domain:` lines grouped by reason, with a header.

## Scope decision (important)
The brief described 20 domains / one anchor / "207 referring domains since June 2026". The **live**
Semrush profile on 2026-11-04 is **~2,008 referring domains** (Ahrefs adds 218 more → **2,226 audited**).
The referring-domain count went 269 (Jun) → 456 (Sep) → 1,942 (Oct) → ~2,008 (Nov). Per the playbook
(Section 3), when the profile has grown materially we audit the **full live profile**, which we did.

The brief's anchor ("High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN…") is only **89 domains** —
not even the largest template. The dominant one is **"erthproducts.com Premium SEO Backlinks for Higher
Google Rankings and Organic Traffic"** on **~1,510 domains**, plus "Professional Niche Edit Links…" (88)
and "purchased niche edits…" (24). Four PBN anchor templates, one operation.

## Two-campaign split (confirmed)
- **Link-scheme flood → home page** (2,289 of 2,552 Semrush links), dofollow, throwaway TLDs
  (.shop/.online/.store/.site/.website/.space), auto-generated hosts. → Spam.
- **Commissioned-looking campaign → deep product pages** (`/products/golf-course-divot-mix`,
  `/products/bio-retention-soil`, `/products/erth-engineered-soils`, `/products/top-dressing-*`,
  `/what-is-erth-food`, legacy `/dnn/`), exact-match / geo anchors, directory+bookmarking+podcast
  placements. → Held (Pending Partner), never auto-disavowed.

## Statuses (2,226 referring domains)
See the Summary tab for the live numbers. Six statuses only, no Review buckets.

## Data sources (honest accounting)
- **Authority Score (AS)** — Semrush (`backlinks_refdomains.domain_ascore`). This is the only metric used
  in a decision rule (AS ≥ 20 → genuine site → Keep). Ahrefs-only discovered domains have no Semrush AS
  (shown blank / 0 — brand-new throwaway domains Semrush does not index).
- **Per-link detail, anchors, targets, dofollow, First Seen, IP, response codes** — Semrush
  `backlinks` + `backlinks_refdomains`; Ahrefs `all-backlinks` + `referring-domains` fill discovery gaps.
- **RD's, Traffic, Organic Keywords** (Referring Domain Audit + Disavow List) — Ahrefs `batch-analysis`
  (bulk, 100 targets/call). **Deviation from the playbook's "metrics from Semrush" rule**, made because
  per-domain Semrush pulls for ~2,200 domains (≈40 units each for RD's) exceed a sensible API budget and
  throughput. These three columns are **descriptive only and never drive a verdict** — every disavow rests
  on visible link evidence (anchor / page title / URL template / host). If you want these three columns
  re-pulled from Semrush `domain_rank` (Traffic + Keywords, 10 units/call) for full method purity, that is
  a cheap follow-up.
- Discovery: Semrush 1,976 domains, Ahrefs-only 218, Both 32.

## Evidence rules (no metric-only disavows)
Nothing is disavowed on Authority Score, TLD, shared IP, or a vendor "is_spam" flag alone. Every disavowed
domain carries visible evidence: a PBN/sales-copy anchor, a spam page title, a spam URL template, or a
machine-generated/known spam host name (incl. all-digit `.xyz` labels). Verified exhaustively, both
directions (`erth/check/verify.py`): 0 disavow domains without visible evidence; 0 genuine client
citations in the file; 0 Keep/Held domains carrying a dofollow spam link.

## Before uploading (client actions)
1. **Confirm owned/redirect domains.** No `redirect_url` appeared in the Semrush link data, so one file
   for erthproducts.com is correct as built. You indicated other owned domains exist — send their names so
   any that are referring domains are marked **Own Site**, and so each Search Console property that needs
   its own file gets one (the money-site file would then carry the full union).
2. **Confirm with Harbinger and the previous SEO partner** who commissioned the deep-page/exact-match
   links. The 91 Held domains are excluded from the file pending that confirmation.
3. **Check whether a disavow file already exists** on the erthproducts.com property. If one does, uploading
   **replaces** it — merge first. If the client has checked and there is none, this is the first file.
4. Do not submit to Google Search Console until 1–3 are done.

## Reproduce
`erth/scripts/{load,classify,pipeline,build,records}.py`, checks in `erth/check/{verify,compare}.py`.
Raw pulls in `erth/data/`. Change only the client constants at the top of the scripts.
