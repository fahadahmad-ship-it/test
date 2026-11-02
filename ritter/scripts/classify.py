"""Classifier: assigns exactly one of the six statuses to each referring domain,
following BACKLINK_AUDIT_PLAYBOOK.md Section 6 verdict order (first match wins).

Statuses (no 'Review' buckets):
  Spam (Disavow) | Spam (Nofollow, No Action) | Held (Pending Partner) |
  Held (Nofollow, No Action) | Keep | Own Site

Every Spam (Disavow) line must rest on VISIBLE evidence (spam anchor, spam title,
spam URL, or a known network host) and have >=1 dofollow link. Nothing is
disavowed on Authority Score, TLD, or shared IP alone.
"""
import glob
import collections
import sys

sys.path.insert(0, "/home/user/test/ritter/scripts")
import config as C
from load import read_semrush_csv, host_of, path_of, canon_domain, slash24

HOME_PATHS = ("/", "", "/index.html", "/home", "/index.php")

ANCHOR_SPAM_SALESCOPY = "Spam: keyword stuffed SEO sales copy"
ANCHOR_SPAM_OFFTOPIC = "Spam: off topic"
ANCHOR_EXACT = "Exact match commercial"
ANCHOR_EXACT_GEO = "Exact match commercial (geo)"
ANCHOR_NAKED = "Naked URL"
ANCHOR_BRANDED = "Branded"
ANCHOR_GENERIC = "Generic"
ANCHOR_EMPTY = "Empty or image"
ANCHOR_OTHER = "Contextual or other"

GENERIC_ANCHORS = {"visit website", "website", "click here", "read more", "here",
                   "visit site", "view website", "website ↗", "learn more",
                   "this website", "homepage", "home page", "link", "more info"}


def _has(text, needles):
    t = (text or "").lower()
    return any(n in t for n in needles)


def anchor_type(anchor, title):
    a = (anchor or "").strip()
    al = a.lower()
    if a == "" or a == "<EmptyAnchor>" or a.lower() == "emptyanchor":
        return ANCHOR_EMPTY
    # Spam sales copy: in the anchor itself OR a blatant PBN title with a bare anchor
    if _has(al, C.PBN_ANCHOR_SIGNALS):
        return ANCHOR_SPAM_SALESCOPY
    if _has(al, C.OFFTOPIC_SIGNALS):
        return ANCHOR_SPAM_OFFTOPIC
    # Naked URL / bare domain
    if al.startswith("http://") or al.startswith("https://") or al.startswith("www.") \
            or C.MONEY_DOMAIN in al or al.endswith(".com") or al.endswith(".net") \
            or al.endswith(".org") or al.endswith(".info"):
        # but a service phrase that merely contains a tld-looking token is not naked
        if _has(al, [s for s in C.SERVICE_TERMS]):
            pass
        else:
            return ANCHOR_NAKED
    # Exact-match commercial (service vocabulary)
    if _has(al, C.SERVICE_TERMS):
        if _has(al, C.GEO_TERMS):
            return ANCHOR_EXACT_GEO
        return ANCHOR_EXACT
    # Branded
    if _has(al, C.BRAND_TERMS):
        return ANCHOR_BRANDED
    if al in GENERIC_ANCHORS:
        return ANCHOR_GENERIC
    return ANCHOR_OTHER


def title_is_spam(title):
    return _has(title, C.SPAM_TITLE_SIGNALS) or _has(title, C.PBN_ANCHOR_SIGNALS)


def title_names_client(title):
    t = (title or "").lower()
    return _has(t, C.BRAND_TERMS) or "ritter" in t


def host_is_spam(domain):
    return _has(domain, C.SPAM_HOST_SIGNALS)


def is_deep_target(url):
    return path_of(url) not in HOME_PATHS


def build_domain_records(backlinks, refdomains, comp_metrics, rank_metrics):
    """Group links under their referring root domain and attach metrics."""
    rd_set = set(canon_domain(r["domain"]) for r in refdomains)
    rd_by_dom = {canon_domain(r["domain"]): r for r in refdomains}

    def to_root(host):
        h = canon_domain(host)
        if h in rd_set:
            return h
        # strip leftmost labels until a known refdomain matches
        labels = h.split(".")
        for i in range(1, len(labels) - 1):
            cand = ".".join(labels[i:])
            if cand in rd_set:
                return cand
        # fall back to last two labels (registrable-ish)
        if len(labels) >= 2:
            return ".".join(labels[-2:])
        return h

    links_by_dom = collections.defaultdict(list)
    for b in backlinks:
        dom = to_root(host_of(b["source_url"]))
        links_by_dom[dom].append(b)

    domains = set(rd_set) | set(links_by_dom.keys())
    records = {}
    # /24 density for network-host signal
    ip24 = collections.Counter()
    for d in domains:
        rdrow = rd_by_dom.get(d)
        ip = (rdrow or {}).get("ip", "")
        s24 = slash24(ip)
        if s24 and not any(ip.startswith(p) for p in C.CDN_IP_PREFIXES_EXCLUDE):
            ip24[s24] += 1

    for d in domains:
        links = links_by_dom.get(d, [])
        rdrow = rd_by_dom.get(d, {})
        comp = comp_metrics.get(d, {})
        rank = rank_metrics.get(d, {})
        rec = {
            "domain": d,
            "links": links,
            "ip": rdrow.get("ip", ""),
            "country": rdrow.get("country", ""),
            "rd_first_seen": rdrow.get("first_seen", ""),
            "rd_last_seen": rdrow.get("last_seen", ""),
            "rd_ascore_low": rdrow.get("domain_ascore", ""),
            # metrics (prefer comparison AS; fall back to refdomains AS)
            "AS": comp.get("authority_score", rdrow.get("domain_ascore", "")),
            "own_backlinks": comp.get("backlinks_num", ""),
            "own_rds": comp.get("domains_num", ""),
            "traffic": rank.get("organic_traffic", ""),
            "organic_keywords": rank.get("organic_keywords", ""),
        }
        records[d] = rec
    return records, ip24


