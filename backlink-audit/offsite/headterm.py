"""Correction: a page's top keyword is not always its opportunity keyword.

top-pages returns the keyword a page gets the MOST TRAFFIC from, which is
usually one it already ranks well for. The opportunity is the opposite -- a
high-volume term the page ranks poorly for. magnesium-bisglycinate-vs-glycinate
reports "magnesium bisglycinate vs magnesium glycinate" (3,300, #5) because
that is where its traffic comes from, while the actual prize is "magnesium
bisglycinate" (26,000, #13) at eight times the CPC.
"""
CTR = {1: .270, 2: .155, 3: .110, 4: .080, 5: .062, 6: .049, 7: .040,
       8: .033, 9: .028, 10: .025, 11: .020, 12: .017, 13: .015, 14: .013,
       15: .012, 16: .011, 17: .010, 18: .009, 19: .008, 20: .007,
       23: .004, 25: .003}

# page, head keyword, volume, current pos, target pos, cpc, refdomains
CASES = [
    ("best-magnesium-for-sleep", "best magnesium for sleep",
     29000, 9, 4, 0.35, 0),
    ("best-magnesium-for-sleep", "which magnesium is best for sleep",
     9600, 8, 4, 0.04, 0),
    ("magnesium-bisglycinate-vs-glycinate", "magnesium bisglycinate",
     26000, 13, 8, 0.50, 19),
    ("creatine-before-or-after-…-take-it", "when to take creatine",
     28000, 25, 12, 0.03, 3),
    ("creatine-before-or-after-…-take-it", "creatine before or after workout",
     21000, 14, 8, 0.03, 3),
    ("best-multivitamin-for-men", "best multivitamin for men",
     29000, 23, 21, 0.30, 237),
    ("best-multivitamin-for-men", "best men's multivitamin",
     12100, 14, 13, 0.30, 237),
    ("magnesium-taurate-vs-glycinate", "magnesium taurate benefits",
     5400, 6, 4, 0.05, 7),
    ("magnesium-malate-vs-glycinate", "magnesium malate benefits",
     9000, 3, 2, 0.06, 3),
]
print(f"{'PAGE':38}{'HEAD KEYWORD':36}{'VOL':>7}{'RD':>5}"
      f"{'POS':>5}{'->':>4}{'GAIN':>7}{'$/MO':>7}")
print("-" * 109)
tot = {}
for page, kw, vol, pos, tgt, cpc, rd in CASES:
    gain = vol * (CTR.get(tgt, .003) - CTR.get(pos, .003))
    print(f"{page[:36]:38}{kw[:34]:36}{vol:>7,}{rd:>5}{pos:>5}{tgt:>4}"
          f"{round(gain):>7,}{round(gain*cpc):>7,}")
    tot.setdefault(page, [0, 0, rd])
    tot[page][0] += gain
    tot[page][1] += gain * cpc
print()
print(f"{'PAGE TOTAL':38}{'REF DOMAINS':>14}{'GAIN/MO':>12}{'$/MO':>10}")
print("-" * 76)
for p, (g, v, rd) in sorted(tot.items(), key=lambda x: -x[1][1]):
    print(f"{p[:36]:38}{rd:>14}{round(g):>12,}{round(v):>10,}")
