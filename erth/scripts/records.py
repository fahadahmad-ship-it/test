"""Assemble the 7-tab record set + disavow files from the classified pipeline."""
import os
import sys
import glob
import json
import collections
import datetime as dt
from urllib.parse import urlsplit

sys.path.insert(0, "erth/scripts")
import pipeline as P
import classify as C
import build as B
from load import host_of, load_csv_comma

CLIENT_NAME = "Erth Products"
MONEY = "erthproducts.com"
DISAVOW_FILE = "disavow_erthproducts.txt"

STATUS_ORDER = ["Spam (Disavow)", "Held (Pending Partner)", "Held (Nofollow, No Action)",
                "Spam (Nofollow, No Action)", "Keep", "Own Site"]
STATUS_MEANING = {
    "Spam (Disavow)": "Confirmed spam with at least one dofollow link. Included in the disavow file.",
    "Held (Pending Partner)": "Exact match commercial anchor, or a link aimed at a deep product, capability or industry page. Held for the previous SEO partner to confirm before any disavow.",
    "Held (Nofollow, No Action)": "Same, but every link is nofollow so it passes no ranking value. No disavow needed either way.",
    "Spam (Nofollow, No Action)": "Spam, but every link is nofollow and passes no ranking value, so no disavow is needed.",
    "Keep": "Genuine or harmless link. Keep.",
    "Own Site": "Client owned domain that redirects into the site.",
}


def load_metrics():
    p = "erth/data/ahrefs/metrics.csv"
    if not os.path.exists(p):
        return {}
    out = {}
    for r in load_csv_comma(p):
        out[r["domain"].strip().lower()] = r
    return out


def path_of(url):
    return urlsplit(url if "//" in url else "http://" + url).path.rstrip("/")


def site_type(host, title, ascore):
    h = host.lower()
    t = (title or "").lower()
    if ascore and ascore >= 20:
        return "Genuine site"
    if any(k in h for k in ["bookmark", "socialcrowd", "mark.", "marks."]):
        return "Social bookmarking site"
    if any(k in h for k in ["blogspot", "blog", "news", "article", "medium", "wordpress"]):
        return "Guest article or content farm"
    if any(k in h for k in ["director", "listing", "list", "biz", "local", "dir", "find",
                            "lookup", "business", "yellow", "zip", "chamber", "spot"]):
        return "Low quality web directory"
    return "Low quality web directory"


def example_page(d):
    """Pick the best example linking page: a dofollow live (200) link, else any."""
    best = None
    for r in d["links"]:
        http = str(r.get("http") or "")
        if not r["nofollow"] and http in ("200", "200.0"):
            return r
        if best is None:
            best = r
    return best or (d["links"][0] if d["links"] else None)


def top_anchor(d):
    if not d["links"]:
        return ""
    cnt = collections.Counter((r["anchor"] or "").strip() for r in d["links"])
    return cnt.most_common(1)[0][0]


def is_subdomain_of_any(dom, allset):
    for p in allset:
        if p != dom and dom.endswith("." + p):
            return p
    return None


