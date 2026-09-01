# Backlink Audit & Disavow Preparation — ngwindows.com

**Date:** 2026-09-01
**Sources:** Ahrefs (Site Explorer referring domains + anchors) and Semrush (Backlink Analytics referring domains)
**Purpose:** Identify manipulative / toxic referring domains and stage a Google disavow file. **Every disavowed domain is flagged with explicit evidence for your manual review before submission.**

---

## 1. Headline finding

ngwindows.com carries a **heavily manipulated, paid-PBN backlink profile**. This is not a borderline call — the link scheme announces itself in the anchor text itself. Sample anchors pulled from Ahrefs (all `is_spam=true`, seen across 200+ referring domains):

- *"There was a time when ngwindows.com struggled to make an impact online… A friend recommended **SEOExpress.org and their backlink building service** truly worked wonders! In less than two months, my site's traffic increased by over 400%"* — **222 referring domains**
- *"Complete SEO for ngwindows.com: **premium guest posts, contextual backlinks**, on-page and local SEO… delivering durable DR/DA/TF gains"* — **44 referring domains**
- *"**High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service** ngwindows.com Rank First Page Google Fast SEO Link Building **Buy Backlinks Online Cheap**"* — **21 referring domains**
- *"JOIN OUR TELEGRAM https://t.me/s/darksidelinks"* — 10 referring domains
- Random gibberish anchors (e.g. `tLvtiPx5V2OVDzj`), wallpaper/scraper spam, gambling anchors.

The anchor profile alone is grounds to disavow the manipulative portion of the profile.

---

## 2. Profile size

| Metric | Ahrefs | Semrush |
|---|---|---|
| Total backlinks | — | 5,206 |
| Referring domains (pulled) | 250 | 559 |
| Ahrefs `is_spam=true` (of 250 pulled) | 77 | — |

- **Unique referring domains after merge: 803** (241 Ahrefs-only, 553 Semrush-only, 9 in both).
- The low overlap means the two tools surface *different* slices of the spam network — using both materially widens coverage.

---

## 3. Classification method (how each domain was validated)

Each domain was scored on **independent, corroborating signals** — no domain is disavowed on a single soft metric alone:

- **Name footprint** — domain name is itself a spam category (backlink-seller, `*.blogspot.com` PBN, gambling/casino, adult, URL-shortener, expired-domain catcher, "website-worth/stats" generator, spam directory).
- **Ahrefs `is_spam=true`** — Ahrefs' own spam classifier.
- **Dedicated link-network IP** — ≥4 of ngwindows' referring domains share one **non-CDN** IP (Cloudflare / Google / AWS shared ranges were excluded so co-location on a CDN is never counted as a network).
- **Known link-farm IP block** (e.g. `118.139.*`, `203.161.54.114`, `184.168.*`, Moldova `195.20.19.178`).
- **Dead / zero-value** — Domain Rating / Authority Score ≤3, **0 organic traffic, 0 ranking keywords**.
- **Geo** — Moldova spam-cluster hosting.

### Confidence tiers
| Tier | Rule | Action |
|---|---|---|
| **HIGH** (316) | Self-evident name/host footprint, **or ≥2 independent toxic signals** | In `disavow.txt` — strong recommend |
| **MEDIUM** (327) | Exactly one strong toxic signal | In `disavow.txt` — verify then submit |
| **REVIEW** (97) | Low authority only, no hard footprint | **NOT** auto-disavowed — your call |
| **KEEP** (63) | Recognized brand / authority ≥30, no toxic footprint | **Protected — do not disavow** |

---

## 4. Results (evidence-tiered — verified at backlink level)

Every flagged domain was checked against its **actual backlink** (real source URL, anchor, follow status pulled from Semrush + Ahrefs). That lets us tier by strength of evidence rather than lump everything together:

- **P1 — Core: 312** — clear spam footprint or ≥2 independent signals. Disavow with confidence.
- **P2 — Recommended: 209** — a dead/low-quality domain that **also** carries a corroborating link signal (dofollow, money/spam anchor, farm-IP, or Ahrefs `is_spam`).
- **➡ Recommended disavow = P1 + P2 = 521 domains** (this is what `disavow.txt` submits by default).
- **P3 — Optional: 107** — flagged on a *single* "dead/low-quality" signal only, where the actual link is **nofollow + a branded mention** and nothing else. Not clearly manipulative, so **left commented-out** in `disavow.txt`; uncomment to push the total to 628.
- **Manual review: 112** (+ the 107 P3) — includes the window-microsite cluster.
- **Protected (KEEP): 63 domains**

**Why not 628?** The earlier 628 counted 316 "MEDIUM," of which 110 rested on one soft "dead domain" signal. Judged against the real link (nofollow, branded, no other spam marker), those aren't clearly manipulative — Google advises disavowing only clearly manipulative links — so they moved to P3/Optional. — e.g. apple.com, yahoo.com, bing.com, pinterest.com, bbb.org, yellowpages.com, nextdoor.com, zoominfo.com, porch.com, expertise.com, glass.com, glassonweb.com, windowanddoor.com, windowdigest.com, constantcontact.com, chamberofcommerce.com.

