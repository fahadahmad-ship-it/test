import sys, csv, openpyxl
src, outdir = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    safe = name.strip().lower().replace(' ', '-').replace('.', '')
    path = f"{outdir}/reachgorilla-{safe}.csv"
    n = 0
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            cells = ['' if c is None else c for c in row]
            while cells and cells[-1] == '': cells.pop()
            if not cells: continue
            w.writerow(cells); n += 1
    print(f"{path}: {n-1} data rows")
