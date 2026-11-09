# Bolton Service WNC audit — locked decisions

- Client / money site: boltonservicewnc.com
- Owned redirect domains (301 into money site, confirmed by user): boltonwnc.com, webolton.com
- GSC upload access (confirmed): ALL THREE properties. Produce 3 submittable disavow files:
  - disavow_boltonservicewnc.com.txt  = FULL UNION of every bad source domain (money-site file)
  - disavow_boltonwnc.com.txt         = attribution set (bad domains whose links point at boltonwnc.com)
  - disavow_webolton.com.txt          = attribution set (bad domains whose links point at webolton.com)
- Confirmation role: brief says "supplier"; sheet keeps saying "partner"; tie partner<->supplier once in each disavow header.
- Scope: FULL live profile (Semrush ~3,231 RD / 5,816 BL; Ahrefs ~1,670 live RD / 4,279 live BL).
- Template: match uploaded KandK_Manufacturing_Backlinks_Audit.xlsx cell-for-cell (see TEMPLATE_SPEC.md). Harbinger logo on Summary.

## Metric sources (honest note for deliverable)
- Authority Score, backlinks, RD's: Semrush (backlinks_comparison at scale; refdomains report as fallback).
- Per-domain organic Traffic + Organic Keywords: Ahrefs batch-analysis (scalable; Semrush domain_rank x3,231 infeasible in-session). Documented deviation.
- Link detail (anchor, target, redirect_url, response_code, first/last seen): Semrush backlinks report (has more links here: 5,816 vs Ahrefs 4,279).
- Ahrefs referring-domains used for additional-domain discovery + IP + DR corroboration.

## Vocabulary (exact-match commercial anchors) — HVAC/plumbing, WNC geo
Services: hvac, air conditioning, ac, heating, furnace, boiler, plumbing, plumber, drain, hydro jetting, heat pump, water heater, duct, cooling.
Geo (Western North Carolina): asheville, weaverville, swannanoa, fletcher, mills river, woodfin, arden, candler, black mountain, hendersonville, wnc, western north carolina.
Deep money pages pattern: /service/..., /location/...  (home page = boltonservicewnc.com/ ; redirect targets boltonwnc.com/, webolton.com/)
