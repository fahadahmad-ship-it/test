# Independent Re-check: the "14 redirect shells" attribution finding

**Role:** adversarial verification of the finding in `anchor-and-attribution-forensics.md` §2–§3, §8
and `FINAL-AUDIT.md` lines 35–52 / `toxic-domain-inventory.md` §183–200.
**Date:** 2026-10-06. **Verifier:** independent; did not author the original finding.

**Bottom line:** the *infrastructure* half of the claim survives contact and is now considerably
better evidenced than it was. The *attribution* half — "~94% of the spam targets the shells, so
deleting the redirects severs ~4,815 toxic links" — **does not survive**. It is not derivable from
the committed evidence, its headline numbers do not reconcile, and the action it recommends is
unsafe to run first.

---

## 1. What I independently verified

### 1.1 DNS was never blocked — the prior analyst stopped one step too early

`anchor-and-attribution-forensics.md` §7.1 states registrant/infrastructure checks were impossible
because "outbound HTTP to all 15 domains was blocked by this environment's egress proxy and `whois`
is unavailable."

**HTTP blocking: confirmed true.** Both `curl` and `WebFetch` are refused at the proxy for all 15
domains and for every third-party redirect-checker, RDAP endpoint and archive service I tried:

```
curl: (56) CONNECT tunnel failed, response 403
x-deny-reason: host_not_allowed
```
`web.archive.org`, `rdap.org`, `rdap.verisign.com`, `www.rdap.net`, `api.redirect-checker.net`,
`urlbacklinkschecker.space` and even `www.ngwindows.com` are all `EGRESS_BLOCKED`. `whois`, `dig`,
`nslookup` and `host` are genuinely not installed.

**But DNS was never blocked.** `getent hosts` works, and port 53 to 8.8.8.8 is open. I wrote a
minimal DNS client (`/tmp/dnsq/q.py`) and pulled A, NS, MX and TXT for all 15 domains plus controls.
This produced the single strongest piece of evidence in the whole engagement, and it was available
to the original analyst the entire time. **The §7.1 claim that infrastructure could not be checked
is wrong.**

### 1.2 The 14 domains are real, live, and sit in ONE GoDaddy account

All 14 resolve, to two IP pairs:

| Group | Forwarding IPs | Domains | Semrush `first_seen` |
|---|---|---|---|
| A | 15.197.225.128 / 3.33.251.168 | ngawindows.com, roiwindows.com, thermalprowindows.com, qualitypluswindows.com, northpointwindows.com, performingwindows.com, thermatrustwindows.com, northgeorgiawindows.net | Jul–Sep **2024** |
| B | 15.197.142.173 / 3.33.152.147 | thermalastwindows.com, e2windows.com, choiceviewwindows.com, ngwindow.com, northgawindows.com, northgeorgiawindow.com | Feb–Jul **2026** |

Two corrections to the brief: there are **four** forwarding IPs, not three (3.33.152.147 was
missed), and the date range is **Jul 2024 – Jul 2026**, not "Jul 2024 – Jul 2025".

These IP pairs are **GoDaddy Domain Forwarding** running on AWS Global Accelerator. This matters:
GoDaddy Domain Forwarding is a self-serve registrar feature that **only the registrant can
configure**. So the redirects are deliberate and were set by whoever owns the domains.

**The decisive new datum — nameservers:**

