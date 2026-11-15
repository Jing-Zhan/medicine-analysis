# -*- coding: utf-8 -*-
"""生成《项目实训总结报告》：基于下发模板的分部分结构，重新排正文与图表。"""
import os
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figs")
DELIV = os.path.join(FIGDIR, "deliver")
SHOT = os.path.join(os.path.dirname(HERE), "ppt", "figures")
OUT = os.path.join(HERE, "项目实训总结报告-目标适应症及用药数据分析系统-终版.docx")

SONG = "宋体"
LATIN = "Times New Roman"
MONO = "Consolas"
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x59, 0x59, 0x59)

TEXT_W = 15.4          # 正文栏宽，单位厘米
FIG_NO = 0
TAB_NO = 0
EQ_NO = 0


# ---------------------------------------------------------------- 基础工具
def set_font(run, size=12, bold=False, italic=False, mono=False, color=None):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    if color is not None:
        f.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    if mono:
        rFonts.set(qn("w:ascii"), MONO)
        rFonts.set(qn("w:hAnsi"), MONO)
        rFonts.set(qn("w:cs"), MONO)
    else:
        rFonts.set(qn("w:ascii"), LATIN)
        rFonts.set(qn("w:hAnsi"), LATIN)
        rFonts.set(qn("w:cs"), LATIN)
    rFonts.set(qn("w:eastAsia"), SONG)
    return run


CITE = re.compile(r"\{\{([0-9,\-]+)\}\}")


def runs(p, text, size=12, bold=False, italic=False, color=None):
    """支持 **加粗** 与 {{n}} 上标引文两种内联标记。"""
    pos = 0
    for m in CITE.finditer(text):
        head = text[pos:m.start()]
        for k, seg in enumerate(re.split(r"\*\*(.+?)\*\*", head)):
            if seg:
                r = p.add_run(seg)
                set_font(r, size=size, bold=bold or (k % 2 == 1), italic=italic, color=color)
        r = p.add_run("[" + m.group(1) + "]")
        set_font(r, size=size - 1, bold=False, color=color)
        r.font.superscript = True
        pos = m.end()
    tail = text[pos:]
    for k, seg in enumerate(re.split(r"\*\*(.+?)\*\*", tail)):
        if seg:
            r = p.add_run(seg)
            set_font(r, size=size, bold=bold or (k % 2 == 1), italic=italic, color=color)
    return p


def P(text, indent=True, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=0,
      ls=1.1, bold=False, keep=False, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = ls
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.first_line_indent = Pt(24) if indent else None
    pf.keep_with_next = keep
    p.alignment = align
    runs(p, text, size=size, bold=bold, color=color)
    return p


def H1(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(14)
    pf.space_after = Pt(8)
    pf.line_spacing = 1.1
    pf.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_font(r, size=15, bold=True)
    pPr = p._p.get_or_add_pPr()
    lvl = OxmlElement("w:outlineLvl")
    lvl.set(qn("w:val"), "0")
    pPr.append(lvl)
    return p


def H2(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(10)
    pf.space_after = Pt(4)
    pf.line_spacing = 1.1
    pf.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    set_font(r, size=13, bold=True)
    pPr = p._p.get_or_add_pPr()
    lvl = OxmlElement("w:outlineLvl")
    lvl.set(qn("w:val"), "1")
    pPr.append(lvl)
    return p


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def cell_border(cell, edge, sz, color="000000"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcPr.append(borders)
    el = OxmlElement("w:" + edge)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), color)
    borders.append(el)


def _insert_pr(tblPr, el, *successors):
    try:
        tblPr.insert_element_before(el, *successors)
    except Exception:
        tblPr.append(el)


def table_borders(table, top=12, bottom=12):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", top), ("bottom", bottom), ("left", 0), ("right", 0),
                     ("insideH", 0), ("insideV", 0)):
        el = OxmlElement("w:" + edge)
        if sz:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "000000")
        else:
            el.set(qn("w:val"), "none")
            el.set(qn("w:sz"), "0")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "auto")
        borders.append(el)
    _insert_pr(tblPr, borders, "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook")


def cell_margins(table, top=30, bottom=30, left=80, right=80):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for edge, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:w"), str(v))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    _insert_pr(tblPr, mar, "w:tblLook")


def CODE(lines, caption=None):
    """灰色底纹代码块，行距固定 12 磅。"""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tbl = t._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "D9D9D9")
        borders.append(el)
    _insert_pr(tblPr, borders, "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook")
    cell_margins(t, top=70, bottom=70, left=140, right=140)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))
    cell = t.cell(0, 0)
    cell.width = Cm(TEXT_W)
    shade(cell, "F5F5F5")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        pf.line_spacing = Pt(12)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.first_line_indent = None
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(line if line.strip() else " ")
        set_font(r, size=10, mono=True)
    if caption:
        P(caption, indent=False, size=10, align=WD_ALIGN_PARAGRAPH.LEFT, before=2, after=8, ls=1.1,
          color=GREY)
    else:
        P("", indent=False, size=9, after=4, ls=1.0)
    return t


def TBL(caption, header, rows, widths, aligns=None, size=10.5, first_col_left=False):
    global TAB_NO
    TAB_NO += 1
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = None
    cap.paragraph_format.space_before = Pt(10)
    cap.paragraph_format.space_after = Pt(3)
    cap.paragraph_format.keep_with_next = True
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run("表 %d　%s" % (TAB_NO, caption))
    set_font(r, size=size, bold=True)

    n_row = len(rows) + 1
    n_col = len(header)
    t = doc.add_table(rows=n_row, cols=n_col)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t)
    cell_margins(t, top=40, bottom=40)
    if aligns is None:
        aligns = [WD_ALIGN_PARAGRAPH.CENTER] * n_col

    for ci, w in enumerate(widths):
        for row in t.rows:
            row.cells[ci].width = Cm(w)

    nrow = len(t.rows)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            trPr.append(OxmlElement("w:tblHeader"))

    for ri, values in enumerate([header] + rows):
        for ci, val in enumerate(values):
            cell = t.cell(ri, ci)
            cell.paragraphs[0].paragraph_format.keep_with_next = (ri == 0 and nrow > 2)
            cell.paragraphs[0].paragraph_format.first_line_indent = None
            cell.paragraphs[0].paragraph_format.line_spacing = 1.0
            cell.paragraphs[0].paragraph_format.space_before = Pt(0)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            cell.paragraphs[0].alignment = aligns[ci]
            r = cell.paragraphs[0].add_run(str(val))
            set_font(r, size=size, bold=(ri == 0))
            if ri == 0:
                cell_border(cell, "bottom", 8)
    # 表后留白
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.first_line_indent = None
    r = p.add_run("")
    set_font(r, size=6)
    return t


