# 物流账单自动核对：开源生态 / 框架 / 测试方案调研

> 调研日期：2026-11-17 · 针对本仓库 `logistics-billing-reconciliation` skill 的下一步演进
> 来源可靠性分级：**[A]** 官方文档/标准/承运商公告 · **[B]** 论文/基准/开源仓库 · **[C]** 厂商博客（仅作方向参考，数字需自验）

---

## 0. 结论先行

账单核对不是"一个大模型读发票"，而是**三层分离**的工程问题。把它们混在一个 prompt 里，是准确率和可审计性最大的敌人：

| 层 | 职责 | 由谁做 | 失败模式 |
|---|---|---|---|
| **L1 抽取层** | 发票/运单/装箱单 → 结构化字段（含每字段的页码+原文引用） | OCR + LLM（schema 约束） | 字段漏抽、串行、数字 OCR 错位 |
| **L2 事实层** | 合同价格表、附加费官方通告、运单实重体积 → 可查询的结构化事实 | 数据库/RAG/API/爬取 | 用了错月份的费率、找不到对应 lane |
| **L3 判定层** | 计价、比对、容差、出结论 | **确定性代码（不是 LLM）** | 让 LLM 算数 → 偶发算错且无法回归 |

Agent（Claude skill）的正确定位是 **L1 的 schema 化抽取 + L2 的检索编排 + L3 结果的人类可读解释与追问**，而**绝不承担 L3 的算术**。目前本仓库的 skill 把三层全放在自然语言指令里，这是最该先改的结构问题。

一句话选型：**Docling/PaddleOCR-VL 做解析 → Claude + 严格 schema 做抽取 → YAML 费率表 + 承运商 API/EIA 做事实层 → Python（Pydantic）做计价判定 → `claude plugin eval` 做回归**。

---

## 1. 任务维度 → 数据源映射

用户提出的四个维度，自动化难度差异极大，应分批攻克：

| 维度 | 数据源 | 自动化可行性 | 推荐方案 |
|---|---|---|---|
| 合同价格表 | 自有 PDF/Excel 报价单、RFQ、rate card | ⭐⭐ 难点在**非标结构**，不在技术 | 先定义 `rate-card.schema.json`，人工/半自动录入一次，之后纯查表。**不要**每次让 LLM 重读 PDF 报价单 |
| 运单实际信息 | AWB/MAWB/HAWB、B/L、装箱单、承运商 tracking API | ⭐⭐⭐⭐ 高 | 承运商 API（结构化）优先；无 API 时解析 PDF |
| 变动费用官方通告 | DHL/FedEx 燃油附加费页、航司 FSC 公告、船司 BAF 公告 | ⭐⭐⭐ 中（页面结构易变） | 定时抓取 + **快照入库（带生效日期）**，核对时按运单日期查历史值，而非实时抓当前值 |
| 交叉校验（可选） | 承运商 rating API 返回的 negotiated rate | ⭐⭐⭐ 中 | 作为第二意见，不作为唯一事实源（见 §3.3 注意事项） |

**关键设计原则：按"运单日期"查费率，不按"今天"查费率。** 发票常在月末寄到，附加费已经改了一轮——这是实务中最高频的误判来源，而当前 skill 的 `references/carrier-surcharge-urls.md` 的 "fetch the page and find the rate effective for the shipment date" 依赖页面保留历史表，多数承运商页面只挂当期值。必须自建快照表。

---

## 2. 现有 skill 的 gap（按优先级）

通读 `SKILL.md` 与 4 个 module 后的具体发现。**P0 两条是计费口径错误，会直接产生错误结论：**

### P0-1 海运 BAF 口径错误
`references/sea-module.md`：`Expected BAF = base ocean freight × BAF rate %`。
实际上船司 BAF 公告几乎都是**固定金额/TEU**（例：2026-02 生效的美西 BAF 为 US$478/TEU、US$27.31/revenue ton；澳新线 US$144/TEU）；LCL 则按 **USD/CBM**（例：US-加勒比线 LCL $0.55/cbm）。按百分比算会得出完全不同的"期望值"。**[A/C]**
→ 改为：`BAF = rate_per_teu × teu_count`（FCL）或 `rate_per_cbm × cbm`（LCL），并保留 `percentage` 作为极少数合同的可选口径。

