#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKER=".code-analyst-skill-source"
FORCE=0
TARGETS="${CODE_ANALYST_SYNC_TARGETS:-codex,agents}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force)
      FORCE=1
      shift
      ;;
    --targets)
      TARGETS="${2:?--targets requires a comma-separated target list}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

target_dir() {
  case "$1" in
    codex)
      printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/skills/code-analyst"
      ;;
    agents)
      printf '%s\n' "${AGENTS_HOME:-$HOME/.agents}/skills/code-analyst"
      ;;
    *)
      echo "Unknown sync target: $1" >&2
      exit 2
      ;;
  esac
}

old_target_dir() {
  case "$1" in
    codex)
      printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/skills/codebase-understanding"
      ;;
    agents)
      printf '%s\n' "${AGENTS_HOME:-$HOME/.agents}/skills/codebase-understanding"
      ;;
    *)
      echo "Unknown sync target: $1" >&2
      exit 2
      ;;
  esac
}

sync_one() {
  local name="$1"
  local target
  local old_target
  target="$(target_dir "$name")"
  old_target="$(old_target_dir "$name")"

  if [ -e "$target" ] && [ ! -f "$target/$MARKER" ]; then
    if [ "$FORCE" -ne 1 ]; then
      echo "$target exists; pass --force to replace the installed skill copy" >&2
      exit 2
    fi
  fi

  if [ -d "$old_target" ]; then
    if [ -f "$old_target/.cbu-skill-source" ] || [ -f "$old_target/$MARKER" ]; then
      rm -rf "$old_target"
    else
      echo "Skipping removal of unmarked legacy skill at $old_target" >&2
    fi
  fi

  rm -rf "$target"
  mkdir -p "$target"
  cp -R "$ROOT/skill/." "$target/"
  printf '%s\n' "$ROOT" > "$target/$MARKER"

  mkdir -p "$target/bin"
  cat > "$target/bin/code-analyst" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export CODE_ANALYST_PROJECT_DIR="$ROOT"
export CODE_ANALYST_CLI_PROG="code-analyst"
export PYTHONPATH="$ROOT/src"
exec python3 -m code_analyst.cli "\$@"
EOF
  chmod +x "$target/bin/code-analyst"

  echo "Synced $name skill files to $target"
  echo "Installed $name skill-local wrapper at $target/bin/code-analyst"
}

IFS=',' read -r -a target_names <<< "$TARGETS"
for target_name in "${target_names[@]}"; do
  if [ -n "$target_name" ]; then
    sync_one "$target_name"
  else
    echo "Empty sync target in --targets list" >&2
    exit 2
  fi
done
