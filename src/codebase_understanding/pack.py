"""Generate a compact learning pack for an unfamiliar project."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .import_graph import create_import_graph, write_import_graph
from .inventory import create_inventory, write_inventory
from .vibe_audit import audit_vibe_project, write_audit


DEFAULT_LIBRARY = Path("/Users/chihoyo/Project/CodebaseUnderstanding/analyses")


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "project"


def choose_output_root(target: Path, out: str | Path | None = None) -> Path:
    if out:
        return Path(out).expanduser().resolve()
    base = DEFAULT_LIBRARY / f"{date.today().isoformat()}-{slugify(target.name)}"
    if not base.exists():
        return base
    for index in range(2, 100):
        candidate = DEFAULT_LIBRARY / f"{base.name}-{index}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not choose a unique output directory under {DEFAULT_LIBRARY}")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _bullet(items: list[str], empty: str = "- 未发现") -> str:
    if not items:
        return empty
    return "\n".join(f"- `{item}`" for item in items)


def _top_reading_order(inventory: dict[str, Any]) -> list[str]:
    entrypoints = inventory.get("entrypoint_candidates", [])
    manifests = inventory.get("manifests", [])
    top_dirs = [name for name in inventory.get("top_directories", {}) if name.endswith("/")]
    ordered = []
    ordered.extend(entrypoints[:8])
    ordered.extend([item for item in manifests if item not in ordered][:8])
    ordered.extend([item for item in top_dirs if item not in ordered][:8])
    return ordered[:12]


def _graph(inventory: dict[str, Any], audit: dict[str, Any], import_graph: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = [
        {
            "id": "target",
            "label": Path(inventory["root"]).name,
            "kind": "entrypoint",
            "group": "目标项目",
            "layer": "Source",
            "path": ".",
            "summary": "被分析的项目根目录。",
        }
    ]
    edges: list[dict[str, Any]] = []

    def add_node(node_id: str, label: str, kind: str, group: str, path: str, summary: str) -> None:
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "kind": kind,
                "group": group,
                "layer": group,
                "path": path,
                "summary": summary,
            }
        )
        edges.append({"from": "target", "to": node_id, "label": "contains", "kind": "contains"})

    for item in inventory.get("manifests", [])[:10]:
        add_node(f"manifest-{slugify(item)}", item, "config", "Manifests", item, "项目配置或元数据入口。")
    for item in inventory.get("entrypoint_candidates", [])[:10]:
        add_node(f"entry-{slugify(item)}", item, "entrypoint", "Entrypoints", item, "可能的用户或运行入口。")
    for item, count in list(inventory.get("top_directories", {}).items())[:12]:
        if item.endswith("/"):
            add_node(f"dir-{slugify(item)}", item, "module", "Top directories", item, f"顶层目录，扫描到 {count} 个文件。")

    nodes.append(
        {
            "id": "vibe-audit",
            "label": "vibe-audit",
            "kind": "test",
            "group": "Checks",
            "layer": "Checks",
            "path": "vibe_audit.json",
            "summary": f"发现 {audit['summary']['finding_count']} 条可能的生成遗留或验证风险。",
        }
    )
    edges.append({"from": "vibe-audit", "to": "target", "label": "examines", "kind": "examines"})

    existing_node_ids = {node["id"] for node in nodes}

    def ensure_file_node(path: str, group: str = "Import graph") -> str:
        node_id = f"file-{slugify(path)}"
        if node_id not in existing_node_ids:
            nodes.append(
                {
                    "id": node_id,
                    "label": path,
                    "kind": "module",
                    "group": group,
                    "layer": group,
                    "path": path,
                    "summary": "由 import graph 发现的源码文件。",
                }
            )
            existing_node_ids.add(node_id)
        return node_id

    for import_edge in import_graph.get("edges", []):
        if import_edge.get("scope") != "internal" or not import_edge.get("to"):
            continue
        from_id = ensure_file_node(import_edge["from"])
        to_id = ensure_file_node(import_edge["to"])
        edges.append(
            {
                "from": from_id,
                "to": to_id,
                "label": "imports",
                "kind": "imports",
            }
        )

    return {
        "title": f"{Path(inventory['root']).name} 快速学习图",
        "summary": "入口、配置、顶层目录和 vibe-audit 风险的第一版结构图。",
        "locale": "zh-CN",
        "nodes": nodes,
        "edges": edges,
        "flows": [
            {
                "name": "快速学习流程",
                "summary": "先盘点结构，再审计生成遗留，最后阅读入口并制定优化路线。",
                "steps": [
                    {"label": "盘点文件与 manifest", "node": "target", "path": "inventory.json", "summary": "建立项目类型、入口、目录分布。"},
                    {"label": "检查 vibe-coded 风险", "node": "vibe-audit", "path": "vibe_audit.json", "summary": "寻找未接线、缺验证、缺文件、重复实现等线索。"},
                    {"label": "提取 import graph", "node": "target", "path": "import_graph.json", "summary": "用文件级依赖边确认实际接线方向。"},
                    {"label": "阅读入口文件", "node": "target", "path": ".", "summary": "从 entrypoint candidates 开始追踪真实路径。"},
                    {"label": "排优化顺序", "node": "vibe-audit", "path": "open-questions.md", "summary": "先修验证和接线，再做架构和功能优化。"},
                ],
            }
        ],
        "evidence": [
            {"claim": "Project types were inferred from manifests and filenames.", "path": "inventory.json", "detail": ", ".join(inventory.get("project_types", []))},
            {"claim": "Vibe audit findings are heuristic leads, not deletion proof.", "path": "vibe_audit.json", "detail": f"{audit['summary']['finding_count']} findings"},
            {"claim": "Import graph edges are file-level static dependencies.", "path": "import_graph.json", "detail": f"{import_graph['summary']['internal_edge_count']} internal edges"},
        ],
        "questions": [item["title"] for item in audit.get("findings", [])[:12]],
    }


def create_pack(
    target: Path | str,
    out: str | Path | None = None,
    max_files: int = 3000,
    tree_depth: int = 3,
) -> dict[str, Any]:
    target_path = Path(target).expanduser().resolve()
    if target_path.is_file():
        target_path = target_path.parent
    output_root = choose_output_root(target_path, out)
    output_root.mkdir(parents=True, exist_ok=True)

    inventory = create_inventory(target_path, max_files=max_files, tree_depth=tree_depth)
    audit = audit_vibe_project(target_path, max_files=max_files)
    import_graph = create_import_graph(target_path, max_files=max_files)
    graph = _graph(inventory, audit, import_graph)

    write_inventory(inventory, output_root / "inventory.json")
    write_audit(audit, output_root / "vibe_audit.json")
    write_import_graph(import_graph, output_root / "import_graph.json")
    _write(output_root / "understanding_graph.json", json.dumps(graph, indent=2, ensure_ascii=False))

    today = date.today().isoformat()
    _write(
        output_root / "source.md",
        f"""# Source

