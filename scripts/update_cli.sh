#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT/scripts/install_cli.sh"
PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s "$ROOT/tests"
"$ROOT/scripts/sync_skill.sh" "$@"
"$ROOT/scripts/check_install.sh"
