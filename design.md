# 设计文档：物流账单自动核对

> 版本 0.1 · 2026-11-17 · 配套调研见 [`research/2026-11-landscape.md`](research/2026-11-landscape.md)
> 来源可靠性：**[A]** 官方文档（Microsoft Learn / Anthropic docs，本文已逐条核对）· **[B]** 开源仓库/论文 · **[C]** 厂商博客（需自验）

---

## 1. 目标与约束

**业务目标**：对一张物流发票做多维度交叉核对——合同价格表、运单实际重量尺寸、官方附加费通告——输出带证据的差异报告。

**两条硬约束决定了整个架构：**

| | 约束 |
|---|---|
| **C1** | **最终生产平台是 Microsoft Copilot Studio**，这是公司唯一许可的 agent 设施。不是"可能迁"，是"一定迁"。 |
| **C2** | 当前开发与验证在 Claude Code（迭代快、能跑脚本、能做评测）。 |

**由 C1 + C2 得出的核心设计原则：**

> **按"双目标"构建，而不是"先做一版 Claude 的，将来再重写"。**
> 每个资产在落笔时就要确定它在 Copilot Studio 里对应什么。不能对应的，要么不做，要么明确标记为"开发期脚手架，不进生产"。

好消息是：经核对官方文档，**这两个平台的契合度比预期高得多**——Copilot Studio 的 Agent Skill 用的就是同一套开放规范（`SKILL.md` + YAML frontmatter + Markdown 指令 + 可选支持文件），MCP 也已 GA。所以真正的迁移成本集中在**数据存储层**和**评测用例格式**，不在领域知识本身。

---

## 2. 架构：四类资产与可移植性评级

把系统拆成四类资产，分别判断可移植性。这张表是本设计文档的核心：

| 资产 | Claude Code 形态 | Copilot Studio 形态 | 可移植性 | 结论 |
|---|---|---|---|---|
| **① 领域知识**（核对流程、各模式检查清单、Incoterm 判断） | `SKILL.md` + `references/*.md` | **Agent Skill**：ZIP 包含 `SKILL.md`（YAML frontmatter）+ 支持文件 **[A]** | ★★★★★ | **同一套规范，几乎可直接上传**。这是最大的利好 |
| **② 确定性计算**（计费重量、附加费、比对、容差） | Python 脚本 | **MCP server tools**（Streamable HTTP）**[A]** | ★★★★★ | **做成 MCP server，两边接同一个服务**。这是最关键的设计决策 |
| **③ 事实数据**（合同价格表、附加费历史快照、运单） | YAML/SQLite 文件 | **Dataverse 表** 或由 MCP server 持有 **[A]** | ★★★☆☆ | 存储要换，但如果数据只经 ②的 MCP 接口访问，skill 层无感 |
| **④ 评测用例** | `claude plugin eval` 的 `evals/` 目录 **[A]** | **Agent Evaluation 测试集** + Power Platform REST API **[A]** | ★★☆☆☆ | 文件格式不通用，但**用例语料（输入发票 + 期望结论）可移植**。按"语料与运行器分离"来组织 |

**一句话架构**：
```
          ┌─────────────────────────────────────────────┐
          │  ① Agent Skill (SKILL.md + references/)      │  ← 两平台通用
          │     只负责：路由 / 追问 / 解释 / 调用工具      │
          └──────────────────┬──────────────────────────┘
                             │ MCP (Streamable HTTP)
          ┌──────────────────▼──────────────────────────┐
          │  ② MCP Server（自托管，确定性计算）            │  ← 两平台通用
          │     chargeable_weight / surcharge_expected   │
          │     / compare_lines / lookup_rate            │
          └──────────────────┬──────────────────────────┘
                             │
          ┌──────────────────▼──────────────────────────┐
          │  ③ 事实层：费率表 · 附加费快照 · 运单          │  ← 需换存储
          │     开发期 SQLite/YAML → 生产 Dataverse       │
          └─────────────────────────────────────────────┘
```

---

## 3. 关键设计决策

### D1 · 确定性计算做成 MCP server，而不是 skill 里的 Python 脚本 ⭐

**理由**：这是唯一能让「计算逻辑」同时服务两个平台的方式。
- Claude Code 侧：直接连本地 MCP server。
- Copilot Studio 侧：MCP 已 GA，从 Tools 页通过 MCP 向导添加，或用 Power Apps 自定义连接器 **[A]**。
- 单元测试、版本管理、审计日志都留在你自己的代码库里，不被任何一个平台绑定。

