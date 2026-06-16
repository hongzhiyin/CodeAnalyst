# ROADMAP - interactive dashboard V1

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 5 - 验证与收尾完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 已补 `ARCHITECTURE.md`，因为本次会改变 graph schema、rendered site 数据展示和 visual-pack 用户可见页面结构。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案：用户回复“继续下一步吧”

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | 当前 graph 生成 | `pack._graph` 已生成 nodes、edges、flows、evidence、questions，但许多源码文件节点摘要只是“由 import graph 发现的源码文件”。 | `src/code_analyst/pack.py` | V1 应增强 graph 数据，而不是另建 dashboard 数据源。 |
| R-2 | 当前页面交互 | `render_site.py` 已支持搜索、节点列表、SVG 图、点击选中、详情、流程、证据、问题。 | `src/code_analyst/render_site.py` | V1 可在现有静态页面上升级详情和解释字段，不需要前端框架。 |
| R-3 | 当前 review 信息 | `review_pack._part_summaries` 已有目录职责、连接指标、下一步阅读建议的启发式逻辑。 | `src/code_analyst/review_pack.py` | 这类信息应前移到 `understanding_graph.json`，供页面直接消费。 |
| R-4 | 现有验证 | `tests/test_render_site.py`、`tests/test_verify_site.py` 验证 HTML/data 写入、embedded JSON 和 site readiness。 | `tests/test_render_site.py`, `tests/test_verify_site.py` | 新 UI 必须保持旧 graph 渲染兼容，并扩大测试断言。 |
| R-5 | 外部参照 | Understand Anything 的可借鉴点是 guided tours、点击节点解释、搜索和 diff/domain 后续交互，不适合直接搬整套 TypeScript dashboard。 | `docs/changes/2026-06-16-understand-anything-comparison/` | V1 借体验模型，不借重依赖。 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS / ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把“可交互页面浏览结构和功能含义”转成 V1 可验收行为。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. V1 不引入重依赖，聚焦现有 graph + static site。

---

## Step 2 - 调研既有实现

**Goal**: 找出最小改动路径。

**Tasks**:
- [x] 读取 `pack._graph`
- [x] 读取 `render_site.py`
- [x] 读取 `review_pack._part_summaries`
- [x] 读取 site 相关测试

**Acceptance**:
1. 现有实现触点和新增字段方案清楚。

---

## Step 3 - 形成并确认方案

**Goal**: 选定 V1 技术边界。

**Tasks**:
- [x] 记录 DECISIONS D-001。
- [x] 明确不引入 React/Tree-sitter/embedding。
- [x] 明确用户已批准继续实现。

**Acceptance**:
1. 可直接进入 production code 修改。

---

## Step 4 - 实施代码与测试

**Goal**: 升级 graph 数据和静态页面详情体验。

**Tasks**:
- [x] 扩展 graph 节点解释字段和阅读路线。
- [x] 升级页面详情面板展示功能含义、证据信号、阅读建议和可点击关系。
- [x] 增加或更新测试。

**Acceptance**:
1. 生成站点能表达被分析项目代码结构和功能含义。

---

## Step 5 - 验证与收尾

**Goal**: 确认新 dashboard 在自动化测试、真实 visual-pack 输出和浏览器交互中可用。

**Tasks**:
- [x] 运行全量单元测试。
- [x] 运行 `visual-pack --verify-site` smoke。
- [x] 用 in-app Browser 通过本地 HTTP 服务器打开生成页面，验证搜索、点击和详情面板。
- [x] 运行 `docdev audit`。

**Acceptance**:
1. 自动化和浏览器验证均通过，docs audit 无 findings。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 17 tests passed |
| SPEC-2 | `PYTHONPATH=src python3 -m code_analyst.cli visual-pack . --out /private/tmp/codeanalyst-dashboard-v1-smoke --verify-site` | 通过 | Ready: yes; 37 nodes; 46 edges; 6 ok checks |
| SPEC-3 | in-app Browser via `http://127.0.0.1:8765/site/index.html` | 通过 | 搜索 `render_site` 后列表过滤；点击结果后详情显示功能含义、连接关系、证据信号和指标 |
| SPEC-4 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/CodeAnalyst --write-report` | 通过 | No findings |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | V1 功能含义仍是启发式，不是 LLM 深读 | 解释可能偏粗 | 用 evidence/inference 语气表达，并保留 path/relations |
| F-2 | 文件级 import graph 不等于运行时调用图 | 用户可能误读边含义 | 页面和证据中继续标记 static dependency |
| F-3 | 大项目节点很多 | 页面可能拥挤 | 保留搜索和分组，后续再做 collapse/filter |
