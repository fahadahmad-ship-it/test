# Controlled Comfort — Tab 08 assessment (56 referring domains)

Client: Controlled Comfort (controlledcomfort.com), HVAC, Omaha NE
Source: Semrush estimate, pulled 16 Sep 2026. Assessed 22 Oct 2026.
Format: Harbinger backlink-audit format (`AUDIT_FORMAT.md`) + playbook (`BACKLINK_AUDIT_PLAYBOOK.md`).
"Supplier" in this brief = the "partner" role the sheet always names (tied together per the format's per-client rule).

---

## Headline: none of these 56 can go in the disavow file yet

**Every one of the 56 domains resolves to `Held (Pending Partner)`, not `Spam (Disavow)`.**
So the disavow file produced now is **empty of active lines** — it is a skeleton that lists
all 56 as commented, pending the supplier's answer. This is not a hedge; it is what the
format and the three principles require:

- **Playbook principle 3:** "When in doubt, hold, do not disavow. Exact-match commercial
  anchors and links to deep money pages may be commissioned placements. Disavowing a link
  the client paid for hurts them."
- **Verdict order, rule 4:** "Exact-match anchor, **or** any link pointing at a deep
  product/capability/industry page → **Held (Pending Partner)**." First match wins, so this
  fires *before* the spam-host rules (rule 9) that these directory names would otherwise trip.
- **Format, Statuses + Rules:** "Held domains never reach disavow.txt. The partner decides first."

The brief's own instruction already says so — "confirm with the previous supplier which
placements were commissioned **before** the file is submitted." Producing a populated
disavow.txt that lists these 56 now would contradict that and risk disavowing links the
client (via the previous supplier) paid for. **The supplier conversation is the gate, and it
has to happen before, not after, any line becomes active.**

## Why all 56 are Held (the evidence, read critically)

Every row carries the two signals the playbook treats as "looks commissioned":

1. **Exact-match commercial anchor with the client's geography** — "Furnace Heating Repair
   Omaha NE", "Air Conditioner Repair Omaha NE", "HVAC Repair Omaha NE", etc. This is
   Controlled Comfort's own service + geo vocabulary, not off-topic (no casino/pharma) and
   not PBN sales copy ("buy backlinks", "DA50 PA40"). So rules 7–8 (off-topic / PBN spam)
   do **not** fire.
2. **Anchor-to-target mapping is deliberate**, which is the tell of a managed campaign, not
   a random blast:
   - Furnace/heating anchors → `/services/heating` (29 domains)
   - AC anchors → `/services/air-conditioning` (17 domains)
   - Broad "HVAC Repair/Replacement" anchors → home page `/` (10 domains)
   The deep-page links (46 of 56) hit money pages, which is itself a Held trigger under rule 4.

**The directory names look like a spam listing network, and that tension is the whole point.**
`topbizdir.com`, `getdirectory.org`, `directoryninja.org`, `listingcenter.org` and the rest
read like a link-listing network. If you went on the host names alone (rule 9) you'd disavow
them. But rule 4 outranks rule 9, and the exact-match + deep-page pattern is exactly what a
**commissioned directory-listing package** looks like. The safe, correct, playbook-mandated
move is to hold the whole set and ask the supplier, not to auto-disavow.

## Signals worth putting in front of the supplier

- **Single coordinated run.** First-seen dates cluster in a tight 17-day window
  (25 Aug – 10 Sep 2026). 56 directory listings, matched anchors, two deep pages + home,
  appearing together, is one placement batch from one vendor — consistent with a single
  commissioned directory package. This is the "one vendor network" key-finding pattern.
- **Templated/spun anchors.** Three domains carry "Furnace Re pairs Omaha NE" (note the
  broken word "Re pairs"): directoryology.com, 5starlocalcenter.com, businessinfoseek.com.
  That spacing artifact is a sign of automated anchor generation. It does **not** change the
  verdict (still exact-match commercial → Held), but it is a quality red flag to raise: a
  commissioned package producing garbled anchors is low quality whoever paid for it.

## Live-data enrichment (Semrush, pulled 2026-10-22) — see `enrichment_findings.md`

The brief table has been checked against the live Semrush profile. The verdict is unchanged
(all 56 Held), but three things now matter:

- **The links are dofollow.** Sampled links to both deep pages are `nofollow=false`, live
  (HTTP 200), on listing pages with authority score 0. So they **pass equity** — any of the 56
  the supplier did *not* commission is a genuine `Spam (Disavow)`, not a nofollow "no action".
- **The 56 badly under-count the problem.** The live profile is **2,440 referring domains**
  (not 56), AS 21, and it is growing at **~70+ new referring domains per day** right now
  (the 1,000 newest RDs span just 13.7 days). The same directory/bookmark/article template
  points at the money pages from **May 2025 to today** — an ~18-month sustained campaign, with
  many brief domains showing *two* placements (a ~Jan 2026 listing and the Aug/Sep 2026 one).
  The eventual disavow (post-supplier) should cover the **whole footprint**, not just these 56;
  a full-profile audit is the right next job.
- **Two discrepancies:** brief "First seen" dates run ~2–4 weeks off Semrush's (estimate — don't
  quote them as exact), and the brief's 17 AC domains didn't surface in the live
  `/services/air-conditioning` pull (likely a trailing-slash target variant — reconcile each of
  the 56 against the live index before finalising).

