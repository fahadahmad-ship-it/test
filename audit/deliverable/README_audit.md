# Controlled Comfort — backlink audit & disavow (delivery note)

Date: 2026-10-22 · Format: Harbinger signed-off audit (`AUDIT_FORMAT.md` + playbook).
Source: Semrush (profile metrics/recon) + client Ahrefs export (per-domain detail, 1,089 ref.
domains / 2,514 backlinks). "Partner" in the workbook = the previous SEO **supplier** this brief
names — same role, tied together here and in the disavow header rather than renaming the column.

## Files
- `controlled_comfort_backlink_audit.xlsx` — 7 tabs: Summary, Referring Domain Audit, All
  Backlinks, Anchor Analysis, Exact Match Anchors, Pending Disavow Lines, Disavow List.
- `disavow_controlledcomfort.txt` — the disavow file. **ONE file, one property**
  (controlledcomfort.com). **No disavow file currently exists on the property (client-confirmed),
  so this is a new upload (add), not a replace.**

## What we found (plain terms)
- The brief listed **56** domains. The live profile is **~1,124 referring hosts / 2,514
  backlinks**, growing ~70+ new referring domains/day — a large, ongoing operation.
- **Two campaigns, split by the page they point at:**
  1. A **home-page PBN / "buy-backlinks" flood** — `*.store` / `*.shop` / numbered `*.xyz`
     link-farms and spun sales-copy anchors ("Premium SEO Backlinks…", "DA 50 PA 40… Buy
     Backlinks Cheap", "Increase your Domain Authority… WhatsApp Us"). These rest on visible
     spam evidence and go in the file.
  2. A **deep service-page directory-listing campaign** — exact-match commercial anchors
     ("Furnace Repair Omaha NE", "Air Conditioner Repair Omaha NE") on `/services/heating` and
     `/services/air-conditioning`. These **may be commissioned** and are **HELD** for the supplier.

## The decision split (status = the six audit statuses; see workbook)
| Status | Domains | In disavow? |
|---|---|---|
| Spam (Disavow) | 348 | Yes |
| Spam (Nofollow, No Action) | 487 | No (all nofollow) |
| Held (Pending Partner/supplier) | 101 | No — pending supplier |
| Held (Nofollow, No Action) | 9 | No |
| Keep | 179 | No |
| Own Site | 0 | — |

*(Two independent adversarial reviews of the Keep/Spam boundary ran before shipping. They found
and fixed: 1 false positive — a page titled "Emergency Electrician Specialists" was wrongly
disavowed because "Specialists" contains the substring "cialis"; now Keep — and 44 false
negatives — link-broker / PBN pages whose spam copy sits in the page TITLE, not the anchor
("Where to buy aged domains and backlinks…", "Powerful PBN Backlinks…"); now disavowed. The
verification suite re-passes both directions after the fixes.)*

## Before you upload — do these first
1. **Confirm with the supplier** which of the 110 HELD directory placements they commissioned.
   Held domains are deliberately **excluded** from the file. Only move a held domain into the file
   if the supplier confirms it was NOT commissioned. Draft request:
   `../supplier_confirmation_request.md`.
2. **Do not upload before that conversation.** The file disavows the 348 evidence-backed spam
   domains only; it is safe to that extent, but the held set is the point of the whole audit.
3. We do **not** submit to Google Search Console for you — you upload it.

## Method notes / honest limits
- **Metrics source:** the "AS" column carries **Ahrefs DR** (and traffic/keywords from Ahrefs),
  because per-domain Semrush Authority Score was not pulled for all ~1,124 domains. The signed-off
  audit prefers Semrush AS as the number; swap it in if you want that exactly. **No decision rests
  on the score** — every disavow line rests on a visible spam anchor/host, not on DR.
  - This matters: 384 domains have DR ≥ 20, but only ~55 are genuine (real traffic). The other
    ~329 are **manipulated-DR link farms** — a naive "DR≥20 → keep" would have kept all of them.
    We kept the ~55 genuine citations (bbb.org, yellowpages, chamber of commerce, omahachamber.org,
    oppd.com, …) and disavowed the farms on evidence.
- **IP column:** not present in the Ahrefs export, so marked "n/a (not in export)".
- **Template match:** `compare.py` against the signed-off `.xlsx` template could not run — the
  template is not in this repo. The workbook follows the format spec (tabs/columns/styling incl.
  the accent `FF0C343D`, Geist, header-only borders). Run `compare.py` when the template is available.
- **Ahrefs API** was exhausted, so Ahrefs detail came from the client CSV export (as the playbook
  expects); Semrush provided the live recon.
