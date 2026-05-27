from __future__ import annotations

import html
import zipfile
from datetime import datetime
from pathlib import Path


OUT = Path("docs/硅氧键催化量子研究平台_软件著作权技术说明书.docx")


def esc(text: object) -> str:
    return html.escape(str(text), quote=False)


def p(text: str = "", style: str | None = None, bold: bool = False, center: bool = False) -> str:
    ppr = ""
    if style or center:
        bits = []
        if style:
            bits.append(f'<w:pStyle w:val="{style}"/>')
        if center:
            bits.append('<w:jc w:val="center"/>')
        ppr = f"<w:pPr>{''.join(bits)}</w:pPr>"
    rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return f"<w:p>{ppr}<w:r>{rpr}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(rows: list[list[object]], header: bool = True) -> str:
    xml = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblStyle w:val="TableGrid"/>',
        '<w:tblW w:w="0" w:type="auto"/>',
        '<w:tblLook w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>',
        "</w:tblPr>",
    ]
    for r_idx, row in enumerate(rows):
        xml.append("<w:tr>")
        for cell in row:
            shade = '<w:shd w:fill="EAF5F8"/>' if header and r_idx == 0 else ""
            xml.append(
                "<w:tc>"
                f"<w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/>{shade}</w:tcPr>"
                f"{p(str(cell), bold=header and r_idx == 0)}"
                "</w:tc>"
            )
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml)


def bullets(items: list[str]) -> str:
    return "".join(p(f"• {item}") for item in items)


def numbered(items: list[str]) -> str:
    return "".join(p(f"{index}. {item}") for index, item in enumerate(items, 1))


def h1(text: str) -> str:
    return p(text, style="Heading1")


def h2(text: str) -> str:
    return p(text, style="Heading2")


