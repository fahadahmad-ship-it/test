# newgarden.com — Referring Domain Profile & Link History Review

**Client:** New Garden Landscaping & Nursery — https://newgarden.com/
**Review date:** 2026-11-02
**Data source:** Ahrefs Site Explorer (subdomains mode)
**Scope of question:** (1) review referring-domain profile and link history; (2) confirm whether paid-anchor links were commissioned; (3) confirm whether reporting shows a manual action; (4) recommend a disavow only if warranted.

---

## Bottom line (TL;DR)

- The historic profile is that of a legitimate local nursery/landscaping business. Since **~April 2026, and explosively from late September 2026**, the profile has been flooded with **auto-generated spam / link-scheme domains** (DR 0, zero-traffic `*.shop` and `*.xyz` farms) and **promotional spam anchors** that name the domain ("Premium SEO Backlinks", "PBN Network Service", "Niche Edit Links", "guest posts, contextual backlinks", "TF boost packages").
- **Were paid-anchor links commissioned? — Cannot be confirmed from the link data, and the footprint argues *against* a bought campaign.** The pattern (hundreds of DR-0 domains spun up on a single day, one nofollow link each, zero traffic) is the signature of **unsolicited spam / possible negative SEO**, not a paid link buy. This must be confirmed with the client/any agency — only they know if links were purchased.
- **Does reporting show a manual action? — Not determinable from the available tools, and no tool here reports one.** Manual actions live only in **Google Search Console → Security & Manual Actions → Manual actions**; they are not exposed by Ahrefs or the GSC performance API. The traffic history is **not consistent** with a link-based manual action tied to the spam (see timing below).
- **Disavow recommendation: NOT warranted at this time.** No confirmed manual action; the spam looks unsolicited/auto-generated (which Google discounts algorithmically); and the main traffic loss *predates* the spam. Recommended action is to **confirm two facts first** (client link-buying history + GSC manual-action status) and only then disavow if either comes back positive.

---

## 1. Referring-domain profile & link history

**Headline metrics (live, 2026-11-02):**

| Metric | Value |
|---|---|
| Domain Rating (DR) | 32 |
| Live backlinks | 3,572 |
| Live referring domains | 1,693 |
| All-time backlinks | 57,155 |
| All-time referring domains | 6,476 |

**Legitimate core (pre-2026):** Genuine citations and editorial/local links consistent with a real garden centre — e.g. `audubon.org`, `vt.edu`, `umn.edu`, `extension.org`, `apartmenttherapy.com`, `sfgate.com`, `gardenersworld.com`, `gardeningknowhow.com`, Google Business/MapQuest/YellowPages/BBB citations, plus a large legitimate `plants.newgarden.com` plant-catalogue footprint. Brand/URL anchors ("New Garden Landscaping & Nursery", "newgarden.com", "www.newgarden.com") dominate the organic history. This part of the profile is healthy and should **not** be touched.

**The anomaly — a referring-domain explosion:**

Referring domains were stable at **~450–530 for all of 2024–early 2026**, then:

| Month | Ref. domains |
|---|---|
| 2026-02 | 470 |
| 2026-03 | 416 |
| 2026-04 | 412 |
| 2026-05 | 566 |
| 2026-06 | 676 |
| 2026-07 | 823 |
| 2026-08 | 880 |
| **2026-09** | **1,779** |
| 2026-10 | 1,692 |
| 2026-11 | 1,693 |

That is roughly a **4x jump (≈ +1,200 referring domains)** over the long-run baseline, almost entirely new spam domains. A single automated burst on **2026-09-28 / 2026-09-29** added dozens of same-day-registered link-farm domains, e.g. `*linkpro.shop`, `serp*.shop`, `seo*.shop`, `rank*.shop`, `index*.shop`, `boldranklab.shop`, `truelinkpro.shop`, plus numeric `########.xyz` domains — nearly all **DR 0, traffic 0, one link each, mostly nofollow**.

---

## 2. Were paid-anchor links commissioned?

**Finding: No evidence in the backlink data that the client commissioned paid-anchor links — and the footprint is more consistent with unsolicited spam / negative SEO than with a paid campaign.**

The anchor-text report contains overt link-scheme/paid-service language that *names the domain*, all flagged by Ahrefs as spam (`is_spam = true`) and all first seen in 2026:

| Anchor text (abridged) | Ref. domains | Dofollow | First seen |
|---|---|---|---|
| "I remember when newgarden.com was lost in the depths of Google… SEOExpress.org…" (spam testimonial) | 604 | 0 | 2026-04-19 |
| "Build Powerful Website Authority with Premium SEO Backlinks newgarden.com" | 244 | 244 | 2026-09-17 |
| "newgarden.com works with travel brands… TF boost packages, automation tools and profile links…" | 219 | 0 | 2026-09-27 |
| "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service newgarden.com…" | 45 | 47 | 2026-08-04 |
| "Boost newgarden.com using premium guest posts, contextual backlinks…" | 45 | 0 | 2026-06-19 |
| "Proven Niche Edit Links for newgarden.com to Raise Domain Rating…" | 11 | 11 | 2026-09-11 |

