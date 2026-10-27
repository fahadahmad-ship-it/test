"""Safe reader for Semrush semicolon-delimited CSV (the K&K trap).

Semrush ships UNQUOTED semicolon-delimited CSV and leaves HTML entities in
titles/anchors. Fields source_title / anchor / target may themselves contain
';'. Strategy: unescape entities first, split second, and recover or reject any
row whose column count is wrong rather than letting a misaligned row through.
"""
import html, os, glob

BL_COLS = ["source_url","source_title","target_url","anchor","nofollow",
           "first_seen","last_seen","response_code","redirect_url","page_ascore"]
RD_COLS = ["domain","backlinks_num","domain_ascore","domain_trust_score",
           "ip","country","first_seen","last_seen"]

# the money site + its known owned/redirect hosts live on target/redirect fields
TARGET_HINTS = ("premierblindsanddesigns",)

def _clean(line):
    return html.unescape(line.rstrip("\n").rstrip("\r"))

def read_backlinks(paths):
    rows, dropped, recovered = [], 0, 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            header = f.readline()  # skip
            for raw in f:
                line = _clean(raw)
                if not line.strip():
                    continue
                parts = line.split(";")
                if len(parts) == 10:
                    rows.append(dict(zip(BL_COLS, parts)))
                    continue
                if len(parts) > 10:
                    # recover: col0 = source_url, last 6 are structured,
                    # middle holds source_title + target_url + anchor.
                    src = parts[0]
                    tail = parts[-6:]  # nofollow..page_ascore
                    mid = parts[1:-6]
                    # target_url = the mid element that looks like the money site
                    ti = None
                    for i, m in enumerate(mid):
                        if any(h in m.lower() for h in TARGET_HINTS):
                            ti = i; break
                    if ti is None:
                        # fall back: first mid element beginning with http
                        for i, m in enumerate(mid):
                            if m.lower().startswith("http"):
                                ti = i; break
                    if ti is None:
                        dropped += 1; continue
                    title = ";".join(mid[:ti])
                    target = mid[ti]
                    anchor = ";".join(mid[ti+1:])
                    vals = [src, title, target, anchor] + tail
                    rows.append(dict(zip(BL_COLS, vals)))
                    recovered += 1
                else:
                    dropped += 1
    return rows, dropped, recovered

def read_refdomains(paths):
    rows, dropped = [], 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            f.readline()
            for raw in f:
                line = _clean(raw)
                if not line.strip():
                    continue
                parts = line.split(";")
                if len(parts) == 8:
                    rows.append(dict(zip(RD_COLS, parts)))
                else:
                    dropped += 1
    return rows, dropped

def host_of(url):
    if not url:
        return ""
    u = url.strip().lower()
    for pre in ("https://","http://"):
        if u.startswith(pre):
            u = u[len(pre):]
    if u.startswith("www."):
        u = u[4:]
    u = u.split("/")[0].split("?")[0].split(":")[0]
    return u

def build_refdomain_matcher(refdomain_names):
    """Return a function host->refdomain using the authoritative Semrush
    refdomain list (longest-suffix match), so public-suffix hosts like
    ggmap.us.com are not mis-rooted to us.com."""
    names = sorted({d.strip().lower() for d in refdomain_names}, key=len, reverse=True)
    def match(host):
        h = host_of(host)
        for d in names:
            if h == d or h.endswith("." + d):
                return d
        return root_domain(h)
    return match

def root_domain(host):
    """Best-effort registrable root (handles common 2-level ccTLDs)."""
    h = host_of(host)
    parts = h.split(".")
    if len(parts) <= 2:
        return h
    two = {"co.uk","org.uk","co.in","com.au","co.nz","com.br","co.za","com.mx","co.jp"}
    if ".".join(parts[-2:]) in two and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])
