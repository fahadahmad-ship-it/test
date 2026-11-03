# New Garden Landscaping & Nursery — Backlink Audit: Critical Review

**Workbook:** `NewGarden_Backlinks_Audit.xlsx` (7 tabs; dated 2026-11-03)
**Subject:** newgarden.com (+ plants.newgarden.com)
**Reviewed:** 2026-11-03, cross-checked against **live Semrush** and **Ahrefs** APIs.
**Verdict:** Mechanically excellent, interpretively over-stated, and built on **one tool only**. Do **not** upload the 1,646-line disavow as-is. One domain is almost certainly a false positive, ~1,000 referring domains Ahrefs sees are not in scope, and the only links that actually matter (133 exact-match) are still unreviewed.

---

## 1. Bottom line

| Question | Answer |
|---|---|
| Are the numbers real? | **Yes.** Totals match live Semrush to the row (8,086 backlinks / 2,683 domains / 7,293 follow / 793 nofollow). |
| Is the workbook internally consistent? | **Yes.** Every status count reconciles across tabs; the disavow file is clean (see §2). |
| Is it safe to upload the disavow? | **No — not yet.** False positive + single-tool blind spot + unreviewed held set (see §3). |
| Is there evidence of a real problem? | **Not in this data.** It's auto-generated scraper spam Google already discounts. The workbook says so — and is right to say "monitor, don't disavow unless GSC shows a manual action or the client confirms buying links." |
| Where's the actual risk, if any? | The **133 exact-match commercial/geo anchors** (Tab 05), which are **100% unreviewed**. Everything else is noise. |

---

## 2. What the workbook gets right (credit where due)

- **Totals are faithful to source.** Live Semrush `backlinks_overview` for newgarden.com returns total 8,086 / domains 2,683 / follows 7,293 / nofollows 793 — identical to the workbook. Authority Score 30.
- **Internal consistency is airtight.** Status counts match across Summary ↔ Referring Domain Audit ↔ All Backlinks:
  Spam(Disavow) 1,646 · Keep 848 · Held-Pending 120 · Spam-Nofollow 56 · Held-Nofollow 13 = **2,683**.
- **The disavow file is technically correct.** 1,646 `domain:` lines, **0 malformed, 0 duplicates, 0 redundant url: lines**, and every "In Disavow = Yes" domain is present. Valid Google format, well under the 100k-line limit.
- **Nofollow handling is correct.** 56 spam + 13 held domains that are nofollow-only are excluded from the disavow — right call, disavowing nofollow links achieves nothing.
- **The held set is correctly quarantined.** 120 dofollow + 13 nofollow exact-match domains = the **133** rows in Tab 05, held out of the disavow pending partner confirmation. Good instinct.
- **The headline recommendation is the correct, conservative one.** "Disavow only if Search Console shows a manual action, or the client confirms buying links. Otherwise just monitor." Keep that line and resist pressure to upload reflexively.

---

## 3. Critical findings (what to fix before anyone uploads)

### F1 — `rosih.ru` is almost certainly a FALSE POSITIVE, and it distorts the whole audit
This single domain is marked **Spam (Disavow)** with **2,536 dofollow backlinks** — 31% of *all* 8,086 backlinks and **60% of the 4,216 "spam" backlinks**. Cross-check:

| | Semrush (workbook) | Ahrefs (live) |
|---|---|---|
| Backlinks from rosih.ru | **2,536** | **3** |
| Spam flag | Spam/Disavow | **not spam** |
| Domain authority | AS 10 | DR 0.9 |
| Organic traffic / keywords | (blank) | **293 visits / ranks for 35 keywords** |
| Anchor | "(Ссылка на источник изображения)" = *"(image source link)"* | same |
| Target | plants.newgarden.com/.../Gold_Drift_Norway_Spruce | — |

What's actually happening: rosih.ru (a real Russian horticulture site with traffic and rankings) **hot-links a New Garden plant image** and each catalogue page that embeds it carries an image-source credit link. Semrush counts every embed as a separate "backlink" (2,536); Ahrefs consolidates to 3 and doesn't consider it spam.