def classify_domain(rec, ip24):
    links = rec["links"]
    d = rec["domain"]
    # link-level facts
    dofollow = [l for l in links if l.get("nofollow", "").lower() != "true"]
    has_dofollow = len(dofollow) > 0
    anchors = [(l.get("anchor", ""), l.get("source_title", ""), l.get("target_url", ""),
               l.get("nofollow", "")) for l in links]
    atypes = [anchor_type(a, t) for (a, t, u, nf) in anchors]
    atype_set = set(atypes)
    titles = [l.get("source_title", "") for l in links]
    any_deep = any(is_deep_target(l.get("target_url", "")) for l in links)
    try:
        AS = float(rec["AS"]) if rec["AS"] not in ("", None) else 0.0
    except ValueError:
        AS = 0.0

    has_exact = ANCHOR_EXACT in atype_set or ANCHOR_EXACT_GEO in atype_set
    has_pbn = ANCHOR_SPAM_SALESCOPY in atype_set
    has_offtopic = ANCHOR_SPAM_OFFTOPIC in atype_set
    any_title_spam = any(title_is_spam(t) for t in titles)
    any_title_client = any(title_names_client(t) and not title_is_spam(t) for t in titles)
    host_spam = host_is_spam(d)
    s24 = slash24(rec["ip"])
    network_host = bool(s24) and ip24.get(s24, 0) >= C.NETWORK_MIN_HOSTS \
        and not any(rec["ip"].startswith(p) for p in C.CDN_IP_PREFIXES_EXCLUDE)

    reason = ""

    # 1. Client-owned / redirect domain
    if d in C.OWNED_DOMAINS or canon_domain(d) == C.MONEY_DOMAIN:
        return "Own Site", "Client-owned property.", atypes
    # 7-10 spam signals computed; but order per playbook: AS>=20 Keep is rule 2.
    # 2. Authority Score >= 20 => genuine site => Keep (protects real directories)
    if AS >= C.KEEP_AS_THRESHOLD:
        # unless the page itself carries visible spam evidence: a PBN/off-topic
        # anchor OR a spam-template page title (aged-domain seller, reverse-IP
        # tool, URL shortener, auto-directory). Score alone never disavows, but
        # visible page evidence overrides a high score.
        if (has_pbn or has_offtopic or any_title_spam) and not any_title_client:
            pass  # visible page-spam evidence overrides the score; follow decided below
        else:
            return "Keep", f"Genuine site (Authority Score {int(AS)}).", atypes
    # 3. Exact-match AND PBN on same domain => Held
    if has_exact and has_pbn:
        st = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
        return st, "Exact-match commercial and SEO sales-copy anchors on the same domain.", atypes
    # 4. Exact-match anchor OR deep money-page link => Held
    if has_exact or any_deep:
        why = "Exact-match commercial anchor." if has_exact else "Links aimed at a deep service page."
        st = "Held (Pending Partner)" if has_dofollow else "Held (Nofollow, No Action)"
        return st, why, atypes
    # 6. Linking page title names the client without SEO sales copy => Keep
    if any_title_client:
        return "Keep", "Business listing / editorial mention that names the client.", atypes
    # 7. Off-topic anchor/host => Spam
    if has_offtopic:
        st = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
        return st, "Off-topic (casino/pharma/adult) anchor.", atypes
    # 8. PBN sales-copy anchor => Spam
    if has_pbn:
        st = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
        return st, "Keyword-stuffed SEO sales-copy anchor (PBN/link-service template).", atypes
    # 9. Spam host name => Spam (needs dofollow to disavow)
    if host_spam:
        st = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
        return st, "Spam host-name signature.", atypes
    # 10. Spam page title / URL template => Spam
    if any_title_spam:
        st = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
        return st, "Spam page title / domain-marketplace template.", atypes
    # 10b. Throwaway free-blog (blogspot) page: bare/branded link, title does not
    #      name the client, no exact-match anchor => PBN scrap page, not editorial.
    if any(d == h or d.endswith("." + h) for h in C.FREE_BLOG_PBN_HOSTS) \
            and not any_title_client and not has_exact:
        if any(at in (ANCHOR_NAKED, ANCHOR_EMPTY, ANCHOR_BRANDED, ANCHOR_GENERIC) for at in atypes):
            st = "Spam (Disavow)" if has_dofollow else "Spam (Nofollow, No Action)"
            return st, "Throwaway free-blog (blogspot) page with no editorial context.", atypes
    # 11. Network host (/24 with 5+ refdomains) => spam only WITH other evidence
    #     (handled above via anchor/title/host). Shared IP alone is never enough.
    # 12. Otherwise => Keep
    return "Keep", "No spam evidence; genuine or harmless.", atypes
