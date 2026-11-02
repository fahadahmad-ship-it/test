import sys
import openpyxl

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=False)
print("=== SHEETS (in order) ===")
for i, ws in enumerate(wb.worksheets):
    print(f"[{i}] {ws.title!r}  dims={ws.dimensions}  max_row={ws.max_row} max_col={ws.max_column}")
    print(f"     freeze={ws.freeze_panes} autofilter={ws.auto_filter.ref} gridlines={ws.sheet_view.showGridLines}")

def dump(ws, max_r, max_c, label):
    print(f"\n===== {label}: {ws.title} (first {max_r} rows x {max_c} cols) =====")
    for r in range(1, min(ws.max_row, max_r) + 1):
        cells = []
        for c in range(1, min(ws.max_column, max_c) + 1):
            v = ws.cell(row=r, column=c).value
            if v is not None:
                s = str(v).replace("\n", "\\n")
                if len(s) > 60:
                    s = s[:57] + "..."
                cells.append(f"{openpyxl.utils.get_column_letter(c)}{r}={s}")
        if cells:
            print("  " + " | ".join(cells))

# Full dump of Summary
summ = wb.worksheets[0]
dump(summ, 60, 10, "FULL SUMMARY")
print("\nMerged cells on Summary:", sorted(str(m) for m in summ.merged_cells.ranges))
