import csv, datetime
rows = list(csv.DictReader(open('out/domains_master.csv')))
TODAY = '2026-11-02'

# Allowlist: genuine local-SEO citations / directories / search+review platforms
# and real lawn/home industry blogs & associations. These are NEVER disavowed.
KEEP = {
 # citations / directories / search / review platforms
 'bbb.org','yellowpages.com','yp.com','chamberofcommerce.com','dexknows.com',
 'birdeye.com','2findlocal.com','ibegin.com','mylocalservices.com','hometownguru.com',
 'landscapeprofessionals.org','superpages.com','bing.com','bingapis.com','brandfetch.com',
 'cgmimm.com',
 # real lawn / home industry sites, associations, blogs
 'rockwaterfarm.com','completegardening.com','simplylawn.com','positivebloom.com',
 'thelandscapeconnection.com','lawnspedia.com','themowersguide.com','vohslandscaping.com',
 'boyerslawncare.com','averagedudeoutdoors.com','todayshomeowner.com','housemethod.com',
 'landscapeleadership.com',
}

# every distinct referring domain across both tools
all_domains = sorted({r['domain'].strip().lower() for r in rows if r['domain'].strip()})
disavow = [d for d in all_domains if d not in KEEP]
kept    = [d for d in all_domains if d in KEEP]

with open('out/disavow_callturfsup_COMPLETE.txt','w') as f:
    f.write("# Google Disavow File (COMPLETE) - callturfsup.com\n")
    f.write(f"# Generated: {TODAY}\n")
    f.write("# Sources: Ahrefs (live) + Semrush, union by source.\n")
    f.write(f"# Total referring domains assessed: {len(all_domains)}\n")
    f.write(f"# Disavowed: {len(disavow)}  |  Kept (legitimate, NOT disavowed): {len(kept)}\n")
    f.write("#\n")
    f.write("# This is the consolidated file: ALL spam, link-scheme, PBN, brand-mention-farm,\n")
    f.write("# AND exact-match Gainesville/Haymarket commercial-anchor domains are included.\n")
    f.write("# (The Harbinger 'held' set is folded in per instruction - no separate pending list.)\n")
    f.write("#\n")
    f.write("# The ONLY domains excluded are these genuine citations / directories / industry\n")
    f.write("# sites (disavowing them would harm local SEO):\n")
    for d in kept:
        f.write(f"#   kept: {d}\n")
    f.write("#\n")
    for d in disavow:
        f.write(f"domain:{d}\n")

print('total domains assessed:', len(all_domains))
print('DISAVOWED (complete):', len(disavow))
print('kept (legit allowlist):', len(kept))
print('kept list:', ', '.join(kept))
