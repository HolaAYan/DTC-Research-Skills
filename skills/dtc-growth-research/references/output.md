# Output Format（输出契约 · 模板与自检）

最终输出**必须包含三个部分**：PART 1（人读摘要）、PART 2（人读详析）、PART 3（机器可读结构化数据）。全篇遵守 `evidence-rules.md` 的引用与分级要求。

> 输出架构：**Research once → One standardized knowledge layer → Multiple downstream outputs.**
> PART 3 详细规范见 `structured-data.md`；PART 3 不得引入新研究、新事实或改数值——它只从 PART 1/2 抽取标准化数据。

---

## PART 1 — Executive Summary（一页速览）

目标：让读者在 1–2 分钟内理解这个品牌。约一页，结构化呈现：

### Brand Snapshot
一句话概括品牌定位。

### Business
商业模式 + 独立站角色（有可靠数据时注明渠道结构；没有则写 No reliable public data found.）。

### Product
核心产品 + 产品差异化 + 价格区间。

### Customer
核心用户 + 主要使用场景 + Purchase Motivation。

### Growth Engine
用一个简单的流程图/结构图展示：

> Customer → Acquisition → Conversion → Retention

并标出品牌**最重要的增长渠道**（仅在有证据支持时标注"主要渠道"）。

### Marketing
Social / Creator / Affiliate / Campaign 的核心特点。

### Competitive Position
与主要竞品相比，品牌最大的差异。

### Key Strengths
3 条。

### Key Pain Points
3 条。

### Growth Opportunities
3 条。

（若某字段缺乏可靠信息，直接标注 No reliable public data found.，不强行填满。）

---

## PART 2 — Detailed Analysis（完整分析）

按以下顺序展开：

1. **01 Brand & Business**
2. **02 Product & Offer**
3. **03 Customer & Market**
4. **04 Acquisition & Growth** —— 若引用独立站流量数据，**不得只写"自然搜索占比"**：按"主口径 + 参照口径"两级呈现——① **主口径 = 最新的一手平台数据**（该平台公开几项就列几项，可为 1–2 条，**不为凑 Top 3 补位**），是所有分析判断的依据；② 参照口径 = 较早/二手转述，**全部并列列出**但仅作参照、不作分析依据。每条给齐：排名 + 渠道名 + 占比 + 规模 + 环比 + SRC + 数据月；未公开项标 UNKNOWN，不反推；两口径差逾 40pp 之类的说明写成**方法论注释**，不进关键发现、不算品牌痛点。
5. **05 Conversion & Retention**
6. **06 Campaign**
7. **07 Growth Diagnosis**

每个章节采用 **Finding → Evidence → Analysis** 的方式，不要单纯堆砌资料。重要数字与事实在行内标注：证据分级 [FACT / OBSERVATION / INFERENCE / ESTIMATE / HYPOTHESIS / UNKNOWN] + 来源（尽量具体页面）+ 日期（动态数据）。

---

### Source Map / Research Coverage（附于 07 之后 · 非研究模块）

> 本节是对**本次研究信源覆盖情况**的声明，**不是第 8 个研究模块**。它只汇总**已经完成**的检索与**已经采集**的信源——**不新增搜索、不新增事实、不重复堆砌完整来源条目**（完整来源记录见 PART 3 `sources`）。本节与 PART 3 必须来自**同一次研究**。

**A. Research Market（研究市场）**
- 主要市场（primary market）
- 选择依据：优先采用可靠的区域营收 / 销售 / 其他已披露地理业务指标；**不得**默认"品牌原产国＝主要市场"
- **Market Status**：该主市场是**已验证**（verified）还是**默认研究市场**（default），须明确区分
- 研究的地理范围；若「业务总览市场」与「DTC 分析市场」不一致，分别说明
- 无法确定时写明：`Primary market not reliably established; North America used as the default research market.`

**B. Source Coverage（来源覆盖）**
按主要来源类别逐项记录：
- 实际检索的平台 / 网站
- 获取到的有效信息
- 独特有效信源数量（如可得；**不编造**）
- 来源类型：first-party / platform / independent reporting / secondary reporting
- 访问日期（如适用）

**C. Research Limitations（研究局限）**
- 无法访问的重要来源
- 不可得的数据
- 证据不足的模块
- 仅由二手报道支撑的 claim
- 无法独立核实的指标

> 硬性禁止：**不得**声称检索过实际未检索的平台；**不得**编造来源数量。

