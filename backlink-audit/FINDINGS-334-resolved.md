# The 334 "no link-level sample" domains — resolved

**Input:** `DOMAINSNEEDINGDATA.md` — 334 referring domains / 3,522 backlinks
whose verdicts rested only on domain authority, backlink count, IP address and
domain name. None of their links appeared in the 50,000-row CSV export, so
there were no anchors, no target URLs and no redirect data behind any of them.

**Status: closed.** All **334 domains now carry link-level evidence — 3,855
links** pulled per-domain through the Semrush connector, with every column the
brief asked for: `source_url`, `anchor`, `target_url`, `nofollow`,
`redirect_url`, `response_code`, `external_num`, `page_ascore`.

| Deliverable | Contents |
|---|---|
| `semrush_backlinks_filtered.csv` | 15,488 rows total; 3,855 of them cover these 334 domains |
| `out/needing_data_resolved.csv` | One row per domain: anchor profile, target profile, redirect hosts, affiliate IDs, dead-link count, verdict, reason |
| `out/disavow_addendum_needing_data.txt` | The 95 proposed disavows, grouped by footprint |
| `resolve_needing_data.py` | The classifier |

---

## 1. How the data was actually obtained

Two corrections to the brief's assumptions, both material:

- **These domains were not absent from the profile — they were absent from the
  unfiltered pull.** The paged pull run earlier (13,896 rows) exhausted at
  offset 13,000, yet a *filtered* call for `mylandingpages.co` returns rows
  immediately. Semrush allocates rows per request, so the only way to reach a
  long-tail domain is to name it in `display_filter`.
- **`display_filter` ORs same-field entries and accepts at least 72 of them.**
  That is what made this tractable: 334 domains resolved in six batched calls
  rather than 334 individual ones.

Of the 334, **243 already had rows** from the earlier pull once matched on
registrable domain — the brief's "not one of their links appears in the export"
was true of the CSV export, not of the connector data gathered since. 162
needed targeted calls; 72 of those needed a second pass at maximum column width
to push the payload past the harness's inline limit so it landed on disk.

## 2. Verdicts

| Verdict | Domains | Links |
|---|---:|---:|
| `KEEP_AFFILIATE_RETAIN` | 123 | 2,000 |
| `REVIEW_MANUALLY` | 116 | 1,354 |
| `DISAVOW` | 95 | 501 |

**197 of the 3,855 links are dead or unreachable** (HTTP 0/404/410) — hygiene,
not toxicity.

Every rule fires on an observable footprint, never a score, so each verdict
traces to a quotable row.

### The 95 disavows

| Footprint | Domains |
|---|---:|
| Domain-stats / shortener scraper network | 45 |
| Link-selling / hacked-site vendor | 27 |
| Cloned UK publisher commerce table | 23 |

**Link vendors that advertise themselves in the anchor.** These are not
ambiguous — the anchor *is* the sales listing and the client's link is the
sample being sold:

- `🍪 TELEGRAM @SALESOVEN | ACCESS TO HACKED SITES FOR SEO` —
  `automaned.com`, `ggpartnersconsortium.com`, `joyrney.com`, `batizens.vn`,
  `lebazzar-demadous.site`
- `TG @LINKS_DEALER | EFFECTIVE SEO LINKS FOR WWW.PERFORMANCELAB.COM` —
  `a1housingservicesltd.co.uk`. **The anchor names the client's own domain**:
  someone is selling links pointed at `performancelab.com` as a product.
- `High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service
  dtcx.com … Buy Backlinks Online Cheap` — `southfwb.com`, `chordmp3.net`,
  `fletcherrld.com`
- `JOIN OUR TELEGRAM https://t.me/s/darksidelinks` — `hwnerds.com`,
  `thetarotalk.com`, `berlin-immobilien-verkaufen.de`
- `Any SEO resource - we have it. 🔥 No resellers, no middlemen` —
  `domraider.eu.com` / `.gb.net` / `.it.com`
- `Where to buy 🚀 aged domains and backlinks 🔥` — `ecommercebenchmarking.com`

