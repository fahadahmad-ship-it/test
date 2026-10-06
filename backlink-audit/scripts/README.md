# Analysis scripts

Run with `python3 -I <script> <args>` from the repo root.

## Ahrefs analysis (this session)
| Script | Args | What it answers |
|---|---|---|
| `decisive.py` | ahrefs-backlinks.tsv | Do any spam anchors name a shell domain, and does any shell appear in a redirect chain? |
| `redirects.py` | ahrefs-backlinks.tsv | Enumerates all 28 distinct redirect chains and every target URL |
| `shellhunt.py` | ahrefs-backlinks.tsv ahrefs-refdomains.tsv | Searches every field of both datasets for the 14 shell domains; also checks the Semrush side for source-vs-anchor asymmetry |
| `crosscheck.py` | ahrefs-refdomains.tsv ahrefs-backlinks.tsv semrush-refdomains.csv | Tool overlap, export completeness, spam-flag breakdown |
| `ahrefs_core.py` | ahrefs-refdomains.tsv ahrefs-backlinks.tsv | Disavow-relevant slice, DR distribution of spam, high-DR spam, top genuine domains |

Data paths: `backlink-audit/data/ahrefs/` and `backlink-audit/data/refdomains.csv`.

`../../scripts/` holds working scripts written by the verification agents.

## Note on the Ahrefs files
Supplied as **UTF-16 LE**, converted to UTF-8 on import. Tab-delimited.
If re-importing a fresh export: `iconv -f UTF-16LE -t UTF-8 in.csv > out.tsv`.
Read with `encoding='utf-8-sig'` to strip the BOM.
