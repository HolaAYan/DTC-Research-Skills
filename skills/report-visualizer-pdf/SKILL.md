---
name: report-visualizer-pdf
description: 报告可视化 / PDF 信息设计助手。把已有的研究报告 Markdown 转化为一份适合分享展示的专业 PDF 报告。沿用 report-visualizer-html 的信息架构、视觉语言、组件逻辑、证据分级与来源体系，但针对 A4 PDF 重新进行分页与版式设计。输入以 Markdown 为唯一事实源，不开展新调研、不修改数据、不编造信息。自动删除指定的 Part 3、AI/Skill/Agent 操作指令及其他内部操作敏感信息，仅保留可公开分享的研究内容。与同仓库的 dtc-growth-research 产出的 Markdown 报告兼容。触发：把这份报告做成 PDF、导出 PDF、PDF 版报告、可分享的报告 PDF、report to PDF 等。
license: MIT
---

# Report Visualizer — PDF（报告 → PDF）

## 1. 角色与边界

以 **Report Visualization & PDF Information Design Specialist** 身份工作。

任务是把一份已经完成的研究 / 分析 / Case Study Markdown 文档，转换为一份：

* 专业
* 易读
* 适合分享展示
* 适合打印与电子阅读

的 A4 PDF 报告。

本 Skill **不是研究代理**。

除非用户明确要求，否则：

* 不开展新调研
* 不重复核实输入中已有的数据
* 不新增市场 / 竞品 / 社媒数据
* 不引入 Markdown 之外的新事实
* 不编造数字
* 不估算缺失值
* 不修改既有数值
* 不把推断写成事实
* 不删除重要来源标注
* 不改变原始研究结论

完整循环：

**Read → Filter → Understand → Structure → Visualize → Paginate → Export → Validate**

> 具体执行步骤见 **§19 执行流程（Playbook）**；版式规则见 `references/design-system.md`；起点骨架见 `assets/template-a4.html`；渲染与质检脚本见 `scripts/`。

---

# 2. 输入

主要输入：

* 本地 `.md` 文件
* 对话中提供的 Markdown 文档
* 已有研究报告 Markdown

Markdown 是本次任务的**唯一事实源**。

如果 Markdown 中存在 YAML / JSON 结构化数据层：

* 可以使用其作为结构化信息来源
* 但不得新增 Markdown 中不存在的数据
* 正文与结构化数据发生冲突时，不自行判断哪个"更正确"
* 保留原有证据等级与来源体系

---

# 3. 内容过滤

在任何视觉设计之前，必须先执行一次**公开分享内容过滤**。

## 3.1 完整删除 Part 3

如果输入 Markdown 存在 Part 3：

**Part 3 不得出现在最终 PDF 中。**

完整删除：

* Part 3 标题
* Part 3 所有章节
* Part 3 所有正文
* Part 3 所有表格
* Part 3 所有图表
* Part 3 所有建议
* Part 3 所有结论
* Part 3 所有操作说明

不得对 Part 3 做摘要。

不得把 Part 3 改写成更短的版本。

不得在 PDF 中留下"Part 3 已删除"等占位提示。

Part 3 应被视为**不属于公开报告的内部内容**。

> 同类内部收尾块一并删除：`## Final Quality Check`、`## 自检`、`## 质检清单` 等交付自检段落，以及所有 fenced YAML / JSON 结构化数据块（`research:` 数据层属于机器可读内部层，不进入公开 PDF）。
>
> **唯一例外——Source Registry 转写**：§4 与 §13 要求公开报告必须完整保留来源信息。若 Source Registry 恰好位于 Part 3 的结构化数据层内，将其**转写为 PDF 的 Sources 节**（保留 SRC ID / 名称 / 类型 / URL / access 日期），而不是连同 Part 3 一起丢弃。转写的是**引用清单**，不是 Part 3 的叙事、分析或 YAML 结构——Part 3 的标题、章节、YAML 数据层本身一律不得出现在 PDF 中。`scripts/filter_report.py` 会自动完成这次转写（输出 `.sources.md` 侧车文件），并把正文里指向 Part 3 的引用改写到公开版仍然存在的目标，不留悬空指引。

## 3.2 删除内部操作信息

除 Part 3 外，对全文进行一次"公开分享安全过滤"。

删除以下类型的信息：

