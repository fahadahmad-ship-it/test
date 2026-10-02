# 3king.cc — Critical Off-Site / Off-Page Audit
Data pulled live from Ahrefs, 2 Oct 2026. All figures `mode=subdomains`.

---

## 1. Headline verdict

**The off-site programme is not working, and the data says it has never worked.**
2,683 referring domains have produced DR 19, 8 ranking keywords, and 18 organic
visits per month. Every one of those 8 keywords is branded. The site has **zero
non-brand organic visibility** after ~16 months and ~5,100 lifetime referring
domains.

| Metric | Value |
|---|---|
| Domain Rating | **19** |
| Ahrefs Rank | 9,174,481 |
| Live backlinks | 20,553 |
| Live referring domains | 2,683 |
| All-time referring domains | 5,101 |
| Organic keywords (VN) | **8** (all branded) |
| Organic keywords, pos 1–3 | 8 |
| Organic traffic/mo | **18** |
| Organic traffic value | ~$11/mo |
| Paid keywords | 0 |

---

## 2. The core problem: links that transfer no equity

### 2.1 Referring domains vs. DR is wildly out of line
A clean profile with 2,683 referring domains normally sits at **DR 50–65**.
3king.cc sits at **19**. That gap is the single most important finding: Google
and Ahrefs are both discounting the overwhelming majority of these links.

### 2.2 DR was flat at ~0.8 for 11 months while 3,000 domains were acquired

| Period | Referring domains | Domain Rating |
|---|---|---|
| Oct 2024 | 10 | 0.1 |
| May 2025 | 20 | 0.0 |
| Jun 2025 | **203** | 0.0 |
| Sep 2025 | 987 | 0.7 |
| Jan 2026 | 2,358 | 0.8 |
| May 2026 | 2,941 | **0.7** |
| Jul 2026 | **3,093** (peak) | 18 |
| Oct 2026 | 2,685 | 19 |

From Jun 2025 to May 2026 the site added **~2,900 referring domains and gained
0.7 DR points.** The jump to DR 18–19 in Jun–Jul 2026 came from a handful of
links, not from the volume. That is the definition of wasted spend.

### 2.3 The profile is now shrinking
Peak was 3,093 refdomains (Jul 2026). Today: 2,685. **-408 domains (-13%) in
three months.** All-time 5,101 vs live 2,683 means **47% of every domain ever
acquired has already been lost.** The links are rented or transient, not earned.

---

## 3. The anchor profile is a liability, not an asset

This is the most damaging finding. The **largest anchor cluster pointing at
3king.cc is not from 3king's own campaigns — it is SEO-vendor spam that uses the
domain as a sales sample.**

| Anchor (truncated) | Ref domains | Dofollow | Ahrefs spam flag |
|---|---|---|---|
| "3king.cc delivers tested editorial links, interview placements and WordPress development…" | **211** | 0 | **spam** |
| `3kingapp.net` | 56 | 34 | clean |
| "High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service **3king.cc** Rank First Page Google Fast SEO…" | **42** | 42 | **spam** |
| `3king.cc` (plain brand) | 40 | **2** | **spam** |
| "TELEGRAM @MASSLINKER \| SOFTWARE TO PUBLISH BACKLINKS YOURSELF" | 37 | 0 | **spam** |
| "3kingapp.net: premium guest posts, high-quality backlinks, on-page SEO…" | 37 | 0 | **spam** |
| "TELEGRAM @SEO_LINKK_ORDER – SEO BACKLINKS, HOMEPAGE LINKS, CROSSLINKS" | 36 | 0 | **spam** |
| "I used to think affordable SEO meant compromising quality until meeting SEOExpress.org…" | 31 | 0 | **spam** |
| "…Black Hat SEO backlinks … Telegram:@ALGX3 / @seo7878" | ~20 across variants | yes | **spam** |

**Actual commercial Vietnamese anchors — the entire set:**

