# New Garden Landscaping & Nursery — Backlink Audit: Critical Review & Rebuild to Signed Format

**Target site:** newgarden.com
**Rebuilt:** 2026-11-03, to conform to `AUDIT_FORMAT.md`, `BACKLINK_AUDIT_PLAYBOOK.md`, and the K&K Manufacturing template.
**Source of truth:** Semrush Backlink Analytics export (= the workbook), live-verified; Ahrefs used only for corroboration.

---

## 1. What changed in this rebuild

The uploaded workbook was already ~95% conformant (it came off the same `build.py`). Two kinds of fixes were applied:

### A. One substantive classification defect — fixed
The playbook (verdict rule 4) says **exact-match commercial/geo anchors are always *Held* for supplier confirmation, never silently kept**. The uploaded workbook left **118** such domains in **Keep**.

Applying the playbook's verdict order (rule 2 "AS ≥ 20 → Keep" outranks rule 4):
- **4 domains stayed Keep** — AS ≥ 20, genuine press/news (`einpresswire.com` AS 48, `newsblaze.in` 25, `lmcordoba.com.ar` 21, `middletownlifemagazine.com` 20).
- **114 domains moved Keep → Held** — 82 dofollow → **Held (Pending Partner)**, 32 nofollow → **Held (Nofollow, No Action)**.

This is validated against the signed template: in K&K, ~99% of exact-match-commercial domains are Held (only 4 incidental exceptions). New Garden now matches that discipline. **The disavow set is unchanged** — Held is never disavowed, so no good or paid link is newly at risk; the fix simply surfaces 82 more domains to the supplier instead of hiding them in Keep.

### B. Format conformance — fixed
- Title now merged **B1:E2** (was unmerged).
- **Key findings** heading → 10 pt; expanded from **6 → 7 findings** (playbook requires seven).
- Anchor-profile header row → 9 pt (was 10).
- Pending-Disavow header wording → "…append to **disavow.txt**…" (matches signed format).

### Count changes (client-facing)
| Status | Before | After |
|---|---:|---:|
| Spam (Disavow) | 1,646 | **1,646** (unchanged) |
| Held (Pending Partner) | 120 | **202** |
| Held (Nofollow, No Action) | 13 | **45** |
| Spam (Nofollow, No Action) | 56 | 56 |
| Keep | 848 | **734** |
| Own Site | 0 | 0 |
| **Total** | 2,683 | 2,683 |

Tab 05 (Exact Match Anchors): 133 → **247 rows**. Pending Disavow Lines: 120 → **202**.

---

## 2. Data validation (independent, live)

- **Semrush live totals match the workbook exactly:** `8,086 backlinks / 2,683 referring domains, AS 30`. Authentic, current export.
- **History (Semrush):** referring domains sat near **700–1,200 for most of the past year, then jumped from ~1,170 (Sep 2026) to ~2,640 (Oct)** — a recent attack.
- **Ahrefs corroboration:** confirms the spam campaigns, the legitimate core (`plants.newgarden.com` catalogue, branded listings), and independently rates the Tab 05 geo anchors **not spam, DR 60** — supporting *hold*, not disavow.

---

## 3. Verification — 16/16 checks pass (`verify.py`)

**Disavow integrity:** all lines `domain:` lowercase, no URLs, no duplicates; every file domain is Spam (Disavow) with ≥1 dofollow; **no Held/Keep/Own-Site/nofollow leak**.
**No false positives:** every one of the 1,646 disavow domains rests on **visible evidence** — a spam/sales-copy anchor, a spam page title (e.g. the `.space` "Where to buy aged domains and backlinks" domain-marketplace titles), an off-topic anchor, or a known directory/SEO host — **none on Authority Score or TLD alone** (the playbook's hard rule, and its `weldrunners` lesson).
**No false negatives:** zero Keep/Held domains carry a dofollow spam anchor; zero nofollow-spam rows actually have a dofollow link.
**Reconciliation:** status counts sum to 2,683; Disavow List = Spam (Disavow) set; Pending = Held (Pending Partner) set; Tab 05 = both Held sets; backlink sums reconcile to 8,086.

**Concentration caveat (unchanged):** `rosih.ru` is 2,536 of the 4,216 "disavowed backlinks" but Ahrefs sees only 3 — it is **image hotlinking** of a `plants.newgarden.com` image, not bought links. Judge scale by **1,646 domains**, not backlink count.

---

## 4. Structural conformance vs the K&K template

Tab order, every data-tab header, freeze panes (B2), autofilter, gridlines, accent `FF0C343D`, Geist, 21 pt title, and the embedded logo all **match**. Residual differences are benign and expected:
- Summary B1 holds the client name (per-client by design).
- Summary has one extra merged region — the **source-note row** (A30), which New Garden's workbook carries and K&K places differently.
- Anchor Analysis has one extra column-width definition (cosmetic; both tabs have the correct 6 columns/headers).

### Caveats I could not clear in this environment
- The playbook's `kk/` scripts and the authoritative `NIC_signed_template.xlsx` are **not in the repo**, so a pixel-exact `compare.py` against the *NIC* template could not be run; the **K&K workbook you supplied was used as the structural reference** instead.
- **Geist** is not installed here, so the font name is set correctly but its on-screen rendering can't be verified locally.
- No raw Semrush/Ahrefs CSVs were supplied; the rebuild used the workbook's own data, which *is* the Semrush export (live totals matched exactly).

---

## 5. Human gates (unchanged — I cannot clear these)
1. **Supplier confirmation.** New Garden's brief calls this role "supplier"; the workbook calls it "partner" — tied together once in the disavow file header. Ask which of the 202 pending placements were commissioned; append to `disavow_newgarden.txt` only those **not** confirmed.
2. **Search Console.** Check for a manual action, and for an existing disavow file on the `newgarden.com` property (uploading **replaces** it). No client-owned redirect domains were found, so the single file is the complete set.
3. Prefer **monitoring** unless a manual action exists or the client confirms buying links. I did **not** contact the supplier and did **not** submit anything to Google.

---

## 6. Files
| File | Contents |
|---|---|
| `NewGarden_Backlinks_Audit.xlsx` | Rebuilt 7-tab workbook, reclassified, 7 findings, logo preserved |
| `disavow_newgarden.txt` | 1,646 spam/dofollow domains, grouped by reason, playbook header, **held for submission** |
| `disavow_newgarden_PENDING_partner_confirmation.txt` | 202 held domains; append only those the supplier does not confirm |
| `build.py` / `verify.py` | Reproducible rebuild + 16-check verification suite |
