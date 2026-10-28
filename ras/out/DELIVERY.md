# RAS Systems — Backlink Audit & Disavow Review
*Prepared by Harbinger Marketing — 2026-10-28*

## The short version

- Your referring-domain profile is under a large, **active link-selling / negative-SEO flood**. Of **3,552 referring domains**, **3,286 are spam** (2,543 with a dofollow link that passes value — these go in the disavow file — and 743 nofollow that need no action).
- The brief's figure (about 458 referring domains, 183 link-selling) was a months-old snapshot. The attack has since **roughly quadrupled**: Semrush counted ~629 referring domains in September and **2,815 now**; with Ahrefs-only discoveries the full live profile is **3,552**. We audited the full live profile, not the brief's list.
- **65 domains are held**, not disavowed — they carry exact-match product anchors or point at deep product pages and *may* have been commissioned by a previous SEO partner. **Nothing is submitted to Google until that question is answered.**
- **201 domains are genuine** (real directories, business listings and editorial mentions) and are kept.

## What's actually happening

Two separate campaigns, easy to tell apart by the page they point at:

1. **The link-selling flood (the problem).** 5,279 of 5,995 links (88%) point at the **home page**, carrying keyword-stuffed SEO sales-copy anchors that advertise a backlink service and name your own domains (ras-systems.com, rasmachines.com, ras-systems.net). This is the negative-SEO / link-spam pattern.
2. **The commissioned-looking set (the open question).** A much smaller set uses exact-match product anchors (e.g. *Panel Bending Machine*, *Metal Folding Machinery*, *FLEXIbend*) or points at deep `/products/` pages. These look like they could have been paid placements. They are **held** for the partner to confirm.

The nine link-selling anchor families driving the flood:

   - "High Authority … Backlinks for … SEO Ranking Growth" — ~1,598 links
   - "… Premium SEO Links for Higher … Rankings" — ~1,429 links
   - Other link-selling sales copy — ~336 links
   - SEO-LINK.VIP / SEOExpress link vendors — ~275 links
   - TELEGRAM @… link-service handles — ~268 links
   - "High Quality Dofollow Backlinks DA 50 PA 40 … PBN Network Service" — ~259 links
   - Guest-post service ("Proven/Expert Guest Post Service for …") — ~171 links
   - "Effective PBN Backlinks for … Strengthen Your Link Profile" — ~88 links
   - MASSLINKER.COM backlink software — ~61 links

## The redirect reality — one file to upload

Three domains you own 301-redirect into the money site, so Semrush folds their inbound links into ras-systems.com's profile:

| Redirects into ras-systems.com | Spam domains attributed |
|---|---|
| rasmachines.com | 1,643 |
| ras-systems.net | 229 |
| ras-systems.us | 0 |

A disavow file applies to **one** Search Console property. We produced one file per property, but the **`disavow_ras-systems.com.txt`** file carries the **complete union** of every bad domain (2,543 domains) — because all owned domains redirect into the money site and Google forwards disavow signals across redirects imperfectly. 
**If you can only upload to the ras-systems.com Search Console property (the usual case), submit that one file and ignore the rest.** If you have Search Console access to the redirect domains too, you may upload their per-property files as well. Please tell us which properties you can upload to.

## Before you upload — two decisions we need from you

1. **The commissioned question (blocking).** Were any of the **65 held domains** paid for by your previous SEO partner? If yes, name them and we remove them from consideration; if no, we append them to the disavow file. Until you answer, they stay out. (Worth knowing: held does **not** mean valuable — 53 of the 65 held domains have no organic traffic at all.)
2. **Disavow vs. dilute.** Uploading a disavow file is the direct fix, but it is a strong signal to Google and is not easily reversed. The alternative is to **dilute** the spam by building a steady stream of genuine, branded, on-topic links so the bad ratio falls over time, and disavow only the worst offenders. Our recommendation: **disavow the 2,543 confirmed-spam dofollow domains** (they are unambiguous link-spam and carry no value to lose), and run branded-link building alongside to rebuild profile health. We can set out a dilution plan if you prefer to hold off on disavowing.

## Honest limits

- **Nothing has been submitted to Google.** The disavow files are drafts pending your answer on the held set.
- We have **not** been told whether a disavow file is already filed on ras-systems.com. If one exists, uploading ours **replaces** it — check first and send us any existing file so we can merge.
- Organic traffic / keyword figures are Semrush. For the low-authority spam domains that Semrush holds no organic data for, we record a true zero (spot-checked); that absence of any audience is itself the clearest sign the domain is a link farm.
- Linking-page live status reflects each tool's last crawl (5,852 of 5,995 link sources last seen returning HTTP 200).

## Files in this delivery

- `RAS_Systems_Backlinks_Audit.xlsx` — the full 7-tab audit workbook.
- `disavow_ras-systems.com.txt` — **the file to upload** (full union; do not upload before the held question is answered).
- `disavow_rasmachines.com.txt`, `disavow_ras-systems.net.txt` — per-property reference files.
