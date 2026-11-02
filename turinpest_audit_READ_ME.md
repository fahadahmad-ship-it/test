# Turin Pest Control — Backlink Audit & Disavow (read me first)

**Deliverables**
- `turinpest_Backlinks_Audit.xlsx` — full audit, 7 sheets (same layout as the K&K template)
- `disavow_turinpest.txt` — Google-format disavow file, **521 domains**

**Data sources:** Semrush (Backlink Analytics) + Ahrefs (spam flag / dofollow), pulled **2026-11-02**.
Classification is **per referring domain**, not per anchor.

---

## Headline: do NOT submit the file as the brief scopes it

The brief's 12 anchors are Semrush-accurate, but the by-anchor plan points at the wrong domains.

| Status | Domains | Backlinks | Action |
|---|---:|---:|---|
| **Spam (Disavow)** | 521 | 672 | In `disavow_turinpest.txt` |
| **Held (Pending Partner)** | 565 | 1,435 | **Not** disavowed — confirm with previous supplier first |
| Spam (Nofollow, No Action) | 67 | 94 | No action (passes no ranking value) |
| Held (Nofollow, No Action) | 16 | 85 | No action |
| Spam? (High-AS, Review) | 1 | 2 | Manual review (not auto-disavowed) |
| Keep | 206 | 429 | Genuine/harmless |
| **Total** | **1,376** | **2,717** | |

## What the brief got wrong (critical findings)

1. **It misses the biggest spam anchors.** `Expert SEO Backlink Services turinpest.com…` (**356 domains**) and `Reliable PBN Backlinks for turinpest.com…` (**40 domains**) are the core of the attack and are **not in the brief**. They dominate the disavow file.
2. **It would disavow commissioned-looking links.** 10 of the 12 anchors are exact-match local anchors (`pest control peachtree city ga`, `home pest control newnan ga`, `crawl space encapsulation newnan ga`…). These are **Held** (565 domains), not disavowed — they look like a prior link-building campaign. **Confirm with the previous supplier before adding any of them** (see the *Pending Disavow Lines* and *Exact Match Anchors* sheets).
3. **The telegram anchor needs no disavow.** `JOIN OUR TELEGRAM …darksidelinks` = 32 domains, **100% nofollow** → no ranking value → excluded (brief listed it as toxic to remove).
4. **Only one brief anchor clearly belongs in the file:** the PBN sales-copy anchor (`High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN…`) = 90 dofollow domains, disavowed. Brief said 52 — undercounted.
5. **The dates don't match.** Brief says "most first seen Jan–Feb 2026"; decoded Semrush timestamps put the real spam burst in **Jul–Oct 2026** (e.g. the 356-domain anchor is Sep 2026; brief #1 is Jul 2026, not Jan).
6. **The attack is still live.** Brief quoted 930 referring domains (17 Sep); Semrush now shows **1,363**. ~430 new domains in six weeks, almost all Ahrefs-flagged spam first-seen Sep–Oct 2026.

## Method / guardrails
- **Disavow = spam signal + at least one dofollow link.** Nofollow-only spam is excluded on purpose.
- Spam signal = keyword-stuffed SEO sales-copy / PBN / telegram anchors **OR** Ahrefs `is_spam` **OR** SEO-farm domain name (e.g. `*backlink*`, `*rankchecker*`, junk-TLD `seo*/rank*` sites).
- **False-positive guards:** real platforms (Yahoo, Bing, Yellowpages, BBB, chambers of commerce, `.gov/.edu`) forced to Keep; any spam domain at **AS ≥ 25** routed to **Review**, never auto-disavowed. Result: zero disavowed domains at AS ≥ 15.
- **Domain granularity:** referring hosts are resolved to the correct registrable unit with public-suffix handling, so blog/free-host subdomains (`*.blogspot.com`, `*.pages.dev`, `*.web.app`) and subdomain services (`*.us.com`) are each judged individually — the file never contains an over-broad line like `domain:blogspot.com`.

## Before you submit
1. **Send the *Exact Match Anchors* / *Pending Disavow Lines* sheets to the previous supplier** and mark what was commissioned. Append confirmed-unclaimed domains to the disavow file.
2. **Check Google Search Console** for a manual action / big ranking drop. A disavow mainly helps with a manual action or a clear algorithmic hit; Google ignores most of this spam automatically, so weigh whether to submit at all vs. monitor.
3. Because the attack is ongoing, plan to **re-pull and top up the file** (and the disavow) in a few weeks.

*Secondary metric columns (RD's / Traffic / Organic Keywords) are blank where the Semrush export doesn't provide them per referring domain.*
