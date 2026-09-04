# 3king.cc — Backlink Plan (Anchors × Target URLs)

_Prepared September 2026. Data source: Ahrefs Site Explorer (live index, 2026-09-01).
Market: **Vietnam** (VN) — game bài / nổ hũ / bắn cá / tài xỉu casino-app portal._

> This is an SEO planning document, not legal advice. 3king.cc operates in a vertical that is
> both **YMYL/heavily spam-policed** and **subject to domain blocking in Vietnam**. The plan is built
> around those two constraints, not against them.

---

## 1. Current state — data snapshot & critical diagnosis

| Metric | Value | Read |
|---|---|---|
| Domain Rating (DR) | **19** | Low. Despite huge link counts → links are near-worthless/toxic. |
| Live backlinks | **21,672** | Volume ≠ value. |
| Live referring domains | **2,523** | Mostly spam/auto-generated. |
| All-time ref domains | 4,791 | ~2,268 already lost/churned — classic spam decay. |
| Ranking URLs | **only `/` and `/no-hu`** | Thin footprint; money verticals not built out. |
| Organic keywords | ~24, **~100% branded** | No non-brand equity captured. |
| Est. organic traffic | ~29/mo | Effectively pre-launch from an SEO standpoint. |
| Sister domain | **3kingapp.net** | Appears throughout anchors — canonical/mirror question (see §7). |

### What the anchor profile actually looks like now (the problem)

The top inbound anchors are **not** brand or keyword anchors — they are spam:

- `TELEGRAM @MASSLINKER … PUBLISH BACKLINKS YOURSELF` — 38 ref domains
- `TELEGRAM @SEO_LINKK_ORDER – SEO BACKLINKS, HOMEPAGE LINKS, CROSSLINKS` — 36
- `High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN … Buy Backlinks Online Cheap` — 23
- `…Black Hat SEO backlinks … Telegram: @seo7878` — dozens of auto-generated variants
- Fake testimonial spam referencing `SEOExpress.org`, `3kingapp.net`
- Genuine brand/topic anchors (`3king.cc`, `3king`, `chơi bắn cá online`, `PLAY ONLINE NOW`) exist but are a **small fraction**.

**Diagnostic conclusion:** the domain is carrying a large toxic/negative-SEO-style footprint. Pouring
fresh links on top without cleanup risks reinforcing an unnatural profile in a niche where Google's
spam systems are specifically tuned. **Sequence must be: (A) audit + disavow → (B) build brand/URL/
generic foundation → (C) layer partial/exact-match money anchors slowly.**

---

## 2. Target URL architecture

Only `/` and `/no-hu` exist as real targets today. A backlink plan needs a **money-page map** first —
you link to pages, and most of these need to be **built/strengthened** before they're link targets.
URL slugs follow the site's observed convention (no diacritics, hyphenated, e.g. `/no-hu`).

| # | Target URL | Vertical (VN) | Primary intent | Priority | Status |
|---|---|---|---|---|---|
| T1 | `https://3king.cc/` | Brand / cổng game | Navigational + brand | **Core** | Live |
| T2 | `https://3king.cc/no-hu` | Nổ hũ (jackpot slots) | Transactional | **High** | Live |
| T3 | `https://3king.cc/ban-ca` | Bắn cá (fish shooting) | Transactional | **High** | Build |
| T4 | `https://3king.cc/tai-xiu` | Tài xỉu (sic bo) | Transactional | **High** | Build |
| T5 | `https://3king.cc/game-bai` | Game bài đổi thưởng (card games) | Transactional | **High** | Build |
| T6 | `https://3king.cc/da-ga` | Đá gà (cockfight betting) | Transactional | Med | Build |
| T7 | `https://3king.cc/the-thao` | Thể thao / cá cược bóng đá | Transactional | Med | Build |
| T8 | `https://3king.cc/casino` | Casino trực tuyến / live | Transactional | Med | Build |
| T9 | `https://3king.cc/xo-so` (or `/lo-de`) | Xổ số / lô đề | Transactional | Low-Med | Build |
| T10 | `https://3king.cc/tai-app` (or `/tai-3king`) | App download (APK/iOS) | Transactional | **High** | Build |
| T11 | `https://3king.cc/khuyen-mai` | Khuyến mãi / giftcode | Commercial | Med | Build |
| T12 | `https://3king.cc/huong-dan/*` | Guides/how-to (blog) | Informational | Support | Build |