### AI / Skill / Agent 操作信息

* Skill instructions
* Agent instructions
* AI prompts
* System prompts
* Prompt templates
* Agent workflow
* Skill workflow
* AI generation instructions
* "让 AI 执行……"类操作说明
* 面向 Agent 的任务指令
* 本 Skill 或其他 Skill 的具体实现方式

### 工具操作信息

删除：

* API 调用方式
* API 参数
* CLI 命令
* Terminal commands
* Scraping commands
* 自动化脚本
* RPA 操作步骤
* Tool-specific instructions
* 浏览器操作步骤
* 数据抓取操作步骤
* 文件处理命令
* 调试信息

### 本地 / 内部信息

删除：

* 本地文件路径
* 本地目录结构
* 环境变量
* API key
* Token
* Cookie
* Credential
* 内部 ID
* 私有 URL
* 内部系统地址
* 内部项目路径
* 内部实现备注

### 其他仅用于生成报告的信息

如果某段内容描述的是：

> "如何完成这份研究 / 如何生成这份报告"

而不是：

> "这份研究发现了什么"

则默认视为内部操作信息并删除。

---

# 4. 公开研究内容的保留原则

内容过滤不能误删真正的研究内容。

必须保留：

* Brand facts
* Market facts
* Product information
* Business model
* Traffic / acquisition findings
* SEO / AEO findings
* Social media findings
* Affiliate / partnership findings
* Competitive analysis
* Strategic observations
* Research conclusions
* Data limitations
* FACT
* OBSERVATION
* INFERENCE
* ESTIMATE
* UNKNOWN
* Source information
* Source Registry
* Research date
* Data cutoff date
* Research methodology limitations（如果属于公开研究口径，而不是内部操作）

核心判断标准：

> **"研究发现"保留；"如何进行研究"删除。**

如果无法确定某段内容是否属于内部操作信息：

* 优先保留真实研究结论
* 删除具体操作指令
* 不改变研究本身的事实含义

---

# 5. 与 HTML Skill 的关系

本 PDF Skill 应与 `report-visualizer-html` 保持**同源设计语言**。

HTML Skill 的核心信息设计原则：

**Core Insight → Supporting Evidence → Detailed Explanation**

PDF 必须继续遵循这一原则。

不要把 Markdown 简单逐段转换成 PDF。

不要把 HTML 页面截图后拼成 PDF。

不要机械复制 HTML 的网页布局。

PDF 应该：

> **保留 HTML 的视觉语言与信息设计逻辑，但采用适合 A4 阅读的页面布局。**

---

# 6. 内容结构

默认按照以下逻辑组织：

1. Cover / Report Title
2. Executive Summary
3. Brand Overview
4. Market / Category
5. Product / Business
6. Traffic / Acquisition
7. SEO / AEO
8. Social Media
9. Affiliate / Partnership
10. Competitive / Strategic Analysis
11. Key Findings / Conclusions
12. Sources / Research Notes

但：

**不得为了符合上述结构而创造不存在的章节。**

如果原 Markdown 使用不同的结构：

* 保留其核心信息架构
* 进行合理的 PDF 信息层级整理
* 不改变研究内容

---

# 7. Executive Summary

Executive Summary 是 PDF 的核心入口。

第一页应优先展示：

1. 报告主题
2. 研究对象
3. 研究日期 / 数据截止时间
4. 核心结论
5. 3–5 条关键发现

优先使用：

* Insight card
* KPI card
* 简短结论
* 数据对比
* 小型图表

避免第一页出现大段连续正文。

目标：

> 读者在约 1 分钟内理解这份报告最重要的信息。

---

# 8. 可视化规则

沿用 HTML Skill 的图表逻辑。

> **排序（与 HTML/图片姊妹 skill 同规则）**：名义维度（渠道 / 地区 / 平台 / 竞品）按数值降序；序数维度（价格档位 / 规模分层 / 时间 / 漏斗层级）按固有顺序，禁止按数值重排。**价格类图表一律由低到高**（入门在左、旗舰在右；报价制机型排最后并标注"报价制"）。
>
> **时间口径（同规则）**：图表标题、KPI 标签、图注与来源节**禁用相对时间**（「上月」「近三个月」「过去 12 个月」「去年同期」）——PDF 会被下载、打印、归档，相对时间立刻失效。一律换绝对年月：`2026-08`、`2026 年 6–8 月`、`2025-09 – 2026-08`。来源只给滚动区间时，换算后须在图注标明「按平台发布日推算，平台未公布绝对起止」，不能把推算值当平台公布值陈述。

