# High Priority Plumbing — Disavow-or-Dilute Recommendation

**Client:** highpriorityplumbing.com (Conyers, GA plumbing & septic)
**Prepared by:** Harbinger Marketing — backlink audit
**Date:** 2026-11-02
**Scope of this memo:** the two spam clusters named in the Audit Overview — the
self-promotional link-service anchors and the messaging-app channel invitations —
with a disavow-or-dilute recommendation for each. Full classification of all
3,276 referring domains is in the accompanying workbook
(`HighPriorityPlumbing_Backlinks_Audit.xlsx`).

---

## Bottom line

| Cluster | Domains | Links pass value? | Recommendation |
|---|---|---|---|
| Self-promotional link-service — WhatsApp pitch (`I will Increase your Domain Authority… WhatsApp Us On:`) | **10** | **Yes — dofollow** | **Disavow** |
| Self-promotional link-service — `.xyz` fake-testimonial on link-seller hosts | **13** | No — nofollow | **Dilute / no action** |
| Messaging-app channel invitation — Telegram (`JOIN OUR TELEGRAM …/darksidelinks`, `…/quarterlinks25`) | **25** | No — nofollow | **Dilute / no action** |

**The deciding factor is dofollow vs nofollow, not the anchor wording.** Google
only transmits ranking signals (good or bad) through dofollow links. A disavow
file only matters for links that pass value. So:

- **The 10 dofollow WhatsApp link-service domains → disavow.** They pass PageRank,
  the anchor is unambiguous link-scheme spam, and they are already captured in the
  disavow file.
- **The 25 Telegram + 13 `.xyz` testimonial domains (all nofollow) → do *not*
  disavow.** They pass no ranking value, so disavowing them achieves nothing.
  The correct response is dilution: keep earning genuine links so this residue
  stays a rounding error, and monitor in case any flip to dofollow.

Disavowing the nofollow clusters would not be *harmful*, but it is busywork that
clutters the file and implies an impact it cannot have. We have excluded them
from the submitted file and listed them here for the record.

---

## Why these clusters exist

High Priority Plumbing is in the middle of an active negative-SEO / link-scheme
flood. Semrush shows the referring-domain count roughly **doubled in two months**
(~1,650 steady through mid-2026 → 3,217 by October 2026). Of the 3,276 referring
domains we audited, **1,661 are spam** (1,592 with at least one dofollow link,
69 nofollow-only), overwhelmingly auto-generated throwaway domains at Authority
Score 0–6.

The two named clusters are small, human-noticeable corners of that flood where
the **link seller advertises itself** in the anchor text rather than stuffing the
client's domain name. They are a useful tell for *who* is running the campaign,
but they are a tiny fraction of the attack and — because they are mostly nofollow
— not where the ranking risk lives.

---

## Cluster 1 — Self-promotional link-service anchor text (23 domains)

Two anchor families, with opposite handling because of the follow flag.

### 1a. WhatsApp link-service pitch — **DISAVOW** (10 domains, all dofollow)

Anchor (verbatim): **`I will Increase your Domain Authority/Rating from 0 -70 in
5 days. WhatsApp Us On: +1(226)799-7565.`** — a link vendor selling its own
service, planted as a dofollow link to the home page. Authority Score 2 on every
domain; two dofollow links each.

| Domain | AS | Dofollow | Status |
|---|---|---|---|
| blog-forest.help | 2 | 2 | Spam (Disavow) |
| corner-writers.blog | 2 | 2 | Spam (Disavow) |
| good-essays.com | 2 | 2 | Spam (Disavow) |
| marketing-updatee.store | 2 | 2 | Spam (Disavow) |
| marketingupdatee.com | 2 | 2 | Spam (Disavow) |
| next-essays.online | 2 | 2 | Spam (Disavow) |
| raven-frost.online | 2 | 2 | Spam (Disavow) |
| solace-moon.online | 2 | 2 | Spam (Disavow) |
| tempest-ash.online | 2 | 2 | Spam (Disavow) |
| xylo-mist.online | 2 | 2 | Spam (Disavow) |

**Recommendation: disavow.** Dofollow + explicit link-selling anchor = textbook
disavow evidence. All 10 are in the submitted file.

### 1b. `.xyz` fake-testimonial on link-seller hosts — **DILUTE / NO ACTION** (13 domains, all nofollow)

