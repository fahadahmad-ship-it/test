# Toxic Domain Inventory — ngwindows.com

**Compiled:** 6 October 2026
**Target:** ngwindows.com (root domain)
**Referring domains enumerated:** 1,232 (full pagination of Semrush `backlinks_refdomains`,
7 pages × 200, sorted `backlinks_num_desc`) — 7,547 backlinks accounted for.
**Raw data:** `/home/user/test/backlink-audit/data/refdomains.csv`,
`/home/user/test/backlink-audit/data/anchors_observed.csv`

> **Data availability — read this before using the counts below.**
> Ahrefs Site Explorer was unavailable for the whole audit (workspace units exhausted,
> resets 2026-10-25). The Semrush API unit balance reached **zero during this audit**,
> after the full referring-domain list and the referring-IP list were retrieved but
> after only **one page (76 links, 73 distinct referring domains)** of anchor-level
> backlink data. That page is the entire evidence base for anchor text and dofollow
> status. Everything in this document is labelled as either **observed** or **inferred**.

---

## 1. Scoring methodology (stated explicitly)

This inventory **does not use Authority Score, Domain Rating, Trust Score, TLD, country
or hosting as grounds for disavowal.** Those signals are descriptive, not probative: a
DR-0 domain can be a legitimate small local site, and a DR-75 domain can be a link
vendor (both occur in this dataset — see §5).

A domain is classified **TOXIC-CRITICAL (disavow)** only when all three conditions are
directly observed in the Semrush `backlinks` report:

| # | Condition | Why it is probative |
|---|---|---|
| 1 | **Anchor text is link-vendor sales copy** — the anchor advertises an SEO/backlink service rather than describing the destination | Anchor text is author-controlled and intentional. Vendor sales copy as anchor is self-identifying manipulation. |
| 2 | **`rel="nofollow"` is absent** (link is dofollow) | A nofollow link passes no PageRank and cannot be the mechanism of a link-based penalty. Nofollow vendor links are recorded but **not** disavowed. |
| 3 | **Shared structural fingerprint** — the same URL path slug, with the same numeric/hex id, recurs across otherwise unrelated registrations | Independent sites do not coincidentally publish `/dir/backlink-seo-experts-211287`. Identical slug + identical anchor across many domains is a single operator. |

Everything that fails any of the three goes into **NOT DISAVOWED**, sub-bucketed by the
reason it failed. Where a domain was never covered by the one page of anchor data, it is
**EXCLUDED FOR INSUFFICIENT EVIDENCE** regardless of how suspicious its name looks.

---

## 2. Classification counts

| Bucket | Domains | Basis |
|---|---:|---|
| **TOXIC-CRITICAL — disavowed** | **66** | Observed vendor anchor + observed dofollow + shared slug fingerprint |
| NOT DISAVOWED — vendor anchor but **nofollow** | 2 | Observed anchor is vendor copy; `rel=nofollow` present |
| NOT DISAVOWED — **benign anchor observed** | 5 | Anchor is a bare domain/URL or generic phrase |
| **INSUFFICIENT EVIDENCE — excluded** | **1,159** | No anchor/dofollow data retrievable before API units hit zero |
| **Total referring domains enumerated** | **1,232** | |

Two of the 66 disavowed domains (`urlbacklinkschecker.space`, `backlinkcheckerseo.space`)
appear in the `backlinks` report but **not** in the 1,232-row `backlinks_refdomains` list —
Semrush's own two endpoints disagree. Both are evidenced and both are included.

### The AS 0–5 band, answered directly

The band contains **1,015 referring domains** (82.4% of 1,232) carrying **6,078 backlinks**.
The anchor-text split requested can only be reported for the 70 of them covered by the one
page of anchor data:

| Sub-bucket of AS 0–5 | Domains | Share of the 1,015 |
|---|---:|---:|
| (a) vendor sales-copy anchor, **dofollow** | 64 | 6.3% |
| (a-nf) vendor sales-copy anchor, nofollow | 2 | 0.2% |
| (b) bare domain-name / bare-URL anchor | 4 | 0.4% |
| (c) empty / image anchor | 0 observed | — |
| (d) genuine-looking anchor | 0 observed in this band | — |
| **no anchor data retrievable** | **945** | **93.1%** |

**This is the honest answer and it is mostly a gap.** 93% of the AS 0–5 band has no anchor
evidence either way. The prior draft treated the whole band as toxic; that was an unsupported
inference, and the corrected position is that **only 64 of 1,015 AS 0–5 domains (6.3%) can
currently be shown to be manipulative.**