Still needed before any line goes live:
- **Per-domain Authority Score / traffic / keywords.** Not pulled for all 56 (profile velocity
  makes bulk sorted pulls very unit-expensive, and **Ahrefs API units are exhausted**). Nothing
  sampled looks like a genuine AS≥20 `Keep` site, but confirm from the client's **Ahrefs CSV**
  or a scoped per-domain Semrush pull.
- **Whether a disavow file already exists** on the controlledcomfort.com Search Console property
  (replace vs add), and **which properties the client can upload to.** Ask the client.

I have **not** fabricated any metric. The full live findings and the exact numbers are in
`enrichment_findings.md`.

## Two things only a human can do (I will not)

- **Contact the previous supplier.** I have no channel to them. Draft query is in
  `supplier_confirmation_request.md` — send it, and record the answer against each domain.
- **Upload to Google Search Console.** Per playbook §11, I do not submit anything to GSC.

---

## Decision table (Tab 05 / Tab 06 content) — one row per domain

Status for all = **Held (Pending Partner)** (supplier in this brief) → **not** in disavow.txt.
Decision = **Hold — await supplier confirmation.** Example backlink = the referring domain's
listing page (needs the exact linking-page URL from the Semrush/Ahrefs export to be "checkable").

### Group A — point at `/services/heating` (29) — furnace / heating anchors
| # | Referring domain | Anchor text | First seen |
|---|---|---|---|
| 1 | listique.org | Furnace Heating Repair Omaha NE | 2026-09-10 |
| 2 | topbizdir.com | Hvac Furnace Service Omaha NE | 2026-09-08 |
| 3 | zynatee.com | Furnace Replacement Omaha NE | 2026-09-07 |
| 4 | theinfosynth.com | Hvac Furnace Service Omaha NE | 2026-09-07 |
| 5 | onepluslisting.com | Hvac Furnace Repair Omaha NE | 2026-09-07 |
| 6 | true-listings.com | Furnace Repair Service Omaha NE | 2026-09-06 |
| 7 | lookuplists.com | Furnace Heating Repair Omaha NE | 2026-09-06 |
| 8 | getdirectory.org | Furnace Heating Repair Omaha NE | 2026-09-06 |
| 9 | localstudio.info | Furnace Replacement Omaha NE | 2026-09-05 |
| 10 | honestdir.com | Furnace Repair And Replacement Omaha NE | 2026-09-05 |
| 11 | localbusinessfinder.co | Furnace Repair Omaha NE | 2026-09-05 |
| 12 | listingcenter.org | Furnace Repair Service Omaha NE | 2026-09-05 |
| 13 | thelistingmatrix.com | Furnace Heating Repair Omaha NE | 2026-09-05 |
| 14 | directoryology.com | Furnace Re pairs Omaha NE *(spun anchor)* | 2026-09-04 |
| 15 | myreallistings.com | Furnace Heating Repair Omaha NE | 2026-09-04 |
| 16 | selectbusinesszone.com | Furnace Repairs Omaha NE | 2026-09-04 |
| 17 | thedirectopia.com | Emergency Furnace Repair Omaha NE | 2026-09-03 |
| 18 | ackoona.org | Furnace Heating Repair Omaha NE | 2026-09-02 |
| 19 | listingsspot.com | Emergency Furnace Repair Omaha NE | 2026-09-01 |
| 20 | businesslistingforall.com | Furnace Heating Repair Omaha NE | 2026-09-01 |
| 21 | 5starlocalcenter.com | Furnace Re pairs Omaha NE *(spun anchor)* | 2026-09-01 |
| 22 | bestlocalcenter.com | Furnace Repairs Omaha NE | 2026-09-01 |
| 23 | ideal-listings.com | Furnace Repair Omaha NE | 2026-08-31 |
| 24 | directoryninja.org | Furnace Replacement Omaha NE | 2026-08-30 |
| 25 | godigitalbusinesshub.com | Hvac Furnace Service Omaha NE | 2026-08-30 |
| 26 | findbusinesses.org | Furnace Heating Repair Omaha NE | 2026-08-30 |
| 27 | getzzby.com | Emergency Furnace Repair Omaha NE | 2026-08-29 |
| 28 | businessinfoseek.com | Furnace Re pairs Omaha NE *(spun anchor)* | 2026-08-29 |
| 29 | easybusinessdirect.com | Emergency Furnace Repair Omaha NE | 2026-08-28 |

