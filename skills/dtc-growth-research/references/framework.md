# 研究框架（7 模块详细指令）

每个模块的产出按 **Finding → Evidence → Analysis** 组织：

- **Finding**：一句话结论
- **Evidence**：支持该结论的事实/观察（带证据分级 + 来源 + 日期）
- **Analysis**：为什么重要（So What）

先整体阅读全部模块再开工，可并行研究，但禁止只堆资料不分析。研究前先读 `evidence-rules.md`（红线）与 `output.md`（输出契约）。

> **研究前置：先定主要市场。** 开工前按 `evidence-rules.md` §6 判定品牌的主要市场（区域营收 → 其他可靠地理指标 → 默认北美），并区分「**已验证的主要市场**（verified）」与「**默认研究市场**（default）」。本报告的产品价格、竞品、评论、社媒、广告与区域数据均以该主要市场为准；判定结果、依据与 Market Status 写入 PART 2 末尾的 **Source Map A** 小节。

---

## 01 Brand & Business

> 这个品牌是谁？它靠什么业务赚钱？独立站在其中扮演什么角色？

### Brand Positioning
- Brand positioning / Value proposition / Mission / Differentiation / Founder story
- 有创始人公开采访、演讲、Podcast、自媒体内容时**优先引用原始内容**（引用其原话并给出来源），而不是二手转述。

### Business Model
- Main business / Main product category
- 渠道类型：DTC / Marketplace / Retail / Wholesale 等
- Geographic markets / 其他重要销售渠道
- **独立站在整体业务中的角色**

分析（仅在有可靠公开数据时）：独立站与其他渠道的业务规模差异。
**没有可靠数据 → 不估算独立站收入占比，不推断其为主渠道。**

---

## 02 Product & Offer

> 品牌卖什么？核心产品是什么？消费者为什么购买？

### Product Portfolio
- Main categories / Product lines / Hero products / Flagship products / New products / Product matrix
- 不要仅凭价格或曝光度判断"最畅销"，除非有证据。

### Pricing
- Price range / Entry-level / Core products / Premium products / Price ladder
- **价格以主要市场的官方区域官网与当地货币为准**：默认北美 → 优先美国官网、USD；主要市场为欧洲 / 日本等 → 优先对应市场的数据与货币（EUR / JPY 等）。
- **不得**用中国站价格替代海外市场价格；多区域站点并存时，说明主分析采用哪一个。

### Offer Strategy
- Discount / Bundle / Subscription / Free shipping / Gift / Warranty / Financing / Membership / Limited editions
- 只在公开页面可观察到时记录（首页、产品页、促销弹窗、邮件截图等）。

### 模块产出：Product Strategy 总结（价格阶梯 + 主力区间 + 差异化打法的综合判断，标注哪些是 INFERENCE）。

---

## 03 Customer & Market

> 谁在购买？为什么购买？市场和竞争环境如何？

### Target Customer
只基于公开证据（官方表述、社媒内容、Reviews 中的用户自述、媒体报道）分析：
- Target audience / Geographic market / Demographic signals / Use cases / Purchase motivations / Customer needs
- **严禁凭空生成用户画像**；区分"品牌自己怎么说"与"从产品与营销可合理推断什么"。

### Customer Voice（社区声音）
优先研究：Reddit（品类 subreddit）/ Trustpilot / Amazon Reviews / YouTube 评论 / 论坛。

分析并归纳**重复出现的主题**（而非单条评论）：
- Why customers buy
- What customers love
- What customers dislike
- Repeated pain points
- Reasons for choosing the brand
- Reasons for switching to competitors

### Market & Competitors
- Main category
- 3–5 个有意义的直接/间接竞品；对每个竞品比较：Positioning / Price / Product / Marketing / Channels
- **竞品比较优先使用同一目标市场的数据**（同市场、同品类）；跨市场比较须说明差异。
- Market size / Market growth / Market share：**仅在存在可靠公开数据时引用**；没有 → 不自行估算。
- **区域数据与全球数据分别标注、不得混用**；**全球份额不得直接与单一区域份额比较**；缺同市场数据时标注范围与局限，**不得**用其他市场数据冒充（详见 `evidence-rules.md` §6）。

