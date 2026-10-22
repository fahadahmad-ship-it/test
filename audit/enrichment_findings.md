# Controlled Comfort — live-data enrichment (Semrush, pulled 2026-10-22)

Enriches the Tab 08 assessment with live Semrush data. **Verdict is unchanged: all 56 → Held
(Pending Partner/supplier).** But the live pull adds three things that matter: the links are
dofollow, the problem is far bigger than 56, and a couple of data points in the brief don't
reconcile against the live index.

> **Ahrefs API units are exhausted (0 left)** at pull time — the exact situation the playbook
> anticipates ("our Ahrefs API units are often exhausted; the client pulls these"). So the
> Ahrefs cross-check (per-domain DR, the live-page HTTP map, extra discovery) and per-domain
> organic traffic/keywords must come from a **client-supplied Ahrefs CSV export**. Everything
> below is Semrush.

## 1. Profile recon (controlledcomfort.com, root domain)
| Metric | Value |
|---|---|
| Total backlinks | 5,147 |
| Referring domains | **2,440** |
| Authority Score | 21 |
| Dofollow links | 4,711 (≈91%) |
| Nofollow links | 435 |
| Referring IPs / class-C | 2,393 / 657 |

The brief/Tab 08 scopes to **56** referring domains. The live profile is **2,440**. Tab 08 is
a *recent slice*, not the whole profile.

## 2. The 56 are the tip of a large, sustained money-page link campaign
Pulling backlinks for the two deep targets directly (cheap, targeted queries) shows the same
directory/bookmark/article template stretching far beyond the 56:

- **Velocity is explosive and current.** The 1,000 most-recently-seen referring domains span
  just **13.7 days** (2026-10-08 → 2026-10-22) — roughly **70+ new referring domains per day**,
  right now. The brief's 56 (first seen late Aug–early Sep) are buried thousands of rows deep.
- **The campaign runs ~18 months.** Links to `/services/air-conditioning` go back to
  **2025-05-04**; links to `/services/heating` to **2025-11-27**. This is an ongoing program,
  not a one-off 56-domain burst.
- **Dozens more same-template domains, not in the brief**, surfaced in just two partial page
  pulls — e.g. heating: sharedbookmark.net, favemarks.net, toplocalguide.org, 1800listings.co,
  wizarddirectory.com, optimadirectory.com, atozbusinesslistings.com; AC: expertschoice.net,
  officialdirectory.co, webdb.co, a2zdirectory.us, imeebo.net, directopedia.us, safewebsitez.com,
  linkroo.org, submitit.co, masterwebdirectory.net, companywebsitelist.com, and many more.
- **Many brief domains show TWO placements** — a ~Dec 2025/Jan 2026 listing *and* an Aug/Sep
  2026 one (e.g. topbizdir.com, zynatee.com, listingcenter.org, easybusinessdirect.com,
  directoryology.com). So the brief's "first seen Aug–Sep 2026" is the *second* wave; the domain
  was already linking months earlier.

**Implication:** when the supplier conversation is done, the disavow should be scoped to the
**whole money-page directory/bookmark footprint**, not just these 56. A full-profile audit
(all 2,440 RDs) is the right next job — Tab 08 under-counts the problem by a wide margin.

## 3. Link characteristics (sampled, both deep pages)
- **Dofollow.** Every sampled deep-page link is `nofollow=false` (one exception: hvacfirms.com
  is nofollow). So these **pass equity** — meaning any of the 56 the supplier did *not*
  commission is a genuine `Spam (Disavow)`, not a nofollow "no action" case.
- **Live.** HTTP 200 across the sample (a few `0` = not freshly crawled).
- **Zero linking-page authority.** `page_score` = 0 on essentially every listing page.
- **Classic paid-directory template.** Each listing emits multiple anchors to the same target:
  the exact-match commercial one ("Air Conditioning Repair Service Omaha NE") **plus** "Visit
  Website" **plus** a branded "controlledcomfort.com". That tri-anchor listing shape is what a
  commissioned directory-submission package looks like — reinforcing *hold and ask the supplier*.

## 4. Two discrepancies to reconcile (don't treat the brief as exact)
1. **Brief dates vs Semrush dates differ by ~2–4 weeks.** e.g. topbizdir.com Semrush first_seen
   ≈ 2026-08-09 vs brief 2026-09-08. Expected for a Semrush *estimate* — fine, but the Tab 08
   "First seen" column should not be quoted as precise.
2. **The brief's 17 AC domains did not surface in the live `/services/air-conditioning` pull.**
   The AC-page link set is real and large, but it's a *different* set of directory hosts than the
   brief's 17. Most likely cause: a **trailing-slash target variant** — listique.org's heating
   link points at `/services/heating/` (with slash) and only appeared via a per-domain filter,
   not the no-slash URL pull. Before finalising, reconcile each of the 56 against the live index
   (exact target URL incl. trailing slash, and confirm the link still resolves).

## 5. Authority Score / Keep check for the 56
Per-domain Semrush AS was **not** pulled for all 56 individually (the profile's extreme velocity
buries them past ~offset 3,000, making bulk sorted pulls very unit-expensive; the two 1,000-row
pulls already cost 120k units for no usable rows). Based on the evidence that *was* gathered —
linking-page authority 0 across the sample, thin/late indexation, uniform directory template —
**none of the 56 reads as a genuine AS≥20 site that rule 2 would flip to `Keep`.** To confirm
belt-and-suspenders, pull per-domain AS from the client's Ahrefs CSV (DR) or a scoped Semrush
`backlinks_overview` per domain; cheap per call, just 56 of them.

## Net effect on the deliverable
- Status of all 56: **Held (Pending Partner/supplier)** — unchanged. Nothing is disavowed yet.
- `disavow_controlledcomfort.txt` stays **0 active lines**; the 56 remain commented/pending.
- New: the links are **dofollow**, so post-confirmation non-commissioned ones are real disavow
  candidates; and the real remediation scope is **far larger than 56** (full-profile audit).
- Blocked on the supplier (commissioned?) and the client (Ahrefs CSV; existing GSC file?).
