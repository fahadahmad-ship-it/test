#!/usr/bin/env python3
"""Robust loader for the Semrush farison backlinks CSV (semicolon, unquoted, HTML entities,
titles/anchors may contain ';'). Reconstructs rows by right-anchoring the 6 fixed trailing
fields and locating the target_url (contains farison) in the middle."""
import sys, glob, html, collections, re, json, os
from urllib.parse import urlparse

COLS = ["source_url","source_title","target_url","anchor","nofollow","first_seen","last_seen","response_code","redirect_url","page_authority_score"]

def host(u):
    try:
        h=urlparse(u.strip()).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except: return ""

def reg_domain(h):
    if not h: return ""
    parts=h.split("."); two=("co.uk","org.uk","com.au","co.in","co.nz","com.br","gb.net","de.com")
    if len(parts)>=3 and ".".join(parts[-2:]) in two: return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts)>=2 else h

def parse_file(path):
    rows=[]; bad=0
    with open(path, encoding="utf-8", errors="replace") as f:
        lines=f.read().split("\n")
    start=1 if lines and lines[0].startswith("source_url") else 0
    for ln in lines[start:]:
        if not ln.strip(): continue
        raw=html.unescape(ln)
        parts=raw.split(";")
        if len(parts)<10: bad+=1; continue
        # right anchor
        page_as=parts[-1]; redirect=parts[-2]; resp=parts[-3]; last=parts[-4]; first=parts[-5]; nofo=parts[-6]
        if nofo not in ("true","false"):
            # misalignment (rare) - try to find nofollow token near the tail
            idx=None
            for i in range(len(parts)-1,0,-1):
                if parts[i] in ("true","false"): idx=i; break
            if idx is None: bad+=1; continue
            nofo=parts[idx]; first=parts[idx+1]; last=parts[idx+2]; resp=parts[idx+3] if idx+3<len(parts) else ""
            redirect=parts[idx+4] if idx+4<len(parts) else ""; page_as=parts[idx+5] if idx+5<len(parts) else ""
            middle=parts[1:idx]
        else:
            middle=parts[1:-6]
        src=parts[0]
        # find target_url in middle (contains farison)
        tidx=None
        for i,m in enumerate(middle):
            if "farison" in m.lower() and m.strip().lower().startswith(("http","//")) or ("farison.com" in m.lower()):
                tidx=i; break
        if tidx is None:
            # fallback: last http in middle is target
            for i,m in enumerate(middle):
                if m.strip().lower().startswith("http"): tidx=i
        if tidx is None:
            title=";".join(middle); target=""; anchor=""
        else:
            title=";".join(middle[:tidx]); target=middle[tidx]; anchor=";".join(middle[tidx+1:])
        rows.append(dict(source_url=src, source_title=title, target_url=target, anchor=anchor,
                         nofollow=nofo, first_seen=first, last_seen=last, response_code=resp,
                         redirect_url=redirect, page_as=page_as))
    return rows, bad

def main():
    files=sorted(glob.glob("/home/user/test/data/farison/fetch/bl_*.csv"), key=lambda p:int(re.findall(r'\d+',os.path.basename(p))[0]))
    allrows=[]; totbad=0
    for p in files:
        r,b=parse_file(p); allrows+=r; totbad+=b
    print("files:",len(files),"| rows parsed:",len(allrows),"| bad/skipped:",totbad)
    # dedupe on (source_url,target_url,anchor)
    seen=set(); dedup=[]
    for r in allrows:
        k=(r["source_url"].strip().lower(), r["target_url"].strip().lower(), r["anchor"].strip().lower())
        if k in seen: continue
        seen.add(k); dedup.append(r)
    print("after dedupe:",len(dedup))
    # property split via redirect_url host (attribution = redirect host if present else target host)
    prop=collections.Counter()
    for r in dedup:
        rh=host(r["redirect_url"]) if r["redirect_url"].strip() else ""
        p = reg_domain(rh) if rh else reg_domain(host(r["target_url"]))
        prop[p]+=1
    print("\nAttribution property (redirect host else target host):")
    for k,v in prop.most_common(10): print(f"  {v}: {k}")
    # referring domains
    refdoms=collections.Counter(reg_domain(host(r["source_url"])) for r in dedup)
    print("\nDistinct referring (registrable) domains in backlinks:", len(refdoms))
    print("Top referring domains by links:")
    for k,v in refdoms.most_common(12): print(f"  {v}: {k}")
    # nofollow
    nofo=collections.Counter(r["nofollow"] for r in dedup); print("\nnofollow:",dict(nofo))
    resp=collections.Counter(r["response_code"] for r in dedup); print("response_code:",dict(resp.most_common(6)))
    # anchor pattern buckets
    def abucket(a):
        al=a.lower()
        if any(k in al for k in ["backlink","pbn","da 50","pa 40","seo ","premium seo","rank first","buy backlink","dofollow backlinks","link building","trust flow","high authority","boost","niche edit","contextual link"]): return "PBN/sales-copy"
        if al in ("farison.com","farison",""): return "naked/empty"
        if "farison lawn care" in al or al=="farison lawn care": return "branded"
        if any(k in al for k in ["lawn","mosquito","weed","flea","tick","tree","shrub","grub","fertiliz","mow","aeration","landscap","irrigation"]) and any(k in al for k in [" ky"," in"," in,"," ky,","louisville","shelbyville","clarksville","washington","albany","prospect","bardstown","kentucky","indiana"]): return "exact-match geo commercial"
        if al in ("visit website","website","google","read more","click here","visit site"): return "generic"
        return "other"
    ab=collections.Counter(abucket(r["anchor"]) for r in dedup)
    print("\nAnchor buckets (all backlinks):")
    for k,v in ab.most_common(): print(f"  {v}: {k}")
    # redirect property: how many links attributed to lawncare-louisvilleky.com
    lc=sum(1 for r in dedup if "lawncare-louisvilleky" in r["redirect_url"].lower())
    print(f"\nlinks with redirect_url to lawncare-louisvilleky.com: {lc}")
    # save parsed rows
    json.dump(dedup, open("/home/user/test/data/farison/backlinks_parsed.json","w"))
    print("saved parsed ->", "/home/user/test/data/farison/backlinks_parsed.json")

main()
