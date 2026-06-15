# ROADMAP - Native install release and public GitHub maintenance

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已实施，本地验证通过
**当前 Step / Current Step**: Step 5 - 验证与收尾
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本需求会新增 release packaging、remote installer、native launcher/update、skill sync source 切换和 GitHub release flow。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | 本机 CLI 健康度 | `PYTHONPATH=src python3 -m code_analyst.cli doctor` 通过；报告 `code-analyst 0.6.1`、PATH wrapper、两个 installed skill-local wrappers 和 analysis library 均存在。 | `src/code_analyst/cli.py`, command output 2026-06-15 | 现有 source-checkout install 健康，不是修复型需求。 |
| R-2 | skill-cli-kit portability | `skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` 返回 0 errors / 1 warning：缺少 `code-analyst sync-skill`。 | `src/code_analyst/cli.py`, audit output 2026-06-15 | 实现 native 前应补 business CLI sync wrapper，避免 portability warning 延续到 release。 |
| R-3 | source wrapper 结构 | `scripts/install_cli.sh` 写 `/opt/homebrew/bin/code-analyst`，wrapper 设置 `CODE_ANALYST_PROJECT_DIR` 和 `PYTHONPATH` 指向源码 checkout。 | `scripts/install_cli.sh` | 当前适合本机开发，不适合普通用户远程安装后脱离源码运行。 |
| R-4 | update lifecycle | `scripts/update_cli.sh` 只做 source lifecycle：install wrapper、跑 unittest、sync skill、check install。 | `scripts/update_cli.sh` | 需要新增 native `code-analyst update`，不要复用 source update 概念。 |
| R-5 | release assets 缺口 | repo 中没有 `install_remote.sh`、`package_release.sh`、release manifest、checksum 或 native release layout。 | `rg install_remote/package_release/release/manifest` 2026-06-15 | 若目标是跨机器安装更新，需要新增 release 分发层。 |
| R-6 | GitHub remote | `origin` 已是 `https://github.com/hongzhiyin/CodeAnalyst.git`；`gh repo view` 显示 `visibility=PRIVATE`。 | `git remote -v`; `gh repo view hongzhiyin/CodeAnalyst --json visibility` | 不需要从零建仓库；需要确认是否转 public，或另建 public release repo。 |
| R-7 | tests | `PYTHONPATH=src python3 -m unittest discover -s tests` 通过 15 tests。 | tests command output 2026-06-15 | 可以在绿色基线上开始 release-layer implementation。 |
| R-8 | Public repo | `gh repo edit hongzhiyin/CodeAnalyst --visibility public --accept-visibility-change-consequences` 成功；`gh repo view` 显示 PUBLIC。 | GitHub CLI output 2026-06-15 | 现有仓库已可承载 public release/update 维护。 |
| R-9 | Source wrapper migration | `./scripts/install_cli.sh` 移除旧 `/opt/homebrew/bin/code-analyst` 生成 wrapper，并写入 `.venv/bin/code-analyst`。 | `scripts/install_cli.sh`, command output 2026-06-15 | 本机 source install 已改为 skill-cli-kit 风格项目内 wrapper。 |
| R-10 | Native local install | `./scripts/install_remote.sh --release-base-url file:///Users/chihoyo/Project/CodeAnalyst/dist/releases --targets codex,agents --sync-skill` 成功安装 0.6.1 到 `~/.local/share/code-analyst/releases/0.6.1`。 | `scripts/install_remote.sh`, `~/.local/bin/code-analyst doctor` output 2026-06-15 | 本地 native install/update 路径通过。 |

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

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把粗略需求转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. 用户确认 SPEC 的目标、范围和非目标。

---

## Step 2 - 调研既有实现

**Goal**: 判断当前项目是否已经满足 native release/install 的必要结构。

**Tasks**:
- [x] 检查 CLI doctor、测试和 `skillcli audit`。
- [x] 检查 install/update/sync scripts。
- [x] 检查 GitHub remote 和 visibility。
- [x] 搜索 release/installer/manifest/checksum 相关实现。

**Acceptance**:
1. ROADMAP §2 记录带证据路径的结论。

---

## Step 3 - 形成并确认方案

**Goal**: 在改 production code 前明确推荐路径和开放问题。

**Recommendation**:

需要更新代码结构，但这是“新增分发层”，不是推翻当前 source-checkout wrapper。推荐路径是：

1. 保留当前 source checkout lifecycle：`./scripts/update_cli.sh --force`。
2. 新增 native release lifecycle：`scripts/package_release.sh`、`scripts/install_remote.sh`、`code-analyst update`、可选 `code-analyst uninstall`。
3. 将现有 GitHub repo `hongzhiyin/CodeAnalyst` 转为 public 后承载 releases；只有在确认想要 CLI 风格 URL 时才新建 `hongzhiyin/code-analyst`。
4. 先修复 `code-analyst sync-skill` audit warning，再做 native release packaging。

