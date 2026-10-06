import csv, sys
SHELLS=['ngawindows.com','roiwindows.com','thermalprowindows.com','qualitypluswindows.com',
'northpointwindows.com','performingwindows.com','thermatrustwindows.com','northgeorgiawindows.net',
'thermalastwindows.com','e2windows.com','choiceviewwindows.com','ngwindow.com','northgawindows.com',
'northgeorgiawindow.com']
bl=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig',newline=''),delimiter='\t'))
rd=list(csv.DictReader(open(sys.argv[2],encoding='utf-8-sig',newline=''),delimiter='\t'))

print("=== Do the 14 shells appear ANYWHERE in the Ahrefs corpus? ===")
hits={s:0 for s in SHELLS}
for r in bl:
    blob=' '.join(str(v or '') for v in r.values()).lower()
    for s in SHELLS:
        if s in blob: hits[s]+=1
for s,n in hits.items(): print(f"  {s:32} {n} rows")
print(f"  TOTAL rows mentioning any shell: {sum(hits.values())}")

print("\n=== Are any shells listed as REFERRING domains in Ahrefs? ===")
ah={(r.get('Domain') or '').lower() for r in rd}
for s in SHELLS:
    print(f"  {s:32} {'YES' if s in ah else 'no'}")

print("\n=== Semrush side: do shells appear as SOURCE domains (vs only in anchors)? ===")
import subprocess
raw=subprocess.run(['git','-C','/home/user/test','show','6f5f407:backlink-audit/work/links_raw.tsv'],
                   capture_output=True,text=True).stdout.splitlines()
src=anc=0
for line in raw:
    p=line.split('\t')
    if len(p)<2: continue
    if any(s in p[0].lower() for s in SHELLS): src+=1
    if any(s in p[1].lower() for s in SHELLS): anc+=1
print(f"  Semrush rows where a shell is the SOURCE domain: {src}")
print(f"  Semrush rows where a shell appears in the ANCHOR: {anc}")
