# Section 4 verification + false-negative hunt — ngwindows.com disavow v2

Scope: verify Section 4 of `disavow-v2-ahrefs.txt` (26 domains / 53 dofollow links), resolve the
benign-vs-toxic contradiction against the earlier pass, and hunt false negatives across both datasets.

Evidence: `data/ahrefs/ahrefs-backlinks.tsv` (2,665 rows), `data/ahrefs/ahrefs-refdomains.tsv`,
Semrush `links_raw.tsv` @ `6f5f407` (3,499 rows), `data/refdomains.csv`. No live refetch (Semrush
ERROR 132; Ahrefs Site Explorer locked). Scripts: `scripts/s4_verify.py`, `s4_agg.py`, `fn_hunt*.py`,
`sem_hunt*.py`, `final.py`. All matching uses `(?<![a-z0-9.-])ngwindows\.com`.

**No recommendation anywhere below rests on DR, Authority Score, traffic, thin content, TLD, country
or hosting.** Grounds cited are the file's own (a)–(e), behavioural only.

---

## 1. JOB 1 — Section 4 per-entry verdict

### 1.1 The claimed facts all hold, exactly

| Claim in the file | Verified |
|---|---|
| 26 domains | 26 — every one present in the Ahrefs export |
| 53 dofollow links | 53 links total, **53/53 `Nofollow=false`**. No nofollow padding. |
| Ahrefs flagged only 9 of 26 | 9 exactly: `domain.com.lc`, `domainanalysis.org`, `domains.com.bz`, `domainsc.com`, `indexaward.com`, `itsyourgold.com`, `prashikshan.in`, `wonvision.com`, `youtoo.in` |
| `/page-34962c4ce6e04e66bc6683ce26dd6c07.html` on 16 hosts | 16 exactly, and **all 16 are in the section** |
| `/61a37460a2eed245244c9bc59896bc7b-l/` on 8 hosts | 8 exactly, **all 8 in the section** |
| `/page/168196/` (the 2 remaining) | 2 exactly: `domains.com.bz`, `itsyourgold.com` |
| Titles "Where to buy aged domains and backlinks" / "Top Domains – Page 168196" | Every one of the 26 carries one of the two. No host carrying either title is missing from the section. |
| Alphabetical-inventory context | Identical on all 24 page-ID hosts: left `ngwind.com ngwindow.com`, right `ngwindsong.com ngwindsongk.com` |

**Per-entry verdict: all 26 SUSTAINED on the stated grounds (b)+(c)+(d).** There is no arithmetic
error, no padding, no entry that fails its own cited evidence. Two refinements worth recording:

- The title is **host-personalised** — `"...aged domains and backlinks 🔥 from www.backlinksbank.com | 3496-2460"`,
  `"...from domainsc.com | 3496-2460"`, `"...from all-aged-domains.com | 3496-2460"` (on `way2check.cv`).
  One template, variable substituted per host, same page-ID suffix. That is a stronger (c) than the
  file claims: it is not merely a copied path, it is one CMS serving 16 skinned mirrors. Note also
  that `way2check.cv` renders *another* operator domain's name (`all-aged-domains.com`) in its own
  title — a slip that ties the hosts to a single operator.
- `itsyourgold.com`'s title is `"Top Domains – Page 168196 – newwebsiteslist.com"`. `itsyourgold.com`
  is serving **`newwebsiteslist.com`'s** branding. Same slip, same conclusion. (See §3.1 — this leads
  directly to a missing host.)

Page type on all 26 is `Listing > Business` / `Listing > Product` / `Listing collection > Business`,
and page category on all 26 contains `Internet > Web services > SEO and marketing`. Ahrefs'
*classifier* missed 17 of them, but Ahrefs' *page categoriser* put 26 of 26 in the SEO-marketing
category. That is independent corroboration of (d) that the file did not claim.

