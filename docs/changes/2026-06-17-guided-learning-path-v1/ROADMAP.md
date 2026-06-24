# ROADMAP - guided learning path V1

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 返工中  
**当前 Step / Current Step**: Step 6 - Understand Anything 风格返工  
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本需求新增 guided learning 数据结构，并改变 visual-pack 站点的信息架构。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案：用户回复“继续下一步”

### Completion Gate

- [ ] 所有实施任务完成或有明确跳过理由
- [ ] 验收标准逐条验证
- [ ] 文档与最终实现一致
- [ ] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | 当前 graph 数据 | `_graph` 已给节点加 `meaning`、`next_read`、`signals`、`metrics`，也有“推荐阅读路线”和“快速学习流程”。 | `src/code_analyst/pack.py:166-453` | 素材已存在，但结构仍是 graph-first，不是 lesson-first。 |
| R-2 | 当前 pack Markdown | `overview.md` 有“最短心智模型”和“建议阅读顺序”，但内容是静态文档，不进入页面第一屏交互体验。 | `src/code_analyst/pack.py:495-520` | V1 应把这类内容结构化进 site data。 |
| R-3 | 当前页面结构 | HTML 第一屏是 sidebar 搜索、统计、node list、SVG graph、selected module、flows/evidence/questions。 | `src/code_analyst/render_site.py:520-555` | 需要重排信息架构，让 quickstart/case 先出现。 |
| R-4 | 当前页面搜索/详情 | 搜索匹配 node label/kind/path/summary/meaning/next_read/signals/metrics；详情只解释选中节点。 | `src/code_analyst/render_site.py:628-644`, `src/code_analyst/render_site.py:741-784` | 它回答“这个节点是什么”，不回答“我该如何学习这个项目”。 |
| R-5 | review pack 可复用素材 | `_part_summaries` 已能给顶层目录责任、相关 flow、入出边和 `next_read`。 | `src/code_analyst/review_pack.py:87-125` | 可借鉴其目录分层思路，但 lesson 数据应由 pack 生成。 |
| R-6 | CLI 链路 | `visual-pack` 直接 `create_pack` 后 `render_site`；`verify-site` 已能做结构 readiness check。 | `src/code_analyst/cli.py:132-150`, `src/code_analyst/cli.py:310-317` | 不需要新增命令，扩展现有 visual-pack 即可。 |
| R-7 | Understand Anything 页面叙事 | 官网把问题定义为普通 code graph 只给 hairball，而产品承诺是 teach you the codebase。 | `https://understand-anything.com/` Hero/Problem sections | CodeAnalyst 页面也应先解释“为什么先看全图没用”，再给学习路径。 |
| R-8 | Understand Anything dashboard 结构 | dashboard 有 `LearnPanel`，以 tour steps、current step、related nodes 组织学习，而不是只展示节点列表。 | `understand-anything-plugin/packages/dashboard/src/components/LearnPanel.tsx` | 当前站点应把 case/chapter 作为主阅读区，节点详情只作为 step 的相关模块。 |
| R-9 | Understand Anything tour generator | tour generator 的启发式路径会先找 entry points，再按 layer/拓扑组织 steps，最后补 concept nodes。 | `understand-anything-plugin/packages/core/src/analyzer/tour-generator.ts` | CodeAnalyst 的 deterministic guide 应继续强化 entrypoint-first 和 evidence-first。 |
| R-10 | 直接照搬边界 | Understand Anything 是 MIT，许可允许复用，但主页是 Astro、dashboard 是 React/Vite。 | `LICENSE`, `homepage/`, `understand-anything-plugin/packages/dashboard/` | 本次借信息架构和视觉语言，不直接引入前端构建栈。 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |
| 6 | Understand Anything 风格返工 | 进行中 |

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

**Goal**: 把“像读书一样学习项目”转成可验收行为。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. V1 目标是 guided lesson first，而不是更复杂的 graph。

---

## Step 2 - 调研既有实现

**Goal**: 找出最小改动路径。

**Tasks**:
- [x] 读取 `pack._graph` 和 Markdown 输出
- [x] 读取 `render_site.py` 页面结构和详情逻辑
- [x] 读取 `review_pack._part_summaries`
- [x] 读取 CLI 和测试触点

**Acceptance**:
1. 现有实现触点和新增 guided learning 数据方案清楚。

---

## Step 3 - 形成并确认方案

**Goal**: 确认 V1 信息架构和实现边界。

**Tasks**:
- [x] 记录 D-001：lesson primary, graph secondary。
- [x] 记录 D-002：扩展 visual-pack，不新增 guide-pack。
- [x] 写清 implementation steps。
- [x] 用户确认实现方案：用户回复“继续下一步”。

**Acceptance**:
1. 用户确认后再改 production code。

## 4. 实施计划

