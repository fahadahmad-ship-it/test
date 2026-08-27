"""Score every ranking page as a link target.

Opportunity is not traffic and it is not position. It is the traffic a page
would gain from a realistic position improvement, discounted by how hard that
improvement is to buy -- and the thing that decides difficulty is how many
referring domains the page already has. A page at #9 with 0 referring domains
and a page at #9 with 237 are not the same investment.

Two corrections that changed the ranking materially:

  A raw CTR model over-rates high-volume head terms, because a page ranks for
  a whole topic rather than one keyword and the head term's volume does not
  scale. Ahrefs' traffic potential -- the total traffic the #1 page for the
  parent topic actually receives -- is the honest ceiling. Applying it moved
  rear-delt-fly from first place to marginal: 84,000 volume, but the topic
  tops out at 7,600 and the page already takes 5,098 of it.

  Commercial proximity is applied last, as a weight rather than a filter, so
  a page can still surface on traffic alone and be judged on its merits.
"""
import csv

CTR = {1: .270, 2: .155, 3: .110, 4: .080, 5: .062, 6: .049, 7: .040,
       8: .033, 9: .028, 10: .025, 11: .020, 12: .017, 13: .015, 14: .013,
       15: .012, 16: .011, 17: .010, 18: .009, 19: .008, 20: .007}


def ctr(pos):
    return CTR.get(int(pos), max(.001, .007 - (pos - 20) * .0002)) \
        if pos <= 20 else max(.001, .007 - (pos - 20) * .0002)


def realistic_target(pos, refdomains):
    """Where 2-3 quality links could plausibly land the page."""
    gain = (5 if refdomains <= 5 else 4 if refdomains <= 20 else
            2 if refdomains <= 50 else 1 if refdomains <= 120 else 0.5)
    if pos <= 3:
        gain *= 0.4
    elif pos <= 5:
        gain *= 0.7
    return max(1, round(pos - gain))


rd = {r['url']: int(r['refdomains'])
      for r in csv.DictReader(open('offsite/refdomains.csv'))}
tp = {r['url']: r for r in csv.DictReader(open('offsite/tp.csv'))}

rows = []
for r in csv.DictReader(open('offsite/toppages.csv')):
    url, refd = r['url'], rd.get(r['url'])
    if refd is None or url not in tp:
        continue
    vol, pos = int(r['top_keyword_volume']), int(r['top_keyword_best_position'])
    cur = int(r['sum_traffic'])
    t = tp[url]
    tgt = realistic_target(pos, refd)
    raw = vol * (ctr(tgt) - ctr(pos))
    headroom = max(0, int(t['traffic_potential']) - cur)
    gain = min(raw, headroom)            # the ceiling correction
    cpc = float(t['cpc_usd'])
    rows.append({
        'url': url.replace('https://www.performancelab.com', ''),
        'vol': vol, 'pos': pos, 'rd': refd, 'tgt': tgt, 'cur': cur,
        'tp': int(t['traffic_potential']), 'head': headroom,
        'raw': round(raw), 'gain': round(gain), 'kd': int(t['difficulty']),
        'cpc': cpc, 'value': round(gain * cpc),
    })

rows.sort(key=lambda x: -x['value'])
print(f"{'PAGE':52}{'VOL':>7}{'POS':>4}{'RD':>4}{'KD':>4}{'NOW':>6}"
      f"{'CEIL':>7}{'RAW':>6}{'GAIN':>6}{'CPC':>6}{'$/MO':>7}")
print("-" * 113)
for x in rows:
    print(f"{x['url'][:50]:52}{x['vol']:>7,}{x['pos']:>4}{x['rd']:>4}"
          f"{x['kd']:>4}{x['cur']:>6,}{x['tp']:>7,}{x['raw']:>6,}"
          f"{x['gain']:>6,}{x['cpc']:>6.2f}{x['value']:>7,}")
print()
print("RAW  = uncapped CTR model.  GAIN = capped at the topic's remaining")
print("headroom.  $/MO = gain x CPC, a proxy for commercial worth.")