def build_body() -> str:
    generated = datetime.now().strftime("%Y年%m月%d日")
    source_rows = [
        ["源码类别", "文件数", "代码行数", "说明"],
        ["Python 后端源码与测试", "27", "2544", "FastAPI、SQLAlchemy、Pydantic、解析器、测试"],
        ["TypeScript / TSX 前端源码", "19", "3515", "Next.js、React 组件、类型定义、数据模型"],
        ["CSS / JS / 配置 / 文档", "17", "615", "Tailwind 全局样式、Web Worker、配置与说明"],
        ["合计", "63", "6674", "已排除依赖、构建产物、缓存、日志、数据库和 lock 文件"],
    ]
    module_rows = [
        ["模块", "主要技术", "功能说明"],
        ["论文知识库", "DOCX OOXML 只读解析、规则抽取", "抽取博士论文题目、摘要、单体族、催化剂模型、机理结论和研究对象。"],
        ["分子库", "React、RDKit、SMILES 描述符", "管理 DCS、MCSOMe、DMOS、TMS 系列、DCS 链长系列、乙烯、丙烯、1-己烯和 TEA。"],
        ["Gaussian 输入生成", "模板引擎、FastAPI", "生成 opt/freq/NBO、Counterpoise、π-complex、O→Ti、TS、IRC 等输入模板。"],
        ["Gaussian 输出解析", "Python 正则解析、Web Worker 预览", "解析 SCF、Gibbs、频率、虚频、HOMO/LUMO、电荷、NBO、Wiberg 和 Counterpoise 能量。"],
        ["电子云与前线轨道", "cube 元数据解析、前端等值面占位", "登记 electron density、ESP、HOMO、LUMO、spin density cube 文件元数据。"],
        ["实验-DFT 对照", "CSV 导入、Pearson 相关性", "将实验活性、插入率、序列长度等与 ΔG‡、ΔGpoison、电子导向和位阻评分关联。"],
        ["可证伪机制模型", "规则引擎、可信度评分", "建立位阻主导、电子导向、TEA 预组织、O→Ti 毒化、链长窗口等机制假说。"],
        ["报告生成", "Markdown/JSON/CSV/HTML", "输出中文科研报告，区分论文抽取、真实上传、用户输入和示例数据。"],
    ]
    db_rows = [
        ["数据表", "用途"],
        ["projects / molecules / conformers", "项目、分子与构象基础信息。"],
        ["gaussian_jobs / gaussian_outputs / parsed_energies", "Gaussian 任务、输出文件和解析能量结果。"],
        ["bond_descriptors / nbo_interactions", "Si–O / Si–Cl 描述符与 NBO 给体-受体相互作用。"],
        ["tea_complexes / ti_complexes / insertion_paths / hydrolysis_paths", "TEA 络合、Ti 毒化、插入路径、水解缩合路径。"],
        ["literature_sources / thesis_entities", "博士论文来源与结构化论文实体。"],
        ["catalyst_models / monomer_families", "催化剂模型与单体族。"],
        ["experimental_datasets / experiment_records / dft_experiment_links", "实验数据与 DFT 描述符关联。"],
        ["mechanism_hypotheses / evidence_items", "可证伪机制假说与证据项。"],
        ["cube_files / reports", "cube 文件元数据与报告内容。"],
    ]
    api_rows = [
        ["接口类型", "接口", "说明"],
        ["分子管理", "GET/POST /api/molecules, GET /api/molecules/{id}", "分子查询、创建和详情读取。"],
        ["Gaussian", "POST /api/gaussian/generate-input, POST /api/gaussian/upload-log", "输入文件生成和输出文件上传解析。"],
        ["解析", "POST /api/parse/gaussian-log", "文本级 Gaussian log 只读解析。"],
        ["分析", "/api/analysis/tea-binding, /ti-poisoning, /insertion-profile, /rate-comparison", "结合能、毒化能、插入势垒和相对速率计算。"],
        ["论文", "POST /api/literature/import-thesis, GET /api/literature/entities", "博士论文文本抽取和实体读取。"],
        ["实验", "POST /api/experiments/import-csv, GET /api/experiments", "实验 CSV 导入与读取。"],
        ["机制", "POST /api/analysis/mechanism-hypotheses", "机制假说评分与中文判断。"],
        ["cube", "POST /api/cube/upload, GET /api/cube/{id}/metadata", "cube 文件元数据登记与查询。"],
        ["报告", "POST /api/reports/generate", "中文科研报告生成。"],
    ]

    body = []
    body.append(p("硅氧键催化量子研究平台", style="Title", center=True))
    body.append(p("SiO Catalyst Quantum Studio Pro", style="Subtitle", center=True))
    body.append(p("软件著作权申请技术说明书", style="Subtitle", center=True))
    body.append(p(f"生成日期：{generated}", center=True))
    body.append(p("适用材料：软件著作权登记、项目技术说明、科研软件验收说明", center=True))
    body.append(page_break())

    body.append(h1("一、软件基本信息"))
    body.append(table([
        ["项目", "内容"],
        ["软件中文名称", "硅氧键催化量子研究平台"],
        ["软件英文名称", "SiO Catalyst Quantum Studio Pro"],
        ["建议登记版本号", "V1.0"],
        ["当前工程版本", "0.1.0"],
        ["软件类别", "科研计算辅助软件 / 量子化学工作流软件 / 化学信息学可视化分析软件"],
        ["开发方式", "独立开发，前后端分离，本地或服务器部署"],
        ["目标用户", "量子化学、计算化学、高分子化学、催化机理与 Ziegler–Natta 催化研究人员"],
    ]))
    body.append(p("本软件面向 Ziegler–Natta 催化剂、TEA 助催化剂、Si–O / Si–Cl 键、甲氧基硅烷功能 α-烯烃共聚单体和插入反应路径，提供从论文知识结构化、分子库管理、Gaussian 文件生成与解析、能量判据计算、实验-DFT 对照、机制假说判别到中文科研报告输出的一体化平台。"))

    body.append(h1("二、开发背景与设计目标"))
    body.append(p("本软件结合博士论文《基于 Ziegler-Natta 催化剂的乙烯、丙烯与功能 α-烯烃单体配位共聚合反应的空间位阻与电子效应研究》的研究背景，围绕功能 α-烯烃在 Ziegler–Natta 催化体系中的插入行为、空间位阻、电子效应和助催化剂相互作用进行软件化建模。"))
    body.append(bullets([
        "将论文中的单体族、链长、催化剂模型、助催化剂和机理结论转化为结构化数据。",
        "支持 DCS、MCSOMe、DMOS 以及 3/5/7-烯基三甲基硅烷和甲基二氯硅烷系列分子的统一管理。",
        "围绕 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、krel 等判据实现严格的能量分析。",
        "在无真实 Gaussian 数据时明确显示“示例数据”，禁止生成伪科学结论。",
        "为中文科研用户提供可视化、可解释、可导出的专业应用研究平台。"
    ]))

    body.append(h1("三、开发语言与技术栈"))
    body.append(table([
        ["层级", "语言 / 框架", "作用"],
        ["前端", "TypeScript、TSX、React 18、Next.js 16", "实现中文科研驾驶舱、页面模块、交互状态、动态加载和可视化组件。"],
        ["前端样式", "TailwindCSS、CSS、Material 3 Expressive 风格", "实现深色/浅色主题、玻璃拟态科研面板、圆角卡片、动效和响应式布局。"],
        ["前端可视化", "Recharts、Framer Motion、lucide-react", "实现雷达图、热图、散点图、能量剖面图、仪表盘、图标和页面动效。"],
        ["前端性能", "Web Worker、Next dynamic import", "实现 Gaussian 大文本本地预览和重组件按需加载，提升界面丝滑度。"],
        ["后端", "Python 3.11+、FastAPI", "提供 RESTful API、文件解析、数据计算和报告生成服务。"],
        ["数据验证", "Pydantic", "实现请求参数校验、响应结构化、错误提示中文化。"],
        ["数据库", "SQLAlchemy、SQLite", "实现 MVP 数据持久化，并保留 PostgreSQL 扩展能力。"],
        ["科学计算", "NumPy、SciPy、pandas、RDKit", "支持分子描述符、实验数据处理、相关性计算和化学结构基础处理。"],
        ["测试", "pytest、httpx、ESLint、TypeScript compiler", "实现后端接口/解析器测试和前端类型、规范检查。"],
    ]))

    body.append(h1("四、代码规模与组成"))
    body.append(p("源码统计口径：排除 node_modules、.next、Python 虚拟环境、缓存文件、日志、数据库、package-lock 和 tsbuildinfo 等非源码文件。"))
    body.append(table(source_rows))
    body.append(table([
        ["目录", "文件数", "代码行数", "说明"],
        ["frontend/app", "3", "150", "Next.js 页面入口、布局与全局样式入口。"],
        ["frontend/components", "12", "2591", "应用主壳、UI 组件、V2 面板、分子视图、解析面板。"],
        ["frontend/lib", "2", "727", "工作台数据、工具函数。"],
        ["frontend/types", "1", "134", "TypeScript 类型定义。"],
        ["frontend/public", "1", "68", "Gaussian 预览 Web Worker。"],
        ["backend/app", "24", "2356", "FastAPI、模型、服务、解析器、报告、数据种子。"],
        ["backend/tests", "3", "188", "后端 API、能量公式、Gaussian parser 测试。"],
    ]))

    body.append(h1("五、总体架构"))
    body.append(p("软件采用前后端分离的 B/S 架构。前端负责中文科研交互、图表、分子展示和局部预览；后端负责文件只读解析、结构化数据存储、能量计算、机制判断和报告输出。"))
    body.append(numbered([
        "表现层：Next.js + React 构建单页科研驾驶舱，左侧中文导航包含论文知识库、分子库、Gaussian 输入生成、Gaussian 输出解析、硅氧键实验室、电子云密度、前线轨道、电荷布居、NBO、QTAIM/NCI、TEA 助剂、Ti 毒化、插入能量面、水解缩合、机制模型、报告生成、数据管理和系统设置。",
        "业务层：FastAPI 提供统一 REST API，封装分子管理、Gaussian 模板、日志解析、能量计算、论文抽取、实验导入、机制判断、cube 元数据和报告生成。",
        "数据层：SQLAlchemy ORM 定义项目、分子、Gaussian 任务、解析结果、实验数据、论文实体、催化剂模型、机制假说、cube 文件和报告等数据表。",
        "安全层：上传文件仅按文本或数据读取，不执行 Gaussian，不执行上传内容，不默认运行任意 shell 命令。",
        "性能层：Gaussian 大文本本地预览放入 Web Worker，重图表和三维视图使用动态加载，页面切换使用 Framer Motion。"
    ]))

    body.append(h1("六、功能模块技术细节"))
    body.append(table(module_rows))
    body.append(h2("6.1 论文知识库模块"))
    body.append(p("论文知识库模块读取博士论文 docx 文档中的 WordprocessingML 文本，抽取题目、摘要和关键词线索，并形成结构化实体。抽取对象包括研究对象、单体族、链长、共聚体系、催化剂模型、助催化剂、DFT 模型和关键机制结论。该模块只读取 docx 文本，不执行宏、嵌入对象或外部程序。"))
    body.append(h2("6.2 分子库模块"))
    body.append(p("分子库模块使用 SMILES 作为分子主标识，结合 RDKit 或近似描述符计算分子量、原子数、重原子数、可旋转键、范德华体积、Si 中心半径、O/Cl 原子数和极性位点数。前端显示中文研究角色、功能位点、电子效应、位阻等级和论文关联结论。"))
    body.append(h2("6.3 Gaussian 输入与输出模块"))
    body.append(p("Gaussian 输入生成模块使用模板化字符串生成 .gjf/.com 输入内容，覆盖 opt/freq/NBO、Counterpoise、π-complex、O→Ti 毒化络合物、插入 TS、IRC、水解和缩合路径。输出解析模块通过 Python 正则表达式扫描 Gaussian log/out 文本，提取能量、频率、电荷、轨道和 NBO 信息。前端 Web Worker 仅用于本地预览，正式结果以后端 API 为准。"))
    body.append(h2("6.4 实验-DFT 对照模块"))
    body.append(p("实验-DFT 对照模块支持用户导入 CSV，将单体、催化剂体系、聚合温度、Al/Ti 比、活性、插入率、1-己烯含量、序列长度、熔点、结晶度和透明性等实验指标与 ΔGπ、ΔG‡、ΔGpoison、TEA binding、steric penalty 和 electronic guiding score 建立关联，并使用散点图、趋势图和一致性矩阵可视化。"))
    body.append(h2("6.5 可证伪机制模型模块"))
    body.append(p("机制模型模块不是简单打分器，而是将每个科学假说拆解为支持证据、反证条件、所需数据、当前数据状态和可信度评分。内置模型包括位阻主导、电子效应导向、TEA 预组织、O→Ti 毒化、链长窗口效应和乙烯/丙烯差异插入模型。"))

    body.append(h1("七、核心数理模型与算法"))
    body.append(p("软件内置能量换算常数和热力学判据，用于从 Gaussian 解析结果或用户输入能量计算相对自由能和速率。"))
    body.append(table([
        ["公式", "含义"],
        ["ΔGbind = G(络合物) − G(单体) − G(TEA)", "TEA 助催化剂络合自由能。"],
        ["ΔGpoison = G(O→Ti 毒化络合物) − G(C=C π-络合物)", "Ti 活性中心毒化判据。"],
        ["ΔGπ = G(π-络合物) − G(游离活性中心 + 单体)", "生产性 C=C π 配位稳定性。"],
        ["ΔG‡ = G(TS) − G(游离活性中心 + 单体)", "插入反应总势垒。"],
        ["ΔG‡complex = G(TS) − G(π-络合物)", "从 π-络合物出发的复合物势垒。"],
        ["krel = exp[−ΔΔG‡ / RT]", "相对插入速率。"],
    ]))
    body.append(table([
        ["常数", "数值"],
        ["Hartree to kcal/mol", "627.509474"],
        ["Hartree to eV", "27.211386245988"],
        ["R", "0.00198720425864083 kcal mol−1 K−1"],
        ["默认温度", "350 K"],
    ]))
    body.append(bullets([
        "若 ΔGpoison > +5 kcal/mol，判断为生产性 C=C 插入占优。",
        "若 0 ≤ ΔGpoison ≤ +5 kcal/mol，判断为 O→Ti 与 C=C 配位竞争。",
        "若 ΔGpoison < 0 kcal/mol，判断为 Ti 活性中心存在甲氧基毒化风险。",
        "若 Si–O 配位后出现键长增大、振动红移、Wiberg 键级下降和 ρBCP 下降，判断为 Lewis 酸配位削弱 Si–O 键。",
        "若 q(O) 更负、ESPmin 更强且 n(O)→Al E(2) 较大，判断为 Al 捕获潜力增强。"
    ]))

    body.append(h1("八、数据库与数据模型"))
    body.append(table(db_rows))
    body.append(p("数据库采用 SQLAlchemy ORM 建模，当前 MVP 使用 SQLite，字段类型和表结构按 PostgreSQL 迁移兼容方式设计。所有关键数据均保留 source/provenance 字段，用于区分真实上传数据、用户输入数据、论文抽取信息和示例数据。"))

    body.append(h1("九、接口设计"))
    body.append(p("后端已实现约 29 个 API 路由，覆盖健康检查、分子管理、Gaussian 输入生成、Gaussian 输出解析、能量分析、论文抽取、实验导入、机制假说、cube 元数据、报告生成和文件校验。"))
    body.append(table(api_rows))

    body.append(h1("十、文件解析与安全机制"))
    body.append(bullets([
        "Gaussian log/out 解析器只读取文本，不执行文件。",
        "cube 解析器只读取文件头、原子数、网格向量和注释信息。",
        "docx 论文抽取器只读取 word/document.xml 等文本节点，不执行宏或嵌入对象。",
        "上传文件扩展名受控，支持 .log、.out、.gjf、.com、.xyz、.csv、.json、.cube、.cub。",
        "Gaussian16 默认不执行，路径需由用户在设置中显式配置。",
        "所有 mock/example 数据均以“示例数据 / MOCK”标注，不能作为真实科学结论。",
        "缺失字段统一返回 null 或“当前文件未提供”，不伪造数据。"
    ]))

    body.append(h1("十一、前端界面与交互设计"))
    body.append(p("前端采用中文科研驾驶舱设计，整体风格参考 Android 16 / Material 3 Expressive，但面向专业科研场景进行克制化处理。界面包含深色/浅色主题、玻璃拟态科研面板、大圆角卡片、胶囊按钮、柔和阴影、动态色彩、平滑页面切换和响应式布局。"))
    body.append(bullets([
        "导航栏全部中文化，包含总览驾驶舱、论文知识库、分子库、Gaussian 输入生成、Gaussian 输出解析、硅氧键实验室等模块。",
        "图表标题、tooltip、legend、单位说明、错误提示和自动机制解释均为中文。",
        "重图表模块使用 dynamic import 按需加载，避免首屏一次性加载全部图表。",
        "Gaussian 大文本预览使用 Web Worker，降低主线程阻塞。",
        "页面切换使用 Framer Motion，实现淡入、位移和模糊过渡。",
        "3D 分子视图提供 fallback 渲染，未加载真实 3Dmol 时仍能显示结构示意。"
    ]))

    body.append(h1("十二、运行环境与适配范围"))
    body.append(table([
        ["类别", "适配内容"],
        ["操作系统", "Windows 10/11、Linux、macOS"],
        ["浏览器", "Chrome、Microsoft Edge、Firefox、Safari 现代版本"],
        ["Node.js", ">= 20"],
        ["Python", ">= 3.11"],
        ["数据库", "SQLite MVP，PostgreSQL-ready schema"],
        ["部署方式", "本地开发、服务器部署、Docker Compose"],
        ["输入文件", ".log、.out、.gjf、.com、.xyz、.csv、.json、.cube、.cub、.docx"],
    ]))

    body.append(h1("十三、测试与验证"))
    body.append(p("当前项目已通过前端类型检查、ESLint、生产构建和后端 pytest 测试。测试覆盖 Gaussian 核心字段解析、NPA 电荷、Wiberg 片段、NBO E(2)、V2 API、实验 CSV、cube 元数据和机制假说接口。"))
    body.append(table([
        ["验证命令", "验证结果"],
        ["npm --prefix frontend run typecheck", "通过"],
        ["npm --prefix frontend run lint", "通过"],
        ["npm --prefix frontend run build", "通过"],
        ["npm run test:backend", "通过，14 个测试用例"],
    ]))

    body.append(h1("十四、可实现结果"))
    body.append(numbered([
        "建立中文科研用户可直接使用的量子化学研究工作台。",
        "将博士论文研究对象与软件数据模型对应起来，形成论文驱动的知识库。",
        "管理功能 α-烯烃、硅烷单体、TEA 助催化剂和催化剂活性中心模型。",
        "生成 Gaussian 输入文件并解析 Gaussian 输出结果。",
        "计算 TEA 结合、Ti 毒化、插入势垒和相对速率。",
        "对实验趋势与 DFT 描述符进行相关性分析和图表展示。",
        "建立可证伪机制模型，输出中文科研判断和反证条件。",
        "导出中文科研报告，明确标注真实数据、用户输入、论文抽取和示例数据。"
    ]))

    body.append(h1("十五、创新点与技术特点总结"))
    body.append(bullets([
        "将 Ziegler–Natta 催化、功能 α-烯烃共聚、Si–O/Si–Cl 电子效应、TEA 助催化剂和 Ti 毒化判据统一到单一软件平台。",
        "针对中文科研用户设计完整中文信息架构，而非简单英文界面翻译。",
        "引入论文知识库，将博士论文中的单体族、链长效应、催化剂模型和机制结论结构化。",
        "同时支持 Gaussian 输入生成、输出解析、cube 元数据、实验 CSV、机制模型和报告导出。",
        "强调可证伪机制模型和数据可靠性，避免将示例数据伪装为真实科学结论。",
        "采用 Web Worker、动态加载和响应式 UI 技术提升大型科研文件处理时的交互流畅性。"
    ]))
    body.append(p("综上，本软件具备明确的科研应用场景、完整的前后端技术架构、可扩展的数据模型、严格的量子化学计算判据和中文科研报告输出能力，可作为面向 Ziegler–Natta 功能 α-烯烃机理研究的专业科研计算应用程序。"))
    return "".join(body)


