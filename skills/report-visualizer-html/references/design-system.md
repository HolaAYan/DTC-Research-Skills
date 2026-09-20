# Design System & Implementation Reference（设计系统与实现参考）

配合 `SKILL.md` 的 Step 2–5 使用。生成 HTML 前阅读本文件；产出必须遵守这里的令牌、配方与约束。骨架以 `assets/template.html` 为基底，本文件说明"怎么选、怎么写、为什么"。

---

## 1. 信息设计原则（内容 → 视觉的映射）

| 内容类型 | 首选表达 | 何时不用 |
|---|---|---|
| 单个最重要数字（营收、份额、转化） | KPI 卡（大数字 + 标签 + 来源） | 数字本身没有独立意义时并入叙述 |
| 3–5 条关键结论 / Finding | Insight / Finding 卡（编号 + 证据徽章） | — |
| 两个及以上对象对比（渠道占比 / 竞品份额 / 价格 / 评分…） | **定量可排序 → 条形组 `.bars` / 柱状 `.vcols`**；需逐行多列对照才用表格 | 只有 1 个对象 |
| 随时间的变化（融资、营收、里程碑） | Timeline（横向或纵向） | 无时间顺序 |
| 转化/流失/分层路径 | Funnel（阶梯条） | 无漏斗逻辑 |
| 机制/因果/增长引擎 | Flow / relationship map（内联 SVG 节点箭头） | 线性列表更清晰时 |
| 一组对象（产品线/社媒账号/Campaign/用户群） | 卡片网格 + 关键字段 | 对象间需精确对比 → 表格 |
| 原话/官方口径 | Quote 卡（引言 + 出处链接） | 可正常转述时 |
| 大量原始细节 | 折叠 `<details>` / 页尾来源面板 | — |

判断标准始终是：**这个组件是否让读者更快理解？** 不为凑数强塞。

### 1.1 默认可视化规则（可比数据 → 图表，防退化）

这是全篇最重要的一条执行规则：

> **报告中任何一组 ≥3 条同维度、可比较的定量数据（占比 / 份额 / 排名 / 粉丝 / 评分 / 价格 / 数量 / 金额 / 时间点），默认必须用图表组件呈现**（水平条形组 / 垂直柱状 / 环形 / 漏斗 / 层流图，见 §4.8 图表套件）。
>
> 不允许把这样的数据退化为"纯文字列表"或"每行一个孤立的 KPI 卡"；表格只用于需要逐行精确对照多列字段的场景。

数字只做文本罗列 = 信息设计失败。宁可少一张卡，不可少一张图。

例外（允许仅表格/文字）：
- 该组数据本身就是**表格语义**（多列交叉对照：平台 × 角色 × 证据、竞品 × 多维度 × 来源）。
- 只有 1–2 个孤立数字（用 KPI 卡）。
- 数据无法同维度比较（混合口径），勉强制图会误导。此时保留原样并标注口径。

## 2. 视觉系统（中性专业 · 默认）

### 2.1 设计令牌（CSS 变量，明暗双主题）

```css
:root{
  /* light */
  --bg:#ffffff; --surface:#f7f7f8; --surface-2:#eef0f3;
  --border:#e4e6eb; --text:#1a1d21; --text-muted:#5c6470;
  --accent:#4f46e5; --on-accent:#ffffff; --accent-soft:#eef2ff;
  --ok:#15803d; --obs:#1d4ed8; --inf:#b45309; --est:#7e22ce; --unk:#475569;
  --radius:12px; --shadow:0 1px 2px rgba(16,24,40,.06),0 4px 12px rgba(16,24,40,.06);
  --font:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{ --bg:#0e1116; --surface:#171b22; --surface-2:#20262f;
    --border:#2b323d; --text:#e7eaf0; --text-muted:#9aa3b2;
    --accent:#818cf8; --on-accent:#0e1116; --accent-soft:#232754;
    --ok:#4ade80; --obs:#60a5fa; --inf:#fbbf24; --est:#c084fc; --unk:#94a3b8;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 16px rgba(0,0,0,.35); }
}
```

### 2.2 排版与间距