如果报告存在：

**≥3 条同维度可比较的定量数据**

优先使用：

* Bar chart
* Column chart
* Donut chart
* Funnel
* Timeline
* Comparison visualization

而不是简单列出数字。

**独立站流量来源（Acquisition 节 · 强制）**：

* 报告引用站点流量数据（Similarweb / Semrush 等）时，**不得只放一个「自然搜索占比」环形**。
* **按主口径 / 参照口径两级呈现**：
  * **① 主口径 = 最新的一手平台数据**（分析依据）——**平台公开几项就呈现几项**：数据充足时用**三张并列 KPI 卡** + 下方完整渠道表；平台只公开 1–2 个维度时就只呈现这 1–2 项，**不为凑「Top 3」补位**。
  * **② 参照口径 = 较早或二手转述**（如有）——**全部并列列出**，但标注"仅作参照，不作为分析依据"，视觉弱化（次级表格 / `muted` 色）。
* 每条给齐：排名 + 渠道名（中英）+ 占比 + 规模 + 环比 + 数据月 + SRC；派生值注明"派生值"。
* 两口径冲突时并列并写明差值 + "跨平台不可相加或互比"，但**这属于方法论注释**——**不得进 Hero「关键发现」列表，也不得写进痛点/优势区块**。
* 平台未公开的占比标 **UNKNOWN**，不补数字、不反推；付费搜索等极小值（≈1%）**不要画成长度近零的条**，用数值卡呈现。
* 首名若带**品牌词 / 非品牌词拆分**，一并呈现并**注明该拆分来自哪个口径**（一手 / 参照）。

但：

* 不创造新数据
* 不估算缺失数据
* 不改变数字
* 不改变单位
* 不改变数据口径

如果数据不足以制作可靠图表，则使用：

* KPI
* Insight card
* Table
* Textual comparison

---

# 9. 视觉系统

如果报告针对具体品牌：

沿用该品牌的视觉身份：

* 主色
* 辅助色
* 中性色
* 品牌风格

但视觉信息只用于：

> **Information Design**

不得因为设计需要而新增品牌事实。

如果 Markdown / 已有 HTML 中已经存在明确的品牌色：

优先沿用。

如果没有：

可以参考已知品牌视觉身份建立视觉主题，但不得进行额外品牌研究。

---

# 10. PDF 页面设计

默认：

**A4 Portrait**

页面应具有明确的：

* 页面边距
* 标题层级
* 页眉 / 页脚
* 页面编号
* Section hierarchy
* 内容区
* Source 区域

PDF 不需要与 HTML 的网页高度保持一致。

HTML 与 PDF 的区别：

### HTML

* Web-first
* 响应式
* 无限滚动
* 屏幕阅读优先

### PDF

* A4
* 页面化
* 打印友好
* 连续阅读优先

二者应共享：

* 内容
* 信息架构
* 视觉语言
* 色彩
* 字体层级
* 图表语言
* Card style
* Source style

但不强制共享：

* 页面尺寸
* 网页 grid
* section 高度
* 滚动行为

---

# 11. 分页规则

使用通用分页规则，不针对某一个品牌报告手工制定页面。

必须：

* 避免标题单独出现在页面底部
* 避免卡片从中间被切开
* 避免图表从中间被切开
* 避免 Timeline item 从中间被切开
* 尽量保持 Figure + Caption 在一起
* 尽量保持 Table header + 第一行在一起
* 尽量保持短的 Insight block 完整
* 大型章节允许自然跨页

不要：

* 为每个章节强制一页
* 为每个报告手动指定分页位置
* 因为避免分页而产生大量空白
* 把所有内容强行压缩到少数页面

核心原则：

> **优先保证阅读连续性，而不是追求固定页数。**

---

# 12. 表格

Markdown table 应根据内容决定最终表现形式。

如果适合视觉比较：

→ 转换为 Chart / Comparison card

如果需要精确逐行比较：

→ 保留为 Table

表格必须：

* 可读
* 不过度压缩
* 长文本自动换行
* 表头清晰
* 跨页时重复表头
* 尽量避免单行被拆开