def content_types() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def document_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>"""


def styles() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:eastAsia="Microsoft YaHei" w:hAnsi="Microsoft YaHei"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:color w:val="0B3A4A"/><w:sz w:val="40"/></w:rPr><w:pPr><w:jc w:val="center"/><w:spacing w:after="260"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rPr><w:color w:val="4A6470"/><w:sz w:val="24"/></w:rPr><w:pPr><w:jc w:val="center"/><w:spacing w:after="180"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:color w:val="0E5266"/><w:sz w:val="30"/></w:rPr><w:pPr><w:keepNext/><w:spacing w:before="360" w:after="180"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:color w:val="1F6E82"/><w:sz w:val="25"/></w:rPr><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/></w:pPr></w:style>
  <w:style w:type="table" w:default="1" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="B7CED6"/><w:left w:val="single" w:sz="4" w:space="0" w:color="B7CED6"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="B7CED6"/><w:right w:val="single" w:sz="4" w:space="0" w:color="B7CED6"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="D4E2E7"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="D4E2E7"/></w:tblBorders><w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
</w:styles>"""


def settings() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/></w:settings>"""


def font_table() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:font w:name="Microsoft YaHei"/></w:fonts>"""


def core_props() -> str:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>硅氧键催化量子研究平台软件著作权技术说明书</dc:title>
  <dc:subject>软件著作权技术说明</dc:subject>
  <dc:creator>SiO Catalyst Quantum Studio Pro</dc:creator>
  <cp:keywords>量子化学;Ziegler-Natta;Gaussian;软件著作权;功能α-烯烃</cp:keywords>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_props() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex OOXML Generator</Application>
</Properties>"""


def document_xml() -> str:
    body = build_body()
    sect = """
<w:sectPr>
  <w:pgSz w:w="11906" w:h="16838"/>
  <w:pgMar w:top="1440" w:right="1260" w:bottom="1440" w:left="1260" w:header="720" w:footer="720" w:gutter="0"/>
</w:sectPr>"""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{body}{sect}</w:body>
</w:document>"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types())
        zf.writestr("_rels/.rels", rels())
        zf.writestr("word/document.xml", document_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels())
        zf.writestr("word/styles.xml", styles())
        zf.writestr("word/settings.xml", settings())
        zf.writestr("word/fontTable.xml", font_table())
        zf.writestr("docProps/core.xml", core_props())
        zf.writestr("docProps/app.xml", app_props())
    print(OUT.resolve())


if __name__ == "__main__":
    main()
