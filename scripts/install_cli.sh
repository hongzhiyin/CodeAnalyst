#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${CODE_ANALYST_BIN_DIR:-/opt/homebrew/bin}"

mkdir -p "$BIN_DIR"

rm -f "$BIN_DIR/cbu" "$BIN_DIR/codeanalyst" "$BIN_DIR/codebase-understanding" "$BIN_DIR/code-analyst"

cat > "$BIN_DIR/code-analyst" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export CODE_ANALYST_PROJECT_DIR="$ROOT"
export CODE_ANALYST_CLI_PROG="code-analyst"
export PYTHONPATH="$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m code_analyst.cli "\$@"
EOF

chmod +x "$BIN_DIR/code-analyst"
echo "Installed code-analyst wrapper in $BIN_DIR"
