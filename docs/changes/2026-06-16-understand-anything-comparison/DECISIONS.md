# DECISIONS - understand-anything comparison

> 本文件记录这次调研中为什么这么建议。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Continue CodeAnalyst and borrow selectively

**日期 / Date**: 2026-06-16

**上下文 / Context**:

Understand Anything 和 CodeAnalyst 都解决 codebase understanding，但前者是多平台插件 + 交互式知识图谱产品，后者是 docs-driven、低依赖、只读、中央分析库优先的个人分析助手。用户需要判断是否继续当前项目，还是 clone/fork 外部项目作为基础。

**选项 / Options**:

- A. 继续 CodeAnalyst，选择性吸收 Understand Anything 的能力。
- B. 克隆/fork Understand Anything，并把后续开发重心迁到它上面。
- C. 两者都维护：CodeAnalyst 作为轻量 CLI，Understand Anything fork 作为重型 dashboard 实验。

**选择 / Chosen**: A 为默认建议；C 可作为后续实验；不建议 B 作为当前主线。

**理由 / Rationale**:

- CodeAnalyst 已有清晰 source-of-truth：read-only target、central analyses library、deterministic CLI、recommendation-only output，这些都和用户过去的工具链偏好一致。
- Understand Anything 的强项是交互式学习体验、Tree-sitter 结构抽取、语义搜索、guided tour、diff impact、incremental update 和多平台插件安装；这些可以拆成 CodeAnalyst-native features，不需要直接迁移产品边界。
- 直接 fork 会引入 TypeScript/pnpm monorepo、Tree-sitter grammar matrix、React/Vite dashboard、target-local `.understand-anything/` 写入和上游同步成本；这会把当前项目从 personal analysis assistant 变成维护一个大型图谱产品。
- CodeAnalyst 的当前短板不是“没有外部项目那么完整”，而是下一层体验还不够产品化：search/chat/onboard/diff/guided tours 可以用现有 pack/review evidence 渐进增强。

**风险 / Risks**:

- 选择性借鉴会慢于直接 fork 获得完整 dashboard，但能保住 CodeAnalyst 的可控性。
- 如果未来目标变成团队共享 dashboard 或 Claude plugin marketplace-first，A 可能不够，需要重新评估 C。
- 一些 Understand Anything 能力依赖 Tree-sitter/LLM pipeline，不能简单照搬到 CodeAnalyst 的标准库 CLI。

**对应代码 / 文档**:

- SPEC §7
- ROADMAP §2, Step 3
- ARCHITECTURE §3-5
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`

## D-002 - Borrow graph interaction before heavy parser dependencies

**日期 / Date**: 2026-06-16

**上下文 / Context**:

Understand Anything 的 Tree-sitter + LLM hybrid 很强，但 CodeAnalyst 当前 native install 和 standard-library-first 路线让安装、验证和跨机器维护更简单。需要决定先借鉴哪一层。

**选项 / Options**:

- A. 先引入 Tree-sitter 和多语言 AST，提升结构精度。
- B. 先增强已有 pack 的交互消费层：search、chat context、onboard guide、diff impact、guided tour、graph schema。
- C. 先重写 dashboard 为 React/Vite。

**选择 / Chosen**: B。

**理由 / Rationale**:

- B 可以复用现有 `inventory.json`、`flow_map.json`、`script_check.json`、`import_graph.json`、`vibe_audit.json`、`review_pack.json`，风险最小。
- 用户可感知收益大：不是多几个扫描字段，而是更容易问、查、学、复盘和决定下一步。
- A 和 C 都值得后续调研，但会改变依赖、打包、安装和验证成本，应先独立 spike。

**风险 / Risks**:

- 现有 import graph 精度仍不如 Tree-sitter；生成的 tour/search 需要清楚标记 evidence vs inference。
- 若 dashboard 体验目标很高，最终仍可能需要前端技术栈。

**对应代码 / 文档**:

- SPEC §9
- ROADMAP §5
- `src/code_analyst/review_pack.py`
- `src/code_analyst/render_site.py`
- `src/code_analyst/verify_site.py`
