---
name: code-analyst
description: Use CodeAnalyst when the user wants to understand how a local folder, codebase, generated app, Codex skill, plugin, script collection, or small software project works. Produce evidence-backed architecture notes, diagrams, review/refactor guidance, and optional local visualization pages. Default to read-only target analysis and write artifacts to the central CodeAnalyst library unless the user explicitly requests another location.
metadata:
  short-description: CodeAnalyst: explain codebases with diagrams, audits, and review guidance
  requires:
    bins: ["code-analyst"]
  cliHelp: "code-analyst --help"
---

# CodeAnalyst

## Purpose

CodeAnalyst turns an unfamiliar or vibe-coded folder into a clear mental model and an optimization path. The normal output is an evidence-backed explanation of what each part does, how the pieces connect, where the risks are, and what improvement or architecture directions are worth considering.

Use the companion CLI for deterministic work. The skill decides what to inspect and how to explain it; the CLI handles repeatable scans, vibe-coded leftover checks, output directory naming, and pack generation.

This skill is a code analysis assistant, not a cross-repository code modification tool. It can recommend changes, refactor directions, and architecture options; actual edits should normally happen inside the target project's own workflow.

## CLI

Resolve helper commands in this order:

1. Run `code-analyst <command>` if it is on `PATH`.
2. If this installed skill path is visible, run `bin/code-analyst <command>`.
3. If `CODE_ANALYST_PROJECT_DIR` points to the source checkout, run:

```bash
CODE_ANALYST_PROJECT_DIR="$CODE_ANALYST_PROJECT_DIR" PYTHONPATH="$CODE_ANALYST_PROJECT_DIR/src" \
  python3 -m code_analyst.cli <command>
```

If none of those work but the canonical local checkout exists, use:

```bash
CODE_ANALYST_PROJECT_DIR=/Users/chihoyo/Project/CodeAnalyst \
  PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src \
  python3 -m code_analyst.cli <command>
```

## Language

Match the user's language in generated artifacts. If the user writes in Chinese, generated Markdown, graph labels, summaries, evidence notes, risk notes, and open questions should be Chinese, while preserving code identifiers, file paths, CLI names, package names, and established technical terms.

## Default Safety

Default stance: analyze, explain, and recommend. Do not modify the target source code unless the user explicitly asks for edits in that target project.

When creating persistent artifacts, default to:

```text
/Users/chihoyo/Project/CodeAnalyst/analyses/<YYYY-MM-DD>-<project-slug>/
```

Only write inside the analyzed target, such as `TARGET/docs/understanding/`, when the user explicitly asks for target-local artifacts.

## Command Surface

Prefer these deterministic commands before free-form exploration:

```bash
code-analyst doctor
code-analyst inventory TARGET --out OUTPUT_ROOT/inventory.json
code-analyst flow-map TARGET --out OUTPUT_ROOT/flow_map.json
code-analyst script-check TARGET --out OUTPUT_ROOT/script_check.json
code-analyst import-graph TARGET --out OUTPUT_ROOT/import_graph.json
code-analyst vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
code-analyst pack TARGET --out OUTPUT_ROOT
code-analyst review-pack TARGET --out OUTPUT_ROOT
code-analyst visual-pack TARGET --out OUTPUT_ROOT
code-analyst render-site OUTPUT_ROOT/understanding_graph.json --out OUTPUT_ROOT/site
```

Fallback when `code-analyst` is not on PATH:

```bash
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli doctor
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli inventory TARGET --out OUTPUT_ROOT/inventory.json
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli flow-map TARGET --out OUTPUT_ROOT/flow_map.json
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli script-check TARGET --out OUTPUT_ROOT/script_check.json
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli import-graph TARGET --out OUTPUT_ROOT/import_graph.json
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli pack TARGET --out OUTPUT_ROOT
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli review-pack TARGET --out OUTPUT_ROOT
PYTHONPATH=/Users/chihoyo/Project/CodeAnalyst/src python3 -m code_analyst.cli visual-pack TARGET --out OUTPUT_ROOT
```

## Operating Modes

Pick the smallest mode that satisfies the request:

- **Quick read**: answer in chat with a compact map, 1-2 Mermaid diagrams, key file references, and likely next files to read.
- **Learning pack**: run `code-analyst pack`; create Markdown notes, `inventory.json`, `vibe_audit.json`, and `understanding_graph.json` under the central library.
- **Visual pack**: run `code-analyst visual-pack`; create the learning pack plus a static visualization page at `OUTPUT_ROOT/site/index.html`.
- **Optimization guide**: after understanding the system shape, rank improvements by reliability, maintainability, and product polish. Provide options and tradeoffs for the target project to implement.
- **Review/design guide**: run `code-analyst review-pack` when persistent guidance is useful; explain what each major part does, identify likely bug risks and architecture debt, and propose refactor or design directions with evidence. Keep the deliverable as analysis unless the user moves into the target project and asks for implementation.

If the user asks for "clear diagrams", "visualization", "web page", or says they want to understand a codebase deeply, prefer **Learning pack** or **Visual pack** unless the target is tiny.

## Core Workflow

1. **Locate the target**
   - If no folder or file is named, ask one concise question for the path.
   - Resolve `~` and relative paths before inspecting.
   - If the target is a Codex skill, inspect `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/`.

2. **Create or choose output root**
   - If files will be created and the user has not named an output path, use the central analysis library.
   - Use `code-analyst pack TARGET` when possible; it chooses the slugged output root automatically unless `--out` is supplied.

3. **Run deterministic first-pass tools**
   - Run `code-analyst inventory` to determine project type, manifests, entrypoints, extensions, and top directories.
   - Run `code-analyst flow-map` to find CLI, service, frontend, Node package, and Codex skill entrypoint hints.
   - Run `code-analyst script-check` to verify declared scripts, bins, and Python entrypoint targets without running them.
   - Run `code-analyst import-graph` to extract Python and JS/TS file-level static dependency edges.
   - Run `code-analyst vibe-audit` for vibe-coded project risks: missing verification, missing script targets, half-wired UI, possibly unused source files, duplicated implementations, stale config.
   - Run `code-analyst doctor` if command availability, installed skill drift, or local setup is uncertain.

4. **Trace real flows**
   - Start from user-facing entrypoints and follow calls into helpers, state, IO, rendering, generated artifacts, or external tools.
   - For each important flow, capture trigger/input, main modules, data transformations, side effects, and output.
   - Separate confirmed facts from inferences.

5. **Explain principles**
   - Identify the core domain model, event lifecycle, dependency direction, and state/data ownership.
   - Prefer "what happens when the user does X" over folder-by-folder narration.
   - Use diagrams that explain behavior, not just directory shape.

6. **Guide optimization**
   - First add or identify a verification loop.
   - Then remove or quarantine generated leftovers.
   - Then improve architecture boundaries and naming.
   - Then polish UX/performance/features.
   - Tie each recommendation to evidence or label it as Inference.
   - Present concrete implementation directions, but leave code changes to the target project's own iteration flow unless the user explicitly changes scope.

## Vibe-Coded Project Lens

Vibe-coded projects often contain dead files, copied templates, half-wired features, or mismatched dependencies. Look for:

- files that are imported nowhere
- UI controls without handlers
- handlers that update state not rendered anywhere
- source files that have no incoming internal import edge
- config for a framework not actually used
- scripts that refer to missing files
- duplicated implementations of the same idea
- missing tests, typecheck, lint, smoke checks, or browser verification

Explain these gently as "likely generated leftovers", "possibly unused paths", or "verification gaps" unless verified.

## Output Contract

For persistent packs, create or use:

```text
OUTPUT_ROOT/
  source.md
  overview.md
  architecture.md
  flows.md
  diagrams.md
  open-questions.md
  inventory.json
  flow_map.json
  script_check.json
  import_graph.json
  vibe_audit.json
  understanding_graph.json
  site/
    index.html
    data.json
```

`code-analyst review-pack` additionally writes:

```text
review.md
review_pack.json
```

Use `code-analyst visual-pack` to create `site/`; use `code-analyst render-site` to regenerate a site from an existing `understanding_graph.json`.

## References

Read `references/quick-learning-framework.md` when the user asks for a deeper personal learning method, optimization plan, or vibe-coding audit.
