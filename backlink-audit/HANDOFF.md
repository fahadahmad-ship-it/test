# Performance Lab — Backlink Audit: Handoff

**Status:** audit complete on available data; blocked on one API pull.
**Branch:** `claude/performancelab-backlink-audit-avlvtz` (repo `fahadahmad-ship-it/test`)
**Working directory:** `backlink-audit/`
**Date:** 2026-08-25

---

## 1. Where it stands

All **2,928 referring domains / 1,362,105 backlinks** carry a verdict.
Totals reconcile to Semrush exactly.

| Action | Domains | Backlinks |
|---|---:|---:|
| `DISAVOW` | 804 | 10,387 |
| `REVIEW_MANUALLY` | 682 | 1,341,756 |
| `KEEP_AFFILIATE_RETAIN` | 1,442 | 9,962 |

Evidence basis per domain:

| Basis | Domains |
|---|---:|
| Link-level (in the 50k sample) | 539 |
| Link-level + risk triage | 63 |
| Link-level sample too thin (<1% of domain) | 1 |
| Domain-level only (outside sample) | 1,829 |
| Domain-level + risk triage | 496 |

**1,829 domains still have no link-level evidence.** Closing that is the
single outstanding task — see §4.

---

## 2. THE OPEN QUESTION — answer this first

### Does anyone recognise `drect.net`?

Every `hexcolor.co` and `currencyconverts.com` "Buy Now!" link routes through:

```
https://drect.net/performancelab
```

This was invisible in the CSV export, which has no `redirect_url` column —
it shows only the resolved destination. It only surfaced from a Semrush API
pull.

**This reversed an earlier conclusion.** The audit had reasoned "the target
carries no tracking parameters, so no affiliate commission can be
attributed, therefore this is not a placement." That reasoning was drawn
from a field that did not exist in the data. `/performancelab` is a
brand-named campaign path on a redirect domain — which *is* attribution
architecture, just path-based rather than query-based.

Consequences either way:

- **If `drect.net` is the client's or their affiliate network's** →
  `hexcolor.co` is a paid placement decision, not a spam decision. It must
  come **out** of any disavow consideration, and `wete.co` /
  `appsrankings.com` almost certainly with it. That is **98% of the link
  profile** resting on this one answer.
- **If nobody recognises it** → it is a third-party redirect layer wrapping
  a templated mass placement, and the three domains stay held for a
  commercial decision.

`appsrankings.com` uses the Turkish anchor "Satın Al!" ("Buy Now!") on
Spanish-language pages, pointing at the English US homepage — one operator
running localised CTAs across auto-generated utility sites.

Public search could not identify `drect.net`'s operator.

---

## 3. What was done

### Two-stage audit

1. `audit.py` — link-level pass over the 50k backlinks export.
2. `refdomain_audit.py` — full 2,928-domain pass over the referring-domain
   export, merging in link-level verdicts where the sample covers them.
3. `build_workbook.py` — consolidated three-tab workbook.
4. `nameshape.py` — statistical generated-vs-brandable domain-name scorer.
5. `semrush_ingest.py` — **written, self-tested, not yet run on real data.**

No third-party toxicity score is consumed. Every verdict derives from raw
metrics and is reproducible from source.

### Disavow composition (804 domains)

| Risk factor | Domains |
|---|---:|
| Directory Submission Spam Network | 274 |
| Link-Selling / SEO Vendor Domain | 156 |
| Numbered Sibling Domain Network (PBN) | 139 |
| PBN Hosting Footprint (Shared C-Block) | 76 |
| Vendor Blog Network (Spun-Content PBN) | 60 |
| Throwaway Free-Host Subdomain | 52 |
| Scraped Aggregator / Auto-Generated Directory | 18 |
| Link Farm / Outbound-Link Bloat | 15 |
| Synthetic Affiliate Doorway Domain | 5 |
| Hacked Site / Injected Link-Vendor Spam | 3 |
| Other (link-level findings) | 6 |

### Notable findings

- **A coordinated campaign, not scattered spam.** 286 domains from one
  `seo-anomaly-*` / `seo-cartel-*` operation. The same operation's Telegram
  handle appears in anchors injected into three hacked institutional hosts
  (`cecar.edu.co`, `sante.gov.mg`, `uba.ar`).
