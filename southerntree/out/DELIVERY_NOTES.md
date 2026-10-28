# Southern Tree Solutions — Backlink Audit & Disavow (southerntreega.com)

**Prepared by Harbinger Marketing · 2026-10-28**

Deliverables in this folder:
- `Southern_Tree_Solutions_Backlinks_Audit.xlsx` — the 7-tab audit workbook (signed Harbinger format).
- `disavow_southerntreega.txt` — the Google disavow file (**4,069 domains**). **Do not upload yet** — see §3.

---

## 1. The headline: the brief was wrong by two orders of magnitude

The task described **"41 referring domains."** The real profile — now audited in full from the complete Semrush export plus Ahrefs discovery:

| Source | Referring domains | Backlinks |
|---|---|---|
| Brief | 41 | — |
| **Audited (Semrush export + Ahrefs)** | **5,360** | 6,983 |

This is an **active, accelerating spam / negative-SEO flood**. Semrush's month-by-month history shows the profile holding ~650 domains through mid-2025, then **5×-ing in the last 30 days**. One keyword-stuffed anchor — *"Get Higher Rankings with Expert SEO Backlinks southerntreega.com"* — drives **4,400 links across 4,349 domains** on its own (~81% of the profile).

Per the audit playbook, we audited the **complete live profile, not the brief's 41.**

## 2. What the audit found

| Status | Domains | In the file? |
|---|---|---|
| **Spam (Disavow)** | **4,069** | **Yes** |
| Spam (Nofollow, No Action) | 519 | No — nofollow, passes nothing |
| Held (Pending Partner) | 645 | No — until the partner confirms |
| Held (Nofollow, No Action) | 102 | No |
| Keep | 25 | No — genuine citations (BBB AS 79, Yellowpages 73, Birdeye 86, DexKnows 78, Brandfetch, local directories) |
| Own Site | 0 | — |
| **Total** | **5,360** | |

**86% of the profile (4,588 domains) is spam.** Two campaigns, easy to tell apart:
- A **link-scheme flood** of keyword-stuffed "SEO backlink" sales-copy anchors + link-indexer / URL-shortener / "domain report" stub pages, almost all pointing at the **home page**. This is the attack → the disavow file.
- A smaller **commissioned-looking campaign**: exact-match commercial anchors ("Tree Service Griffin GA", "Tree Pruning Services Griffin GA") on low-quality directories/article-farms, pointing at **deep `/service/` pages** (1,988 deep-page links). These are **Held** — they *may* have been paid placements, and disavowing a link the client paid for would hurt them.

## 3. 🔴 Read before you upload

**(a) Held domains are excluded on purpose.** 747 domains are held pending confirmation of whether they were commissioned. The brief said to *"confirm with Harbinger"* — but **Harbinger is the agency running this audit**, so confirmation must come from the **client's previous SEO partner**. Until that conversation happens, none of the 747 held domains go in the file. The *Pending Disavow Lines* and *Exact Match Anchors* tabs list them for that review.

**(b) Metrics are Semrush, traffic is Ahrefs.** The **AS** column is the true **Semrush Authority Score**, with IP and backlink counts from the Semrush export. Per-domain **organic traffic** is Ahrefs' estimate (the Semrush export doesn't include it). Nothing is disavowed on a score alone — every one of the 4,069 lines rests on anchor, linking-page title, or host-name evidence (verified both directions, exhaustively).

**(c) One Search Console property.** No client-owned redirect domains were found in the data, so a single disavow file for `southerntreega.com` is correct. **Confirm whether a disavow file is already filed** on the property; if so, uploading **replaces** it. Do not submit to Google Search Console until the partner has reviewed the held set — and we do not submit on the client's behalf.

## 4. One thing worth confirming with the client: Augusta vs Griffin

The **genuine, older citations** (BBB, Yellowpages, Birdeye, Neustar Localeze, the client's own Squarespace) place the business as **"Southern Tree Solutions / Southern Tree Care, Inc." in the Augusta, GA area** (Keysville / Waynesboro / Burke County). The **commissioned-looking 2024+ campaign targets Griffin, GA** (~2.5 hours away). Either the business expanded to Griffin, or that campaign isn't genuinely theirs. A quick confirmation would sharpen how the held set is judged.

## 5. How this was produced (reproducible)

`southerntree/scripts/` — `load.py` (Semrush export + Ahrefs merge), `classify.py` (six-status rules, hardened against DR-inflation and link-indexer spam), `build.py` (workbook + disavow). `southerntree/check/verify.py` runs the both-directions correctness suite and the cell-for-cell template compare against the signed K&K template, and passes with zero failures. Change the format in `build.py`, never by hand in Excel.
