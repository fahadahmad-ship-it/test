#!/usr/bin/env python3
"""Parse spilled Ahrefs MCP tool-result files into one CSV.

The MCP layer spills oversized results to disk as [{type,text}]; the text
holds the JSON payload followed by a render hint and a usage-cost object,
so the payload is extracted with raw_decode rather than a greedy regex.
"""
import csv, glob, json, os, sys

COLS = ["domain", "domain_rating", "traffic_domain", "positions_source_domain",
        "links_to_target", "dofollow_links", "is_spam", "ip_source",
        "first_seen", "last_seen"]


def payload(path):
    txt = "".join(p["text"] for p in json.loads(open(path, encoding="utf-8").read())
                  if p.get("type") == "text")
    i = txt.index("{")
    data, end = json.JSONDecoder().raw_decode(txt[i:])
    return data.get("refdomains", []), txt[i + end:]


def main(pattern, out):
    rows, cost = {}, 0
    for f in sorted(glob.glob(pattern), key=os.path.getmtime):
        recs, tail = payload(f)
        try:
            cost += json.loads(tail[tail.index('{"apiUsageCosts"'):])["apiUsageCosts"]["units-cost-total-actual"]
        except Exception:
            pass
        for r in recs:
            rows[r["domain"]] = r
        print(f"  {os.path.basename(f)}: {len(recs)} rows")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for d in sorted(rows):
            w.writerow(rows[d])
    print(f"unique domains: {len(rows)}  units spent (these files): {cost}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