### P0-2 空运燃油附加费口径
`references/air-module.md`：`Expected surcharge = base freight × published fuel surcharge rate %`。
航司 FSC 常见为 **USD/kg × 计费重量**（也有按 % 的，取决于航司与航线），通常月度或季度随航油指数调整。**[C，需按航司 tariff 确认]**
→ 改为口径可配置：`{basis: per_kg | percent_of_base, value, effective_from, effective_to}`。

### P1 计费重量规则不完整
- 缺 **0.5 kg 向上进位**（空运/快递普遍做法）。当前"差异 > 0.5 kg 才判 ❌"的容差与进位规则会互相打架：承运商合法进位 0.4 kg 时不该报警，而真实超收 0.6 kg 时又可能被当成进位放过。**[C，需按承运商 tariff 固化]**
- 缺 **重量档位（weight break）**：45 / 100 / 300(250) / 500 / 1000 kg，跨档单价下降。实务中"95 kg 按 100 kg 报价更便宜"是合法操作，若不懂档位会把它误判为超收。**[C]**
- 缺 **多件货的体积重聚合规则**：是"逐件体积重求和后与总实重取大"，还是"总体积 ÷ 除数"——不同承运商不同，结果差异可达 10%+。
- 缺 **尺寸取整规则**（每边四舍五入到整 cm 再计算）。

### P1 缺失的检查项（行业标准审计动作）
当前三个 module 都没有，但属于 freight audit 的基本盘 **[C，多家厂商资料一致]**：
- **重复计费检测**（同一 carrier + B/L/PRO/AWB + 金额；以及"修正版发票 vs 原发票"）
- **币种与汇率**（账单币种 ≠ 报价币种时的换算基准日）
- **最低计费额（minimum charge）** 与 LCL 最低 CBM 的联动
- **PSS / GRI / 旺季附加费 / 地址更正费 / 住宅派送费 / 超长超尺寸费**
- **偏远地区（RAS）**：目前写"若是枢纽机场则 ❌"，但 RAS 判定应基于承运商邮编/地区表，不是主观判断
- **三方/四方匹配**：合同 ↔ 运单(B/L) ↔ 发票 ↔ PO

### P2 结构性问题
- **没有机器可读的费率 schema**：所有价格都靠用户贴文本，LLM 每次重新理解一遍报价单 → 不可回归。
- **没有证据引用**：报告里的"Billed $180"无法回溯到发票第几页第几行。审计场景下这是硬需求。
- **容差是硬编码的魔法数字**（0.5 kg / 1% / 2%），应集中成可配置的 tolerance 表，并区分"绝对值容差"与"相对容差"（小额账单 1% 可能只有几分钱）。
- **`<!-- RAG_HOOK -->` 写法方向是对的**，但 RAG（向量检索）其实不适合费率查询——费率是精确结构化查询（carrier + lane + 日期区间 + 箱型），应该用 SQL/字典查表，向量检索只适合"合同条款原文"这类自由文本。建议把 hook 分成 `RATE_LOOKUP`（结构化）和 `CONTRACT_CLAUSE_RAG`（文本检索）两类。

---

## 3. 分层选型

### 3.1 文档解析 / OCR（L1 前半）

| 项目 | 许可 | 适用 | 备注 |
|---|---|---|---|
| **Docling** (IBM) | MIT **[B]** | 首选通用 PDF→结构化 | OmniDocBench 表现稳居开源前列；论文含速度基准 **[B]** |
| **PaddleOCR-VL** | Apache 2.0 **[C]** | 中文发票/表格首选 | 多个 2026 对比给出 OmniDocBench ~96.3、表格 TEDS ~94.8 **[C，口径不一致需自验]** |
| **MinerU** | ⚠️ 许可需确认 | CPU 可跑的管线版 | 不同来源说法冲突（Apache 2.0 / AGPL-3.0 / 4.0 附加条款 / 营收上限）——**商用前必须看 LICENSE** **[C]** |
| **dots.ocr** | MIT **[C]** | 结构化表单 | OmniDocBench ~90.8 **[C]** |
| **pdfplumber** | MIT | 数字版 PDF 取表格 | 当前 skill 已在用，对承运商电子发票够用且零成本 |
| **invoice2data** | ⚠️ README 未明示 **[C]** | **固定格式承运商发票** | YAML/JSON 模板 + 正则。DHL/FedEx 月结发票格式稳定，模板法比 LLM 更准更便宜，强烈建议做为快路径 |

