# Architecture

## 结构事实

- Root: `/Users/chihoyo/Project/CodebaseUnderstanding`
- Files scanned: 24
- Project types: Codex skill, Python project

## 顶层分布

- `AGENTS.md (1)`
- `docs/ (4)`
- `index.md (1)`
- `pyproject.toml (1)`
- `scripts/ (3)`
- `skill/ (2)`
- `src/ (7)`
- `tests/ (5)`

## 依赖方向初判

`import_graph.json` 静态提取到 77 条 import 边，其中 16 条为内部文件依赖。

Inference: 当前 import graph 是文件级静态依赖图，不等同于运行时调用链；动态 import、框架路由、依赖注入和字符串拼接路径仍需要人工或运行时验证。

## 外部工具与副作用

未运行安装、构建、测试或网络命令。目标项目保持只读。
