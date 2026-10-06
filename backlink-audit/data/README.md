# Retained Semrush data — coverage and gaps

Semrush is at **zero API units** (`ERROR 132`) and Ahrefs Site Explorer resets **2026-10-25**.
Nothing here can be re-pulled until then. This is the complete surviving evidence base.

## What we have

| File | Contents | Coverage |
|---|---|---|
| `refdomains.csv` | 1,232 referring domains — domain;ascore;links;country;ip;first_seen;last_seen | **Complete** (full 7-page enumeration) |
| `links_raw.tsv` *(git: `git show 6f5f407:backlink-audit/work/links_raw.tsv`)* | 3,499 link rows — source_url, anchor, nofollow, page_ascore. **No header row.** | **46.4%** of 7,547 links |
| `anchors_multi.csv` *(git: `git show db9dcd8:backlink-audit/work/anchors_multi.csv`)* | 87 anchors with ref-domain and link counts | 17% of 503 anchors, but ~85% of links by volume |
| `anchors_observed.csv` | 76 links — source_domain;source_path;anchor;nofollow | Small, but the only file with path split out |
| `aggregates.csv` | overview, 30-month history, geo, TLD, categories | Complete as pulled |

Two files live only in git history, not the working tree. Recover with the `git show` commands above.

## What we do NOT have

1. **`target_url` / `redirect_url` — never pulled.** This is the decisive gap. Without it, whether
   the spam points at ngwindows.com or at the 14 redirect shells is **inferred from anchor text
   alone**. It determines whether the disavow file is 5 entries or ~92, and whether deleting the
   redirects would sever ~4,800 links or zero. Pull this first when units reset.
2. **~4,048 links (53.6%)** never retrieved.
3. **416 of 503 anchors** — the long tail, estimated at ±3pp, never measured.
4. **`backlinks_pages`** — which target pages absorb the spam. The "~100% homepage" claim rests on
   a partial pull and does not reconcile arithmetically (5,098 spam links cannot fit in ~3,883
   homepage links).
5. **`backlinks_refips`** raw export — cluster counts survive only in prose.
6. **All traffic, organic-keyword and competitor data** — the −87.7% decline, the position bands,
   the Window World Atlanta benchmark. These exist **only as transcribed tables inside
   `impact-and-recovery-roadmap.md`**, never as raw files. They cannot be re-derived or audited
   against source.

## First pulls when units reset (2026-10-25)

1. `backlinks` with `export_columns` including **`target_url` and `redirect_url`**, filtered to
   vendor anchors — settles the central question.
2. `backlinks_pages` — settles which pages are actually hit.
3. Full `backlinks` pagination for the remaining ~4,000 links. **Budget check first:** 500-row
   pages cost ~48,000 units each, which is what exhausted the balance.
4. Ahrefs Site Explorer for the cross-check this audit has never had.
