#!/usr/bin/env python3
"""Append a Semrush execute_report page (saved tool-result JSON) to a CSV file.

Usage: python3 -I append_page.py <tool_result_json> <target_csv>

Writes the header once (only if target_csv does not yet exist), then appends
all data rows (skipping the header line on every page). Prints a summary line:
  PAGE_ROWS=<n> API_UNITS=<u> TOTAL_ROWS=<total data rows in target>
"""
import json
import os
import sys


def main():
    src = sys.argv[1]
    dst = sys.argv[2]

    with open(src, "r", encoding="utf-8") as f:
        obj = json.load(f)

    # The tool-result file may itself be the JSON object, or occasionally the
    # data may be nested. Handle the standard schema.
    data = obj["data"]
    units = 0
    try:
        units = int(obj["metadata"]["usage"]["api_units"])
    except (KeyError, TypeError, ValueError):
        units = 0

    # Normalize line endings and drop a single trailing newline.
    text = data.replace("\r\n", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    lines = text.split("\n") if text else []

    if not lines:
        page_rows = 0
    else:
        header = lines[0]
        rows = lines[1:]
        page_rows = len(rows)
        exists = os.path.exists(dst) and os.path.getsize(dst) > 0
        with open(dst, "a", encoding="utf-8") as out:
            if not exists:
                out.write(header + "\n")
            for r in rows:
                out.write(r + "\n")

    # Count total data rows in target (lines minus header).
    total = 0
    if os.path.exists(dst):
        with open(dst, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f)
        total = max(total - 1, 0)

    print(f"PAGE_ROWS={page_rows} API_UNITS={units} TOTAL_ROWS={total}")


if __name__ == "__main__":
    main()
