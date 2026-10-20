# elitewrecker.com — Backlink Assessment & Disavow (Harbinger format)

Off-page audit of **elitewrecker.com** (Elite Service Recovery & Towing), produced in the
signed-off Harbinger 7-tab workbook format, following `BACKLINK_AUDIT_PLAYBOOK.md` /
`AUDIT_FORMAT.md`. Same method as the K&K Manufacturing audit.

## What's here
- `elitewrecker/scripts/` — the pipeline:
  - `build_universe.py` — union of Semrush + Ahrefs referring domains.
  - `load_classify.py` — merge links, enrich with Semrush metrics, assign the six statuses.
  - `build_xlsx.py` — render the 7-tab workbook (cell-for-cell to the signed template) + disavow file.
  - `check/` — verification suite.
- `elitewrecker/out/` — deliverables: `Elitewrecker_Backlinks_Audit.xlsx`,
  `disavow_elitewrecker.com.txt`.

## Sources & rules
- **Semrush is the source for every metric** (Authority Score, Backlinks, RD's, Traffic, Organic Keywords).
- **Ahrefs** (client-supplied CSV exports) adds link discovery + live-page HTTP status.
- Nothing is disavowed on score / TLD / vendor-flag alone — every disavow line rests on visible
  link evidence (spam anchor, spam page title/URL, or known link-network host).
- **elitewrecker.net is client-owned and 301s into elitewrecker.com**; its links fold into the
  single elitewrecker.com disavow file (the only uploadable Search Console property).
- The disavow file must **not** be uploaded until the previous SEO supplier and Harbinger
  confirm which links were commissioned. Held (Pending Partner) domains are excluded until then.

Raw pulled data and the client's signed template are git-ignored.
