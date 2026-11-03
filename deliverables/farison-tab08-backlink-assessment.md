# farison.com — Tab 08 Disavow Assessment (Ahrefs + Semrush cross-check)

**Date:** 2026-11-03
**Analyst:** SEO (automated verification via Ahrefs API v3 + Semrush Analytics API)
**Scope requested:** Assess the 13 Tab 08 referring domains against the wider profile and produce the disavow file.
**Status:** DRAFT disavow produced. **Not submitted.** Submission is gated on sign-off from Harbinger and the partner who commissioned the links.

---

## 1. Bottom line

The 13 Tab 08 domains are **real, live, dofollow, exact-match links** from a **single coordinated directory-spam network** — that part of Tab 08 holds up. But three of Tab 08's descriptors are wrong or mislabelled, and the scoping is the real problem:

- **The 13 are a small subset of a ~287-domain network** on one IP block (69.13.0.0/16). Disavowing only 13 leaves ~274 identical links untouched.
- **The "345-domain profile" figure matches neither tool.** Ahrefs sees 1,296 live / 2,547 all-time referring domains; Semrush sees 3,667. The denominator in the brief is wrong.
- **"Two external out-domains each"** is a page-template detail, not a property of the sites (which each link out to ~2,000+ domains), and it isn't even true for 2 of the 13.
- **"Trust Flow 0"** is a Majestic metric — not available in Ahrefs or Semrush. The equivalent authority signals do corroborate "junk," but the label is from a tool nobody pulled.

Recommendation: **do not submit the 13-domain file as-is.** Decide network-vs-13 scope with Harbinger and the partner first. If the decision is to disavow, use the full-network file. See §6.

---

## 2. What was verified (and confirmed true)

Checked every Tab 08 row against Ahrefs Site Explorer (`all-backlinks`, `referring-domains`) and Semrush Backlink Analytics on 2026-11-03.

| # | Referring domain | Anchor match | Target URL match | Ahrefs DR | Dofollow | Live now | Shared /16 |
|---|---|---|---|---|---|---|---|
| 1 | gotolistings.org | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.66.56 |
| 2 | getzzby.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.64.201 |
| 3 | findzy.net | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.60.16 |
| 4 | listingspace.net | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.88.216 |
| 5 | showyourbizz.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.131.25 |
| 6 | directoryhop.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.33.64 |
| 7 | premiumlistings.co | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.120.17 |
| 8 | downtownlists.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.44.200 |
| 9 | b-listings.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.7.244 |
| 10 | prolocalbusinesssearch.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.187.177 |
| 11 | boblistings.org | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.8.14 |
| 12 | smallbizdir.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.133.33 |
| 13 | local-business-center.com | ✓ | ✓ | 0.0 | ✓ | ✓ (200) | ✓ 69.13.95.67 |

- **Anchors:** all 13 are exact-match local-service commercial anchors, exactly as Tab 08 lists them.
- **Targets:** all 13 point to the Tab 08 target URLs (farison `/service-area/*` and `/program/*` pages), all resolving 200.
- **Dofollow:** all 13 are dofollow text links.
- **Authority:** Ahrefs DR 0.0 for all 13; Semrush Authority Score ~2 across the network (showyourbizz 6, listingspace 2 observed); 0 organic traffic / 0 ranking keywords for 11 of 13.
- **Footprint:** every one on the 69.13.0.0/16 block.

**This is unambiguously one network of auto-generated directory listings.** Each site uses the same URL templates (`/anchor-slug/` and `/detail/NNNNN/anchor-slug.html`), the same 2-link-to-farison pattern, the same anchor style.

---

## 3. Discrepancies against Tab 08 (critical checks)

### 3.1 "345-domain profile" — does not match either tool
| Metric | Ahrefs | Semrush | Tab 08 |
|---|---|---|---|
| Referring domains | 1,296 live (2,547 all-time) | 3,667 | "345" |
| Total backlinks | 1,832 live (7,066 all-time) | 5,794 | — |
| Authority / DR of farison | — | AS 14 | — |

**345 matches neither.** Before "assessing against the wider 345-domain profile," confirm where 345 came from (an old/filtered export? a different subdomain? Majestic? a referring-**page** count mistaken for domains?). The baseline in the brief is unreliable.

### 3.2 "Two external out-domains each" — mislabelled, and false for 2 of 13
- At the **domain** level these are **mass directories**: each links out to **~1,936–2,904 unique domains** (Ahrefs `dofollow_linked_domains`). They are not thin 2-outlink sites.
- The "two" is a **per-page** figure: the farison-targeting listing page links to 2 external domains (`linked_domains_source_page = 2`). True for 11 of 13.
- **Exceptions:** `getzzby.com` and `gotolistings.org` link to **5** external domains per page (7 external links). They do not fit the "two out-domains" footprint.
- Correct description: *thin 2-outlink listing pages published inside large auto-generated directories.*

### 3.3 "Trust Flow 0" — wrong tool
Trust Flow is a **Majestic** metric. It is not returned by Ahrefs or Semrush and was not (could not be) verified here. The equivalent low-authority signals **do** corroborate junk quality (Ahrefs DR 0, Semrush AS ~2, no organic traffic). If Trust Flow specifically is required for the case file, pull Majestic separately rather than presenting "TF 0" as an Ahrefs/Semrush finding.