### 1.2 The key question: is appearance in a scraped alphabetical inventory grounds for disavowal?

**The case for DROP (the honest version).**
Google's disavow guidance targets *links intended to manipulate your rankings*. Here the intent
plainly runs elsewhere. The operator is monetising an inventory of expired/aged domains; the list is
alphabetical and exhaustive, ngwindows.com sits between `ngwindow.com` and `ngwindsong.com` purely
because of its spelling. There is no evidence of a transaction, no evidence the client or an agency
on their behalf ever bought anything, and the anchor is the bare domain name — the most neutral
anchor that exists. If Google ever audits this file, a reviewer who pulls one of these pages sees a
directory of thousands of domains, not a paid placement for a window installer. Disavowing it
protects nothing, because a link nobody built for you cannot be an unnatural link *of yours*. The
file's own stated discipline — "default to exclusion", "a domain qualifies only on cited anchor text
+ dofollow" — cuts against inclusion: the anchor here carries no manipulative text at all. And 26
entries is 5.7% of the file bought at the cost of its cleanest line of argument.

**The case for KEEP (which I find stronger).**
1. **A disavow file is not a finding of the linker's intent; it is a statement about PageRank you
   decline to receive.** The operative question is not "did this operator mean to boost ngwindows.com"
   but "is this a dofollow link from a page whose own purpose is the sale of links, which Google
   would count toward ngwindows.com's profile". Both halves are affirmatively true: 53/53 dofollow,
   and the page's own `<title>` says it sells backlinks. Motive is the operator's; exposure is the
   client's.
2. **(d) is a self-evidencing ground that does not depend on motive.** The page title is
   `"Where to buy 🚀 aged domains and backlinks 🔥"`. This is a link-marketplace page under Google's
   own link-spam policy regardless of who is listed on it. Inbound dofollow from a page advertising
   link sales is precisely the pattern the policy describes.
3. **The "it's just a scraper" reading is now refuted by the data.** See §3.1: the same page-ID
   appears on **35 hosts** across both tools, including sister pairs registered by one operator
   (`tyre.pro` / `tyres.pro`, `way2check.cv` / `way2check.art`,
   `topleveldomains.space` / `alltopleveldomains.space`,
   `backlinkhouse.com` / `backlinkshouse.com`). A genuine "website worth" utility has one domain. 35
   skinned mirrors of one page-ID on near-duplicate registrations is a link network wearing a
   scraper's clothes. Its inventory listing is the *delivery vehicle* for dofollow PageRank; the
   alphabetical dressing is what makes it look innocent.
4. **Asymmetry of error.** The cost of disavowing a genuinely inert marketplace link is zero —
   these pages drive no traffic and confer no editorial value anyone would miss. The cost of leaving
   53 dofollow links from self-declared link vendors in the profile, in a file submitted precisely
   because the profile is under manual-action suspicion, is not zero.

**Recommendation: KEEP Section 4** — but rewrite its header to lead with (d) (the page's own
self-declaration of link selling) and demote the alphabetical-inventory context from a ground to a
*caveat*, stated openly. The current header's "weaker-MOTIVE tier" framing invites the reviewer to
discount the whole section; the motive is irrelevant to the decision and the header should say so.
Suggested replacement for the NOTE line:

> NOTE: ngwindows.com appears here inside a scraped alphabetical inventory, so no manipulative
> intent toward this client is alleged or needed. The ground is that these are dofollow links from
> pages whose own titles advertise the sale of links and aged domains, served from one templated CMS
> across 35 mirrored hosts. Intent is the operator's; the PageRank is the client's to decline.

If the reviewer overrules this and drops Section 4, drop it **together with** the 23 conditional
additions in §3.1/§3.2 — they stand or fall on the identical reasoning, and keeping one without the
other reintroduces exactly the inconsistency §2 describes.

### 1.3 False-positive check within Section 4

