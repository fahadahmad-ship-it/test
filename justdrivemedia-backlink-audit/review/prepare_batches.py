"""Package per-domain evidence into JSONL batches for the reviewer agents."""
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
WB = HERE.parent / "justdrivemedia-backlink-audit.xlsx"
d = pd.read_excel(WB, sheet_name="Domain Audit")
b = pd.read_excel(WB, sheet_name="All Backlinks")


def cut(s, n):
    if not isinstance(s, str):
        return None
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + "…"


def num(v):
    return None if pd.isna(v) else (int(v) if float(v).is_integer() else float(v))


ev = {}
for dom, g in b.groupby("Referring Domain"):
    anchors = (g.assign(a=g["Anchor Text"].fillna("(empty / image link)").astype(str))
                 .groupby(["a", "Anchor Type"]).size().sort_values(ascending=False))
    pages = g.drop_duplicates("Linking Page URL").head(2)
    ev[dom] = {
        "anchors": [{"text": cut(a, 140), "type": t, "count": int(n)} for (a, t), n in anchors.head(4).items()],
        "distinct_anchors": int(len(anchors)),
        "link_types": g["Link Type"].value_counts().to_dict(),
        "pages": [{"url": cut(r["Linking Page URL"], 150), "title": cut(r["Linking Page Title"], 100),
                   "outbound_links_on_page": num(r["Outbound Links on Page"]),
                   "category": cut(r["Page Category"], 60),
                   "text_around_link": cut(r["Text Around Link"], 140)} for _, r in pages.iterrows()],
    }

recs = []
for _, r in d.iterrows():
    recs.append({
        "domain": r["Domain"],
        "rule_verdict": r["Verdict"],
        "rule_cluster": r["Spam Network / Cluster"] if isinstance(r["Spam Network / Cluster"], str) else None,
        "first_seen": str(r["First Seen"])[:10],
        "ahrefs": {"DR": num(r["Ahrefs DR"]), "organic_traffic": num(r["Ahrefs Organic Traffic"]),
                   "ranking_keywords": num(r["Ahrefs Ranking Keywords"]), "spam_flag": r["Ahrefs Spam Flag"] if isinstance(r["Ahrefs Spam Flag"], str) else None,
                   "links": num(r["Ahrefs Links"]), "dofollow_links": num(r["Ahrefs Dofollow Links"])},
        "semrush": {"authority_score": num(r["Semrush Authority Score"]), "backlinks": num(r["Semrush Backlinks"]),
                    "ip": r["IP"] if isinstance(r["IP"], str) else None, "country": r["Country"] if isinstance(r["Country"], str) else None},
        "backlinks_analysed": num(r["Backlinks Analysed"]),
        **ev.get(r["Domain"], {"anchors": [], "distinct_anchors": 0, "link_types": {}, "pages": []}),
    })
df = pd.DataFrame({"rec": recs, "domain": d["Domain"], "verdict": d["Verdict"], "cluster": d["Spam Network / Cluster"].fillna("")})

spam = df["verdict"] == "Spam – Disavow"
words = df["domain"].str.contains(r"backlink|baclink|seo|rank|serp|checker|dapa|directory|directoy|link|outrank|crawl|index|"
                                  r"boost|pbn|traffic|casino|slot|anchor|authority", case=False)
numeric = df["domain"].str.fullmatch(r"\d+\.xyz")
spam_anchors = d["Spammy Anchors"].fillna(0) > 0
quality = ((d["Ahrefs Organic Traffic"].fillna(0) >= 10) | (d["Ahrefs Ranking Keywords"].fillna(0) >= 3)
           | (d["Semrush Authority Score"].fillna(0) >= 10))
weak = spam & ~numeric & (quality | (~spam_anchors & ~words))
directories = spam & (df["cluster"] == "Low-quality web directories")

batches = {
    "01": df[~spam],                                  # everything currently kept
    "02": df[weak | directories],                     # weakest spam cases + directories
}
rest = df[spam & ~weak & ~directories].sort_values(["cluster", "domain"])
chunks = [rest.iloc[i::1] for i in range(1)]
n = 6
size = -(-len(rest) // n)
for i in range(n):
    batches[f"{i + 3:02d}"] = rest.iloc[i * size:(i + 1) * size]

total = 0
for k, part in batches.items():
    path = HERE / f"batch_{k}.jsonl"
    with path.open("w") as fh:
        for rec in part["rec"]:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    total += len(part)
    print(k, len(part), f"{path.stat().st_size / 1024:.0f} KB", part["cluster"].value_counts().head(3).to_dict())
print("total", total, "of", len(d))
