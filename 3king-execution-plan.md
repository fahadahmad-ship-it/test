# 3king.cc — Critical Execution Plan
Supersedes the action items in the audit, keyword gap and link plan.
All figures verified against live Ahrefs/Semrush, 2 Oct 2026.

**Baseline to beat: 19 organic visits/month. 3 ranking keywords (Semrush).
All brand. 2,683 referring domains. DR 19.**

---

## 0. THE TWO QUESTIONS THAT GATE EVERYTHING

Neither costs money. Both change the plan materially. **Answer before any spend.**

### Q1 — Who controls the other 3king domains?

Verified: `3king.cc` links out to **3king.win (2,755 dofollow)**, 3king.app
(2,557), .game, .live, .dev, .online, 3kinggames.net, 3kingslot.com.
`3king-game-mobile.com` links out to **3king.win and nothing else**.
`3king-game.com` (DR 0) holds **#1** on the brand SERP.

| If… | Then |
|---|---|
| **Same operator** | 3king.cc is a satellite. Stop competing internally, consolidate onto **3king.win** (DR 56, built 2019, real app-download anchor history, currently 0 VN keywords). Links 2–4 are waste. |
| **Separate parties** | The brand SERP is genuinely contested. Links 2–4 are justified and the entity work becomes urgent. |

**Owner: client. Cost: one email. This is worth more than the entire link budget.**

### Q2 — Is the "tặng 30k" promotion still live?

Link 3 targets it. If the offer is expired, you would be buying a permanent link
to a dead page. **Owner: client. Cost: zero.**

---

## 1. RECOVER THE MONEY (Week 1, parallel, costs nothing)

541 placements billed. **17 verified as real links** to 3king.cc. The client's own
delivery CSV is the evidence: ~500 rows returned `Skip to content` / `#content`
as the "verified anchor/target", meaning no link was found on the page.

Issue a formal recovery demand for the ~524 undelivered placements.

**This is the highest-ROI action in this document and involves no SEO.**

---

## 2. PHASE 1 — ON-PAGE (Week 1–2, blocking)

The 5 links cannot be placed first. 4 of 5 target pages are mis-targeted against
their keyword. Evidence is the live page titles:

| Page | Current title | Problem |
|---|---|---|
| `/ban-ca` | "Bắn cá online – Chơi bắn cá trực tuyến **miễn phí** HOT nhất" | Says **free**; keyword is **đổi thưởng** (real-money). Opposite intent. |
| `/` | "3King – Game Đổi Thưởng Nhận Tiền Thật Uy Tín" | No `tải`/APK/Android/iOS — cannot serve download intent |
| `/su-kien-khuyen-mai` | "Sự kiện khuyến mãi – Đăng ký 3King nhận ngay ưu đãi" | No "30k" anywhere |
| `/thong-tin/bi-quyet-no-hu-thang-dam` | "Bí quyết nổ hũ thắng đậm – Cách tiếp cận khác biệt" | `cách chơi` absent |

### Tasks

| # | Task | Page | Done when |
|---|---|---|---|
| 1.1 | Retitle + rewrite around `game bắn cá đổi thưởng`; demote "miễn phí" | `/ban-ca` | "đổi thưởng" in title, H1, first 100 words |
| 1.2 | **Build** a download page | **`/tai-app`** (new) | APK + iOS, version no., changelog, screenshots, FAQ schema, 1,000+ words VN |
| 1.3 | Add "tặng 30k" to title/H1/body — **only if Q2 confirms live** | `/su-kien-khuyen-mai` | Offer named explicitly |
| 1.4 | Add `cách chơi nổ hũ` as H2 + in intro | `/thong-tin/bi-quyet-no-hu-thang-dam` | Phrase present verbatim |
| 1.5 | Confirm `/` carries brand + category in title and H1 | `/` | Already passes — no change |

**`/tai-app` is the only genuine architecture gap.** The clone beats you on
download intent because it has `/tai-ngay-2/` and you have nothing.

---

## 3. PHASE 2 — INTERNAL EQUITY (Week 2, costs nothing)