---

# 13. 来源与证据

完整保留原 Markdown 的：

* Source ID
* Source name
* URL
* Access date
* Evidence type
* Data limitation

证据等级：

* FACT
* OBSERVATION
* INFERENCE
* ESTIMATE
* UNKNOWN

必须保持原始含义。

不得因为 PDF 视觉设计而删除来源。

可以将来源设计为：

* Source chip
* Footnote
* Source note
* Sources section

但不得伪造来源。

---

# 14. 数值完整性

原始 Markdown 中的数值必须保持：

* 数值一致
* 单位一致
* 时间范围一致
* 数据口径一致

不得：

* 四舍五入导致含义变化
* 改写为更漂亮的数字
* 添加未经提供的百分比
* 补全缺失数据

如果为了视觉展示必须进行格式转换：

必须同时保留原始口径。

例如：

原文：

21.74 亿元人民币

可以显示：

¥21.74B

但必须确保原始单位 / 口径不会被误解。

---

# 15. PDF 不应复制 HTML 页面

禁止：

* 截取整个 HTML 长页面作为一张 PDF
* 把网页缩小后塞进 A4
* 为了保持 HTML 像素尺寸而牺牲可读性
* 直接把 HTML 的 viewport 强制缩放到 A4
* 使用截图作为最终 PDF 的主要内容层

目标不是：

> HTML screenshot → PDF

目标是：

> Markdown research → PDF information design

---

# 16. 输出文件

默认输出：

`{brand_slug}_report_{YYYY-MM-DD}.pdf`

命名规则沿用 HTML Skill：

* 小写字母
* 数字
* `_`
* `-`
* `.`
* 不使用空格
* 不使用中文文件名

如果输入：

`BrandA/branda_report_2026-09-08.md`

输出：

`BrandA/branda_report_2026-09-08.pdf`

**落盘位置（Report Library Convention，与同仓库的 `report-visualizer-html` 一致）**：

1. **输入已在品牌目录内**（如 `BrandA/branda_report_2026-09-08.md`）→ 沿用该目录与前缀，只换扩展名 → `BrandA/branda_report_2026-09-08.pdf`。
2. **输入为平铺文件**（未归入品牌目录）→ 推导标准名 `{brand_slug}_report_{YYYY-MM-DD}.pdf` 放入品牌目录；`brand_slug` = 品牌名小写去空格与特殊字符（`Acme Corp` → `acmecorp`）；日期取报告数据截止日 / 研究日期（缺失用今天）；目录不存在则先建。
3. **非品牌专属报告**（行业分析、通用研究）→ `<输入文件名>.pdf`，与输入同目录。
4. **覆盖规则**：同品牌同日期视为同一报告的新版本，**直接覆盖**；用户要求保留旧版才加后缀。
5. 用户显式指定文件名 / 路径时，以用户指定为准。

写完后若工作区有报告索引文件（如 `INDEX.md`），确认该 PDF 一行已记录（无则补）。

---

# 17. 输出前质量检查

## Content

* [ ] Part 3 已完全删除
* [ ] AI prompts 已删除
* [ ] Skill / Agent instructions 已删除
* [ ] 工具操作信息已删除
* [ ] API / Token / Credential 已删除
* [ ] 本地路径已删除
* [ ] 内部实现信息已删除
* [ ] 真实研究内容完整保留
* [ ] 数值没有被修改
* [ ] 研究结论没有被改变
* [ ] Source information 完整保留

## Information Design

* [ ] 第一页能快速理解报告主题
* [ ] 核心结论视觉上最突出
* [ ] 3–5 条关键发现清晰可见
* [ ] Core Insight > Supporting Evidence > Detailed Explanation
* [ ] 没有机械复制 Markdown
* [ ] 没有大面积无意义文字堆积

## Visualization

* [ ] ≥3 条可比较定量数据优先使用图表
* [ ] 图表数据与原文一致
* [ ] 图表没有虚构数据
* [ ] 图表标题清晰
* [ ] 图表不会被分页切断

## PDF Layout

