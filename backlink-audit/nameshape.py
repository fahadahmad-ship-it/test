#!/usr/bin/env python3
"""Statistical domain-name shape scoring.

Separates machine-generated hostnames from human-chosen brandable ones
without a dictionary, using orthographic statistics that hold for English-
like names: vowel ratio, consonant-run length, digit and hyphen density.
"""
import re

VOWELS = set("aeiouy")

# Compact stem list: enough common English and niche stems to give positive
# evidence of a human-chosen name. Absence is not evidence of spam on its
# own — the statistical tests carry that.
STEMS = set("""
health fit gym muscle nutri supple vitamin brain mind body life live well
sport athlet run walk swim bike yoga food eat diet meal recipe cook kitchen
green leaf soul zen calm sleep rest energy power strong lean bulk shred
best top good great pure true real natural organic clean fresh smart
blog news media press post story world global local daily weekly time
shop store buy sell deal market trade price
lab labs pro plus prime peak core edge apex summit
man men woman women boy girl kid baby mom dad family home house
tech soft data web net site page link app cloud digital online
guide review tip trick hack help learn study school academy course
love happy joy smile bright light dark night day sun moon star sky
water fire earth wind stone rock river ocean sea beach mountain forest
dog cat pet animal bird fish farm garden plant flower tree
travel trip tour adventure explore journey path road way
money cash fund bank invest finance business work job career team group
art design style fashion beauty skin hair face look image photo video
book read write word text talk speak voice sound music song play game
care cure heal therapy clinic doctor nurse medic pharma drug pill
bro dude guy folk people person human self mine your our
""".split())


# Hosts where the interesting label is the subdomain, not the registrable name.
_SUBDOMAIN_HOSTS = (
    "blogspot.com", "wordpress.com", "weebly.com", "wixsite.com",
    "pages.dev", "workers.dev", "github.io", "netlify.app", "vercel.app",
    "substack.com", "tumblr.com", "medium.com", "000webhostapp.com",
)


def _core(domain: str) -> str:
    """The label a human (or a generator) actually chose.

    For a free-host subdomain that is the subdomain — scoring 'blogspot'
    instead of 'lreeswcqcxz' throws away the entire signal.
    """
    d = domain.lower().strip()
    for h in _SUBDOMAIN_HOSTS:
        if d.endswith("." + h):
            return d[: -(len(h) + 1)].split(".")[0]
    parts = d.split(".")
    if len(parts) == 1:
        return parts[0]
    if len(parts) >= 3 and len(parts[-1]) <= 3 and len(parts[-2]) <= 3:
        return parts[-3]
    return parts[-2]


def max_consonant_run(s: str) -> int:
    runs = re.findall(r"[^aeiouy0-9\-]+", s)
    return max((len(r) for r in runs), default=0)


def vowel_ratio(s: str) -> float:
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c in VOWELS) / len(letters)


def stem_hits(s: str) -> int:
    return sum(1 for w in STEMS if len(w) >= 4 and w in s)


def name_shape(domain: str):
    """Return (verdict, score, detail).

    verdict is 'generated', 'suspicious' or 'plausible'.
    """
    c = _core(domain)
    digits = sum(ch.isdigit() for ch in c)
    hyphens = c.count("-")
    alpha = "".join(ch for ch in c if ch.isalpha())
    run = max_consonant_run(c)
    vr = vowel_ratio(c)
    hits = stem_hits(c)

    score = 0
    reasons = []
    if re.search(r"seo|backlink|ranks?\b|submit|directory", c):
        score += 2; reasons.append("SEO/link-scheme token")
    if run >= 5:
        score += 3; reasons.append(f"{run}-consonant run")
    elif run == 4:
        score += 1; reasons.append("4-consonant run")
    if vr < 0.22 and len(alpha) >= 7:
        score += 2; reasons.append(f"vowel ratio {vr:.0%}")
    if digits >= 3:
        score += 2; reasons.append(f"{digits} digits")
    elif digits and len(alpha) <= 6:
        score += 1; reasons.append("digits in short name")
    if hyphens >= 3:
        score += 2; reasons.append(f"{hyphens} hyphens")
    elif hyphens == 2:
        score += 1; reasons.append("2 hyphens")
    if len(c) >= 26:
        score += 1; reasons.append("very long")
    # Stems are positive evidence only for a compact, unhyphenated name.
    # Several stems strung together with hyphens is exact-match-domain
    # keyword stuffing, which is a spam signal rather than a brandable one.
    if hits >= 3 and hyphens >= 1:
        score += 2; reasons.append(f"{hits} stems + hyphens (EMD stuffing)")
    elif hits >= 4:
        score += 1; reasons.append(f"{hits} stems (keyword-stuffed)")
    elif hits and hyphens <= 1:
        score -= min(hits, 2); reasons.append(f"{hits} common stem(s)")

    verdict = ("generated" if score >= 3
               else "suspicious" if score == 2
               else "plausible")
    return verdict, score, "; ".join(reasons) or "unremarkable"


if __name__ == "__main__":
    SPAM = ["lreeswcqcxz.blogspot.com", "pkbtembnm.blogspot.com",
            "dsspkjk.blogspot.com", "keshpakcxz.blogspot.com",
            "seo-anomaly-top-42.xyz", "bhs-links-bg.xyz",
            "us-en--prozenith.com", "2020-directory.com",
            "addurl-directory.com", "health-supplements-review.com",
            "divinehealthandhealing-ways.com", "a2zseoarticles.com",
            "99ranks.com", "wwwhollywoodk.blogspot.com",
            "general-health-spectrum.com", "daadvn.blogspot.com"]
    GOOD = ["leafysouls.com", "spotmebro.com", "leanbulking.com",
            "thekeytoglutenfree.com", "adventurerz.com",
            "valentinosnaturals.com", "nootropicsexpert.com",
            "generationiron.com", "mindbodydad.com", "bbcgoodfood.com",
            "eastbayexpress.com", "worldofvegan.com", "alexfergus.com",
            "drywearapparel.com", "cleanlabelproject.org",
            "thesun.co.uk", "human-memory.net", "fitnessvolt.com"]
    print(f"{'DOMAIN':40}{'VERDICT':12}{'SCORE':>6}  DETAIL")
    tp = fp = 0
    for d in SPAM:
        v, s, why = name_shape(d)
        tp += v != "plausible"
        print(f"{d:40}{v:12}{s:>6}  {why}")
    print("-" * 90)
    for d in GOOD:
        v, s, why = name_shape(d)
        fp += v != "plausible"
        print(f"{d:40}{v:12}{s:>6}  {why}")
    print()
    print(f"spam flagged     : {tp}/{len(SPAM)}")
    print(f"good FALSE-flags : {fp}/{len(GOOD)}")
