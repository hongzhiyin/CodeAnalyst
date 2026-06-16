# DECISIONS - interactive dashboard V1

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Upgrade the static visual-pack dashboard before adding heavy dependencies

**日期 / Date**: 2026-06-16

**上下文 / Context**:

用户最终希望 CodeAnalyst 生成一个可交互页面，用于浏览被分析项目的代码结构和功能含义。当前项目已有 `understanding_graph.json` 与静态 `render-site`，但还没有足够的节点功能解释。

**选项 / Options**:

- A. 在现有 Python standard-library static site 上升级 graph schema 和详情面板。
- B. 直接引入 React/Vite dashboard。
- C. 先引入 Tree-sitter，再重做 graph 和页面。

**选择 / Chosen**: A。

**理由 / Rationale**:

- A 最符合 CodeAnalyst 现有 read-only、central analyses、standard-library-first、native install 简洁性的项目合同。
- 现有 `visual-pack` 已有数据与页面管线，V1 的用户收益主要来自更好的解释字段和详情体验，而不是换技术栈。
- B 和 C 都可能是后续方向，但会扩大安装、打包、测试和发布成本，不适合作为第一步。

**风险 / Risks**:

- 启发式功能含义不如 LLM/Tree-sitter 深，但 V1 会保留证据、路径和关系，避免过度断言。
- 静态 SVG 布局仍可能不如专业图谱库，后续可在数据合同稳定后再升级前端。

**对应代码 / 文档**:

- SPEC §5-8
- ROADMAP Step 4
- ARCHITECTURE §2-4
- `src/code_analyst/pack.py`
- `src/code_analyst/render_site.py`
- `tests/test_pack.py`
- `tests/test_render_site.py`