---

## 3. The two evidenced networks

### Network A — shared-slug `/dir/` vendor network (59 domains, all dofollow)

Six distinct page slugs, each reused verbatim across many unrelated domains, each carrying
one fixed anchor string:

| Shared path | Domains | Fixed anchor on every one |
|---|---:|---|
| `/dir/backlink-seo-experts-211287` | 15 | "Professional thermalprowindows.com SEO Backlinks for Stronger Website Authority" |
| `/dir/seo-ranking-links-170322` | 10 | "Expert Backlink Building Services to Grow qualitypluswindows.com Website Rankings" |
| `/dir/professional-seo-links-148030` | 10 | "ngawindows.com Premium Link Building Experts for Website Ranking Growth" |
| `/dir/trusted-seo-backlinks-150104` | 10 | "northpointwindows.com Premium SEO Links for Higher Search Engine Rankings" |
| `/dir/ethical-seo-backlinks-160633` | 9 | "performingwindows.com Premium SEO Backlinks for Higher Google Rankings and Organic Traffic" |
| `/dir/quality-authority-backlinks-148096` | 5 | "Increase Google Visibility with High Quality Backlinks ngwindows.com" |

Naming convention is uniform: `dachecker*`, `dapachecker*`, `backlinkchecker*`,
`seochecker*`, `rankchecker*`, `serpchecker*` on `.site/.space/.shop/.store/.website/.online`.

### Network B — "guest post / niche edit" vendor network (7 domains, all dofollow)

`ggmap.co.com` · `newearthsummit.org` · `nivira.shop` · `mertio.shop` · `mervi.shop` ·
`nimbra.shop` · `bestseoquill.site`

Fingerprint: machine-generated long-form URLs under a selling-path segment
(`/dofollow-index/`, `/guest-post-network/`, `/crawl-index-network/`, `/link-building-hub/`,
`/organic-growth-links/`, `/niche-relevance-hub/`, `/seo-authority-links/`,
`/serp-growth-network/`) terminating in a 6-hex id. The most explicit anchor observed in the
entire dataset is from `nivira.shop`:

> "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service
> northpointwindows.com Rank First Page Google Fast SEO Link Building Buy Backlinks Online Cheap"

---

## 4. Subnet / hosting clustering evidence

**The headline "428 class-C subnets across 1,141 IPs" figure in the draft audit is not
measuring what it appears to measure.** 861 of 1,232 referring domains (**69.9%**) resolve
to Cloudflare anycast ranges (104.21.x, 172.67.x, 104.16–104.26.x, 172.64–172.66.x). Those
IPs are a CDN front door, not a host. The 221 distinct "class-C subnets" they spread across
are an artifact of Cloudflare's address allocation and say nothing about who owns the sites.
Subnet-diversity analysis of this profile is therefore **uninformative in both directions**
and should not be cited as evidence of clustering or of its absence.

What *is* informative is the non-Cloudflare residue. Worst offenders by referring domains
on a single IP (from `backlinks_refips`, sorted `domains_num_desc`):

| IP | Country | Ref. domains | Backlinks | Character of the cluster |
|---|---|---:|---:|---|
| 118.139.181.85 | SG | 29 | 727 | "website worth"/stats scraper farm |
| 203.161.54.114 | US | 27 | 186 | domains literally named `99backlinksbuy.com`, `buyfairbacklinks.com`, `clicktobuybacklinks.com`, … |
| 195.20.19.178 | MD | 19 | 263 | URL-shortener / link-redirect network |
| 142.251.111.132 | US | 13 | 341 | Google/Blogspot (shared platform IP — not a network) |
| 184.168.115.60 | SG | 9 | 405 | stats scraper farm (GoDaddy shared) |
| 118.139.176.46 | SG | 9 | 365 | stats scraper farm |
| 118.139.161.199 | SG | 5 | 146 | `backlinkhouse.com`, `backlinkon.com`, `backlinkshouse.com`, `backlinkstree.com`, `backlinksbank.com` |
| 67.223.118.29 | US | 6 | 20 | mixed |
| **15.197.225.128** | US | 5 | 26 | `northgeorgiawindows.net`, `performingwindows.com`, `roiwindows.com`, `thermalprowindows.com`, `thermatrustwindows.com` |
| **15.197.142.173** | US | 5 | 13 | `e2windows.com`, `ngwindow.com`, `northgawindows.com`, `northgeorgiawindow.com`, `thermalastwindows.com` |
| **3.33.251.168** | US | 7 | 17 | `ngawindows.com`, `northpointwindows.com`, `qualitypluswindows.com`, … |
| 188.40.17.96 | DE | 5 | 9 | `locabee.ch/.com/.gr`, `wogibtswas.de/.net` (one operator, benign directory) |
| 191.101.14.187 | US | 4 | 11 | `contractorsup.com`, `doorswindowscompany.com`, `renovationsup.com`, `usabuildingsuppliers.com` |

