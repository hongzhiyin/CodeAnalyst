# Analyses

This directory is the central library for generated CodeAnalyst packs.

Git policy:

- Generated analysis runs are ignored by default.
- Curated analysis packs may be explicitly unignored in the root `.gitignore`.
- Static `site/` outputs and `*-manual.json` scratch checks are not tracked because they can be regenerated with `code-analyst visual-pack` or `code-analyst render-site`.

Currently tracked curated pack:

- `2026-06-10-code-analyst-framework-import-graph/`
