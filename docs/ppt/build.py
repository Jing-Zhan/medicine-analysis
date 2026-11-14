# -*- coding: utf-8 -*-
"""
生成汇报 PPT：目标适应症及用药数据分析系统

叙事顺序：为什么做 → 怎么解决 → 做出来什么样 → 怎么实施的 → 技术内部怎么走。
章节五给出数据流向与 Kylin 实景截图位，不放推算出来的数字。
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn

INK = RGBColor(0x1F, 0x2A, 0x33)
MUTED = RGBColor(0x5B, 0x6B, 0x78)
GREEN = RGBColor(0x2F, 0x5D, 0x46)
GREEN_LT = RGBColor(0xE8, 0xF0, 0xEA)
GOLD = RGBColor(0xA8, 0x81, 0x3C)
GOLD_LT = RGBColor(0xFA, 0xF3, 0xE9)
BLUE = RGBColor(0x2F, 0x66, 0x90)
BLUE_LT = RGBColor(0xE9, 0xEF, 0xF4)
LINE = RGBColor(0xD8, 0xE0, 0xDC)
SOFT = RGBColor(0xF5, 0xF8, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1E, 0x24, 0x2B)
CODE_TXT = RGBColor(0xD6, 0xE0, 0xE8)
CODE_DIM = RGBColor(0x8F, 0xA3, 0xB2)
OK_TXT = RGBColor(0x7B, 0xD3, 0x9A)
GREY_D = RGBColor(0x6B, 0x7A, 0x88)
BODY_TXT = RGBColor(0x3A, 0x47, 0x53)

FONT = "微软雅黑"
MONO = "Consolas"

W, H = 13.333, 7.5
LEFT = 0.62
CW = 12.09
BODY = 1.74

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def new_slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()
    bg.shadow.inherit = False
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
        p.line_spacing = b.get("ls", 1.14)
        if b.get("space_before"):
            p.space_before = Pt(b["space_before"])
        if b.get("space_after"):
            p.space_after = Pt(b["space_after"])
        runs = b["text"] if isinstance(b["text"], list) else [(b["text"], b.get("color", INK))]
        for text, color in runs:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(b.get("size", 18))
            r.font.bold = b.get("bold", False)
            r.font.color.rgb = color
            r.font.name = b.get("font", FONT)
    return tb


def header(s, chapter, title, lead=None):
    txt(s, LEFT, 0.26, CW, 0.30, [dict(text=chapter, size=13, bold=True, color=GREEN)])
    txt(s, LEFT, 0.50, CW, 0.62, [dict(text=title, size=30, bold=True, color=INK)])
    if lead:
        txt(s, LEFT, 1.13, CW, 0.34, [dict(text=lead, size=17, color=MUTED)])
    rect(s, LEFT, 1.56, CW, 0.02, fill=GREEN)


def footer(s, page):
    txt(s, LEFT, 6.98, 7.0, 0.28, [dict(text="目标适应症及用药数据分析系统", size=11, color=MUTED)])
    txt(s, W - LEFT - 1.2, 6.98, 1.2, 0.28,
        [dict(text=str(page).zfill(2), size=11, bold=True, color=GREEN, align=PP_ALIGN.RIGHT)])


def code_block(s, x, y, w, lines, size=13, title=None, pad=0.22, lh=1.45):
    n = len(lines)
    h = pad * 2 + n * size * lh / 72.0 + (0.30 if title else 0) + 0.22
    rect(s, x, y, w, h, fill=DARK)
    top = y + pad - 0.04
    if title:
        txt(s, x + 0.26, top, w - 0.5, 0.26, [dict(text=title, size=11.5, color=CODE_DIM, font=MONO)])
        top += 0.30
    blocks = []
    for item in lines:
        text, color = item if isinstance(item, tuple) else (item, CODE_TXT)
        blocks.append(dict(text=text, size=size, color=color, font=MONO, ls=lh))
    txt(s, x + 0.26, top, w - 0.5, h - (top - y) - pad + 0.04, blocks)
    return y + h


def shot(s, x, y, w, h, tag, hint, size=15, tag_size=17):
    rect(s, x, y, w, h, fill=RGBColor(0xF2, 0xF5, 0xF7), line=RGBColor(0xA9, 0xB6, 0xBF), lw=1.0, dash=True)
    txt(s, x + 0.15, y + h / 2 - 0.5, w - 0.3, 0.42,
        [dict(text=tag, size=tag_size, bold=True, color=RGBColor(0x71, 0x82, 0x8F), align=PP_ALIGN.CENTER)])
    txt(s, x + 0.15, y + h / 2 - 0.02, w - 0.3, 0.62,
        [dict(text=hint, size=size, color=RGBColor(0x8A, 0x99, 0xA5), align=PP_ALIGN.CENTER, ls=1.2)])


def make_table(s, x, y, w, ratios, rows, font=15, head_font=15, row_h=0.44, head_h=0.48,
               aligns=None, head_fill=GREEN, bold_col=None):
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
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = head_fill if ri == 0 else (WHITE if ri % 2 == 1 else SOFT)
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
                r.font.color.rgb = INK if is_b else BODY_TXT
    return total


def kpi(s, x, y, w, h, value, unit, label, accent=GREEN):
    rect(s, x, y, w, h, fill=WHITE, line=LINE, lw=0.75)
    txt(s, x + 0.18, y + 0.12, w - 0.36, 0.62,
        [dict(text=[(value, accent), (unit, MUTED)], size=31, bold=True)])
    txt(s, x + 0.18, y + 0.76, w - 0.36, h - 0.82, [dict(text=label, size=13.5, color=MUTED, ls=1.14)])


def problem_page(page, title, lead, problem, steps, effects):
    s = new_slide()
    header(s, "02　项目设计", title, lead)
    rect(s, LEFT, BODY, CW, 0.94, fill=GOLD_LT, line=GOLD, lw=0.75)
    txt(s, LEFT + 0.26, BODY + 0.1, 1.6, 0.26, [dict(text="问题表现", size=12.5, bold=True, color=GOLD)])
    txt(s, LEFT + 1.75, BODY + 0.1, CW - 2.0, 0.74,
        [dict(text=problem, size=13.5, color=BODY_TXT, ls=1.24)])
    txt(s, LEFT, 2.86, 5.0, 0.3, [dict(text="我们的做法", size=15, bold=True, color=GREEN)])
    sy = 3.2
    for i, (name, desc) in enumerate(steps):
        rect(s, LEFT, sy, 0.4, 0.4, fill=GREEN, shape=MSO_SHAPE.OVAL)
        txt(s, LEFT, sy + 0.08, 0.4, 0.26,
            [dict(text=str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)])
        txt(s, LEFT + 0.56, sy + 0.02, 6.1, 0.3, [dict(text=name, size=14.5, bold=True, color=INK)])
        txt(s, LEFT + 0.56, sy + 0.34, 6.1, 0.34, [dict(text=desc, size=12.5, color=MUTED, ls=1.18)])
        sy += 0.88
    txt(s, 7.5, 2.86, 5.2, 0.3, [dict(text="做出来的效果", size=15, bold=True, color=BLUE)])
    ey = 3.2
    for v, label in effects:
        rect(s, 7.5, ey, 5.21, 0.8, fill=BLUE_LT, line=BLUE, lw=0.7)
        txt(s, 7.7, ey + 0.06, 2.3, 0.4, [dict(text=v, size=19, bold=True, color=BLUE)])
        txt(s, 9.95, ey + 0.14, 2.6, 0.54, [dict(text=label, size=12, color=BODY_TXT, ls=1.18)])
        ey += 0.88
    footer(s, page)
    return s


# ================================================================ 01 封面
s = new_slide()
rect(s, 0, 0, W, 2.02, fill=GREEN)
txt(s, LEFT, 0.54, CW, 0.32, [dict(text="大数据实训项目汇报　2026 年 11 月", size=15,
                                   color=RGBColor(0xC9, 0xDC, 0xCE))])
txt(s, LEFT, 0.94, CW, 0.78, [dict(text="目标适应症及用药数据分析系统", size=42, bold=True, color=WHITE)])
txt(s, LEFT, 2.38, CW, 0.42,
    [dict(text="把六张业务表做成 13 个查询接口与三套分析页面", size=18, color=MUTED)])
rect(s, LEFT, 3.02, 1.9, 0.05, fill=GOLD)
cards3 = [
    ("100 万行", "处方与用药明细", "单月 200812 全量数据"),
    ("13 个", "查询接口", "覆盖 12 张分析图表"),
    ("3 套", "分析页面", "首页、适应症页、药品页"),
]
cw3 = (CW - 0.5) / 3
for i, (v, lab, sub) in enumerate(cards3):
    x = LEFT + i * (cw3 + 0.25)
    rect(s, x, 3.32, cw3, 1.42, fill=SOFT, line=LINE, lw=0.75)
    txt(s, x + 0.24, 3.48, cw3 - 0.4, 0.5, [dict(text=v, size=29, bold=True, color=GREEN)])
    txt(s, x + 0.24, 4.02, cw3 - 0.4, 0.32, [dict(text=lab, size=16, bold=True, color=INK)])
    txt(s, x + 0.24, 4.36, cw3 - 0.4, 0.3, [dict(text=sub, size=13.5, color=MUTED)])
txt(s, LEFT, 5.28, CW, 0.34, [dict(text="第二小组", size=17, bold=True, color=INK)])
txt(s, LEFT, 5.68, CW, 0.34, [dict(text="占竞　　李艺淼　　付悌安　　杨博文　　洪嘉伟", size=17, color=MUTED)])
rect(s, LEFT, 6.34, CW, 0.02, fill=LINE)
txt(s, LEFT, 6.48, CW, 0.30,
    [dict(text="服务器 192.168.207.179　主站 83 端口　大屏 8000 端口　Kylin 7070 端口", size=13.5, color=MUTED)])

# ================================================================ 02 目录
s = new_slide()
header(s, "目录", "汇报内容与页码")
toc = [
    ("01", "项目背景", "为什么做、总体思路、数据基础", "03"),
    ("02", "项目设计", "三个问题各自的设计、页面与接口、与课程任务对照", "06"),
    ("03", "项目结果", "系统页面总览、三处细节、指标怎么算", "11"),
    ("04", "实施过程与方法", "六个阶段、部署方式、状态检查", "16"),
    ("05", "技术原理与架构", "数据流向、Kylin 建模与 Cube、引擎切换", "21"),
    ("06", "组织与管理", "人员分工与五天进度", "24"),
    ("07", "总结", "完成情况与后续计划", "25"),
]
y = 1.78
for num, name, desc, pg in toc:
    rect(s, LEFT, y, CW, 0.64, fill=SOFT if int(num) % 2 == 1 else WHITE, line=LINE, lw=0.6)
    txt(s, LEFT + 0.14, y + 0.1, 0.9, 0.42, [dict(text=num, size=23, bold=True, color=GREEN)])
    txt(s, LEFT + 1.1, y + 0.04, 3.2, 0.32, [dict(text=name, size=19, bold=True, color=INK)])
    txt(s, LEFT + 1.1, y + 0.36, 8.2, 0.24, [dict(text=desc, size=13.5, color=MUTED)])
    txt(s, LEFT + CW - 1.5, y + 0.16, 1.2, 0.3,
        [dict(text="P" + pg, size=13.5, color=MUTED, align=PP_ALIGN.RIGHT)])
    y += 0.71
footer(s, 2)

# ================================================================ 03 为什么做
s = new_slide()
header(s, "01　项目背景", "为什么做这个项目",
       "手上有六张业务表，日常分析要回答四类问题，但现在每次都要重新写一遍 SQL")
txt(s, LEFT, BODY, 6.1, 0.3, [dict(text="业务上要回答的四类问题", size=15, bold=True, color=GREEN)])
qs = [
    ("哪些病用药最多", "按疾病看处方量与费用，确定重点关注哪些适应症"),
    ("哪些药覆盖广", "按药品看覆盖的医院与城市，判断市场覆盖范围"),
    ("谁在用什么药", "按科室、年龄看用药分布，发现结构差异"),
    ("用得是否合理", "注射剂、基本药物、抗菌药物三项占比是否偏高"),
]
qy = BODY + 0.36
for k, v in qs:
    rect(s, LEFT, qy, 6.1, 0.72, fill=SOFT, line=LINE, lw=0.7)
    txt(s, LEFT + 0.22, qy + 0.18, 2.2, 0.3, [dict(text=k, size=13.5, bold=True, color=GREEN)])
    txt(s, LEFT + 2.4, qy + 0.16, 3.5, 0.44, [dict(text=v, size=12.5, color=BODY_TXT, ls=1.2)])
    qy += 0.8
txt(s, 6.95, BODY, 5.76, 0.3, [dict(text="现在的工作方式与三个困难", size=15, bold=True, color=GOLD)])
flow = ["打开数据库，手工写多表关联 SQL", "等几十秒拿到结果，复制到 Excel", "换一个维度，SQL 重写一遍"]
fy = BODY + 0.36
for i, t in enumerate(flow):
    rect(s, 6.95, fy, 5.76, 0.5, fill=GOLD_LT, line=GOLD, lw=0.6)
    txt(s, 7.15, fy + 0.11, 0.5, 0.28, [dict(text=str(i + 1), size=12, bold=True, color=GOLD)])
    txt(s, 7.6, fy + 0.1, 5.0, 0.3, [dict(text=t, size=12.5, color=BODY_TXT)])
    fy += 0.58
diffs = [
    ("关联多", "一条分析要连三到六张表，SQL 长，容易漏条件"),
    ("字段脏", "维表文本带回车符，同一科室被拆成两项"),
    ("响应慢", "百万行关联一次几十秒，页面点不动"),
]
for k, v in diffs:
    rect(s, 6.95, fy, 5.76, 0.62, fill=WHITE, line=LINE, lw=0.65)
    txt(s, 7.15, fy + 0.16, 0.95, 0.28, [dict(text=k, size=13, bold=True, color=GOLD)])
    txt(s, 8.15, fy + 0.15, 4.45, 0.32, [dict(text=v, size=12.5, color=MUTED)])
    fy += 0.7
rect(s, LEFT, 6.1, CW, 0.64, fill=GREEN_LT, line=GREEN, lw=0.75)
txt(s, LEFT + 0.26, 6.22, CW - 0.5, 0.4,
    [dict(text="项目要做的：把上面这些重复劳动固化成 13 个固定接口和三套页面，口径统一、结果可复核",
          size=14, color=GREEN)])
footer(s, 3)

# ================================================================ 04 总体思路
s = new_slide()
header(s, "01　项目背景", "总体解决思路", "三个困难对应三项设计，最终落到三套页面上")
rows = [
    ["遇到的困难", "我们的做法", "达到的效果"],
    ["关联多，SQL 难写", "按疾病与药品、疾病、药品、处方与药品四种组合分组统计，写成四张汇总表，接口直接查表",
     "接口不再扫明细表，最慢 15.74 秒"],
    ["字段脏，口径不一", "六张维表建视图去掉回车符，占比等于分组处方数除以维度总处方数，公式只写在服务层",
     "三个页面同一指标由同一段代码算出"],
    ["响应慢，页面点不动", "取值几十种的字段提前算好，取值成千上万种的字段建索引，前端超时放宽到 60 秒",
     "首页 0.61 秒，13 个接口全部 200"],
]
make_table(s, LEFT, BODY, CW, [0.19, 0.53, 0.28], rows, font=12.5, head_font=13.5,
           row_h=0.92, head_h=0.5, aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])
txt(s, LEFT, 5.02, CW, 0.3, [dict(text="数据从表到页面经过四步", size=15, bold=True, color=GREEN)])
chain = [("明细表", "六张业务表，100 万行"), ("汇总表", "四张聚合表，10 万级"),
         ("接口", "13 个查询接口"), ("页面", "三套页面，12 张图")]
cw4 = (CW - 0.9) / 4
for i, (name, desc) in enumerate(chain):
    x = LEFT + i * (cw4 + 0.3)
    rect(s, x, 5.42, cw4, 1.02, fill=GREEN if i % 2 == 0 else BLUE)
    txt(s, x + 0.14, 5.52, cw4 - 0.28, 0.32, [dict(text=name, size=15, bold=True, color=WHITE)])
    txt(s, x + 0.14, 5.88, cw4 - 0.28, 0.44,
        [dict(text=desc, size=11.5, color=RGBColor(0xEC, 0xF3, 0xEF), ls=1.2)])
    if i < 3:
        txt(s, x + cw4 + 0.02, 5.74, 0.26, 0.3,
            [dict(text="→", size=18, bold=True, color=MUTED, align=PP_ALIGN.CENTER)])
footer(s, 4)

# ================================================================ 05 数据基础与目标
s = new_slide()
header(s, "01　项目背景", "数据基础与项目目标", "先确认手上有什么数据，再把目标写成可校验的数字")
txt(s, LEFT, BODY, 6.4, 0.3, [dict(text="六张业务表", size=15, bold=True, color=GREEN)])
rows = [
    ["表名", "内容", "规模"],
    ["prescription_diseases", "处方与用药明细", "1000000 行"],
    ["t_view_disease", "疾病三级分类", "42501 条"],
    ["t_view_drug", "药品属性", "205971 种"],
    ["t_view_hospital", "医院与城市", "全国范围"],
    ["t_view_section", "科室", "20 类"],
]
th = make_table(s, LEFT, BODY + 0.36, 6.4, [0.4, 0.3, 0.3], rows, font=12.5, head_font=12.5,
                row_h=0.44, head_h=0.44)
txt(s, LEFT, BODY + 0.36 + th + 0.2, 6.4, 0.6,
    [dict(text="单月数据，时间字段 200812，年龄 40 至 89 岁，男女接近 1 比 1",
          size=12.5, color=MUTED, ls=1.24)])
txt(s, 7.3, BODY, 5.4, 0.3, [dict(text="四条目标", size=15, bold=True, color=GREEN)])
goals = [
    ("分析视角", "5 类", "地区与医院、年龄、适应症、药品、科室"),
    ("查询接口", "13 个", "覆盖三套页面的全部图表"),
    ("响应时间", "2 秒与 20 秒", "单表 2 秒内，多表关联 20 秒内"),
    ("部署方式", "一条命令", "拉起全部服务并逐项自检"),
]
gy = BODY + 0.36
for k, v, d in goals:
    rect(s, 7.3, gy, 5.41, 0.86, fill=SOFT, line=LINE, lw=0.7)
    txt(s, 7.5, gy + 0.1, 1.3, 0.26, [dict(text=k, size=12, bold=True, color=MUTED)])
    txt(s, 8.85, gy + 0.06, 3.6, 0.36, [dict(text=v, size=18, bold=True, color=GREEN)])
    txt(s, 7.5, gy + 0.48, 5.0, 0.3, [dict(text=d, size=11.5, color=MUTED)])
    gy += 0.94
rect(s, 7.3, gy + 0.04, 5.41, 0.76, fill=GREEN_LT, line=GREEN, lw=0.7)
txt(s, 7.5, gy + 0.14, 5.0, 0.56,
    [dict(text="验收依据：接口全部返回 200、页面取真实接口、11 项基准值可复核", size=12, color=GREEN, ls=1.2)])
footer(s, 5)

# ================================================================ 06 问题一
problem_page(
    6, "问题一与设计：六表关联改为查汇总表",
    "一条关于某类疾病用了哪些药的分析要连三张表，百万行每次现算",
    "疾病与药品分在两张维表里，处方明细只存编码。要得到某类疾病用了哪些药、各多少，"
    "必须把明细表、疾病表、药品表关联起来再分组，一条 SQL 十几行，漏一个条件结果就偏。",
    [
        ("先定下常用组合", "统计需求集中在四类：疾病合计、药品合计、疾病与药品组合、处方与药品组合"),
        ("按组合建汇总表", "每张表只存编码、名称、数量三列，主键唯一，从建表上避免重复计数"),
        ("接口改成查汇总表", "先用汇总表取出编码与数量，再与维表关联补名称，不再扫明细表"),
        ("新需求按同样方式扩展", "科室用药结构对比也是先建 agg_section_drug，接口只查汇总结果"),
    ],
    [("4 张汇总表", "覆盖 13 个接口中的 8 个"), ("15.74 秒", "最慢接口，此前单次关联需数十秒"),
     ("99 万行", "最大汇总表行数，最小 4 万行")],
)

# ================================================================ 07 问题二
problem_page(
    7, "问题二与设计：统一维表与统计口径",
    "同一指标两个人算出两个数，根源在维表脏数据和算法不统一",
    "维表里的文本字段带回车符，同一科室被拆成两项；药品表有列错位，剂型值出现在厂商列；"
    "同一个人在不同页面把分母取错，占比就算错。",
    [
        ("六张维表统一建视图", "每张维表建一个 t_view_ 视图，字段统一去回车、去空格再对外提供"),
        ("文本字段限长", "建汇总表时文本列统一截到 255 位，否则主键建不上，导入直接报错"),
        ("比率算法只写一处", "占比的分子分母都按处方数加权，写在 Service 层，各页面调用同一个方法"),
        ("缺失值统一处理", "名称缺失填未标注或未分类，并且不参与 Top 榜排序"),
    ],
    [("一处算法", "三套页面同一指标由同一段代码算出"), ("9 个索引", "建在清洗后的视图字段上"),
     ("两类脏数据", "回字符与列错位已在视图层处理")],
)

# ================================================================ 08 问题三
problem_page(
    8, "问题三与设计：预计算加索引",
    "百万行关联一次几十秒，页面等不起，还要避免出现假数据",
    "跨表关联一次要几十秒，页面点开是白屏。前端原来设 8 秒超时，把还在计算的请求当成失败，"
    "结果页面上一半是真数据一半是假数据。",
    [
        ("取值少的字段交给预计算", "年龄、性别、年月、科室、医院等级等八列取值在 2 到 431 种之间，预计算成 256 个组合"),
        ("取值多的字段建索引", "医院、科室、药品这类有上千上万种取值的字段不预计算，改在 MySQL 建 9 个索引"),
        ("前端超时与失败处理", "超时放宽到 60 秒；接口报错时显示错误提示，不再用假数据顶替"),
        ("一个配置项切换引擎", "配置 query.engine 在 kylin 与 mysql 之间切换，业务代码不用改"),
    ],
    [("0.61 秒", "首页概览接口实测"), ("15.74 秒", "最慢的跨表关联接口"),
     ("13 个", "接口全部返回 200")],
)

# ================================================================ 09 页面与接口
s = new_slide()
header(s, "02　项目设计", "页面、图表与接口的对应关系",
       "每个页面回答什么问题，背后调哪个接口，一一对应")
rows = [
    ["分析对象", "页面", "页面上的图表", "接口", "数据来源"],
    ["适应症", "适应症页", "关联药品组合、科室分布、年龄分布、费用负担", "/disease/ 开头 5 个",
     "agg_disease_total"],
    ["药品", "药品页", "覆盖城市、覆盖医院、适应症分布、科室分布、用药结构对比", "/drug/ 开头 5 个",
     "agg_drug_total"],
    ["机构", "首页", "省份分布、城市等级、年龄分布、药品前十", "/home/ 开头 4 个",
     "明细表与维表"],
    ["汇总", "独立大屏", "省份地图、药品前十、病症前十、金额分布、关系图", "Django 5 个接口",
     "同一份 MySQL 库"],
]
th = make_table(s, LEFT, BODY, CW, [0.11, 0.12, 0.37, 0.2, 0.2], rows, font=11.5, head_font=12,
                row_h=0.7, head_h=0.44)
rect(s, LEFT, BODY + th + 0.24, CW, 1.34, fill=SOFT, line=LINE, lw=0.75)
txt(s, LEFT + 0.28, BODY + th + 0.34, CW - 0.5, 0.3,
    [dict(text="设计上的三点考虑", size=13.5, bold=True, color=INK)])
pts = [
    "一个页面只回答一组问题，图表按分析对象分组，避免把十几种图堆在一起",
    "接口按对象分前缀，前端按页面路径取数，新增分析只需加一个接口和一个组件",
    "页面顶部保留关键词搜索框，输入疾病或药品名即可切换分析目标",
]
py = BODY + th + 0.68
for t in pts:
    txt(s, LEFT + 0.28, py, CW - 0.6, 0.3, [dict(text="· " + t, size=12, color=MUTED)])
    py += 0.3
footer(s, 9)

# ================================================================ 10 与课程任务对照
s = new_slide()
header(s, "02　项目设计", "与课程实训任务的对照",
       "任务资料要求 20 个分析任务，逐条对照我们的实现方式与所用技术")
rows = [
    ["课程任务", "要求的做法", "我们的实现", "状态"],
    ["任务12 至 15　城市等级、年龄比例、药品销额、省份格局", "后端走 Kylin 查询，前端 Vue 展示",
     "首页四张图，四个接口", "已实现"],
    ["任务16 至 19　用药组合、联合用药、年龄分布、科室分布", "同上",
     "适应症页四张图，四个接口", "已实现"],
    ["任务20 至 23　覆盖城市、对应适应症、覆盖医院、科室分布", "同上",
     "药品页四张图，四个接口", "已实现"],
    ["任务24　药品关联规则分析", "Pandas 与 Apriori 算法",
     "规则文件已接入大屏，药品名编码待统一", "部分实现"],
    ["任务25 至 31　Django 大屏与五张图", "Django 与 ECharts",
     "大屏五个取数接口，地图与关系图取同一份 MySQL", "已实现"],
]
th = make_table(s, LEFT, BODY, CW, [0.36, 0.24, 0.32, 0.08], rows, font=11.5, head_font=12,
                row_h=0.62, head_h=0.44)
txt(s, LEFT, BODY + th + 0.2, 4.0, 0.3, [dict(text="三处我们自己加的设计", size=14, bold=True, color=GOLD)])
inn = [
    ("双通道路由", "取值少的走 Cube，取值多的走索引"),
    ("四张预聚合表", "把百万行明细压成可复用的中间结果"),
    ("科室用药结构对比", "三套页面里唯一横向比较结构的表"),
]
iw = (CW - 0.4) / 3
iy = BODY + th + 0.54
for i, (k, v) in enumerate(inn):
    x = LEFT + i * (iw + 0.2)
    rect(s, x, iy, iw, 0.86, fill=GOLD_LT, line=GOLD, lw=0.7)
    txt(s, x + 0.2, iy + 0.1, iw - 0.4, 0.28, [dict(text=k, size=13, bold=True, color=GOLD)])
    txt(s, x + 0.2, iy + 0.42, iw - 0.4, 0.4, [dict(text=v, size=11.5, color=BODY_TXT, ls=1.2)])
footer(s, 10)

# ================================================================ 11 系统总览
s = new_slide()
header(s, "03　项目结果", "系统页面总览", "四块界面各自回答一类问题，全部取真实接口数据")
grid = [
    ("首页总览", "首页", "四个总量指标加四张分布图，看整体盘子", "截图位 01", "192.168.207.179:83/#/home"),
    ("适应症分析", "适应症页", "输入疾病名，看它的用药、科室、年龄与费用", "截图位 02", "192.168.207.179:83/#/disease"),
    ("药品分析", "药品页", "输入药品名，看它的覆盖范围与用药结构", "截图位 03", "192.168.207.179:83/#/drug"),
    ("可视化大屏", "独立大屏", "省份地图、药品与病症前十、药物关系图", "截图位 05", "192.168.207.179:8000"),
]
gw = (CW - 0.4) / 2
for i, (name, path, desc, tag, url) in enumerate(grid):
    x = LEFT + (i % 2) * (gw + 0.4)
    y = BODY + (i // 2) * 2.42
    shot(s, x, y, gw, 1.72, tag, url, size=11.5)
    txt(s, x, y + 1.8, 2.4, 0.3, [dict(text=name, size=15, bold=True, color=INK)])
    txt(s, x + 2.5, y + 1.84, gw - 2.5, 0.3, [dict(text=path, size=11.5, color=MUTED)])
    txt(s, x, y + 2.1, gw, 0.28, [dict(text=desc, size=12, color=MUTED)])
footer(s, 11)

# ================================================================ 12 首页
s = new_slide()
header(s, "03　项目结果", "首页总览：四个总量指标加四张分布图",
       "数据全部来自 /home/ 开头的四个接口，接口失败时显示错误而不是占位数字")
shot(s, LEFT, BODY, 8.05, 4.6, "截图位 01　首页总览",
     "采集地址　http://192.168.207.179:83/#/home", size=14)
kpis = [("100", " 万行", "处方与用药明细总量"), ("13", " 个", "分析查询接口数量"),
        ("0.61", " 秒", "/home/overview 实测耗时"), ("6", " 节点", "集群组件全部在监听")]
for i, (v, u, lab) in enumerate(kpis):
    kpi(s, 8.95, BODY + i * 1.16, 3.76, 1.02, v, u, lab, accent=GREEN if i % 2 == 0 else BLUE)
footer(s, 12)

# ================================================================ 13 适应症页
s = new_slide()
header(s, "03　项目结果", "适应症页：某类疾病用了什么药、花多少钱",
       "接口 /disease/burden 返回的数据与页面显示一致")
shot(s, LEFT, BODY, 5.3, 3.9, "截图位 02　适应症分析",
     "http://192.168.207.179:83/#/disease", size=12.5)
txt(s, 6.15, BODY, 6.55, 0.3, [dict(text="费用负担前五，按总金额排序", size=14, bold=True, color=GREEN)])
rows = [
    ["疾病大类", "处方数", "总金额 元", "均次 元"],
    ["腺瘤和腺癌", "5,942", "156,850.62", "26.40"],
    ["其他器官的结核", "5,478", "148,405.26", "27.09"],
    ["孕产妇并发其他疾病", "4,676", "122,397.39", "26.18"],
    ["动态未定或未知的肿瘤", "4,482", "118,627.17", "26.47"],
    ["操作并发症", "3,372", "88,463.92", "26.23"],
]
th = make_table(s, 6.15, BODY + 0.32, 6.55, [0.4, 0.19, 0.25, 0.16], rows, font=13, head_font=13,
                row_h=0.4, head_h=0.4,
                aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
by = BODY + 0.32 + th + 0.12
rect(s, 6.15, by, 6.55, 1.24, fill=GOLD_LT, line=GOLD, lw=0.75)
txt(s, 6.35, by + 0.08, 6.1, 0.26, [dict(text="这三个数怎么算出来的", size=12.5, bold=True, color=GOLD)])
calcs = [
    "处方数　该大类下全部处方记录的条数",
    "总金额　该大类各条记录的金额字段求和后保留两位",
    "均次费用　总金额除以处方数，用于区分人多与花钱多",
]
cy = by + 0.38
for c in calcs:
    txt(s, 6.35, cy, 6.1, 0.26, [dict(text=c, size=11.5, color=BODY_TXT)])
    cy += 0.26
rect(s, LEFT, 5.92, CW, 0.82, fill=GREEN_LT, line=GREEN, lw=0.75)
txt(s, LEFT + 0.26, 6.0, CW - 0.5, 0.28,
    [dict(text="表里能看出的情况", size=13.5, bold=True, color=GREEN)])
txt(s, LEFT + 0.26, 6.28, CW - 0.5, 0.4,
    [dict(text="均次费用集中在 26 元附近，排名主要由处方数决定，费用指标区分度低，"
               "因此把重点放在三项用药占比上", size=12.5, color=MUTED, ls=1.2)])
footer(s, 13)

# ================================================================ 14 药品页
s = new_slide()
header(s, "03　项目结果", "药品页：新增科室用药结构对比",
       "这一页与另外两页的区别在于，它按科室分组横向比较三项用药占比")
shot(s, LEFT, BODY, 5.5, 3.7, "截图位 03　药品分析",
     "http://192.168.207.179:83/#/drug", size=12.5)
txt(s, LEFT, 5.56, 5.5, 0.28, [dict(text="上半部分：药品自身属性与覆盖范围", size=11.5, color=MUTED)])

rect(s, 6.35, BODY, 6.36, 3.0, fill=WHITE, line=GREEN, lw=1.0)
rect(s, 6.35, BODY, 6.36, 0.07, fill=GREEN)
txt(s, 6.55, BODY + 0.14, 6.0, 0.3, [dict(text="下半部分：科室用药结构对比", size=15.5, bold=True, color=GREEN)])
txt(s, 6.55, BODY + 0.52, 6.0, 0.26,
    [dict(text="取处方数前 10 个科室，同表并列，占比都按科室处方数加权", size=11.5, color=MUTED)])
calcs2 = [
    "注射剂占比　剂型含注射的处方数除以该科室处方数",
    "基本药物占比　基本药物标记为是的处方数除以该科室处方数",
    "抗菌药物占比　通用名含抗菌关键词的处方数除以该科室处方数",
]
cy = BODY + 0.9
for c in calcs2:
    rect(s, 6.55, cy, 5.96, 0.5, fill=SOFT)
    txt(s, 6.7, cy + 0.13, 5.7, 0.28, [dict(text=c, size=11.5, color=BODY_TXT)])
    cy += 0.56
txt(s, 6.55, cy + 0.04, 6.0, 0.26,
    [dict(text="分子分母都来自 agg_section_drug 与药品维表的同一次关联", size=11, color=MUTED)])
shot(s, 6.35, 4.76, 6.36, 1.34, "截图位 04　结构对比表",
     "部署完成后补采，需先执行 agg_structure.sql", size=11)
rect(s, LEFT, 5.96, 5.5, 0.74, fill=BLUE_LT, line=BLUE, lw=0.75)
txt(s, LEFT + 0.2, 6.04, 5.1, 0.26, [dict(text="为什么单独留出位置", size=11.5, bold=True, color=BLUE)])
txt(s, LEFT + 0.2, 6.3, 5.1, 0.34,
    [dict(text="三套页面里唯一横向比较结构的表", size=11, color=BODY_TXT)])
footer(s, 14)

# ================================================================ 15 数据校验
s = new_slide()
header(s, "03　项目结果", "数据一致性校验",
       "总额出现差额时不停留在判断，而是算出差多少、差在哪")
boxes = [
    ("事实表直接求和", "26,239,620.54", "元　一百万行明细", SOFT, LINE, GREEN),
    ("关联维表后求和", "26,207,933.86", "元　内连接丢失部分记录", SOFT, LINE, BLUE),
    ("差额与原因", "31,686.68", "元　来自 1,164 行医院编号为空", GOLD_LT, GOLD, GOLD),
]
bw = (CW - 0.3) / 3
for i, (k, v, u, fill, ln, accent) in enumerate(boxes):
    x = LEFT + i * (bw + 0.15)
    rect(s, x, BODY, bw, 1.46, fill=fill, line=ln, lw=0.75)
    txt(s, x + 0.22, BODY + 0.1, bw - 0.4, 0.26, [dict(text=k, size=13, bold=True, color=accent)])
    txt(s, x + 0.22, BODY + 0.38, bw - 0.4, 0.5, [dict(text=v, size=26, bold=True, color=INK)])
    txt(s, x + 0.22, BODY + 1.0, bw - 0.4, 0.3, [dict(text=u, size=12.5, color=MUTED)])
ty = BODY + 1.68
txt(s, LEFT, ty, 6.0, 0.3, [dict(text="其余五项基准值", size=15, bold=True, color=GREEN)])
rows = [
    ["校验项", "期望值", "实测值"],
    ["处方表行数", "1,000,000", "1,000,000"],
    ["各年龄行数", "每岁 20,000", "20,000"],
    ["性别分布", "接近 1 比 1", "500222 比 499778"],
]
make_table(s, LEFT, ty + 0.36, 6.0, [0.38, 0.3, 0.32], rows, font=13.5, head_font=13.5,
           row_h=0.44, head_h=0.44)
rows2 = [
    ["校验项", "期望值", "实测值"],
    ["自定义索引", "9 个", "9 个"],
    ["HDFS 数据目录", "6 个", "6 个"],
    ["疾病预聚合表", "等于诊断数", "42,501 行"],
]
make_table(s, 6.72, ty + 0.36, 5.99, [0.38, 0.3, 0.32], rows2, font=13.5, head_font=13.5,
           row_h=0.44, head_h=0.44)
rect(s, LEFT, 6.16, CW, 0.56, fill=GREEN_LT, line=GREEN, lw=0.75)
txt(s, LEFT + 0.26, 6.28, CW - 0.5, 0.28,
    [dict(text="校验脚本 dump_baseline.py 可重复执行，指标写入数据基准值文档，供验收逐项复核",
          size=13, color=GREEN)])
footer(s, 15)

# ================================================================ 16 实施流程
s = new_slide()
header(s, "04　实施过程与方法", "实施流程与阶段产物", "六个阶段，每个阶段有明确产物")
stages = [
    ("一", "环境搭建", "六个组件端口全通"),
    ("二", "数据入仓", "六张表 100 万行"),
    ("三", "维度建模", "bi_cube 状态 READY"),
    ("四", "接口开发", "13 个接口返回 200"),
    ("五", "前端联调", "12 张图表取真实数"),
    ("六", "部署验收", "基准值文档与自检"),
]
n = len(stages)
step = CW / n
rect(s, LEFT + 0.3, 2.52, CW - 0.6, 0.03, fill=LINE)
for i, (num, name, out) in enumerate(stages):
    cx = LEFT + step * i + step / 2
    color = GREEN if i % 2 == 0 else BLUE
    rect(s, cx - 0.3, 2.26, 0.6, 0.56, fill=color, shape=MSO_SHAPE.OVAL)
    txt(s, cx - 0.3, 2.36, 0.6, 0.34, [dict(text=num, size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)])
    txt(s, cx - step / 2 + 0.1, 2.98, step - 0.2, 0.32,
        [dict(text=name, size=16.5, bold=True, color=INK, align=PP_ALIGN.CENTER)])
    txt(s, cx - step / 2 + 0.1, 3.36, step - 0.2, 0.56,
        [dict(text=out, size=13, color=MUTED, align=PP_ALIGN.CENTER, ls=1.22)])
txt(s, LEFT, 4.16, CW, 0.3, [dict(text="实施中遇到的三个实际情况与处理方式", size=15, bold=True, color=GOLD)])
issues = [
    ("数据入仓", "维度表文本带回车符，分组结果出现重复项", "清洗时统一去回车，再重建视图"),
    ("维度建模", "单表 Cube 无法回答跨表关联的 12 个接口", "高基数关联改走 MySQL 并建 9 个索引"),
    ("接口联调", "重新编译后新接口仍返回 404", "启动脚本比对 jar 与进程时间，自动重启"),
]
iy = 4.6
for k, prob, fix in issues:
    rect(s, LEFT, iy, CW, 0.62, fill=SOFT, line=LINE, lw=0.6)
    txt(s, LEFT + 0.2, iy + 0.16, 1.3, 0.3, [dict(text=k, size=13, bold=True, color=GREEN)])
    txt(s, LEFT + 1.55, iy + 0.15, 5.2, 0.32, [dict(text=prob, size=13, color=MUTED)])
    txt(s, LEFT + 6.95, iy + 0.15, 5.0, 0.32, [dict(text=fix, size=13, color=INK)])
    iy += 0.7
footer(s, 16)

# ================================================================ 17 阶段一二
s = new_slide()
header(s, "04　实施过程与方法", "阶段一二：环境搭建与数据入仓",
       "集群与数据库分别用脚本拉起，端口逐个校验")
yn = code_block(s, LEFT, BODY, 6.0, [
    ("# 六个组件一次拉起", CODE_DIM),
    "bash /opt/start-cluster.sh",
    "ss -lnt | grep -E '2181|9000|8088|16010'",
    "",
    ("# 数据落库与入仓", CODE_DIM),
    "hdfs dfs -ls /bi_data/mysql",
    "mysql -uroot -p yiyao -e \\",
    "  'SELECT COUNT(*) FROM prescription_diseases;'",
], size=12, title="实际操作命令")
txt(s, LEFT, yn + 0.24, 6.0, 0.28, [dict(text="两个数据处理细节", size=14.5, bold=True, color=INK)])
txt(s, LEFT, yn + 0.56, 6.0, 1.3,
    [dict(text="维度表文本字段带回车符，分组时同一名称被拆成两项，清洗时统一去掉", size=13,
          color=MUTED, ls=1.3),
     dict(text="药品表存在后缀列，生成列 drug_code 与业务列 drug 并存，关联时用后者", size=13,
          color=MUTED, ls=1.3)])
txt(s, 6.9, BODY, 5.8, 0.3, [dict(text="端口与数据校验结果", size=14.5, bold=True, color=GREEN)])
checks = [
    ("2181", "ZooKeeper"), ("9000", "HDFS"), ("8088", "YARN"),
    ("16010", "HBase"), ("9083", "Hive 元数据"), ("7070", "Kylin"),
    ("3306", "MySQL"), ("83", "后端接口"), ("8000", "大屏"),
]
for i, (port, name) in enumerate(checks):
    x = 6.9 + (i % 3) * 1.95
    y = BODY + 0.36 + (i // 3) * 0.58
    rect(s, x, y, 1.85, 0.48, fill=SOFT, line=LINE, lw=0.6)
    txt(s, x + 0.14, y + 0.1, 0.8, 0.28, [dict(text=port, size=13, bold=True, color=GREEN, font=MONO)])
    txt(s, x + 0.86, y + 0.11, 0.95, 0.26, [dict(text=name, size=11.5, color=MUTED)])
tin = BODY + 2.22
txt(s, 6.9, tin, 5.8, 0.3, [dict(text="数据规模", size=14.5, bold=True, color=GREEN)])
rows = [
    ["数据项", "数量"],
    ["处方与用药明细", "1,000,000 行"],
    ["疾病维度", "42,501 个"],
    ["药品维度", "205,971 种"],
    ["HDFS 数据目录", "6 个"],
]
make_table(s, 6.9, tin + 0.36, 5.8, [0.6, 0.4], rows, font=13.5, head_font=13.5,
           row_h=0.36, head_h=0.38, aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
footer(s, 17)

# ================================================================ 18 阶段三四
s = new_slide()
header(s, "04　实施过程与方法", "阶段三四：维度建模与接口开发",
       "Cube 负责取值少的字段聚合，接口把结果整理成前端直接可用的结构")
txt(s, LEFT, BODY, 6.0, 0.3, [dict(text="bi_cube 实测参数", size=14.5, bold=True, color=GREEN)])
rows = [
    ["项目", "实测值"],
    ["Kylin 项目", "yiyao"],
    ["Cube 名称", "bi_cube"],
    ["构建状态", "READY"],
    ["维度与度量", "8 维 2 度量"],
    ["Cuboid 数量", "256"],
    ["Cube 体积", "2.95 GB"],
    ["构建耗时", "23.13 分钟"],
]
th = make_table(s, LEFT, BODY + 0.36, 6.0, [0.42, 0.58], rows, font=13.5, head_font=13.5,
                row_h=0.4, head_h=0.42, aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT])
txt(s, LEFT, BODY + 0.36 + th + 0.2, 6.0, 0.6,
    [dict(text="以上七项数值取自 Kylin 界面与 cube_info.py 的输出，第 22 页有对应截图",
          size=12.5, color=MUTED, ls=1.24)])
txt(s, 6.9, BODY, 5.8, 0.3, [dict(text="接口实测耗时", size=14.5, bold=True, color=GREEN)])
rows2 = [
    ["接口", "耗时"],
    ["/home/overview", "0.61 秒"],
    ["/home/citylevel", "2.0 秒"],
    ["/home/top10", "5.97 秒"],
    ["/drug/hospital", "7.91 秒"],
    ["/disease/section", "9.81 秒"],
    ["/drug/diseases", "15.44 秒"],
    ["/disease/drug", "15.74 秒"],
]
th2 = make_table(s, 6.9, BODY + 0.36, 5.8, [0.62, 0.38], rows2, font=13.5, head_font=13.5,
                 row_h=0.4, head_h=0.42, aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
by = BODY + 0.36 + th2 + 0.18
rect(s, 6.9, by, 5.8, 0.84, fill=GREEN_LT, line=GREEN, lw=0.75)
txt(s, 7.1, by + 0.1, 5.4, 0.28, [dict(text="验收口径", size=13.5, bold=True, color=GREEN)])
txt(s, 7.1, by + 0.4, 5.4, 0.36,
    [dict(text="单表聚合不超过 2 秒，多表关联不超过 20 秒，13 个接口全部满足",
          size=13, color=BODY_TXT)])
footer(s, 18)

# ================================================================ 19 部署方式
s = new_slide()
header(s, "04　实施过程与方法", "部署方式：目录结构与启动自检",
       "脚本放在 /opt 下，可反复执行，不会重复拉起进程")
txt(s, LEFT, BODY, 5.9, 0.3, [dict(text="服务器目录结构", size=14.5, bold=True, color=GREEN)])
tree = [
    ("/home/medicine-analysis", "项目根目录"),
    ("├ backend/yiyao", "服务源码与 jar"),
    ("├ frontend", "Vue 源码与构建产物"),
    ("├ screen", "Django 大屏"),
    ("├ deploy/sql", "建表与聚合脚本"),
    ("└ deploy/scripts", "启停与状态自检"),
]
ty0 = BODY + 0.36
for i, (path, desc) in enumerate(tree):
    yy = ty0 + i * 0.3
    if i % 2 == 0:
        rect(s, LEFT, yy - 0.02, 5.9, 0.28, fill=SOFT)
    txt(s, LEFT + 0.1, yy, 2.8, 0.26, [dict(text=path, size=11.5, bold=True, color=INK, font=MONO)])
    txt(s, LEFT + 3.05, yy + 0.02, 2.75, 0.24, [dict(text=desc, size=11.5, color=MUTED)])
shot(s, LEFT, ty0 + 1.92, 5.9, 2.5, "截图位 08　一键启动输出",
     "在平台终端执行 bash /opt/start-all.sh 后截图", size=11)
txt(s, 6.75, BODY, 5.96, 0.3, [dict(text="脚本执行的三个动作", size=14.5, bold=True, color=GREEN)])
steps3 = [
    ("检测", "六个集群端口与 MySQL 逐个探测，已在跑的直接跳过"),
    ("拉起", "后端以 nohup 启动，轮询 /home/overview 直到返回 200"),
    ("自检", "13 个接口逐个请求，打印状态码与耗时，失败项标红"),
]
sy = BODY + 0.36
for i, (k, v) in enumerate(steps3):
    rect(s, 6.75, sy, 5.96, 0.88, fill=SOFT, line=LINE, lw=0.7)
    txt(s, 6.95, sy + 0.1, 0.9, 0.26, [dict(text="步骤" + "一二三"[i], size=11.5, bold=True, color=GOLD)])
    txt(s, 6.95, sy + 0.34, 0.95, 0.32, [dict(text=k, size=16, bold=True, color=INK)])
    txt(s, 8.0, sy + 0.22, 4.5, 0.56, [dict(text=v, size=13, color=MUTED, ls=1.2)])
    sy += 0.96
rect(s, 6.75, 5.1, 5.96, 1.56, fill=BLUE_LT, line=BLUE, lw=0.75)
txt(s, 6.95, 5.2, 5.5, 0.28, [dict(text="处理过的一次端口占用问题", size=13.5, bold=True, color=BLUE)])
txt(s, 6.95, 5.5, 5.5, 1.06,
    [dict(text="重新编译后 83 端口仍在监听，脚本判定无需启动，新接口返回 404。"
               "现在比对 jar 与进程的修改时间，jar 更新就自动重启。", size=13, color=BODY_TXT, ls=1.26)])
footer(s, 19)

# ================================================================ 20 状态检查
s = new_slide()
header(s, "04　实施过程与方法", "运行状态检查脚本",
       "env-status.sh 只读不写，不动任何进程，随时可以跑")
txt(s, LEFT, BODY, 5.9, 0.3, [dict(text="九个端口逐项检查", size=14.5, bold=True, color=GREEN)])
for i, (port, name) in enumerate(checks):
    x = LEFT + (i % 3) * 1.95
    y = BODY + 0.38 + (i // 3) * 0.58
    rect(s, x, y, 1.85, 0.48, fill=SOFT, line=LINE, lw=0.6)
    txt(s, x + 0.14, y + 0.1, 0.8, 0.28, [dict(text=port, size=13, bold=True, color=GREEN, font=MONO)])
    txt(s, x + 0.86, y + 0.11, 0.95, 0.26, [dict(text=name, size=11.5, color=MUTED)])
shot(s, LEFT, BODY + 2.3, 5.9, 2.28, "截图位 09　状态检查输出",
     "执行 bash /opt/env-status.sh 后截图，含端口、数据、接口三段", size=11)
txt(s, 6.75, BODY, 5.96, 0.3, [dict(text="四个运维脚本", size=14.5, bold=True, color=GREEN)])
tools = [
    ("start-all.sh", "拉起全部服务并自检"),
    ("env-status.sh", "只查状态，几秒出结果"),
    ("cube_info.py", "读取 Cube 体积与构建耗时"),
    ("dump_baseline.py", "导出十一项基准值供复核"),
]
ty = BODY + 0.36
for k, v in tools:
    rect(s, 6.75, ty, 5.96, 0.78, fill=SOFT, line=LINE, lw=0.7)
    txt(s, 6.95, ty + 0.1, 5.5, 0.28, [dict(text=k, size=13.5, bold=True, color=GREEN, font=MONO)])
    txt(s, 6.95, ty + 0.42, 5.5, 0.28, [dict(text=v, size=12.5, color=MUTED)])
    ty += 0.86
rect(s, 6.75, 5.62, 5.96, 1.04, fill=GOLD_LT, line=GOLD, lw=0.75)
txt(s, 6.95, 5.72, 5.5, 0.28, [dict(text="检查项写在脚本里", size=13.5, bold=True, color=GOLD)])
txt(s, 6.95, 6.02, 5.5, 0.56,
    [dict(text="换人接手时跑一遍即可知道系统状态，不依赖记忆", size=13, color=BODY_TXT, ls=1.24)])
footer(s, 20)

# ================================================================ 21 数据流向
s = new_slide()
header(s, "05　技术原理与架构", "数据流向：一条请求从表到页面经过六步",
       "每一步都标了真实的数据量与耗时，接口如何选路写在下半页")
nodes = [
    ("MySQL 业务表", ["六张表", "100 万行"]),
    ("HDFS 与 Hive", ["bi_data/mysql", "6 个目录"]),
    ("Kylin 预计算", ["256 个 cuboid", "2.95 GB"]),
    ("四张 agg 表", ["4 万至 100 万行", "9 个索引"]),
    ("13 个接口", ["0.61 至 15.74 秒", "全部 200"]),
    ("三套页面", ["12 张图表", "83 与 8000"]),
]
nw = (CW - 5 * 0.28) / 6
for i, (name, rows2) in enumerate(nodes):
    x = LEFT + i * (nw + 0.28)
    rect(s, x, BODY, nw, 1.34, fill=GREEN if i % 2 == 0 else BLUE)
    txt(s, x + 0.12, BODY + 0.12, nw - 0.24, 0.3, [dict(text=name, size=13, bold=True, color=WHITE, ls=1.1)])
    txt(s, x + 0.12, BODY + 0.56, nw - 0.24, 0.7,
        [dict(text=r, size=11, color=RGBColor(0xEC, 0xF3, 0xEF), ls=1.2) for r in rows2])
    if i < 5:
        txt(s, x + nw + 0.02, BODY + 0.52, 0.24, 0.28,
            [dict(text="→", size=16, bold=True, color=MUTED, align=PP_ALIGN.CENTER)])

txt(s, LEFT, 3.3, CW, 0.3, [dict(text="接口取数的两条路径", size=14.5, bold=True, color=GREEN)])
paths = [
    ("路径一　命中 Cube", GREEN, "5 个接口", "低基数维度直接组合，不查明细表",
     "0.61 秒到 2 秒"),
    ("路径二　转 MySQL", BLUE, "8 个接口", "先查汇总表，再走索引关联维表取名称",
     "5 秒到 15.74 秒"),
]
pw = (CW - 0.3) / 2
for i, (name, color, cnt, desc, cost) in enumerate(paths):
    x = LEFT + i * (pw + 0.3)
    rect(s, x, 3.66, pw, 1.16, fill=WHITE, line=color, lw=1.0)
    rect(s, x, 3.66, 0.06, 1.16, fill=color)
    txt(s, x + 0.26, 3.76, 3.0, 0.3, [dict(text=name, size=14, bold=True, color=color)])
    txt(s, x + 3.3, 3.72, 1.6, 0.34, [dict(text=cnt, size=15, bold=True, color=INK, align=PP_ALIGN.RIGHT)])
    txt(s, x + 0.26, 4.12, pw - 0.5, 0.4, [dict(text=desc, size=12, color=BODY_TXT)])
    txt(s, x + 0.26, 4.5, pw - 0.5, 0.28, [dict(text="实测 " + cost, size=11.5, color=MUTED)])

rect(s, LEFT, 5.0, CW, 1.7, fill=SOFT, line=LINE, lw=0.75)
txt(s, LEFT + 0.28, 5.1, CW - 0.5, 0.28,
    [dict(text="页面怎么拿到这些数", size=13.5, bold=True, color=INK)])
facts = [
    "接口返回统一包一层成功标记与数据体，前端按数据体取数，失败时给出错误提示",
    "对象字段名统一转成首字母大写再下发，前端组件按固定字段名渲染，不用逐页适配",
    "图表组件只做渲染，取数逻辑集中在每个组件的 load 方法，搜索时重新调用一次",
]
fy = 5.44
for t in facts:
    txt(s, LEFT + 0.28, fy, CW - 0.6, 0.3, [dict(text="· " + t, size=12, color=MUTED)])
    fy += 0.32
footer(s, 21)

# ================================================================ 22 Kylin 与 Cube
s = new_slide()
header(s, "05　技术原理与架构", "Kylin 建模与 Cube 构建",
       "八列维度、两个度量，构建一次约 23 分钟，页面上的聚合直接读它")
txt(s, LEFT, BODY, 5.4, 0.3, [dict(text="建模参数，取自 Kylin 界面", size=14, bold=True, color=GREEN)])
rows = [
    ["项目", "取值"],
    ["Kylin 项目", "yiyao"],
    ["Cube 名称", "bi_cube"],
    ["状态", "READY"],
    ["维度", "8 个"],
    ["度量", "SUM(PRICE) 与 SUM(AMOUNT)"],
    ["Cuboid", "256"],
    ["体积", "2.95 GB"],
    ["构建耗时", "23.13 分钟"],
]
make_table(s, LEFT, BODY + 0.34, 5.4, [0.34, 0.66], rows, font=12.5, head_font=12.5,
           row_h=0.4, head_h=0.42, aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT])
txt(s, LEFT, BODY + 0.34 + 0.42 + 8 * 0.4 + 0.16, 5.4, 0.9,
    [dict(text="八个维度：年龄、性别、年月、医院、科室、职称、支付方式、数据类型",
          size=11, color=MUTED, ls=1.24)])
shot(s, 6.35, BODY, 6.36, 2.2, "截图位 06　Kylin 模型详情",
     "Kylin 界面 yiyao 项目下 bi_cube，要能看到 READY 与维度度量列表", size=11)
shot(s, 6.35, BODY + 2.36, 6.36, 2.2, "截图位 07　构建历史或 cuboid 列表",
     "同一页面的 Cuboids 页签或 Build 页签，要能看到构建时间与 256 个 cuboid", size=11)
footer(s, 22)

# ================================================================ 23 引擎切换
s = new_slide()
header(s, "05　技术原理与架构", "查询引擎切换与 SQL 改写",
       "业务 SQL 只维护一份，改写规则集中在网关，切换只改一个配置项")
rect(s, LEFT, BODY, CW, 0.9, fill=SOFT, line=LINE, lw=0.75)
txt(s, LEFT + 0.3, BODY + 0.1, 2.0, 0.26, [dict(text="配置项", size=12, bold=True, color=MUTED)])
txt(s, LEFT + 0.3, BODY + 0.4, 4.4, 0.32,
    [dict(text="query.engine = kylin | mysql", size=16, bold=True, color=GREEN, font=MONO)])
txt(s, LEFT + 5.4, BODY + 0.14, 6.4, 0.62,
    [dict(text="切换时业务代码不改动，Kylin 不可用时改一行配置即可回到 MySQL",
          size=13, color=MUTED, ls=1.22)])
txt(s, LEFT, BODY + 1.1, 6.0, 0.3, [dict(text="SQL 改写规则，五条", size=14, bold=True, color=GREEN)])
rows = [
    ["原写法", "改写后"],
    ["BIGDATA.PRESCRIPTION_DISEASES", "prescription_diseases"],
    ["M_DIAGNOSTIC", "m_diagnostic1"],
    ["PRESCRIPTION_DISEASES.AGE", "m_age"],
    ["M_DRUG = DRUG.DRUG", "DRUG_CODE = DRUG.DRUG"],
    ["VARCHAR", "CHAR"],
]
th = make_table(s, LEFT, BODY + 1.44, 6.0, [0.56, 0.44], rows, font=12, head_font=12,
                row_h=0.42, head_h=0.42)
txt(s, 6.9, BODY + 1.1, 5.8, 0.3, [dict(text="需要改写的原因", size=14, bold=True, color=GREEN)])
reasons = [
    ("表名", "课程 SQL 按数仓命名引用表，Kylin 侧映射到已建模型"),
    ("字段", "Kylin 维度列与业务表列名不同，需要一一对齐"),
    ("类型", "Kylin 不支持 VARCHAR，统一改为 CHAR"),
]
ry = BODY + 1.44
for k, v in reasons:
    rect(s, 6.9, ry, 5.8, 0.62, fill=SOFT, line=LINE, lw=0.65)
    txt(s, 7.1, ry + 0.15, 0.9, 0.28, [dict(text=k, size=13, bold=True, color=GREEN)])
    txt(s, 7.95, ry + 0.13, 4.6, 0.38, [dict(text=v, size=12.5, color=BODY_TXT)])
    ry += 0.7
by = BODY + 1.44 + th + 0.16
rect(s, LEFT, by, 6.0, 0.9, fill=GREEN_LT, line=GREEN, lw=0.75)
txt(s, LEFT + 0.2, by + 0.1, 5.6, 0.26, [dict(text="实测分布", size=12, bold=True, color=GREEN)])
txt(s, LEFT + 0.2, by + 0.38, 5.6, 0.42,
    [dict(text="13 个接口中 5 个由 Cube 直接回答，8 个转 MySQL 索引关联", size=11.5, color=BODY_TXT, ls=1.2)])
rect(s, 6.9, by, 5.8, 0.9, fill=GOLD_LT, line=GOLD, lw=0.75)
txt(s, 7.1, by + 0.1, 5.4, 0.26, [dict(text="为什么不再加维度", size=12, bold=True, color=GOLD)])
txt(s, 7.1, by + 0.38, 5.4, 0.42,
    [dict(text="八维已是 256 个 cuboid、23 分钟；医院与科室基数大，进 Cube 会让构建时间不可接受",
          size=11.5, color=BODY_TXT, ls=1.2)])
footer(s, 23)

# ================================================================ 24 分工与进度
s = new_slide()
header(s, "06　组织与管理", "人员分工与进度安排", "五天排期，每天有明确产出")
rows = [
    ["成员", "角色", "承担工作", "交付物"],
    ["占竞", "组长", "架构设计、Kylin 建模、后端接口", "13 个接口与查询网关"],
    ["李艺淼", "数据", "数据清洗、Cube 构建、可视化大屏", "bi_cube 与 Django 大屏"],
    ["付悌安", "前端", "三套页面、图表组件、结构对比模块", "12 张图表与对比表"],
    ["杨博文", "文档", "需求规格、部署验收、数据集与基准值", "五份文档"],
    ["洪嘉伟", "测试", "接口性能、数据一致性、验收用例", "测试用例与校验脚本"],
]
th = make_table(s, LEFT, BODY, CW, [0.1, 0.09, 0.48, 0.33], rows, font=13.5, head_font=13.5,
                row_h=0.5, head_h=0.48)
txt(s, LEFT, BODY + th + 0.24, CW, 0.3, [dict(text="五天进度与当日产出", size=14.5, bold=True, color=GREEN)])
days = [("11-11", "环境搭建", "六组件端口全通"), ("11-12", "数据入仓", "六张表一百万行"),
        ("11-13", "维度建模", "bi_cube READY"), ("11-14", "接口与前端", "13 接口与三页"),
        ("11-15", "联调验收", "基准值与文档")]
dw = (CW - 0.4 * 4) / 5
dy = BODY + th + 0.6
for i, (d, name, out) in enumerate(days):
    x = LEFT + i * (dw + 0.4)
    rect(s, x, dy, dw, 1.24, fill=GREEN if i < 4 else GOLD)
    txt(s, x + 0.16, dy + 0.1, dw - 0.3, 0.26,
        [dict(text=d, size=12, bold=True, color=RGBColor(0xDD, 0xEA, 0xE1))])
    txt(s, x + 0.16, dy + 0.38, dw - 0.3, 0.34, [dict(text=name, size=15.5, bold=True, color=WHITE)])
    txt(s, x + 0.16, dy + 0.76, dw - 0.3, 0.4,
        [dict(text=out, size=12, color=RGBColor(0xF0, 0xF6, 0xF2), ls=1.2)])
footer(s, 24)

# ================================================================ 25 总结
s = new_slide()
header(s, "07　总结", "完成情况与后续计划", "已完成项均可复核，后续计划按优先级排列")
txt(s, LEFT, BODY, 5.9, 0.3, [dict(text="已完成并可复核", size=15, bold=True, color=GREEN)])
done = [
    "六节点集群与 13 个接口在 192.168.207.179 上持续运行",
    "bi_cube 8 维 2 度量 256 个 cuboid，构建耗时 23.13 分钟",
    "四张预聚合表上线，疾病 42,501 行、药品 205,971 行",
    "三套页面共 12 张图表，数据全部来自后端接口",
    "五份交付文档与四个运维脚本，检查项可重复执行",
]
dy0 = BODY + 0.36
for it in done:
    rect(s, LEFT, dy0, 5.9, 0.66, fill=SOFT, line=LINE, lw=0.65)
    rect(s, LEFT + 0.18, dy0 + 0.26, 0.1, 0.1, fill=GREEN, shape=MSO_SHAPE.OVAL)
    txt(s, LEFT + 0.42, dy0 + 0.13, 5.3, 0.46, [dict(text=it, size=12.5, color=BODY_TXT, ls=1.16)])
    dy0 += 0.74
txt(s, 6.9, BODY, 5.8, 0.3, [dict(text="后续计划", size=15, bold=True, color=BLUE)])
plan = [
    ("第一项", "按科室维度扩展预聚合表，覆盖更多组合"),
    ("第二项", "接入按月增量构建，把单月数据扩展为多个月"),
    ("第三项", "13 个接口纳入自动化测试，改一次跑一遍"),
    ("第四项", "基准值校验接入启动脚本，每次部署自动比对"),
]
py = BODY + 0.36
for k, v in plan:
    rect(s, 6.9, py, 5.8, 0.86, fill=BLUE_LT, line=BLUE, lw=0.7)
    txt(s, 7.1, py + 0.1, 1.0, 0.26, [dict(text=k, size=11.5, bold=True, color=BLUE)])
    txt(s, 7.1, py + 0.38, 5.3, 0.42, [dict(text=v, size=13, color=BODY_TXT, ls=1.18)])
    py += 0.96
rect(s, LEFT, 6.26, CW, 0.6, fill=GREEN)
txt(s, LEFT + 0.3, 6.38, CW - 0.6, 0.3,
    [dict(text="系统地址 http://192.168.207.179:83/　大屏 http://192.168.207.179:8000/　代码与文档已提交",
          size=14, bold=True, color=WHITE)])
footer(s, 25)

out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "目标适应症及用药数据分析系统_汇报PPT.pptx")
prs.save(out_path)
print("saved:", out_path)
print("slides:", len(prs.slides._sldIdLst))
