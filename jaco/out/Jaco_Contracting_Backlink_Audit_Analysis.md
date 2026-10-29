# Backlink Audit — Critical Analysis: jacocontracting.com

*Prepared 2026-10-29 · Harbinger Marketing format · Semrush = metric source, Ahrefs = discovery + live-page corroboration*

## Headline

**jacocontracting.com is under an active, accelerating negative-SEO / PBN link-spam attack.** Of **2,212 referring domains** now in the live profile, **1,773 (80%) are spam**. **1,166 carry at least one dofollow link and go in the disavow file**; 607 more are spam but entirely nofollow (no action needed). **259** domains are **held** for the previous SEO partner to confirm before any disavow, because they carry exact-match commercial anchors or deep-page links that may have been commissioned. **180** are genuine and kept.

## The profile at a glance

| Status | Domains | Backlinks | Share of domains |
|---|---:|---:|---:|
| Spam (Disavow) | 1,166 | 1,207 | 52.7% |
| Held (Pending Partner) | 142 | 1,606 | 6.4% |
| Held (Nofollow, No Action) | 117 | 395 | 5.3% |
| Spam (Nofollow, No Action) | 607 | 659 | 27.4% |
| Keep | 180 | 628 | 8.1% |
| Own Site | 0 | 0 | 0.0% |
| **Total** | **2,212** | **4,495** | **100%** |

- Live profile (Semrush): **3,258 backlinks / 1,292 referring domains / Authority Score 17**. Ahrefs: DR 21.
- Merged Semrush + Ahrefs: **4,495 unique links across 2,212 referring domains** (1,360 links discovered only by Ahrefs).
- **One Search Console property.** Every link points directly at jacocontracting.com; no owned domains 301-redirect in, so a single disavow file (`disavow_jacocontracting.txt`) covers the whole profile.

## Seven findings

1. **1,773 of 2,212 referring domains are spam.** 1,166 have a dofollow link and are in the disavow file; 607 are nofollow and pass no value.
2. **The attack is recent and accelerating.** Referring domains sat at ~200–280 for most of 2025–early 2026, then climbed 362 (Jul 26) → 406 (Aug) → 526 (Sep) → **1,289 (Oct 2026)**. Of the 1,166 disavow domains, **1,074 first appeared in Sep–Oct 2026** — the spam roughly tripled the profile in two months. The brief's older figures are a stale snapshot; this audit covers the full live profile.
3. **One file covers everything.** No redirect/owned domains feed the site, so you upload a single file for the jacocontracting.com property. (Confirm whether a disavow file already exists on the property first — uploading replaces it.)
4. **Two campaigns, easy to tell apart by target page.** **2,505 link-scheme / sales-copy / naked-URL links hit the home page**; the **503 exact-match commercial links hit deep location & service pages** (Covington, Atlanta, Chattanooga, Macon roofing pages). The home-page flood is the attack; the deep-page commercial anchors are what may have been commissioned.
5. **The dominant anchor is backlink sales copy naming the client's own domain.** "Premium Backlink Experts for jacocontracting.com Websites Seeking High…" appears on **912 domains**. The whole anchor profile is dominated by PBN templates such as "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service…".
6. **259 domains are held for the partner**, in case any exact-match commercial placements were paid for. They are **excluded from the disavow file** until confirmed. The big one, `addirectory.org`, alone auto-generates 664 "Roofing Contractor Covington" links.
7. **Held does not mean good.** 196 of the 259 held domains have zero organic traffic. Several spam clusters share a /24 subnet — 118.139.181.0/24 (30), 195.20.19.0/24 (17), 5.100.156.0/24 (13) — i.e. single operators running many domains (Cloudflare/CDN ranges excluded). No domain is disavowed on a shared IP alone.

## Anchor-text profile (all backlinks)

| Anchor type | Backlinks | Share | Referring domains |
|---|---:|---:|---:|
| Spam: keyword stuffed SEO sales copy | 1,699 | 37.8% | 1,654 |
| Exact match commercial (geo) | 1,206 | 26.8% | 201 |
| Naked URL | 858 | 19.1% | 258 |
| Generic | 358 | 8.0% | 75 |
| Exact match commercial | 244 | 5.4% | 146 |
| Empty or image | 43 | 1.0% | 18 |
| Spam: off topic | 42 | 0.9% | 30 |
| Contextual or other | 41 | 0.9% | 19 |
| Branded | 4 | 0.1% | 2 |

## What is genuine (kept)

The audit protects real citations. Highest-authority kept domains include:

| Domain | Authority Score | Organic traffic | Links |
|---|---:|---:|---:|
| bbb.org | 80 | 5,384,918 | 2 |
| nextdoor.com | 74 | 3,663,900 | 1 |
| yellowpages.com | 73 | 5,408,904 | 20 |
| rocketreach.co | 73 | 940,472 | 1 |
| birdeye.com | 68 | 1,123,631 | 3 |
| dnb.com | 67 | 462,007 | 1 |
| contactout.com | 55 | 120,903 | 1 |
| loc8nearme.com | 52 | 59,964 | 1 |
| gaf.com | 51 | 430,075 | 3 |
| sitelike.org | 51 | 13,491 | 2 |

## Method & evidence rules

- **Semrush is the source for every metric** (Authority Score, backlinks, referring domains, traffic, keywords). Ahrefs contributes extra link discovery and the live-page HTTP check only — never a metric.
- **Nothing is disavowed on a score, a TLD, or a shared IP alone.** Every disavow line rests on visible evidence: a spam anchor, a spam page title, or a known link-network / backlink-marketplace host name.
- **When in doubt, hold.** Exact-match commercial anchors and deep money-page links may be commissioned placements; they are held for the previous partner, never auto-disavowed.
- Off-topic spam (gambling / pharma / adult / malicious Telegram links) is treated as spam even when a domain also carries a commercial anchor — it is never a legitimate commissioned placement.

## Deliverables

- **`Jaco_Contracting_Backlinks_Audit.xlsx`** — 7 tabs (Summary, Referring Domain Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List), signed-off Harbinger format.
- **`disavow_jacocontracting.txt`** — 1,166 `domain:` lines, grouped by reason, for the jacocontracting.com Search Console property.

## Before you upload — required steps

1. **Confirm the Held set with the previous SEO partner / the business.** If any held domains were commissioned placements, do not disavow them; append the rest from the *Pending Disavow Lines* tab.
2. **Check whether a disavow file already exists** on the Search Console property. If one does, uploading **replaces** it — merge first. If the client has checked and there is none, this is the first file.
3. Do not submit to Google Search Console on the client's behalf without sign-off.

