# Copilot Studio 落地前置条件 — 待 IT / 安全确认

> 用途：这三个问题的答案决定架构，不决定进度细节。越早问越好——其中第 1 条若为「否」，
> 计算层方案需要整体换一条路，而那部分工作在 Phase 2 就会开始写。
> 技术事实已核对 Microsoft Learn（2026-11-17），下面每条都附了依据，IT 无需自行查证。

## 背景（一段话）

我们在做物流账单自动核对。生产平台是 Copilot Studio（公司许可的 agent 设施）。
架构上领域知识做成 Copilot Studio 的 **Agent Skill**（官方支持上传 `SKILL.md` + 支持文件的
ZIP 包），确定性计算（计费重量、附加费、费率比对）做成一个**自托管的 MCP server**，
由 agent 作为 tool 调用。费率表落在 **Dataverse**。

---

## 问题 1（最关键）· 自建 MCP server 能否被 Copilot Studio 访问

**问：** 我们能否在公司环境里部署一个 HTTPS 服务，并让 Copilot Studio 的 agent 作为 MCP
server 调用它？具体需要确认：

| 要点 | 我们的需求 | 依据 |
|---|---|---|
| 传输协议 | 必须是 **Streamable HTTP**。SSE 自 2025-08 起 Copilot Studio 已不支持 | Learn: *Connect your agent to an existing MCP server* |
| 可达性 | Copilot Studio 是云服务，需要能发起到我们服务的出站请求 | 同上 |
| 私有网络 | 社区反馈称部署在 Azure 私有网络内的自建 MCP server **无法**被直连。**这一条请你们确认**，我们没有权威来源 | 社区问答，未经官方确认 |
| 认证 | 支持 None / **API key** / **OAuth 2.0**（动态发现 DCR、动态、手工配置三种）。我们倾向 OAuth 2.0 | Learn 同页 |
| 注册路径 | 另有企业路径：用 **Agent 365 CLI** 注册 BYO MCP server → M365 管理中心审批 + Entra 授权 → 最多 30 分钟后在环境中可见。**这条路径是否是你们希望我们走的？** | Learn 同页 |

**为什么重要：** MCP 是唯一能让同一套计算逻辑同时服务开发环境（Claude Code）和生产环境
（Copilot Studio）的机制。单元测试、审计日志、版本管理都留在我们自己的代码库里。

**如果答案是「否」：** 计算逻辑要改用 Power Automate 的 agent flow 或 Power Platform 自定义
连接器后端重写一遍，并且要分别为两个平台维护两份实现。这会显著增加工作量，也会让「同一套
逻辑两边跑」的保证失效。**所以这一条请优先回答。**

---

## 问题 2 · DLP 数据策略是否放行

**问：** 我们的 Power Platform 环境的 DLP（数据丢失防护）策略，是否允许 agent 使用自定义
连接器 / MCP server？需要走什么审批？

**背景（对你们应是加分项）：** Copilot Studio 访问 MCP server 是**通过 Power Platform 连接器
通道**实现的，因此**现有的 DLP 数据策略天然就能管住它**——不需要为 MCP 单独建一套管控。
依据：Learn 原文 *"Access to MCP servers in Copilot Studio relies on Power Platform connectors
for connectivity. This condition means that if a data policy regulates Power Platform
connectors, it also regulates access to the MCP server and its tools for your agent."*

**顺带确认：** 单次连接器响应上限 **5 MB**（GCC 环境为 450 KB）。我们会据此做分页，但需要
知道我们的环境属于哪一类。

---

## 问题 3 · 模型的跨区数据处理是否过合规

**问：** 账单核对会把**发票内容**（收发货人名称与地址、货值、商业条款）送给模型处理。
Copilot Studio 的模型列表中，Claude Sonnet 4.6 / Opus 4.6 / 4.7 均为 GA，但多数条目标注
**cross-geo**（官方措辞：*"data might be processed outside your region"*）。
另外，来自 Anthropic / xAI / Mistral 的**外部模型**托管在 Microsoft 管理边界之外，适用模型
厂商自己的服务条款。

**需要你们判断：**
1. 发票类商业数据能否接受 cross-geo 处理？
2. 如果不能，我们是否只能用非 cross-geo 的 GPT 系模型？
3. 外部模型（Anthropic 直供）这条路径是否被公司政策允许？

**如果必须换模型：** 我们已经建好了评测集（12 个用例，含对抗与负样本），换模型只需重跑一遍
评测、对比分数。这是我们在开发阶段先建评测的原因之一，所以这一条不会卡住进度，只会影响
最终用哪个模型。

---

## 顺带需要知道的（不阻塞，但影响排期）

| 项 | 问题 |
|---|---|
| Harness 与计费 | 我们需要 **Microsoft Copilot harness**（官方举例即为「读发票、匹配 PO、异常转审批」的应付账款场景），其计费为 **Copilot Credits** 按用量。预算由谁承担、是否需要设上限？ |
| 环境 | 是否已有 dev / test / prod 三套 Power Platform 环境与部署管道？agent 存放在 Dataverse solution 中，走管道发布 |
| Dataverse | 费率表需要落在 Dataverse 表。谁有建表权限？ |
| 评测自动化 | Copilot Studio 的 Agent Evaluation 可通过 **Power Platform REST API** 跑 CI。需要一个有相应 Power Platform API scope 的应用注册（app registration）——由谁创建？ |

---

## 我们这边的状态

- Phase 0（计费口径修正）已完成。
- Phase 1（评测基建）已完成：12 个用例、双臂基线、grader 全部可回归。
- Phase 2（三层分离 + MCP server）即将开始，**问题 1 的答案直接决定这部分怎么写**。
