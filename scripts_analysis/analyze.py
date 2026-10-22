import json, csv, re
from collections import Counter, defaultdict

DOMAINS = "/home/user/test/audit/data/classified_domains.json"
LINKS = "/home/user/test/audit/data/classified_links.csv"

with open(DOMAINS, encoding="utf-8") as f:
    dom = json.load(f)

links = []
with open(LINKS, encoding="utf-8") as f:
    rdr = csv.DictReader(f)  # comma-delimited UTF-8
    for row in rdr:
        links.append(row)

print("num domains:", len(dom))
print("num links:", len(links))
sc = Counter(d.get("status") for d in dom.values())
print("status counts:", dict(sc))
print("link cols:", list(links[0].keys()))

keepheld = {k:v for k,v in dom.items() if v.get("status","").startswith(("Keep","Held"))}
flagged = {k:v for k,v in keepheld.items() if v.get("spam_flag")}
print("keep/held:", len(keepheld), " keep/held spam-flagged:", len(flagged))
print("keep spam-flagged:", sum(1 for v in flagged.values() if v["status"]=="Keep"))

# ---- spam signature regexes (visible evidence) ----
SPAM = re.compile(r"(buy\s+back ?links?|back ?links? for sale|sell\s+back ?links?|"
    r"\bDA\s?\d{2}\b|\bPA\s?\d{2}\b|DA\d+\s*PA\d+|increase (your )?domain authority|"
    r"boost (your )?(domain authority|ranking|seo)|guest post|pbn|private blog network|"
    r"casino|slot(s| gacor| online)|judi|togel|poker|betting|sportsbook|baccarat|"
    r"viagra|cialis|pharma|tadalafil|sildenafil|rx\b|canadian pharmacy|"
    r"escort|porn|xxx|\bsex\b|replica|rolex|\bloan\b|payday|forex|bitcoin|crypto|"
    r"essay writing|write my essay|cheap|\bseo services?\b|rank higher|"
    r"domain rating|dofollow link|link building service|google ranking)", re.I)

HOST_SPAM = re.compile(r"(casino|poker|slot|judi|togel|betting|pharma|viagra|cialis|"
    r"escort|porn|xxx|replica|loan|payday|forex|crypto|seo-?|backlink|buy-|cheap)", re.I)

def scan(text):
    if not text: return None
    m = SPAM.search(text)
    return m.group(0) if m else None

# Build per-domain link info
dlinks = defaultdict(list)
for r in links:
    dlinks[r["referring_domain"]].append(r)

# Anchor types that indicate commercial exact-match / money page => Held
def has_commercial(d):
    for r in dlinks.get(d, []):
        at = (r.get("anchor_type") or "").lower()
        if "exact" in at or "commercial" in at or "money" in at:
            return True
    return False

results = []
for d, v in keepheld.items():
    status = v["status"]
    dofollow = int(v.get("dofollow") or 0)
    nofollow = int(v.get("nofollow") or 0)
    ev = []
    # scan domain-level fields
    for field in ("top_anchor","example_title","example_url","domain"):
        hit = scan(str(v.get(field) or ""))
        if hit: ev.append((field, hit, str(v.get(field))))
    # host spam check on domain name
    hh = HOST_SPAM.search(d)
    if hh: ev.append(("host", hh.group(0), d))
    # scan every link row's anchor + title + url + referring domain
    dofollow_spam = False
    for r in dlinks.get(d, []):
        for col in ("anchor","title","url"):
            hit = scan(str(r.get(col) or ""))
            if hit:
                nf = str(r.get("nofollow","")).strip().lower()
                is_do = nf in ("false","0","","no")
                ev.append((col, hit, str(r.get(col))[:120], "dofollow" if is_do else "nofollow"))
                if is_do: dofollow_spam = True
    if ev:
        results.append({
            "domain": d, "status": status, "dofollow": dofollow, "nofollow": nofollow,
            "spam_flag": v.get("spam_flag"), "dofollow_spam": dofollow_spam,
            "commercial": has_commercial(d), "ev": ev,
        })

print("\n==== CANDIDATES WITH VISIBLE SPAM EVIDENCE:", len(results), "====")
for r in results:
    print("\n###", r["domain"], "| status:", r["status"], "| dofollow:", r["dofollow"],
          "nofollow:", r["nofollow"], "| spam_flag:", r["spam_flag"],
          "| dofollow_spam:", r["dofollow_spam"], "| commercial:", r["commercial"])
    for e in r["ev"][:6]:
        print("   -", e)
