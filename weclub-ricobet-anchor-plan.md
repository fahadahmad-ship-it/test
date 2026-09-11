# WeClub (MY) & Ricobet (MX) — Critical Anchor Text & Target-URL Plan

**Prepared:** 2026-09-10 · Data: Ahrefs live (DR, top pages, keywords, anchors)
**Clients:** weclubmy2.com (WeClub — Malaysia online casino) · ricobet.com.mx (Ricobet — Mexico online casino/sportsbook)

> ⚠️ **Compliance / risk note (read first).** Online gambling is a heavily regulated, high-risk SEO niche. Malaysia prohibits most online gambling (these brands operate offshore); Mexico regulates it via SEGOB. Exact-match commercial anchors in this vertical carry a high manual-action / algorithmic-penalty risk, and both profiles are **already** carrying aggressive spam. This plan is deliberately conservative on exact-match and prioritises cleanup. Follow local advertising rules for any placement you control.

---

## 1. The #1 problem on BOTH sites: toxic anchors → disavow first

Neither anchor profile is safe to build on until cleaned. Both are dominated by the same negative-SEO / black-hat clusters:

**WeClub toxic anchors (disavow):** `PAGEWOO.COM…` (207 RD), `…SEOExpress.org…` testimonial (145 RD), `TELEGRAM @SEO_ANOMALY…` (139+40 RD), `TG @BHS_LINKS…` (107+80 RD), `@SEO_CARTEL…` (51), `@SEO_LINKK_ORDER` (48), `@LINKS_DEALER…` (46), `@SALESOVEN…ACCESS TO HACKED SITES` (34), `MASSLINKER.COM` (33), `High Quality Dofollow Backlinks DA 50 PA 40 PBN…` (33+27), `BLACK SEO LINKS…@SEO_LINKK` (27).

**Ricobet toxic anchors (disavow):** `TELEGRAM @SEO_ANOMALY…` (79+20 RD), `TG @BHS_LINKS…` (70+20 RD), `…Link-Legion.com` anchors ("rico cassino", "ricco slot", "rico bet bono sin depósito") (30/30/20 RD), `@LINKS_DEALER…` (12), `JOIN OUR TELEGRAM…darksidelinks` (9).

**Action:** export full backlinks, isolate these anchor clusters + `is_spam=true`, submit a **domain-level disavow** in GSC for each site, and monitor monthly (this is an ongoing attack pattern, not a one-off). **No new anchor building should start before the disavow is filed.**

## 2. Second problem: exact-match over-optimisation (WeClub)

"Online Casino Malaysia" (15,657 links / 63 RD) and "trusted online casino Malaysia" (10,290 links / 64 RD) are **massive sitewide/footer exact-match** anchors from a tiny domain set — a classic footprint. This alone is penalty-bait. New links must **not** add exact-match to the homepage; dilute hard toward branded/naked.

## 3. Third problem: mirror-domain fragmentation (WeClub)

Anchors point across **weclubmy2.com, weclub88, weclub88.net, weclub88.cc** — link equity is split across mirror/proxy domains. Decide the **canonical domain**, 301/consolidate the mirrors (or clearly designate the active one), and point new branded anchors at the canonical only. Otherwise you're diluting your own authority.

---

## 4. Target-URL map (where links should point)

Spread anchors across money pages — not just the homepage (concentration = footprint). Priority tier = how much link equity to route there.

### WeClub — target URLs
| Priority | Target URL | Page role | Primary keyword themes (MY: EN/BM/ZH) |
|---|---|---|---|
| P1 | `/` (homepage) | Brand + head term | weclub; online casino malaysia; 网上赌场 |
| P1 | `/livecasino` | Live casino | live casino malaysia; live casino online; 真人娱乐场 |
| P1 | `/` slots page (e.g. `/slots`) | Slots | online slots malaysia; slot game malaysia; permainan slot |
| P2 | `/fishing-game` | Fishing games | fishing game online; ikan game; 捕鱼游戏 |
| P2 | `/esport` (sportsbook) | Sports/esports betting | sports betting malaysia; judi bola; taruhan sukan |
| P2 | `/online-casino-promotion` | Promotions/bonus | casino bonus malaysia; free credit; kredit percuma |
| P3 | `/vip` | VIP programme | weclub vip; vip casino malaysia |
| P3 | `/login`, `/check-in`, `/howtojoin` | Navigational | weclub login (branded only) |

### Ricobet — target URLs
| Priority | Target URL | Page role | Primary keyword themes (MX, Spanish) |
|---|---|---|---|
| P1 | `/` (homepage) | Brand + head term | ricobet; casino online méxico; casino en línea |
| P1 | `/slotsgame` (+ `?sub=pragmatic/joker`) | Slots | tragamonedas online; slots pragmatic play; juegos de casino |
| P1 | `/livecasino` | Live casino | casino en vivo méxico |
| P2 | `/freespin` | Free spins | giros gratis; tiradas gratis; freespins |
| P2 | sportsbook page (e.g. `/deportes`) | Sports betting | apuestas deportivas méxico |
| P2 | promociones page | Bonuses | bono sin depósito; bono de bienvenida |
| P3 | `/minigame` | Mini games | minijuegos casino |
| P3 | `/login` | Navigational | ricobet iniciar sesión (branded only) |

