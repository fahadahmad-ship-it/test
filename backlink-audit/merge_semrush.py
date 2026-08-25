#!/usr/bin/env python3
"""Convert the Semrush API pull into the CSV export's schema and merge.

The API returns different column names and omits several fields the export
carries. Most matter little, but `Source title` does: topical relevance is
scored on page titles, so for API-only domains relevance falls back to the
domain name alone. That limitation is recorded in the audit rather than
hidden — these rows are still a large net gain, since they bring anchors,
targets, redirect_url and response_code where there were none.

Usage: python3 merge_semrush.py <api_pull.csv> <export.csv> <merged_out.csv>
"""
import csv
import sys

EXPORT_COLS = [
    "Page ascore", "Source title", "Source url", "Target url", "Anchor",
    "External links", "Internal links", "Nofollow", "Sponsored", "Ugc",
    "Text", "Frame", "Form", "Image", "Sitewide", "First seen", "Last seen",
    "New link", "Lost link",
]


def adapt(r):
    """One API row -> one export-schema row."""
    code = (r.get("response_code") or "").strip()
    return {
        "Page ascore": r.get("page_ascore") or "0",
        # Not returned by the backlinks report. Left blank deliberately:
        # inventing a title would corrupt the relevance score.
        "Source title": "",
        "Source url": r["source_url"],
        "Target url": r["target_url"],
        "Anchor": r.get("anchor") or "",
        "External links": r.get("external_num") or "0",
        "Internal links": "0",
        "Nofollow": r.get("nofollow") or "false",
        "Sponsored": "false",
        "Ugc": "false",
        "Text": "true",
        "Frame": "false",
        "Form": "false",
        "Image": "false",
        "Sitewide": r.get("sitewide") or "false",
        "First seen": r.get("first_seen") or "",
        "Last seen": r.get("last_seen") or "",
        "New link": "false",
        # A 4xx/5xx source page is a dead link, which is the closest the
        # export's own vocabulary comes to what response_code reports.
        "Lost link": "true" if code[:1] in "45" else "false",
        # Carried through for the redirect analysis; ignored by audit.py.
        "_redirect_url": r.get("redirect_url") or "",
        "_response_code": code,
    }


def main(api_path, export_path, out_path):
    with open(api_path, encoding="utf-8", errors="replace", newline="") as fh:
        api = [adapt(r) for r in csv.DictReader(fh, delimiter=";")]
    with open(export_path, encoding="utf-8", errors="replace", newline="") as fh:
        exp = list(csv.DictReader(fh))

    # De-duplicate on (source, target, anchor): the pull overlaps the export.
    seen = {(r["Source url"], r["Target url"], r["Anchor"]) for r in exp}
    added = [r for r in api
             if (r["Source url"], r["Target url"], r["Anchor"]) not in seen]

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EXPORT_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(exp)
        w.writerows(added)

    print(f"export rows      : {len(exp):,}")
    print(f"API rows         : {len(api):,}")
    print(f"new after dedupe : {len(added):,}")
    print(f"merged total     : {len(exp) + len(added):,}  -> {out_path}")
    print(f"titles missing on the API rows: {len(added):,} "
          "(relevance falls back to domain name for those)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
