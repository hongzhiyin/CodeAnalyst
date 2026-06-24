# DECISIONS - guided learning path V1

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Make the lesson primary and the graph secondary

**日期 / Date**: 2026-06-17

**上下文 / Context**:
`v0.6.2` 的交互式图谱能展示节点和关系，但用户反馈它仍然像把整套体系一次性摊开。目标体验应该更像读书或学数学：先从一个实际问题进入，再解释方法、步骤、原理和模块。

**选项 / Options**:
- A. 继续强化图谱：增加筛选、布局、更多节点说明。优点是延续当前实现；缺点是仍然不提供学习顺序。
- B. 让 guided lesson 成为第一屏，图谱退为索引/附录。优点是直接解决“先读哪里、为什么读”的问题；缺点是需要新增教程数据结构和页面布局。
- C. 直接引入 LLM 长文教程。优点是自然语言质量可能更好；缺点是输出不可复现，且会模糊证据边界。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户要的是“教材式理解”，不是更大的地图。
- 现有 graph、flow-map、script-check、import-graph 已能提供证据；缺的是叙事顺序。
- B 保持标准库和确定性 CLI 合同，同时给未来 LLM 增强留接口。

**风险 / Risks**:
- V1 的教程文案会偏模板化，需要用清晰结构弥补自然语言不足。
- 如果入口识别不准，案例路径可能只是线索而非真实运行证明；页面必须明确证据类型。

**对应代码 / 文档**:
- SPEC §1-§8
- ROADMAP Step 3
- `src/code_analyst/pack.py`
- `src/code_analyst/render_site.py`

## D-002 - Extend visual-pack instead of adding guide-pack now

**日期 / Date**: 2026-06-17

**上下文 / Context**:
用户最终想打开一个可交互页面学习项目。当前已有 `visual-pack`、`render-site`、`verify-site` 的端到端生成和验证链路。

**选项 / Options**:
- A. 新增 `guide-pack` 命令，专门生成教程页面。
- B. 扩展 `visual-pack`，让同一个站点同时拥有 guided lesson 和 graph 索引。
- C. 只生成 `guide.md`，不改站点。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户关心的是页面体验，不是新增命令。
- 复用 `visual-pack --verify-site` 可以保持验证闭环。
- 图谱仍有价值，但应该服务于教程步骤跳转，而不是抢占第一屏。

**风险 / Risks**:
- `render_site.py` 会承担更多 UI 复杂度。缓解：V1 用静态章节/步骤布局，不引入前端框架。
- 未来若教程输出变重，可能需要拆出 `guide-pack`；但现在先避免命令面过早膨胀。

**对应代码 / 文档**:
- SPEC §3.1
- ARCHITECTURE §3-§5
- `src/code_analyst/cli.py`
- `src/code_analyst/render_site.py`

## D-003 - Borrow the teaching interface, not the frontend stack

**日期 / Date**: 2026-06-17

**上下文 / Context**:
用户反馈首版 guide 页面仍然像旧 dashboard，只是在上方加了一点教材内容。重新调研 Understand Anything 后，关键启发是它先把普通图谱定义为“无讲解的毛线团”，再用 guided tour / LearnPanel / domain view 教用户理解代码。它的代码许可是 MIT，但实现栈是 Astro homepage + React/Vite dashboard。

**选项 / Options**:
- A. 直接复制 Understand Anything 的 Astro/React dashboard 结构。优点是更接近原项目；缺点是会引入新构建链和运行时，破坏当前标准库静态站点合同。
- B. 复制它的信息架构和视觉语言：reader/tour 优先、图谱降级为 reference index、步骤关联节点。优点是直接解决用户体验问题，同时保持 CodeAnalyst 现有 CLI 和静态 HTML 输出。
- C. 继续在旧 dashboard 上增加 guide 文案。优点是改动少；缺点是已经被用户验证不满足目标。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户要的是学习体验，不是某个前端框架。
- 当前 `render-site` 能生成单文件静态 HTML，适合复制信息架构而不是复制技术栈。
- B 保留 MIT 参考来源的可借鉴点，同时避免后续安装、构建和发布复杂度。

**风险 / Risks**:
- 标准库模板会变长，后续可能需要拆分静态资产或引入轻量前端构建。
- 如果只借样式不继续增强内容生成，页面仍可能显得模板化；本次同步给章节增加本章问题和原理字段。

**对应代码 / 文档**:
- ROADMAP Step 6
- `src/code_analyst/render_site.py`
- `src/code_analyst/pack.py`
