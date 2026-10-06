> ## ⚠️ CORRECTION — the "76 missing domains" finding in this document is WRONG
>
> This verification compared the Semrush `148096` cluster against **Section 1 only**, then
> reported the non-matches as absent from the disavow file. They are not. Checked against all
> **460** entries:
>
> - Semrush `148096` cluster (dofollow + word-boundary client anchor): **87 domains**
> - Already in the disavow file: **87**
> - **Genuinely missing: 0**
>
> Every named example — `100ranking.com`, `1seoservices.com`, `7-seo.com`, `backlinksindia.com`,
> `goldbacklinks.com`, `stormbacklink.com`, `seozens.com`, `diversifiedseo.com` — is in
> **Section 6**, which exists precisely to hold Semrush-only domains Ahrefs never crawled.
>
> **No domains need adding on this basis.** The rest of this document's verification work
> (258/258 confirmed, trap checks, false-positive scan, the five overstatement findings) stands
> and was independently checked.

# Adversarial verification — disavow-v2-ahrefs.txt, SECTION 1

Target: `ngwindows.com`. File under review: `/home/user/test/backlink-audit/disavow-v2-ahrefs.txt`
(lines 39–314; 258 `domain:` entries). File was NOT modified.

Evidence used: `data/ahrefs/ahrefs-backlinks.tsv` (2,665 rows), `data/ahrefs/ahrefs-refdomains.tsv`
(1,357 rows), `git show 6f5f407:backlink-audit/work/links_raw.tsv` (Semrush, 3,499 rows),
plus a live `public-domain-rating-free` call on all 258 domains (2026-10-06).

---

## 1. VERDICT

**258 / 258 fully verify. 0 entries to remove.**

Extraction: lines 56–314 yield exactly 258 `domain:` lines, 258 unique — no duplicates inside
Section 1, and **zero overlap** with the other 202 entries in the rest of the file
(460 `domain:` lines total, 460 unique across the whole file).

Every claim in the section header was tested row-by-row against the Ahrefs export:

| Claim in header | Result |
|---|---|
| 258 domains | **258** unique hosts — exact match, set-equal to the export (0 in list but not export; 0 in export but not list) |
| 516 links | **516** rows with path `/dir/quality-authority-backlinks-148096` |
| path byte-identical on all 516 | **516/516.** 1 unique path. Also: 516/516 rows containing `148096` anywhere in the URL resolve to that same path — no variants, no query strings, no subdomains, all `https`, no `www` on the referring side |
| anchor byte-identical | **516/516** `Increase Google Visibility with High Quality Backlinks ngwindows.com`. 1 unique value. Searching the whole 2,665-row export for that exact anchor returns exactly those 516 rows and nothing else; zero near-miss/case/whitespace variants |
| `Nofollow=false` | **516/516.** Also `UGC=false` 516/516, `Sponsored=false` 516/516 — genuinely PageRank-passing |
| `Is spam=true` on 258/258 | **258/258** in refdomains.tsv, and **516/516** at row level in backlinks.tsv |
| 1 unique page title | **516/516** identical: `High Quality SEO Link Building Experts Helping Websites Gain Powerful Backlinks, Improve Search Engine Rankings, and Increase Their Organic Online Presence - Page 148,096` |

Corroborating uniformity not claimed in the header but checked: `Referring page HTTP code` = 200
(516/516), `Type` = text (516/516), `Content` = true (516/516), `Language` = en (516/516),
`Left context` and `Right context` empty (516/516 — raw injected link, no surrounding prose).

Refdomains cross-check: all 258 present, `Links to target` = 2 and `Dofollow links` = 2 on
**258/258**, `Lost` empty on 258/258, `Is spam` = true on 258/258.

### Task 3 — the `performingwindows.com` trap: CLEAR
- Anchor is byte-identical across all 516 and the character before `ngwindows.com` is a space —
  genuine word-boundary match, not a suffix of a shell name.