- All 14 shells: **`ns23.domaincontrol.com` / `ns24.domaincontrol.com`** — the *identical* pair.
- `ngwindows.com` (the client's real site): **Cloudflare** (`jim/pat.ns.cloudflare.com`), MX =
  **Microsoft 365** (`ngwindows-com.mail.protection.outlook.com`).
- Control case — `northgeorgiawindows.com`, a *different* company (Nelson Exteriors), also at
  GoDaddy: **`ns73`/`ns74.domaincontrol.com`**, Google site-verification TXT, no MX.

GoDaddy spreads customers across many nameserver pairs; the control case proves a different GoDaddy
customer gets a different pair. **All 14 landing on ns23/ns24 is strong evidence of a single
registrar account / single operator.** Across *both* IP groups and *both* registration waves — so
the 2024 and 2026 batches are the same hand.

Equally important, and *not* in the original finding: **the client's own stack shares nothing with
the 14.** ngwindows.com is Cloudflare + Microsoft 365; the 14 are GoDaddy + GoDaddy's default
`secureserver.net` MX (which is auto-provisioned on registration and is therefore not evidence of
use). There is no infrastructure link between the client and the shells.

### 1.3 The 14 behave like redirects in the link data

In `data/refdomains.csv` all 14 appear as referring domains to ngwindows.com with **2–6 links each,
57 links total — 0.8% of the 7,547-link profile**, ascore 2, country US. A content site accumulates
varied links; 2–6 links apiece is the classic footprint of a redirect record. This corroborates
"these 301 into ngwindows.com." I could not observe the 301 itself (HTTP blocked), but
GoDaddy-forwarding IPs + presence as low-link referring domains to ngwindows.com is good
circumstantial proof. **I put the bare structural claim "the 14 are redirect domains pointing into
ngwindows.com, under one operator" at ~92%.**

### 1.4 The vendor campaign-ID claim holds up — and is stronger than stated

This *is* testable from the raw export, and I re-derived it independently. Of 3,500 rows, 1,047 have
a trailing `-NNNNNN` slug across 21 IDs. Mapping ID → domain named in the anchor:

| Slug ID | n | Dominant domain | Purity |
|---|---|---|---|
| -148030 | 181 | ngawindows.com | 100% |
| -211287 | 156 | thermalprowindows.com | 100% |
| -170322 | 148 | qualitypluswindows.com | 100% |
| -160633 | 147 | performingwindows.com | 100% |
| -150104 | 138 | northpointwindows.com | 100% |
| **-148096** | **112** | **ngwindows.com** | **100%** |
| -178285 | 88 | roiwindows.com | 100% |
| -211290 | 41 | thermatrustwindows.com | 100% |

Overall slug-ID purity **99.81%** (1,045/1,047). And **zero** of 3,500 anchors name two domains.
The vendor really does run one campaign per target, and **ngwindows.com is itself just target #15
in the same vendor account, same slug format, same spam network.** That is a real finding and it is
solid.

Note what it does *and does not* prove: it proves **one buyer bought fifteen campaigns**. It says
nothing about **who the buyer is**.

### 1.5 DR check — and why the DR evidence is worthless

All 14 return DR 0.0, and ngwindows.com returns 27.0. I validated the free endpoint against known
targets (google.com 100, bbb.org 93, guildquality.com 75, atlantahomeimprovement.com 45,
thermalwindows.com 30), so the endpoint works.

**But `northgeorgiawindows.com` — a live competitor site with real content — also returns DR 0.0,**
as does `nelsonexteriors.com`. DR 0 therefore means "below Ahrefs' index threshold", which is
routine for small local sites. **"All 14 are Ahrefs DR 0" is not evidence that they are
content-free, and should be struck from the supporting-evidence list.** It is consistent with the
shell hypothesis; it does not discriminate.

### 1.6 Open-web check: at least two are real third-party brands, five are client brand variants

The client is **NG Windows**, Alpharetta GA, founded 2003 by Ted Kirk as **North Georgia Replacement
Windows**, recently rebranded, exclusive Infinity by Marvin dealer for Georgia, and a Therma-Tru
dealer (Roswell GA). Against that:

- **Client brand variants (5):** `ngawindows.com`, `ngwindow.com`, `northgawindows.com`,
  `northgeorgiawindow.com`, `northgeorgiawindows.net`. Note the three registered **Jun–Jul 2026**
  are typos of the *new* "NG Windows" name — i.e. defensive registration tracking the rebrand.
  Genuinely strong evidence for the property-side reading.
- **`thermatrustwindows.com`** is adjacent to Therma-Tru, a brand the client actually sells.
- **Real, active, unrelated businesses (2):** **ThermaLast Windows**, a New Jersey manufacturer
  since 2013 (showrooms South Amboy, Summit, Staten Island) trading at `thermalast.net`; and
  **ROI Windows**, the window division of ROI Home Improvements in Waco, Texas
  (`roihomeimprovements.com`). Neither owns the `*windows.com` variant in our list — someone else
  registered the brand-adjacent `.com` and pointed it at an Alpharetta installer.
- **No trace found (6):** performingwindows, qualitypluswindows, northpointwindows,
  choiceviewwindows, e2windows, thermalprowindows (a "Thermal Pro Windows & Siding" exists in Salt
  Lake City, unrelated).

So "zero unrelated window domains anywhere in the anchor set"
(`anchor-and-attribution-forensics.md` §152) **is false.** At least two are variants of real
out-of-state window brands. The original hypothesis table rests partly on a claim the open web
contradicts.

---

## 2. What I could NOT verify — and the load-bearing failure

### 2.1 The redirect destination and the registrant

Not verifiable here. Every HTTP path, every RDAP/WHOIS endpoint, every archive service and every
redirect checker is blocked by the egress proxy (§1.1). I have no registrant name, no creation
date, and no first-hand observation of a 301 or its `Location` header.

### 2.2 The committed evidence cannot support the attribution claim at all

This is the serious one.

`git show 6f5f407:backlink-audit/work/links_raw.tsv` is **3,500 rows, exactly 4 tab-separated
columns, no header**: `source_url`, `anchor`, `nofollow`, `page_ascore`. There is **no target
column and no `redirect_url` column.**

Two problems follow:

1. **The commit message for 6f5f407 is false.** It states the file is "the Semrush link-level
   export (source URL, anchor, dofollow status, **target**)… Committed so every disavow decision is
   traceable to the row that justifies it." The target column is not in the file. The audit's own
   traceability guarantee does not hold for the one column the headline finding depends on.
2. **`anchor-and-attribution-forensics.md` §7.2 cites "`redirect_url` values"** as part of the
   evidence base. No committed artefact contains that field. It may have existed in an uncommitted
   API response, but it cannot be checked, and Semrush is now dead.

**So the entire "these are the link targets, not anchors naming rivals" inference rests on anchor
text alone.** And the anchor text is vendor sales copy with the domain as a template token:

> `Expert Backlink Building Services to Grow qualitypluswindows.com Website Rankings`
> `Niche edits on qualitypluswindows.com helped us rank in the top 3 for key terms`

A template that interpolates the domain the campaign was *ordered under* is **exactly as consistent
with the link pointing at ngwindows.com directly** as with it pointing at the shell. The raw data
cannot distinguish these. The original finding treats one reading as established and never states
that the discriminating column is absent.

### 2.3 The headline numbers do not reconcile

From the committed 3,500 rows, assigning each row the domain its anchor names:

| | rows | share |
|---|---|---|
| Anchor names one of the 14 shells | 2,793 | 79.8% |
| Anchor names ngwindows.com only | 412 | 11.8% |
| Anchor names neither | 295 | 8.4% |

Shell share of domain-naming rows = 2,793 / 3,205 = **87.1%**.

The audit claims **94.4%**, from "~4,815 via redirect vs ~283 direct". Neither figure is
reproducible:

- **4,815 exceeds the entire 3,500-row export.** It is an extrapolation over the 28% of the profile
  Semrush never returned (units exhausted at 72% coverage), presented in bold as a count of links
  that would "vanish at source".
- The "~283 direct" figure contradicts the **412** direct-naming rows actually in the file.
- 94.4% vs 87.1% — the gap comes from the same unexplained extrapolation.

An irreversible recommendation is sized by a number ~1.4× larger than the evidence file that is
supposed to justify it.

---

## 3. My own confidence figures

I split the original Hypothesis A, because "purchased campaign run on the property" silently
conflates two scenarios with opposite remediation paths.

| # | Hypothesis | My confidence | Reasoning |
|---|---|---|---|
| **A1** | **Client-side commissioned** — client, prior agency or freelancer with registrar access owns the 14 | **~45%** | Five domains are typo-variants of the client's own brand, three registered right as the 2003-era name was retired for "NG Windows" — only a brand owner does that. GoDaddy forwarding requires registrant access. ngwindows.com is target #15 in the same vendor account. |
| **A2** | **SEO vendor / lead-gen partner owns the shells**; client has no registrar control and may not know they exist | **~30%** | All 14 in one GoDaddy account (ns23/ns24) that shares *nothing* with the client's Cloudflare + Microsoft 365 stack. Buying keyword/brand-adjacent domains and 301-ing them at the money site is standard low-end vendor practice — it keeps the spam off the client's own domain. Two of the 14 are variants of *other companies'* live brands (ThermaLast NJ, ROI Windows TX), which a legitimate Alpharetta installer has no business reason to own. |
| **B** | **Negative SEO via attacker-owned 301s** (redirect laundering) | **~15%** | A real, documented technique, and the original rebuttal to it is weak — it argues the attacker's cost per link is uneconomic, which misses *why* the technique is used: laundering through redirects makes the victim look like the *beneficiary* of manipulation (and, here, like a hijacker of competitor brands), which is far more damaging and far harder to disavow than a direct blast. What genuinely argues against B is the brand-typo subset and the rebrand-timed 2026 registrations — an attacker gains little from those. I keep B meaningfully alive, not at 12%. |
| **C** | **Unrelated domain monetiser / affiliate** forwarding a portfolio at whoever converts | **~10%** | Fits the two real-brand variants and the six untraceable generics; fits the GoDaddy-only footprint. Does not fit the client-brand typos. |

**"Property-side, not hostile" (A1+A2) ≈ 75%,** against the claimed ~85%. And only **A1 ≈ 45%**
supports the recommended action, because A2 and C mean the client cannot execute it.

Separately, and more important than the hypothesis split: **the claim that ~94% of the spam targets
the shells is itself only ~55–60% likely to be correct**, because the discriminating column is
missing and the alternative reading of the anchor template is equally consistent (§2.2). The
original document assigns no uncertainty to this step at all — it is treated as observed fact and
everything downstream inherits that. The ~85% figure is the confidence on *registrant identity*
conditional on the targeting claim being true; the two were never multiplied.

---

## 4. Is "delete the 301 redirects" safe as the #1 action?

**No. It should not be the first action, and in its current blanket form it should not be
recommended at all.**

1. **The premise is unverified.** If the 2,793 links point at ngwindows.com *directly* and the
   shell name is just a template token, deleting the redirects severs **zero** toxic links. The
   action then has pure downside. Nothing in the committed evidence rules this out.
2. **It destroys real brand assets.** At least five of the 14 are the client's own brand variants,
   covering a company that traded as "North Georgia Replacement Windows" from 2003 and rebranded
   only recently. Legacy citations are still live on the open web (Houzz, BBB, GuildQuality,
   Therma-Tru's dealer directory, Yelp) under the old name. Those redirects carry type-in traffic,
   legitimate legacy link equity and probably live leads. The audit does say "keep the defensive
   typo-variants registered" — but Action 1 as written instructs dropping the redirect on all 14
   *including* those five. Keeping a domain registered while killing its redirect preserves the
   asset and discards the value.
3. **It may not be executable.** Under A2/C (~40% combined) the client has no access to that
   GoDaddy account. The audit flags this as "*if* the client controls them" in one line of §214
   while stating the action unconditionally in the §8 headline and in `FINAL-AUDIT.md`.
4. **It is sized by an unreproducible number** (§2.3).
5. **It is hard to reverse.** Redirect equity, once dropped and re-crawled, does not come back by
   re-enabling the forward.

**What should be #1 instead:** establish who owns the GoDaddy account holding all 14 — a single
question to the client, answerable in minutes, which resolves A1 vs A2 vs B/C outright. The disavow
work (which is reversible, and which covers the spam under *every* hypothesis) proceeds in
parallel. If deletion does go ahead later, it should be: 410 on the nine non-brand domains only,
brand variants left redirecting, staged and monitored — not a blanket drop of all 14.

---

## 5. The single cheapest test that settles it

**Fetch two spam source pages from an unrestricted machine and read the `href`.**

```
curl -sL https://urlbacklinkschecker.space/dir/seo-ranking-links-170322 | grep -o 'href="[^"]*windows[^"]*"'
curl -sL https://backlinkcheckerseo.space/dir/ethical-seo-backlinks-160633 | grep -o 'href="[^"]*windows[^"]*"'
```

Thirty seconds, no API units, no Semrush, no Ahrefs. If the `href` is `qualitypluswindows.com`, the
redirect-laundering model is confirmed and the 94% claim can be properly re-measured. If it is
`ngwindows.com`, **the entire finding collapses** and the top recommendation would have destroyed
the client's brand redirects for nothing.

This is a better first test than the WHOIS lookup §7.1 proposes, because WHOIS answers *who owns the
shells* but leaves the load-bearing *targeting* claim untested. Do the `href` test first; it decides
whether the ownership question is even worth asking.

**What would take this to ~99%:** the `href` test confirming shell targets, **plus** RDAP/WHOIS on
all 14 showing a registrant or registrar account matching the client, **plus** the client confirming
they can log into the GoDaddy account carrying ns23/ns24. All three are cheap. None has been done.

---

## 6. Corrections the other documents need (not applied — out of scope for this doc)

1. `anchor-and-attribution-forensics.md` §7.1 — DNS was available; infrastructure *was* checkable.
2. §152 — "zero unrelated window domains" is false (ThermaLast, ROI Windows).
3. §7.2 / commit 6f5f407 message — no `redirect_url`/target column exists in any committed artefact.
4. §487 / `FINAL-AUDIT.md`:52 / `toxic-domain-inventory.md` — 94.4% and 4,815 are not reproducible;
   the committed export gives 87.1% and a 3,500-row ceiling.
5. Supporting-evidence lists — drop "all Ahrefs DR 0" as discriminating evidence (§1.5).
6. The brief's "3 IPs" and "Jul 2024–Jul 2025" — actually 4 IPs and Jul 2024–Jul 2026.