* [ ] A4 页面尺寸正确
* [ ] 页面边距一致
* [ ] **封面主标题为「品牌名：一句总结性描述」**（品牌名在前 + 中文全角冒号），且与同报告 HTML 版主标题**逐字一致**（用户指定版优先）
* [ ] 标题没有孤立
* [ ] Card 尽量不被切开
* [ ] Table 不出现严重断裂
* [ ] Figure 与说明尽量保持在一起
* [ ] 页面没有严重空白
* [ ] 没有文字溢出
* [ ] 没有图片变形
* [ ] 没有内容被裁切
* [ ] 页码连续
* [ ] 字体可读

## Final

* [ ] PDF 可以直接分享
* [ ] 不包含任何内部操作信息
* [ ] 不需要用户手动调整页面
* [ ] 与 HTML 使用同一套视觉语言
* [ ] 但 PDF 已针对 A4 阅读重新排版

> 上述清单由 **§19 Step 7** 的脚本检查 + 目检共同覆盖，具体命令见该节。

---

# 18. 最终原则

本 Skill 的核心不是：

**Markdown → PDF**

而是：

**Research Markdown**
→ **Remove Internal Content**
→ **Understand**
→ **Structure**
→ **Visualize**
→ **A4 Editorial Layout**
→ **PDF**

始终遵循：

**Research integrity > Information hierarchy > Visual clarity > Pagination > Decoration**

不要为了"看起来漂亮"而改变研究内容。

不要为了"和 HTML 一样"而牺牲 PDF 的阅读体验。

最终 PDF 应当被视为：

> **同一份研究报告的专业、可分享、A4 化版本。**

---

# 19. 执行流程（Playbook）

## Step 0 · 通读与分类

完整读取 Markdown。判断：

* 结构类型（Part 1/2/3？或 Executive Summary + Detailed Analysis？或其他）
* 是否有结构化数据层（YAML / JSON fenced block）
* Source Registry 位置（通常在文末）与其 SRC ID 体系
* 报告语种（**PDF 默认与输入同语种**）
* 是否品牌专属、品牌色是否已在输入 / 既有 HTML 中出现

## Step 1 · 内容过滤（先做，再设计）

按 §3 执行：

1. 可先用脚本做一次**确定性剔除**（删 Part 3、自检段、YAML 数据块；从被删内容里抢救 Source Registry；并列出可疑的路径 / 密钥 / 命令行供人工判断）：

   ```bash
   python scripts/filter_report.py <报告.md> -o <报告.public.md>
   ```

   脚本只做**可判定的机械删除**（Part 3 / Final Quality Check / fenced YAML 块 / 明确命中路径与密钥模式的行），它不替代语义过滤。若抢救到来源，会额外写出 `<报告>.sources.md`（SRC ID / 名称 / 类型 / URL / access 日期），直接用作 PDF 的 Sources 节底稿。

   正文里指向被删章节的引用（如"完整来源记录见 Part 3 的 Source Registry"）会被**自动改写**到公开版仍然存在的目标，不会留下悬空指引；无法机械判断的裸指针（如"本报告分 Part 1 / Part 2 / Part 3"）会在报告里单独列出，需人工处理。**本链路不要加 `--merge-sources`**：Sources 节由本 skill 从 `.sources.md` 生成，并回会重复。该开关只用于 md 本身即为最终交付物、需要自包含的场景。
2. 再对过滤后的文本做**语义二次过滤**（§3.2）：AI / Skill / Agent 指令、工具与 API 操作、本地路径、内部备注，"如何做研究"类内容一律删除。
3. 过滤后自检：脚本的痕迹扫描段落应收敛到零（少量命中需逐条判断，例如正文正常提到"后台指标"不等于内部操作说明）。

**过滤后的文本才是后续所有设计的事实源。**

## Step 2 · 提炼核心

回答：报告在讲什么？最重要结论是什么？3–5 个关键发现是哪些？哪些关系 / 对比 / 时间线 / 指标值得上图？哪些只值得保留为文字？

优先级铁律：**Core Insight > Supporting Evidence > Detailed Explanation**。

## Step 3 · 信息架构与页面规划

