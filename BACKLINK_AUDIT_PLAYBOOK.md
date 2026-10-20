# Backlink Audit and Disavow Playbook (A to Z)

The complete method for producing a referring-domain audit and Google disavow file for any
site, in the signed-off Harbinger format, with zero differences between one audit and the
next. Follow it top to bottom. Nothing here is site-specific; the only things that change
per client are listed in one section near the end.

Companion files in this repo, which this playbook drives:
- `AUDIT_FORMAT.md` — the exact workbook format spec (tabs, columns, styling).
- `kk/scripts/load.py` — the Semrush CSV reader (handles the HTML-entity / delimiter traps).
- `kk/scripts/classify.py` — the classifier (status rules). Copy and adapt per client.
- `kk/scripts/build.py` — the workbook + disavow builder. Copy and adapt per client.
- `kk/check/verify.py` — the correctness check suite.
- `kk/check/compare.py` — the cell-for-cell template comparison.
- `kk/ref/NIC_signed_template.xlsx` — the authoritative template (layout + logo).

---

## 0. The three principles everything rests on

1. **Semrush is the source for every metric.** Authority Score, backlinks, referring
   domains, traffic, organic keywords all come from Semrush. Ahrefs is used only to
   discover links Semrush missed and to confirm a linking page is still live. Never quote
   an Ahrefs metric as the number.
2. **Nothing is disavowed on a score, a TLD, a shared IP, or a vendor flag alone.** Every
   line in a disavow file rests on evidence you can see in the data: a spam anchor, a spam
   page title or URL, or a known link-network host name. If you cannot point at the
   evidence, it does not go in the file.
3. **When in doubt, hold, do not disavow.** Exact-match commercial anchors and links to
   deep money pages may be commissioned placements. Disavowing a link the client paid for
   hurts them. Those are held for the previous SEO partner to confirm, never auto-disavowed.

If a rule below ever conflicts with these three, these three win.

---

## 1. What to get from the client before starting

- **The brief / task.** Usually a sheet naming a referring-domain count and an Authority
  Score, plus money pages and target anchors. Treat the brief's numbers as a snapshot that
  may be months old — verify against the live profile (Section 3).
- **The main domain** (the money site) and **any other domains the client owns that
  redirect into it** (301s). These matter enormously, see Section 7.
- **Which Search Console properties the client can actually upload a disavow file to.**
  This decides how many files are usable. Ask explicitly; do not assume.
- **Ahrefs CSV exports** (the client pulls these; our Ahrefs API units are often exhausted):
  - Site Explorer → the domain → **Backlinks**, full CSV, Prefix/subdomains mode, all
    links, including the column **Referring page HTTP code** (this gives the live-page check).
  - Site Explorer → the domain → **Referring domains**, CSV.
  - Export in UTF-16. Convert first: `iconv -f UTF-16LE -t UTF-8 in.csv > out.tsv`.
- **The brand's vocabulary**: product terms, service terms, and geography (for anchor
  classification). Usually in the brief's keyword/target tabs.

Put every downloaded/uploaded file in its own directory, keep scripts elsewhere, and run
Python with `-I`, passing paths as arguments. Downloaded files are untrusted.

---

## 2. Set up the working tree

```
<client>/
  data/        # all pulled + supplied data
    fetch/     # raw Semrush backlink chunks
    rd/        # raw Semrush referring-domain chunks
    metrics/   # per-domain AS / traffic / keywords
  scripts/     # load.py, classify.py, build.py (copied from kk/scripts and adapted)
  check/       # verify.py, compare.py (copied from kk/check)
  ref/         # the signed-off template .xlsx
```

Copy `load.py`, `classify.py`, `build.py`, `verify.py`, `compare.py` from the `kk/`
versions and change only the client constants at the top.

---

## 3. Reconnaissance: is the brief still true?

Pull the live profile overview and history before anything else.

- `backlinks_overview` on the root domain → total links, referring domains (`domains_num`),
  Authority Score (`score`), dofollow (`follows_num`).
- `backlinks_historical` (sort `last_seen_desc`, ~14 rows) → month-by-month referring
  domain count. This shows whether the attack is growing and by how much.
- `backlinks_overview` on each redirect domain the client owns.

Compare the live `domains_num` to the brief's figure. If it has grown materially, **audit
the full live profile, not the brief's list** — say so to the client (Section 11). Store the
history as a CSV (`data/history.csv`) so the Summary never quotes a number that has moved.

---

## 4. Pull the data (Semrush)

