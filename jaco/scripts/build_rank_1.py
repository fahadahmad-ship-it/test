#!/usr/bin/env python3
import sys

INPUT = "/home/user/test/jaco/data/metrics/shard_1.txt"
OUTPUT = "/home/user/test/jaco/data/metrics/rank_1.csv"

# Domains that returned a Semrush data row (keyword, traffic). Everything else -> 0,0 (no_data).
results = {
    "bbb.org": (9087559, 5384918),
    "backlinksindia.info": (1, 0),
    "backlinksindia.link": (1, 0),
    "backlinksitechecker.online": (2, 0),
    "backlinksocean.link": (16, 0),
    "backlinkspulse.com": (7, 0),
    "backlinkspulse.info": (3, 0),
    "backlinksreport.store": (2, 0),
    "backlinkstores.com": (1, 0),
    "backlinkwizards.link": (5, 0),
    "best-seo-domains.com": (7, 0),
    "bestfloridaseo.com": (1, 0),
    "besthelptips.com": (6, 0),
    "bestlinkchecker.site": (1, 0),
    "bestlinkchecker.website": (1, 0),
    "bestprosintown.com": (92105, 6936),
    "bestseocenter.info": (1, 0),
    "bestseocenter.link": (15, 0),
    "bestseosuite.com": (3, 0),
    "bestsidingrepair.com": (2, 0),
    "bevwo.com": (52, 0),
    "bidhub.com": (1117, 479),
    "big-easy-seo.info": (1, 0),
    "birdeye.com": (4630069, 1123631),
    "bizarchive.com": (151, 0),
    "bizfront.org": (84, 0),
    "bizscoreai.com": (1, 0),
    "blegg.biz": (2, 0),
    "blinks.monster": (2, 0),
    "blinks.sbs": (1, 1),
    "blogdachecker.shop": (3, 0),
    "bloomberry.com": (4328, 2342),
    "bowlisting.com": (81, 0),
    "bravarooftile.com": (12382, 24282),
    "brickvest.com": (16, 0),
    "bubblelife.com": (8926, 5027),
    "buddylinks.org": (8, 0),
    "bulkbacklinkanalyzer.website": (1, 0),
    "bulkbacklinkmaker.space": (1, 0),
    "bulkbacklinkschecker.online": (4, 0),
    "bulkbacklinkschecker.shop": (2, 0),
    "bulkdacheckeronline.space": (2, 0),
    "bulkdacheckertools.online": (1, 0),
    "bulkdapachecker.space": (1, 0),
    "bulkpadachecker.space": (1, 0),
    "bulkpadachecker.store": (3, 0),
    "bunity.com": (43, 313),
    "businesshonors.org": (7, 0),
    "businessresource.co": (86, 0),
    "caatn.org": (136, 100),
    "carroll-ga.org": (1721, 2206),
    "catoosachamberofcommerce.com": (817, 854),
    "chambermaster.com": (210832, 109961),
    "chattanooga-directory.com": (43, 0),
    "childcarepartnerships.org": (1, 0),
    "citationbuilding.site": (1, 0),
    "citylocalhub.com": (6, 0),
    "citysquares.com": (4413, 1143),
    "clicknmark.com": (2, 0),
    "clientim.com": (3, 0),
    "coldlytics.com": (2352, 5559),
    "commercialroofingdirectory.com": (1, 0),
    "competitionchecker.shop": (1, 0),
    "complaintinfo.com": (1, 0),
    "compworth.com": (12, 0),
    "concretenetworkusa.com": (53, 0),
    "constantcontact.com": (106630, 398048),
    "contactout.com": (199793, 120903),
}

with open(INPUT) as f:
    domains = [ln.strip().lower() for ln in f if ln.strip()]

lines = ["domain,organic_keywords,organic_traffic"]
for d in domains:
    kw, tr = results.get(d, (0, 0))
    lines.append(f"{d},{kw},{tr}")

with open(OUTPUT, "w") as f:
    f.write("\n".join(lines) + "\n")

traffic_zero = sum(1 for d in domains if results.get(d, (0, 0))[1] == 0)
print("input_count", len(domains))
print("data_rows", len(lines) - 1)
print("traffic_zero", traffic_zero)
print("results_keys_not_in_input", [k for k in results if k not in set(domains)])
