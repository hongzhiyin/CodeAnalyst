"""File-level import graph extraction for Python and JS/TS projects."""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .inventory import collect_files, rel


PY_EXTS = {".py"}
JS_EXTS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
SUPPORTED_EXTS = PY_EXTS | JS_EXTS

IMPORT_RE = re.compile(
    r"""
    (?:
      import\s+(?:[^'";]+?\s+from\s+)?["']([^"']+)["']
      |
      export\s+(?:[^'";]+?\s+from\s+)?["']([^"']+)["']
      |
      require\(\s*["']([^"']+)["']\s*\)
      |
      import\(\s*["']([^"']+)["']\s*\)
    )
    """,
    re.VERBOSE,
)


def _read_text(path: Path, limit: int = 400000) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _source_files(root: Path, max_files: int) -> list[Path]:
    return [path for path in collect_files(root, max_files=max_files) if path.suffix.lower() in SUPPORTED_EXTS]


def _python_module_index(root: Path, files: list[Path]) -> dict[str, str]:
    index: dict[str, str] = {}
    for path in files:
        if path.suffix.lower() not in PY_EXTS:
            continue
        relative = rel(path, root)
        without_ext = relative[:-3]
        parts = without_ext.split("/")
        if parts[-1] == "__init__":
            module = ".".join(parts[:-1])
            if module:
                index[module] = relative
        else:
            index[".".join(parts)] = relative
        if parts and parts[0] == "src" and len(parts) > 1:
            src_parts = parts[1:]
            if src_parts[-1] == "__init__":
                src_module = ".".join(src_parts[:-1])
                if src_module:
                    index[src_module] = relative
            else:
                index[".".join(src_parts)] = relative
    return index


def _js_module_index(root: Path, files: list[Path]) -> dict[str, str]:
    index: dict[str, str] = {}
    for path in files:
        if path.suffix.lower() not in JS_EXTS:
            continue
        relative = rel(path, root)
        path_no_ext = relative[: -len(path.suffix)]
        index[path_no_ext] = relative
        if path.name.startswith("index."):
            index[str(Path(path_no_ext).parent).replace("\\", "/")] = relative
    return index


def _resolve_python_import(
    source: Path,
    root: Path,
    module: str,
    level: int,
    index: dict[str, str],
) -> tuple[str | None, str]:
    if level <= 0:
        return index.get(module), "internal" if module in index else "external"

    source_rel = rel(source, root)
    package_parts = source_rel[:-3].split("/")[:-1]
    # One leading dot means current package; two means parent package.
    prefix_parts = package_parts[: max(0, len(package_parts) - (level - 1))]
    target = ".".join(part for part in [*prefix_parts, module] if part)
    if target in index:
        return index[target], "internal"
    if module:
        for candidate in index:
            if candidate == target or candidate.startswith(target + "."):
                return index[candidate], "internal"
    return None, "relative-unresolved"


def _python_edges(path: Path, root: Path, index: dict[str, str]) -> list[dict[str, Any]]:
    text = _read_text(path)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [
            {
                "from": rel(path, root),
                "to": None,
                "module": None,
                "kind": "parse_error",
                "language": "python",
                "line": exc.lineno,
                "detail": str(exc),
            }
        ]

    edges: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                target, scope = _resolve_python_import(path, root, module, 0, index)
                edges.append(
                    {
                        "from": rel(path, root),
                        "to": target,
                        "module": module,
                        "kind": "imports",
                        "language": "python",
                        "scope": scope,
                        "line": getattr(node, "lineno", None),
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            target, scope = _resolve_python_import(path, root, module, node.level, index)
            edges.append(
                {
                    "from": rel(path, root),
                    "to": target,
                    "module": "." * node.level + module,
                    "kind": "imports",
                    "language": "python",
                    "scope": scope,
                    "line": getattr(node, "lineno", None),
                }
            )
    return edges


def _resolve_js_import(source: Path, root: Path, specifier: str, index: dict[str, str]) -> tuple[str | None, str]:
    if not specifier.startswith((".", "/")):
        return None, "external"

    source_dir = Path(rel(source.parent, root))
    if specifier.startswith("/"):
        candidate = Path(specifier.lstrip("/"))
    else:
        candidate = source_dir / specifier
    normalized = candidate.as_posix()
    normalized = re.sub(r"/+", "/", normalized)

    checks = [normalized]
    checks.extend(f"{normalized}{ext}" for ext in JS_EXTS)
    checks.extend(f"{normalized}/index{ext}" for ext in JS_EXTS)

    for check in checks:
        key = check
        suffix = Path(check).suffix
        if suffix in JS_EXTS:
            key = check[: -len(suffix)]
        if key in index:
            return index[key], "internal"
        if check in index.values():
            return check, "internal"
    return None, "relative-unresolved"


def _js_edges(path: Path, root: Path, index: dict[str, str]) -> list[dict[str, Any]]:
    text = _read_text(path)
    edges: list[dict[str, Any]] = []
    for match in IMPORT_RE.finditer(text):
        specifier = next(group for group in match.groups() if group)
        target, scope = _resolve_js_import(path, root, specifier, index)
        line = text.count("\n", 0, match.start()) + 1
        edges.append(
            {
                "from": rel(path, root),
                "to": target,
                "module": specifier,
                "kind": "imports",
                "language": "javascript",
                "scope": scope,
                "line": line,
            }
        )
    return edges


def create_import_graph(target: Path | str, max_files: int = 3000) -> dict[str, Any]:
    root = Path(target).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Target does not exist: {root}")
    if root.is_file():
        root = root.parent

    files = _source_files(root, max_files=max_files)
    py_index = _python_module_index(root, files)
    js_index = _js_module_index(root, files)

    edges: list[dict[str, Any]] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix in PY_EXTS:
            edges.extend(_python_edges(path, root, py_index))
        elif suffix in JS_EXTS:
            edges.extend(_js_edges(path, root, js_index))

    scope_counts = Counter(edge.get("scope", "unknown") for edge in edges)
    language_counts = Counter(edge.get("language", "unknown") for edge in edges)
    internal_edges = [edge for edge in edges if edge.get("scope") == "internal" and edge.get("to")]
    return {
        "target": str(root),
        "file_count_scanned": len(files),
        "truncated": len(files) >= max_files,
        "summary": {
            "edge_count": len(edges),
            "internal_edge_count": len(internal_edges),
            "scope_counts": dict(sorted(scope_counts.items())),
            "language_counts": dict(sorted(language_counts.items())),
        },
        "files": [rel(path, root) for path in files],
        "edges": edges,
    }


def write_import_graph(graph: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def import_graph_summary(graph: dict[str, Any]) -> str:
    summary = graph["summary"]
    lines = [
        f"Target: {graph['target']}",
        f"Source files scanned: {graph['file_count_scanned']}{' (truncated)' if graph['truncated'] else ''}",
        f"Import edges: {summary['edge_count']}",
        f"Internal edges: {summary['internal_edge_count']}",
    ]
    if summary["language_counts"]:
        lines.append("Languages: " + ", ".join(f"{k}={v}" for k, v in summary["language_counts"].items()))
    if summary["scope_counts"]:
        lines.append("Scopes: " + ", ".join(f"{k}={v}" for k, v in summary["scope_counts"].items()))
    for edge in graph["edges"][:20]:
        target = edge.get("to") or edge.get("module") or "unknown"
        lines.append(f"- {edge['from']} -> {target} [{edge.get('scope')}]")
    if len(graph["edges"]) > 20:
        lines.append(f"... {len(graph['edges']) - 20} more edges")
    return "\n".join(lines)
