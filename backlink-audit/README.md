# Performance Lab — Backlink Disavow Audit

Deterministic, rule-based toxic-link audit for `performancelab.com`.
No third-party toxicity score is consumed or trusted; every verdict is
derived from raw metrics in the export and is reproducible from source.

```bash
python3 audit.py <backlinks.csv> <outdir>
```

## Outputs

| File | Contents |
|---|---|
| `domain_audit.csv` | One row per referring domain — the primary deliverable. |
| `url_drilldown.csv` | Per-URL rows for every `DISAVOW` / `REVIEW_MANUALLY` domain. |
| `disavow.txt` | Google-format disavow file, grouped and commented by risk factor. |
| `SUMMARY.md` | Executive summary, equity exposure, priority targets, held-for-decision items. |
| `performancelab_backlink_audit.xlsx` | **Consolidated single-sheet workbook** — every domain and drill-down URL on one surface, built by `build_workbook.py`. |

```bash
python3 build_workbook.py <outdir>          # after audit.py
```

The workbook puts domain rows (`Level=DOMAIN`) and their per-URL drill-down
(`Level=URL`) on one sheet, colour-coded by action, with an autofilter and a
dropdown on every Action cell. The summary block at the top uses live
`COUNTIFS`/`SUMIFS`, so as an analyst resolves `REVIEW_MANUALLY` rows to
`DISAVOW` or `KEEP` in place, the domain, backlink and follow-link totals
update with them.

## Input reality vs. brief

The brief specified ~1.4M backlinks across ~3,000 referring domains and a
column set including `Anchor Type`, `HTTP Status`, `Referring Domains
Count` and `Estimated Organic Traffic (Source)`.

The supplied export is a **Semrush backlinks export of 50,000 rows across
615 referring domains** — a ~3.6% sample of the stated profile — with a
different schema. Columns actually present:

`Page ascore, Source title, Source url, Target url, Anchor, External links,
Internal links, Nofollow, Sponsored, Ugc, Text, Frame, Form, Image,
Sitewide, First seen, Last seen, New link, Lost link`

Consequences, and how each was handled:

| Missing signal | Substitute used |
|---|---|
| `Referring Domain` | Derived from `Source url` (see *Domain keying*). |
| `Anchor Type` | Derived by classifier — Branded / URL / Exact-Commercial / CTA-Generic / Phrasing / Empty-Image. |
| `Estimated Organic Traffic` | `Page ascore` (Semrush page authority) as an authority proxy. **This is the weakest substitution** — a zero-traffic ghost domain can still carry a nonzero ascore. |
| `HTTP Status` | Unavailable. Dead-loop and parked-domain detection in the affiliate protocol **could not be executed**; affiliate gateways are retained on pattern match without a liveness check. |
| `Referring Domains Count` | Unavailable; no inbound-authority check on source domains. |
| `Link Type` (redirect) | Unavailable. Redirects are not distinguishable from direct links in this export. |

Verdicts are therefore sound for what the export contains, but the audit is
**not complete for the full 1.4M-link profile**. Re-run against a full
export with status codes and source traffic before filing the disavow.

## Evaluation unit — domain keying

Aggregation happens at the **registrable domain**, with two corrections that
materially change the disavow file:

1. **Shared publishing platforms** (`blogspot.com`, `substack.com`,
   `wordpress.com`, `medium.com`, …) key on the **full hostname**. Each
   account is an independent publisher. Keying these at the root would merge
   unrelated sites and emit `domain:blogspot.com` — a disavow line that
   discards every Blogspot link the brand will ever earn.
2. **Generic second-level labels under a ccTLD** (`edu.co`, `gov.mg`,
   `co.uk`, …) keep a third label. Three hacked institutional hosts appear
   in this dataset; `domain:edu.co` would disavow every Colombian
   university.

## Rule order

Protected assets resolve **before** any spam rule can fire.

**Tier 1 — protected (never disavowed)**
1. Opti-Nutra brand estate — `performancelab.com`, `mindlabpro.com`, `testolabpro.com`, `prelabpro.com`.
2. Affiliate / tracking infrastructure — known networks plus `go.`/`track.`/`offers.`-style tracker hosts.
3. Dedicated partner landing pages — all links resolve to one bespoke target path outside the standard site structure with brand-led anchors (e.g. `whatismoneypodcast.com` → `/breedlove`).
4. Search & AI answer surfaces — reported, excluded from the disavow file; they pass no manipulable equity.

**Tier 2 — spam (fires regardless of anchor profile)**

