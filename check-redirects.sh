#!/usr/bin/env bash
# Redirect + status checker. Works on macOS (bash 3.2 / BSD curl) and Linux.
#
#   ./check-redirects.sh        human-readable table
#   ./check-redirects.sh csv    CSV output

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'

DOMAINS=(hellanzb.com postcodegazette.com aabss.org xnet2.com icmfg.com naruto-mx.com)
# Override from the command line:  ./check-redirects.sh csv example.com foo.com
MODE=table; [ "$1" = csv ] && { MODE=csv; shift; }
[ "$#" -gt 0 ] && DOMAINS=("$@")

[ "$MODE" = csv ] && echo "domain,status_chain,final_code,final_url,server"

for d in "${DOMAINS[@]}"; do
  hdrs=$(curl -sSIL --max-time 30 -A "$UA" "https://$d/" 2>/dev/null)

  # "301>301>200"
  chain=$(printf '%s\n' "$hdrs" | grep -i '^HTTP/' \
          | awk '{printf "%s%s", sep, $2; sep=">"} END{print ""}')

  # "https://a.com/ -> https://b.com/"
  hops=$(printf '%s\n' "$hdrs" | grep -i '^location:' | tr -d '\r' \
          | awk '{printf "%s%s", sep, $2; sep=" -> "} END{print ""}')

  srv=$(printf '%s\n' "$hdrs" | grep -i '^server:' | tr -d '\r' | tail -1 | awk '{print $2}')

  summary=$(curl -sSL -o /dev/null --max-time 30 -A "$UA" \
              -w '%{http_code} %{url_effective}' "https://$d/" 2>/dev/null)
  code=${summary%% *}
  url=${summary#* }

  if [ "$MODE" = csv ]; then
    echo "$d,\"${chain:-ERR}\",${code:-000},\"${url}\",\"${srv}\""
  else
    printf '%-24s %-16s final=%s\n' "$d" "${chain:-ERR}" "${code:-000}"
    [ -n "$hops" ] && printf '    redirects to: %s\n' "$hops"
    printf '    lands on:     %s\n' "$url"
    [ -n "$srv" ] && printf '    server:       %s\n' "$srv"
    echo
  fi
done