**建议**：数字版 PDF 走 `pdfplumber`/`invoice2data` 模板（确定性、零 token）；扫描件/非标格式才降级到 Docling 或 VLM。不要一上来就全部喂 VLM。

### 3.2 结构化抽取（L1 后半）

- **Claude + 严格 JSON schema**，每个字段强制返回 `{value, page, source_text}`——"要求模型给出原文 span"是目前唯一可工程化的置信度与可追溯手段 **[C]**。
- 如果要脱离 Claude Code 做独立服务：**instructor**（Pydantic + 自动重试，把校验错误回灌给模型）是最轻的默认选项；**BAML** 适合对脏输出容忍度要求高的场景；**PydanticAI** 偏完整 agent 框架，只做抽取偏重 **[C]**。
- ⚠️ 重要提醒（来源原话意思）：**schema 校验只保证格式，不保证事实正确**。所以 L3 必须独立校验（例如：抽到的件数 × 单件重 ≈ 总重）。

### 3.3 事实层（L2）

**(a) 合同价格表** — 自建，没有现成开源方案。建议 schema：
```yaml
# rate-cards/dhl-express-2026H2.yaml
carrier: DHL_EXPRESS
contract_id: "CN-2026-0042"
effective: {from: 2026-07-01, to: 2026-12-31}
currency: USD
divisor: 5000            # 体积重除数
rounding: {weight_increment_kg: 0.5, mode: up}
lanes:
  - {origin: CN, dest: DE, service: EXPRESS_WORLDWIDE,
     breaks: [{max_kg: 0.5, price: 28.4}, {max_kg: 1.0, price: 33.1}, ...]}
surcharges:
  fuel: {basis: percent_of, applies_to: [freight], source: dhl_fsc_table}
  non_stackable: {basis: per_shipment, value: 0, requires_evidence: true}
```

**(b) 变动费用官方通告** — 分三类取数：
- **快递燃油附加费**：DHL/FedEx 官网页面（已在 `carrier-surcharge-urls.md`）。改为**定时抓取 + 快照入库**，表结构 `(carrier, region, effective_from, effective_to, rate_pct, source_url, fetched_at, raw_html_hash)`。
- **卡车/陆运燃油**：**EIA Open Data API**（美国能源部每周柴油零售价，1994-03 至今，免费但需 API key）**[A]**。这是美国卡运 FSC 合同的标准基准，可直接按合同 baseline 表算出期望值——**这是本项目唯一能做到"完全确定性验证"的附加费**，优先级建议拉高。注意发布时点来源说法不一（周一 / 次周二 10:00 ET），自动化前看 EIA 官方发布日历 **[A/C]**。
- **海运 BAF / 空运 FSC**：船司/航司公告页，无统一 API。Container News 之类的行业媒体会汇总生效公告，可作为抓取线索 **[C]**。

**(c) 运单信息 / 交叉校验**：
- **DHL MyDHL API**（Rating 返回账号费率）、**FedEx REST**（SOAP 已于 2026-06-01 完全退役，老集成必须迁移）、**UPS**（已弃用 access key，改 OAuth 2.0）**[A/C]**。
- ⚠️ **DHL 明确声明 rating 返回的费率与时效 "indicative and not guaranteed"，且其条款限制 rating 数据的展示方式** **[A]**。所以：**API 费率只能当"交叉校验的第二意见"，不能当作判定依据**，否则争议时站不住。合同价格表才是唯一权威事实源。
- **FreightUtils MCP**（`soapyred/freightutils-mcp`，**MIT**，26 个工具，242 commits，但仅 8 stars）**[B]**：含 `chargeable_weight_calculator`、`cbm_calculator`、`consignment_calculator`、`container_lookup`、`incoterms_lookup`、`unlocode_lookup`、`airport_lookup`、`hs_code_lookup`、`adr_*`。**没有燃油附加费**。
  → 价值判断：**不建议直接作为生产依赖**（单人维护、8 stars、计价逻辑是审计核心不应外包给黑盒），但**非常值得作为参考实现去读**，尤其 `consignment_calculator` 的多模式计费重聚合逻辑和 `incoterms_lookup` 的数据组织方式。

