# DECISIONS - Native install release and public GitHub maintenance

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Add native GitHub Releases install alongside source checkout install

**日期 / Date**: 2026-06-15

**上下文 / Context**:
CodeAnalyst 原 source-checkout install/update 已经健康：doctor 通过、installed skill wrappers 存在。缺口不是本机能不能用，而是普通用户或另一台机器是否能不 clone 源码、不设置 `CODE_ANALYST_PROJECT_DIR`，直接安装并更新稳定 release。用户随后确认把现有 GitHub repo 转 public，并移除旧本地全局 wrapper 安装方式。

**选项 / Options**:
- A. 继续只支持 source checkout wrapper - 维护最简单，但跨机器安装更新仍依赖 clone 源码和本机路径。
- B. 直接发布到 PyPI/npm - 标准包管理体验更强，但会把问题提前变成包生态、凭据、依赖和发布规范问题。
- C. 增加 public GitHub Releases/native installer，同时保留 source checkout path - 支持一条命令安装/更新，又不污染系统 Python，也保留开发者本地 workflow。

**选择 / Chosen**: C

**理由 / Rationale**:
- 符合根 SPEC 的 skill+CLI 分层：deterministic install/update/package/sync 由 scripts/CLI 执行，skill 只负责判断何时使用。
- 避免 PEP 668 / system Python mutation；native launcher 通过 release-local `PYTHONPATH` 运行。
- GitHub Releases 能同时承载 manifest、checksum、tarball 和 installer，足够支撑当前个人工具的版本维护。
- 现有 repo `hongzhiyin/CodeAnalyst` 已转为 public，可直接成为 release/update 维护入口；不必先引入 npm/PyPI。
- Source checkout 安装改用 `.venv/bin/code-analyst`，与 skill-cli-kit 的开发安装模式一致，也避免继续写 `/opt/homebrew/bin`。

**风险 / Risks**:
- GitHub Release 尚未发布；公开 curl installer 需要 release assets 发布后才能使用。
- native launcher 和 source wrapper 可能同时存在，PATH 顺序会影响实际运行的 `code-analyst`。doctor 必须显示当前 root。
- release packaging 漏文件会导致 CLI、skill 和 docs 版本漂移；package smoke 必须覆盖 release 内容和 installed skill sync。
- 公开仓库会暴露 repo 历史和内容；转 public 前需要用户确认没有不应公开的文件。

**对应代码 / 文档**:
- SPEC §1-§9
- ROADMAP Step 3
- ARCHITECTURE §3-§6
- `scripts/install_cli.sh`
- `scripts/update_cli.sh`
- `scripts/sync_skill.sh`
- `src/code_analyst/cli.py`
