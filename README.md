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
- the source copied into global user skills under `~/.agents/skills/code-analyst`
  and the Codex runtime copy under `~/.codex/skills/code-analyst`

## Native Install

```bash
curl -fsSL https://github.com/hongzhiyin/CodeAnalyst/releases/latest/download/install_remote.sh | sh
~/.local/bin/code-analyst doctor
~/.local/bin/code-analyst update
```

The native installer uses GitHub Releases, installs under
`~/.local/share/code-analyst`, writes `~/.local/bin/code-analyst`, and refreshes
installed skill copies by default.

## Source Checkout Development

```bash
./scripts/install_cli.sh
./.venv/bin/code-analyst doctor
./.venv/bin/code-analyst sync-skill --targets codex,agents --force
```

The source checkout install is intentionally project-local. It no longer writes
a global `/opt/homebrew/bin/code-analyst` wrapper.

## Common Commands

```bash
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
./.venv/bin/code-analyst sync-skill --targets codex,agents --force
./scripts/package_release.sh
```

After source changes, run the full local lifecycle:

```bash
./scripts/update_cli.sh --force
```

`update_cli.sh` installs the project-local CLI wrapper, runs tests, and syncs both skill
copies so Codex app skill discovery and existing Codex runtime paths stay in
step.

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