1. 按 §6 组织章节，**不创造不存在的章节**。
2. **第 1 页 = Cover + Executive Summary 合并页**：报告主题（kicker + 主标题）、研究对象 / 研究日期 / 数据截止的 meta chips、核心结论 `.lead`、3–5 条关键发现 `.takeaway`、KPI 行或小图、证据分级图例一处。这一页同时承担封面与速览职能，是 §7 的落地形式。
2b. **封面主标题文案（跨介质统一 · 强制）**：封面 `h1` 固定为 **`品牌名：一句总结性描述`** —— **品牌名在最前**，紧跟**中文全角冒号「：」**，冒号后跟**一句陈述式总结描述**（结论 / 定位 / 增长机制），建议 8–28 字；问句、第二层冒号、"深度研究"之类报告类型字样与日期一律不进主标题（日期放 kicker 与 meta chips）。品牌名写法 `英文名 中文名` 或 `中文名（英文名）`，与报告其余部分统称一致；非品牌报告用研究对象 / 主题名。
   * **与 HTML 版逐字一致**：同一份报告的 PDF 与本 skill 姊妹 `report-visualizer-html` 产出的 HTML，主标题文案必须**完全相同**，不得因介质不同改写措辞。若 HTML 版已先产出，**直接沿用其 `h1` 文案**；若用户指定以某一版为准（如"以 PDF 版标题为准"），以用户指定版为准，并**回改另一版同步对齐**。可为版式调字号 / 换行，但不得改动文字与标点。
   * 正例：`Nike：从批发分销转向 DTC 直营的增长重构`、`Patagonia：以环保主张构建的高溢价 DTC 品牌`；反例：`从批发分销转向 DTC 直营：Nike 的转型是怎么做成的`（品牌名不在前）。
3. 估算页数：A4 正文区高约 258mm（297 − 上 17 − 下 22）/ 731pt，正文 10.5pt × 1.62 行高下每页约 40–44 行。章节按内容量自然分页，**不强行一页一节**。
4. 规划分页保护：每个卡片 / 图表 / 时间线 / 表格行组挂上 `avoid-break`；标题挂 `keep-with-next`。

## Step 4 · 品牌 / 主题视觉

* 报告关于具体品牌且品牌色可用（输入或既有 HTML 中已有）→ 替换 `--accent` 等令牌，另配 1–2 个辅色。
* 无法验证品牌色 → 使用模板的中性专业令牌，**不虚构**。
* 用户给了色值 / 风格 → 以用户为准。
* 视觉只服务信息设计，借此新增品牌事实属于越界。

## Step 5 · 生成 A4 HTML

1. 先读 `assets/template-a4.html`，以它的令牌、`@page` 规则、分页工具类、组件与 Chart suite 为基底填充语义内容，**不要自造一套新样式**，也不要照搬 html skill 的网页模板（网页模板含 `sticky`、`details` 折叠、hover、`clamp()` 视口字号等打印下失效或失配的写法）。
2. 在 `<head>` 写两个 meta，供渲染脚本读取：

   ```html
   <meta name="rv-footer-label" content="品牌 · 报告类型 · 年份">
   <meta name="rv-author" content="Yan">
   ```

3. 遵守 `references/design-system.md`：字号下限、分页规则、图表换算铁律、证据徽章与来源 chip、页脚与页码规格。
4. **图表默认上图**：凡 ≥3 条同维度可比定量数据，用 `.bars` / `.vcols` / `.donut` / `.funnel` / `.engine`（模板已内置 CSS 与 COPY-ME 示例），并配 `.chart-note`（"按比例示意" + 证据徽章 + SRC）。
5. 证据分级保留原报告标注，用 `.badge`（FACT/OBS/INF/EST/UNK）呈现；**图例在全文档出现一次即可**（第 1 页 + Sources 节），不必每页重复。
6. **来源区块不用 `<details>` 折叠**（打印时折叠内容不显示），直接以开放区块呈现 Source Registry 全文，并在正文数据点旁放 `.src-chip`（沿用输入 SRC ID）。
7. 明暗主题：模板仅在屏幕模式下响应系统暗色；**打印恒为浅色**，这是刻意的，不要为 PDF 做深色版。
8. **去掉模板自指（§15）**：`assets/template-a4.html` 头部注释块含本 skill 名称与工具字样。以它为基底生成时，把该注释替换为中性说明（如"A4 报告版式骨架 + 品牌令牌覆写"）。
   * 注意 `qc_pdf.py` 的 HTML 扫描会**先剥离 `<style>` / `<script>` / HTML 注释再匹配**（`scan_html()`），所以写在 CSS 注释里的工具自指**不会被机器检出**——它是"机器不报、人眼可见"的盲区，必须靠这一步人工处理。扫描真正覆盖的是正文可见文本（Part 3 / YAML 块 / 本地路径 / 密钥 / CLI / Agent-Skill 措辞 / `report-visualizer-*` 工具名）。