---

## 04 Acquisition & Growth

> 这个品牌主要如何获得客户？

### 独立站流量来源（**强制**）

凡报告引用独立站 / 官网流量数据（Similarweb / Semrush / 类似站点分析工具），**不得只给"自然搜索占比"一条**。按以下四条执行：

**① 数据充足时展示排名前 3 渠道的全部数据。**
每条给齐：**排名 + 渠道名（中英） + 占比 + 规模（月访问量/该渠道月流量） + 环比/趋势 + 数据源(SRC) + 数据月**。这里说的"前 3"是**平台确实能取到 3 条以上渠道数据时的要求**。

**② 平台只给出 1–2 种来源时，就只展示这些已知项。**
**不为凑"Top 3"而编造排名、补齐空缺或均分余量**。表格里渠道行数少于 3 是正常结果，不是缺漏；缺的维度标 **UNKNOWN**，**严禁反推或估算填充**。若确需用总访问量折算，必须显式标注"派生值，仅示意量级"。

**③ 多口径冲突：全部并列列出，但分析重心只放在最新的一手数据上。**
- **口径优先级**：`一手平台数据` > `二手转述`；同期数据 `最新` > `较早`。分析、结论、诊断、机会一律基于**最新且可信的一手口径**。
- 二手转述（如行业媒体引用平台截图）、过时口径（数据月明显早于最新一条）、无法验证来源的数字，**只作"参照口径"并列列出，不用于分析判断**。
- 差距大时并列呈现并显式注明差值，以及"**跨平台数字不可相加或互比**"；但**口径差异本身只写在方法论注释/研究局限里，不得进 Executive Summary 的"关键发现"，也不算品牌痛点或优势**（那是测量方法的问题，不是品牌的问题）。
- 数据必须**有真实来源**：不虚构，也不把二手转述当一手使用；取不到一手时如实说明"该维度仅得二手口径"。

**④ 其余配套。**
- 若首名（自然搜索）另有**品牌词 / 非品牌词拆分**，一并记录——它直接决定"承接型 vs 发现型"站点的判断，是后续诊断（模块 07）的关键依据。某口径独有的拆分要注明该口径属性（一手或参照）。
- 前三名合计占比可作为一句结论（如"前三大来源合计约 3/4"），但须标明其口径来自哪个平台、是否为主口径。
- 若主口径自报数字**内部无法调和**（如某渠道环比降幅与月度总量矛盾），记录为"口径提示（不作分析依据）"，趋势以可自洽的指标为准。

### SEO / Organic
- Organic search presence / Content strategy / Blog or editorial strategy / Search visibility / 重要内容主题
- 使用用户提供的 SEMrush/Ahrefs 查询结果，或依据可见的 Blog 结构与主题做观察，不虚构排名数据。
- 报告自然搜索时**不要只写一个总占比**：同时给出渠道排名位置（见上"独立站流量来源"）与品牌词/非品牌词结构（若有）。

### Paid
仅在能获得公开证据时分析（Meta Ad Library / Google Ads Transparency / 可见广告位）：
- Meta / Google / TikTok / 其他付费渠道、Creative themes、Offer strategy
- **禁止**因广告存在而推断广告预算、ROAS 或广告销售额。

### Social Strategy（详见下方专项要求）
先列出品牌运营的官方社交平台（Instagram / TikTok / YouTube / Facebook / X / LinkedIn / 其他），尽量记录：
- Official account / Followers / Posting frequency / Content format / Content themes / Engagement signals / Platform-specific strategy

**重点分析：不同平台是否承担不同营销角色？** 例如 Brand awareness / Product education / Social proof / Community / Conversion / Creator acquisition。判断必须有可见证据（内容差异、账号简介、外链去向）。

### Modash Requirement（必查）
- 必须查询 Modash（modash.io）。
- 若 Modash 收录该品牌 → 使用其公开数据，提供对应 Modash 页面，明确说明数据来源。
- 若 Modash 未收录 → **不得声称品牌没有 Creator/Influencer marketing**；继续通过官方社媒、Creator 账号、新闻报道等公开信息研究。

