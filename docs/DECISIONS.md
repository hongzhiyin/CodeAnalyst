# Codebase Understanding DECISIONS

## D-001 - Split Codebase Understanding into Skill plus CLI

**Status**: accepted

**Date**: 2026-06-08

**Context**:

The installed `codebase-understanding` skill is already useful, but most repeatable work still happens as free-form agent behavior: file enumeration, manifest detection, vibe-coded leftover checks, output-root naming, pack generation, and validation. Current public guidance points in the same direction: repository instructions should stay concise, repeated workflows should become skills or commands, agent work needs explicit verification, and unnecessary context files can increase cost or even reduce task success.

**Options**:

1. Keep only the existing skill and add more prose.
2. Create a CLI-only tool and stop using a skill.
3. Use a layered `skill + CLI` design.

**Decision**:

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
- `src/codebase_understanding/*`
- `skill/SKILL.md`

## D-002 - Install the CLI as PATH Wrappers Instead of System Python Package

**Status**: accepted

**Date**: 2026-06-08

**Context**:

The first `scripts/install_cli.sh` attempted `python3 -m pip install "$ROOT"` and failed because the Homebrew Python environment is externally managed under PEP 668. The CLI has no third-party runtime dependencies and can run directly from the source checkout with `PYTHONPATH=src`.

**Options**:

1. Force pip with `--break-system-packages`.
2. Create a project `.venv` and require users/skills to call `.venv/bin/cbu`.
3. Install small shell wrappers in `/opt/homebrew/bin` that set `PYTHONPATH` to this source checkout and execute `python3 -m codebase_understanding.cli`.

**Decision**:

Choose option 3.

**Rationale**:

- It avoids mutating the externally managed Python environment.
- It keeps `cbu` available from any folder, matching the companion skill command surface.
- It stays simple because the CLI is standard-library only.
- It keeps the source project as the durable implementation rather than copying generated code into site-packages.

**Risks**:

- The wrappers depend on `/Users/chihoyo/Project/CodebaseUnderstanding` staying in place.
- If Python changes incompatibly, `cbu doctor` should surface it.

**Affected Docs/Code**:

- `scripts/install_cli.sh`
- `src/codebase_understanding/cli.py`
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

**Decision**:

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

- `src/codebase_understanding/import_graph.py`
- `src/codebase_understanding/cli.py`
- `src/codebase_understanding/pack.py`
- `tests/test_import_graph.py`