None found. All 26 are machine-generated marketplace/stats registrations; there is no real business,
no correct-geography local listing, no editorial page among them. Checked specifically for the
failure mode that matters (a genuine site swept up): zero.

---

## 2. The benign-vs-toxic contradiction, resolved

Six Section 4 entries — `alljobs.info`, `allwebsitesdirectory.com`, `domainsc.com`, `bestwebstats.com`,
`domain.com.lc`, `homefinance.co.in` — were classified **benign** by the earlier pass. Three documents
are involved and they do not actually conflict; they were decided on different evidence.

**What the earlier pass could see.** `as0-5-anchor-evidence.md` §Conclusions 1 and 3 and
`SUPERSEDED-ngwindows-backlink-audit.md` §7 "Network C" were built on the **Semrush** export, whose
only link-level fields are `source_url, anchor, nofollow, page_ascore`. **There is no page-title
column and no target-URL column.** The classification rule actually applied was *"worst anchor
observed"* — and the anchor on every one of these rows is the bare string `ngwindows.com`. Under a
rule that reads anchors only, a bare domain anchor is indistinguishable from a benign citation, so
these landed in "Bare sister-domain name only — no manipulative anchor — must be excluded".

**What the Ahrefs export added.** Two fields the earlier pass never had:
`Referring page title` (`"Where to buy 🚀 aged domains and backlinks 🔥"`) and the full
`Referring page URL` path (the shared page-ID). Ground (d) and ground (c) were literally
unobservable in the Semrush data. They are not a reinterpretation of the old evidence; they are new
evidence.

**So the contradiction is a coverage artefact, not a disagreement.** Both passes are correct on
their own evidence. The resolution is:

- The earlier "benign" verdict was **correct as to ground (a)** — the anchor is not manipulative,
  and it still is not. Nothing in Section 4 rests on (a), and nothing should.
- The earlier verdict was **silent, not exculpatory, as to (c) and (d)** — it had no data on either.
- `SUPERSEDED-ngwindows-backlink-audit.md` is in any case explicitly superseded, and its Network C
  rationale is partly inadmissible under the standing constraint anyway: it argued from Singapore
  hosting, AS 2–4 and `.sbs`/`.monster`/`.cv` TLDs. Those grounds must not be revived in either
  direction — they can neither condemn nor acquit.
- One live inconsistency does need fixing. `recheck-disavow.md` §2.2 removed `best-seo-domains.com`
  partly on the reasoning that it "does not carry the shared-slug fingerprint" and that bare-domain
  anchors on `/<8-char>-list/` paths are the same benign category as `domainsc.com` and `theface.in`.
  That reasoning is now obsolete twice over: `domainsc.com` and `theface.in` have been promoted on
  (c)+(d), and `/<token>-list/` **is** the fingerprint family (see §3.2). `best-seo-domains.com`
  should come back if Section 4 is kept.

**Action:** add a one-line reconciliation note to the Section 4 header so a reviewer who finds the
old "benign" verdict is not ambushed — e.g. *"17 of these were classified benign by the Semrush-only
pass (as0-5-anchor-evidence.md §1). That pass had no page-title or path column; grounds (c) and (d)
were unobservable to it. Its anchor-level finding is unchanged and no entry here relies on (a)."*

---

## 3. JOB 2 — FALSE NEGATIVES to ADD

Method: (i) cluster every dofollow link from an unlisted host by exact URL path; (ii) regex both
datasets for vendor vocabulary in titles/anchors and for `Page category = SEO and marketing` among
unflagged hosts; (iii) scan all 699 Semrush-only hosts for a word-boundary dofollow `ngwindows.com`
anchor. The 460-entry file covers 460 unique domains; 138 Ahrefs hosts have dofollow links and are
not in it.

