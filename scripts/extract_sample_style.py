import json, openpyxl
SAMPLE="/root/.claude/uploads/9d82c30c-07ae-5996-87a2-5bb7f1e78f3f/221c7568-NewGarden_Backlinks_Audit.xlsx"
wb=openpyxl.load_workbook(SAMPLE)
def st(c):
    f=c.font; b=c.border; a=c.alignment
    return dict(v=(str(c.value)[:22] if c.value is not None else None),
        font=f"{f.name}/{f.size}/b{f.bold}/{(f.color.rgb if f.color else None)}",
        fill=(c.fill.fgColor.rgb if c.fill and c.fill.patternType else None),
        bord="".join(s[0] if getattr(b,s).style else "-" for s in ("left","right","top","bottom")),
        al=f"{a.horizontal}/{a.vertical}/wrap{a.wrap_text}", numfmt=c.number_format)
out={}
for t in wb.sheetnames:
    ws=wb[t]
    widths={k:round(v.width,2) for k,v in ws.column_dimensions.items() if v.width}
    # explicit row heights for first 5 data rows + header
    rhs={k:v.height for k,v in ws.row_dimensions.items() if v.height}
    rhs_sample={k:rhs[k] for k in list(rhs)[:8]}
    info=dict(widths=widths, default_row_h=ws.sheet_format.defaultRowHeight,
              row_heights=rhs_sample, freeze=ws.freeze_panes, gridlines=ws.sheet_view.showGridLines,
              autofilter=ws.auto_filter.ref)
    # representative cells
    cells={}
    if t=="Summary":
        for a in ["B1","A3","B3","A4","D4","A12","A13","A21","B21","C22","A30"]:
            try: cells[a]=st(ws[a])
            except: pass
    else:
        hdr=next(ws.iter_rows(min_row=1,max_row=1))
        cells["A1"]=st(ws["A1"]); cells["A2"]=st(ws["A2"]); cells["C2"]=st(ws["C2"]); cells["D2"]=st(ws["D2"])
        if t=="Exact Match Anchors":
            cells["F2"]=st(ws["F2"]); cells["G2"]=st(ws["G2"])
        if t=="Disavow List":
            cells["B2"]=st(ws["B2"]); cells["C2"]=st(ws["C2"])  # AS, Backlinks numfmt
        if t=="Anchor Analysis":
            cells["C2"]=st(ws["C2"]); cells["D2"]=st(ws["D2"])  # backlinks, share numfmt
    info["cells"]=cells
    out[t]=info
print(json.dumps(out,indent=1,default=str))
