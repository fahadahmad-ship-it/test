"""
Semrush CSV reader for the New Garden backlink audit.

Handles the two Semrush export traps (playbook section 4):
  1. Semrush ships UNQUOTED, semicolon-delimited CSV.
  2. It leaves HTML entities in titles/anchors. An entity such as `&amp;`
     ends in a `;`, so splitting on `;` BEFORE unescaping shatters a field
     (the "K&K" trap). Fix: html.unescape() the whole line FIRST, split on
     `;` SECOND, and reject any row whose column count is wrong rather than
     letting a mis-split row through.

Everything here is pure stdlib so it runs with `python3 -I`.
"""
import html, os, glob


def _read_rows(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    out = []
    for line in raw.split("\n"):
        if line == "":
            continue
        out.append(html.unescape(line))  # unescape FIRST
    return out


def load_csv(path):
    """Return (header:list, rows:list[dict], rejected:list[str]).

    Robust to the two traps:
      - HTML entities (unescaped in _read_rows, before any split);
      - raw newlines embedded in titles/anchors. A logical record has exactly
        `n` fields (n-1 semicolons). We accumulate physical lines until the
        field count reaches n: if it lands on n -> emit; if it overshoots n
        (a genuine content semicolon) -> reject that buffer and resync.
    """
    lines = _read_rows(path)
    if not lines:
        return [], [], []
    header = lines[0].split(";")  # split SECOND
    n = len(header)
    rows, rejected = [], []
    buf = None
    for ln in lines[1:]:
        buf = ln if buf is None else buf + " " + ln  # rejoin embedded newline
        parts = buf.split(";")
        if len(parts) < n:
            continue                      # still accumulating a wrapped field
        if len(parts) == n:
            rows.append(dict(zip(header, parts)))
            buf = None
        else:                             # overshoot -> content semicolon
            rejected.append(buf)
            buf = None
    if buf is not None:
        rejected.append(buf)
    return header, rows, rejected


def load_glob(pattern, expect_header=None):
    """Load + concatenate many chunk files that share one header.

    The header line repeats in every chunk file; keep it once.
    """
    files = sorted(glob.glob(pattern))
    all_rows, all_rej, header = [], [], None
    for fp in files:
        h, rows, rej = load_csv(fp)
        if not h:
            continue
        if header is None:
            header = h
        elif h != header:
            raise ValueError(f"header mismatch in {fp}:\n{h}\nvs\n{header}")
        all_rows.extend(rows)
        all_rej.extend((fp, r) for r in rej)
    if expect_header:
        assert header == expect_header, f"unexpected header {header}"
    return header, all_rows, all_rej


def truthy(v):
    return str(v).strip().lower() in ("true", "1", "yes", "y")


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        h, rows, rej = load_csv(p)
        print(f"{p}: {len(rows)} rows, {len(rej)} rejected, cols={h}")
