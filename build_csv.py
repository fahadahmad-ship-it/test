import csv, json, sys

def build(jsonl_path, csv_path, cols, keycol):
    seen = set()
    rows = []
    dupes = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            k = obj.get(keycol)
            if k in seen:
                dupes += 1
                continue
            seen.add(k)
            rows.append(obj)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for obj in rows:
            w.writerow([obj.get(c, "") for c in cols])
    return len(rows), dupes

ref_cols = ["domain","domain_rating","links_to_target","dofollow_links","traffic_domain",
            "dofollow_refdomains","first_seen","positions_source_domain","ip_source","is_spam"]
bl_cols = ["root_name_source","anchor","is_dofollow","is_nofollow","link_type","url_from",
           "title","url_to","is_sponsored","is_ugc","domain_rating_source","ip_source","is_spam"]

n1, d1 = build("/home/user/test/data/refdomains.jsonl", "/home/user/test/data/refdomains.csv", ref_cols, "domain")
n2, d2 = build("/home/user/test/data/backlinks.jsonl", "/home/user/test/data/backlinks.csv", bl_cols, "root_name_source")
print(f"refdomains: {n1} rows, {d1} dupes removed")
print(f"backlinks: {n2} rows, {d2} dupes removed")
