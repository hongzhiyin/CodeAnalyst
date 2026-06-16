# SPEC - interactive dashboard V1

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 实现中 |
| 需求来源 | 用户希望 CodeAnalyst 最终有一个可交互页面，用来浏览被分析项目的代码结构及其功能含义 |
| 工作包目录 | `docs/changes/2026-06-16-interactive-dashboard-v1/` |
| 最后更新 | 2026-06-16 |

## 1. 一句话目标

让 `code-analyst visual-pack TARGET` 生成的静态页面不仅能展示关系图，还能让用户点击、搜索并理解被分析项目中模块/文件/入口的功能含义、连接关系和推荐阅读顺序。

## 2. 背景与问题

- 当前行为：`visual-pack` 已生成 `understanding_graph.json` 和 `site/index.html`，页面支持节点列表、搜索、SVG 关系图、节点详情、流程、证据和开放问题。
- 问题：现有节点摘要偏“入口/目录/证据”层，文件节点多为“由 import graph 发现的源码文件”，还不能稳定回答“这个文件/目录的功能含义是什么、为什么要看它、接下来读哪里”。
- 期望收益：用户打开页面后可以像浏览项目地图一样理解结构、功能、入口、依赖和风险，而不是只看到技术关系图。

## 3. 范围

### 3.1 本次要做

- 扩展 `understanding_graph.json` 的节点语义字段，至少覆盖功能含义、阅读建议、连接指标和证据信号。
- 让 `pack` 生成更有解释力的目录、入口、配置、源码文件、检查节点和 flow 节点。
- 升级静态页面详情面板，展示选中节点的功能含义、路径、分组、入边/出边、关键证据信号和下一步阅读建议。
- 保持页面无需构建步骤、无需联网、无需前端框架。
- 为新 graph 字段和页面渲染增加回归测试。

### 3.2 本次不做

- 不引入 React/Vite、Tree-sitter、embedding search 或 LLM API。
- 不把分析产物默认写进被分析目标项目。
- 不实现完整 semantic chat、多人协作 dashboard 或 post-commit auto-update。
- 不改变 `visual-pack` 的命令名称和默认输出位置。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户运行 `code-analyst visual-pack TARGET --verify-site` | 生成中央分析包和可打开的 `site/index.html` |
| S2 | 用户在页面搜索文件、目录或入口 | 列表筛选，点击结果后详情面板显示功能含义和连接关系 |
| S3 | 用户选择一个源码文件节点 | 页面说明它可能负责什么、从哪里被引用、引用了谁、下一步应该读什么 |
| S4 | 用户选择一个目录或 flow 节点 | 页面说明该结构区域/流程线索的作用和相关证据 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `understanding_graph.json` 节点可包含 `meaning`、`next_read`、`signals`、`metrics` 等解释字段 | `tests/test_pack.py` 断言生成字段 | 草稿 |
| R2 | 页面详情面板必须展示功能含义、下一步阅读和证据信号 | `tests/test_render_site.py` 断言 HTML 包含对应容器/文案 | 草稿 |
| R3 | 页面仍通过结构验证和 `verify-site` | `tests/test_verify_site.py` 和 `verify-site` | 草稿 |
| R4 | 目标项目保持只读，输出仍在中央 analyses 或用户指定 `--out` | `source.md` 和 existing invariant | 草稿 |

## 6. 约束与不变式

1. **#1**: 默认不写入被分析目标项目；所有新增页面和 JSON 产物仍写入 pack 输出目录。
2. **#2**: 功能含义必须来自确定性扫描证据或清楚标记为推断；不能伪装成运行时证明。
3. **#3**: V1 必须保持 Python standard-library runtime，不新增安装依赖。
4. **#4**: 新页面必须优雅处理旧 graph JSON；旧节点没有新增字段时仍能渲染。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧 `understanding_graph.json` | 正常渲染，缺失解释字段时显示已有 summary / path / relations |
| `visual-pack` 无 `--verify-site` | 仍生成 `site/index.html` 和 `site/data.json` |
| `render-site` 单独使用 | 支持扩展字段，但不要求调用者提供 |
| 目标项目 | 保持只读 |

## 8. 验收标准

1. `PYTHONPATH=src python3 -m unittest discover -s tests` 通过。
2. `PYTHONPATH=src python3 -m code_analyst.cli visual-pack . --out /tmp/... --verify-site` 生成 site，`verify-site` 返回 ready。
3. 生成的 `site/index.html` 支持搜索、点击节点，并在详情中显示功能含义、连接关系、证据信号和阅读建议。
4. `docdev audit /Users/chihoyo/Project/CodeAnalyst --write-report` 无 findings。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否要引入真正函数/类级节点？ | V1 不做；先把文件/目录级语义做好 | 否 |
| Q2 | 是否要做 React/Vite dashboard？ | V1 不做；静态页面足够验证交互模型 | 否 |
| Q3 | 是否要做语义搜索或问答？ | V1 不做；后续可基于 graph/review_pack 增加 | 否 |
