#!/usr/bin/env python3
"""
report.py — generate the critical-analysis writeup (markdown) from the classified data.
Run after classify.py/build.py so numbers reconcile with the workbook.
Writes out/Jaco_Contracting_Backlink_Audit_Analysis.md
"""
import json, os, datetime
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
CLIENT = "jacocontracting.com"

CLOUDFLARE_PREFIXES = ("104.21.", "172.67.", "104.16.", "104.17.", "104.18.", "104.19.", "104.20.", "172.64.", "172.65.", "172.66.", "172.68.", "172.69.", "172.70.", "172.71.")

def mon(u):
    return datetime.datetime.fromtimestamp(u, datetime.timezone.utc).strftime("%Y-%m") if u else "unknown"

def main():
    domains = json.load(open(os.path.join(DATA, "domains_classified.json")))
    links = [json.loads(l) for l in open(os.path.join(DATA, "links_classified.jsonl"))]
    by = defaultdict(list)
    for L in links:
        by[L["refdomain"]].append(L)
    doms = list(domains.values())
    nd = len(doms); nl = len(links)
    sc = Counter(v["status"] for v in doms)
    bc = Counter();
    for v in doms: bc[v["status"]] += v["backlinks"]

    spam_dof = sc["Spam (Disavow)"]; spam_nof = sc["Spam (Nofollow, No Action)"]
    held_p = sc["Held (Pending Partner)"]; held_nf = sc["Held (Nofollow, No Action)"]
    keep = sc["Keep"]
    spam_total = spam_dof + spam_nof; held_total = held_p + held_nf

    # anchor types
    at = Counter(L["anchor_type"] for L in links)
    atd = defaultdict(set)
    for L in links: atd[L["anchor_type"]].add(L["refdomain"])

    # target split
    def deep(L):
        u = L["target_url"].lower().split("//",1)[-1].replace("www.","").rstrip("/")
        return u.startswith(CLIENT) and u[len(CLIENT):] not in ("","/")
    SCHEME=("Spam: keyword stuffed SEO sales copy","Spam: off topic","Naked URL")
    COMM=("Exact match commercial","Exact match commercial (geo)")
    scheme_home=sum(1 for L in links if L["anchor_type"] in SCHEME and not deep(L))
    comm_deep=sum(1 for L in links if L["anchor_type"] in COMM and deep(L))
    comm_total=sum(1 for L in links if L["anchor_type"] in COMM)

    # first-seen timeline of disavow domains
    fs = Counter(mon(v.get("first_seen")) for v in doms if v["status"]=="Spam (Disavow)")
    recent = fs.get("2026-09",0)+fs.get("2026-10",0)

    # /24 networks (exclude Cloudflare + big CDNs)
    c24 = Counter()
    for v in doms:
        ip=v.get("ip","")
        if ip and ip.count(".")==3 and not ip.startswith(CLOUDFLARE_PREFIXES):
            c24[".".join(ip.split(".")[:3])+".0/24"]+=1
    top_nets=[(n,c) for n,c in c24.most_common(8) if c>=5]

    # top salescopy anchor
    sales=Counter(L["anchor"] for L in links if L["anchor_type"]=="Spam: keyword stuffed SEO sales copy")
    top_sales=sales.most_common(1)[0] if sales else ("",0)
    top_sales_dom=len({L["refdomain"] for L in links if L["anchor"]==top_sales[0]})

    held_zero=sum(1 for v in doms if v["status"].startswith("Held") and (v.get("organic_traffic",0) or 0)==0)
    # keep genuine high authority
    keep_hi=sorted([v for v in doms if v["status"]=="Keep"], key=lambda v:-(v.get("AS") or 0))[:10]

    L=[]
    def p(s=""): L.append(s)
    p(f"# Backlink Audit — Critical Analysis: {CLIENT}")
    p()
    p(f"*Prepared {datetime.date.today().isoformat()} · Harbinger Marketing format · Semrush = metric source, Ahrefs = discovery + live-page corroboration*")
    p()
    p("## Headline")
    p()
    p(f"**{CLIENT} is under an active, accelerating negative-SEO / PBN link-spam attack.** "
      f"Of **{nd:,} referring domains** now in the live profile, **{spam_total:,} ({spam_total/nd:.0%}) are spam**. "
      f"**{spam_dof:,} carry at least one dofollow link and go in the disavow file**; {spam_nof:,} more are spam "
      f"but entirely nofollow (no action needed). **{held_total:,}** domains are **held** for the previous SEO "
      f"partner to confirm before any disavow, because they carry exact-match commercial anchors or deep-page "
      f"links that may have been commissioned. **{keep:,}** are genuine and kept.")
    p()
    p("## The profile at a glance")
    p()
    p("| Status | Domains | Backlinks | Share of domains |")
    p("|---|---:|---:|---:|")
    for s in ["Spam (Disavow)","Held (Pending Partner)","Held (Nofollow, No Action)","Spam (Nofollow, No Action)","Keep","Own Site"]:
        p(f"| {s} | {sc.get(s,0):,} | {bc.get(s,0):,} | {sc.get(s,0)/nd:.1%} |")
    p(f"| **Total** | **{nd:,}** | **{nl:,}** | **100%** |")
    p()
    p(f"- Live profile (Semrush): **3,258 backlinks / 1,292 referring domains / Authority Score 17**. Ahrefs: DR 21.")
    p(f"- Merged Semrush + Ahrefs: **{nl:,} unique links across {nd:,} referring domains** (1,360 links discovered only by Ahrefs).")
    p(f"- **One Search Console property.** Every link points directly at {CLIENT}; no owned domains 301-redirect in, "
      f"so a single disavow file (`disavow_jacocontracting.txt`) covers the whole profile.")
    p()
    p("## Seven findings")
    p()
    p(f"1. **{spam_total:,} of {nd:,} referring domains are spam.** {spam_dof:,} have a dofollow link and are in the "
      f"disavow file; {spam_nof:,} are nofollow and pass no value.")
    p(f"2. **The attack is recent and accelerating.** Referring domains sat at ~200–280 for most of 2025–early 2026, "
      f"then climbed 362 (Jul 26) → 406 (Aug) → 526 (Sep) → **1,289 (Oct 2026)**. Of the {spam_dof:,} disavow domains, "
      f"**{recent:,} first appeared in Sep–Oct 2026** — the spam roughly tripled the profile in two months. "
      f"The brief's older figures are a stale snapshot; this audit covers the full live profile.")
    p(f"3. **One file covers everything.** No redirect/owned domains feed the site, so you upload a single file for the "
      f"{CLIENT} property. (Confirm whether a disavow file already exists on the property first — uploading replaces it.)")
    p(f"4. **Two campaigns, easy to tell apart by target page.** **{scheme_home:,} link-scheme / sales-copy / naked-URL "
      f"links hit the home page**; the **{comm_deep:,} exact-match commercial links hit deep location & service pages** "
      f"(Covington, Atlanta, Chattanooga, Macon roofing pages). The home-page flood is the attack; the deep-page "
      f"commercial anchors are what may have been commissioned.")
    p(f"5. **The dominant anchor is backlink sales copy naming the client's own domain.** "
      f"\"{top_sales[0][:70]}…\" appears on **{top_sales_dom:,} domains**. The whole anchor profile is dominated by "
      f"PBN templates such as \"High Quality Dofollow Backlinks DA 50 PA 40 Premium PBN Network Service…\".")
    p(f"6. **{held_total:,} domains are held for the partner**, in case any exact-match commercial placements were paid "
      f"for. They are **excluded from the disavow file** until confirmed. The big one, `addirectory.org`, alone "
      f"auto-generates {max((v['backlinks'] for v in doms if v['domain']=='addirectory.org'), default=0)} "
      f"\"Roofing Contractor Covington\" links.")
    if top_nets:
        nets_str = ", ".join(f"{n} ({c})" for n,c in top_nets[:3])
        p(f"7. **Held does not mean good.** {held_zero:,} of the {held_total:,} held domains have zero organic traffic. "
          f"Several spam clusters share a /24 subnet — {nets_str} — i.e. single operators running many domains "
          f"(Cloudflare/CDN ranges excluded). No domain is disavowed on a shared IP alone.")
    else:
        p(f"7. **Held does not mean good.** {held_zero:,} of the {held_total:,} held domains have zero organic traffic.")
    p()
    p("## Anchor-text profile (all backlinks)")
    p()
    p("| Anchor type | Backlinks | Share | Referring domains |")
    p("|---|---:|---:|---:|")
    for t,c in at.most_common():
        p(f"| {t} | {c:,} | {c/nl:.1%} | {len(atd[t]):,} |")
    p()
    p("## What is genuine (kept)")
    p()
    p("The audit protects real citations. Highest-authority kept domains include:")
    p()
    p("| Domain | Authority Score | Organic traffic | Links |")
    p("|---|---:|---:|---:|")
    for v in keep_hi:
        p(f"| {v['domain']} | {v.get('AS','')} | {v.get('organic_traffic',0):,} | {v['backlinks']} |")
    p()
    p("## Method & evidence rules")
    p()
    p("- **Semrush is the source for every metric** (Authority Score, backlinks, referring domains, traffic, keywords). "
      "Ahrefs contributes extra link discovery and the live-page HTTP check only — never a metric.")
    p("- **Nothing is disavowed on a score, a TLD, or a shared IP alone.** Every disavow line rests on visible "
      "evidence: a spam anchor, a spam page title, or a known link-network / backlink-marketplace host name.")
    p("- **When in doubt, hold.** Exact-match commercial anchors and deep money-page links may be commissioned "
      "placements; they are held for the previous partner, never auto-disavowed.")
    p("- Off-topic spam (gambling / pharma / adult / malicious Telegram links) is treated as spam even when a domain "
      "also carries a commercial anchor — it is never a legitimate commissioned placement.")
    p()
    p("## Deliverables")
    p()
    p("- **`Jaco_Contracting_Backlinks_Audit.xlsx`** — 7 tabs (Summary, Referring Domain Audit, All Backlinks, "
      "Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List), signed-off Harbinger format.")
    p(f"- **`disavow_jacocontracting.txt`** — {spam_dof:,} `domain:` lines, grouped by reason, for the {CLIENT} "
      "Search Console property.")
    p()
    p("## Before you upload — required steps")
    p()
    p("1. **Confirm the Held set with the previous SEO partner / the business.** If any held domains were "
      "commissioned placements, do not disavow them; append the rest from the *Pending Disavow Lines* tab.")
    p("2. **Check whether a disavow file already exists** on the Search Console property. If one does, uploading "
      "**replaces** it — merge first. If the client has checked and there is none, this is the first file.")
    p("3. Do not submit to Google Search Console on the client's behalf without sign-off.")
    p()
    out=os.path.join(OUT,"Jaco_Contracting_Backlink_Audit_Analysis.md")
    open(out,"w",encoding="utf-8").write("\n".join(L)+"\n")
    print("wrote",out)

if __name__=="__main__":
    main()
