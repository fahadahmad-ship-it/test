import sys
import openpyxl

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=True)
print("SHEETS:", wb.sheetnames)
print("=" * 70)
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    print(f"\n### SHEET: {ws.title}  (rows={len(rows)}, cols={ws.max_column})")
    for i, r in enumerate(rows[:6]):
        cells = []
        for c in r:
            s = "" if c is None else str(c)
            if len(s) > 45:
                s = s[:42] + "..."
            cells.append(s)
        print(f"  r{i}:", cells)
