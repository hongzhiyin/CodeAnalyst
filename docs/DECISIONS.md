# CodeAnalyst DECISIONS

## D-001 - Split CodeAnalyst into Skill plus CLI

**Status**: accepted

**Date**: 2026-06-08

**Context**:

The installed `code-analyst` skill is already useful, but most repeatable work still happens as free-form agent behavior: file enumeration, manifest detection, vibe-coded leftover checks, output-root naming, pack generation, and validation. Current public guidance points in the same direction: repository instructions should stay concise, repeated workflows should become skills or commands, agent work needs explicit verification, and unnecessary context files can increase cost or even reduce task success.

**Options**:

1. Keep only the existing skill and add more prose.
2. Create a CLI-only tool and stop using a skill.
3. Use a layered `skill + CLI` design.

**Chosen**:

Choose option 3: use `skill + CLI`.

**Rationale**:

- The CLI gives deterministic, repeatable outputs for scans, audits, and generated analysis packs.
- The skill remains the right place for judgment: mode selection, evidence interpretation, diagrams worth drawing, and optimization guidance.
- This matches the local pattern already proven by other personal tooling: deterministic code for deterministic flow, skill layer for decisions and explanation.
- It avoids bloating `SKILL.md` with details that can live in scripts, references, and machine-readable JSON.

**Risks**:

- Heuristic `vibe-audit` can produce false positives, so findings must be labeled as suspected until confirmed.
- A CLI can become too broad; ROADMAP steps must keep the command surface small.
- If the source project and installed skill drift, future agents may use stale instructions. A sync/check script is needed next.

**Evidence**:

- Local inspection found the installed skill has only two scripts: inventory and static site renderer.
- Local inspection found the current workspace had only `index.md` before this bootstrap.
- External sources used for this decision:
  - OpenAI Codex use cases: understand large codebases, create an agent-friendly CLI, save workflows as skills.
  - GitHub Docs on keeping repository custom instructions short and scoped.
  - Anthropic Claude Code best practices on explore-plan-verify and context management.
  - arXiv 2602.11988 on unnecessary context-file requirements increasing cost and hurting task success.
  - arXiv 2602.14690 on Skills/Subagents being underused and often static-only.

**Affected Docs/Code**:

- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `src/code_analyst/*`
- `skill/SKILL.md`

## D-002 - Install the CLI as PATH Wrappers Instead of System Python Package

**Status**: accepted

**Date**: 2026-06-08

**Context**:

The first `scripts/install_cli.sh` attempted `python3 -m pip install "$ROOT"` and failed because the Homebrew Python environment is externally managed under PEP 668. The CLI has no third-party runtime dependencies and can run directly from the source checkout with `PYTHONPATH=src`.

**Options**:

1. Force pip with `--break-system-packages`.
2. Create a project `.venv` and require users/skills to call `.venv/bin/code-analyst`.
3. Install small shell wrappers in `/opt/homebrew/bin` that set `PYTHONPATH` to this source checkout and execute `python3 -m code_analyst.cli`.

**Chosen**:

Choose option 3.

**Rationale**:

- It avoids mutating the externally managed Python environment.
- It keeps `code-analyst` available from any folder, matching the companion skill command surface.
- It stays simple because the CLI is standard-library only.
- It keeps the source project as the durable implementation rather than copying generated code into site-packages.

**Risks**:

- The wrappers depend on `/Users/chihoyo/Project/CodeAnalyst` staying in place.
- If Python changes incompatibly, `code-analyst doctor` should surface it.

**Affected Docs/Code**:

- `scripts/install_cli.sh`
- `src/code_analyst/cli.py`
- `docs/ROADMAP.md`

## D-003 - Use File-Level Static Import Graph Before Call Graphs

**Status**: accepted

**Date**: 2026-06-08

**Context**:

The next framework step needs stronger evidence about actual wiring. A full call graph would be more expressive, but it is hard to make reliable across Python, React, Vite, Next.js, dynamic imports, and framework routing without adding heavy dependencies or producing false confidence.

**Options**:

