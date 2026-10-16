"""Shared reader for the Semrush CSV exports.

Semrush ships unquoted semicolon delimited CSV and leaves HTML entities in page
titles and anchors. "K&amp;K" therefore carries a semicolon of its own and
splits a row into an extra column, which matters a lot on a client called K&K.
Unescape first, split second, and keep a count of anything still the wrong shape
rather than letting it through silently.
"""
import csv, glob, html, io, collections

def read_semrush(paths, ncols=None):
    rows, bad = [], []
    hdr = None
    for p in sorted(paths):
        with open(p, encoding='utf-8') as fh:
            lines = fh.read().split('\n')
        h = lines[0].split(';')
        if hdr is None:
            hdr = h
        elif h != hdr:
            raise SystemExit(f'header mismatch in {p}')
        n = ncols or len(hdr)
        for ln in lines[1:]:
            if not ln.strip():
                continue
            parts = html.unescape(ln).split(';')
            if len(parts) != n:
                bad.append((p, ln))
                continue
            rows.append(dict(zip(hdr, parts)))
    return hdr, rows, bad

def host(url):
    try:
        h = url.split('/')[2].lower()
    except IndexError:
        return ''
    return h.split(':')[0].removeprefix('www.')
