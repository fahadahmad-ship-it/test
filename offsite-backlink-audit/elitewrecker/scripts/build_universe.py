import csv, io, glob, os

base = "/home/user/test/offsite-backlink-audit/elitewrecker"

def read_semi(path, col):
    out=[]
    with io.open(path,"r",encoding="utf-8") as f:
        r=csv.reader(f,delimiter=";")
        hdr=next(r)
        ci=hdr.index(col)
        for row in r:
            if len(row)>ci and row[ci].strip(): out.append(row[ci].strip().lower())
    return out

# Semrush refdomains
sem=set()
for p in sorted(glob.glob(base+"/data/rd/semrush_refdomains_*.csv")):
    sem.update(read_semi(p,"domain"))

# Ahrefs refdomains (tab, UTF-8, quoted)
ah=set()
with io.open(base+"/data/ahrefs_refdomains.tsv","r",encoding="utf-8-sig") as f:
    r=csv.reader(f,delimiter="\t",quotechar='"')
    hdr=next(r); ci=hdr.index("Domain")
    for row in r:
        if len(row)>ci and row[ci].strip(): ah.add(row[ci].strip().lower())

union=sorted(sem|ah)
print("Semrush refdomains:",len(sem))
print("Ahrefs refdomains :",len(ah))
print("Overlap           :",len(sem&ah))
print("Semrush-only      :",len(sem-ah))
print("Ahrefs-only       :",len(ah-sem))
print("UNION (master)    :",len(union))

open(base+"/data/metrics/master_domains.txt","w").write("\n".join(union)+"\n")

# chunk files of 200 for domain_rank fan-out
os.makedirs(base+"/data/metrics/chunks",exist_ok=True)
CH=200
nch=0
for i in range(0,len(union),CH):
    nch+=1
    open(base+f"/data/metrics/chunks/chunk_{i:04d}.txt","w").write("\n".join(union[i:i+CH])+"\n")
print("chunks written:",nch,"of up to",CH,"domains each")
