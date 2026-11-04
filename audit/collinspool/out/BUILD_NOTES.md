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

## Inputs NOT supplied (same as the sample) and effect
1. **Signed template `NIC_signed_template.xlsx`, Harbinger logo, `kk/` scripts.** Scripts
   written from the spec, not the signed code. **`compare.py` could not be run** (no
   template); structure matches `AUDIT_FORMAT.md`, pixel styling is best-effort and
   unverified. No logo embedded. Font Geist is set but will substitute if not installed.
2. **Money-page list (§10).** Approximated from the Tab-08 target URLs
   (`/services/`, `/location/`, `/positions/`); exact-match **anchor** is the primary
   Held trigger, so this has little effect here.
3. **Client's Ahrefs CSV export (§1).** Not supplied + 250-cap ⇒ Ahrefs is a sample. A
   full Semrush∪Ahrefs merge needs the client to pull the full Ahrefs CSV.

## Spec conflicts between the two docs (resolved the same way as the sample)
| Point | AUDIT_FORMAT.md | Playbook | Used |
|---|---|---|---|
| Data-cell borders | thin all round | header-only; "don't box every cell" | header-row borders + gridlines |
| Summary title size | 9 bold accent | 21 | 9 bold accent |

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