The site has ~90 URLs. **~35 real Vietnamese articles sit at UR 4.5 with zero
external links and almost no internal equity.** Six competitor-review pages
(`/thong-tin/789-club`, `/789club-tai-xiu`, `/789-no-hu`, `/789-game`, `/79king`,
`/79king-game-bai`) sit at **UR 0**.

| # | Task | Why |
|---|---|---|
| 2.1 | Noindex/delete the ~25 UR-0 dead URLs: `/su-kien/*` event posts (incl. mojibake slugs `hot-ng-hng-ngy-1-yelwe-tbk7p`, `s1ua86x2ntx8939unk8v5l285qc9kq`), `/new-page`, `/su-kien-khuyen-mai-1`, `/jackpot`, `/hoat-dong-hang-ngay` | They absorb internal PageRank and return nothing |
| 2.2 | Canonicalise `/su-kien/` → `/su-kien`; robots-block `?offset=`, `?format=rss` | Crawl waste |
| 2.3 | In-body contextual links from `/` to `/tai-app`, `/ban-ca`, `/su-kien-khuyen-mai` — first viewport, **not footer** | Squarespace sitewide footer links are heavily discounted |
| 2.4 | `/tai-app` ⇄ `/su-kien-khuyen-mai` reciprocal | Download + bonus is one user journey; the clone splits them across two URLs |
| 2.5 | Link the 35 `/thong-tin/` articles into `/no-hu` and `/ban-ca` contextually | Activates an existing, unused asset |
| 2.6 | Put `/tai-app` in main nav | Every link target ≤1 click from `/` |

**Phase 2 is free and may outperform all five links.**

---

## 4. PHASE 3 — THE 5 LINKS (Week 3+, after Phases 1–2)

| # | Keyword (Semrush) | Vol | KD | Full target URL | Anchor | Status |
|---|---|---|---|---|---|---|
| 1 | game bắn cá đổi thưởng | 8,100 | 49 | `https://3king.cc/ban-ca` | `game bắn cá đổi thưởng 3King` | After 1.1 |
| 2 | 3king | 9,900 | 70 | `https://3king.cc/` | `3King` | **Go now** |
| 3 | 3king tặng 30k | 1,900 | 53 | `https://3king.cc/su-kien-khuyen-mai` | `khuyến mãi 3King – tặng 30k` | After Q2 + 1.3 |
| 4 | tải game 3king | 9,900 | 62 | `https://3king.cc/tai-app` | `tải game 3King` | After 1.2 |
| 5 | cách chơi nổ hũ | 1,600 | 34 | `https://3king.cc/thong-tin/bi-quyet-no-hu-thang-dam` | `cách chơi nổ hũ` | After 1.4 |

Anchor mix: 3 branded / 1 brand-qualified partial / 1 informational partial.
**Zero bare exact-match. Zero naked URLs.**

Note link 4's target changed from `/` to `/tai-app`.

### Placement criteria — pass/fail, no vendor discretion

Vietnamese language · VN audience ≥60% · gaming/entertainment/tech vertical ·
Ahrefs DR ≥25 **and** page-level organic traffic ≥50/mo · indexed before payment ·
in-body prose within first 60% of article · dofollow · ≤25 external outbound links ·
≤3 external gambling links on the page.

**Verified prospects:** `voz.vn` (DR 60, 807k VN traffic — confirmed linking to
competitor `topnohu.com`), `forumketqua.net` (DR 45), `topnohu.com` (DR 42),
`kqbd.mobi` (DR 38), `apkcombo.com` / `apkpure.com` (app listings — self-owned,
so vendor fraud is structurally impossible).

**Blacklist:** compromised VN government/university hosts
(`thanhtra.bvhttdl.gov.vn`, `qlditich.dsvh.gov.vn`, `chuyentrang.viendinhduong.vn`,
`dangkyhoc.tuaf.edu.vn`), the hacked `.edu`/`.org` injection cluster, all named
link vendors already in the profile, and the entire previous vendor's inventory.

### Payment

