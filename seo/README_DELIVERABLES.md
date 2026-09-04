# Master Lawn — SEO Deliverables Index & Notes

**Client:** https://www.masterlawn.com/ · **Data source:** Semrush · **Snapshot:** 2026-09-04
**Scope covered:** Task 1 (Backlink Audit), Task 2 (Disavow prep), Task 3 (Baseline Benchmark). Task 4 (Authority link acquisition) is parked pending your sign-off.

---

## Headline result (after 2 independent QA passes)

Reviewed **every** referring domain (1,169 unique) and **every** backlink (3,651).

| Verdict | Domains | Meaning |
|---|---:|---|
| 🔴 **TOXIC** | **986 (84.3%)** | Recommended for disavow |
| 🟢 KEEP | 113 | Legitimate / relevant — do not disavow |
| 🟡 MONITOR | 65 | Ambiguous / low-value local citations — watch, do NOT disavow yet |
| ⚫ OWN | 5 | Client/sister properties — never disavow |

**Local-citation safeguard:** for a local business, low-quality directory *citations* (a real "Lawn Aeration Huntsville AL" listing) can help local SEO, so they are handled carefully. The spam network here deliberately fakes those anchors — 806 toxic domains use real city/service anchors but sit on PBN farms/throwaway hosts (camouflage). Only standalone, non-farm business directories were pulled out of the disavow into MONITOR; every geo-anchor link is listed on the **Local Citations Review** sheet for a human check.

**Why so many?** The profile is dominated by an automated **directory/article/bookmark PBN + link-selling network** (single-IP farms on `64.182.x`, `69.13.x`, `94.46.x`, `118.139.x`, `159.198.75.x`, `195.20.19.178`), plus gambling/off-topic and foreign-hosting spam, and "buy backlinks / DA-PA / telegram" anchors. ~90% of referring domains sit at Authority Score ≤6. This is manipulation / negative-SEO contamination, not earned authority.

---

## The files

### 1. `MasterLawn_Backlink_Audit.xlsx` — the full audit
| Sheet | What it contains |
|---|---|
| **Summary** | Scope, verdict counts, % toxic, key finding. Start here. |
| **Referring Domains** | All 1,170 domains, each with verdict, toxicity score, Authority Score, backlinks, IP, country, first/last seen, reason code, and evidence. Colour-coded; auto-filtered; header frozen. |
| **All Backlinks** | All 3,651 links — source URL, target URL, **anchor text**, nofollow, sitewide, page AS, referring domain, inherited verdict, dates. Auto-filtered. |
| **Anchor Analysis** | Top anchors with ref-domain/backlink counts; spam & gambling anchors flagged red. |
| **Distributions** | Referring domains by Authority Score, by TLD zone, and by country (IP geo). |
| **Toxic Clusters** | PBN farms grouped by shared IP /24 (how many toxic domains sit on each). |
| **Methodology** | The 3-axis (Trust / Relevance / Language) scoring rubric and verdict thresholds. |

### 2. `MasterLawn_Disavow.xlsx` (+ `disavow_masterlawn.txt`) — the disavow prep
| Sheet | What it contains |
|---|---|
| **Disavow (domain-level)** | The **1,003 TOXIC** domains as `domain:` entries, with Authority Score, IP, country, reason code and evidence. Auto-filtered. |
| **README** | Submission steps, what's included/excluded, and QA sign-off requirements. |

`disavow_masterlawn.txt` = the Google-format file (1,003 `domain:` lines, comment header). **Status: QA-PENDING** — do not upload until the false-positive sweep + two-analyst + client sign-off are done.

### 3. `MasterLawn_Baseline_Benchmark.xlsx` — the critical baseline (Task 3)
| Sheet | What it contains |
|---|---|
| **Baseline Benchmark** | Semrush authority & backlink profile, this audit's toxicity split, organic visibility (rank, keywords, traffic, value), and pending GSC/GA4 items. |
| **Local Keyword Set** | Services × geo modifiers (Memphis/Germantown/Collierville/Bartlett/Olive Branch/Southaven/Huntsville) to load into rank tracking. |
| **Change Log** | Dated row for the 2026-09-04 baseline; add a row each month to trend the recovery. |

### Supporting files (audit trail)
- `MasterLawn-SEO-Audit-Plan.md` — the overall project plan across all 4 tasks.
- `classify.py` — the deterministic classifier that produced the workbooks (reproducible).
- `data/` — raw Semrush exports + both QA review layers (`qa/` first pass, `qa2/` critical second pass) so every verdict is traceable.

---

## How the 1,003 were validated (why you can trust the list)

1. **Pass 0 — deterministic classifier** over all 1,170 domains (Authority Score, PBN IP clusters, spam name patterns, spam TLDs, gambling/off-topic, foreign-geo, on-topic/geo relevance offsets).
2. **QA pass 1** — agents adjudicated the 204 borderline (MONITOR) domains + verified the 74 KEEP.
3. **QA pass 2 (critical, adversarial)** — every one of the (then) 1,057 TOXIC domains was re-reviewed by 7 agents with a mandate to **rescue anything plausibly real**, and all KEEP re-checked to **catch hidden spam**. Net effect: ~50+ domains rescued out of disavow (real local/lawn businesses, .edu/charity, legit platforms), a handful of programmatic lead-gen directories pulled into TOXIC.

**Design & formatting:** yes — the workbooks use styled/frozen header rows, colour-coded verdicts, auto-filters on every large table, sized columns, wrapped evidence text, and a self-documenting Summary/Methodology/README. They're built to hand to a client or work in directly.

## Before you submit the disavow (recommended)
- Human false-positive sweep of the **KEEP** and **MONITOR** sheets (49 monitor domains are deliberately excluded from the file).
- Confirm ownership of `masterlawninc.com`, `masterlawn.org`, `masterlawn.net`, `midsouthturf.com`, `greenkingspray.com` (treated as OWN, never disavowed).
- Upload to the correct GSC property; refresh **monthly** (the injection is ongoing) and always re-upload the full cumulative file.
