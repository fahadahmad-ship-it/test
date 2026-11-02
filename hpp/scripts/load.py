"""
Semrush CSV reader for the highpriorityplumbing.com audit.

Handles the Semrush export traps:
- unquoted, semicolon-delimited
- HTML entities left in titles/anchors (e.g. &amp; whose trailing ';' would
  otherwise fragment a row). Unescape FIRST, then split.
- free-text fields (source_title, anchor) may still contain a literal ';'.
  We parse from BOTH ENDS: the trailing columns are fixed-format
  (bool / int / url / int), and target_url starts with 'http', so the two
  free-text fields can be recovered unambiguously without dropping rows.
"""
import html
import glob
import os

BL_HEADER = ["source_url", "source_title", "target_url", "anchor", "nofollow",
             "first_seen", "last_seen", "response_code", "redirect_url", "page_ascore"]
RD_HEADER = ["domain", "backlinks_num", "domain_ascore", "domain_trust_score",
             "ip", "country", "first_seen", "last_seen"]


def _unescape(s):
    # entities first so &amp;-style trailing ';' does not fragment the row
    return html.unescape(s)


def parse_backlinks(paths):
    """Yield dicts for every backlink row across the given files."""
    rows = []
    rejected = 0
    seen_header = False
    for path in sorted(paths):
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                if not line:
                    continue
                if line.startswith("source_url;"):
                    seen_header = True
                    continue
                line = _unescape(line)
                toks = line.split(";")
                if len(toks) < 9:
                    rejected += 1
                    continue
                source_url = toks[0]
                # fixed trailing 6: nofollow, first_seen, last_seen, response_code, redirect_url, page_ascore
                page_ascore = toks[-1]
                redirect_url = toks[-2]
                response_code = toks[-3]
                last_seen = toks[-4]
                first_seen = toks[-5]
                nofollow = toks[-6]
                middle = toks[1:-6]  # source_title, target_url, anchor (any may hold stray ';')
                # find target_url = first token starting with http
                tgt_idx = None
                for i, t in enumerate(middle):
                    if t.startswith("http"):
                        tgt_idx = i
                        break
                if tgt_idx is None:
                    rejected += 1
                    continue
                source_title = ";".join(middle[:tgt_idx])
                target_url = middle[tgt_idx]
                anchor = ";".join(middle[tgt_idx + 1:])
                # sanity on fixed fields
                if nofollow not in ("true", "false"):
                    rejected += 1
                    continue
                rows.append({
                    "source_url": source_url,
                    "source_title": source_title,
                    "target_url": target_url,
                    "anchor": anchor,
                    "nofollow": nofollow == "true",
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                    "response_code": response_code,
                    "redirect_url": redirect_url,
                    "page_ascore": page_ascore,
                })
    return rows, rejected


def parse_refdomains(paths):
    rows = []
    rejected = 0
    for path in sorted(paths):
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                if not line:
                    continue
                if line.startswith("domain;"):
                    continue
                line = _unescape(line)
                toks = line.split(";")
                if len(toks) < 8:
                    rejected += 1
                    continue
                # domain has no ';'. Trailing 7 fixed; but country/ip rarely hold ';'.
                # parse from both ends: domain=first; then backlinks_num, ascore, trust from left;
                # last_seen, first_seen, country, ip from right.
                domain = toks[0]
                last_seen = toks[-1]
                first_seen = toks[-2]
                country = toks[-3]
                ip = toks[-4]
                backlinks_num = toks[1]
                domain_ascore = toks[2]
                domain_trust = toks[3]
                rows.append({
                    "domain": domain,
                    "backlinks_num": backlinks_num,
                    "domain_ascore": domain_ascore,
                    "domain_trust_score": domain_trust,
                    "ip": ip,
                    "country": country,
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                })
    return rows, rejected


def canon_host(url_or_host):
    """lowercase host, strip scheme/path/www."""
    s = url_or_host.strip().lower()
    if "://" in s:
        s = s.split("://", 1)[1]
    s = s.split("/", 1)[0]
    s = s.split("?", 1)[0]
    if s.startswith("www."):
        s = s[4:]
    return s


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else "/home/user/test/hpp"
    bl_paths = glob.glob(os.path.join(base, "data/fetch/bl_*.csv"))
    rd_paths = glob.glob(os.path.join(base, "data/rd/rd_*.csv"))
    bl, bl_rej = parse_backlinks(bl_paths)
    rd, rd_rej = parse_refdomains(rd_paths)
    print(f"backlink rows parsed: {len(bl)} (rejected {bl_rej}) from {len(bl_paths)} files")
    print(f"refdomain rows parsed: {len(rd)} (rejected {rd_rej}) from {len(rd_paths)} files")
    # dedupe backlinks on canonical (source_url, target_url, anchor)
    seen = set()
    uniq = 0
    for r in bl:
        k = (r["source_url"].rstrip("/").lower(), r["target_url"].rstrip("/").lower(), r["anchor"])
        if k not in seen:
            seen.add(k); uniq += 1
    print(f"unique backlinks: {uniq}")
    # unique refdomain hosts
    hosts = set(canon_host(r["source_url"]) for r in bl)
    print(f"distinct source hosts in backlinks: {len(hosts)}")
    rd_hosts = set(canon_host(r["domain"]) for r in rd)
    print(f"distinct refdomain rows: {len(rd)} distinct hosts: {len(rd_hosts)}")
