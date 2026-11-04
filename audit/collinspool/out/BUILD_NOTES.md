# Collins Pool Management audit — build notes, deviations & limitations

Built 2026-11-04 by re-pulling the live profile from Semrush + Ahrefs and running the
pipeline (`audit/collinspool/scripts/{load,classify,build}.py`, `check/verify.py`) against
`AUDIT_FORMAT.md` + `BACKLINK_AUDIT_PLAYBOOK.md`. `verify.py` passes all checks.

The pipeline is the same code used for the New Garden sample, re-pointed via the client
constants at the top of `classify.py` (client name, money domain, pool/lifeguard
vocabulary, Atlanta/Alpharetta/Marietta GA geo, `/services/ /location/ /positions/` money
pages) — exactly the "copy and adapt per client" model the playbook §10 describes.

## Data pulled (today)
- **Semrush (complete):** 5,801 backlinks, 2,006 referring domains. Matches the overview
  (5,803 / 2,003; 5,484 dofollow / 319 nofollow).
- **Ahrefs (sampled):** 250 referring domains + 250 backlinks — the **Ahrefs MCP caps
  both endpoints at 250 rows/call** (live profile is 1,054 refdomains / 1,614 backlinks).
  Used for discovery (144 Ahrefs-only links added) + is_spam/http_code corroboration only.
- After de-dup on canonical `(source_url, target_url, anchor)` (playbook §5):
  **5,776 unique links across 2,087 referring domains.**

## The "592-domain profile" (brief) is not reconcilable with the live data
Semrush 2,003 / Ahrefs 1,054 live / 1,702 all-time — none equal 592. Most likely a GSC
"top linking sites" export or a dated snapshot. Flagged in the Summary and delivery note.

## Tab-08 (76 flagged domains) — handling
- 74/76 are in the live Semrush profile: **42 → Spam(Disavow)**, **32 → Held(Pending)**.
- **2 not in the live profile:** `daechul.co.com` (Section-1 PBN) and `articles4all.org`
  (Section-2 directory; Ahrefs last_seen 2026-10-28, i.e. lost). They are **not** in the
  generated disavow file because the build is evidence-based on the live profile (playbook
  principle 2). Recommendation to the team: manually append `daechul.co.com` to the
  disavow and hold `articles4all.org` if the original Tab-08 source still shows them.

## Format verified cell-for-cell against the signed sample (incl. XML level)
`check/compare.py` compares this workbook's formatting against the signed sample
(the uploaded `NewGarden_Backlinks_Audit.xlsx`) across tabs, order, headers, column
widths, row heights, **default row height (sheetFormatPr)**, fonts (name/size/bold/italic/
**colour**), **fills**, borders, alignment (per column), **number formats (per column)**,
date types, freeze panes, filters, gridlines, merges and the logo (drawing XML is
byte-identical). A full per-column sweep of every data tab (header + data cell, all
columns) reports **0** differences.

Earlier openpyxl-only checks gave false passes (the playbook §9 warns of this). The
XML/colour/fill-level review then found and fixed real gaps: the Summary status and
anchor-profile **mini-tables** (accent-fill white-bold headers, white-fill bordered
bodies), **accent-coloured** section headings, the **grey italic** source line, 21pt
title, per-column alignment, `#,##0` / `%` number formats, First Seen as a real date,
and default data-row height 15.75.

**Result: identical to the sample except the values that are meant to be client-specific**
— the Summary title ("Collins Pool Management") and the Pending Disavow header, which
names this client's own file (`disavow_collinspool.txt`). (The workbook also has 7 key
findings vs the sample's 6, per the playbook's "seven findings" rule — content, not
format.)

- **Logo:** the Harbinger logo is the *agency* logo (same for every client), so it was
  extracted from the signed sample (`audit/collinspool/ref/harbinger_logo.png`) and
  embedded at the same anchor/size. Not a client asset, so reuse is correct.
- **Title size:** the signed sample uses **21pt** bold accent (not 9pt). The AUDIT_FORMAT
  text ("shrank to 9") did not match the actual signed file; the file wins — 21pt used.
- **Borders:** header row bordered, data cells unbordered — matches the sample (and the
  playbook's "don't box every cell"), gridlines left at default.
- **Data cells:** Geist 9, black font on white fill — matches the sample.
- Font Geist is named throughout; it will substitute visually only if the renderer lacks
  Geist, but the stored format is identical to the sample.

## Inputs NOT supplied and effect
1. **`NIC_signed_template.xlsx` + `kk/` scripts.** Scripts written from the spec, not the
   signed code; but the OUTPUT is verified against the signed sample (above).
2. **Money-page list (§10).** Approximated from the Tab-08 target URLs
   (`/services/`, `/location/`, `/positions/`); exact-match **anchor** is the primary
   Held trigger, so this has little effect here.
3. **Client's Ahrefs CSV export (§1).** Not supplied + 250-cap ⇒ Ahrefs is a sample. A
   full Semrush∪Ahrefs merge needs the client to pull the full Ahrefs CSV.

## Deliberate methodology choices
- **AS = Semrush refdomains `domain_ascore`**, not `backlinks_comparison` (cost: the
  overview call alone was 112k units; a full comparison sweep is many more). Safe because
  AS only short-circuits to Keep (rule 2); 0 disavowed domains are AS ≥ 20.
- **Link de-dup** per §5: raw Semrush headline 5,803 backlinks → 5,776 unique links.
- **`root_of`** uses a public-suffix approximation (co.uk, com.au, blogspot.com, …).

## Disavow evidence (no weak-only lines)
1,528 PBN/link-selling anchor · 57 spam page title/URL · 8 spam host. **0** rest on
AS/TLD/IP alone; **0** name the client without sales copy; **0** at AS ≥ 20.

## Cost
- Semrush: ~1.12M API units (full re-pull) + ~112k recon (overview).
- Ahrefs: ~6,250 units (250 refdomains + 250 backlinks) + ~50 stats.

## Outstanding (client/partner actions)
1. Confirm with Harbinger + the commissioning partner before upload (brief requirement).
2. Partner fills the 381 Exact Match confirmation cells.
3. Check GSC for a manual action / existing disavow file (upload replaces it).
4. Decide the 2 not-found Tab-08 domains.
5. Supply the full Ahrefs CSV for a complete merge.
6. Brief's deadline (end Oct 2026) is past (today 2026-11-04).