**反面方案（不采用）**：把计算写成 skill 包里的 Python 脚本。Claude Code 能执行，但 Copilot Studio 的 skill 包虽然"可以包含 scripts" **[A]**，其执行模型与 Claude Code 不同，不能假定等价；且文档明确指出知识源场景下 *"agents can't write and run code"* **[A]**。**计算能力不能依赖平台恩赐。**

### D2 · `SKILL.md` 的 description 必须是一行短句 ⭐

**现状问题**：当前 `description` 是 **821 字符、5 句话**。Copilot Studio 的 skill 加载有硬性校验，*"Description too long — The effective description is longer than the model-facing catalog can accept"* 会导致**该 skill 被静默跳过**（agent 其余部分照常加载）**[A]**。

**这里有真实张力**：Claude 侧的最佳实践鼓励在 description 里写足触发条件；Copilot Studio 要求单行摘要。

**解法**：
- frontmatter `description`：一行，≤200 字符，只说"是什么 + 何时用"。
- 触发细节（DHL/FedEx/顺丰、"check the invoice"、chargeable weight 等）移到正文开头的 `## When to use this skill` 一节。两个平台的编排器都读正文。

同时要满足的其他加载期校验 **[A]**：`name` 非空且唯一、UTF-8 **无 BOM**、frontmatter 是合法 YAML（含冒号的值要加引号）。

### D3 · 费率表绝不作为 XLSX 知识源

Copilot Studio 文档明确：*"While you can add structured files, such as XLSX files from SharePoint, agents can't write and run code. Responses to analytical questions might not be optimal."* **[A]**
且 SharePoint 列表查询**只返回前 2,048 行** **[A]**——一份完整的快递分区费率表轻易超过这个量。

→ 费率表走 **Dataverse 表**或由 MCP server 持有，通过 `lookup_rate(carrier, lane, date, weight)` 这样的**精确查询工具**访问。
→ 这也印证了调研结论：**费率查询是结构化查询，不是 RAG**。向量检索只留给"合同条款原文"这类自由文本。

### D4 · 不依赖任何 Claude Code 专有能力

开发期可以用，但不能进入生产路径：

| 不可依赖 | 替代 |
|---|---|
| Bash / 任意命令执行 | MCP tool |
| 本地文件系统读写 | MCP tool 参数与返回值 / Dataverse |
| 子 agent（Agent tool） | Copilot Studio 的 connected agents / task agents（语义不同，不要预设等价） |
| 终端输出格式 | 结构化返回 + 平台自己的呈现 |

### D5 · 报告输出不强制 JSON

Copilot Studio 指引：强制刚性输出格式（如 *"respond only in JSON"*）会**压掉 agent 的引用标记（citation markers）** **[C，社区转述官方指引]**。而证据引用正是审计场景的硬需求。

→ 报告主体用 Markdown 表格（当前 SKILL.md 的模板方向是对的），需要机器可读时，由 ②的 MCP tool 返回结构化结果，而不是让 agent 吐 JSON。

### D6 · 规则与容差外置为数据文件

容差（0.5kg / 1% / 2%）、重量档位、各承运商除数、附加费口径，全部放进 ③，由 ② 读取。
两个好处：(a) 改规则不动 skill 文本，不触发重新评测全集；(b) 不同客户/合同可以带不同参数。

---

## 4. Copilot Studio 落地细节（已核对官方文档）

### 4.1 Harness 选择：Microsoft Copilot harness

Copilot Studio 现在有三种 harness（运行时）**[A]**。本项目应选 **Microsoft Copilot harness**，官方给出的适用场景几乎就是本项目的原题：

> *"It's the best fit for scenarios such as an accounts payable process, where an agent or workflow reads invoices, matches them to purchase orders, and routes exceptions for approval."* **[A]**

该 harness 的相关能力：目标分解与多步推理、跨 connectors/knowledge/MCP/connected agents 调工具、步骤失败后重试与换路径、原生读写 Word/Excel/PowerPoint/PDF、支持 skills 与 memory、沙箱执行。计费为 **Copilot Credits（按用量）** **[A]**。

> ⚠️ 文档正在换代：部分页面（配额、模型选择、MCP）标注 *"applies to … the standard harness"*，而 skills 页面说 skill 定义适用于 Microsoft Copilot harness **[A]**。**落地前必须在目标租户里实测确认**哪些配额与功能对所选 harness 生效。

### 4.2 MCP 接入（②的落地路径）

