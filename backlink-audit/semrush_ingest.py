#!/usr/bin/env python3
"""Ingest link-level rows pulled from the Semrush MCP backlinks report.

The original CSV export lacked `response_code` and `redirect_url`. Their
absence is why the affiliate protocol's redirect-liveness check could not be
run, and why the hexcolor.co links looked like direct homepage links when
they in fact route through a redirect service.

Input: a CSV written from Semrush `execute_report(report='backlinks')` rows,
semicolon-delimited as the API returns them.

Usage:
    python3 semrush_ingest.py <semrush_rows.csv> <outdir>
"""
import csv
import sys
from collections import Counter, defaultdict
from urllib.parse import urlsplit

from audit import host_of, audit_key, _registrable, BRAND_OWNED

# Columns requested from the API, in order.
COLUMNS = [
    "source_url", "target_url", "anchor", "nofollow", "response_code",
    "redirect_url", "external_num", "page_ascore", "sitewide",
    "first_seen", "last_seen",
]

# --------------------------------------------------------------------------
# Redirect-chain analysis
# --------------------------------------------------------------------------

# Redirect hosts observed carrying brand campaign paths. A link that passes
# through one of these is routed through link-management infrastructure —
# evidence of a deliberate placement, not an organic citation.
def redirect_profile(rows):
    """Summarise the redirect layer for one referring domain."""
    hops = [r["redirect_url"].strip() for r in rows if r.get("redirect_url", "").strip()]
    if not hops:
        return {"routed": False, "hosts": [], "paths": [], "share": 0.0}
    hosts = Counter(host_of(h) for h in hops)
    paths = Counter(urlsplit(h).path.strip("/").lower() for h in hops)
    return {
        "routed": True,
        "hosts": hosts,
        "paths": paths,
        "share": len(hops) / len(rows),
    }


def classify_redirect(prof, brand_tokens=("performancelab", "mindlabpro",
                                          "testolabpro", "prelabpro",
                                          "burnlabpro")):
    """Is the redirect layer campaign infrastructure or a cloak?

    A single redirect host carrying a brand-named campaign path across the
    whole domain is link-management/affiliate architecture. The brief says
    that must never be flagged toxic merely for being a redirect.
    """
    if not prof["routed"]:
        return None
    host, _ = prof["hosts"].most_common(1)[0]
    path, _ = prof["paths"].most_common(1)[0]
    branded_path = any(t in path.replace("-", "").replace("_", "")
                       for t in brand_tokens)
    single_host = len(prof["hosts"]) == 1
    if branded_path and single_host and prof["share"] >= 0.9:
        return ("ROUTED_CAMPAIGN", host, path,
                f"All links route through {host}/{path} — a single "
                "brand-named campaign path. This is link-management or "
                "affiliate infrastructure, and the brief protects it: a "
                "redirect is not itself a toxicity signal.")
    if len(prof["hosts"]) > 3:
        return ("ROUTED_MIXED", host, path,
                f"Links route through {len(prof['hosts'])} different redirect "
                "hosts — inconsistent with a single managed campaign.")
    return ("ROUTED_OTHER", host, path,
            f"Links route through {host}/{path}.")


# --------------------------------------------------------------------------
# HTTP status handling
# --------------------------------------------------------------------------

def status_profile(rows):
    codes = Counter(r.get("response_code", "").strip() for r in rows)
    total = sum(codes.values()) or 1
    dead = sum(n for c, n in codes.items() if c.startswith(("4", "5")))
    return {"codes": codes, "dead_share": dead / total}


def main(src, outdir):
    with open(src, encoding="utf-8", errors="replace", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    print(f"rows ingested: {len(rows):,}")

    by_dom = defaultdict(list)
    for r in rows:
        by_dom[audit_key(host_of(r["source_url"]))].append(r)
    print(f"referring domains covered: {len(by_dom):,}")

    out = []
    for d, rs in sorted(by_dom.items(), key=lambda kv: -len(kv[1])):
        prof = redirect_profile(rs)
        rc = classify_redirect(prof)
        st = status_profile(rs)
        out.append({
            "Referring Domain": d,
            "Links Pulled": len(rs),
            "Redirect Routed %": f"{prof['share']:.0%}",
            "Redirect Host": rc[1] if rc else "",
            "Redirect Path": rc[2] if rc else "",
            "Redirect Verdict": rc[0] if rc else "DIRECT",
            "Dead Link %": f"{st['dead_share']:.0%}",
            "HTTP Codes": ", ".join(f"{c}:{n}" for c, n in st["codes"].most_common(4)),
            "Unique Anchors": len({r["anchor"] for r in rs}),
            "Top Anchor": Counter(r["anchor"] for r in rs).most_common(1)[0][0],
            "Nofollow %": f"{sum(1 for r in rs if r.get('nofollow')=='true')/len(rs):.0%}",
            "Redirect Note": rc[3] if rc else "Direct link, no redirect hop.",
        })

    path = f"{outdir}/redirect_and_status_profile.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    routed = [o for o in out if o["Redirect Verdict"] != "DIRECT"]
    print(f"domains routed through a redirect: {len(routed):,}")
    for o in routed[:15]:
        print(f"  {o['Referring Domain']:30} -> {o['Redirect Host']}/"
              f"{o['Redirect Path']}  ({o['Redirect Verdict']})")
    print(f"Written: {path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