### 3.4 计算与规则判定（L3）

**核心主张：这一层必须是纯 Python，可单元测试，零 LLM。**

- **Pydantic**：发票/运单/费率的模型与跨字段校验（例：`总重 ≥ Σ 单件重`、`币种 ∈ 合同允许币种`）**[C]**。
- **规则即数据**：把"DDP 下不得向收货人收税"这类规则写成 YAML/JSON 规则表 + Python 执行器，而不是写在 Markdown 指令里。好处：可枚举、可测试、可按客户定制。
- 不建议引入的重型方案：**Great Expectations / Pandera** 面向"数据集级"质量监控，对"单票发票逐条判定"是错配 **[C]**；**OPA/Rego** 要多部署一个运行时，当前规模不划算。等到做批量月结对账（几千条一起跑）时，Pandera 才有意义。
- 轻量规则引擎（`rule-engine`、`business-rules`、`py-rules-engine`）可选，但本场景规则数量（估计 50–150 条）用结构化 Python + YAML 完全够，先不引入 **[C]**。

### 3.5 编排（Agent 层）

- **Claude Agent Skill（当前路线）是对的选择**：核对工作本质是"有大量领域知识 + 需要追问用户 + 需要人类可读解释"，skill 比写死的 pipeline 更合适。
- 演进方向：把 skill 从"全是自然语言指令"改成 **"薄指令 + 厚脚本"**——SKILL.md 只负责路由、追问、解释；`scripts/` 下放确定性计算（Python），skill 指示 Claude 调用它们。这与 Anthropic 官方文档类 skill（pdf/xlsx/docx 都是 SKILL.md + 可执行脚本）的做法一致 **[A]**。
- 若未来要做无人值守的批量服务，再考虑 LangGraph / PydanticAI 做状态机编排；现在不需要。

### 3.6 数据标准（中长期互操作）

| 标准 | 状态 | 用途 |
|---|---|---|
| **IATA ONE Record** (`IATA-Cargo/ONE-Record`, **MIT**) **[B]** | 活跃，有 ontology + OpenAPI + Playground API | 空运数据模型的事实标准，建模 AWB/shipment 时直接借用其字段命名，省掉自己设计 |
| **DCSA OpenAPI** (`dcsaorg/DCSA-OpenAPI`, Apache 2.0 **[C]**) | 活跃 | 海运集装箱 B/L、booking、track&trace 标准，建模海运单时同理 |
| **EDI X12 210 / 310** | 210=Motor Freight Invoice，310=Freight Details & Invoice | 若客户是北美大货主，账单可能直接以 EDI 到账。开源 Python 侧 **pyx12**（GPL，更新慢）、**pydifact**（EDIFACT 侧）、Walmart **gozer**（Java, X12）；**没有找到专门解析 210/310 的活跃开源 Python 库** **[C]** → 这是一个真实空白，也是潜在差异化点 |

**建议**：字段命名直接对齐 ONE Record / DCSA，不要自创。未来接客户系统、接 EDI 时成本差一个量级。

---

## 4. 同类开源项目：现实评价

GitHub 上搜 "freight invoice audit" 能找到 8–10 个项目，但**没有一个是可依赖的框架**，几乎都是个人作品集级别的 demo **[B/C]**：

