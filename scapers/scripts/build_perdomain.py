#!/usr/bin/env python3
# Aggregate Ahrefs link-level CSV into per-domain JSON for the classifier.
# python3 -I scapers/scripts/build_perdomain.py <ahrefs_backlinks.csv> <out_perdomain.json>
import sys, csv, json, collections

def detect_delim(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.readline()
    for d in [",",";","\t"]:
        if d in head:
            return d
    return ","

def truthy(v):
    return str(v).strip().lower() in ("true","1","yes","t")

def main():
    src, out = sys.argv[1:3]
    delim = detect_delim(src)
    rows = []
    with open(src, encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f, delimiter=delim)
        cols = {c.lower(): c for c in (r.fieldnames or [])}
        def g(row, *names):
            for n in names:
                if n in cols: return row.get(cols[n], "")
            return ""
        for row in r:
            root = (g(row,"root_name_source") or g(row,"name_source")).strip().lower()
            host = (g(row,"name_source") or root).strip().lower()
            if not root:
                continue
            rows.append(dict(
                root=root, host=host,
                url_from=g(row,"url_from"), url_to=g(row,"url_to"),
                anchor=g(row,"anchor"),
                dofollow=truthy(g(row,"is_dofollow")),
                nofollow=truthy(g(row,"is_nofollow")),
                http=str(g(row,"http_code")).strip(),
                title=g(row,"title"),
            ))
    perdom = {}
    by_root = collections.defaultdict(list)
    for x in rows:
        by_root[x["root"]].append(x)
    for root, items in by_root.items():
        anchors = collections.Counter(x["anchor"] for x in items)
        do = sum(1 for x in items if x["dofollow"])
        nf = sum(1 for x in items if x["nofollow"] or not x["dofollow"])
        targets = sorted({x["url_to"] for x in items if x["url_to"]})
        # example: prefer http 200 + dofollow + a real page
        def score(x):
            return (x["http"]=="200", x["dofollow"], len(x["url_from"]))
        best = sorted(items, key=score, reverse=True)[0]
        top_anchor = anchors.most_common(1)[0][0] if anchors else ""
        perdom[root] = dict(
            anchors=[[a, c] for a, c in anchors.most_common()],
            dofollow=do, nofollow=nf,
            targets=targets[:50],
            top_anchor=top_anchor,
            example_url=best["url_from"], example_title=best["title"],
            hosts=sorted({x["host"] for x in items}),
        )
    json.dump(perdom, open(out, "w", encoding="utf-8"))
    print("per-domain roots:", len(perdom), "from", len(rows), "ahrefs links")

if __name__ == "__main__":
    main()
