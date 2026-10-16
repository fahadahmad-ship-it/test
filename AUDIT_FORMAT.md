# Backlink audit format

The signed off format for New Image Canopy. Every later audit of this kind follows it,
whatever the client. `audit/scripts/build.py` produces it; change the format there, not by
hand in Excel, so the next audit starts from the same place.

## Tabs, in this order

| # | Tab | One row per | Columns |
|---|-----|-------------|---------|
| 1 | Summary | n/a | 5 |
| 2 | Referring Domain Audit | referring domain | 17 |
| 3 | All Backlinks | link | 9 |
| 4 | Anchor Analysis | distinct anchor | 6 |
| 5 | Exact Match Anchors | domain and anchor | 7 |
| 6 | Pending Disavow Lines | domain awaiting a decision | 3 |
| 7 | Disavow List | line in disavow.txt | 7 |

## Columns

**Referring Domain Audit** Domain, Status, AS, Backlinks, RD's, Traffic, In Disavow,
Links Point To, Dofollow Links, Nofollow Links, First Seen, Top Anchor Text,
Example Linking Page, Linking Page Title, Source, IP, Disavow Line

**All Backlinks** Referring Domain, Status, Tool, Anchor Text, Anchor Type, Link Type,
Linking Page URL, Linking Page Title, Target URL

**Anchor Analysis** Anchor Text, Anchor Type, Backlinks, Share of Backlinks,
Referring Domains, Spam Domains Using It

**Exact Match Anchors** Referring domain, Example backlink (linking page),
Exact-match commercial anchor, Market, Site type (indicative),
Partner confirmed? (Y/N), Final decision

**Pending Disavow Lines** Referring domain, Disavow line (append to disavow.txt once
confirmed), Recommendation

**Disavow List** Disavow Line, AS, Backlinks, RD's, Traffic, Organic Keywords,
Top Anchor Text

## Styling

One accent colour, `FF0C343D`, for header rows and for the cells the partner fills in.
Everything else white. No status colour coding: the Status column carries the meaning, so
the sheet prints legibly and nobody has to learn a key.

- Font Geist throughout. Sizes 9 for data and most headers, 10 for the Summary status
  table header and the Key findings heading, 11 for section headings, 21 for the title.
- Header row: Geist 9 bold, white on `FF0C343D`, centred, wrapped, height 31.5.
- Data rows: Geist 9, white fill, vertically centred, thin border all round.
  Height 22.5, except Referring Domain Audit at 15.75.
- Input cells the partner fills in: `FF0C343D` fill, white font.
- Every data tab: freeze panes at B2, autofilter across the full range, gridlines on.
- Summary: gridlines off, all rows 22.5, title merged across B1:E2.

## Statuses

Six, and no others. Review buckets are not used: anything that cannot be decided is
resolved into one of these on its own evidence.

| Status | Means |
|--------|-------|
| Spam (Disavow) | Confirmed spam with at least one dofollow link. In the file. |
| Spam (Nofollow, No Action) | Spam, but every link is nofollow, so nothing passes. |
| Held (Pending Partner) | Exact match commercial or press release anchor. Out of the file until the previous SEO partner confirms. |
| Held (Nofollow, No Action) | Same, but nofollow, so no decision is needed. |
| Keep | Genuine or harmless. |
| Own Site | Client owned property or redirect. |

## Rules the audit holds to

- Semrush is the source for every metric: Authority Score, Backlinks, RD's, Traffic,
  Organic Keywords. Ahrefs contributes additional referring domains, link detail, and the
  HTTP status of linking pages, never a metric.
- Nothing is disavowed on Authority Score or TLD alone. Every line in the file rests on
  link evidence: the anchor, the linking page title, or a known link network host.
- Held domains never reach disavow.txt. The partner decides first.
- A root domain that carries no link of its own, while a subdomain of it does, is not a
  second referring site. Keep the row that holds the link.
- Every row on the decision tab carries a real, checkable example backlink.
- disavow.txt uses `domain:` lines, grouped by reason, with a header stating the count and
  the warning not to upload before the partner has confirmed.

## Before sending

`build.py` prints the counts. Check them against the Summary, and check that no Held,
Keep or Own Site domain appears in disavow.txt. The scripts in this repo do both.
