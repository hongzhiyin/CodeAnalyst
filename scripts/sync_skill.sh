#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${CODEX_HOME:-$HOME/.codex}/skills/code-analyst"
OLD_TARGET="${CODEX_HOME:-$HOME/.codex}/skills/codebase-understanding"
MARKER=".code-analyst-skill-source"

if [ -e "$TARGET" ] && [ ! -f "$TARGET/$MARKER" ]; then
  if [ "${1:-}" != "--force" ]; then
    echo "$TARGET exists; pass --force to replace the installed skill copy" >&2
    exit 2
  fi
fi

if [ "${1:-}" = "--force" ]; then
  shift
fi

if [ -d "$OLD_TARGET" ]; then
  if [ -f "$OLD_TARGET/.cbu-skill-source" ] || [ -f "$OLD_TARGET/$MARKER" ]; then
    rm -rf "$OLD_TARGET"
  else
    echo "Skipping removal of unmarked legacy skill at $OLD_TARGET" >&2
  fi
fi

rm -rf "$TARGET"
mkdir -p "$TARGET"
cp -R "$ROOT/skill/." "$TARGET/"
printf '%s\n' "$ROOT" > "$TARGET/$MARKER"

mkdir -p "$TARGET/bin"
cat > "$TARGET/bin/code-analyst" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export CODE_ANALYST_PROJECT_DIR="$ROOT"
export CODE_ANALYST_CLI_PROG="code-analyst"
export PYTHONPATH="$ROOT/src"
exec python3 -m code_analyst.cli "\$@"
EOF
chmod +x "$TARGET/bin/code-analyst"

echo "Synced skill files to $TARGET"
echo "Installed skill-local wrapper at $TARGET/bin/code-analyst"