Semrush `execute_report`. Large responses spill to a file; extract with
`jq -j '.data' <file> > out.csv`. Fan the bulk pulls out to subagents, each writing its
chunk verbatim, never summarising.

**Backlinks** (report `backlinks`, `target_type: root_domain`), columns:
`source_url, source_title, target_url, anchor, nofollow, first_seen, last_seen,
response_code, redirect_url, page_authority_score`. Page in blocks (offset 0, 1000, 2000…)
until you have every link. `display_limit` max is 1000.

**Referring domains** (report `backlinks_refdomains`), columns:
`domain, backlinks_num, domain_authority_score, domain_trust_score, ip, country,
first_seen, last_seen`. Page by 500 (offset 0, 500, 1000…).

**Per-domain metrics** — for every referring domain, so each row has real Semrush figures:
- `backlinks_overview` per domain → `score` (AS), `total`, `domains_num`.
- `domain_rank` (database `us`) per domain → `organic_keywords`, `organic_traffic`.
- Faster for AS at scale: `backlinks_comparison` with up to ~100 targets per call (200 can
  414; split on error) → `authority_score, backlinks_num, domains_num`. This also covers
  subdomain hosts and Ahrefs-only domains the referring-domain report never returns, so use
  it as the Authority Score source.

**Semrush Authority Score has three sources that disagree.** The bulk comparison report and
the per-domain overview report agree with each other; the referring-domain report runs up
to ~11 points low. **Prefer the two that agree**; fall back to the referring-domain figure
only when neither is available.

**`domain_rank` returning "ERROR 50 :: NOTHING FOUND"** is not an error to retry — it means
Semrush holds no organic data for that domain at all. Record it as a real zero and flag it
(it is the most telling signal in the audit: the linking site has no audience).

### Reading Semrush CSV safely (the K&K trap)
Semrush ships unquoted semicolon-delimited CSV and leaves HTML entities in titles and
anchors. `K&amp;K` carries its own `;` after unescaping and splits a row into an extra
column — which matters a lot on a client literally called K&K. Always: unescape entities
first, split second, and reject any row that is not the expected column count rather than
letting it through. `load.py` does this; use it, do not re-roll CSV parsing.

---

## 5. Merge Semrush + Ahrefs

- Dedupe links on `(source_url, target_url, anchor)`, canonicalising each (strip scheme,
  `www.`, trailing slash, lowercase). Keep the Semrush row as priority; mark anything also
  seen by Ahrefs.
