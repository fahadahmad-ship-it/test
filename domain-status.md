# Domain Status & Resolution Report

Six domains checked. HTTP status captured 2026-10-02 from an unrestricted
network; DNS resolution captured in-session the same day.

## The table

| # | Domain | Status | Where it resolves / redirects |
|---|--------|--------|-------------------------------|
| 1 | https://hellanzb.com/ | **301** → 200 | Cloudflare (`104.21.29.197`, `172.67.149.187`) — **301 redirects to `https://3king.cc/`** |
| 2 | https://postcodegazette.com/ | **301 → 301** → 200 | Cloudflare (`104.21.89.50`, `172.67.137.207`) — **double hop: → `hellanzb.com` → `3king.cc`** |
| 3 | https://aabss.org/ | **200** | `128.199.224.64` (DigitalOcean) — no redirect, serves directly |
| 4 | https://xnet2.com/ | **301** → 200 | Cloudflare (`104.21.48.145`, `172.67.223.212`) — **301 redirects to `https://3king.cc/`** |
| 5 | https://icmfg.com/ | **200** | Cloudflare (`104.21.73.23`, `172.67.137.167`) — no redirect, serves directly |
| 6 | https://naruto-mx.com/ | **200** | `128.199.224.64` (DigitalOcean) — no redirect, serves directly |

No 302s anywhere. Every redirect in this set is a clean 301 (permanent).

## Two distinct groups

**Group A — redirecting to `3king.cc` (3 domains)**
`hellanzb.com`, `postcodegazette.com`, `xnet2.com`. All on Cloudflare, all 301.

**Group B — serving 200, no redirect (3 domains)**
`aabss.org`, `icmfg.com`, `naruto-mx.com`.
`aabss.org` and `naruto-mx.com` share one IP (`128.199.224.64`); `icmfg.com` is on Cloudflare.

## What the redirect target is

`3king.cc` is a **Vietnamese real-money gambling / "game đổi thưởng" portal** —
slots, fish-shooting, betting, deposits and withdrawals. It resolves to
`198.185.159.144/145` and `198.49.23.144/145`, which are **Squarespace** ranges.

So three expired//acquired domains with unrelated historical topics (a Usenet
client, a UK postcode news site, a networking domain) are 301-ing their
accumulated link equity into a Vietnamese gambling site. That is the textbook
signature of an expired-domain PBN funnel.

### Why this matters

- A **301 passes link equity**. These three are deliberately pushing whatever
  authority the old domains had into the gambling target. That is the intent.
- Google treats a 301 from an expired domain to a wholly unrelated topic as a
  spam signal. Historically it tends to get the redirect's equity discounted to
  nothing, and association with the scheme can taint anything else on the same
  footprint.
- If you are evaluating these as acquisitions: the backlink profiles are
  currently pointed at gambling. Expect a reclamation period after repointing,
  and expect some of the existing links to be already devalued.
- If these are *your* domains: this is an active risk, not a theoretical one.

## Specific issues found

**`postcodegazette.com` has a redirect chain, not a single hop.**
It goes `postcodegazette.com` → `hellanzb.com` → `3king.cc` — two 301s. Each
extra hop bleeds a little equity, and chains are more fragile (break the middle
link and the whole chain dies). If the redirect is intended, point it straight
at the destination in one hop. This is the one concrete technical defect in the set.

**The three 200s are unverified as to content.**
A 200 confirms something is being served — it does **not** tell you whether that
is a real site, a parked page, or a placeholder. `aabss.org` and `naruto-mx.com`
sharing a single DigitalOcean box makes it worth confirming they are not serving
identical boilerplate.

## Recommended follow-ups

Check what the 200s are actually serving:

```bash
for d in aabss.org icmfg.com naruto-mx.com; do
  echo "=== $d ==="
  curl -sSL -A "Mozilla/5.0" "https://$d/" | grep -iEo '<title>[^<]*' | head -1
  curl -sSL -A "Mozilla/5.0" "https://$d/" | wc -c
done
```

