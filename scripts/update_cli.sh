#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/install_cli.sh"
PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s "$ROOT/tests"
"$ROOT/.venv/bin/code-analyst" sync-skill "$@"
"$ROOT/scripts/check_install.sh"
