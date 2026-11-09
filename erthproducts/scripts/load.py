"""Load + merge Semrush and Ahrefs data into per-referring-domain records.
Usage: python3 -I load.py <datadir> <out_merged.json>
Semrush = priority for metrics; Ahrefs adds discovery domains, link detail, HTTP status.
"""
import sys, os, json, glob, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

DATADIR = sys.argv[1]
OUT = sys.argv[2]

# ---------- 1. Semrush backlinks ----------
bl_path = os.path.join(DATADIR, "fetch", "semrush_backlinks.csv")
_, sem_bl, bad_bl = C.read_semrush_csv(bl_path, 10)
print(f"semrush backlinks: {len(sem_bl)} (malformed {bad_bl})")

# ---------- 2. Semrush refdomains ----------
sem_rd = {}
for p in sorted(glob.glob(os.path.join(DATADIR, "rd", "*.csv"))):
    _, rows, bad = C.read_semrush_csv(p, 9)
    for r in rows:
        d = r["domain"].strip().lower()
        if d and d not in sem_rd:
            sem_rd[d] = r
print(f"semrush refdomains: {len(sem_rd)}")

# ---------- 3. Ahrefs refdomains ----------
ah_rd = {}
ap = os.path.join(DATADIR, "ahrefs", "ahrefs_refdomains.csv")
if os.path.exists(ap):
    with open(ap, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            d = (r.get("domain") or "").strip().lower()
            if d:
                ah_rd[d] = r
print(f"ahrefs refdomains: {len(ah_rd)}")

# ---------- 4. Ahrefs backlinks ----------
ah_bl = []
# Prefer the final merged/deduped file; fall back to intermediate page dumps.
final_bl = os.path.join(DATADIR, "ahrefs", "ahrefs_backlinks.json")
if os.path.exists(final_bl):
    cand = [final_bl]
else:
    cand = sorted(glob.glob(os.path.join(DATADIR, "ahrefs", "_bl_pages", "*")))
def pull_rows(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("backlinks", "all_backlinks", "data", "rows", "items"):
            if isinstance(obj.get(k), list):
                return obj[k]
    return []
for p in sorted(cand):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            ah_bl += pull_rows(json.load(fh))
    except Exception as e:
        print(f"  warn: could not parse {p}: {e}")
print(f"ahrefs backlinks: {len(ah_bl)}")

def ah_get(r, *names):
    for n in names:
        if n in r and r[n] not in (None, ""):
            return r[n]
    return None

# ---------- 5. Build unified link list ----------
def mk_link(source_url, source_title, target_url, anchor, nofollow, first_seen,
            last_seen, resp, redirect_url, tool):
    return {
        "source_url": source_url or "", "source_title": C.unescape(source_title) or "",
        "target_url": target_url or "", "anchor": C.unescape(anchor) or "",
        "nofollow": bool(nofollow), "first_seen": first_seen, "last_seen": last_seen,
        "response_code": str(resp) if resp not in (None, "") else "",
        "redirect_url": redirect_url or "", "tool": tool,
        "ref_host": C.canon_host(source_url),
    }

def key(l):
    return (C.canon_host(l["source_url"]) + C.path_of(l["source_url"]).rstrip("/"),
            C.canon_host(l["target_url"]) + C.path_of(l["target_url"]).rstrip("/"),
            (l["anchor"] or "").strip().lower())

links = {}
for r in sem_bl:
    l = mk_link(r["source_url"], r["source_title"], r["target_url"], r["anchor"],
                r["nofollow"].strip().lower() == "true", r["first_seen"], r["last_seen"],
                r["response_code"], r.get("redirect_url", ""), "Semrush")
    links[key(l)] = l

ah_added = 0
for r in ah_bl:
    su = ah_get(r, "url_from", "source_url", "urlFrom")
    tu = ah_get(r, "url_to", "target_url", "urlTo")
    an = ah_get(r, "anchor", "anchor_text") or ""
    nf = ah_get(r, "nofollow", "is_nofollow")
    nf = (str(nf).lower() in ("true", "1", "yes")) if nf is not None else False
    fs = ah_get(r, "first_seen", "first_seen_link")
    ls = ah_get(r, "last_seen", "last_visited", "last_seen_link")
    hc = ah_get(r, "http_code", "referring_page_http_code", "http_code_target")
    st = ah_get(r, "title", "page_title", "source_title") or ""
    l = mk_link(su, st, tu, an, nf, fs, ls, hc, "", "Ahrefs")
    k = key(l)
    if k in links:
        links[k]["tool"] = "Both"
        if not links[k]["response_code"] and l["response_code"]:
            links[k]["response_code"] = l["response_code"]
    else:
        links[k] = l
        ah_added += 1
print(f"merged links: {len(links)} (ahrefs-only added {ah_added})")

# ---------- 6. Group by referring domain (registrable) ----------
recs = {}
def rec_for(host):
    rd = C.reg_domain(host)
    if rd not in recs:
        recs[rd] = {"domain": rd, "hosts": set(), "links": []}
    recs[rd]["hosts"].add(host)
    return recs[rd]

for l in links.values():
    host = l["ref_host"] or C.reg_domain(C.canon_host(l["source_url"]))
    if not host:
        continue
    rec_for(host)["links"].append(l)

# domains known only from refdomain exports but with no captured link -> still create row
for d in list(sem_rd) + list(ah_rd):
    rd = C.reg_domain(d)
    if rd not in recs:
        recs[rd] = {"domain": rd, "hosts": {d}, "links": []}

# ---------- 7. Attach Semrush/Ahrefs domain metrics + aggregates ----------
def first_num(*vals):
    for v in vals:
        if v not in (None, ""):
            try:
                return float(str(v).rstrip("."))
            except Exception:
                pass
    return None

out = []
for rd, rec in recs.items():
    hosts = rec["hosts"]
    srd = None
    for h in list(hosts) + [rd]:
        if h in sem_rd:
            srd = sem_rd[h]; break
    ard = None
    for h in list(hosts) + [rd]:
        if h in ah_rd:
            ard = ah_rd[h]; break
    ls = rec["links"]
    dofollow = sum(1 for l in ls if not l["nofollow"])
    nofollow = sum(1 for l in ls if l["nofollow"])
    # first seen = earliest across links + refdomain exports
    dates = [C.ts_to_date(l["first_seen"]) for l in ls]
    if srd:
        dates.append(C.ts_to_date(srd.get("first_seen")))
    if ard:
        dates.append(C.ts_to_date(ard.get("first_seen")))
    dates = [d for d in dates if d]
    first_seen = min(dates).isoformat() if dates else None
    # links point to: home vs deep
    homes = sum(1 for l in ls if C.is_home(l["target_url"]))
    deeps = len(ls) - homes
    if ls:
        points = "Home page" if deeps == 0 else ("Product pages" if homes == 0 else "Home + product pages")
    else:
        points = ""
    tool = "Both" if any(l["tool"] == "Both" for l in ls) else (
        "Semrush+Ahrefs" if {l["tool"] for l in ls} >= {"Semrush", "Ahrefs"} else (
        ls[0]["tool"] if ls else ("Semrush" if srd else "Ahrefs")))
    out.append({
        "domain": rd,
        "hosts": sorted(hosts),
        "as": first_num(srd and srd.get("domain_ascore")),
        "sem_backlinks": int(first_num(srd and srd.get("backlinks_num")) or len(ls)),
        "ip": (srd or {}).get("ip", "") if srd else "",
        "country": (srd or {}).get("country", "") if srd else "",
        "dofollow": dofollow, "nofollow": nofollow,
        "first_seen": first_seen,
        "links_point_to": points,
        "n_links": len(ls),
        "tool": tool,
        "links": ls,
        "in_semrush": srd is not None,
        "in_ahrefs": ard is not None,
    })

out.sort(key=lambda r: r["domain"])
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False)
print(f"WROTE {len(out)} referring-domain records -> {OUT}")
print(f"  with >=1 dofollow link: {sum(1 for r in out if r['dofollow'])}")
print(f"  no links captured:      {sum(1 for r in out if r['n_links']==0)}")
