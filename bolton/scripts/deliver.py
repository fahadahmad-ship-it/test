"""
deliver.py — generate the plain-text client delivery note (SUMMARY.md) from counts.json.
Run after build.py. No artifacts (per repo CLAUDE.md); plain Markdown file only.
"""
import os, json, csv, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
OUT = os.path.join(BASE, 'out'); DATA = os.path.join(BASE, 'data')
sys.path.insert(0, HERE)
import build
c = json.load(open(os.path.join(OUT, 'counts.json')))
# manual-review items: disavowed domains that still have organic traffic
_ctx = build.build(); _rows = _ctx['rows']
_aggs = {d: build.agg_domain(d, _rows[d], _ctx) for d in _rows}
reviews = sorted(((d, _aggs[d]['traffic'], _rows[d]['reason']) for d in _rows
                  if _rows[d]['status']=='Spam (Disavow)' and (_aggs[d]['traffic'] or 0) >= 50),
                 key=lambda x: -x[1])
review_md = '\n'.join(f"- `{d}` — organic traffic {t:,}; {rs}. " for d,t,rs in reviews) or '- (none)'
sd = c['status_domains']; sl = c['status_links']
hist = list(csv.DictReader(open(os.path.join(DATA,'history.csv')), delimiter=';'))
sep = next((h for h in hist if h['date_unix']=='1788235200'), None)
aug = hist[0]; now = hist[-1]
spam_total = sd.get('Spam (Disavow)',0)+sd.get('Spam (Nofollow, No Action)',0)
held_total = sd.get('Held (Pending Partner)',0)+sd.get('Held (Nofollow, No Action)',0)

md = f"""# Bolton Service WNC — backlink audit & disavow: delivery note

**Prepared for:** Bolton Service WNC ({ 'boltonservicewnc.com' })
**Date:** 2026-11-09
**Deliverables in this folder (`bolton/out/`):**
- `Bolton_Service_WNC_Backlinks_Audit.xlsx` — the 7-tab audit workbook (Harbinger format).
- `disavow_boltonservicewnc.com.txt` — **the file to upload for the money site** (full union).
- `disavow_boltonwnc.com.txt` — upload for the boltonwnc.com property.
- `disavow_webolton.com.txt` — upload for the webolton.com property.

## What we found
- Your live link profile is **{c['total_domains']:,} referring domains / {c['total_links']:,} backlinks** — a large
  negative-SEO spam flood, not organic growth. Authority Score is 10.
- **The attack is recent and fast:** {sep['domains_num'] if sep else '—'} referring domains in September 2026,
  {now['domains_num']} by the start of November. The brief's figure was an older snapshot; we audited the full live profile.
- **Two separate campaigns, easy to tell apart:**
  - A link-scheme flood of PBN "SEO sales copy" anchors (e.g. *"High Quality Dofollow Backlinks DA 50 PA 40 …"*)
    pointed at your **home page**. This is the attack.
  - A set of directory links with **exact-match local service anchors** (e.g. *"AC Service Swannanoa NC"*)
    pointed at deep **/service/** and **/location/** pages. These *may* have been commissioned, so they are **held**.

## The verdict (every one of the {c['total_domains']:,} domains classified)
| Status | Domains | Backlinks |
|---|---:|---:|
| Spam (Disavow) | {sd.get('Spam (Disavow)',0):,} | {sl.get('Spam (Disavow)',0):,} |
| Held (Pending Partner) | {sd.get('Held (Pending Partner)',0):,} | {sl.get('Held (Pending Partner)',0):,} |
| Held (Nofollow, No Action) | {sd.get('Held (Nofollow, No Action)',0):,} | {sl.get('Held (Nofollow, No Action)',0):,} |
| Spam (Nofollow, No Action) | {sd.get('Spam (Nofollow, No Action)',0):,} | {sl.get('Spam (Nofollow, No Action)',0):,} |
| Keep | {sd.get('Keep',0):,} | {sl.get('Keep',0):,} |
| Own Site | {sd.get('Own Site',0):,} | {sl.get('Own Site',0):,} |

- **{c['disavow_domains']:,} domains go in the disavow file** (confirmed spam with at least one dofollow link).
- **{sd.get('Spam (Nofollow, No Action)',0):,} spam domains need no action** — every link is nofollow, so they pass nothing.
- **{sd.get('Held (Pending Partner)',0):,} domains are HELD** for the previous supplier to confirm before any disavow.

## Redirects & which file to upload
You own two domains that 301-redirect into the site — **boltonwnc.com** and **webolton.com** — and the spam
targets them by name. Semrush rolls their links into the money-site profile, so one audit captured everything.
You told us you can upload to **all three** Search Console properties, so there is one file per property:
- **`disavow_boltonservicewnc.com.txt` is the full union of every bad domain** ({c['disavow_by_property']['boltonservicewnc.com']:,} point
  directly at the money site; the rest reach it through the two redirects). Upload this one to the money-site property.
- `disavow_boltonwnc.com.txt` ({c['disavow_by_property']['boltonwnc.com']:,}) and `disavow_webolton.com.txt`
  ({c['disavow_by_property']['webolton.com']:,}) each carry only the domains whose links point at that property.

Before uploading: **confirm whether a disavow file already exists** on each property. If one does, uploading
**replaces** it — merge first. If none exists, these are the first files.

## Before you submit — the supplier conversation
The brief calls the party who confirms commissioned links the **"supplier"**; the workbook calls the same role
**"partner"** throughout (so every audit reads the same). The {sd.get('Held (Pending Partner)',0):,} held domains carry exact-match
commercial anchors or links to deep money pages that *could* be paid placements. **Do not upload any disavow file
until the supplier confirms which of those anchors were commissioned.** Tab 5 (Exact Match Anchors) and Tab 6
(Pending Disavow Lines) list exactly what to ask about; the two blank columns on Tab 5 are for their answers.

## Manual review before you upload ({len(reviews)} domains)
These are IN the disavow file on visible evidence (an off-topic anchor or a link injected at the
site's /sitemap), but they also have some organic traffic, so confirm each by hand before submitting
— a judgement call, not an error:
{review_md}

## Honest limits
- **Metrics source:** Authority Score, backlinks and referring-domain counts are from **Semrush**; per-domain
  organic **Traffic and Organic Keywords are from Semrush `domain_rank`** (the correct primary source). The
  Ahrefs API workspace hit its monthly unit ceiling mid-audit (resets 2026-11-25), so Ahrefs contributed only a
  100-domain metrics sample and no second link-discovery pass; this does **not** affect any disavow decision —
  every one rests on the visible anchor, page title, or host, never on a score.
- **Live-page status** of example links rests on Semrush's last crawl (we could not fetch every linking host).
- We have **not** submitted anything to Google Search Console — that is yours to do after the supplier confirms.
"""
open(os.path.join(OUT, 'SUMMARY.md'), 'w').write(md)
print('wrote', os.path.join(OUT, 'SUMMARY.md'))
