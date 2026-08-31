# NMI — Backlink Audit: Methodology & Productisation

Two things live in this document: **the screening model** SUSO uses to judge a link (which is
what we are actually selling), and **the split** between the free pitch snapshot and the paid
audit engagement.

---

## 1. The screening model

The core methodological claim, and the one the NMI data proves in one slide:

> **Authority Score alone does not tell you whether a link is good or bad.**
> A link needs score **and** traffic **and** a clean anchor/context profile.

NMI is the proof. The spam network pointing at nmi.com right now runs at **DR 32–74** — it would
pass almost any score-based filter — and carries **zero organic traffic** on essentially every
domain. Score-only screening cannot see it.

### 1a. Acquisition filter — what we will build

A prospect must clear **all four**:

| # | Gate | Threshold | Rationale |
|---|---|---|---|
| 1 | Authority | **AS 30+** | Below this it does not move Battenhall's reported metric |
| 2 | Traffic | **1,000+ monthly organic** | Real audience. Filters PBNs that pass on score |
| 3 | Relevance | Payments, fintech, e-commerce, developer or adjacent B2B | Topical relevance is what these SERPs reward |
| 4 | Profile health | Clean outbound pattern, no link-selling footprint, real editorial content | Catches networks that clear 1–3 |

A domain at **AS 30+ that also links to a competitor** is treated as a priority target — it is
proven to link to companies in this category, so relevance and willingness are both evidenced.

### 1b. Toxicity filter — what we flag on the existing profile

Assessed on evidence, not on score:

| Signal | What it catches |
|---|---|
| **Zero organic traffic** at any DR/AS | PBNs, expired-domain networks, parked inventory |
| **Commercial spam anchors** | Third-party link networks (the Telegram anchor on NMI) |
| **Domain-name pattern clusters** | `*-seoexpress-*.store`, `*backlinks*.shop`, `*directory.com` farms |
| **Uniform link volume across many domains** | Programmatic placement — NMI's typo-domain cluster |
| **Outbound link ratio / linked-domain count** | Link farms with no editorial function |
| **Anchor-to-target mismatch** | Injected or hacked links |

**We do not treat low AS as toxic on its own.** An AS 15 niche payments blog with 3,000 monthly
visitors is a better link than an AS 50 zero-traffic directory, and the model has to say so.

---

## 2. Pitch snapshot vs paid audit

| | **Pitch snapshot** (free, in the deck) | **Full audit** (paid engagement) |
|---|---|---|
| AS comparison vs 3 named competitors | ✅ | ✅ |
| AS 30+ counts and the gap multiple | ✅ headline only | ✅ full distribution, all competitors |
| Good-link count (1,000+ traffic) | ✅ headline only | ✅ exact, paginated, segmented |
| Spam network | ✅ **named, sized, not listed** | ✅ full domain list, severity, disavow file |
| Flagged anchors | ✅ 2 examples | ✅ complete anchor audit + risk scoring |
| Typo-domain cluster | ❌ withheld | ✅ ownership resolution |
| Link intersect | ✅ **4 sample domains** | ✅ full ~140-domain pool, vetted and prioritised |
| Target page map | ✅ summarised | ✅ per-page allocation and forecast |
| Toxicity / disavow recommendation | ❌ | ✅ |
| Internal linking & consolidation review | ❌ mentioned only | ✅ |

**The rule:** the pitch proves we found things. The audit is where we say what they are.
Naming the spam network without listing it is the whole play — it demonstrates capability and
creates the reason to buy.

---

## 3. Audit scope and effort

| Phase | Work | Effort |
|---|---|---|
| 1 | Full referring domain export, paginated (Ahrefs + Semrush, deduped) | 0.5 day |
| 2 | Quality segmentation: AS bands × traffic bands × dofollow/content | 0.5 day |
| 3 | Toxicity pass: pattern clustering, anchor review, zero-traffic isolation | 1 day |
| 4 | Editorial vs footprint segmentation (**R1** — the KPI baseline) | 0.5 day |
| 5 | Full link intersect across 5 competitors, vetted and categorised | 1 day |
| 6 | Target page mapping + per-page link gap analysis | 0.5 day |
| 7 | Disavow recommendation + internal linking/consolidation review | 0.5 day |
| 8 | Write-up and presentation | 1 day |
| | **Total** | **~5.5 days** |

**Deliverables:** audit document, referring-domain workbook (segmented), prioritised prospect
pool, disavow candidate file, target page map with link allocation, 60-minute walkthrough.

⚠️ **Not yet priced.** Blocked on the same rate card as the retainer scopes (`02` §7, B1).

---

## 4. Open methodology items

| # | Item | Status |
|---|---|---|
| ~~M1~~ | ~~Exact count of RDs with 1,000+ traffic~~ | **RESOLVED — 783 of 4,164 (18.8%)**, via paginated banding |
| ~~M2~~ | ~~Exact size of the spam network~~ | **RESOLVED — 851+ total, 327 at DR 30+**, of which only 12 have any traffic |
| M3 | Typo-domain cluster ownership | **Blocked** — needs WHOIS/registrar check or a direct question to NMI |
| M4 | Editorial vs footprint RD split (R1) | Open — required before any KPI is agreed |
| M5 | Spam network impact assessment | Open — **do not claim penalty risk in the pitch without this** |

M1 and M2 are now exact and safe to quote: **783 good links**, **327 DR 30+ spam domains**.
The sub-DR-5 spam tail is still capped and should be quoted as "851+ total", not a precise figure.
