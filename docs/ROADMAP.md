# CodeAnalyst ROADMAP

## Current Progress

**Phase**: Phase 1 - CodeAnalyst personal code analysis assistant
**Current Step**: Global skill sync update implemented; verification and commit pending

## Step 0 - Decide the Framework Shape

**Goal**: 确认 `code-analyst` 是否需要升级为 `skill + CLI`，并把判断落到可维护文档里。

**Tasks**:
- [x] Inspect existing installed skill and scripts.
- [x] Check current workspace shape.
- [x] Compare against current public guidance for agent instructions, CLI tools, skills, and context management.
- [x] Document D-001.

**Acceptance**:
1. SPEC contains concrete invariants for the new framework.
2. DECISIONS contains a monotonic foundational decision.
3. ARCHITECTURE records installed-skill vs source-project boundary.

## Step 1 - Build CLI Foundation

**Goal**: 让重复的快速学习动作可以通过稳定命令执行。

**Tasks**:
- [x] Add `pyproject.toml` and `src/code_analyst`.
- [x] Implement `inventory`, `vibe-audit`, `pack`, and `doctor`.
- [x] Add focused tests for inventory, audit, and pack generation.
- [x] Add install/sync helper scripts.

**Acceptance**:
1. `PYTHONPATH=src python3 -m code_analyst.cli doctor` exits successfully.
2. `PYTHONPATH=src python3 -m code_analyst.cli pack /Users/chihoyo/.codex/skills/code-analyst --out analyses/...` creates the expected Markdown and JSON files.
3. Tests pass with `PYTHONPATH=src python3 -m unittest discover -s tests`.
4. Invariants #1, #2, #3, and #5 still hold.

## Step 2 - Upgrade the Companion Skill

**Goal**: 让后续 Codex 能稳定知道什么时候用 CLI、什么时候靠 agent 判断。

**Tasks**:
- [x] Draft `skill/SKILL.md` with command-first workflow.
- [x] Add `skill/references/quick-learning-framework.md`.
- [x] Sync into `/Users/chihoyo/.codex/skills/code-analyst` after user approval.
- [x] Run installed-skill validation.

**Acceptance**:
1. The skill references `code-analyst` command surface.
2. The skill keeps target projects read-only by default.
3. The skill explains the analysis framework in Chinese for Chinese requests.
4. Manual structure validation passes; `quick_validate.py` was attempted but the current Python lacks `yaml`.

## Step 3 - Visual and Static Analysis Expansion

**Goal**: 从“第一版学习包”升级到更强的结构图、调用图、风险图和优化路线图。

**Tasks**:
- [x] Add import graph extraction for Python and JS/TS.
- [x] Add route/component detection for common frontend stacks as first-pass flow hints.
- [x] Add script/command verification without installing dependencies.
- [x] Integrate or vendor the static site renderer into the source project.
- [x] Add optional browser verification for generated visual packs.
- [x] Add `render-site` and `visual-pack` CLI commands.

**Acceptance**:
1. Visual graph has non-empty nodes, edges, flows, evidence, and questions for non-trivial projects.
2. The framework can distinguish wired paths from likely leftovers.
3. The generated improvement plan ranks reliability, architecture, and product polish separately.
4. `code-analyst import-graph` extracts file-level Python and JS/TS dependencies and `pack` writes `import_graph.json`.
5. `code-analyst flow-map` and `code-analyst script-check` support non-frontend targets such as CLIs, services, Codex skills, and Node packages.

## Step 3a - Adopt skill-cli-kit portability contract

**Goal**: 让 `code-analyst` 作为 CLI-backed skill 时不依赖旧 installed scripts 或 hard-coded path guessing。

**Tasks**:
- [x] Add skill frontmatter metadata for required `code-analyst` bin and `cliHelp`.
- [x] Document CLI resolution through PATH, installed `bin/code-analyst`, and `CODE_ANALYST_PROJECT_DIR`.
- [x] Generate installed skill-local `bin/code-analyst` during sync.
- [x] Sync both Codex app user skill discovery path `~/.agents/skills/code-analyst` and Codex runtime path `~/.codex/skills/code-analyst`.
- [x] Add a project-local update lifecycle script.
- [x] Add source `README.md` and `skill/agents/openai.yaml`.