### 3.4 "First seen" dates — inconsistent with both tools
Each domain carries **two link generations**:
1. a **legacy** pretty-URL (`/anchor-slug/`), now **301-redirected / lost**, first seen **2024-10 → 2025-10**;
2. a **current** `/detail/NNNNN.html` URL, **live (200)**, first seen **~Aug 2026**.

Tab 08's dates are a mix of the two, and three match neither:

| Domain | Tab 08 first seen | Ahrefs live `/detail` | Ahrefs legacy (lost) | Note |
|---|---|---|---|---|
| gotolistings.org | 2026-08-12 | 2026-08-03 | 2024-10-23 | ~ live |
| getzzby.com | 2026-08-15 | 2026-09-05 | 2024-10-23 | ~3 wks off live |
| findzy.net | 2025-10-08 | 2026-08-12 | 2025-10-03 | matches legacy |
| listingspace.net | 2026-03-17 | 2026-08-16 | 2025-10-03 | **matches neither** |
| showyourbizz.com | 2026-08-05 | 2026-08-09 | 2025-10-04 | ~ live |
| directoryhop.com | 2025-10-11 | 2026-08-03 | 2025-02-15 | **matches neither** |
| premiumlistings.co | 2026-07-23 | 2026-08-12 | 2025-10-23 | ~3 wks off live |
| downtownlists.com | 2026-08-18 | 2026-08-16 | 2025-02-12 | ~ live |
| b-listings.com | 2026-05-05 | 2026-08-09 | 2025-10-03 | **matches neither** |
| prolocalbusinesssearch.com | 2026-08-18 | 2026-08-16 | 2025-02-12 | ~ live |
| boblistings.org | 2026-08-08 | 2026-08-04 | 2025-02-12 | ~ live |
| smallbizdir.com | 2026-08-01 | 2026-08-07 | 2025-02-15 | ~ live |
| local-business-center.com | 2025-10-07 | 2026-08-10 | 2025-10-03 | matches legacy |

Takeaway: the Tab 08 "First seen" column is **not a clean single export** and shouldn't be used as-is to argue a tidy "recent campaign" timeline. Several of these links have existed since **late 2024 / early 2025**, not mid-2026. The ~Aug 2026 cluster is the network **migrating its URL structure** (pretty-URL → `/detail/` URL), which re-triggered "first seen" on the new URLs.

### 3.5 "Trust Flow 0 / all spam" — 2 of 13 not flagged by Ahrefs
Ahrefs' spam classifier flags **11 of 13** as `is_spam=true` but **not** `boblistings.org` or `prolocalbusinesssearch.com` (both show a trace of organic traffic / 1 keyword). They are plainly the same network — so the disavow case should rest on the **footprint** (shared /16, identical template, exact-match anchors), not on the `is_spam` flag, which is not uniform.

---

## 4. The real footprint: ~287 domains, not 13

The strongest shared signal is not "two out-domains" — it's the **IP block**. A Semrush pull of farison's referring domains on `69.13.*` returns **287 unique domains across 188 class-C subnets**, every one a directory-style name (primelistings.info, 247businessdirectory.net, localbusinessfinder.co, bigbusinesseslisting.com, …) linking to farison with the same 2-dofollow-exact-match pattern. All 13 Tab 08 domains appear in that list.

So Tab 08 is **~4.5% of the network**. Full list: `deliverables/disavow-farison-69.13-network.txt` (287 domains). Supporting data: `data/refdomains-69.13.csv`.

**Implication for the decision:** disavowing 13 and stopping is close to a no-op for link hygiene — if this network is a risk, the other ~274 carry the same risk; if it isn't, the 13 don't need disavowing either. The meaningful choice is *13 vs 287 (vs nothing)*, and that is exactly what Harbinger and the partner need to weigh in on.

---

## 5. Open questions for Harbinger + the commissioning partner

1. **Who built these?** The brief says a partner *commissioned* these links. If so, this is a **bought low-quality directory campaign**, not a negative-SEO attack — which changes it from "defensive disavow" to "clean up what we paid for + vendor conversation." Confirm before framing.
2. **Scope: 13, 287, or none?** This is the core decision. My recommendation: if disavowing, disavow the whole 69.13 network (287), not just Tab 08.
3. **Is there an actual problem to solve?** Disavow is for manual-action recovery or clear algorithmic risk. No GSC manual-action or ranking-loss signal was checked here (that data lives in Search Console, not Ahrefs/Semrush). **Confirm there is a penalty / ranking issue** before disavowing — Google ignores most junk directory links already, and an unnecessary disavow can only cost you.
4. **Where did "345" and "Trust Flow 0" come from?** Reconcile the Tab 08 metrics with the live tool data in §3 so the case file is defensible.

---

## 6. Deliverables & next step

| File | Contents |
|---|---|
| `deliverables/disavow-farison-tab08.txt` | The 13 Tab 08 domains (as requested), `domain:` level. |
| `deliverables/disavow-farison-69.13-network.txt` | Full 287-domain network (recommended review scope). |
| `data/refdomains-69.13.csv` | Raw domain;ip evidence for the network. |
| `deliverables/farison-tab08-backlink-assessment.md` | This report. |

**Both disavow files are drafts and have NOT been submitted to Google Search Console.** Per the brief, submission waits on confirmation from Harbinger and the partner. Also note the brief's internal deadline ("end of October 2026") has already passed as of 2026-11-03 — flag the slip when you circulate this.

---
*Verification performed against Ahrefs API v3 and Semrush Analytics API on 2026-11-03. Monetary/authority metrics as reported by each provider; figures are provider estimates and differ between tools by design.*
