# ngwindows.com audit — verification checklist

Tick as you go. Ordered by impact. ✅ = already confirmed.

| # | Check | Where / how | What it decides | Done |
|---|---|---|---|---|
| **1** | **Manual Actions** | GSC → Security & Manual Actions | **Gates the whole disavow.** None + no bought links → most likely don't file at all | ☐ |
| **2** | **Links report** (external links, top linking sites) | GSC → Links → Export | Google's real view. Semrush says 1,232 domains, Ahrefs 1,357, overlap only 338 — neither is truth | ☐ |
| **3** | **Daily clicks 20 Jun – 31 Jul 2025** | GSC → Performance, daily view | If the fall starts ~30 Jun → June 2025 core update is near-certain as the cause of the −87.7% | ☐ |
| **4** | **Pages report, May vs Aug 2025** | GSC → Performance → Pages, compare | Tests the **2025 migration** theory — currently untested, could outrank core updates | ☐ |
| **5** | **`/blog/` impressions vs clicks, 16 mo** | GSC → Performance, filter `/blog/` | Impressions fall = core update. Impressions hold, clicks fall = AI Overviews | ☐ |
| **6** | **Confirm all 14 redirect destinations** | `curl -sI https://<domain>/ \| grep -i location` (loop below) | Confirms the shell model across the set. `roiwindows.com` + `thermalastwindows.com` are **other real companies** — watch those two | ☐ |
| **7** | **Read a spam page's real `href`** | `curl -sL https://urlbacklinkschecker.space/dir/seo-ranking-links-170322 \| grep -o 'href="[^"]*windows[^"]*"'` | Shell → exposure is only campaign `148096` (258 domains). `ngwindows.com` → far bigger, disavow expands | ☐ |
| **8** | **Wayback May vs Aug 2025** | `web.archive.org/web/2025*/ngwindows.com` | Redesign/migration in that window = likely real cause of the traffic collapse | ☐ |
| **9** | **Who owns the GoDaddy account?** | Ask client | All 14 on `ns23`/`ns24.domaincontrol.com` = one account. Decides if remediation is even possible | ☐ |
| **10** | **Did you ever own `northgeorgiawindows.net`?** | Ask client | It's the `.net` of their exact trading name. Vendor-held = recoverable asset + trademark issue | ☐ |
| **11** | **Anyone buy links since Jun 2026?** | Ask client | Cleanup vs defence. Also feeds #1 | ☐ |
| **12** | **Did you rebuild the site in 2025?** | Ask client | Pairs with #4 and #8 | ☐ |
| **13** | **Fix the GBP website URL** | Google Business Profile → website field | Malformed (`%3F` not `?`). **72 backlinks** land on a broken URL and 301 | ☐ |
| **14** | **Audit `guildquality.com` link** | Ask GuildQuality | Client already holds it (8,670 surveys, Guildmaster Awards) but it's absent from link data → likely nofollow | ☐ |
| **15** | **Confirm Yelp / Houzz are nofollow** | Check the live profiles | Both live but absent from link data. **Do not** report as missing citations | ☐ |
| **16** | **Phone GNFCC for dues** | Greater North Fulton Chamber | DR 44, exact territory. Client has **zero Georgia chamber links** — only chamber citation is in **Tennessee** | ☐ |
| **17** | **Decide on `gnpmilton.com`** | — | Genuinely lost, but DR 26 and a paid-placement network — reclaiming likely means paying | ☐ |
| **18** | **Register `ngwind.com`?** | Registrar | 15th brand variant. **Does not resolve** — currently unregistered | ☐ |
| **19** | **Ahrefs SE on `thermalprowindows.com`** | After 2026-10-25 | Should show ~150+ links from campaign `211287`. Resolves residual uncertainty | ☐ |
| **20** | **Semrush `target_url` + `redirect_url`** | After top-up | The column never pulled. **Budget first** — 500-row pages cost ~48k units | ☐ |
| **21** | **Semrush `backlinks_pages`** | After top-up | "~100% homepage" doesn't reconcile; Ahrefs shows 90 distinct target URLs | ☐ |
| **22** | **Remaining ~4,048 Semrush links** | After top-up | 53.6% of links never retrieved | ☐ |
| — | ~~`northgeorgiawindows.net` is a redirect~~ | — | **✅ Confirmed 2026-10-06** | ✅ |

## Command for #6

```bash
for d in ngawindows.com roiwindows.com thermalprowindows.com qualitypluswindows.com \
         northpointwindows.com performingwindows.com thermatrustwindows.com \
         northgeorgiawindows.net thermalastwindows.com e2windows.com \
         choiceviewwindows.com ngwindow.com northgawindows.com northgeorgiawindow.com; do
  printf '%-28s ' "$d"; curl -sI --max-time 10 "https://$d/" | grep -i '^location:' || echo '(none)'
done
```

## Settled — don't re-open

| Finding | Status |
|---|---|
| Redirect mechanism | ~95% (campaign-ID partition) + confirmed directly for `northgeorgiawindows.net` |
| One registrar account | Verified by DNS. Client's site is Cloudflare — no shared infrastructure |
| **Don't delete the redirects** | Removes zero spam links (disavow is per-property); destroys brand equity since 2003 |
| **Don't filter on authority** | 632 spam domains are DR ≥30; genuine local links sit at DR 2–20 |
| Traffic collapse pre-dates the spam | True — but *why* is still open (#3, #4, #8) |
| Links aren't the bottleneck | Gap is commercial: `/windows` doesn't rank, `window replacement atlanta` at **position 15** |
