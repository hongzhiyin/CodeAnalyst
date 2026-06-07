# Flows

## 快速学习流程

Trigger: 用户请求理解一个本地项目。

Path:
1. `cbu inventory` 扫描项目形态、manifest、入口候选、目录分布。
2. `cbu import-graph` 提取 Python/JS/TS 的静态 import 边，确认源码文件之间的实际依赖方向。
3. `cbu vibe-audit` 检查缺少验证、缺失脚本目标、半接线 UI、疑似未引用文件、重复实现。
4. `cbu pack` 生成 Markdown 和 JSON，供 agent 继续做证据化解释。
5. Agent 从入口文件追踪真实行为，并把不确定内容标为 Inference。

Side effects: 只写入中央分析包，不写目标项目。

Output: `overview.md`、`architecture.md`、`flows.md`、`diagrams.md`、`open-questions.md`、`inventory.json`、`import_graph.json`、`vibe_audit.json`、`understanding_graph.json`。