| Anchor | Ref domains |
|---|---|
| Tải game bắn cá | 4 |
| chơi bắn cá online | 3 |
| chơi tài xỉu online | 3 |
| bắn cá online đổi thưởng | 2 |
| tài xỉu trực tuyến | 2 |

**~14 referring domains carry a real target keyword.** Out of 2,683.

Three consequences:
1. The domain is embedded in public link-vendor advertising networks. Anyone
   auditing it sees "PBN", "Black Hat SEO", "Buy Backlinks Cheap" next to the brand.
2. Even the plain-brand anchor `3king.cc` (40 domains) is spam-flagged with only
   **2 dofollow** links — the brand signal itself is being discounted.
3. `3kingapp.net` appears across 56+56 domains of anchors. There is
   cross-contamination between two properties sharing one toxic footprint; Google
   will cluster them.

---

## 4. Referring domain quality: directory, profile and vendor tier

Top referring domains by DR, with reality checked:

| Domain | DR | Links | Status | What it actually is |
|---|---|---|---|---|
| vimeo.com | 96 | 1 | **lost** | profile spam |
| pages.dev | 93 | 1 | **lost** | free hosting subdomain |
| about.me | 90 | 1 | **lost** | profile spam |
| reverbnation.com | 90 | 1 | **lost** | profile spam |
| itxoft.com | 81 | 4 | **all 4 lost** | link vendor |
| temp-site.link | 75 | 1 | live | throwaway hosting, 1 traffic |
| factmags.com | 75 | 1 | live | links to 40.8M domains — pure spam farm |
| hol.es | 74 | 3 | live | free hosting, 2 traffic |
| rank-your.site | 73 | 1 | **lost** | link vendor |
| backlinker.shop | 71 | 1 | live | **link vendor** |
| buybacklinks.agency | 69 | 1 | live | **link vendor** |
| rankva.com / rank-top.click | 67 / 59 | 1 | **lost** | link vendors |

Not one of the top-DR referring domains is a Vietnamese site, a gaming site, or
a publisher with editorial standing. The high-DR entries are either free-hosting
subdomains, UGC profiles, or companies that sell backlinks.

---

## 5. The guest-post programme (from your 541-row CSV)

| Check | Result |
|---|---|
| Rows billed | **541** across 512 domains |
| Rows with anchor + target filled | **19** |
| Verified target actually resolving to 3king.cc | **17** |
| Most common "verified anchor" | `Skip to content` (161) |
| Most common "verified target" | `#content` (80), `#primary` (48), `#` (31) |
| Indexed status on sampled rows | **Not indexed** |

The verification pass is grabbing skip-nav links, which means on ~500 of those
pages **the crawler could not find a link to 3king.cc at all.** Either the links
were never placed, were removed after payment, or are rendered in a way that is
invisible to crawlers. This is unverified delivery on roughly 96% of the invoice.

**Placement relevance is also wrong on the links that do exist.** Verified
placements sit on: `pwinsider.com` (pro wrestling), `fifa-infinity.com` (football
games), `theplaidhorse.com` (equestrian), `bellyupsports.com` (US sports),
`programminginsider.com` (software), `theclintoncourier.net` (Mississippi local
news), `mygreenbucks.net` (US personal finance). Vietnamese-language gambling
anchors on US regional news and horse-show sites is the single clearest spam
pattern in Google's playbook.

**Zero** of the sampled placements are: Vietnamese-language, VN-hosted, gaming or
casino vertical, or geo-relevant.

Link targets are also undiversified — of 19 real links: 10 → homepage,
6 → `/ban-ca`, 3 → `/no-hu`. No supporting content layer to link into.

---

## 6. Ranking reality check — and a strategy problem

### 6.1 Current rankings (VN)

