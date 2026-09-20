# PART 3 — Structured Research Data（结构化数据层 · 详细规范）

## 0. 定位与铁律

PART 3 是**机器可读的知识层（single source of truth）**，让下游 Skill（HTML 可视化 / 图片生成 / PPT / 社媒内容 / 案例研究等）无需重做研究即可消费本报告。

**单向数据流，禁止回填研究：**

> Research（PART 1/2 已完成的研究）→ Structured Data（PART 3）
>
> **而不是** Research → 新研究 → Structured Data

- 不得为填充结构化字段而新增搜索或研究任务。
- 不得引入新事实、不得改变任何数值、不得把 INFERENCE 改写为 FACT、不得重写证据分级。
- PART 3 **不复制** PART 1/2 的长文；只抽取可复用的原子信息（facts/metrics/insights/entities/relationships），并尽量用 Source ID 引用。
- 不评估 confidence 就不写；禁止编造任意 confidence 分。
- 类别缺失时直接省略该节；不建空字段。

## 1. 输出位置与格式

- 紧跟 PART 2（07 Growth Diagnosis）之后、任何附录之前输出：

```
## PART 3 — Structured Research Data
```

- 主体为一个 **YAML fenced code block**（单一 document，方便下游整体提取与解析）。YAML 前后只写一句引导说明，不重复内容。
- YAML 根键固定为 `research`。

## 2. 概念结构

```text
research:
├── metadata
├── brand
├── business
├── product
├── customer
├── market            # 无可靠数据时省略，不写占位
├── acquisition
├── social
├── creator            # 含 Modash
├── affiliate
├── website            # 转化观察（Conversion）
├── retention
├── campaigns
├── brand_moments      # 可选：非三主案例的品牌节点（如大型品牌跃迁动作）
├── competitors
├── growth_engine
├── strengths
├── pain_points
├── opportunities
├── insights
├── metrics            # 关键指标速览（可选，仅在有价值时）
└── sources            # Source Registry
```

结构可随研究实际内容增删，不强行一致。

## 3. 字段规范

### 3.1 metadata

| 字段 | 说明 |
|---|---|
| title / brand / industry | 研究标题、品牌、品类 |
| geographic_market | 主要市场（注明 Market Status：verified / default） |
| research_date / data_cutoff_date | 研究执行日 / 数据截止日（通常同日） |
| report_version | 有多次迭代才写 |
| method | 固定写 dtc-growth-research framework |
| note | 数据口径提醒（如"营收为官方口径非审计"）——保留报告中的数据提示 |

### 3.2 证据对象（Evidence Object，贯穿所有数值字段）

```yaml
key_metric:
  value: 235000
  unit: followers
  date: "2026-09-08"
  source: SRC-012        # 引用 Source Registry ID
  evidence_type: FACT    # FACT|OBSERVATION|INFERENCE|ESTIMATE|UNKNOWN
```

- `confidence`：仅当研究方法确实给出评估时才加，否则省略。
- 注意：`evidence_type` 描述**证据性质**，与 Source Registry 中的 `type`（来源类别）、`source_nature`（来源性质）是三个不同维度，三者不得互相替代（详见 §3.14）。

### 3.3 主要事实（facts / 各模块下的 factual 字段）

每个重要事实统一为：`value/statement + date + source(SRC ID) + evidence_type`。不要在 PART 3 里重述长解释。

### 3.4 insights

每条：`statement + evidence + evidence_type`（OBSERVATION=可直接观察；INFERENCE=多证据推导）。禁止把 INFERENCE 表述为事实。

### 3.5 products

每个产品字段：`name / category / price(value+unit) / positioning / key_differentiation / status`（status ∈ Existing|New|Pre-launch|Limited|Unknown，仅在有证据时使用）`+ source`。

### 3.6 customer

结构：`target_audience / use_cases / purchase_motivations / customer_needs / positive_themes / negative_themes / pain_points / customer_language(原话引用, 可选) / sources(SRC list)`。不要把定性客户证据转成不支持的画像统计。

