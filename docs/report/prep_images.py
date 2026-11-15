# -*- coding: utf-8 -*-
"""把交付目录里的截图整理成报告用图：整页截图、拼版附录图。"""
import os

from PIL import Image

DELI = r"D:\大三上作业\数据实训\medicine-analysis\docs\交付"
OUT = r"D:\大三上作业\数据实训\medicine-analysis\docs\report\figs\deliver"
os.makedirs(OUT, exist_ok=True)

SHOT = os.path.join(DELI, "截图")
CHARTS = os.path.join(DELI, "12张图表")
JSOND = os.path.join(DELI, "json")


def path(*parts):
    return os.path.join(*parts)


def save(im, name):
    p = os.path.join(OUT, name)
    im.save(p, optimize=True)
    print("%-22s %s" % (name, im.size))


# ---------------------------------------------------------------- 整页截图
home = Image.open(path(SHOT, "01.png")).convert("RGB")
save(home, "p-home.png")

dis = Image.open(path(SHOT, "02.png")).convert("RGB")
save(dis, "p-disease.png")

drug = Image.open(path(SHOT, "03 (1).png")).convert("RGB")
save(drug, "p-drug.png")

screen = Image.open(path(SHOT, "05.png")).convert("RGB")
w, h = screen.size
screen.crop((0, 0, w, h - 62)).save(os.path.join(OUT, "p-screen.png"), optimize=True)
print("p-screen.png", screen.crop((0, 0, w, h - 62)).size)

kylin = Image.open(path(SHOT, "06.png")).convert("RGB")
save(kylin, "p-kylin.png")

start = Image.open(path(SHOT, "07.png")).convert("RGB")
save(start, "p-startall.png")

yarn = Image.open(path(SHOT, "09.png")).convert("RGB")
save(yarn, "p-yarn.png")

struct = Image.open(path(SHOT, "08.png")).convert("RGB")
save(struct, "p-structure.png")


# ---------------------------------------------------------------- 拼版
def trim(im, pad=6):
    """去掉截图四周的空白，便于拼版。"""
    g = im.convert("L")
    inv = g.point(lambda v: 255 if v < 246 else 0)
    bbox = inv.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad); t = max(0, t - pad)
    r = min(im.size[0], r + pad); b = min(im.size[1], b + pad)
    return im.crop((l, t, r, b))


def sheet(paths, cols, cell_w, gap=14, bg=(255, 255, 255), border=(214, 214, 214)):
    scaled = []
    for p in paths:
        im = trim(Image.open(p).convert("RGB"))
        w, h = im.size
        nh = int(round(h * cell_w / w))
        scaled.append(im.resize((cell_w, nh), Image.LANCZOS))
    # 逐列顺序排布，避免等高对齐留出大片空白
    per_col = (len(scaled) + cols - 1) // cols
    cols_imgs = [scaled[i * per_col:(i + 1) * per_col] for i in range(cols)]
    heights = [sum(i.size[1] for i in c) + gap * (len(c) + 1) for c in cols_imgs]
    W = cols * cell_w + (cols + 1) * gap
    H = max(heights)
    canvas = Image.new("RGB", (W, H), bg)
    for ci, imgs in enumerate(cols_imgs):
        x = gap + ci * (cell_w + gap)
        y = gap
        for im in imgs:
            canvas.paste(im, (x, y))
            y += im.size[1] + gap
    return canvas


chart_files = sorted(os.listdir(CHARTS))
chart_files = [f for f in chart_files if f.lower().endswith(".png")]
chart_paths = [os.path.join(CHARTS, f) for f in chart_files]
print("charts", len(chart_paths))
save(sheet(chart_paths, 2, 760), "s-charts.png")

json_names = ["%02d.png" % i for i in range(1, 13)]
json_paths = [os.path.join(JSOND, n) for n in json_names if os.path.exists(os.path.join(JSOND, n))]
print("json", len(json_paths))
save(sheet(json_paths, 2, 760, gap=12), "s-json.png")

ops_paths = [os.path.join(OUT, "p-yarn.png"), os.path.join(OUT, "p-structure.png")]
save(sheet(ops_paths, 1, 1500, gap=16), "s-ops.png")
