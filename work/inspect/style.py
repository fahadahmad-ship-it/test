import sys, openpyxl
p = sys.argv[1]
wb = openpyxl.load_workbook(p)
def bs(side): return side.style if side else None
def desc_cell(ws, ref):
    c = ws[ref]
    f=c.font; fill=c.fill; al=c.alignment; b=c.border
    fillc = fill.fgColor.rgb if fill and fill.patternType else None
    print(f"  {ref}: val={str(c.value)[:28]!r} font={f.name},{f.size},bold={f.bold},color={f.color.rgb if f.color else None} fill={fillc} align=({al.horizontal},{al.vertical},wrap={al.wrap_text}) border=(L{bs(b.left)},R{bs(b.right)},T{bs(b.top)},B{bs(b.bottom)})")
for ws in wb.worksheets:
    print("="*60, ws.title)
    print("  widths:", {k:round(v.width,1) for k,v in list(ws.column_dimensions.items()) if v.width})
    print("  rowH sample:", {r:round(d.height,2) for r,d in list(ws.row_dimensions.items())[:4] if d.height}, "default:", ws.sheet_format.defaultRowHeight)
    for ref in ["A1","B1","A2","A3"]:
        try: desc_cell(ws, ref)
        except Exception as e: print("  ",ref,"err",e)
    for im in getattr(ws,'_images',[]):
        a=im.anchor; fr=a._from
        print(f"  IMAGE col={fr.col} colOff={fr.colOff} row={fr.row} rowOff={fr.rowOff} ext.cx={getattr(a.ext,'cx','?')} cy={getattr(a.ext,'cy','?')}")
# Summary detailed rows 3-28
ws=wb['Summary']
print("\n--- Summary full ---")
for r in range(1,29):
    row=[]
    for c in range(1,6):
        v=ws.cell(r,c).value
        if v is not None: row.append(f"{chr(64+c)}{r}={str(v)[:60]!r}")
    if row: print(" ", " | ".join(row))
