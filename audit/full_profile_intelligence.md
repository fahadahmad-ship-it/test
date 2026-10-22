# Controlled Comfort — full-profile intelligence (Ahrefs export, 2026-10-22)

Scoping output from the client's Ahrefs CSVs (1,089 referring domains / 2,514 backlinks).
This is **not** a finished disavow — it is the map of what a full-profile audit must sort out.
Tab 08's 56 are one of (at least) three distinct patterns in this profile.

## Profile at a glance
| Metric | Value |
|---|---|
| Referring domains (Ahrefs) | 1,089 |
| Backlinks | 2,514 (all HTTP 200; 1,164 dofollow) |
| Ahrefs "Is spam" = true | 911 (83%) |
| Zero organic traffic | 989 (90%) |
| Links to home page `/` | 2,236 |
| Links to deep `/services/*` pages | 178 |
| Hosts pointing ONLY at deep pages | 72 |
| Hosts pointing ONLY at home | 1,016 |

The playbook's "two campaigns" split holds at scale: a **deep-page** set (the commissioned-looking
directory listings — the 56 live here) and a **home-page flood** (the bulk spam/PBN footprint).

## ⚠️ The DR≥20 trap (why "Keep if DR≥20" must NOT be applied mechanically)
384 referring domains have DR ≥ 20. But splitting them by real audience:

- **~55 are genuinely authoritative citations** (Is spam=false AND organic traffic > 0) — real
  directories and local bodies. **Protect these; never disavow.** Examples:
  bbb.org (DR93), yellowpages.com (DR89), expertise.com, birdeye.com, chamberofcommerce.com,
  procore.com, dexknows.com, rocketreach.co, dandb.com, owler.com, leadiq.com, citysquares.com,
  **omahachamber.org**, **oppd.com** (Omaha Public Power District), mylocalservices.com, fyple.com,
  macraesbluebook.com, townepost.com, cgmimm.com, thecompanycheck.com, cortera.com, maytaghvac.com,
  downtobid.com, allpeople.com, phonebooks.com, omaha-ne.com.
- **~329 have DR 20–60 but ZERO traffic and the spam flag** — manipulated-DR PBN / "buy backlinks"
  farms. A naive DR≥20→Keep rule would have **kept all 329**. They are spam, not genuine.

**Lesson applied:** the Keep decision rests on real audience + genuine host, never on DR/AS alone.
This is the playbook's principle 2 ("nothing on a score alone") doing real work here.

## The three bad-link patterns in this profile
1. **Tab 08 directory / listing network (the 56 + many more).** DR 0, exact-match HVAC+"Omaha NE"
   anchors, pointing at `/services/heating`, `/services/air-conditioning`, and home; zero traffic;
   live; dofollow; classic tri-anchor listing template (exact-match + "Visit Website" +
   "controlledcomfort.com"). → **Held (Pending supplier)** — may be commissioned local-SEO
   directory submissions. ~72 hosts point only at deep pages; the broader directory set is larger
   still. **Do not disavow until the supplier answers.**

2. **PBN / "buy backlinks" link-farm network.** Manipulated DR 20–60, zero traffic, spam-flagged,
   PBN sales-copy anchors/hosts. Signatures in the data: **122 `*.store`** ("link-baron-…",
   "seoexpress-…", "rank-forge-…", "outrank-hq-…"), **68 `*.shop`** backlink farms, **82 numbered
   `*.xyz`** (e.g. 37486xxx.xyz, 11763xxx.xyz), plus buybacklinks.agency, worldtopbacklinks.com,
   99backlinksbuy.com, etc. → **Spam (Disavow)** on host/anchor evidence. This is NOT a commissioned
   local-SEO signature; it reads like a cheap-link-farm or negative-SEO footprint. **This set is
   disavowable now on evidence, independent of the supplier conversation** — pending your go-ahead.

3. **Genuine citations (~55).** → **Keep.** Listed above. Protect-list for the verification sweep.

## Recommended next step
A **full-profile audit** (all 1,089 RDs) in the signed-off 7-tab format, producing:
- `Keep` for the ~55 genuine citations (+ any others that pass the audience test on inspection);
- `Spam (Disavow)` **active lines** for the PBN/link-farm network (evidence-based, not commissioned);
- `Held (Pending Partner)` for the directory/listing network (the 56 and their kin) — still out of
  the file until the supplier confirms;
- exhaustive both-directions verification (no genuine citation in the file; no dofollow spam left out).

The Tab 08 deliverable (the 56, all Held) stands on its own and is unchanged. The disavow file for
the 56 stays at **0 active lines** pending the supplier. Say the word and I'll build the full
workbook + the complete disavow (PBN network active, directory network held, citations kept).

## Caveats
- DR, traffic, keywords here are **Ahrefs** figures. The signed-off audit quotes **Semrush** metrics
  as the number (Ahrefs for discovery/live-check only). For the final workbook I'll reconcile the
  per-domain metrics to Semrush; the Keep/Spam/Held split above is driven by evidence (anchor, host,
  audience, spam corroboration), not by the DR number alone.
- "Is spam" is Ahrefs' flag — used here only as corroboration, never as the sole basis for a line.
