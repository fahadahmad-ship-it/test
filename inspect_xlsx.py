import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
print("sheets:", wb.sheetnames)
for name in wb.sheetnames:
    ws = wb[name]
    print(f"\n--- {name}: {ws.max_row} rows x {ws.max_column} cols ---")
    for i, row in enumerate(ws.iter_rows(max_row=4, values_only=True)):
        print("  ", row)
        if i >= 3: break
