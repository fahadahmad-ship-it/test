# Domain Status & Resolution Check

Checked: 2026-10-02

## Results

| # | Domain | HTTP Status (301 / 302 / etc.) | Where Domain Is Resolving |
|---|--------|-------------------------------|---------------------------|
| 1 | https://hellanzb.com/ | **Not verified** — egress blocked | Resolves → Cloudflare: `104.21.29.197`, `172.67.149.187` (IPv6: `2606:4700:3031::6815:1dc5`, `2606:4700:3035::ac43:95bb`) |
| 2 | https://postcodegazette.com/ | **Not verified** — egress blocked | Resolves → Cloudflare: `104.21.89.50`, `172.67.137.207` (IPv6: `2606:4700:3034::6815:5932`, `2606:4700:3037::ac43:89cf`) |
| 3 | https://aabss.org/ | **Not verified** — egress blocked | Resolves → **`128.199.224.64`** (DigitalOcean, direct — no CDN) |
| 4 | https://xnet2.com/ | **Not verified** — egress blocked | Resolves → Cloudflare: `104.21.48.145`, `172.67.223.212` (IPv6: `2606:4700:3037::6815:3091`, `2606:4700:3034::ac43:dfd4`) |
| 5 | https://icmfg.com/ | **Not verified** — egress blocked | Resolves → Cloudflare: `104.21.73.23`, `172.67.137.167` (IPv6: `2606:4700:3033::ac43:89a7`, `2606:4700:3037::6815:4917`) |
| 6 | https://naruto-mx.com/ | **Not verified** — egress blocked | Resolves → **`128.199.224.64`** (DigitalOcean, direct — no CDN) |

All six domains resolve in DNS. `www.` resolves identically to the apex for every one of them.

## Notes worth flagging

- **`aabss.org` and `naruto-mx.com` share the exact same IP (`128.199.224.64`).**
  Two unrelated-looking domains on one DigitalOcean box is the classic signature of a
  PBN / redirect farm. These are the two most likely to be serving 301s to a money site.
- The other four sit behind Cloudflare, so the origin IP is masked. A Cloudflare IP tells
  you nothing about whether the site is live, parked, or redirecting — the status code is
  the only thing that will.

## Why the status column is empty

This session's network egress policy denied all six hosts at the proxy
(`403` to `CONNECT`), and the same block applied to the server-side fetch path:

```
connect_rejected: gateway answered 403 to CONNECT (policy denial or upstream failure)
  hellanzb.com:443, postcodegazette.com:443, aabss.org:443,
  xnet2.com:443, icmfg.com:443, naruto-mx.com:443
```

DNS is unaffected, which is why the resolution column is complete.

To unblock: open the cloud environment menu in the session title bar → **Edit** →
**Network access**, and either raise the access level or add these six hosts to the
allowed domains. Access levels are documented at
https://code.claude.com/docs/en/claude-code-on-the-web

## Run it yourself

Save and run this anywhere with open internet; it prints the full redirect chain
and the final landing URL for each domain.

```bash
#!/usr/bin/env bash
DOMAINS=(hellanzb.com postcodegazette.com aabss.org xnet2.com icmfg.com naruto-mx.com)

for d in "${DOMAINS[@]}"; do
  echo "=============================================="
  echo "https://$d/"
  echo "----------------------------------------------"

  # Full header chain: every status code and Location hop
  curl -sSIL --max-time 30 \
       -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36' \
       "https://$d/" 2>&1 | grep -iE '^(HTTP/|location:|server:|cf-ray:)'

  echo "---"
  # Summary line
  curl -sSL -o /dev/null --max-time 30 \
       -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36' \
       -w 'final_code=%{http_code}  hops=%{num_redirects}  final_url=%{url_effective}  ip=%{remote_ip}\n' \
       "https://$d/"
  echo
done
```

### How to read the output

- **`301`** — permanent redirect. The hop that matters for SEO; link equity passes.
  Check the `Location:` header for where it points.
- **`302` / `307`** — temporary redirect. Passes little to no equity. On a domain you
  bought for its backlinks, a 302 is usually a misconfiguration worth fixing.
- **`200`** — resolving and serving content directly, no redirect.
- **`403` / `503` with `server: cloudflare`** — Cloudflare bot challenge, not a real
  site failure. Re-run with the browser User-Agent above, or check from a residential IP.
- **`404` / `410`** — DNS resolves but nothing is being served at the root.
- **A redirect chain longer than 1 hop** — e.g. `http → https → www → /path`. Each extra
  hop bleeds a little equity; worth collapsing to a single 301.

One thing to watch: a domain can 200 for a normal browser and 301 only for Googlebot
(cloaked redirect). If these are acquisition candidates, re-run the script a second time
with `-A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'` and
compare the two chains. A difference between them is a red flag.
