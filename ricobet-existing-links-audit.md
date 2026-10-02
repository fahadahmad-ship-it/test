# ricobet.com.mx — Audit of the 404 Links Already Built
Source: client delivery CSV (`backlinks-439.csv`), 404 rows, Feb–Sep 2026.
Cross-referenced against live Semrush/Ahrefs. 2 Oct 2026.

---

## 1. HEADLINE

**404 placements billed. 12 verified as actually pointing at ricobet.com.mx.
400 of 404 are "Not indexed". 72 are dead pages.**

| Check | Result |
|---|---|
| Rows billed | **404** across 390 unique domains |
| Rows with an anchor **and** target filled | **18 (4%)** |
| Verified target actually resolving to ricobet | **12 (3%)** |
| **"Not indexed"** | **400 / 404 (99%)** |
| HTTP 404 (dead page) | 59 |
| HTTP 0 (unreachable) | 12 |
| HTTP 525 | 1 |
| **Total dead placements** | **72 (18%)** |

---

## 2. THE VERIFICATION CRAWL FOUND NO LINK ON MOST PAGES

Most common "Verified target URL" — i.e. what the crawler actually found:

| Value | Count |
|---|---|
| `#content` | 42 |
| `#` | 30 |
| `#primary-content` | 25 |
| `#primary` | 23 |
| `#main` | 5 |
| **Total skip-nav fragments** | **125** |
| `https://www.ricobet.com.mx/` | 10 |
| `https://www.ricobet.com.mx/promotion` | 2 |

Most common "Verified anchor":

| Value | Count |
|---|---|
| **Skip to content** | **97** |
| Contact Us | 22 |
| ✕ | 9 |
| Casino / My Shop / Auto / Cats And Dogs | 3 each |

These are WordPress accessibility skip-links and template chrome. The crawler
grabbed the first element in the DOM **because there was no link to ricobet on the
page to grab.**

---

## 3. THE PLACEMENTS ARE A CASINO PBN

Where the verified target *did* resolve, it frequently pointed at other gambling
sites rather than ricobet:

`mrcasinomy.com/contact-us/` · `admiral-xcasino.com/contact-us/` ·
`rouletteyy.com/category/roulette/` · `maxgameon.com/category/casino/` ·
`pringodingo.com/category/betting/` · `viralgamesnews.com` ·
`gambling-online-theory.com/category/poker/`

A cluster of interlinked casino blogs with no audience, cross-linking to each
other. That is a private blog network, not editorial placement — and it explains
the 99% non-indexation directly. **Google is refusing to keep these pages in the
index at all.**

---

## 4. DELIVERY PATTERN

| Month | Placements | Dead pages |
|---|---|---|
| 2026-02 | 134 | **37** |
| 2026-04 | 134 | **33** |
| 2026-05 | 118 | 2 |
| 2026-06 | 5 | 0 |
| 2026-07 | 4 | 0 |
| 2026-08 | 5 | 0 |
| 2026-09 | 4 | 0 |

386 of 404 placements landed in three months (Feb–May), then volume collapsed to
4–5/month. **70 of the 268 links from the Feb and April batches are already dead**
— 26% attrition inside eight months.

Data quality is also poor: 2 rows carry the text `casino online mexico` in the
**Target URL** column, and 38 rows have `home` in the Follow/nofollow column.

---

## 5. THE FINDING THAT MATTERS MOST FOR THE NEW ORDER

**The anchors and targets I recommended have already been bought — and they failed.**

Every row that has a real anchor and target (all 18):

| Anchor | Target | Indexed |
|---|---|---|
| rico bet ×3 | `/` | Not indexed |
| ricobet ×3 | `/` | Not indexed |
| casino online mexico ×6 | `/` (2 rows have a broken target) | Not indexed |
| bono sin depósito casino méxico ×2 | **`/promotion`** | Not indexed |
| tragamonedas en Ricobet | **`/slots`** | Not checked |
| casino online México | `/` | Not checked |
| minijuegos de Ricobet | `/` | Not checked |
| Ricobet | `/` | Not checked |

Compare to my proposed order:

| My proposal | Already tried? | Outcome |
|---|---|---|
| `Ricobet` → `/` | **Yes** | Not indexed |
| `casino online Ricobet` → `/` | **Yes** (as "casino online mexico") | Not indexed |
| `bono sin depósito Ricobet` → `/promotion` | **Yes** (as "bono sin depósito casino méxico") | Not indexed |
| `casino en vivo Ricobet` → `/livecasino` | No | — |
| `giros gratis sin depósito` → `/register` | No | — |

**Three of my five links replicate placements that have already been bought and
produced nothing.** Not because the keyword, anchor or target was wrong — the
targeting was reasonable — but because **the placements were never indexed.**

---

## 6. WHAT THIS CORRECTS

Earlier in this engagement I argued the constraint was first page-level links,
then domain Authority Score. This CSV supplies a simpler and better-evidenced
answer.

**The constraint is placement indexation.** 99% of the link inventory sits on
pages Google will not index. An unindexed page passes nothing — no equity, no
anchor signal, no relevance. That fully explains:

- Why `/promotion` carries 221 referring domains and ranks for nothing
- Why domain AS is **17** on 1,224 referring domains, while `versusbet.mx` reaches
  **AS 26** on fewer (1,119) and a quarter the follow links
- Why the site has zero non-brand rankings despite 404 placements

**Ricobet does not have a link-quantity problem, a targeting problem, or an
anchor problem. It has an inventory problem.**

---

## 7. REVISED RECOMMENDATION

**Do not order 5 more links from this supply chain.** Repeating the same anchors
and targets through the same vendor will reproduce the same result.

**Before any new order:**

1. **Recovery demand.** 404 billed, 12 verified, 99% unindexed, 18% dead on
   arrival. The client's own CSV is the evidence.
2. **Confirm indexation is a vendor problem, not a site problem.** Check Search
   Console that `/promotion`, `/register`, `/livecasino` and `/slots` are indexed.
   If ricobet's own pages are also unindexed, that is the real issue and no link
   will fix it.
3. **Change the acceptance test.** Index status is the only metric that has
   mattered here, and it was never enforced.

**If 5 links are ordered anyway**, the single change that matters is not which
keyword or anchor — it is this: **pay only for placements that are in Google's
index 14 days after going live.** On this CSV's performance that would have made
roughly 4 of 404 payable.

**The one target worth adding is `/livecasino`** — it has zero backlinks, so it is
the only page where a new link is not landing on top of hundreds of inert ones.
Everything else in my earlier order has been tried.
