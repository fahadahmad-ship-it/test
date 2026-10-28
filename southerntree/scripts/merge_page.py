"""
Merge one Ahrefs page into an accumulator and compute the next cursor.

Usage:
    python3 -I merge_page.py <backlinks|refdomains> <accumulator.json> <raw_page_file>

<raw_page_file> may be:
  - the harness tool-result file: a JSON list of {"type":"text","text":"..."} items,
    where one item's text parses to {"backlinks":[...]} or {"refdomains":[...]};
  - a JSON object {"backlinks":[...]} / {"refdomains":[...]};
  - a bare JSON array of row dicts.

Prints a single status line:
  NEW=<n> BATCH=<n> TOTAL=<n> MAXSEEN=<iso> NEXT_CURSOR=<iso> STALL=<0|1>
STALL=1 means the whole page was already seen (ties at the cursor) and NEXT_CURSOR
was advanced by +1s to make progress. The caller stops when BATCH==0, or when
STALL=1 twice in a row with NEW=0.
"""
import json
import sys
import datetime

mode, acc_path, page_path = sys.argv[1], sys.argv[2], sys.argv[3]
KEYFIELD = {"backlinks": None, "refdomains": "domain"}[mode]
SEENFIELD = "first_seen_link" if mode == "backlinks" else "first_seen"


def extract_array(raw):
    if isinstance(raw, list):
        # tool-result wrapper?
        if raw and isinstance(raw[0], dict) and "text" in raw[0] and "type" in raw[0]:
            for item in raw:
                try:
                    obj = json.loads(item["text"])
                except Exception:
                    continue
                if isinstance(obj, dict) and mode in obj:
                    return obj[mode]
            return []
        return raw  # bare array of rows
    if isinstance(raw, dict) and mode in raw:
        return raw[mode]
    return []


def key_of(r):
    if mode == "backlinks":
        return (r.get("url_from", ""), r.get("url_to", ""), r.get("anchor", ""))
    return r.get("domain", "")


with open(page_path, encoding="utf-8") as fh:
    raw = json.load(fh)
page = extract_array(raw)

try:
    with open(acc_path, encoding="utf-8") as fh:
        acc = json.load(fh)
except FileNotFoundError:
    acc = []

seen = {key_of(r) for r in acc}
new = 0
for r in page:
    k = key_of(r)
    if k not in seen:
        seen.add(k)
        acc.append(r)
        new += 1

with open(acc_path, "w", encoding="utf-8") as fh:
    json.dump(acc, fh)

maxseen = max((r.get(SEENFIELD, "") for r in page), default="")
stall = 0
next_cursor = maxseen
if page and new == 0:
    # whole page already known => ties at cursor; advance strictly by +1 second
    stall = 1
    try:
        dt = datetime.datetime.fromisoformat(maxseen.replace("Z", "+00:00"))
        next_cursor = (dt + datetime.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        next_cursor = maxseen

print(f"NEW={new} BATCH={len(page)} TOTAL={len(acc)} MAXSEEN={maxseen} NEXT_CURSOR={next_cursor} STALL={stall}")
