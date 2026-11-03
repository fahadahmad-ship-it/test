# New Garden audit — build notes, deviations & limitations

Built 2026-11-03 by re-pulling the live profile from Semrush + Ahrefs and running
a from-scratch pipeline (`audit/newgarden/scripts/{load,classify,build}.py`,
`check/verify.py`) against `AUDIT_FORMAT.md` + `BACKLINK_AUDIT_PLAYBOOK.md`.

`verify.py` passes all checks. The points below are where this build had to make a
call the two spec docs did not settle, or where an input the playbook assumes was
not available in this environment. Flagged honestly per playbook §11.

## Inputs that were NOT supplied (and the effect)

1. **Signed template `NIC_signed_template.xlsx` + Harbinger logo PNG + `kk/` scripts.**
   - The scripts here were written fresh from the two spec docs, not copied/adapted
     from `kk/`. Logic follows the playbook; code is not the signed code.
   - **`compare.py` (cell-for-cell template match) could not be run** — no template to
     compare against. Structure (tabs, order, columns, statuses) matches `AUDIT_FORMAT.md`;
     pixel-level styling is best-effort and unverified.
   - **No logo embedded.** The Summary names the missing asset in its source line.
   - **Font Geist** is set on every cell, but if the renderer lacks Geist it will
     substitute — appearance will differ from the signed file.

2. **Money-page list (playbook §10).** Not supplied. The deep-money-page signal
   (verdict rule 4) was calibrated from the live `target_url` set to fire only on
   `/service/…`, `/location/…` and local landing slugs on the **main** site — it
   excludes the `plants.newgarden.com` catalogue and `/notes/` blog. Without the
   client's real money-page list this is an approximation; exact-match **anchor** is
   the primary Held trigger.

3. **Client's Ahrefs CSV export (playbook §1).** Not supplied, and the **Ahrefs MCP
   API caps `referring-domains` and `all-backlinks` at 250 rows per call** (live
   profile is 1,694 refdomains / 3,573 backlinks per Ahrefs stats). So Ahrefs
   contributed a **250-domain + 250-link sample** for discovery/corroboration only
   (found 42 Ahrefs-only domains, 133 Ahrefs-only links, carried their first_seen +
   http_code). A complete Semrush∪Ahrefs merge needs the client to pull the full
   Ahrefs CSV; this build is **Semrush-complete, Ahrefs-sampled**.

## Spec conflicts between the two docs (how they were resolved)

| Point | AUDIT_FORMAT.md | Playbook | Used here |
|---|---|---|---|
| Data-cell borders | "thin border all round" | header-only; "do not box every cell" (§8/§12) | **Header-row borders + gridlines on** (playbook, its explicit lesson) |
| Summary title size | 9 bold accent | 21 (§8) | **9 bold accent** (AUDIT_FORMAT, it notes the client shrank it) |

Both are defensible; resolve against the real signed template when available.

## Deliberate methodology choices

- **Authority Score = Semrush refdomains `domain_ascore`**, not `backlinks_comparison`.
  Reason: cost (one 681-row refdomain page alone cost 27,640 units; a full comparison
  sweep is ~27 calls) and the 250-cap. Safe because AS is only used by rule 2 to
  **short-circuit to Keep** — a genuine site with no spam evidence is kept by rule 12
  regardless, so the refdomain report's ~11-pt understatement cannot create a false
  positive. 0 disavowed domains have AS ≥ 20.
- **Link de-duplication (playbook §5):** links are deduped on canonical
  `(source_url, target_url, anchor)`. Semrush's raw headline is **8,086 backlinks**;
  after dedup + Ahrefs discovery the workbook holds **7,189 unique links**. The
  workbook/Summary report the deduped figure.
- **7 Semrush rows rejected** by the CSV loader (embedded newline/semicolon in
  Pinterest profile titles) — benign, Keep-type; <0.1%.
- **`root_of` uses a public-suffix approximation** (co.uk, com.au, blogspot.com,
  web.app, …) so multi-part TLDs and platform subdomains are not wrongly merged.

## Notable classification outcomes (and how they differ from the earlier sample)

- **rosih.ru → Keep** (2,536 raw / 1,642 dedup image-source links from a `.ru` image
  scraper). No spam anchor/host/title → no evidence to disavow (principles 2 & 3). The
  earlier sample disavowed it; this build does not.
- **Directory farms → Held (Pending Partner)**, not Keep: `webmash.org`,
  `mysmallbiz.net`, `directoryplus.biz`, `fixx.co`, `powerbizdirectory.com`. They
  carry a geo exact-match anchor on at least one page (rule 4), so they are held for
  partner review rather than silently kept (the sample's false-negative) or
  auto-disavowed. They appear in **Pending Disavow Lines** to add if unconfirmed.
- **Disavow evidence:** 1,640 PBN sales-copy anchor · 50 spam title/URL · 17 spam
  host. **0** rest on AS/TLD/IP alone; **0** name the client without sales copy.

## Cost
- Semrush: ~967k API units (full backlink + refdomain re-pull) + ~56k recon.
- Ahrefs: ~6,250 units (250 refdomains + 250 backlinks).

## Outstanding (client/partner actions)
1. Partner to fill `Partner confirmed?` / `Final decision` on the 344 Exact Match rows.
2. Client to check Google Search Console for a manual action and whether a disavow
   file already exists on newgarden.com (uploading replaces it).
3. For a complete merge, client to supply the full Ahrefs backlink + refdomain CSVs.
4. Do not upload before the partner conversation. Submission to GSC is manual.