Anchor (verbatim): **`"As a small business owner, I was overwhelmed by the
complexities of SEO. Thankfully, I found highpriority…"`** — a fabricated
testimonial, planted as a **nofollow** link on domains whose names *are* link-
service brands (`seoboosthq.xyz`, `rankbuilder.xyz`, `offpageagency.xyz`,
`sponsoredlinks.xyz`, `linkoutreach.xyz`, `editorlinks.xyz`, `nichelinks.xyz`,
`topranklinks.xyz`, `page1boost.xyz`, `rankscalers.xyz`, `offpagepro.xyz`,
`offpagestudio.xyz`, `backlinknest.xyz`). Authority Score 0 across the board.

**Recommendation: do not disavow — dilute.** Every link is nofollow and passes no
value. Disavowing them changes nothing. Leave them out of the file; they are
recorded in the workbook as `Spam (Nofollow, No Action)`.

---

## Cluster 2 — Messaging-app channel invitation (25 domains, all nofollow) — **DILUTE / NO ACTION**

Two Telegram channel-invite anchors, both **nofollow** on every domain, zero
dofollow links anywhere in the set:

- **`JOIN OUR TELEGRAM https://t.me/s/darksidelinks`** — 22 domains
- **`OUR TELEGRAM CHANEL https://t.me/s/quarterlinks25`** — 3 domains

These are classic forum/comment/blog-injection spam advertising a Telegram "link
deals" channel. Several sit on subdomains of otherwise-ordinary hosts
(e.g. `s52.hekko24.pl`, `shop.lopezexpressgt.com`, a school library at
`alazharcilacap.sch.id`), which is why they roll up to a handful of parent rows
in the workbook; the genuine high-authority parents (e.g. `hekko24.pl`) are kept,
and the spam subdomains are marked no-action.

**Recommendation: do not disavow — dilute and monitor.** All 25 are nofollow and
pass no ranking value. There is nothing to disavow. Keep them under observation;
if any reappear as dofollow in a later crawl, they move to the disavow file then.

---

## These clusters in context (important)

The 51 named domains are **not** where the ranking risk sits. They are 51 of
1,661 spam domains, and only the 10 dofollow WhatsApp domains carry weight. The
real exposure is the **1,592-domain dofollow link-scheme flood** — overwhelmingly
the anchor *"Premium SEO Authority Backlinks to Help highpriorityplumbing.com
Websites Rank Higher"* (on ~1,409 domains) and hundreds of backlink-seller hosts
(`backlinkchecker…`, `seobacklinks…`, `buybacklinks…`, `linkbuilding…`). **That**
full set is the disavow file (1,592 `domain:` lines), and it is where dilution
alone is not enough — those dofollow links should be disavowed.

So the complete answer to "disavow or dilute?" is:

- **Disavow** everything that is spam **and dofollow** — the 10 WhatsApp domains
  plus the ~1,582 other dofollow spam domains. (One file, already built.)
- **Dilute / no-action** everything that is spam but **nofollow** — the 25
  Telegram + 13 `.xyz` testimonial + ~31 other nofollow-spam domains. Keep
  earning authoritative local links (GA plumbing/septic citations, press,
  genuine directories) so the residual spam share keeps shrinking.

---

## Action plan

1. **Submit the disavow file** (`disavow_highpriorityplumbing.txt`, 1,592 domains)
   to the highpriorityplumbing.com Search Console property — **after** the step
   below. The 10 WhatsApp domains are included; the nofollow clusters are not.
2. **Partner check first.** 945 domains are *Held (Pending Partner)* — exact-match
   commercial anchors ("Septic Tank Service Conyers GA", etc.) and deep service/
   location-page links that may be a commissioned local-SEO campaign. Do **not**
   disavow these until the previous SEO partner confirms none were paid
   placements. They are excluded from the file.
3. **Confirm the existing-file question.** If a disavow file already exists on the
   property, uploading **replaces** it — merge first. If the client has confirmed
   there is none, submit as-is.
4. **Dilute, don't chase.** For the nofollow spam (Telegram, `.xyz`, etc.), invest
   in genuine link acquisition rather than disavow housekeeping; re-audit the
   profile monthly while the attack is active.

## Limits / honesty notes

- One Search Console property, one file: no client-owned domains redirect into the
  site (the only `redirect_url` seen is `ift.tt`, an IFTTT share), so a single
  file is both necessary and sufficient.
- Metrics are Semrush (Authority Score, backlinks, referring domains, traffic,
  organic keywords). Example-page live status rests on Semrush's last crawl.
- The Held set needs the partner's answer before any of it can be actioned.
- Do not submit anything to Google Search Console on the client's behalf without
  their sign-off.
