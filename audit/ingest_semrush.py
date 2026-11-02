import json, sys, csv, io, os

# Usage: python3 -I ingest_semrush.py <tool_result_file> <out_csv>
# Semrush execute_report result: either {data: "...;csv..."} OR the MCP
# tool-result array [{type,text}] whose text is that JSON. Handles both.

src = sys.argv[1]
out = sys.argv[2]

raw = open(src).read()
obj = json.loads(raw)

# unwrap possible [{type,text}] shape
if isinstance(obj, list):
    text = "".join(p.get("text", "") for p in obj if isinstance(p, dict)
                    and not p.get("text", "").lstrip().startswith('{"apiUsageCosts'))
    obj = json.loads(text)

data = obj["data"] if isinstance(obj, dict) else obj
# semrush uses ';' delimiter
reader = list(csv.reader(io.StringIO(data), delimiter=';'))
header = reader[0]
rows = reader[1:]

exists = os.path.exists(out)
with open(out, 'a', newline='') as f:
    w = csv.writer(f)
    if not exists:
        w.writerow(header)
    for r in rows:
        w.writerow(r)

print("header:", header)
print("rows_this_page:", len(rows))
with open(out) as f:
    total = sum(1 for _ in f) - 1
print("total_rows_in_out:", total)
# print pagination metadata if present
md = obj.get("metadata", {}) if isinstance(obj, dict) else {}
print("pagination:", md.get("pagination"))