| 项目 | 技术栈 | 对本项目的可取之处 |
|---|---|---|
| `morris198/freight-invoice-automation` | LLM 抽取 + **确定性 Python 规则做审批决策**，干净的入 SQL + 异常转人工 | **架构最值得抄**：正是 §0 的三层分离，可直接参考其"自动通过 / 转人工"的阈值设计 |
| `anmol3012/FREIGHT-INVOICE-VALIDATION-SYSTEM` | FastAPI + React，**MIT**，20 步确定性审计引擎 + 重复计费检测 | 抄它的**检查项清单**和重复检测逻辑 |
| `ManchikaAbhiram/FreightIQ` | Django：合同费率计算 → 校验 → 异常调查 → 经理审批 → credit note 对账 | 抄它的**状态机与流程闭环**（我们现在只有"出报告"，没有"拿到 credit note 关闭"） |
| `shreyansh2003/freight-audit-lab` | 合成数据 + **密封答案集(sealed answer key)** 打分 | **抄它的测试思路**（见 §5.3），这是所有项目里最有参考价值的一条 |
| `farid-richa/freight-invoice-auditor` | pandas 逐行 re-rate → Excel 报告 | 月结批量对账的输出形态参考 |

**结论：不要 fork 任何一个。** 价值在于三样东西：**检查项清单**、**三层架构的印证**、**测试方法**。核心竞争力恰恰在它们都没有的地方——多模式（快递/海运/空运）的中国出口场景、Incoterm 合规、以及 agent 的追问能力。

---

## 5. 测试与评测方案（本次调研重点）

### 5.1 `claude plugin eval`：skill 的原生回归测试 **[A]**

Claude Code 自带的 skill/plugin 评测命令，**这是本项目最该先落地的测试基建**。要求 Claude Code ≥ v2.1.269、git ≥ 2.31、插件有 manifest。

目录结构（`claude plugin eval init` 会自动生成）：
```
logistics-billing-reconciliation/
├── .claude-plugin/plugin.json
├── skills/...
└── evals/
    ├── dhl-fuel-surcharge-stale-rate/
    │   ├── prompt.md          # frontmatter: max_turns/allowed_tools; body: 用户会怎么说
    │   ├── graders/
    │   │   ├── criteria.md    # type: llm，写成具体 PASS/FAIL 条件
    │   │   └── skill-fired.md # type: tool_used，确认 skill 真被触发
    │   └── case.yaml          # 可选，仅 context.* 字段用
    ├── ignores-unrelated-request/   # 负样本：不该触发
    └── results/               # 加进 .gitignore
```

6 种 grader：`regex`、`tool_used`、`tool_order`、`file_exists`（**零成本**，从 transcript/文件算）+ `llm`、`baseline`（调判官模型，**产生费用**）。**没有自定义代码 grader**。

机制上最值得注意的两点：
1. **每个 case 默认跑 3 次**（agent 非确定性，单次无意义），case 分数 = 多次均值；
2. **自动跑 no-plugin baseline**，给出 `WITH / W/OUT / Δ`。**Δ≈0 意味着这个 skill 根本没起作用**——对"写了一堆 Markdown 指令到底有没有用"这个问题，这是唯一客观答案。

实践要点（官方建议）：
- 长输出（如生成的报告文件）用 **`regex` grader 查内容**，不要用 `llm` grader——判官模型读长文本时方差大。`llm` grader 只留给短输出。
- 单 case 快速迭代：`claude plugin eval . --case <name> --runs 1 --ablation none`，但改动要在默认 3 次下复验。
- 可在 CI 上按分数 gate。

另有 **skill-creator 插件自己的 `evals/evals.json` 格式**，与 `claude plugin eval` 的 case 格式**互不读取** **[A]**——选一个，建议选 `claude plugin eval`（有 baseline 对比）。

### 5.2 三层测试金字塔

| 层 | 测什么 | 用什么 | 要求 |
|---|---|---|---|
| **单元测试**（底，最多） | 计价公式：体积重除数、0.5kg 进位、重量档位、BAF per TEU、LCL 最低 CBM、FSC 口径、币种换算 | pytest，纯 Python，零 LLM | **100% 覆盖，毫秒级，必须全绿**。这些是审计结论的地基，不允许概率性正确 |
| **抽取准确率**（中） | 字段级 F1：发票号/AWB/重量/尺寸/各费用行 | 自建黄金集 + 逐字段比对 | 分字段设阈值：**金额与重量字段要求 ≥99%**，地址之类可放宽 |
| **端到端判定**（顶，最少） | 整票的 PASS/FAIL/❓ 是否正确 | `claude plugin eval` | 看混淆矩阵，不看准确率（见 §5.4） |

### 5.3 黄金数据集与合成数据

