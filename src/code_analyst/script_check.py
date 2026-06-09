"""Static checks for declared project scripts and command entrypoints."""

from __future__ import annotations

import json
import re
import shlex
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


FILE_TOKEN_RE = re.compile(r"(?<![@\w/-])([A-Za-z0-9_./-]+\.(?:js|mjs|cjs|ts|tsx|py|sh|html|json|toml|yaml|yml))")
KNOWN_TOOL_COMMANDS = {
    "astro",
    "bash",
    "bun",
    "cargo",
    "deno",
    "docker",
    "eslint",
    "go",
    "jest",
    "make",
    "next",
    "node",
    "npm",
    "npx",
    "pnpm",
    "python",
    "python3",
    "pytest",
    "tsc",
    "tsx",
    "vite",
    "vitest",
    "yarn",
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _check(status: str, source: str, name: str, target: str | None, detail: str, evidence: str | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "source": source,
        "name": name,
        "target": target,
        "detail": detail,
        "evidence": evidence,
    }


def _module_to_candidates(root: Path, module: str) -> list[Path]:
    parts = module.split(".")
    candidates = [
        root.joinpath(*parts).with_suffix(".py"),
        root.joinpath(*parts) / "__init__.py",
        root / "src" / Path(*parts).with_suffix(".py"),
        root / "src" / Path(*parts) / "__init__.py",
    ]
    return candidates


def _check_python_entrypoint(root: Path, source: str, name: str, value: str) -> dict[str, Any]:
    module = value.split(":", 1)[0].strip()
    if not module:
        return _check("warn", source, name, value, "Python entrypoint is empty.", value)
    for candidate in _module_to_candidates(root, module):
        if candidate.exists():
            return _check("ok", source, name, candidate.relative_to(root).as_posix(), "Python entrypoint module exists.", value)
    return _check("missing", source, name, module, "Python entrypoint module was not found under root or src/.", value)


def _script_file_checks(root: Path, source: str, name: str, command: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for match in FILE_TOKEN_RE.finditer(command):
        token = match.group(1).strip("./")
        if token.startswith(("http", "node_modules")):
            continue
        candidate = root / token
        status = "ok" if candidate.exists() else "missing"
        detail = "Referenced file exists." if status == "ok" else "Referenced file was not found."
        checks.append(_check(status, source, name, token, detail, command))
    return checks


def _script_command_check(source: str, name: str, command: str) -> dict[str, Any] | None:
    try:
        parts = shlex.split(command)
    except ValueError:
        return _check("warn", source, name, None, "Could not parse script command with shlex.", command)
    if not parts:
        return _check("warn", source, name, None, "Script command is empty.", command)
    command_name = parts[0]
    if "=" in command_name and len(parts) > 1:
        command_name = parts[1]
    if command_name in KNOWN_TOOL_COMMANDS or command_name.startswith(("./", "../")):
        return None
    if command_name.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx", ".py", ".sh")):
        return None
    return _check("info", source, name, command_name, "Command name is not verified; it may be provided by dependencies or PATH.", command)


def check_scripts(target: Path | str) -> dict[str, Any]:
    root = Path(target).expanduser().resolve()
    if root.is_file():
        root = root.parent
    if not root.exists():
        raise FileNotFoundError(f"Target does not exist: {root}")

    checks: list[dict[str, Any]] = []
    package = _load_json(root / "package.json")
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    for name, command in sorted(scripts.items()):
        if not isinstance(command, str):
            checks.append(_check("warn", "package.json scripts", name, None, "Script value is not a string.", str(command)))
            continue
        file_checks = _script_file_checks(root, "package.json scripts", name, command)
        checks.extend(file_checks)
        command_check = _script_command_check("package.json scripts", name, command)
        if command_check:
            checks.append(command_check)
        if not file_checks and not command_check:
            checks.append(_check("ok", "package.json scripts", name, None, "No missing file references found.", command))

    bins = package.get("bin")
    if isinstance(bins, str):
        candidate = root / bins
        checks.append(
            _check("ok" if candidate.exists() else "missing", "package.json bin", Path(root).name, bins, "Node bin target exists." if candidate.exists() else "Node bin target was not found.", bins)
        )
    elif isinstance(bins, dict):
        for name, target_path in sorted(bins.items()):
            if not isinstance(target_path, str):
                continue
            candidate = root / target_path
            checks.append(
                _check("ok" if candidate.exists() else "missing", "package.json bin", name, target_path, "Node bin target exists." if candidate.exists() else "Node bin target was not found.", target_path)
            )

    pyproject = _load_toml(root / "pyproject.toml")
    project_scripts = pyproject.get("project", {}).get("scripts", {})
    if isinstance(project_scripts, dict):
        for name, value in sorted(project_scripts.items()):
            if isinstance(value, str):
                checks.append(_check_python_entrypoint(root, "pyproject project.scripts", name, value))

    poetry_scripts = pyproject.get("tool", {}).get("poetry", {}).get("scripts", {})
    if isinstance(poetry_scripts, dict):
        for name, value in sorted(poetry_scripts.items()):
            if isinstance(value, str):
                checks.append(_check_python_entrypoint(root, "pyproject tool.poetry.scripts", name, value))

    status_counts = Counter(item["status"] for item in checks)
    return {
        "target": str(root),
        "summary": {
            "check_count": len(checks),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "checks": checks,
    }


def write_script_check(report: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def script_check_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Target: {report['target']}",
        f"Checks: {report['summary']['check_count']}",
    ]
    if report["summary"]["status_counts"]:
        lines.append("Statuses: " + ", ".join(f"{k}={v}" for k, v in report["summary"]["status_counts"].items()))
    for item in report["checks"][:24]:
        target = f" -> {item['target']}" if item.get("target") else ""
        lines.append(f"- [{item['status']}] {item['source']}:{item['name']}{target}: {item['detail']}")
    if len(report["checks"]) > 24:
        lines.append(f"... {len(report['checks']) - 24} more checks")
    return "\n".join(lines)
