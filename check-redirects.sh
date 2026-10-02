#!/usr/bin/env bash
# Prints: domain | status chain | final code | redirect target
# Usage: ./check-redirects.sh          (table)
#        ./check-redirects.sh csv      (CSV, paste back to Claude)

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
DOMAINS=(hellanzb.com postcodegazette.com aabss.org xnet2.com icmfg.com naruto-mx.com)

[ "$1" = csv ] && echo "domain,status_chain,final_code,final_url,server"

for d in "${DOMAINS[@]}"; do
  hdrs=$(curl -sSIL --max-time 30 -A "$UA" "https://$d/" 2>/dev/null)

  # every status code in the chain, e.g. "301 > 301 > 200"
  chain=$(printf '%s' "$hdrs" | grep -i '^HTTP/' | awk '{print $2}' | paste -sd'>' -)
  # every Location hop
  hops=$(printf '%s' "$hdrs" | grep -i '^location:' | awk '{print $2}' | tr -d '\r' | paste -sd' -> ' -)
  srv=$(printf '%s' "$hdrs" | grep -i '^server:' | tail -1 | awk '{print $2}' | tr -d '\r')

  read -r code url < <(curl -sSL -o /dev/null --max-time 30 -A "$UA" \
      -w '%{http_code} %{url_effective}' "https://$d/" 2>/dev/null)

  if [ "$1" = csv ]; then
    echo "$d,\"${chain:-ERR}\",${code:-000},\"${url}\",\"${srv}\""
  else
    printf '%-24s %-18s final=%-4s\n' "$d" "${chain:-ERR}" "${code:-000}"
    [ -n "$hops" ] && printf '    redirects to: %s\n' "$hops"
    printf '    lands on:     %s\n\n' "$url"
  fi
done
