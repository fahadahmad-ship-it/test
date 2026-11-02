"""Semrush CSV reader. Handles the HTML-entity / semicolon-delimiter trap:
Semrush ships unquoted, semicolon-delimited CSV and leaves HTML entities in
titles and anchors. An entity such as `&amp;` contains its own `;`; if you split
before unescaping, that `;` splits a row into an extra column. So: UNESCAPE
FIRST, SPLIT SECOND, and reject any row whose column count is not the expected
width rather than letting a malformed row through. (Playbook Section 4.)
"""
import html
import glob
import os


def read_semrush_csv(paths, expected_cols):
    """Read one or more Semrush CSV page files that share a header.
    Returns (rows, rejects) where rows is a list of dicts keyed by header names.
    `expected_cols` is the number of columns the header must have.
    """
    rows = []
    rejects = []
    header = None
    for path in paths:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            raw_lines = fh.read().split("\n")
        for i, raw in enumerate(raw_lines):
            if raw == "":
                continue
            # UNESCAPE ENTITIES FIRST so an embedded `;` inside e.g. &amp; is gone
            line = html.unescape(raw)
            parts = line.split(";")
            if header is None and i == 0:
                header = parts
                if len(header) != expected_cols:
                    raise SystemExit(
                        f"Header width {len(header)} != expected {expected_cols} in {path}: {header}")
                continue
            # skip a repeated header line in later pages
            if parts == header:
                continue
            if len(parts) != expected_cols:
                rejects.append((path, i, len(parts), raw[:200]))
                continue
            rows.append(dict(zip(header, parts)))
    return rows, rejects, header


def canon_domain(d):
    """Canonicalize a host to a registrable-ish comparison key."""
    d = (d or "").strip().lower()
    for pre in ("http://", "https://"):
        if d.startswith(pre):
            d = d[len(pre):]
    if d.startswith("www."):
        d = d[4:]
    d = d.split("/")[0].split("?")[0].split("#")[0]
    if d.endswith("."):
        d = d[:-1]
    return d


def host_of(url):
    """Host of a URL (lowercased, www-stripped)."""
    u = (url or "").strip()
    for pre in ("http://", "https://"):
        if u.lower().startswith(pre):
            u = u[len(pre):]
    u = u.split("/")[0].split("?")[0].split("#")[0].lower()
    if u.startswith("www."):
        u = u[4:]
    return u


def path_of(url):
    """Path portion of a URL, lowercased, no query/fragment."""
    u = (url or "").strip()
    for pre in ("http://", "https://"):
        if u.lower().startswith(pre):
            u = u[len(pre):]
    if "/" in u:
        p = "/" + u.split("/", 1)[1]
    else:
        p = "/"
    p = p.split("?")[0].split("#")[0].lower()
    return p or "/"


def is_home_target(url, money_domain):
    """True if the URL points at the money site's home page (root), not a deep page."""
    h = host_of(url)
    p = path_of(url)
    if money_domain not in h:
        # could be a redirect domain; treat by path only
        pass
    return p in ("/", "", "/index.html", "/home", "/index.php")


def slash24(ip):
    ip = (ip or "").strip()
    bits = ip.split(".")
    if len(bits) == 4:
        return ".".join(bits[:3]) + ".0/24"
    return ""


if __name__ == "__main__":
    import sys
    # quick self-check on the fetched files
    bl_paths = sorted(glob.glob("/home/user/test/ritter/data/fetch/backlinks_p*.csv"))
    rd_paths = sorted(glob.glob("/home/user/test/ritter/data/rd/refdomains_p*.csv"))
    print("backlink files:", bl_paths)
    print("refdomain files:", rd_paths)
    if bl_paths:
        rows, rej, hdr = read_semrush_csv(bl_paths, 10)
        print(f"backlinks rows={len(rows)} rejects={len(rej)} header={hdr}")
        for r in rej[:8]:
            print("  REJECT", r)
    if rd_paths:
        rows, rej, hdr = read_semrush_csv(rd_paths, 9)
        print(f"refdomains rows={len(rows)} rejects={len(rej)} header={hdr}")
        for r in rej[:8]:
            print("  REJECT", r)
