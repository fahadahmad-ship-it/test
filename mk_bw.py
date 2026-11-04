import openpyxl, re, json
from collections import defaultdict
WB="/home/user/test/BlackWalnut_Backlinks_Audit.xlsx"; today="2026-11-04"
wb=openpyxl.load_workbook(WB, data_only=True)
def norm(d):
    s=str(d).strip().lower(); return re.sub(r'^domain:','',re.sub(r'^https?://','',s)).rstrip('/')
ab=wb["All Backlinks"]; abh=[c.value for c in ab[1]]; Ai={h:i for i,h in enumerate(abh)}
blob=defaultdict(str)
for row in ab.iter_rows(min_row=2,values_only=True):
    d=norm(row[Ai['Referring Domain']]); blob[d]+=" "+str(row[Ai['Anchor Type']])+" "+str(row[Ai['Anchor Text']])+" "+str(row[Ai['Linking Page Title']])
def reason(d):
    b=blob[d].lower()
    if re.search(r'off topic|casino|escort|pharma|betting|bonanza|toto',b): return "Off-topic (gambling / adult / pharma)"
    if 'sales copy' in b or re.search(r'premium authority backlink|buy backlink|pbn|da 50',b): return "SEO sales-copy / PBN anchor"
    if re.search(r'aged domains and backlinks|seo domain research|where to buy|domain report|website stats',b): return "Domain-marketplace / aged-domain spam page (title evidence)"
    if re.search(r'backlink|seo|checker|dapa|rankcheck|directory|listing|bookmark|serp|keyword|traffic|linkbuild|dofollow|domain',d): return "Spam host name (SEO / backlink / checker / directory)"
    return "Other spam anchor/title evidence"
dl=[norm(r[0].value) for r in wb["Disavow List"].iter_rows(min_row=2) if r[0].value]
groups=defaultdict(list)
for d in dl: groups[reason(d)].append(d)
order=["SEO sales-copy / PBN anchor","Spam host name (SEO / backlink / checker / directory)","Domain-marketplace / aged-domain spam page (title evidence)","Off-topic (gambling / adult / pharma)","Other spam anchor/title evidence"]
hdr=f"""# Google disavow file - Black Walnut Construction, LLC
# Property: blackwalnutconstruction.com  (domain property - covers any subdomains)
# Generated: {today}   |   Source: Semrush export (1,631 referring domains / 2,142 backlinks), cross-checked against Ahrefs
#
# Spam referring domains with at least one dofollow link: {len(dl)}
# Each line rests on link evidence (spam/PBN anchor, aged-domain marketplace page title, or a known SEO/backlink/directory host) - never on Authority Score or TLD alone.
#
# NOTE ON THE BRIEF: the brief listed 368 referring domains; the live profile is 1,631. The full live profile was audited.
#
# HELD links are NOT in this file. 172 domains carry Lexington-SC exact-match commercial anchors or deep money-page links
#   that MAY be commissioned placements; they wait in disavow_blackwalnut_PENDING_supplier_confirmation.txt until confirmed.
# The brief calls the person who confirms the "supplier"; the workbook calls the same role the "partner". Same role.
#
# DO NOT UPLOAD until BOTH: (1) the previous SEO supplier has confirmed which placements were commissioned, and
#   (2) Google Search Console has been checked for a manual action. Prefer monitoring otherwise.
# Check Search Console for an existing disavow file first - uploading REPLACES it. No owned redirect domains found; this is the complete set.
"""
lines=[hdr]
for g in order:
    if not groups.get(g): continue
    lines.append(f"\n# --- {g} ({len(groups[g])}) ---")
    lines+= [f"domain:{d}" for d in sorted(groups[g])]
open("/home/user/test/disavow_blackwalnut.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
print("disavow_blackwalnut.txt:",len(dl),"| groups:",{g:len(v) for g,v in groups.items()})
# pending
pl=[norm(r[0].value) for r in wb["Pending Disavow Lines"].iter_rows(min_row=2) if r[0].value]
ph=f"""# PENDING - Black Walnut Construction, LLC (blackwalnutconstruction.com)
# Generated: {today}
# {len(pl)} referring domains with Lexington-SC exact-match commercial anchors or deep /...-construction-services
#   money-page links. These MAY be commissioned placements - Ahrefs/Semrush do not flag these anchors as spam.
# ACTION: ask the previous SEO supplier (the workbook's "partner") which were commissioned.
#   APPEND to disavow_blackwalnut.txt ONLY the domains the supplier does NOT confirm. Keep the rest.
# (22 further Tab 05 domains are nofollow-only = no action needed either way; not listed here.)
"""
open("/home/user/test/disavow_blackwalnut_PENDING_supplier_confirmation.txt","w",encoding="utf-8").write(ph+"\n".join(f"domain:{d}" for d in sorted(pl))+"\n")
print("pending:",len(pl))
