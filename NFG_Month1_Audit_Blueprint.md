# NFG Month-1 Foundation Audit — Workbook Blueprint

**Client (target):** nationalfosteringgroup.co.uk (NFG)
**Agency:** SUSO · **Snapshot date:** 2026-09-22 · **Database/region:** UK
**Deliverable:** Off-site competitor analysis · Backlink-gap target list · Keyword analysis
**Month-1 scope:** Foundation only — no link placements, no content shipped. This is the diagnostic + target map that Month 2+ outreach executes against.

---

## Governance — the two rules that bind every cell

1. **Metric firewall (Semrush-only).** Every *reported metric* — Authority Score (AS), follow/nofollow split, search volume, KD, traffic, CPC, and any number feeding a ranking/formula — is **Semrush-sourced only**. One consistent yardstick. Ahrefs DR/UR/traffic never appear in a client-facing cell.
2. **Lists may be pooled (Ahrefs + Semrush).** Raw *lists* of backlinks/referring domains that feed the prospect database may be pooled from both engines to widen coverage. But once pooled, every row is **re-scored against Semrush AS** before it enters any ranking. A pooled row with no Semrush AS is flagged `AS_source = unmatched` and kept in Raw only (or re-queried in Semrush), never scored on Ahrefs numbers.

Supporting discipline: canonical domain normalization (eTLD+1, strip www/protocol/trailing slash, lowercase) applied identically everywhere; single dated snapshot window; every column names its exact source report + region filter; spam/excluded rows retained in Raw with a reason, never silently deleted.

**Competitor set (9):** thefca.co.uk · thefosteringnetwork.org.uk · capstonefostercare.co.uk · ispfostering.org.uk · fosterplus.co.uk · fosteringpeople.co.uk · swiisfostercare.com · compassfostering.com · orangegrovefostercare.co.uk
Tag `thefca` and `thefosteringnetwork` as **Sector Body** (high-authority, informational — benchmarked but weighted separately); the other 7 as **Commercial IFA** (direct money-term + regional rivals).

---

## Workbook: `NFG_Month1_Foundation_Audit_2026-09-22_v1.xlsx` — 12 tabs

Flow: exec answer first → NFG baseline → competitor baseline → gap analysis → regional whitespace → the one rolled-up action list → evidence/appendix.

| # | Tab | Purpose | Audience | Data |
|---|-----|---------|----------|------|
| 0 | README & Methodology | Scope, sources, definitions, caveats, sign-off | Both | — |
| 1 | Executive Scorecard | 6–10 headline numbers + 3 "so what" takeaways + NFG-vs-field visuals | Exec | SR |
| 2 | Competitor Benchmark | One row per domain: authority, links, ref domains, traffic, keywords | Exec+Analyst | SR |
| 3 | NFG Backlink Profile | Client current off-site state (critical audit) | Analyst | SR |
| 4 | NFG Keyword Profile | Client current ranking state (critical audit) | Analyst | SR |
| 5 | Backlink Gap Target List | Domains linking to competitors, not NFG — scored | Analyst | Pooled lists, SR score |
| 6 | Keyword Gap | Keywords competitors rank for, NFG doesn't/weakly | Analyst | SR |
| 7 | Regional Whitespace Map | UK region link matrix + local demand vs NFG presence | Exec+Analyst | Pooled lists + SR |
| 8 | Anchors & Toxicity | NFG anchor mix + spam/disavow flags | Analyst | SR |
| 9 | Competitor Link Detail | Per-competitor referring-domain evidence (feeds 5 & 7) | Analyst | Pooled lists |
| 10 | ★ Priority Target List | Cross-tab rolled-up single Month-2+ action queue | Exec+Analyst | Derived |
| 11 | Data Dictionary & Raw Exports | Column definitions, source attribution, dated raw dumps, changelog | Analyst | Both |

Legend: **SR** = Semrush · **AH** = Ahrefs · **Pooled** = AH+SR list, SR-scored.

---

