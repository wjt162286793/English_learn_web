from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR


W, H = 13.333, 7.5
CYAN = RGBColor(5, 228, 255)
CYAN_DARK = RGBColor(23, 107, 134)
CYAN_PALE = RGBColor(223, 248, 251)
INK = RGBColor(33, 48, 60)
MUTED = RGBColor(103, 124, 136)
BG = RGBColor(245, 249, 251)
WHITE = RGBColor(255, 255, 255)
LINE = RGBColor(219, 233, 237)


def rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def box(slide, x, y, w, h, fill=WHITE, line=None, radius=True, transparency=0):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.fill.transparency = transparency
    shape.line.color.rgb = line or fill
    shape.line.width = Pt(0.8)
    return shape


def text(slide, txt, x, y, w, h, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         font="Microsoft YaHei", valign=MSO_ANCHOR.TOP, margin=0.06):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = txt
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_footer(slide, num):
    text(slide, "DCTC 样本管理系统操作手册", 0.55, 7.12, 5.2, 0.18, 8, MUTED)
    text(slide, f"{num:02d}", 12.25, 7.08, 0.5, 0.22, 9, CYAN_DARK, True, PP_ALIGN.RIGHT)


def add_title(slide, title, kicker=None):
    if kicker:
        text(slide, kicker.upper(), 0.58, 0.38, 2.0, 0.22, 8, CYAN_DARK, True)
    text(slide, title, 0.55, 0.62, 8.7, 0.5, 25, INK, True)
    box(slide, 0.58, 1.18, 0.68, 0.05, CYAN, CYAN, False)


def add_placeholder(slide, x, y, w, h, label, sub="点击替换为系统截图"):
    box(slide, x, y, w, h, RGBColor(238, 247, 249), LINE, True)
    # simple browser chrome
    box(slide, x + 0.12, y + 0.12, w - 0.24, 0.25, RGBColor(228, 240, 243), RGBColor(228, 240, 243), True)
    for i, c in enumerate([RGBColor(255, 153, 153), RGBColor(255, 205, 118), RGBColor(122, 219, 174)]):
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.22 + i * 0.14), Inches(y + 0.18), Inches(0.06), Inches(0.06))
        dot.fill.solid(); dot.fill.fore_color.rgb = c; dot.line.color.rgb = c
    text(slide, label, x + 0.18, y + h / 2 - 0.24, w - 0.36, 0.35, 14, CYAN_DARK, True, PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    text(slide, sub, x + 0.18, y + h / 2 + 0.15, w - 0.36, 0.25, 9, MUTED, False, PP_ALIGN.CENTER)


def add_note_card(slide, x, y, w, h, number, title_txt, body="在此补充操作说明、字段含义或注意事项。"):
    box(slide, x, y, w, h, WHITE, LINE, True)
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.18), Inches(y + 0.18), Inches(0.38), Inches(0.38))
    circ.fill.solid(); circ.fill.fore_color.rgb = CYAN_PALE; circ.line.color.rgb = CYAN_PALE
    text(slide, str(number), x + 0.18, y + 0.205, 0.38, 0.24, 10, CYAN_DARK, True, PP_ALIGN.CENTER)
    text(slide, title_txt, x + 0.68, y + 0.18, w - 0.88, 0.28, 13, INK, True)
    text(slide, body, x + 0.18, y + 0.62, w - 0.36, h - 0.75, 10, MUTED)


def base_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid(); bg.fore_color.rgb = BG
    return slide


def cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor(237, 249, 251)
    # Cover visual field, designed to be replaced by the supplied login background.
    box(slide, 7.35, 0, 5.98, 7.5, RGBColor(219, 247, 250), RGBColor(219, 247, 250), False)
    for x, y, d, a in [(8.2, 1.0, 2.5, 45), (10.4, 3.7, 1.5, 25), (8.8, 5.1, 3.2, 60)]:
        s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
        s.fill.solid(); s.fill.fore_color.rgb = CYAN; s.fill.transparency = a
        s.line.color.rgb = CYAN; s.line.transparency = 100
    # visual placeholder
    add_placeholder(slide, 7.85, 1.48, 4.75, 4.18, "登录页背景图", "建议替换为用户提供的高清背景图片")
    text(slide, "DCTC", 0.72, 0.68, 1.35, 0.35, 18, CYAN_DARK, True)
    text(slide, "样本管理系统", 2.02, 0.7, 2.0, 0.3, 12, MUTED)
    text(slide, "DCTC样本管理系统\n操作手册", 0.72, 2.05, 5.9, 1.4, 31, INK, True)
    text(slide, "系统操作说明 · 页面结构 · 流程指引", 0.78, 3.75, 5.3, 0.32, 13, CYAN_DARK)
    box(slide, 0.78, 4.35, 4.7, 0.66, WHITE, WHITE, True)
    text(slide, "适用于样本、项目、资源与库存等模块的操作培训", 1.02, 4.55, 4.2, 0.22, 10, MUTED)
    text(slide, "DOCUMENT TEMPLATE / 2026", 0.78, 6.86, 2.4, 0.18, 8, MUTED, True)


