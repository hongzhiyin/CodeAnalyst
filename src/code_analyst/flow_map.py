"""Project-kind aware flow and entrypoint discovery."""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .inventory import collect_files, rel


SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
FRONTEND_EXTS = {".jsx", ".tsx", ".vue", ".svelte"}
TEXT_EXTS = SOURCE_EXTS | FRONTEND_EXTS | {".json", ".html", ".toml"}
CONTROL_RE = re.compile(r"<(button|form|input|select|textarea)\b([^>]*)>", re.IGNORECASE | re.DOTALL)
HANDLER_RE = re.compile(r"\b(on[A-Z][A-Za-z0-9_]*)\s*=")
STATE_RE = re.compile(r"\b(useState|useReducer|createContext|useStore|zustand|redux)\b")
ROUTE_FILE_RE = re.compile(r"(^|/)(pages|app)/.*\.(jsx|tsx|js|ts)$")


def _read_text(path: Path, limit: int = 300000) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _is_test_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return "tests" in parts or "test" in parts or path.name.startswith(("test_", "spec_"))


def _python_markers(path: Path) -> dict[str, bool]:
    text = _read_text(path)
    markers = {
        "argparse": False,
        "click": False,
        "typer": False,
        "main_guard": False,
        "fastapi": False,
        "flask": False,
        "django": False,
        "uvicorn": False,
    }
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return markers

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".", 1)[0]
                if root_name in markers:
                    markers[root_name] = True
        elif isinstance(node, ast.ImportFrom):
            root_name = (node.module or "").split(".", 1)[0]
            if root_name in markers:
                markers[root_name] = True
        elif isinstance(node, ast.If):
            if _is_main_guard(node):
                markers["main_guard"] = True
        elif isinstance(node, ast.Call):
            func_dump = ast.dump(node.func)
            if "FastAPI" in func_dump:
                markers["fastapi"] = True
            if "Flask" in func_dump:
                markers["flask"] = True
    return markers


def _is_main_guard(node: ast.If) -> bool:
    compare = node.test
    if not isinstance(compare, ast.Compare):
        return False
    if not isinstance(compare.left, ast.Name) or compare.left.id != "__name__":
        return False
    if not any(isinstance(op, ast.Eq) for op in compare.ops):
        return False
    return any(isinstance(comparator, ast.Constant) and comparator.value == "__main__" for comparator in compare.comparators)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _flow(flow_id: str, kind: str, title: str, confidence: str, evidence: list[str], entrypoints: list[str] | None = None, next_steps: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": flow_id,
        "kind": kind,
        "title": title,
        "confidence": confidence,
        "entrypoints": entrypoints or [],
        "evidence": evidence,
        "next_steps": next_steps or [],
    }


