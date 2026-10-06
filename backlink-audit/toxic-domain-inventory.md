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
or hosting as grounds for disavowal.** Those signals are descriptive, not probative, and in
this dataset they point the wrong way in both directions: 27 link sellers here hold Ahrefs
**DR 59–60**, while genuine local businesses such as `forsythcounty.com` and
`georgiashutters.com` sit at **DR 3.6 and 2.2**.

A domain is disavowed only on per-domain evidence, under one of two qualifying criteria,
behind one gate:

| | Criterion | Why it is probative |
|---|---|---|
| **1** | **Observed vendor sales-copy anchor** + **shared structural fingerprint** (same path slug with the same numeric id recurring across unrelated registrations) | Anchor text is author-controlled. Independent sites do not coincidentally publish `/dir/backlink-seo-experts-211287` with identical anchor copy. |
| **gate** | **`rel="nofollow"` must be absent** | A nofollow link passes no PageRank and cannot be the mechanism of a link penalty. Vendor links that are nofollow are recorded but never disavowed. |
| **3** | **Domain-name character** — the registrable domain is itself a link-selling brand (`*backlink*`, `*buybacklinks*`, `*seolinks*`, `*dachecker*`, `*rankchecker*`) | Criterion 1 alone misses high-DR sellers that use benign bare-URL anchors. The name is a declaration of purpose independent of any one link. |

**Criterion 3 exists because criterion 1 is not sufficient on its own.** The 27 domains on
host 203.161.54.114 — `99backlinksbuy.com`, `buyfairbacklinks.com`,
`clicktobuybacklinks.com`, `webrankingsolutionbacklinks.com` and the rest — would pass both
an anchor test and any DR threshold. Verified on the Ahrefs free endpoint, **all 27 return
DR 59–60**. A uniform DR block across 27 unrelated registrations on one IP is itself a
signature of artificially inflated seller sites.

### The scope rule that matters more than any of the above

**~94% of this spam campaign does not point at ngwindows.com at all.** It points at 14
content-free domains that 301-redirect into ngwindows.com. Those links are removed **at
source** by deleting the redirects, which is strictly better than disavowing them. The
disavow file is therefore scoped to the **~283 directly-pointing links only**; everything
redirect-borne is routed to a remediation section instead.

---

## 2. Classification counts

| Bucket | Domains | Basis |
|---|---:|---|
| **TOXIC-CRITICAL — disavowed (criterion 1, direct target)** | **5** | Observed vendor anchor naming ngwindows.com itself + dofollow + shared slug |
| **TOXIC-CRITICAL — disavowed (criterion 3, name character)** | **29** | Link-selling brand name; 27 of them share host 203.161.54.114 at DR 59–60 |
| **Total disavow entries** | **34** | |
| TOXIC — evidenced but **redirect-borne**, resolved by deleting the 301 | 61 | Vendor anchor + dofollow + shared slug, but anchor targets a shell domain |
| Operator-controlled **301 redirect shells** — delete, do not disavow | 14 | Content-free redirect domains; destination of ~94% of the campaign |
| NOT DISAVOWED — vendor anchor but **nofollow** | 2 | Fails the dofollow gate |
| NOT DISAVOWED — **benign anchor observed** | 5 | Bare domain/URL or generic phrase |
| **PROTECTED** — explicit exclusion list for any future sweep | 15 | Legitimate local/trade sites, several at DR 2–18 |
| **INSUFFICIENT EVIDENCE — excluded** | **1,159** | No anchor/dofollow/routing data retrievable |
| **Total referring domains enumerated** | **1,232** | |

Two of the evidenced domains (`urlbacklinkschecker.space`, `backlinkcheckerseo.space`)
appear in the `backlinks` report but **not** in the 1,232-row `backlinks_refdomains` list —
Semrush's own two endpoints disagree.

**The disavow file shrank from 66 entries to 34, and that is the correct direction.** 61 of
the 66 were evidenced manipulative links that nonetheless should not be disavowed, because
they are placed against redirect shells the operator controls and can simply delete.

### The AS 0–5 band, answered directly

The band contains **1,015 referring domains** (82.4% of 1,232) carrying **6,078 backlinks**.
The anchor-text split requested can only be reported for the 70 of them covered by the one
page of anchor data:

| Sub-bucket of AS 0–5 | Domains | Share of the 1,015 |
|---|---:|---:|
| (a) vendor sales-copy anchor, **dofollow** — of which: | 64 | 6.3% |
| &nbsp;&nbsp;→ targets ngwindows.com directly → **disavowed** | 5 | 0.5% |
| &nbsp;&nbsp;→ targets a 301 redirect shell → **delete the redirect instead** | 59 | 5.8% |
| (a-nf) vendor sales-copy anchor, nofollow | 2 | 0.2% |
| (b) bare domain-name / bare-URL anchor | 4 | 0.4% |
| (c) empty / image anchor | 0 observed | — |
| (d) genuine-looking anchor | 0 observed in this band | — |
| **no anchor data retrievable** | **945** | **93.1%** |

