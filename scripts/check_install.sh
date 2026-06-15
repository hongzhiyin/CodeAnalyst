#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${CODE_ANALYST_CLI:-$ROOT/.venv/bin/code-analyst}"

PYTHONPATH="$ROOT/src" python3 -m code_analyst.cli doctor
PYTHONPATH="$ROOT/src" python3 -m unittest discover -s "$ROOT/tests"
test -x "$CLI"
"$CLI" --version
"$CLI" sync-skill --targets codex --dry-run
test -f "${CODEX_HOME:-$HOME/.codex}/skills/code-analyst/SKILL.md"
test -x "${CODEX_HOME:-$HOME/.codex}/skills/code-analyst/bin/code-analyst"
test -f "${AGENTS_HOME:-$HOME/.agents}/skills/code-analyst/SKILL.md"
test -x "${AGENTS_HOME:-$HOME/.agents}/skills/code-analyst/bin/code-analyst"
