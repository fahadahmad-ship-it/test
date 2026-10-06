> # ⚠️ CORRECTED — figures in this file do not reproduce
>
> Re-derivation found this analysis understated its own result and overstated its
> independence. Its 84.3% re-derives to **87.4%** (the input was missing ~143 links),
> and the "sample A / sample B agreement" cited elsewhere is an artifact: **sample A
> is a strict subset of sample B**. On genuinely new observations the vendor share is
> **47.0%**, and the defensible band-wide estimate is **~66% (62–83%)**.
>
> The script and method are sound; the inputs and the independence claim were not.
> **See `recheck-numbers.md` and `FINAL-AUDIT.md` §4 for the corrected figures.**

# AS 0–5 Band: Anchor-Text Evidence Review

**Question asked:** do not disavow any link purely for being low authority. What are the
Authority Score 0–5 domains' anchors actually saying?

**Method:** 1,000 link-level records pulled from Semrush `backlinks` (source_url, anchor,
nofollow, page_authority_score), sorted `last_seen_desc`. Source URLs resolved to registrable
domains and joined against the Authority Score of each referring domain from
`data/refdomains.csv`. Script: `anchor-band-analysis.py` (reproducible).

**Coverage:** 855 of 1,000 links matched a scored referring domain; **485 distinct AS 0–5
domains** observed, out of ~1,011 in the full profile (48% coverage).

**Sampling bias — stated honestly:** sorting by `last_seen_desc` biases the sample toward
*currently active* links, which is where the live spam campaign sits. The benign share of the
untested half is therefore likely **higher**, not lower, than the figures below. These numbers
are an upper bound on toxicity, not a lower one.

---

## Link-level: anchor bucket × authority band × follow status

| Anchor bucket | AS 0–5 dofollow | AS 0–5 nofollow | AS 6–29 | AS 30+ |
|---|---|---|---|---|
| **Vendor sales copy** | **584** | 7 | 6 | **0** |
| Bare sister-domain name | 93 | 34 | 7 | 0 |
| Brand / naked URL | 20 | 19 | 15 | 4 |
| Empty / image / generic | 1 | 1 | 9 | 3 |
| Topical | 10 | 29 | 2 | 6 |
| Other | 0 | 1 | 3 | 1 |

**584 dofollow vendor-spam links in the AS 0–5 band versus zero in the AS 30+ band.** The spam
correlates with the authority tier, but it is not *identified* by it — the anchor string is
independently damning and is the only admissible evidence.

## Domain-level: AS 0–5 domains classified by the worst anchor observed

| Classification | Domains | Share | of which dofollow |
|---|---|---|---|
| Vendor sales copy | **409** | 84.3% | 403 |
| Bare sister-domain name only | 50 | 10.3% | 36 |
| Topical anchors only | 12 | 2.5% | 5 |
| Brand / naked URL only | 12 | 2.5% | 4 |
| Empty / image only | 2 | 0.4% | 1 |

---

## Conclusions

1. **Low authority is not the grounds, and must never be cited as such.** 15.7% of the AS 0–5
   band (76 of 485 domains) shows *no* manipulative anchor at all. Those domains are low-quality
   but behaviourally harmless and must be excluded from any disavow. Examples:
   `allwebsitesdirectory.com`, `domain.com.lc`, `domainsc.com`, `blinks.monster`, `alljobs.info`,
   `atlantatoprated.com`, `crowdyhome.com`, `backlinkstree.com`, and the blogspot scraper
   subdomains.

2. **Where grounds do exist, they are documentary, not statistical.** 403 AS 0–5 domains link
   **dofollow** using literal link-vendor sales copy — "High Quality Dofollow Backlinks DA 50
   PA 40 Premium PBN Network Service … Buy Backlinks Online Cheap", "Premium White Hat SEO Links
   for …", and anchors containing Telegram link-selling handles (`t.me/s/darksidelinks`,
   `t.me/s/quarterlinks25`). That is self-evidencing manipulation independent of any metric.

3. **The bare sister-domain cluster is a separate event and should be left alone.** 50 domains,
   28% of them nofollow, first appearing Jul 2025 — a year before the Jun 2026 blast. These are
   auto-generated stats/scraper farms, not the PBN.

4. **Operative rule for the disavow file:** a domain qualifies only on *cited anchor text +
   dofollow status*. Default is exclusion. Any domain whose evidence cannot be quoted goes to an
   "insufficient evidence — not disavowed" list instead.

5. **This finding is now partly superseded.** Per `anchor-and-attribution-forensics.md`, ~94% of
   this spam reaches ngwindows.com through 14 operator-controlled 301 redirect domains. Deleting
   those redirects severs the links at source and is strictly better than disavowing them.
   Disavow scope collapses to the ~283 links pointing at ngwindows.com directly.
