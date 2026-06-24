# ARCHITECTURE - guided learning path V1

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 返工中 |
| 创建原因 | 新增 guided learning 数据结构，并改变 `visual-pack` 站点第一屏信息架构 |
| 最后更新 | 2026-06-17 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/code_analyst/pack.py` | 扫描目标项目，写 Markdown/JSON pack，并生成 `understanding_graph.json`。 | 需要新增 guided learning 数据生成和文件输出。 |
| `src/code_analyst/render_site.py` | 从 `understanding_graph.json` 渲染静态 HTML；首版改动后仍保留大量旧 dashboard 结构。 | 需要把 reader lesson 放到第一屏，并把图谱、搜索、节点列表下移为 Reference Index。 |
| `src/code_analyst/review_pack.py` | 从 pack evidence 生成 review、模块 summary 和下一步建议。 | 可借鉴 `_part_summaries` 的目录职责、连接指标和 `next_read` 思路。 |
| `src/code_analyst/cli.py` | `visual-pack` 调用 `create_pack` 后调用 `render_site`，`verify-site` 校验输出。 | 不新增命令，复用现有 visual-pack 链路。 |
| `tests/test_pack.py` | 验证 pack 产物和 graph 字段。 | 需要增加 guided learning 字段断言。 |
| `tests/test_render_site.py` | 验证 rendered HTML/data 输出。 | 需要增加 quickstart/case/chapter UI 和旧 graph 兼容测试。 |

## 2. 当前调用链 / 数据流

```text
code-analyst visual-pack TARGET
  -> cli.cmd_visual_pack
  -> pack.create_pack
     -> inventory / flow_map / script_check / import_graph / vibe_audit
     -> pack._graph(...)
     -> write understanding_graph.json
  -> render_site.render_site(understanding_graph.json)
     -> render graph-first static HTML
  -> optional verify_site
```

当前 `understanding_graph.json` 包含 `nodes`、`edges`、`flows`、`evidence`、`questions`。`flows` 里已有“推荐阅读路线”，但它只是图谱页面中的一个列表，不是引导用户理解项目的主叙事。

## 3. 目标结构

```text
code-analyst visual-pack TARGET
  -> cli.cmd_visual_pack
  -> pack.create_pack
     -> evidence collectors
     -> pack._learning_guide(...)
        -> quickstart
        -> case_study
        -> chapters
        -> steps with node/path evidence
     -> write learning_guide.json
     -> write understanding_graph.json with guide field
  -> render_site.render_site(understanding_graph.json)
     -> render reader-first static HTML
     -> render selected module context after the lesson
     -> render graph/search/node list as Reference Index
  -> optional verify_site
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `src/code_analyst/pack.py` | 修改 | 新增 `_learning_guide(...)`，从 inventory/flow/script/import/audit/graph 生成确定性教程结构；章节可包含本章问题和原理。 | 不调用 LLM，不运行目标项目。 |
| `src/code_analyst/pack.py` | 修改 | 写出 `learning_guide.json`，并把同一对象放入 `understanding_graph.json["guide"]`。 | 不破坏旧 graph schema。 |
| `src/code_analyst/render_site.py` | 修改 | 读取可选 `data.guide`，第一屏渲染 reader mode hero、graph-vs-lesson 对比、case study、章节步骤和跳转按钮。 | 不引入构建工具或外部 JS/CSS。 |
| `src/code_analyst/render_site.py` | 修改 | 图谱、搜索、节点列表和详情保留，但作为教材后的 Reference Index 和上下文面板。 | 不要求旧 pack 重新生成。 |
| `tests/test_pack.py` | 修改 | 验证 guide JSON、steps 引用和 graph embedding。 | 不用 snapshot 锁死大段文案。 |
| `tests/test_render_site.py` | 修改 | 验证 reader-first HTML、Reference Index、交互按钮和旧 graph 兼容。 | 不要求像素级测试。 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| JSON file | `learning_guide.json` | 新增教程数据产物。 | 新文件；旧消费者可忽略。 |
| Graph field | `understanding_graph.json.guide` | 新增同一教程对象，供 `render-site` 单文件消费。 | 可选字段；缺失时降级。 |
| Site data | `site/data.json.guide` | 透传教程对象。 | 可选字段；缺失时旧 UI 可用。 |
| HTML | `site/index.html` | 第一屏改为 reader-first；图谱、搜索和节点列表下移为 Reference Index。 | 不改变静态打开方式。 |

## 6. 测试与观测点

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m code_analyst.cli visual-pack . --out <tmp> --verify-site`
- Browser smoke：打开当前项目 demo，确认第一屏是 reader mode / quickstart / case，旧 sidebar 和 SVG graph 不在第一屏主导位置，点击教程步骤能选中相关节点。
- Backward compatibility：用没有 `guide` 字段的 fixture 渲染，不报错。
