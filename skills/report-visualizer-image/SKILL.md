---
name: report-visualizer-image
description: 图片版报告可视化 / Visual Storytelling & Information Design。把已有的研究/分析/Case Study/结构化知识文档转化为一套"同一视觉系统、可直接投放"的 PNG 图片资产（Brand Snapshot、KPI Overview、Growth Engine、Customer Journey、Competitive Landscape、Product Matrix、Campaign Timeline、Customer Voice、Strengths/Pain/Opportunities、Strategic Framework 等），每张图独立成画、1–3 秒可读，适合 PPT/社媒/案例分享。输入任意 .md/.txt/.html/粘贴长文本；含结构化数据层（根键 research: 的 YAML、evidence_type/source SRC-ID 字段体系、Source Registry）时自动优先采用并沿用 SRC ID，没有也能直接从正文抽取，无需用户预重构。只做"理解 → 选故事 → 结构化 → 可视化"，不新增调研、不编数字、不改数值、不虚构品牌身份；保留 FACT/OBSERVATION/INFERENCE/ESTIMATE/UNKNOWN 证据分级与来源标注。与同仓库的 dtc-growth-research 等产出结构化数据的报告天然兼容，但不绑定任何研究 skill。触发：把报告做成图/图片、report to images、图片版报告、海报式洞察图、一页一图的可视化卡片组、给 PPT/社媒用的视觉资产等。输出：品牌目录下 `{brand_slug}_visuals_{日期}_v{N}_{ratio}/`（多版本并存、不覆盖旧版）内含 1600×1200@2x PNG 12–16 张（默认高密度，来源页逐条附完整 URL）+ 画廊 index.html + 可复用 html 源。
---

# Report Visualizer — Image（报告 → 同视觉系统图片集）

## 1. 角色与边界

以 **Visual Storytelling & Information Design Specialist** 身份工作。任务是把已有文档转换为**一套互相一致的视觉资产**，让观众快速理解报告。核心循环：

> Understand（读懂）→ Select（选故事）→ Structure（结构化）→ Visualize（成图）

**本 skill 不是研究代理。** 除非用户明确要求，否则不开展新调研、不核实新来源、不把推断写成事实、不为凑视觉而补数据。输入是唯一事实源。

## 2. 输入兼容

输入形态：本地文件路径（.md/.txt/.html/纯文本）、粘贴文本、对话内长文本。docx/pdf 先抽成文本再进入流程。

内容结构分三类，全部支持，无需用户预重构：

- **A. Executive Summary + Detailed Analysis + Structured Data**
- **B. Executive Summary + Detailed Analysis**
- **C. 其他研究 / 分析 / 案例 / 知识文档**

**结构化数据检测**：通读时留意 YAML/JSON fenced block。典型信号：根键 `research:`、`evidence_type`、`source: SRC-xxx`、`sources:` Source Registry、`metadata.research_date`。

- 存在 → 以结构化数据为**主要结构化来源**，报告正文为上下文（叙事、解释、语境）。
- 不存在 → **直接从正文抽取**所需事实/洞察/关系/指标，绝不要求用户先造结构化数据。

## 3. 工作流程

### Step 0 · 通读与分类
完整读取输入。判断 A/B/C、结构化数据层位置（通常在文末）、Source Registry 及其 SRC ID、报告语种（**图片文案与输入同语种**）、报告主题（是否品牌专属）。

### Step 1 · 提炼核心故事（先于任何制图）
回答：报告的中心故事是什么？**3–7 条最强洞察**是哪几条？哪些关系/对比/时间线/指标值得上图？哪些只值得留白为文字？
优先级铁律：

> 重要洞察 > 有趣信息 > 装饰内容

不要试图可视化一切。

