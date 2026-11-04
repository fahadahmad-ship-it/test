"""Semrush/Ahrefs CSV loader for the erthproducts.com backlink audit.

Handles the Semrush semicolon-delimited export safely:
- unescape HTML entities per field (titles/anchors carry &amp; etc.)
- split on ';', reject rows whose column count != header count
- never re-roll ad-hoc CSV parsing elsewhere; import from here.
"""
import csv
import html
import io
from urllib.parse import urlsplit


def _read_semicolon(path):
    """Yield dict rows from a Semrush ';'-delimited export. Rejects malformed rows."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = [ln for ln in text.split("\n") if ln != ""]
    if not lines:
        return [], []
    header = lines[0].split(";")
    ncol = len(header)
    rows = []
    bad = 0
    for ln in lines[1:]:
        parts = ln.split(";")
        if len(parts) != ncol:
            bad += 1
            continue
        rows.append({header[i]: html.unescape(parts[i]) for i in range(ncol)})
    return rows, {"header": header, "bad": bad, "total": len(lines) - 1}


def host_of(url):
    """Registrable-ish host: strip scheme, leading www., lowercase. Keep full host otherwise."""
    if not url:
        return ""
    u = url.strip()
    if "//" not in u:
        u = "http://" + u
    h = urlsplit(u).netloc.lower()
    if h.startswith("www."):
        h = h[4:]
    # drop port
    if ":" in h:
        h = h.split(":")[0]
    return h


def registrable(host):
    """Best-effort registrable domain for grouping subdomains under their root.
    Not a full PSL; handles common multi-part TLDs seen in this data."""
    if not host:
        return ""
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    two = {"co", "com", "org", "net", "gov", "edu", "ac", "us"}
    # e.g. foo.co.in -> foo.co.in only if second-level is a known ccSLD
    if parts[-2] in two and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def load_backlinks(paths):
    rows = []
    meta = []
    for p in paths:
        r, m = _read_semicolon(p)
        rows.extend(r)
        meta.append((p, m))
    return rows, meta


def load_refdomains(paths):
    rows = []
    meta = []
    for p in paths:
        r, m = _read_semicolon(p)
        rows.extend(r)
        meta.append((p, m))
    return rows, meta


def load_csv_comma(path):
    """Standard RFC-4180 comma CSV reader (Ahrefs exports). Returns list of dicts."""
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append({k: html.unescape(v) if isinstance(v, str) else v
                        for k, v in row.items()})
    return out


if __name__ == "__main__":
    import glob
    bl, m = load_backlinks(sorted(glob.glob("erth/data/fetch/bl_p*.csv")))
    print("backlinks rows:", len(bl), "meta:", m)
    rd, m2 = load_refdomains(sorted(glob.glob("erth/data/rd/rd_p*.csv")))
    print("refdomain rows:", len(rd), "meta:", m2)
