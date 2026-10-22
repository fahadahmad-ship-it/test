# Aaron's Home Tech — Backlink Audit & Disavow Review

**Money site:** aaronshometech.com
**Prepared by:** Harbinger Marketing
**Data source:** Semrush (backlinks, referring domains, anchors, authority & organic metrics)
**Date:** 2026-10-22

---

## Headline

aaronshometech.com is under an **active, accelerating negative-SEO / link-seller
flood.** Semrush shows the referring-domain count climbing from roughly **900 a
year ago → 1,699 last month → 5,399 now**, while Authority Score has fallen from
**28 (2022) to 10**. The new links are overwhelmingly a single link-vendor's PBN
("buy backlinks", "premium PBN", "niche edit", "DA 50 PA 40" sales-copy anchors),
and the same network is selling links to a cluster of unrelated businesses at the
same time — the tell-tale footprint of one paid link operation.

No client brief figure was supplied for the referring-domain count, so **the full
live profile (5,392 referring domains) was audited**, not a sample.

## What we found (every referring domain classified on its own evidence)

| Status | Domains | In disavow file? |
|---|---|---|
| **Spam (Disavow)** — confirmed spam, ≥1 dofollow link | **4,123** | Yes |
| **Spam (Nofollow, No Action)** — spam but all links nofollow | 208 | No (passes nothing) |
| **Held (Pending Partner/supplier)** — commercial/commissioned-looking, confirm first | 961 | No (held) |
| **Held (Nofollow, No Action)** | 52 | No |
| **Keep** — genuine / editorial / authoritative | 46 | No |
| **Own Site** — client-owned (aaronssystems.com, aaronssecurity.com) | 2 | No |
| **Total** | **5,392** | **4,123 in file** |

Nothing was disavowed on an Authority Score, a TLD, or a shared IP alone — every
one of the 4,123 file domains rests on visible evidence (a spam anchor, a spam
page title, a known link-farm host, or a same-network member domain) **and** has
at least one dofollow link to the site. The check was run exhaustively in both
directions over all 5,392 domains: **zero** high-authority or trafficked sites are
in the file (every domain with ≥100 monthly organic visits — indeed.com, birdeye.com,
growjo.com, wiza.co, etc. — is Kept), and **zero** dofollow PBN/off-topic spam links
are left out. Every domain classified "Nofollow, No Action" was re-checked against
its **full** link set (not a sample) to confirm none hides a dofollow link — none did.

Note on the 961 Held set: it is larger than a first pass suggested because the
previous supplier's directory campaign (business-directory pages carrying exact-match
commercial geo anchors to deep `/services/` and `/location/` pages) is held for
confirmation rather than kept or disavowed. Many are low-authority; some may still be
disavowed once the supplier rules out a commission.

## The two campaigns (this is the important distinction for you)

The target page separates two different things:

1. **The home-page flood (disavow).** ~10,500 of the analyzed links point at the
   home page with PBN sales-copy anchors. This is the negative-SEO / link-spam
   attack. These are the 4,123 **Spam (Disavow)** domains.
2. **The deep-page, commercial-anchor campaign (HELD).** ~1,500 links point at deep
   `/services/…-ga/` and `/location/…-ga/` money pages using **exact-match
   commercial geo anchors** (e.g. "home theater installation atlanta ga"). These are
   older and look **commissioned** — most likely the previous SEO supplier's
   directory/placement work. Per your brief these are **Held**, not disavowed, until
   the previous supplier confirms whether they were commissioned.

## What to do with the files

- **`disavow_aaronshometech.com.txt`** — the disavow file for the aaronshometech.com
  Search Console property. 4,123 `domain:` lines, grouped by reason. It is the full
  **union** of bad domains for the money site.
- **Do NOT upload it yet.** First have the previous-supplier conversation about the
  **961 Held (Pending Partner) domains** (the "Pending Disavow Lines" tab lists these —
  the dofollow held links that could be disavowed; a further 52 held links are nofollow
  and need no action). Any the supplier confirms were **not** commissioned can then be
  appended to the file; any that were commissioned stay out.
- Uploading a disavow file **replaces** any file already on the property. We did not
  receive an existing file — please confirm whether one exists before uploading
  (if so, we merge rather than replace).

## Open items we need from you

1. **Owned domains:** `aaronssystems.com` (Aaron's Systems Integrators, Inc.) and
   `aaronssecurity.com` are treated as **Own Site**. Please confirm you own them and
   whether they **301-redirect into aaronshometech.com**. Their bad links are already
   folded into the money-site file; if you have separate Search Console access to
   them, we can also produce per-property files.
2. **Previous supplier:** any name or list of domains/placements lets us confirm the
   Held set faster (the sheet always says "partner"; your brief calls this role the
   "supplier" — same thing).
3. **Search Console access:** which properties can you actually upload a disavow file
   to?

## Honest limits on this audit

- **Ahrefs API units were exhausted** on this workspace this cycle, so link discovery
  and live-page confirmation rely on Semrush's last crawl (the `response_code` column)
  rather than a fresh Ahrefs fetch. If you can export the Ahrefs **Backlinks CSV
  (with the "Referring page HTTP code" column)** and **Referring domains CSV**, we'll
  fold them in for live-page checks and any extra link discovery.
- **Authority Score** uses Semrush's bulk comparison report (which agrees with the
  domain overview); it was pulled for all 5,392 domains.
- **Organic traffic / keywords** were pulled for every retained, held, and
  higher-authority domain plus every disavow candidate with any authority, to make
  sure no trafficked/genuine site is wrongly disavowed. The remaining no-authority
  spam domains (freshly-registered PBN hosts) are recorded as zero, consistent with
  Semrush returning no organic data for them (validated: 0 of a 60-domain sample of
  AS<3 spam had any organic traffic).
- **All Backlinks tab** lists the analyzed link set — ~19,560 of the ~40,274 links in
  the profile — with **every one of the 5,392 referring domains represented** by at
  least one example link. The disavow decision is made per referring domain, so this
  is complete for decision purposes; the Summary's backlink totals use the *full*
  per-domain counts (the Total reads 40,277), so they reflect the whole profile. The
  full link-by-link dump can be pulled on request. The per-domain "Dofollow / Nofollow
  Links" counts reflect the analyzed links (a floor for a few very high-volume
  domains); the follow/nofollow *verdict* was confirmed against each domain's full
  link set where it mattered.

## Format

The workbook matches the signed **K&K Manufacturing** template **cell-for-cell** —
verified by `check/compare.py` with **zero structural differences** (tabs, column
headers, widths, row heights, fonts/sizes, fills, header-only borders, alignment,
freeze panes, autofilters, gridlines, number formats, input cells, and the Harbinger
logo on the Summary). The Summary carries the status table, the anchor-type profile
table, and seven key findings, exactly as in the template.

## The workbook

`Aarons_Home_Tech_Backlink_Audit.xlsx` — seven tabs in the signed-off Harbinger
format: **Summary, Referring Domain Audit, All Backlinks, Anchor Analysis,
Exact Match Anchors, Pending Disavow Lines, Disavow List.** The Exact Match Anchors
tab has two input columns for the supplier review ("Partner confirmed? (Y/N)" and
"Final decision").

We do not submit anything to Google Search Console on your behalf.
