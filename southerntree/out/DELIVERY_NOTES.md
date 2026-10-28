# Southern Tree Solutions — Backlink Audit & Disavow (southerntreega.com)

**Prepared by Harbinger Marketing · 2026-10-28**

Deliverables in this folder:
- `Southern_Tree_Solutions_Backlinks_Audit.xlsx` — the 7-tab audit workbook (signed Harbinger format).
- `disavow_southerntreega.txt` — the Google disavow file (460 domains). **Do not upload yet** — see §3.

---

## 1. The headline: the brief was wrong by two orders of magnitude

The task described **"41 referring domains."** The live profile is nothing like that:

| Source | Referring domains | Backlinks |
|---|---|---|
| Brief | 41 | — |
| **Semrush (live)** | **4,723** | 6,276 |
| Ahrefs (live, audited here) | 1,723 | 3,253 |

This is an **active, accelerating spam / negative-SEO flood**: Semrush's month-by-month history shows the profile holding ~650 domains through mid-2025, then **5×-ing in the last 30 days** (959 → 4,658 in Oct 2026). One keyword-stuffed anchor — *"Get Higher Rankings with Expert SEO Backlinks southerntreega.com"* — accounts for ~79% of the Semrush profile on its own.

Per the audit playbook, we audited the **live profile, not the brief's 41.**

## 2. What the audit found (the 1,723 domains we could pull)

| Status | Domains | In the file? |
|---|---|---|
| Spam (Disavow) | **460** | Yes |
| Spam (Nofollow, No Action) | 497 | No — nofollow, passes nothing |
| Held (Pending Partner) | 645 | No — until the partner confirms |
| Held (Nofollow, No Action) | 100 | No |
| Keep | 21 | No — genuine citations (BBB, DexKnows, Birdeye, Brandfetch, local directories) |
| Own Site | 0 | — |

**Two campaigns, easy to tell apart:**
- A **link-scheme flood** of keyword-stuffed "SEO backlink" sales-copy anchors and link-indexer / URL-shortener / "domain report" stub pages, almost all pointing at the **home page**. This is the attack.
- A smaller **commissioned-looking campaign**: exact-match commercial anchors ("Tree Service Griffin GA", "Tree Pruning Services Griffin GA") on low-quality directories/article-farms, pointing at **deep `/service/` pages**. These are **Held** for the previous SEO partner to confirm — they *may* have been paid placements, and disavowing a link the client paid for would hurt them.

## 3. 🔴 Read before you upload — three things that change the file

**(a) This file is PARTIAL. Semrush API units ran out mid-pull.** We retrieved the full Semrush overview, growth history and anchor profile, but only 2,000 of 6,276 backlink rows and none of the per-domain Semrush metrics before the account hit a zero balance. The audit was then completed on **Ahrefs**, which indexes far fewer of the brand-new flood domains than Semrush (1,864 vs 4,723). **The true spam count is materially higher than the 460 shown here.** To enumerate the remaining ~2,800 Semrush-only flood domains, top up Semrush API units and we can extend the file.

**(b) Metrics are Ahrefs, not Semrush.** The "AS" column carries **Ahrefs Domain Rating (DR)** and traffic is Ahrefs' estimate — because Semrush was exhausted. Note DR is inflated on these spam link-farms (DR 49–79 on pure spam), so the classifier never "keeps" a domain on authority alone; every disavow rests on anchor / title / host evidence.

**(c) Held domains are excluded on purpose.** 745 domains are held pending confirmation of whether they were commissioned. The brief said to *"confirm with Harbinger"* — but **Harbinger is the agency running this audit**, so confirmation must come from the **client's previous SEO partner**. Until that conversation happens, none of the 745 held domains go in the file.

**Also:** one Search Console property only (`southerntreega.com`) — no client-owned redirect domains were found in the data, so a single disavow file is correct. **Confirm whether a disavow file is already filed** on the property; if so, uploading **replaces** it. Do not submit to Google Search Console until the partner has reviewed the held set — and we do not submit on the client's behalf.

## 4. One thing worth checking: Augusta vs Griffin

The **genuine, older citations** (BBB, Yellowpages, Birdeye, Neustar Localeze, the client's own Squarespace) place the business as **"Southern Tree Solutions / Southern Tree Care, Inc." in the Augusta, GA area** (Keysville / Waynesboro / Burke County). The **commissioned-looking 2024+ campaign targets Griffin, GA** (~2.5 hours away). Either the business expanded to Griffin, or that campaign isn't genuinely theirs. Worth a quick confirmation with the client, as it affects how the held set is judged.

## 5. How this was produced (reproducible)

`southerntree/scripts/` — `load.py` (Semrush+Ahrefs merge), `classify.py` (six-status rules), `build.py` (workbook + disavow). `southerntree/check/verify.py` runs the both-directions correctness suite and the cell-for-cell template compare; it passes with zero failures. Change the format in `build.py`, never by hand in Excel.
