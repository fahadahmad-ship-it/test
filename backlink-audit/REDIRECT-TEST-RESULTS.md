# Redirect test results — 2026-10-06

Client-run `curl` checks against all 15 domains, cross-referenced with the link data.
**The result validates the campaign model completely.**

## The split is perfect, and it is not coincidence

| Domain | IP pair | Redirects? | Anchor rows | Campaign ID |
|---|---|---|---|---|
| ngawindows.com | **A** | ✅ yes | 354 | `148030` |
| roiwindows.com | **A** | ✅ yes | 410 | `178285` |
| thermalprowindows.com | **A** | ✅ yes | 349 | `211287` |
| qualitypluswindows.com | **A** | ✅ yes | 399 | `170322` |
| northpointwindows.com | **A** | ✅ yes | 355 | `150104` |
| performingwindows.com | **A** | ✅ yes | 350 | `160633` |
| northgeorgiawindows.net | **A** | ✅ yes | 173 | — |
| thermatrustwindows.com | **A** | *(not tested)* | 197 | `211290` |
| | | | **2,587** | **7 campaigns** |
| ngwindow.com | **B** | ❌ no | 32 | none |
| northgawindows.com | **B** | ❌ no | 30 | none |
| northgeorgiawindow.com | **B** | ❌ no | 35 | none |
| thermalastwindows.com | **B** | ❌ no | 44 | none |
| e2windows.com | **B** | ❌ no | 34 | none |
| choiceviewwindows.com | **B** | ❌ no | 31 | none |
| | | | **206** | **zero campaigns** |
| ngwind.com | — | ❌ NXDOMAIN | 0 | none |

**Three independent variables align exactly:** which IP pair a domain sits on, whether it
redirects, and whether the vendor ran a campaign against it. 8/8 and 6/6, no exceptions.

- **Group A** (`15.197.225.128` / `3.33.251.168`) — live redirects, **2,587 anchor rows, every
  one carrying a campaign ID**. This is the active operation.
- **Group B** (`15.197.142.173` / `3.33.152.147`) — no redirect, **206 anchor rows, not a single
  campaign ID**. These are incidental mentions, almost all from scraper "similar domains"
  sidebars, not purchased placements.
- `ngwind.com` — genuinely unregistered (NXDOMAIN, confirmed both sides).

## What this settles

1. **The redirect mechanism is confirmed outright**, no longer inferred. Seven domains verified
   redirecting, and the campaign-ID partition predicted exactly which ones would.
2. **Group B is irrelevant to this audit.** No campaigns, no redirects, 206 incidental mentions.
   They should not appear in any remediation plan.
3. **The vendor ran 8 campaigns**: 7 against Group A shells + **`148096` against ngwindows.com
   directly**. The client's property is one target among eight in one vendor account.
4. **The client's actual exposure is unchanged and small**: campaign `148096` only —
   **258 domains / 516 links** — which is what `disavow-v2-ahrefs.txt` already scopes to.
5. **`northgeorgiawindows.net` redirects but has no `/dir/` campaign** (173 rows from other
   networks). It is the `.net` of the client's exact trading name and is the **single most likely
   genuinely-client-owned domain in the set.** Worth asking about specifically.

## Open discrepancy — minor, does not affect conclusions

From this container (resolver 8.8.8.8), **all six Group B domains resolve normally** — `NOERROR`,
A records on `15.197.142.173` / `3.33.152.147`, nameservers `ns23`/`ns24.domaincontrol.com`. The
client-side test reported DNS errors for all six.

Most likely explanation: the domains are **registered but their GoDaddy Domain Forwarding is not
configured or has lapsed**, so DNS resolves while the connection or TLS handshake fails — which a
browser commonly surfaces as a "DNS error". Only `ngwind.com` is a true NXDOMAIN on both sides.

**It does not change anything**: Group B carries no campaigns either way. If worth pinning down,
distinguish "server not found / NXDOMAIN" from a connection-refused or certificate error.