**This resolves `dtcx.com`.** It appeared in the earlier connector pass as a
redirect host on 69 referring domains, shape-compatible with link management.
The anchors settle it: `dtcx.com` is the **PBN/backlink service being
advertised**, not client infrastructure. Any domain routing through it is
carrying a sold link.

**One scraper operator, many TLDs.** 45 domains publish the identical page
under rotating titles — `✅ Website Stats 📊`, `👲 Domain Report 👲`,
`❤️ URL Shared ❤️`, `seo domain research` — with bare-domain anchors
(`nutropic.com`, `testolabpro.com`, `dtcx.com`), 1,973–10,159 outbound links
per page, and **the same numeric record IDs** (39738, 49117, 57252, 59258,
71951, 181868, 232128) across unrelated domains. Same database, same operator.
Members include `analyticshaven.top`, `blogsphere.top`, `creativeposts.top`,
`dailymusings.top`, `metamagic.top`, `optimizeflow.top`, `bye.fyi`,
`byteshort.xyz`, `quero.party`, `drjack.world`, `screenshots.wiki`,
`atomizelink.icu`, `anchorurl.cloud`, `shortenurls.eu`, `buzzshrink.website`,
`urls-shortener.eu`, `seol.store`, `takes.homes`.

**Two publisher-clone networks.** Verbatim commerce tables lifted from real UK
publishers and replicated across throwaway domains:

- **15 domains** clone BBC *Good Food* / *olivemagazine* ("Best vitamin D
  supplements 2026", "Taster box – 4 bars (£8.99)"), all three links identical,
  all redirecting to `nutropic.com/products/taster-pack`:
  `aevascience.pics`, `axisholistic.rest`, `dailyrestora.study`,
  `elegantfreelancers.com`, `kurahorizon.sbs`, `kurapulse.space`,
  `moduspax.website`, `prismcrafts.xyz`, `vedaflow.online`,
  `vividlypulse.lifestyle` / `.living` / `.xyz`, `zenoppa.site`,
  `pattern-aegis.live`
- **8 domains** clone a Hearst UK nail-supplements article
  ("UK Approved(Esquire,Red,HB,GH,Country Living,Prima)"): `premworld.online`,
  `summercenter.store`, `summersworl.online`, `namepromo.online`,
  `worldboxe.online`, `yourboxe.online`, `yourcenter.online`, `yellos.online`

## 3. The finding that is a commercial decision, not a spam call

**Affiliate account `68990cbe508aa` operates 43 of these 334 domains.**

They are free-blog-platform hosts — `aboutyoublog.com`, `anchor-blog.com`,
`blazingblog.com`, `blogars.com`, `bluxeblog.com`, `pages10.com`,
`blogdosaga.com`, `blogsvirals.com` and 35 more. The audit had them as "No
Link-Level Sample - Unverified" and the shape looks like the blog-network spam
the audit already catalogued. The link data says otherwise: every target URL
carries that one affiliate account ID. This is **a single affiliate in the
client's own programme**, mass-posting on free blog platforms.

The anchors are filler — `here`, `click here`, `more info`, `check here`,
`website` — and **the links are follow, not nofollow**.

I have deliberately *not* filed these as either KEEP or DISAVOW. An affiliate
ID tells you **who built a link, not whether it is safe to keep**: follow
affiliate links are a link-scheme exposure for the client whoever placed them.
Equally, disavowing 43 domains belonging to a paying partner is a commercial
act, not a hygiene one. They are `REVIEW_MANUALLY` with an
affiliate-compliance reason: the fix is to require that affiliate to nofollow
its links, and to disavow only if it will not.

Smaller accounts follow the same pattern at lower volume: `5f4ec409c99f6`
(4 domains, all 307-redirect gateways — `supplementlifestyle.com`,
`wellife.org`, `wlghconferences.org`, `seriouslifemagazine.com`,
`supplementnatural.com`, each with a per-site `data1=` code),
`542004f70c101` (3), `5f1e14c2db517` (3).

`a_bid=a2ad38c1` appears on 66 of the 334 — that is a **programme-wide banner
ID, not an account**. Counting it as one would have manufactured a 66-domain
phantom network; it is recorded separately.

## 4. Verdicts that reverse the old flag

- **`appsrankings.com` — retention confirmed.** The brief called this "the
  largest unverified retention in the audit", held on an *inference* that it
  shares the `hexcolor.co` affiliate network. Its `redirect_url` had never been
  pulled. It has now: every sampled link is anchor `Satın Al!`, nofollow, at
  the bare homepage, routing through **`https://drect.net/performancelab`** —
  the exact `hexcolor.co` footprint. The inference was right. Its fate rides
  with `hexcolor.co` on the `drect.net` ownership question, not on the disavow
  list.
- **`/breedlove` is a 7-domain sponsor network, not link velocity.**
  `thebitsignal.com` (37 links, flagged "Newly-Seen Domain, Aggressive Link
  Velocity"), `btcpods.xyz` (8, flagged "Spam-Associated TLD") and
  `onlyboosts.social` (6) send **100% of their links to
  `performancelab.com/breedlove`** — the bespoke sponsor path for the "What is
  Money?" podcast. The audit already rescued `whatismoneypodcast.com` on
  exactly this basis; the rule has to apply to its peers. Outside the 334,
  `noderunners.network` (72 links) and `snipd.com` (14) share the footprint —
  and `noderunners.network` carries an Ahrefs `is_spam` flag it does not
  deserve.
- **`chronotherapeutics.org` is affiliate infrastructure, not a target.** It
  appears in this list *and* as the redirect host for `gossiphealth.com`'s 48
  links. Its own pages are 301 gateways (`/performancelabmind`,
  `/go/performance-lab-flex`) carrying `a_aid=5fad81fe89a7d`.
- **70 domains were flagged "Hosting Cluster - Verify Ownership".** Ownership
  is now resolved by footprint rather than by IP: 24 disavow, 21 keep,
  25 review.
- **`zephrcf.com`** is `forbes-forbescom-live.non-prod.zephrcf.com` — a
  **Forbes staging environment** leaking a real "Forbes Vetted" article. Not
  spam; a publisher infrastructure artefact. Nofollow, so nothing to act on.

## 5. False positives caught in this pass

| Nearly did | Why wrong | Fix |
|---|---|---|
| Disavowed `duckduckgo.github.io` as a scraper network | It is DuckDuckGo's open-source data listing. The bare-domain/high-outlink signature fires correctly but the spam reading does not follow — the same trap as `blogspot.com` and the Shopify C-block in the original audit | Reputable-listing host guard: `.github.io`, `.gitlab.io`, `.readthedocs.io`, `wikipedia.org`, `.edu`, `.gov` are held for review, never disavowed on that signature |
| Rescued `moscowtimes.top` as a "sponsor landing page" | Its one link points at `/search` — site furniture, not a bespoke partner page | Sponsor rule now needs ≥3 links and rejects a generic-path list |
| Merged 66 unrelated affiliates into one network | `a_bid` is a programme-wide banner ID; only `a_aid` identifies an account | Account clustering keys on `a_aid`/`aff` only |
| Missed `onlyboosts.social`'s sponsor path | Its six links carry five "distinct" paths differing only by trailing URL-encoded U+2060 word-joiners | Target paths normalised (unquote + strip zero-width) before any same-path rule |

## 6. Limits

- Counts differ from the brief's by construction: the API served **3,855
  links** against 3,522 stated, because the referring-domain export's
  `Backlinks (true)` and the link-level report are different populations.
- The brief's plain-text list holds **336** entries against the 334 in its tier
  tables; the tables are authoritative and were used.
- `page_ascore` is 0 or near-0 for most of these rows, so page-level authority
  adds nothing here. Verdicts rest on anchors, targets, redirects and outlink
  counts.
- Redirect hosts still could not be resolved live — the environment's network
  policy denies `drect.net`, `nutropic.com`, `dtcx.com` and the rest.
  `dtcx.com` is nonetheless settled by anchor evidence (§2).
- The 43-domain affiliate cluster is **held, not decided** — see §3.