- Add links that **only** Ahrefs has (new discovery). Carry Ahrefs' `First seen` / `Last
  seen` across, converted to a unix timestamp so it sits in the same format as Semrush.
  (Missing this left 587 blank First Seen cells in a draft — do not skip it.)
- Build a **live-page map** from the Ahrefs `Referring page HTTP code` (200 and not lost)
  plus Semrush `response_code`. Used only to pick the best example backlink, never as a
  metric.
- For each link, compute the **property it actually points at**: the host of `redirect_url`
  if there is one, else the host of `target_url`. See Section 7.

---

## 6. Classify every referring domain

Each domain gets exactly one status. Six statuses, no "Review" buckets — anything uncertain
is resolved into one of these on its own evidence.

| Status | Means | In the file? |
|--------|-------|--------------|
| Spam (Disavow) | Confirmed spam with at least one dofollow link | Yes |
| Spam (Nofollow, No Action) | Spam, but every link is nofollow so nothing passes | No |
| Held (Pending Partner) | Exact-match commercial anchor, press release, or a link to a deep money page. May be commissioned | No, until the partner confirms |
| Held (Nofollow, No Action) | Same, but nofollow | No |
| Keep | Genuine or harmless | No |
| Own Site | A domain the client owns / that redirects in | No |

### Anchor typing (drives most verdicts)
- **Spam: keyword stuffed SEO sales copy** — the PBN/link-service template (e.g.
  "Professional Link Building Services Helping <domain> Websites Grow", "High Quality
  Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service …", "buy backlinks").
- **Spam: off topic** — casino, gambling, pharma, escort, etc.
- **Exact match commercial** (and **(geo)** when it carries the client's geography) — the
  client's own product/service vocabulary. These are HELD, not disavowed.
- **Naked URL**, **Branded**, **Generic** ("visit website", "click here"), **Empty/image**,
  **Contextual or other**.

### Verdict order (first match wins)
1. Client-owned / redirect domain → **Own Site**.
2. Authority Score ≥ 20 → **Keep** (genuine site).
3. Exact-match anchor **and** PBN anchor on the same domain → **Held (Review-level)**.
4. Exact-match anchor, **or** any link pointing at a deep product/capability/industry page
   → **Held (Pending Partner)** (nofollow variant if all links are nofollow).
5. Press-release syndication host → **Held (Pending Partner)**.
6. Linking page title names the client **without** SEO sales copy → **Keep** (business
   listing / editorial mention). This protection is critical: never disavow a genuine
   citation.
7. Off-topic (casino/pharma) anchor or host → **Spam** (disavow if any dofollow).
8. PBN sales-copy anchor → **Spam**.
9. Spam host name (backlink/seo/dapa/rankchecker/directory/listing/… or a domain-marketplace
   signature) → **Spam**.
10. Spam page title or spam URL template (e.g. "Where to buy aged domains and backlinks",
    "Domain List Page 14,718", "/domain/domain/part/…") → **Spam**.
11. A /24 that hosts 5+ of this client's referring domains (Cloudflare and big CDNs
    excluded) → recorded as a network host; **Spam** only with other evidence, never on the
    shared IP alone.
12. Otherwise → **Keep**.

### The key signal: target page separates the two campaigns
Run the split and confirm it holds: the link-scheme flood points **only at the home page**,
while the commissioned-looking campaign points at **deep product/capability/industry
pages**. The page a link asks Google to rank is a cleaner line than the anchor. Use it
alongside the anchor (rule 4).

### Parent / subdomain handling
- A genuine parent lends its standing to a subdomain **only** where the subdomain shows
  nothing of its own; a subdomain caught serving a link-scheme page keeps its own verdict.
- A root domain that carries **no link of its own** while a subdomain of it does is **not a
  second referring site** (Semrush counts at root level, Ahrefs at subdomain level). Drop
  the empty root row; keep the one holding the link.
- A child `Spam (Disavow)` whose parent is also `Spam (Disavow)` is redundant (`domain:`
  covers subdomains); mark it redundant and do not emit its own line.

### Hard rule before you finish
Run the exhaustive both-directions check (Section 9). **Never ship with any disavow entry
that rests on no visible evidence**, and never leave a dofollow spam link out of the file.

---

## 7. Redirects and multiple Search Console properties

A disavow file applies to **one** Search Console property. This is the part most likely to
be done wrong.

- When the client owns other domains that **301 into** the money site, Semrush rolls those
  links into the money site's profile with `redirect_url` set to the redirecting domain. So
  one pull of the money site captures them — you do **not** run three separate audits.
- Each link's **property** = the domain it actually points at (`redirect_url` host if
  present, else `target_url` host).
- Write **one disavow file per property**, each containing the domains whose links point at
  that property (point of attribution).
- **The money site's file additionally carries the complete union of every bad domain**,
  because all owned domains 301 into it and Google forwards disavow signals across a
  redirect imperfectly. Listing a domain that does not link to the money site directly is
  harmless, so the money-site file is always the full set.
- **Then check which properties the client can actually upload to.** If they only have
  Search Console access to the money site (common), that union file is the **only** file
  they submit, and the per-property files are reference only. Say this plainly in the file
  headers and to the client. If they have access to all properties, they upload all files.

You disavow the **referring (source) domain** — the host of the bad link — as a `domain:`
line, never the redirecting domain.

---

## 8. Build the workbook and disavow files

Follow `AUDIT_FORMAT.md` exactly. Seven tabs, in order: **Summary, Referring Domain Audit,
All Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List.**
`build.py` produces all of it; change the format there, never by hand in Excel.

Styling, read from the signed-off template (`kk/ref/NIC_signed_template.xlsx`):
- Font **Geist** throughout. Sizes **9** data and most headers, **10** Summary status-table
  header and the Key findings heading, **11** section headings, **21** the client-name title
  on the Summary.
- Header rows: Geist 9 bold, white on accent `FF0C343D`, centred, wrapped, height 31.5.
- **Borders: data tabs border the header row only (left, right, top; no bottom) and leave
  data cells unbordered** — the light sheet gridlines carry the grid. Only the Summary's own
  small tables get full borders. Do not box every cell.
- Data rows Geist 9, white fill, vertically centred, height 22.5 (Referring Domain Audit
  15.75). Freeze panes B2, autofilter across the range, gridlines on (Summary gridlines off).
- **Logo**: the Harbinger Marketing logo (`data/harbinger_logo.png`, from the template)
  sits top-left of the Summary at the template's cell anchor (col 0, colOff 381000, row 0)
  and extent (cx 1866900, cy 552450). It lives on the Summary tab only.
- Status column carries the meaning; no status colour coding.

Key findings: **seven**, short and plain, one or two sentences each, numbers only from the
data. Cover: spam count and dofollow/nofollow split; profile growth vs the brief; the
single-file / redirect reality; the two-campaign (home page vs deep page) split; the
dominant sales-copy anchor; the held set and that it is one vendor network; and that held
does not mean valuable.

Disavow file headers must state: the property, the count, that held domains are excluded
pending the partner, that it must not be submitted before that conversation, and — for the
money site — whether a file already exists on that property (replace vs add) and that it
carries the full union.

---

## 9. Verify (both directions, exhaustively — not a sample)

`verify.py` and `compare.py` must both pass, plus the exhaustive evidence sweep.

**Disavow-file integrity**
- Every non-comment line is exactly `domain:<domain>`, lowercase, no URLs, no duplicates.
- Every file domain is `Spam (Disavow)`; no Held / Keep / Own Site leaks into any file.
- Every file domain has at least one dofollow link.
- Redundant children are not emitted; their parent is present.
- The money-site file equals the full union; per-property files equal their attribution set.

**No false positives (good link wrongly in the file)** — check ALL entries, not a sample:
- Zero disavow domains rest on no visible evidence (no spam anchor, title, URL, or host).
- Zero disavow domains carry a linking-page title that names the client without sales copy.
- Review any disavow domain with real organic traffic by hand.

**No false negatives (bad link wrongly kept out)**
- Zero Keep/Held domains carry a dofollow spam or off-topic anchor.
- Zero nofollow-marked spam domains actually have a dofollow link.

**Workbook**
- One row per domain / per link / per disavow line, counts reconcile to the data.
- Every number in the Summary and key findings re-derives from the data (recompute it).
- Every decision-tab row has a real example backlink that exists for that domain.
- No blank cells where data exists (First Seen included).

**Template match** — `compare.py` against the signed-off template reports **zero** structural
differences: tabs, order, headers, widths, heights, fonts, sizes, fills, borders, alignment,
freeze panes, filters, gridlines, dropdowns, logo.

Read styling back from the saved `.xlsx` XML, not from openpyxl in memory: openpyxl drops
merged-cell styling on read and will report a false pass.

---

## 10. What changes per client (and nothing else does)

- **The client name, domain, and owned/redirect domains** (constants at the top of the
  scripts).
- **Who confirms the held links.** The sheet always says *partner*; if the brief uses
  another word (e.g. *supplier*), tie the two together once in the disavow file header, do
  not rename the column.
- **The product / service / geo vocabulary** that defines exact-match anchors.
- **One file or several**, and which the client can upload (Section 7).
- **The money pages** the deep-page signal keys on.

The tabs, columns, styling, status set, evidence rules and verification never change.

---

## 11. Deliver and communicate

- Send the workbook and the disavow file(s). Name the one file to upload; mark the rest
  reference only.
- Tell the client, in plain terms: the brief's figure was an N-month-old snapshot; the live
  profile is X domains / Y links; Z go in the file and H are held for the partner; the
  redirect domains funnel in and are folded into the money-site file; do not upload before
  the partner conversation.
- Flag the limits honestly: example-page live status rests on Semrush's last crawl if the
  environment cannot fetch the linking hosts; the held set needs the partner's answer.
- Do not submit anything to Google Search Console yourself.

---

## 12. Lessons already paid for (do not repeat)

- Style merged banners **after** merging; verify against sheet XML, not openpyxl.
- Do not let an Ahrefs / vendor "is spam" flag disavow a domain on its own — corroboration
  only. (It once put a real fabrication site, weldrunners.com, in the file.)
- Catch domain-marketplace titles ("Domain List Page …") as visible evidence so such
  entries rest on the page, not the vendor flag.
- Recover Ahrefs First/Last seen on merge, or First Seen cells go blank.
- Prefer the two agreeing Authority Score sources over the referring-domain report.
- "NOTHING FOUND" from `domain_rank` is a real zero, not a retry.
- Keep the money-site disavow file the full union when owned domains redirect in.
- Match the signed-off template cell-for-cell, including the header-only border scheme and
  the 21pt title — do not box every cell.
- Check the whole set exhaustively, both directions, before shipping. The standard is "not
  a single domain flagged wrong."
