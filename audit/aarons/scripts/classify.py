"""
Classifier for the aaronshometech.com audit. One status per referring domain.
Six statuses, no "Review" bucket (BACKLINK_AUDIT_PLAYBOOK section 6); anything
uncertain is resolved on its own evidence. Evidence-based: nothing is disavowed
on score/TLD/IP alone — every Spam verdict rests on a visible anchor, title, URL
or host signature.

Run: python3 -I scripts/classify.py data/joined.json scripts/config.py data/classified.json
"""
import sys, os, json, importlib.util, re

def load_config(path):
    spec = importlib.util.spec_from_file_location("config", path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return cfg

HOME_RE = re.compile(r"^https?://(www\.)?aaronshometech\.com/?$", re.I)

def norm(s):
    return (s or "").lower()

def is_deep_target(url):
    """A deep money page = path beyond '/' on the money site (services/location/etc)."""
    u = norm(url)
    u = re.sub(r"^https?://(www\.)?", "", u)
    if not u.startswith("aaronshometech.com"):
        # target may be a redirect host; treat non-moneysite targets as not-deep here
        return False
    path = u[len("aaronshometech.com"):]
    return len(path.strip("/")) > 0

def any_sig(text, sigs):
    t = norm(text)
    return any(s in t for s in sigs)

_OFFTOPIC_RE = None
def offtopic_hit(text, cfg):
    """Word-boundary match for off-topic tokens, so short tokens don't match
    inside unrelated words (e.g. 'cialis' inside 'specialist', 'slot' in 'slots')."""
    global _OFFTOPIC_RE
    if _OFFTOPIC_RE is None:
        _OFFTOPIC_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in cfg.OFFTOPIC_TOKENS) + r")\b")
    t = norm(text)
    # also split domain punctuation so concatenated host tokens are seen as words
    t2 = re.sub(r"[._/\-]", " ", t)
    return bool(_OFFTOPIC_RE.search(t)) or bool(_OFFTOPIC_RE.search(t2))