## Tab 0 — README & Methodology
Non-tabular blocks: Project & client · Reporting period + `Snapshot date: 2026-09-22` cell (referenced by every other tab header) · Data-source rule (SR-only metrics / pooled-for-lists) · Region = UK · Competitor set with Sector-Body vs Commercial-IFA tags · Metric definitions (AS, DR, referring domain, gap, whitespace, toxic tail) · Caveats box · SUSO contact & sign-off.

## Tab 1 — Executive Scorecard (SR)
KPI band + visuals over this grid: `Metric · NFG Value · Field Median (=MEDIAN of competitors) · Field Best (=MAX) · NFG Rank /10 (=RANK) · Gap to Median · Percentile · Trend ▲▼`.

**Headline numbers:** Authority Score · Referring Domains · Total Backlinks · Organic Keywords (UK) · Est. Organic Traffic (UK) · Top-3 keywords · Backlink-gap opportunities found (+ "consensus" ≥4-competitor count) · Keyword-gap opportunities (Missing/Weak/Untapped split) · Regional whitespace regions flagged High · Dofollow ratio / toxic-anchor exposure.

**Visuals:** horizontal bar of 10 domains on Composite Strength (NFG highlighted → "NFG sits Nth of 10") · bullet/gap bars per KPI vs median & best · UK region mini-map coloured by whitespace · opportunity funnel (backlink → keyword → priority actions).

**Three "so what" takeaways (prose):**
- Off-site vs on-site: which is the primary constraint, with the referring-domain gap-to-median number.
- N high-value backlink targets already trusted by 4+ competitors but missing from NFG — fastest-consensus wins.
- M UK regions with strong fostering demand where NFG is weak and competitors present — highest-leverage play.

*(Colour: follow the `dataviz` accessible palette, swap in SUSO brand colours; colour-blind-safe, legible light/dark; never colour alone — pair with icon/text.)*

## Tab 2 — Competitor Benchmark (SR, 10 rows)
Backbone pull: **`competitors_research → backlinks_comparison`** (one report, one date, all 10 → guaranteed comparability), plus `domain_overview → domain_rank` and `organic_research` for keyword/traffic columns.

`Domain · Is_NFG · Authority_Score · Total_Backlinks · Referring_Domains · Referring_IPs · Referring_Subnets · Follow_% · Follow_RefDomains_% · Backlinks_per_RefDomain · Text/Image/Form/Frame_% · Toxic_Tail_% (AS 0–10 ref domains ÷ total, via backlinks_ascore_profile) · Topical_Relevant_% (backlinks_categories_profile) · Gov_Edu_RefDomains · New_RefDomains_12m · Lost_RefDomains_12m · Organic_Keywords_UK · Est_Organic_Traffic_UK · Est_Traffic_Cost_£ · Top3_Keywords · Index_AS · Index_RefDomains (value ÷ cohort median ×100) · Rank_AS /10 · Rank_RefDomains /10 · Composite_Strength (min-max-normalized mean of AS, ref domains, keywords, traffic) · Distinctive_Strength (analyst note) · Snapshot_Date`.
Conditional: NFG row bold+highlighted; colour scale on Composite; data bars on ref domains & traffic. Report gap-to-median and gap-to-leader on AS and Referring Domains — the two numbers that frame the deliverable.

## Tab 3 — NFG Backlink Profile (SR, deep)
Reports: `backlinks_overview · backlinks · backlinks_refdomains · backlinks_anchors · backlinks_ascore_profile · backlinks_categories(_profile) · backlinks_historical · backlinks_geo · backlinks_tld · backlinks_pages · backlinks_refips` (+ AH `broken-backlinks` and SR last-seen for reclamation list).

**Summary block:** AS · total backlinks · ref domains · follow% (link *and* referring-domain level) · AS-band distribution · anchor concentration · geo split · 12-mo velocity · new/lost 90d.
**Row-per-referring-domain:** `Referring_Domain · Domain_AS · Backlinks_from_Domain · First_Seen · Last_Seen · Follow_Flag · Link_Type · Target_URL (backlinks_pages) · Category · Region (inferred, §Tab7) · TLD · Toxicity_Score · Spam_Flag · Reason · Status (Live/Lost/Broken)`.

