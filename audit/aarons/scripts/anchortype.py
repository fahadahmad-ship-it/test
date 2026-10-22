"""Anchor-type classifier. Labels match the signed K&K template exactly."""
import re, importlib.util

# canonical anchor-type labels, in the template's Summary order
TYPES = [
    "Spam: keyword stuffed SEO sales copy",
    "Spam: off topic",
    "Exact match commercial",
    "Exact match commercial (geo)",
    "Naked URL",
    "Branded",
    "Generic",
    "Empty or image",
    "Contextual or other",
]

def _cfg(path="scripts/config.py"):
    spec = importlib.util.spec_from_file_location("config", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def anchor_type(anchor, cfg, target_url=""):
    a = (anchor or "").strip().lower()
    if a in ("", "<emptyanchor>") or a.startswith("<empty"):
        return "Empty or image"
    # off-topic hard spam (word-boundary so 'cialis' doesn't match 'specialist')
    if re.search(r"\b(" + "|".join(re.escape(t) for t in cfg.OFFTOPIC_TOKENS) + r")\b", a):
        return "Spam: off topic"
    # PBN / keyword-stuffed SEO sales copy
    if any(s in a for s in cfg.SPAM_ANCHOR_SIGNATURES) or any(s in a for s in cfg.SPAM_SOFT_SIGNATURES):
        return "Spam: keyword stuffed SEO sales copy"
    # naked URL / domain as anchor (includes a bare client domain)
    if re.match(r"^(https?://|www\.)\S+$", a) or re.match(r"^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}(/\S*)?$", a):
        return "Naked URL"
    # branded (brand text, not a URL)
    if any(b in a for b in cfg.BRAND_TOKENS):
        return "Branded"
    # generic
    if a in ("visit website", "click here", "website", "view site", "visit site",
             "go to website", "read more", "learn more", "here", "this website",
             "company page visit website", "original source", "visit aaronshometech.com",
             "🌐 visit website", "view", "more"):
        return "Generic"
    # exact-match commercial (geo)
    if any(t in a for t in cfg.SERVICE_TERMS):
        if any(g in a for g in cfg.GEO_TERMS):
            return "Exact match commercial (geo)"
        return "Exact match commercial"
    return "Contextual or other"