def classify_domain(rec, cfg, as_override=None):
    d = rec["domain"]
    # authoritative AS: backlinks_comparison (agrees with overview) when available,
    # else the referring-domain report AS (runs ~11 low; documented fallback)
    AS = rec.get("domain_ascore", 0)
    if as_override and d in as_override:
        AS = as_override[d]
        rec["as_authoritative"] = AS
    links = rec.get("links", [])

    anchors = [norm(l["anchor"]) for l in links]
    titles  = [norm(l["source_title"]) for l in links]
    redirects = [norm(l["redirect_url"]) for l in links]
    follows = [(not l["nofollow"]) for l in links]
    has_dofollow = any(follows)
    all_nofollow = (len(links) > 0 and not has_dofollow)

    blob_anchor = " || ".join(anchors)
    blob_title  = " || ".join(titles)
    blob_redir  = " || ".join(redirects)

    # --- evidence flags ---
    hard_spam_anchor = any_sig(blob_anchor, cfg.SPAM_ANCHOR_SIGNATURES) or \
                       any_sig(blob_anchor, cfg.SPAM_SOFT_SIGNATURES)
    spam_title = any_sig(blob_title, cfg.SPAM_TITLE_SIGNATURES) or \
                 ("backlink building services" in blob_title) or \
                 ("authority backlink services" in blob_title) or \
                 ("seo rank boost" in blob_title) or \
                 bool(re.search(r"page\s*[\d,]{3,}", blob_title)) or \
                 ("premium backlink" in blob_title)
    offtopic = offtopic_hit(blob_anchor, cfg) or offtopic_hit(blob_title, cfg) or \
               offtopic_hit(d, cfg)
    # a PBN co-client named in anchor/redirect = link-farm page selling to many clients
    coclient = any_sig(blob_anchor, cfg.PBN_COCLIENT_TOKENS) or \
               any(any(tok in r for tok in cfg.PBN_COCLIENT_TOKENS) for r in redirects)

    # the referring domain's OWN name is a member of the same link vendor's network
    # (its other clients: roofing/screening/etc.) -> irrelevant cross-link, not editorial
    coclient_domain = (d not in cfg.OWNED_DOMAINS) and any(tok in d for tok in cfg.PBN_COCLIENT_TOKENS)

    host_spam = any(sig in d for sig in cfg.SPAM_HOST_SIGNATURES)
    spammy_tld = bool(re.search(r"\.(shop|online|xyz|site|space|store|icu|club|monster|wiki|biz|sbs|click|link|live|today|fun|life|cfd|rest|lol)$", d))

    # commercial exact-match (geo) anchor: service term (+ geography), not sales copy
    def is_commercial(a):
        if not a:
            return False
        if any(s in a for s in cfg.SPAM_ANCHOR_SIGNATURES):
            return False
        if any(s in a for s in cfg.SPAM_SOFT_SIGNATURES):
            return False
        return any(t in a for t in cfg.SERVICE_TERMS)
    commercial = any(is_commercial(a) for a in anchors)
    commercial_geo = any(is_commercial(a) and any(g in a for g in cfg.GEO_TERMS) for a in anchors)

    # deep money-page target reached by a non-hardspam anchor = commissioned-looking
    deep_commissioned = any(
        is_deep_target(l["target_url"]) and
        not any_sig(l["anchor"], cfg.SPAM_ANCHOR_SIGNATURES) and
        not any_sig(l["anchor"], cfg.SPAM_SOFT_SIGNATURES)
        for l in links)

    # branded / editorial: anchor is a brand token or naked client domain, or the
    # linking-page title names the client WITHOUT sales copy
    branded_anchor = any(
        (any(b in a for b in cfg.BRAND_TOKENS) or a.strip("/ ") in
         ("aaronshometech.com", "https://aaronshometech.com", "http://aaronshometech.com",
          "www.aaronshometech.com"))
        and not any_sig(a, cfg.SPAM_ANCHOR_SIGNATURES)
        for a in anchors)
    editorial_title = any(
        any(b in t for b in cfg.BRAND_TOKENS) and not any_sig(t, cfg.SPAM_TITLE_SIGNATURES)
        and not any_sig(t, cfg.SPAM_ANCHOR_SIGNATURES) and "backlink" not in t
        for t in titles)

    # press-release syndication host (rule 5) -> held, may be commissioned
    pr_host = any(h in d for h in getattr(cfg, "PRESS_RELEASE_HOSTS", []))
    held_signal = commercial_geo or commercial or deep_commissioned or pr_host
    hard_spam = hard_spam_anchor or spam_title or offtopic or coclient or coclient_domain
    # host/TLD signal only counts as spam evidence for low-authority domains and
    # never on its own for a domain with real authority
    host_signal = (host_spam or spammy_tld) and AS < cfg.KEEP_AS_THRESHOLD

    status = None
    reason = ""
    evidence = ""

    # --- verdict order (first match wins), following BACKLINK_AUDIT_PLAYBOOK s6 ---
    if d in cfg.OWNED_DOMAINS:
        status, reason = "Own Site", "Client-owned / brand-cluster domain (Aaron's)"
        evidence = "owned domain"
    elif d in cfg.AGENCY_DOMAINS:
        status, reason = "Keep", "Harbinger Marketing (managing agency) citation"
        evidence = "agency domain"
    elif offtopic and (has_dofollow or len(links) == 0):
        # off-topic (casino/pharma/adult) is never genuine for this client, even at high AS
        status, reason = "Spam (Disavow)", "Off-topic (gambling/pharma/adult/etc.) link"
        evidence = _ev_spam(anchors, titles, cfg) or "off-topic anchor/host"
        rec["spam_group"] = "off_topic"
    elif offtopic:
        status, reason = "Spam (Nofollow, No Action)", "Off-topic link but every link is nofollow"
        evidence = "off-topic (nofollow)"
        rec["spam_group"] = "off_topic"
    elif AS >= cfg.KEEP_AS_THRESHOLD and not coclient_domain:
        # rule 2: a genuine, authoritative site is kept (never disavow a real citation)
        status, reason = "Keep", f"Genuine site (Authority Score {AS})"
        evidence = f"AS={AS}"
    elif held_signal and hard_spam:
        # rule 3: exact-match/commercial AND PBN on the same domain -> hold, confirm
        base = "Held (Pending Partner)" if has_dofollow or len(links) == 0 else "Held (Nofollow, No Action)"
        status = base
        reason = "Commercial/deep-page link present alongside PBN anchors; confirm if commissioned before any action"
        evidence = _ev_commercial(anchors, links, cfg)
    elif held_signal:
        base = "Held (Pending Partner)" if has_dofollow or len(links) == 0 else "Held (Nofollow, No Action)"
        status = base
        reason = "Exact-match commercial (geo) anchor or deep money-page link; may be commissioned by the previous supplier"
        evidence = _ev_commercial(anchors, links, cfg)
    elif editorial_title and not hard_spam:
        # rule 6: the linking PAGE TITLE names the client without sales copy = genuine
        # citation (a naked brand anchor alone is not enough; PBN pages use those too).
        # Only reached when there is no commercial/deep held-signal above.
        status, reason = "Keep", "Editorial / business-listing citation naming the client without sales copy"
        evidence = "editorial (title names client)"
    elif hard_spam:
        kind = "PBN / link-service sales-copy"
        ev = _ev_spam(anchors, titles, cfg)
        if ev in ("", "spam signature"):
            if coclient_domain:
                ev = f"same link-network member domain (unrelated industry): {d}"
                kind = "same-network cross-link"
            elif coclient:
                ev = "anchor/redirect names another client of the same link vendor"
                kind = "same-network cross-link"
        if has_dofollow:
            status, reason = "Spam (Disavow)", f"{kind} with a dofollow link to the site"
        elif all_nofollow:
            status, reason = "Spam (Nofollow, No Action)", f"{kind}; every link is nofollow"
        else:
            status, reason = "Spam (Disavow)", f"{kind}"
        evidence = ev
        rec["spam_group"] = "pbn"
    elif host_signal:
        if all_nofollow:
            status, reason = "Spam (Nofollow, No Action)", "Spam host-name/TLD signature; all links nofollow"
        else:
            status, reason = "Spam (Disavow)", "Spam host-name / link-farm TLD signature on a no-authority domain"
        evidence = f"host: {d}"
        rec["spam_group"] = "host"
    else:
        # no visible spam evidence -> retained (never disavow without evidence)
        status, reason = "Keep", "No spam evidence visible; retained (not disavowed without evidence)"
        evidence = "no evidence"

    rec["status"] = status
    rec["status_reason"] = reason
    rec["evidence"] = evidence
    rec.setdefault("spam_group", "")
    rec["has_dofollow"] = has_dofollow
    rec["all_nofollow"] = all_nofollow
    rec["n_links"] = len(links)
    rec["commercial"] = commercial or commercial_geo
    rec["deep_commissioned"] = deep_commissioned
    rec["hard_spam"] = hard_spam
    rec["held_signal"] = bool(held_signal)
    # pick a representative example link + top anchor + where it points
    rec["example"] = _example(links)
    rec["top_anchor"] = _top_anchor(anchors)
    rec["points_to"] = _points_to(links)
    return rec