### 3.7 acquisition

**结构（推荐）：映射 + `channels` 子列表** —— `traffic_measurement_note / traffic_sources_primary / traffic_sources_reference(可选) / cross_methodology_gap(可选) / branded_split(可选) / site_traffic(可选) / channels[...]`。

- `traffic_measurement_note`（**必填**）：一句话写明多口径处理原则——各口径全部并列、**分析基准取最新的一手平台数据**、较早或二手转述仅作参照、跨平台不可相加或互比、未公开项标 UNKNOWN 且"**能取到几个渠道就列几个**"。
- `traffic_sources_primary`（**必填**）：**最新的一手平台口径**，所有分析判断的依据。
  `methodology（平台 + 数据月 + 是否一手） / data_month / source(SRC) / evidence_type / channels[]`。
  `channels[]` 每条：`channel / visits(或 share) / share_of_total(派生值须注明) / mom_change / strategic_role / note(可选)`。
  **渠道条数 = 该平台实际公开的条数，不固定 3 条**——只公开 1–2 种就只列 1–2 条，**不为凑排名而补位**；未公开的维度写 `UNKNOWN`，严禁反推。
  （平台若另给桌面端/分端流量旅程等**不同分母**的数据，放独立子键并注明"分母不同，不可与 share_of_total 混比"。）
- `traffic_sources_reference`（**可选**，有多口径时才写）：较早或二手转述口径，**仅并列呈现，不作分析依据**。
  `methodology / data_month / source / source_nature（如 Secondary reporting） / evidence_type / shares[]`；`shares[]` 只需 `{channel, share}`。
- `cross_methodology_gap`（多口径差距大时写）：`statement（差值与可比项） / handling（并列不做归因） / analysis_basis（注明全部基于 primary） / source / evidence_type`。
  ⚠️ 这类内容**只写进本节与"研究局限"，不得上升为 `insights` / 关键发现 / pain_points**（口径差异是测量方法问题，不是品牌的问题）。
- `branded_split`（可选）：品牌词/非品牌词拆分，**分别标注证据来自哪个口径**（`primary_evidence` / `reference_evidence`），一手证据优先。
- `site_traffic`：`monthly_visits_est / three_month_trend(可选) / engagement(可选) / date / source / evidence_type`。
- `channels`：其余获客渠道，每个 `channel(SEO|Paid Search|Paid Social|Organic Social|Creator|Affiliate|Referral|PR|Content|Partnership|Other) / evidence / strategic_role / data(可选) / source / evidence_type`。只列研究支持的渠道。

> 兼容与迁移：旧版单键 `traffic_sources_top3`（固定 3 条）已废弃——它无法表达"某平台只公开 1–2 种来源"与"多口径择新"两种情况。仍见此键时按下述映射改写：`traffic_sources_top3` → `traffic_sources_primary.channels`（去掉固定 3 条约束），双平台并列的 `share` 字符串拆为 `traffic_sources_primary` + `traffic_sources_reference`。
>
> 兼容：`acquisition` 也可直接是渠道序列（`- channel: …`）。但**只要引用了站点流量数据，就必须同时提供 `traffic_sources_primary`**。注意序列后不能接同级 mapping 键（见 §校验），故推荐直接用上面的映射结构。

### 3.8 social

每个平台：`platform / account / followers(value) / posting_frequency / content_themes / content_format / strategic_role / source / date`。粉丝数无法核实则 `followers: UNKNOWN`，不估算。
Modash 单列（`modash`）：收录时给 `url / findings / date`；未收录时 `status: Not Found` 并注明"不据此推断无 creator 营销"。

### 3.9 website（Conversion）

每个观察：`page_element(如 homepage_hero / product_page / reviews / trust_signals / faq …) / observation / role / strength_or_friction(→ strength|friction) / source / evidence_type`。只写公开可见元素；后台指标一律不写。

### 3.10 competitors

每个竞品：`name / positioning / product_difference / price_difference / channel_difference / marketing_difference / relevant_data(可选) / source`。无证据的维度省略。

