"""Shared dataset builder: reads data, classifies, returns everything the
workbook + disavow files + verifier need. Import this; do not re-roll parsing."""
import os, glob, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(__file__))
import load, classify

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

MONEY = "premierblindsanddesigns.com"
REDIRECTS = {"thepremierdesigns.com"}   # owned domains that 301 into the money site

def _num(x):
    try: return float(x)
    except: return None

def _ts(x):
    try:
        t = int(float(x))
        if t > 0:
            return datetime.fromtimestamp(t, tz=timezone.utc).replace(tzinfo=None)
    except: pass
    return None

def link_property(l):
    """The Search-Console property a link is attributed to: redirect host if the
    link reaches the site through a 301, else the target host."""
    r = load.host_of(l["redirect_url"])
    if r:
        return r
    return load.host_of(l["target_url"])

def load_metrics():
    """Per-domain Semrush metrics pulled via fan-out:
    domain;ascore;rds;backlinks_total;organic_keywords;organic_traffic"""
    m = {}
    for p in glob.glob(os.path.join(DATA,"metrics","metrics_*.csv")):
        for line in open(p, encoding="utf-8"):
            line=line.strip()
            if not line: continue
            parts=line.split(";")
            if len(parts) < 6: continue
            d=parts[0].strip().lower()
            def i(x):
                try: return int(float(x))
                except: return 0
            m[d]={"ascore":i(parts[1]),"rds":i(parts[2]),"total":i(parts[3]),
                  "orgkw":i(parts[4]),"traffic":i(parts[5])}
    return m

AHREFS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ahrefs_in")