1. Build a full cross-language call graph now.
2. Start with file-level import graph extraction for Python and JS/TS.
3. Skip static dependency extraction and rely on manual reading.

**Chosen**:

Choose option 2.

**Rationale**:

- File-level import edges are deterministic, cheap, and explain a lot of real wiring.
- Python can use `ast` from the standard library; JS/TS can use conservative import/require regexes for first-pass evidence.
- The output is easy to visualize and easy to label as static dependency evidence.
- It avoids claiming runtime behavior that static analysis cannot prove.

**Risks**:

- Dynamic imports, framework routes, dependency injection, and generated modules may be missed.
- JS/TS regex parsing is intentionally conservative and may not cover every syntax shape.
- External imports are named but not resolved to packages or versions yet.

**Affected Docs/Code**:

- `src/code_analyst/import_graph.py`
- `src/code_analyst/cli.py`
- `src/code_analyst/pack.py`
- `tests/test_import_graph.py`

## D-004 - Adopt skill-local `bin/code-analyst` wrappers for installed skills

**Status**: accepted

**Date**: 2026-06-08

**Context**:

After `skill-cli-kit` became the reusable portability checker, auditing this
project showed that `code-analyst` had the right source shape but
still relied on older installed-skill assumptions: source `SKILL.md` did not
advertise the `code-analyst` dependency, sync did not generate an installed
skill-local wrapper, and updates required manual sequencing.

**Options**:

1. Keep the existing installed scripts and hard-coded source fallback.
2. Require only global `/opt/homebrew/bin/code-analyst`.
3. Adopt the `skill-cli-kit` contract: source skill metadata, PATH first,
   installed `bin/code-analyst` second, `CODE_ANALYST_PROJECT_DIR` source fallback third, and a
   project-local update lifecycle.

**Chosen**:

Choose option 3.

**Rationale**:

- It lets agents run the CLI from arbitrary working directories without
  guessing the source path.
- It keeps `/Users/chihoyo/Project/CodeAnalyst` as the editable
  source checkout and treats installed skill directories as generated copies.
- It makes `skillcli audit` useful as an ongoing portability regression check.
- It replaces older installed helper scripts with one wrapper back to the
  source CLI, reducing drift.

**Risks**:

- The wrapper depends on the source checkout path staying stable. Mitigation:
  `code-analyst doctor` surfaces the installed wrapper state and `scripts/sync_skill.sh
  --force` regenerates it.
- Replacing the installed skill can remove old files that were not copied back
  into source. Mitigation: keep `agents/openai.yaml`, `output-contract.md`, and
  `diagram-recipes.md` under `skill/` before syncing.

**Affected Docs/Code**:

- `skill/SKILL.md`
- `skill/agents/openai.yaml`
- `skill/references/output-contract.md`
- `skill/references/diagram-recipes.md`
- `scripts/sync_skill.sh`
- `scripts/update_cli.sh`
- `src/code_analyst/cli.py`
- `README.md`

## D-005 - Keep review and design guidance in this analysis assistant

**Status**: accepted

**Date**: 2026-06-10

**Context**:

The framework is expanding beyond codebase understanding into code reading,
review, refactor suggestions, and architecture design guidance. The intended
shape is an analysis assistant: it explains what each part of a project does,
how the pieces connect, where the risks are, and what improvement directions
are worth considering. Actual code changes should happen in the target
project's own iteration loop.

**Options**:

1. Limit this project to basic codebase onboarding only.
2. Create a separate project immediately for review/refactor/design guidance.
3. Keep code reading, review, refactor direction, and architecture design
   guidance in this project, while leaving actual edits to each target project.

**Chosen**:

Choose option 3.

**Rationale**:

- Review/design recommendations reuse the same deterministic scans and
  evidence contracts.
- Keeping them together avoids duplicating CLI wrappers, pack generation,
  site rendering, and skill sync logic.
- The natural deliverable here is a better mental model plus better options,
  not a patch against another repository.
- Target projects should own their own code changes, tests, commits, and
  product iteration history.

**Risks**:

- The command surface can become too broad. Mitigation: ROADMAP separates
  understanding, review/design guidance, and target-project implementation.