**First, the good news — the exclusions verify.** Every large excluded block is genuinely 100%
nofollow and therefore correctly excluded: SEOExpress 577 hosts / 577 rows / **0 dofollow**;
`ysh5qk2` 65 hosts / 130 rows / **0 dofollow**; `/bibiacseo/` 19, `/buytfnseo/` 15, `/ashgeoseo/` 15,
"Directory Pages Index" 24 hosts, "Domain Report" 5, "Website Stats" 6, "Dark Side Links" 8 — all
**0 dofollow**. The five topically-impossible injections (`intermeritocracy.com`,
`monetaryhistoryofworld.com`, `worldbusinesspromote.com`, `marketingexperts.click`,
`dreamscometroup.com`) are **0 dofollow**. Section 1 is complete at 258 hosts / 516 dofollow rows,
all on one path, none missing. **The 10.6% classifier under-fire did not leave a dofollow hole on the
Ahrefs side** — of 138 unlisted dofollow hosts, exactly **zero** carry vendor vocabulary in title or
anchor, and the only 10 Ahrefs-flagged ones are precisely the 10 already documented as false
positives under NOT-DISAVOWED [2]. The real hole is in the **Semrush-only** half, which the file
only mined for ground (a).

### 3.1 — Marketplace network: 20 missing hosts on the file's own fingerprints (CONDITIONAL on keeping Section 4)

Grounds (b)+(c)+(d), identical to Section 4. Union of both tools on the two page-IDs is **35 hosts**
and **9 hosts**, not 16 and 8 — Ahrefs crawled 16 of 35. All rows below are `nofollow=false` with
anchor `ngwindows.com`.

`/page-34962c4ce6e04e66bc6683ce26dd6c07.html` — 19 uncovered hosts (Semrush `links_raw.tsv`):

```
http://www.1000.co.in/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://2x9.co/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://all-aged-domains.com/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://alltopleveldomains.space/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.backlinkhouse.com/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.backlinkshouse.com/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://booksreadr.org/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://carplz.com/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://globalecommerce.org/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
https://mail.allwebsitesdirectory.com/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.procycling.org/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.themumbai.in/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.thirty.co.in/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://topleveldomains.space/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.tyres.pro/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://uaewebdirectory.info/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.way2check.art/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.websitescrawl.art/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
http://www.webworthchecker.cv/page-34962c4ce6e04e66bc6683ce26dd6c07.html	ngwindows.com	false	0
```

`mail.allwebsitesdirectory.com` is **already covered** by `domain:allwebsitesdirectory.com` (the
`domain:` directive covers subdomains) — do not add a separate line. Net **18 new entries** here.

`/61a37460a2eed245244c9bc59896bc7b-l/` — 1 uncovered host:

```
https://www.getwebsiteworth.com/61a37460a2eed245244c9bc59896bc7b-l/	ngwindows.com	false	0
https://getwebsiteworth.com/61a37460a2eed245244c9bc59896bc7b-l/	ngwindows.com	false	0
```

`/page/168196/` — 1 uncovered host, and it is the **origin** of the cluster:

```
https://www.newwebsiteslist.com/page/168196/	ngwindows.com	false	0
```

This is the host whose brand `itsyourgold.com` renders in its own `<title>`
(`"Top Domains – Page 168196 – newwebsiteslist.com"`). Listing the two mirrors while omitting the
original is indefensible.

**Total §3.1: 20 new entries** (18 + 1 + 1).

Why this is not an authority argument: the operator identity is established by *behaviour* —
one page-ID served from 35 hosts, host-substituted titles, and four sister-domain pairs
(`tyre.pro`/`tyres.pro`, `way2check.cv`/`way2check.art`,
`topleveldomains.space`/`alltopleveldomains.space`, `backlinkhouse.com`/`backlinkshouse.com`) where
one of each pair is already in the file and the other is not. No DR, hosting or TLD is invoked.

### 3.2 — The listing-path kit: 3 hosts (CONDITIONAL on keeping Section 4)

