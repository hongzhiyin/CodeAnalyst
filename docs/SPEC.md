# CodeAnalyst SPEC

## 1. Goal

把 `code-analyst` 逐步升级为 **CodeAnalyst**：适合个人长期使用的代码分析助手。CLI 负责可重复、可验证的代码扫描和产物生成；skill 负责阅读代码、解释各部分在做什么、提出改进建议、重构方向和架构设计方案。

本项目不承担跨项目自动改代码的职责。真正的代码修改、重构落地和项目迭代应回到被分析项目自身进行。

## 2. Decision Table

| Topic | Choice | Why |
|---|---|---|
| 产品名 | `CodeAnalyst` | 比 `CodeReader` 更能表达分析、判断、review 和重构建议，同时不暗示自动改代码。 |
| 主体形态 | `skill + CLI` | skill 保存判断框架，CLI 固化重复、确定性的扫描/审计/建包/验证步骤。 |
| 默认写入位置 | `/Users/chihoyo/Project/CodeAnalyst/analyses/` | 保持被分析项目干净，方便跨项目积累学习产物。 |
| CLI 名称 | `code-analyst` | 符合多词 CLI 惯例，并和产品名 `CodeAnalyst` 对齐。 |
| 第一版核心命令 | `inventory` / `flow-map` / `script-check` / `import-graph` / `vibe-audit` / `pack` / `review-pack` / `visual-pack` / `render-site` / `verify-site` / `doctor` | 覆盖快速盘点、多项目类型入口线索、脚本入口验证、静态依赖图、vibe coding 风险识别、分析包生成、review/重构/架构建议、静态可视化、站点验证、环境自检。 |
| review / refactor / architecture | 同项目内做 read-only review/design pack；真正改代码回到目标项目执行 | review/design 复用当前证据层；写入目标项目属于目标项目自己的迭代边界。 |
| 运行依赖 | Python 标准库优先 | 避免在临时项目里先陷入依赖安装。 |
| 产物语言 | 跟随用户语言；中文请求生成中文文档 | 和原 skill 契约保持一致，减少二次整理。 |
| 外部最佳实践吸收 | 只吸收可操作原则，不复制长篇上下文 | 降低常驻指令膨胀带来的成本和误导。 |
| installed skill portability | source skill 同步时生成 `bin/code-analyst`，skill 声明 `metadata.requires.bins` 和 `cliHelp`，fallback 使用 `CODE_ANALYST_PROJECT_DIR` | 后续 agent 可以从 PATH、skill-local wrapper 或 source checkout 稳定找到 CLI。 |

## 3. Invariants

**#1** Read-only target invariant: 除非用户明确要求，CLI 和 skill 不能写入被分析目标项目，只能读取目标并把产物写入中央分析库或用户指定输出目录。

**#2** Evidence invariant: 每个关键结论都必须能追溯到文件、命令输出、脚本检测结果，或明确标记为 `Inference`。

**#3** Deterministic CLI invariant: 可重复的文件枚举、manifest 检测、vibe audit、分析包目录创建、JSON 校验必须由 CLI 完成，而不是每次由模型自由发挥。

**#4** Small-context invariant: skill 文案只保留决策流程和命令选择；长模板、检查清单、输出契约和示例放到 references 或 CLI 产物里。

**#5** Vibe-coded project invariant: 对 AI 生成项目的分析必须显式检查 likely generated leftovers：未引用文件、半接线 UI、缺失脚本目标、框架配置/依赖不匹配、重复实现、缺少验证闭环。

**#6** Improvement guidance invariant: 分析包不能只解释“现在是什么”，还要给出下一步优化路线：先修可信度/验证，再修架构，再扩功能。

**#7** Installed skill wrapper invariant: 已同步的 agent skill copy 必须包含 `bin/code-analyst`，并且该 wrapper 指向 `/Users/chihoyo/Project/CodeAnalyst` 这个 source checkout；installed skill 不是可编辑 source-of-truth。

**#8** Recommendation-only invariant: 本项目可以提出 review、重构、架构设计和优化路线，但默认不生成会直接修改目标项目的 patch；落地修改应在目标项目自己的上下文、测试和版本控制中进行。

**#9** Naming invariant: `CodeAnalyst` 是面向人的正式名字；`code-analyst` 是唯一 CLI；`code_analyst` 是 Python 包；源目录和 installed skill 都应使用 CodeAnalyst / code-analyst 命名。

## 4. Output Contract

`code-analyst pack TARGET` 默认生成：

```text
analyses/<YYYY-MM-DD>-<project-slug>/
  source.md
  overview.md
  architecture.md
  flows.md
  diagrams.md
  open-questions.md
  inventory.json
  flow_map.json
  script_check.json
  import_graph.json
  vibe_audit.json
  understanding_graph.json
```

`code-analyst review-pack TARGET` 在标准 pack 基础上继续生成：

```text
review.md
review_pack.json
```

`code-analyst visual-pack TARGET` 继续生成：

```text
site/
  index.html
  data.json
site_verification.json  # when --verify-site is used
```

## 5. Success Criteria

- `python3 -m code_analyst.cli doctor` 能检查本地运行环境。
- `code-analyst doctor` 能作为主 CLI 命令运行。
- `python3 -m code_analyst.cli inventory <target>` 能输出 JSON 或摘要。
- `python3 -m code_analyst.cli flow-map <target>` 能输出 CLI、服务、前端、skill 等入口/流程线索。
- `python3 -m code_analyst.cli script-check <target>` 能验证声明的脚本、bin、Python entrypoint 是否指向真实目标。
- `python3 -m code_analyst.cli import-graph <target>` 能输出 Python 和 JS/TS 的文件级 import 边。
- `python3 -m code_analyst.cli vibe-audit <target>` 能给出温和、可证据追踪的 vibe coding 风险。
- `python3 -m code_analyst.cli pack <target>` 能生成中央分析包。
- `python3 -m code_analyst.cli review-pack <target>` 能生成只读 review、重构方向和架构设计建议。
- `python3 -m code_analyst.cli review-pack --from-pack <pack-root>` 能不重扫目标、从已有 pack 重新生成 review 建议。
- `python3 -m code_analyst.cli visual-pack <target>` 能生成中央分析包和静态站点。
- `python3 -m code_analyst.cli verify-site <site>` 能验证静态站点的 HTML、`data.json`、内嵌 graph JSON 和浏览器数据启动脚本。
- skill 能清楚告诉后续 Codex：什么时候调用哪个 CLI 命令，什么时候只读，什么时候进入优化建议。
- `skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` 不应有结构错误；portable wrapper、metadata、update lifecycle 相关 warning 应被及时修复。
