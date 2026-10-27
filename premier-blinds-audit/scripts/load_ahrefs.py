"""Loader for Ahrefs UTF-16 exports (converted to UTF-8 TSV). Ahrefs adds
referring domains, link detail and HTTP status — never a metric."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import load

def _rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def backlinks(path):
    out=[]
    for r in _rows(path):
        out.append({
            "source_url": (r.get("Referring page URL") or "").strip(),
            "source_title": (r.get("Referring page title") or "").strip(),
            "target_url": (r.get("Target URL") or "").strip(),
            "anchor": (r.get("Anchor") or "").strip(),
            "nofollow": "true" if (r.get("Nofollow") or "").strip().lower()=="true" else "false",
            "http": (r.get("Referring page HTTP code") or "").strip(),
            "first_seen": (r.get("First seen") or "").strip(),
            "last_seen": (r.get("Last seen") or "").strip(),
            "lost": (r.get("Lost") or "").strip(),
            "type": (r.get("Type") or "").strip(),
        })
    return out

def refdomains(path):
    out=[]
    for r in _rows(path):
        out.append({"domain": (r.get("Domain") or "").strip().lower(),
                    "dr": (r.get("DR") or "").strip(),
                    "first_seen": (r.get("First seen") or "").strip()})
    return out

def canon(url):
    u=load.host_of(url)
    path=url.split(u,1)[-1] if u else ""
    path=path.split("?")[0].split("#")[0].rstrip("/").lower()
    return u+path

if __name__=="__main__":
    import glob
    A="/home/user/work/ahrefs_in"
    abl=backlinks(A+"/bl.tsv"); ard=refdomains(A+"/rd.tsv")
    # Semrush sets
    sbl,_,_=load.read_backlinks(sorted(glob.glob("premier/data/fetch/bl_*.csv")))
    srd,_=load.read_refdomains(sorted(glob.glob("premier/data/rd/rd_*.csv")))
    srd_set={r["domain"].strip().lower() for r in srd}
    match=load.build_refdomain_matcher(srd_set)
    # Ahrefs refdomain roots not in Semrush
    ard_roots={load.root_domain(d["domain"]) for d in ard}
    new_rd=sorted(d for d in ard_roots if d not in srd_set and match(d) not in srd_set)
    print("Ahrefs backlinks:",len(abl)," Ahrefs refdomains:",len(ard))
    print("Ahrefs refdomain roots:",len(ard_roots))
    print("NEW refdomains (not in Semrush set):",len(new_rd))
    print("  sample:",new_rd[:20])
    # link-level overlap
    scan={ (canon(l["source_url"]),canon(l["target_url"]),(l["anchor"] or "").strip().lower()) for l in sbl }
    newlinks=[l for l in abl if (canon(l["source_url"]),canon(l["target_url"]),(l["anchor"] or "").strip().lower()) not in scan]
    print("NEW links (not in Semrush by canon key):",len(newlinks)," of",len(abl))
    # http code distribution
    from collections import Counter
    print("Ahrefs HTTP codes:",dict(Counter(l["http"] for l in abl).most_common(8)))
    print("Ahrefs target hosts:",dict(Counter(load.host_of(l["target_url"]) for l in abl).most_common(6)))