### 3.11 campaigns

**恰好 3 个** Campaign（signature / recent / latest 的角色用 `campaign_type` 表示），字段：`name / date / type / product / target_audience / core_message / channels / creator_or_partnership / offer / public_result / source / evidence_type`。无公开结果 → `public_result: Not publicly disclosed`。

- **不多不少 3 条**。若观察到超过 3 个值得记录的节点，**不要**把 `campaigns` 撑到 4 条以上，也不要把同一条同时写进两个位置——把「非三主案例」的节点移入**独立顶层键 `research.brand_moments`**（字段精简：`name / date / role(说明为何不列入三主案例，如「品牌跃迁动作」) / product / creator_or_partnership / public_result / source / evidence_type`）。PART 2 的 06 章同样只在正文写 3 个主案例，其余归入「其他代表性节点」小节。
- 选取原则：`Signature` 取最能代表品牌长期定位的一条；`Recent` 取近 12 个月最有代表性的一条；`Latest` 取当前正在跑的一条。

### 3.12 growth_engine

用图结构表示（下游 HTML/图片/PPT 依赖此节）：

```yaml
growth_engine:
  description: 一句话增长逻辑
  nodes:
    - id: N1
      label: 产品差异化（硬件买断无订阅）
    - id: N2
      label: Creator 种草
    ...
  relationships:
    - from: N1
      to: N2
      relation: drives
    ...
  evidence_type: INFERENCE   # 引擎本身是对证据的综合推导
```

节点与关系必须由研究证据推导；不同品牌可以是不同形态（链路/双轨/环），**禁止套用固定模板**。

### 3.13 strengths / pain_points / opportunities

- strengths：`statement / supporting_evidence / evidence_type`
- pain_points：`statement / type(observed|potential) / supporting_evidence / evidence_type`
- opportunities：`statement / why / evidence / potential_impact / difficulty / priority`
- priority/impact/difficulty 仅在研究给出可辩护依据时写（沿用报告 07 章中的 高/中高/中/低 文字档，不制造任意数值分）。

### 3.14 sources（Source Registry）

每条：`id(SRC-001…) / name / type / source_nature(可选) / url / access_date / relevant_sections(可选)`。PART 3 内一律用 `source: SRC-00X` 引用；一个来源在 registry 中只定义一次。

**三个字段维度不同，禁止互相替代：**

| 字段 | 描述什么 | 取值 |
|---|---|---|
| `type` | 来源**类别**（渠道 / 载体） | `First-party` \| `Platform` \| `Media` \| `Community` |
| `source_nature` | 来源**性质**（原始还是转述） | `Original` \| `Independent reporting` \| `Secondary reporting` \| `Syndicated` |
| `evidence_type` | **证据性质**（挂在数据对象上，不写在 sources 内） | `FACT` \| `OBSERVATION` \| `INFERENCE` \| `ESTIMATE` \| `UNKNOWN` |

- `Estimate` **不再作为来源类别**：不再写 `type: Estimate`；估算数据统一由引用它的数据对象上的 `evidence_type: ESTIMATE` 表达。
- `source_nature` 为**可选**字段：新报告应尽量填写；无法判断或来源为历史数据时可省略，不得为填空而编造。
- 同一份通稿与其转载报道**不得**被拆成多条"独立来源"：转载方 `source_nature` 记为 `Syndicated` 或 `Secondary reporting`。

## 4. 最小模板骨架