### Step 2 · 选定视觉集（按 §1.7 密度标准铺开）
从参考 `references/design-system.md` 的视觉目录中选出**受报告支撑**的类型，**默认目标 12–16 张**（见 design-system §1.7），不是"报告讲得动的最小集合"；输入确实单薄时才降到 8–10 张，且每页仍须做满信息层（4–5 层、含独立解读层）。必含页清单见 §1.7（Brand Snapshot / 口径对照 / 产品与价格 / 增长机制 / 留存 / 获客 / 创作者生态 / 用户画像 / 口碑双面 / 竞争格局 / Campaign / 优劣势与机会 / 来源总览）——报告有相应内容就出页。
可能类型：Brand/Topic Snapshot、KPI Overview、Growth Engine、Customer Journey、Competitive Landscape、Product Matrix、Campaign Timeline、Acquisition Ecosystem、Customer Voice、Creators & Social、Retention System、Conflicting Estimates、Strengths/Pain/Opportunities、Strategic Framework。
页数多不等于重复：相邻页若讲同一件事，就该合并。每张图必须有一个清晰目的。

### Step 3 · 确立一致视觉系统与品牌身份
1. 先读 `assets/report-canvas.css`（画布 + 设计令牌 + 通用组件的基础 CSS），以它为基底扩展，不另起炉灶。
2. **品牌报告**：以品牌官网/公开视觉身份为主要参考。允许轻量探测官方站点主题 CSS 提取主色/辅色（curl 首页 → 找自定义主题 css → 统计高频色值），也可问用户拿品牌色板。logo 仅在可获取且适用时用（本 skill 不自动下载/嵌入 logo，可用文字字标代替）。
3. **非品牌报告**：用中性专业视觉系统（assets/report-canvas.css 默认令牌即可）。
4. **不发明品牌身份**：色值未验证 → 回退中性系统并说明。
5. 全套图共享同一套设计令牌：主色、辅色、字体层级、间距系统、卡片/边框样式、证据徽章、Source chip、页眉页脚版式。图片要像同一份报告的一页页。

### Step 4 · 逐张设计（版面规划规范见 design-system §2，标题系统见 §3，画布/解剖见 §1）
**先整体构图，后落单个元素。** 每张图按 §2 层级规划：Canvas → Safe Area → Grid → Major Content Areas → Components → Typography → Labels/Sources。任何文字/卡片/图表都不允许脱离整体构图单独摆放。

画布：每张 1600×1200 逻辑像素（渲染 ×2 → 3200×2400 PNG）。统一解剖结构：
- **页眉带**：kicker（EN 标签在前 + 页号在后，如 `BRAND SNAPSHOT · 01 / 09`）+ 主标题（4–16 字、品牌主色、≤2 行，视觉主导）+ 副题（小号浅色承载结论）+ 数据日期 chip——全套同构、同位置（§3）
- **内容区**：一种主视觉 + 简短支撑标签，禁止长段落；主视觉占内容区主体，内容分配不足时按 §2.1 顺序放大组件/增大图示/重排网格，禁止装饰凑数或大片留白
- **页脚带**：图序号/名称 + 数据口径一行说明 + 本图用到的 SRC chips + **作者署名**（页脚右端 SRC chips 之后放 `© {year} {Author}`，样式 `.foot .fby`；作者默认 `Yan`，用户另有指定则用其名——见 design-system §1.4「作者署名」）
- 每张图上所有定量元素保留来源 chip 与证据徽章；估算值标 **ESTIMATE**，图标比例只作示意、数值文本原样显示。
- **几何硬约束**：含时间线/流程/轴的图，marker 几何中心必须落在轴线（同轴同坐标），禁止目测近似；放不下时先重构布局（精简→删冗余→放大组件→重排网格→拆分），最后才动字号，禁止缩字号硬塞（§2、§1.4）。
- **标题提炼**：主标题只留 Core Concept / Core Finding，结论与解释全部下沉副题；标题过长按 §3.1 顺序精简，禁止缩字号迁就长标题。**品牌名按图位分档**：首图主标题必须含品牌名，其余各页不强制——按内容提炼主标题，用「主标题 + 副标题」组合把内容说完整（§3.10）。

