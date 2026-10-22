import sys
for path in sys.argv[1:]:
    print("="*70)
    print("FILE:", path.split('/')[-1])
    raw = open(path,'rb').read()
    print("bytes:", len(raw), "| first bytes:", raw[:4])
    enc = None
    for e in ('utf-16','utf-16-le','utf-8-sig','utf-8'):
        try:
            t = raw.decode(e)
            enc = e; break
        except Exception as ex:
            continue
    print("decoded with:", enc)
    text = raw.decode(enc)
    # normalize newlines
    lines = text.splitlines()
    print("line count:", len(lines))
    hdr = lines[0]
    delim = '\t' if hdr.count('\t') >= hdr.count(',') else ','
    print("delimiter:", repr(delim))
    cols = hdr.split(delim)
    print("num columns:", len(cols))
    for i,c in enumerate(cols):
        print(f"  [{i}] {c.strip().strip(chr(34))}")
    print("--- first data row (truncated) ---")
    if len(lines)>1:
        print(lines[1][:400])