| 项 | 事实 **[A]** |
|---|---|
| 传输 | **仅 Streamable**。SSE 自 2025-08 起不再支持 |
| 接入方式 | Tools 页 → Add a tool → Model Context Protocol（MCP 向导，推荐）；或 Power Apps 自定义连接器 |
| 自定义连接器标记 | OpenAPI schema 中 `x-ms-agentic-protocol: mcp-streamable-1.0`，`operationId: InvokeMCP` |
| 认证 | None / **API key** / **OAuth 2.0**（Dynamic discovery(DCR) / Dynamic / Manual 三种） |
| 原语支持 | **Tools 与 Resources**。⚠️ *Resource 必须被配置为某个 tool 的输出*才能被 agent 使用 |
| 工具粒度控制 | 可关掉 `Allow all`，逐个工具开关；关掉后新增工具默认关闭 |
| 企业注册路径 | 也可用 **Agent 365 CLI** 注册 BYO MCP server → M365 管理中心审批 + Entra 授权 → 最多 **30 分钟**后出现在环境中 |
| **治理（重要）** | **MCP 走 Power Platform 连接器通道，因此受 DLP 数据策略管控**。这对"公司许可的设施"是加分项：安全团队能用现有策略管住它 |
| 定制限制 | 不能在 Copilot Studio 里覆写 MCP 工具的描述或输入配置 **[C]** |
| 私网 | 社区反馈：无法直连部署在 Azure 私有网络内的自建 MCP server **[C，需与 IT 确认]** |

**→ 对我们的影响**：MCP server 必须**公网可达 + Streamable HTTP + API key 或 OAuth2**。这是一个需要尽早和公司 IT/安全确认的前置条件，建议在 Phase 1 就确认，不要等到 Phase 4。

### 4.3 配额与限制（会影响设计的）**[A]**

| 项 | 限制 | 对本项目的含义 |
|---|---|---|
| Skills | 100 / agent | 充裕 |
| 知识源 | 500（所有类型合计） | 充裕 |
| 上传文件 | 512 MB / 个，500 个 | 充裕 |
| Topics | 1,000 / agent | 不用 topics 路线，无影响 |
| **连接器负载** | **5 MB**（GCC 450 KB） | ⚠️ MCP 单次返回不能超过。多票批量对账要**分页返回** |
| 消息 + 工具响应 | 受所选模型上下文窗口限制 | ⚠️ 不要把整份费率表塞进工具返回值，只返回命中的那几行 |
| 模型流式响应 | **5 分钟超时**，不可配置 | ⚠️ 单票核对要在 5 分钟内完成；重活推到 MCP server 异步 |
| SharePoint | 生成式编排下 **25 个站点 URL**；无 M365 Copilot 许可时 **>7 MB 文件不能用于生成答案**；列表只读**前 2,048 行** | 见 D3 |

### 4.4 模型

Copilot Studio 的模型列表里 **Claude Sonnet 4.6（General）、Claude Opus 4.6 / 4.7（Deep）均为 GA** **[A]**，另可添加来自 Anthropic / xAI / Mistral 的**外部模型**作为主模型 **[A]**。

→ **这进一步降低迁移风险**：在 Claude 上调好的指令，到 Copilot Studio 可以跑在同族模型上，行为漂移小于换模型厂商。
→ ⚠️ 但多数 Claude 条目标注 **cross-geo**（*"data might be processed outside your region"*）**[A]**，且外部模型托管在 Microsoft 管理边界之外、适用 Anthropic 自己的服务条款 **[C]**。**发票含商业敏感信息，这一条必须先过公司合规。**

### 4.5 评测（④的落地路径）

Copilot Studio 内置 **Agent Evaluation**，测试方法有 8 种 **[A]**：

| 方法 | 打分 | 对我们的用途 |
|---|---|---|
| Exact match | 通过/失败 | **金额、重量等数字字段的首选**——确定性 |
| Keyword match | 通过/失败 | 检查报告里出现了预期的差异项 |
| **Tool use** | 通过/失败 | **验证是否真的调了 MCP 计算工具**（对应 Claude 侧的 `tool_used` grader） |
| Compare meaning / Text similarity | 0-100% | 结论措辞的相似度 |
| Custom | 通过/失败 | 自定义判定标准与标签（对应 Claude 侧的 `llm` grader） |
| General quality / Content safety | 100% / 通过失败 | 本场景次要 |

**CI/CD**：通过 **Power Platform REST API** 自动跑评测 **[A]**：
```
GET  /copilotstudio/environments/{envId}/bots/{botId}/api/makerevaluation/testsets?api-version=2024-10-01
POST /copilotstudio/environments/{envId}/bots/{botId}/api/makerevaluation/testsets/{testSetId}/run?api-version=2024-10-01
```
异步执行，返回 `runId` 再取结果；可用 `mcsConnectionId` 指定用户身份跑（不传则无认证运行）**[A]**。