### Step 5 · 渲染 PNG

1. **建输出目录**（多版本并存，**永不覆盖已有版本**）：
   - **输入属某品牌目录**（默认）：`<品牌目录>/{brand_slug}_visuals_{YYYY-MM-DD}_v{N}_{ratio}/`
     - `{brand_slug}` 与该品牌报告文件的前缀一致（`bluetti` / `bambulab` / `insta360`…）
     - `{YYYY-MM-DD}` = **成图生成日**（注意不是报告日期，二者可能不同，如报告 09-08、3x4 图集 09-09）
     - `{ratio}` = 画布比例，`4x3`（1600×1200，默认）或 `3x4`（1200×1600），由 §5.1 场景参数决定
     - `v{N}` = **版本序号**：扫描品牌目录下已有的 `{brand_slug}_visuals_*` 目录，取最大 N 后 +1；无则 `v1`。同一品牌多套图并存是常态（设计改版 / 换画布比例 / 重做视觉系统都算新版），**禁止覆盖旧版**。
   - **非品牌报告**：`<输入文件名>_visuals_{YYYY-MM-DD}_v1_{ratio}/`，与输入同目录，版本规则同上。
   - html 源放其下 `src_html/`。
2. 每张图写一个自包含 html（`<link>` 指向同目录 `_sys.css`，由 `assets/report-canvas.css` 拷贝而来并覆写品牌令牌）。
3. 用 `scripts/shot_to_png.py` 批量截图（自动发现本机 Chrome/Edge，1600×1200@2x）。用法见脚本 docstring。
   - **输出目录坑（2026-09 沉淀）**：脚本默认把 PNG 写到 **html 同目录**，而 html 按约定放在 `<图集>/src_html/`，于是 PNG 会落进 `src_html/` 而非图集根目录。必须显式传 `--outdir .`（或图集根目录绝对路径），否则图集根目录会缺 PNG、画廊 `index.html` 的 `<img src="NN_x.png">` 全部 404。
4. 生成 `index.html` 画廊（展示全部 PNG，附每张标题/一句话说明/来源提示），便于整体预览交付。
5. 落盘后：若工作区维护有资产索引文件，为该图集补录一行（含版本、比例、张数、生成日）。

### Step 6 · 质量检查（第 6 节清单全过才交付）
每张 PNG 生成后尽量目检（Read 看图）；若当前环境无法看图，用 `scripts/qc_layout.cjs` 做几何质检（越界 / 裁切 / 页脚侵入），用 `scripts/_geo.cjs` 验正文区占版，并配合像素采样确认非空白、主题色已生效。**含来源总览页时另跑 `scripts/_urlcheck.cjs --registry <sources.md|registry.json>`** —— URL 的静默截断不会越界、不会被 `_geo.cjs` 的 `over` 捕获，只能靠它逐条比对注册表文本并检查 `scrollHeight`；**`--registry` 必传**，不传只验裁切、不验文本逐字一致（输出 `textOk: SKIPPED`）。

## 4. 铁律（源完整性与零新增）

- **只做转换，不做研究**：输入是唯一事实源；不顺手补数据/行业均值/竞品。
- **数值零改动**：原样呈现。确需换算（如 RMB→USD）时同屏标注换算口径并保留原数值与单位。
- **区分事实与分析**：证据分级标签（FACT/OBSERVATION/INFERENCE/ESTIMATE/UNKNOWN，含复合）原样保留并可视区分；INFERENCE 永不表述为事实；无信息处保留 UNKNOWN 或直接留白，不做"看起来有数据"的占位图。
- **引用可追溯**：输入已有 Source Registry → 沿用其 SRC ID 与 url。**正文图用 SRC chip（不铺长 URL）**；**来源总览页必须逐条给出完整 URL**（可复制、可回溯）——这是唯一例外，也是"数据可验证"的落点。没有 registry → 用原文来源标注（来源名短标签 + 可得的 URL）。
- **图片是速读介质**：短标题、短标签、明确数字、短注解；详细解释留在原报告，不上图。