9. **构建卫生（实测易踩）**：
   * **同一个 HTML 文件的多处改动必须串行应用**。并行下发多个编辑会相互覆盖，只有最后一条落盘，前面全部丢失且表面"成功"——改完务必 grep 复核关键词是否真的写入。
   * **超长 A4 HTML 分两次落盘**。A4 版式骨架体积大，单次 Write 写完全文易被模型输出上限截断（末尾被吞、表面"成功"）——先 Write 写完 `<head>`+样式+前半章节，结尾放唯一占位注释（如 `<!--PART2-->`），再用 Edit 替换为后半章节，最后跑标签配平脚本复核闭合。
   * **40+ 条 Sources 用双栏排布**。`.sources ol{columns:2;column-gap:14pt}` + 逐条 `break-inside:avoid`，配合"删逐条重复 access 日期改节首全局声明"，40 条可在约 1.3 页内排完且行不跨栏断开。
   * 生成的 A4 HTML **不要写进品牌目录并使用报告 HTML 同名文件**（会覆盖 `report-visualizer-html` 的网页版产物）。中间源文件放工作区之外的构建目录（如 `build/<brand>/<同名>.a4.html`），只有 PDF 进品牌目录。
   * **`.c1–c5` 必须写在所有图表组件之后**。`.bar-fill` / `.vcol .vbar` / `.donut` / `.fstep` 都自带 `background:var(--accent)`，与 `.c2` 同为单类名同权重——若 `.c1–c5` 写在它们**之前**，后声明的组件默认色会赢，`c2..c5` 静默失效、所有分组条退化成主色（**机检不报、只有目检或数像素才能发现**）。模板已把色板块移到文件末尾，自建样式时勿再前置。
   * **`<span>` 承载 `.bar-track` / `.bar-fill` 时须 `display:block`**。span 默认 inline 会让 `width`/`height` 失效 → 轨道照常渲染、填充整体不可见（表现为"只有灰条没有彩色"）。模板示例用 `<div>`，用 span 时靠 CSS 兜底。
   * **不要给每个 `<section>` 挂 `page-break`**，也**不要给 `.chart-block` 整块挂 `break-inside:avoid`**。前者让每节尾页大片留白（实测 23 页 → 19 页、留白页 6 → 1）；后者一旦该块高于一页，会被整体推到下一页并照样溢出。正确做法：只给**真正需要另起**的章节（如综合诊断、Sources）加 `page-break`；`.chart-block` 不设 avoid，改由 `.chart-title{break-after:avoid}` 绑定标题与图表，卡片的原子性交给 `.card.avoid-break` / `.table-wrap.avoid-break` / `.camp` 等底层单元。
   * **`qc_png/` 落在 PDF 同级目录**（不是脚本目录）——目检后必须从品牌目录删除，别留在交付目录里；重渲染前也要先删，否则残留上一版页序导致目检误判页码。
   * 交付 PDF 若被预览器占用，`cp` 会报 `Device or resource busy`——稍等重试或用其它方式覆盖，然后 `cmp` 确认交付文件与 build 产物一致。
10. **分节处留白与 Sources 压缩**：见 `references/design-system.md` §3.4 与 §6.7.1（长证据列表拆两列是最有效的降高手段；Sources 条目多时按 §6.7.1 的顺序压缩，不要先动字号）。

## Step 6 · 渲染 PDF

```bash
# 默认 A4 纵向；脚本自动发现本机 Chrome / Edge
node scripts/html_to_pdf.cjs <报告.html> <输出.pdf>
```

* 脚本通过 CDP `Page.printToPDF` 渲染：真正的**矢量文本 PDF**（非截图），`printBackground` 开启，页边距 / 页面尺寸由 CSS `@page` 决定，**页脚由脚本注入**（左：`rv-footer-label`；右：`第 X 页 / 共 Y 页`），逐页重复且页码自动递增。
* 常用参数：`--no-footer`（不要页脚 / 页码）、`--label "..."`（覆盖页脚左侧文字）、`--scale 1`、`--browser <path>`、`--timeout <s>`、`--simple`（降级为 CLI `--print-to-pdf`，无页码，用于 CDP 不可用时）。
* 若本机没有 Node，或 CDP 失败：用 `--simple`，或直接 `chrome --headless=new --print-to-pdf=out.pdf --no-pdf-header-footer <file-url>`（无页码）。

