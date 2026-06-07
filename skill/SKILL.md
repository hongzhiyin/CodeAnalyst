---
name: codebase-understanding
description: Use when the user wants to understand how a local folder, codebase, generated app, Codex skill, plugin, script collection, or small software project works. Produce evidence-backed architecture notes, diagrams, and optional local visualization pages. Default to read-only target analysis and write artifacts to the central CodebaseUnderstanding library unless the user explicitly requests another location.
metadata:
  short-description: Explain codebases with diagrams, audits, and visual maps
---

# Codebase Understanding

## Purpose

Turn an unfamiliar or vibe-coded folder into a clear mental model and an optimization path. The normal output is an evidence-backed explanation, a small set of behavior diagrams, and, when useful, a persistent learning pack.

Use the companion CLI for deterministic work. The skill decides what to inspect and how to explain it; the CLI handles repeatable scans, vibe-coded leftover checks, output directory naming, and pack generation.

If `cbu` is not installed, use the source checkout command:

```bash
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli <command>
```

## Language

Match the user's language in generated artifacts. If the user writes in Chinese, generated Markdown, graph labels, summaries, evidence notes, risk notes, and open questions should be Chinese, while preserving code identifiers, file paths, CLI names, package names, and established technical terms.

## Default Safety

Default stance: analyze and explain. Do not modify the target source code unless the user explicitly asks for edits.

When creating persistent artifacts, default to:

```text
/Users/chihoyo/Project/CodebaseUnderstanding/analyses/<YYYY-MM-DD>-<project-slug>/
```

Only write inside the analyzed target, such as `TARGET/docs/understanding/`, when the user explicitly asks for target-local artifacts.

## Command Surface

Prefer these deterministic commands before free-form exploration:

```bash
cbu doctor
cbu inventory TARGET --out OUTPUT_ROOT/inventory.json
cbu import-graph TARGET --out OUTPUT_ROOT/import_graph.json
cbu vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
cbu pack TARGET --out OUTPUT_ROOT
cbu visual-pack TARGET --out OUTPUT_ROOT
cbu render-site OUTPUT_ROOT/understanding_graph.json --out OUTPUT_ROOT/site
```

Fallback when `cbu` is not on PATH:

```bash
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli doctor
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli inventory TARGET --out OUTPUT_ROOT/inventory.json
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli import-graph TARGET --out OUTPUT_ROOT/import_graph.json
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli pack TARGET --out OUTPUT_ROOT
PYTHONPATH=/Users/chihoyo/Project/CodebaseUnderstanding/src python3 -m codebase_understanding.cli visual-pack TARGET --out OUTPUT_ROOT
```

## Operating Modes

Pick the smallest mode that satisfies the request:

- **Quick read**: answer in chat with a compact map, 1-2 Mermaid diagrams, key file references, and likely next files to read.
- **Learning pack**: run `cbu pack`; create Markdown notes, `inventory.json`, `vibe_audit.json`, and `understanding_graph.json` under the central library.
- **Visual pack**: run `cbu visual-pack`; create the learning pack plus a static visualization page at `OUTPUT_ROOT/site/index.html`.
- **Optimization guide**: after understanding the system shape, rank improvements by reliability, maintainability, and product polish. Do not edit the target unless the user asks.

If the user asks for "clear diagrams", "visualization", "web page", or says they want to understand a codebase deeply, prefer **Learning pack** or **Visual pack** unless the target is tiny.

## Core Workflow

1. **Locate the target**
   - If no folder or file is named, ask one concise question for the path.
   - Resolve `~` and relative paths before inspecting.
   - If the target is a Codex skill, inspect `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/`.

2. **Create or choose output root**
   - If files will be created and the user has not named an output path, use the central analysis library.
   - Use `cbu pack TARGET` when possible; it chooses the slugged output root automatically unless `--out` is supplied.

3. **Run deterministic first-pass tools**
   - Run `cbu inventory` to determine project type, manifests, entrypoints, extensions, and top directories.
   - Run `cbu import-graph` to extract Python and JS/TS file-level static dependency edges.
   - Run `cbu vibe-audit` for vibe-coded project risks: missing verification, missing script targets, half-wired UI, possibly unused source files, duplicated implementations, stale config.
   - Run `cbu doctor` if command availability, installed skill drift, or local setup is uncertain.

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
  import_graph.json
  vibe_audit.json
  understanding_graph.json
  site/
    index.html
    data.json
```

Use `cbu visual-pack` to create `site/`; use `cbu render-site` to regenerate a site from an existing `understanding_graph.json`.

## References

Read `references/quick-learning-framework.md` when the user asks for a deeper personal learning method, optimization plan, or vibe-coding audit.