**None of the clusters above are in the disavow file** — co-hosting is not per-domain
evidence of a manipulated link, and in the three bolded rows it is evidence of something
quite different (§5).

---

## 5. Three findings the draft audit got wrong or missed

### 5.1 The 17 "other window companies" are a brand-variant cluster on three shared IPs

The draft read anchors like `ngawindows.com`, `roiwindows.com`, `thermalprowindows.com` as
proof of a vendor blasting a scraped list, with ngwindows.com as a bystander. The hosting
data points elsewhere. Seventeen window-company domains that **link to ngwindows.com** sit on
just three AWS Global Accelerator IPs — and several are near-exact brand variants of the
client: `ngwindow.com`, `northgawindows.com`, `northgeorgiawindow.com`,
`northgeorgiawindows.net` alongside `ngwindows.com`.

These domains first appeared in **July 2024 – July 2025**, a full year before the link blast
(late June 2026), and the red-team pass found the cluster is ~34% nofollow. That is not a
PBN blast profile. **Inference, clearly labelled:** this looks like a portfolio of brand
variants and lead-gen microsites under common control rather than a third-party attack.
It is excluded from the disavow file and flagged as the single most important thing to put
to the client directly: *do you own or control these domains?* The answer changes the whole
framing of the audit.

### 5.2 The draft's class-C subnet evidence does not survive contact with the data

70% Cloudflare-fronted (§4). The "1,141 IPs / 428 class-C subnets / ~2.9 domains per subnet"
reasoning in the draft audit is measuring Cloudflare, not a link network, and should be
struck from the client-facing report.

### 5.3 Authority Score is not correlated with manipulation in this profile

Direct counter-examples from the Ahrefs free DR endpoint:

- `seonix.agency` — **DR 65** — publishes fabricated testimonials ("After hiring
  northgeorgiawindows.net for niche edits, my sales doubled within 1 month"). A high-DR
  link vendor. (Still not disavowed: the link is nofollow.)
- `factmags.com` — **DR 75** — yet co-hosted on 203.161.54.114 with 27 domains named
  `buyfairbacklinks.com`, `99backlinksbuy.com`, `clicktobuybacklinks.com`. High DR, highly
  suspicious company. No anchor evidence → excluded.
- `csswinner.com` — **DR 75** — flagged toxic in the draft on AS/country grounds. No anchor
  evidence of manipulation → removed.
- `eurekster.com` — **DR 53** — same, removed.

Conversely the 66 disavowed domains include several at DR 0 **and** the evidence against
them has nothing to do with their DR. Any AS/DR threshold applied to this profile would have
produced roughly 8% false positives in one direction and missed DR-65+ vendors in the other.

---

## 6. Honest statement of what remains unknown

- **1,159 of 1,232 referring domains (94%) have no anchor-level evidence** in this audit.
  360 of them carry Network A's naming convention and 284 of those first appeared in the
  14 days to 6 Oct 2026. They are *probably* the same network. That is an inference from
  naming and timing, not evidence, and it is not actioned.
- The link blast is **still running**: the most recent link in the dataset was first seen
  2026-10-06 15:01 UTC, the audit date itself. Whatever is produced now will be stale within
  weeks; the disavow file needs re-running monthly until new-domain velocity returns to
  baseline.
- No `rel="sponsored"` or UGC breakdown could be re-verified at the link level.
- Ahrefs' crawler finds links Semrush misses. The disavow should eventually cover the union
  of both tools. Re-run after **2026-10-25**.

---

## 7. Deliverable

`/home/user/test/backlink-audit/disavow-ngwindows.txt` — 66 `domain:` entries, every one
carrying its own inline evidence (shared path slug, exact anchor string, dofollow status),
grouped by network, with explicit NOT-DISAVOWED and INSUFFICIENT-EVIDENCE sections and the
preserved manual-review notes.
