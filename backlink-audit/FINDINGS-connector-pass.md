# Performance Lab — Backlink Audit: Connector Pass

**Date:** 2026-08-25
**Branch:** `claude/perf-lab-backlink-audit-zdkg4x`
**Continues:** `backlink-audit/HANDOFF.md` (branch
`claude/performancelab-backlink-audit-avlvtz`)

The handoff's blocker was that Semrush and Ahrefs reported
`connected: true` but `enabledInChat: false`, so `execute_report` returned
"No such tool available". Both connectors respond in this thread, so §4 of
the handoff — the outstanding pull — has been run.

---

## 1. What was pulled

### §4a Semrush link-level pull

`semrush_backlinks_filtered.csv` — **13,896 unique rows**, 14 pages of 1,000
(`display_limit` caps at 1,000, not the 10,000 the handoff assumed). Filter and
columns exactly as specified: `hexcolor.co`, `wete.co` and `appsrankings.com`
excluded, sorted `first_seen_asc` for stable offset paging. No duplicate rows
across pages; the result set exhausted at offset 13,000.

The handoff projected ~19,300 rows from the referring-domain export's
`Backlinks (true)` column. The API returned 13,896. The domain-level totals and
the link-level report are not the same population — the export counts backlinks
Semrush attributes to a domain, the backlinks report returns rows it will serve.

The pull covers **2,133 distinct referring domains**, of which **1,619 of the
2,324 previously unsampled domains now carry link-level evidence — 70%**. The
remaining **705 are still domain-level only**. That is a substantial closure of
the handoff's central gap, not a complete one.

Context note: oversized MCP results spill to disk automatically, so all 13,896
rows landed in files rather than the conversation. The handoff's warning about
paging 19k rows through context does not apply on this harness.

### §4b Ahrefs cross-check

Cost is **15–19 units/row, not the 30 the handoff recorded**, and the
referring-domains endpoint caps at **250 rows per call** whatever `limit` says.
Quota spent this pass: ~49k of 400,000 (12%).

`ahrefs_refdomains.csv` — 1,431 domains. `ahrefs_is_spam.csv` and
`ahrefs_ghost_domains.csv` — targeted slices pulled with `output=csv`, which is
far more compact than the JSON default.

Ahrefs reports **2,838 live referring domains** against Semrush's 2,928, and
10,113 all-time. `traffic_domain` and `positions_source_domain` are live, which
closes the traffic-validation gap the handoff named as its biggest blind spot
(§6) for every domain collected.

**Caveat on this file:** it mixes one `history=all_time` pull with later
`history=live` pulls. Rows with a non-null `last_seen` are **lost** links, not
current exposure. This matters — see §4.

---

## 2. The redirect layer is not one host

The handoff framed `drect.net` as *the* redirect question. The link-level data
shows a redirect layer of **44 distinct hosts** across 1,892 links, and the
composition changes the picture:

| Redirect host | Links | Ref. domains | Reading |
|---|---:|---:|---|
| `nutropic.com` | 542 | 200 | Third-party, fans across 200 unrelated domains |
| `testolabpro.com` | 356 | 125 | **Client's own brand estate** |
| `drect.net` | 348 | 3 | Third-party, confined to the `hexcolor.co` family |
| `fitliving.org` | 269 | 14 | Third-party, `/go/` affiliate paths |
| `dtcx.com` | 108 | 69 | Third-party, fans across 69 domains |
| `performancelabs.com` | 59 | 37 | Note: **plural**, not the client's domain |
| `prelabpro.com` | 15 | 11 | **Client's own brand estate** |

A host that fans across 200 unrelated referring domains is link-management
infrastructure, not a per-site cloak. `nutropic.com` and `dtcx.com` have that
shape and neither is in `BRAND_OWNED`.

`performancelabs.com` (plural) is worth flagging on its own: it looks like the
client's domain, is not, and carries DR 0.5 with zero traffic.

### A defect this exposed in `semrush_ingest.py`

`classify_redirect()` required a brand-named *path* to return
`ROUTED_CAMPAIGN`. In the live data these hops land on the bare root
(`testolabpro.com/`), so **125 domains redirecting through the client's own
brand estate were classified `ROUTED_OTHER`** — read as a third-party redirect
layer. Host ownership is the stronger signal, so it is now checked first and
returns a new `ROUTED_BRAND_OWNED` verdict. The prior behaviour is preserved:
`drect.net/performancelab` still returns `ROUTED_CAMPAIGN`, multi-host still
returns `ROUTED_MIXED`.

---

## 3. `eastbayexpress.com` — mechanism resolved

Handoff §7 decision 2 asked whether this was a bought placement. **All 235**
`eastbayexpress.com` rows in the pull route through one URL:

