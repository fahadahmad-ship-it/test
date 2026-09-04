# Master Lawn — Backlink Audit, Disavow & Authority Rebuild Plan

**Client:** Master Lawn — https://www.masterlawn.com/
**Prepared:** 2026-09-04
**Scope:** (1) Backlink Profile Audit, (2) Disavow Preparation & Submission, (3) SEO Baseline Benchmarking, (4) Authority Link Acquisition
**Data sources:** Ahrefs API v3, Semrush, Google Search Console (client to grant access)

---

## 0. TL;DR — What the data already tells us

A baseline pull on 2026-09-04 shows a profile that is **wide but weak and contaminated**:

| Metric (Semrush) | Value | Read |
|---|---|---|
| Authority Score (AS) | **23** | Low; inflated by spam volume, not earned trust |
| Referring domains | **1,167** | High relative to authority/organic footprint |
| Total backlinks | **3,613** | — |
| Organic keywords (US) | **2,525** (104 in top 3) | Real but modest footprint |
| Organic traffic | **~2,391 / mo** (~$10,324 value) | Modest for the link count |

**The tell:** 1,167 referring domains but Authority Score 23, with ~90% of those domains at AS ≤6, is the fingerprint of a **manipulated / spam-injected link profile** — not organic authority. A sample of the profile confirms it directly:

- **Money-anchor spam** advertising link-selling services *through* Master Lawn's own backlinks — e.g. *"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service masterlawn.com … Buy Backlinks Online Cheap"* and *"Take masterlawn.com to page one with high-quality backlinks, guest posts…"*.
- **Telegram / "darkside links"** and **gambling** anchors (`m98ufa.com`, `hotonlinegaming.com`, `@happygrannypies`).
- A large cluster of **PBN / link-shop domains** (`buybacklinks.agency`, `backlinker.shop`, `seolinkpro.shop`, `rankxlinks.shop`, `premiumseolinks.shop`, dozens of `*.shop`), most with **high DR but zero organic traffic** — the classic PBN signature.
- Much of it **first seen in 2025–2026 and still arriving**, i.e. an **active** contamination stream (negative-SEO pattern and/or fallout from a prior low-quality link vendor).
- A parallel target, **`masterlawninc.com`**, is being spammed with identical templates — confirm whether this is a client-owned/legacy domain and fold it into the audit if so.

**Implication for sequencing:** the disavow (Task 2) is not cosmetic cleanup — it is risk mitigation against an ongoing spam stream, and it must precede or run alongside authority rebuilding (Task 4) so new, clean links aren't diluted by toxic noise. Because the injection is ongoing, disavow is a **recurring** process for this client, not a one-off.

> ⚠️ **Disavow is a last resort with real downside.** Google's guidance is that most sites never need one, and disavowing links Google already ignores can *remove* value if done carelessly. Every step below is built around **conservative, evidence-based classification and QA** so we only neutralize links that are genuinely harmful (or the target of a manual action), never healthy ones.

---

## Task 1 — Backlink Profile Audit

**Objective:** Review and classify *all* referring domains (Ahrefs + Semrush, de-duplicated) by **trust, relevance, and language**, producing a defensible, auditable classification that feeds the disavow decision and the rebuild strategy.

### 1.1 Data collection
1. **Ahrefs** — export live + recently-lost referring domains (`site-explorer-referring-domains`) with: `domain, domain_rating, traffic_domain, links_to_target, dofollow_links, is_spam, is_dofollow, first_seen, last_seen, ip_source, positions_source_domain, languages`.
2. **Semrush** — `backlinks_research` referring-domains export with Authority Score, category, first/last seen, and its own toxicity indicators.
3. **Google Search Console** — Links report (`Top linking sites`) as the third source. GSC reflects what Google actually attributes; a domain present in GSC carries more weight in the disavow decision.
4. **Merge & de-dupe** to a single master sheet keyed on root domain. Reconcile the ~1,111 (Ahrefs live) vs Semrush vs GSC counts; note source coverage per domain (which tools see it).

### 1.2 Classification framework (three axes → one verdict)

Each referring domain is scored on three axes, then bucketed:

**A. Trust / Quality**
- Authority: Ahrefs DR + Semrush AS, **cross-checked against organic traffic**. *High DR + ~0 traffic = PBN red flag, not authority.*
- Spam flags: Ahrefs `is_spam`, Semrush toxicity score, all-nofollow/UGC-only patterns.
- Footprint: link volume from the domain, sitewide vs contextual, homepage vs deep page, dofollow vs nofollow.
- Domain shape: spammy TLDs (`.shop`, `.click`, `.icu`, `.top`, `.xyz`, `.website`, `.space`, `.store`) used for link-selling; expired/repurposed domains; keyword-stuffed or randomized hostnames (`hzdlpq.com`, `kgzxkf.com`).

**B. Relevance**
- Topical: is the linking site related to lawn care, landscaping, home services, local business, horticulture, pest/mosquito control? Or unrelated (crypto, gambling, adult, generic "SEO services", watches, essay mills)?
- Geographic: Master Lawn serves the **Memphis TN metro** (Germantown, Collierville, Bartlett) and **Olive Branch MS**, plus a **Huntsville AL** service area. US/local relevance is a positive trust signal; irrelevant foreign geos are neutral-to-negative.

**C. Language**
- Detect referring-page language (Ahrefs `languages` + manual spot-check). Non-English pages linking with English commercial or lawn-care anchors to a hyper-local US service business are almost always spam/PBN and weigh toward toxic.

**Verdict buckets:**
| Bucket | Definition | Action |
|---|---|---|
| 🟢 **Trusted / Keep** | Relevant, real traffic, editorial/natural, English or legit local | Keep; mine for outreach lookalikes (Task 4) |
| 🟡 **Neutral / Monitor** | Low value but not harmful (scrapers, low-DR directories, syndication) | No disavow; monitor |
| 🔴 **Toxic / Disavow candidate** | PBN, link-shop, spam anchors, gambling/adult, DR-inflated zero-traffic, foreign-lang commercial spam | → Task 2 pipeline |
| ⚫ **Manual-review** | Ambiguous; needs human eyes before any action | Analyst decision, logged |

### 1.3 Method
- **Programmatic first pass:** auto-flag on objective rules (is_spam=true; DR>30 & traffic=0; spam-TLD + money/SEO anchor; gambling/adult keyword anchors; sitewide low-DR footprints). This alone will surface the bulk of the ~1,100 domains as candidates.
- **Anchor-text analysis** (`site-explorer-anchors`): quantify branded vs money vs junk anchors. Injected sales-pitch and Telegram anchors are unambiguous toxic markers.
- **IP / footprint clustering:** group by `ip_source`, registration date, and naming pattern to catch PBN networks (e.g. the `seoexpress.*` and `*.shop` families) as clusters rather than one-by-one.
- **Human QA second pass:** sample-verify auto-flags and adjudicate ⚫ manual-review before anything reaches the disavow file.

### 1.4 Deliverables
- `backlink-classification-master.csv` — every referring domain with all three axis scores, verdict, evidence, and source coverage (Ahrefs/Semrush/GSC).
- **Audit summary deck/memo** — profile health, % toxic, cluster map, root-cause hypothesis (bad vendor vs negative SEO vs both), before/after DR & anchor charts.
- Feeds directly into Task 2.

### 1.5 Acceptance criteria
- 100% of referring domains from all three sources classified (no blanks).
- Every 🔴 toxic verdict carries a machine-readable reason code + evidence.
- Two-analyst sign-off on the toxic list before Task 2.

---

## Task 2 — Disavow File Preparation & Submission

**Objective:** From the Task 1 toxic set, build, QA, and submit a Google-compliant disavow file — conservatively, and repeatably given the ongoing injection.

### 2.1 Toxicity criteria (a domain must meet clear, logged thresholds)
Disavow when one or more hold, **and** there is no offsetting legitimacy:
- Ahrefs `is_spam=true` **or** Semrush toxicity above threshold, corroborated by a second signal.
- Link-selling / PBN footprint: spam-TLD clusters, "buy backlinks / rank first page / DA-PA" anchors, guest-post-farm networks.
- Irrelevant high-risk verticals: gambling, adult, crypto, pharma, essay mills, counterfeit goods.
- DR/AS-inflated with ~0 organic traffic **and** unnatural anchor/footprint.
- Foreign-language pages linking with commercial/lawn anchors inconsistent with a local US service business.
- Obvious negative-SEO injection (bulk identical anchors, dark-web/Telegram anchors).