- 正文 15–16px、行高 1.6–1.7；标题层级：Hero H1 clamp(1.6rem,4vw,2.4rem) → 章节 H2 1.25–1.4rem → 卡片 H3 1.05rem。
- 数字/指标用 `--mono` 或加粗 tabular 数字（`font-variant-numeric: tabular-nums`），方便对比。
- 间距按 4px 网格（4/8/12/16/24/32/48）；卡片内边距 20–24px；section 间 40–56px。
- 圆角统一 10–14px；卡片轻阴影 + 1px 边框。

### 2.3 品牌色处理

- 报告关于具体品牌且品牌主色可用 → 用其主色替换 `--accent`（light/dark 各配一档），次级强调色 ≤2 个；徽章语义色不变。
- 可读性约束：正文对比度 ≥ 4.5:1；大面积底色不用品牌高饱和色（用它做点缀/顶部条/标题强调）。
- 无可靠品牌色 → 保持默认中性系统，不要虚构。

## 3. 证据分级徽章（Evidence Badge）

徽章 = 原报告的 `FACT / OBSERVATION / INFERENCE / ESTIMATE / UNKNOWN`（含复合 `FACT/OBSERVATION` 时用其组合或主级，保持原文）。颜色仅作辅助，文字必须可读：

```css
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:.02em;border:1px solid;vertical-align:2px}
.badge.fact{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 45%,transparent);background:color-mix(in srgb,var(--ok) 12%,transparent)}
.badge.obs{color:var(--obs);border-color:color-mix(in srgb,var(--obs) 45%,transparent);background:color-mix(in srgb,var(--obs) 12%,transparent)}
.badge.inf{color:var(--inf);border-color:color-mix(in srgb,var(--inf) 45%,transparent);background:color-mix(in srgb,var(--inf) 12%,transparent)}
.badge.est{color:var(--est);border-color:color-mix(in srgb,var(--est) 45%,transparent);background:color-mix(in srgb,var(--est) 12%,transparent)}
.badge.unk{color:var(--unk);border-color:color-mix(in srgb,var(--unk) 45%,transparent);background:color-mix(in srgb,var(--unk) 12%,transparent)}
```

> 若目标浏览器过旧不支持 `color-mix`，改为硬编码的浅色底/深色字。

图例放首屏或 Hero 下方一行：
`FACT 可验证事实 · OBSERVATION 观察 · INFERENCE 推断 · ESTIMATE 第三方估算 · UNKNOWN 无可靠公开信息`（沿用报告自身对分级的中文解释）。

**注意**：报告未分级的数据点，不要加徽章；报告标注如 `FACT/OBSERVATION` 请保留组合文字或用 `主级·次级` 表示。

## 4. 组件配方

### 4.1 Hero（首屏三件事）

```html
<header class="hero">
  <p class="kicker">DTC GROWTH RESEARCH · 2026-09-08</p>
  <h1>Nike：从批发分销转向 DTC 直营的增长重构</h1>
  <p class="lead"><b>核心结论：</b>……<b>关键短语/数字</b>……（最重要的一句话，1–3 行，重点加粗）</p>
  <div class="meta-chips"><span class="chip">研究对象 Nike</span><span class="chip">证据分级见页尾</span></div>
  <aside class="takeaway">
    <h2>3–5 个关键发现</h2>
    <ol><li><strong>……</strong> —— 一句话解释 <span class="badge fact">FACT</span></li>…</ol>
  </aside>
</header>
```

Takeaway 用高对比容器（`background:var(--accent-soft); border:1px solid var(--border); border-left:3px solid var(--accent)`），是全页最重的视觉块。

**主标题文案铁律（跨介质统一）**：Hero `h1` 固定为 **`品牌名：一句总结性描述`** —— 品牌名在最前 + 中文全角冒号「：」+ 一句陈述式描述（结论 / 定位 / 增长机制），建议 8–28 字，问句与第二层冒号均不可，日期 / 报告类型不进主标题。**同一份报告的 HTML 与 PDF 必须逐字同标题**；两版并存时以用户指定者为准、另一版同步改齐，未指定时后生成方沿用先生成方文案。反例：`从批发分销转向 DTC 直营：Nike 的转型是怎么做成的`（品牌名被挤到冒号后）。

