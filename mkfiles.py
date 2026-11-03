import openpyxl, re
from collections import defaultdict
WB="/home/user/test/NewGarden_Backlinks_Audit.xlsx"; today="2026-11-03"
wb=openpyxl.load_workbook(WB, data_only=True)
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^domain:','',re.sub(r'^https?://','',s)).rstrip('/')

# reason per disavow domain from All Backlinks
ab=wb["All Backlinks"]; abh=[c.value for c in ab[1]]; Ai={h:i for i,h in enumerate(abh)}
anchors=defaultdict(list); hosts=set()
for row in ab.iter_rows(min_row=2):
    d=norm(row[Ai['Referring Domain']].value); anchors[d].append((str(row[Ai['Anchor Type']].value),str(row[Ai['Anchor Text']].value)))
def reason(d):
    ats=[a for a,_ in anchors.get(d,[])]; txt=" ".join(t for _,t in anchors.get(d,[])).lower()
    if d=="rosih.ru": return "Image hotlink / scraper (one domain, image-source links)"
    if any('sales copy' in a.lower() for a in ats): return "SEO sales-copy / PBN anchor"
    if re.search(r'(casino|porn|pharma|viagra|escort|loan|betting)',txt): return "Off-topic (gambling/pharma/adult)"
    if re.search(r'(backlink|seo|dapa|rankcheck|directory|listing|bookmark|domainlist|aged.?domain)',d): return "Spam host name (directory / SEO / backlink marketplace)"
    return "Other spam anchor/title evidence"

dl=wb["Disavow List"]; doms=[norm(r[0].value) for r in dl.iter_rows(min_row=2) if r[0].value]
groups=defaultdict(list)
for d in doms: groups[reason(d)].append(d)
order=["SEO sales-copy / PBN anchor","Spam host name (directory / SEO / backlink marketplace)","Off-topic (gambling/pharma/adult)","Image hotlink / scraper (one domain, image-source links)","Other spam anchor/title evidence"]
header=f"""# Google disavow file - New Garden Landscaping & Nursery
# Property: newgarden.com  (domain property - covers www., plants. and estimate. subdomains)
# Generated: {today}   |   Source: Semrush export (2,683 referring domains / 8,086 backlinks), cross-checked against Ahrefs
#
# Spam referring domains with at least one dofollow link: {len(doms)}
# Each line rests on link evidence (spam anchor, spam page title, or a known link-network / directory host) - not on Authority Score or TLD alone.
#
# HELD links are NOT in this file. {202} domains carry exact-match commercial/geo anchors that MAY be
#   commissioned placements; they wait in disavow_newgarden_PENDING_partner_confirmation.txt until confirmed.
# In New Garden's brief the person who confirms is called the "supplier"; the workbook calls the same role
#   the "partner". They are the same role.
#
# DO NOT UPLOAD until BOTH are true:
#   1. the previous SEO supplier has confirmed which placements were commissioned, and
#   2. you have checked Google Search Console for a manual action.
# Prefer monitoring: disavow only if a manual action exists or the client confirms buying links.
# Check Search Console for an existing disavow file on this property first - uploading REPLACES the current file.
# No client-owned redirect domains were found, so this single file is the complete set for the property.
"""
lines=[header]
for g in order:
    if not groups.get(g): continue
    lines.append(f"\n# --- {g} ({len(groups[g])}) ---")
    for d in sorted(groups[g]): lines.append(f"domain:{d}")
open("/home/user/test/disavow_newgarden.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
print("disavow_newgarden.txt:",len(doms),"domains; groups:",{g:len(v) for g,v in groups.items()})

# pending file
pend=wb["Pending Disavow Lines"]; pl=[norm(r[0].value) for r in pend.iter_rows(min_row=2) if r[0].value]
ph=f"""# PENDING - New Garden Landscaping & Nursery (newgarden.com)
# Generated: {today}
# {len(pl)} referring domains with an EXACT-MATCH commercial / geo anchor (Greensboro / Winston-Salem local-service
#   copy) pointing at deep /service/ and /location/ pages. These MAY be commissioned placements.
#   Independent check: Ahrefs marks these anchors NOT spam. Held out of the disavow file until confirmed.
#
# ACTION: ask the previous SEO supplier (the workbook's "partner") which of these were commissioned.
#   APPEND to disavow_newgarden.txt ONLY the domains the supplier does NOT confirm. Keep the rest.
# (45 further Tab 05 domains are nofollow-only = no action needed either way; they are not listed here.)
"""
open("/home/user/test/disavow_newgarden_PENDING_partner_confirmation.txt","w",encoding="utf-8").write(ph+"\n".join(f"domain:{d}" for d in sorted(pl))+"\n")
print("pending file:",len(pl),"domains")