**This is the honest answer and it is mostly a gap.** 93% of the AS 0–5 band has no anchor
evidence either way. The prior draft treated the whole band as toxic; that was an unsupported
inference, and the corrected position is that **only 64 of 1,015 AS 0–5 domains (6.3%) can
currently be shown to be manipulative — and only 5 of those 1,015 (0.5%) are both
manipulative and pointing at ngwindows.com directly.**

---

## 3. The two evidenced networks

### Network A — shared-slug `/dir/` vendor network (59 domains, all dofollow)

Only **one of the six clusters targets ngwindows.com directly**; the other five name a
redirect shell in their anchor and are resolved by deleting that shell's 301.

Six distinct page slugs, each reused verbatim across many unrelated domains, each carrying
one fixed anchor string:

| Shared path | Domains | Fixed anchor on every one |
|---|---:|---|
| `/dir/backlink-seo-experts-211287` | 15 | "Professional thermalprowindows.com SEO Backlinks for Stronger Website Authority" |
| `/dir/seo-ranking-links-170322` | 10 | "Expert Backlink Building Services to Grow qualitypluswindows.com Website Rankings" |
| `/dir/professional-seo-links-148030` | 10 | "ngawindows.com Premium Link Building Experts for Website Ranking Growth" |
| `/dir/trusted-seo-backlinks-150104` | 10 | "northpointwindows.com Premium SEO Links for Higher Search Engine Rankings" |
| `/dir/ethical-seo-backlinks-160633` | 9 | "performingwindows.com Premium SEO Backlinks for Higher Google Rankings and Organic Traffic" |
| `/dir/quality-authority-backlinks-148096` | 5 | "Increase Google Visibility with High Quality Backlinks ngwindows.com" — **DIRECT, disavowed** |

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

### 5.1 The spam is not aimed at ngwindows.com — it is aimed at 14 redirect shells

The draft read anchors like `ngawindows.com`, `roiwindows.com`, `thermalprowindows.com` as
proof of a vendor blasting a scraped list of window companies, with ngwindows.com an
innocent bystander. The `redirect_url` field shows the opposite: those domain names in the
anchors are not *mentions*, they are the **link targets**. Fourteen content-free domains
301-redirect into ngwindows.com, and ~94% of the campaign lands on them:

`ngawindows.com` · `roiwindows.com` · `thermalprowindows.com` · `qualitypluswindows.com` ·
`northpointwindows.com` · `performingwindows.com` · `thermatrustwindows.com` ·
`northgeorgiawindows.net` · `thermalastwindows.com` · `e2windows.com` ·
`choiceviewwindows.com` · `ngwindow.com` · `northgawindows.com` · `northgeorgiawindow.com`

Four of the fourteen are near-exact brand variants of the client. They cluster on three AWS
Global Accelerator IPs (15.197.225.128, 15.197.142.173, 3.33.251.168) and first appeared
Jul 2024 – Jul 2025, a year before the blast.

Two consequences, and they are the whole remediation plan:

1. **This reframes attribution.** A negative-SEO attacker does not build 14 redirect shells
   into the victim. This reads as a purchased or managed campaign run on behalf of the
   ngwindows.com property. The residual uncertainty is registrant identity, which could not
   be checked from this environment — **put it to the client directly**.
2. **Deleting the redirects beats disavowing.** It severs ~94% of the spam at source, removes
   it from Google's view entirely rather than merely asking Google to ignore it, and requires
   no Search Console submission. The disavow file is left covering only the ~283 links that
   hit ngwindows.com directly.

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

Conversely the disavowed domains include several at DR 0 **and** the evidence against them
has nothing to do with their DR. Any AS/DR threshold applied to this profile would have
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
- **Section 2 of the disavow file (29 name-character entries) has unverified anchors and
  unverified redirect routing.** It rests on domain-name character plus the shared-host /
  uniform-DR-60 fingerprint. It is the weaker half of the file and can be dropped if a
  minimal submission is preferred.
- Registrant identity of the 14 redirect shells could not be checked from this environment.
  That single fact decides whether this is a cleanup or a defence.
- No `rel="sponsored"` or UGC breakdown could be re-verified at the link level.
- Ahrefs' crawler finds links Semrush misses. The disavow should eventually cover the union
  of both tools. Re-run after **2026-10-25**.

---

## 7. Deliverable

`/home/user/test/backlink-audit/disavow-ngwindows.txt` — **34** `domain:` entries, each
carrying its own inline evidence (shared path slug + exact anchor + dofollow status, or
link-selling brand name + shared host + verified Ahrefs DR), with:

- an explicit scope statement that the file covers direct links only;
- a **"DO NOT DISAVOW — RESOLVE BY DELETING THE REDIRECT"** section naming the 14 shells and
  all 61 redirect-borne vendor domains, so the evidence is preserved without being actioned;
- a **PROTECTED** list of 15 legitimate low-DR local and trade sites that any future
  authority-threshold sweep must exclude;
- the carried-forward manual-review notes on `derchidoor.com`, `csswinner.com`,
  `atlantahomeimprovement.com`, `constantcontact.com` and `24-7pressrelease.com`;
- a closing coverage statement: **5.9% of referring domains anchor-verified, 94.1%
  unverified and deliberately excluded.**
