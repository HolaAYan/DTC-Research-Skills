# DTC Research Skills

面向出海 / DTC 品牌增长研究的一套 Agent Skills：**先做严谨的系统研究，再把同一份研究变成可读的可视化报告。**

skill 之间构成一条完整链路——一次研究，三种交付形态：

```
                                      ┌──►  report-visualizer-html
                                      │        报告 → 单文件 HTML
                                      │
dtc-growth-research  ─────────────────┼──►  report-visualizer-pdf
   研究 → Markdown 报告                │        报告 → A4 PDF
                                      │
                                      └──►  report-visualizer-image
                                               报告 → PNG 图片集
```

研究一次，下游可直接复用：报告里的结构化数据层（YAML）可以被多个可视化产物消费，不必重做调研。

---

## 这套 skill 解决什么问题

拆解一个 DTC / 独立站品牌的增长体系，通常要回答：它是谁、卖什么、卖给谁、如何获客、如何转化、如何留存、靠什么增长。市面上的公开资料零散且真伪混杂，随手一问得到的往往是"看起来很完整"的模糊说法。

这套 skill 把这件事变成一套**有证据纪律的流程**：

- 每条重要信息标注证据等级：`FACT` / `OBSERVATION` / `INFERENCE` / `ESTIMATE` / `HYPOTHESIS` / `UNKNOWN`
- 信源按可靠性分四层，**一手优先**：Tier 1 官网与官方材料 > Tier 2 第三方平台数据库 > Tier 3 权威媒体 > Tier 4 社区
- **查不到就写 `No reliable public data found.`** —— 不用行业均值、不用相似品牌数据填充，不把推断写成事实
- 第三方估算与官方数据严格区分口径，不互相冒充

---

## 包含的 skill

### 1. `dtc-growth-research` — 深度增长研究

按七个模块推进研究：**01 Brand & Business → 02 Product & Offer → 03 Customer & Market → 04 Acquisition & Growth → 05 Conversion & Retention → 06 Campaign → 07 Growth Diagnosis**，每个模块以 Finding → Evidence → Analysis 组织，不做资料堆砌。

输出为三段式：

| 段落 | 内容 | 用途 |
|---|---|---|
| PART 1 | Executive Summary（约一页） | 1–2 分钟抓住核心结论 |
| PART 2 | Detailed Analysis（01–07 + Source Map） | 支撑证据与推理过程 |
| PART 3 | Structured Research Data（YAML，根键 `research`） | 机器可读知识层，供下游可视化直接复用 |

PART 3 的铁律是**只抽取、不新研**：数据必须派生自 PART 1/2 已完成的研究，不新增搜索、不改数值、不改变证据分级。这样下游产物与研究报告永远一致。

### 2. `report-visualizer-html` — 报告转 HTML 可视化

把研究报告转成**单文件、自包含、响应式**的 HTML 页面：无外部框架与字体依赖，可离线打开，支持明暗双主题。

它只做转换，不做研究——输入是唯一事实源，绝不"顺手补个数据"。几条关键设计：

- **防退化**：报告中出现 ≥3 条同维度可比较的定量数据，默认用图表呈现，不允许退化成纯文字列表
- **图表着色必须承载语义**：单序列整组同色；只有真实分组（竞品 vs 本品牌、口径 A vs 口径 B）才使用辅助色，且必须配色键。颜色答不出"在告诉读者什么"就改回主题色
- **证据可追溯**：数据点旁带 Source chip（`SRC-004`），完整来源登记表放页尾折叠区，含访问日期
- 附带自检脚本 `skills/report-visualizer-html/scripts/audit_chart_colors.py`，扫描全站非主题色着色点，捕捉"颜色误用"这类浏览器不报错、肉眼看不出、但会误导读者的问题

### 3. `report-visualizer-pdf` — 报告转 A4 PDF

把同一份研究报告转成 A4 版式的 PDF。与 HTML 版共享信息架构、组件与证据体系，但针对**纸张**重新做分页与版式设计：pt 字号体系、分页保护、打印恒为浅色。

它比 HTML 版多一层能力：**公开分享过滤**。一份内部研究报告里通常混着不适合对外发布的内容——结构化数据层、执行指令、本地路径、工具操作痕迹。这个 skill 把这些确定性剔除，并按需把来源登记从被删的结构化数据里抢救出来，只留下可公开的研究内容。

三个脚本，零第三方依赖（PDF 渲染靠本机 Chrome / Edge 的 CDP）：

