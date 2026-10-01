# betterwaste.co.uk — KWR review & new opportunity analysis

**Date:** 1 Oct 2026 · **Market:** UK · **Primary data:** Semrush (UK database) · **Cross-check:** Ahrefs (indexed URLs only)

## Files

| File | What's in it |
|---|---|
| `01-findings.md` | Full write-up: current state, structural problems, competitor analysis, opportunity clusters, prioritised roadmap |
| `02-new-keywords.csv` | 104 recommended keywords, in the same column format as the client sheet (Market / Type / Mapped URL / Keyword / SV), plus Semrush search intent, KD, difficulty grade, page status and priority |
| `04-serp-competition.md` | Live top-10 SERP check on 24 decision-critical keywords — who actually ranks, which SERPs are council/gov-blocked, and a revised priority order |
| `05-difficulty-verdict.md` | **Start here.** Every difficulty call graded on the Semrush Authority Score of the sites actually ranking. States the test used, the easy/medium/hard split, and the build order |
| `06-segmented-plan.csv` | The full plan segmented by page (same block layout as the client tracker): one block per target URL, each keyword with intent, SV, KD, difficulty grade and the Authority Score evidence behind it |
| `07-page-inventory.md` | **Correction.** Full crawled-URL check of what actually exists on the site. 15 pages I had scored as CREATE already exist, and the Manchester redirect direction was backwards |
| `03-fix-list.csv` | Technical / mapping fixes found during the audit, with the evidence URL and position |

All volumes, KD and competitor Authority Scores are **Semrush UK** throughout. CPC is not included. Ahrefs is used only for the indexed-URL evidence behind the www / non-www finding.

## Column notes — `02-new-keywords.csv`

- **Mapped URL** — the page on betterwaste.co.uk each keyword should be targeted at.
- **Page Status** — `CREATE` (page does not exist), `OPTIMISE` (page exists and already
  ranks, needs work), `FIX` (ranking is landing on the wrong URL), `EXCLUDE` (do not target).
- **Intent (Semrush)** — Semrush search intent. `Commercial` = researching a provider,
  `Transactional` = ready to buy/enquire, `Informational` = researching the topic,
  `Navigational` = looking for a specific brand. Two values means Semrush assigns both.
  Two location keywords return no intent value from Semrush and are marked `n/a`.

## Difficulty grading — the rule used

Better Waste is **Semrush Authority Score 20**. The test applied throughout is:
*how many sites at AS ≤ 25 — at or below Better Waste — currently rank in the top 10?*

| Grade | Rule |
|---|---|
| EASY | 3+ ranking sites at AS ≤ 25, and fewer than 4 council/gov slots |
| MEDIUM | 1–2 at AS ≤ 25, or lowest AS is 26–30 with fewer than 4 council/gov slots |
| HARD | Nothing at AS ≤ 25, or 4+ council/gov slots |
| AVOID | SERP intent is not commercial waste service |
| UNVERIFIED | Insufficient AS data to grade honestly |

**Evidence Source** states the basis for every row: `direct AS check` (31 keywords),
`inherited` (66 — shares a SERP family with a directly-checked keyword, named in the
evidence cell), `not checked` (7).

Authority Scores were pulled for 85 ranking domains via Semrush bulk backlink analysis.

**CPC is not included** in any deliverable.