> Route P1 URLs the bulk of links; deep pages get topical/partial anchors so the profile looks like a real brand, not a homepage-blasting campaign.

---

## 5. Anchor-text distribution model (for ALL new links)

Because both profiles are already over-optimised + spammed, new links skew **branded/natural**. Target mix:

| Anchor type | Target share | WeClub examples | Ricobet examples |
|---|---:|---|---|
| **Branded** | 40% | WeClub, WeClub Malaysia, WeClub88 | Ricobet, Ricobet México, Ricobet Casino |
| **Naked URL** | 20% | weclubmy2.com, www.weclubmy2.com | ricobet.com.mx, www.ricobet.com.mx |
| **Generic / CTA** | 15% | play here, visit site, main sekarang, 点击这里 | jugar aquí, visita el sitio, más información |
| **Partial / branded-topical** | 17% | WeClub live casino, WeClub slots, WeClub online casino | Ricobet casino online, Ricobet tragamonedas, casino Ricobet |
| **Exact-match commercial** | **≤8%** (high-trust editorial only) | online casino Malaysia; live casino Malaysia | casino online México; casino en vivo |

**Hard rules:**
- Exact-match commercial (≤8%) **only** on genuinely high-authority, topically-relevant, contextual placements — never sitewide, footer, or on low-DR/PBN pages. Given WeClub's existing 15k exact-match footprint, treat this cap as a ceiling you rarely hit.
- Every **navigational/login** page gets **branded anchors only**.
- Match anchor **language to the placement** (BM/EN/ZH for MY; Spanish for MX) — a Spanish anchor on an English page (or vice-versa) reads unnatural.
- Keep partial/branded-topical as the workhorse — it carries keyword relevance without the exact-match risk.

---

## 6. Worked anchor examples by target URL

### WeClub
| Target URL | Branded | Partial / topical | Generic | Exact (rare) |
|---|---|---|---|---|
| `/` | WeClub · WeClub Malaysia · WeClub88 | WeClub online casino · WeClub trusted casino | play at WeClub · main di WeClub | online casino Malaysia |
| `/livecasino` | WeClub Live Casino | WeClub live dealer games · live casino at WeClub | play live casino | live casino Malaysia |
| slots page | WeClub Slots | WeClub slot games · slots on WeClub | spin & play | online slots Malaysia |
| `/fishing-game` | WeClub Fishing | WeClub fishing games · ikan game WeClub | try fishing game | — |
| `/esport` | WeClub Sports | WeClub sportsbook · judi bola WeClub | bet here | sports betting Malaysia |
| `/online-casino-promotion` | WeClub Promotions | WeClub bonus · WeClub free credit | claim bonus | casino bonus Malaysia |

### Ricobet
| Target URL | Branded | Partial / topical | Generic | Exact (rare) |
|---|---|---|---|---|
| `/` | Ricobet · Ricobet México | Ricobet casino online · casino Ricobet | jugar en Ricobet | casino online México |
| `/slotsgame` | Ricobet Slots | tragamonedas en Ricobet · slots Ricobet Pragmatic | jugar tragamonedas | tragamonedas online |
| `/livecasino` | Ricobet Casino en Vivo | casino en vivo de Ricobet | jugar en vivo | casino en vivo México |
| `/freespin` | Ricobet Giros Gratis | giros gratis en Ricobet | obtén giros gratis | tiradas gratis |
| sportsbook | Ricobet Apuestas | apuestas deportivas Ricobet | apostar aquí | apuestas deportivas México |
| promociones | Ricobet Promociones | bono de Ricobet · bono de bienvenida Ricobet | reclama tu bono | bono sin depósito |

---

## 7. Sequencing (90 days)

1. **Weeks 1–2:** File disavows (both). Decide WeClub canonical domain + consolidate mirrors. Stop all exact-match acquisition.
2. **Weeks 3–8:** Build **branded + naked + generic** first to rebalance the ratio (aim 60%+ of new links). Spread across P1/P2 URLs. Local-language placements.
3. **Weeks 9–12:** Introduce **partial/topical** anchors to deep pages; add a *few* exact-match only on the strongest, most relevant editorial links. Re-check anchor ratios and toxic re-growth monthly.

**KPIs:** toxic RD trending down; branded-share of live anchors up; exact-match share down from its current spike; deep-page (non-homepage) links up; brand + head-term rankings holding/improving without a manual action.

## 8. Bottom line
- **Do not build anchors yet — disavow first.** Both profiles are actively spammed.
- **Dilute, don't reinforce.** WeClub's exact-match homepage anchors are already a liability; new links go branded/natural and to deep pages.
- **Consolidate WeClub's mirror domains** so equity isn't split.
- **Localise anchors** and keep exact-match ≤8%, high-trust only. In this niche, a clean, brand-led, well-distributed profile is the competitive edge — the spam route is what got both sites into a hole.
