"""Per-domain recommendation for every row in the review queue.

The review queue is what the rules deliberately refuse to decide. Each entry
below is a hand recommendation with the evidence that produced it, read off
the actual placements rather than the domain metrics. Nothing here changes a
verdict on its own -- it populates the sheet's Review Queue tab so the client
decides with the evidence in front of them.

Format: domain -> (recommendation, evidence)
"""

DISAVOW, KEEP, ASK = "DISAVOW", "KEEP", "ASK_CLIENT"

DECISIONS = {
    # -- injected / hacked placements ------------------------------------
    "955x.com": (DISAVOW, "Random directory injection: /islatulk883267/"
                 "3384solicitor-news/wiki/The-Director-Of-Fat-Loss. Nofollow, "
                 "so inert, but not an editorial placement."),
    "french-styles.com": (DISAVOW, "Random directory injection: /fduuc5/"
                          "does-magnesium-make-urine-yellow on a domain about "
                          "French style. Same shape as jeffjsnider.com and "
                          "walshskitchen.com -- one operator."),
    "jeffjsnider.com": (DISAVOW, "Random directory injection: /2p90a/"
                        "when-is-the-best-time-to-take-caltrate."),
    "walshskitchen.com": (DISAVOW, "Random directory injection: /wwx25fv/"
                          "index.php?topic6771=funeral-homes-rice-lake-wi, "
                          "anchor 'jvic'. Compromised host."),
    "whatisglutathione.net": (DISAVOW, "Keyword doorway: /whatisglutathione."
                              "php?Action=1&PageID=613044&k=best-glutathione-"
                              "supplement. The keyword is in the query string."),
    "alphapowershop.online": (DISAVOW, "Links from /blog-admin, a page that "
                              "should not be public, anchor '[17]'."),
    "hlhw.fun": (DISAVOW, "/index-191.html with anchor 'Click here...'. "
                 "Doorway page, no content."),
    "luftsi.info": (DISAVOW, "/index-110.html with anchor 'Click For Best "
                    "Price'. Same generator as hlhw.fun."),
    "fi38.com": (DISAVOW, "Links from /test-post-new/ with anchor 'BUY NOW'."),

    # -- vendor blog networks -------------------------------------------
    "kingranks.com": (DISAVOW, "2,448 outbound links per page on SEO/marketing "
                      "filler ('The Relationship Between SEO And Social "
                      "Networking'), bare-domain anchor. Sibling of "
                      "wayranks.com -- same template, same anchor style."),
    "wayranks.com": (DISAVOW, "2,592 outbound links per page, same filler "
                     "template and anchor style as kingranks.com."),
    "skylinkseo.site": (DISAVOW, "2,504 outbound links per page across "
                        "unrelated subjects -- budget travel, career guidance, "
                        "summer outfits -- all linking to supplement brands. "
                        "No publisher has that subject range."),
    "27.be": (DISAVOW, "Auto-generated domain-auction feed (/live-domain-"
              "auction-feed/nl?page=102), anchor '.com'. 19 follow links from "
              "listing rows, no editorial intent."),

    # -- scraped / spun content ----------------------------------------
    "producthubspot.com": (DISAVOW, "Serves /blog/the-9-best-multivitamins-for-"
                           "men-according-to-a-registered-dietitian-2023/ -- "
                           "byte-identical to top-dealshub.com. A scraped "
                           "publisher article on two domains at authority 2."),
    "top-dealshub.com": (DISAVOW, "Same scraped article path as "
                         "producthubspot.com. Nofollow, so inert."),
    "omegahealthsystems.com": (DISAVOW, "/the-14-finest-multivitamins-for-girls-"
                               "2024-information/ against worldworthliving.com's "
                               "/the-14-best-multivitamins-for-women-2024-guide/ "
                               "-- finest/best, girls/women, information/guide. "
                               "Spun from one source, anchors spun too."),
    "worldworthliving.com": (DISAVOW, "Spun pair with omegahealthsystems.com."),
    "ashthdhatu.com": (DISAVOW, "Slug ends '-bodynutrition': the article was "
                       "lifted from bodynutrition.org with the source's name "
                       "still in the URL."),
    "eastphoenixau.com": (DISAVOW, "/c-pages/cafeine-anhydrous.html -- scraped "
                          "caffeine articles on an unrelated domain. Nofollow."),
    "decoupage-paper.com": (DISAVOW, "Recipe scraper (/best-hash-brown-egg-bake-"
                            "recipes) with anchor 'Source'. Nofollow, inert."),
    "dapago.net": (DISAVOW, "Recipe scraper, same 'Source' anchor pattern as "
                   "decoupage-paper.com. Nofollow, inert."),
    "crazypeople.online": (DISAVOW, "old.crazypeople.online/post/416022 -- "
                           "scraped forum content."),
    "musicareview.com": (DISAVOW, "Album database (/album/1362930042/fitness-"
                         "single-lizzo) carrying 'Buy Now!' supplement links. "
                         "Nofollow, inert."),
    "revaliew.com": (DISAVOW, "/businesses/testolabpro.com -- auto-generated "
                     "site profile. Nofollow, so a disavow changes nothing; "
                     "filed for a clean profile only."),
    "rugbynewsbeast.com": (DISAVOW, "Anchors 'ar', 'kr', 'mnv', 'mq' on an "
                           "archive page averaging 1,501 outbound links. "
                           "Injected, not editorial."),
    "academicsongs.com": (DISAVOW, "A domain named for academic songs "
                          "publishing eye-vitamin and pre-workout reviews with "
                          "'Buy performance lab From Official Website' anchors. "
                          "Repurposed domain, exact-match commercial CTAs."),

    # -- retain: editorial, reference or affiliate -----------------------
    "duckduckgo.github.io": (KEEP, "DuckDuckGo's Tracker Radar Wiki, a privacy "
                             "research dataset. performancelab.com is listed "
                             "because the store embeds DoubleClick, Shopify, "
                             "Klaviyo and Typekit. A citation in open data."),
    "metabengsci.com": (KEEP, "Anchors '[74]' and '74. Best Energy Pills...' -- "
                        "numbered references in a technical article. Same as "
                        "the benchchem.com and smolecule.com bibliographies."),
    "cfshelp.info": (KEEP, "'Best Nootropics for Traumatic Brain Injury' citing "
                     "Omega-3s. On topic, editorial."),
    "geriatricacademy.com": (KEEP, "Authority 15, 15 follow links, anchors 'MCT "
                             "Energy Oil' and 'Men's Multivitamins and "
                             "Minerals' in drug-interaction articles. Health "
                             "publisher; the relevance lexicon missed it."),
    "narcolepsylifeacademy.com": (KEEP, "/lifestyle-essentials recommending "
                                  "'Mind Lab Pro. Designed to boost your...' "
                                  "and 'Performance Lab B-Complex'. Genuine "
                                  "niche recommendation page."),
    "armfighter.com": (KEEP, "Arm-wrestling publisher at authority 22 with a "
                       "supplements section ('CHECK OUT THE FULL LINE OF "
                       "SUPPLEMENTS'). Off-lexicon, not off-topic."),
    "hyroxy.com": (KEEP, "HYROX racing site, 'Pre Lab Pro is the best pre "
                   "workout supplement'. Fitness affiliate."),
    "caffeine-alternatives.com": (KEEP, "Anchors 'Performance Lab Caffeine 2' "
                                  "and 'Performance Lab® B-Complex'. On topic."),
    "knowyourbrain2.weebly.com": (KEEP, "Anchors 'Performance Lab® Mind', "
                                  "'Performance Lab® Omega-3', 'Performance "
                                  "Lab® Sleep'. Nofollow review site."),
    "scentses4d.wordpress.com": (KEEP, "/2020/10/27/vitamin-c/ citing a "
                                 "Performance Lab blog post by full URL."),
    "gutandbody.com": (KEEP, "'Check Price →' affiliate review site, on topic, "
                       "nofollow."),
    "fatburnerranked.com": (KEEP, "'See Performance Lab Pricing' -- affiliate "
                            "review, nofollow."),
    "reneebovet.co": (KEEP, "/product-affiliate-links/ with 'Brain Health "
                      "Support' and 'Immune Support'. An affiliate link page: "
                      "protected architecture."),
    "theaffiliateslist.com": (KEEP, "An affiliate-programme directory, "
                              "multilingual ('Laboratoire de performance', "
                              "'Laboratorio de rendimiento'). Nofollow."),
    "aferg.co": (KEEP, "/energy-yt and /multim-web -- a creator's link "
                 "shortener with per-channel campaign suffixes. Tracking "
                 "infrastructure, not a placement."),
    "kiladeals.com": (KEEP, "Coupon aggregator, on topic. Protected by brief."),
    "smatdeals.com": (KEEP, "/coupon/performance-lab-discount-code.html. "
                      "Coupon aggregator, protected by brief."),
    "losmejoressuplementos.es": (KEEP, "Spanish supplement reviews, 'Comprar "
                                 "ahora'. The relevance lexicon is English."),
    "drugs-forum.org": (KEEP, "Forum Q&A ('are tart cherry pills as effective "
                        "as the juice'), editorial anchors."),
    "muzcle.com": (KEEP, "/creatine-vs-bcaa/ with numbered citation '3'."),
    "lifttilyadie.com": (KEEP, "/how-much-creatine-per-day/, anchor 'caffeine'. "
                         "Editorial."),
    "myfastingbuddy.com": (KEEP, "Fasting article, anchor '50 calories'. "
                           "Editorial citation."),
    "pureminerals.uk": (KEEP, "/msm/ with 'joint health' and 'cartilage "
                        "health'. On topic."),
    "naturalhealthwriter.com": (KEEP, "A health copywriter's portfolio; the "
                                "'exact-match' anchors are her article titles."),
    "leebell.co.uk": (KEEP, "/published-articles/ listing 'The Dangers of "
                      "Overtraining', 'Velocity-Based Training'. A coach's "
                      "portfolio."),
    "meghanbell.com": (KEEP, "Personal blog; the 247-link average is tag and "
                       "author archives, and the anchor is editorial prose."),
    "hmscicomms.com": (KEEP, "Science-communications consultancy blog."),
    "jsrproductions.com": (KEEP, "Anchor '[Source]' -- a citation."),
    "manufacturerusa.com": (KEEP, "/california/Performance-Labs-Inc-l2666.html "
                            "-- a factual business-directory listing of the "
                            "company itself."),
    "onlyboosts.social": (KEEP, "Podcast episode linking the /breedlove partner "
                          "landing page. Same class as whatismoneypodcast.com."),
    "cro.media": (KEEP, "Shopify-store directory, 100% nofollow across 20 "
                  "links. No equity passes, so nothing to disavow."),
    "morerss.com": (KEEP, "RSS reader rendering a feed that cited the brand. "
                    "Incidental, not placed."),
    "altgng.com": (KEEP, "Link-aggregator post citing a Performance Lab blog "
                   "URL. Incidental."),
    "gaidot.net": (KEEP, "Hacker News mirror (hnpaper-labs.gaidot.net/u/...). "
                   "Renders whatever the feed carries."),
    "lunoo.com": (KEEP, "Affiliate-programme index (/tag/high-commission-"
                  "rates), anchor 'Visit'."),
    "ecortelyou.github.io": (KEEP, "Personal project blog citing a Performance "
                             "Lab article by URL."),
    "astro-solid-hn-edge.netlify.app": (KEEP, "Astro/Solid framework demo "
                                        "rendering the live Hacker News feed. "
                                        "Same as the other HN clone demos."),
    "fuelcell101.com": (KEEP, "Anchor 'Vitamin C and Omega-3 Together: "
                        "Benefits' -- an article citation."),
    "chin-thai-restaurant-brackenheim.de": (KEEP, "German nutrition article "
        "citing brain-energy research. One follow link, authority 9. Odd "
        "subject for a restaurant site and worth a look, but the placement "
        "itself reads editorial and there is no second signal."),
    "praxisdrmedpschierer-vilsbiburg.de": (KEEP, "German medical practice "
        "publishing a nutrition article on Montmorency cherries and melatonin. "
        "On topic for a practice; one follow link."),
    "rlrhmember.blogspot.com": (KEEP, "One backlink, authority 2, no link-level "
                                "data. Not enough to act on either way."),
    "natuhealthblog.blogspot.com": (KEEP, "Three backlinks, authority 0, no "
                                    "link-level data."),
    "web-tau-bice-50.vercel.app": (KEEP, "One backlink, authority 2, no "
                                   "link-level data."),

    # -- needs the client ------------------------------------------------
    "dtcx.com": (ASK, "Links to the brand with image anchors 'Performance Lab "
                 "Logo' and 'Nutropic Logo' -- which reads like an owned or "
                 "partner property. But dtcx.com is also promoted BY several "
                 "of the spam networks in this audit: 'visit dtcx.com for "
                 "latest info' on businessvocal.com and thecloudherald.com, "
                 "and 'Premium PBN Network Service dtcx.com Rank First' on a "
                 "link-vendor page. Either it is yours, or a link seller is "
                 "riding the brand. Please confirm before any action."),
}
