# ARCHITECTURE - Native install release and public GitHub maintenance

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已实施，本地验证通过 |
| 创建原因 | 新增 release packaging、remote installer、native launcher/update、GitHub Release 分发和 skill sync source 切换 |
| 最后更新 | 2026-06-15 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `pyproject.toml` | 定义 `code-analyst` package version 和 script entrypoint。 | release manifest/version source。 |
| `src/code_analyst/__init__.py` | 暴露 CLI version。 | native package/version 检查需要同步。 |
| `src/code_analyst/cli.py` | argparse command surface；包括分析、pack、review、doctor、`sync-skill` 和 native `update`。 | 已修改。 |
| `scripts/install_cli.sh` | 安装 source-checkout `.venv/bin/code-analyst` wrapper，并移除识别到的旧 `/opt/homebrew/bin` wrapper。 | 已修改为开发者入口，不等同于 native installer。 |
| `scripts/install_remote.sh` | 下载 manifest/artifact、校验 sha256、安装 native release、写 `~/.local/bin/code-analyst` launcher。 | 已新增。 |
| `scripts/package_release.sh` | 生成 release tarball、sha256、manifest 和 installer assets。 | 已新增。 |
| `scripts/sync_skill.sh` | 把 active root 的 `skill/` 同步到 `~/.agents` 和 `~/.codex`，并写 skill-local wrapper。 | 已支持 dry-run，由 `code-analyst sync-skill` 委派调用。 |
| `scripts/update_cli.sh` | source checkout lifecycle：install、test、sync、check。 | 保留；native update 走 `code-analyst update`。 |
| `scripts/check_install.sh` | 验证 source wrapper、测试和 installed skill copies。 | 已改为使用 `.venv/bin/code-analyst`。 |
| `skill/SKILL.md` | agent workflow source-of-truth。 | release package 必须包含，并在 update 后同步到 agent homes。 |
| `README.md` | 当前只写 source checkout quick start。 | 需要增加 native install/update quick start。 |

## 2. 当前调用链 / 数据流

```text
source checkout:
  ./scripts/install_cli.sh
    -> .venv/bin/code-analyst wrapper
    -> CODE_ANALYST_PROJECT_DIR=/Users/chihoyo/Project/CodeAnalyst
    -> PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src
    -> python3 -m code_analyst.cli

source update:
  ./scripts/update_cli.sh --force
    -> install_cli.sh
    -> python3 -m unittest discover -s tests
    -> scripts/sync_skill.sh --force
    -> scripts/check_install.sh

skill sync:
  scripts/sync_skill.sh --force
    -> copy skill/ to ~/.agents/skills/code-analyst and ~/.codex/skills/code-analyst
    -> write bin/code-analyst wrappers pointing back to source checkout
```

## 3. 目标结构

```text
release authoring:
  scripts/package_release.sh
    -> dist/code-analyst-<version>.tar.gz
    -> dist/code-analyst-<version>.tar.gz.sha256
    -> dist/manifest.json
    -> dist/install_remote.sh

native install:
  curl -fsSL https://github.com/hongzhiyin/CodeAnalyst/releases/latest/download/install_remote.sh | sh
    -> download manifest + artifact
    -> verify sha256
    -> ~/.local/share/code-analyst/releases/<version>/
    -> ~/.local/share/code-analyst/current -> releases/<version>
    -> ~/.local/bin/code-analyst launcher
    -> code-analyst doctor

native update:
  code-analyst update [--no-sync-skill] [--targets codex,agents]
    -> resolve GitHub Releases manifest
    -> install latest release if newer or --force
    -> refresh ~/.local/share/code-analyst/current
    -> sync installed skill copies unless skipped

source developer path:
  ./scripts/update_cli.sh --force
    -> unchanged source wrapper/test/sync/check lifecycle
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `src/code_analyst/cli.py` | 修改 | Add `sync-skill` thin delegation and `update` native install command. | 不复制 `scripts/sync_skill.sh` 的 target resolution/copy logic。 |
| `scripts/package_release.sh` | 新增 | Build release assets from source checkout. | 不从 installed skill homes 取文件。 |
| `scripts/install_remote.sh` | 新增 | Install latest or configured release from GitHub/file base URL. | 不需要源码 checkout、pip global install 或 token。 |
| `scripts/sync_skill.sh` | 修改 | 支持 native release root 或 source root 生成 wrappers。 | 不把 release 下载逻辑放进 sync script。 |
| `scripts/check_install.sh` | 修改或拆分 | Verify source checkout path; optional native smoke checker verifies release root. | 不把 release 发布流程塞进普通 source check。 |
| `README.md` | 修改 | 分开说明 native install/update 和 source checkout development install。 | 不把 private-token flow 当普通安装路径。 |
| `docs/SPEC.md` / `docs/ARCHITECTURE.md` / `docs/ROADMAP.md` / `docs/DECISIONS.md` | 修改 | 记录 durable release/install contract and acceptance. | 不写临时 smoke 输出到 root docs。 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| Install root | `~/.local/share/code-analyst/releases/<version>/` | 新增 native release storage。 | 不影响 source checkout。 |
| Current pointer | `~/.local/share/code-analyst/current` | 指向当前 native release。 | update 原子切换。 |
| Native launcher | `~/.local/bin/code-analyst` | 新增用户级 release launcher。 | source checkout 改用 `.venv/bin`，全局 command 默认可指向 native launcher。 |
| Release base URL | `CODE_ANALYST_RELEASE_BASE_URL` | 支持 file URL smoke 和镜像安装。 | 默认 GitHub Releases latest assets。 |
| Sync targets | `CODE_ANALYST_SYNC_TARGETS` / `--targets` | native update 可复用现有 target 语义。 | 默认仍为 `codex,agents`。 |
| GitHub repo | `hongzhiyin/CodeAnalyst` | 当前 PRIVATE；推荐转 PUBLIC 或另建 public repo。 | private release flow 只作为开发/测试备用。 |

## 6. 测试与观测点

- Unit tests for `sync-skill` command delegation and `update` argument parsing.
- Package smoke: generated tarball includes `src/`, `skill/`, scripts, pyproject, README, docs.
- Local file URL install smoke: `CODE_ANALYST_RELEASE_BASE_URL=file://... ./scripts/install_remote.sh`.
- Native doctor: `~/.local/bin/code-analyst doctor` reports release root and installed skill wrappers.
- Skill sync smoke after native install/update: installed `SKILL.md` matches release `skill/SKILL.md`; `bin/code-analyst` points to release/current instead of stale source checkout when native sync is used.
- Public GitHub smoke after release: curl installer from latest release and run `code-analyst doctor`.
