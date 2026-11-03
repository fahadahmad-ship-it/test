# New Garden Landscaping & Nursery — Backlink Audit: Critical Review & Disavow Prep

**Target site:** newgarden.com
**Source workbook:** `NewGarden_Backlinks_Audit.xlsx`
**Reviewed:** 2026-11-03
**Reviewer:** independent re-check against live Ahrefs + Semrush (not a restatement of the workbook)

> **Note on the brief.** The task text and the 22-row table referenced `blackwalnutconstruction.com` — that was a *sample* of the format. The actual data to assess is this workbook, for **newgarden.com**. "Tab 05" = the **Exact Match Anchors** sheet (the held, possibly-commissioned placements).

---

## 1. Bottom line

- The audit is **sound and internally consistent.** Every count reconciles, and the single most important safety check passes: **no held / pending / exact-match / "Keep" domain has leaked into the disavow file.**
- The underlying data is **authentic and current** — live Semrush totals match the workbook exactly, and an independent Ahrefs pull confirms the same spam campaigns and the same legitimate core.
- **Disavow file is prepared** (`disavow_newgarden.txt`, 1,646 domains). It is **not** submitted, and it should not be until two human gates clear (Search Console manual-action check + supplier confirmation).
- Two things to correct in how the audit is *presented* (not errors in the decisions): the "4,216 spam backlinks" headline is inflated by one image-hotlink domain, and "disavow" is being treated as the default when **monitoring** is the more defensible default here.

---

## 2. What was produced

| File | Contents | Status |
|---|---|---|
| `disavow_newgarden.txt` | 1,646 spam domains with ≥1 dofollow link, Google format | **Ready, HELD for submission** |
| `disavow_newgarden_PENDING_partner_confirmation.txt` | 120 held exact-match/geo domains | Append **only** for domains the supplier does **not** confirm |
| `NewGarden_Backlink_Audit_Critical_Review.md` | this review | — |

---

## 3. Data validation (independent, "check on all tools")

**Semrush (the workbook's own source), live 2026-11-03:**
`total=8086 · domains=2683 · follows=7293 · nofollows=793 · AS=30 · images=292`
→ Matches the workbook's stated `8,086 backlinks / 2,683 referring domains` **exactly**. The export is faithful and not stale.

**Ahrefs (independent second opinion):**
- Confirms the spam campaigns and independently flags them spam: *"Build Powerful Website Authority with Premium SEO Backlinks newgarden.com"*, *"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN…"*, and the *"SEOExpress.org"* fake-testimonial spam (604 ref domains).
- Confirms the legitimate core: branded *"New Garden Landscaping & Nursery Inc"* and the `plants.newgarden.com` plant-catalogue citations (not spam, DR 52) — correctly kept.
- Confirms the Tab 05 geo anchors *"Landscape Maintenance Services in Greensboro/Winston-Salem, NC"* (97 ref domains each) are marked **not spam, DR 60** — supporting the decision to **hold rather than disavow** them.
- Spot-checks: `favemarks.net` → spam in both tools; `atozbookmarks.net` (Tab 05) → present, not spam; rows are genuine, not fabricated.

---

## 4. Correctness checks on the workbook (all pass)

| Check | Result |
|---|---|
| Summary counts vs actual tab rows | ✅ reconcile (1,646 / 848 / 120 / 56 / 13 = 2,683) |
| Held "Pending Partner" domains in disavow file | ✅ **0 leaks** |
| Tab 05 exact-match domains in disavow file | ✅ **0 leaks** |
| "Keep" domains in disavow file | ✅ **0 leaks** |
| Every disavow domain is `Spam (Disavow)` in the audit | ✅ 1,646/1,646 |
| Disavow domains carry a dofollow link | ✅ all; 0 contradictions |
| Duplicate disavow lines | ✅ none |
| Nofollow-"no action" rows with a dofollow link | ✅ 0 contradictions |
| Spam anchors hiding in "Keep" (false negatives) | ✅ none found |

**False-positive risk (the real danger of disavowing):** the **highest-authority domain in the entire disavow set is only AS 18** (a hacked-link injection — *"LINKS FOR newgarden.com TELEGRAM @…"*), then rosih.ru at AS 10. No strong editorial/legitimate domain is being disavowed. The 9 disavow domains whose top anchor is a plain `newgarden.com` are all link-farm TLDs (`a1webdirectory.xyz`, `australianwebdirectory.shop`, `.space` directories) — correctly caught by the TLD rule. **Risk of harming good links: very low.**

---

## 5. Two presentation issues to fix

1. **The "4,216 disavowed backlinks" figure is misleading.** `rosih.ru` alone accounts for **2,536 of them (60%)**. Ahrefs sees only **3** links from that domain — the signature of **image hotlinking** (rosih.ru embeds a `plants.newgarden.com` image across thousands of its catalogue pages; Semrush counts each page as a backlink). Disavowing the *domain* is harmless, but describe the scale as **1,646 spam domains**, not "4,216 spam links," and don't characterise rosih.ru as bought links.

2. **Default action should be "monitor," not "disavow."** The Summary itself says it well: disavow only if Search Console shows a **manual action** or the client **confirms buying links**. Google ignores obvious auto-generated spam on its own, and an unnecessary disavow can remove value. The file should sit ready and be submitted only when a gate below actually triggers.

---

## 6. Tab 05 (Exact Match Anchors) — the held set

133 domains, all "Directory / blog" type, carrying exact-match local-service anchors:
- **70 Winston-Salem**, **51 Greensboro**, **12 non-geo**
- **120 dofollow → "Held (Pending Partner)"** (candidates for the pending file)
- **13 nofollow → "No action"** (pass no value either way)

These are the links that **must be confirmed with the previous SEO supplier before any disavow**. They look like a single coordinated local-SEO package (consistent anchors, directory sources) — which is exactly why they could be a legitimate commissioned placement rather than toxic spam. Columns F (*Partner confirmed? Y/N*) and G (*Final decision*) are intentionally blank, to be filled **after** the supplier responds.

---

## 7. Human gates — what I did NOT do (and cannot)

- **I did not contact the previous supplier**, and I cannot confirm on their behalf which anchors were commissioned. That confirmation is a prerequisite to finalising the pending set.
- **I did not submit anything to Google.** The disavow file is prepared and held.
- **Check Google Search Console** for a manual action before submitting — this data does not show one, and if there is none, monitoring is the better path.

### Recommended next steps
1. Confirm with the previous SEO supplier which Tab 05 placements were commissioned; record Y/N in column F and the decision in column G.
2. For the domains **not** confirmed, append `disavow_newgarden_PENDING_partner_confirmation.txt` to `disavow_newgarden.txt`.
3. Check Search Console for a manual action. If none and the client never bought links, **monitor** rather than submit.
4. If submitting: upload `disavow_newgarden.txt` in Google's Disavow Tool for the correct property (note links point to `newgarden.com`, `www.newgarden.com`, and `plants.newgarden.com` — a domain-property disavow covers all).