**`.lead`（核心结论段）样式铁律**（两条）：
1. `.lead` 必须 `width:100%` 占满内容区、与上下文同宽，**不要**设 `max-width:xxch` 导致窄于页面。
2. `.lead` 是「结论卡片」而非裸文字：须带 `background:var(--surface); border:1px solid var(--border); border-left:4px solid var(--accent); border-radius:0 var(--radius) var(--radius) 0; padding:14px 18px`——即**细边框 + 左侧 accent 粗线条勾勒 + 浅背景 + 右侧圆角**，与同页 `.takeaway` 视觉呼应；文本色用 `var(--text)`（非 muted）。

**`.lead` 重点加粗规则**：核心结论文本内的**关键短语必须用 `<b>` 加粗**（`.lead b{font-weight:750}`），让读者一眼抓住论证骨架——参考模式：`<b>核心结论：</b>……是<b>「XX + XX」驱动的YY</b>——……<b>关键数字/结论</b>（口径）。

### 4.2 Insight / Finding 卡

```html
<section class="finding-card">
  <div class="finding-head"><span class="fnum">01</span><h3>一家"供应链能力 + 全球品牌叙事"的出海公司，正处于规模化前夜</h3></div>
  <ul class="evidence">
    <li><span class="badge fact">FACT</span> 母公司为…… <span class="src-chip"><a href="https://…" target="_blank" rel="noopener">SRC-001 ↗</a></span></li>
  </ul>
  <p class="analysis">Analysis：……（用视觉区分，如左侧竖线或底色）</p>
</section>
```

Evidence 用列表（保留报告原文的每条来源标注），Analysis 用 `border-left` + 弱化文字呈现，与 Evidence 区明显区分。

### 4.3 KPI 卡

```html
<div class="kpi-grid">
  <div class="kpi"><p class="kpi-label">2024 营收</p><p class="kpi-value">¥21.74<small>亿</small></p>
    <p class="kpi-note">+22.3% YoY · 招股书口径（媒体转引）<a href="…">SRC-002 ↗</a></p></div>
  …
</div>
```

`.kpi-grid{display:flex;flex-wrap:nowrap;gap:16px}` + `.kpi-grid>.kpi{flex:1 1 0;min-width:0}`。**等宽单行铁律**：KPI 卡用 flex 单行排布、每张 `flex:1 1 0` 等宽、共同占满整行——无论 3 张还是 6+ 张都**一行铺满、等宽**，绝不因固定 min 宽度把第 N 张挤到第二行。卡片很多时文字自然换行、卡片自动等比变窄即可，不必设最小宽度。

**KPI 卡内部四铁律**（三部分「小标题 / 大数字 / 解释说明」各自第一行对齐 + 纯数字）：
1. **纯数字**：`.kpi-value` 只放数字本身 + 必要的计量单位（`¥`/`亿`/`万`/`%`/`+`/`/5` 满分），**前后不加描述文字**——如「约 ¥400 亿」写「¥400 亿」（"约"挪到 note）、「5000 万+ 注册用户」拆成 label「MakerWorld 社区注册用户」+ value「5000 万+」。日期只保留到**年-月**（「2020-11-09」→「2020-11」）。评分列**确切数字**、不列范围（「4.4–4.5/5」→「4.5/5」）。
2. **小标题行高统一**：`.kpi-label` 设 `min-height:2.9em;line-height:1.45`（固定 2 行），保证所有卡片的大数字从**同一基线**开始，不因 label 行数不同而错位。
3. **大数字单行**：`.kpi-value` 必须 `white-space:nowrap;overflow:hidden;text-overflow:ellipsis`，字号 clamp `clamp(1.15rem,2vw,1.6rem)`，确保长数字**始终单行**、绝不折成两排。
4. **解释说明第一行对齐**：`.kpi-note` 用 `padding-top:6px;border-top:1px solid var(--border)` 顶部对齐（**不用** `margin-top:auto` 底部对齐、不设 `min-height` 强行等高）——让所有卡片的 note **第一行在同一高度**，长度差异向下自然延展。

### 4.4 表格 / 对比矩阵

```html
<div class="table-wrap">
<table>
  <caption>渠道结构对比（招股书口径，媒体转引）</caption>
  <thead><tr><th>渠道</th><th class="num">2024</th><th class="num">2025 Q1–3</th><th>来源</th></tr></thead>
  <tbody>
    <tr><td>独立站（DTC）</td><td class="num">25.2%</td><td class="num">30.4%</td><td><a href="…">SRC-003 ↗</a></td></tr>
  </tbody>