```
https://fitliving.org/go/nootropics-perfomancelabmind-productpage-general-all/?%2186a1n02ku
```

A `/go/` link-manager path, a campaign slug naming the product *and* the
placement (`productpage-general-all`), and a tracking parameter. All 235 are
follow links returning HTTP 200.

That is affiliate attribution architecture. The exact-match anchor replicated
across paginated archives — the audit's stated reason for flagging the
domain — is the placement's own template, not anchor abuse by a spammer.

**This does not by itself decide the verdict.** It resolves the *mechanism*: the
links are a managed placement, not organic editorial. Whether to keep them is
still the commercial question of whether `fitliving.org` is the client's
affiliate — the same ownership question as `drect.net`.

### `drect.net` — still unidentified

Confirmed present, on 3 referring domains (`hexcolor.co`, `currencyconverts.com`,
`appsupports.co`), always on the path `/performancelab`. Live resolution was
attempted and **blocked by this environment's network policy** (the agent proxy
returned 403 to CONNECT for `drect.net`, `nutropic.com`, `dtcx.com`,
`fitliving.org`, `performancelabs.com`, `securelinksdirectory.com`). Ownership
remains a client question. Handoff §2 stands.

---

## 4. Redirect-liveness check — run for the first time

The brief asked for this and it had been skipped throughout for want of a
`response_code` column.

| Status | Links |
|---|---:|
| 200 | 11,894 |
| 0 (unreachable) | 723 |
| 301 / 302 / 303 / 307 | 730 |
| 404 / 410 | 353 |
| 403 | 162 |
| 5xx | 29 |

**987 links are dead or unreachable** (0, 404, 410). These are hygiene, not
toxicity: a dead link passes nothing and needs no disavow. Per-domain detail is
in `out/redirect_and_status_profile.csv`.

Follow/nofollow across the new rows: **9,898 follow / 3,998 nofollow** — a much
higher follow share than the profile-wide picture, because the three excluded
domains carry the nofollow bulk.

---

## 5. Proposed verdict changes — 567

`out/proposed_changes.csv` carries one row per change with its evidence.
`out/crosscheck_full.csv` carries all 3,519 domains considered.

| Change | Domains |
|---|---:|
| `NOT_AUDITED` → `DISAVOW` | 383 |
| `REVIEW_MANUALLY` → `DISAVOW` | 96 |
| `KEEP_AFFILIATE_RETAIN` → `DISAVOW` | 83 |
| `KEEP_AFFILIATE_RETAIN` → `REVIEW_MANUALLY` | 3 |
| `NOT_AUDITED` → `REVIEW_MANUALLY` | 2 |

Grounds for the 562 proposed disavows:

| Basis | Domains |
|---|---:|
| Vendor-flagged spam with no traffic to contradict it | 407 |
| SEO-vendor `.shop` network (machine-generated names) | 88 |
| Zero-traffic / zero-ranking follow-link source | 67 |

`out/disavow_addendum.txt` holds these as Google-format lines, grouped by
basis, separate from the 804 already filed.

### The ghost domains — §6's residual risk, now measurable

The handoff's §6 warned that "a zero-traffic ghost domain with a nonzero ascore
may be under-flagged" and that the 419 Low-confidence KEEPs were where false
negatives most likely remained. With Ahrefs traffic that is now testable, and
the answer is yes:

| Domain | Follow links | Traffic | Ranking keywords |
|---|---:|---:|---:|
| `healthynaturlremedy.com` | 2,847 | 0 | 0 |
| `smartlivingseniors.com` | 832 | 0 | 0 |
| `ultimatestrengths.com` | 566 | 0 | 0 |
| `allgoodhealth.net` | 496 | 0 | 0 |
| `ignitefitnez.com` | 438 | 0 | 0 |
| `verybigbrain.com` | 261 | 0 | 0 |
| `reignitethemind.com` | 210 | 0 | 0 |

High-volume **follow** links from domains with no audience and no rankings at
all. `primeacuity.com` and `reignitethemind.com` share IP `208.123.116.145`;
`thesportwriter.com` and `enutritionreads.com` share `195.179.238.13`. Several
were High confidence KEEPs.

### Networks the audit did not have

**13 non-CDN shared-IP clusters** among domains absent from the audit, all
directory/link-vendor shaped:

| IP | Domains | Sample |
|---|---:|---|
| `213.199.63.182` | 8 | `allistingdirectory.com`, `authorityprodirectory.com` |
| `92.249.46.138` | 5 | `acquire.co.in`, `addurl.in`, `allinone.co.in` |
| `167.86.98.5` | 4 | `ahrefs-links.com`, `guestpostsdirectory.com` |
| `167.86.101.193` | 4 | `bestbusniessdirectory.com`, `eliterankdirectory.com` |
| `75.98.175.91` | 3 | `testosteroneboosters{australia.com,uk.co.uk}` |

