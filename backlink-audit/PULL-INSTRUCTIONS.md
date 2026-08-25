# Semrush pull — run this in the thread where the connector works

## Why

334 referring domains carry a verdict based only on authority, backlink
count, IP and name. **Not one of their links appears in the 50k export**, so
there are no anchors, no targets and no redirect data to judge them on.
Every client correction that reversed a verdict in this set —
`appsupports.co`, `leafysouls.com`, `thecompleteportal.com`,
`cloudaicrypto.com`, `illuminatelabv.com` — came from exactly this gap.
They total 3,522 backlinks (0.3% of the profile), but they are the only
unresolved part of the audit.

## The call

One paginated pull, excluding the three mass-footprint domains that are now
confirmed `drect.net` affiliate traffic. Everything else fits in ~27,623
rows, from which the 334 review domains are filtered locally.

```
execute_report(report='backlinks', params={
  target: 'performancelab.com',
  target_type: 'root_domain',
  display_limit: 10000,
  display_offset: 0,          // then 10000, then 20000
  export_columns: ['source_url','target_url','anchor','nofollow',
                   'response_code','redirect_url','external_num',
                   'page_authority_score','sitewide','first_seen','last_seen'],
  display_filter: [
    {field:'refdomain', operation:'equals', sign:'-', value:'hexcolor.co'},
    {field:'refdomain', operation:'equals', sign:'-', value:'wete.co'},
    {field:'refdomain', operation:'equals', sign:'-', value:'appsrankings.com'}]})
```

Repeat with `display_offset` 10000 and 20000 until a page returns fewer
rows than the limit.

**Page the output to disk as it arrives.** The rows come back through the
conversation, so holding 27k of them in context will exhaust it.

## Handing the result back — use the branch, not chat

Both threads have this repo. The other thread can commit the pull output
straight to the branch, and this one can fetch it — no uploading 27k rows
through a conversation.

In the thread that ran the pull:

```bash
cd backlink-audit
# write the pull output to data/semrush_backlinks_filtered.csv, then:
git add data/semrush_backlinks_filtered.csv
git commit -m "Add Semrush link-level pull for the 334 unsampled domains"
git push origin claude/performancelab-backlink-audit-avlvtz
```

Then say so here and I will run:

```bash
git pull origin claude/performancelab-backlink-audit-avlvtz
python3 semrush_ingest.py data/semrush_backlinks_filtered.csv out
python3 audit.py           data/semrush_backlinks_filtered.csv out
python3 refdomain_audit.py data/semrush_backlinks_filtered.csv \
                           data/performancelab_refdomains.csv out
python3 build_workbook.py  out
```

That thread does not need to interpret anything — it only needs to fetch
and commit. All the classification logic lives here.

## Alternatively, send it back

Save the semicolon-delimited output (one header line, then rows) as
`semrush_backlinks_filtered.csv` and upload it. Then:

```bash
cd backlink-audit
python3 semrush_ingest.py semrush_backlinks_filtered.csv out
python3 audit.py           <that file> out
python3 refdomain_audit.py <that file> data/performancelab_refdomains.csv out
python3 build_workbook.py  out
```

## What it unlocks

- **`redirect_url`** — the affiliate-redirect detector protects any domain
  routing through `drect.net`, `testolabpro.com`, `nutropic.com` or
  `prelabpro.com` automatically. That is how `hexcolor.co` resolved.
- **`response_code`** — the redirect-liveness check the brief asked for,
  skipped throughout for want of this column.
- **Anchors and targets** — the 334 stop being guesses.

## Also worth settling

`appsrankings.com` (22,204 backlinks) is retained on *inference* that it
shares the `hexcolor.co` network, not on observed data. One filtered call
confirms it:

```
display_filter: [{field:'refdomain', operation:'equals', sign:'+',
                  value:'appsrankings.com'}]
export_columns: ['source_url','target_url','anchor','redirect_url']
```

If `redirect_url` shows `drect.net`, the retention is verified. If not, it
is the largest wrong KEEP in the audit.