def FIG(name, caption, width=TEXT_W, folder=None):
    global FIG_NO
    FIG_NO += 1
    path = os.path.join(folder or FIGDIR, name)
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(6)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(width))
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = None
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.line_spacing = 1.0
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run("图 %d　%s" % (FIG_NO, caption))
    set_font(r, size=10.5)
    return p




APP_NO = 0


def FIGA(name, caption, width=TEXT_W):
    global APP_NO
    APP_NO += 1
    path = os.path.join(FIGDIR, "deliver", name)
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(6)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(width))
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = None
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.line_spacing = 1.0
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run("附图 %d　%s" % (APP_NO, caption))
    set_font(r, size=10.5)
    return p


def EQ(expr, no=True):
    """公式居中，编号右对齐。expr 中用 _{..} 与 ^{..} 表示上下标。"""
    global EQ_NO
    EQ_NO += 1
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(4)
    pf.space_after = Pt(4)
    pf.line_spacing = 1.3
    pf.tab_stops.add_tab_stop(Cm(TEXT_W / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Cm(TEXT_W - 0.2), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run("\t")
    set_font(r, size=12)
    parts = re.split(r"(_\{[^}]*\}|\^\{[^}]*\})", expr)
    for seg in parts:
        if not seg:
            continue
        if seg.startswith("_{"):
            r = p.add_run(seg[2:-1])
            set_font(r, size=12, italic=True)
            r.font.subscript = True
        elif seg.startswith("^{"):
            r = p.add_run(seg[2:-1])
            set_font(r, size=12, italic=True)
            r.font.superscript = True
        else:
            r = p.add_run(seg)
            set_font(r, size=12, italic=True)
    if no:
        r = p.add_run("\t（%d）" % EQ_NO)
        set_font(r, size=12)
    return p


def add_field(paragraph, instr, size=9):
    r1 = paragraph.add_run()
    set_font(r1, size=size)
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    r1._r.append(fld1)

    r2 = paragraph.add_run()
    set_font(r2, size=size)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r2._r.append(it)

    r3 = paragraph.add_run()
    set_font(r3, size=size)
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    r3._r.append(fld2)

    r4 = paragraph.add_run("1")
    set_font(r4, size=size)

    r5 = paragraph.add_run()
    set_font(r5, size=size)
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    r5._r.append(fld3)


# ---------------------------------------------------------------- 文档骨架
doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.8)
sec.right_margin = Cm(2.8)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)
sec.header_distance = Cm(1.5)
sec.footer_distance = Cm(1.6)
sec.different_first_page_header_footer = True

normal = doc.styles["Normal"]
normal.font.size = Pt(12)
normal.font.name = LATIN
normal.element.rPr.rFonts.set(qn("w:eastAsia"), SONG)

# 页眉
hp = sec.header.paragraphs[0]
hp.paragraph_format.first_line_indent = None
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = hp.add_run("实训总结报告")
set_font(r, size=9, color=GREY)
pPr = hp._p.get_or_add_pPr()
pbdr = OxmlElement("w:pBdr")
bottom = OxmlElement("w:bottom")
bottom.set(qn("w:val"), "single")
bottom.set(qn("w:sz"), "6")
bottom.set(qn("w:space"), "1")
bottom.set(qn("w:color"), "999999")
pbdr.append(bottom)
pPr.append(pbdr)

# 页脚
fp = sec.footer.paragraphs[0]
fp.paragraph_format.first_line_indent = None
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run("- ")
set_font(r, size=9)
add_field(fp, " PAGE ")
r = fp.add_run(" -")
set_font(r, size=9)

# 封面页眉页脚留空
for part in (sec.first_page_header, sec.first_page_footer):
    part.paragraphs[0].text = ""


# ---------------------------------------------------------------- 封面
def cover_line(text, size, bold=False, before=0, after=0, ls=1.0, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = None
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = ls
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, text, size=size, bold=bold, color=color)
    return p


cover_line("", 12, before=0, after=0)
cover_line("项目实训总结报告", 34, bold=True, before=26, after=8)
cover_line("目标适应症及用药数据分析系统", 18, before=0, after=4)
cover_line("数据实训　2026 年 11 月 11 日至 11 月 15 日", 11.5, before=0, after=26, color=GREY)

info = [("题　　目", "目标适应症及用药数据分析系统"),
        ("学　　院", ""),
        ("专　　业", "软件工程"),
        ("班　　级", ""),
        ("学　　生", "占竞"),
        ("学　　号", ""),
        ("指导教师", "")]
ct = doc.add_table(rows=len(info), cols=2)
ct.alignment = WD_TABLE_ALIGNMENT.CENTER
ct.autofit = False
table_borders(ct, top=0, bottom=0)
cell_margins(ct, top=0, bottom=0, left=100, right=100)
for ri, (k, v) in enumerate(info):
    row = ct.rows[ri]
    row.height = Cm(1.0)
    c0, c1 = row.cells
    c0.width = Cm(3.4)
    c1.width = Cm(8.6)
    p0 = c0.paragraphs[0]
    p0.paragraph_format.first_line_indent = None
    p0.paragraph_format.line_spacing = 1.0
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p0.add_run(k + "：")
    set_font(r, size=14, bold=True)
    p1 = c1.paragraphs[0]
    p1.paragraph_format.first_line_indent = None
    p1.paragraph_format.line_spacing = 1.0
    p1.paragraph_format.space_before = Pt(2)
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p1.add_run(v if v else "　")
    set_font(r, size=14)
    cell_border(c1, "bottom", 6)

cover_line("2026 年 11 月", 14, before=26, after=0)

# 封面底部配图
p = doc.add_paragraph()
pf = p.paragraph_format
pf.first_line_indent = None
pf.space_before = Pt(20)
pf.space_after = Pt(0)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(os.path.join(FIGDIR, "cover-band.jpg"), width=Cm(TEXT_W))

doc.add_page_break()

# ---------------------------------------------------------------- 正文信息块
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("学院　******* 学院　　　专业　软件工程　　　班级　*******")
set_font(r, size=12)
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("学生　占竞　　　　　　　　学号　*******　　　指导教师　*******")
set_font(r, size=12)
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = None
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(10)
r = p.add_run("设计题目　目标适应症及用药数据分析系统")
set_font(r, size=12)

# ================================================================ 一、选题背景与意义
H1("一、选题背景与意义")
H2("（一）选题目的及意义")
P("本次实训下发 6 个原始文本文件，合计约 240MB，清洗后得到 100 万条处方记录。字段包括医院编号、"
  "医院等级、城市与省份、科室、医师职称、患者年龄与性别、药品通用名、诊断名称、支付方式、"
  "数据类型、处方金额与单价。这批数据能够回答的问题集中在四个方面：哪些适应症用药最集中，"
  "哪些药品贡献的金额最大，不同地区与科室的用药结构是否存在差异，年龄与性别如何影响用药。")
