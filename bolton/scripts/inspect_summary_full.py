import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=False)
ws = wb["Summary"]
print("=== Full text + number_format for key cells ===")
for coord in ["B1"]+[f"E{r}" for r in range(4,10)]+[f"A{r}" for r in range(12,19)]:
    c = ws[coord]
    print(f"\n--- {coord} (numfmt={c.number_format}) ---")
    print(repr(c.value))
print("\n=== number formats: status table B/C/D rows 4-10, anchor B/C/D rows 21-28 ===")
for r in list(range(3,11))+list(range(20,29)):
    fmts = {col: ws[f"{col}{r}"].number_format for col in "ABCD"}
    print(f"row {r}: {fmts}")