### Group B — point at `/services/air-conditioning` (17) — AC anchors
| # | Referring domain | Anchor text | First seen |
|---|---|---|---|
| 30 | premiuminc.org | Air Conditioner Servicing Omaha NE | 2026-09-01 |
| 31 | ultimatesites.info | Air Conditioner Repair Omaha NE | 2026-08-31 |
| 32 | yourpremium.org | Ac Repair Omaha NE | 2026-08-30 |
| 33 | rozzbee.com | Air Conditioner Repair Omaha NE | 2026-08-29 |
| 34 | topincitylocal.com | Air Conditioner Servicing Omaha NE | 2026-08-29 |
| 35 | probusinessworld.com | Air Conditioner Repair Omaha NE | 2026-08-29 |
| 36 | woorivo.com | Ac Repair Omaha NE | 2026-08-28 |
| 37 | localbusinessesdir.com | Ac Repair Omaha NE | 2026-08-28 |
| 38 | showmelocalpro.com | Air Conditioner Servicing Omaha NE | 2026-08-28 |
| 39 | populardirectory.co | Air Conditioner Repair Omaha NE | 2026-08-27 |
| 40 | directorist.net | Air Conditioner Repair Omaha NE | 2026-08-27 |
| 41 | snapsearch.org | Air Conditioner Servicing Omaha NE | 2026-08-27 |
| 42 | seekbump.org | Air Conditioner Repair Omaha NE | 2026-08-26 |
| 43 | yellowmarketplaces.com | Air Conditioner Repair Omaha NE | 2026-08-26 |
| 44 | directoryview.com | Ac Repair Omaha NE | 2026-08-26 |
| 45 | localdirectory247.com | Air Conditioner Servicing Omaha NE | 2026-08-25 |
| 46 | getlistedahead.com | Air Conditioner Repair Omaha NE | 2026-08-25 |

### Group C — point at home page `/` (10) — broad HVAC anchors
| # | Referring domain | Anchor text | First seen |
|---|---|---|---|
| 47 | thelistingcloud.net | HVAC Repair Omaha NE | 2026-08-30 |
| 48 | weblistings.info | HVAC Repair Omaha NE | 2026-08-30 |
| 49 | directorycentered.com | Hvac Repair Service Omaha NE | 2026-08-30 |
| 50 | busineessupdir.com | Hvac Repair Service Omaha NE | 2026-08-29 |
| 51 | findlocalcenter.com | HVAC Repair Omaha NE | 2026-08-29 |
| 52 | a-zbusinesses.com | Hvac Repair Service Omaha NE | 2026-08-28 |
| 53 | localbusinessguide.org | Hvac Repair Service Omaha NE | 2026-08-28 |
| 54 | atozweb.org | Hvac Replacement Services Omaha NE | 2026-08-25 |
| 55 | localpagesdirectory.com | Hvac Replacement Omaha NE | 2026-08-25 |
| 56 | searchknock.com | Hvac Replacement Services Omaha NE | 2026-08-25 |

> Note on Group C: even the home-page links carry exact-match commercial geo anchors, so they
> are Held under rule 4 regardless of target. The home/deep-page split here is *not* the clean
> "two campaigns" separation the playbook describes (spam→home, commissioned→deep) — here the
> whole set shares the commissioned signature, which is another reason to treat it as one
> package and ask the supplier about all 56 together.

## After the supplier answers
- Domains the supplier **did not** commission → genuinely unsolicited; re-assess on their own
  evidence (anchor, title, host, dofollow). Those that are spam with ≥1 dofollow link become
  `Spam (Disavow)` and move into disavow.txt (as `domain:` lines, grouped by reason).
- Domains the supplier **did** commission → a strategy conversation (keep vs. clean up), not an
  audit auto-disavow. Record the confirmation against the row; do not disavow unilaterally.
- Then (and only then) finalise disavow.txt, re-run the verification both-directions sweep, and
  confirm no Held/Keep/Own Site domain leaked into the file.
