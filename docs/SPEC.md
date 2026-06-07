# Codebase Understanding SPEC

## 1. Goal

把 `codebase-understanding` 从一个仅靠 `SKILL.md` 编排的分析流程，升级为适合个人长期使用的快速学习框架：CLI 负责可重复、可验证的代码扫描和产物生成；skill 负责选择策略、解释证据、提出下一步优化路径。

## 2. Decision Table

| Topic | Choice | Why |
|---|---|---|
| 主体形态 | `skill + CLI` | skill 保存判断框架，CLI 固化重复、确定性的扫描/审计/建包/验证步骤。 |
| 默认写入位置 | `/Users/chihoyo/Project/CodebaseUnderstanding/analyses/` | 保持被分析项目干净，方便跨项目积累学习产物。 |
| 第一版 CLI 名称 | `cbu`，同时保留 `codebase-understanding` entry point | `cbu` 足够短，长命令便于脚本/文档自解释。 |
| 第一版核心命令 | `inventory` / `import-graph` / `vibe-audit` / `pack` / `visual-pack` / `render-site` / `doctor` | 覆盖快速盘点、静态依赖图、vibe coding 风险识别、分析包生成、静态可视化、环境自检。 |
| 运行依赖 | Python 标准库优先 | 避免在临时项目里先陷入依赖安装。 |
| 产物语言 | 跟随用户语言；中文请求生成中文文档 | 和原 skill 契约保持一致，减少二次整理。 |
| 外部最佳实践吸收 | 只吸收可操作原则，不复制长篇上下文 | 降低常驻指令膨胀带来的成本和误导。 |

## 3. Invariants

**#1 Read-only target invariant**: 除非用户明确要求，CLI 和 skill 不能写入被分析目标项目，只能读取目标并把产物写入中央分析库或用户指定输出目录。

**#2 Evidence invariant**: 每个关键结论都必须能追溯到文件、命令输出、脚本检测结果，或明确标记为 `Inference`。

**#3 Deterministic CLI invariant**: 可重复的文件枚举、manifest 检测、vibe audit、分析包目录创建、JSON 校验必须由 CLI 完成，而不是每次由模型自由发挥。

**#4 Small-context invariant**: skill 文案只保留决策流程和命令选择；长模板、检查清单、输出契约和示例放到 references 或 CLI 产物里。

**#5 Vibe-coded project invariant**: 对 AI 生成项目的分析必须显式检查 likely generated leftovers：未引用文件、半接线 UI、缺失脚本目标、框架配置/依赖不匹配、重复实现、缺少验证闭环。

**#6 Improvement guidance invariant**: 分析包不能只解释“现在是什么”，还要给出下一步优化路线：先修可信度/验证，再修架构，再扩功能。

## 4. Output Contract

`cbu pack TARGET` 默认生成：

```text
analyses/<YYYY-MM-DD>-<project-slug>/
  source.md
  overview.md
  architecture.md
  flows.md
  diagrams.md
  open-questions.md
  inventory.json
  import_graph.json
  vibe_audit.json
  understanding_graph.json
```

`cbu visual-pack TARGET` 继续生成：

```text
site/
  index.html
  data.json
```

## 5. Success Criteria

- `python3 -m codebase_understanding.cli doctor` 能检查本地运行环境。
- `python3 -m codebase_understanding.cli inventory <target>` 能输出 JSON 或摘要。
- `python3 -m codebase_understanding.cli import-graph <target>` 能输出 Python 和 JS/TS 的文件级 import 边。
- `python3 -m codebase_understanding.cli vibe-audit <target>` 能给出温和、可证据追踪的 vibe coding 风险。
- `python3 -m codebase_understanding.cli pack <target>` 能生成中央分析包。
- `python3 -m codebase_understanding.cli visual-pack <target>` 能生成中央分析包和静态站点。
- skill 能清楚告诉后续 Codex：什么时候调用哪个 CLI 命令，什么时候只读，什么时候进入优化建议。