**自建黄金集是不可替代的**（20–50 票脱敏真实发票 + 人工核定答案），这是整个项目最有价值的资产。公开数据只能补充：

| 资源 | 规模/许可 | 用途 |
|---|---|---|
| **DocILE** (`rossumai/docile`) **[B]** | ~6.7k 标注商业单据 + 100k 合成 + ~1M 未标注；55 个字段类；**代码 MIT，数据集许可未明示，需 token 从 docile.rossum.ai 下载** | **抽取层基准**。定义 KILE（字段定位抽取）与 LIR（行项目识别）两个任务，自带 `docile_evaluate`（AP/F1/P/R，COCO 式插值）。LIR 任务与"发票费用行"高度对应，直接可用其指标口径 |
| **FATURA** **[C]** | 10k 合成发票图像、24 个语义类、50 种版式 | 版式鲁棒性测试；许可需在原始仓库确认 |
| **docsynth** (PyPI, 开源) **[C]** | Python，**所有字段值预先已知、精确到分，无需 LLM** | **生成带黄金答案的合成发票**。对"故意植入错误"的对抗测试特别合适 |
| `shreyansh2003/freight-audit-lab` 的 **sealed answer key** 思路 **[B]** | — | 答案集与数据分离、评分时才揭晓，防止调参时信息泄漏 |

**必须自建的对抗用例集**（每类至少 3 票，这是最能提升实际捕获率的投入）：
1. 体积重用错除数（6000 当 5000）
2. 燃油附加费用了**上一个月**的费率
3. **重复计费**（同一 AWB 两张发票；修正版发票未注销原发票）
4. DDP 条款下向收货人计收关税/DHC
5. 报价单外凭空出现的附加费（phantom accessorial）
6. LCL 最低 CBM 与实际 CBM 的边界（0.9 / 1.0 / 1.1 CBM）
7. 跨重量档位的合法低价（**负样本——不该报警**）
8. 承运商合法的 0.5kg 向上进位（**负样本**）
9. 币种/汇率换算基准日差异
10. 多件货体积重聚合口径差异

### 5.4 该看什么指标

**不要用"准确率"。** 账单核对是极度不平衡的二分类（多数行项目是对的），且两类错误代价完全不同：

| 指标 | 含义 | 目标 | 理由 |
|---|---|---|---|
| **漏报率 (FN)** | 真超收被判通过 | 尽可能低 | 直接等于真金白银损失 |
| **误报率 (FP)** | 正常费用被判 ❌ | **严格控制** | 每个误报都要人去查 + 去跟承运商吵。FP 过高会导致整个系统被弃用——这是自动化对账项目最常见的死法 |
| **❓ 占比** | 需人工澄清的比例 | 可接受但要降 | 这是"诚实的不确定"，比瞎判好；但 >30% 就失去自动化意义 |
| 单票成本 / 延迟 | token + 人工时间 | 对比人工基线 | 用于证明 ROI |
| **recovery rate** | 实际追回金额 / 发现的差异金额 | 业务终局指标 | 发现≠追回，需要 §4 FreightIQ 那样的流程闭环 |

建议显式在 skill 中引入 **"低于 X 金额的差异不报警"** 的阈值（实务上追一笔 $3 的差异不划算），并让它可配置。

---

## 6. 可直接复用的 Claude skills

本会话已可用、与本项目直接相关的：

| skill | 用法 |
|---|---|
| **pdf** | 发票/装箱单解析（当前 SKILL.md 已正确引用）。扫描件走 OCR 分支 |
| **xlsx** | **价格表导入导出的主通道**——客户的 rate card 90% 是 Excel。还可用于月结批量对账输出 |
| **docx** | 向承运商发争议函/credit note 申请的正式文书 |
| **skill-creator** | 改 skill 本身 + 跑它自己的 `evals/evals.json`；写新 module 时的脚手架 |
| **dataviz** | 差异趋势图、按承运商/航线的超收分布（做成管理层看的月报） |
| **Artifact** | 把核对报告发布成可分享的页面，比终端文本更适合给财务/采购看 |