```yaml
research:
  metadata:
    title: "..."
    brand: "..."
    industry: "..."
    geographic_market: "..."
    research_date: "YYYY-MM-DD"
    data_cutoff_date: "YYYY-MM-DD"
    method: "dtc-growth-research framework"
    note: "..."
  brand:
    snapshot: "..."
    entity: { statement: "...", source: SRC-001, evidence_type: FACT }
    ...
  products:
    - name: "..."
      category: "..."
      price: { value: ..., unit: USD, date: "...", source: SRC-001, evidence_type: FACT }
      positioning: "..."
      key_differentiation: "..."
      status: Existing
  customer:
    target_audience: "..."
    ...
  acquisition: [...]
  social: [...]
  creator:
    modash: { status: Found | Not Found, url: "...", findings: "...", date: "..." }
  website: [...]
  campaigns: [...]
  competitors: [...]
  growth_engine:
    description: "..."
    nodes: [...]
    relationships: [...]
  strengths: [...]
  pain_points: [...]
  opportunities: [...]
  insights: [...]
  sources:
    - id: SRC-001
      name: ...
      type: First-party
      source_nature: Original
      url: ...
      access_date: "YYYY-MM-DD"
```

## 5. PART 3 专属自检

- **Research Integrity**：结构化数据只含 PART 1/2 已有信息；无新增无依据事实；数值未变；证据分级未变。
- **Source Integrity**：重要数据点均可溯源；SRC ID 与 registry 一致。
- **Source Classification Integrity**：`type` 只取 `First-party|Platform|Media|Community`（不得出现已废弃的 `Estimate`）；`source_nature` 若填写，只取 `Original|Independent reporting|Secondary reporting|Syndicated`；`type` / `source_nature` / `evidence_type` 三者不得互相替代；同一通稿与其转载未被计为多条独立来源。
- **Reusability**：仅凭本层即可让下游 skill 产出 HTML / 图片 / PPT / 社媒内容，无需重做研究。
- **Efficiency**：本层简洁；不复制长段分析；能引用就不重述。
- **YAML Syntax Safety（必做，交付前用 Python `yaml.safe_load` 实跑一次）**：
  - **双引号字符串内禁止出现 ASCII 双引号 `"`**。中文标题里的书名号内嵌引号（如 `《影石"全景王座"晃动》`）会提前闭合字符串并导致 `ParserError`。中文引号一律改写为 `「」` 或全角 `“”`。同理，`"` 内的撇号用单引号或改用中文标点。
  - **序列（list）中不可直接接同级 mapping 键**。`acquisition:` 下若先写 `- channel: …` 序列、再写同缩进的 `crowdfunding:`，会报 `expected <block end>`。做法：把额外键提为 `research` 下的顶层键（如 `research.crowdfunding`），或把 `acquisition` 改成 `{channels: [...], crowdfunding: {...}}` 映射。
  - 校验脚本模板：
    ```python
    import re, io, yaml
    s = io.open(path, encoding='utf-8').read()
    b = re.findall(r'```yaml\n(.*?)\n```', s, re.S)[0]
    r = yaml.safe_load(b)['research']
    srcs = {x['id'] for x in r['sources']}
    # ⚠️ 引用集合必须扫「全文」（PART 1/2 正文 + YAML 数据层），并剔除 sources 登记行本身。
    #    只扫 YAML 块会双向出错：把「仅正文引用」的来源误判为 unused，
    #    同时把「全篇从未引用」的来源漏判（它不在 YAML 里当然扫不到）。
    whole = re.sub(r'^\s*-\s*\{?id: SRC-.*$', '', s, flags=re.M)   # 去掉登记行
    refs = set(re.findall(r'SRC-\d{3}', whole))
    assert not refs - srcs, f'未注册引用 {refs - srcs}'
    assert not srcs - refs, f'注册但全文未引用 {sorted(srcs - refs)}'
    print('OK', list(r.keys()), '| registry', len(srcs), '| refs', len(refs))
    ```
    > 登记行剔除正则按 `- {id: SRC-001, ...}`（inline）与 `- id: SRC-001`（block）两种写法均适用；若 registry 用了别的排版，改成对应形式，或改为「切掉 `^\s*sources:` 至文末」（该方法要求 `sources` 是 YAML 最后一个键）。
  - 顺带核验：registry 无未解析引用、无"注册了但**全文**未引用"的来源（正文引用了、YAML 里没引用，**不算** unused）、`type` 无 `Estimate` 残留、`source_nature` 取值合规、campaign 含 Signature/Recent/Latest 三类、Modash 节点有明确 status。