**Rule:** never point external links at a page that isn't finished and indexable. Build T3–T11 as real
silo pages (unique content, internal links from `/` and each other) *before* they enter the link plan.

---

## 3. Anchor-text strategy (the core of the ask)

### 3.1 Governing principles for this domain

1. **Brand-led, not exact-match-led.** The niche punishes over-optimized commercial anchors, and this
   domain already looks manipulated. Keep exact-match money anchors a small, capped slice.
2. **Diversify heavily.** Hundreds of near-identical anchors are a footprint. Rotate variants.
3. **Match anchor to intent & page.** Money anchors only to money pages; brand/generic to homepage.
4. **Vietnamese-first.** Anchors should read like real VN player language, with a minority of
   naked-URL and English ("PLAY NOW") for natural noise.
5. **Blocking-resilient (see §7).** Favour **brand + naked-URL** anchors that survive a domain swap;
   avoid tying all equity to exact-match anchors on one blockable URL.

### 3.2 Target anchor distribution (for NEW links only)

| Anchor class | Target % | Example anchors | Points to |
|---|---|---|---|
| **Branded** | **35–40%** | `3king`, `3king game`, `3king games`, `nhà cái 3king`, `cổng game 3king`, `3king app`, `3king casino` | Mostly T1; some to relevant deep pages |
| **Naked URL** | **15–20%** | `3king.cc`, `https://3king.cc`, `www.3king.cc`, `3king.cc/no-hu` | T1 + deep pages |
| **Generic / natural** | **15–20%** | `tại đây`, `xem thêm`, `truy cập`, `trang chủ`, `link vào`, `nhấn vào đây`, `chi tiết`, `website`, `tải game` | T1, T10 |
| **Brand + keyword (partial)** | **12–18%** | `nổ hũ 3king`, `bắn cá 3king`, `tài xỉu 3king`, `game bài 3king`, `tải game 3king` | Matching deep page |
| **Exact-match money** | **≤ 8–10% total** (capped) | `nổ hũ đổi thưởng`, `bắn cá đổi thưởng`, `tài xỉu online`, `game bài đổi thưởng` | Matching deep page only |
| **Compound/co-occurrence & images** | remainder | long-tail phrases, image/alt links, `[image]` | mixed |

> Enforce a **per-page exact-match cap**: no single money page should have >15–20% of *its* anchors as
> exact-match. Track the running blend monthly and correct drift.

### 3.3 Anchor pools per target URL

Rotate within each pool; never reuse the same anchor >2–3× per 100 links.

**T1 — Homepage `/` (brand hub):**
`3king` · `3king game` · `3king games` · `nhà cái 3king` · `cổng game 3king` · `3king casino` ·
`3king.cc` · `https://3king.cc` · `trang chủ 3king` · `tại đây` · `xem thêm` · `truy cập 3king` ·
`link vào 3king` · `3king online`

**T2 — Nổ hũ `/no-hu`:**
`nổ hũ 3king` · `game nổ hũ 3king` · `nổ hũ` · `nổ hũ đổi thưởng` · `game nổ hũ đổi thưởng` ·
`nổ hũ online` · `3king.cc/no-hu` · `chơi nổ hũ tại đây`

**T3 — Bắn cá `/ban-ca`:**
`bắn cá 3king` · `game bắn cá 3king` · `bắn cá` · `bắn cá đổi thưởng` · `chơi bắn cá online` ·
`game bắn cá online` · `bắn cá 3king.cc`

**T4 — Tài xỉu `/tai-xiu`:**
`tài xỉu 3king` · `tài xỉu` · `tài xỉu online` · `game tài xỉu` · `tài xỉu đổi thưởng` ·
`chơi tài xỉu 3king`

