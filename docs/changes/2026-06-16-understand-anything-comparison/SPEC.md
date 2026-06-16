# SPEC - understand-anything comparison

> 本文件描述本次调研应该回答什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 调研完成，等待用户选择后续方向 |
| 需求来源 | 用户要求联网搜索 `understand-anything`，比较它和 CodeAnalyst 的区别、可借鉴点，并判断继续当前项目还是 fork/clone 外部项目 |
| 工作包目录 | `docs/changes/2026-06-16-understand-anything-comparison/` |
| 最后更新 | 2026-06-16 |

## 1. 一句话目标

帮助用户基于外部项目证据和 CodeAnalyst 现有合同，决定下一步是继续开发 CodeAnalyst、选择性吸收 Understand Anything 的能力，还是迁移到 Understand Anything fork。

## 2. 背景与问题

- 当前行为：CodeAnalyst 是 read-only analysis assistant，CLI 负责确定性扫描和中央分析包生成，skill 负责解释、review、refactor/design guidance；默认产物写入 `/Users/chihoyo/Project/CodeAnalyst/analyses/`，不写被分析目标项目。
- 外部参照：Egonex-AI/Understand-Anything 是 TypeScript/pnpm monorepo，主打多平台插件、Tree-sitter + LLM hybrid、多 agent pipeline、交互式 dashboard、语义搜索、diff impact、business/domain view、knowledge-base analysis 和可提交 `.understand-anything/` 图谱。
- 问题：两者同属 codebase understanding，但产品边界、写入策略、依赖复杂度、交互体验和分发路径不同；需要判断是否值得迁移或借鉴。
- 期望收益：避免重复造轮子，同时保留 CodeAnalyst 已经稳定的 docs-driven、read-only、central-library、standard-library-first 方向。

## 3. 范围

### 3.1 本次要做

- 联网确认主项目、当前活跃度、核心功能、安装方式、技术栈和输出模型。
- 对比 CodeAnalyst 与 Understand Anything 的目标、架构、产物、依赖、写入边界、适用场景。
- 列出 CodeAnalyst 值得借鉴的能力，并按优先级给出建议。
- 给出是否继续当前项目或 fork/clone Understand Anything 的判断。

### 3.2 本次不做

- 不克隆 Understand Anything 到本工作区。
- 不把 Understand Anything 代码或依赖迁入 CodeAnalyst。
- 不改变 CodeAnalyst production code、CLI surface、安装脚本或 skill 文案。
- 不代表用户决定未来一定采用某个功能；本次只给决策建议。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户想知道是否继续 CodeAnalyst | 得到基于 CodeAnalyst docs 与外部 repo 证据的明确建议 |
| S2 | 用户想借鉴 Understand Anything | 得到可拆解、可排期、符合 CodeAnalyst invariants 的能力清单 |
| S3 | 用户考虑 fork 外部项目 | 清楚知道 fork 的收益、成本和会破坏哪些 CodeAnalyst 既有选择 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | 调研必须使用当前联网证据，不依赖旧印象 | ROADMAP research log 记录 URL、日期、关键事实 | 完成 |
| R2 | 比较必须引用 CodeAnalyst source-of-truth docs | ROADMAP research log 引用 `docs/SPEC.md`、`docs/ARCHITECTURE.md`、`docs/DECISIONS.md` | 完成 |
| R3 | 建议必须区分 borrow、defer、avoid/fork 三类 | ROADMAP 和 DECISIONS 给出分类建议 | 完成 |
| R4 | 建议不能破坏 read-only target invariant，除非显式标为未来需要重新决策 | SPEC 约束与 DECISIONS risks 覆盖该点 | 完成 |

## 6. 约束与不变式

1. **#1**: 本次调研不写入被分析目标项目，也不克隆外部项目到 CodeAnalyst 工作区。
2. **#2**: 对外部项目的事实必须来自 GitHub/Web 当前证据，或标记为推断。
3. **#3**: 推荐方向不得静默违反 CodeAnalyst 项目级 read-only target、evidence、deterministic CLI、small-context 和 recommendation-only invariants。
4. **#4**: 借鉴建议必须被拆成 CodeAnalyst-native roadmap ideas，而不是把外部项目整体当作替代实现。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 继续 CodeAnalyst | 保留 Python standard-library-first CLI、central analyses library、docs-driven source-of-truth 和 read-only target boundary |
| 借鉴外部能力 | 先做 schema/search/onboarding/diff guidance 等可独立落地能力，再评估 Tree-sitter 或 React dashboard |
| 采用 Understand Anything fork | 视为新产品线或实验分支，不作为 CodeAnalyst 的直接替换 |

## 8. 验收标准

1. 用户能看出两项目的核心差异和各自适用场景。
2. 用户能得到明确建议：继续 CodeAnalyst，选择性借鉴 Understand Anything，不建议直接 fork 替换。
3. 本工作包记录调研证据、取舍、后续风险，并通过 `docdev audit`。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否未来要允许 target-local shareable graph，例如 `.understand-anything/` 风格？ | 不建议默认允许；如要做，必须新增 output mode 决策并保持默认中央库 | 否 |
| Q2 | 是否引入 Tree-sitter 依赖？ | 有价值，但会改变 standard-library-first 取舍；建议先作为 optional enhancement 调研 | 否 |
| Q3 | 是否建设 React/Vite dashboard？ | 体验收益高，维护成本也高；建议先增强现有 static site/schema/search，再考虑 | 否 |