## 5. 输出契约

### 5.1 输出场景参数（开局确认，避免返工）
任务开始时先问用途：**研究展示 / PPT 演示 / 社媒公开**。社媒公开场景默认启用以下口径：
- **画布比例 4:3**：1600×1200 逻辑 px，@2x 输出 3200×2400 PNG，适配主流社媒信息图/轮播比例。
- **正文区占版（design-system §1.3）**：每张图以"副题下缘 → 页脚上缘"为正文区；**内容整体高度 = 正文区 × 70%–80%**，上下居中（`fillPct ∈ [70,80]`、`centerDelta ≈ 0`），块间空隙最小化、块内文字上下居中于容器。**禁止**用大块 space-evenly 或缩字号撑版/缩内容。
  - **收敛配方（2026-09 沉淀）**：首轮探针常有多页落在区间外，一律用**页面本地 `<style>` 覆写**收敛（绝不改 `_sys.css`）。超上限（>80）时**先削减纵向节奏**——`.content{gap}`、各块 `gap`/`row-gap`、卡片 `padding`、网格行距，每次下调 3–6px 后重探；实测 fillPct 与总高度近似线性：**高出 1 个百分点 ≈ 需减约 8–9px 总高**（故 82% → 目标 76% 约需减 50px），优先调间距与 padding，**最后**才动字号且不得低于 §1.4 下限。低于下限（<70）反过来加间距/放大主视觉，不做 space-evenly 硬撑。
- **页眉页脚字号（design-system §1.5）**：页眉 × 26/19 ≈ 1.368、页脚 × (26/19) × 1.2 ≈ 1.642、正文主类 × ≈ 1.52，按"区段缩放"实施。
- **来源日期格式**：只写"数据截至 2026-09"（年-月）；事件本身日期（如上市日）可保留完整。
- **去自指**：图内不出现"出自某报告 / 第几章 / 研究框架名 / 工具名 / 原文 / 正文回溯"等 meta 信息；只保留观众需要的口径说明。
- **作者署名（默认必有）**：**每一张图**的页脚右端 SRC chips 之后固定放 `© {year} {Author}`（作者默认 `Yan`；用户指定其他署名时用其名）。画廊 index.html 同步：每张卡片说明加同一署名行，页尾版权声明也带 `© {year} {Author}`（参照 design-system §1.4）。
- **来源页（必须附完整 URL）**：视觉集最后放来源总览图，每条 = `SRC chip + 类型 tag + 短名 + 完整 URL`（URL 等宽小字折行、**逐条可复制**；**只给来源名不给 URL 视为不合格**）。类型 tag：官网/官方/平台/媒体/社区/估算。**来源页总数硬上限 2 页**（2026-09-17 用户指定，取代旧"≥30 条可拆多页"）——装不下时按 design-system §1.4 档位表**增列数（4→5）+ 降字号**压回 2 页（字号下限：短名 ≥12.5px / URL ≥9.5px / tag ≥9px），**不得加第 3 页**；首页放来源类型分布条、末页放口径说明条（各恒定 4 格）。
- **信息密度（默认 12–16 张）**：按 design-system §1.7 执行——页数由报告内容量决定；每页 4–5 个信息层且**必含独立解读层**；不得回落成"4–8 张轻量集"（输入确实单薄时仍需 ≥8 张并做满信息层）。
- **证据分级图例**：FACT/OBSERVATION/INFERENCE/ESTIMATE/UNKNOWN 五色徽章及一句话含义，在**每一页页脚常驻**（同一行内联，不占内容区）。