</table>
</div>
```

`.table-wrap{overflow-x:auto}` 保证移动端；表头 `position:sticky` 可选；列对齐 `.num{text-align:right;font-variant-numeric:tabular-nums}`。对比显著差异可加 `.up{color:var(--ok)}`/`.down{color:var(--inf)}` 等（仅指示方向，加文字/箭头辅助，不纯靠颜色）。

### 4.5 Timeline

纵向（默认，适合少量里程碑混在正文/卡片内）：

```html
<ol class="timeline">
  <li><time>2013-06-18</time><p><strong>品牌成立</strong> —— 首款产品发布 <span class="badge fact">FACT</span></p></li>
  <li><time>2020</time><p><strong>主力产品线推出，首个爆款众筹约 $6.7M</strong></p></li>
  <li><time>2023</time><p>完成新一轮融资，投后估值约 ¥82 亿</p></li>
  <li><time>2026-02-15</time><p>递交主板 IPO 申请</p></li>
</ol>
```

CSS：左竖线（`border-left:2px solid var(--border)`）+ 每项前置圆点（`::before` 绝对定位圆点 `background:var(--accent)`），`time` 用 mono/加粗小字。

横向（`<ol class="timeline-h">`，适合品牌里程碑整段单独一行横向铺开）：

```html
<ol class="timeline-h">
  <li><time>2020</time><p><strong>成立 + X1 众筹</strong>：约 5,575 backers / $700 万</p></li>
  <li><time>2022-11</time><p><strong>TIME 2022 最佳发明</strong></p></li>
  <li><time>2023</time><p>P1 压到 ¥3,000 档；MakerWorld 上线</p></li>
  <li><time>2024</time><p>出货约 120 万台；营收 55–60 亿</p></li>
  <li><time>2025</time><p>营收破百亿；H2D 发布</p></li>
</ol>
```

CSS 已内置（`.timeline-h`：flex 等宽、顶部轴线 + 圆点、`time` 加粗 accent 色）。**选型规则**：里程碑作为独立信息块、且希望横向扫读时用 `.timeline-h`；混在窄卡片或正文里则用纵向 `.timeline`。

**多行自动换行铁律（长历史必守）**：品牌发展历史长（约 ≥6 个节点或内容总量放不下一行）时，`.timeline-h` 必须**自动换行铺满多行直至内容完整呈现**——实现为 `display:flex;flex-wrap:wrap;gap:22px 14px`，每项 `flex:1 1 200px;min-width:150px`。**严禁用 `overflow-x:auto` 横向滚动让读者左右拖动**，也严禁缩字号硬塞一行。换行后每个节点仍保留自己的顶部轴线段 + 圆点（marker 中心精确落在该项轴线左端）；行间留白 ≥20px 与节点间距一致。

### 4.6 Funnel（阶梯）

用 div 宽度递减实现，如：独立站 30.4% → 加购 → 转化（示例性）。标注"示意层级/原文指标"，逐层标注数值 + 来源，缺失的漏斗层**不要编数字**（如报告只有各渠道占比就画占比条，不画转化率漏斗）。

```html
<div class="funnel">
  <div class="fstep" style="--w:100%"><span>曝光 / 全渠道触达</span><b>—</b></div>
  <div class="fstep" style="--w:58%"><span>线上渠道</span><b>58.5%</b></div>
  <div class="fstep" style="--w:30%"><span>独立站</span><b>30.4%</b></div>