| 脚本 | 作用 |
|---|---|
| `scripts/filter_report.py` | 公开分享内容过滤：剔除内部章节块与 YAML 数据块，把 Source Registry 抢救为独立来源文件，并输出内部痕迹扫描报告 |
| `scripts/html_to_pdf.cjs` | HTML → PDF 渲染器（CDP `Page.printToPDF`，矢量文本、注入页码页脚、逐页重复） |
| `scripts/qc_pdf.py` | 质检：页数与 A4 尺寸、逐页墨迹覆盖率、正文包围盒越界、页脚存在性、逐页渲染 PNG + HTML 内容安全扫描 |

### 4. `report-visualizer-image` — 报告转 PNG 图片集

把报告转成一套**同一视觉系统、可直接投放**的 PNG 图片资产（每张 1600×1200@2x），每张独立成画、1–3 秒可读，适用于 PPT、社媒、案例分享。

不是"把报告截图"，而是**重新选故事**：先提炼 3–7 条最强洞察、判断哪些关系与对比值得上图，再按统一的画面结构（页眉带 / 正文区 / 页脚带）逐张设计。核心约束：

- **一套图共享一份设计令牌**（主色、字级、间距、卡片样式、证据徽章、来源 chip），读起来像同一份报告的一页页
- **正文区占版 70%–80% 且上下居中**，靠几何探针机械验证，不靠目测；不够就补信息层，不允许用空白撑版或缩字号硬塞
- **远读优先**：图片常以半幅宽度展示，字级按"远读"设计，宁大勿小
- **来源页必须逐条给出完整 URL**（唯一允许高密度的一页），并跑脚本逐字比对登记表 —— URL 的静默截断不会越界、不会被几何探针抓到，只能靠它

同样只做转换、不做研究：不新增数据、不改数值、不虚构品牌身份，证据分级与来源标注原样保留。

四个脚本，零第三方依赖（截图靠本机 Chrome / Edge 的无头渲染）：

| 脚本 | 作用 |
|---|---|
| `scripts/shot_to_png.py` | HTML → PNG 批量截图（自动发现本机 Chrome / Edge，1600×1200@2x） |
| `scripts/_geo.cjs` | 正文区几何探针：量 `fillPct` / `centerDelta` / `over`，验证占版与居中 |
| `scripts/qc_layout.cjs` | 布局质检：元素越界、主内容侵入页脚 |
| `scripts/_urlcheck.cjs` | 来源页 URL 完整性探针：逐条比对登记表文本，并断言无视觉裁切 |

---

## 效果示例

同一份 momcozy 报告的四种形态，均由上述 skill 端到端产出：

| 文件 | 形态 | 说明 |
|---|---|---|
| [`momcozy_report_2026-09-16.md`](examples/momcozy_report_2026-09-16.md) | Markdown 研究报告 | 三段式输出的公开版（结构化数据层已过滤），含 39 条来源登记 |
| [`momcozy_report_2026-09-16.html`](examples/momcozy_report_2026-09-16.html) | 单文件 HTML | 首屏结论、KPI 卡组、图表套件、证据徽章与页尾来源登记表 |
| [`momcozy_report_2026-09-16.pdf`](examples/momcozy_report_2026-09-16.pdf) | A4 PDF（16 页） | 打印版式，含逐页页码页脚与完整 Sources 节 |
| [`momcozy_visuals_2026-09-16_v1_4x3/`](examples/momcozy_visuals_2026-09-16_v1_4x3/index.html) | PNG 图片集（15 张） | 1600×1200@2x 图片资产，含画廊 `index.html` 与可编辑 `src_html/` 源 |

HTML 与图片集画廊下载后直接用浏览器打开即可（无需服务器、无需联网）；PDF 为矢量文本，可搜索、可复制。图片集由 15 张 PNG 组成，覆盖品牌快照、口径对照、产品与价格、增长引擎、留存、获客、创作者生态、用户画像、口碑、竞争格局、Campaign、转化、优劣势与机会、来源总览。

---

## 安装

Agent Skills 是各主流 agent 工具共用的开放格式，把 skill 目录放进对应的 skills 目录即可：

| 工具 | 用户级目录 | 项目级目录 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| GitHub Copilot / VS Code | `~/.copilot/skills/` | `.github/skills/` |
| WorkBuddy | `~/.workbuddy/skills/` | `.workbuddy/skills/` |
| 通用 | `~/.agents/skills/` | — |

```bash
git clone https://github.com/HolaAYan/DTC-Research-Skills.git
cp -r DTC-Research-Skills/skills/* ~/.claude/skills/     # 换成上表中你所用工具的目录
```

