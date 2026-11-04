import openpyxl
S=openpyxl.load_workbook("/root/.claude/uploads/9d82c30c-07ae-5996-87a2-5bb7f1e78f3f/221c7568-NewGarden_Backlinks_Audit.xlsx")
M=openpyxl.load_workbook("/home/user/test/deliverables/Farison_Backlinks_Audit.xlsx")
def sig(c):
    f=c.font;b=c.border;a=c.alignment
    return (f.name,f.size,bool(f.bold),(f.color.rgb if f.color else None),
            (c.fill.fgColor.rgb if c.fill and c.fill.patternType else None),
            "".join(x[0] if getattr(b,x).style else "-" for x in ("left","right","top","bottom")),
            a.horizontal,a.vertical,bool(a.wrap_text),c.number_format)
diffs=[]
for t in S.sheetnames:
    s=S[t]; m=M[t]
    # widths
    sw={k:round(v.width,1) for k,v in s.column_dimensions.items() if v.width}
    mw={k:round(v.width,1) for k,v in m.column_dimensions.items() if v.width}
    if sw!=mw: diffs.append(f"[{t}] widths differ: sample={sw} mine={mw}")
    # default row height
    if s.sheet_format.defaultRowHeight!=m.sheet_format.defaultRowHeight:
        diffs.append(f"[{t}] defaultRowHeight sample={s.sheet_format.defaultRowHeight} mine={m.sheet_format.defaultRowHeight}")
    # header height
    if round((s.row_dimensions[1].height or 0),2)!=round((m.row_dimensions[1].height or 0),2):
        diffs.append(f"[{t}] row1 height sample={s.row_dimensions[1].height} mine={m.row_dimensions[1].height}")
    # gridlines/freeze
    if s.sheet_view.showGridLines!=m.sheet_view.showGridLines: diffs.append(f"[{t}] gridlines differ")
    if s.freeze_panes!=m.freeze_panes: diffs.append(f"[{t}] freeze sample={s.freeze_panes} mine={m.freeze_panes}")
    # header A1 + data A2 + a numeric cell
    if t!="Summary":
        for addr in ("A1","A2","C2","D2"):
            if sig(s[addr])!=sig(m[addr]):
                diffs.append(f"[{t}] {addr}: sample={sig(s[addr])} | mine={sig(m[addr])}")
# Summary specific cells
for addr in ("B1","A3","A4","D4"):
    if sig(S['Summary'][addr])!=sig(M['Summary'][addr]):
        diffs.append(f"[Summary] {addr}: sample={sig(S['Summary'][addr])} | mine={sig(M['Summary'][addr])}")
print("STYLE DIFFS:",len(diffs))
for d in diffs: print(" -",d)
