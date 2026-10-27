# Premier Blinds & Designs — Backlink Audit & Disavow

Prepared by Harbinger Marketing · 2026-10-27 · format = the signed-off Harbinger
audit (New Image Canopy / K&K template). All metrics are Semrush.

## In plain terms

Premier Blinds & Designs is under a **negative-SEO / PBN link attack**. The live
Semrush profile is **4,493 backlinks from 3,159 referring domains** at Authority
Score 14. The attack **exploded in the last month**: 782 referring domains in
September 2026, ~3,159 now — a ~4× jump. We audited the **full live profile**, not
an older snapshot.

| Status | Domains | In the disavow file? |
|---|---|---|
| Spam (Disavow) | 2,603 | **Yes** |
| Spam (Nofollow, No Action) | 82 | No — nofollow, passes nothing |
| Held (Pending Partner) | 439 | **No — awaiting confirmation** |
| Held (Nofollow, No Action) | 1 | No |
| Keep | 33 | No — genuine citations |
| Own Site | 1 | No — `thepremierdesigns.com` (redirects in) |
| **Total** | **3,159** | |

**Two campaigns, easy to tell apart.** 3,756 links hit the **home page** with
backlink sales-copy anchors (e.g. *"Build Strong SEO Authority with High Quality
Links from premierblindsanddesigns.com"*, *"DA 50 PA 40 Premium PBN Network
Service"*). The exact-match **geo** anchors (*"Custom Window Treatments Peachtree
City GA"*, *"Motorized Window Shades Atlanta GA"*) hit **deep /product/ pages**.
The home-page flood is the attack; the deep-page set is what *might* have been
commissioned.

## The files, and which to upload where

You confirmed Premier can upload to **both** owned Search Console properties, so
there are two disavow files:

1. **`disavow_premierblindsanddesigns.com.txt`** — the money site. **2,603 domains.**
   This is the **full union** of every bad domain, including those that reach the
   site through the `thepremierdesigns.com` 301 redirect (Google forwards disavow
   signals across redirects imperfectly, so the money-site file carries everything).
   **Upload this to the premierblindsanddesigns.com property.**
2. **`disavow_thepremierdesigns.com.txt`** — the redirect property. **1,559 domains**
   (those whose links are attributed to `thepremierdesigns.com`). **Upload this to
   the thepremierdesigns.com property.**

Both files group domains by the reason they are listed, and every line is a
`domain:` line resting on **visible evidence** — a spam anchor, a spam page
title/URL, or a known link-network host — never on Authority Score, TLD or IP alone.

**Do not upload either file yet** — first resolve the held-link question below.
We have **not** submitted anything to Google Search Console; Premier uploads these.
We have **not** confirmed whether a disavow file already exists on either property —
if one does, uploading **replaces** it, so merge first.

## The "commissioned link" question — your first task

The 439 **Held (Pending Partner)** domains are the links that *may have been
commissioned*. They carry exact-match commercial/geo anchors pointing at deep
product and service pages — the signature of paid or semi-automated placements,
not the random home-page spam flood. They are **excluded from the disavow files
until someone confirms** whether Premier (or its previous SEO provider) paid for
any of them. Disavowing a link the client paid for would throw away a real asset.

**What to do:** open the **"Exact Match Anchors"** tab (Tab 5, 518 rows). It lists
each held domain, a real example linking page, the exact-match anchor, the market
(Peachtree City / Atlanta / Georgia / Non-geo), and an indicative site type. The
last two columns — **"Partner confirmed? (Y/N)"** and **"Final decision"** (the
teal input cells) — are for whoever ran Premier's prior link building to fill in:

- Mark **Y** for any link they recognise as a commissioned placement → it stays
  **out** of the disavow file (keep it).
- Mark **N** for anything they did not commission → append its line (from the
  **"Pending Disavow Lines"** tab, Tab 6) to the disavow file and re-upload.

Note on wording: the task framed this as "confirm with the client." In this format
the confirming party is whoever ran the **prior link-building** (the "partner" /
previous SEO provider). The client should identify that party; the held set is
their call, not something to auto-disavow.

Unlike some campaigns, this held set is **not one IP network** — it scatters across
many hosts and /24 ranges, 378 of 440 held domains have **zero organic traffic**, and
388 sit at Authority Score ≤ 2. Held does **not** mean valuable.

## Data completeness

Every referring domain carries **real Semrush metrics**, pulled per-domain:
- **Authority Score** and **RD's** (the referring domain's own referring-domain count)
  from `backlinks_overview` — the per-domain source.
- **Organic Traffic** and **Organic Keywords** from `domain_rank` (US database). A
  `NOTHING FOUND` response is recorded as a true **0** (per the playbook) — and the
  overwhelming majority of these PBN/junk domains genuinely have no organic audience.
  98 of 3,159 domains show any organic traffic; the real publishers (yahoo,
  yellowpages, superpages, hunterdouglas, bing, citylifestyle, sitelike) all land in
  **Keep**, never in a disavow file — confirmed by the hand-review check.

One input note (not a gap in the workbook): the source is **Semrush**. The
environment's network policy blocked fetching the client site and linking hosts, and
no Ahrefs CSV export was supplied by the client, so live-page HTTP status rests on
Semrush's last-crawl `response_code` rather than an Ahrefs cross-check. Supply the
Ahrefs backlink + referring-domain CSV exports and we'll fold in any links Semrush
missed and add the Ahrefs live-page verification.

## Verification (both directions, exhaustive — not a sample)

`verify.py` and `compare.py` both pass:
- Every disavow line is `domain:<host>`, lowercase, no duplicates, no URLs.
- 0 non-Spam(Disavow) domains leak into either file; every listed domain has ≥1
  dofollow link; no redundant subdomain children.
- Money-site file = full union; redirect file = its attribution subset.
- 0 disavow domains rest on no visible evidence; 0 are genuine citations naming the
  client without sales copy.
- 0 Keep/Held domains carry a dofollow spam/off-topic anchor; 0 nofollow-spam
  domains actually have a dofollow link.
- Workbook row counts reconcile to the data; **zero** structural differences vs the
  signed template (tabs, order, headers, widths, heights, fonts, fills, borders,
  freeze panes, filters, gridlines, logo).