P("在原始文本上直接回答这些问题并不现实。文件按行存储，没有索引，没有统一的名称对照，"
  "同一家医院在不同文件中的编码写法也不完全一致。要把它们变成可以反复查询的指标，"
  "必须先完成三件事：把数据装进能够按列检索的存储，把业务问题翻译成维度与度量，"
  "把结果固定成统一结构的接口。这三件事连起来构成本项目的工作范围。")
P("系统的目标可以拆成四条。第一，把 100 万条原始记录导入可检索的明细库，行数与金额都能够核对。"
  "第二，按低基数维度建立立方体，验证预计算这条链路在本环境中能否走通。"
  "第三，提供 13 个数据接口，覆盖药品、适应症、区域、人群四个方向，返回结构统一。"
  "第四，用前端页面与可视化大屏呈现结果，页面显示的数字与数据库口径一致。")
P("这项工作的意义在三个层面。业务层面，100 万条记录被整理成 13 组可查询指标，"
  "原先需要人工统计的问题变成一次请求。技术层面，课堂上的 HDFS、Hive、HBase、Kylin、"
  "SpringBoot、Vue 与 Django 被串成一条能够跑通的链路，每个组件都在链路上承担明确职责，"
  "而不是并列罗列。团队层面，五个人在五天内完成从环境到验收的全过程，"
  "形成了一套可以复用的实施顺序、文档规范与检查清单，这套流程的复用价值不低于任何一个接口。")
P("需要说明项目的边界。下发的数据只覆盖 2008 年 12 月一个月，年月字段只有一个取值，"
  "趋势类分析无法展开；有 1,164 行处方的医院编号在区域维表中找不到对应记录，"
  "全表金额与按区域汇总的金额相差 31,686.68 元。这两点是数据本身的特征，与实现方式无关，"
  "第四章单独说明处理方式。")

H2("（二）国内外研究现状")
P("数据仓库领域目前以维度建模为主流方法{{1}}。它的基本做法是把业务过程抽象成事实表与维表，"
  "事实表记录发生了什么以及可累加的度量，维表保存描述性属性，查询时按维表上的属性对事实表分组汇总{{2}}。"
  "这种结构把数据组织成星型，事实表位于中心，维表分布在外围，优点是结构稳定、查询语义清晰，"
  "缺点是维度一多，按任意组合聚合的代价会随数据量线性上升，联机分析处理正是在这个矛盾上展开的{{3}}。")
P("为降低聚合代价，工程上出现了预计算思路。Apache Kylin 由 eBay 研发，2014 年 11 月进入 Apache 基金会"
  "孵化器，2015 年 12 月成为顶级项目{{4}}。它的核心是把多维组合提前物化，每一个维度组合对应一个 cuboid，"
  "构建阶段把所有需要的 cuboid 一次算好并写入存储，查询阶段先判断这次查询涉及哪些维度，"
  "再定位到对应的 cuboid 直接读取{{9}}。数据源通常取自 Hive，存储通常使用 HBase，构建引擎可以用 MapReduce "
  "或 Spark。同类的列式方案还有 Druid{{5}} 与 ClickHouse{{6}}，思路相近，都是以额外的存储空间与构建时间"
  "换取查询响应时间。")
P("国内在医药流通与医院信息化领域积累了大量处方数据，分析需求集中在合理用药监测、药品销售结构与"
  "疾病谱统计三个方向，药品不良反应监测年度报告每年汇总全国上报的病例，是这一类分析的主要数据来源之一{{7}}。"
  "在管理要求上，六部门联合印发的关于加强医疗机构药事管理促进合理用药的意见对处方审核、"
  "用药监测与处方点评提出了明确要求{{8}}，从制度上把处方数据从记录变成了需要持续分析的对象。"
  "早期做法以固定报表为主，报表口径写死在存储过程里，业务一旦要求换一个维度组合就要重新开发。"
  "近年来把维度建模与预计算引入业务分析逐渐常见，同时数据治理问题也暴露得更明显，"
  "主数据不统一、时间覆盖不足、维表缺失都会直接影响结论，这些问题在技术方案里没有位置，"
  "却决定了分析结果能不能用。")
P("本项目取的是这条主流路线，但没有完全照搬实训资料给出的通用步骤。资料给出的路线是把原始文件"
  "转成 SequenceFile 写入 HBase 作为明细存储，用 Hive 外部表映射，Kylin 选取全部字段建立方体，"
  "后端统一查询 Kylin，前端部署在独立容器。实际执行时遇到两处硬约束，一是 HBase 自带的 Hadoop "
  "客户端版本与集群不一致，批量导入无法完成；二是按全部字段建立方体会让维度组合达到千万级，"
  "不具备可行性，cuboid 数量随维度数按指数增长的规律在 Kylin 的建模文档中有明确说明{{9}}。"
  "因此把明细存储改为 HDFS 与 MySQL 双写，把立方体维度收缩到 8 个低基数维度，并在后端加入双引擎切换。"
  "这些调整在第三章逐项说明，它们是在本项目的环境与数据条件下能够跑通并被复核的选择，"
  "不构成对通用路线的否定。")

# ================================================================ 二、完成内容成果
H1("二、完成内容成果")
H2("（一）核心完成内容")
P("六个环节全部完成。环境搭建阶段把 ZooKeeper、HDFS、YARN、HBase、Hive、Kylin 六个组件"
  "与 MySQL、后端、大屏逐个拉起，13 个端口全部可探测；数据入仓阶段完成 6 个文本文件的解析与导入，"
  "明细库中处方记录 100 万行；维度建模阶段建立 8 维 2 度量立方体，"
  "构建状态 READY，体积 2.95GB；接口开发阶段完成 13 个数据接口与统一返回结构；"
  "前端与大屏阶段完成三套页面共 12 张图表与 5 张大屏子图；部署与验证阶段完成同源部署、"
  "一键启动脚本与 18 条测试用例。")
P("系统整体分为四层，如图 1 所示。最下层是原始文件与分布式存储，原始文件落在 HDFS 上，"
  "由 Hive 外部表映射成 6 张表并建立星型模型。第二层是存储与预计算，MySQL 保存明细与 9 个索引，"
  "Kylin 保存 8 维 2 度量的立方体，另有 7 张预聚合表承担科室用药结构这类固定口径的查询。"
  "第三层是服务层，SpringBoot 对外提供 13 个接口，所有取数请求经过同一个查询网关。"
  "最上层是应用层，Vue 三套页面通过 83 端口同源访问后端，Django 大屏在 8000 端口直连数据库取数。")
FIG("fig1-arch.png", "系统总体架构与数据流向", 15.0)