def _ev_spam(anchors, titles, cfg):
    for a in anchors:
        if any_sig(a, cfg.SPAM_ANCHOR_SIGNATURES) or any_sig(a, cfg.SPAM_SOFT_SIGNATURES):
            return "anchor: " + a[:120]
    for t in titles:
        if any_sig(t, cfg.SPAM_TITLE_SIGNATURES) or "backlink" in t or re.search(r"page\s*[\d,]{3,}", t):
            return "title: " + t[:120]
    return "spam signature"

def _ev_commercial(anchors, links, cfg):
    for l in links:
        a = norm(l["anchor"])
        if a and any(t in a for t in cfg.SERVICE_TERMS) and not any_sig(a, cfg.SPAM_ANCHOR_SIGNATURES):
            return "anchor: " + a[:120]
    for l in links:
        if is_deep_target(l["target_url"]):
            return "deep target: " + l["target_url"][:120]
    return "commercial/deep"

def _example(links):
    if not links:
        return {}
    # prefer a live (200), dofollow link
    live = [l for l in links if str(l.get("response_code")) == "200"]
    pool = live or links
    df = [l for l in pool if not l["nofollow"]]
    l = (df or pool)[0]
    return {"source_url": l["source_url"], "source_title": l["source_title"],
            "target_url": l["target_url"], "anchor": l["anchor"],
            "nofollow": l["nofollow"], "response_code": l.get("response_code"),
            "redirect_url": l.get("redirect_url")}