def assemble():
    canon, links, by = P.run()
    metrics = load_metrics()

    # ---- redundancy: child disavow under a disavowed parent ----
    disavow_domains = {dom for dom, d in by.items() if d["status"] == "Spam (Disavow)"}
    covered = {}
    for dom in disavow_domains:
        parent = is_subdomain_of_any(dom, disavow_domains)
        if parent:
            covered[dom] = parent

    def anchor_type_of(r):
        return C.anchor_type(r["anchor"], r.get("title", ""), r.get("url_from", ""),
                             host_of(r.get("url_from", "")))

    # ---------- All Backlinks rows ----------
    abl_rows = []
    for dom in sorted(by):
        d = by[dom]
        for r in d["links"]:
            abl_rows.append({
                "domain": dom, "status": d["status"], "tool": r["tool"],
                "anchor": r["anchor"], "anchor_type": anchor_type_of(r),
                "link_type": "Nofollow" if r["nofollow"] else "Dofollow",
                "url_from": r["url_from"], "title": r.get("title", ""), "target": r["target"],
            })

    # ---------- Referring Domain Audit rows ----------
    rda_rows = []
    for dom in sorted(by):
        d = by[dom]
        m = metrics.get(dom, {})
        dof = sum(1 for r in d["links"] if not r["nofollow"])
        nof = sum(1 for r in d["links"] if r["nofollow"])
        st = d["status"]
        if st == "Spam (Disavow)":
            indis = "Covered by parent" if dom in covered else "Yes"
        elif st.startswith("Held"):
            indis = "Held"
        else:
            indis = "No"
        ex = example_page(d)
        bl_num = d["node"].get("backlinks_num") or len(d["links"])
        disline = ("domain:" + dom) if (st == "Spam (Disavow)" and dom not in covered) else ""
        rda_rows.append({
            "domain": dom, "status": st,
            "as": d["ascore"] if d["node"].get("src_semrush") else (d["ascore"] or None),
            "backlinks": bl_num,
            "rds": int(m["refdomains"]) if m.get("refdomains") not in (None, "", "null") else None,
            "traffic": int(m["org_traffic"]) if m.get("org_traffic") not in (None, "", "null") else None,
            "in_disavow": indis, "points_to": MONEY, "dofollow": dof, "nofollow": nof,
            "first_seen": d["first_seen"], "top_anchor": top_anchor(d),
            "example_page": ex["url_from"] if ex else "", "title": ex.get("title", "") if ex else "",
            "source": d["source"], "ip": d["ip"], "disavow_line": disline,
        })

    # ---------- Anchor Analysis rows ----------
    anch = {}
    for dom in by:
        d = by[dom]
        seen_dom = set()
        for r in d["links"]:
            a = (r["anchor"] or "").strip()
            key = a
            node = anch.setdefault(key, {"anchor": a, "type": anchor_type_of(r),
                                         "backlinks": 0, "domains": set(), "spam_domains": set()})
            node["backlinks"] += 1
            node["domains"].add(dom)
            if d["status"].startswith("Spam"):
                node["spam_domains"].add(dom)
    total_links = len(links)
    anchor_rows = []
    for a, node in sorted(anch.items(), key=lambda kv: -kv[1]["backlinks"]):
        anchor_rows.append({
            "anchor": node["anchor"] if node["anchor"] else "<EmptyAnchor>",
            "anchor_type": node["type"], "backlinks": node["backlinks"],
            "share": node["backlinks"] / total_links,
            "refdomains": len(node["domains"]), "spam_domains": len(node["spam_domains"]),
        })

    # ---------- Exact Match Anchors rows ----------
    exact_rows = []
    for dom in sorted(by):
        d = by[dom]
        seen = set()
        for r in d["links"]:
            at = anchor_type_of(r)
            if at not in ("Exact match commercial", "Exact match commercial (geo)"):
                continue
            a = (r["anchor"] or "").strip()
            if a in seen:
                continue
            seen.add(a)
            exact_rows.append({
                "domain": dom, "example": r["url_from"], "anchor": a,
                "market": "Georgia" if at.endswith("(geo)") else "Non-geo",
                "site_type": site_type(host_of(r["url_from"]), r.get("title", ""), d["ascore"]),
            })

    # ---------- Pending Disavow Lines rows ----------
    pending_rows = []
    for dom in sorted(by):
        d = by[dom]
        if d["status"].startswith("Held"):
            pending_rows.append({
                "domain": dom, "line": "domain:" + dom,
                "reco": f"Append only if the partner does not claim it, to {DISAVOW_FILE}",
            })

    # ---------- Disavow List rows ----------
    disavow_rows = []
    for dom in sorted(by):
        d = by[dom]
        if d["status"] == "Spam (Disavow)" and dom not in covered:
            m = metrics.get(dom, {})
            disavow_rows.append({
                "line": "domain:" + dom, "as": d["ascore"] if d["node"].get("src_semrush") else (d["ascore"] or None),
                "backlinks": d["node"].get("backlinks_num") or len(d["links"]),
                "rds": int(m["refdomains"]) if m.get("refdomains") not in (None, "", "null") else None,
                "traffic": int(m["org_traffic"]) if m.get("org_traffic") not in (None, "", "null") else None,
                "org_kw": int(m["org_keywords"]) if m.get("org_keywords") not in (None, "", "null") else None,
                "top_anchor": top_anchor(d),
            })

    # ---------- Summary ----------
    status_domain_counts = collections.Counter(d["status"] for d in by.values())
    status_bl_counts = collections.Counter()
    for d in by.values():
        status_bl_counts[d["status"]] += len(d["links"])
    total_domains = len(by)
    summary_status = []
    for st in STATUS_ORDER:
        dc = status_domain_counts.get(st, 0)
        summary_status.append([st, dc, status_bl_counts.get(st, 0),
                               dc / total_domains if total_domains else 0, STATUS_MEANING[st]])
    summary_total = ["Total", total_domains, sum(status_bl_counts.values()), 1.0]

    # anchor-type profile
    type_bl = collections.Counter()
    type_dom = collections.defaultdict(set)
    for dom in by:
        for r in by[dom]["links"]:
            at = anchor_type_of(r)
            type_bl[at] += 1
            type_dom[at].add(dom)
    TYPE_ORDER = ["Spam: keyword stuffed SEO sales copy", "Naked URL", "Exact match commercial",
                  "Exact match commercial (geo)", "Generic", "Branded", "Empty or image",
                  "Contextual or other"]
    summary_anchor = []
    for t in TYPE_ORDER:
        bl = type_bl.get(t, 0)
        summary_anchor.append([t, bl, bl / total_links if total_links else 0, len(type_dom.get(t, set()))])

    n_disavow = len(disavow_rows)
    n_spam_total = status_domain_counts["Spam (Disavow)"] + status_domain_counts["Spam (Nofollow, No Action)"]
    n_held = status_domain_counts["Held (Pending Partner)"] + status_domain_counts["Held (Nofollow, No Action)"]
    spam_bl = status_bl_counts["Spam (Disavow)"] + status_bl_counts["Spam (Nofollow, No Action)"]
    key_findings = [
        f"{n_spam_total:,} of the {total_domains:,} referring domains are spam. {n_disavow:,} have a dofollow link and go in the disavow file; the rest are nofollow and pass no value, so no action is needed.",
        f"The attack exploded well beyond the brief. Semrush recorded 269 referring domains in June 2026 and ~2,008 now, with the sharpest jump between September (456) and October (1,942). We audited the full live profile, not the brief's 207.",
        f"One disavow file covers erthproducts.com. No owned domains were found redirecting into the site in the link data; confirm owned/redirect domains before upload so each Search Console property gets its own file if needed.",
        f"Two patterns, easy to tell apart. The link-scheme flood points at the home page; the {n_held} held domains point at deep product pages (bio retention soil, golf divot mix, engineered soils, top dressing).",
        f"The dominant anchor, on ~1,510 domains, is backlink sales copy that names the client's own domain ('erthproducts.com Premium SEO Backlinks for Higher Google Rankings and Organic Traffic'). Three more PBN anchor templates follow.",
        f"{n_held} domains are held for the previous SEO partner to confirm, in case any were paid placements. They are directory, bookmarking and podcast links with exact-match product anchors to deep pages.",
        f"Held does not mean valuable: almost all held domains have Authority Score 2 and little or no organic traffic. Nothing is disavowed until the partner has confirmed the held set.",
    ]

    records = {
        "client_name": CLIENT_NAME,
        "summary_status": summary_status, "summary_total": summary_total,
        "key_findings": key_findings, "summary_anchor": summary_anchor,
        "rda_rows": rda_rows, "abl_rows": abl_rows, "anchor_rows": anchor_rows,
        "exact_rows": exact_rows, "pending_rows": pending_rows, "disavow_rows": disavow_rows,
    }
    return records, by, covered


