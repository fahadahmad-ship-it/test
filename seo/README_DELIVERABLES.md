# Master Lawn — SEO Deliverables Index & Notes

**Client:** https://www.masterlawn.com/ · **Data source:** Semrush (Authority Score & Traffic), cross-checked with Ahrefs · **Snapshot:** 2026-09-04
**Scope:** Task 1 (Backlink Audit), Task 2 (Disavow prep), Task 3 (Baseline Benchmark). Task 4 (Authority link acquisition) parked pending sign-off.

---

## Headline result

Reviewed **every** referring domain (1,169 unique) and **every** backlink (3,651).

| Verdict | Domains | Meaning |
|---|---:|---|
| 🔴 **TOXIC** | **852 (72.9%)** | Disavow — **every one has hard spam evidence AND zero organic traffic** |
| 🟢 KEEP | 113 | Legitimate / relevant — do not disavow |
| 🟡 MONITOR | 199 | Ambiguous, low-value local citations, all-nofollow, or signal-only — watch, do NOT disavow |
| ⚫ OWN | 5 | Client/sister properties — never disavow |

### Why these 865 are actually spam (not just "low score")
Every disavowed domain is backed by evidence visible in the raw URLs/anchors — independent of any authority metric:
- **819** sit on known **PBN hosting farms** (shared /16 blocks: 64.182.x, 69.13.x, 94.46.x, 118.139.x, …).
- **576** serve the *identical* auto-generated URL template `/detail/<id>/<service-city>.html` (one software across hundreds of domains).
- **57** share a duplicate `/page-<hash>` file across domains; **31** an `/all/<id>/<n>.html` injection template.
- **32** links literally advertise the scheme ("buy backlinks / DA 50 PA 40 / PBN network"); **9** "boost your DA, WhatsApp us"; **1** telegram/darkside; **9** bookmark-spam; **5** gambling.

The **Disavow List** and **Referring Domains** sheets show the evidence tag per domain, so each entry is justified.

### Judgment calls handled conservatively
- **Nofollow:** all-nofollow toxic domains pass no PageRank → moved to MONITOR (low-quality nofollow directory citations can still aid GMB/local NAP).
- **Local citations:** genuine reputable directories are KEPT; standalone low-quality directories moved to MONITOR; every geo-anchor link is listed on the **Local Citations Review** sheet.
- **Signal-only:** 51 domains with no hard fingerprint and not on a farm were moved to MONITOR — not disavowed.

---

## The files

### 1. `MasterLawn_Backlink_Audit.xlsx`
| Sheet | Contents |
|---|---|
| **Dashboard** | KPI tiles + 6 charts (verdict split, Authority-Score distribution, toxic-by-year, country, TLD, PBN IP clusters). |
| **Executive Summary** | Metrics, classification result, key findings, recommendation. |
| **Referring Domains** | All 1,169, classified: verdict, Authority Score, Dofollow/Nofollow counts, IP, **Spam evidence**, reason. Colour-coded, auto-filtered, frozen header. |
| **All Backlinks** | All 3,651 links — source URL, target URL, anchor, nofollow, sitewide, verdict. |
| **Disavow List** | The 865 domains as `domain:` entries, each with its **spam evidence**. |
| **Local Citations Review** | Every geo-anchor link with on-farm flag + example anchor/target for human review. |
| **Anchor Analysis / Toxic Clusters / Methodology** | Anchor spam flags · PBN farms by IP · scoring rubric + nofollow/evidence policy. |

### 2. `MasterLawn_Disavow.xlsx` (+ `disavow_masterlawn.txt`)
Standalone disavow — 865 `domain:` entries with evidence + a README with submission steps. `disavow_masterlawn.txt` is the Google-format file. **Status: QA-PENDING** until false-positive sweep + client sign-off.

### 3. `MasterLawn_Baseline_Benchmark.xlsx`
KPI tiles + Semrush metrics (AS 23, traffic 2,391/mo), toxicity split, Local Keyword Set, Change Log.

### Supporting / audit trail
- `MasterLawn-SEO-Audit-Plan.md` — overall 4-task plan.
- `build_audit_v2.py` / `build_extras_v2.py` / `classify.py` — reproducible generators.
- `data/` — raw Semrush exports + QA layers (`qa/`, `qa2/` critical pass, `qa3/` local-citation) so every verdict is traceable.

---

## How the list was validated
1. Deterministic classifier over all domains (Authority Score, PBN IPs, spam patterns, TLDs, geo/relevance).
2. **QA pass 1** — agents adjudicated borderline + verified keeps.
3. **QA pass 2 (adversarial, 8 agents)** — re-checked every toxic to rescue false-positives; re-verified keeps.
4. **Nofollow + local-citation + hard-evidence passes** — disavow narrowed to only dofollow, demonstrable spam.
5. **Cross-checked with Ahrefs** (independent crawler) — same PBN/directory domains confirmed dofollow.
   *Limitation: pages could not be live-fetched from this environment (egress proxy blocks the spam domains); verification is via URL/anchor fingerprints + two crawlers, not rendered screenshots.*

Journey of the disavow count: 1,057 → 1,003 → 986 (dedupe) → 916 (dofollow-only) → 865 (evidence-backed) → **852 (zero-traffic only)**.

## Before you submit
- Human sweep of **MONITOR (199)** and **KEEP (113)** sheets.
- Confirm ownership of masterlawninc.com / masterlawn.org / .net / midsouthturf.com / greenkingspray.com (OWN).
- Upload to the correct GSC property; refresh monthly (injection ongoing); always re-upload the full cumulative file.