def contents(prs):
    slide = base_slide(prs)
    add_title(slide, "目录", "CONTENTS")
    items = ["系统登录与首页", "项目管理", "条码导入", "管样核对", "样本入库", "库存盘点",
             "样本转移", "样本轨迹", "出库前核对", "样本出库", "资源管理", "稽查轨迹",
             "系统管理", "系统监控", "物资管理", "入库确认", "出库确认", "常见问题与备注"]
    for i, item in enumerate(items):
        col = i // 9
        row = i % 9
        x = 0.62 + col * 6.2
        y = 1.52 + row * 0.53
        box(slide, x, y, 5.6, 0.42, WHITE, LINE, True)
        text(slide, f"{i+1:02d}", x + 0.15, y + 0.08, 0.42, 0.18, 9, CYAN_DARK, True)
        text(slide, item, x + 0.7, y + 0.06, 4.65, 0.22, 12, INK)
        # tiny module marker
        mark = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 5.18), Inches(y + 0.15), Inches(0.08), Inches(0.08))
        mark.fill.solid(); mark.fill.fore_color.rgb = CYAN; mark.line.color.rgb = CYAN
    add_footer(slide, 2)


def section_divider(prs):
    slide = base_slide(prs)
    box(slide, 0.62, 1.45, 12.1, 4.55, RGBColor(234, 251, 252), RGBColor(234, 251, 252), True)
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.92), Inches(1.88), Inches(1.55), Inches(1.55))
    c.fill.solid(); c.fill.fore_color.rgb = CYAN; c.fill.transparency = 12; c.line.color.rgb = CYAN
    text(slide, "01", 1.18, 2.3, 1.0, 0.45, 28, WHITE, True, PP_ALIGN.CENTER)
    text(slide, "样本管理", 3.0, 2.03, 5.6, 0.62, 32, INK, True)
    text(slide, "从项目、样本到库存与轨迹，建立统一的管理操作路径", 3.02, 2.82, 6.5, 0.3, 14, CYAN_DARK)
    for i, item in enumerate(["项目关联", "入库 / 出库", "库存盘点", "轨迹追溯"]):
        box(slide, 3.02 + i * 2.0, 4.2, 1.68, 0.72, WHITE, LINE, True)
        text(slide, item, 3.12 + i * 2.0, 4.46, 1.48, 0.2, 11, INK, True, PP_ALIGN.CENTER)
    add_footer(slide, 3)


def subdirectory(prs):
    slide = base_slide(prs)
    add_title(slide, "样本管理｜子目录", "CHAPTER 01")
    text(slide, "本章节页面可按实际系统菜单继续拆分；没有子模块时保留单标题卡片即可。", 0.62, 1.35, 7.2, 0.3, 11, MUTED)
    modules = [("01", "冰箱", "冰箱、层架、列位与容量维护"), ("02", "样本管理", "样本入库、转移、出库与状态"), ("03", "样本与冻存类型", "样本类型、冻存条件与编码"), ("04", "管样容器类型", "管型、盒型与容器规则"), ("05", "寄送信息", "物流、寄送与外部交接")]
    for i, (num, title_txt, desc) in enumerate(modules):
        row = i // 3; col = i % 3
        x = 0.62 + col * 4.18
        y = 2.05 + row * 1.42
        box(slide, x, y, 3.72, 1.08, WHITE, LINE, True)
        text(slide, num, x + 0.22, y + 0.2, 0.55, 0.22, 10, CYAN_DARK, True)
        text(slide, title_txt, x + 0.82, y + 0.16, 2.65, 0.28, 15, INK, True)
        text(slide, desc, x + 0.82, y + 0.57, 2.6, 0.24, 9, MUTED)
    add_footer(slide, 4)


def image_left(prs):
    slide = base_slide(prs)
    add_title(slide, "页面操作说明模板", "LAYOUT A · 70 / 30")
    add_placeholder(slide, 0.62, 1.48, 8.05, 4.92, "完整系统页面截图", "左侧占位区约 70%，适合首页 / 列表页 / 详情页")
    box(slide, 8.98, 1.48, 3.72, 4.92, WHITE, LINE, True)
    text(slide, "页面说明", 9.3, 1.78, 2.8, 0.3, 15, INK, True)
    add_note_card(slide, 9.22, 2.28, 3.22, 1.05, 1, "进入页面", "补充菜单路径、角色权限和进入条件。")
    add_note_card(slide, 9.22, 3.5, 3.22, 1.05, 2, "关键区域", "圈出筛选条件、数据列或主要按钮。")
    add_note_card(slide, 9.22, 4.72, 3.22, 1.05, 3, "操作结果", "填写完成后页面状态或提示信息。")
    add_footer(slide, 5)