- Target: `{target_path}`
- Analysis date: {today}
- Output mode: understanding pack
- Output root: `{output_root}`
- Target writes: none
""",
    )

    reading_order = _top_reading_order(inventory)
    _write(
        output_root / "overview.md",
        f"""# Overview

## 这是什么

项目类型初判：{", ".join(inventory.get("project_types", []))}

## 最短心智模型

先看 manifest 和入口文件，确认项目实际运行方式；再看 `import_graph.json` 的内部依赖边确认实际接线；最后看 `vibe_audit.json`，把疑似生成遗留和验证缺口当作下一步追踪线索。

## 建议阅读顺序

{_bullet(reading_order)}

## 关键入口

{_bullet(inventory.get("entrypoint_candidates", []))}

## 关键配置

{_bullet(inventory.get("manifests", []))}
""",
    )

    top_dirs = [f"{name} ({count})" for name, count in inventory.get("top_directories", {}).items()]
    _write(
        output_root / "architecture.md",
        f"""# Architecture

## 结构事实

- Root: `{inventory['root']}`
- Files scanned: {inventory['file_count_scanned']}{' (truncated)' if inventory['truncated'] else ''}
- Project types: {", ".join(inventory.get("project_types", []))}

## 顶层分布

{_bullet(top_dirs)}

## 依赖方向初判

`import_graph.json` 静态提取到 {import_graph['summary']['edge_count']} 条 import 边，其中 {import_graph['summary']['internal_edge_count']} 条为内部文件依赖。

Inference: 当前 import graph 是文件级静态依赖图，不等同于运行时调用链；动态 import、框架路由、依赖注入和字符串拼接路径仍需要人工或运行时验证。

## 外部工具与副作用

未运行安装、构建、测试或网络命令。目标项目保持只读。
""",
    )

    _write(
        output_root / "flows.md",
        """# Flows

## 快速学习流程

Trigger: 用户请求理解一个本地项目。

Path:
1. `cbu inventory` 扫描项目形态、manifest、入口候选、目录分布。
2. `cbu import-graph` 提取 Python/JS/TS 的静态 import 边，确认源码文件之间的实际依赖方向。
3. `cbu vibe-audit` 检查缺少验证、缺失脚本目标、半接线 UI、疑似未引用文件、重复实现。
4. `cbu pack` 生成 Markdown 和 JSON，供 agent 继续做证据化解释。
5. Agent 从入口文件追踪真实行为，并把不确定内容标为 Inference。

Side effects: 只写入中央分析包，不写目标项目。

Output: `overview.md`、`architecture.md`、`flows.md`、`diagrams.md`、`open-questions.md`、`inventory.json`、`import_graph.json`、`vibe_audit.json`、`understanding_graph.json`。
""",
    )

    _write(
        output_root / "diagrams.md",
        """# Diagrams

## Skill + CLI 学习框架

```mermaid
flowchart TD
  User[用户问题] --> Skill[skill 判断模式]
  Skill --> Inventory[cbu inventory]
  Skill --> Audit[cbu vibe-audit]
  Skill --> Pack[cbu pack]
  Inventory --> Evidence[结构证据]
  Audit --> Risks[风险线索]
  Pack --> Notes[学习包]
  Notes --> Improve[优化路线]
```

## 产物管线

```mermaid
flowchart LR
  Target[目标项目] --> Scan[inventory.json]
  Target --> Imports[import_graph.json]
  Target --> Audit[vibe_audit.json]
  Scan --> Markdown[Markdown notes]
  Imports --> Graph[understanding_graph.json]
  Audit --> Questions[open-questions.md]
  Scan --> Graph[understanding_graph.json]
  Audit --> Graph
```
""",
    )

    open_questions = [
        f"- [{item['severity']}] {item['title']}: {item['recommendation']}"
        for item in audit.get("findings", [])[:30]
    ]
    if not open_questions:
        open_questions = ["- 暂无明显 vibe-audit 风险；仍建议运行项目自带验证命令确认。"]
    _write(
        output_root / "open-questions.md",
        "# Open Questions\n\n" + "\n".join(open_questions),
    )

    return {
        "output_root": str(output_root),
        "inventory": inventory,
        "import_graph": import_graph,
        "audit": audit,
        "graph": graph,
    }
