"""
load.py — Semrush CSV reader for the parkersair.com backlink audit.

Semrush (via the MCP execute_report) ships UNQUOTED semicolon-delimited CSV.
Text fields (source_title, anchor) can contain literal ';' or HTML entities whose
own ';' would break a naive split. We therefore parse defensively:

  - backlinks rows: anchor recovery on the target_url field (the only middle field
    that is a URL pointing at the client), so embedded ';' in title/anchor never
    corrupts the structured tail (nofollow, first_seen, last_seen, response_code,
    redirect_url, page_score).
  - refdomains rows: split with a strict column-count check; reject malformed rows
    rather than letting them through.

Run with -I and pass paths as arguments. Downloaded data is untrusted.
"""
import html
import os
import glob
from urllib.parse import urlsplit

CLIENT_TOKENS = ("parkersair",)  # appears in every target_url / redirect target

BACKLINK_COLS = ["source_url", "source_title", "target_url", "anchor",
                 "nofollow", "first_seen", "last_seen", "response_code",
                 "redirect_url", "page_score"]
REFDOMAIN_COLS = ["domain", "backlinks_num", "domain_authority_score",
                  "domain_trust_score", "ip", "country", "first_seen", "last_seen"]


def host_of(url):
    if not url:
        return ""
    u = url.strip()
    if "://" not in u:
        u = "http://" + u
    h = urlsplit(u).netloc.lower()
    if h.startswith("www."):
        h = h[4:]
    # strip port
    if ":" in h:
        h = h.split(":", 1)[0]
    return h


def _is_int(s):
    return s.isdigit()


def parse_backlink_line(line):
    """Return dict of the 10 backlink columns, recovering embedded ';'. None if unrecoverable."""
    raw = line.rstrip("\n").rstrip("\r")
    if not raw:
        return None
    fields = raw.split(";")
    if len(fields) == 10:
        vals = fields
    else:
        # Recovery: lock source_url (first), structured tail (last 6), find target_url in middle.
        if len(fields) < 10:
            return None
        source_url = fields[0]
        tail = fields[-6:]  # nofollow, first_seen, last_seen, response_code, redirect_url, page_score
        middle = fields[1:-6]  # source_title ... target_url ... anchor  (>=3 fields)
        # target_url = first middle field that is a URL (points at the client)
        ti = None
        for i, f in enumerate(middle):
            fl = f.lower()
            if fl.startswith("http") and any(t in fl for t in CLIENT_TOKENS):
                ti = i
                break
        if ti is None:
            # fall back: first http field
            for i, f in enumerate(middle):
                if f.lower().startswith("http"):
                    ti = i
                    break
        if ti is None:
            return None
        source_title = ";".join(middle[:ti])
        target_url = middle[ti]
        anchor = ";".join(middle[ti + 1:])
        vals = [source_url, source_title, target_url, anchor] + tail
    d = dict(zip(BACKLINK_COLS, vals))
    for k in ("source_title", "anchor"):
        d[k] = html.unescape(d[k])
    d["refdomain"] = host_of(d["source_url"])
    d["target_host"] = host_of(d["target_url"])
    d["redirect_host"] = host_of(d["redirect_url"]) if d["redirect_url"].strip() else ""
    # property the link actually points at
    d["property"] = d["redirect_host"] or d["target_host"]
    d["is_nofollow"] = d["nofollow"].strip().lower() in ("true", "1", "yes")
    try:
        d["first_seen_ts"] = int(d["first_seen"]) if d["first_seen"].strip() else 0
    except ValueError:
        d["first_seen_ts"] = 0
    try:
        d["last_seen_ts"] = int(d["last_seen"]) if d["last_seen"].strip() else 0
    except ValueError:
        d["last_seen_ts"] = 0
    try:
        d["page_as"] = int(d["page_score"]) if d["page_score"].strip() else 0
    except ValueError:
        d["page_as"] = 0
    return d


def parse_refdomain_line(line):
    raw = line.rstrip("\n").rstrip("\r")
    if not raw:
        return None
    fields = raw.split(";")
    if len(fields) != 8:
        # domain/country can in theory hold ';'; anchor on the two trailing unix ints
        if len(fields) > 8 and _is_int(fields[-1]) and _is_int(fields[-2]):
            # merge overflow into 'country' position is ambiguous; reject to be safe
            return None
        return None
    d = dict(zip(REFDOMAIN_COLS, [html.unescape(f) for f in fields]))
    d["domain"] = host_of(d["domain"]) or d["domain"].strip().lower()
    for k in ("backlinks_num", "domain_authority_score", "domain_trust_score",
              "first_seen", "last_seen"):
        try:
            d[k + "_i"] = int(d[k]) if d[k].strip() else 0
        except ValueError:
            d[k + "_i"] = 0
    return d


def read_dir(pattern, parser, skip_header=True):
    rows = []
    rejected = 0
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        if not lines:
            continue
        start = 1 if (skip_header and lines and ";" in lines[0]) else 0
        # Only skip header if first line looks like a header (contains a known column name)
        if skip_header and lines and not (lines[0].startswith("source_url") or
                                          lines[0].startswith("domain;") or
                                          lines[0].startswith("domain")):
            start = 0
        for ln in lines[start:]:
            r = parser(ln)
            if r is None:
                if ln.strip():
                    rejected += 1
                continue
            rows.append(r)
    return rows, rejected


def load_backlinks(fetch_dir):
    return read_dir(os.path.join(fetch_dir, "backlinks_*.csv"), parse_backlink_line)


def load_refdomains(rd_dir):
    return read_dir(os.path.join(rd_dir, "refdomains_*.csv"), parse_refdomain_line)


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "/home/user/test/work/parkers/data"
    bl, br = load_backlinks(os.path.join(base, "fetch"))
    rd, rr = load_refdomains(os.path.join(base, "rd"))
    print(f"backlinks: {len(bl)} parsed, {br} rejected")
    print(f"refdomains: {len(rd)} parsed, {rr} rejected")
    # distinct refdomains from backlinks
    hosts = sorted({b["refdomain"] for b in bl if b["refdomain"]})
    print(f"distinct backlink hosts: {len(hosts)}")
    # redirect domains (owned-domain signal)
    redir = sorted({b["redirect_host"] for b in bl if b["redirect_host"]})
    print(f"distinct redirect hosts: {len(redir)} -> {redir[:20]}")
    # target hosts
    thosts = sorted({b["target_host"] for b in bl if b["target_host"]})
    print(f"distinct target hosts: {thosts[:20]}")