**Implementation Steps After Approval**:

- [ ] Add `code-analyst sync-skill --targets --force --dry-run` as a thin wrapper over `scripts/sync_skill.sh`.
- [ ] Add native release package layout and `scripts/package_release.sh`.
- [ ] Add `scripts/install_remote.sh` with manifest download, sha256 verification, user-local install root, and launcher generation.
- [ ] Add `code-analyst update` for native installs, with `--no-sync-skill` and target selection.
- [ ] Add native-aware doctor/status fields so source checkout vs release install is visible.
- [ ] Update README and root docs with source install vs native release install.
- [ ] Add tests for command parsing, release manifest/package helpers, and sync-skill delegation.
- [ ] Run local file URL install/update smoke before any GitHub release.
- [ ] After user confirms GitHub visibility strategy, publish a release and run public installer smoke.

**Acceptance**:
1. 用户确认 Q1: 转 public 现有 repo，还是创建另一个 public repo。
2. 用户确认是否开始实施上述 steps。

---

## Step 4 - 实施代码与测试

**Goal**: 实现 public/native install 维护路径，并移除旧全局 source wrapper 安装方式。

**Tasks**:
- [x] Add `code-analyst sync-skill --targets --force --dry-run` as a thin wrapper over `scripts/sync_skill.sh`.
- [x] Add native release package layout and `scripts/package_release.sh`.
- [x] Add `scripts/install_remote.sh` with manifest download, sha256 verification, user-local install root, and launcher generation.
- [x] Add `code-analyst update` for native installs, with `--no-sync-skill` and target selection.
- [x] Add native-aware doctor fields so source checkout vs release install is visible.
- [x] Update README and root docs with source install vs native release install.
- [x] Add tests for CLI sync/update command surface.
- [x] Convert existing GitHub repo to public.

**Acceptance**:
1. Code changes implement SPEC R1-R7.

---

## Step 5 - 验证与收尾

**Goal**: 验证 source checkout、native file URL install/update、docs/audit 全部一致。

**Tasks**:
- [x] Run unit tests.
- [x] Run `skillcli audit`.
- [x] Run `docdev audit`.
- [x] Run source checkout install/update lifecycle.
- [x] Run native file URL install/update lifecycle.
- [x] Record remaining public release publication gap.

**Acceptance**:
1. Verification table records every acceptance command and result.

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| Current doctor | `PYTHONPATH=src python3 -m code_analyst.cli doctor` | 通过 | CodeAnalyst CLI 0.6.1 ready |
| Current tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 17 tests |
| Current portability audit | `skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` | 通过 | 0 errors / 0 warnings |
| Current GitHub visibility | `gh repo view hongzhiyin/CodeAnalyst --json visibility` | 通过 | PUBLIC |
| Source install | `./scripts/install_cli.sh` | 通过 | Removed `/opt/homebrew/bin/code-analyst`; installed `.venv/bin/code-analyst` |
| Source update lifecycle | `./scripts/update_cli.sh --force` | 通过 | Tests, sync, check all passed |
| Release package | `scripts/package_release.sh --out dist/releases` | 通过 | artifact, sha256, manifest, installer generated |
| Native install smoke | `./scripts/install_remote.sh --release-base-url file:///Users/chihoyo/Project/CodeAnalyst/dist/releases --targets codex,agents --sync-skill` | 通过 | Installed 0.6.1 to `~/.local/share/code-analyst/releases/0.6.1` |
| Native update smoke | `~/.local/bin/code-analyst update --release-base-url file:///Users/chihoyo/Project/CodeAnalyst/dist/releases --no-sync-skill` | 通过 | Launcher and current release refreshed |
| Native doctor | `~/.local/bin/code-analyst doctor` | 通过 | Native root and installed skill wrappers ok |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | GitHub repo 已 public，但尚未创建 versioned GitHub Release。 | README 的 curl latest installer 需要 release 发布后才能公开使用。 | 下一步发布 tag/release 并做 public URL smoke。 |
| F-2 | native install 和 source wrapper 都叫 `code-analyst`，PATH 顺序可能导致用户实际运行来源不明确。 | update/doctor 可能作用到意外来源。 | doctor 显示 launcher root；source wrapper 改为 `.venv/bin`，全局 PATH 默认指向 native launcher。 |
| F-3 | native install 默认 sync installed skill homes 会写用户目录。 | 沙箱或权限问题可能中断 update。 | 提供 `--no-sync-skill`，并在失败时给出可重试命令。 |
| F-4 | release packaging 若遗漏 `skill/` 或 scripts，会导致 agent 安装可运行 CLI 但 skill 不一致。 | 版本漂移。 | package smoke 和 native install smoke 已覆盖 CLI version、installed `SKILL.md` 和 skill-local wrapper。 |