- Review recommendations can sound more certain than the evidence supports.
  Mitigation: keep evidence citations and inference labels mandatory.

**Affected Docs/Code**:

- `docs/SPEC.md`
- `docs/ROADMAP.md`
- `src/code_analyst/review_pack.py`

## D-006 - Add multi-kind flow map and script checks before deeper call graphs

**Status**: accepted

**Date**: 2026-06-10

**Context**:

The framework needs to support more than frontend projects. CLI tools,
backend services, Node packages, Codex skills, and generated apps all have
different user-facing entrypoints. A deeper call graph remains useful, but
before that the tool needs a reliable way to find declared commands and
project-kind-specific flow hints.

**Options**:

1. Prioritize frontend route/component detection only.
2. Build full cross-language call/dataflow analysis now.
3. Add generic `flow-map` and `script-check` first, with frontend hints as one
   project kind among several.

**Chosen**:

Choose option 3.

**Rationale**:

- It directly supports CLI, service, skill, Node, and frontend targets.
- It keeps analysis read-only and dependency-free.
- It catches common generated-project failures: stale scripts, missing bins,
  unverified Python entrypoints, and UI controls/handlers that need tracing.

**Risks**:

- Flow hints are not runtime proof. They must be presented as leads.
- Some dynamic framework routes and generated commands may be missed.

**Affected Docs/Code**:

- `src/code_analyst/flow_map.py`
- `src/code_analyst/script_check.py`
- `src/code_analyst/cli.py`
- `src/code_analyst/pack.py`
- `tests/test_flow_map.py`
- `tests/test_script_check.py`

## D-007 - Add `review-pack` as recommendation output, not patch output

**Status**: accepted

**Date**: 2026-06-10

**Context**:

Step 4 needs a durable output for code review, refactor direction, and
architecture design advice. The project should help the user read code and
choose better next moves, while leaving actual edits to each analyzed target
project.

**Options**:

1. Extend `pack` only and put all advice into existing Markdown files.
2. Add `review-pack` that reuses the standard pack evidence and writes
   `review.md` plus `review_pack.json`.
3. Add a patch-generating refactor command.

**Chosen**:

Choose option 2.

**Rationale**:

- A dedicated command makes the analysis-assistant mode explicit.
- Reusing pack evidence keeps advice tied to `inventory`, `flow-map`,
  `script-check`, `import-graph`, and `vibe-audit`.
- JSON output gives future agents a stable way to consume severity,
  confidence, implementation risk, and evidence.
- Avoiding patches preserves the target-project boundary.

**Risks**:

- Advice can become formulaic if the heuristics stay too generic. Mitigation:
  ROADMAP keeps project-kind-specific templates as follow-up work.
- A user may expect this command to fix code. Mitigation: CLI and Markdown
  output both state that recommendations should be implemented in the target
  project.

**Affected Docs/Code**:

- `src/code_analyst/review_pack.py`
- `src/code_analyst/cli.py`
- `tests/test_review_pack.py`
- `docs/SPEC.md`
- `docs/ROADMAP.md`
- `skill/SKILL.md`

## D-008 - Rename to CodeAnalyst and remove legacy aliases

**Status**: accepted

**Date**: 2026-06-10

**Context**:

The user wants the project to feel like a reusable assistant for understanding,
analyzing, reviewing, and planning refactors across many other codebases.
`CodeReader` was attractive but too reading-only. `CodeAnalyst` better captures
analysis and judgment without implying that this project directly edits target
projects.

Earlier technical identifiers were wired into wrappers, installed skills,
generated analysis paths, memory records, and docs. The final direction is to
finish the rename instead of preserving legacy aliases long term.

**Options**:

1. Keep old aliases indefinitely.
2. Use CodeAnalyst as display name but keep old package, skill, and wrapper names.
3. Rename the project to CodeAnalyst, keep only `code-analyst` as the CLI, and
   remove old wrappers/installed skill copies during install/sync.

**Chosen**:

Choose option 3.

**Rationale**:

- `CodeAnalyst` is the human-facing name and `code-analyst` is the idiomatic
  multi-word shell command.