0% on claim · 40% day 14 (live, correct anchor/rel, indexed) · 30% day 60 ·
30% day 90. Per verified placement, never per package. **Day-0 audit must confirm
the link is in raw HTML before JS execution** — the check that would have caught
524 of 541 failures.

---

## 5. WHAT NOT TO DO

| Don't | Why |
|---|---|
| **Disavow** | Withdrawn. The clone carries byte-identical vendor spam and ranks #1. Niche-wide scraper spray, not a suppressor. |
| **Target `nổ hũ`, `nổ hũ đổi thưởng`, `game đổi thưởng`, `game nổ hũ đổi thưởng`** | All parasite-occupied: hacked `/vi-vn/` hosts incl. `ielts.tips`, `cbdguide.io`, a Brazilian federal institute. No slot exists. |
| **Target `bắn cá đổi thưởng` (KD 80)** | App-store SERP. Distinct from `game bắn cá đổi thưởng`. |
| **Buy more link volume** | `topnohu.com` ranks #3 on Pinterest/Qiita/Docker/`pages.dev` links — the same junk you own 2,683 of. Links are not the differentiator. |
| **Buy ".gov.vn DR 70" placements** | That is compromised-host access. Terminate any vendor offering it. |
| **Forecast off Semrush volumes alone** | Ahrefs/Semrush diverge 14×–540×. `tải game 3king`: 9,900 vs 300. |

---

## 6. MEASUREMENT AND KILL CRITERIA

### Success at 8 weeks (post Phases 1–2 + links 2 and 5)
- `3king` / `3kinggame` moves from **#3 to #1–2**
- Non-brand ranking keywords > 0
- `/ban-ca` ranks for `game bắn cá đổi thưởng` anywhere in top 50

### Success at 6 months
- **1,000–3,000 organic visits/month** (from 19)
- Brand SERP owned
- `game bắn cá đổi thưởng` top 20

### KILL CRITERIA — stop and re-diagnose

**If `3king.cc` has not moved from #3 to #1–2 on its own brand term within 8 weeks
of Phase 1 + 2 + links 2 and 5 — stop. Approve no further link budget.**

A DR 19 site with 2,683 referring domains that cannot beat a **DR 0** domain on
its own name after on-page fixes and clean links has a **network-level
suppression problem**, not a link problem. At that point the only remaining
options are portfolio consolidation onto 3king.win or migration to a clean
domain — and no quantity of links changes the answer.

---

## 7. HONEST OUTCOME RANGE

| Scenario | Probability | 6-month outcome |
|---|---|---|
| Brand SERP recovered + `game bắn cá đổi thưởng` lands | ~35% | 2,000–3,000 visits/mo |
| Brand SERP recovered only | ~30% | 800–1,500 visits/mo |
| On-page helps, brand SERP stays contested | ~20% | 150–400 visits/mo |
| Network-level suppression holds | ~15% | No material change → consolidate or migrate |

**Expected case is roughly 800–1,500 visits/month — a 40–80× improvement on 19,
and still a small business outcome in absolute terms.**

The addressable market is ~8,000/mo of genuine non-brand demand plus ~23,000/mo
of brand (Semrush; materially lower on Ahrefs). **It is not the 470,000/mo I
quoted in the first audit.** Every larger number in this vertical sits behind
SERPs occupied by compromised infrastructure or law-enforcement journalism, and
is not purchasable at any budget.

---

## 8. SEQUENCE SUMMARY

| When | What | Cost |
|---|---|---|
| **Week 1** | Q1 ownership · Q2 offer live · recovery demand | **Zero** |
| Week 1–2 | Phase 1 on-page (1.1–1.4) + build `/tai-app` | Low |
| Week 2 | Phase 2 internal linking + prune | **Zero** |
| Week 3 | Place links 2 and 5 | Low |
| Week 5 | Place links 1, 3, 4 | Low |
| **Week 11** | **Kill-criteria review** | Zero |
| Month 3+ | Scale only if the 8-week gate passed | — |

**Three of the first four actions cost nothing, and they carry more expected value
than all five links combined.**
