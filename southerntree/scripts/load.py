"""
Loader / merger for the southerntreega.com audit.

Reads the raw pulls from disk and normalizes them into a single link model and a
per-referring-domain aggregate. Handles:
  - Semrush backlinks CSV  : semicolon-delimited, UNQUOTED, HTML entities left in
    titles/anchors (the "K&K trap"). Parsed robustly, never with naive split.
  - Ahrefs backlinks CSV    : standard RFC-4180 CSV (comma, quoted).
  - Ahrefs refdomains CSV   : standard CSV, one row per referring domain (metrics).

Nothing here makes a verdict; classify.py does that. Downloaded files are untrusted
-- run this with `python3 -I` and pass paths as arguments.
"""

import csv
import html
import sys
import os
import glob
from urllib.parse import urlsplit

CLIENT_HOST = "southerntreega.com"

# Order of columns requested from Semrush `backlinks` (must match the pull).
SEMRUSH_COLS = [
    "source_url", "source_title", "target_url", "anchor", "nofollow",
    "first_seen", "last_seen", "response_code", "redirect_url", "page_ascore",
]
# Indices of the structured (semicolon-free) right-hand block after `anchor`:
#   nofollow, first_seen, last_seen, response_code, redirect_url, page_ascore  (6 cols)
SEMRUSH_RIGHT = 6


def registrable_root(host):
    """Best-effort registrable root domain from a host string."""
    host = (host or "").strip().lower()
    if not host:
        return ""
    if "//" in host:
        host = urlsplit(host).netloc or host
    host = host.split("/")[0].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    # two-level public suffixes commonly seen on these spam hosts
    two = {"co.uk", "co.in", "org.uk", "com.au", "co.za", "com.br", "co.nz", "net.au"}
    if ".".join(parts[-2:]) in two and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def host_of(url):
    try:
        netloc = urlsplit(url if "//" in url else "http://" + url).netloc
        return netloc.split(":")[0].lower()
    except Exception:
        return ""


def canon_link_key(source_url, target_url, anchor):
    def c(u):
        u = (u or "").strip().lower()
        u = u.split("://")[-1]
        if u.startswith("www."):
            u = u[4:]
        return u.rstrip("/")
    return (c(source_url), c(target_url), (anchor or "").strip().lower())


def path_is_deep(url):
    """True if the target URL points at a deep page, not the home page."""
    try:
        p = urlsplit(url if "//" in url else "http://" + url).path
    except Exception:
        p = ""
    p = (p or "").strip("/")
    return bool(p) and p.lower() not in ("index.html", "index.php", "home")


# --------------------------------------------------------------------------
# Semrush parsing (robust, both-ends reconstruction)
# --------------------------------------------------------------------------
def parse_semrush_line(line):
    """Reconstruct a Semrush backlink row despite unquoted semicolons in free text.

    Strategy: unescape HTML entities first (removes the `;` inside &amp; etc.),
    then anchor on structure -- source_url is field 0, the 6 right-hand columns
    are semicolon-free, and target_url is the one http(s) field sitting between
    the free-text source_title and anchor.
    """
    line = html.unescape(line.rstrip("\n"))
    f = line.split(";")
    if len(f) == len(SEMRUSH_COLS):
        fields = f
    elif len(f) > len(SEMRUSH_COLS):
        source_url = f[0]
        right = f[-SEMRUSH_RIGHT:]
        middle = f[1:-SEMRUSH_RIGHT]           # [title..., target_url, anchor...]
        ti = None
        for i, part in enumerate(middle):
            pl = part.strip().lower()
            if pl.startswith("http") and ("southerntreega" in pl or "/service" in pl or i > 0):
                ti = i
                break
        if ti is None:
            for i, part in enumerate(middle):
                if part.strip().lower().startswith("http"):
                    ti = i
                    break
        if ti is None:
            return None
        source_title = ";".join(middle[:ti])
        target_url = middle[ti]
        anchor = ";".join(middle[ti + 1:])
        fields = [source_url, source_title, target_url, anchor] + right
    else:
        return None
    return dict(zip(SEMRUSH_COLS, fields))


def load_semrush(files):
    links = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            header = fh.readline()
            for line in fh:
                if not line.strip():
                    continue
                rec = parse_semrush_line(line)
                if rec is None:
                    continue
                src = rec["source_url"]
                tgt = rec["target_url"]
                redirect = rec.get("redirect_url") or ""
                prop_host = host_of(redirect) if redirect else host_of(tgt)
                links.append({
                    "source_url": src,
                    "source_host": host_of(src),
                    "source_title": rec.get("source_title", ""),
                    "target_url": tgt,
                    "target_host": host_of(tgt),
                    "redirect_url": redirect,
                    "property_host": prop_host,
                    "anchor": rec.get("anchor", ""),
                    "is_dofollow": str(rec.get("nofollow", "")).strip().lower() in ("false", "0", ""),
                    "first_seen": rec.get("first_seen", ""),
                    "response_code": rec.get("response_code", ""),
                    "refdomain": registrable_root(host_of(src)),
                    "subdomain": host_of(src),
                    "tool": "Semrush",
                    "target_is_deep": path_is_deep(tgt),
                })
    return links


# --------------------------------------------------------------------------
# Ahrefs parsing (standard CSV)
# --------------------------------------------------------------------------
def _truthy(v):
    return str(v).strip().lower() in ("true", "1", "yes")


