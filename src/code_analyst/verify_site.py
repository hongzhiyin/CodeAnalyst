"""Verify generated CodeAnalyst static visual sites."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .render_site import validate_graph


GRAPH_DATA_RE = re.compile(
    r'<script id="graph-data" type="application/json">(.*?)</script>',
    flags=re.S,
)


def _check(status: str, name: str, detail: str) -> dict[str, str]:
    return {"status": status, "name": name, "detail": detail}


def _site_dir(path: Path | str) -> Path:
    site_path = Path(path).expanduser().resolve()
    if site_path.is_file():
        return site_path.parent
    return site_path


def _load_json_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def _embedded_graph(html_text: str) -> tuple[dict[str, Any] | None, str | None]:
    match = GRAPH_DATA_RE.search(html_text)
    if not match:
        return None, "missing graph-data script tag"
    try:
        return json.loads(match.group(1)), None
    except json.JSONDecodeError as exc:
        return None, f"invalid embedded JSON: {exc}"


def _validate_graph_shape(data: dict[str, Any], source: str) -> dict[str, str]:
    try:
        validate_graph(data)
    except SystemExit as exc:
        return _check("error", source, str(exc))
    return _check("ok", source, "Graph shape is valid.")


def verify_site(path: Path | str) -> dict[str, Any]:
    """Return a deterministic readiness report for a generated visual site."""

    site_dir = _site_dir(path)
    index_path = site_dir / "index.html"
    data_path = site_dir / "data.json"
    checks: list[dict[str, str]] = []

    if index_path.exists():
        checks.append(_check("ok", "index.html", "HTML entry file exists."))
    else:
        checks.append(_check("missing", "index.html", "HTML entry file is missing."))

    if data_path.exists():
        checks.append(_check("ok", "data.json", "Rendered graph data file exists."))
    else:
        checks.append(_check("missing", "data.json", "Rendered graph data file is missing."))

    data_json: dict[str, Any] | None = None
    if data_path.exists():
        data_json, error = _load_json_file(data_path)
        if error:
            checks.append(_check("error", "data.json parse", error))
        elif data_json is not None:
            checks.append(_validate_graph_shape(data_json, "data.json graph"))

    embedded_json: dict[str, Any] | None = None
    if index_path.exists():
        try:
            html_text = index_path.read_text(encoding="utf-8")
        except OSError as exc:
            html_text = ""
            checks.append(_check("error", "index.html read", str(exc)))
        if html_text:
            embedded_json, error = _embedded_graph(html_text)
            if error:
                checks.append(_check("error", "embedded graph-data", error))
            elif embedded_json is not None:
                checks.append(_validate_graph_shape(embedded_json, "embedded graph-data"))
            if "JSON.parse(document.getElementById('graph-data').textContent)" in html_text:
                checks.append(_check("ok", "browser data bootstrap", "HTML can bootstrap graph data in a browser."))
            else:
                checks.append(_check("warn", "browser data bootstrap", "Expected browser bootstrap script was not found."))

    if data_json is not None and embedded_json is not None:
        if data_json.get("nodes") == embedded_json.get("nodes") and data_json.get("edges") == embedded_json.get("edges"):
            checks.append(_check("ok", "data parity", "data.json and embedded graph-data agree on nodes and edges."))
        else:
            checks.append(_check("warn", "data parity", "data.json and embedded graph-data differ."))

    status_counts = Counter(item["status"] for item in checks)
    node_count = 0
    edge_count = 0
    graph_data = data_json or embedded_json or {}
    if isinstance(graph_data.get("nodes"), list):
        node_count = len(graph_data["nodes"])
    if isinstance(graph_data.get("edges"), list):
        edge_count = len(graph_data["edges"])

    ok = not any(item["status"] in {"missing", "error"} for item in checks)
    return {
        "target": str(site_dir),
        "ok": ok,
        "file_url": index_path.as_uri() if index_path.exists() else None,
        "summary": {
            "check_count": len(checks),
            "status_counts": dict(sorted(status_counts.items())),
            "node_count": node_count,
            "edge_count": edge_count,
        },
        "checks": checks,
    }


def write_site_verification(report: dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def site_verification_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Target: {report['target']}",
        f"Ready: {'yes' if report['ok'] else 'no'}",
        f"Checks: {report['summary']['check_count']}",
        f"Nodes: {report['summary']['node_count']}",
        f"Edges: {report['summary']['edge_count']}",
    ]
    if report["summary"]["status_counts"]:
        lines.append("Statuses: " + ", ".join(f"{key}={value}" for key, value in report["summary"]["status_counts"].items()))
    if report.get("file_url"):
        lines.append(f"Open: {report['file_url']}")
    for item in report["checks"][:24]:
        lines.append(f"- [{item['status']}] {item['name']}: {item['detail']}")
    if len(report["checks"]) > 24:
        lines.append(f"... {len(report['checks']) - 24} more checks")
    return "\n".join(lines)