- Regex `(?<![A-Za-z0-9.-])ngwindows\.com` over all 516 Section 1 anchors: **516/516 pass**.
- `performingwindows` appears in **0** rows of the Ahrefs export (anchor, target or referring URL).
- Zero of the 258 Section 1 hostnames contain the string `window` at all, so none is itself one of
  the known shells (`performingwindows.com`, `ngawindows.com`, `northgawindows.com`,
  `thermalprowindows.com`, etc. per REDIRECT-TEST-RESULTS.md).
- Note for context: the Semrush export DOES contain 353 `performingwindows` rows, but **none** of
  them is in the 148096 cluster — all 112 Semrush 148096 rows carry the ngwindows.com anchor.

### Task 5 — target attribution: CLEAR
All 516 `Target URL` values resolve to host `ngwindows.com`. Two literal values, 258 each:
`https://www.ngwindows.com/` and `https://ngwindows.com/`. The 258 `www` rows carry
`Redirect Chain URLs = https://ngwindows.com/` (the client's own www→apex redirect); the 258 apex
rows have an empty chain. **No row points at a shell domain.** This section is correctly filed
under ngwindows.com.

### Task 2 — false-positive hunt: none found
- All 258 are machine-generated SEO-tool-keyword names (`dapacheckerbulk`, `bulkdrcheckerfree`,
  `webpagerankchecker`…) on 7 cheap gTLDs: `.shop` 50, `.store` 49, `.website` 44, `.site` 41,
  `.space` 37, `.online` 30, `.link` 7. **Zero `.com`, zero brandable names, zero real-business names.**
- Export-side: `Domain rating` 0 on 496/516 rows (max 0.6); `Page traffic` = 0 on **516/516**;
  `Domain traffic` non-zero on only 8 rows (max 21).
- Live `public-domain-rating-free` run today on all 258: **all 258 return DR 0.0–0.6**, matching the
  export. Nothing has grown into a real property since the export.
- `Page type` is the only field with variation (`Listing > Business` 372, `Listing > Service` 106,
  `Listing > Product` 38) — that is the vendor's own randomised listing-template label on an
  otherwise byte-identical page, not evidence of genuine editorial content. The header does not
  claim uniformity here, so this is not a defect.
- WebSearch on the most generically-named candidates (`rankchecker.space`, `backlinkschecker.site`,
  `blogpostbacklinks.online`) returns no trace of any of them — no reviews, no listings, no presence.
- Closest things to an anomaly, all still safely disavowable: `blogpostbacklinks.online`
  (`Dofollow linked domains` = **512,274** — it is a link-farm hub, which strengthens the case, not
  weakens it); `dacheckerforfree.online`, `backlinkscheckers.website`, `dapacheckerbulk.space`,
  `freedadrchecker.space` (traffic 1–21, 1–2 keywords — noise, not a business).

---

## 2. ENTRIES TO REMOVE

**None.** Every one of the 258 has all four claimed elements present and exact. There is no entry
for which evidence could not be located.

---

## 3. WHERE THE EVIDENCE IS WEAKER THAN CLAIMED

These do not justify removing anything, but the section is narrower than it reads.

**(W1) "516 links" is 258 pages, not 516 placements.** There are exactly **258 unique referring page
URLs**; every one appears twice, once per target variant (www and apex). Links per page = 2 for
258/258 hosts. So the real footprint is 258 pages × 2 href variants. "516 links" is a true Ahrefs
row count but overstates the distinct placements to any reader who does not open the export.

**(W2) Liveness is single-observation and stale.** `First seen == Last seen` on **514 / 516** rows —
Ahrefs saw these links once and has never re-crawled them. Only `rankchecker.space` (2 rows) was
re-confirmed (2026-09-18 → 2026-09-24). Last-seen dates run 2026-09-17 to 2026-09-29, i.e. **7–19
days before the export's own freshness horizon** of 2026-10-06. Section 1 is systematically staler
than the rest of the export.

**(W3) `Lost status` carries no information here.** It is empty on all 516 Section 1 rows — but also
empty on **all 2,665 rows** of the export. This is a live-links-only export; the column cannot
distinguish live from dead and must not be cited as proof of liveness. Answering task 4 honestly:
nothing in the evidence base shows any of these as dead, and nothing in it could.

**(W4) Cross-tool corroboration is 11, not 258.** Semrush's own 148096 cluster is 87 domains /
112 rows, all with the identical anchor and `nofollow=false`. Only **11 of those 87** are in
Section 1 (`7-seo.link`, `backlinkfindertool.shop`, `backlinkfreeseo.link`, `backlinkindia.link`,
`backlinksseochecker.space`, `bulkbacklinkreport.space`, `dacheckerseo.store`,
`freebulkdachecker.shop`, `massdachecker.website`, `onlinewebsitechecker.space`,
`seocheckerforfree.site`). The other **247 rest on Ahrefs alone**, from one crawl, never re-seen.

**(W5) Grounds (d) is listed but not counted.** The header says "Grounds (a)+(b)+(c)+(e), all four
present on every entry" and then separately describes (d). (d) does in fact hold uniformly (1 unique
title, 516/516), so this is only a drafting inconsistency — but as written the reader is told four
grounds and shown five.