### Critical QA / second-look (every decision re-checked)
An independent verification pass re-examined each domain and surfaced **57 QA items**, of which ~29 are genuine judgment calls a human should confirm (the rest are positive "confirmed by both tools" notes). The QA rules catch: *passed-but-toxic*, *flagged-but-has-real-traffic*, *high-authority-but-off-topic (possible paid guest post)*, and *own-network*. See the **QA Second-Look** tab / `qa_note` column.

### ⚠️ Window-company microsite cluster — DO NOT blind-disavow (15 domains, now REVIEW)
A cluster of near-identical window-brand domains sits on shared AWS IPs (`15.197.225.128`, `15.197.142.173`, `3.33.152.147`, `3.33.251.168`): **ngawindows.com, ngwindow.com, northgawindows.com, northgeorgiawindow.com, northgeorgiawindows.net, roiwindows.com, thermalprowindows.com, thermalastwindows.com, thermatrustwindows.com, northpointwindows.com, performingwindows.com, qualitypluswindows.com, choiceviewwindows.com, e2windows.com** (+ `windowdoor-test.com`, an apparent staging domain). Because the client is *North Georgia Windows*, these are very likely **the client's own microsites / typo-domains or a self-built PBN**. They were moved out of the disavow set into **REVIEW** — confirm ownership first: you disavow a *third-party* PBN, but you redirect/consolidate your *own* sites rather than disavow them.

### HIGH-confidence category breakdown
| Category | Domains |
|---|---|
| Multi-signal spam (2+ signals) | 134 |
| Link-selling / SEO-service PBN (name footprint) | 66 |
| Blogspot PBN / keyword-stuffed spam posts | 53 |
| URL-shortener / redirect link network | 18 |
| Auto-generated stats / "website-worth" pages | 10 |
| Low-quality directory / TLD-list spam | 10 |
| Gambling / casino spam | 9 |
| Free-host throwaway pages | 9 |
| Expired-domain / auto network | 5 |
| Adult spam | 2 |

### Largest identified link networks (by shared dedicated IP)
| Referring domains | IP | Notes |
|---|---|---|
| 32 | 118.139.181.85 | Singapore link-farm (`*.co.in`, `*.space`, directory spam) |
| 27 | 203.161.54.114 | "buy backlinks" seller farm (`*backlinks*.com`) |
| 19 | 195.20.19.178 | Moldova URL-shortener / redirect network |
| 9 | 118.139.176.46 | Same SG farm cluster |
| 9 | 184.168.115.60 | Domain-stats / worth-checker generator farm |
| 6 | 67.223.118.29 | SEO-link / gambling mix |
| 5 | 118.139.161.199 | `backlink*` seller cluster |
| 5 | 188.40.17.96 | `locabee.*` / `wogibtswas.*` cluster |

The `rankvance*` family (rankvance.info/.online/.website + agency/authority/links/boost variants — ~13 domains) is a single SEO-service network caught by name footprint.

---

## 5. Files in this folder

| File | What it is |
|---|---|
| `ngwindows_backlink_audit.xlsx` | **Master workbook — everything in tabs:** Summary · All Domains · Disavow-HIGH · Disavow-MEDIUM · Manual Review · Keep · QA Second-Look · Link Networks · Toxic Anchors · Ahrefs raw · Semrush raw. Colour-coded by decision. |
| `disavow.txt` | **Google-format disavow file**, `domain:` entries, grouped HIGH then MEDIUM with category comments. Ready to submit after your review. |
| `disavow_flagged_for_review.csv` | Every flagged domain (628 disavow + 112 review) with confidence, category, evidence, and QA note. |
| `merged_all_domains.csv` | All 803 domains incl. the 63 KEEP, with full signals + decision + QA note. |
| `ahrefs_refdomains.csv` / `semrush_refdomains.csv` | Raw pulls from each source. |
| `toxic_anchors.txt` | The smoking-gun spam anchor texts. |

---

## 6. Recommended next steps

1. **Review `disavow_flagged_for_review.csv`.** Start with MEDIUM "Single-signal low-quality" (322) — these are dead/zero-traffic domains flagged on one signal; confirm none is a small legitimate partner/local site before including.
2. Sanity-check the **REVIEW** list (97) — mostly small local/niche sites; move any obvious spam into disavow, leave legitimate ones out.
3. Confirm the **KEEP** list (63) — verify nothing you actually want to disavow slipped in (a couple of high-authority-but-thin blogs sit near the 30 cutoff).
4. Submit the finalized `disavow.txt` in **Google Search Console → Disavow Links Tool** at the **domain** level (already formatted as `domain:`).
5. Consider outreach/removal for any links you can actually get taken down before disavowing; disavow is the fallback.

> Disavow is a powerful, slow-to-reverse tool. This audit deliberately splits HIGH / MEDIUM / REVIEW so you disavow the proven scheme aggressively while manually adjudicating the ambiguous tail.
