# CodeAnalyst

Central library for analysis artifacts generated while understanding local codebases, generated apps, Codex skills, plugins, and small software projects.

This workspace is now also the source project for the personal `code-analyst` skill + CLI framework. The docs-driven source of truth is in `docs/`, the CLI implementation is in `src/code_analyst/`, and the syncable skill draft is in `skill/`.

## CLI

During local development:

```bash
PYTHONPATH=src python3 -m code_analyst.cli doctor
PYTHONPATH=src python3 -m code_analyst.cli inventory TARGET
PYTHONPATH=src python3 -m code_analyst.cli flow-map TARGET
PYTHONPATH=src python3 -m code_analyst.cli script-check TARGET
PYTHONPATH=src python3 -m code_analyst.cli import-graph TARGET
PYTHONPATH=src python3 -m code_analyst.cli vibe-audit TARGET
PYTHONPATH=src python3 -m code_analyst.cli pack TARGET
PYTHONPATH=src python3 -m code_analyst.cli review-pack TARGET
PYTHONPATH=src python3 -m code_analyst.cli visual-pack TARGET
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
    flow_map.json
    script_check.json
    understanding_graph.json
    review.md
    review_pack.json
    site/
      index.html
      data.json
```

`<YYYY-MM-DD>-<project-slug>` is a template. A real folder should look like `2026-06-07-some-app`, not `YYYY-MM-DD-project-slug` and not `<YYYY-MM-DD>-<project-slug>`.

## Policy

- Use this central library by default for exploratory analysis, reviews, and learning.
- Do not write artifacts into the analyzed target project unless explicitly requested.
- If target-local notes are needed later, copy or regenerate the relevant analysis under `TARGET/docs/understanding/`.
