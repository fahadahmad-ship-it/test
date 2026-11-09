# Bolton Service WNC — backlink audit & disavow: delivery note

**Prepared for:** Bolton Service WNC (boltonservicewnc.com)
**Date:** 2026-11-09
**Deliverables in this folder (`bolton/out/`):**
- `Bolton_Service_WNC_Backlinks_Audit.xlsx` — the 7-tab audit workbook (Harbinger format).
- `disavow_boltonservicewnc.com.txt` — **the file to upload for the money site** (full union).
- `disavow_boltonwnc.com.txt` — upload for the boltonwnc.com property.
- `disavow_webolton.com.txt` — upload for the webolton.com property.

## What we found
- Your live link profile is **3,232 referring domains / 5,817 backlinks** — a large
  negative-SEO spam flood, not organic growth. Authority Score is 10.
- **The attack is recent and fast:** 1341 referring domains in September 2026,
  2850 by the start of November. The brief's figure was an older snapshot; we audited the full live profile.
- **Two separate campaigns, easy to tell apart:**
  - A link-scheme flood of PBN "SEO sales copy" anchors (e.g. *"High Quality Dofollow Backlinks DA 50 PA 40 …"*)
    pointed at your **home page**. This is the attack.
  - A set of directory links with **exact-match local service anchors** (e.g. *"AC Service Swannanoa NC"*)
    pointed at deep **/service/** and **/location/** pages. These *may* have been commissioned, so they are **held**.

## The verdict (every one of the 3,232 domains classified)
| Status | Domains | Backlinks |
|---|---:|---:|
| Spam (Disavow) | 2,294 | 3,601 |
| Held (Pending Partner) | 590 | 1,127 |
| Held (Nofollow, No Action) | 31 | 107 |
| Spam (Nofollow, No Action) | 185 | 506 |
| Keep | 129 | 465 |
| Own Site | 3 | 11 |

- **2,294 domains go in the disavow file** (confirmed spam with at least one dofollow link).
- **185 spam domains need no action** — every link is nofollow, so they pass nothing.
- **590 domains are HELD** for the previous supplier to confirm before any disavow.

## Redirects & which file to upload
You own two domains that 301-redirect into the site — **boltonwnc.com** and **webolton.com** — and the spam
targets them by name. Semrush rolls their links into the money-site profile, so one audit captured everything.
You told us you can upload to **all three** Search Console properties, so there is one file per property:
- **`disavow_boltonservicewnc.com.txt` is the full union of every bad domain** (1,921 point
  directly at the money site; the rest reach it through the two redirects). Upload this one to the money-site property.
- `disavow_boltonwnc.com.txt` (222) and `disavow_webolton.com.txt`
  (668) each carry only the domains whose links point at that property.

Before uploading: **confirm whether a disavow file already exists** on each property. If one does, uploading
**replaces** it — merge first. If none exists, these are the first files.

## Before you submit — the supplier conversation
The brief calls the party who confirms commissioned links the **"supplier"**; the workbook calls the same role
**"partner"** throughout (so every audit reads the same). The 590 held domains carry exact-match
commercial anchors or links to deep money pages that *could* be paid placements. **Do not upload any disavow file
until the supplier confirms which of those anchors were commissioned.** Tab 5 (Exact Match Anchors) and Tab 6
(Pending Disavow Lines) list exactly what to ask about; the two blank columns on Tab 5 are for their answers.

## Manual review before you upload (4 domains)
These are IN the disavow file on visible evidence (an off-topic anchor or a link injected at the
site's /sitemap), but they also have some organic traffic, so confirm each by hand before submitting
— a judgement call, not an error:
- `upc.edu.pe` — organic traffic 29,141; Off-topic (casino/pharma/etc.) anchor. 
- `ozogeeks.com` — organic traffic 430; Link injected at client /sitemap page. 
- `abacaresstaffing.com` — organic traffic 82; Off-topic (casino/pharma/etc.) anchor. 
- `thesigningstore.com` — organic traffic 64; Link injected at client /sitemap page. 

## Honest limits
- **Metrics source:** Authority Score, backlinks and referring-domain counts are from **Semrush**; per-domain
  organic **Traffic and Organic Keywords are from Semrush `domain_rank`** (the correct primary source). The
  Ahrefs API workspace hit its monthly unit ceiling mid-audit (resets 2026-11-25), so Ahrefs contributed only a
  100-domain metrics sample and no second link-discovery pass; this does **not** affect any disavow decision —
  every one rests on the visible anchor, page title, or host, never on a score.
- **Live-page status** of example links rests on Semrush's last crawl (we could not fetch every linking host).
- We have **not** submitted anything to Google Search Console — that is yours to do after the supplier confirms.
