# Flows

## 快速学习流程

Trigger: 用户请求理解一个本地项目。

Path:
1. `code-analyst inventory` 扫描项目形态、manifest、入口候选、目录分布。
2. `code-analyst flow-map` 按项目类型提取 CLI、服务、前端、skill 等入口线索。
3. `code-analyst script-check` 检查声明的脚本、bin、Python entrypoint 是否指向真实目标。
4. `code-analyst import-graph` 提取 Python/JS/TS 的静态 import 边，确认源码文件之间的实际依赖方向。
5. `code-analyst vibe-audit` 检查缺少验证、缺失脚本目标、半接线 UI、疑似未引用文件、重复实现。
6. `code-analyst pack` 生成 Markdown 和 JSON，供 agent 继续做证据化解释。
7. Agent 从入口文件追踪真实行为，并把不确定内容标为 Inference。

Side effects: 只写入中央分析包，不写目标项目。

Output: `overview.md`、`architecture.md`、`flows.md`、`diagrams.md`、`open-questions.md`、`inventory.json`、`flow_map.json`、`script_check.json`、`import_graph.json`、`vibe_audit.json`、`understanding_graph.json`。