def write_disavow(by, covered, out_path):
    groups = collections.OrderedDict([
        ("PBN / keyword-stuffed SEO sales-copy link network", []),
        ("Other confirmed spam (directory / marketplace / auto-generated)", []),
    ])
    for dom in sorted(by):
        d = by[dom]
        if d["status"] != "Spam (Disavow)" or dom in covered:
            continue
        ev = d["evidence"].lower()
        if "pbn" in ev or "sales-copy" in ev or "sales copy" in ev:
            groups["PBN / keyword-stuffed SEO sales-copy link network"].append(dom)
        else:
            groups["Other confirmed spam (directory / marketplace / auto-generated)"].append(dom)
    n = sum(len(v) for v in groups.values())
    lines = []
    lines.append(f"# Disavow file for erthproducts.com (Google Search Console property)")
    lines.append(f"# Generated {dt.date.today().isoformat()} by the Harbinger backlink audit.")
    lines.append(f"# {n} domains, all confirmed spam with at least one dofollow link.")
    lines.append(f"# DO NOT UPLOAD until Harbinger and the previous SEO partner have confirmed the held set.")
    lines.append(f"# Held (pending-partner) domains are deliberately EXCLUDED from this file. See the")
    lines.append(f"#   'Pending Disavow Lines' tab; append them here only if the partner does not claim them.")
    lines.append(f"# Scope check: confirm whether a disavow file already exists on this property.")
    lines.append(f"#   If one does, uploading REPLACES it. If the client has checked and there is none, this is the first.")
    lines.append(f"# Lines are domain: entries (cover all subdomains). Redundant child subdomains are omitted.")
    lines.append("")
    for reason, doms in groups.items():
        if not doms:
            continue
        lines.append(f"# --- {reason} ({len(doms)}) ---")
        for dom in doms:
            lines.append(f"domain:{dom}")
        lines.append("")
    open(out_path, "w").write("\n".join(lines))
    return n, {k: len(v) for k, v in groups.items()}


if __name__ == "__main__":
    records, by, covered = assemble()
    os.makedirs("erth/out", exist_ok=True)
    xlsx = B.build(records, "erth/out/Erth_Products_Backlinks_Audit.xlsx",
                   logo_path="erth/ref/harbinger_logo.png")
    n, groups = write_disavow(by, covered, "erth/out/" + DISAVOW_FILE)
    print("workbook:", xlsx)
    print("disavow lines:", n, groups)
    print("tabs rows: RDA=%d ABL=%d Anchor=%d Exact=%d Pending=%d Disavow=%d" % (
        len(records["rda_rows"]), len(records["abl_rows"]), len(records["anchor_rows"]),
        len(records["exact_rows"]), len(records["pending_rows"]), len(records["disavow_rows"])))