def _top_anchor(anchors):
    if not anchors:
        return ""
    from collections import Counter
    return Counter([a for a in anchors if a]).most_common(1)[0][0] if any(anchors) else ""

def _points_to(links):
    """Summarize where this domain's links point: Home / Deep pages / mix."""
    if not links:
        return ""
    home = sum(1 for l in links if HOME_RE.match(l["target_url"] or ""))
    deep = sum(1 for l in links if is_deep_target(l["target_url"]))
    if home and deep:
        return "Home + deep pages"
    if deep:
        return "Deep money page(s)"
    if home:
        return "Home page"
    return "Other"


def load_as_override(metrics_dir):
    import glob, html
    out = {}
    if not metrics_dir:
        return out
    for p in glob.glob(os.path.join(metrics_dir, "*cmp*.csv")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = html.unescape(line.strip())
                if not line or line.startswith("target;"):
                    continue
                parts = line.split(";")
                if len(parts) < 2:
                    continue
                dd = parts[0].strip().lower()
                try:
                    out[dd] = int(parts[1])
                except ValueError:
                    continue
    return out


def load_rank(metrics_dir):
    import glob, html
    out = {}
    if not metrics_dir:
        return out
    for p in glob.glob(os.path.join(metrics_dir, "*rank*.csv")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = html.unescape(line.strip())
                if not line or line.lower().startswith("domain;"):
                    continue
                parts = line.split(";")
                if len(parts) < 4:
                    continue
                dd = parts[0].strip().lower()
                try:
                    out[dd] = (int(parts[3]), int(parts[2]))  # (traffic, keywords)
                except (ValueError, IndexError):
                    continue
    return out


def main():
    joined = json.load(open(sys.argv[1], encoding="utf-8"))
    cfg = load_config(sys.argv[2])
    out_path = sys.argv[3] if len(sys.argv) > 3 else None
    metrics_dir = sys.argv[4] if len(sys.argv) > 4 else None
    as_override = load_as_override(metrics_dir)
    if as_override:
        sys.stderr.write(f"[classify] authoritative AS loaded for {len(as_override)} domains\n")
    rank = load_rank(metrics_dir)
    if rank:
        sys.stderr.write(f"[classify] organic metrics loaded for {len(rank)} domains\n")
    domains = joined["domains"]
    for rec in domains.values():
        classify_domain(rec, cfg, as_override)
        if rec["domain"] in rank:
            rec["organic_traffic"] = rank[rec["domain"]][0]
            rec["organic_keywords"] = rank[rec["domain"]][1]

    from collections import Counter
    counts = Counter(r["status"] for r in domains.values())
    sys.stderr.write("[classify] status counts:\n")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        sys.stderr.write(f"   {k:32s} {v}\n")
    # disavow set = Spam (Disavow) with a dofollow link
    disavow = [r for r in domains.values()
               if r["status"] == "Spam (Disavow)" and r["has_dofollow"]]
    sys.stderr.write(f"[classify] disavow domains (dofollow): {len(disavow)}\n")
    # integrity probes
    no_ev = [r for r in domains.values()
             if r["status"] == "Spam (Disavow)" and r["evidence"] in ("", "spam signature", "no evidence")]
    sys.stderr.write(f"[classify] disavow w/ weak/no evidence string: {len(no_ev)}\n")
    noev_hostonly = [r for r in disavow if r["evidence"].startswith("host:")]
    sys.stderr.write(f"[classify] disavow resting on host-name only: {len(noev_hostonly)}\n")
    held = [r for r in domains.values() if r["status"].startswith("Held")]
    sys.stderr.write(f"[classify] held domains: {len(held)}\n")

    if out_path:
        json.dump(joined, open(out_path, "w", encoding="utf-8"))
        sys.stderr.write(f"[classify] wrote {out_path}\n")


if __name__ == "__main__":
    main()