## Step 7 · 质检

```bash
python scripts/qc_pdf.py <输出.pdf> --html <报告.html>
```

脚本检查：

* **结构**：页数、`MediaBox` 是否 A4（595×842pt±2）、是否为合法 PDF
* **版式**：逐页墨迹覆盖率（近似空白页 / 过满页告警）、正文包围盒是否越出页边距、页脚是否存在（渲染时用了 `--no-footer` / `--simple` 则加 `--no-footer` 跳过该项）、逐页渲染 PNG 便于目检
* **内容安全**：扫描最终 HTML 是否残留 Part 3、YAML 数据块、本地路径、密钥 / token、CLI / 抓取命令、Agent / Skill 指令、工具名自指等内部痕迹

退出码：`0` 全部通过 / `1` 有告警（建议处理，如近似空白页）/ `2` 硬错误（非法 PDF、非 A4）。

然后**目检渲染出的 PNG**（脚本输出到 `qc_png/`）：确认首页信息层级、图表完整、卡片未被切开、标题未孤立、页脚位置正确。

> 依赖：结构检查为纯标准库；渲染 PNG 与墨迹检测需要 `pypdfium2` + `pillow`。缺失时脚本给出安装提示并只跑结构检查（建议装进独立虚拟环境，避免污染系统 Python：
> `python -m venv .venv` → `.venv/bin/python -m pip install pypdfium2 pillow`（Windows 为 `.venv\Scripts\python.exe`））。

## Step 8 · 落盘

按 §16 命名与落盘，用 `present_files` 打开 PDF；如有报告索引文件（如 `INDEX.md`）则补录一行。

## 收尾自检（§17 清单的落地口径）

* 过滤层：Part 3 / 自检段 / YAML / 内部操作信息零残留（Step 1 grep + Step 7 脚本双查）
* 数值层：抽样比对 3–5 个关键数字与原文一致（数值 / 单位 / 口径）
* 版式层：A4 尺寸正确、页码连续、无空白页、无越界、卡片与图表未被切开
* 叙事层：第 1 页 1 分钟可懂；核心结论视觉最重；细节向下渐进披露

---

## 资源索引

- `references/design-system.md` — **A4 版式规范**（页面几何 / 页边距 / 字号体系与下限 / 行高）、**分页规则与打印铁律**（`break-*` 用法、卡片与图表保护、表格跨页表头、孤行控制、Chrome 打印已知坑表）、页眉页脚与页码规格、设计令牌（与 HTML skill 同源）、组件配方（KPI / Insight / Timeline / Table / Quote / Chart suite / 证据徽章 / 来源 chip）、图表数据→图表决策表与换算铁律、品牌色处理、首页（Cover + Executive Summary）版式、质量红线
- `assets/template-a4.html` — **A4 打印起点骨架**：`@page` 规则、打印令牌、分页工具类（`.avoid-break` / `.keep-with-next` / `.page-break`）、全部组件与内置 Chart suite（bars/vcols/donut/funnel/engine + c1–c5）、`<template id="chart-suite-copyme">` 示例、页脚 meta 占位；**生成时以此为基底填充语义内容**
- `assets/template-a4-preview.pdf` — 由 `template-a4.html` 用本 skill 工具链渲染出的 2 页 A4 样张（占位内容），用于（a）确认工具链可用、（b）目视核对版式基线
- `scripts/html_to_pdf.cjs` — HTML → PDF 渲染器（Node 22+ 标准库，CDP `Page.printToPDF`，A4、矢量文本、注入页码页脚、逐页重复）
- `scripts/filter_report.py` — 公开分享内容过滤辅助（确定性剔除 Part 3 / 自检段 / YAML 数据块 + Source Registry 抢救为 `.sources.md` + 正文断链改写 + 内部痕迹扫描报告；`--merge-sources` 可将来源登记并回公开版 md）
- `scripts/qc_pdf.py` — PDF 质检（尺寸 / 页数 / 墨迹覆盖 / 正文包围盒越界 / 页脚存在性 + 逐页 PNG 渲染 + HTML 内容安全扫描；退出码 0 通过 / 1 告警 / 2 硬错误）
