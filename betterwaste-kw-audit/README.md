# betterwaste.co.uk — KWR review & new opportunity analysis

**Date:** 1 Oct 2026 · **Market:** UK · **Primary data:** Semrush (UK database) · **Cross-check:** Ahrefs (GB, Domain Rating + indexed URLs only)

## Files

| File | What's in it |
|---|---|
| `01-findings.md` | Full write-up: current state, structural problems, competitor analysis, opportunity clusters, prioritised roadmap |
| `02-new-keywords.csv` | 104 recommended keywords, in the same column format as the client sheet (Market / Type / Mapped URL / Keyword / SV), plus Semrush search intent, KD, CPC, page status and priority |
| `04-serp-competition.md` | Live top-10 SERP check on 24 decision-critical keywords — who actually ranks, which SERPs are council/gov-blocked, and a revised priority order |
| `05-difficulty-verdict.md` | Critical re-check of every difficulty call, graded on the DR of sites actually ranking. States the test used, and flags every correction to my earlier grading |
| `06-segmented-plan.csv` | The full plan segmented by page (same block layout as the client tracker): one block per target URL, each keyword with intent, SV, KD, CPC, difficulty grade and the evidence behind it |
| `03-fix-list.csv` | Technical / mapping fixes found during the audit, with the evidence URL and position |

All volumes, CPC and KD are **Semrush UK** throughout. Ahrefs is used only for Domain Rating and indexed-URL evidence — no Ahrefs keyword difficulty is quoted.

## Column notes — `02-new-keywords.csv`

- **Mapped URL** — the page on betterwaste.co.uk each keyword should be targeted at.
- **Page Status** — `CREATE` (page does not exist), `OPTIMISE` (page exists and already
  ranks, needs work), `FIX` (ranking is landing on the wrong URL), `EXCLUDE` (do not target).
- **SERP Check (Semrush top 10)** — verdict from the live SERP analysis in `04-serp-competition.md`.
  24 of 104 keywords checked (the decision-critical ones); the rest read `not checked`.
- **Intent (Semrush)** — Semrush search intent. `Commercial` = researching a provider,
  `Transactional` = ready to buy/enquire, `Informational` = researching the topic,
  `Navigational` = looking for a specific brand. Two values means Semrush assigns both.
  Two location keywords return no intent value from Semrush and are marked `n/a`.

## Difficulty grading — the rule used

Better Waste is **DR 26**. The test applied in `05-difficulty-verdict.md` and
`06-segmented-plan.csv` is: *how many sites with DR ≤ 30 currently rank in the top 10?*

| Grade | Rule |
|---|---|
| EASY | 3+ results at DR ≤ 30 — reachable on content quality alone |
| MEDIUM | 1–2 results at DR ≤ 30 — needs a strong page plus some links |
| HARD | 0 results at DR ≤ 30, or 4+ council/gov slots — defer |
| AVOID | SERP intent is not commercial waste service |
| UNVERIFIED | SERP not individually checked and no valid sibling to inherit from |

**Evidence Source** column states the basis for every row:
`direct` (own Ahrefs DR check), `semrush-only` (top-10 domains, no DR data available),
`inherited` (shares a SERP family with a directly-checked keyword — the evidence cell
names which), `not checked`.