---

## 4. RECOMMENDED FINAL COUNT

**258 domains — unchanged. Remove nothing.**

Restate the link count as **258 referring pages (516 Ahrefs link rows: www + apex target variant
from each page)** rather than a bare "516 links".

This is the cleanest tier in the file: a single vendor campaign ID (`148096`) with one path, one
anchor, one title, dofollow, spam-flagged by Ahrefs at both row and domain level, and all 258 hosts
confirmed still indexed at DR ~0 today. Disavowing at domain level is correct — there are no other
links from these 258 hosts in the export (0 rows from any of them on any other path), so no
collateral loss.

---

## 5. WHAT THE SECTION HEADER OVERSTATES

1. **"raises the domain count from 87 to 258"** — materially misleading. Ahrefs did **not** confirm
   and extend the Semrush 87; the two sets overlap on **11**. Ahrefs contributes 247 that Semrush
   never saw, and **fails to corroborate 76 of the Semrush 87**. The accurate statement is: the
   campaign-148096 cluster is **334 domains across both tools** (87 + 258 − 11), of which Ahrefs
   sees 258 and Semrush sees 87.
2. **"Ahrefs independently confirms it"** — independent confirmation exists for 11 domains. For the
   other 247 Ahrefs is the sole source, on a single uncorroborated crawl observation.
3. **"516 links"** — 258 pages; see W1.
4. **Implied liveness** — see W2/W3. The file's global header already concedes "link liveness is as
   of each export's Last-seen date"; Section 1 should carry that caveat explicitly, since its
   last-seen dates are the oldest in the export.
5. **"Grounds … all four present on every entry"** vs five grounds listed — see W5.

### Separate finding: under-inclusion (outside Section 1's scope, but relevant before filing)
**76 domains** sit in the Semrush export with the byte-identical `/dir/quality-authority-backlinks-148096`
path, the byte-identical anchor naming ngwindows.com, and `nofollow=false` — and are **not in the
disavow file at all** (checked against all 460 entries, 0 matches). They are the same campaign on
the same evidential footing as the 11 corroborated entries. Examples: `100ranking.com`,
`1seoservices.com`, `7-seo.com`, `backlinksindia.com`, `goldbacklinks.com`, `stormbacklink.com`,
`seozens.com`, `diversifiedseo.com`, `geobacklinks.link`, `proseobacklinks.link`. The full list is
reproducible with:
`git show 6f5f407:backlink-audit/work/links_raw.tsv | awk -F'\t' '$1 ~ /148096/'`.
Section 1 is not wrong; it is incomplete. Adding these would take the cluster to 334.
