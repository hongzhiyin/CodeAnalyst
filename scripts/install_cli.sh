#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VENV_DIR=${CODE_ANALYST_VENV_DIR:-"$ROOT/.venv"}
BIN_DIR="$VENV_DIR/bin"
BIN="$BIN_DIR/code-analyst"
LEGACY_BIN_DIR=${CODE_ANALYST_LEGACY_BIN_DIR:-/opt/homebrew/bin}

mkdir -p "$BIN_DIR"

cat > "$BIN" <<EOF
#!/usr/bin/env sh
CODE_ANALYST_PROJECT_DIR="$ROOT" CODE_ANALYST_CLI_PROG="code-analyst" PYTHONPATH="$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m code_analyst.cli "\$@"
EOF

chmod +x "$BIN"

for legacy in cbu codeanalyst codebase-understanding code-analyst; do
  legacy_path="$LEGACY_BIN_DIR/$legacy"
  if [ -f "$legacy_path" ] && grep -q 'python3 -m code_analyst.cli' "$legacy_path" 2>/dev/null; then
    rm -f "$legacy_path"
    echo "Removed legacy global wrapper at $legacy_path"
  fi
done

echo "Installed code-analyst wrapper at $BIN"
echo "Try: $BIN doctor"
