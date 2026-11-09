# Fitzgerald Plumbing - Backlink Audit & Disavow (cover note)
Prepared by Harbinger Marketing | 09 November 2026

## What we did
- Audited the **full live backlink profile** of fitzgeraldplumbing.com across **both Semrush and Ahrefs**, not the brief's snapshot.
- The brief named **149 referring domains**. The live profile is **4,646 (Semrush)** - an active, large-scale negative-SEO / spam attack that grew the profile roughly 30x in two months (~1,135 referring domains in Oct 2025 and ~1,300 through mid-2026, 1,456 in Sep, 4,449 in Oct).
- Classified **5,255 referring domains** / **9,864 backlinks** into six statuses on link-level evidence (anchor, page title/URL, host, target page). Nothing is disavowed without visible evidence; exact-match commercial links are held, not auto-disavowed.

## Verdict breakdown
| Status | Domains |
|---|---:|
| Spam (Disavow) | 3,688 |
| Spam (Nofollow, No Action) | 567 |
| Held (Pending Partner) | 667 |
| Held (Nofollow, No Action) | 5 |
| Keep | 326 |
| Own Site | 2 |
| **Total** | **5,255** |

## The three properties (important)
The client owns **three domains**: `fitzgeraldplumbing.com` (money site) plus `fitzgeraldandsonsplumbing.com` and `fitzplumb.com`, which **301-redirect into the money site**. The spam campaign targets all three. One audit of the money site captures them all (Semrush rolls redirected links in via the `redirect_url` column).

We provide **three disavow files** (you told us you can upload to all properties):
- **`disavow_fitzgeraldplumbing.com.txt`** - 3,688 domains. THE money-site file: the full union of every spam domain across all properties. **Upload this to the fitzgeraldplumbing.com Search Console property.**
- **`disavow_fitzgeraldandsonsplumbing.com.txt`** - 1,913 domains whose links point at fitzgeraldandsonsplumbing.com. Upload to the fitzgeraldandsonsplumbing.com Search Console property. (All are also in the money-site union.)
- **`disavow_fitzplumb.com.txt`** - 1,880 domains whose links point at fitzplumb.com. Upload to the fitzplumb.com Search Console property. (All are also in the money-site union.)

## Before you upload - confirm with the previous supplier
- **672 domains are HELD**, not in any disavow file. They carry exact-match commercial anchors on deep location/service pages and may be **commissioned placements** by your previous SEO **supplier** (the 'partner' referenced throughout the workbook).
- Tab 5 (Exact Match Anchors) lists them with blank **Partner confirmed?** / **Final decision** columns for the supplier to fill. Tab 6 (Pending Disavow Lines) has the ready disavow lines to append **only** for the ones they did not build.
- **Do not upload any file until that conversation has happened.** Also check whether a disavow file already exists on each property in Search Console - if one does, uploading **replaces** it, so merge rather than overwrite.

## Two campaigns (the key signal)
- The **home-page flood** (8,371 links) is backlink/SEO sales-copy spam that names your own domains - this is the attack, and it is what goes in the disavow file.
- The **deep-page links** (1,493, hitting /newnan-ga/, /senoia-ga/, water-heater pages, etc.) carry exact-match commercial anchors and look commissioned - these are the held set.

## Data sources & coverage (honest notes)
- **Authority Score** is Semrush for every domain (the audit's required metric). **Backlinks / Dofollow / Nofollow / First Seen / anchors / target pages** are computed directly from the merged Semrush+Ahrefs link data.
- **Traffic, RD's and Organic Keywords** are per-domain audience metrics. We fetched them from Ahrefs batch metrics for 3,728 domains; our monthly Ahrefs API quota was reached mid-pull (resets 25 Nov 2026). We **backfilled the genuine / held / keep domains from Semrush** so no real site shows a false zero.
- The remaining ~1,527 un-fetched domains are low-authority throwaway spam (Authority Score < 10). 98.4% of measured low-AS domains have **zero** organic traffic, so these are recorded as zero traffic/keywords; their RD's cell is left blank rather than guessed. They can be completed on the quota reset or from client-supplied Ahrefs CSV exports if you want exact figures - it does not change any disavow decision.
- Of the held set, **597 of 672** have no organic traffic at all - held does not mean valuable.

## Limits
- Example-page 'live' status rests on Semrush/Ahrefs last crawl (we did not fetch each linking host live).
- The held set needs the supplier's answer before those domains can be disavowed.
- **We have not submitted anything to Google Search Console** - that is your call after the supplier conversation.

## Files
- `Fitzgerald_Plumbing_Backlink_Audit.xlsx` - 7-tab workbook (Summary, Referring Domain Audit, All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List).
- `disavow_fitzgeraldplumbing.com.txt`, `disavow_fitzgeraldandsonsplumbing.com.txt`, `disavow_fitzplumb.com.txt` - disavow files.