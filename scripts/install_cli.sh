#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${CBU_BIN_DIR:-/opt/homebrew/bin}"

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/cbu" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m codebase_understanding.cli "\$@"
EOF

cat > "$BIN_DIR/codebase-understanding" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m codebase_understanding.cli "\$@"
EOF

chmod +x "$BIN_DIR/cbu" "$BIN_DIR/codebase-understanding"
echo "Installed cbu and codebase-understanding wrappers in $BIN_DIR"