Plus an **88-domain `.shop` SEO-vendor network** (`pageseo*.shop`,
`seolink*.shop`, `rank*.shop`, `googleseo*.shop`) — uniform 6 links each, all
nofollow, DR 0–54, zero traffic.

**Correction to an early reading:** the `bhs-links-*.xyz` and
`seo-anomaly-top-*.xyz` families are already in the audit and already
disavowed. They were not missed. Only the `.shop` network is new.

Likewise the `.pics` / `.best` / `.icu` cluster (`luggic.pics`, `damull.pics`,
`icepto.best`, `zedrou.icu` …) that surfaced in the first Ahrefs pull carries
`last_seen` dates from 2023–2025 — **lost links, not current exposure**. They
are correctly absent from the proposals. This is why the `history` parameter
matters: it defaults to `all_time`.

---

## 6. False positives caught in this pass

Three, all in work produced during this pass, all fixed before writing out:

| Nearly did | Why wrong | Fix |
|---|---|---|
| Rescued 45 disavowed domains to KEEP because their links hop through `testolabpro.com` | They are directory/PBN-hosting spam — checked, and **none** was disavowed on redirect grounds. A first-party redirect answers the redirect inference and nothing else | Brand-owned hop only overturns a verdict whose stated basis was the redirect itself, and never over independent spam evidence |
| Disavowed `brandfetch.com` (1.15M visits), `za.com` (1.19M), `fmtc.co` (an affiliate-feed provider) | Ahrefs `is_spam` fires on all three. The audit consumes no third-party toxicity score by design, and this is why | Traffic brake: `is_spam` above 500 visits or 100 ranking keywords buys manual review, never a disavow |
| Clustered `.pics`/`.best` domains on IPs `188.114.96–97.x` | That is Cloudflare — the same trap as Shopify's `23.227.38.0/24`, which holds the client's own estate | Added to `SHARED_FRONTEND_PREFIXES` |

---

## 7. Honest limits

- **407 of 562 proposed disavows rest primarily on Ahrefs `is_spam`**, gated by
  a zero-traffic check. That is weaker than the rest of this audit, which
  derives every verdict from raw metrics. Treat the 88 `.shop` and 67
  zero-traffic groups as firm and this group as strong-but-vendor-derived.
- **The full chain was not re-run.** `audit.py` and `refdomain_audit.py` need
  the two original CSV exports, which are not in this container (only the prior
  thread's outputs are). Handoff §4d is therefore still outstanding, and what
  is delivered here is an *overlay* keyed on `Referring Domain`, not a
  regenerated audit. Re-supply the two exports and the chain can run.
- **Ahrefs enumeration is partial** — 1,431 of 2,838 live domains. The 250-row
  cap plus prefix partitioning made full enumeration expensive; the two
  targeted slices were pulled instead because they carry the decisions. The
  `[0-9a]` partition returned exactly 250 rows and is therefore truncated.
- **705 of the 2,324 unsampled domains still have no link-level evidence** —
  70% of the gap closed, not all of it.
- **Redirect hosts could not be resolved live** — network policy, §3.
- The workbook was **not** rebuilt; `build_workbook.py` reads the audit
  outputs, which this pass does not overwrite. The overlay is CSV-only by
  design, so nothing already delivered is silently mutated.

---

## 8. Next steps

1. **Client decisions** — `drect.net` and `fitliving.org` ownership. Between
   them they gate `hexcolor.co`, `wete.co`, `appsrankings.com` (98% of the
   profile) and `eastbayexpress.com` (667 follow links).
2. **Re-supply the two CSV exports** so handoff §4d can run and the overlay can
   be folded into the workbook.
3. **Review `proposed_changes.csv`** — the 83 `KEEP` → `DISAVOW` first, as
   those reverse a delivered verdict.
4. Optionally finish the Ahrefs enumeration (~1,400 domains, ~27k units).

## Files added this pass

| File | Contents |
|---|---|
| `semrush_backlinks_filtered.csv` | 13,896 link-level rows (handoff §4a) |
| `ahrefs_refdomains.csv` | 1,431 referring domains with traffic/spam/IP |
| `ahrefs_is_spam.csv` | 250 vendor-flagged domains, ≥5 links |
| `ahrefs_ghost_domains.csv` | 73 zero-traffic zero-ranking domains, ≥30 links |
| `crosscheck.py` | Overlay generator |
| `out/crosscheck_full.csv` | All 3,519 domains considered |
| `out/proposed_changes.csv` | 567 proposed changes with evidence |
| `out/disavow_addendum.txt` | 562 disavow lines, grouped by basis |
| `out/redirect_and_status_profile.csv` | Per-domain redirect + HTTP status |