</div>
```

`.fstep{width:var(--w);margin-inline:auto;…}` 配渐变底色（CSS 已内置 template Chart suite，直接套用）。

### 4.7 Flow / Relationship map（增长引擎等）

报告给出关系图（如 `growth_engine: nodes + relationships`）时用内联结构渲染。**默认用模板内置的纵向层流**：`.engine > .elayer(可含多个 .enode) + .econn`（关系标签），逐层向下，适配移动端。节点样式已内置（fill var(--surface)、左侧 accent 竖线、`<b>` 层名小标）。节点文字必须用 CSS 变量配色，勿硬编码黑/白。

横向关系网（需左右并列分支）时可自加少量 CSS，或退化为「阶段 → 箭头 → 阶段」的紧凑卡片链；单图节点 ≤ 8，文字 ≤ 16px 可读。

### 4.8 图表套件（默认启用 · Chart Suite）

> 所有图表 CSS **已内置在 `assets/template.html`**（Chart suite 区块），不要自造样式，直接套 class。模板内附 COPY-ME 示例注释。
> 图标原则：每个数据点必须**原样显示真实数值文本**，柱长只做比例示意；每组图配 `chart-note` 注明示意口径 + 证据徽章 + 来源。

**数据 → 图表决策表**

| 数据形态 | 典型出现位置 | 默认图表 | 用法 |
|---|---|---|---|
| 一组占比 / 份额 / 排名（地区、渠道、竞品份额、平台分布、订阅档位） | Market / Acquisition / Social / Competitors | 水平条形组 `.bars` | 每行 label + track/fill + 真实数值；**默认整组同色**，仅真实分组时才用 `c1..c5` + 色键 `.ckey`（见下方"着色语义"） |
| 一组数量需对比量级（粉丝、评论数、条数、金额、backers） | Social / Creator / Metrics | 水平条形组 `.bars` | 同上；`fill` 宽度 = 值÷组内最大×100% |
| 同一指标多档位 / 多时间点（价格阶梯、历年营收、评论增长） | Product / Business | 垂直柱状 `.vcols` | 内联 `style="--v:值;--max:组内最大"`；**整组同色，不给单根换色** |
| 单一关键占比强调（DTC 占比、某渠道占比） | Snapshot / KPI 区 | 环形 `.donut` | 内联 `style="--p:30.4"`（`--col` 默认即主色，通常不传） |
| 层级递减 / 转化结构（渠道漏斗、免费→付费路径） | Conversion / Retention | 漏斗 `.funnel` | `style="--w:值%"`；无数据层不编数字 |
| 机制 / 因果 / growth_engine（nodes+relationships） | Growth Engine / Diagnosis | 纵向层流 `.engine` | `.elayer` 分层（可含多个 `.enode`），`.econn` 标关系 |
| 里程碑 / 时间顺序（融资、产品迭代、Campaign） | Business / Campaign | 时间线 `.timeline` | 已内置 |
| 多列精确对照（平台×角色×证据、竞品多维×来源） | Social / Competitors | 表格 `.table-wrap` | 唯一"表格优先"场景 |

**布局默认**：横向三张并列卡 `.grid3`（或两张 `.cols2`）内嵌小图，比整页大图信息密度更高。参考基准：客户 / 市场节用 grid3 卡分别内嵌「地区分布」「流量国别」「竞品份额」三个 bars 组；获客节 finding 内嵌「赞助平台结构」bars 组 + KPI 卡带 4 个关键指标。

**独立站流量来源（Acquisition 节 · 强制）**
- 报告只要引用站点流量数据（Similarweb / Semrush 等），**禁止只放一个「自然搜索占比」环形**。
- **按主口径 / 参照口径两级呈现**：
  * **① 主口径 = 最新的一手平台数据**（分析依据）。**平台公开几项就呈现几项**——数据充足时用**三张并列 KPI 卡**（`#1/#2/#3` + 渠道名 + 占比 + 一行规模/环比）+ 下方完整渠道表；平台只公开 1–2 个维度时就只放这 1–2 张卡，**不为凑「Top 3」补位或均分余量**。
  * **② 参照口径 = 较早或二手转述**（如有）：**全部并列列出**（不得因为看着矛盾就删），但明确标注"仅作参照，不作为分析依据"，视觉上弱化（次级表格 / `.muted`）。
- 每条给齐：排名 + 渠道名（中英）+ 占比 + 规模 + 环比 + 数据月 + SRC；派生值注明"派生值"。
- 两口径冲突时并列并写明差值 + "跨平台不可相加或互比"，但**这属于方法论注释**——**不得进 Hero 的「关键发现」列表，也不得写进痛点/优势区块**。
- 某渠道占比平台未公开 → 标 **UNKNOWN**，不补数字、不反推；付费搜索等极小值（≈1%）**不要画成长度近零的条**，改用文字数值卡并注明"过短，按比例仅示意"。
- 自然搜索若带**品牌词 / 非品牌词拆分**，一并呈现并**注明该拆分来自哪个口径**（一手 / 参照），决定"承接型 vs 发现型"结论。

