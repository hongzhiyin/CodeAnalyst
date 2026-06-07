#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$ROOT/src" python3 -m codebase_understanding.cli doctor
PYTHONPATH="$ROOT/src" python3 -m unittest discover -s "$ROOT/tests"
command -v cbu >/dev/null
cbu --version