**T5 — Game bài `/game-bai`:**
`game bài 3king` · `game bài đổi thưởng` · `đánh bài online` · `game đánh bài đổi thưởng` ·
`game bài 3king.cc` · `cổng game bài 3king`

**T6 — Đá gà `/da-ga`:** `đá gà 3king` · `đá gà trực tuyến` · `đá gà online` · `xem đá gà 3king`

**T7 — Thể thao `/the-thao`:** `thể thao 3king` · `cá cược thể thao` · `cá độ bóng đá` · `kèo bóng đá 3king`

**T8 — Casino `/casino`:** `casino 3king` · `casino trực tuyến` · `casino online` · `sòng bài trực tuyến 3king`

**T9 — Xổ số `/xo-so`:** `xổ số 3king` · `lô đề online` · `xổ số online` · `quay số 3king`

**T10 — App download `/tai-app`:**
`tải 3king` · `tải app 3king` · `tải game 3king` · `link tải 3king` · `tải 3king apk` ·
`tải 3king ios` · `3king app` · `tải game`

**T11 — Khuyến mãi `/khuyen-mai`:**
`khuyến mãi 3king` · `giftcode 3king` · `khuyến mãi nạp đầu 3king` · `ưu đãi 3king`

**T12 — Guides `/huong-dan/*`:**
`hướng dẫn 3king` · `cách chơi nổ hũ` · `cách chơi tài xỉu` · `mẹo bắn cá` · informational long-tail
(these earn the *natural* generic/branded links that balance the profile).

---

## 4. Master anchor → target mapping (deliverable)

Blended plan for a **90-day / ~180 new-link** cycle (adjust volume to budget). Percentages follow §3.2.

| Anchor class | Example anchors (rotate) | Target URL(s) | % of new links | ~Links / 90d |
|---|---|---|---|---|
| Branded | `3king`, `3king game`, `nhà cái 3king`, `cổng game 3king` | T1 (+ deep) | 37% | ~67 |
| Naked URL | `3king.cc`, `https://3king.cc`, `3king.cc/no-hu` | T1, T2, T10 | 17% | ~31 |
| Generic | `tại đây`, `xem thêm`, `truy cập`, `link vào` | T1, T10, T12 | 17% | ~31 |
| Partial (brand+kw) | `nổ hũ 3king`, `bắn cá 3king`, `tài xỉu 3king`, `tải game 3king` | T2–T5, T10 | 15% | ~27 |
| Exact money | `nổ hũ đổi thưởng`, `bắn cá đổi thưởng`, `game bài đổi thưởng` | T2–T5 (matched) | 9% | ~16 |
| Long-tail / image | co-occurrence phrases, alt-text, `[img]` | T12 + mixed | 5% | ~9 |

Per-vertical split of the **partial + exact** money slice (~43 links) — weight to priority verticals:
Nổ hũ ~30% · Bắn cá ~20% · Tài xỉu ~18% · Game bài ~17% · App download ~15% (rest spread to T6–T9/T11).

---

## 5. Link-source mix, quality bar & velocity

Volume is not the constraint here (they have 21k links) — **quality and relevance** are. Skew to fewer,
better, topically-relevant links.

### Tiers (link directly to money/brand pages)

- **Tier 1 — Editorial / niche-relevant (highest value, ~40% of effort):**
  Guest posts & niche edits on **Vietnamese/Asian gaming, sports, esports, tech, entertainment and
  review** sites with *real organic traffic* and *editorial review*. Vet on: real VN traffic (not just
  DR), topical relevance, clean outbound profile. These carry the partial/exact money anchors.
- **Tier 2 — Foundational / branded (safe volume, ~40%):**
  Branded profiles, Web 2.0 properties, social/business profiles, curated directories, VN forums
  (with brand/URL/generic anchors). Balances the profile and builds entity signals.
- **Tier 3 — Supportive (~20%):**
  Contextual mentions, image links, syndication, tiered links pointing at Tier-1 assets (not at the
  money site) to strengthen them without adding raw risk to 3king.cc.

