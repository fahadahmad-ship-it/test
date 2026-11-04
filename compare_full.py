import openpyxl
BW="/home/user/test/BlackWalnut_Backlinks_Audit.xlsx"
KK="/root/.claude/uploads/00899f38-e3d1-54d4-a148-a694f2eb9402/5011db2c-KandK_Manufacturing_Backlinks_Audit.xlsx"
def bstyle(s): return s.style if s else None
def fdesc(c):
    f=c.font; a=c.alignment; b=c.border
    fill=c.fill.fgColor.rgb if (c.fill and c.fill.patternType) else None
    return (f.name,f.size,f.bold,(f.color.rgb if f.color else None),fill,a.horizontal,a.vertical,a.wrap_text,c.number_format,
            bstyle(b.left),bstyle(b.top),bstyle(b.right),bstyle(b.bottom))
bw=openpyxl.load_workbook(BW); kk=openpyxl.load_workbook(KK)
issues=0
for s in kk.sheetnames:
    wb_=bw[s]; wk=kk[s]
    cwb={k:round(v.width,2) for k,v in wb_.column_dimensions.items() if v.width}
    cwk={k:round(v.width,2) for k,v in wk.column_dimensions.items() if v.width}
    diffw={k:(cwb.get(k),cwk.get(k)) for k in set(cwb)|set(cwk) if cwb.get(k)!=cwk.get(k)}
    def rh(ws,r): return ws.row_dimensions[r].height
    hdr=fdesc(wb_['A1'])==fdesc(wk['A1'])
    d2=fdesc(wb_['A2'])==fdesc(wk['A2']) and fdesc(wb_['B2'])==fdesc(wk['B2'])
    # data row height: sample several rows
    bw_heights=set(rh(wb_,r) for r in range(2,min(wb_.max_row,0)+1)) if False else None
    import statistics
    bwh=[rh(wb_,r) for r in range(2, min(wb_.max_row,200)+1)]
    kkh=[rh(wk,r) for r in range(2, min(wk.max_row,200)+1)]
    from collections import Counter
    bwmode=Counter(bwh).most_common(1)[0] if bwh else None
    kkmode=Counter(kkh).most_common(1)[0] if kkh else None
    # check appended-row heights specifically
    tailprob=""
    if s in ("Exact Match Anchors","Pending Disavow Lines"):
        tail=[rh(wb_,r) for r in range(max(2,wb_.max_row-40), wb_.max_row+1)]
        tailprob=f" tail-heights set? {sorted(set(tail))}"
    status="OK"
    if diffw or not hdr or not d2 or bwmode!=kkmode: status="*** DIFF ***"; issues+=1
    print(f"{s}: {status}")
    if diffw: print("   colwidth:",diffw)
    if not hdr: print("   header A1 BW:",fdesc(wb_['A1']),"\n             KK:",fdesc(wk['A1']))
    if not d2:
        if fdesc(wb_['A2'])!=fdesc(wk['A2']): print("   A2 BW:",fdesc(wb_['A2']),"\n      KK:",fdesc(wk['A2']))
        if fdesc(wb_['B2'])!=fdesc(wk['B2']): print("   B2 BW:",fdesc(wb_['B2']),"\n      KK:",fdesc(wk['B2']))
    print(f"   data-row height mode BW{bwmode} KK{kkmode}{tailprob}")
print("\nSHEETS WITH DIFFS:",issues)
