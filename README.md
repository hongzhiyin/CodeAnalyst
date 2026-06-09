# CodeAnalyst

Personal code analysis assistant and agent-friendly CLI.

CodeAnalyst helps read unfamiliar projects, explain what each part does, map
how flows connect, and propose review, refactor, and architecture directions.
It does not normally modify analyzed projects; implementation work should happen
in each target project's own repo.

Naming note: **CodeAnalyst** is the product/display name. The CLI is
`code-analyst`, and the source checkout is `/Users/chihoyo/Project/CodeAnalyst`.

This repository is both:

- the source checkout for the `code-analyst` skill and CLI
- the central library for generated analysis packs under `analyses/`

## Quick Start

```bash
./scripts/install_cli.sh
code-analyst doctor
code-analyst flow-map /path/to/project
code-analyst script-check /path/to/project
code-analyst pack /path/to/project
code-analyst review-pack /path/to/project
code-analyst review-pack --from-pack /path/to/analysis-pack
code-analyst visual-pack /path/to/project
code-analyst visual-pack /path/to/project --verify-site
code-analyst verify-site /path/to/analysis-pack/site
```

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
./scripts/check_install.sh
./scripts/sync_skill.sh --force
```

After source changes, run the full local lifecycle:

```bash
./scripts/update_cli.sh --force
```

## Project Map

| Path | Purpose |
|---|---|
| `docs/` | SPEC / ARCHITECTURE / ROADMAP / DECISIONS source of truth |
| `src/code_analyst/` | Deterministic CLI implementation |
| `skill/` | Source skill copied into installed agent skill homes |
| `scripts/` | Install, sync, check, and update wrappers |
| `tests/` | Focused regression tests |
| `analyses/` | Generated and curated CodeAnalyst packs |

Generated analysis runs are ignored by default. Curated packs may be explicitly
unignored in `.gitignore`.

## Documentation Map

| File | Contents |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | Rules, invariants, output contract, and success criteria |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Current source/installed shape, layers, modules, and data flow |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Current progress, steps, tasks, and acceptance criteria |
| [docs/DECISIONS.md](docs/DECISIONS.md) | D-XXX trade-off log |
