# Codebase Understanding ROADMAP

## Step 0 - Decide the Framework Shape

**Goal**: 确认 `codebase-understanding` 是否需要升级为 `skill + CLI`，并把判断落到可维护文档里。

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
- [x] Add `pyproject.toml` and `src/codebase_understanding`.
- [x] Implement `inventory`, `vibe-audit`, `pack`, and `doctor`.
- [x] Add focused tests for inventory, audit, and pack generation.
- [x] Add install/sync helper scripts.

**Acceptance**:
1. `PYTHONPATH=src python3 -m codebase_understanding.cli doctor` exits successfully.
2. `PYTHONPATH=src python3 -m codebase_understanding.cli pack /Users/chihoyo/.codex/skills/codebase-understanding --out analyses/...` creates the expected Markdown and JSON files.
3. Tests pass with `PYTHONPATH=src python3 -m unittest`.
4. Invariants #1, #2, #3, and #5 still hold.

## Step 2 - Upgrade the Companion Skill

**Goal**: 让后续 Codex 能稳定知道什么时候用 CLI、什么时候靠 agent 判断。

**Tasks**:
- [x] Draft `skill/SKILL.md` with command-first workflow.
- [x] Add `skill/references/quick-learning-framework.md`.
- [x] Sync into `/Users/chihoyo/.codex/skills/codebase-understanding` after user approval.
- [x] Run installed-skill validation.

**Acceptance**:
1. The skill references `cbu` command surface.
2. The skill keeps target projects read-only by default.
3. The skill explains the learning framework in Chinese for Chinese requests.
4. Manual structure validation passes; `quick_validate.py` was attempted but the current Python lacks `yaml`.

## Step 3 - Visual and Static Analysis Expansion

**Goal**: 从“第一版学习包”升级到更强的结构图、调用图、风险图和优化路线图。

**Tasks**:
- [x] Add import graph extraction for Python and JS/TS.
- [ ] Add route/component detection for common frontend stacks.
- [ ] Add script/command verification without installing dependencies.
- [x] Integrate or vendor the static site renderer into the source project.
- [ ] Add optional browser verification for generated visual packs.
- [x] Add `render-site` and `visual-pack` CLI commands.

**Acceptance**:
1. Visual graph has non-empty nodes, edges, flows, evidence, and questions for non-trivial projects.
2. The framework can distinguish wired paths from likely leftovers.
3. The generated improvement plan ranks reliability, architecture, and product polish separately.
4. `cbu import-graph` extracts file-level Python and JS/TS dependencies and `pack` writes `import_graph.json`.