- 命名：图集内部为 `<NN>_<visual-slug>.png`（如 `01_brand_snapshot.png`）+ `index.html` 画廊 + `src_html/` 可编辑源；**图集目录本身的命名与版本递增见 Step 5.1**（`{brand_slug}_visuals_{date}_v{N}_{ratio}/`，品牌报告落在品牌目录内）。
- 画布：1600×1200 逻辑 px，渲染 deviceScaleFactor=2 → 3200×2400。
- 每张图的 SRC chips 聚合于页脚，正文 chip 只放 SRC-ID 短码；Evidence 徽章图例在每张图页脚或全套首图说明一次。
- 交付时用 present_files 打开画廊与 PNG。

## 6. 最终质量检查（输出前逐项过）

- [ ] 每张图是否视觉语言/字体层级/间距/卡片风格/图标/图表风格一致，像同一份报告？
- [ ] 品牌报告的视觉身份是否被如实反映（色值来自官网证据或用户提供，未虚构）？
- [ ] 所有数字是否与输入一致？是否有被改动/美化/换算后丢失原口径？
- [ ] 每个定量元素是否有来源（SRC chip）？估算是否标 ESTIMATE？
- [ ] FACT/OBSERVATION/INFERENCE/ESTIMATE/UNKNOWN 区分是否保留、未给未分级数据强贴标签？
- [ ] **证据标签是否统一用 chip**：正文中是否完全用 `.ev` 缩写 chip（FACT/OBS/INF/EST/UNK）表达证据类型，无任何「（INFERENCE）/（OBS，SRC-xxx）/证据：…/Observed/Potential」之类的解释性文字残留？
- [ ] **并列展开部分文字格式是否统一**：同一张图里相同性质的并列元素（如 4 张 KPI 大数字、3 张 SPO 卡、4 张竞品卡、Top5 条形行）是否共用同一字号 / 颜色 / 徽章类型 / 卡片 padding，不出现"其中一张主题色、其它黑色"或"其中一行用 INF chip、其它用 OBS chip"这种半途不一致？
- [ ] 是否避免了无支撑的主张与"假装有数据"的占位图？
- [ ] 每张图是否只有一个清晰目的？文本密度是否适合 1–3 秒读懂？
- [ ] 每张图是否**整体构图**：主视觉占内容区主体、无装饰凑数、同层元素网格对齐（共左/右缘/列）、KPI 等高同基线？
- [ ] **几何硬约束**：时间线/流程/轴类元素 marker 是否真正落在轴线上（同轴同坐标），而非目测近似？
- [ ] **组件与文字匹配**：无小盒塞大文；无文字溢出/裁切/重叠/撞图标；溢出时先重构布局再调字号？
- [ ] **标题系统**：每张主标题 4–16 字、≤2 行、品牌主色，跨图位置/层级/颜色一致；副题更小更浅承载结论；标题未承载整段结论（§3）？
- [ ] **品牌名分档**：首图主标题含品牌名？其余各页按内容提炼、用「主标题 + 副标题」把内容说完整（§3.10）——既无"看不出分析对象"的通用标题，也未把品牌名硬塞进每张标题？
- [ ] **信息密度**：张数 ≥12（输入单薄时 ≥8）？每页 4–5 个信息层且含**独立解读层**（§1.7）？无"一块内容 + 大片留白"页？
- [ ] **来源页 URL**：来源总览页每条 SRC 都附完整 URL（非仅来源名）？**来源页总数 ≤ 2 页**（超出时已按 §1.4 档位表降字号 / 增列数 / 并辅助块，URL 未低于 9.5px）？**是否已跑 `scripts/_urlcheck.cjs --registry <登记表>` 并确认 `urlMismatch=[]`、`urlClipped=[]`、汇总 `pass: true`**（静默截断 `_geo.cjs` 抓不到；不传 `--registry` 会退化成只查裁切）？
- [ ] **流量来源（分口径）**：若报告引用站点流量数据，获客页是否**按「主口径（最新一手数据，公开几项列几项）+ 参照口径（较早/二手，全部并列但仅作参照）」两级呈现**（数据充足时给排名前 3 的全部数据，只有 1–2 项时就只放这 1–2 项、不为凑数补位），而非只有「自然搜索占比」一条？两口径差值是否**只写在方法论注释、没有混进关键发现/痛点**？未公开项是否标 UNKNOWN？
- [ ] **正文区占版（§1.3）**：每张图 `fillPct ∈ [70, 80]`、`centerDelta ≈ 0`、`over=[]`，内容整体居中、上下对称留白；块间空隙最小化（8–18px），块内文字上下居中于容器。
- [ ] **作者署名**：每张图页脚是否都有 `© {year} {Author}`（默认 Yan），画廊卡片与页尾版权是否同步？
- [ ] 留白是否有意（仅区块间/重要元素周围/安全区），无图幅过小或文字过小造成的空区？
- [ ] 整套图能否独立讲清报告核心故事（不需要回原文也能懂大意）？
- [ ] **落盘命名**：是否写入 `<Brand>/{brand_slug}_visuals_{生成日}_v{N}_{ratio}/`？v{N} 是否为已有最大版本 +1（未覆盖旧版）？ratio 是否与实际画布一致？文件名是否无空格/中文/特殊字符？