**两侧 grader 的对应关系**（这是"用例语料可移植"的具体含义）：

| Claude `claude plugin eval` | Copilot Studio Agent Evaluation |
|---|---|
| `regex` grader | Keyword match / Exact match |
| `tool_used` grader | Tool use |
| `llm` grader | Custom（自定义指令 + 标签） |
| **no-plugin baseline（Δ）** | **无等价物** ← 见 §5 |

> ⚠️ 社区提到测试集上限 100 条用例、结果 89 天后过期 **[C，未在官方页核实]**。若为真，**基线导出必须存在 Copilot Studio 之外**——这也正是"语料与运行器分离"的另一个理由。

---

## 5. 明确不可移植的部分

诚实列出来，避免将来惊讶：

1. **`claude plugin eval` 的 no-plugin baseline（Δ）** —— Copilot Studio 没有"不加载 skill 跑一遍"的对照。
   → **趁现在在 Claude Code 上把 Δ 测出来并存档**。这是回答"这些指令到底有没有用"的唯一窗口，迁移后就没有了。
2. **Bash / 任意脚本执行** —— 见 D4。
3. **`claude plugin eval` 的 3 次重跑机制** —— Copilot Studio 侧需自己循环调 REST API 多跑几轮再取均值（官方评测指引本身也建议多跑取平均 **[C]**）。
4. **子 agent 编排语义** —— 两边概念不等价，不要跨平台复用编排假设。
5. **MCP 工具描述的平台内覆写** —— Copilot Studio 不支持 **[C]**，所以**工具描述必须在 MCP server 端写好**，这反而是好事：描述也成了可版本管理的代码。

---

## 6. 路线图（已按 Copilot Studio 约束重排）

与 `research/2026-11-landscape.md` §7 的差异：**MCP server 提前，Copilot Studio 前置条件确认提前。**

**Phase 0 — 止血（1–2 天）** ✅ 2026-11-18 完成
- [x] 修海运 BAF 口径（per TEU / per CBM，非百分比）· 另把 CAF 单独拆出（CAF 确实是百分比）
- [x] 修空运 FSC 口径（per kg / percent 可配置）· 另修正 express FSC 的「适用基数」问题
- [x] 补 0.5 kg 进位与重量档位，理清与容差的关系 → 新增共用文件 `references/weight-rules.md`
- [x] **按 D2 改 `description` 为单行**（182 字符），触发细节移入正文 `## When to Use This Skill`

**Phase 1 — 测试基建 + 前置条件确认（1 周）**
- [ ] `claude plugin eval init`，10 个用例（3 正常 / 5 对抗 / 2 负样本）
- [ ] **跑出 Δ 并存档**（迁移后不可再得，见 §5.1）
- [ ] 用例语料存成平台中立格式：`evals/corpus/<case>/{input/, expected.yaml}`，再由各平台的 runner 读取
- [ ] **并行推进：找 IT/安全确认三件事** —— ① 自建 MCP server 能否公网暴露给 Copilot Studio；② DLP 策略是否放行自定义连接器；③ Claude 模型 cross-geo 处理是否过合规

**Phase 2 — 三层分离 + MCP server（2–3 周）**
- [ ] `schemas/`：invoice / rate-card / surcharge（字段名对齐 IATA ONE Record、DCSA）
- [ ] `mcp-server/`：Streamable HTTP + API key 认证，工具 `chargeable_weight` / `expected_surcharge` / `lookup_rate` / `compare_lines`
- [ ] 每个工具 100% 单元测试覆盖（pytest）
- [ ] SKILL.md 瘦身为"路由 + 追问 + 解释"，计算全部委托 MCP
- [ ] **返回值分页**，单次 < 5 MB（§4.3）

**Phase 3 — 事实层（1 个月+）**
- [ ] 附加费快照表（**按运单日期查历史值**）
- [ ] EIA API 接入（美国陆运 FSC 的确定性验证）
- [ ] 重复计费检测（需跨发票持久化）
- [ ] 承运商 rating API 作为第二意见（明确标注 indicative）

**Phase 4 — Copilot Studio 落地（预留 2–4 周，含审批等待）**
- [ ] 在目标租户建 Microsoft Copilot harness agent
- [ ] 上传 skill ZIP（`SKILL.md` + `references/`），验证加载期校验全过
- [ ] 接入 MCP server（向导或自定义连接器 + Agent 365 CLI 注册路径）
- [ ] 费率表迁入 Dataverse
- [ ] 用例语料导入 Agent Evaluation 测试集，接 Power Platform REST API 进 CI
- [ ] 进 Dataverse solution，走 环境管道（dev → test → prod）
- [ ] **对账**：同一批用例在两个平台的结论差异逐条解释清楚，再切换

