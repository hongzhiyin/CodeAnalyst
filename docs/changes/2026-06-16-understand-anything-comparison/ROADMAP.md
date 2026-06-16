# ROADMAP - understand-anything comparison

> 本文件追踪本次调研做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 调研完成，等待用户确认后续路线
**当前 Step / Current Step**: Step 3 - 形成并确认方案
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 已补 `ARCHITECTURE.md`，因为本次调研核心是两个项目的结构、数据流和输出模型差异。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [ ] 用户已确认实现方案

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证
- [x] 文档与最终调研结论一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | CodeAnalyst product boundary | CodeAnalyst 目标是个人长期使用的代码分析助手；CLI 做确定性扫描和产物生成，skill 做解释、review 和设计建议；默认不跨项目自动改代码。 | `docs/SPEC.md` §1, §3, §4 | 继续开发时应保留 read-only target、central library 和 recommendation-only 边界。 |
| R-2 | CodeAnalyst architecture | 当前是 Python standard-library-first CLI + synced skill + static HTML visual pack；核心模块包括 inventory、flow-map、script-check、import-graph、vibe-audit、pack、review-pack、render-site、verify-site。 | `docs/ARCHITECTURE.md` §1-4 | CodeAnalyst 更像轻量、可验证、低依赖的 analysis toolkit。 |
| R-3 | Understand Anything identity | GitHub 搜索主结果为 `Egonex-AI/Understand-Anything`，README 描述为把 codebase、knowledge base、docs 变成交互式知识图谱，支持 Claude Code、Codex、Cursor、Copilot、Gemini CLI 等。 | https://github.com/Egonex-AI/Understand-Anything | 它不是单纯 CLI scanner，而是多平台插件 + 图谱产品。 |
| R-4 | External project activity | GitHub API 于 2026-06-16 返回 public repo、约 60.6k stars、约 5k forks、open issues/PRs 合计较多、默认分支 main、最新 pushed_at 2026-06-11；latest release 为 v2.7.3，published_at 2026-05-19。 | GitHub API `/repos/Egonex-AI/Understand-Anything` and `/releases/latest` | 外部项目活跃且社区强，但也意味着大项目治理和上游变动成本。 |
| R-5 | Understand Anything command surface | README 列出 `/understand`、`/understand-dashboard`、`/understand-chat`、`/understand-diff`、`/understand-explain`、`/understand-onboard`、`/understand-domain`、`/understand-knowledge`、`--auto-update`、subdirectory scope 和 language output。 | https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/README.md | 最值得借鉴的是围绕已有 graph 的后续交互命令，而不是一次性 pack 本身。 |
| R-6 | Understand Anything output model | `/understand` 生成 `.understand-anything/knowledge-graph.json`，README 鼓励提交 `.understand-anything/` 中除 intermediate 和 diff-overlay 外的内容，并可用 post-commit hook 保持新鲜。 | README "Share the Graph with Your Team" | 这是团队共享优势，但默认写入 target repo，与 CodeAnalyst invariant #1 相冲突。 |
| R-7 | Understand Anything implementation | Root `package.json` 是 pnpm monorepo；core package 依赖 Tree-sitter grammars、web-tree-sitter、zod、yaml、fuse.js；dashboard package 依赖 React/Vite、xyflow、dagre、d3-force、elkjs、graphology、zustand 等。 | Raw `package.json`, `understand-anything-plugin/packages/core/package.json`, `packages/dashboard/package.json` | 功能强，但依赖和维护面明显大于 CodeAnalyst；直接 fork 会改变项目成本模型。 |
| R-8 | Understand Anything pipeline | README 表示 Tree-sitter 提供确定性结构事实，LLM 生成语义摘要、layer、business-domain、guided tours 等；`/understand` 编排多个 specialized agents，并做并行 file analysis 与 incremental updates。 | README "Under the Hood" | 可借鉴 "deterministic structure + semantic layer" 的表达和 graph reviewer/incremental 思路。 |
| R-9 | Install/distribution | Understand Anything 对 Claude Code 走 plugin marketplace，对 Codex 等走 curl installer，installer clone 到 `~/.understand-anything/repo` 并创建平台 symlink；Cursor/Copilot 有 plugin auto-discovery。 | README "Multi-Platform Installation" | 它的多平台安装覆盖面值得观察，但 CodeAnalyst 已有 native release/source checkout 分离路线。 |
| R-10 | Borrow candidates | Guided tours、semantic/fuzzy search、diff impact、explain/onboard/chat、language-aware dashboard labels、layer grouping、tested_by edges、incremental fingerprinting 都可拆成 CodeAnalyst-native features。 | README + latest release notes | 应按 CodeAnalyst invariants 小步吸收，先做 schema/search/review outputs，再考虑重依赖。 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研外部项目与当前项目 | 完成 |
| 3 | 形成并确认方案 | 进行中 |
| 4 | 实施代码与测试 | 跳过：本次是只读调研，不改 production code |
| 5 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把外部项目对比需求转成可验收的调研问题。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 的目标、范围和非目标足以支撑最后建议。

---

## Step 2 - 调研外部项目与当前项目

**Goal**: 收集足够证据，区分事实和推断。

**Tasks**:
- [x] 读取 CodeAnalyst 项目级 SPEC / ROADMAP / ARCHITECTURE / DECISIONS。
- [x] 联网搜索 `understand-anything`，确认主仓库与当前活跃度。
- [x] 读取外部 README、GitHub metadata、release notes、package manifests、核心目录列表。
- [x] 对比写入边界、输出模型、依赖和产品体验。

**Acceptance**:
1. 调研记录能支撑继续、借鉴或 fork 的判断。

---

## Step 3 - 形成并确认方案

**Goal**: 给出后续路线建议，并等待用户选择是否进入实现。

**Tasks**:
- [x] 写入 DECISIONS D-001。
- [x] 输出 borrow / defer / avoid-fork 分类。
- [x] 明确下一步若继续 CodeAnalyst，应先做哪些低风险能力。
- [ ] 用户确认下一步实现方向。

**Acceptance**:
1. 用户能据此决定下一步是否排期 CodeAnalyst feature work。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `docdev new-change "understand-anything-comparison" /Users/chihoyo/Project/CodeAnalyst` | 通过 | 创建 scoped packet |
| SPEC-2 | 联网搜索 GitHub 和读取 README/API/raw manifests | 通过 | 证据记录在 §2 |
| SPEC-3 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/CodeAnalyst --write-report` | 通过 | No findings; wrote `docs/_generated/docdev/audit.json` |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 外部 repo 持续高速变化 | 当前调研会过期 | 未来实现前重新打开 README/release notes |
| F-2 | 直接 fork 会把 CodeAnalyst 拉向 TypeScript monorepo + dashboard product | 破坏低依赖、read-only、中央库和 docs-driven节奏 | 不建议作为默认路线 |
| F-3 | 引入 Tree-sitter 会改善结构精度但增加安装/打包复杂度 | 影响 native release 和 cross-machine install | 先做 optional spike，不进核心路径 |
| F-4 | target-local shareable graph 对团队协作有价值 | 与 invariant #1 冲突 | 如要做，新增显式 `--target-local` 或 export mode 决策，默认仍写中央库 |
