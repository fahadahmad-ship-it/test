import openpyxl
SAMPLE="/root/.claude/uploads/9d82c30c-07ae-5996-87a2-5bb7f1e78f3f/221c7568-NewGarden_Backlinks_Audit.xlsx"
MINE="/home/user/test/deliverables/Farison_Backlinks_Audit.xlsx"
s=openpyxl.load_workbook(SAMPLE); m=openpyxl.load_workbook(MINE)
print("TAB ORDER match:", s.sheetnames==m.sheetnames)
print(" sample:",s.sheetnames)
print(" mine  :",m.sheetnames)
print("\nHEADER ROW comparison per tab:")
for t in s.sheetnames:
    if t=="Summary": continue
    sh=[c.value for c in next(s[t].iter_rows(max_row=1))]
    mh=[c.value for c in next(m[t].iter_rows(max_row=1))]
    print(f"  [{t}] headers identical: {sh==mh}")
    if sh!=mh:
        print("    sample:",sh); print("    mine  :",mh)
print("\nSTYLING (mine vs AUDIT_FORMAT choice vs sample):")
def cell(wb,t,a): return wb[t][a]
for label,wb in [("sample",s),("mine",m)]:
    rda=wb['Referring Domain Audit']
    h=rda['A1']; d=rda['A2']; title=wb['Summary']['B1']
    print(f"  {label}: title B1 size={title.font.size} bold={title.font.bold} | header fill={h.fill.fgColor.rgb} font={h.font.name}/{h.font.size} white={h.font.color.rgb if h.font.color else None}")
    print(f"           data A2 border.left={d.border.left.style} | freeze={rda.freeze_panes} | gridlines={rda.sheet_view.showGridLines} | hdr.height={rda.row_dimensions[1].height}")
    print(f"           Summary gridlines={wb['Summary'].sheet_view.showGridLines} | logo on Summary={len(getattr(wb['Summary'],'_images',[]))}")