**Critical-reviewer checklist (answer each with evidence rows):** velocity anomalies/spikes (month + cause) · anchor over-optimization (money-anchor %, top-5 concentration) · toxic/low-AS clusters + toxic-tail % · lost/broken mid-high-AS links (reclamation backlog) · follow ratio both levels · single-domain link inflation (backlinks-per-domain outliers) · topical-relevance shortfall · link-equity concentration (homepage vs deep/location pages) · IP/subnet concentration (PBN) · geo alignment for a UK-only business.

**Vertical thresholds (UK fostering — low-authority, high-trust, local-intent; set relative to the cohort):** follow ratio healthy ~50–75% (>90% = manipulation smell, <40% = weak) · any single money anchor >10–15% or top-5 money anchors >35% = over-optimization · AS profile should be pyramid-shaped, report % ref domains in AS 0–10 as "toxic tail" · `.gov.uk/.ac.uk/.nhs.uk/.org.uk` presence = positive trust marker and a target class.

## Tab 4 — NFG Keyword Profile (SR Organic Research, DB=uk)
Master pull `organic_research → resource_organic` **positions 1–100** (the quick-win band lives in 11–30); totals from `domain_rank`; de-dup from `resource_organic_unique`; subdomain split from `domain_organic_subdomains`; trend from `resource_rank_history`.

Row-per-keyword: `Keyword · Position · Previous_Position · Position_Band (1–3/4–10/11–20/21–30/31–50/51–100) · Search_Volume_UK · Est_Traffic · Traffic_% · CPC_£ · Competition · SERP_Features · Ranking_URL · URL_Bucket (homepage/money/allowance/types/regional/blog/careers) · Branded_Flag · Sub-brand/Region_Tag · Intent_Tier · Geography (National vs Regional+place) · Cluster (money/regional/allowance/eligibility/informational) · Quick-Win_Flag (pos 11–30 & commercial) · Cannibalization_Flag (2+ NFG URLs rank same keyword) · Decline_Flag · Notes/Action`.

