# SPEC - guided learning path V1

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 返工中 |
| 需求来源 | 用户反馈：当前交互式总览能看到结构，但不能像阅读教材一样理解入口、工作原理和模块作用；首版 guide 仍保留太多旧 dashboard 结构，需要更贴近 Understand Anything 的教学式页面风格 |
| 工作包目录 | `docs/changes/2026-06-17-guided-learning-path-v1/` |
| 最后更新 | 2026-06-17 |

## 1. 一句话目标

让 `visual-pack` 生成的页面从“项目地图”升级为“项目教材”：用户打开页面后先看到 quickstart、一个实际案例和章节式讲解，再按由浅入深的路径理解入口、运行路径、核心模块和后续深读方向；完整图谱只作为后续参考索引。

## 2. 背景与问题

- 当前行为：`visual-pack` 首版 guide 已经有 quickstart/case/chapter，但页面仍保留大量旧 dashboard 信息架构，搜索、节点列表、SVG 图谱和详情仍然像主体验。
- 问题：总览式图谱把体系一次性铺开，适合作为索引，但不负责教学顺序；即使加了 guide，如果旧 dashboard 仍然主导页面，用户仍然不知道“先读哪里、为什么读、这个项目怎样从一个实际问题运转起来”。
- 期望收益：页面像一本技术书的第一章：先用一个具体问题建立动机，再讲方法步骤和背后的原理，最后把模块逐步拆开。

## 3. 范围

### 3.1 本次要做

- 为 `pack` / `visual-pack` 产物增加 guided learning 数据：quickstart、实际问题、学习目标、章节、步骤、相关证据和模块引用。
- 让静态站点第一屏优先展示 guided learning，而不是优先展示完整图谱。
- 参考 Understand Anything 的体验取向：先讲“为什么普通 graph 不够”，再给 reader-first 的学习路径、案例和章节；图谱、搜索、节点列表下移为 Reference Index。
- 为当前 CodeAnalyst 项目生成一个可验证案例，例如“用户运行 `code-analyst visual-pack TARGET` 时，系统如何从 CLI 入口走到分析包、图谱和静态站点”。
- 保留图谱、搜索、节点详情作为学习过程中的索引和深读工具。
- 保持标准库实现，不增加前端构建工具或运行时依赖。

### 3.2 本次不做

- 不引入 LLM 自动生成长篇教程；V1 使用确定性启发式和已有证据，避免不可复现输出。
- 不实现完整 runtime call graph；继续把 import graph 标记为静态依赖证据。
- 不运行、构建或修改被分析目标项目。
- 不把每个文件都写成长文；V1 聚焦入口路径、核心模块和读者最先需要的心智模型。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户打开 `visual-pack` 生成站点 | 第一屏看到 reader mode：这个项目解决什么问题、为什么不能先看全图、建议先理解哪个实际案例、预计阅读顺序是什么。 |
| S2 | 用户选择“从实际问题开始” | 页面展示一个案例路径：触发条件、入口文件、方法步骤、每步依赖的模块、哪些地方是证据、哪些地方是 inference。 |
| S3 | 用户读完 quickstart 后继续深入 | 页面按章节拆解模块：入口层、证据采集层、产物生成层、可视化层、验证/发布层；每章只给下一步需要的信息。 |
| S4 | 用户想查某个模块细节 | 图谱、搜索和节点详情仍可用，并能从教程步骤跳转到相关节点。 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `pack` 产物必须包含 guided learning 数据，至少有 `quickstart`、`case_study`、`chapters`、`steps`、`evidence` 字段。 | 单元测试读取 JSON 产物并断言字段存在。 | 通过 |
| R2 | `visual-pack` 站点第一屏必须展示 reader-first quickstart、实际案例和章节，而不是保留旧 dashboard/sidebar/graph 为主视图。 | 浏览器/HTML 测试断言页面含 reader-grid、case/chapter UI 和 Reference Index；人工检查第一屏。 | 返工中 |
| R3 | 每个教程步骤必须能引用一个已有 graph node 或证据文件路径，不能成为无法追溯的散文。 | 单元测试校验 referenced node/path 存在；人工检查当前项目 demo。 | 通过 |
| R4 | 当前图谱能力必须保持兼容：搜索、点击节点、关系跳转、site verification 仍可用。 | 现有 `tests/test_render_site.py`、`tests/test_verify_site.py` 和 browser smoke。 | 通过 |
| R5 | 旧 `understanding_graph.json` 没有 guided learning 字段时，`render-site` 仍能降级显示旧图谱。 | 添加 backward compatibility fixture。 | 通过 |

## 6. 约束与不变式

1. **#1**: 不破坏根 SPEC #1：默认不得写入被分析目标项目。
2. **#2**: 不破坏根 SPEC #2：教程中的关键结论必须能追溯到文件、命令输出、脚本检测结果，或明确标记为 `Inference`。
3. **#3**: 不破坏根 SPEC #3：guided learning 的可重复数据结构由 CLI 生成，而不是每次由模型自由发挥。
4. **#4**: 教程必须渐进披露，不能把所有模块一次性摊开作为主要路径。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧 graph 没有 `guide` / guided learning 字段 | `render-site` 降级到当前图谱优先布局，不报错。 |
| 非 CLI 项目缺少明确 command entrypoint | V1 生成通用学习路径：从 manifest、README/入口候选、flow-map 和 import graph 开始。 |
| 大项目节点很多 | 教程只选入口路径和核心目录，完整节点图作为索引保留。 |
| 多语言或未知项目类型 | 产物语言跟随现有 locale；未知类型用项目类型、manifest、flow hints 生成保守章节。 |

## 8. 验收标准

1. 以 CodeAnalyst 自身为目标生成 demo 站点时，第一屏能看出“如何从 `visual-pack` 命令理解项目工作原理”的 reader mode、quickstart 和案例路径，且旧图谱不再是第一屏主角。
2. 用户可以按章节从入口、工作流、核心模块到验证/发布逐步阅读，而不是先面对完整体系图。
3. `PYTHONPATH=src python3 -m unittest discover -s tests` 通过。
4. `PYTHONPATH=src python3 -m code_analyst.cli visual-pack . --out <tmp> --verify-site` 通过。
5. 根 SPEC #1、#2、#3、#6 仍成立。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | V1 是否需要新增独立命令 `guide-pack`？ | 不需要。先让 `visual-pack` 的页面变成教材式入口，减少命令面膨胀。 | 否 |
| Q2 | V1 是否需要 AI 生成更自然的长文？ | 暂不需要。先把可复现的教学结构做好；后续可把 LLM 摘要作为可选增强。 | 否 |
| Q3 | 案例路径是否必须针对每个项目都完全准确？ | V1 必须证据化、保守表达；不能静态证明的部分标记为入口线索或 Inference。 | 否 |
