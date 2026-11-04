# Black Walnut Construction, LLC — Backlink Audit & Disavow Prep

**Target site:** blackwalnutconstruction.com
**Produced:** 2026-11-04, in the signed Harbinger/NIC format (`AUDIT_FORMAT.md`), following `BACKLINK_AUDIT_PLAYBOOK.md`, using the K&K Manufacturing workbook as the structural template.
**Source of truth:** Semrush Backlink Analytics (live), cross-checked against Ahrefs.

---

## 1. Headline

- **The brief is badly out of date.** It cited **368** referring domains; the live profile is **1,631 referring domains / 2,142 backlinks** (Semrush, 2026-11-04). Per the playbook, the **full live profile was audited**, not the brief's 22-row sample.
- **This is a recent negative-SEO / spam flood.** Referring domains sat at ~60–90 through 2025, then exploded: ~206 (Jan 2026) → ~461 (Sep) → **~1,575 (Oct)**. Authority Score is **8**.
- **1,364 spam domains** (dofollow) are prepared in the disavow file; **172** directory/geo placements are **held** for supplier confirmation; the file is **not** submitted.
- **16/16 verification checks pass.** No held/keep/own-site domain leaks into the disavow file; every disavowed domain rests on visible link evidence.

---

## 2. Classification (all 1,631 domains, playbook verdict order)

| Status | Domains | Backlinks | Meaning |
|---|---:|---:|---|
| Spam (Disavow) | **1,364** | 1,372 | Spam with ≥1 dofollow link — in the disavow file |
| Held (Pending Partner) | **172** | 625 | Lexington-SC exact-match anchor **or** deep money-page link — may be commissioned; awaiting supplier |
| Held (Nofollow, No Action) | 22 | 34 | Same, but nofollow — no action |
| Spam (Nofollow, No Action) | 54 | 55 | Spam, all nofollow — no action |
| Keep | 19 | 56 | Genuine/harmless (agency site, higher-AS citations) |
| Own Site | 0 | 0 | — |
| **Total** | **1,631** | **2,142** | |

### The two campaigns are cleanly separable (the key signal)
- **Link-scheme / PBN flood → home page.** All **1,395** sales-copy/PBN links point at the home page. The dominant anchor, on **1,151 domains**, is *"blackwalnutconstruction.com premium authority backlinks for better search visibility"*; a PBN anchor (*"…DA 50 PA 40 Premium PBN… buy backlinks online cheap"*) spans **95 domains** (the brief's "62"). → **Spam.**
- **Commissioned-looking geo campaign → deep money pages.** **227** links with Lexington-SC exact-match anchors (office/retail/commercial/residential construction) point at the four `/commercial-`, `/office-`, `/residential-`, `/retail-construction-services` pages. → **Held** for supplier confirmation (these may be a paid local-directory package).

All 22 brief-listed domains were classified: the directories (`powerbizdirectory`, `webmash`, `favemarks`, `bizfront`, `blegg.biz`, …) are **Held**; the `.sbs/.cfd` "seo domain research" nofollow ones are **Spam (Nofollow)**; clear PBN ones (`australianwebdirectory.shop`, `bestwebstats`, `bisprofit`) are **Spam (Disavow)**.

---

## 3. Evidence rule — no disavow on score or TLD alone

Every one of the 1,364 disavow lines rests on visible evidence, grouped by reason in the file:
- **1,289** — SEO sales-copy / PBN anchor
- **65** — aged-domain / "where to buy backlinks" marketplace **page titles** (e.g. `queries.co.in`, `uaewebdirectory.info`, the `domraider.*` network's *"Any SEO resource… no middlemen, lowest prices"*)
- **2** — spam host name (SEO/backlink/checker/directory)
- **8** — other spam anchor/title evidence

Verified: **zero** disavow domains rest on Authority Score or TLD alone; **zero** Keep/Held domains carry a dofollow spam anchor; deep-page directories (`powerbizdirectory`, `webmash`) are correctly **Held**, not disavowed.

### Two borderline Keeps flagged
`cracktstreamsas.blogspot.com` (piracy-streaming blog) and `factmags.com` (AS4) were in the brief but carry only naked-URL home-page links with **no** spam anchor/title/host signal. Per the playbook's evidence rule they stay **Keep**. They are the client's/supplier's call to add if desired — noted, not silently disavowed.

---

## 4. Deliverables

| File | Contents |
|---|---|
| `BlackWalnut_Backlinks_Audit.xlsx` | 7-tab workbook in signed format (logo preserved), 1,631 domains, 7 key findings |
| `disavow_blackwalnut.txt` | 1,364 spam/dofollow domains, grouped by reason, playbook header, **held for submission** |
| `disavow_blackwalnut_PENDING_supplier_confirmation.txt` | 172 held domains; append only those the supplier does **not** confirm |
| `classify.py` / `build.py` / `mk_bw.py` / `verify_bw.py` | Reproducible pipeline + 16-check verification (all pass) |

Workbook tabs: Summary · Referring Domain Audit · All Backlinks · Anchor Analysis · Exact Match Anchors (Tab 05) · Pending Disavow Lines · Disavow List. Structurally matches the K&K template (tab order, headers, freeze panes, autofilter, gridlines, accent, Geist, 21 pt title, logo).

---

## 5. Caveats (environment)
- Semrush is the metric source; **Ahrefs was used only to corroborate** the spam campaigns (API-unit limits, as the playbook anticipates) rather than for a fresh full discovery pull.
- The oldest ~142-link page was transcribed from the live response with a few duplicate-anchor rows collapsed and emojis stripped — this affects only the per-link "All Backlinks" tab detail, not the headline counts (which come from the refdomains export and reconcile to 2,142).
- Geist is set as the font but can't be rendered/verified in this environment; the authoritative `NIC_signed_template.xlsx` isn't in the repo, so K&K was used as the structural reference.

---

## 6. Human gates (I cannot clear these)
1. **Supplier confirmation.** The brief calls this role "supplier"; the workbook/file call it "partner" — tied together in the disavow header. Ask which of the 172 pending Lexington-SC placements were commissioned; append to `disavow_blackwalnut.txt` only those **not** confirmed.
2. **Search Console.** Check for a manual action and for an existing disavow file on the `blackwalnutconstruction.com` property (uploading **replaces** it). No owned redirect domains were found, so this single file is the complete set.
3. Prefer **monitoring** unless a manual action exists or the client confirms buying links. I did **not** contact the supplier and did **not** submit anything to Google.