TBL("系统规模与完成情况",
    ["项目", "规模", "说明"],
    [["原始数据", "6 个文本文件，约 240MB", "竖线分隔，字段顺序一致"],
     ["处方记录", "1,000,000 行", "明细表，与 Hive 侧计数一致"],
     ["Hive 外部表", "6 张", "星型模型，映射 HDFS 目录"],
     ["明细库表与索引", "6 张表，9 个索引", "含 1 个去除后缀的生成列"],
     ["立方体", "8 维 2 度量，256 个 cuboid", "体积 2.95GB，状态 READY"],
     ["预聚合表", "7 张", "科室结构与画像口径"],
     ["后端接口", "13 个", "返回结构统一，全部 200"],
     ["前端图表", "12 张", "三套页面，取数经过接口"],
     ["大屏子图", "5 张", "Django 直连数据库"],
     ["测试用例", "18 条", "接口 13 条，大屏 5 条，全部通过"]],
    [3.6, 5.6, 6.2], aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
                              WD_ALIGN_PARAGRAPH.LEFT])

P("接口数量与页面数量在推进过程中有过变化。最初设计 12 个接口，验收前补充首页概览接口，形成 13 个；"
  "前端图表按页面统计为 12 张，大屏另有 5 张子图，两者取数方式不同，前者经过后端接口，"
  "后者由 Django 直连数据库。这类数量上的差异在文档里容易写错，我们用需求规格说明书与"
  "数据基准值两份文档固定口径，验收时以基准值为准。")

H2("（二）成果与实际交付")
P("系统部署在一台 Linux 虚拟机上，对外提供两个访问地址。83 端口由 SpringBoot 提供，"
  "前端产物打包在同一程序的静态目录下，页面与接口同源，因此不存在跨域配置；"
  "8000 端口由 Django 提供大屏。两个端口共用一个启动脚本，脚本先探测六个组件端口，"
  "缺哪个启动哪个，随后拉起后端与大屏，最后逐个请求 13 个接口并打印状态码与耗时。")
FIG("p-home.png", "首页实际运行画面，图中三个图表分别取自城市等级、年龄分布与药品前十接口", 14.4, folder=DELIV)
P("首页给出六个概览指标与四张分布图，适应症页与药品页分别按疾病和药品两个方向组织图表，"
  "药品页下半部分是按科室分组的三项占比对比。页面上的每个数字都来自接口，接口的数据来自数据库，"
  "不存在写死的示例值。适应症页的查询涉及四张表的关联，是本系统中查询代价最高的一类，"
  "页面上以加载提示的方式明确告知等待时间。")
P("适应症页以疾病为入口，顶部的搜索框按疾病名称过滤，下图是检索甲状腺肿之后的实际结果。"
  "左侧是疾病与药品的组合关系图，中间是联合用药的弦图，右侧是不同年龄人群的分布气泡图，"
  "三张图的数据来自同一分组接口，检索词改变时三张图同时刷新。")
FIG("p-disease.png", "适应症页实际运行画面，按甲状腺肿检索后的三张图", 14.4, folder=DELIV)
P("药品页在三张分布图之下增加了按科室分组的用药结构与厂商份额。左侧五个指标分别是"
  "注射剂使用率、基本药物使用率、抗菌药物使用率、非处方药占比与特殊管理药品占比，"
  "右侧是按金额排序的厂商份额前十，并给出厂商总数、前十集中度与赫芬达尔指数。"
  "这一块是本项目在原有工程之外补充的结构对比模块。")
FIG("p-drug.png", "药品页实际运行画面，含科室用药结构与厂商份额", 14.4, folder=DELIV)
TBL("13 个接口与实测耗时",
    ["接口路径", "分析内容", "耗时"],
    [["/home/overview", "首页概览指标", "0.61"],
     ["/home/citylevel", "城市等级竞争分析", "2.08"],
     ["/home/age", "年龄患病比例分析", "2.16"],
     ["/home/top10", "销售金额前十分析", "5.97"],
     ["/home/province", "各省份销售格局", "1.94"],
     ["/disease/union", "适应症与药品关联", "15.65"],
     ["/disease/drug", "药品关联关系图", "15.74"],
     ["/disease/age", "适应症年龄分布", "7.68"],
     ["/disease/section", "适应症科室分布", "9.81"],
     ["/drug/cities", "城市用药分布", "5.18"],
     ["/drug/hospital", "药品与医院等级分布", "7.91"],
     ["/drug/diseases", "药品对应适应症", "15.44"],
     ["/drug/section", "药品科室分布", "13.37"]],
    [5.2, 7.4, 2.8])

P("13 个接口全部返回 200，最快的首页概览接口 0.61 秒，最慢的目标适应症与药品关联接口 15.74 秒，"
  "平均 7.96 秒，中位数 7.68 秒。耗时差异由查询形状决定：只涉及事实表的聚合落在预计算或单表扫描上，"
  "需要按药品编码、诊断编码在维表中逐行探测的关联查询，代价随行数增长。"
  "重复运行存在秒级波动，表中的数值是数据基准值文档记录的一次完整运行结果。")

P("大屏使用同一份数据，以省份地图加四个子图的方式呈现，适合投屏讲解。地图需要把库中的省份全称"
  "映射成地图组件使用的简称，这一步在服务端完成，前端只接收可以直接渲染的名称与数值。")
FIG("p-screen.png", "可视化大屏实际运行画面，中部为省份地图，四周为五个子图", 14.6, folder=DELIV)

