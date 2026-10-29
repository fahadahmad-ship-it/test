import sys
# argv[1] = path to raw batch data file (starts with header line), argv[2] = output csv
raw = open(sys.argv[1]).read().split("\n")
out = sys.argv[2]
rows = []
for i, line in enumerate(raw):
    if i == 0:
        continue  # skip per-batch header
    if line.strip() == "":
        continue
    rows.append(line)
with open(out, "a") as f:
    for r in rows:
        f.write(r + "\n")
print("appended", len(rows))
