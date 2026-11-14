# -*- coding: utf-8 -*-
"""
生成汇报 PPT：目标适应症及用药数据分析系统

配色：学术报告常用的四组主色，按章分配，避免整本只有一种绿。
字号：标题 33 磅，正文 12 至 15 磅，图注 12 磅，表头 13 磅。
第 11 至 21、23、24 页嵌入服务器实拍图，图注写明图号、内容与来源。
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from PIL import Image

INK = RGBColor(0x14, 0x1E, 0x28)
INK2 = RGBColor(0x39, 0x45, 0x50)
MUTED = RGBColor(0x63, 0x70, 0x7B)
PAPER = RGBColor(0xFB, 0xFA, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xDE, 0xD9, 0xCE)
LINE2 = RGBColor(0xC9, 0xC2, 0xB2)

NAVY = RGBColor(0x1B, 0x3A, 0x5C)
OXBLOOD = RGBColor(0x7A, 0x2E, 0x2E)
TEAL = RGBColor(0x2E, 0x6F, 0x6A)
GOLD = RGBColor(0x9A, 0x76, 0x30)
STEEL = RGBColor(0x4A, 0x6F, 0xA5)
SLATE = RGBColor(0x4E, 0x5A, 0x66)

FONT = "微软雅黑"
MONO = "Consolas"

W, H = 13.333, 7.5
LEFT = 0.62
CW = 12.09
BODY = 1.98
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def tint(color, f):
    return RGBColor(int(color[0] + (255 - color[0]) * f),
                    int(color[1] + (255 - color[1]) * f),
                    int(color[2] + (255 - color[2]) * f))


def new_slide(bg=PAPER):
    s = prs.slides.add_slide(BLANK)
    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    box.fill.solid()
    box.fill.fore_color.rgb = bg
    box.line.fill.background()
    box.shadow.inherit = False
    return s


def _flat(sp):
    st = sp._element.find(qn("p:style"))
    if st is not None:
        sp._element.remove(st)
    sp.shadow.inherit = False


def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, dash=False):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(lw)
        if dash:
            sp.line.dash_style = MSO_LINE.DASH
    _flat(sp)
    sp.text_frame.word_wrap = True
    return sp


def txt(s, x, y, w, h, blocks, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for b in blocks:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = b.get("align", PP_ALIGN.LEFT)
        p.line_spacing = b.get("ls", 1.16)
        if b.get("space_before"):
            p.space_before = Pt(b["space_before"])
        if b.get("space_after"):
            p.space_after = Pt(b["space_after"])
        runs = b["text"] if isinstance(b["text"], list) else [(b["text"], b.get("color", INK))]
        for text, color in runs:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(b.get("size", 15))
            r.font.bold = b.get("bold", False)
            r.font.color.rgb = color
            r.font.name = b.get("font", FONT)
    return tb


def header(s, accent, chapter, no, title, lead=None):
    rect(s, LEFT, 0.36, 0.12, 0.24, fill=accent)
    txt(s, LEFT + 0.26, 0.31, 6.6, 0.32, [dict(text=chapter, size=14, bold=True, color=accent)])
    txt(s, W - 2.4, 0.1, 1.75, 0.9,
        [dict(text=no, size=52, bold=True, color=tint(accent, 0.82), align=PP_ALIGN.RIGHT)])
    txt(s, LEFT, 0.68, CW - 2.0, 0.7, [dict(text=title, size=32, bold=True, color=INK)])
    if lead:
        txt(s, LEFT, 1.42, CW - 0.6, 0.42, [dict(text=lead, size=18, color=MUTED)])
    rect(s, LEFT, 1.84, CW, 0.035, fill=accent)
    rect(s, LEFT, 1.885, CW, 0.012, fill=LINE2)


def footer(s, accent, page):
    txt(s, LEFT, 6.99, 8.0, 0.28, [dict(text="目标适应症及用药数据分析系统", size=10.5, color=MUTED)])
    txt(s, W - LEFT - 1.2, 6.99, 1.2, 0.28,
        [dict(text=str(page).zfill(2), size=11, bold=True, color=accent, align=PP_ALIGN.RIGHT)])


def card(s, x, y, w, h, accent, title=None, fill=WHITE, title_size=15):
    rect(s, x, y, w, h, fill=fill, line=LINE, lw=0.9)
    rect(s, x, y, w, 0.055, fill=accent)
    if title:
        txt(s, x + 0.26, y + 0.18, w - 0.5, 0.34,
            [dict(text=title, size=title_size, bold=True, color=accent)])


def figure(s, x, y, w, h, name, no, caption, source=None, accent=NAVY):
    path = os.path.join(FIG_DIR, name)
    iw, ih = Image.open(path).size
    ratio = iw * 1.0 / ih
    pad = 0.08
    box_w, box_h = w - pad * 2, h - pad * 2
    if box_w / box_h > ratio:
        dh = box_h
        dw = dh * ratio
    else:
        dw = box_w
        dh = dw / ratio
    rect(s, x, y, w, h, fill=WHITE, line=LINE2, lw=0.9)
    s.shapes.add_picture(path, Inches(x + (w - dw) / 2), Inches(y + (h - dh) / 2),
                         Inches(dw), Inches(dh))
    cap_h = 0.64 if source else 0.4
    cy = y + h + 0.06
    rect(s, x, cy, w, cap_h, fill=tint(accent, 0.9))
    txt(s, x + 0.16, cy + 0.08, w - 0.3, 0.26,
        [dict(text=[("图 %d　" % no, accent), (caption, INK2)], size=11.5)])
    if source:
        txt(s, x + 0.16, cy + 0.35, w - 0.3, 0.24, [dict(text=source, size=10, color=MUTED)])
    return cy + cap_h


def make_table(s, x, y, w, ratios, rows, font=13, head_font=13, row_h=0.42, head_h=0.44,
               aligns=None, accent=NAVY, bold_col=None):
    nrow, ncol = len(rows), len(ratios)
    total = head_h + row_h * (nrow - 1)
    gt = s.shapes.add_table(nrow, ncol, Inches(x), Inches(y), Inches(w), Inches(total))
    tbl = gt.table
    tbl.first_row = True
    tbl.horz_banding = False
    for i, r in enumerate(ratios):
        tbl.columns[i].width = Inches(w * r)
    tbl.rows[0].height = Inches(head_h)
    for i in range(1, nrow):
        tbl.rows[i].height = Inches(row_h)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = accent
            else:
                cell.fill.fore_color.rgb = WHITE if ri % 2 == 1 else tint(accent, 0.94)
            p = cell.text_frame.paragraphs[0]
            if aligns:
                p.alignment = aligns[ci]
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT
            r.font.size = Pt(head_font if ri == 0 else font)
            if ri == 0:
                r.font.bold = True
                r.font.color.rgb = WHITE
            else:
                is_b = bold_col is not None and ci == bold_col
                r.font.bold = is_b
                r.font.color.rgb = INK if is_b else INK2
    return total


def chip(s, x, y, w, h, label, value, accent):
    rect(s, x, y, w, h, fill=WHITE, line=LINE, lw=0.9)
    rect(s, x, y, 0.075, h, fill=accent)
    txt(s, x + 0.3, y + 0.14, w - 0.5, 0.3, [dict(text=label, size=12, bold=True, color=accent)])
    txt(s, x + 0.3, y + 0.48, w - 0.5, 0.44, [dict(text=value, size=15, bold=True, color=INK)])


def problem_page(page, accent, title, lead, problem, steps, effects):
    s = new_slide()
    header(s, accent, "02　项目设计", "02", title, lead)
    rect(s, LEFT, BODY, CW, 1.08, fill=tint(accent, 0.92), line=tint(accent, 0.55), lw=0.9)
    rect(s, LEFT, BODY, 0.08, 1.08, fill=accent)
    txt(s, LEFT + 0.32, BODY + 0.13, 1.7, 0.3, [dict(text="问题表现", size=12.5, bold=True, color=accent)])
    txt(s, LEFT + 2.0, BODY + 0.13, CW - 2.35, 0.86,
        [dict(text=problem, size=14, color=INK2, ls=1.26)])
    txt(s, LEFT, 3.24, 5.4, 0.34, [dict(text="我们的做法", size=17, bold=True, color=INK)])
    sy = 3.66
    for i, (name, desc) in enumerate(steps):
        rect(s, LEFT, sy, 0.46, 0.46, fill=accent, shape=MSO_SHAPE.OVAL)
        txt(s, LEFT, sy + 0.09, 0.46, 0.3,
            [dict(text=str(i + 1), size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)])
        txt(s, LEFT + 0.64, sy + 0.01, 6.0, 0.32, [dict(text=name, size=15.5, bold=True, color=INK)])
        txt(s, LEFT + 0.64, sy + 0.36, 6.0, 0.36, [dict(text=desc, size=12.5, color=MUTED, ls=1.2)])
        sy += 0.79
    txt(s, 7.4, 3.24, 5.3, 0.34, [dict(text="做出来的效果", size=17, bold=True, color=INK)])
    ey = 3.66
    for v, label in effects:
        rect(s, 7.4, ey, 5.31, 0.79, fill=WHITE, line=tint(accent, 0.55), lw=0.9)
        txt(s, 7.62, ey + 0.1, 2.5, 0.44, [dict(text=v, size=18.5, bold=True, color=accent)])
        txt(s, 10.1, ey + 0.14, 2.45, 0.56, [dict(text=label, size=11.5, color=INK2, ls=1.2)])
        ey += 0.79
    footer(s, accent, page)
    return s


# ================================================================ 01 封面
s = new_slide(NAVY)
rect(s, 0, 0, W, H, fill=NAVY)
rect(s, 0, 5.05, W, 2.45, fill=tint(NAVY, 0.12))
txt(s, LEFT, 0.92, CW, 0.36, [dict(text="大数据实训项目汇报", size=17, color=tint(NAVY, 0.62))])
txt(s, LEFT, 1.4, CW, 1.0, [dict(text="目标适应症及用药数据分析系统", size=44, bold=True, color=WHITE)])
rect(s, LEFT, 2.52, 2.4, 0.06, fill=GOLD)
txt(s, LEFT, 2.8, CW, 0.46,
    [dict(text="六张业务表　13 个查询接口　三套分析页面", size=19, color=tint(NAVY, 0.7))])
cards3 = [("100 万行", "处方与用药明细"), ("13 个", "查询接口"), ("12 张", "分析图表")]
cw3 = (CW - 0.6) / 3
for i, (v, lab) in enumerate(cards3):
    x = LEFT + i * (cw3 + 0.3)
    rect(s, x, 3.54, cw3, 1.24, fill=tint(NAVY, 0.16), line=tint(NAVY, 0.34), lw=1.0)
    txt(s, x + 0.28, 3.68, cw3 - 0.4, 0.58, [dict(text=v, size=29, bold=True, color=WHITE)])
    txt(s, x + 0.28, 4.3, cw3 - 0.4, 0.32, [dict(text=lab, size=14.5, color=tint(NAVY, 0.66))])
txt(s, LEFT, 5.44, CW, 0.4, [dict(text="第二小组", size=18, bold=True, color=WHITE)])
txt(s, LEFT, 5.88, CW, 0.4,
    [dict(text="占竞　　李艺淼　　付悌安　　杨博文　　洪嘉伟", size=18, color=tint(NAVY, 0.62))])
txt(s, LEFT, 6.52, CW, 0.34,
    [dict(text="服务器 192.168.207.179　　主站 83　　大屏 8000　　Kylin 7070", size=13.5, color=tint(NAVY, 0.5))])

# ================================================================ 02 目录
s = new_slide()
header(s, NAVY, "目录", "00", "汇报内容与页码")
toc = [("01", "项目背景", "为什么做、总体思路、数据基础", "03", NAVY),
       ("02", "项目设计", "三个问题的设计、页面与接口、任务对照", "06", OXBLOOD),
       ("03", "项目结果", "系统输出、三页实证、结构对比、数据校验", "11", TEAL),
       ("04", "实施过程与方法", "六个阶段、部署方式、启动日志", "17", GOLD),
       ("05", "技术原理与架构", "数据流向、Kylin 与 Cube、引擎切换", "22", STEEL),
       ("06", "组织与管理", "人员分工与五天进度", "25", SLATE),
       ("07", "总结", "完成情况与后续计划", "26", NAVY)]
y = 2.02
for num, name, desc, pg, color in toc:
    rect(s, LEFT, y, CW, 0.66, fill=WHITE, line=LINE, lw=0.8)
    rect(s, LEFT, y, 0.085, 0.66, fill=color)
    txt(s, LEFT + 0.26, y + 0.1, 0.9, 0.44, [dict(text=num, size=23, bold=True, color=color)])
    txt(s, LEFT + 1.28, y + 0.05, 3.6, 0.34, [dict(text=name, size=18.5, bold=True, color=INK)])
    txt(s, LEFT + 1.28, y + 0.38, 8.6, 0.26, [dict(text=desc, size=12.5, color=MUTED)])
    txt(s, LEFT + CW - 1.4, y + 0.19, 1.1, 0.3,
        [dict(text="P" + pg, size=13.5, bold=True, color=color, align=PP_ALIGN.RIGHT)])
    y += 0.7
footer(s, NAVY, 2)

# ================================================================ 03 为什么做
s = new_slide()
header(s, NAVY, "01　项目背景", "01", "为什么做这个项目",
       "六张业务表、一百万行明细，日常分析要回答四类问题")
txt(s, LEFT, BODY, 6.0, 0.32, [dict(text="业务上要回答的四类问题", size=16, bold=True, color=NAVY)])
qs = [("哪些病用药最多", "按疾病看处方量与费用"),
      ("哪些药覆盖最广", "按药品看覆盖的医院与城市"),
      ("谁在用什么药", "按科室、年龄看用药分布"),
      ("用得是否合理", "三项用药占比是否偏高")]
qy = BODY + 0.42
for k, v in qs:
    rect(s, LEFT, qy, 6.0, 0.8, fill=WHITE, line=LINE, lw=0.8)
    rect(s, LEFT, qy, 0.07, 0.8, fill=NAVY)
    txt(s, LEFT + 0.26, qy + 0.24, 2.6, 0.34, [dict(text=k, size=15, bold=True, color=NAVY)])
    txt(s, LEFT + 2.95, qy + 0.22, 2.85, 0.42, [dict(text=v, size=12.5, color=MUTED, ls=1.18)])
    qy += 0.88
txt(s, 6.95, BODY, 5.76, 0.32, [dict(text="现在的工作方式", size=16, bold=True, color=OXBLOOD)])
flow = ["打开数据库，手工写多表关联 SQL", "等十几秒拿到结果，复制到 Excel", "换一个维度，SQL 重写一遍"]
fy = BODY + 0.42
for i, t in enumerate(flow):
    rect(s, 6.95, fy, 5.76, 0.5, fill=tint(OXBLOOD, 0.92), line=LINE, lw=0.7)
    txt(s, 7.15, fy + 0.12, 0.4, 0.3, [dict(text=str(i + 1), size=13, bold=True, color=OXBLOOD)])
    txt(s, 7.62, fy + 0.11, 5.0, 0.32, [dict(text=t, size=12.5, color=INK2)])
    fy += 0.56
diffs = [("关联多", "一条分析要连三到六张表"),
         ("字段脏", "回车符把同一科室拆成两项"),
         ("响应慢", "百万行关联一次十几秒")]
for k, v in diffs:
    rect(s, 6.95, fy, 5.76, 0.62, fill=WHITE, line=LINE, lw=0.7)
    rect(s, 6.95, fy, 0.07, 0.62, fill=OXBLOOD)
    txt(s, 7.15, fy + 0.17, 1.0, 0.3, [dict(text=k, size=13.5, bold=True, color=OXBLOOD)])
    txt(s, 8.22, fy + 0.16, 4.35, 0.34, [dict(text=v, size=12.5, color=MUTED)])
    fy += 0.66
rect(s, LEFT, 6.1, CW, 0.7, fill=NAVY)
txt(s, LEFT + 0.32, 6.24, CW - 0.6, 0.42,
    [dict(text="项目要做的：把这些重复劳动固化成 13 个固定接口和三套页面", size=14.5, bold=True, color=WHITE)])
footer(s, NAVY, 3)

# ================================================================ 04 总体思路
s = new_slide()
header(s, NAVY, "01　项目背景", "01", "总体解决思路", "三个困难对应三项设计，最终落到三套页面上")
rows = [["遇到的困难", "我们的做法", "达到的效果"],
        ["关联多，SQL 难写", "按四种组合分组统计，写成四张汇总表，接口直接查表", "最慢 15.26 秒"],
        ["字段脏，口径不一", "六张维表建视图去回车，占比公式只写在服务层", "同一指标同一个数"],
        ["响应慢，页面点不动", "取值少的字段预计算，取值多的字段建索引", "首页 0.61 秒"]]
th = make_table(s, LEFT, BODY, CW, [0.22, 0.56, 0.22], rows, font=13.5, head_font=13.5,
                row_h=0.9, head_h=0.5, accent=NAVY,
                aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])
txt(s, LEFT, BODY + th + 0.34, CW, 0.34, [dict(text="数据从表到页面经过四步", size=16, bold=True, color=NAVY)])
chain = [("明细表", "六张业务表，100 万行"), ("汇总表", "七张聚合表，10 万级"),
         ("接口", "13 个查询接口"), ("页面", "三套页面，12 张图")]
cw4 = (CW - 0.9) / 4
cy = BODY + th + 0.8
for i, (name, desc) in enumerate(chain):
    x = LEFT + i * (cw4 + 0.3)
    rect(s, x, cy, cw4, 1.1, fill=NAVY if i % 2 == 0 else STEEL)
    txt(s, x + 0.16, cy + 0.13, cw4 - 0.3, 0.34, [dict(text=name, size=16.5, bold=True, color=WHITE)])
    txt(s, x + 0.16, cy + 0.54, cw4 - 0.3, 0.48,
        [dict(text=desc, size=11.5, color=tint(NAVY, 0.72), ls=1.2)])
    if i < 3:
        txt(s, x + cw4 + 0.02, cy + 0.38, 0.26, 0.32,
            [dict(text="→", size=18, bold=True, color=MUTED, align=PP_ALIGN.CENTER)])
footer(s, NAVY, 4)

# ================================================================ 05 数据基础与目标
s = new_slide()
header(s, NAVY, "01　项目背景", "01", "数据基础与项目目标", "先确认手上有什么数据，再把目标写成可校验的数字")
rows = [["表名", "内容", "规模"],
        ["prescription_diseases", "处方与用药明细", "1000000 行"],
        ["t_view_disease", "疾病三级分类", "42501 条"],
        ["t_view_drug", "药品属性", "205971 种"],
        ["t_view_hospital", "医院与城市", "全国范围"],
        ["t_view_section", "科室", "20 类"]]
th = make_table(s, LEFT, BODY, 6.6, [0.42, 0.3, 0.28], rows, font=12, head_font=12,
                row_h=0.46, head_h=0.46, accent=NAVY)
chip(s, LEFT, BODY + th + 0.24, 6.6, 1.12, "数据范围",
     "单月 200812，年龄 40 至 89 岁，男女接近 1 比 1", NAVY)
txt(s, 7.5, BODY, 5.2, 0.32, [dict(text="四条目标", size=16, bold=True, color=NAVY)])
goals = [("分析视角", "5 类"), ("查询接口", "13 个"),
         ("响应时间", "2 秒与 20 秒"), ("部署方式", "一条命令")]
gy = BODY + 0.42
for k, v in goals:
    rect(s, 7.5, gy, 5.21, 0.84, fill=WHITE, line=LINE, lw=0.8)
    rect(s, 7.5, gy, 0.07, 0.84, fill=NAVY)
    txt(s, 7.75, gy + 0.26, 2.2, 0.36, [dict(text=k, size=13.5, color=MUTED)])
    txt(s, 9.85, gy + 0.18, 2.65, 0.5, [dict(text=v, size=20, bold=True, color=NAVY, align=PP_ALIGN.RIGHT)])
    gy += 0.92
rect(s, 7.5, gy + 0.04, 5.21, 0.9, fill=tint(NAVY, 0.9), line=tint(NAVY, 0.55), lw=0.9)
txt(s, 7.75, gy + 0.18, 4.8, 0.66,
    [dict(text="验收依据：接口全部返回 200、页面取真实接口、11 项基准值可复核",
          size=12, color=NAVY, ls=1.22)])
footer(s, NAVY, 5)

# ================================================================ 06 问题一
problem_page(
    6, OXBLOOD, "问题一与设计：六表关联改为查汇总表",
    "一条关于某类疾病用了哪些药的分析要连三张表",
    "疾病与药品分在两张维表里，处方明细只存编码。要得到某类疾病用了哪些药、各多少，"
    "必须把明细表、疾病表、药品表关联起来再分组，一条 SQL 十几行，漏一个条件结果就偏。",
    [("先定下常用组合", "统计需求集中在四类：疾病、药品、疾病与药品、处方与药品"),
     ("按组合建汇总表", "每张表只存编码、名称、数量三列，主键唯一，避免重复计数"),
     ("接口改成查汇总表", "先取编码与数量，再与维表关联补名称，不再扫明细表"),
     ("新需求同样方式扩展", "科室结构对比也是先建 agg_section_drug，接口只查结果")],
    [("4 张汇总表", "覆盖 13 个接口中的 8 个"), ("15.26 秒", "最慢接口，此前需数十秒"),
     ("99 万行", "最大汇总表，最小 4 万行")],
)

# ================================================================ 07 问题二
problem_page(
    7, OXBLOOD, "问题二与设计：统一维表与统计口径",
    "同一指标两个人算出两个数，根源在脏数据和算法不统一",
    "维表文本字段带回车符，同一科室被拆成两项；药品表有列错位，剂型值出现在厂商列；"
    "同一个人在不同页面把分母取错，占比就算错。",
    [("六张维表建视图", "每张维表建一个 t_view_ 视图，字段去回车、去空格后再对外提供"),
     ("文本字段限长", "汇总表文本列统一截到 255 位，否则主键建不上，导入直接报错"),
     ("比率算法只写一处", "分子分母都按处方数加权，写在 Service 层，各页面调同一个方法"),
     ("缺失值统一处理", "名称缺失填未标注或未分类，并且不参与 Top 榜排序")],
    [("一处算法", "三套页面同一指标同一段代码"), ("9 个索引", "建在清洗后的视图字段上"),
     ("两类脏数据", "回字符与列错位已在视图层处理")],
)

# ================================================================ 08 问题三
problem_page(
    8, OXBLOOD, "问题三与设计：预计算加索引",
    "百万行关联一次十几秒，还要避免页面上出现假数据",
    "跨表关联一次要十几秒，页面点开是白屏。前端原来设 8 秒超时，把还在计算的请求当成失败，"
    "结果页面上一半是真数据一半是假数据。",
    [("取值少的字段预计算", "年龄、性别、年月等维度取值 2 到 431 种，预计算成 256 个组合"),
     ("取值多的字段建索引", "医院、科室、药品有上千上万种取值，改在 MySQL 建 9 个索引"),
     ("前端超时与失败处理", "超时放宽到 60 秒；接口报错时显示错误，不再用假数据顶替"),
     ("一个配置项切换引擎", "query.engine 在 kylin 与 mysql 之间切换，业务代码不改")],
    [("0.61 秒", "首页概览接口实测"), ("15.26 秒", "最慢的跨表关联接口"),
     ("13 个", "接口全部返回 200")],
)

# ================================================================ 09 页面与接口
s = new_slide()
header(s, OXBLOOD, "02　项目设计", "02", "页面、图表与接口的对应关系",
       "每个页面回答什么问题，背后调哪个接口")
rows = [["分析对象", "页面", "页面上的图表", "接口", "数据来源"],
        ["适应症", "适应症页", "关联药品、科室分布、年龄分布、费用负担", "/disease/ 5 个", "agg_disease_total"],
        ["药品", "药品页", "覆盖城市、覆盖医院、适应症、科室、结构对比", "/drug/ 5 个", "agg_drug_total"],
        ["机构", "首页", "省份、城市等级、年龄分布、药品前十", "/home/ 4 个", "明细表与维表"],
        ["汇总", "独立大屏", "省份地图、药品前十、病症前十、关系图", "Django 5 个", "同一份 MySQL"]]
th = make_table(s, LEFT, BODY, CW, [0.11, 0.12, 0.38, 0.19, 0.2], rows, font=12, head_font=12.5,
                row_h=0.74, head_h=0.46, accent=OXBLOOD)
card(s, LEFT, BODY + th + 0.28, CW, 1.46, OXBLOOD, "设计上的三点考虑")
pts = ["一个页面只回答一组问题，图表按分析对象分组，避免把十几种图堆在一起",
       "接口按对象分前缀，前端按页面路径取数，新增分析只需加一个接口和一个组件",
       "页面顶部保留关键词搜索框，输入疾病或药品名即可切换分析目标"]
py = BODY + th + 0.72
for t in pts:
    txt(s, LEFT + 0.3, py, CW - 0.6, 0.32, [dict(text="· " + t, size=12.5, color=INK2)])
    py += 0.32
footer(s, OXBLOOD, 9)

# ================================================================ 10 任务对照
s = new_slide()
header(s, OXBLOOD, "02　项目设计", "02", "与课程实训任务的对照",
       "任务资料要求 20 个分析任务，逐条对照实现方式与所用技术")
rows = [["课程任务", "要求的做法", "我们的实现", "状态"],
        ["任务12 至 15　城市等级、年龄、销额、省份", "后端 Kylin，前端 Vue", "首页四张图，四个接口", "已实现"],
        ["任务16 至 19　用药组合、年龄、科室分布", "同上", "适应症页四张图，四个接口", "已实现"],
        ["任务20 至 23　覆盖城市、适应症、医院、科室", "同上", "药品页四张图，四个接口", "已实现"],
        ["任务24　药品关联规则分析", "Pandas 与 Apriori", "规则文件接入大屏，编码待统一", "部分实现"],
        ["任务25 至 31　Django 大屏与五张图", "Django 与 ECharts", "大屏五个取数接口", "已实现"]]
th = make_table(s, LEFT, BODY, CW, [0.36, 0.22, 0.34, 0.08], rows, font=12, head_font=12.5,
                row_h=0.66, head_h=0.46, accent=OXBLOOD)
txt(s, LEFT, BODY + th + 0.26, 5.2, 0.32, [dict(text="三处我们自己加的设计", size=15, bold=True, color=OXBLOOD)])
inn = [("双通道路由", "取值少的走 Cube，取值多的走索引"),
       ("七张汇总表", "把百万行明细压成可复用的中间结果"),
       ("科室结构对比", "唯一横向比较结构的一张表")]
iw = (CW - 0.4) / 3
iy = BODY + th + 0.64
for i, (k, v) in enumerate(inn):
    x = LEFT + i * (iw + 0.2)
    rect(s, x, iy, iw, 0.94, fill=tint(OXBLOOD, 0.93), line=tint(OXBLOOD, 0.58), lw=0.9)
    txt(s, x + 0.24, iy + 0.12, iw - 0.44, 0.3, [dict(text=k, size=13.5, bold=True, color=OXBLOOD)])
    txt(s, x + 0.24, iy + 0.48, iw - 0.44, 0.42, [dict(text=v, size=11.5, color=INK2, ls=1.2)])
footer(s, OXBLOOD, 10)

# ================================================================ 11 系统输出总览
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "系统输出总览",
       "四块界面全部取真实接口数据，图为服务器运行时的实际截图")
cells = [("fig-home.png", "首页：城市等级、年龄结构、药品销额", "192.168.207.179:83/#/home"),
         ("fig-disease.png", "适应症页：用药组合树与联合用药环", "192.168.207.179:83/#/disease"),
         ("fig-drug-bottom.png", "药品页：覆盖医院与科室分布", "192.168.207.179:83/#/drug"),
         ("fig-dashboard.png", "独立大屏：省份地图与分配指标", "192.168.207.179:8000")]
gw = (CW - 0.4) / 2
for i, (name, cap, src) in enumerate(cells):
    x = LEFT + (i % 2) * (gw + 0.4)
    y = BODY - 0.06 + (i // 2) * 2.42
    figure(s, x, y, gw, 1.9, name, i + 1, cap, None, accent=TEAL)
txt(s, LEFT, 6.72, CW, 0.24,
    [dict(text="图 1 至图 4 采集自 192.168.207.179 的 83 端口与 8000 端口，采集时间 2026-11-14",
          size=10.5, color=MUTED)])
footer(s, TEAL, 11)

# ================================================================ 12 首页
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "首页：四个总量指标加四张分布图",
       "城市等级按销售金额排序，四级到一级递减")
figure(s, LEFT, BODY - 0.08, 7.55, 4.2, "fig-home.png", 5,
       "首页四张分布图，数值取真实接口", "2026-11-14 17:01 采集，192.168.207.179:83", accent=TEAL)
kpis = [("100 万行", "处方与用药明细"), ("13 个", "查询接口，全部 200"),
        ("0.61 秒", "/home/overview 实测"), ("15.26 秒", "最慢接口 /disease/union")]
ky = BODY - 0.08
for v, lab in kpis:
    rect(s, 8.4, ky, 4.31, 0.94, fill=WHITE, line=LINE, lw=0.9)
    rect(s, 8.4, ky, 0.075, 0.94, fill=TEAL)
    txt(s, 8.66, ky + 0.12, 3.9, 0.42, [dict(text=v, size=20, bold=True, color=TEAL)])
    txt(s, 8.66, ky + 0.56, 3.9, 0.3, [dict(text=lab, size=11.5, color=MUTED)])
    ky += 1.06
rect(s, 8.4, 6.26, 4.31, 0.6, fill=tint(TEAL, 0.9), line=tint(TEAL, 0.55), lw=0.9)
txt(s, 8.6, 6.35, 3.9, 0.44,
    [dict(text="四级城市 837.8 万元，一级城市 364.5 万元", size=11, color=INK2, ls=1.16)])
footer(s, TEAL, 12)

# ================================================================ 13 适应症页
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "适应症页：某类疾病用了什么药、花多少钱",
       "页面下方是费用负担表，数据来自 /disease/burden")
figure(s, LEFT, BODY - 0.08, 6.75, 2.6, "fig-burden.png", 6,
       "费用负担表：前十个疾病大类与占比列", "采集自 192.168.207.179:83/#/disease", accent=TEAL)
txt(s, LEFT, 5.02, 6.75, 0.32, [dict(text="表里能看出的情况", size=14, bold=True, color=TEAL)])
rect(s, LEFT, 5.4, 6.75, 1.46, fill=tint(TEAL, 0.92), line=tint(TEAL, 0.55), lw=0.9)
txt(s, LEFT + 0.28, 5.54, 6.2, 1.2,
    [dict(text="均次费用集中在 26 元附近，排名主要由处方数决定，费用指标区分度低。"
               "因此把重点从费用转到注射剂、基本药物、抗菌药物三项占比。",
          size=12.5, color=INK2, ls=1.3)])
txt(s, 7.6, BODY - 0.08, 5.11, 0.32, [dict(text="费用负担前五，按总金额排序", size=14, bold=True, color=TEAL)])
rows = [["疾病大类", "处方数", "总金额", "均次"],
        ["腺瘤和腺癌", "5,942", "156,850.62", "26.40"],
        ["其他器官的结核", "5,478", "148,405.26", "27.09"],
        ["孕产妇并发其他疾病", "4,676", "122,397.39", "26.18"],
        ["动态未定或未知的肿瘤", "4,482", "118,627.17", "26.47"],
        ["操作并发症", "3,372", "88,463.92", "26.23"]]
th = make_table(s, 7.6, BODY + 0.28, 5.11, [0.4, 0.19, 0.25, 0.16], rows, font=11.5, head_font=11.5,
                row_h=0.4, head_h=0.4, accent=TEAL,
                aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
by = BODY + 0.28 + th + 0.2
card(s, 7.6, by, 5.11, 1.54, TEAL, "这三个数怎么算出来的", title_size=13.5)
for i, c in enumerate(["处方数　该大类下全部处方记录的条数",
                       "总金额　各条记录金额求和后保留两位",
                       "均次费用　总金额除以处方数"]):
    txt(s, 7.84, by + 0.6 + i * 0.29, 4.7, 0.28, [dict(text=c, size=11.5, color=INK2)])
footer(s, TEAL, 13)

# ================================================================ 14 药品页
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "药品页：新增科室用药结构对比",
       "这一页与另外两页的区别在于，它按科室分组横向比较三项占比")
figure(s, LEFT, BODY - 0.08, 7.35, 2.92, "fig-drug-top.png", 7,
       "药品页上半部分：覆盖城市与对应适应症", "采集自 192.168.207.179:83/#/drug", accent=TEAL)
card(s, 8.2, BODY - 0.08, 4.51, 2.92, TEAL, "下半部分：科室用药结构对比", title_size=13.5)
calcs = [("注射剂占比", "剂型含注射的处方数除以该科室处方数"),
         ("基本药物占比", "基本药物标记为是的处方数除以该科室处方数"),
         ("抗菌药物占比", "通用名含抗菌关键词的处方数除以该科室处方数")]
cy = BODY + 0.52
for k, v in calcs:
    rect(s, 8.42, cy, 4.07, 0.66, fill=tint(TEAL, 0.94))
    txt(s, 8.58, cy + 0.07, 3.8, 0.26, [dict(text=k, size=11, bold=True, color=TEAL)])
    txt(s, 8.58, cy + 0.33, 3.8, 0.3, [dict(text=v, size=10.5, color=INK2)])
    cy += 0.72
txt(s, 8.42, cy + 0.02, 4.0, 0.3, [dict(text="取处方数前 10 个科室，同表并列", size=10.5, color=MUTED)])
rect(s, LEFT, 5.14, CW, 1.64, fill=tint(TEAL, 0.9), line=tint(TEAL, 0.5), lw=0.9)
rect(s, LEFT, 5.14, 0.08, 1.64, fill=TEAL)
txt(s, LEFT + 0.32, 5.28, CW - 0.6, 0.32,
    [dict(text="为什么单独留出位置", size=14, bold=True, color=TEAL)])
txt(s, LEFT + 0.32, 5.68, CW - 0.6, 1.0,
    [dict(text="三套页面里只有这张表把科室当作分组维度横向比较结构，能直接看出哪个科室的注射剂、"
               "基本药物与抗菌药物使用比例偏离整体水平。下一张是它的实际运行结果。",
          size=12.5, color=INK2, ls=1.28)])
footer(s, TEAL, 14)

# ================================================================ 15 结构对比实测
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "科室用药结构对比的运行结果",
       "建表用时 1 分 18 秒，两张表共 186.8 万行")
figure(s, LEFT, BODY - 0.08, 7.15, 2.36, "fig-structure.png", 8,
       "建表命令与五个科室的三项占比输出", "服务器终端实录，2026-11-14", accent=TEAL)
txt(s, 8.0, BODY - 0.08, 4.71, 0.32, [dict(text="前五个科室的实测占比", size=14, bold=True, color=TEAL)])
rows = [["科室", "处方数", "注射剂", "基本药物", "抗菌药"],
        ["外科", "96,988", "21.85", "20.55", "15.02"],
        ["急诊医学科", "86,969", "21.93", "20.61", "15.10"],
        ["其他", "82,651", "21.72", "20.27", "14.98"],
        ["内科", "77,972", "21.88", "20.43", "15.22"],
        ["肿瘤科", "74,895", "22.09", "20.52", "15.26"]]
make_table(s, 8.0, BODY + 0.28, 4.71, [0.24, 0.2, 0.18, 0.2, 0.18], rows, font=10.5, head_font=10.5,
           row_h=0.38, head_h=0.38, accent=TEAL,
           aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * 4)
card(s, LEFT, 4.9, CW, 1.9, TEAL, "这组数据说明了什么", title_size=15)
finds = ["五个科室的注射剂占比在 21.72 到 22.09 之间，跨度 0.37 个百分点；另两项同样在 0.4 个百分点以内",
         "说明这份数据的科室用药结构高度接近，该表的价值在于监测异常：某科室一旦偏离就能被发现",
         "原来设想的科室之间差异明显并不成立，因此页面只如实呈现占比，不把它渲染成对比结论"]
fy2 = 5.36
for t in finds:
    txt(s, LEFT + 0.32, fy2, CW - 0.65, 0.42, [dict(text="· " + t, size=12, color=INK2, ls=1.22)])
    fy2 += 0.46
footer(s, TEAL, 15)

# ================================================================ 16 数据校验
s = new_slide()
header(s, TEAL, "03　项目结果", "03", "数据一致性校验", "总额出现差额时算出差多少、差在哪")
boxes = [("事实表直接求和", "26,239,620.54", "元　一百万行明细"),
         ("关联维表后求和", "26,207,933.86", "元　内连接丢失部分记录"),
         ("差额与原因", "31,686.68", "元　1,164 行医院编号为空")]
bw = (CW - 0.3) / 3
for i, (k, v, u) in enumerate(boxes):
    x = LEFT + i * (bw + 0.15)
    acc = TEAL if i < 2 else GOLD
    rect(s, x, BODY, bw, 1.5, fill=WHITE, line=LINE, lw=0.9)
    rect(s, x, BODY, bw, 0.055, fill=acc)
    txt(s, x + 0.26, BODY + 0.18, bw - 0.4, 0.3, [dict(text=k, size=12.5, bold=True, color=acc)])
    txt(s, x + 0.26, BODY + 0.52, bw - 0.4, 0.5, [dict(text=v, size=24, bold=True, color=INK)])
    txt(s, x + 0.26, BODY + 1.1, bw - 0.4, 0.3, [dict(text=u, size=11.5, color=MUTED)])
txt(s, LEFT, 3.9, 6.0, 0.32, [dict(text="七张表的行数，取自 06.txt", size=14, bold=True, color=TEAL)])
rows = [["表名", "行数"], ["prescription_diseases", "1,000,000"], ["agg_disease_total", "42,501"],
        ["agg_drug_total", "205,971"], ["agg_disease_drug", "999,935"]]
make_table(s, LEFT, 4.3, 6.0, [0.62, 0.38], rows, font=12, head_font=12, row_h=0.4, head_h=0.4,
           accent=TEAL, aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
rows2 = [["表名", "行数"], ["agg_pres_drug", "999,999"], ["agg_section_drug", "870,702"],
         ["agg_cat_drug", "997,681"], ["自定义索引", "9 个"]]
make_table(s, 6.72, 4.3, 5.99, [0.62, 0.38], rows2, font=12, head_font=12, row_h=0.4, head_h=0.4,
           accent=TEAL, aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
rect(s, LEFT, 6.08, CW, 0.72, fill=tint(TEAL, 0.9), line=tint(TEAL, 0.5), lw=0.9)
txt(s, LEFT + 0.3, 6.18, CW - 0.6, 0.54,
    [dict(text="校验口径：行数、年龄分布、性别比、索引数、HDFS 目录数写成基准值文档，dump_baseline.py 可重复导出比对",
          size=11.5, color=INK2, ls=1.18)])
footer(s, TEAL, 16)

# ================================================================ 17 实施流程
s = new_slide()
header(s, GOLD, "04　实施过程与方法", "04", "实施流程与阶段产物", "六个阶段，每个阶段有明确产物")
stages = [("一", "环境搭建", "六个组件端口全通"), ("二", "数据入仓", "六张表 100 万行"),
          ("三", "维度建模", "bi_cube READY"), ("四", "接口开发", "13 个接口 200"),
          ("五", "前端联调", "12 张图表真数"), ("六", "部署验收", "基准值与自检")]
n = len(stages)
step = CW / n
rect(s, LEFT + 0.3, 2.66, CW - 0.6, 0.035, fill=LINE2)
for i, (num, name, out) in enumerate(stages):
    cx = LEFT + step * i + step / 2
    rect(s, cx - 0.34, 2.38, 0.68, 0.62, fill=GOLD if i % 2 == 0 else OXBLOOD, shape=MSO_SHAPE.OVAL)
    txt(s, cx - 0.34, 2.5, 0.68, 0.36,
        [dict(text=num, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)])
    txt(s, cx - step / 2 + 0.1, 3.16, step - 0.2, 0.34,
        [dict(text=name, size=16.5, bold=True, color=INK, align=PP_ALIGN.CENTER)])
    txt(s, cx - step / 2 + 0.1, 3.56, step - 0.2, 0.6,
        [dict(text=out, size=12, color=MUTED, align=PP_ALIGN.CENTER, ls=1.2)])
txt(s, LEFT, 4.38, CW, 0.32, [dict(text="实施中遇到的三个实际情况与处理方式", size=16, bold=True, color=GOLD)])
issues = [("数据入仓", "维度表文本带回车符，分组出现重复项", "清洗时统一去回车，重建视图"),
          ("维度建模", "单表 Cube 答不了跨表关联的 12 个接口", "高基数关联改走 MySQL，建 9 个索引"),
          ("接口联调", "重新编译后新接口仍返回 404", "脚本比对 jar 与进程时间，自动重启")]
iy = 4.82
for k, prob, fix in issues:
    rect(s, LEFT, iy, CW, 0.66, fill=WHITE, line=LINE, lw=0.8)
    rect(s, LEFT, iy, 0.07, 0.66, fill=GOLD)
    txt(s, LEFT + 0.28, iy + 0.18, 1.4, 0.32, [dict(text=k, size=12.5, bold=True, color=GOLD)])
    txt(s, LEFT + 1.8, iy + 0.17, 5.0, 0.34, [dict(text=prob, size=12, color=MUTED)])
    txt(s, LEFT + 6.95, iy + 0.17, 4.9, 0.34, [dict(text=fix, size=12, color=INK2)])
    iy += 0.72
footer(s, GOLD, 17)

# ================================================================ 18 阶段一二
s = new_slide()
header(s, GOLD, "04　实施过程与方法", "04", "阶段一二：环境搭建与数据入仓",
       "集群与数据库分别用脚本拉起，端口逐个校验")
rect(s, LEFT, BODY, 6.0, 3.24, fill=NAVY)
txt(s, LEFT + 0.3, BODY + 0.18, 5.4, 0.28,
    [dict(text="实际操作命令", size=10.5, color=tint(NAVY, 0.6), font=MONO)])
cmd = ["bash /opt/start-cluster.sh", "ss -lnt | grep -E '2181|9000|8088'", "",
       "hdfs dfs -ls /bi_data/mysql", "mysql -uroot -p yiyao -e \\",
       "  'SELECT COUNT(*) FROM prescription_diseases;'"]
cy = BODY + 0.56
for line in cmd:
    if line:
        txt(s, LEFT + 0.3, cy, 5.5, 0.3, [dict(text=line, size=11.5, color=tint(NAVY, 0.8), font=MONO)])
    cy += 0.36
txt(s, LEFT, 5.46, 6.0, 0.32, [dict(text="两个数据处理细节", size=14, bold=True, color=GOLD)])
chips2 = [("回车符", "分组时同一名称被拆成两项，清洗时统一去掉"),
          ("后缀列", "生成列 drug_code 与业务列 drug 并存，关联用后者")]
cx2 = LEFT
for k, v in chips2:
    rect(s, cx2, 5.84, 2.95, 1.04, fill=WHITE, line=LINE, lw=0.8)
    rect(s, cx2, 5.84, 0.07, 1.04, fill=GOLD)
    txt(s, cx2 + 0.24, 5.94, 2.6, 0.28, [dict(text=k, size=12, bold=True, color=GOLD)])
    txt(s, cx2 + 0.24, 6.24, 2.6, 0.56, [dict(text=v, size=11, color=MUTED, ls=1.18)])
    cx2 += 3.05
txt(s, 6.95, BODY, 5.76, 0.32, [dict(text="九个端口逐项校验", size=14, bold=True, color=GOLD)])
checks = [("2181", "ZooKeeper"), ("9000", "HDFS"), ("8088", "YARN"), ("16010", "HBase"),
          ("9083", "Hive"), ("7070", "Kylin"), ("3306", "MySQL"), ("83", "接口"), ("8000", "大屏")]
for i, (port, name) in enumerate(checks):
    x = 6.95 + (i % 3) * 1.92
    y = BODY + 0.4 + (i // 3) * 0.62
    rect(s, x, y, 1.86, 0.52, fill=WHITE, line=LINE, lw=0.7)
    txt(s, x + 0.16, y + 0.12, 0.78, 0.3, [dict(text=port, size=12.5, bold=True, color=GOLD, font=MONO)])
    txt(s, x + 0.92, y + 0.14, 0.88, 0.26, [dict(text=name, size=10.5, color=MUTED)])
txt(s, 6.95, 4.54, 5.76, 0.32, [dict(text="数据规模", size=14, bold=True, color=GOLD)])
rows = [["数据项", "数量"], ["处方与用药明细", "1,000,000 行"], ["疾病维度", "42,501 个"],
        ["药品维度", "205,971 种"], ["HDFS 数据目录", "6 个"]]
make_table(s, 6.95, 4.92, 5.76, [0.6, 0.4], rows, font=12, head_font=12,
           row_h=0.4, head_h=0.4, accent=GOLD, aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
footer(s, GOLD, 18)

# ================================================================ 19 阶段三四
s = new_slide()
header(s, GOLD, "04　实施过程与方法", "04", "阶段三四：维度建模与接口开发",
       "Cube 负责取值少的字段聚合，接口整理成前端可用的结构")
txt(s, LEFT, BODY, 5.9, 0.32, [dict(text="bi_cube 实测参数", size=14, bold=True, color=GOLD)])
rows = [["项目", "实测值"], ["Kylin 项目", "yiyao"], ["Cube 名称", "bi_cube"],
        ["构建状态", "READY"], ["源记录数", "1,000,000"], ["Cuboid 数量", "256"],
        ["Cube 体积", "2.95 GB"], ["构建耗时", "23.13 分钟"]]
th = make_table(s, LEFT, BODY + 0.34, 5.9, [0.44, 0.56], rows, font=12, head_font=12,
                row_h=0.4, head_h=0.42, accent=GOLD, aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT])
rect(s, LEFT, BODY + 0.34 + th + 0.2, 5.9, 0.9, fill=tint(GOLD, 0.9), line=tint(GOLD, 0.55), lw=0.9)
txt(s, LEFT + 0.26, BODY + 0.48 + th + 0.2, 5.4, 0.64,
    [dict(text="维度取年龄、性别、年月、医院、科室、职称、支付方式、数据类型八列",
          size=11, color=INK2, ls=1.2)])
txt(s, 6.85, BODY, 5.86, 0.32, [dict(text="13 个接口实测耗时", size=14, bold=True, color=GOLD)])
rows2 = [["接口", "秒", "接口", "秒"],
         ["/home/overview", "0.61", "/disease/age", "7.20"],
         ["/home/citylevel", "2.12", "/disease/section", "9.34"],
         ["/home/age", "2.19", "/drug/cities", "5.20"],
         ["/home/top10", "5.84", "/drug/hospital", "7.67"],
         ["/home/province", "1.99", "/drug/diseases", "14.67"],
         ["/disease/union", "15.26", "/drug/section", "12.98"],
         ["/disease/drug", "15.17", "", ""]]
make_table(s, 6.85, BODY + 0.34, 5.86, [0.34, 0.16, 0.34, 0.16], rows2, font=11, head_font=11,
           row_h=0.38, head_h=0.38, accent=GOLD,
           aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
rect(s, 6.85, 5.6, 5.86, 0.9, fill=tint(GOLD, 0.9), line=tint(GOLD, 0.55), lw=0.9)
txt(s, 7.09, 5.7, 5.5, 0.3, [dict(text="验收口径", size=12, bold=True, color=GOLD)])
txt(s, 7.09, 6.0, 5.5, 0.42,
    [dict(text="单表不超过 2 秒，多表关联不超过 20 秒，13 个接口全部满足", size=11.5, color=INK2)])
footer(s, GOLD, 19)

# ================================================================ 20 部署方式
s = new_slide()
header(s, GOLD, "04　实施过程与方法", "04", "部署方式：目录结构与启动自检",
       "脚本放在 /opt 下，可反复执行，不会重复拉起进程")
txt(s, LEFT, BODY, 5.9, 0.32, [dict(text="服务器目录结构", size=14, bold=True, color=GOLD)])
tree = [("/home/medicine-analysis", "项目根目录"), ("├ backend/yiyao", "服务源码与 jar"),
        ("├ frontend", "Vue 源码与构建产物"), ("├ screen", "Django 大屏"),
        ("├ deploy/sql", "建表与聚合脚本"), ("└ deploy/scripts", "启停与状态自检")]
ty0 = BODY + 0.38
for i, (path, desc) in enumerate(tree):
    yy = ty0 + i * 0.4
    rect(s, LEFT, yy - 0.03, 5.9, 0.38, fill=WHITE if i % 2 else tint(GOLD, 0.94))
    txt(s, LEFT + 0.14, yy + 0.02, 3.0, 0.3, [dict(text=path, size=11.5, bold=True, color=INK, font=MONO)])
    txt(s, LEFT + 3.3, yy + 0.05, 2.45, 0.26, [dict(text=desc, size=10.5, color=MUTED)])
card(s, LEFT, ty0 + 2.52, 5.9, 1.6, GOLD, "六个组件与两个应用", title_size=13.5)
txt(s, LEFT + 0.28, ty0 + 2.96, 5.35, 1.1,
    [dict(text="ZooKeeper 2181、HDFS 9000、YARN 8088、HBase 16010、Hive 9083、Kylin 7070",
          size=10.5, color=INK2, ls=1.3),
     dict(text="后端 83 与 Django 大屏 8000，由同一个脚本检测后拉起", size=10.5, color=INK2, ls=1.3)])
txt(s, 6.85, BODY, 5.86, 0.32, [dict(text="脚本执行的三个动作", size=14, bold=True, color=GOLD)])
steps3 = [("检测", "六个集群端口与 MySQL 逐个探测，已在跑的直接跳过"),
          ("拉起", "后端以 nohup 启动，轮询 /home/overview 直到 200"),
          ("自检", "13 个接口逐个请求，打印状态码与耗时，失败标红")]
sy = BODY + 0.38
for i, (k, v) in enumerate(steps3):
    rect(s, 6.85, sy, 5.86, 0.9, fill=WHITE, line=LINE, lw=0.8)
    rect(s, 6.85, sy, 0.07, 0.9, fill=GOLD)
    txt(s, 7.12, sy + 0.13, 1.0, 0.26, [dict(text="步骤" + "一二三"[i], size=10, bold=True, color=MUTED)])
    txt(s, 7.12, sy + 0.4, 1.2, 0.34, [dict(text=k, size=15, bold=True, color=INK)])
    txt(s, 8.4, sy + 0.26, 4.15, 0.56, [dict(text=v, size=11, color=MUTED, ls=1.2)])
    sy += 0.98
rect(s, 6.85, 5.34, 5.86, 1.4, fill=tint(OXBLOOD, 0.93), line=tint(OXBLOOD, 0.55), lw=0.9)
txt(s, 7.09, 5.44, 5.4, 0.3, [dict(text="处理过的一次端口占用问题", size=12, bold=True, color=OXBLOOD)])
txt(s, 7.09, 5.76, 5.4, 0.9,
    [dict(text="重新编译后 83 端口仍在监听，脚本判定无需启动，新接口返回 404。现在比对 jar 与进程的修改时间，"
               "jar 更新就自动重启。", size=11, color=INK2, ls=1.24)])
footer(s, GOLD, 20)

# ================================================================ 21 启动日志
s = new_slide()
header(s, GOLD, "04　实施过程与方法", "04", "一键启动的实际输出",
       "五阶段自检全部通过，13 个接口逐个打印状态码与耗时")
figure(s, LEFT, BODY - 0.08, 4.65, 3.98, "fig-startall.png", 9,
       "start-all.sh 五阶段输出与 13 个接口耗时", "服务器终端实录，2026-11-14", accent=GOLD)
txt(s, 5.6, BODY - 0.08, 7.11, 0.32, [dict(text="这份输出能逐项核对", size=15, bold=True, color=GOLD)])
pts2 = [("阶段一", "六个组件端口全部在监听，逐个打印 2181 到 7070"),
        ("阶段二", "MySQL 3306 在监听，处方表读到 1000000 行"),
        ("阶段三", "后端 /home/overview 与前端页面都返回 200"),
        ("阶段四", "Django 大屏取数正常，健康检查 db 为 true"),
        ("阶段五", "13 个接口逐个计时，最慢 /disease/union 15.26 秒")]
py2 = BODY + 0.24
for k, v in pts2:
    rect(s, 5.6, py2, 7.11, 0.62, fill=WHITE, line=LINE, lw=0.8)
    rect(s, 5.6, py2, 0.07, 0.62, fill=GOLD)
    txt(s, 5.84, py2 + 0.16, 1.1, 0.28, [dict(text=k, size=11.5, bold=True, color=GOLD)])
    txt(s, 7.05, py2 + 0.15, 5.45, 0.38, [dict(text=v, size=11.5, color=INK2)])
    py2 += 0.7
rect(s, 5.6, 5.86, 7.11, 0.8, fill=tint(GOLD, 0.9), line=tint(GOLD, 0.55), lw=0.9)
txt(s, 5.84, 5.95, 6.7, 0.26, [dict(text="脚本末尾同时打印五个访问入口", size=10.5, bold=True, color=GOLD)])
txt(s, 5.84, 6.22, 6.7, 0.4,
    [dict(text="主站 83、大屏 8000、Kylin 7070、YARN 8088、HDFS 50070、HBase 16010",
          size=10, color=INK2, ls=1.18)])
footer(s, GOLD, 21)

# ================================================================ 22 数据流向
s = new_slide()
header(s, STEEL, "05　技术原理与架构", "05", "数据流向：从表到页面经过六步",
       "每一步都标了真实数据量与耗时")
nodes = [("MySQL 业务表", ["六张表", "100 万行"]), ("HDFS 与 Hive", ["bi_data/mysql", "6 个目录"]),
         ("Kylin 预计算", ["256 个 cuboid", "2.95 GB"]), ("agg 汇总表", ["七张表", "9 个索引"]),
         ("13 个接口", ["0.61 至 15.26 秒", "全部 200"]), ("三套页面", ["12 张图表", "83 与 8000"])]
nw = (CW - 5 * 0.26) / 6
for i, (name, rs) in enumerate(nodes):
    x = LEFT + i * (nw + 0.26)
    rect(s, x, BODY, nw, 1.44, fill=STEEL if i % 2 == 0 else NAVY)
    txt(s, x + 0.12, BODY + 0.14, nw - 0.24, 0.44, [dict(text=name, size=12, bold=True, color=WHITE, ls=1.1)])
    txt(s, x + 0.12, BODY + 0.68, nw - 0.24, 0.7,
        [dict(text=r, size=10.5, color=tint(STEEL, 0.74), ls=1.24) for r in rs])
    if i < 5:
        txt(s, x + nw + 0.01, BODY + 0.56, 0.24, 0.3,
            [dict(text="→", size=14, bold=True, color=MUTED, align=PP_ALIGN.CENTER)])
txt(s, LEFT, 3.66, CW, 0.32, [dict(text="接口取数的两条路径", size=15, bold=True, color=STEEL)])
paths = [("路径一　命中 Cube", "5 个接口", "取值少的维度直接组合，不查明细表", "0.61 到 2.19 秒"),
         ("路径二　转 MySQL", "8 个接口", "先查汇总表，再走索引关联维表取名称", "5.20 到 15.26 秒")]
pw = (CW - 0.3) / 2
for i, (name, cnt, desc, cost) in enumerate(paths):
    x = LEFT + i * (pw + 0.3)
    acc = STEEL if i == 0 else NAVY
    rect(s, x, 4.06, pw, 1.14, fill=WHITE, line=tint(acc, 0.5), lw=1.0)
    rect(s, x, 4.06, 0.08, 1.14, fill=acc)
    txt(s, x + 0.32, 4.16, 3.2, 0.32, [dict(text=name, size=13.5, bold=True, color=acc)])
    txt(s, x + 3.1, 4.14, 1.8, 0.34, [dict(text=cnt, size=13.5, bold=True, color=INK, align=PP_ALIGN.RIGHT)])
    txt(s, x + 0.32, 4.54, pw - 0.62, 0.34, [dict(text=desc, size=11.5, color=INK2)])
    txt(s, x + 0.32, 4.9, pw - 0.62, 0.28, [dict(text="实测 " + cost, size=10.5, color=MUTED)])
card(s, LEFT, 5.44, CW, 1.32, STEEL, "页面怎么拿到这些数", title_size=13.5)
facts = ["接口统一包一层 code 与 data，前端按 data 取数，失败时给出错误提示",
         "字段名统一转成首字母大写下发，十二张图共用一套取数写法",
         "图表只做渲染，取数写在组件的 load 方法；前端超时 60 秒"]
fy3 = 5.87
for t in facts:
    txt(s, LEFT + 0.3, fy3, CW - 0.6, 0.3, [dict(text="· " + t, size=11.5, color=INK2)])
    fy3 += 0.3
footer(s, STEEL, 22)

# ================================================================ 23 Kylin
s = new_slide()
header(s, STEEL, "05　技术原理与架构", "05", "Kylin 建模与 Cube 构建",
       "八列维度、两个度量，Cube 建成后页面聚合直接读它")
figure(s, LEFT, BODY - 0.08, 7.35, 3.86, "fig-kylin.png", 10,
       "Kylin 的 bi_cube 列表：READY、2.95 GB、源记录 100 万", "Kylin 控制台截图，2026-11-12", accent=STEEL)
rows = [["项目", "取值"], ["项目名", "yiyao"], ["Cube", "bi_cube"], ["状态", "READY"],
        ["创建时间", "11-12 02:49"], ["完成时间", "11-12 03:14"], ["体积", "2.95 GB"],
        ["源记录", "1,000,000"], ["Cuboid", "256"]]
make_table(s, 8.2, BODY - 0.08, 4.51, [0.4, 0.6], rows, font=11, head_font=11,
           row_h=0.38, head_h=0.38, accent=STEEL, aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT])
rect(s, 8.2, 4.96, 4.51, 1.62, fill=tint(STEEL, 0.9), line=tint(STEEL, 0.5), lw=0.9)
txt(s, 8.44, 5.08, 4.05, 0.3, [dict(text="为什么只放八列", size=12.5, bold=True, color=STEEL)])
txt(s, 8.44, 5.42, 4.05, 1.08,
    [dict(text="维度每加一列，cuboid 翻倍。八列已是 256 个组合，构建二十多分钟；医院与科室基数上千，"
               "进 Cube 后构建时间不可接受，因此改走 MySQL 索引。",
          size=11, color=INK2, ls=1.26)])
footer(s, STEEL, 23)

# ================================================================ 24 引擎切换
s = new_slide()
header(s, STEEL, "05　技术原理与架构", "05", "查询引擎切换与接口返回",
       "业务 SQL 只维护一份，改写规则集中在网关")
figure(s, LEFT, BODY - 0.08, 6.95, 2.06, "fig-json.png", 11,
       "/home/province 的原始返回：code 200 与各省数值", "浏览器直接访问接口，2026-11-14", accent=STEEL)
txt(s, 7.8, BODY - 0.08, 4.91, 0.32, [dict(text="改写规则五条", size=14, bold=True, color=STEEL)])
rows = [["原写法", "改写后"], ["BIGDATA.PRESCRIPTION_DISEASES", "prescription_diseases"],
        ["M_DIAGNOSTIC", "m_diagnostic1"], ["PRESCRIPTION_DISEASES.AGE", "m_age"],
        ["M_DRUG = DRUG.DRUG", "DRUG_CODE = DRUG.DRUG"], ["VARCHAR", "CHAR"]]
make_table(s, 7.8, BODY + 0.28, 4.91, [0.56, 0.44], rows, font=9, head_font=9.5,
           row_h=0.36, head_h=0.36, accent=STEEL)
rect(s, LEFT, 4.34, CW, 1.0, fill=WHITE, line=LINE, lw=0.9)
rect(s, LEFT, 4.34, 0.07, 1.0, fill=STEEL)
txt(s, LEFT + 0.3, 4.44, 4.7, 0.3,
    [dict(text="query.engine = kylin | mysql", size=13, bold=True, color=STEEL, font=MONO)])
txt(s, 5.6, 4.46, 6.3, 0.78,
    [dict(text="切换时业务代码不改；实测 13 个接口中 5 个由 Cube 直接回答，8 个转 MySQL 索引关联。",
          size=11.5, color=INK2, ls=1.22)])
card(s, LEFT, 5.5, CW, 1.26, STEEL, "返回结构带来的好处", title_size=13)
txt(s, LEFT + 0.3, 5.94, CW - 0.6, 0.76,
    [dict(text="code 为 200 表示成功，data 里是业务数组；字段名统一转成 Counter、Price、Amount、Name，"
               "十二张图共用同一套取数写法，新增图表只要换 url 与字段映射。",
          size=11.5, color=INK2, ls=1.24)])
footer(s, STEEL, 24)

# ================================================================ 25 分工
s = new_slide()
header(s, SLATE, "06　组织与管理", "06", "人员分工与进度安排", "五天排期，每天有明确产出")
rows = [["成员", "角色", "承担工作", "交付物"],
        ["占竞", "组长", "架构设计、Kylin 建模、后端接口", "13 个接口与查询网关"],
        ["李艺淼", "数据", "数据清洗、Cube 构建、可视化大屏", "bi_cube 与 Django 大屏"],
        ["付悌安", "前端", "三套页面、图表组件、结构对比模块", "12 张图表与对比表"],
        ["杨博文", "文档", "需求规格、部署验收、数据集与基准值", "五份文档"],
        ["洪嘉伟", "测试", "接口性能、数据一致性、验收用例", "测试用例与校验脚本"]]
th = make_table(s, LEFT, BODY, CW, [0.1, 0.09, 0.48, 0.33], rows, font=12.5, head_font=12.5,
                row_h=0.5, head_h=0.48, accent=SLATE)
txt(s, LEFT, BODY + th + 0.26, CW, 0.32, [dict(text="五天进度与当日产出", size=15, bold=True, color=SLATE)])
days = [("11-11", "环境搭建", "六组件端口全通"), ("11-12", "数据入仓", "六张表一百万行"),
        ("11-13", "维度建模", "bi_cube READY"), ("11-14", "接口与前端", "13 接口与三页"),
        ("11-15", "联调验收", "基准值与文档")]
dw = (CW - 0.4 * 4) / 5
dy = BODY + th + 0.66
for i, (d, name, out) in enumerate(days):
    x = LEFT + i * (dw + 0.4)
    rect(s, x, dy, dw, 1.3, fill=SLATE if i < 4 else GOLD)
    txt(s, x + 0.18, dy + 0.13, dw - 0.3, 0.28, [dict(text=d, size=11.5, bold=True, color=tint(SLATE, 0.74))])
    txt(s, x + 0.18, dy + 0.44, dw - 0.3, 0.36, [dict(text=name, size=15, bold=True, color=WHITE)])
    txt(s, x + 0.18, dy + 0.84, dw - 0.3, 0.42,
        [dict(text=out, size=11, color=tint(SLATE, 0.8), ls=1.2)])
footer(s, SLATE, 25)

# ================================================================ 26 总结
s = new_slide()
header(s, NAVY, "07　总结", "07", "完成情况与后续计划", "已完成项均可复核，后续计划按优先级排列")
txt(s, LEFT, BODY, 5.9, 0.32, [dict(text="已完成并可复核", size=15, bold=True, color=TEAL)])
done = ["六节点集群与 13 个接口在服务器上持续运行",
        "bi_cube 8 维 2 度量 256 个 cuboid，体积 2.95 GB",
        "七张汇总表上线，最大 100 万行，索引 9 个",
        "三套页面共 12 张图表，数据全部来自接口",
        "五份交付文档与四个运维脚本，检查项可重复"]
dy0 = BODY + 0.4
for it in done:
    rect(s, LEFT, dy0, 5.9, 0.7, fill=WHITE, line=LINE, lw=0.8)
    rect(s, LEFT, dy0, 0.07, 0.7, fill=TEAL)
    txt(s, LEFT + 0.34, dy0 + 0.18, 5.35, 0.4, [dict(text=it, size=12, color=INK2)])
    dy0 += 0.78
txt(s, 6.9, BODY, 5.8, 0.32, [dict(text="后续计划", size=15, bold=True, color=STEEL)])
plan = [("第一项", "按科室维度扩展预聚合表，覆盖更多组合"),
        ("第二项", "接入按月增量构建，把单月扩展为多个月"),
        ("第三项", "13 个接口纳入自动化测试，改一次跑一遍"),
        ("第四项", "基准值校验接入启动脚本，每次部署比对")]
py = BODY + 0.4
for k, v in plan:
    rect(s, 6.9, py, 5.8, 0.9, fill=tint(STEEL, 0.93), line=tint(STEEL, 0.55), lw=0.9)
    txt(s, 7.14, py + 0.12, 1.1, 0.28, [dict(text=k, size=10.5, bold=True, color=STEEL)])
    txt(s, 7.14, py + 0.42, 5.3, 0.42, [dict(text=v, size=12, color=INK2, ls=1.18)])
    py += 0.98
rect(s, LEFT, 6.3, CW, 0.6, fill=NAVY)
txt(s, LEFT + 0.32, 6.42, CW - 0.6, 0.36,
    [dict(text="http://192.168.207.179:83/　　大屏 http://192.168.207.179:8000/　　代码与文档已提交",
          size=13, bold=True, color=WHITE)])
footer(s, NAVY, 26)

out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "目标适应症及用药数据分析系统_汇报PPT.pptx")
prs.save(out_path)
print("saved:", out_path)
print("slides:", len(prs.slides._sldIdLst))