**Acceptance**:
1. `skillcli audit /Users/chihoyo/Project/CodeAnalyst --json` reports 0 errors and 0 warnings.
2. `./scripts/update_cli.sh --force` installs, tests, checks, syncs, and checks again.
3. `code-analyst doctor` reports both installed skill-local wrappers when sync has run.

## Step 3b - Add multi-kind flow and script evidence

**Goal**: 让分析不限于前端项目，也能快速定位 CLI、服务、Node package、Codex skill 的入口和脚本可信度。

**Tasks**:
- [x] Add `code-analyst flow-map` for Python CLI/service, Node scripts/bin, frontend UI hints, and Codex skill flows.
- [x] Add `code-analyst script-check` for package scripts, package bins, and Python entrypoints.
- [x] Add `flow_map.json` and `script_check.json` to generated packs and visual graph evidence.
- [x] Add regression tests for flow and script checks.

**Acceptance**:
1. `code-analyst flow-map /Users/chihoyo/Project/CodeAnalyst` reports source CLI entries without treating tests as runtime flows.
2. `code-analyst script-check /Users/chihoyo/Project/CodeAnalyst` verifies the local `pyproject.toml` entrypoints.
3. `code-analyst visual-pack` writes `flow_map.json`, `script_check.json`, and a graph containing flow/check nodes.

## Step 4 - Analysis-assistant review and design packs

**Goal**: 在同一证据层上增加代码阅读、review、重构方向、架构设计建议，并明确把真正改代码的执行留在目标项目里。

**Tasks**:
- [x] Add `review-pack` or equivalent read-only command.
- [x] Rank findings by severity, evidence confidence, and implementation risk.
- [x] Generate refactor/design proposals that cite inventory/import/flow/script evidence.
- [x] Add output sections that explain "what each part does", "why it exists", "how it connects", and "what to improve next".
- [x] Keep write-capable refactoring outside this project unless a future project explicitly owns that workflow.
- [x] Improve language quality and project-kind-specific advice templates.
- [x] Add optional `--from-pack` mode to regenerate review guidance from an existing pack without rescanning the target.

**Acceptance**:
1. Review/design outputs stay read-only unless the user explicitly requests code edits.
2. Recommendations distinguish bug risk, architecture debt, missing tests, and product/UX gaps.
3. Outputs provide actionable options for the target project to implement, but do not present patches as this project's normal deliverable.
4. `code-analyst review-pack TARGET` writes `review.md` and `review_pack.json`.
5. `code-analyst review-pack --from-pack PACK_ROOT` regenerates review outputs from existing evidence without rescanning the target.

## Step 5 - CodeAnalyst naming migration

**Goal**: 完成 CodeAnalyst 命名迁移，只保留 `code-analyst` 作为正式 CLI，并把源目录迁到 `/Users/chihoyo/Project/CodeAnalyst`。

**Tasks**:
- [x] Adopt `CodeAnalyst` as the product/display name in README and docs.
- [x] Add `code-analyst` as the primary CLI.
- [x] Remove old CLI aliases from source scripts.
- [x] Rename Python package to `code_analyst`.
- [x] Rename installed skill target to `code-analyst`.
- [x] Rename source checkout to `/Users/chihoyo/Project/CodeAnalyst`.
- [ ] Update external memory notes after the physical path rename; repo docs are refreshed, but writing to `~/.codex/memories` still needs approval.

**Acceptance**:
1. `code-analyst doctor` works from PATH.
2. Installed skill copy is `/Users/chihoyo/.codex/skills/code-analyst` and includes `bin/code-analyst`.
3. Old generated PATH wrappers are removed.
4. Source checkout lives at `/Users/chihoyo/Project/CodeAnalyst`.
