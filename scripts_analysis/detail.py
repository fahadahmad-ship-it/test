import json, csv
from collections import defaultdict

with open("/home/user/test/audit/data/classified_domains.json", encoding="utf-8") as f:
    dom = json.load(f)
links = []
with open("/home/user/test/audit/data/classified_links.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        links.append(row)
dlinks = defaultdict(list)
for r in links:
    dlinks[r["referring_domain"]].append(r)

check = ["seolium.com","winningseo.site","eliteseo.site","backlinkstree.com",
         "booastrankingwithbacklinks.com","bestseobacklinkforsite.com",
         "awards.pulseofthecitynews.com","nexusnext.agency","rankyour.website"]
for d in check:
    v = dom.get(d, {})
    print("\n==========", d, "| status:", v.get("status"), "| do:", v.get("dofollow"),
          "nf:", v.get("nofollow"), "| flag:", v.get("spam_flag"))
    print("  top_anchor:", repr(v.get("top_anchor")))
    print("  example_title:", repr(v.get("example_title")))
    print("  example_url:", repr(v.get("example_url")))
    print("  reason:", repr(v.get("reason"))[:200])
    for r in dlinks.get(d, []):
        print("   LINK anchor=%r | nofollow=%r | link_type=%r | title=%r | url=%r" % (
            r.get("anchor"), r.get("nofollow"), r.get("link_type"),
            (r.get("title") or "")[:90], (r.get("url") or "")[:90]))