### Quality bar (hard rules)

- No more Telegram/"buy cheap PBN"/auto-blast sources — that's what created the current mess.
- Prefer VN-language pages; check the referring page actually gets search traffic.
- Cap dofollow exact-match; mix in nofollow/UGC/sponsored for a natural follow ratio.
- Diversify referring IPs, CMS footprints, and anchor variants.

### Velocity

- Ramp gradually: e.g. **~40 → 60 → 80 links/month** across the cycle, brand/URL-heavy first,
  money anchors introduced only from month 2 once foundation + disavow are in place.
- Keep velocity smooth; avoid spikes on any single money anchor.

---

## 6. Cleanup / disavow (do this first)

1. Export full referring domains + anchors; flag `is_spam=true` and the obvious spam-anchor clusters
   (Telegram/@handles, "buy backlinks", "black hat SEO", fake testimonials).
2. Build a **disavow file at domain level** for those clusters; submit in Google Search Console.
3. Re-audit monthly — spam link injection in this niche is ongoing (possible negative SEO), so disavow
   is a **maintenance process**, not a one-off.
4. Only after the foundation build begins should new money anchors be layered on (§3.1 sequence).

---

## 7. Blocking resilience & the 3kingapp.net question (niche-specific)

Vietnam blocks gambling domains (DNS/IP). Two implications for the **link plan specifically**:

- **Weight brand + naked-URL anchors.** If `3king.cc` is blocked and you move to a new domain, links
  built to the **brand** and to a redirectable **homepage URL** transfer via 301 far better than a pile
  of exact-match anchors deep-linked to one blockable path. This is a deliberate reason the exact-match
  slice is capped at ~9%.
- **Resolve the canonical domain now.** `3kingapp.net` is entangled across the anchor profile. Decide
  **one canonical money domain** and 301 the other into it (page-by-page), so link equity consolidates
  instead of splitting/cannibalizing. Do not run both as independent SEO targets.
- **Keep a "link inventory" you can re-point.** Track every Tier-1 placement so, on a domain swap, you
  can update the highest-value links to the new domain rather than relying solely on 301s.

---

## 8. Phased rollout & KPIs

| Phase | Weeks | Focus | Anchor emphasis |
|---|---|---|---|
| 0 — Audit & disavow | 1–2 | Toxic cleanup, canonical decision (3king.cc vs 3kingapp.net) | — |
| 1 — Foundation | 3–6 | Build T3–T11 pages; Tier-2 branded/URL links | Brand / URL / generic |
| 2 — Authority | 7–10 | Tier-1 guest posts/niche edits to T1–T5, T10 | + partial (brand+kw) |
| 3 — Money push | 11–13+ | Controlled exact-match to matured money pages | + exact (capped) |

**KPIs:** DR trend; **clean** ref-domains gained (spam excluded); non-branded VN keywords in top 100 →
top 10 for nổ hũ / bắn cá / tài xỉu / game bài; money-page (T2–T5, T10) traffic; anchor-blend adherence
to §3.2; disavowed-domain count trending down (health check).

---

## 9. Critical cautions

- **Don't scale links onto an unclean profile** — cleanup precedes build, or you compound the footprint.
- **DR is not a target** — clean, relevant, traffic-bearing links are; ignore "DA50 PBN" sellers.
- **Exact-match discipline is the whole game** in this niche — the failure mode here is over-optimization,
  and this domain is already carrying an over-optimized/spam footprint.
- **Resolve 3king.cc vs 3kingapp.net before spending** — otherwise you fund two diluted profiles.

_All backlink metrics above are from Ahrefs' live index (2026-09-01). Vietnamese search-volume/vertical
priorities are informed by the domain's own ranking data plus market knowledge; validate exact volumes
in Ahrefs Keywords Explorer (VN) before finalizing per-vertical link weighting._

---

## 10. Execution log & monthly build