Near-identical titles or byte counts on the two shared-IP domains means a
template, not real sites.

Check for cloaking — a redirect shown only to search engines:

```bash
for d in aabss.org icmfg.com naruto-mx.com; do
  echo "=== $d ==="
  curl -sSIL -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
    "https://$d/" | grep -iE '^(HTTP/|location:)'
done
```

If any of these 200 for a browser but 301 for Googlebot, they belong in Group A
and are cloaking it. Worth ruling out before you trust the 200.

## Method

Status chains from `curl -sSIL` following redirects, browser User-Agent.
DNS via the system resolver (apex and `www` resolve identically for all six).
`check-redirects.sh` in this repo reproduces the status column.

---

# Batch 2 — second domain set

Checked 2026-10-02. DNS from the session resolver; HTTP captured from an
unrestricted network.

## The table

| # | Domain | Status | Where it resolves / redirects |
|---|--------|--------|-------------------------------|
| 1 | https://angryziber.com/ | **No status — DNS does not resolve** | Name exists, **no A/AAAA record**. Nothing to connect to. |
| 2 | https://bomarinterconnect.com/ | **No status — DNS does not resolve** | Name exists, **no A/AAAA record**. Nothing to connect to. |
| 3 | https://kristinkreuk.net/ | **200** (parking lander) | `13.248.169.48` (AWS Global Accelerator) — **parked**, JS redirect to `/lander` |
| 4 | https://mornfall.net/ | **200** (parking lander) | `76.223.54.146` (AWS Global Accelerator) — **parked**, byte-identical to #3 |
| 5 | http://sc29.org/ | **405** to HEAD; `server: Parking/1.0` | `64.190.63.222` — **parked**. HTTPS fails: no cert for the hostname. |

**No 301s and no 302s anywhere in this batch.** Nothing here redirects at the
HTTP level. This set is entirely dead or parked — the opposite profile from
batch 1.

## What each one actually is

**angryziber.com, bomarinterconnect.com — dead.**
The names resolve as names but carry no address record, so no TCP connection is
possible and no status code can exist. Any backlinks currently point into a void.
(`angryziber.com` was the home of Angry IP Scanner, which now lives at
`angryip.org` — the old domain was simply abandoned.)

**kristinkreuk.net, mornfall.net — parked, same operator.**
Both serve exactly 114 bytes, byte-for-byte identical:

```html
<!DOCTYPE html><html><head><script>window.onload=function(){window.location.href="/lander"}</script></head></html>
```

That is a parking lander: a **JavaScript** redirect to `/lander`, not an HTTP
redirect. The AWS Global Accelerator IPs plus an identical payload confirm a
single parking provider holding both.

**sc29.org — parked, and misconfigured on top.**
`server: Parking/1.0` is an explicit parking banner. HTTPS fails with a TLS
`unrecognized name` alert, meaning the server holds no certificate for this
hostname — it is reachable over plain HTTP only.

## Two measurement caveats

**The 405 is an artifact of the method, not the domain's real status.**
`curl -I` sends `HEAD`, and this parking server does not allow it. A normal `GET`
will almost certainly return `200` with a parking page. Confirm with:

```bash
curl -sSL -o /dev/null -w 'GET status=%{http_code}\n' -A "Mozilla/5.0" "http://sc29.org/"
```

**A 200 here does not mean a live site.**
All three reachable domains return a success status while serving nothing of
substance. Status code alone would have been misleading on this batch — the
body is what distinguished them.

## SEO consequence

A JavaScript `window.location` redirect is **not** a 301. It passes no link
equity in the way a server-side 301 does, and Google treats parking pages as
thin content. For all five domains, any historical authority is currently
going nowhere:

- Two cannot be reached at all.
- Three serve parking pages.

If these are acquisition candidates, none is live, so there is nothing to
preserve — only a historical backlink profile to evaluate on its own merits.
That is a different question from the status check and needs a backlink tool.