**Two readings, and why the evidence favours the second:**

- *If links had been bought,* these could be the money anchors of that campaign. But a genuine paid campaign typically yields cleaner commercial/keyword anchors on mid-tier blogs — not DR-0 `.shop` farms created en masse in one day.
- *More consistent with the data:* automated spam networks scrape a domain and auto-generate "rank newgarden.com" / "buy backlinks for newgarden.com" listings. The same-day `.shop`/`.xyz` burst, DR 0, zero traffic, single nofollow link each is the classic fingerprint of **auto-generated spam or negative SEO**, which the site owner did not order.

**→ Action required to actually answer this question:** ask the client and any current/former SEO agency, in writing, whether they (or anyone on their behalf) ever purchased links, guest posts, "niche edits", PBN links, or "DR/TF boost" packages. The link data alone cannot establish intent/commissioning; it can only show the footprint above. Treat the named anchors as the concrete list to put in front of them.

---

## 3. Does reporting show a manual action?

**Finding: Not determinable from any tool used here, and none of the available tools surface a manual action.**

- A Google **manual action** is reported **only** inside Google Search Console → **Security & Manual Actions → Manual actions**. It is **not** exposed by Ahrefs, nor by the GSC Search-Analytics/performance API. So neither this review nor any connected reporting tool here can "see" a manual action — it has to be read directly in the property's GSC by someone with access.
- **Proxy signal from the traffic curve argues against a link-based manual penalty tied to the spam.** Organic traffic peaked at ~15,900/mo in **May 2025**, then fell ~88% to a trough of ~1,830 by **Jan 2026** — *before* the spam links appeared. It then partially recovered (to ~6,940 in Jun 2026) *while* the spam was already arriving, and has softened again since Sep 2026. A manual action for unnatural links would normally produce a sharp drop **after** the links appeared; here the biggest decline **predates** them, pointing to an **algorithmic / core-update or on-site cause**, not a link penalty.

**→ Action required:** have someone with GSC access confirm the Manual Actions report (and the Security Issues report) directly, and screenshot it for the file. That is the only authoritative source.

---

## 4. Disavow recommendation

**Recommendation: Do NOT file a disavow at this time.** A disavow is not warranted on the current evidence, for three reasons:

1. **No confirmed manual action.** Google's own guidance (and repeated statements from its Search team) is that the disavow tool is for cases where you either have a **manual action for unnatural links** or a **strong, specific reason** to believe spammy/paid links *you are responsible for* will trigger one. Neither is established here.
2. **The spam looks unsolicited / auto-generated.** Google states it **ignores the vast majority of spammy links algorithmically**, and negative-SEO-style junk (DR-0 `.shop`/`.xyz` farms, nofollow, zero traffic) is exactly what its systems are built to discount. Disavowing it usually changes nothing.
3. **The traffic loss doesn't line up with the links.** The major decline predates the spam, so disavowing these domains is unlikely to recover the lost traffic — and a careless disavow can **remove value from legitimate links** if the file is too broad.

**Decision rule — disavow only if one of these turns out true:**

- **A)** GSC shows a **manual action** citing unnatural inbound links (partial or site-wide); **or**
- **B)** The client/agency **confirms they purchased** the links in the spam anchors above (i.e. they are self-made and could attract a manual action).

**If A or B is confirmed,** prepare a **targeted** disavow file at the **domain level** covering only the identified spam/paid sources — e.g. the `*.shop` / `*.xyz` link-farm cluster and the paid-service-anchor domains — while explicitly **excluding** the legitimate core (educational, editorial, local-citation, and `plants.newgarden.com` catalogue links). Keep the file conservative and documented.

**If neither is confirmed (most likely),** do **not** disavow. Instead: document the finding, **monitor** referring-domain growth monthly for continued negative-SEO activity, and keep the evidence on file so a disavow can be filed quickly *if* a manual action later appears.

---

## 5. Recommended next steps (in order)

1. **Check GSC Manual Actions + Security Issues** directly (authoritative answer to Q3). Screenshot for the file.
2. **Get written confirmation** from client + any SEO vendor on whether links were ever bought (authoritative answer to Q2).
3. **Hold the disavow** unless step 1 or 2 comes back positive; if it does, file a **targeted domain-level** disavow of the spam/paid cluster only.
4. **Investigate the real traffic driver:** the Sep 2025 → Jan 2026 decline predates the spam and is the bigger business problem — review core-update dates, on-site/technical changes, and ranking losses for that window separately from the link question.
5. **Monitor** referring domains monthly for ongoing spam injection.

---

### Caveats
- All link/traffic figures are Ahrefs estimates (crawl-based); exact live counts fluctuate. `is_spam` is Ahrefs' classification, not Google's.
- "Commissioned" and "manual action" are both questions the available data **cannot fully close** — they require the client's own records and GSC access, as noted above. This review flags the evidence and the exact items to verify rather than asserting a conclusion the data does not support.