- Removing legacy aliases keeps future docs, installed skills, and PATH
  wrappers simpler.
- A single physical source checkout path avoids confusing new agents.
- Install/sync scripts can clean up known generated legacy wrappers and skill
  copies safely.

**Risks**:

- Existing memory entries and older chat references may still mention the old
  path. Mitigation: final responses should call out the new path after the move.
- Removing wrappers can break old shell habits. Mitigation: README.md and
  AGENTS.md show only the new command.

**Affected Docs/Code**:

- `README.md`
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `scripts/install_cli.sh`
- `scripts/sync_skill.sh`
- `scripts/check_install.sh`
- `pyproject.toml`

## D-009 - Close Phase 1 with from-pack review regeneration and site verification

**Status**: accepted

**Date**: 2026-06-10

**Context**:

After the CodeAnalyst naming migration, the remaining Phase 1 tail items were
mostly continuity and validation gaps: review packs could only be generated by
rescanning a target, visual packs had no deterministic readiness check after
rendering, and ROADMAP/memory handoff needed to point future agents at the new
source path.

**Options**:

1. Leave these as manual agent habits.
2. Add dependency-heavy browser automation as the default validation path.
3. Add standard-library `verify-site`, `visual-pack --verify-site`, and
   `review-pack --from-pack`, then keep true browser/UI inspection as an
   optional agent workflow on top.

**Chosen**:

Choose option 3.

**Rationale**:

- `review-pack --from-pack` lets future agents regenerate review guidance from
  saved evidence even when the target project has moved, been deleted, or is
  expensive to rescan.
- `verify-site` catches missing files, invalid JSON, broken embedded graph data,
  and browser bootstrap problems without adding runtime dependencies.
- Keeping browser automation optional preserves the Python standard-library
  default while still giving visual-pack users a concrete verification step.
- Project-kind-specific review guidance makes recommendations less generic
  without turning CodeAnalyst into a patch generator.

**Risks**:

- `verify-site` is a structural readiness check, not proof of visual polish in
  an actual browser. Agents should still use Browser/Playwright when pixel-level
  or interaction verification matters.
- `--from-pack` can regenerate advice from stale evidence. The review output
  records the source pack root so freshness remains visible.

**Affected Docs/Code**:

- `src/code_analyst/verify_site.py`
- `src/code_analyst/review_pack.py`
- `src/code_analyst/cli.py`
- `tests/test_verify_site.py`
- `tests/test_review_pack.py`
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

## D-010 - Sync CodeAnalyst to global user skills and Codex runtime skills

**Status**: accepted

**Date**: 2026-06-10

**Context**:

`code-analyst` was synced only to `~/.codex/skills/code-analyst`. The CLI and
current thread could use it, but Codex app skill discovery and slash/skill UI
expect user-authored skills under `~/.agents/skills`. This made the skill work
as a local runtime helper while still being hard to find from the app UI.

**Options**:

1. Keep syncing only to `~/.codex/skills`.
2. Manually copy the current skill to `~/.agents/skills` once.
3. Make `scripts/sync_skill.sh` sync both `~/.agents/skills/code-analyst` and
   `~/.codex/skills/code-analyst` by default, and keep `scripts/update_cli.sh`
   as the one update lifecycle.

**Chosen**:

Choose option 3.

**Rationale**:

- `~/.agents/skills` is the global user skill discovery path for Codex app.
- `~/.codex/skills` remains useful for existing local runtime behavior in this
  environment.
- A single source checkout and one sync script avoid stale installed copies.
- Running tests before sync keeps broken source changes from being promoted to
  the global skill directories.

**Risks**:

- The sync script writes outside the repository and therefore requires explicit
  approval in sandboxed sessions.
- Existing unmarked skill folders are not overwritten unless `--force` is used,
  preserving manually maintained directories.

**Affected Docs/Code**:

- `scripts/sync_skill.sh`
- `scripts/update_cli.sh`
- `scripts/check_install.sh`
- `src/code_analyst/cli.py`
- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `README.md`
- `pyproject.toml`
- `src/code_analyst/__init__.py`
