"""Anchor-type classifier shared by build.py and the Anchor Analysis tab."""
import re, importlib.util

def _cfg(path="scripts/config.py"):
    spec = importlib.util.spec_from_file_location("config", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def anchor_type(anchor, cfg, target_url=""):
    a = (anchor or "").strip().lower()
    if a in ("", "<emptyanchor>") or a.startswith("<empty"):
        return "Empty / image"
    # off-topic hard spam (word-boundary so 'cialis' doesn't match 'specialist')
    if re.search(r"\b(" + "|".join(re.escape(t) for t in cfg.OFFTOPIC_TOKENS) + r")\b", a):
        return "Spam: off-topic"
    # PBN / SEO sales-copy spam
    if any(s in a for s in cfg.SPAM_ANCHOR_SIGNATURES) or any(s in a for s in cfg.SPAM_SOFT_SIGNATURES):
        return "Spam: SEO sales-copy"
    # branded (client brand tokens or naked client domain)
    naked_client = a.strip("/ ").replace("https://", "").replace("http://", "").replace("www.", "")
    if naked_client.rstrip("/") in ("aaronshometech.com", "aaronssystems.com", "aaronssecurity.com"):
        return "Naked URL (branded)"
    if any(b in a for b in cfg.BRAND_TOKENS):
        return "Branded"
    # naked URL (any scheme/host form) for non-brand
    if re.match(r"^(https?://|www\.)\S+$", a) or re.match(r"^[a-z0-9.-]+\.[a-z]{2,}/?$", a):
        return "Naked URL"
    # generic
    if a in ("visit website", "click here", "website", "view site", "visit site",
             "go to website", "read more", "learn more", "here", "this website",
             "company page visit website", "original source", "visit aaronshometech.com",
             "🌐 visit website", "original source"):
        return "Generic"
    # exact-match commercial (geo)
    if any(t in a for t in cfg.SERVICE_TERMS):
        if any(g in a for g in cfg.GEO_TERMS):
            return "Exact-match commercial (geo)"
        return "Exact-match commercial"
    return "Contextual / other"