**Phase 5 — 闭环与规模化**：争议函 → credit note 跟踪 → 关闭；月结批量；仓储账单 module。

---

## 7. 对现有仓库的改造动作

| # | 动作 | 为什么 | 阶段 |
|---|---|---|---|
| 1 | ~~`description` 改单行，触发细节进正文~~ ✅ | Copilot Studio 会静默跳过超长 description 的 skill | P0 |
| 2 | ~~确认 `SKILL.md` 为 UTF-8 无 BOM、frontmatter 合法 YAML~~ ✅ 已验证（无 BOM、无 CRLF、frontmatter 为合法 key: value 映射、description 无需加引号） | 加载期校验 | P0 |
| 3 | ~~修 BAF / FSC 口径~~ ✅ | 结论会算错 | P0 |
| 4 | 把容差与承运商参数抽到 `config/tolerances.yaml`、`config/carriers.yaml` | D6 | P1 |
| 5 | 新增 `mcp-server/`，计算逻辑搬进去 | D1，两平台通用 | P2 |
| 6 | ~~把 `<!-- RAG_HOOK -->` 改名为 `<!-- RATE_LOOKUP -->`~~ ✅ 随 P0 一并完成（重写这些段落时顺手做了）；`CONTRACT_CLAUSE_RAG` 待实际有合同条款检索需求时再加 | 费率查询不是 RAG；也对应 Dataverse vs 知识源两种落地 | P2 |
| 7 | `evals/corpus/` 平台中立语料 + 各平台 runner 适配 | ④的可移植性只能这样拿到 | P1 |
| 8 | ~~README 增加"目标平台：Copilot Studio"说明~~ ✅ | 让后来人不写进不可移植的依赖 | P0 |

---

## 8. 风险

| 风险 | 影响 | 应对 |
|---|---|---|
| **MCP server 无法从公司网络暴露给 Copilot Studio** | ②的方案失效，计算要改用 Power Automate 的 agent flow 重写一遍 | **Phase 1 就确认**，不要等 Phase 4。备选：计算逻辑封装成 Power Platform 自定义连接器后端，或 agent flow |
| Claude 模型 cross-geo 不过合规 | 需换 GPT 系模型，指令行为会漂移 | 评测语料已就位的话，换模型只是重跑一遍；这是 Phase 1 做评测的另一个理由 |
| Copilot Studio 文档正在换代（harness/workflows 概念重命名） | 按文档设计的细节可能过时 | 所有配额与功能**在目标租户实测确认**；本文档每条事实都标了来源与核对日期 |
| Copilot Credits 成本不可控 | 预算问题 | 官方支持 pay-as-you-go credit 上限 **[C]**；评测本身也消耗 credits **[A]**，CI 频率要控制 |
| 测试集 100 条上限 / 结果 89 天过期（未核实）**[C]** | 基线丢失 | 语料与基线导出都存在仓库里 |
| 发票含商业与个人敏感信息 | 合规 | 测试数据脱敏；黄金集不进公共仓库；DLP 策略覆盖 MCP 连接器 |

---

## 9. 来源

**Microsoft 官方（本文已逐页核对，核对日期 2026-11-17）**
- [Choose a harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Agent skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview) · [Create a skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-create) · [Add an existing skill（含接受格式与加载期校验）](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing)
- [Connect your agent to an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent) · [Add tools and resources from an MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent)
- [Quotas and limits](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
- [Select the agent's AI model（模型与区域可用性）](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model)
- [Agent evaluation test methods](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview) · [Automate evaluations with Power Platform API](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-rest-api)
- [Security and governance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance) · [Solutions overview (ALM)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview)
- [MCP is now GA in Copilot Studio（公告）](https://www.microsoft.com/en-us/copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)
- [Expanding model choice in Microsoft 365 Copilot](https://www.microsoft.com/en-us/microsoft-365/blog/2025/09/24/expanding-model-choice-in-microsoft-365-copilot/)

**Anthropic 官方**
- [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals) · [Agent Skills](https://code.claude.com/docs/en/skills) · [anthropics/skills（含 `spec/`）](https://github.com/anthropics/skills)

**其他** —— 领域与开源生态来源见 [`research/2026-11-landscape.md`](research/2026-11-landscape.md) §9。
