# SPEC - Native install release and public GitHub maintenance

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已实施，本地验证通过；GitHub Release 发布待单独执行 |
| 需求来源 | 用户询问当前项目是否需要支持 native install，并在 GitHub 上创建 public 仓库用于版本更新维护 |
| 工作包目录 | `docs/changes/2026-06-15-native-install-release-public-repo/` |
| 最后更新 | 2026-06-15 |

## 1. 一句话目标

让 CodeAnalyst 在不依赖本机源码 checkout 的场景下，可以通过 public GitHub Releases 安装、更新并同步 agent skill。

## 2. 背景与问题

- 当前行为：source checkout 安装现在写入 `.venv/bin/code-analyst`；native installer 支持 release manifest、checksum、remote installer、native launcher 和 `code-analyst update`。
- 问题：public GitHub Release 尚未发布；README 中的 GitHub Releases curl 入口需要 release assets 发布后才可公开使用。
- 期望收益：新机器和后续 agent 可以用一条 GitHub Releases installer 安装稳定版本，再用 `code-analyst update` 获取新版本；本机开发不再依赖 `/opt/homebrew/bin` source wrapper。

## 3. 范围

### 3.1 本次要做

- 支持 public GitHub Releases 风格的 native install/update 分发路径。
- 保留 source-checkout install/update 作为开发者维护路径。
- 明确 public GitHub 仓库策略：当前 `origin` 已是 `https://github.com/hongzhiyin/CodeAnalyst.git`，但 visibility 是 `PRIVATE`。
- 增加 release package、remote installer、native launcher/update、checksum/manifest、smoke verification 和文档入口。
- 修复现有 `skillcli audit` warning：补 `code-analyst sync-skill`，并让它薄封装 `scripts/sync_skill.sh`。

### 3.2 本次不做

- 不把 CodeAnalyst 发布到 PyPI 或 npm。
- 不要求用户修改全局 shell rc 文件或手动设置 `CODE_ANALYST_PROJECT_DIR` 才能使用 release 版本。
- 不改变 CodeAnalyst 默认只读分析目标项目的边界。
- 不在未经确认时直接切换 GitHub 仓库 visibility 或创建新 public repo。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户在新机器运行 public release installer | 安装到用户目录，写入 `~/.local/bin/code-analyst` launcher，并通过 `code-analyst doctor` 自检。 |
| S2 | 用户已有 native install 后运行 `code-analyst update` | 下载最新 release manifest 和 artifact，校验 checksum，切换 current release，并按默认策略刷新 installed skill copies。 |
| S3 | 用户在源码 checkout 中继续开发 | `./scripts/update_cli.sh --force` 仍然安装 source wrapper、跑测试、sync skill、check install。 |
| S4 | 用户想发布新版本 | release packager 生成 tarball、manifest、checksums 和 installer assets，供 GitHub Release 发布和 smoke test 使用。 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | release artifact 必须包含运行 CLI 所需的 `src/`、`skill/`、必要 scripts 和版本元数据。 | `scripts/package_release.sh --out dist/releases` | 通过 |
| R2 | remote installer 必须下载 manifest/artifact，校验 checksum，安装到用户目录并写入 launcher。 | `./scripts/install_remote.sh --release-base-url file:///Users/chihoyo/Project/CodeAnalyst/dist/releases` | 通过 |
| R3 | native launcher 不依赖源码 checkout，默认从 installed release 运行 CLI。 | `~/.local/bin/code-analyst doctor` 显示 `/Users/chihoyo/.local/share/code-analyst/releases/0.6.1` | 通过 |
| R4 | `code-analyst update` 必须能更新 native release，并默认同步 installed skill copies；应提供跳过 sync 的选项。 | `~/.local/bin/code-analyst update --release-base-url file:///Users/chihoyo/Project/CodeAnalyst/dist/releases --no-sync-skill` | 通过 |
| R5 | source-checkout developer path 仍然可用，并与 native install 文档分开。 | `./scripts/update_cli.sh --force` 和 `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 |
| R6 | `code-analyst sync-skill` 必须薄封装 `scripts/sync_skill.sh`，避免 CLI 和脚本复制两套 sync 逻辑。 | `skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` 0 errors / 0 warnings | 通过 |
| R7 | GitHub release path 必须明确 public repo 策略。 | `gh repo view hongzhiyin/CodeAnalyst --json visibility` 显示 PUBLIC | 通过 |

## 6. 约束与不变式

1. **#1**: 不破坏根 SPEC #1：默认不得写入被分析目标项目。
2. **#2**: 不破坏根 SPEC #3：可重复 install/update/package/sync 行为必须由 CLI/scripts 完成。
3. **#3**: native release install 不能要求全局 pip install、不能修改系统 Python、不能要求用户手动设置 `CODE_ANALYST_PROJECT_DIR`。
4. **#4**: source checkout 和 native release 是两个不同维护路径；文档和 doctor 输出必须能区分二者。
5. **#5**: public release installer 不能依赖私有 GitHub token、不能把 token 写入 launcher 或持久 metadata。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧 `/opt/homebrew/bin/code-analyst` source wrapper | `scripts/install_cli.sh` 会移除识别到的旧生成 wrapper；source checkout 改用 `.venv/bin/code-analyst`。 |
| 当前 `scripts/update_cli.sh --force` | 保留为 source checkout lifecycle，不替代 native `code-analyst update`。 |
| 当前 installed skill wrappers | native sync 后应指向当前 native release；source sync 后应指向 source checkout。两者不能无提示混淆。 |
| 当前 GitHub remote 是 private | 实现前需确认：转 public，或新建 public release repo。 |

## 8. 验收标准

1. 用户可以从 public GitHub Releases 安装 CodeAnalyst，无需 clone 源码 checkout。
2. 用户可以通过 native `code-analyst update` 更新版本并刷新 skill copies。
3. `PYTHONPATH=src python3 -m unittest discover -s tests`、`code-analyst doctor`、`skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` 通过且无结构 warning。
4. 本地 file URL release smoke 和 public GitHub release smoke 均通过。
5. 根 SPEC #1、#3、#7、#9 仍成立。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否直接把 `hongzhiyin/CodeAnalyst` 从 PRIVATE 改成 PUBLIC？ | 已按用户确认转为 PUBLIC。 | 否 |
| Q2 | native install 是否写入 `~/.local/bin/code-analyst`，同时保留 `/opt/homebrew/bin/code-analyst` source wrapper？ | 已改为 native 写 `~/.local/bin`，source checkout 写 `.venv/bin`，旧 `/opt/homebrew/bin` 生成 wrapper 已移除。 | 否 |
| Q3 | native `code-analyst update` 是否默认同步所有 agent homes？ | 默认 sync `codex,agents`，并提供 `--no-sync-skill` 和 `--targets`。 | 否 |
