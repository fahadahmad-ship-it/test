# RAS Systems — Backlink Audit & Disavow (Harbinger format)

Referring-domain audit and Google disavow review for **ras-systems.com**, produced in the
signed-off Harbinger/NIC workbook format. Follows `BACKLINK_AUDIT_PLAYBOOK.md` and
`AUDIT_FORMAT.md`.

Money site: **ras-systems.com**. Owned domains that 301-redirect into it:
**rasmachines.com, ras-systems.net, ras-systems.us** (Semrush folds their inbound links into
the money-site profile via `redirect_url`).

## Layout
```
ras/
  data/
    fetch/        # raw Semrush backlinks pages (bl_*.csv)
    rd/           # raw Semrush referring-domains pages (rd_*.csv)
    metrics/      # as_comparison.csv (Authority Score, bulk), as_delta.csv, domain_rank.csv
    ahrefs/       # client-supplied Ahrefs exports (UTF-16 + converted .utf8.csv)
    work/         # derived domain lists
    harbinger_logo.png
  ref/            # K&K signed template (format reference)
  scripts/
    load.py           # robust Semrush (semicolon) + Ahrefs (TSV) readers
    rootdom.py        # registrable-domain extraction (publicsuffixlist, keeps blogspot/web.app subdomains distinct)
    classify.py       # anchor typing + 6-status domain classifier (playbook rules)
    pipeline.py       # merge Semrush+Ahrefs, per-domain aggregation + classification
    build.py          # builds the 7-tab workbook + per-property disavow files + DELIVERY.md
    verify.py         # both-directions correctness checks
    compare.py        # cell-for-cell structural match vs the signed template
  out/            # deliverables: workbook, disavow_*.txt, DELIVERY.md
```

## Rebuild
```
python3 -I scripts/build.py      # writes out/RAS_Systems_Backlinks_Audit.xlsx + disavow files + DELIVERY.md
python3 -I scripts/verify.py     # correctness checks (both directions)
python3 -I scripts/compare.py ref/KandK_template.xlsx out/RAS_Systems_Backlinks_Audit.xlsx
```

**Nothing here has been submitted to Google.** The disavow files are drafts; held domains are
excluded pending the previous SEO partner's confirmation.
