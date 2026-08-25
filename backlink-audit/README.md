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
| `SUMMARY.md` | Executive summary, equity exposure, priority targets. |

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
6. Scraped aggregators, directory/link-scheme domains.
7. PBN / templated mass footprint — ≥20 auto-generated pages, ≤2 distinct anchors, no niche overlap.
8. Sitewide injection — one non-branded anchor on ≥80% of ≥8 pages.
9. Extreme outbound-link farms (≥1,500 avg external links).

**Safety brake.** Past this point a profile that is ≥80% branded or bare-URL
anchors can only be downgraded to `REVIEW_MANUALLY`, never disavowed.
Circumstantial signals — topical irrelevance, elevated outbound-link counts —
are not sufficient grounds to discard a brand mention. High anchor diversity
(≥60% distinct) likewise blocks irrelevance-based disavowal, since editorial
variety is the opposite of a templated placement.

**Tier 3–4** — borderline signals route to `REVIEW_MANUALLY`; topically
relevant and brand-mention profiles are retained.

## Remediation priority

Nofollow links pass no equity, so a nofollow-only footprint is hygiene, not
remediation. Every disavow row carries a priority:

- **P1** — follow links at volume (≥25)
- **P2** — follow links, low volume
- **P3** — nofollow only, no equity passed

This matters here: 98.1% of disavow-flagged backlinks in this export are
nofollow. Sequencing by priority prevents a headline row count from setting
the workload.

## Known limitations

- No liveness check on redirects or affiliate gateways (no `HTTP Status`).
- `Page ascore` is a weak proxy for organic traffic; a genuinely
  zero-traffic domain with a nonzero ascore may be under-flagged.
- Topical relevance is lexicon-based over domain names and page titles, not
  page-body content — non-English sources are under-detected.
- The URL drill-down caps at 250 rows per domain for templated footprints;
  the cap is disclosed in `SUMMARY.md`, never silent.