**Do NOT disavow:** relevant local citations & directories, legitimate low-DR small business/blog links, nofollow links that are merely low-value, or anything ambiguous — send those to monitor, not the file. When in doubt, leave it out.

### 2.2 Domain-level vs URL-level
- Default to **`domain:`** entries for spam/PBN networks (cleaner, covers sitewide and future URLs on the same host).
- Reserve URL-level lines for one-off toxic links on otherwise-legitimate domains.

### 2.3 QA of the final list
1. **Format validation** — plain-text UTF-8, one entry per line, `domain:` syntax correct, comments (`#`) for provenance, ≤ file-size/line limits, no duplicates, no live/valuable domains caught by mistake.
2. **False-positive sweep** — diff the disavow set against 🟢/🟡 buckets and against GSC top-linking sites; pull anything relevant/branded/real-traffic back out.
3. **Second-analyst review + client sign-off** — explicit approval before submission (irreversible-in-effect; changes take weeks to reprocess).
4. **Snapshot** the exact submitted file to version control with date.

### 2.4 Submission
- Submit via **Google Search Console Disavow Tool** on the correct property (confirm domain vs URL-prefix property; include `www`/non-`www`/http/https coverage as needed).
- If **`masterlawninc.com`** is client-owned, prepare and submit a separate file for that property.
- **Note:** disavow addresses Google penalty/algorithmic risk; it does **not** remove links from Ahrefs/Semrush or stop new spam. Pair with GSC **manual-actions** monitoring; file a reconsideration request only if a manual action exists.

### 2.5 Cadence (because injection is ongoing)
- Re-run classification → disavow refresh **monthly** (or on traffic/ranking anomaly).
- The disavow file is **cumulative** — always re-upload the *complete* list, never a delta.

### 2.6 Deliverables
- `disavow-masterlawn-YYYY-MM-DD.txt` (submitted, versioned) + `disavow-changelog.md`.
- Submission confirmation screenshot + QA sign-off log.
- A seeded starter candidate list is provided in `disavow-candidates-sample.txt` (**QA-pending, not final**).

### 2.7 Acceptance criteria
- File passes format validation and false-positive sweep with two-analyst + client sign-off.
- Submitted to the correct property/properties; confirmation archived.

---

## Task 3 — SEO Baseline Benchmarking

**Objective:** Freeze a "before" snapshot so the impact of disavow + rebuild is measurable. **Captured 2026-09-04** — see `baseline-benchmark-2026-09-04.md`.

### 3.1 What we baseline
- **Authority:** Semrush Authority Score (23), ref-domain counts, backlink counts, dofollow ratio, anchor-text distribution (branded vs money vs junk), % toxic.
- **Rankings:** target-keyword positions (local "lawn care / fertilization / weed control / mosquito control + Germantown/Collierville/Bartlett/Memphis TN, Olive Branch MS, Huntsville AL"), top-3 / top-10 counts, share of the local pack; set up **Semrush Position Tracking / Ahrefs Rank Tracker** for ongoing capture.
- **Organic traffic & value:** Semrush est. traffic (~2,391/mo, ~$10,324 value) and, once granted, **GSC** clicks/impressions/CTR/avg-position + **GA4** organic sessions/conversions (the source of truth).
- **Visibility:** organic keyword count (278; 27 in top 3), top pages, top-page dependency.

### 3.2 Method & cadence
- Snapshot **now** (done), then **monthly**; hold a formal **before/after** comparison at 90 and 180 days post-disavow.
- Store snapshots as dated rows in one tracking sheet for clean trend lines; annotate the disavow submission date on all charts (disavow effects lag weeks–months).

### 3.3 Deliverables
- `baseline-benchmark-2026-09-04.md` (this snapshot) + an ongoing tracking sheet.
- Rank-tracker project configured with the local keyword set and competitors.

### 3.4 Acceptance criteria
- All metrics captured with source + date; rank tracker live; GSC/GA4 access confirmed (or flagged as a client dependency).

---

## Task 4 — Authority Link Acquisition

**Objective:** Secure **1–2 high-quality, relevant** local/industry backlinks to begin rebuilding genuine trust and dilute the spam signal with real authority.