| Keyword | Pos | Volume | Traffic | Branded |
|---|---|---|---|---|
| 3kinggame | 3 | 250 | 1 | yes |
| tải game 3king | 3 | 40 | 7 | yes |
| tai 3king | 2 | 30 | 4 | yes |
| tải 3king | 2 | 20 | 4 | yes |
| 3king games | 3 | 10 | 2 | yes |
| 3king bet / 3king online / game 3 king | 1–2 | 0 | 0 | yes |

Note the site ranks only **#2–3 for its own brand name** — a DR 19 site with a
spam-flagged brand anchor cannot even own its brand SERP. That is the clearest
single symptom of the discounted profile.

### 6.2 The target keywords are a strategic mistake

| Keyword | Volume (VN) | KD | **Traffic potential** |
|---|---|---|---|
| nổ hũ | 69,000 | 0 | **0** |
| tài xỉu | 55,000 | 67 | 16,000 |
| tài xỉu online | 17,000 | 54 | 11,000 |
| bắn cá | 10,000 | 69 | 34,000 |
| game bắn cá đổi thưởng | 2,600 | 0 | **0** |
| nổ hũ đổi thưởng | 1,600 | 27 | **0** |
| bắn cá online | 1,300 | 53 | 32,000 |
| cổng game đổi thưởng | 10 | 40 | 13,000 |

**`nổ hũ` — 69,000 searches, traffic potential 0.** The SERP:

| Pos | Result |
|---|---|
| 1 | YouTube video (DR 99) — 24,044 traffic |
| 2 | People Also Ask |
| 3 | **tienphong.vn — "Triệt phá đường dây đánh bạc trăm tỷ kiểu game 'Nổ hũ'"** (police bust a 100-billion-đồng gambling ring) — DR 82, 1,208 refdomains |

Google is serving `nổ hũ` as a **news/entertainment query about illegal gambling
enforcement**, not a commercial one. No commercial operator ranks. The budget
spent building `nổ hũ` anchors is unrecoverable regardless of link quality —
there is no commercial slot to win. Same for `nổ hũ đổi thưởng` (TP 0) and
`game bắn cá đổi thưởng` (TP 0).

### 6.3 `bắn cá online` shows what actually ranks

| Pos | URL | DR | Refdomains |
|---|---|---|---|
| 1 | play.google.com (bancaonline) | 100 | 1,712 |
| 2 | **ica.net.vn** | **10** | 2,520 |
| 3 | apps.apple.com | 97 | — |
| 4 | gamevui.vn | 47 | — |
| 6 | vtco.esgame.vn | **29** | 1,893 |
| 10 | download.com.vn | 71 | — |

Two things:
- The SERP is an **app-store / download-aggregator SERP.** Google wants an app
  entity, not a landing page.
- `ica.net.vn` ranks **#2 at DR 10** with 2,520 refdomains — a near-identical link
  footprint to 3king.cc, but it ranks because it is a real app with a Play Store
  listing, a brand entity, and VN-relevant signals. **DR is not the gate.
  Entity and relevance are.** 3king.cc has the link volume and none of the entity.

---

## 7. Where 3king.cc is lacking off-site — ranked

