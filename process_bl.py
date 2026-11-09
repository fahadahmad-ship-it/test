import json, sys, csv, io, os

RESULTS = sys.argv[1]
OUT = "/home/user/test/data/ahrefs_backlinks.csv"
HEADER = "name_source,root_name_source,anchor,is_dofollow,is_nofollow,link_type,url_from,url_to,title,is_spam,first_seen_link,domain_rating_source"

data = json.load(open(RESULTS))
txt = "".join(p["text"] for p in data)
lines = txt.split("\n")
# drop trailing non-CSV marker lines
clean = [l for l in lines if not l.startswith("Display these results")
         and not l.startswith('{"apiUsageCosts"')]
# strip trailing empty lines
while clean and clean[-1] == "":
    clean.pop()
csvtext = "\n".join(clean)
rows = list(csv.reader(io.StringIO(csvtext)))
# first row is header
assert rows[0][0] == "name_source", rows[0][:2]
datarows = rows[1:]
page_data = len(datarows)

# units
units = None
for l in lines:
    if l.startswith('{"apiUsageCosts"'):
        units = json.loads(l)["apiUsageCosts"]["units-cost-total-actual"]

# build seen set from existing output
seen = set()
exists = os.path.exists(OUT)
if exists:
    with open(OUT, newline="") as f:
        r = csv.reader(f)
        next(r, None)  # header
        for row in r:
            if len(row) >= 8:
                seen.add((row[6], row[7], row[2]))

new = 0
out_f = open(OUT, "a", newline="")
w = csv.writer(out_f, lineterminator="\n")
if not exists:
    out_f.write(HEADER + "\n")
last_url_from = None
for row in datarows:
    if len(row) < 12:
        continue
    last_url_from = row[6]
    triple = (row[6], row[7], row[2])
    if triple in seen:
        continue
    seen.add(triple)
    w.writerow(row)
    new += 1
out_f.close()

# total data rows now
total = 0
with open(OUT, newline="") as f:
    total = sum(1 for _ in f) - 1

print(f"page_data_rows={page_data} new_rows_appended={new} total_now={total} units={units}")
print(f"last_url_from={last_url_from}")