TBL("随项目提交的交付物",
    ["类别", "名称", "内容"],
    [["技术文档", "需求规格说明书", "13 个接口与 5 张大屏图的功能、返回字段、验收标准"],
     ["技术文档", "可行性分析报告", "技术、经济、操作三方面论证与查询路径分工依据"],
     ["技术文档", "数据基准值", "13 个接口与 6 项概览指标的实测数值"],
     ["技术文档", "部署与验收说明", "集群启动、数据准备、部署步骤、验收清单与故障记录"],
     ["技术文档", "数据集说明", "数据来源、导入方式、数据特征与口径差异"],
     ["技术文档", "环境架构说明", "组件关系、端口分配、数据流向与排查手册"],
     ["过程文档", "功能测试用例", "18 条用例、执行结果与缺陷记录"],
     ["过程文档", "答辩材料", "汇报提纲与逐页要点"],
     ["脚本与代码", "运维脚本 4 个", "一键启停与自检、状态检查、立方体信息、基准值抓取"],
     ["脚本与代码", "后端、前端、大屏", "SpringBoot、Vue 与 Django 三部分源码"]],
    [2.8, 4.6, 8.0],
    aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

P("交付物分为四类。技术文档 6 份、过程文档 2 份、运维脚本 4 个，代码包括后端、前端与大屏三部分，"
  "托管在同一仓库。所有文档中的关键数字都能从服务器上重新抓取，基准值抓取脚本可以复跑，"
  "因此文档与系统之间不会出现长期不一致。")

TBL("测试用例执行结果",
    ["类别", "用例数", "通过", "判定依据"],
    [["接口类", "13", "13", "返回状态 200，字段与基准值一致，无数据时返回空数组"],
     ["大屏类", "5", "5", "取数来源字段为数据库，数值与基准值一致"],
     ["合计", "18", "18", "全部用例通过"]],
    [2.6, 2.6, 2.6, 7.6])

P("18 条用例中接口类 13 条、大屏类 5 条，全部通过。接口类的判定依据是返回状态 200、"
  "字段与基准值一致、无数据时返回空数组而不是报错；大屏类的判定依据是取数来源字段为数据库。"
  "这一条是后期补上的，此前页面在查询超时后会回退到内置演示数据，外观与真实数据没有区别，"
  "验收时无法分辨，第四章说明处理过程。")

# ================================================================ 三、方案及过程
H1("三、方案及过程")
H2("（一）设计思路与方法")
P("整体思路是先定问题再定结构。13 个业务问题对应 13 个接口，接口需要哪些字段决定了建模需要"
  "哪些维度与度量，维度确定后才谈得上预计算的范围，预计算覆盖不到的部分由明细库承担。"
  "这条推导顺序决定了后面所有取舍，也解释了立方体为什么只有 8 个维度而不是全部字段。")
P("事实表选处方明细，一行代表一次处方，包含 9 个可分组字段与 2 个可累加度量。维表 5 张，"
  "分别是医院与区域、科室、药品、诊断与医师。事实表与维表之间通过编码关联，"
  "编码在原始文件中带有格式差异，例如明细表的药品编码带有序号后缀而维表中没有，"
  "这类差异在建模阶段统一处理。")
P("维度数量与立方体规模之间是指数关系。设维度数为 m，全部维度组合包含每一种维度取子集的情形，"
  "组合数等于各阶组合数之和：")
EQ("N = ∑_{k=0}^{m} C(m,k) = 2^{m}")
P("8 个维度对应 256 个 cuboid，实测构建耗时 23.13 分钟，体积 2.95GB，是输入中间表 60.95MB 的 54 倍。"
  "若按 13 个接口实际用到的 20 个字段建模，组合数为 1,048,576，构建时间与存储都不具备可行性。"
  "这是收缩维度的直接依据，也是把高基数关联交给关系型数据库的原因。")
P("立方体的 8 个维度全部取自事实表，分别是年龄、性别、年月、数据类型、支付方式、医师职称、"
  "科室、医院。药品编码与诊断编码没有进入立方体，两者在数据中的取值分别是 232,574 与 42,501，"
  "属于高基数，一旦进入立方体，维度组合与构建时间都会失控。需要按药品或诊断关联的查询共 8 个，"
  "改由 MySQL 承担，配合生成列与 9 个索引降低关联成本。查询路径的分工如图 6 所示。")
FIG("fig3-engine.png", "查询引擎切换与接口调用链路", 15.0)
P("指标口径在文档中统一定义，避免同一个词在不同页面含义不同。均次费用为金额合计除以处方数：")
EQ("c̄ = ( ∑_{i=1}^{n} A_{i} ) / n")
P("结构占比为某一分类的处方数除以该分组的总处方数，用于科室用药结构对比：")
EQ("p_{k} = n_{k} / n × 100%")
P("适应症与药品之间的关联强度用支持度、置信度与提升度三个量描述，N 为全局处方数，c 表示共现次数：")
EQ("s(d,g) = c(d,g) / N")
EQ("c(g|d) = c(d,g) / c(d)")
EQ("l(d,g) = c(g|d) ∕ ( c(g) / N )")
P("金额口径的一致性用差额描述，全表金额合计与按维表关联后的金额合计之差应当能够由具体行解释：")
EQ("Δ = | ∑_{i=1}^{N} A_{i} − ∑_{j=1}^{M} A'_{j} |")
P("与实训资料给出的通用路线相比，本项目有四处偏离，每一处都有明确原因，如表 5 所示。"
  "偏离集中在明细存储、立方体维度、查询路径与前端部署四个环节，共同点是优先保证链路能够跑通"
  "并且结果可复核，而不是形式上与资料一致。")
TBL("通用路线与本项目的四处偏离",
    ["环节", "通用路线", "本项目", "原因"],
    [["明细存储", "HBase", "HDFS 与 MySQL", "HBase 客户端版本与集群不一致，批量导入未能完成，"
                                          "改用 HDFS 加 Hive 外部表后结果与预期一致"],
     ["立方体维度", "全部字段", "8 个低基数维度", "维度数与 cuboid 数呈指数关系，"
                                            "20 个字段的组合数超过一百万，不具备可行性"],
     ["查询路径", "统一查询 Kylin", "双引擎按配置切换", "药品编码与诊断编码基数过高，"
                                                    "关联类查询由 MySQL 索引承担更稳定"],
     ["前端部署", "独立容器", "打包进后端同源提供", "前端请求构成跨域，改为同源后对外只有一个地址"]],
    [2.4, 3.0, 3.6, 6.4],
    aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
            WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("交付形态上还有一处选择，前端产物不单独部署容器，而是打包进后端程序的静态目录。"
  "这样页面与接口同源，对外只有一个地址，换机器部署时接口地址自动跟随。"
  "代价是前端更新需要重新打包后端，对五天周期的项目可以接受。")

H2("（二）关键实施过程")
P("实施按六个阶段推进，阶段之间存在依赖，前一阶段的产出是后一阶段的输入，如图 7 所示。")
FIG("fig2-stage.png", "六个阶段的实施流程与依赖关系", 15.2)
P("**环境搭建。** 平台提供的是一台 Linux 虚拟机，六个组件通过脚本按序启动，顺序为 ZooKeeper、"
  "HDFS、YARN、HBase、Hive metastore、Kylin。顺序不能随意调整，ZooKeeper 是其余组件的协调服务，"
  "HBase 依赖 HDFS，Kylin 依赖 Hive metastore 与 HBase。启动完成后逐个探测端口，"
  "任何一项不通都不进入下一阶段。脚本可以反复执行，已经在跑的组件直接跳过，"
  "避免重复拉起进程。")
CODE(["for p in 2181 9000 8088 16010 9083 7070; do",
      "  port_up $p || need_cluster=1",
      "done",
      "if [ $need_cluster -eq 0 ]; then",
      "  ok \"6 个组件端口全部在监听，跳过启动\"",
      "else",
      "  bash /opt/start-cluster.sh > /tmp/start-cluster.log 2>&1",
      "fi"],
     "代码 1　集群端口探测与按需启动，摘自 deploy/scripts/start-all.sh")
P("**数据入仓。** 原始文件为竖线分隔的文本，字段数与列顺序在 6 个文件中一致。先按下发材料执行"
  "建库建表脚本，再批量导入 6 个文件，最后核对行数。导入前的建表与导入后的核对各占一半工作量，"
  "前者决定字段类型是否够用，后者决定后续所有统计是否可信。")
CODE(["mysql -uroot -p123456 < sql.sql",
      "bash loadData.sh",
      "mysql -uroot -p123456 yiyao -e \"select 'prescription_diseases', count(*)",
      "  from prescription_diseases;\"",
      "hive -e \"select count(1) from bigdata.prescription_diseases\""],
     "代码 2　建库、导入与两侧行数核对")
P("处方明细表导入后为 1,000,000 行，Hive 侧的计数与 MySQL 侧一致。"
  "文本中残留的回车符会被带进科室名称一列，导致同一科室出现两种写法，"
  "这类问题在导入后用一条清洗语句统一处理，并在验收时检查返回的名称是否还带控制字符。")
P("**维度建模。** 立方体在 Kylin 界面中建立，数据源选 Hive 中的 bigdata 库，事实表选处方明细，"
  "维度取 8 个低基数字段，度量取处方金额求和与处方单价求和。构建时先用少量数据跑一次，"
  "确认维度与度量的对应关系无误，再做全量构建。全量构建耗时 23.13 分钟，完成后体积 2.95GB，"
  "状态转为 READY，如图 8 所示。")
FIG("p-kylin.png", "立方体 bi_cube 的状态、体积与构建时间", 13.2, folder=DELIV)
P("除立方体外另建 7 张预聚合表，连同 9 个索引一次建完，实测耗时 1 分 18 秒，用于立方体覆盖不到的固定口径，例如按科室分组的注射剂、"
  "基本药物与抗菌药物三项占比。预聚合表在 MySQL 中显式建表后插入，不用建表即查的写法，"
  "原因是后者会把聚合结果推断成文本类型，导致无法建立索引。")
CODE(["-- 组合频次：把适应症与药品的共现次数提前算好",
      "INSERT INTO agg_pair (disease_code, drug_code, cnt)",
      "SELECT p.m_diagnostic1, p.drug_code, COUNT(*)",
      "FROM prescription_diseases p",
      "WHERE p.m_diagnostic1 IS NOT NULL AND p.m_diagnostic1 <> ''",
      "  AND p.drug_code IS NOT NULL AND p.drug_code <> ''",
      "GROUP BY 1, 2;"],
     "代码 3　适应症与药品组合频次的预计算，摘自 deploy/sql/agg_profile.sql")
P("**接口开发。** 后端按页面划分三组控制器，每组对应一套页面，接口返回统一包成三段结构，"
  "code 表示状态，data 表示业务数组，msg 表示错误信息。取数入口收敛到一个网关类，"
  "网关根据配置项决定连 Kylin 还是 MySQL，并把 Kylin 方言的 SQL 改写成 MySQL 方言，"
  "业务方法里写的始终是一份标准 SQL。")
CODE(["public static String toMysqlSql(String sql) {",
      "    String s = sql;",
      "    for (String[] pair : TABLE_MAP) s = s.replace(pair[0], pair[1]);",
      "    s = DRUG_JOIN.matcher(s).replaceAll(\"DRUG_CODE = DRUG.DRUG\");",
      "    s = s.replaceAll(\"(?i)\\\\bPRESCRIPTION_DISEASES\\\\.AGE\\\\b\",",
      "                     \"PRESCRIPTION_DISEASES.m_age\");",
      "    s = s.replaceAll(\"(?i)\\\\bM_DIAGNOSTIC\\\\b\", \"m_diagnostic1\");",
      "    s = s.replaceAll(\"(?i)\\\\bVARCHAR\\\\b\", \"CHAR\");",
      "    return s;",
      "}"],
     "代码 4　Kylin 方言到 MySQL 方言的改写，摘自 KylinUtil.java")
P("**前端与大屏。** 前端在原有工程上完成依赖安装、接口地址配置与页面改造，"
  "三套页面共 12 张图表，每张图只负责渲染，取数逻辑抽成公共方法。打包用工程自带的构建脚本，"
  "产物 16 个文件、7.58MB，压缩后 1.95MB，资源路径改为相对路径后放入后端静态目录。")
CODE(["npm install          # 依赖安装，共 1958 个包",
      "npm run build        # 产物在 dist/，共 16 个文件",
      "cp -r dist/* /home/medicine-analysis/backend/yiyao/src/",
      "              main/resources/static/"],
     "代码 5　前端打包与产物复制")
P("大屏用 Django 搭建，五张子图通过五个取数接口从数据库读取，不经过后端网关。"
  "大屏与后端共用同一份数据，因此在验收时可以跨端核对同一个指标，"
  "这为金额口径的比对提供了一条独立路径。")
P("**部署与验证。** 部署用一个脚本完成，脚本先判断组件与端口状态，再拉起后端与大屏，"
  "轮询健康检查接口直到返回 200，最后逐个请求 13 个接口并打印状态码与耗时，如图 9 所示，每次运行打印的耗时存在秒级差异。"
  "验收按数据基准值逐项比对，接口返回的字段名与数值都必须一致。")
FIG("p-startall.png", "一键启动脚本的自检输出，13 个接口逐个打印状态码与耗时", 10.6, folder=DELIV)

# ================================================================ 四、问题与改进
H1("四、问题与改进")
H2("（一）遇到的主要问题")
P("第一个问题是按资料步骤批量导入 HBase 反复失败。现象是作业在提交阶段超时，"
  "日志里出现客户端与集群版本不匹配的提示。定位后发现 HBase 自带的 Hadoop 客户端版本低于集群版本，"
  "文件本地化阶段无法完成。强行对齐版本会牵动整个集群，风险过高，因此改为 HDFS 加 Hive 外部表的链路，"
  "HBase 转为只承担立方体实体的存储。改造后查询结果与预期一致，明细链路不再依赖 HBase。")
P("第二个问题是服务器无法访问代码托管平台。域名解析被污染，连接在握手阶段就超时，"
  "git clone 与 git push 都无法执行。处理方式是把仓库地址换成镜像地址，"
  "并在部署脚本中加入多轮重试与压缩包完整性校验，避免下载到不完整的包后继续部署。")
P("第三个问题是接口改查 MySQL 后出现语法错误与数值偏差。两侧的列名与方言存在差异，"
  "年龄列在立方体侧叫 AGE 而明细库中叫 m_age，诊断列在两侧名称不同，"
  "年月字段在 MySQL 中是保留字，药品编码在明细表中带有序号后缀。"
  "如果每个接口各改一遍，改动量大且容易遗漏，最终把七处映射统一收敛到查询网关，"
  "业务方法不做改动。")
P("第四个问题是页面图表中混入演示数据。前端原先设置 8 秒的回退阈值，多表关联查询超过阈值"
  "就被判定为失败，自动替换成内置演示数据，外观与真实数据完全一致。"
  "现象是同一页面上部分图表为真实数据、部分为演示数据，从界面上无法分辨。"
  "这个问题影响的是结论可信度而不是功能，处理方式是把阈值调整到 60 秒，"
  "并且只在请求失败时启用备用数据，慢查询不再触发替换。")

H2("（二）处理方式与结果")
P("四个问题的处理结果可以量化。明细链路改道后，导入与查询不再受 HBase 版本影响；"
  "仓库访问改用镜像后，部署脚本可以无人值守执行；网关统一改写后，业务代码零改动，"
  "两种引擎可以用同一套接口比对结果；回退逻辑修正后，页面显示的数据与数据库口径一致，"
  "并在测试用例中增加了对取数来源字段的校验，使演示数据无法通过验收。")
P("生成列与索引是第三项的延续。明细表的药品编码形如带序号后缀的字符串，而维表中的编码没有后缀，"
  "直接关联用不上索引。处理方式是用生成列在写入时去掉后缀并建立索引，同时补齐诊断、科室、"
  "医院三列的索引，多表关联能够命中索引，明细关联类接口的耗时从 13.8 秒降到 9.5 秒量级。")
CODE(["-- 明细表 m_drug 形如 DM0000178036_2，维表 drug 是 DM0000178036",
      "ALTER TABLE prescription_diseases",
      "  ADD COLUMN drug_code VARCHAR(64)",
      "  GENERATED ALWAYS AS (SUBSTRING_INDEX(m_drug, '_', 1)) STORED;",
      "CREATE INDEX idx_drug_code ON prescription_diseases (drug_code);",
      "CREATE INDEX idx_diag1   ON prescription_diseases (m_diagnostic1);"],
     "代码 6　去除编码后缀的生成列与索引，摘自 deploy/sql/mysql_indexes.sql")
P("数据层面还有三个问题，它们不改变功能，但改变结论的可信度。第一，数据集只有一个月，"
  "年月字段只有一个取值，涉及时间的图表只有一个刻度，增长率只能返回空数组。"
  "第二，有 1,164 行处方的医院编号在区域维表中没有对应记录，内连接会把这些行直接过滤掉，"
  "全表金额为 26,239,620.54 元，按区域汇总为 26,207,933.86 元，差额 31,686.68 元。")
P("差额可以用一条语句定位到具体行，这也是口径差异能够被追溯的前提：")
CODE(["SELECT COUNT(*) AS lost_rows, ROUND(SUM(amount), 2) AS lost_amount",
      "FROM prescription_diseases p",
      "LEFT JOIN t_view_areas a ON p.hosp_id = a.hosp_id",
      "WHERE a.hosp_id IS NULL;"],
     "代码 7　定位维表缺失导致的金额差额")
P("查询结果是 1,164 行、31,686.68 元，与全表合计减去按区域合计的差额完全吻合。"
  "我们的处理是把差额单独算出来并写进数据基准值文档，而不是让它消失在查询里。"
  "第三，原始实现中的性别字段由年龄的奇偶推算生成，并非数据本身携带的字段，"
  "而明细表中存在记录真实性别的列。我们改为读取真实列，并在文档中记录这一改动，"
  "因为用推算字段做出的性别对比没有意义。")
P("这三项没有在系统里做特殊处理，而是作为已知口径写进文档，页面如实呈现能够得到的结果。"
  "选择这样处理的理由很直接：数据覆盖范围与主数据质量不是五天实训能够解决的问题，"
  "但结论必须建立在可核对的数字上，与其掩盖差异，不如把差异写清楚。")

# ================================================================ 五、总结与后续计划
H1("五、总结与后续计划")
H2("（一）实训小结")
P("五个人按能力分工，每人负责一段链路，工作量与依赖关系如表 6 所示。环境与建模由组长承担，"
  "这一段是所有后续工作的前提，卡住就全线停摆，因此放在最前并留出最多时间；"
  "数据仓库与大屏、数据导入与前端、文档与基准值、测试与验收四段并行推进，"
  "每天下班前汇总当天产出与阻塞项，第二天优先处理阻塞项。")
TBL("五天分工与承担工作",
    ["成员", "角色", "承担工作"],
    [["占竞", "组长", "排期与分工、集群启动与巡检、Kylin 建模与立方体构建、后端接口与部署联调"],
     ["李艺淼", "数据仓库", "Hive 建库建表与外部表关联、Django 大屏工程与五张子图取数"],
     ["付悌安", "数据导入与前端", "六张表导入与行数核对、三套页面 12 张图表、科室结构对比模块"],
     ["杨博文", "文档与基准值", "需求规格、部署验收、数据集说明、数据基准值与接口核对表"],
     ["洪嘉伟", "测试与验收", "18 条测试用例、13 个接口计时、金额三方对账与验收清单"]],
    [2.4, 3.6, 9.4],
    aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
P("回到项目本身，有三点体会值得记录。第一，接口契约要先定。前端与后端并行开发时，"
  "如果返回结构没有提前约定，联调阶段就要反复改动，"
  "先定字段名与层级再用它去写取数逻辑，返工量会小很多。第二，预计算与明细库不是二选一。"
  "立方体解决的是低基数维度上的组合查询，高基数关联与明细查询必须由关系型数据库承担，"
  "把两者当成互相替代会走弯路。第三，文档与脚本的价值在第五天才体现出来。"
  "前两天写文档像是在做无用功，到验收时每个数字都要有出处、每次部署都要能复现，"
  "这时候能省下的是反复确认的时间。")
P("不足也明确。系统没有登录与权限控制，任何拿到地址的人都能访问全部数据；"
  "接口没有做缓存，重复请求会重复计算；耗时较长的几个关联接口仍在 15 秒量级，"
  "在数据量继续增长后会进一步恶化；前端的三套页面结构相近，存在可以抽取的公共组件。"
  "这些都在下文列为后续计划。")

H2("（二）后续计划")
P("这五天走完的六个阶段目前只在我们五个人手里，换一个人接手需要重新摸索一遍。"
  "后续工作的第一步是把过程固化成流程，第二步是在流程上做工具化与自动化，"
  "整体分为四个阶段，如图 10 所示。")
FIG("fig4-plan.png", "后续计划的四个阶段与验收方式", 12.0)
P("流程化的具体内容是把六个阶段写成清单，每个阶段写清三样东西：输入是什么，产出是什么，"
  "怎么判断可以进入下一阶段。例如数据入仓阶段的输入是 6 个原始文件，产出是 6 张表与一份行数核对记录，"
  "判断标准是两侧计数一致且与基准值相符。清单的作用是把判断依据从个人经验变成文件，"
  "后来的人照着清单做即可。")
P("工具化针对清单里可判定的环节。建表、导入、行数核对、基准值抓取、接口自检这几步的判据是确定的，"
  "可以写成脚本由程序执行；维度如何选取、差额是数据问题还是系统问题、页面图表该如何组织，"
  "这几步依赖判断，短期内仍由人来做。现在已经有四个脚本承担了其中一部分，"
  "下一步是把剩下的可判定环节补齐。")
P("在此基础上做一个数据整理与可视化的 agent。输入是一份行业数据与几个业务问题，"
  "输出是表结构、接口与页面。它的工作拆成三段：探查阶段读取字段类型、空值率与取值基数，"
  "标出哪些列适合做维度、哪些列只能做明细；建模阶段按业务问题挑选维度与度量，"
  "判断哪些组合进预聚合、哪些留在明细库；生成阶段产出建表语句、接口与图表配置，"
  "同时计算总额、行数与空值三项校验，差额必须能够落到具体行。")
P("现在这套系统就是这个 agent 的手工版本。8 维 2 度量的参数、7 张预聚合表的写法、"
  "13 个接口的返回结构、五项校验的口径，都可以直接作为模板复用。"
  "流程化的意义正在于此，把这些模板从记得变成文件，agent 才有依据可循。")
P("最后一步是验证。拿一份非医药行业的数据走一遍这条流程，看它是否仍然成立。"
  "如果成立，说明这套方法是可迁移的；如果不成立，就能定位到哪一步绑死在医药数据的特征上。"
  "这一步既是后续计划的验收方式，也是对前面所有工作的检验。")


# ================================================================ 六、参考文献
H1("六、参考文献")
REFS = [
    "KIMBALL R, ROSS M. The data warehouse toolkit: the definitive guide to dimensional modeling[M]. "
    "3rd ed. Indianapolis: John Wiley & Sons, 2013.",
    "INMON W H. Building the data warehouse[M]. 4th ed. Indianapolis: John Wiley & Sons, 2005.",
    "王珊, 萨师煊. 数据库系统概论[M]. 5版. 北京: 高等教育出版社, 2014.",
    "The Apache Software Foundation. The Apache Software Foundation announces Apache Kylin as a "
    "top-level project[EB/OL]. (2015-12-08)[2026-11-15]. "
    "https://blogsarchive.apache.org/foundation/entry/the_apache_software_foundation_announces85.",
    "YANG F, TSCHETTER E, LEAUTE X, et al. Druid: a real-time analytical data store[C]//Proceedings of "
    "the 2014 ACM SIGMOD International Conference on Management of Data. New York: ACM, 2014: 157-168.",
    "SCHULZE R, SCHREIBER T, YATSISHIN I, et al. ClickHouse: lightning fast analytics for everyone[J]. "
    "Proceedings of the VLDB Endowment, 2024, 17(12). DOI:10.14778/3685800.3685802.",
    "国家药品监督管理局. 国家药品不良反应监测年度报告（2023年）[EB/OL]. (2024-03-26)[2026-11-15]. "
    "https://www.nmpa.gov.cn/xxgk/fgwj/qita/20240326161403166.html.",
    "卫生健康委, 教育部, 财政部, 等. 关于加强医疗机构药事管理促进合理用药的意见[EB/OL]. "
    "(2020-02-21)[2026-11-15]. https://www.gov.cn/gongbao/content/2020/content_5522549.htm.",
    "Apache Software Foundation. Apache Kylin documentation[EB/OL]. [2026-11-15]. "
    "https://kylin.apache.org/docs/.",
]
for _i, _ref in enumerate(REFS, 1):
    _p = doc.add_paragraph()
    _pf = _p.paragraph_format
    _pf.first_line_indent = Cm(-0.95)
    _pf.left_indent = Cm(0.95)
    _pf.space_before = Pt(0)
    _pf.space_after = Pt(4)
    _pf.line_spacing = 1.1
    _p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _r = _p.add_run("[%d] %s" % (_i, _ref))
    set_font(_r, size=10.5)

# ================================================================ 七、附录
_h = H1("七、附录　系统截图与接口返回")
_h.paragraph_format.page_break_before = True
H2("（一）三套页面的分栏截图")
P("随项目提交的十二张图表截图为三套页面在不同滚动位置的分栏画面，下图按原始顺序拼合。"
  "首页部分给出城市等级、年龄分布、药品前十与各省份四张图，适应症页部分给出组合关系图、"
  "联合用药弦图、年龄分布气泡图与科室分布饼图，药品页部分给出三个分布图、科室用药结构、"
  "厂商份额与疾病费用构成表。所有图表的数据均来自接口，没有使用内置示例值。")
FIGA("s-charts.png", "三套页面十二张图表的分栏截图", 15.2)

H2("（二）接口返回体")
P("13 个接口的返回结构一致，最外层都是 code 与 data 两段，code 为 200 表示成功，data 为业务数组。"
  "以各省份销售格局接口为例，返回体如下，字段名已经统一成 Counter、Price、Amount、Name 这套写法，"
  "省份全称作为 Name 的值，数值保留两位小数。")
CODE(["{\"code\": 200, \"msg\": \"success\", \"data\": [",
      "  {\"Counter\": \"68021\", \"Price\": \"169394.32\",",
      "   \"Amount\": \"1779425.90\", \"Name\": \"上海市\"},",
      "  {\"Counter\": \"85386\", \"Price\": \"213459.49\",",
      "   \"Amount\": \"2240304.93\", \"Name\": \"广东省\"},",
      "  ... 共 31 个省级行政区",
      "]}"], "代码 8　/home/province 的原始返回，节选两条")
P("下图是其中 12 个接口在浏览器中直接访问得到的原始返回，用于说明字段结构在 13 个接口之间保持一致，"
  "首页概览接口是唯一返回小写字段 label、value、unit 的例外。完整的字段与数值见数据基准值文档。")
FIGA("s-json.png", "13 个接口在浏览器中的原始返回体", 15.2)

H2("（三）集群与运行状态")
P("上图为 YARN 的资源与应用列表，两个节点在线、内存总量 16GB，说明集群处于可以接收作业的状态；"
  "下图为在服务器上执行预聚合脚本的输出，先打印四张表的行数用于核对，再按科室输出处方数与三项占比，"
  "末尾是执行耗时 1 分 18 秒。这两张图与正文的接口耗时、金额校验互相对应。")
FIGA("s-ops.png", "YARN 资源状态与预聚合表的构建输出", 15.2)

doc.save(OUT)
print("saved:", OUT)
print("figures:", FIG_NO, "tables:", TAB_NO, "equations:", EQ_NO)