5. Hacked-site / link-vendor injection (anchor advertises a link vendor).
6. Vendor blog networks — free-blog hosts used only by link sellers.
7. Spun-content networks — the same article, near-verbatim, on 3+ other referring domains.
8. Synthetic affiliate doorway domains (geo-prefixed / doubled-hyphen patterns).
9. Throwaway auto-generated account subdomains.
10. Scraped aggregators, directory/link-scheme domains.
11. PBN / templated mass footprint — ≥20 auto-generated pages, ≤2 distinct anchors, no niche overlap.
12. Sitewide injection — one non-branded anchor on ≥80% of ≥8 pages.
13. Extreme outbound-link farms (≥1,500 avg external links).

### Cross-domain network detection

Rules 6–9 exist because per-domain analysis is structurally blind to
networks. A single link from `tkzblog.com` looks like an ordinary low-value
blog link; the pattern is only visible in aggregate. Before classification
the audit therefore builds a global index of normalised page titles and
flags any domain running an article that appears on **three or more other
referring domains**.

This caught 24 domains — carrying **follow** links — that per-domain rules
had cleared as topically relevant, because their spun articles were about
fish oil and nootropics and so passed the niche-relevance test. Relevance
had become the thing protecting them.

The counter-check matters as much: one publisher syndicating its own
article across international editions (`thesun.co.uk` / `the-sun.com` /
`thesun.ie`) is not a network. Domains are collapsed to a brand core before
the count, so a single brand cannot trip the rule.

**Safety brake.** Past this point a profile that is ≥80% branded or bare-URL
anchors can only be downgraded to `REVIEW_MANUALLY`, never disavowed.
Circumstantial signals — topical irrelevance, elevated outbound-link counts —
are not sufficient grounds to discard a brand mention. High anchor diversity
(≥60% distinct) likewise blocks irrelevance-based disavowal, since editorial
variety is the opposite of a templated placement.

**Tier 3–4** — borderline signals route to `REVIEW_MANUALLY`; topically
relevant and brand-mention profiles are retained.

## Confidence gate

`DISAVOW` requires **High** confidence. Anything below it is routed to
`REVIEW_MANUALLY` instead, and the risk factor is suffixed
`[below disavow confidence bar]`. A filed disavow is slow and awkward to
unwind; a review queue is not.

Three domains are additionally held back by name in `MANUAL_REVIEW_OVERRIDE`
for an explicit client decision, each carrying the evidence that makes the
call a judgement rather than a rule — `hexcolor.co`, `currencyconverts.com`,
and `eastbayexpress.com`. See the summary for the reasoning.

## Remediation priority

Nofollow links pass no equity, so a nofollow-only footprint is hygiene, not
remediation. Every disavow row carries a priority:

- **P1** — follow links at volume (≥25)
- **P2** — follow links, low volume
- **P3** — nofollow only, no equity passed

This matters here: 98.1% of disavow-flagged backlinks in this export are
nofollow. Sequencing by priority prevents a headline row count from setting
the workload.

## Workbook formula validation

`recalc.py` could not be used in this environment: LibreOffice headless
hangs here even on a four-cell workbook, so both attempts timed out without
recalculating anything. The formulas were therefore validated directly
instead:

- every range spans exactly the data rows (`10:2154`), checked programmatically;
- the referenced columns resolve to the intended headers (`A`=Level,
  `F`=Action Recommendation, `K`=Backlinks, `L`=Follow (Equity) Links);
- expected results were computed independently from `domain_audit.csv`, and
  the TOTAL row reconciles to the raw export — 615 domains, 50,000
  backlinks, 3,431 follow links;
- only `COUNTIFS`, `SUMIFS` and `SUM` are used: all Excel-2007-era, so no
  `_xlfn.` prefix is needed and no spilling-array metadata is involved.

One consequence remains. openpyxl writes formulas with no cached values, and
nothing recalculated them, so those twelve summary cells read as empty to
anything relying on cached values (`pandas`, `load_workbook(data_only=True)`,
some previewers). Excel and LibreOffice compute them on open. The 2,145 data
rows are literal values and are unaffected.

## Known limitations

- No liveness check on redirects or affiliate gateways (no `HTTP Status`).
- `Page ascore` is a weak proxy for organic traffic; a genuinely
  zero-traffic domain with a nonzero ascore may be under-flagged.
- Topical relevance is lexicon-based over domain names and page titles, not
  page-body content — non-English sources are under-detected.
- The URL drill-down caps at 250 rows per domain for templated footprints;
  the cap is disclosed in `SUMMARY.md`, never silent.