| # | Gap | Severity |
|---|---|---|
| 1 | **Anchor profile owned by third-party link-spam vendors.** Largest anchor cluster (211 domains) advertises SEO services. "PBN", "Black Hat SEO", Telegram vendor anchors across ~200 domains. Brand anchor itself spam-flagged. | **Critical** |
| 2 | **No equity transfer.** 2,683 refdomains → DR 19. ~2,900 domains added for +0.7 DR over 11 months. | **Critical** |
| 3 | **No topical or geographic relevance.** Zero VN-language, zero gaming-vertical, zero VN-hosted referring domains in the top tier. Vietnamese anchors on US sports/equestrian/local-news sites. | **Critical** |
| 4 | **~96% of the guest-post deliverable is unverifiable.** 522/541 rows have no anchor or target; verification returns skip-nav links; sampled rows "Not indexed". | **Critical** |
| 5 | **No brand entity.** No Play Store / App Store listing surfacing, no news or Wikipedia co-citation, no social or review-platform presence. Competitors at DR 10–29 outrank on entity strength alone. | **High** |
| 6 | **47% lifetime link attrition; profile now shrinking** (-408 domains since July). Rented links, not earned. | **High** |
| 7 | **Keyword targeting misallocated.** Primary spend on `nổ hũ` family — traffic potential 0, SERP owned by YouTube and police-raid news coverage. | **High** |
| 8 | **Nofollow/UGC-heavy at the top.** Highest-DR refs are vimeo, about.me, reverbnation, pages.dev profiles — and most are already lost. | **Medium** |
| 9 | **No deep-link diversity.** 19 real links across only 3 URLs (`/`, `/ban-ca`, `/no-hu`). No content assets to link to. | **Medium** |
| 10 | **Cross-contamination with `3kingapp.net`** — 112+ referring domains carry 3kingapp anchors in the same spam clusters. Google will cluster the two properties and the penalty risk travels. | **Medium** |

---

## 8. What to do — in priority order

**Stop first**
1. **Halt the current guest-post vendor.** 541 links, ~19 verifiable, zero
   non-brand rankings, DR flat through the entire engagement. Demand verification
   on the 522 unverified rows or a refund before another order.
2. **Stop building `nổ hũ` anchors entirely.** Traffic potential is 0. The slot
   does not exist.

**Clean up**
3. **Full disavow pass.** Export all 2,683 refdomains, filter on Ahrefs
   `is_spam`, the vendor-anchor clusters (Telegram/@masslinker/@seo7878/PBN/
   "Black Hat SEO"), free-hosting TLDs (`.pages.dev`, `hol.es`, `temp-site.link`,
   `rank-*.{site,click}`, `*backlink*`), and `factmags.com`-class farms. This will
   likely be 1,500–2,000 domains. File in GSC.
4. **Decide on `3kingapp.net`.** Either consolidate deliberately (301 + shared
   brand) or sever completely. The current half-shared spam footprint gives you
   the downside of both.

**Rebuild**
5. **Build the entity before the links.** Play Store + App Store listing, a
   consistent NAP/brand profile, VN-language brand presence. The #2 result for
   `bắn cá online` is DR 10 — it beats you on entity, not authority.
6. **Re-target to winnable terms with real potential:** `bắn cá online`
   (TP 32,000, KD 53), `bắn cá` (TP 34,000), `tài xỉu online` (TP 11,000, KD 54),
   `cổng game đổi thưởng` (TP 13,000, KD 40). Build the content assets to support
   them — you currently have 3 linkable URLs.
7. **Shift to VN-relevant placements only.** 20 genuine Vietnamese gaming/tech
   placements will outperform 541 US-general-news placements. Set relevance,
   language and indexation as pass/fail acceptance criteria on every order.
8. **Enforce verification contractually:** live dofollow link, correct anchor,
   correct target, page indexed in Google, re-checked at 30/60/90 days. Pay on
   verified placement, not on publication.

**Expect regulatory drag.** Online gambling is restricted in Vietnam, which is
why `nổ hũ` returns enforcement journalism and why the commercial SERPs route to
app stores. Any off-site plan has to work through app-store and entity channels
rather than classic editorial link building, because the editorial slots are not
available at any budget.

---

## 9. Honest bottom line

3king.cc does not have a link-building shortfall. It has **2,683 referring
domains and DR 19** — the opposite problem. The programme has been buying volume
in a market where volume is already discounted to near-zero, on irrelevant
properties, with anchors that advertise the spam itself, against keywords that
have no commercial SERP. The profile is now contracting.

More links of the current type will not move anything. The recoverable path is:
stop the spend, disavow hard, build a real brand entity, and re-aim at the
`bắn cá` / `tài xỉu online` cluster where traffic potential actually exists.