The `-l/` in `/61a37460a2eed245244c9bc59896bc7b-l/` is not decorative — it is one member of a
`<random-token>-{l|li|list|listing}/` path family. Three more hosts use it, all dofollow, all with a
bare `ngwindows.com` anchor:

```
https://best-seo-domains.com/x3pal60g-list/	ngwindows.com	false	0
https://best-seo-domains.com/d315qjt8-list/	ngwindows.com	false	0
https://domraider.de.com/q3v7311v-listing/	ngwindows.com	false	0
https://domraider.gb.net/r1rl868e-li/	ngwindows.com	false	0
```

Grounds (b)+(c). `best-seo-domains.com` has 12/12 dofollow rows. `domraider.de.com` /
`domraider.gb.net` are a sister pair on the same brand across two registry suffixes, using two
different suffix variants of the same path kit — that variation across hosts is itself the
fingerprint. This **reverses** `recheck-disavow.md` §2.2's removal of `best-seo-domains.com`, on the
explicit basis it flagged ("the single entry that could legitimately come back"): its path *does*
carry the shared fingerprint, once the family is recognised.

**Total §3.2: 3 new entries.**

### 3.3 — `newsblogsports.site`: the file's single clearest miss (UNCONDITIONAL)

The Section 2 PBN uses paths of the form `/all/<n>/<n>`. That path family has **23 hosts** in the
Ahrefs export. **22 are in the file. One is not.**

```
https://newsblogsports.site/all/358/10
title : Best Tool for Pinterest SiteToSocial Fully Automated AI Generated Pins Grow Your Website Traffic
anchor: Best Pinterest Tool SiteToSocial.com to Grow Your Website Traffic Fully Automated
target: https://ngwindows.com/     Nofollow: false     Is spam: FALSE
Page type: Site page > Services   Page category: Internet > Web services > SEO and marketing
```

Grounds (b) dofollow; (c) `/all/<n>/<n>` path shared with 22 already-listed PBN hosts; (d) the page
title and the anchor are both verbatim traffic/link-vendor sales copy, and Ahrefs' own categoriser
files it under `Internet > Web services > SEO and marketing`. Ahrefs' classifier scored it
`Is spam=false` — **this is the 10.6% under-fire, caught**. It is also the only dofollow row in the
entire export that is unlisted and sits in the SEO-marketing page category. 2 dofollow links.

### 3.4 — NEW CLUSTER "Network D": compromised-host link injection, 3 hosts (UNCONDITIONAL)

Not previously identified in any document in this repository. Three mutually unrelated hosts — a
Chinese trading company, a US non-destructive-testing firm and a Hungarian site — each serve a page
at a **random 5–7 character directory** with a **scraped nonsense title** and an injected dofollow
link to ngwindows.com using a keyword-rich anchor lifted from ngwindows.com's own SERP title.

```
https://www.beihaishitrade.com/wp-content/uploads/2023/5p6kj/article.php?tag=rebecca-fitoussi-caps
title : rebecca fitoussi caps
anchor: Our Family | North Georgia Replacement Windows   ->  https://www.ngwindows.com/our-story
Nofollow: false   Is spam: FALSE   lang: en,fr

https://nextndt.com/puk5eu9/article.php?id=rebecca-fitoussi-caps
title : rebecca fitoussi caps
anchor: Our Family | North Georgia Replacement Windows   ->  https://www.ngwindows.com/our-story
Nofollow: false   Is spam: FALSE   lang: en,fr

https://matyesz.hu/p14abe/receiving-touchdown-leaders-2021
https://matyesz.hu/p14abe/ptcas-application-2021-2022
title : receiving touchdown leaders 2021   (identical title on both URLs)
anchor: Windows & Doors Roswell GA | North GA Replacement Windows ...  ->  https://www.ngwindows.com/
Nofollow: false   Is spam: FALSE
```

