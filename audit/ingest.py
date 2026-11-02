import json, sys, csv, io, os

# Usage: python3 -I ingest.py <tool_result_file> <out_csv>
# Reads the MCP tool-result JSON array [{type,text}], concatenates text,
# which is CSV. Appends rows to out_csv (dedup header), prints count + cursor.

src = sys.argv[1]
out = sys.argv[2]

with open(src, 'r') as f:
    data = json.load(f)

# concatenate all text parts, skipping apiUsageCosts metadata parts
parts = []
for part in data:
    if not isinstance(part, dict):
        continue
    t = part.get("text", "")
    if t.lstrip().startswith('{"apiUsageCosts'):
        continue
    parts.append(t)
text = "".join(parts)

# text may itself be a CSV string; parse
reader = list(csv.reader(io.StringIO(text)))
if not reader:
    print("NO ROWS")
    sys.exit(0)

header = reader[0]
rows = reader[1:]

# write/append
exists = os.path.exists(out)
with open(out, 'a', newline='') as f:
    w = csv.writer(f)
    if not exists:
        w.writerow(header)
    for r in rows:
        w.writerow(r)

# find first_seen_link column for cursor
try:
    idx = header.index('first_seen_link')
    last = rows[-1][idx] if rows else None
except ValueError:
    last = None

print("header:", header)
print("rows_this_page:", len(rows))
print("cursor_first_seen_link:", last)

# total rows in out
with open(out) as f:
    total = sum(1 for _ in f) - 1
print("total_rows_in_out:", total)