def load_semrush_ui_backlinks(path):
    """Semrush web-UI backlink export: UTF-8-BOM, comma-delimited, RFC-4180 quoted."""
    links = []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for rec in csv.DictReader(fh):
            src = (rec.get("Source url") or "").strip()
            tgt = (rec.get("Target url") or "").strip()
            src_host = host_of(src)
            links.append({
                "source_url": src,
                "source_host": src_host,
                "source_title": rec.get("Source title", "") or "",
                "target_url": tgt,
                "target_host": host_of(tgt),
                "redirect_url": "",
                "property_host": CLIENT_HOST,
                "anchor": rec.get("Anchor", "") or "",
                "is_dofollow": (rec.get("Nofollow", "") or "").strip().lower() != "true",
                "first_seen": rec.get("First seen", "") or "",
                "response_code": "",
                "refdomain": registrable_root(src_host),
                "subdomain": src_host,
                "tool": "Semrush",
                "target_is_deep": path_is_deep(tgt),
            })
    return links


def load_semrush_ui_refdomains(path):
    """Semrush web-UI referring-domain export -> per-domain Semrush metrics (AS, IP, country)."""
    meta = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for rec in csv.DictReader(fh):
            dom = registrable_root((rec.get("Domain") or "").strip().lower())
            if not dom:
                continue
            m = meta.setdefault(dom, {})
            a = rec.get("Domain ascore")
            if a not in (None, ""):
                m["as_sem"] = max(int(float(a)), m.get("as_sem", -1))
            b = rec.get("Backlinks")
            if b not in (None, ""):
                m["backlinks_sem"] = m.get("backlinks_sem", 0) + int(float(b))
            if rec.get("IP Address"):
                m.setdefault("ip", rec["IP Address"].strip())
            if (rec.get("Country") or "").strip():
                m.setdefault("country", rec["Country"].strip())
            fs = (rec.get("First seen") or "").strip()
            if fs and ("first_seen_sem" not in m or fs < m["first_seen_sem"]):
                m["first_seen_sem"] = fs
    return meta


def load_ahrefs_backlinks(files):
    import json
    links = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            src = rec.get("url_from", "") or ""
            tgt = rec.get("url_to", "") or ""
            src_host = (rec.get("name_source") or host_of(src)).lower()
            root = (rec.get("root_name_source") or registrable_root(src_host)).lower()
            links.append({
                "source_url": src,
                "source_host": src_host,
                "source_title": rec.get("title", "") or "",
                "target_url": tgt,
                "target_host": host_of(tgt),
                "redirect_url": "",                       # no client-owned redirect domains
                "property_host": CLIENT_HOST,
                "anchor": rec.get("anchor", "") or "",
                "is_dofollow": bool(rec.get("is_dofollow")),
                "first_seen": rec.get("first_seen_link", "") or "",
                "response_code": rec.get("http_code", ""),
                "refdomain": root,
                "subdomain": src_host,
                "ip": rec.get("ip_source") or "",
                "dr": rec.get("domain_rating_source"),
                "rds": rec.get("refdomains_source_domain"),
                "is_spam_flag": bool(rec.get("is_spam")),
                "link_type": rec.get("link_type", "") or "",
                "tool": "Ahrefs",
                "target_is_deep": path_is_deep(tgt),
            })
    return links


def load_ahrefs_refdomains(files):
    import json
    meta = {}
    for path in files:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            dom = registrable_root((rec.get("root_domain_name") or rec.get("domain") or "").lower())
            if not dom:
                continue
            m = meta.setdefault(dom, {})
            dr = rec.get("domain_rating")
            if dr not in (None, ""):
                m["dr"] = max(float(dr), m.get("dr", -1.0))
            tr = rec.get("traffic_domain")
            if tr not in (None, ""):
                m["traffic"] = max(int(float(tr)), m.get("traffic", 0))
            lt = rec.get("links_to_target")
            if lt not in (None, ""):
                m["links_to_target"] = m.get("links_to_target", 0) + int(float(lt))
            if rec.get("ip_source"):
                m.setdefault("ip", rec["ip_source"])
            fs = rec.get("first_seen")
            if fs and ("first_seen" not in m or fs < m["first_seen"]):
                m["first_seen"] = fs
            pos = rec.get("positions_source_domain")
            if pos not in (None, ""):
                m["positions"] = max(int(float(pos)), m.get("positions", 0))
            if rec.get("is_spam"):
                m["is_spam"] = True
    return meta


def canonical_merge(semrush_links, ahrefs_links):
    """Union of links, deduped on canonical key; tool = Semrush / Ahrefs / Both."""
    by_key = {}
    for l in semrush_links:
        by_key[canon_link_key(l["source_url"], l["target_url"], l["anchor"])] = l
    for l in ahrefs_links:
        k = canon_link_key(l["source_url"], l["target_url"], l["anchor"])
        if k in by_key:
            existing = by_key[k]
            existing["tool"] = "Both"
            # fill IP/DR/ip from Ahrefs if Semrush lacked them
            for fld in ("ip", "dr", "is_spam_flag", "link_type"):
                if fld in l and not existing.get(fld):
                    existing[fld] = l[fld]
        else:
            by_key[k] = l
    return list(by_key.values())


if __name__ == "__main__":
    fetch = sorted(glob.glob("southerntree/data/fetch/backlinks_*.csv"))
    arf = sorted(glob.glob("southerntree/data/ahrefs/backlinks_*.csv"))
    ard = sorted(glob.glob("southerntree/data/ahrefs/refdomains_*.csv"))
    s = load_semrush(fetch) if fetch else []
    a = load_ahrefs_backlinks(arf) if arf else []
    merged = canonical_merge(s, a)
    doms = {}
    for l in merged:
        doms.setdefault(l["refdomain"], []).append(l)
    print(f"semrush links={len(s)} ahrefs links={len(a)} merged={len(merged)} refdomains={len(doms)}")