安装后无需额外配置，agent 会按需自动加载。

---

## 使用

不需要记命令，用自然语言触发即可。

**做研究：**

```
深度研究 Glossier 的独立站增长路径
拆解 Allbirds 的获客渠道与转化策略
研究 Rimowa 的 creator 营销和 Campaign 节奏
XX 为什么能在三年内做到品类第一
```

**生成可视化（HTML / PDF / 图片集）：**

```
把这份报告做成 HTML 页面
把 glossier_report_2026-09-08.md 转成网页版报告
把这份报告导出成 PDF
把 glossier_report_2026-09-08.md 做成可分享的 A4 PDF
把这份报告做成图片集，给 PPT 和社媒用
```

四个 skill 可以单独用，也可以串联：先跑研究拿到 Markdown 报告，再让它出 HTML / PDF / 图片集——三个可视化 skill 消费同一份研究，数据不会走样。

如果报告里有不适合对外发布的内容（结构化数据层、执行指令、本地路径），走 PDF 版即可：它的过滤层会先清干净，再排版。

---

## 目录结构

```
DTC-Research-Skills/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── examples/
│   ├── momcozy_report_2026-09-16.md     公开版研究报告（Markdown）
│   ├── momcozy_report_2026-09-16.html   单文件 HTML 可视化报告
│   ├── momcozy_report_2026-09-16.pdf    A4 PDF 报告（16 页）
│   └── momcozy_visuals_2026-09-16_v1_4x3/
│       ├── index.html                   图片集画廊
│       ├── 01–15_*.png                  15 张 3200×2400 PNG
│       └── src_html/                    可编辑 HTML 源 + _sys.css
└── skills/
    ├── dtc-growth-research/
    │   ├── SKILL.md
    │   └── references/
    │       ├── framework.md          七模块逐模块研究指令
    │       ├── evidence-rules.md     证据分级、信源分级与数据规则
    │       ├── output.md             三段式输出契约与自检清单
    │       └── structured-data.md    PART 3 数据模型与 YAML 规范
    ├── report-visualizer-html/
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── design-system.md      组件配方、图表规范、着色语义
    │   ├── assets/
    │   │   └── template.html         自包含起点骨架（含内置图表套件）
    │   └── scripts/
    │       └── audit_chart_colors.py 图表着色语义审计
    ├── report-visualizer-pdf/
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── design-system.md      A4 版式规范、分页规则与打印铁律
    │   ├── assets/
    │   │   ├── template-a4.html      A4 打印骨架（含内置图表套件）
    │   │   └── template-a4-preview.pdf  2 页样张，用于核对版式基线
    │   └── scripts/
    │       ├── filter_report.py      公开分享内容过滤
    │       ├── html_to_pdf.cjs       HTML → PDF 渲染器（CDP）
    │       └── qc_pdf.py             PDF 质检 + 内容安全扫描
    └── report-visualizer-image/
        ├── SKILL.md
        ├── references/
        │   └── design-system.md      画布解剖、版面规划、远读与密度规范
        ├── assets/
        │   └── report-canvas.css     画布基础样式 + 设计令牌 + 通用组件
        └── scripts/
            ├── shot_to_png.py        HTML → PNG 批量截图
            ├── _geo.cjs              正文区几何探针
            ├── qc_layout.cjs         布局质检（越界 / 侵入页脚）
            └── _urlcheck.cjs         来源页 URL 完整性探针
```

---

## 许可与免责

本项目采用 **MIT License**（见 `LICENSE`）。你可以自由使用、修改、分发，**包括商业用途**，条件是在副本或实质性部分中保留版权声明与许可声明。每个 skill 的 frontmatter 中也标注了 `license: MIT`。

**`examples/` 目录为例外**：其中的示例报告与图片集是作者的研究产出，仅用于展示这套 skill 的实际效果，版权归作者所有，**不在 MIT 授权范围内**（以报告页脚与图片页脚的版权声明为准）。如希望在自己的项目中使用其中的研究内容，请先取得授权。

两点需要说明：

1. **不构成专业建议。** 本项目提供的是一套研究方法与模板，其产出的任何分析都不构成投资、法律或商业建议。
2. **第三方数据版权归原平台。** 示例报告与 skill 文档中引用的第三方数据（如流量统计平台、点评平台、众筹平台等）版权与使用条款归各自平台所有。本许可仅覆盖本项目作者的原创表达，不构成对任何第三方数据的授权。

---

Copyright (c) 2026 Yan · MIT License