### 4.1 Targeting principles
- **Relevance > raw DR.** A DR-30 Memphis home-services or horticulture site beats a DR-70 generic "SEO" domain every time — and looks nothing like the toxic profile.
- **Real organic traffic required** (screen out the DR-inflated/zero-traffic pattern that poisoned this profile).
- **Editorial / earned**, never bought — no guest-post farms, no link-shops, no PBNs. Rebuilding trust while buying links is self-defeating.

### 4.2 Prospecting (highest-probability first)
1. **Local / geo-relevant:** Memphis/Germantown/Collierville/Bartlett & Olive Branch MS chambers of commerce, "best lawn care in Memphis" local roundups, local news & lifestyle (Memphis Commercial Appeal, local mags), BBB, and genuine local business associations. Huntsville AL equivalents for that service area.
- **Industry / topical:** lawn-care & landscaping associations (e.g. NALP), turf/horticulture resources, supplier & manufacturer "where to buy / find a pro" pages, non-competing partner referrals (irrigation, pest control, tree services).
3. **Relationship & unlinked mentions:** vendors, suppliers, local sponsorships/events, and existing unlinked brand mentions converted to links.
4. **Content-led / digital PR:** leverage existing ranking assets (the watering/fertilizing and "dead vs dormant grass" blog posts already attract links) — pitch data/seasonal lawn-care tips to local media for earned coverage.
5. **Competitor link intersection:** mine 🟢 links of local competitors (Ahrefs Link Intersect / `rank-tracker-competitors`) for realistic, relevant targets.

### 4.3 Execution
- Build a vetted prospect list (each passes the Task-1 trust/relevance/language test *before* outreach).
- Personalized outreach with a genuine value hook (local expertise, seasonal data, sponsorship, resource contribution).
- Track outreach → placement in a CRM/sheet; verify each secured link is indexed, dofollow-where-appropriate, and on a relevant page.

### 4.4 Deliverables
- Vetted prospect + outreach tracker.
- **1–2 secured, verified, relevant backlinks** with screenshots/URLs and rationale.

### 4.5 Acceptance criteria
- Each secured link passes the same trust/relevance/language bar used to *reject* the toxic ones; live, indexed, contextually placed.

---

## Sequencing, ownership & risks

### Recommended sequence
1. **Week 1:** Access (GSC, GA4, Semrush/Ahrefs projects) + Task 3 baseline (partly done) + start Task 1 collection.
2. **Weeks 1–2:** Task 1 classification (programmatic + human QA).
3. **Week 2–3:** Task 2 disavow build, QA, sign-off, submit.
4. **Weeks 2–6 (parallel & ongoing):** Task 4 authority acquisition; Task 3 monitoring.
5. **Monthly:** re-audit → disavow refresh (ongoing injection) → benchmark snapshot.

### Dependencies / client asks
- GSC + GA4 access; confirm ownership of **`masterlawninc.com`** and any legacy domains; approval authority for the disavow sign-off.

### Risks & mitigations
- **Over-disavowing** healthy links → conservative criteria, false-positive sweep, two-analyst + client sign-off.
- **Ongoing spam injection** → treat disavow as recurring; monitor manual actions; consider reporting a negative-SEO pattern.
- **Disavow ≠ instant recovery** → effects lag weeks–months and won't fix non-link issues; set expectations and annotate timelines.
- **Wrong GSC property** → verify domain vs URL-prefix and protocol/host coverage before submitting.

---

## Appendix A — Evidence sample (from 2026-09-04 pull)

**Toxic anchor examples (verbatim):**
- "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service masterlawn.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap"
- "Take masterlawn.com to page one with high-quality backlinks, guest posts, on-page and local SEO…"
- "Before finding SEOExpress.org, masterlawn.com seemed invisible on search engines…" (227 ref-domains, is_spam=true)
- "LINKS FOR www.masterlawn.com TELEGRAM @happygrannypies" / "JOIN OUR TELEGRAM …/darksidelinks"

**Toxic domain examples (DR shown; note ~0 traffic):** `buybacklinks.agency` (DR69), `backlinker.shop` (DR73), `rankyour.website` (DR74), `a2zseoarticles.com` (DR62), `seolinkpro.shop` (DR52), `premiumseolinks.shop` (DR52), `seoexpress.*` cluster, `m98ufa.com` (gambling), `hotonlinegaming.com` — full list in the classification export.

*(Figures are point-in-time Ahrefs/Semrush estimates as of 2026-09-04 and will drift.)*