> **Policy note:** Disavow is intentionally **not** used — the vertical runs on spam and the toxic
> profile is treated as baseline cost. Naturalness is managed on the *outbound build side* (anchor blend
> discipline, page matching, diversification), not by cleaning inbound spam.

### Month 1 (built) — 7 links

| Anchor | Target | Class |
|---|---|---|
| 3king | `/` | Branded |
| 3King | `/` | Branded |
| 3king game | `/` | Branded |
| game nổ hũ | `/no-hu` | Exact money |
| chơi bắn cá online | `/ban-ca` | Exact money |
| bắn cá online | `/ban-ca` | Exact money |
| app tài xỉu online | `/` | Money (mismatched → homepage) |

**Issues to correct:** (a) 0 naked-URL and 0 generic anchors; (b) `/ban-ca` took 2 exact-match anchors
in one month (concentration); (c) `app tài xỉu online` pointed at `/` — no `/tai-xiu` page existed.

### Month 2 (planned) — the critical 7 (ranking-focused)

**Principle: concentration over coverage.** With only 7 links, spreading one link per page moves
nothing. Stack them on the pages closest to ranking to push near-rankers into the top 10. Weighting is
by *probability of converting an existing near-ranking*, not by covering every vertical.

| # | Priority | Anchor | Target URL | Class | Why it moves rankings |
|---|---|---|---|---|---|
| 1 | ★★★ | `nổ hũ 3king` | `https://3king.cc/no-hu` | Partial | Relevance to the proven near-ranking page |
| 2 | ★★★ | `nổ hũ đổi thưởng` | `https://3king.cc/no-hu` | Exact | Commercial intent, new variant (≠ M1 "game nổ hũ") |
| 3 | ★★★ | `3king.cc/no-hu` | `https://3king.cc/no-hu` | Naked URL | Completes a natural mini-profile; passes authority |
| 4 | ★★ | `bắn cá 3king` | `https://3king.cc/ban-ca` | Partial | Diversifies /ban-ca off pure exact; adds authority |
| 5 | ★★ | `bắn cá online 3king` | `https://3king.cc/ban-ca` | Partial | 2nd relevance signal without a raw exact |
| 6 | ★★ | `nhà cái 3king` | `https://3king.cc/` | Branded | Domain/entity authority → lifts all deep pages |
| 7 | ★★ | `3king.cc/ban-ca` | `https://3king.cc/ban-ca` | Naked URL | `/tai-xiu` is a dead URL (404) → reallocated to the proven /ban-ca page |

> **Note:** `/tai-xiu` returns no working page (confirmed 404), so the original #7 (`tài xỉu đổi thưởng`
> → `/tai-xiu`) is **pulled** — never link to a non-200 URL. The slot moves to `/ban-ca` as a naked-URL
> anchor to balance that page's profile.

**Concentration:** 7 links → 3 confirmed-live URLs (`/no-hu` ×3, `/ban-ca` ×3, `/` ×1).
**Blend:** Partial 3 · Exact 1 · URL 2 · Branded 1 — relevance-rich, not exact-stacked. No Month-1
anchor+URL pair reused.

**Why these vs. spreading wider:** `/no-hu` already exists *and* ranks (branded) → cheapest page to push
over the top-10 line, so it gets the heaviest stack. `/ban-ca` already took 2 exacts in M1, so it gets
partials (authority + diversity, not over-optimization). One homepage brand link compounds into deep
pages via internal equity. `/game-bai`, `/tai-app` and generic filler are **deliberately deferred** —
a single link each would rank nothing; add them after `/no-hu` and `/ban-ca` are pushed.

**Page-build backlog (blocking future links):** `/tai-xiu` (404 — highest-volume vertical, top
priority), `/game-bai`, `/tai-app`, `/khuyen-mai`. Each must return **200 + be indexable with real
content and internal links** before it can be a link target. Verify every target URL returns 200
before placement.

**Rolling rule:** once `/no-hu`/`/ban-ca` reach page 1, rotate the stack to the next vertical rather than
piling more exact anchors on a won page; keep cumulative exact-match trending down with brand/URL/generic.