def stacked_steps(prs):
    slide = base_slide(prs)
    add_title(slide, "步骤操作说明模板", "LAYOUT B · 55 / 45")
    for i in range(3):
        add_placeholder(slide, 0.62, 1.55 + i * 1.58, 6.15, 1.24, f"步骤 {i+1} 截图", "替换为对应操作步骤截图")
    box(slide, 7.15, 1.55, 5.55, 4.98, WHITE, LINE, True)
    text(slide, "操作步骤与说明", 7.48, 1.86, 3.5, 0.3, 15, INK, True)
    add_note_card(slide, 7.42, 2.38, 4.95, 1.05, 1, "步骤标题", "用动词描述本步骤，例如：选择项目、填写字段、提交保存。")
    add_note_card(slide, 7.42, 3.62, 4.95, 1.05, 2, "字段说明", "补充必填项、格式要求、默认值或校验规则。")
    add_note_card(slide, 7.42, 4.86, 4.95, 1.05, 3, "注意事项", "补充权限、异常提示、撤回和重复提交等情况。")
    add_footer(slide, 6)


def table_form(prs):
    slide = base_slide(prs)
    add_title(slide, "表格与表单说明模板", "LAYOUT C · TABLE / FORM")
    box(slide, 0.62, 1.48, 7.75, 4.95, WHITE, LINE, True)
    text(slide, "截图 / 表格区域", 0.95, 1.76, 2.0, 0.25, 14, INK, True)
    # table-like editable scaffold
    cols = [1.25, 1.65, 2.3, 1.45]
    headers = ["项目编号", "样本编号", "样本名称 / 状态", "操作"]
    x = 0.95
    for cw, hd in zip(cols, headers):
        box(slide, x, 2.25, cw, 0.43, CYAN_DARK, CYAN_DARK, False)
        text(slide, hd, x + 0.05, 2.38, cw - 0.1, 0.16, 9, WHITE, True, PP_ALIGN.CENTER)
        x += cw
    for r in range(5):
        x = 0.95
        for c, cw in enumerate(cols):
            box(slide, x, 2.68 + r * 0.5, cw, 0.5, RGBColor(251, 253, 254), LINE, False)
            txt = "填写字段" if c < 3 else "编辑 / 查看"
            text(slide, txt, x + 0.05, 2.84 + r * 0.5, cw - 0.1, 0.15, 9, MUTED, False, PP_ALIGN.CENTER)
            x += cw
    box(slide, 8.72, 1.48, 3.98, 4.95, WHITE, LINE, True)
    text(slide, "字段说明", 9.05, 1.76, 2.5, 0.25, 14, INK, True)
    for i, (t, d) in enumerate([("筛选条件", "说明查询范围与组合条件。"), ("新增 / 提交", "说明按钮位置、必填字段与保存结果。"), ("操作列", "说明查看、编辑、删除等权限。"), ("提示信息", "说明成功、失败和异常提示。")]):
        add_note_card(slide, 8.98, 2.25 + i * 0.92, 3.45, 0.74, i + 1, t, d)
    add_footer(slide, 7)


def conclusion(prs):
    slide = base_slide(prs)
    box(slide, 0.62, 1.25, 12.1, 5.15, RGBColor(233, 250, 252), RGBColor(233, 250, 252), True)
    text(slide, "操作要点与备注", 1.0, 1.72, 5.0, 0.55, 28, INK, True)
    text(slide, "将实际业务规则、权限范围和异常处理补充到以下卡片中。", 1.02, 2.42, 7.5, 0.28, 13, CYAN_DARK)
    for i, title_txt in enumerate(["权限与角色", "数据规范", "异常处理"]):
        x = 1.02 + i * 3.82
        box(slide, x, 3.35, 3.25, 1.55, WHITE, LINE, True)
        text(slide, f"0{i+1}", x + 0.24, 3.62, 0.45, 0.24, 10, CYAN_DARK, True)
        text(slide, title_txt, x + 0.82, 3.58, 2.0, 0.28, 14, INK, True)
        text(slide, "在此补充本模块的关键注意事项和培训提醒。", x + 0.24, 4.18, 2.7, 0.34, 10, MUTED)
    text(slide, "DCTC 样本管理系统 · 操作手册模板", 1.02, 5.65, 5.0, 0.25, 10, MUTED)
    add_footer(slide, 8)


def main():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    cover(prs)
    contents(prs)
    section_divider(prs)
    subdirectory(prs)
    image_left(prs)
    stacked_steps(prs)
    table_form(prs)
    conclusion(prs)
    out = "/workspace/DCTC样本管理系统操作手册_PPT架子.pptx"
    prs.save(out)
    print(out)


if __name__ == "__main__":
    main()