def _ahrefs_unix(s):
    s=(s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d"):
        try: return str(int(datetime.strptime(s,fmt).timestamp()))
        except: pass
    return ""

def _canonkey(l):
    import load_ahrefs
    return (load_ahrefs.canon(l["source_url"]), load_ahrefs.canon(l["target_url"]),
            (l["anchor"] or "").strip().lower())

def build():
    bl, dropped, rec = load.read_backlinks(sorted(glob.glob(os.path.join(DATA,"fetch","bl_*.csv"))))
    rd, rddrop = load.read_refdomains(sorted(glob.glob(os.path.join(DATA,"rd","rd_*.csv"))))
    rdmap = {r["domain"].strip().lower(): r for r in rd}
    metrics = load_metrics()
    for l in bl:
        l["source"] = "Semrush"; l["http"] = (l.get("response_code") or "").strip()

    # ---- merge Ahrefs (discovery + link detail + HTTP status; never a metric) ----
    ahrefs_names = set()
    ablpath = os.path.join(AHREFS_DIR, "bl.tsv")
    ahrefs_new = ahrefs_both = 0
    if os.path.exists(ablpath):
        import load_ahrefs
        abl = load_ahrefs.backlinks(ablpath)
        ard = load_ahrefs.refdomains(os.path.join(AHREFS_DIR, "rd.tsv"))
        ahrefs_names = {r["domain"].strip().lower() for r in ard}
        index = {}
        for l in bl: index.setdefault(_canonkey(l), l)
        for al in abl:
            k = (load_ahrefs.canon(al["source_url"]), load_ahrefs.canon(al["target_url"]),
                 (al["anchor"] or "").strip().lower())
            if k in index:
                s = index[k]
                s["source"] = "Semrush, Ahrefs"
                if not s["http"]: s["http"] = al["http"]
                ahrefs_both += 1
            else:
                bl.append({
                    "source_url": al["source_url"], "source_title": al["source_title"],
                    "target_url": al["target_url"], "anchor": al["anchor"],
                    "nofollow": al["nofollow"], "first_seen": _ahrefs_unix(al["first_seen"]),
                    "last_seen": _ahrefs_unix(al["last_seen"]), "response_code": al["http"],
                    "redirect_url": "", "page_ascore": "", "source": "Ahrefs", "http": al["http"],
                })
                ahrefs_new += 1

    match = load.build_refdomain_matcher(set(rdmap.keys()) | ahrefs_names)

    groups = defaultdict(list)
    for l in bl:
        groups[match(l["source_url"])].append(l)

    domains = {}
    links_out = []
    for d in sorted(set(groups) | set(rdmap)):
        links = groups.get(d, [])
        if not links:
            continue  # refdomain row whose links folded into another host key
        r = rdmap.get(d)
        rd_asc = _num(r["domain_ascore"]) if r else None
        mt = metrics.get(d)
        # prefer the backlinks_overview Authority Score; fall back to the
        # referring-domain figure if the per-domain pull failed (metric 0 but rd>0)
        if mt and mt["ascore"] > 0:
            asc = float(mt["ascore"])
        elif rd_asc is not None:
            asc = rd_asc
        elif mt:
            asc = float(mt["ascore"])
        else:
            asc = None
        status, reason = classify.classify_domain(d, links, asc)

        dof = sum(1 for l in links if l["nofollow"].strip().lower() == "false")
        nof = len(links) - dof
        anchors = Counter((l["anchor"] or "").strip() for l in links)
        top_anchor = anchors.most_common(1)[0][0] if anchors else ""
        props = []
        for l in links:
            p = link_property(l)
            tag = p + (" (redirect)" if load.host_of(l["redirect_url"]) in REDIRECTS else "")
            if tag not in props:
                props.append(tag)
        first_seens = [_ts(l["first_seen"]) for l in links if _ts(l["first_seen"])]
        if r and _ts(r["first_seen"]):
            first_seens.append(_ts(r["first_seen"]))
        first_seen = min(first_seens) if first_seens else None
        # example linking page: prefer dofollow + a live HTTP 200 (Semrush or Ahrefs)
        def rank(l):
            http = (l.get("http") or l.get("response_code") or "").strip()
            return (0 if l["nofollow"].strip().lower()=="false" else 1,
                    0 if http=="200" else 1)
        ex = sorted(links, key=rank)[0]
        # Source = which tool(s) found this domain's links
        srcs = {l.get("source","Semrush") for l in links}
        flat = set()
        for s in srcs: flat.update(x.strip() for x in s.split(","))
        source = "Semrush, Ahrefs" if {"Semrush","Ahrefs"} <= flat else ("Ahrefs" if flat=={"Ahrefs"} else "Semrush")

        in_disavow = ("Yes" if status=="Spam (Disavow)" else
                      "Held" if status.startswith("Held") else "No")
        disavow_line = ("domain:"+d) if status=="Spam (Disavow)" else ""

        domains[d] = {
            "domain": d, "status": status, "reason": reason,
            "ascore": asc if asc is not None else 0.0,
            "backlinks": len(links),
            "rds": (mt["rds"] if mt else None),        # referring-domain's own RD count (backlinks_overview)
            "traffic": (mt["traffic"] if mt else 0),   # organic traffic (domain_rank, us)
            "orgkw": (mt["orgkw"] if mt else 0),       # organic keywords (domain_rank, us)
            "in_disavow": in_disavow,
            "points_to": ", ".join(props),
            "dofollow": dof, "nofollow": nof,
            "first_seen": first_seen,
            "top_anchor": top_anchor,
            "example_page": ex["source_url"],
            "example_title": ex["source_title"],
            "source": source,
            "ip": (r["ip"] if r else "") or "",
            "disavow_line": disavow_line,
            "properties": {link_property(l) for l in links},
            "links": links,
        }
        for l in links:
            links_out.append({
                "refdomain": d, "status": status, "tool": l.get("source","Semrush"),
                "anchor": l["anchor"], "anchor_type": classify.anchor_type(l["anchor"]),
                "link_type": "Dofollow" if l["nofollow"].strip().lower()=="false" else "Nofollow",
                "page_url": l["source_url"], "page_title": l["source_title"],
                "target_url": l["target_url"],
            })

    # ---- anchor analysis (one row per distinct anchor) ----
    total_links = len(links_out)
    anchor_rows = defaultdict(lambda: {"bl":0, "doms":set(), "spamdoms":set(), "type":""})
    for lo in links_out:
        a = lo["anchor"].strip()
        rec0 = anchor_rows[a]
        rec0["bl"] += 1
        rec0["doms"].add(lo["refdomain"])
        rec0["type"] = lo["anchor_type"]
        if lo["status"].startswith("Spam"):
            rec0["spamdoms"].add(lo["refdomain"])

    # ---- disavow redundancy: child removed if any other disavow domain is its suffix ----
    disavow_domains = sorted(d for d,v in domains.items() if v["status"]=="Spam (Disavow)")
    dset = set(disavow_domains)
    def redundant(d):
        for p in dset:
            if p != d and d.endswith("." + p):
                return True
        return False
    emitted = [d for d in disavow_domains if not redundant(d)]
    redundant_children = [d for d in disavow_domains if redundant(d)]

    return {
        "domains": domains, "links": links_out, "anchors": anchor_rows,
        "total_links": total_links, "dropped": dropped, "recovered": rec,
        "disavow_domains": disavow_domains, "emitted": emitted,
        "redundant_children": redundant_children,
        "ahrefs_new": ahrefs_new, "ahrefs_both": ahrefs_both,
    }

if __name__ == "__main__":
    ds = build()
    from collections import Counter as C
    dist = C(v["status"] for v in ds["domains"].values())
    print("domains=%d links=%d dropped=%d" % (len(ds["domains"]), len(ds["links"]), ds["dropped"]))
    for k,v in dist.most_common(): print("  %-28s %d" % (k,v))
    print("disavow domains=%d emitted lines=%d redundant children=%d" %
          (len(ds["disavow_domains"]), len(ds["emitted"]), len(ds["redundant_children"])))
    print("redundant sample:", ds["redundant_children"][:10])
