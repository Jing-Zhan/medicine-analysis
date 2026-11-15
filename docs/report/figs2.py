# -*- coding: utf-8 -*-
"""生成实训总结报告用的四张示意图，按印刷尺寸设计，输出到 docs/report/figs。"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

NAVY = RGBColor(0x1B, 0x3A, 0x5C)
TEAL = RGBColor(0x2E, 0x6F, 0x6A)
GOLD = RGBColor(0x9A, 0x76, 0x30)
SLATE = RGBColor(0x4E, 0x5A, 0x66)
INK = RGBColor(0x14, 0x1E, 0x28)
MUTED = RGBColor(0x5A, 0x66, 0x72)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figs_src")
OUT = os.path.join(HERE, "figs")
os.makedirs(SRC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)


def tint(color, f):
    return RGBColor(int(color[0] + (255 - color[0]) * f),
                    int(color[1] + (255 - color[1]) * f),
                    int(color[2] + (255 - color[2]) * f))


def bare(shp):
    sp = shp._element
    style = sp.find(qn("p:style"))
    if style is not None:
        sp.remove(style)
    return shp


def new_slide(w, h, name):
    prs = Presentation()
    prs.slide_width = Inches(w)
    prs.slide_height = Inches(h)
    prs.save  # noqa
    return prs, prs.slides.add_slide(prs.slide_layouts[6])


def box(s, x, y, w, h, fill, line=None, lw=0.75):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    bare(shp)
    return shp


def text(s, x, y, w, h, lines, anchor=MSO_ANCHOR.MIDDLE):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for item in lines:
        if isinstance(item, str):
            item = dict(text=item)
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = item.get("align", PP_ALIGN.CENTER)
        p.line_spacing = item.get("ls", 1.1)
        if item.get("space_before"):
            p.space_before = Pt(item["space_before"])
        r = p.add_run()
        r.text = item["text"]
        f = r.font
        f.name = "黑体"
        f.size = Pt(item.get("size", 9))
        f.bold = item.get("bold", False)
        f.color.rgb = item.get("color", INK)
    return tb


def arrow(s, x, y, w, h, color=MUTED, direction="right"):
    shp = s.shapes.add_shape({"right": MSO_SHAPE.RIGHT_ARROW, "down": MSO_SHAPE.DOWN_ARROW,
                              "up": MSO_SHAPE.UP_ARROW}[direction],
                             Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    bare(shp)
    return shp


def save(prs, name):
    prs.save(os.path.join(SRC, name + ".pptx"))
    print("saved", name)


# ------------------------------------------------------------------ 图一 总体架构
W1, H1 = 6.3, 3.55
prs, s = new_slide(W1, H1, "fig1")
rows = [
    ("应用层", 0.10, NAVY, [("Vue 三套页面", "12 张图表，83 端口"), ("Django 大屏", "5 张子图，8000 端口")]),
    ("服务层", 0.94, GOLD, [("SpringBoot 后端", "13 个数据接口，统一返回结构")]),
    ("存储层", 1.78, TEAL, [("MySQL 明细库", "6 表 9 索引"), ("Kylin 立方体", "8 维 2 度量"), ("7 张预聚合表", "固定口径")]),
    ("数据源", 2.62, SLATE, [("6 个原始文本文件", "约 240MB"), ("HDFS 与 Hive 外表", "6 张表，星型模型")]),
]
RH = 0.66
for label, y, c, items in rows:
    box(s, 0.05, y, 0.26, RH, c)
    text(s, 0.05, y, 0.26, RH, [dict(text=label, size=7.5, bold=True, color=WHITE, ls=1.0)])
    n = len(items)
    x0, avail = 0.37, W1 - 0.37 - 0.05
    gap = 0.08 if n > 1 else 0
    bw = (avail - gap * (n - 1)) / n
    for i, (t1, t2) in enumerate(items):
        x = x0 + i * (bw + gap)
        box(s, x, y, bw, RH, tint(c, 0.9), c, 1.0)
        text(s, x + 0.05, y + 0.03, bw - 0.1, RH - 0.06,
             [dict(text=t1, size=9.5, bold=True, color=c),
              dict(text=t2, size=7.5, color=INK, space_before=2)])
for x in (1.6, 4.7):
    arrow(s, x, 0.78, 0.14, 0.14, MUTED, "up")
for x in (1.6, 3.1, 4.7):
    arrow(s, x, 1.62, 0.14, 0.14, MUTED, "up")
arrow(s, 1.6, 2.46, 0.14, 0.14, MUTED, "up")
arrow(s, 3.9, 2.46, 0.14, 0.14, MUTED, "up")
save(prs, "fig1-arch")

# ------------------------------------------------------------------ 图二 六阶段流程
W2, H2 = 6.3, 2.45
prs, s = new_slide(W2, H2, "fig2")
stages = [("11-11", "环境搭建", "六个组件端口全通", GOLD),
          ("11-12", "数据入仓", "六张表一百万行", GOLD),
          ("11-13", "维度建模", "立方体状态 READY", TEAL),
          ("11-14", "接口开发", "13 个接口返回 200", NAVY),
          ("11-14", "前端与大屏", "12 图与 5 张子图", NAVY),
          ("11-15", "部署与验证", "17 条用例全部通过", SLATE)]
bw, bh, gap = 1.80, 0.78, 0.19
for i, (day, name, out, c) in enumerate(stages):
    col, row = i % 3, i // 3
    x = 0.12 + col * (bw + gap)
    y = 0.30 + row * 1.13
    box(s, x, y, bw, bh, tint(c, 0.9), c, 1.1)
    text(s, x + 0.06, y + 0.04, bw - 0.12, bh - 0.08,
         [dict(text=day + "　" + name, size=9, bold=True, color=c),
          dict(text=out, size=7.5, color=INK, space_before=3)])
    if col < 2:
        arrow(s, x + bw + 0.03, y + 0.31, gap - 0.06, 0.16, MUTED)
# 第一行末端折回第二行起点
box(s, 5.0 - 0.03, 0.30 + bh, 0.06, 0.12, MUTED)
box(s, 0.98, 0.30 + bh + 0.12, 5.02 - 0.98, 0.06, MUTED)
arrow(s, 0.88, 0.30 + bh + 0.18, 0.16, 0.14, MUTED, "down")
save(prs, "fig2-stage")

# ------------------------------------------------------------------ 图三 查询链路
W3, H3 = 6.3, 3.05
prs, s = new_slide(W3, H3, "fig3")
box(s, 0.05, 0.08, 2.75, 0.56, tint(NAVY, 0.9), NAVY, 1.1)
text(s, 0.1, 0.1, 2.65, 0.52,
     [dict(text="浏览器", size=9.5, bold=True, color=NAVY),
      dict(text="Vue 页面与大屏", size=7, color=INK, space_before=1)])
arrow(s, 2.86, 0.28, 0.2, 0.16, MUTED)
box(s, 3.12, 0.08, 2.6, 0.56, tint(NAVY, 0.9), NAVY, 1.1)
text(s, 3.17, 0.1, 2.5, 0.52,
     [dict(text="Controller", size=9.5, bold=True, color=NAVY),
      dict(text="13 个接口入口", size=7, color=INK, space_before=1)])
arrow(s, 4.32, 0.66, 0.16, 0.16, MUTED, "down")

box(s, 0.05, 0.86, 5.67, 0.46, tint(GOLD, 0.88), GOLD, 1.1)
text(s, 0.15, 0.88, 5.47, 0.42,
     [dict(text="查询网关：query.engine 决定走 kylin 还是 mysql，五条方言改写在此统一生效",
           size=8, bold=True, color=GOLD)])
arrow(s, 1.35, 1.36, 0.16, 0.16, MUTED, "down")
arrow(s, 4.2, 1.36, 0.16, 0.16, MUTED, "down")

box(s, 0.05, 1.56, 2.75, 0.52, tint(TEAL, 0.9), TEAL, 1.1)
text(s, 0.1, 1.58, 2.65, 0.48,
     [dict(text="Kylin 立方体　7070", size=9, bold=True, color=TEAL),
      dict(text="命中 256 个 cuboid", size=7, color=INK, space_before=1)])
box(s, 2.97, 1.56, 2.75, 0.52, tint(TEAL, 0.9), TEAL, 1.1)
text(s, 3.02, 1.58, 2.65, 0.48,
     [dict(text="MySQL 明细库　3306", size=9, bold=True, color=TEAL),
      dict(text="6 张表与 9 个索引", size=7, color=INK, space_before=1)])
arrow(s, 1.35, 2.12, 0.16, 0.16, MUTED, "down")
arrow(s, 4.2, 2.12, 0.16, 0.16, MUTED, "down")

box(s, 0.05, 2.32, 5.67, 0.52, tint(SLATE, 0.9), SLATE, 1.1)
text(s, 0.15, 2.34, 5.47, 0.48,
     [dict(text="统一返回结构　code、data、msg 三段", size=9, bold=True, color=SLATE),
      dict(text="字段名统一转成 Counter、Price、Amount、Name", size=7, color=INK, space_before=1)])
save(prs, "fig3-engine")

# ------------------------------------------------------------------ 图四 后续计划
W4, H4 = 6.3, 2.05
prs, s = new_slide(W4, H4, "fig4")
plan = [("现在", "六步只在我们五个人手里，换人接手要重新摸索一遍", SLATE),
        ("第一步", "写成流程清单，每步写清输入、产出与判断标准", GOLD),
        ("第二步", "把可判定的环节脚本化，建表、导入、核对、自检", GOLD),
        ("第三步", "做数据整理与可视化的 agent，接手探查、建模与校验", TEAL),
        ("验证", "换一份非医药行业的数据走一遍，看方法是否成立", NAVY)]
top = 0.12
for i, (tag, desc, c) in enumerate(plan):
    y = top + i * 0.38
    box(s, 0.05, y, 0.06, 0.3, c)
    text(s, 0.22, y, 0.95, 0.3, [dict(text=tag, size=9, bold=True, color=c, align=PP_ALIGN.LEFT)])
    text(s, 1.2, y, 5.0, 0.3, [dict(text=desc, size=8.5, color=INK, align=PP_ALIGN.LEFT)])
save(prs, "fig4-plan")
