import zipfile, re
def facts(path):
    z=zipfile.ZipFile(path)
    names=z.namelist()
    styles=z.read("xl/styles.xml").decode("utf-8","ignore")
    fonts=set(re.findall(r'name val="([^"]+)"', styles))
    fills=set(re.findall(r'rgb="([0-9A-Fa-f]{8})"', styles))
    wbx=z.read("xl/workbook.xml").decode()
    sheets=re.findall(r'<sheet name="([^"]+)"',wbx)
    imgs=[n for n in names if n.startswith("xl/media/")]
    # summary merged cells
    import glob
    s1=z.read("xl/worksheets/sheet1.xml").decode()
    merges=re.findall(r'<mergeCell ref="([^"]+)"',s1)
    return dict(sheets=sheets, fonts=sorted(fonts), accent=("FF0C343D" in fills),
               media=imgs, summ_merges=sorted(merges))
t=facts("work/parkers/ref/KK_template.xlsx")
o=facts("work/parkers/out/parkersair_backlink_audit.xlsx")
print("SHEETS match:", t["sheets"]==o["sheets"], "\n  tmpl:",t["sheets"],"\n  out :",o["sheets"])
print("FONTS  tmpl:",t["fonts"])
print("FONTS  out :",o["fonts"])
print("Geist present both:", "Geist" in t["fonts"], "Geist" in o["fonts"], " | non-Geist fonts in out:",[f for f in o["fonts"] if f not in ("Geist","Calibri")])
print("Accent FF0C343D present both:", t["accent"], o["accent"])
print("Logo image present  tmpl:",t["media"]," out:",o["media"])
print("Summary merged cells match:", t["summ_merges"]==o["summ_merges"], "\n  tmpl:",t["summ_merges"],"\n  out :",o["summ_merges"])
