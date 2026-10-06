# Outstanding checks to complete the ngwindows.com audit

Everything below is a verification this audit could not perform, with the exact method and
**what each answer changes**. Ordered by decision impact, not effort.

**Confirmed 2026-10-06 (user):** `northgeorgiawindows.net` **is a redirect.** The 301-shell
mechanism is verified end to end for at least one domain. Campaign-ID evidence already put the
mechanism at ~95%; this closes it for that domain.

---

## A. Five minutes, any unrestricted machine — highest value

> This container's network policy blocks these hosts (`x-deny-reason: host_not_allowed`), which is
> why they are listed for you rather than done. Alternatively, add them under
> Network access → Custom → Allowed domains in the cloud environment settings and I can run them.

### A1. Confirm the destination of all 14 redirects
```bash
for d in ngawindows.com roiwindows.com thermalprowindows.com qualitypluswindows.com \
         northpointwindows.com performingwindows.com thermatrustwindows.com \
         northgeorgiawindows.net thermalastwindows.com e2windows.com \
         choiceviewwindows.com ngwindow.com northgawindows.com northgeorgiawindow.com; do
  printf '%-28s ' "$d"; curl -sI --max-time 10 "https://$d/" | grep -i '^location:' || echo '(none)'
done
```
- **All → ngwindows.com:** mechanism confirmed for the whole set. Nothing in the disavow changes
  (no entry depends on it), but the attribution section can be stated as fact.
- **Any → somewhere else:** that domain is not part of this story and needs separate treatment.
- **Any 200 with content:** it is a real site, not a shell — re-examine.

### A2. Read a spam page's actual `href` — tests the *targeting* claim, not just the redirect
```bash
curl -sL https://urlbacklinkschecker.space/dir/seo-ranking-links-170322 \
  | grep -o 'href="[^"]*windows[^"]*"' | sort -u
```
- Returns a **shell** → the full model is confirmed; the client's exposure really is only
  campaign `148096` (258 domains / 516 links).
- Returns **ngwindows.com** → exposure is far larger and the disavow must expand substantially.

### A3. Wayback diff — the untested explanation for the traffic collapse
Open `web.archive.org/web/2025*/ngwindows.com` and compare a **May 2025** snapshot against an
**August 2025** one. Look for a redesign, URL changes, or a platform migration.
- A migration in that window would **outrank Google core updates** as the cause of the −87.7%
  decline. It is currently *untested, not excluded*, and it is the single biggest analytical gap.

---

## B. Questions only the client can answer

| # | Question | Why it matters |
|---|---|---|
| **B1** | **Who holds the GoDaddy account** for the 14 domains? (All share `ns23`/`ns24.domaincontrol.com` — one account.) | Decides whether remediation is even possible. Client-owned → they control it. Vendor-owned → they may not. |
| **B2** | Did you ever own **`northgeorgiawindows.net`**? It is the `.net` of your exact trading name. | If a vendor now controls your brand `.net`, that is a recoverable asset and a trademark issue. |
| **B3** | Did anyone — staff, agency, freelancer, Fiverr/Telegram vendor — **buy links or "SEO packages" since June 2026**? | Decides cleanup vs defence, and whether a disavow is filed at all. |
| **B4** | **Did you rebuild or migrate the website during 2025?** | Pairs with A3. A yes likely explains the traffic collapse. |
| **B5** | Are you under 20 FTE? | Determines eligibility for the free Georgia Chamber Federation route. |

---

## C. Google Search Console — free, available right now

**This audit never consulted GSC once.** It is the only authoritative source for several of these.

| # | Check | What it settles |
|---|---|---|
| **C1** | **Manual Actions panel** | **Gates the entire disavow.** No manual action + no bought links → most guidance says do not file. 90 seconds. |
| **C2** | **Links report** (external links, top linking sites) | Google's own view — neither Semrush (1,232 domains) nor Ahrefs (1,357) matches it, and they overlap by only 338. This is the real denominator. |
| **C3** | **Daily clicks, 20 Jun – 31 Jul 2025** | The most decisive single chart. If the fall starts ~30 June, the June 2025 core update explanation becomes near-certain. |
| **C4** | **`/blog/` impressions vs clicks, 16 months** | Separates a core-update demotion (impressions fall) from AI Overviews (impressions hold, clicks fall). |
| **C5** | **Pages report, May vs Aug 2025** | Confirms or kills the migration hypothesis alongside A3. |

---

## D. After the API resets — Ahrefs 2026-10-25, Semrush when topped up

| # | Pull | Purpose |
|---|---|---|
| **D1** | **Ahrefs Site Explorer on `thermalprowindows.com`** | Highest-value single query. Under the redirect model it should show ~150+ links from campaign `211287`. Resolves the residual uncertainty directly. |
| **D2** | Semrush `backlinks` with **`target_url` + `redirect_url`** | The column never pulled. Confirms routing per link rather than by inference. **Budget first — 500-row pages cost ~48,000 units and that is what exhausted the balance.** |
| **D3** | Semrush `backlinks_pages` | Which pages absorb the spam. The "~100% homepage" claim does not reconcile arithmetically and Ahrefs shows 90 distinct target URLs. |
| **D4** | Remaining ~4,048 Semrush links (53.6% never retrieved) | Completes the anchor evidence. |

---

## E. Small fixes worth doing regardless of the above

| # | Item | Detail |
|---|---|---|
| **E1** | **Fix the Google Business Profile URL** | It is malformed — `%3F` instead of `?`, so the query string parses as a path. **72 backlinks** land on it and 301. Two-minute fix in the GBP website field. |
| **E2** | Audit the **`guildquality.com`** link attribute | The client already holds this (8,670 surveys, Guildmaster Awards). It is absent from the referring-domain data, so the profile link is likely nofollow. Ask GuildQuality. |
| **E3** | Confirm **Yelp / Houzz** are nofollow | Both have live profiles but are absent from the link data. Do **not** report them as missing citations. |
| **E4** | Phone **GNFCC** for dues | Greater North Fulton Chamber (DR 44) covers the exact territory. Dues unpublished. The client holds **zero Georgia chamber links** — its only chamber citation is in **Tennessee**. |
| **E5** | Decide on **`gnpmilton.com`** | Genuinely lost (DR 26, 2 links) but the network runs a paid "Book Your Interview" model, so reclaiming likely means paying again. |
| **E6** | Note **`ngwind.com`** | A 15th brand variant, found in scraper sidebars. **Does not resolve** — not currently registered. Consider defensive registration. |

---

## What is already settled — do not re-litigate

- **Redirect mechanism:** ~95% via campaign-ID partition (8 campaigns, 8 brands, zero crossover;
  45 domains crawled by both tools, Ahrefs returns campaign `148096` on 45/45). Now confirmed for
  `northgeorgiawindows.net` directly.
- **One registrar account:** all 14 on `ns23`/`ns24.domaincontrol.com`, GoDaddy Domain Forwarding.
  Verified by DNS. The client's own site is on Cloudflare — no shared infrastructure.
- **Do not delete the redirects.** It removes zero spam links (a disavow is per-property) and
  destroys brand-variant equity for a business trading since 2003.
- **Do not filter on authority.** 632 spam domains are DR ≥30; genuine local links sit at DR 2–20.
- **The traffic collapse pre-dates the spam** — though *why* it happened is still open (A3/C3/C5).
- **Links are not the competitive bottleneck.** The gap is commercial: `/windows` does not rank and
  `window replacement atlanta` (720/mo, $41 CPC) sits at **position 15**.