Grounds:
- **(c) structural fingerprint across unrelated hosts.** `beihaishitrade.com` and `nextndt.com` serve
  the **same `article.php` script**, the **same nonsense title** (`rebecca fitoussi caps`), the
  **same anchor**, to the **same target URL**. These two hosts have nothing to do with each other or
  with windows. `article.php` is the only occurrence of that filename in the whole export, and it is
  on both. `beihaishitrade.com`'s copy is dropped inside `/wp-content/uploads/2023/` — a WordPress
  media directory, which does not host PHP in a healthy install. That is a site compromise, not a
  publisher.
- **(c) extended to `matyesz.hu`** on the same kit: random short directory (`/p14abe/`, cf. `/puk5eu9/`,
  `/5p6kj/`), scraped junk titles (US college-football stats, a physical-therapy application form) on
  a Hungarian host, two distinct URLs serving one identical title, one identical anchor.
- **(b)** all 6 links dofollow.
- Topical impossibility: the file already treats topically-impossible injection as behaviourally the
  strongest evidence in the dataset (NOT-DISAVOWED [1]) — and excluded those five **only because
  they were nofollow**. These three are the same behaviour, **dofollow**. By the file's own stated
  logic they are mandatory additions.
- Ahrefs flagged none of the three. Classifier under-fire again.

**Total §3.4: 3 new entries** (6 dofollow links).

### 3.5 — `backlinksolutions.info` (UNCONDITIONAL)

```
https://backlinksolutions.info/seo-link-building-packages-259/	ngwindows.com	false	0
```

Grounds (b) dofollow; (d) the URL path is the vendor's own product page —
`/seo-link-building-packages-259/` — i.e. a link-selling page naming ngwindows.com. Semrush-only;
Ahrefs has never crawled the host, so absence of an Ahrefs flag is absence of coverage. This belongs
in **Section 6**, which already admits exactly this evidence shape (dofollow + word-boundary anchor
naming ngwindows.com on a link-vendor page); it was missed because Section 6 appears to have been
built by matching vendor sales-copy *anchors*, and this row's anchor is the bare domain while the
vendor character sits in the path.

### 3.6 — Examined and REJECTED (recorded so they are not re-raised)

| Domain | Why not |
|---|---|
| `ihiwg.org` (2 df) | Serves a byte-copy of `barbend.com`'s real article incl. its title. A content scraper that inherited a legitimate publisher's link. No targeting of ngwindows.com. Weak motive *and* weak behaviour. |
| `maverickmansions.com` (4 df) | AI-generated article in 4 language permutations (`/`, `/ca/`, `/zh-TW/`, `/zh-CN/`) citing an ngwindows.com blog post as a footnote source. Permutation fingerprint exists but the link is a citation with a bare-URL anchor. Borderline; recommend leave. |
| `octanecdn.com` (2 df, DR 63) | `octanecdn.com/ngwindowsnew/*.pdf` — **the client's own marketing PDFs on their own CDN.** Never disavow. |
| `dynamix.site` (2 df, DR 72) | The client's web-design agency portfolio page. Legitimate. |
| `windowdoor-test.com` (12 df) | Staging mirror of `windowanddoor.com`, a real trade publication, same article paths. Editorial. |
| `processregister.com`, `find-us-here.com` | Carry `ngwindows.com` against a UK firm ("Cybi Plastics", phone +44-1248-422012). A directory **data error**, not link building. |
| `p.eurekster.com`, `robuta.com`, `smb.co`, `pinqube.com`, `windowssearch-exp.com`, `gsitestatus.com` | Search/SERP mirrors and stats lookups that index every domain. Editorially neutral. |
| `foaminsulationtips.com` (4 df) | Hot-linked image from ngwindows.com's own `phpThumb` endpoint. The client is the source. |
| 2012 blogspot rows (`tobye-wetware`, `chlamydia-genome`) | 2012-dated, predate every campaign in this profile by 13 years. |
| The 10 under NOT-DISAVOWED [2] | Independently re-checked; all 10 remain correct false-positive calls. |

