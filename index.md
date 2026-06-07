# Codebase Understanding

Central library for analysis artifacts generated while understanding local codebases, generated apps, Codex skills, plugins, and small software projects.

This workspace is now also the source project for the personal `codebase-understanding` skill + CLI framework. The docs-driven source of truth is in `docs/`, the CLI implementation is in `src/codebase_understanding/`, and the syncable skill draft is in `skill/`.

## CLI

During local development:

```bash
PYTHONPATH=src python3 -m codebase_understanding.cli doctor
PYTHONPATH=src python3 -m codebase_understanding.cli inventory TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli import-graph TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli vibe-audit TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli pack TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli visual-pack TARGET
```

## Structure

```text
analyses/
  <YYYY-MM-DD>-<project-slug>/
    source.md
    overview.md
    architecture.md
    flows.md
    diagrams.md
    open-questions.md
    inventory.json
    understanding_graph.json
    site/
      index.html
      data.json
```

`<YYYY-MM-DD>-<project-slug>` is a template. A real folder should look like `2026-06-07-some-app`, not `YYYY-MM-DD-project-slug` and not `<YYYY-MM-DD>-<project-slug>`.

## Policy

- Use this central library by default for exploratory analysis, reviews, and learning.
- Do not write artifacts into the analyzed target project unless explicitly requested.
- If target-local notes are needed later, copy or regenerate the relevant analysis under `TARGET/docs/understanding/`.