生态入口 **[B/C]**：
- `anthropics/skills` — 官方仓库，含 `spec/`（Agent Skills 规范）与 `template/`。注意：**官方文档类 skill 是 "SKILL.md + 可执行脚本" 的形态**，正是 §3.5 建议的方向。
- `travisvn/awesome-claude-skills` — 社区清单。
- 分发：`/plugin marketplace add anthropics/skills`；另有 `claude-plugins-official`（Anthropic 策划）与 `claude-community`（第三方过审）两个市场。**没有统一的官方 skills marketplace** **[C]**。

LLM 评测框架（若将来脱离 Claude Code 做独立服务才需要）**[C]**：**DeepEval**（pytest 风格，Apache 2.0，适合 CI 回归）、**promptfoo**（YAML/CLI，适合 prompt/模型矩阵对比与红队，MIT）、**Inspect AI**（UK AISI，MIT，沙箱内验证 agent 轨迹）。现阶段 `claude plugin eval` 足够，不建议提前引入。

另外值得知道：**公开 agent 基准里没有发票对账/财务核对的任务**。τ-bench（航空/零售，后续变体加了电信/银行）、TheAgentCompany（模拟软件公司）、ENTERPRISEOPS-GYM（8 个业务域，**不含财务**）都不覆盖 **[B/C]**。
→ 含义：**没有现成的 benchmark 能证明这个 skill 好不好，必须自建黄金集**。反过来说，一个公开的"物流账单核对 benchmark"本身就是有价值的开源贡献。

---

## 7. 建议 roadmap

**Phase 0 — 止血（1–2 天）**
- [ ] 修 P0-1 海运 BAF 口径（per TEU / per CBM）
- [ ] 修 P0-2 空运 FSC 口径（per kg / percent，可配置）
- [ ] 补 0.5 kg 进位与重量档位说明，理清与容差的关系

**Phase 1 — 测试基建（1 周）** ← 建议优先于加功能
- [ ] 加 `.claude-plugin/plugin.json`，跑 `claude plugin eval init`
- [ ] 10 个 case：3 正常通过 / 5 对抗（§5.3 的 1/2/3/4/5）/ 2 负样本（§5.3 的 7/8）
- [ ] 看 Δ 值：验证这 377 行 Markdown 到底带来了多少增量
- [ ] 建 `tests/` 放计价公式的 pytest（此时还没有脚本，就先写出期望行为）

**Phase 2 — 三层分离（2–3 周）**
- [ ] `schemas/`：`invoice.schema.json`、`rate-card.schema.json`、`surcharge.schema.json`（字段命名对齐 ONE Record / DCSA）
- [ ] `scripts/`：`chargeable_weight.py`、`surcharge.py`、`compare.py`（纯 Python + Pydantic，100% 单测）
- [ ] SKILL.md 瘦身为"路由 + 追问 + 解释"，计算全部委托给脚本
- [ ] 抽取强制返回 `{value, page, source_text}`，报告里带证据引用

**Phase 3 — 事实层（1 个月+）**
- [ ] 附加费快照表 + 定时抓取（**按运单日期查历史值**）
- [ ] EIA API 接入（美国陆运 FSC 的确定性验证）
- [ ] 重复计费检测（需要跨发票的持久化存储——这是第一个真正需要数据库的功能）
- [ ] 承运商 rating API 作为第二意见（明确标注为 indicative）

**Phase 4 — 闭环与规模化**
- [ ] 争议函生成 → credit note 跟踪 → 关闭（参考 FreightIQ 状态机）
- [ ] 月结批量模式（此时 Pandera 才有意义）
- [ ] 仓储账单 module（已在 `extension-points.md` 规划）

---

## 8. 风险与合规注意

1. **Incoterms 2020 是 ICC 的版权内容**，没有可自由分发的机器可读数据集。skill 里只能写"责任归属的判断逻辑"，不要整段复制 ICC 规则文本。
2. **承运商 API 条款限制 rating 数据的展示方式**（DHL 明示）**[A]**，且费率为 indicative。不要把 API 返回值当判定依据，也注意别违约展示。
3. **发票含商业敏感信息与个人信息**（收发货人、地址、货值）。测试数据必须脱敏；黄金集不要进公共仓库。
4. **MinerU 许可存疑**，商用前核对 LICENSE；DocILE 数据集许可未明示，商用前确认 **[B/C]**。
5. **别让 LLM 算数**。这条值得重复：所有金额/重量运算走代码，LLM 只负责抽取、路由和解释。