**Brand structure to encode** (tag as branded, but region-tagged): NFA / NFA North → Yorkshire, Lincolnshire · Reach Out Care → North East, Cumbria · plus every "Fostering in [city]" location page — enumerate the full trading-name/location list *before* the pull (an incomplete brand regex is the #1 way branded traffic gets miscounted).

**Critical checks:** branded-vs-non-branded share of keywords *and* traffic (over-reliance on brand = headline risk for a lead-gen client) · thin coverage of money terms ("become a foster carer", "fostering agencies", "foster carer pay/salary", "fostering allowance", "apply to foster", "fostering near me") · cannibalization · quick-wins in 11–30 · declines on money/regional terms · traffic concentration · zero-traffic ranking bloat · intent/landing-page mismatch.
**Summary block:** total & unique keywords · traffic & cost · branded/non-branded counts+traffic · counts by band/intent/cluster/URL-bucket · national vs regional · money-terms ranked top-10 / 11–30 / not-ranked scorecard · cannibalization & decline counts · top-N traffic concentration % · subdomain split.

## Tab 5 — ★ Backlink Gap Target List (pooled lists, SR-scored) — core deliverable
**Spine:** `competitors_research → backlinks_matrix` (referring domain × per-target link counts — natively gives "# competitors linking" and the NFG-linked flag in one object). **Widen** with per-competitor `backlinks_refdomains` (SR) + Ahrefs `referring-domains`. **Exclusion set** = NFG's own referring domains (SR + AH).

**Method:** normalize domain key → pool + de-dup (track `Seen_in_Semrush`/`Seen_in_Ahrefs`) → record which competitors each domain links to → subtract NFG's set (pure gap) → **re-score in Semrush AS** (`AS_source = matched/unmatched`) → enrich (link type, category, region, first-seen, backlinks-per-domain) → spam screen (§Tab8 rubric) → score & sort → segment by acquisition type + region.

Columns: `Referring_Domain · Seen_in_Semrush · Seen_in_Ahrefs · Authority_Score · AS_Source · Num_Competitors_Linking (1–9) · Competitor_Targets · Links_to_NFG (=N) · Dominant_Link_Type · Category · Relevance_Score (topical×regional 0–1) · Region · Region_Signal · Region_Confidence · Backlinks_per_Domain · First_Seen · Spam_Flag · Toxicity_Score · AS_norm · CompetitorCount_norm · LinkType_Score · Priority_Score · Tier (1/2/3) · Acquisition_Type · Outreach_Notes · Snapshot_Date`.

**Priority formula (Semrush-scored, tunable weights):**
`Priority = 0.30·AS_norm + 0.30·CompetitorCount_norm + 0.20·Relevance + 0.20·LinkType − SpamPenalty(gate)`
where AS_norm = AS/100; CompetitorCount_norm = #competitors/9 (many competitors, not NFG = proven-relevant near-certain miss); Relevance = topical (fostering/childcare/social-care/education/local-gov/UK-news = 1, adjacent 0.5, off-topic 0) blended with regional bonus for NFG whitespace (**Yorkshire & Humber, North East**); LinkType = follow-editorial/gov/edu 1, follow-directory 0.6, nofollow 0.3. Hard-spam excluded entirely. Tie-breaks: competitor count → AS → whitespace region → follow → freshest.
**Tiering:** T1 quick wins (high score + realistic: directories, citations, membership bodies, unlinked mentions) · T2 editorial/news outreach · T3 aspirational high-AS/gov/edu. Rows linked by ≥4 competitors flagged **consensus targets**.

## Tab 6 — Keyword Gap (SR `competitors_research → domain_domains`, DB=uk)
5-domain ceiling → NFG anchors every call + 4 rivals. **Batches:** A = NFG + Capstone + ISP + FosterPlus + FosteringPeople · B = NFG + Swiis + Compass + Orange Grove + (Capstone as bridge) · C = NFG + theFCA + FosteringNetwork + 2 strongest IFAs · D (optional) = NFG + newly-confirmed competitors (LA portals/charities/jobs boards). Run **missing** (rivals rank, NFG absent) *and* **weak** (NFG >15/20 while rival top-10). Dedup keywords across batches; pull KD/intent/CPC once per unique keyword via `keyword_research → overview` to avoid drift.

Columns: `Keyword · Cluster · Place_Tag · Search_Volume_UK · KD · KD_vs_NFG_reach · CPC_£ · Intent · Intent_Multiplier (×3 transactional / ×2 high-commercial / ×1 info) · NFG_Position · Gap_Type (Missing/Weak/Untapped) · Rival_Positions · Rival_Density (# of 9 ranking) · Best_Rival+Position · Quick-Win_Flag · Priority_Score · Regional_Pairing_Flag · Recommended_Action (new page/optimize/add FAQ/internal link) · Target_URL · SERP_Features`.
**Opportunity score** = (normalized Volume × Intent multiplier) ÷ KD band, adjusted for rival density + quick-win. Clusters: money · regional · allowance/pay · eligibility · informational (+ question flag via `keyword_research → questions`).
**Summary block:** total gap keywords + addressable UK volume by cluster · Missing/Weak/Untapped counts · winnable-vs-stretch by KD band · top-20 Month-1 shortlist · Competitor Landscape (per-domain type, keywords, traffic, common keywords with NFG, # terms beating NFG, trend) from `domain_organic_organic` — used to **validate the true organic competitor set** (Confirmed / Weak / Not-a-competitor / New).

## Tab 7 — Regional Whitespace Map (pooled lists + SR)
**View D1 — Link matrix:** rows = 12 UK regions + Non-UK/Unknown, cols = 10 domains; cells = count of that domain's **top-100 referring domains by AS** (SR `backlinks_refdomains`, consistent cut across all 10) in that region, plus a parallel %-of-top-100 cell so big domains don't visually dominate.
**View D2 — Classified rows:** `Referring_Domain · Counted_for_Domain · AS · Region · Region_Signal · Region_Confidence (H/M/L) · Links_to_NFG · Num_Competitors_Linking · Spam_Outlier_Flag+Reason · In_Gap_List`.
**View — Local demand vs presence:** `UK_Region/City · Local_Search_Demand (SR geo keyword volume) · NFG_Ranking_Presence · Competitors_Present · Gap_Domains_in_Region (from Tab 5) · Whitespace_Score · Recommended_Focus`.

Region classification is **manual from domain/brand/outlet/gov/edu signals, not IP-geo** (Cloudflare/US CDNs make IP-geo unreliable); every call records the evidence string + confidence; low-confidence → Unknown. Known context to confirm/refresh: NFG strength = **North West + Scotland**; whitespace = **Yorkshire & Humber + North East** (both proven attainable by theFCA/FosteringNetwork, and both inside NFG's real service geography via NFA North and Reach Out Care — so pages/links can be built on genuine local proof).
**Joint priority:** regions scoring keyword whitespace **and** link deficit become the Month-1 regional priorities (feeds Tab 10 via the Regional_Pairing_Flag).

## Tab 8 — Anchors & Toxicity (SR)
**Anchors** (`backlinks_anchors`): `Anchor_Text · Anchor_Type (branded/money/generic/naked-URL/image-alt) · Backlinks · Referring_Domains · %_of_Total · Over_Optimization_Flag`.
**Toxicity** (`backlinks_refdomains + backlinks_refips + backlinks_ascore_profile` + rubric): `Referring_Domain · AS · Toxicity_Score (0–1) · Trigger_Reasons · Hard_Exclude/Soft_Flag · Disavow_Candidate · Shared_Subnet_Group`.
**Rubric — Hard-exclude:** AS 0–5 no relevance · adult/gambling/pharma/payday/off-topic foreign farms · PBN/subnet signatures · volume-inflation outliers (backlinks-to-one-target ≥~1,000 or >20× cohort median — the `hu17.net → 26,791 links to Capstone` archetype) · scraper "information point" domains · paid/reciprocal sitewide directories. **Soft-flag (keep, penalize):** AS 6–15 but relevant · 100%-nofollow · high backlinks-per-domain · Non-UK/Unknown · dying sites (collapsing `backlinks_historical`). Disavow candidates roll to Tab 10 as a capped defensive block.

## Tab 9 — Competitor Link Detail (pooled evidence)
Long format: `Competitor · Referring_Domain · Referring_URL · Target_URL · Anchor · Link_Type · Domain_AS (SR) / DR (AH, evidence only) · First_Seen · Region · Spam_Flag · Also_Links_to_NFG · Source (AH/SR/AH+SR) · Dedup_Key`. Raw evidence underpinning Tabs 5 & 7; dedup collapses on `normalized-refdomain × competitor`, keep max metric values, record pooled source.

## Tab 10 — ★ Priority Target List (cross-tab roll-up)
Collapses Backlink Gap (5) + Keyword Gap (6) + Regional Whitespace (7) + defensive Toxicity (8) into ONE ranked Month-2+ queue.
`Rank · Action_Type (Backlink outreach / Content-for-keyword / Regional push / Disavow) · Target (domain|keyword|region) · Rationale · Supporting_Metric_1 · Supporting_Metric_2 · Region_Tag · Effort (L/M/H) · Unified_Priority_Score · Owner/Status (editable) · Month_Target (editable)`.
**Unified score (0–100):** normalize each source's native score to 0–1, then `0.45·source_score + 0.20·competitor-consensus + 0.20·regional-whitespace-multiplier + 0.15·(1−effort)`. Backlink and keyword items compete on one scale; regional whitespace multiplies items in high-demand/low-NFG regions; disavow enters as a small flagged defensive block. Sort by score desc, then effort asc (quick wins float up). Top 20–30 shaded "Month 2 shortlist."

## Tab 11 — Data Dictionary & Raw Exports
**A — Dictionary:** every column across all tabs → name · tab · definition · type · source (SR report / AH report / Derived) · formula · units. **B — Raw index:** `Domain · Engine · Report · Pull_Date · Region_Filter · Row_Count` per sub-sheet, including `AS_source=unmatched` and hard-excluded spam (kept for transparency, never scored). **C — Changelog:** version · date · editor · change.

---

## Data hygiene, formatting & handoff
- **Normalization/dedup:** eTLD+1 everywhere; dedup key = normalized refdomain (× competitor in Tab 9); keep raw URL + normalized domain.
- **Firewall control:** metric cells Semrush-only; pooled lists carry a Source column; AS and DR never in one column.
- **Snapshot:** single README date referenced by all headers; raw exports filenamed with tool + pull date.
- **Formatting:** freeze header row + first ID column; auto-filter, pre-sorted by primary score; NFG one accent colour, competitors neutral; green/amber/red only for scores/flags; data bars on volume/authority; legend on README + compact on scored tabs; caveats box on README + Scorecard; ISO dates, £, thousands separators; lock formula columns, leave Owner/Status/Month editable; tab colours group exec / analyst / appendix.
- **File:** written to disk as `.xlsx` (per repo rule — no Artifacts/design canvases). Version in filename + changelog.

## Build sequence (dependency-ordered)
1. **Pulls (parallel):** SR `backlinks_comparison` + `domain_rank` + per-domain `backlinks_overview/anchors/ascore_profile/historical` (all 10) → Tabs 2,3,8. SR `resource_organic` (all 10, UK) → Tabs 4,2. Pooled AH+SR referring-domain lists + `backlinks_matrix` → Tab 9. SR `domain_domains` batches → Tab 6. SR geo keyword volumes → Tab 7.
2. **Baselines:** Tab 2, then Tabs 3 & 4.
3. **Raw + dedup + spam:** load Tab 9, normalize, exclude spam, dedup — **must precede Tab 5**.
4. **Gap analysis:** Tab 5 (= Tab 9 minus NFG's own domains, AS-scored) · Tab 6 (batches joined to Tab 4) · Tab 8.
5. **Regional:** Tab 7 (top-100 classification matrix + geo demand + region tags from Tab 5).
6. **Roll-up:** Tab 10 (needs 5,6,7,8 final & scored).
7. **Exec + docs:** Tab 1 (needs Tab 2 + counts from 5/6/7) · Tabs 0 & 11 last.

**Critical path:** pooled lists → Tab 9 (normalize+dedup+spam) → Tab 5 → Tab 10 → Tab 1.

---

## Caveats to state in the deliverable
- Semrush metrics are third-party **estimates** (volume, KD, position, traffic modelled, not Google-truth); directional, snapshot-dated; not blended with GA/GSC in reported columns.
- **Index coverage:** neither engine indexes the whole web; pooling widens but the database is a sample — absence of a link ≠ proof it doesn't exist.
- **Two-yardstick cost:** Ahrefs-only domains without a Semrush AS are excluded from scored ranking (Raw only) — accepted to keep the yardstick consistent. AS ≠ DR, never compared in one cell.
- **Regional classification is manual & inferential** (IP-geo unreliable); `Region_Confidence` flags uncertainty; some domains stay Unknown by design.
- **Top-100 cut** for the regional map is a comparable strong-links sample, not a full profile.
- **Spam/toxicity is rules-based judgment**, not a certified third-party verdict; thresholds and formula weights are tunable priors to agree with the reviewer.
- **Gap ≠ guaranteed win** (domains may be unreachable/paid/closed); tiering encodes acquisition realism, not outcomes.
- **Branded miscount risk** if the sub-brand list is incomplete — enumerate exhaustively first.
- **Sector bodies** (theFCA, FosteringNetwork) distort the set — benchmarked but tagged/weighted separately.
- **domain_domains 5-domain ceiling** forces careful cross-batch dedup or gap volume double-counts.
- **KD is not authority-adjusted** — the `KD_vs_NFG_reach` column mitigates; a judgment call pending the authority read.
- **Regional pages must respect real service geography** (NFA North, Reach Out Care first) — avoid thin/doorway-page risk.
- This is a **plan** — no live metrics asserted; all cells populate only when the analyst runs the named Semrush calls at one labelled snapshot.

---

## Appendix A — Reference doc carry-over (UK Regional Competitor Link Analysis)

The client-supplied regional analysis is treated as a **validated prior**: its findings pre-seed Tabs 5, 7 and 8 and must be reconciled against (not overwritten by) the fresh Semrush pulls. Nothing below is dropped.

**A.1 Regional referring-domain matrix (identifiable high/mid-AS domains only) — reproduce & refresh in Tab 7.**
NFG's own counts to beat: Scotland 6 · Wales 1 · N.Ireland 1 · North West 9 · Yorkshire&Humber 0 · North East 0 · East Midlands 1 · West Midlands 4 · East of England 3 · London 2 · South East 2 · South West 1.
Reading: NFG strongest in **North West (9)** and **Scotland (6)**; **zero in Yorkshire & Humber and North East** (clear whitespace); theFosteringNetwork owns Yorkshire (5), theFCA owns Northern Ireland (6) and North East (4); ISP dominates South East (7). Only theFosteringNetwork and theFCA have broad all-nations coverage.

**A.2 Named regional gap seed domains (link to competitors, not NFG) — pre-load into Tab 5/7 and verify with a fresh pull:**
- **Yorkshire & Humber:** hulldailymail.co.uk, yorkshireeveningpost.co.uk, thestar.co.uk, leeds.ac.uk, doncasterfreepress.co.uk
- **North East:** chroniclelive.co.uk, sunderlandecho.com, northumberlandgazette.co.uk, newcastleworld.com
- **Northern Ireland:** belfasttelegraph.co.uk, belfastlive.co.uk, qub.ac.uk, derryjournal.com, familysupportni.gov.uk
- **East Midlands:** nottinghampost.com, derbytelegraph.co.uk, northamptonchron.co.uk
- **South East:** kentonline.co.uk, kent.gov.uk, theisleofthanetnews.com, bucksherald.co.uk
- **South West:** bristolpost.co.uk, plymouthherald.co.uk, stroudtimes.com, totalguidetobath.com
- **Scotland:** glasgowlive.co.uk, scotsman.com, dailyrecord.co.uk, iriss.org.uk, celcis.org
- **Wales:** gov.wales, cardiff.ac.uk, nation.cymru, wales247.co.uk

**A.3 Spam outliers (never inflate the matrix or enter targets — flag in Tab 8):**
- hu17.net (AS 28) → 26,791 backlinks to capstonefostercare.co.uk — implausible volume, injected/widget spam.
- sunderlandinformationpoint.co.uk → 184 links to compassfostering.com — disproportionate local-directory pattern.

**A.4 Recommendations to carry into Tab 10 (Priority Target List):**
- **Priority pick — close the Yorkshire & North East gap:** no NFG presence; both proven attainable via theFosteringNetwork/theFCA. Pair with NFG's real geography: **NFA North** covers Yorkshire & Lincolnshire (+ "Fostering in York" page); **Reach Out Care** covers North East, North Yorkshire & Cumbria (+ "Fostering in Newcastle" page).
- **Consider a Northern Ireland push** if NFG operates there — theFCA has a unique NI cluster (press + QUB + gov) no one else replicates.
- **Protect & extend the North West lead** (Liverpool Echo, Lancashire Live, Cheshire Live) + adjacent NW (Manchester, Wirral, Warrington).
- **Benchmark ISP's South East playbook** (Kent, Bucks, Milton Keynes press) if NFG has SE operations.
- The reference used **top-100 refdomains per site**; a **full manual audit of all referring domains** would sharpen the picture — this is exactly the *gap-list depth* decision (top 100 / 250 / full).
