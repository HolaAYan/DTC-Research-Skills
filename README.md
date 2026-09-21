# DTC Research Skills

面向出海 / DTC 品牌增长研究的两个 Agent Skills：**先做严谨的系统研究，再把研究变成可读的可视化报告。**

两个 skill 构成一条完整链路：

```
dtc-growth-research  ──►  report-visualizer-html
   研究 → Markdown 报告        报告 → 单文件 HTML
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

---

## 效果示例

[`examples/momcozy_report_2026-09-16.html`](examples/momcozy_report_2026-09-16.html) —— 一份用上述两个 skill 端到端产出的真实报告，包含首屏结论、KPI 卡组、图表套件、证据徽章与页尾来源登记表。

下载后直接用浏览器打开即可（无需服务器、无需联网）。

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

**生成可视化：**

```
把这份报告做成 HTML 页面
把 glossier_report_2026-09-08.md 转成网页版报告
```

两个 skill 可以单独用，也可以串联：先跑研究拿到 Markdown 报告，再让它转成 HTML。

---

## 目录结构

```
DTC-Research-Skills/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── examples/
│   └── momcozy_report_2026-09-16.html
└── skills/
    ├── dtc-growth-research/
    │   ├── SKILL.md
    │   └── references/
    │       ├── framework.md          七模块逐模块研究指令
    │       ├── evidence-rules.md     证据分级、信源分级与数据规则
    │       ├── output.md             三段式输出契约与自检清单
    │       └── structured-data.md    PART 3 数据模型与 YAML 规范
    └── report-visualizer-html/
        ├── SKILL.md
        ├── references/
        │   └── design-system.md      组件配方、图表规范、着色语义
        ├── assets/
        │   └── template.html         自包含起点骨架（含内置图表套件）
        └── scripts/
            └── audit_chart_colors.py 图表着色语义审计
```

---

## 许可与免责

本项目采用 **MIT License**（见 `LICENSE`）。你可以自由使用、修改、分发，**包括商业用途**，条件是在副本或实质性部分中保留版权声明与许可声明。每个 skill 的 frontmatter 中也标注了 `license: MIT`。

**`examples/` 目录为例外**：其中的示例报告是作者的研究产出，仅用于展示这两个 skill 的实际效果，版权归作者所有，**不在 MIT 授权范围内**（以报告页脚的版权声明为准）。如希望在自己的项目中使用其中的研究内容，请先取得授权。

两点需要说明：

1. **不构成专业建议。** 本项目提供的是一套研究方法与模板，其产出的任何分析都不构成投资、法律或商业建议。
2. **第三方数据版权归原平台。** 示例报告与 skill 文档中引用的第三方数据（如流量统计平台、点评平台、众筹平台等）版权与使用条款归各自平台所有。本许可仅覆盖本项目作者的原创表达，不构成对任何第三方数据的授权。

---

Copyright (c) 2026 Yan · MIT License