1. 在 `pack.py` 新增 `_learning_guide(...)`：
   - 从 `flow_map` 选择一个实际案例路径，优先 CLI/bin/script entrypoint。
   - 生成 `quickstart`、`case_study`、`chapters`、`steps`。
   - 每个 step 引用 `node` 或 `path`，并标记 evidence/inference。
2. `create_pack` 写出 `learning_guide.json`，并把 guide 嵌入 `understanding_graph.json["guide"]`。
3. `render_site.py` 改为 guide-first：
   - 第一屏：quickstart + case study + 章节目录。
   - 每个 step 有“查看相关模块”按钮，点击后选中 graph node。
   - graph/search/details 保留在后续区域。
   - 无 guide 字段时降级到旧图谱布局。
4. 更新测试：
   - `tests/test_pack.py` 检查 guide 产物和引用。
   - `tests/test_render_site.py` 检查 quickstart/case/chapter HTML 和旧数据兼容。
5. 验证当前项目 demo：
   - `visual-pack . --out <tmp> --verify-site`
   - 浏览器打开站点，确认第一屏从 `visual-pack` 案例开始讲入口、步骤和模块。

## Step 4 - 实施代码与测试

**Goal**: 让 `visual-pack` 输出 guide 数据，并让站点第一屏变成教材式入口。

**Tasks**:
- [x] 在 `pack.py` 新增 `_learning_guide(...)`。
- [x] 写出 `learning_guide.json` 并嵌入 `understanding_graph.json["guide"]`。
- [x] 在 `render_site.py` 渲染 quickstart、case study、chapter route 和 step jump buttons。
- [x] 保持无 guide 旧 graph 兼容。
- [x] 更新 `tests/test_pack.py` 和 `tests/test_render_site.py`。

**Acceptance**:
1. 当前项目 demo 第一屏显示 quickstart/case，而不是只显示完整图谱。
2. 教程步骤能跳转到相关 graph node 详情。

## Step 5 - 验证与收尾

**Goal**: 确认自动化测试、真实 visual-pack、浏览器交互和 docs audit 全部通过。

**Tasks**:
- [x] 运行全量单元测试。
- [x] 运行当前项目 `visual-pack --verify-site`。
- [x] 用 in-app Browser 打开 demo 并点击教程步骤。
- [x] 运行 `docdev audit`。

**Acceptance**:
1. 验证记录覆盖 SPEC §8。

## Step 6 - Understand Anything 风格返工

**Goal**: 把首版 guide-first 页面进一步改成 reader-first 教材页面，避免旧 dashboard 结构继续占据主体验。

**触发 / Trigger**:
用户反馈首版页面“还是不行”，因为它保留了原本大部分结构，真正教材部分太少，需要好好参考 Understand Anything 的页面样式和风格。

**Tasks**:
- [x] 重新调研 Understand Anything 官网、dashboard LearnPanel、tour generator 和 license。
- [x] 记录 D-003：借鉴 reader/tour 信息架构，不直接引入 Astro/React 实现。
- [x] 改造 `render_site.py`：第一屏改为 reader mode hero + graph-vs-lesson 对比 + 学习路径。
- [x] 将搜索、节点列表和 SVG 图谱下移到 Reference Index。
- [x] 扩充 `learning_guide.json` 章节：每章增加本章问题和原理。
- [ ] 更新测试和文档状态。
- [ ] 重新跑单测、真实 visual-pack、Browser smoke 和 docdev audit。

**Acceptance**:
1. Demo 第一屏不再展示旧 sidebar / node list / SVG graph。
2. 页面能像教材一样从一个真实问题进入，按章节读，每步仍可跳到相关模块。
3. Reference Index 保留搜索、图谱和节点详情，作为后查工具。

## 5. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 18 tests passed |
| SPEC-2 | `PYTHONPATH=src python3 -m code_analyst.cli visual-pack . --out analyses/2026-06-17-codeanalyst-guided-learning-demo --verify-site` | 通过 | Ready: yes; 37 nodes; 46 edges; 6 ok checks |
| SPEC-3 | Browser 打开 `http://127.0.0.1:8766/index.html` | 通过 | 第一屏 guide 可见；点击 `pack.py` 步骤后跳转到模块详情 |
| SPEC-4 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/CodeAnalyst --write-report` | 通过 | No findings |

## 6. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | V1 仍是确定性启发式，不是深度 AI 教材 | 文字可能没有人工教程自然 | 先把结构和证据链做好，后续可加可选 LLM summary。 |
| F-2 | 静态分析不能证明真实运行时调用链 | 案例路径可能被误读为 runtime proof | 页面明确区分 entrypoint hint、static import 和 inference。 |
| F-3 | 站点复杂度增加 | `render_site.py` 可能变长 | V1 只做静态章节/步骤，不引入框架；后续再考虑拆前端。 |
