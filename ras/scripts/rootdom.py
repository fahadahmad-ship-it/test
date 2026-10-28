"""Root-domain extraction with a pragmatic public-suffix list for the multi-level TLDs
that actually show up in backlink spam data."""

# two-level public suffixes (eTLD) we must keep 3 labels for
TWO_LEVEL = set("""
co.uk org.uk me.uk gov.uk ac.uk co.in net.in org.in gen.in firm.in co.nz org.nz
com.au net.au org.au id.au co.za org.za com.br net.br org.br com.mx com.ar com.co
co.id or.id web.id com.sg com.my com.ph com.tr com.ua com.pk com.bd com.ng com.gh
co.ke co.th in.th co.il org.il com.hk com.tw com.vn com.cn net.cn org.cn com.sa
com.eg com.kw com.qa com.lb com.pe com.ve com.ec com.do com.uy com.py com.bo
co.jp ne.jp or.jp go.jp com.ru org.ru net.ru com.pl com.es com.pt com.gr com.ro
com.cy com.mt co.rs org.rs com.hr com.ba com.mk com.al com.ge com.az com.kz
com.by com.md com.am com.np com.lk com.mm com.kh com.la com.mn
""".split())

try:
    from publicsuffixlist import PublicSuffixList
    _PSL = PublicSuffixList()
except Exception:
    _PSL = None

def root_domain(host):
    host = (host or '').strip().lower()
    if not host:
        return ''
    if ':' in host:
        host = host.split(':')[0]
    host = host.strip('.')
    if not host:
        return ''
    if _PSL is not None:
        # privatesuffix keeps private registries (blogspot.com, co.com, edu.pe, ...) as
        # distinct registrable domains, and strips www/other subdomains otherwise.
        ps = _PSL.privatesuffix(host)
        if ps:
            return ps
        # no known public suffix (e.g. intranet host) -> fall through to heuristic
    if host.startswith('www.'):
        host = host[4:]
    parts = host.split('.')
    if len(parts) <= 2:
        return host
    last2 = '.'.join(parts[-2:])
    last3 = '.'.join(parts[-3:])
    if last2 in TWO_LEVEL:
        return last3
    return last2

if __name__ == '__main__':
    tests = ['www.foo.co.uk','a.b.example.com','sub.1000.co.in','example.com','x.y.z.com.au','portal.ras-systems.com']
    for t in tests:
        print(t, '->', root_domain(t))
