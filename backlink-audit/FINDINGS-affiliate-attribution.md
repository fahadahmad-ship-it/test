# Affiliate attribution: a rogue affiliate is spamming a PBN

Derived from the 50k backlinks export. No third-party flag involved —
this comes from tracking parameters in the raw target URLs.

## 1. Performance Lab runs Post Affiliate Pro

**567 backlinks across 73 referring domains** carry `a_aid` / `a_bid`
parameters on the target URL:

```
https://www.performancelab.com/products/mind-lab-pro?a_aid=5f4e9bd7d388a&a_bid=aa4be909&data1=86a1n02ku
```

`a_aid` is the affiliate ID, `a_bid` the creative. This is an evidence-based
affiliate whitelist drawn from the data rather than inferred from domain
names — see `out/confirmed_affiliate_domains.csv`.

`fitliving.org` is the same architecture seen from the publisher side —
`/go/` cloaked redirects with structured campaign slugs:

```
fitliving.org/go/supplements-performancelab-prelabpro-gen-all/?%2186a2vjz80
fitliving.org/go/nootropics-perfomancelabmind-productpage-general-all/?...
fitliving.org/go/wl-testolabpro-homepage-general-all/?...
```

Read `{vertical}-{brand}-{product}-{audience}-{geo}`. Unambiguous affiliate
infrastructure, and protected by the brief. Its current `KEEP` verdict is
correct, but was reached via topical relevance rather than this evidence.

## 2. One affiliate ID owns every spam placement

| `a_aid` | Links | Domains | DISAVOW-flagged | Spam share |
|---|---:|---:|---:|---:|
| **`68990cbe508aa`** | **61** | **24** | **24** | **100%** |
| `5d3efa06f1393` | 4 | 2 | 1 | 50% |
| `5f9802ef2d90f` | 103 | 1 | 0 | 0% |
| `9stspoxu6dy16` | 73 | 2 | 0 | 0% |
| `643cca5c87303` | 69 | 2 | 0 | 0% |
| every other ID | — | — | 0 | 0% |

`68990cbe508aa` placed 61 tracked links across 24 domains, and **all 24 are
the spun-content vendor blog network** — `bloggazza.com`,
`activosblog.com`, `tkzblog.com`, `mpeblog.com`, `diowebhost.com` and the
rest, on throwaway auto-generated accounts running spun fish-oil articles.

No other affiliate has a meaningfully spammy footprint.

## 3. The disavow verdicts stand

Affiliate tracking does **not** make these links legitimate. The brief
anticipates exactly this case: retain affiliate gateways, but flag
"a spam network masquerading as an affiliate". That is what this is —
someone monetising a PBN through the affiliate programme.

So the 24 domains stay `DISAVOW`, and this becomes an **affiliate-programme
compliance issue as well as an SEO one**: the placements are earning
commission on links that damage the domain they point at.

`securelinksdirectory.com` is the same pattern under a different ID
(`5d3efa06f1393`, which also placed a clean link on `fortune.com`).

## 4. Recommended action

1. **Audit affiliate `68990cbe508aa`** in Post Affiliate Pro. Terminate or
   require removal — 61 links across a PBN is not a marginal violation.
2. **Keep all 24 domains in the disavow file.** Commission paid does not
   make a spun-content network safe to keep.
3. **Protect the other 41 affiliate domains** already at `KEEP`.
4. **Re-check the 4 affiliate domains sitting in `REVIEW`** — their
   affiliate status is now evidence, not inference:

   | Domain | Tracked links | Current risk factor |
   |---|---:|---|
   | `ebylife.com` | 13 | Elevated Exact-Match Anchor Ratio |
   | `orlandomagazine.com` | 6 | Elevated Exact-Match Anchor Ratio |
   | `eastbayexpress.com` | 5 | Exact-Match Anchor Abuse (Syndicated) |
   | `geriatricacademy.com` | 2 | Unclassified |

   **`eastbayexpress.com` matters most.** It is the largest single equity
   exposure after the held three, and 5 of its links carry `a_aid` — so it
   is at least partly an affiliate placement rather than organic editorial.
   The other 662 point at the bare product URL with an exact-match anchor,
   which is why it is not a clean retain either. This needs the commercial
   answer: was the placement bought?

## 5. Correction

An earlier reading of this data appeared to show `hexcolor.co` carrying the
same `86a…` tracking namespace as `fitliving.org` and `eastbayexpress.com`.
It does not. Those were hex colour codes — `hexcolor.co/hex/86ac0c`,
`/hex/e86a35` — matching a regex by coincidence on a site that publishes a
page per colour value.

**All 45,412 `hexcolor.co` targets are bare URLs with zero query
parameters.** No affiliate attribution is present. The only tracking-layer
evidence for `hexcolor.co` remains the `drect.net/performancelab` redirect
hop, which is still unidentified.