def _python_cli_flows(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    flows: list[dict[str, Any]] = []
    for path in files:
        if path.suffix != ".py":
            continue
        if _is_test_path(path):
            continue
        markers = _python_markers(path)
        relative = rel(path, root)
        score = 0
        evidence: list[str] = []
        if path.name in {"cli.py", "__main__.py", "main.py"}:
            score += 2
            evidence.append(f"`{relative}` has CLI-like filename.")
        if markers["argparse"] or markers["click"] or markers["typer"] or markers["main_guard"]:
            score += 2
            evidence.append(f"`{relative}` contains CLI/runtime markers.")
        if score:
            flows.append(
                _flow(
                    f"python-cli-{relative}",
                    "python-cli",
                    f"Python CLI/runtime entry: {relative}",
                    "high" if score >= 3 else "medium",
                    evidence,
                    [relative],
                    ["Read argument parsing and dispatch functions, then follow imported helpers."],
                )
            )
    return flows[:20]


def _python_service_flows(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    flows: list[dict[str, Any]] = []
    for path in files:
        if path.suffix != ".py":
            continue
        if _is_test_path(path):
            continue
        markers = _python_markers(path)
        relative = rel(path, root)
        found = []
        if markers["fastapi"]:
            found.append("FastAPI service")
        if markers["flask"]:
            found.append("Flask service")
        if markers["django"]:
            found.append("Django app")
        if markers["uvicorn"]:
            found.append("ASGI server")
        if found or path.name in {"server.py", "app.py"}:
            flows.append(
                _flow(
                    f"python-service-{relative}",
                    "service",
                    f"Python service candidate: {relative}",
                    "medium",
                    [f"`{relative}` contains service markers: {', '.join(found) or path.name}."],
                    [relative],
                    ["Check route registration, request handlers, and startup command before assuming runtime behavior."],
                )
            )
    return flows[:20]


def _node_package_flows(root: Path) -> list[dict[str, Any]]:
    package = _load_json(root / "package.json")
    flows: list[dict[str, Any]] = []
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    for name, command in sorted(scripts.items()):
        if not isinstance(command, str):
            continue
        kind = "frontend" if any(token in command for token in ("vite", "next", "astro", "svelte", "vue")) else "node-script"
        flows.append(
            _flow(
                f"package-script-{name}",
                kind,
                f"package script: {name}",
                "medium",
                [f"`package.json` script `{name}` runs `{command}`."],
                ["package.json"],
                ["Use script-check results to confirm referenced files before running it."],
            )
        )
    bins = package.get("bin")
    if isinstance(bins, str):
        flows.append(_flow("package-bin-default", "node-cli", "Node CLI bin", "high", [f"`package.json` bin points to `{bins}`."], [bins]))
    elif isinstance(bins, dict):
        for name, target in sorted(bins.items()):
            if isinstance(target, str):
                flows.append(_flow(f"package-bin-{name}", "node-cli", f"Node CLI bin: {name}", "high", [f"`package.json` bin `{name}` points to `{target}`."], [target]))
    return flows[:30]


def _frontend_flows(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    flows: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() not in FRONTEND_EXTS and path.name not in {"App.jsx", "App.tsx", "main.jsx", "main.tsx"}:
            continue
        text = _read_text(path)
        relative = rel(path, root)
        handlers = sorted(set(HANDLER_RE.findall(text)))
        controls = [match[0].lower() for match in CONTROL_RE.findall(text)]
        state_markers = sorted(set(STATE_RE.findall(text)))
        is_route = bool(ROUTE_FILE_RE.search(relative))
        if handlers or controls or state_markers or is_route or path.name.startswith(("App.", "main.")):
            evidence = []
            if is_route:
                evidence.append(f"`{relative}` matches a route-like pages/app path.")
            if handlers:
                evidence.append(f"`{relative}` contains handlers: {', '.join(handlers[:8])}.")
            if controls:
                counts = Counter(controls)
                evidence.append("Controls: " + ", ".join(f"{name}={count}" for name, count in sorted(counts.items())))
            if state_markers:
                evidence.append(f"State markers: {', '.join(state_markers)}.")
            flows.append(
                _flow(
                    f"frontend-{relative}",
                    "frontend-ui",
                    f"Frontend UI path: {relative}",
                    "medium",
                    evidence,
                    [relative],
                    ["Trace handlers into state updates, API calls, and rendered output."],
                )
            )
    return flows[:40]


def _codex_skill_flows(root: Path) -> list[dict[str, Any]]:
    skill = root / "SKILL.md"
    if not skill.exists():
        return []
    entries = ["SKILL.md"]
    if (root / "agents" / "openai.yaml").exists():
        entries.append("agents/openai.yaml")
    if (root / "bin").exists():
        entries.append("bin/")
    return [
        _flow(
            "codex-skill",
            "skill",
            "Codex skill invocation flow",
            "high",
            ["`SKILL.md` exists and defines the agent-facing workflow."],
            entries,
            ["Read SKILL.md first; then inspect referenced scripts, references, agents, and wrappers."],
        )
    ]


def create_flow_map(target: Path | str, max_files: int = 3000) -> dict[str, Any]:
    root = Path(target).expanduser().resolve()
    if root.is_file():
        root = root.parent
    if not root.exists():
        raise FileNotFoundError(f"Target does not exist: {root}")

    files = [path for path in collect_files(root, max_files=max_files) if path.suffix.lower() in TEXT_EXTS or path.name in {"package.json", "pyproject.toml", "SKILL.md"}]
    flows: list[dict[str, Any]] = []
    flows.extend(_codex_skill_flows(root))
    flows.extend(_node_package_flows(root))
    flows.extend(_python_cli_flows(root, files))
    flows.extend(_python_service_flows(root, files))
    flows.extend(_frontend_flows(root, files))

    kind_counts = Counter(flow["kind"] for flow in flows)
    confidence_counts = Counter(flow["confidence"] for flow in flows)
    return {
        "target": str(root),
        "file_count_scanned": len(files),
        "truncated": len(files) >= max_files,
        "summary": {
            "flow_count": len(flows),
            "kind_counts": dict(sorted(kind_counts.items())),
            "confidence_counts": dict(sorted(confidence_counts.items())),
        },
        "flows": flows,
    }


def write_flow_map(flow_map: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(flow_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def flow_map_summary(flow_map: dict[str, Any]) -> str:
    lines = [
        f"Target: {flow_map['target']}",
        f"Flows: {flow_map['summary']['flow_count']}",
    ]
    if flow_map["summary"]["kind_counts"]:
        lines.append("Kinds: " + ", ".join(f"{k}={v}" for k, v in flow_map["summary"]["kind_counts"].items()))
    for flow in flow_map["flows"][:24]:
        entries = ", ".join(flow.get("entrypoints", [])[:3])
        suffix = f" ({entries})" if entries else ""
        lines.append(f"- [{flow['kind']}/{flow['confidence']}] {flow['title']}{suffix}")
    if len(flow_map["flows"]) > 24:
        lines.append(f"... {len(flow_map['flows']) - 24} more flows")
    return "\n".join(lines)