## 资源索引

- `references/design-system.md` — 视觉系统与设计令牌（画布规范/版式解剖/类型/间距/网格；**§1.7 信息密度标准**：默认 12–16 张 / 每页 4–5 层含独立解读层 / 必含页清单 / 来源页必附完整 URL）、**版面规划与几何规范（§2：内容分配/显式网格/组件尺寸由内容决定/对齐规则/几何硬约束/时间线锚定/溢出预防/有意留白）**、**标题系统规范（§3：标题长度/标题vs副题/统一格式/品牌主色/装饰条/层级/宽度40-70%/跨图一致/提炼优先级；§3.10 品牌名分档：首图必含品牌名、其余靠主标题+副标题）**、图表编码规则（条形/环形/分段条/时间线/流程图/矩阵/KPI 卡）、组件库与解剖配方（每类视觉一张图的布局建议）、文本密度规则、证据徽章与来源 chip 规范、品牌身份处理、渲染与质检清单
- `assets/report-canvas.css` — 画布基础样式 + 设计令牌 + 通用组件 CSS（页眉页脚/KPI 卡/条形组/环形/徽章/chip/面板/网格）；**每轮生成时拷贝为输出目录 `src_html/_sys.css` 并按品牌覆写令牌**
- `scripts/shot_to_png.py` — HTML→PNG 批量截图（本机 Chrome/Edge 自动发现，1600×1200@2x，纯标准库）
- `scripts/qc_layout.cjs` — 可选几何质检（Node 22+）：元素越界 / 主内容侵入页脚检测，用于无法目检 PNG 的无头环境；需传 Chrome/Edge 路径与 html 绝对路径
- `scripts/_geo.cjs` — **正文区几何探针**：量 `bodyH`/`fillPct`/`topGap`/`botGap`/`centerDelta`/`blockGaps`/`over`，按 §1.3 / §1.6 验证 `fillPct ∈ [70,80]`、`centerDelta ≈ 0`、`over=[]`；用法 `node _geo.cjs <chrome.exe> <html…>`。
- `scripts/_urlcheck.cjs` — **来源页 URL 完整性探针**（2026-09 沉淀，同期补 `--registry`）：逐条比对来源卡渲染文本与 Source Registry（逐字一致），并断言 `scrollHeight ≤ clientHeight`（无视觉裁切，`_geo.cjs` 的 `over` 抓不到这类静默截断）。用法 `node _urlcheck.cjs <chrome.exe> <html…> --registry <sources.md|registry.json>`；**`--registry` 必传**，否则只验裁切（`textOk: SKIPPED`）并打印提示。通过线：各页 `urlMismatch=[]` / `urlClipped=[]` + 汇总 `pass: true`（含 Registry 无未落地条目）；短名 `ellipsis` 截断不算失败（`nmClipped` 单列供判断）。**凡出来源页必跑**（§1.4）。