---

## 9. 来源

**官方 / 标准**
- [Claude Code: Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) · [Agent Skills](https://code.claude.com/docs/en/skills)
- [DHL Express MyDHL API](https://developer.dhl.com/express) · [EIA Open Data](https://www.eia.gov/opendata/) · [EIA Gasoline & Diesel Fuel Update](https://www.eia.gov/petroleum/gasdiesel/)
- [IATA ONE Record (GitHub, MIT)](https://github.com/IATA-Cargo/ONE-Record) · [ONE Record 规范站](https://iata-cargo.github.io/ONE-Record/stable) · [DCSA OpenAPI](https://github.com/dcsaorg/DCSA-OpenAPI)
- [New BAF surcharges effective February 1, 2026 (Container News)](https://container-news.com/new-baf-surcharges-effective-february-1-2026/)

**论文 / 基准 / 开源仓库**
- [DocILE Benchmark (arXiv 2302.05658)](https://arxiv.org/abs/2302.05658) · [rossumai/docile](https://github.com/rossumai/docile)
- [Docling 论文 (arXiv 2501.17887)](https://arxiv.org/pdf/2501.17887) · [pdf-extraction-agenda（解析方案汇总）](https://github.com/dantetemplar/pdf-extraction-agenda)
- [anthropics/skills](https://github.com/anthropics/skills) · [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [soapyred/freightutils-mcp (MIT)](https://github.com/soapyred/freightutils-mcp)
- [invoice2data](https://github.com/invoice-x/invoice2data) · [pyx12](https://pypi.org/project/pyx12/) · [walmartlabs/gozer](https://github.com/walmartlabs/gozer)
- 同类项目：[morris198/freight-invoice-automation](https://github.com/morris198/freight-invoice-automation) · [anmol3012/FREIGHT-INVOICE-VALIDATION-SYSTEM](https://github.com/anmol3012/FREIGHT-INVOICE-VALIDATION-SYSTEM) · [ManchikaAbhiram/FreightIQ](https://github.com/ManchikaAbhiram/FreightIQ) · [shreyansh2003/freight-audit-lab](https://github.com/shreyansh2003/freight-audit-lab) · [farid-richa/freight-invoice-auditor](https://github.com/farid-richa/freight-invoice-auditor)
- [τ-bench](https://www.semanticscholar.org/paper/70aa016c1f68fd5c0261f26ad20017b8307650af) · [Holistic Agent Leaderboard (arXiv 2510.11977)](https://arxiv.org/pdf/2510.11977)
- [docsynth (PyPI)](https://pypi.org/project/docsynth/) · [FATURA 数据集说明](https://www.emergentmind.com/topics/fatura-dataset)

**厂商 / 行业资料（方向参考，数字需自验）**
- [Cass: Six Best Practices in Freight Audit and Payments](https://www.cassinfo.com/hubfs/Case%20Studies/6%20Best%20Practices/Cass%20-%20Six%20Best%20Practices%20in%20Freight%20Audit%20and%20Payments.pdf) · [FreightWaves: Freight invoice audits](https://www.freightwaves.com/news/freight-invoice-audits-and-why-they-matter) · [Lojistic: 常见计费错误](https://www.lojistic.com/blog/freight-invoice-auditing-common-errors-that-inflate-shipping-costs)
- OCR 对比：[Spheron](https://www.spheron.network/blog/best-open-source-ocr-vlm-self-host-gpu-cloud-2026/) · [Docsumo](https://www.docsumo.com/blog/best-ocr-models) · [paddleocr.dev/compare](https://paddleocr.dev/compare)
- 评测框架对比：[evalshift](https://www.evalshift.dev/blog/open-source-llm-evaluation-frameworks) · [DeepEval](https://deepeval.com/blog/top-5-llm-evaluation-frameworks)
- 结构化输出：[Instructor 文档](https://python.useinstructor.com)
- [FreightWaves: freight shipping API 概览](https://www.freightwaves.com/checkpoint/freight-shipping-api/)
