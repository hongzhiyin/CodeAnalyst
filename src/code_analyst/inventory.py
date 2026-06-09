"""Deterministic inventory helpers for unfamiliar codebases."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    ".turbo",
    ".cache",
    "node_modules",
    "bower_components",
    "dist",
    "build",
    "coverage",
    "target",
    "analyses",
    "_generated",
    ".venv",
    "venv",
    "env",
}

MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "settings.gradle",
    "composer.json",
    "Gemfile",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "next.config.js",
    "next.config.mjs",
    "tsconfig.json",
    ".codex-plugin/plugin.json",
    "SKILL.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
}

ENTRYPOINT_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "cli.py",
    "__main__.py",
    "index.js",
    "index.ts",
    "index.tsx",
    "main.js",
    "main.ts",
    "main.tsx",
    "App.tsx",
    "App.jsx",
    "index.html",
    "SKILL.md",
}


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".DS_Store")


def should_skip_file(name: str) -> bool:
    return name in {".DS_Store"} or name.endswith(".pyc")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text_prefix(path: Path, limit: int = 12000) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def collect_files(root: Path, max_files: int = 3000) -> list[Path]:
    files: list[Path] = []
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = sorted(d for d in dir_names if not should_skip_dir(d))
        current = Path(current_root)
        for file_name in sorted(file_names):
            if should_skip_file(file_name):
                continue
            path = current / file_name
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def build_tree(files: list[Path], root: Path, max_depth: int) -> dict[str, Any]:
    tree: dict[str, Any] = {}
    for path in files:
        parts = rel(path, root).split("/")
        cursor = tree
        for part in parts[: max_depth + 1]:
            cursor = cursor.setdefault(part, {})
    return tree


def compact_tree_lines(tree: dict[str, Any], indent: str = "", limit: int = 160) -> list[str]:
    lines: list[str] = []
    for index, key in enumerate(sorted(tree.keys())):
        if len(lines) >= limit:
            lines.append(f"{indent}...")
            break
        marker = "`- " if index == len(tree) - 1 else "|- "
        lines.append(f"{indent}{marker}{key}")
        child = tree[key]
        if child:
            next_indent = indent + ("   " if index == len(tree) - 1 else "|  ")
            lines.extend(compact_tree_lines(child, next_indent, limit - len(lines)))
    return lines


def detect_project_types(root: Path, files: list[Path]) -> list[str]:
    names = {rel(p, root) for p in files}
    base_names = {p.name for p in files}
    types: list[str] = []

    if "SKILL.md" in base_names:
        types.append("Codex skill")
    if ".codex-plugin/plugin.json" in names:
        types.append("Codex plugin")

    package_text = ""
    if "package.json" in base_names:
        for path in files:
            if path.name == "package.json":
                package_text = read_text_prefix(path)
                break
        if any(token in package_text for token in ("react", "vite", "next", "vue", "svelte")):
            types.append("frontend app")
        if any(token in package_text for token in ("express", "fastify", "koa", "hono", "nestjs")):
            types.append("Node service")
        if '"bin"' in package_text:
            types.append("Node CLI")
        if not types:
            types.append("Node or web project")

    if "pyproject.toml" in base_names or "requirements.txt" in base_names:
        types.append("Python project")
    if "Cargo.toml" in base_names:
        types.append("Rust project")
    if "go.mod" in base_names:
        types.append("Go project")
    if "pom.xml" in base_names or "build.gradle" in base_names:
        types.append("Java project")
    if any(p.suffix.lower() == ".ipynb" for p in files):
        types.append("notebook project")

    return sorted(set(types)) or ["unknown or mixed project"]


def create_inventory(target: Path | str, max_files: int = 3000, tree_depth: int = 3) -> dict[str, Any]:
    root = Path(target).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Target does not exist: {root}")
    if root.is_file():
        root = root.parent

    files = collect_files(root, max_files)
    ext_counts = Counter((p.suffix.lower() or "[no extension]") for p in files)
    by_top_dir: dict[str, int] = defaultdict(int)
    for path in files:
        parts = rel(path, root).split("/")
        by_top_dir[parts[0] if len(parts) == 1 else parts[0] + "/"] += 1

    manifests: list[str] = []
    entrypoints: list[str] = []
    for path in files:
        relative = rel(path, root)
        if path.name in MANIFEST_NAMES or relative in MANIFEST_NAMES:
            manifests.append(relative)
        if path.name in ENTRYPOINT_NAMES:
            entrypoints.append(relative)

    tree = build_tree(files, root, tree_depth)
    return {
        "root": str(root),
        "file_count_scanned": len(files),
        "truncated": len(files) >= max_files,
        "project_types": detect_project_types(root, files),
        "manifests": sorted(set(manifests)),
        "entrypoint_candidates": sorted(set(entrypoints)),
        "top_directories": dict(sorted(by_top_dir.items(), key=lambda item: item[0])),
        "extensions": dict(ext_counts.most_common(40)),
        "tree_depth": tree_depth,
        "tree": tree,
    }


def write_inventory(inventory: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def inventory_summary(inventory: dict[str, Any]) -> str:
    lines = [
        f"Root: {inventory['root']}",
        f"Files scanned: {inventory['file_count_scanned']}{' (truncated)' if inventory['truncated'] else ''}",
        "Project types: " + ", ".join(inventory["project_types"]),
    ]
    if inventory["manifests"]:
        lines.append("Manifests: " + ", ".join(inventory["manifests"][:20]))
    if inventory["entrypoint_candidates"]:
        lines.append("Entrypoint candidates: " + ", ".join(inventory["entrypoint_candidates"][:20]))
    extensions = inventory.get("extensions", {})
    if extensions:
        lines.append("Top extensions: " + ", ".join(f"{k}={v}" for k, v in list(extensions.items())[:12]))
    lines.append("Tree:")
    lines.extend(compact_tree_lines(inventory.get("tree", {})))
    return "\n".join(lines)