---

## 4. Newly-discovered clusters, summarised

1. **Marketplace network is 2.2× larger than documented.** Page-ID `3496-2460` runs on **35 hosts**
   (16 in Ahrefs, 31 in Semrush, union 35), `6137-4602` on **9**, `/page/168196/` on **3**. The file
   captured only the Ahrefs-visible slice. Four sister-domain pairs confirm single-operator control.
   The true shape is one templated CMS with host-substituted titles, not 26 independent scrapers.
2. **Network D — compromised-host injection** (§3.4). Previously unidentified. `article.php` dropped
   into random short directories on three unrelated legitimate hosts, dofollow, keyword-rich anchors
   harvested from ngwindows.com's own page titles. Behaviourally the strongest *dofollow* evidence in
   the dataset, and Ahrefs flagged none of it.
3. **The `<token>-{l|li|list|listing}/` path kit** (§3.2) links the Section 4 `-l/` page-ID to
   `best-seo-domains.com` and the `domraider.*` pair, and overturns one prior removal decision.
4. **Where the under-fire actually bites.** The Ahrefs *dofollow* surface is clean — 0 of 138
   unlisted dofollow hosts carry vendor vocabulary. The misses are (i) one `/all/` PBN host Ahrefs
   scored clean, (ii) the injection cluster Ahrefs scored clean, and (iii) the Semrush-only half,
   which was mined for ground (a) anchors but never for grounds (c)/(d) paths. (iii) is where 23 of
   the 27 additions come from, and it is a methodological gap, not a data gap.

---

## 5. Recommended total entry count

**Baseline note:** the file changed on disk during this review (a parallel pass withdrew Section 5 —
`whosmypro.com` and `homeownerideas.com` — as false positives). Header now reads
`TOTAL ENTRIES: 458`. Verified against the current file: 458 `domain:` lines, no duplicates, split
258 / 43 / 14 / **26** / 117 across Sections 1, 2, 3, 4, 6. **Section 4 is unchanged**, so every
finding above stands as written. Counts below use 458.

| | Entries | Conditional on Section 4? |
|---|---|---|
| Current file (post Section-5 withdrawal) | 458 | — |
| §3.1 marketplace fingerprint hosts | +20 | yes |
| §3.2 listing-path kit | +3 | yes |
| §3.3 `newsblogsports.site` | +1 | no |
| §3.4 Network D injection | +3 | no |
| §3.5 `backlinksolutions.info` | +1 | no |

- **Recommended (keep Section 4, add all): 486 entries.**
- If the reviewer drops Section 4 instead: 458 − 26 + 5 = **437 entries**, and §3.1/§3.2 must be
  dropped with it.
- **Minimum defensible floor, whatever happens to Section 4: 463** — the five unconditional
  additions in §3.3–§3.5 are mandatory on the file's own stated grounds and should go in regardless.

I did not evaluate the Section 5 withdrawal; it is outside this brief. Note only that §3.4 creates a
new Section 7, so the next free section number is 7 whether or not Section 5 is reinstated.

Section placement for the additions: §3.1 and §3.2 extend **Section 4** (restate its counts as
49 domains / ~75 dofollow links); §3.3 extends **Section 2**; §3.5 extends **Section 6**; §3.4 needs a
new **Section 7 — compromised-host link injection, dofollow. 3 domains / 6 links. Grounds (b)+(c)**.

Also update in the header: `TOTAL ENTRIES`, the Section 4 block (counts, the (d)-first reframing in
§1.2, the §2 reconciliation note), and NOT-DISAVOWED [4], whose "777 Semrush-only domains with no
dofollow anchor naming ngwindows.com" is **wrong as stated** — 33 Semrush-only hosts carry a
dofollow word-boundary `ngwindows.com` anchor and are not in the file; 23 of them are recommended
above and the remaining 10 are the legitimate hosts in §3.6.