---

## PART 3 — Structured Research Data（结构化数据层）

紧跟 PART 2 之后输出。详细规范见 `references/structured-data.md`。

要点：
- 输出一个 YAML fenced code block（根键 `research`），供下游 Skill（HTML / 图片 / PPT / 社媒 / 案例研究）直接解析。
- 结构按研究实际内容组织：metadata → brand → business → product → customer → market → acquisition → social → creator(Modash) → affiliate → website → retention → campaigns → brand_moments(可选) → competitors → growth_engine → strengths → pain_points → opportunities → insights → sources。类别缺失即省略。
- 证据对象统一携带 `value/unit/date/source(SRC ID)/evidence_type`；不编 confidence。
- 来源用 Source Registry（`SRC-001`…）引用，注册表只定义一次；每条来源含 `type`（类别）与可选 `source_nature`（性质），详见 `structured-data.md` §3.14。
- **只抽取、不新研**：不新增事实、不改数值、不改证据分级。

---

## 引用格式

- 紧跟声明放置来源，如：`FACT [官网 About: https://…]`
- 估算数据：`ESTIMATE [Similarweb, As of YYYY-MM-DD]`
- 观察：`OBSERVATION [首页, https://…]`
- 推断：`INFERENCE（基于 …）`
- 无数据：`No reliable public data found.`
- Campaign 无公开结果：`Result: Not publicly disclosed`

---

## Final Quality Check（输出前自检清单）

输出前逐项核对，任何一项为"是"则先修正再交付：

### Data
- [ ] 是否存在任何没有来源的定量数据？
- [ ] 是否错误地把估算当成事实？
- [ ] 是否存在 AI 自行推测的收入、市场份额、流量、ROAS、转化率等？
- [ ] 动态数据是否注明查询日期（As of YYYY-MM-DD）？

### Sources
- [ ] 是否优先使用官方一手来源？
- [ ] 是否查询了 Modash（并说明了收录情况）？
- [ ] 是否使用了可靠第三方来源并标注 Estimated？
- [ ] Reddit / Trustpilot 等社区信息是否基于重复主题，而非单条评论代表整体？

### Source Map & Market
- [ ] PART 2 末尾是否附有 Source Map / Research Coverage（A 研究市场 / B 来源覆盖 / C 研究局限）？
- [ ] 是否声明了主要市场及其依据，并区分"已验证"与"默认研究市场"？
- [ ] Source Map 是否只汇总已有检索，未新增搜索、未新增事实、未与 PART 3 重复？
- [ ] 是否避免了把同一通稿及其转载计为多个独立来源（`source_nature` 是否正确）？
- [ ] `type` 中是否已无废弃的 `Estimate`（估算统一用 `evidence_type: ESTIMATE`）？
- [ ] 是否存在仅为凑来源数量而做的搜索？

### Analysis
- [ ] 是否区分 FACT / OBSERVATION / INFERENCE / UNKNOWN？
- [ ] 07 Growth Diagnosis 是否全部来自前面模块的证据？
- [ ] Growth Opportunity 是否每条都有明确依据与影响/难度/优先级？

### Output
- [ ] 是否先给出一页 Executive Summary？
- [ ] 是否提供了按 01–07 组织的 Detailed Analysis？
- [ ] 是否提供了 PART 3 Structured Research Data（YAML）？
- [ ] 是否避免了单纯堆砌资料？
- [ ] 是否突出回答了"这个品牌为什么增长"？

### File & Naming（落盘，见 SKILL.md §8）
- [ ] 是否已写入 `<Brand>/{brand_slug}_report_{YYYY-MM-DD}.md`（品牌目录直接在工作区根下）？
- [ ] 品牌目录名是否用惯用写法、文件前缀是否为小写 slug（无空格/中文/特殊字符）？
- [ ] 日期是否为研究完成日 = 数据截止日？
- [ ] 工作区若有报告索引文件（如 `INDEX.md`），是否已追加该品牌记录？

### PART 3 Integrity
- [ ] 结构化层是否只含 PART 1/2 已有信息（无新增事实、数值未变、证据分级未变）？
- [ ] 重要数据点是否可经 Source ID 溯源到 Source Registry？
- [ ] 是否足以让下游 Skill 在不重做研究的情况下生成 HTML/图片/PPT/社媒内容？
- [ ] 是否简洁——能引用就不重述、无空字段、无占位指标？
