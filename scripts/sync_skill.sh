#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${CODEX_HOME:-$HOME/.codex}/skills/codebase-understanding"

mkdir -p "$TARGET"
cp "$ROOT/skill/SKILL.md" "$TARGET/SKILL.md"
mkdir -p "$TARGET/references"
cp "$ROOT/skill/references/quick-learning-framework.md" "$TARGET/references/quick-learning-framework.md"
mkdir -p "$TARGET/scripts"
cp "$ROOT/src/codebase_understanding/render_site.py" "$TARGET/scripts/render_understanding_site.py"
chmod +x "$TARGET/scripts/render_understanding_site.py"

echo "Synced skill files to $TARGET"
