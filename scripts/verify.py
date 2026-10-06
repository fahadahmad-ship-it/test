import csv, sys, collections, re, json
P='/home/user/test/backlink-audit/data/ahrefs/ahrefs-backlinks.tsv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
print("rows",len(rows))
print(json.dumps(rows[0],indent=1)[:1500])
