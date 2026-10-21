"""
Semrush CSV reader for the aaronshometech.com audit.

Handles the K&K CSV trap (BACKLINK_AUDIT_PLAYBOOK section 4): Semrush ships
unquoted semicolon-delimited CSV and may leave HTML entities in titles/anchors.
We: unescape entities first, split second, and reject any row that is not the
expected column count rather than letting a stray delimiter corrupt the table.

Run with `python3 -I` and pass paths as arguments (downloaded data is untrusted).

Outputs a joined JSON (domains with attached link evidence) to stdout or a file.
"""
import sys, os, csv, json, html, glob
from urllib.parse import urlparse

RD_COLS = ["domain", "backlinks_num", "domain_ascore", "domain_trust_score",
           "ip", "country", "first_seen", "last_seen"]
BL_COLS = ["source_url", "source_title", "target_url", "anchor", "nofollow",
           "first_seen", "last_seen", "response_code", "redirect_url", "page_ascore"]
AN_COLS = ["anchor", "domains_num", "backlinks_num", "first_seen", "last_seen"]


def _rows(path, ncol):
    """Yield unescaped, length-checked rows from a semicolon CSV. Skips header."""
    bad = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            line = html.unescape(line)            # entities first
            parts = line.split(";")               # split second
            if i == 0 and parts and parts[0] in ("domain", "source_url", "anchor"):
                continue                           # header
            if len(parts) != ncol:                 # reject malformed
                bad += 1
                continue
            yield parts
    if bad:
        sys.stderr.write(f"[load] {os.path.basename(path)}: skipped {bad} malformed rows\n")


def read_rd(paths):
    out = {}
    for p in paths:
        for r in _rows(p, len(RD_COLS)):
            rec = dict(zip(RD_COLS, r))
            d = rec["domain"].strip().lower()
            if not d:
                continue
            # numeric coercions
            for k in ("backlinks_num", "domain_ascore", "domain_trust_score"):
                try:
                    rec[k] = int(rec[k])
                except ValueError:
                    rec[k] = 0
            for k in ("first_seen", "last_seen"):
                try:
                    rec[k] = int(rec[k])
                except ValueError:
                    rec[k] = 0
            rec["domain"] = d
            if d not in out or rec["backlinks_num"] > out[d]["backlinks_num"]:
                out[d] = rec
    return out


def read_backlinks(paths):
    out = []
    for p in paths:
        for r in _rows(p, len(BL_COLS)):
            rec = dict(zip(BL_COLS, r))
            rec["nofollow"] = (rec["nofollow"].strip().lower() == "true")
            for k in ("first_seen", "last_seen"):
                try:
                    rec[k] = int(rec[k])
                except ValueError:
                    rec[k] = 0
            try:
                rec["page_ascore"] = int(rec["page_ascore"])
            except ValueError:
                rec["page_ascore"] = 0
            out.append(rec)
    return out


def read_anchors(path):
    out = []
    for r in _rows(path, len(AN_COLS)):
        rec = dict(zip(AN_COLS, r))
        for k in ("domains_num", "backlinks_num", "first_seen", "last_seen"):
            try:
                rec[k] = int(rec[k])
            except ValueError:
                rec[k] = 0
        out.append(rec)
    return out


def host_of(url):
    u = url.strip().lower()
    if "://" not in u:
        u = "http://" + u
    try:
        h = urlparse(u).hostname or ""
    except ValueError:
        h = ""
    if h.startswith("www."):
        h = h[4:]
    return h


def registrable(host, domain_set):
    """Reduce a hostname to the referring domain it belongs to, by matching the
    longest spine domain that is a suffix. Falls back to a 2-label guess."""
    if not host:
        return ""
    if host in domain_set:
        return host
    labels = host.split(".")
    # try progressively shorter suffixes, longest first
    for i in range(len(labels) - 1):
        cand = ".".join(labels[i:])
        if cand in domain_set:
            return cand
    # fallback: last two labels (works for single-label TLDs that dominate here)
    return ".".join(labels[-2:]) if len(labels) >= 2 else host


def join(rd, backlinks):
    domain_set = set(rd.keys())
    for d in rd.values():
        d["links"] = []
    unmatched = 0
    for bl in backlinks:
        host = host_of(bl["source_url"])
        d = registrable(host, domain_set)
        if d in rd:
            rd[d]["links"].append(bl)
        else:
            unmatched += 1
    if unmatched:
        sys.stderr.write(f"[load] {unmatched} links did not map to a spine domain\n")
    return rd


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    rd = read_rd(sorted(glob.glob(os.path.join(base, "rd", "rd_*.csv"))))
    bl = read_backlinks(sorted(glob.glob(os.path.join(base, "fetch", "bl_*.csv"))))
    joined = join(rd, bl)
    covered = sum(1 for d in joined.values() if d["links"])
    sys.stderr.write(f"[load] domains={len(joined)} links={len(bl)} "
                     f"domains_with_link_evidence={covered}\n")
    payload = {"domains": joined}
    text = json.dumps(payload)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        sys.stderr.write(f"[load] wrote {out_path} ({len(text)} bytes)\n")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
