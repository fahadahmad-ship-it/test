# parkersair.com — Backlink Audit & Disavow (delivery summary)

**Client:** Parker's Heating & Air Conditioning Inc. (parkersair.com) — HVAC contractor, Cordele / Leesburg, Georgia
**Date:** 2026-10-27
**Format:** signed-off Harbinger / New Image Canopy audit template (7 tabs, unchanged layout)

## Files
- `parkersair_backlink_audit.xlsx` — the workbook (Summary + 6 data tabs).
- `disavow_parkersair.txt` — the Google disavow file (1,641 `domain:` lines). **Reference only until the step below is done.**

## Headline numbers (live Semrush profile, not the old snapshot)
| Status | Domains | Backlinks |
|---|---:|---:|
| Spam (Disavow) | 1,650 | 1,699 |
| Spam (Nofollow, No Action) | 66 | 130 |
| Held (Pending Client) | 609 | 1,222 |
| Keep | 153 | 452 |
| Own Site | 0 | 0 |
| **Total referring domains** | **2,478** | **3,503** |

The disavow file carries **1,641** lines — the 1,650 dofollow-spam domains minus **9 redundant `mail.*` subdomains** already covered by their parent domain.

## What the data shows
1. **A large, actively growing link-scheme flood.** Referring domains roughly doubled **1,044 → 2,415 in one month** (31 Aug → 30 Sep 2026) and sit at 2,478 now — far above the figures in your tracking sheet. The audit was run against the **full live profile**.
2. **The two campaigns separate cleanly by target page.** Every one of the 1,650 disavow domains points **only at the home page** with keyword-stuffed SEO sales-copy anchors. The 609 held domains point at **deep `/services/…/cordele` and `/leesburg` pages** with genuine HVAC + Georgia-geo anchors — the signature of possibly-commissioned local SEO.
3. **Held ≠ valuable.** 522 of the 609 held domains have **zero organic traffic** in Semrush; they are low-quality directory/listing pages. They are held only because the anchor/target *could* indicate a paid placement.
4. **One file, one property.** No client-owned domains redirect into parkersair.com, and it is the only Search Console property, so a **single** disavow file covers everything.

## Your flagged anchor patterns (from the tracking sheet) — how each was handled
| Anchor pattern | In the audit |
|---|---|
| `…premium pbn network service parkersair.com …buy backlinks online cheap` | PBN sales-copy → **Spam (Disavow)** |
| `join our telegram https://t.me/s/darksidelinks` | link-scheme spam → **Spam (Disavow)** |
| `premium seo link building experts helping parkersair.com websites rank higher` | dominant anchor, ~1,396 domains → **Spam (Disavow)** |
| `reliable niche edit links for parkersair.com …` | niche-edit spam → **Spam (Disavow)** |

All four are the same network and are in the disavow file.

## The action that needs you (the "confirm with the client" step)
The **609 held domains** are listed on **Tab 5 (Exact Match Anchors)** with the exact-match commercial anchor, the market (Cordele / Leesburg / Americus / etc.), and a real example linking page — plus two blank input columns, **"Partner confirmed? (Y/N)"** and **"Final decision."** **Tab 6 (Pending Disavow Lines)** has the ready-to-append `domain:` line for each.

**Confirm with the client whether any outreach/placements were commissioned.**
- If **not commissioned** → append that domain's line from Tab 6 to `disavow_parkersair.txt`.
- If **commissioned** → leave it out (disavowing a paid placement would hurt rankings).

Per the brief, the SEO team records this disavow judgement **by end of October 2026.**

## Before uploading to Google
- **Confirm with the client whether a disavow file already exists** on the parkersair.com property. If one does, uploading **replaces** it — merge the existing entries in first. If the client confirms none exists, this is the first file.
- Do **not** upload before the held-link confirmation above. We do not submit to Search Console on your behalf.

## Method & limitations (full transparency)
- **Semrush is the metric source** for Authority Score, backlinks, referring domains, traffic and organic keywords (3,503 backlinks + 2,461 referring domains pulled in full; organic traffic/keywords pulled per domain for all 2,478). `no_data`/"NOTHING FOUND" from Semrush is recorded as a real zero (no audience — the key spam signal).
- **Every disavow line rests on visible evidence** (a spam anchor, a spam page title/URL, or a spam host name) — never on Authority Score, TLD, or shared IP alone. Verified both directions: 0 good links wrongly in the file, 0 dofollow-spam links wrongly kept out.
- **Ahrefs link-discovery/HTTP-status merge was not run** — it needs the client-pulled Ahrefs CSV exports, which weren't provided. Example-page status therefore rests on Semrush's last crawl. Supplying the Ahrefs CSVs later would only add links, not change the verdicts.
- The referring domain's own **"RD's"** column was left blank (no bulk Semrush source at this scale; it does not affect any disavow/hold decision, which rest on the anchor, target page and evidence).
