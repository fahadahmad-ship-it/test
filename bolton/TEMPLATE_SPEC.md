# Bolton Service WNC — workbook spec (reverse-engineered from KandK_Manufacturing_Backlinks_Audit.xlsx)

Authoritative template = the uploaded K&K workbook. Where it differs from AUDIT_FORMAT.md,
**the template wins** (noted inline). Client = Bolton Service WNC, money site = boltonservicewnc.com.

## Global styling
- Font **Geist** everywhere. Data cells: size 9, regular, color `FF000000`, fill white `FFFFFFFF`.
- Accent color `FF0C343D`.
- Header cells (all data tabs + Summary tables): Geist 9 **bold**, font `FFFFFFFF`, fill `FF0C343D`,
  align center/center, wrap=True, border = **L/R/T thin, NO bottom** (`thin` sides left+right+top only).
  Exception: Anchor Analysis A1 wrap=False; All Backlinks C1 ("Tool") align=left.
- **Data cells: NO borders at all.** Gridlines carry the grid. (Template beats AUDIT_FORMAT's "border all round".)
- Header row height **31.5**. Data row height **22.5**, EXCEPT Referring Domain Audit data rows **15.75**.
- Alignment in data rows: text cols (domain, status, anchor text, URLs, titles, disavow line, recommendation)
  = left (h=None/left); numeric & short-code cols (AS, Backlinks, RD's, Traffic, counts, In Disavow, Source, IP,
  Market, Tool) = center; all vertical=center.
- Partner **input cells** (Exact Match Anchors cols F & G): fill `FF0C343D`, font white `FFFFFFFF`, left, empty.
- Every data tab: freeze_panes **B2**, autofilter across full range `A1:<lastcol><lastrow>`, gridlines ON.
- Summary: gridlines OFF, no freeze, no autofilter.

## Number formats
- Integers (Backlinks, RD's, Traffic, Organic Keywords, Share counts): `#,##0`
- AS, Dofollow Links, Nofollow Links, Referring Domains(count on Anchor/Summary): `General`
- First Seen: `d mmm yyyy`
- Summary status table Share of Domains (D): `0.0%`
- Summary anchor table Share of Backlinks (C): `0.0%`
- Anchor Analysis Share of Backlinks (D): `0.00%` (two decimals here)

## Tab 1 — Summary  (A1:E28, gridlines off)
- Logo PNG top-left: OneCellAnchor from col0 colOff **381000** row0 rowOff0, ext cx **1866900** cy **552450**.
  File: bolton/data/harbinger_logo.png (170x50). Summary only.
- B1:E2 merged = client name "Bolton Service WNC", Geist **21** bold `FF0C343D`, center/center.
- Col widths: A 38.86, B 16.29, C 17.57, D 18.71, E 120. All rows height 22.5.
- Row 3 header (A3:E3): Status | Domains | Backlinks | Share of Domains | What it means. Geist **10** bold white on accent, wrap, full thin borders (this table gets full borders, unlike data tabs).
- Rows 4-9 status rows (order exactly): Spam (Disavow); Held (Pending Partner); Held (Nofollow, No Action);
  Spam (Nofollow, No Action); Keep; Own Site. Geist 9, white fill, **full thin borders**. B/C/D center, E wrap-left, A left.
  E column standard text:
  - Spam (Disavow): "Confirmed spam with at least one dofollow link. Included in the disavow file."
  - Held (Pending Partner): "Exact match commercial anchor, or a link aimed at a product, capability or industry page. May have been commissioned. Not in the disavow file until the previous partner confirms."
  - Held (Nofollow, No Action): "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way."
  - Spam (Nofollow, No Action): "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed."
  - Keep: "Genuine or harmless link. Keep."
  - Own Site: "Client owned domain that redirects into the site."
- Row 10 Total: A "Total", B=domains total, C=backlinks total, D=1.0 (0.0%→100.0%). Geist 9 **bold**, full borders.
- Row 11 "Key findings": Geist **10** bold, no fill, no border.
- Rows 12-18: seven findings, each merged `A<r>:E<r>`, Geist 9, wrap, no border. (client-specific prose)
- Row 19 "Anchor text profile (all backlinks)": Geist **11** bold `FF0C343D`, no fill/border (section heading).
- Row 20 header (A20:D20): Anchor type | Backlinks | Share of Backlinks | Referring Domains. Geist 9 bold white on accent, full borders.
- Rows 21-28 anchor rows (8 rows in K&K; we list the anchor types we actually have, ordered by Backlinks desc).
  Geist 9 white fill full borders. A left, B/C/D center. A=#,##0? No—A is text(anchor type)=General, B=#,##0, C=0.0%, D=#,##0.
  (Template rows 21-28 number formats: A `#,##0` is spurious on text; use General for the type label.)

## Tab 2 — Referring Domain Audit  (17 cols A-Q)  data row h=15.75
Headers: Domain | Status | AS | Backlinks | RD's | Traffic | In Disavow | Links Point To | Dofollow Links |
Nofollow Links | First Seen | Top Anchor Text | Example Linking Page | Linking Page Title | Source | IP | Disavow Line
Widths: A36 B24.71 C9.57 D13 E9.43 F9.71 G12.43 H21.29 I14 J8.71 K12 L45 M8.71 N40 O14 P15 Q14
numfmt: D,E,F = #,##0 ; K = "d mmm yyyy" ; C,I,J = General
align center: C,D,E,F,G(In Disavow),I,J,O(Source),P(IP). left: A,B,H,L,M,N,Q. K center.
"In Disavow" values: Yes / No / Held. "Links Point To" = property host. "Source" = Semrush / Ahrefs / Both.

## Tab 3 — All Backlinks  (9 cols)  data row h=22.5
Headers: Referring Domain | Status | Tool | Anchor Text | Anchor Type | Link Type | Linking Page URL | Linking Page Title | Target URL
Widths: A25.43 B27.14 C14.71 D55 E32 F10 G55 H53.14 I30.57
C ("Tool") header+data align left. F (Link Type: Dofollow/Nofollow) center. A,B,D,E,G,H,I left.

## Tab 4 — Anchor Analysis  (6 cols)  data row h=22.5
Headers: Anchor Text | Anchor Type | Backlinks | Share of Backlinks | Referring Domains | Spam Domains Using It
Widths: A115.86 B37.71 C14 D8.71 E13 F20.29 ; A1 header wrap=False.
C=#,##0, D=0.00%, E/F General. C,D,E,F center; A,B left. Sorted by Backlinks desc.

## Tab 5 — Exact Match Anchors  (7 cols)  data row h=22.5
Headers: Referring domain | Example backlink (linking page) | Exact-match commercial anchor | Market |
Site type (indicative) | Partner confirmed? (Y/N) | Final decision
Widths: A25.43 B59 C53.14 D16 E24.57 F15.43 G15
F,G = partner INPUT cells (accent fill FF0C343D, white font, empty). C,D center; A,B,E left. One row per domain+anchor (held exact-match commercial).

## Tab 6 — Pending Disavow Lines  (3 cols)  data row h=22.5
Headers: Referring domain | Disavow line (append to disavow.txt once confirmed) | Recommendation
Widths: A32 B44 C48. All left. One row per Held domain awaiting a decision.

## Tab 7 — Disavow List  (7 cols)  data row h=22.5
Headers: Disavow Line | AS | Backlinks | RD's | Traffic | Organic Keywords | Top Anchor Text
Widths: A44 B14 C15.57 D14 E11.14 F14.86 G98.86
C,D,E,F=#,##0; B=General. B,C,D,E,F center; A,G left. One row per emitted disavow line (domain: lines).

## Six statuses only (no Review buckets)
Spam (Disavow) | Spam (Nofollow, No Action) | Held (Pending Partner) | Held (Nofollow, No Action) | Keep | Own Site

## Client specifics for Bolton (to confirm/apply)
- Confirmation role in brief = **supplier** (task says "previous supplier"). Column stays "partner"; tie partner↔supplier once in disavow header.
- Owned/redirect domains + uploadable GSC properties: PENDING user input.
- Vocabulary (exact-match anchors): HVAC/plumbing/electrical service terms + WNC/Western North Carolina geo — to derive from site + Semrush organic keywords.