Consequences:
- The anchor-type label **"Spam: keyword stuffed SEO sales copy" is wrong** — it's an image caption, not SEO sales copy.
- It is the **#1 anchor** in Tab 04 (31% of backlinks) — a pure artifact of one image.
- It inflates "spam backlinks" from a real ~1,680 to the stated 4,216.
- **Disavowing it cuts off image attribution from a legitimate site for zero SEO benefit** (image-source links to a plant-image URL carry ~no ranking relevance, and Ahrefs doesn't even see 2,536 of them).

**Action:** remove `domain:rosih.ru` from the disavow (or at minimum re-classify it "image hotlink — no action"), and stop letting it drive the headline counts.

### F2 — Single-tool blind spot: the audit is 100% Semrush; Ahrefs sees a different ~1,000 domains
Every row's Source/Tool = Semrush. Cross-checking the profile:

| Metric | Semrush (live) | Ahrefs (live, incl. subdomains) |
|---|---|---|
| Referring domains | **2,683** | **1,694** |
| Backlinks | 8,086 | 3,573 (57,167 all-time) |

The two indexes overlap only partially. In a 6-domain spot check, **2 domains (lydiaroyrealestate.com, allbacklinkchecker.space) don't exist in Ahrefs at all**, while Ahrefs holds live links that a Semrush-only pull can miss. A disavow built from one tool is **structurally incomplete** — it will leave untouched whatever the other tool indexes.

**Action:** if you're going to disavow at scale, merge Ahrefs referring domains into the candidate set before finalising (I can pull and de-dupe the full Ahrefs list). Otherwise accept that "1,646" is "1,646 *as Semrush sees it*," not the whole network.

### F3 — The "spam" is auto-generated scraper noise, not a targeted attack — which argues *against* disavowing
- One anchor, *"Build Powerful Website Authority with Premium SEO backlinks…"*, appears on **1,469 distinct domains** (1,488 backlinks). These are throwaway SEO-reseller/scraper sites that list thousands of domains each; New Garden just appears in their junk pages. (Ahrefs confirms these sites link out to 5,000–19,000 domains apiece.)
- **1,513 of 2,683 domains (56%) were first seen in 2026-10** — a single burst last month.
- **67% sit on Cloudflare ranges** (172.67.x = 930, 104.21.x = 880). Note: that clustering is **a Cloudflare artifact, not proof of one network** — don't read it the way you'd read a dedicated PBN host.
- This is exactly the profile Google's algorithms already ignore. Uploading 1,646 lines here is cosmetic unless there's a manual action. The workbook's own guidance agrees.

**Action:** check GSC for a manual action and watch rankings around the **Oct 2026** spike. Disavow only if either shows a real problem.

### F4 — The one part that actually matters is 100% unreviewed
Tab 05 (Exact Match Anchors) lists **133 domains** with commercial/geo anchors (e.g. "Landscape Maintenance Services Greensboro NC" / "…Winston-Salem"), split **Winston-Salem 70 · Greensboro 51 · Non-geo 12**. These are the *only* links that look deliberately built — the classic signature of a paid link-building package, and the only place genuine Penguin/manual-action risk would sit. **Both decision columns ("Partner confirmed?", "Final decision") are blank for all 133.**

Spot-check of the held domains (Ahrefs):
- `atozbookmarks.net` (DR 0.1, 6,893 out-domains, OVH 15.204.x) and `favemarks.net` (DR 0.2, spam, 5,440 out-domains, OVH 15.204.x) — **mass social-bookmarking sites on the same host.** Consistent with a cheap bookmarking-submission package, not editorial placements.
- `hometosight.com` (DR 37, not spam, Cloudflare) — a higher-authority outlier with a more editorial anchor. Treat individually.

**Action:** this is where the human/partner review belongs. Fill Tab 05 columns F & G. If the partner confirms a commissioned package, those are the links to clean up (and a vendor conversation); if not, they're low-tier and Google likely ignores them anyway.

### F5 — The "Keep" bucket (848) over-claims "genuine"
Several high-backlink "Keep" domains are scraper/stat sites, not editorial links: `sitelike.org`, `fixx.co` (207), `webmash.org` (373), `mysmallbiz.net` (274), `directoryplus.biz` (270), `powerbizdirectory.com` (93). Harmless and correctly *not* disavowed, but they aren't "genuine, branded or editorial" links — the genuine subset (eurekster, yellowpages/superpages, real notes-page citations) is smaller than 848 implies. Not an error; just don't quote "848 genuine links" to the client.

### F6 — Minor / data-quality notes
- "RD's" and "Traffic" columns are **blank by design** (Semrush's referring-domains export omits them — disclosed in the workbook). Ahrefs *does* provide both, so a merge would fill these.
- The anchor-type classifier mislabels the rosih.ru image caption as "SEO sales copy" (see F1) — a rules bug worth fixing if this template is reused.
- No Majestic Trust/Citation Flow here; if the client's prior reports cite "TF", it's a separate tool.

---

## 4. Tool reconciliation (one place)

| | Semrush (workbook + live) | Ahrefs (live) |
|---|---|---|
| Referring domains (live) | 2,683 | 1,694 |
| Backlinks (live) | 8,086 | 3,573 |
| Backlinks (all-time) | — | 57,167 |
| Site authority | AS 30 | — |
| rosih.ru backlinks | 2,536 (spam) | 3 (not spam) |
| Follow / nofollow | 7,293 / 793 | — |

The gap is the story: **the two tools disagree on ~37% of the referring-domain count and by 800× on the single biggest "spam" source.** Any disavow decision has to account for that, not pick one tool and treat it as ground truth.

---

## 5. Recommended sequence before this disavow goes anywhere

1. **Don't upload yet.** Confirm a GSC manual action exists (or that the client/partner confirms buying links). No manual action → monitor only.
2. **Pull rosih.ru out** of the disavow (false positive) and re-label the image-hotlink class.
3. **Fill Tab 05 (133 domains)** with the partner — this is the real decision, and it's the commissioned-package question.
4. **If disavowing at scale, merge Ahrefs** referring domains into the candidate list first, or acknowledge the Semrush-only blind spot in the deliverable.
5. **Baseline rankings** for the Greensboro / Winston-Salem service terms now and watch them through the Oct-2026 spam spike, so you can tell noise from a real effect.

---

*Cross-checks run live against Semrush Backlink Analytics and Ahrefs Site Explorer on 2026-11-03. Tool figures are provider estimates and differ by design; discrepancies above are reported, not reconciled away.*
