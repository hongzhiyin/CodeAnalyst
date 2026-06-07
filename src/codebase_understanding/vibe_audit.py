"""Heuristic checks for vibe-coded project leftovers."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .inventory import ENTRYPOINT_NAMES, collect_files, rel


SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
TEXT_EXTS = SOURCE_EXTS | {".json", ".md", ".toml", ".yaml", ".yml", ".html", ".css", ".scss", ".sh"}
CONFIG_STEMS = {"vite.config", "next.config", "tailwind.config", "postcss.config", "eslint.config"}
TEST_MARKERS = {"test", "tests", "spec", "__tests__", "pytest", "vitest", "jest", "playwright"}


def _read_text(path: Path, limit: int = 200000) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _load_package_json(root: Path) -> dict[str, Any]:
    path = root / "package.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _deps(package: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            names.update(value.keys())
    return names


def _finding(
    *,
    category: str,
    title: str,
    severity: str,
    path: str | None,
    detail: str,
    recommendation: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{category}-{title}".lower()).strip("-")
    return {
        "id": slug[:80],
        "category": category,
        "title": title,
        "severity": severity,
        "path": path,
        "detail": detail,
        "evidence": evidence or [],
        "recommendation": recommendation,
    }


def _has_test_signal(root: Path, files: list[Path], package: dict[str, Any]) -> bool:
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    if any(any(marker in name.lower() or marker in str(cmd).lower() for marker in TEST_MARKERS) for name, cmd in scripts.items()):
        return True
    for path in files:
        relative = rel(path, root).lower()
        if any(marker in relative for marker in TEST_MARKERS):
            return True
    return False


def _missing_script_targets(root: Path, package: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return findings

    target_pattern = re.compile(r"(?<![@\w/-])([A-Za-z0-9_./-]+\.(?:js|mjs|cjs|ts|tsx|py|sh|html|json))")
    for name, command in scripts.items():
        if not isinstance(command, str):
            continue
        for match in target_pattern.finditer(command):
            token = match.group(1).strip("./")
            if token.startswith(("http", "node_modules")):
                continue
            candidate = root / token
            if "/" in token and not candidate.exists():
                findings.append(
                    _finding(
                        category="script",
                        title=f"Script '{name}' references a missing file",
                        severity="high",
                        path="package.json",
                        detail=f"`npm run {name}` appears to reference `{token}`, but that file was not found.",
                        evidence=[f"{name}: {command}"],
                        recommendation="Confirm whether this is a generated leftover, then fix the script or remove it.",
                    )
                )
    return findings


def _framework_mismatches(root: Path, files: list[Path], package: dict[str, Any]) -> list[dict[str, Any]]:
    deps = _deps(package)
    names = {rel(path, root) for path in files}
    findings: list[dict[str, Any]] = []

    if any(name.startswith("vite.config.") for name in names) and package and "vite" not in deps:
        findings.append(
            _finding(
                category="config",
                title="Vite config exists without Vite dependency",
                severity="medium",
                path="vite.config.*",
                detail="A Vite config file exists, but `vite` was not found in package dependencies.",
                recommendation="Check whether the config is stale or the dependency declaration is incomplete.",
            )
        )
    if any(name.startswith("next.config.") for name in names) and package and "next" not in deps:
        findings.append(
            _finding(
                category="config",
                title="Next config exists without Next dependency",
                severity="medium",
                path="next.config.*",
                detail="A Next.js config file exists, but `next` was not found in package dependencies.",
                recommendation="Check whether the app migrated away from Next.js or package metadata is stale.",
            )
        )
    if "package.json" in names and "tsconfig.json" in names and not any(ext in {".ts", ".tsx"} for ext in (p.suffix for p in files)):
        findings.append(
            _finding(
                category="config",
                title="TypeScript config without TypeScript source",
                severity="low",
                path="tsconfig.json",
                detail="`tsconfig.json` exists, but no `.ts` or `.tsx` source files were scanned.",
                recommendation="If the project is JavaScript-only now, remove stale TS config or document why it remains.",
            )
        )
    return findings


def _suspected_unused_sources(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    source_files = [
        path
        for path in files
        if path.suffix.lower() in SOURCE_EXTS
        and path.name not in ENTRYPOINT_NAMES
        and not any(part in TEST_MARKERS for part in path.parts)
        and not any(path.name.startswith(stem) for stem in CONFIG_STEMS)
    ]
    text_files = [path for path in files if path.suffix.lower() in TEXT_EXTS]
    contents: dict[Path, str] = {path: _read_text(path) for path in text_files}
    findings: list[dict[str, Any]] = []

    for path in source_files[:800]:
        stem = path.stem
        if stem in {"index", "__init__"}:
            continue
        mentioned = False
        for other, text in contents.items():
            if other == path:
                continue
            if stem in text or rel(path, root) in text:
                mentioned = True
                break
        if not mentioned:
            findings.append(
                _finding(
                    category="wiring",
                    title="Possibly unused source file",
                    severity="low",
                    path=rel(path, root),
                    detail="This source file was not referenced by name or relative path in the scanned text files.",
                    recommendation="Treat as a lead, not proof: confirm with imports/routes/build output before deleting.",
                )
            )
        if len(findings) >= 30:
            break
    return findings


def _ui_controls_without_handlers(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    tag_pattern = re.compile(r"<(button|form|input|select|textarea)\b([^>]*)>", re.IGNORECASE | re.DOTALL)
    required = {
        "button": "onClick",
        "form": "onSubmit",
        "input": "onChange",
        "select": "onChange",
        "textarea": "onChange",
    }
    for path in files:
        if path.suffix.lower() not in {".jsx", ".tsx"}:
            continue
        text = _read_text(path)
        local_hits: list[str] = []
        for tag, attrs in tag_pattern.findall(text):
            tag_lower = tag.lower()
            needed = required[tag_lower]
            if tag_lower == "button" and re.search(r'type=["\']submit["\']', attrs):
                continue
            if needed not in attrs:
                local_hits.append(f"<{tag_lower}> without {needed}")
        if local_hits:
            counts = Counter(local_hits)
            findings.append(
                _finding(
                    category="ui",
                    title="UI controls may be half-wired",
                    severity="medium",
                    path=rel(path, root),
                    detail="Some JSX controls appear without the handler normally expected for that control type.",
                    evidence=[f"{name}: {count}" for name, count in sorted(counts.items())],
                    recommendation="Click through or inspect state flow before assuming these controls are functional.",
                )
            )
        if len(findings) >= 20:
            break
    return findings


def _duplicate_stems(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    by_stem: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        if path.suffix.lower() in SOURCE_EXTS and path.stem not in {"index", "__init__"}:
            by_stem[path.stem.lower()].append(path)

    findings: list[dict[str, Any]] = []
    for stem, paths in sorted(by_stem.items()):
        if len(paths) < 2:
            continue
        findings.append(
            _finding(
                category="duplication",
                title=f"Multiple source files share the stem '{stem}'",
                severity="low",
                path=None,
                detail="Duplicate names can be intentional, but vibe-coded projects often accumulate alternate implementations.",
                evidence=[rel(path, root) for path in paths[:8]],
                recommendation="Compare responsibilities and remove or rename stale alternatives if one path is unused.",
            )
        )
        if len(findings) >= 20:
            break
    return findings


def audit_vibe_project(target: Path | str, max_files: int = 3000) -> dict[str, Any]:
    root = Path(target).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Target does not exist: {root}")
    if root.is_file():
        root = root.parent

    files = collect_files(root, max_files)
    package = _load_package_json(root)
    findings: list[dict[str, Any]] = []

    if not _has_test_signal(root, files, package):
        findings.append(
            _finding(
                category="verification",
                title="No obvious test or verification signal",
                severity="medium",
                path=None,
                detail="No test script, test file, or common verification directory was found in the scanned files.",
                recommendation="Before optimization, add one runnable check that can fail: test, typecheck, lint, or smoke script.",
            )
        )

    findings.extend(_missing_script_targets(root, package))
    findings.extend(_framework_mismatches(root, files, package))
    findings.extend(_ui_controls_without_handlers(root, files))
    findings.extend(_suspected_unused_sources(root, files))
    findings.extend(_duplicate_stems(root, files))

    severity_counts = Counter(item["severity"] for item in findings)
    category_counts = Counter(item["category"] for item in findings)
    return {
        "target": str(root),
        "file_count_scanned": len(files),
        "truncated": len(files) >= max_files,
        "summary": {
            "finding_count": len(findings),
            "severity_counts": dict(sorted(severity_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
        },
        "findings": findings,
    }


def write_audit(audit: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def audit_summary(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        f"Target: {audit['target']}",
        f"Files scanned: {audit['file_count_scanned']}{' (truncated)' if audit['truncated'] else ''}",
        f"Findings: {summary['finding_count']}",
    ]
    if summary["severity_counts"]:
        lines.append("Severity: " + ", ".join(f"{k}={v}" for k, v in summary["severity_counts"].items()))
    for item in audit["findings"][:20]:
        path = f" ({item['path']})" if item.get("path") else ""
        lines.append(f"- [{item['severity']}] {item['title']}{path}")
    if len(audit["findings"]) > 20:
        lines.append(f"... {len(audit['findings']) - 20} more findings")
    return "\n".join(lines)