- **The backlinks export is capped at 50,000 rows** — 3.67% of the profile,
  and not a random sample: `hexcolor.co` alone is 90.8% of it. Auditing it
  alone reached 603 of 2,928 domains and missed `wete.co` entirely (209,306
  backlinks, the #2 referrer).
- **Nofollow dominates the flagged volume.** Every disavow row carries a
  P1/P2/P3 priority keyed on follow links, so a nofollow-only footprint is
  sequenced as hygiene rather than repair.

### False positives caught and fixed

Each of these would have destroyed real assets:

| Would have flagged | Why wrong | Fix |
|---|---|---|
| `domain:blogspot.com` | Root keying merged 11 unrelated spam blogs; would discard every Blogspot link forever | Shared platforms key on full hostname |
| `domain:edu.co`, `domain:gov.mg` | Would disavow every Colombian university | Generic ccTLD second-levels keep a third label |
| Shopify `23.227.38.0/24` (81 domains) | Hosts the client's own brand estate | `SHARED_PLATFORM_CBLOCK` exclusion list |
| The Sun (3 editions) | One publisher syndicating its own article | Domains collapse to a brand core before network counting |
| `whatismoneypodcast.com` | 13 links to bespoke `/breedlove` sponsor path | Partner-landing-page rule |
| `ebylife.com` | Real health blog, 170 distinct anchors | Anchor-diversity guard |
| `mercyforanimals.org`, `ranktracker.com` | 100% branded anchors | Branded-anchor safety brake |
| `burnlabpro.com` | Opti-Nutra brand estate | Added to `BRAND_OWNED` |

### Rules considered and deliberately rejected

- **Batch-registration date clustering.** 58 directory-spam domains share
  three consecutive first-seen dates — but so do `jpost.com` and
  `mundonow.com`. Investigative signal only, never a rule.
- **Name-shape disavow.** Would have added 18 domains but misreads
  initialisms (`jsrproductions`, `hmscicomms`) as machine-generated. Those
  average four links each — false-positive risk dwarfs the gain. Name shape
  flags for review only.

---

## 4. NEXT TASK — the Semrush pull

**Why:** 1,829 domains have no anchor, target, placement or status data.
The API exposes `response_code` and `redirect_url`, which the CSV lacks —
these enable the redirect-liveness check the brief asked for and which has
been skipped throughout.

**Blocker in the originating thread:** Semrush and Ahrefs show
`connected: true` but `enabledInChat: false`; `mcp__Semrush__execute_report`
returns "No such tool available". `enabledInChat` is per-conversation, so a
thread where the connectors work can run this.

### 4a. Run this in a thread with Semrush enabled

Paginate with `display_offset` until exhausted. Expect **~19,300 rows**
covering all 2,324 unsampled domains.

```
execute_report(report='backlinks', params={
  target: 'performancelab.com',
  target_type: 'root_domain',
  display_limit: 10000,
  display_offset: 0,
  export_columns: ['source_url','target_url','anchor','nofollow',
                   'response_code','redirect_url','external_num',
                   'page_authority_score','sitewide','first_seen','last_seen'],
  display_filter: [
    {field:'refdomain', operation:'equals', sign:'-', value:'hexcolor.co'},
    {field:'refdomain', operation:'equals', sign:'-', value:'wete.co'},
    {field:'refdomain', operation:'equals', sign:'-', value:'appsrankings.com'}]})
```

Excluding those three is deliberate: they are 97.97% of all backlinks, are
already characterised at link level, and are held for the §2 decision
anyway. Excluding them makes the pull ~70x smaller at no loss.

Save the semicolon-delimited output (header + rows) to
`semrush_backlinks_filtered.csv`.

**Caution:** rows return through the conversation and consume context. Page
to disk as they arrive; do not hold 19k rows in context.

### 4b. Ahrefs coverage cross-check — names only

Confirmed cost: **30 units/row**, quota 400,000/month, 0 used.
Pull the referring-domain *list only*, not backlinks, and diff against
Semrush's 2,928. Pull backlinks **only** for domains Semrush does not know.

```
site-explorer-referring-domains(target='performancelab.com',
                                mode='subdomains', limit=...)
```

Ahrefs carries fields Semrush lacks — `traffic` (source organic traffic),
`refdomains_source`, `class_c`, `is_spam`, `url_redirect`. If budget ever
allows, these close the traffic-validation gap in §6.

### 4c. Feed results back

```bash
python3 semrush_ingest.py semrush_backlinks_filtered.csv out
```

Produces `out/redirect_and_status_profile.csv` with per-domain redirect and
HTTP-status verdicts. `classify_redirect()` separates:

- `ROUTED_CAMPAIGN` — one redirect host, one brand-named path, ≥90% of links
  → link-management / affiliate infrastructure, **protected by the brief**
- `ROUTED_MIXED` — many redirect hosts → inconsistent with a managed campaign
- `DIRECT` — no redirect hop

Self-tested against the observed `drect.net` pattern and a synthetic
multi-host case.

### 4d. Then re-run the full chain

```bash
python3 audit.py           <backlinks.csv> out
python3 refdomain_audit.py <backlinks.csv> <refdomains.csv> out
python3 build_workbook.py  out
```

**Expected:** the 419 Low-confidence KEEPs and most of the 682-domain review
queue resolve to real verdicts. Expect the pass to surface **more spam** —
every pass into that bucket so far has (24-domain blog network → 274
directories → 52 free-host subdomains).

---

## 5. Deliverables

| File | Contents |
|---|---|
| `out/performancelab_backlink_audit.xlsx` | **Main deliverable.** 3 tabs: full audit (2,928 domains + 1,521 URLs), Disavow (804, copy-ready `domain:` lines + Confirmed dropdown), Review Queue (682, volume-sorted + Decision dropdown). Live `COUNTIFS`/`SUMIFS`. |
| `out/full_refdomain_audit.csv` | All 2,928 domains, 26 columns |
| `out/disavow_full.txt` | Google-format, grouped by risk factor |
| `out/url_drilldown.csv` | Per-URL rows for flagged domains |
| `out/SUMMARY.md` | Executive summary |
| `README.md` | Full methodology, rule order, limitations |

**Workbook caveat:** LibreOffice hangs in the build sandbox (times out on a
4-cell file), so `recalc.py` could not cache formula values. Formulas were
validated directly — ranges, column mapping, and independently computed
expected values; the TOTAL row reconciles to 1,362,105. The 12 summary cells
read blank in previewers until Excel opens the file and computes. Data rows
are literals and unaffected.

---

## 6. Known limitations

- **No source organic traffic.** Neither export carries it; `Page ascore` is
  a weak proxy. A zero-traffic ghost domain with a nonzero ascore may be
  under-flagged. Ahrefs `traffic` would close this.
- **No redirect-liveness check yet** — pending §4.
- **419 Low-confidence KEEPs** rest on a niche-sounding domain name or an
  authority score alone. **This is where residual false negatives most
  likely remain.** Generated networks adopt legitimate-looking surface
  features; only cross-domain evidence (shared titles, C-blocks, naming
  generators) exposes them.
- **Topical relevance is lexicon-based** over domain names and page titles,
  not page bodies. Non-English sources are under-detected.
- **URL drill-down caps at 250 rows/domain** for templated footprints;
  disclosed in `SUMMARY.md`, never silent.
- **560 domains were risk-triaged into KEEP** — labelled `(Risk-Triaged)`,
  evidence suffixed `+ risk triage`. That is a decision that they are not
  worth acting on, **not** a verification of quality.

---

## 7. Decisions needed from the client

1. **`drect.net` — recognised or not?** Decides `hexcolor.co`, `wete.co`,
   `appsrankings.com` = 98% of the profile. §2.
2. **`eastbayexpress.com`** — 679 follow links, exact-match anchor "best
   nootropics for improving physical performance" replicated across
   paginated archives, on a real news outlet. Largest single equity
   exposure after the held three. Was it a bought placement?
3. **Filing scope** — file the 804 now, or wait for the §4 pull to complete
   first? The 804 are all High confidence and independent of the pull.
