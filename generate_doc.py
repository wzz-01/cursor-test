#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《研发体系薪酬管理制度草案-v5.docx》
保持原v4格式和列不变，仅优化"任职资格要求"列的内容：
将角色定位与能力要求、认证与笔试要求、故事点产出要求三个维度整合到该列中。
必须达到的能力后边标注红色星号*
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml


def set_cell_shading(cell, color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def add_run(paragraph, text, bold=False, size=None, font_name=None, color=None):
    run = paragraph.add_run(text)
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    if font_name:
        run.font.name = font_name
        run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return run


def set_paragraph_format(paragraph, space_before=0, space_after=0, line_spacing=1.5, alignment=None):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if alignment is not None:
        paragraph.alignment = alignment


def write_rich_cell(cell, items_by_section, font_size=9):
    """在一个单元格中写入分组的多条目内容，带红色星号标注必达项"""
    cell.text = ''
    first_section = True
    for section_title, items in items_by_section:
        if first_section:
            p = cell.paragraphs[0]
            first_section = False
        else:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(4)

        run = p.add_run(section_title)
        run.bold = True
        run.font.size = Pt(font_size + 0.5)
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        p.paragraph_format.space_after = Pt(1)

        for text, is_required in items:
            ip = cell.add_paragraph()
            ip.paragraph_format.space_before = Pt(0)
            ip.paragraph_format.space_after = Pt(1)
            ip.paragraph_format.line_spacing = 1.15

            if is_required:
                display = text.rstrip(' *').rstrip('*').rstrip()
                run = ip.add_run(display)
                run.font.size = Pt(font_size)
                run.font.name = '宋体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                star = ip.add_run(' *')
                star.bold = True
                star.font.size = Pt(font_size + 0.5)
                star.font.name = '宋体'
                star._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                star.font.color.rgb = RGBColor(255, 0, 0)
            else:
                display = text.rstrip(' *').rstrip('*').rstrip()
                run = ip.add_run(display)
                run.font.size = Pt(font_size)
                run.font.name = '宋体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def create_document():
    doc = Document()

    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
        section.page_width = Cm(29.7)
        section.page_height = Cm(21.0)
        section.orientation = 1

    # ==================== 标题 ====================
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(title_para, '研发体系薪酬管理制度', bold=True, size=22, font_name='黑体')
    set_paragraph_format(title_para, space_before=12, space_after=6, line_spacing=1.5)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(subtitle, '（草案 V5）', bold=False, size=14, font_name='宋体')
    set_paragraph_format(subtitle, space_before=0, space_after=12, line_spacing=1.5)

    # ==================== 一、总则 ====================
    h1 = doc.add_paragraph()
    add_run(h1, '一、总则', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h1, space_before=12, space_after=6, line_spacing=1.5)

    for c in [
        '1. 为建立科学、规范的研发人员薪酬管理体系，充分发挥薪酬的激励作用，吸引和留住优秀研发人才，促进公司研发能力持续提升，特制定本制度。',
        '2. 本制度适用于公司研发体系所有岗位人员，包括但不限于软件开发工程师、测试工程师、架构师、技术经理、项目经理等岗位。',
        '3. 研发体系薪酬管理遵循以下原则：',
    ]:
        p = doc.add_paragraph()
        add_run(p, c, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    for pr in [
        '（1）公平性原则：同岗同级同薪，确保内部公平；',
        '（2）竞争性原则：薪酬水平对标市场，保持对外部人才的吸引力；',
        '（3）激励性原则：通过级别晋升和绩效考核拉开差距，激发员工积极性；',
        '（4）可持续性原则：薪酬增长与公司业务发展和效益相匹配。',
    ]:
        p = doc.add_paragraph()
        add_run(p, pr, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=2, space_after=2, line_spacing=1.5)
        p.paragraph_format.left_indent = Cm(1.0)

    # ==================== 二、薪酬结构 ====================
    h2 = doc.add_paragraph()
    add_run(h2, '二、薪酬结构', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h2, space_before=12, space_after=6, line_spacing=1.5)

    for item in [
        '1. 研发人员薪酬由以下部分组成：基本工资 + 绩效工资 + 项目奖金 + 年终奖金 + 其他补贴。',
        '2. 基本工资：根据岗位级别确定，是薪酬的固定组成部分，按月发放。',
        '3. 绩效工资：根据季度/年度绩效考核结果发放，占总薪酬的20%-30%。',
        '4. 项目奖金：根据项目完成情况、个人贡献度发放，具体标准另行规定。',
        '5. 年终奖金：根据公司年度经营业绩和个人年度综合考核结果发放。',
        '6. 其他补贴：包括餐补、交通补贴、通讯补贴等，按公司统一标准执行。',
    ]:
        p = doc.add_paragraph()
        add_run(p, item, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    # ==================== 三、岗位级别体系 ====================
    h3 = doc.add_paragraph()
    add_run(h3, '三、岗位级别体系', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h3, space_before=12, space_after=6, line_spacing=1.5)

    for d in [
        '1. 研发体系岗位共设置7个级别，由低到高依次为：1级（初级）、2级（初中级）、3级（中级）、4级（中高级）、5级（高级）、6级（资深/专家级）、7级（首席/总监级）。',
        '2. 每个级别对应明确的任职资格要求，员工须满足相应级别的任职资格标准方可评定或晋升至该级别。',
        '3. 级别评定每年进行一次，特殊情况可申请提前评审。',
    ]:
        p = doc.add_paragraph()
        add_run(p, d, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    # ==================== 四、岗位级别及任职资格要求（核心优化部分） ====================
    h4 = doc.add_paragraph()
    add_run(h4, '四、岗位级别及任职资格要求', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h4, space_before=12, space_after=6, line_spacing=1.5)

    intro = doc.add_paragraph()
    add_run(intro, '以下为各级别岗位的详细任职资格要求。"任职资格要求"列从三个维度进行评定：角色定位与能力要求、认证与笔试要求、故事点产出要求。其中，标注"', size=12, font_name='宋体')
    star = intro.add_run('*')
    star.bold = True
    star.font.size = Pt(12)
    star.font.color.rgb = RGBColor(255, 0, 0)
    star.font.name = '宋体'
    star._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    add_run(intro, '"的条目为必须达到的硬性条件，未标注的条目为加分项（非必须，但达到可作为评审加分依据）。', size=12, font_name='宋体')
    set_paragraph_format(intro, space_before=3, space_after=6, line_spacing=1.5)

    # 生成表格
    levels_data = get_levels_data()
    add_levels_table(doc, levels_data)

    # ==================== 五、故事点管理说明 ====================
    h5 = doc.add_paragraph()
    add_run(h5, '五、故事点管理说明', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h5, space_before=12, space_after=6, line_spacing=1.5)

    for item in [
        '1. 故事点（Story Point）是衡量研发人员工作产出的量化指标，综合反映任务复杂度、工作量和技术难度。',
        '2. 故事点由项目经理/技术负责人在需求评审时统一评估分配，采用斐波那契数列（1, 2, 3, 5, 8, 13, 21）进行估算。',
        '3. 故事点的统计周期为自然月，季度和年度数据由月度数据汇总得出。',
        '4. 故事点评估标准：',
    ]:
        p = doc.add_paragraph()
        add_run(p, item, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    for d in [
        '（1）1-2点：简单任务，如配置修改、简单Bug修复、文档更新等；',
        '（2）3-5点：中等任务，如功能模块开发、接口联调、中等复杂度Bug修复等；',
        '（3）8-13点：复杂任务，如核心功能开发、技术方案设计与实施、复杂系统联调等；',
        '（4）21点：极复杂任务，如架构设计、技术攻关、核心系统重构等。',
    ]:
        p = doc.add_paragraph()
        add_run(p, d, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=2, space_after=2, line_spacing=1.5)
        p.paragraph_format.left_indent = Cm(1.0)

    for item in [
        '5. 故事点完成质量要求：完成的故事点须通过代码评审和测试验收，存在严重缺陷的任务不计入有效故事点。',
        '6. 故事点数据将作为级别评定、绩效考核和晋升评审的重要参考依据。',
        '7. 各级别故事点产出要求详见第四部分各级别任职资格表中"故事点产出要求"部分。',
    ]:
        p = doc.add_paragraph()
        add_run(p, item, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    # ==================== 六、级别评定与晋升机制 ====================
    h6 = doc.add_paragraph()
    add_run(h6, '六、级别评定与晋升机制', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h6, space_before=12, space_after=6, line_spacing=1.5)

    for item in [
        '1. 级别评定委员会由技术总监、人力资源部门及相关业务负责人组成。',
        '2. 晋升评审流程：个人申请→直属领导推荐→材料审核→技术答辩→评委会评定→结果公示。',
        '3. 晋升评审每年组织一次（原则上在每年第四季度），特殊贡献者可申请破格晋升。',
        '4. 晋升须同时满足以下条件：',
    ]:
        p = doc.add_paragraph()
        add_run(p, item, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    for d in [
        '（1）在当前级别任职满一年以上；',
        '（2）满足目标级别的任职资格要求中所有必达标准（标注*的条目）；',
        '（3）最近一年绩效考核结果为"良好"及以上；',
        '（4）获得直属领导和评审委员会的认可。',
    ]:
        p = doc.add_paragraph()
        add_run(p, d, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=2, space_after=2, line_spacing=1.5)
        p.paragraph_format.left_indent = Cm(1.0)

    p = doc.add_paragraph()
    add_run(p, '5. 降级条件：连续两个考核周期绩效不达标，或发生严重违规行为，可启动降级流程。', size=12, font_name='宋体')
    set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    # ==================== 七、附则 ====================
    h7 = doc.add_paragraph()
    add_run(h7, '七、附则', bold=True, size=15, font_name='黑体')
    set_paragraph_format(h7, space_before=12, space_after=6, line_spacing=1.5)

    for item in [
        '1. 本制度由人力资源部负责解释和修订。',
        '2. 本制度自发布之日起执行，原有相关制度同时废止。',
        '3. 本制度如与国家法律法规相抵触，以国家法律法规为准。',
    ]:
        p = doc.add_paragraph()
        add_run(p, item, size=12, font_name='宋体')
        set_paragraph_format(p, space_before=3, space_after=3, line_spacing=1.5)

    return doc


def add_levels_table(doc, levels_data):
    """生成岗位级别总表，保持原文件的列格式：级别 | 岗位名称 | 角色定位 | 任职资格要求 | 薪资范围"""

    col_count = 5
    row_count = 1 + len(levels_data)
    table = doc.add_table(rows=row_count, cols=col_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    col_widths = [Cm(1.5), Cm(3.5), Cm(4.5), Cm(14.0), Cm(2.2)]
    headers = ['级别', '岗位名称', '角色定位', '任职资格要求', '薪资范围']

    for ci in range(col_count):
        cell = table.rows[0].cells[ci]
        cell.width = col_widths[ci]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(headers[ci])
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        run.font.color.rgb = RGBColor(255, 255, 255)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, '4472C4')

    for ri, lv in enumerate(levels_data):
        row = table.rows[ri + 1]
        for ci in range(col_count):
            row.cells[ci].width = col_widths[ci]

        # 级别
        c0 = row.cells[0]
        c0.text = ''
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(str(lv['level']) + '级')
        r0.bold = True
        r0.font.size = Pt(11)
        r0.font.name = '宋体'
        r0._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # 岗位名称
        c1 = row.cells[1]
        c1.text = ''
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(lv['job_title'])
        r1.font.size = Pt(10)
        r1.font.name = '宋体'
        r1._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        c1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # 角色定位
        c2 = row.cells[2]
        c2.text = ''
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(lv['role_desc'])
        r2.font.size = Pt(9.5)
        r2.font.name = '宋体'
        r2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        c2.vertical_alignment = WD_ALIGN_VERTICAL.TOP

        # 任职资格要求（核心：整合三个维度）
        c3 = row.cells[3]
        sections = [
            ('【一、角色定位与能力要求】', lv['role_items']),
            ('【二、认证与笔试要求】', lv['cert_items']),
            ('【三、故事点产出要求】', lv['sp_items']),
        ]
        write_rich_cell(c3, sections, font_size=9)
        c3.vertical_alignment = WD_ALIGN_VERTICAL.TOP

        # 薪资范围
        c4 = row.cells[4]
        c4.text = ''
        p4 = c4.paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r4 = p4.add_run(lv['salary'])
        r4.font.size = Pt(10)
        r4.font.name = '宋体'
        r4._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        c4.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        if ri % 2 == 1:
            for ci in range(col_count):
                if ci != 3:
                    set_cell_shading(row.cells[ci], 'F2F7FC')

    # 表后注释
    note = doc.add_paragraph()
    add_run(note, '注：标注 ', size=10, font_name='宋体')
    star = note.add_run('*')
    star.bold = True
    star.font.size = Pt(11)
    star.font.color.rgb = RGBColor(255, 0, 0)
    star.font.name = '宋体'
    star._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    add_run(note, ' 的条目为必须达到的硬性条件，未标注的条目为加分项（非必须，但达到可作为评审加分依据）。', size=10, font_name='宋体')
    set_paragraph_format(note, space_before=4, space_after=8, line_spacing=1.2)


def get_levels_data():
    """
    定义1-7级的完整数据。
    每级包含：level, job_title, role_desc, salary, role_items, cert_items, sp_items
    role_items/cert_items/sp_items 中每条为 (text, is_required) 元组
    """
    return [
        {
            'level': 1,
            'job_title': '初级开发工程师',
            'role_desc': '在高级工程师指导下完成模块级开发任务，配合团队完成日常开发工作。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('在高级工程师指导下完成模块级开发任务，能独立编写简单功能代码', True),
                ('熟悉至少一门主流编程语言（如Java、Python、C++等），掌握基本语法和常用数据结构', True),
                ('能阅读和理解项目已有代码，按照编码规范完成代码编写', True),
                ('了解基本的软件开发流程（需求分析、设计、编码、测试），能配合团队完成日常工作', True),
                ('具备基础的数据库操作能力（SQL增删改查）', True),
                ('参与过至少1个完整项目的开发（含实习或毕业设计项目）', False),
                ('了解版本控制工具（如Git）的基本使用', False),
                ('了解前端或后端某一方向的基础技术栈', False),
            ],
            'cert_items': [
                ('通过公司初级技术笔试（满分100分，要求≥60分）', True),
                ('计算机相关专业本科及以上学历，或非相关专业但通过公司技术入门考核', True),
                ('持有软件设计师（中级）或同等级别职业资格证书', False),
                ('持有主流技术厂商初级认证（如Oracle OCA、AWS Cloud Practitioner等）', False),
            ],
            'sp_items': [
                ('月均完成有效故事点 ≥ 15点', True),
                ('季度累计完成有效故事点 ≥ 45点', True),
                ('故事点完成任务中，简单任务（1-3点）占比不限', False),
                ('代码评审通过率 ≥ 85%', False),
            ],
        },
        {
            'level': 2,
            'job_title': '初中级开发工程师',
            'role_desc': '能独立承担模块级开发任务，在常规业务需求中可自主完成设计与编码。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('能独立承担模块级开发任务，自主完成常规业务需求的设计与编码', True),
                ('熟练掌握至少一门主流编程语言及其核心框架（如Spring Boot、Django等）', True),
                ('具备独立排查和修复中等复杂度Bug的能力', True),
                ('能编写较为规范的技术文档（如接口文档、详细设计文档）', True),
                ('参与过至少2个完整项目的开发，具备一定的业务理解能力', True),
                ('了解常用设计模式（如单例、工厂、观察者等）及其应用场景', False),
                ('具备基本的性能意识，能在开发中避免明显的性能问题', False),
                ('能协助初级工程师解答技术问题', False),
            ],
            'cert_items': [
                ('通过公司初中级技术笔试（满分100分，要求≥65分）', True),
                ('计算机相关专业本科及以上学历', True),
                ('持有软件设计师（中级）或同等级别职业资格证书', False),
                ('持有主流技术厂商初中级认证（如Oracle OCP、AWS Solutions Architect Associate等）', False),
                ('参加过公司组织的技术培训并考核通过', False),
            ],
            'sp_items': [
                ('月均完成有效故事点 ≥ 20点', True),
                ('季度累计完成有效故事点 ≥ 60点', True),
                ('完成任务中，中等及以上复杂度任务（≥3点）占比 ≥ 30%', True),
                ('代码评审通过率 ≥ 88%', False),
                ('参与至少1次需求评审或技术方案评审', False),
            ],
        },
        {
            'level': 3,
            'job_title': '中级开发工程师',
            'role_desc': '能独立承担子系统或核心模块的设计与开发，具备系统设计的基本能力。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('能独立承担子系统或核心模块的设计与开发工作', True),
                ('精通至少一门编程语言及其主流框架，熟悉第二门编程语言', True),
                ('能进行模块级技术方案设计，输出详细设计文档', True),
                ('具备较强的问题分析和排查能力，能独立解决复杂技术问题', True),
                ('参与过至少3个完整项目的开发，其中至少1个担任过核心开发角色', True),
                ('熟悉常用中间件（如Redis、消息队列、Nginx等）的使用与配置', True),
                ('具备Code Review能力，能对初级工程师代码进行有效评审', False),
                ('了解微服务架构的基本概念和实践', False),
                ('能主动发现项目中的技术风险并提出改进建议', False),
                ('具备一定的技术分享能力，能在团队内进行技术交流', False),
            ],
            'cert_items': [
                ('通过公司中级技术笔试（满分100分，要求≥70分）', True),
                ('计算机相关专业本科及以上学历，工作经验2年以上', True),
                ('持有软件设计师（中级）或系统集成项目管理工程师证书', False),
                ('持有主流技术厂商中级认证（如Oracle OCP、AWS Solutions Architect Associate、阿里云ACP等）', False),
                ('在公司内部技术评审中获得过"优秀方案"评价', False),
            ],
            'sp_items': [
                ('月均完成有效故事点 ≥ 28点', True),
                ('季度累计完成有效故事点 ≥ 84点', True),
                ('完成任务中，中等及以上复杂度任务（≥5点）占比 ≥ 40%', True),
                ('参与故事点评估工作，评估准确率 ≥ 75%', False),
                ('代码评审通过率 ≥ 90%', False),
            ],
        },
        {
            'level': 4,
            'job_title': '中高级开发工程师',
            'role_desc': '能主导子系统架构设计与技术选型，对系统性能、可用性、可扩展性有深入理解。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('能主导子系统的架构设计与技术选型', True),
                ('精通至少两门编程语言及其生态，能根据场景选择合适的技术方案', True),
                ('能独立完成系统级技术方案设计，并主导技术评审', True),
                ('具备性能优化能力，能对系统进行性能瓶颈分析和调优', True),
                ('参与过至少5个完整项目，其中至少2个担任过技术负责人或核心架构角色', True),
                ('熟练掌握分布式系统设计（如分布式缓存、分布式事务、分布式消息等）', True),
                ('具备带领3-5人小团队完成项目交付的能力', False),
                ('能指导中级及以下工程师的技术成长', False),
                ('具备跨团队技术协调沟通能力', False),
                ('有过技术攻关经历，解决过生产环境重大技术问题', False),
            ],
            'cert_items': [
                ('通过公司中高级技术笔试（满分100分，要求≥75分）', True),
                ('计算机相关专业本科及以上学历，工作经验4年以上', True),
                ('持有系统架构设计师（高级）或信息系统项目管理师证书', False),
                ('持有主流技术厂商高级认证（如AWS Solutions Architect Professional、阿里云ACE等）', False),
                ('在公司内部或行业技术会议上做过技术分享', False),
                ('参加公司组织的架构设计专项考核并通过', False),
            ],
            'sp_items': [
                ('月均完成有效故事点 ≥ 35点', True),
                ('季度累计完成有效故事点 ≥ 105点', True),
                ('完成任务中，复杂任务（≥8点）占比 ≥ 25%', True),
                ('主导或参与架构类任务（≥13点）至少1次/季度', False),
                ('负责的模块代码评审覆盖率 ≥ 95%', False),
            ],
        },
        {
            'level': 5,
            'job_title': '高级开发工程师',
            'role_desc': '能主导整个系统/产品线的技术架构设计，制定技术路线图和演进计划。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('能主导整个系统/产品线的技术架构设计，制定技术路线图和演进计划', True),
                ('在某一技术领域具有深厚积累，是团队的技术标杆', True),
                ('能解决跨系统、跨领域的复杂技术难题', True),
                ('具备从0到1搭建系统的能力，能完成技术架构的全链路设计', True),
                ('参与过至少8个项目，其中至少3个担任技术负责人', True),
                ('精通高并发、高可用系统设计，有大规模系统实战经验', True),
                ('能带领5-10人技术团队完成复杂项目交付', True),
                ('具备技术规划能力，能制定团队技术发展方向', False),
                ('有过核心系统重构或重大技术升级的成功经历', False),
                ('具备培养中高级工程师的能力，有明确的技术指导成果', False),
                ('能输出高质量技术文章或在行业会议上发表演讲', False),
            ],
            'cert_items': [
                ('通过公司高级技术笔试（满分100分，要求≥80分）', True),
                ('计算机相关专业本科及以上学历（硕士优先），工作经验6年以上', True),
                ('持有系统架构设计师（高级）证书', True),
                ('持有主流技术厂商高级认证（如AWS Solutions Architect Professional、Google Cloud Professional等）', False),
                ('通过公司组织的高级架构设计专项答辩', False),
                ('在国内外技术社区有一定影响力（如技术博客、开源贡献等）', False),
            ],
            'sp_items': [
                ('月均完成有效故事点 ≥ 40点（含指导他人产出）', True),
                ('季度累计完成有效故事点 ≥ 120点', True),
                ('完成任务中，复杂任务（≥8点）占比 ≥ 35%', True),
                ('主导架构类任务（≥13点）至少2次/季度', True),
                ('团队整体故事点产出环比增长 ≥ 5%', False),
                ('在故事点评估中担任评审角色，评估偏差率 ≤ 20%', False),
            ],
        },
        {
            'level': 6,
            'job_title': '资深/专家级工程师',
            'role_desc': '能主导公司级技术战略规划和重大技术决策，在特定技术领域达到行业专家水平。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('能主导公司级技术战略规划和重大技术决策', True),
                ('在特定技术领域达到行业专家水平，具有行业影响力', True),
                ('能解决业界前沿或行业级的技术难题，引领技术创新', True),
                ('具备多个产品线/系统的架构设计与治理能力', True),
                ('参与过至少12个项目，其中至少5个担任技术总负责人', True),
                ('在高并发、分布式、大数据、云原生等至少2个方向有深入实践经验', True),
                ('能带领10-20人技术团队，建立技术梯队和人才培养体系', True),
                ('推动过公司级的技术标准化和平台化建设', False),
                ('有过技术专利申请或核心技术论文发表经历', False),
                ('能代表公司参与行业技术标准的制定或讨论', False),
                ('建立过完善的技术评审和质量保障体系', False),
            ],
            'cert_items': [
                ('通过公司专家级技术笔试（满分100分，要求≥85分）', True),
                ('计算机相关专业硕士及以上学历（博士优先），工作经验8年以上', True),
                ('持有系统架构设计师（高级）证书', True),
                ('持有至少2项主流技术厂商高级认证', True),
                ('通过公司组织的专家级技术答辩评审', True),
                ('在行业技术大会上发表过演讲或有公开发表的技术论文', False),
                ('有开源项目核心贡献者经历', False),
            ],
            'sp_items': [
                ('团队月均故事点产出达标（团队整体 ≥ 团队人数 × 25点）', True),
                ('个人月均完成有效故事点 ≥ 35点（含技术攻关和架构类任务）', True),
                ('季度内主导完成至少3个复杂任务（≥13点）', True),
                ('推动技术改进带来的效率提升可量化（如人均产出提升10%以上）', False),
                ('建立或优化故事点评估体系，使团队评估准确率 ≥ 80%', False),
            ],
        },
        {
            'level': 7,
            'job_title': '首席/总监级工程师',
            'role_desc': '全面负责公司研发技术体系的战略规划与落地执行，具备行业顶尖技术视野。',
            'salary': '参照公司\n薪酬标准',
            'role_items': [
                ('全面负责公司研发技术体系的战略规划与落地执行', True),
                ('具备行业顶尖的技术视野和判断力，能准确把握技术发展趋势', True),
                ('主导公司核心技术竞争力的构建，推动关键技术突破', True),
                ('具备跨业务线、跨技术域的全局架构治理能力', True),
                ('参与过至少15个项目，其中至少8个担任技术总负责人', True),
                ('在多个技术领域具有深入造诣，能进行跨领域技术决策', True),
                ('具备20人以上技术团队的管理经验，成功建立过高效能技术团队', True),
                ('推动过至少1项对公司业务产生重大影响的技术变革', True),
                ('在行业内具有较高知名度和影响力', False),
                ('有技术专利或核心技术论文发表', False),
                ('参与过行业技术标准的制定', False),
                ('建立过完善的研发效能度量和持续改进体系', False),
            ],
            'cert_items': [
                ('通过公司首席级技术笔试（满分100分，要求≥90分）', True),
                ('计算机相关专业硕士及以上学历，工作经验10年以上', True),
                ('持有系统架构设计师（高级）证书', True),
                ('持有至少3项主流技术厂商高级认证', True),
                ('通过公司组织的首席/总监级答辩评审（含外部专家评审）', True),
                ('在国内外顶级技术大会上发表过主题演讲', False),
                ('有业界知名开源项目主导经历', False),
                ('获得过行业级技术奖项或荣誉', False),
            ],
            'sp_items': [
                ('研发体系整体故事点产出持续达标（月度波动 ≤ 10%）', True),
                ('推动建立完善的故事点管理体系和效能度量体系', True),
                ('个人季度内主导或深度参与至少2个战略级技术任务（≥21点）', True),
                ('研发效能（人均故事点产出）年度环比提升 ≥ 10%', False),
                ('推动故事点与业务价值的关联分析，建立价值导向的产出评估体系', False),
                ('团队故事点交付质量（一次性通过率）≥ 95%', False),
            ],
        },
    ]


if __name__ == '__main__':
    doc = create_document()
    output_path = '/workspace/研发体系薪酬管理制度草案-v5.docx'
    doc.save(output_path)
    print(f'文档已生成: {output_path}')