**换算与铁律**
- `bar-fill` 宽度 = 该值 ÷ 组内最大值 × 100%（占比较组时可直接用占比值），**不要用数值本身当像素宽度**。
- `vcol` 高同理：`--max` = 组内最大值。
- **多序列色板必须用复合选择器**：写 `.bar-fill.c2` / `.vcol .vbar.c2`，**不要**只写 `.c2`。单用 `.c2`（权重 0,1,0）与 `.bar-fill`（同为 0,1,0）权重相同，会被样式表里后定义的 `.bar-fill{background:…}` 覆盖 —— **症状是所有条都变成同一个颜色、色板静默失效，且不报错极易漏检**。模板已改为复合选择器；如自行增补色板，同步保持复合写法。交付前用 `getComputedStyle` 抽查一条 `.c2` 的实际 `backgroundColor` 是否与 `.c1` 不同。

**着色语义（v1.4 起强制 · 颜色必须承载信息）**

> 判断标准只有一句：**这个颜色在告诉读者什么？** 答不上来就统一用主题色。

- **默认整组同色**：单序列图一律用 `c1`（`--brand` / `--accent`），整组同色。垂直柱状 `.vcols` 不加类即为主色，**不要给其中某一根加色**。
- **只有真实分组才上辅助色**：图内存在真实二分／多分（竞品 vs 本品牌、赞助 vs 自运营、口径 A vs 口径 B、现价 vs 原价）时才用 `c2/c3…`；**有分组就必须在图旁给色键 `.ckey`**（模板内置），并在 `chart-note` 补一句"颜色仅作分组区分，不表示数值高低"。
- **禁用辅助色的三类情形**（实测踩坑，均为"看着像有含义其实没有"）：
  1. **单条高亮** —— 想突出某个 SKU／某渠道，却给它换色。读者会以为"这条性质不同"，而正确做法是靠文案（label 里写"爆款旗舰"）或排序把它放首位。
  2. **时间序列挑一根换色** —— 如"近三月"里把低谷月涂成另一个色，但 `chart-note` 又说不出该月有什么特殊事件。
  3. **量纲不同的并列图形** —— 如"占比 70% 环形"与"总额 $27.59 万环形"并排。两者不可互推，同色反而正确（同属一个成交结构）；用色区分会暗示不存在的对比关系。
- **辅助色是证据分级色，不是调色盘**：`--obs/--ok/--est/--inf` 分别对应 OBSERVATION／FACT 类／ESTIMATE／INFERENCE 徽章。借到图表里**必须显式解释**，否则读者会把"观察级证据"误读成"数据分组"。
- **色键类名用 `.ckey`，不要用 `.legend`**：`.legend` 已被页头证据分级图例占用（`FACT 可验证事实 / OBSERVATION 观察 / …`），复用会因同权重后定义覆盖而破坏页头布局。交付前 `document.querySelectorAll('.legend').length` 应为 1（页头）。

每组图下方一行 `.chart-note`：`柱长按数值比例示意` + `<span class="badge …">分级</span>` + `SRC-NN ↗`（沿用输入 SRC ID）。
- 数值、单位、口径零改动；ESTIMATE 徽章必须保留在 chart-note 或数据点旁。
- 若两组数据量级差异过大（如 $3.3B vs $27M）导致比例失真 → 用 `chart-note` 注明"不等轴，仅示意"或不强排同图，改用表格并列两口径（勿归一化成同图误导）。

