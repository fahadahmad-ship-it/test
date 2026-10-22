# aaronshometech.com backlink audit

Semrush-sourced referring-domain audit + Google disavow file in the signed-off
Harbinger format (see `../../AUDIT_FORMAT.md` and the playbook). Ahrefs API units
were exhausted this cycle, so this audit is Semrush-only (see `out/AUDIT_SUMMARY.md`).

## Deliverables (`out/`)
- `Aarons_Home_Tech_Backlink_Audit.xlsx` — 7-tab workbook.
- `disavow_aaronshometech.com.txt` — disavow file for the money-site property (full union).
- `AUDIT_SUMMARY.md` — client-facing findings, actions, open items, and limits.

## Pipeline (`scripts/`)
All scripts run with `python3 -I` and take paths as arguments (downloaded data is untrusted).

1. `load.py data data/joined.json` — read the Semrush CSVs (`data/rd`, `data/fetch`),
   join link evidence to referring domains, dedupe links.
2. `classify.py data/joined.json config.py data/classified.json data/metrics` — one
   status per domain on visible evidence (six statuses, no Review bucket). Uses the
   bulk comparison Authority Score (`data/metrics/*cmp*`) and organic metrics
   (`data/metrics/*rank*`).
3. `build.py data/classified.json config.py data/anchors_0.csv out/Aarons_Home_Tech_Backlink_Audit.xlsx out/`
   — build the workbook + disavow file.
4. `verify.py data/classified.json config.py out/disavow_aaronshometech.com.txt out/Aarons_Home_Tech_Backlink_Audit.xlsx`
   — disavow-file integrity + exhaustive both-directions evidence sweep + workbook structure.

`config.py` holds the only per-client constants (money site, owned domains,
service/geo vocabulary, spam signatures). `anchortype.py` is the shared anchor-type
classifier.

## Data provenance
- Referring domains: Semrush `backlinks_refdomains` (5,392 domains).
- Link evidence: Semrush `backlinks` — bulk passes + one filtered pull per otherwise
  uncovered domain, so every referring domain has real link evidence (16,598 links).
- Anchors: Semrush `backlinks_anchors`.
- Authority/own-profile metrics: Semrush `backlinks_comparison` (all 5,392).
- Organic traffic/keywords: Semrush `domain_rank` (us) for all retained/held/
  higher-authority domains + disavow candidates with authority; no-authority spam
  (AS<3) recorded as real zeros (validated: 0/60 sampled had any traffic).

`data/joined.json`, `data/classified.json`, `data/chunks/`, `data/all_domains.txt`
are regenerable intermediates (gitignored); the raw Semrush pulls are kept.