### Affiliate / Partnership
存在公开信息时研究：Affiliate program / Affiliate platform / Commission / Affiliate partners / Coupon & deal sites / Creator affiliates / Partnership strategy。
无公开数据 → 明确说明 No reliable public data found.

### Crowdfunding
若品牌曾在 Kickstarter / Indiegogo 等发起项目，记录：
Campaign / Product / Date / Funding goal / Amount raised / Backers / Campaign highlights。
所有结果必须有来源（平台页面或权威报道），无来源不写。

---

## 05 Conversion & Retention

> 品牌如何把流量转化为客户，并让客户继续购买？

### Website Analysis（官网分析，只分析实际打开过的页面）

**Information Architecture**
- Main navigation / Main pages / Product pages / About / Blog / Support / Community / 其他重要页面

**Homepage**
- Hero / Value proposition / CTA / Product presentation / Benefits / Social proof / Reviews / UGC / Media & awards / Offer / FAQ / Trust signals

**Product Page**（信息足够时）
- Product positioning / Benefits / Images & video / Reviews / UGC / FAQ / Warranty / Shipping / Returns / CTA / Cross-sell & upsell

### CRO Diagnosis（转化诊断）
回答：
> What does the website do well?
> What creates trust?
> What may create friction?
> What conversion elements are missing?

**只能分析实际观察到的页面元素，不得假设后台数据（转化率、A/B 测试、热力图等一律不虚构）。**

### Retention（留存）
仅当可获得公开证据时研究：
- Email / SMS（落地页订阅、弹窗、邮件截图等可见信号）
- Loyalty / Referral / Subscription / Membership / Community / Post-purchase communication / Cross-sell & upsell

**无法观察后台数据 → 不得推断其真实留存率、复购率或 LTV。**

---

## 06 Campaign

选 **3 个有代表性的 Campaign**：

| 编号 | 类型 | 时间要求 |
|---|---|---|
| Campaign 1 | Signature Campaign（品牌发展史上有代表性） | 原则上至少 6 个月以前 |
| Campaign 2 | Recent Campaign | 过去 6–12 个月 |
| Campaign 3 | Latest Campaign | 目前最新 / 正在进行 |

每个 Campaign 尽量分析：
- Campaign name / Date / Objective / Target audience / Product
- Core message / Offer / Channels / Social & Creator involvement / Content
- **Results**（必须有公开来源；没有 → 写 `Result: Not publicly disclosed`）
- Why it matters（该 Campaign 对品牌增长的意义）

> **恰好 3 个主案例**。若研究过程中发现超过 3 个值得记录的节点，**不要**在正文里平铺成 Campaign 4、5……，而是保留 3 个主案例（Signature / Recent / Latest 各一），其余压缩为章末的「其他代表性节点」小节（一行一个：名称 + 时间 + 一句话角色），并在 PART 3 写入独立顶层键 `research.brand_moments`。同一条节点不得在 `campaigns` 与 `brand_moments` 中重复出现。

---

## 07 Growth Diagnosis（增长诊断 · 综合分析）

本模块是研究终点。**不重复前面章节的资料**，而是综合前面证据回答。

### Growth Engine（增长引擎）
用简洁链路概括品牌当前最核心的增长逻辑，例如：

> Product → Creator → Social Proof → DTC Conversion → Referral

**链路必须由研究结果推导**，不得套用固定模板。每条箭头尽量注明依据来源。

### Growth Strengths（增长优势，3–5 条）
每条格式：**Evidence → Why it matters**

### Pain Points（主要问题，3–5 条）
严格区分两类：
- **Observed Problem**：公开信息可直接观察到的问题
- **Potential Problem**：基于证据的合理推论（必须标注为推断）

### Growth Opportunities（增长机会，3–5 条）
每条包含：
- Opportunity / Supporting evidence / Why it matters / Potential impact / Difficulty / Priority

**禁止提出与本研究证据无关的泛泛建议**（例如没有任何内容/社媒证据时建议"加强内容营销"）。