**条形图行布局稳定性（label 收边铁律 · v1.3 起强制）**
- `.bars` 的 `.bar-row` 使用**可收缩三列弹性网格**：`grid-template-columns:minmax(0,42%) minmax(60px,1fr) auto`，label 列设 `min-width:0;overflow-wrap:anywhere;word-break:break-word`、轨道列 `min-width:0;width:100%`、数值列定宽自适应且 `white-space:nowrap;justify-self:end`——保证**任意卡片宽度下 label 完整收于容器文字宽度内、不越出页面文字宽度**，同时同一 `.bars` 组内条形轨道左端尽量对齐。
- **严禁旧式硬性定宽网格**（如 `minmax(150px,…) minmax(90px,…) minmax(130px,200px)`）：最小列宽合计会超过窄卡内容宽（约 300px），把 label 挤出到页面文字宽度外。放不下的长 label 让它在自身列内折行（`word-break:break-word` + `.blabel .s` 副标签），不缩小轨道到不可读、不缩字号硬塞、不加横向滚动。
- **备注不塞进数值列**：比例/口径/来源等备注（如"CONTEXT 口径""MakerWorld 占 81.6%"）放到 label 下方的 `.s` 小字（`.blabel .s{display:block;font-size:11.5px;color:var(--text-muted)}`），或统一收进该图 `chart-note`；数值列只放真实数字（可带一行 `<small>` 极短注）。
- 若两行合并展示（如"付费社媒 · 邮件 0.45%+0.39%"）会破坏"一行一值"，应拆成独立行或明确写出两值文本。
- 每组图下方 `.chart-note` 照常保留（示意口径 + 证据徽章 + SRC）。

**作者署名（byline）**
- 页面 footer 预留作者行：`<p><strong>作者：{Name}</strong> · © {year} {Name}，保留所有权利。未经授权不得商用转载。</p>`。
- 何时加：委托方/作者提供姓名时（如"署名 某某"）务必加；未提供则省略，不强加占位。

### 4.9 Quote 卡

```html
<figure class="quote">
  <blockquote>"We always prioritized product quality over short-term volume…"</blockquote>
  <figcaption>— 某品牌联合创始人 <a href="…">来源 ↗</a></figcaption>
</figure>
```

引号用大字号 + `border-left`，figcaption 标注说话者身份与来源（保留原文语言，不翻译官网原话时可加"原话"提示）。

### 4.10 来源面板（页尾折叠，可见但不抢首屏）

```html
<details class="sources">
  <summary>Sources（N 条）· 证据分级说明</summary>
  <ol>
    <li id="SRC-001"><b>SRC-001</b> example.com 官网 — First-party —
      <a href="https://…" target="_blank" rel="noopener">链接 ↗</a> · access 2026-09-08</li>
  </ol>
</details>
```

正文里 `.src-chip`（小型浅底圆角 chip）可 `href="#SRC-001"` 锚点跳转或直链外网——**沿用输入已有的 SRC ID 与 url，不新建**。

## 5. 布局与骨架

- 页宽 ≤ 1100px 居中（`.wrap{max-width:1080px;margin-inline:auto;padding-inline:20px}`）。
- section 标题统一编号（01 / 02…）帮助定位；`<section aria-labelledby>` 或直接 h2。
- 顶部可选细 accent 条（4px 品牌色/主色）强化主题。
- 打印友好：`@media print` 隐藏 details/折叠按钮，背景转白（`print-color-adjust:exact` 视情况）。

### 5.1 品牌速览（Snapshot）卡片布局铁律

品牌速览区常有三类信息块：「商业模式」「渠道结构」「品牌里程碑」（或类似的短文字块 + 时间线块）。**按内容量分组布局，禁止三块竖排等高**：

- **两条短文字块（商业模式 / 渠道结构）+ 一条时间线（里程碑）** → 前两块用 `.cols2`（一行两列等宽），时间线块另起一行、全宽 `.card` 内用横向 `.timeline-h` 铺开。
- **三条等长文字块**（无时间线）→ 用 `.grid3` 一行三列。
- **两块差异明显**（一块文字短、一块是长时间线）→ 文字块 + 时间线块可上下两行，时间线横向铺开。

原则：**先看内容量再定列数**——文字少的块不要硬撑等高竖排导致大块空白；同组等长块用多列，长内容块（时间线）独立全宽横向展开。

## 6. 无障碍与质量红线

- 正文对比度 ≥ 4.5:1；不用纯颜色传达信息（颜色 + 文字/图标并用）。
- 语义化：`header/main/section/article/figure/table`、正确 h 层级；`<html lang>` 匹配报告语种。
- SVG 图表加 `role="img"` + `<title>` 描述；装饰性元素 `aria-hidden`。
- 链接 `target="_blank" rel="noopener"`；可聚焦元素保留 focus 样式（`:focus-visible{outline:2px solid var(--accent)}`）。
- 数值统一使用原报告单位与口径；需要缩写时"中文缩写 + 括号内原文口径"。
- 移动端检查：卡片单列、表格横向滚动、Hero 不溢出。
