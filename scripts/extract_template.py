import sys, os, json
import openpyxl
from openpyxl.utils import get_column_letter

path = sys.argv[1]
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
wb = openpyxl.load_workbook(path)  # keep styles + images

def font_s(f):
    return dict(name=f.name, size=f.size, bold=f.bold, italic=f.italic,
                color=(f.color.rgb if f.color else None))
def fill_s(c):
    f = c.fill
    return dict(type=f.patternType, fg=(f.fgColor.rgb if f.fgColor else None))
def bord_s(c):
    b = c.border
    return {side: (getattr(b, side).style if getattr(b, side) else None)
            for side in ("left","right","top","bottom")}
def align_s(c):
    a = c.alignment
    return dict(h=a.horizontal, v=a.vertical, wrap=a.wrap_text)

report = {}
for ws in wb.worksheets:
    info = {}
    info["freeze_panes"] = ws.freeze_panes
    info["gridlines"] = ws.sheet_view.showGridLines
    info["auto_filter"] = ws.auto_filter.ref
    info["merged"] = [str(m) for m in ws.merged_cells.ranges][:10]
    info["max_row"] = ws.max_row
    info["max_col"] = ws.max_column
    # column widths
    widths = {}
    for col, dim in ws.column_dimensions.items():
        if dim.width:
            widths[col] = round(dim.width, 2)
    info["col_widths"] = widths
    # row heights (sample a few)
    rh = {}
    for r, dim in list(ws.row_dimensions.items())[:6]:
        if dim.height:
            rh[r] = dim.height
    info["row_heights_sample"] = rh
    info["row_dim_default"] = ws.sheet_format.defaultRowHeight
    # representative cells
    cells = {}
    for addr in ["A1","B1","A2","B2","A3","B3","A4"]:
        try:
            c = ws[addr]
        except Exception:
            continue
        if c.value is None and addr not in ("B1",):
            pass
        cells[addr] = dict(value=(str(c.value)[:30] if c.value is not None else None),
                           font=font_s(c.font), fill=fill_s(c),
                           border=bord_s(c), align=align_s(c))
    info["cells"] = cells
    # images
    imgs = []
    for img in getattr(ws, "_images", []):
        try:
            anchor = img.anchor
            a = {}
            if hasattr(anchor, "_from"):
                fr = anchor._from
                a = dict(col=fr.col, colOff=fr.colOff, row=fr.row, rowOff=fr.rowOff)
            ext = {}
            if hasattr(anchor, "ext") and anchor.ext is not None:
                ext = dict(cx=anchor.ext.width, cy=anchor.ext.height)
            # save image bytes
            data = img._data() if callable(getattr(img, "_data", None)) else None
            fn = os.path.join(outdir, f"{ws.title.replace(' ','_')}_img{len(imgs)}.png")
            if data:
                with open(fn, "wb") as fh:
                    fh.write(data)
            imgs.append(dict(anchor_from=a, ext=ext, saved=fn, size_bytes=(len(data) if data else 0)))
        except Exception as e:
            imgs.append(dict(error=str(e)))
    info["images"] = imgs
    report[ws.title] = info

print(json.dumps(report, indent=1, default=str))
