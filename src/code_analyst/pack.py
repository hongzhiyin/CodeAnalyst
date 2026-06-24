"""Generate a compact learning pack for an unfamiliar project."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .flow_map import create_flow_map, write_flow_map
from .import_graph import create_import_graph, write_import_graph
from .inventory import create_inventory, write_inventory
from .script_check import check_scripts, write_script_check
from .vibe_audit import audit_vibe_project, write_audit


DEFAULT_LIBRARY = Path("/Users/chihoyo/Project/CodeAnalyst/analyses")


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


def _path_kind(path: str, inventory: dict[str, Any]) -> str:
    normalized = path.rstrip("/")
    name = Path(normalized).name.lower()
    top = normalized.split("/", 1)[0].lower()
    manifests = set(inventory.get("manifests", []))
    entrypoints = set(inventory.get("entrypoint_candidates", []))
    if path in entrypoints or normalized in entrypoints:
        return "entrypoint"
    if path in manifests or normalized in manifests:
        return "config"
    if top in {"skill", "skills"} or name == "skill.md":
        return "skill"
    if top in {"tests", "test", "__tests__"} or name.startswith("test_") or name.endswith(".test.ts") or name.endswith(".spec.ts"):
        return "test"
    if top in {"scripts", "bin"}:
        return "script"
    if top in {"docs", "doc"} or Path(normalized).suffix.lower() in {".md", ".rst", ".txt"}:
        return "document"
    if name in {"package.json", "pyproject.toml", "tsconfig.json", "makefile", "dockerfile"}:
        return "config"
    return "module"


def _functional_meaning(path: str, kind: str, file_count: int | None = None) -> str:
    is_dir = path.endswith("/")
    normalized = path.rstrip("/")
    name = Path(normalized).name
    lower = name.lower()
    top = normalized.split("/", 1)[0].lower()
    count_text = f"，扫描到 {file_count} 个文件" if file_count is not None else ""

    if kind == "entrypoint":
        return "可能的用户触发或运行入口；理解项目行为时优先从这里追踪调用和依赖。"
    if kind == "config":
        return "项目配置、构建、依赖或工具元数据；用来确认项目如何安装、运行和验证。"
    if kind == "skill":
        return "Agent-facing 工作流或技能说明；决定后续 agent 如何调用工具、读取证据和解释项目。"
    if kind == "test":
        return "验证层；用来确认现有行为、回归风险和项目是否有可信的反馈闭环。"
    if kind == "script":
        return "自动化脚本或命令入口；通常承担安装、同步、打包、发布或本地维护流程。"
    if kind == "document":
        return "文档或决策记录；用于理解项目目标、使用方式、约束和历史取舍。"
    if is_dir:
        if top in {"src", "lib", "app"}:
            return f"主要实现代码区域{count_text}；通常是理解产品行为和模块边界的核心入口。"
        if top in {"components", "pages", "routes"}:
            return f"界面或路由区域{count_text}；通常承载用户可见流程。"
        if top in {"server", "api", "services"}:
            return f"服务端或集成区域{count_text}；通常承载外部请求、后台流程或业务接口。"
        return f"顶层结构区域{count_text}；需要结合入口、依赖边和脚本检查判断它是否属于主路径。"
    if lower == "cli.py":
        return "命令行分发入口；通常连接用户命令、扫描模块、生成产物和验证流程。"
    if lower == "pack.py":
        return "分析包生成逻辑；通常负责把扫描证据汇总成 Markdown、JSON 和可视化数据。"
    if lower == "render_site.py":
        return "静态可视化页面渲染逻辑；负责把 graph JSON 变成可交互 HTML。"
    if lower == "review_pack.py":
        return "只读 review 和设计建议生成逻辑；负责把扫描证据转成下一步优化路线。"
    if lower.endswith(".py"):
        return "Python 源码模块；需要结合 import graph 的入边/出边判断它在运行路径中的角色。"
    if lower.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
        return "JavaScript/TypeScript 源码模块；需要结合 import graph 和框架入口判断实际接线。"
    return "代码或项目文件；需要结合路径、入口线索和依赖关系确认功能含义。"


def _node_next_read(kind: str, path: str, incoming: int, outgoing: int, related_flows: list[str]) -> str:
    if related_flows:
        return f"先对照相关流程：{', '.join(related_flows[:3])}，再沿入口文件追踪真实行为。"
    if kind == "entrypoint":
        return "从这个入口向外追踪 import 边和脚本声明，确认用户动作最终调用哪些模块。"
    if outgoing:
        return "继续阅读它导入的内部模块，确认下游职责和副作用边界。"
    if incoming:
        return "回到引用它的上游节点，确认它是主路径依赖还是辅助实现。"
    if kind == "config":
        return "用它确认项目运行、构建、测试或 agent 调用方式，再回到对应入口。"
    if kind == "test":
        return "用这些验证文件反推重要行为，再确认核心路径是否被覆盖。"
    return "先确认它是否在入口、脚本或 import graph 主路径上，再决定是否深入阅读。"


def _node_signals(
    path: str,
    kind: str,
    incoming: int,
    outgoing: int,
    related_flows: list[str],
    inventory: dict[str, Any],
) -> list[str]:
    signals: list[str] = [f"kind={kind}"]
    if path in inventory.get("manifests", []):
        signals.append("manifest/config candidate")
    if path in inventory.get("entrypoint_candidates", []):
        signals.append("entrypoint candidate")
    if incoming:
        signals.append(f"incoming internal imports={incoming}")
    if outgoing:
        signals.append(f"outgoing internal imports={outgoing}")
    for flow in related_flows[:3]:
        signals.append(f"related flow={flow}")
    return signals


def _node_by_path(graph: dict[str, Any], path: str) -> str | None:
    normalized = path.rstrip("/")
    for node in graph.get("nodes", []):
        node_path = str(node.get("path", "")).rstrip("/")
        if node_path == normalized or str(node.get("path", "")) == path:
            return str(node.get("id"))
    return None


def _first_existing_node(graph: dict[str, Any], node_ids: list[str]) -> str:
    known = {str(node.get("id")) for node in graph.get("nodes", [])}
    for node_id in node_ids:
        if node_id in known:
            return node_id
    return "target"


def _guide_step(
    label: str,
    summary: str,
    node: str,
    path: str,
    evidence_type: str,
    evidence: str,
    takeaway: str,
) -> dict[str, str]:
    return {
        "label": label,
        "summary": summary,
        "node": node,
        "path": path,
        "evidence_type": evidence_type,
        "evidence": evidence,
        "takeaway": takeaway,
    }


def _learning_guide(
    inventory: dict[str, Any],
    import_graph: dict[str, Any],
    flow_map: dict[str, Any],
    script_check: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    project_name = Path(inventory["root"]).name
    flows = flow_map.get("flows", [])
    checks = script_check.get("checks", [])
    ok_checks = [item for item in checks if item.get("status") == "ok"]
    primary_flow = flows[0] if flows else {}
    primary_entry = ""
    for entry in primary_flow.get("entrypoints", []):
        if entry:
            primary_entry = str(entry)
            break
    if not primary_entry and inventory.get("entrypoint_candidates"):
        primary_entry = str(inventory["entrypoint_candidates"][0])

    command_name = ""
    command_path = ""
    if ok_checks:
        command_name = str(ok_checks[0].get("name") or "")
        command_path = str(ok_checks[0].get("target") or ok_checks[0].get("source") or "")
    if not command_name and primary_flow:
        command_name = str(primary_flow.get("title") or "主要入口")
    if not command_path:
        command_path = primary_entry or "flow_map.json"

    entry_node = _node_by_path(graph, primary_entry) if primary_entry else None
    manifest_path = inventory.get("manifests", [None])[0] or "inventory.json"
    manifest_node = _node_by_path(graph, str(manifest_path)) or "target"
    command_node = _node_by_path(graph, command_path) or entry_node or _first_existing_node(graph, ["script-check", "flow-map", "target"])
    pack_node = _node_by_path(graph, "src/code_analyst/pack.py") or _first_existing_node(graph, ["flow-map", "target"])
    render_node = _node_by_path(graph, "src/code_analyst/render_site.py") or _first_existing_node(graph, ["target"])
    cli_node = _node_by_path(graph, "src/code_analyst/cli.py") or entry_node or command_node
    verify_node = _node_by_path(graph, "src/code_analyst/verify_site.py") or _first_existing_node(graph, ["script-check", "vibe-audit", "target"])
    flow_node = "flow-map" if _first_existing_node(graph, ["flow-map"]) == "flow-map" else "target"
    script_node = "script-check" if _first_existing_node(graph, ["script-check"]) == "script-check" else "target"

    case_title = (
        f"用户运行 `{command_name}` 时，系统如何找到入口并生成可读产物"
        if command_name
        else "用户触发项目入口时，系统如何从入口走到核心产物"
    )
    case_steps = [
        _guide_step(
            "确认项目入口和运行方式",
            "先不要读所有文件。用 manifest、脚本检查和 flow-map 判断用户真正可能触发哪个入口。",
            command_node,
            command_path,
            "confirmed",
            "script_check.json / flow_map.json",
            "入口是学习路线的起点；没有入口，图谱只是一张散开的地图。",
        ),
        _guide_step(
            "进入分发层",
            "阅读入口文件，找出命令如何被解析并分派到具体功能模块。",
            cli_node,
            primary_entry or command_path,
            "entrypoint hint",
            primary_flow.get("title", "entrypoint_candidates") if primary_flow else "entrypoint_candidates",
            "这一层回答“用户动作进来后，代码把它交给谁处理”。",
        ),
        _guide_step(
            "收集证据而不是直接猜功能",
            "用 flow-map、script-check、import-graph 和 vibe-audit 建立可追溯证据，再进入解释。",
            flow_node,
            "flow_map.json",
            "confirmed",
            f"flows={flow_map['summary']['flow_count']}, internal_imports={import_graph['summary']['internal_edge_count']}",
            "这一步把阅读从直觉变成有证据的学习路径。",
        ),
        _guide_step(
            "把证据组织成学习包",
            "pack 层把扫描结果汇总成 Markdown、JSON、graph 和 guided lesson，供页面和 agent 继续消费。",
            pack_node,
            "src/code_analyst/pack.py",
            "static dependency",
            "understanding_graph.json / learning_guide.json",
            "这里是从“原始扫描结果”变成“可学习材料”的关键转换。",
        ),
        _guide_step(
            "把学习包渲染成可交互教材",
            "render-site 把 guide、节点、关系和证据嵌入静态 HTML，让用户按章节阅读并随时跳回索引。",
            render_node,
            "src/code_analyst/render_site.py",
            "static dependency",
            "site/index.html",
            "图谱仍然存在，但它服务于教程步骤，而不是抢占学习入口。",
        ),
        _guide_step(
            "验证页面和剩余风险",
            "最后用 verify-site、测试和开放问题确认产物结构可用，并标出需要人工判断的地方。",
            verify_node,
            "site_verification.json",
            "confirmed",
            "verify-site / vibe_audit.json",
            "学习路径的终点不是读完所有文件，而是知道下一步该验证什么。",
        ),
    ]

    generic_intro = [
        "从一个实际问题开始，而不是先看完整图谱。",
        "先确认入口和证据，再沿主路径拆模块。",
        "把完整图谱当作索引：读到某一步再跳进去查关系。",
    ]
    project_types = ", ".join(inventory.get("project_types", [])) or "unknown"
    guide = {
        "version": 1,
        "quickstart": {
            "title": f"{project_name} 学习路线",
            "problem": f"如果你第一次接触 `{project_name}`，先回答一个具体问题：{case_title}。",
            "why_this_path": "这个路径会经过入口、证据采集、产物生成、页面渲染和验证，比直接看总览图更接近真实理解过程。",
            "learning_goals": generic_intro,
            "start_node": command_node,
            "start_path": command_path,
            "project_types": project_types,
        },
        "case_study": {
            "title": case_title,
            "trigger": f"用户触发 `{command_name or primary_flow.get('title', '项目入口')}`。",
            "mental_model": "把项目当成一条工作流来读：入口接收用户动作，证据模块确认事实，pack 层组织材料，render 层呈现教材，验证层确认产物可信。",
            "steps": case_steps,
        },
        "chapters": [
            {
                "title": "第 1 章：先找入口，不先读全图",
                "question": "用户的动作到底从哪个文件或命令进入系统？",
                "summary": "目标是确定用户动作从哪里进入系统，以及哪个文件负责分发。",
                "principle": "学习一个项目时，入口相当于例题题干；先确认触发条件，后面的模块才有阅读顺序。",
                "steps": [case_steps[0], case_steps[1]],
            },
            {
                "title": "第 2 章：用证据建立心智模型",
                "question": "哪些结论是工具确认过的事实，哪些只是静态线索？",
                "summary": "目标是区分 confirmed facts、entrypoint hints、static dependencies 和 inference。",
                "principle": "先把证据类型分清，才能避免把 import graph 误读成真实运行时调用链。",
                "steps": [case_steps[2]],
            },
            {
                "title": "第 3 章：理解产物生成链路",
                "question": "扫描结果怎样变成可以阅读、可以点击、可以验证的学习材料？",
                "summary": "目标是看懂扫描结果如何变成学习包、图谱和页面。",
                "principle": "pack 层负责把分散事实变成稳定数据结构；render 层只负责把这些结构转成阅读体验。",
                "steps": [case_steps[3], case_steps[4]],
            },
            {
                "title": "第 4 章：回到验证和下一步",
                "question": "读到这里以后，哪些结论还能继续相信，哪些需要人工或运行时验证？",
                "summary": "目标是知道哪些结论可信，哪些还需要运行或人工确认。",
                "principle": "教材式页面不应该假装自己证明了一切；它应该告诉你证据边界和下一步验证方向。",
                "steps": [case_steps[5]],
            },
        ],
        "steps": case_steps,
        "evidence": [
            {"type": "confirmed", "path": "inventory.json", "detail": f"project_types={project_types}"},
            {"type": "entrypoint hint", "path": "flow_map.json", "detail": f"flows={flow_map['summary']['flow_count']}"},
            {"type": "confirmed", "path": "script_check.json", "detail": f"checks={script_check['summary']['check_count']}"},
            {"type": "static dependency", "path": "import_graph.json", "detail": f"internal_edges={import_graph['summary']['internal_edge_count']}"},
        ],
    }
    return guide


def _graph(
    inventory: dict[str, Any],
    audit: dict[str, Any],
    import_graph: dict[str, Any],
    flow_map: dict[str, Any],
    script_check: dict[str, Any],
) -> dict[str, Any]:
    internal_edges = [
        edge
        for edge in import_graph.get("edges", [])
        if edge.get("scope") == "internal" and edge.get("to")
    ]
    incoming_by_file = Counter(str(edge["to"]) for edge in internal_edges)
    outgoing_by_file = Counter(str(edge["from"]) for edge in internal_edges)
    flows = flow_map.get("flows", [])

    def related_flows_for(path: str) -> list[str]:
        normalized = path.rstrip("/")
        return [
            flow["title"]
            for flow in flows
            if any(
                str(entry).startswith(path)
                or str(entry).startswith(normalized + "/")
                or str(entry) == normalized
                for entry in flow.get("entrypoints", [])
            )
        ][:6]

    def insight(path: str, kind: str, file_count: int | None = None) -> dict[str, Any]:
        related_flows = related_flows_for(path)
        if path.endswith("/"):
            incoming = sum(count for target, count in incoming_by_file.items() if target.startswith(path))
            outgoing = sum(count for source, count in outgoing_by_file.items() if source.startswith(path))
        else:
            incoming = incoming_by_file[path]
            outgoing = outgoing_by_file[path]
        return {
            "meaning": _functional_meaning(path, kind, file_count),
            "next_read": _node_next_read(kind, path, incoming, outgoing, related_flows),
            "signals": _node_signals(path, kind, incoming, outgoing, related_flows, inventory),
            "metrics": {
                "incoming_internal_imports": incoming,
                "outgoing_internal_imports": outgoing,
                **({"file_count": file_count} if file_count is not None else {}),
            },
        }

    nodes: list[dict[str, Any]] = [
        {
            "id": "target",
            "label": Path(inventory["root"]).name,
            "kind": "entrypoint",
            "group": "目标项目",
            "layer": "Source",
            "path": ".",
            "summary": "被分析的项目根目录。",
            "meaning": "分析的目标项目根；所有结构、流程、风险和阅读路线都从这里展开。",
            "next_read": "从入口候选、manifest 和 flow-map 开始，再沿 import graph 追踪主路径。",
            "signals": [
                f"project types={', '.join(inventory.get('project_types', []))}",
                f"files scanned={inventory.get('file_count_scanned', 0)}",
            ],
            "metrics": {
                "files_scanned": inventory.get("file_count_scanned", 0),
                "manifest_count": len(inventory.get("manifests", [])),
                "entrypoint_count": len(inventory.get("entrypoint_candidates", [])),
            },
        }
    ]
    edges: list[dict[str, Any]] = []

    def add_node(
        node_id: str,
        label: str,
        kind: str,
        group: str,
        path: str,
        summary: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "id": node_id,
            "label": label,
            "kind": kind,
            "group": group,
            "layer": group,
            "path": path,
            "summary": summary,
        }
        if extra:
            payload.update(extra)
        nodes.append(
            payload
        )
        edges.append({"from": "target", "to": node_id, "label": "contains", "kind": "contains"})

    for item in inventory.get("manifests", [])[:10]:
        add_node(
            f"manifest-{slugify(item)}",
            item,
            "config",
            "Manifests",
            item,
            "项目配置或元数据入口。",
            insight(item, "config"),
        )
    for item in inventory.get("entrypoint_candidates", [])[:10]:
        add_node(
            f"entry-{slugify(item)}",
            item,
            "entrypoint",
            "Entrypoints",
            item,
            "可能的用户或运行入口。",
            insight(item, "entrypoint"),
        )
    for item, count in list(inventory.get("top_directories", {}).items())[:12]:
        if item.endswith("/"):
            kind = _path_kind(item, inventory)
            add_node(
                f"dir-{slugify(item)}",
                item,
                kind,
                "Top directories",
                item,
                f"顶层目录，扫描到 {count} 个文件。",
                insight(item, kind, count),
            )

    nodes.append(
        {
            "id": "vibe-audit",
            "label": "vibe-audit",
            "kind": "test",
            "group": "Checks",
            "layer": "Checks",
            "path": "vibe_audit.json",
            "summary": f"发现 {audit['summary']['finding_count']} 条可能的生成遗留或验证风险。",
            "meaning": "启发式风险检查结果；帮助定位缺验证、缺脚本、半接线 UI 或疑似未使用文件。",
            "next_read": "把这些 findings 当作追踪线索，先验证再决定是否重构或删除。",
            "signals": [f"findings={audit['summary']['finding_count']}"],
            "metrics": {"findings": audit["summary"]["finding_count"]},
        }
    )
    edges.append({"from": "vibe-audit", "to": "target", "label": "examines", "kind": "examines"})

    nodes.append(
        {
            "id": "flow-map",
            "label": "flow-map",
            "kind": "data",
            "group": "Checks",
            "layer": "Checks",
            "path": "flow_map.json",
            "summary": f"发现 {flow_map['summary']['flow_count']} 条入口或流程线索。",
            "meaning": "按项目类型提取的入口和流程候选；用于决定从哪里开始阅读真实用户路径。",
            "next_read": "优先选择用户可触发入口，再沿 entrypoints 和 import graph 展开。",
            "signals": [f"flows={flow_map['summary']['flow_count']}"],
            "metrics": {"flows": flow_map["summary"]["flow_count"]},
        }
    )
    edges.append({"from": "flow-map", "to": "target", "label": "maps", "kind": "maps"})

    nodes.append(
        {
            "id": "script-check",
            "label": "script-check",
            "kind": "test",
            "group": "Checks",
            "layer": "Checks",
            "path": "script_check.json",
            "summary": f"检查 {script_check['summary']['check_count']} 个脚本或命令入口声明。",
            "meaning": "脚本和命令入口的静态可信度检查；判断 README/package/pyproject 声明是否指向真实目标。",
            "next_read": "先修 missing/warn 的入口声明，再把 ok 的脚本作为运行或验证路径。",
            "signals": [f"checks={script_check['summary']['check_count']}"],
            "metrics": {"checks": script_check["summary"]["check_count"]},
        }
    )
    edges.append({"from": "script-check", "to": "target", "label": "checks", "kind": "checks"})

    existing_node_ids = {node["id"] for node in nodes}

    def ensure_file_node(path: str, group: str = "Import graph") -> str:
        node_id = f"file-{slugify(path)}"
        if node_id not in existing_node_ids:
            kind = _path_kind(path, inventory)
            nodes.append(
                {
                    "id": node_id,
                    "label": path,
                    "kind": kind,
                    "group": group,
                    "layer": group,
                    "path": path,
                    "summary": "由 import graph 发现的源码文件。",
                    **insight(path, kind),
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

    for flow in flow_map.get("flows", [])[:24]:
        flow_id = f"flow-{slugify(flow['id'])}"
        nodes.append(
            {
                "id": flow_id,
                "label": flow["title"],
                "kind": "entrypoint",
                "group": "Flow map",
                "layer": "Flow map",
                "path": ", ".join(flow.get("entrypoints", [])[:2]) or "flow_map.json",
                "summary": "; ".join(flow.get("evidence", [])[:2]) or "入口或流程线索。",
                "meaning": f"{flow['title']}：{'; '.join(flow.get('evidence', [])[:2]) or '由 flow-map 提取的入口或流程线索。'}",
                "next_read": "打开对应 entrypoints，确认这个流程是否是用户真实触发路径。",
                "signals": [f"kind={flow.get('kind', 'flow')}", *[f"entrypoint={entry}" for entry in flow.get("entrypoints", [])[:3]]],
                "metrics": {"entrypoints": len(flow.get("entrypoints", [])), "evidence_items": len(flow.get("evidence", []))},
            }
        )
        edges.append({"from": "flow-map", "to": flow_id, "label": flow["kind"], "kind": "maps"})

    def reading_step_for(path: str) -> dict[str, str]:
        if path in inventory.get("entrypoint_candidates", []):
            node = f"entry-{slugify(path)}"
        elif path in inventory.get("manifests", []):
            node = f"manifest-{slugify(path)}"
        elif path.endswith("/"):
            node = f"dir-{slugify(path)}"
        else:
            node = f"file-{slugify(path)}"
        return {
            "label": path,
            "node": node,
            "path": path,
            "summary": _node_next_read(_path_kind(path, inventory), path, incoming_by_file[path], outgoing_by_file[path], related_flows_for(path)),
        }

    reading_steps = [reading_step_for(path) for path in _top_reading_order(inventory)]

    return {
        "title": f"{Path(inventory['root']).name} 快速学习图",
        "summary": "可搜索、可点击的代码结构与功能含义地图，覆盖入口、配置、目录、源码文件、流程线索和风险证据。",
        "locale": "zh-CN",
        "nodes": nodes,
        "edges": edges,
        "flows": [
            {
                "name": "推荐阅读路线",
                "summary": "按入口、manifest 和顶层目录排列的第一轮阅读顺序。",
                "steps": reading_steps,
            },
            {
                "name": "快速学习流程",
                "summary": "先盘点结构，再审计生成遗留，最后阅读入口并制定优化路线。",
                "steps": [
                    {"label": "盘点文件与 manifest", "node": "target", "path": "inventory.json", "summary": "建立项目类型、入口、目录分布。"},
                    {"label": "检查 vibe-coded 风险", "node": "vibe-audit", "path": "vibe_audit.json", "summary": "寻找未接线、缺验证、缺文件、重复实现等线索。"},
                    {"label": "提取 import graph", "node": "target", "path": "import_graph.json", "summary": "用文件级依赖边确认实际接线方向。"},
                    {"label": "建立 flow map", "node": "flow-map", "path": "flow_map.json", "summary": "按项目类型提取 CLI、服务、前端、skill 等入口线索。"},
                    {"label": "检查脚本入口", "node": "script-check", "path": "script_check.json", "summary": "验证声明的脚本、bin、Python entrypoint 是否指向真实目标。"},
                    {"label": "阅读入口文件", "node": "target", "path": ".", "summary": "从 entrypoint candidates 开始追踪真实路径。"},
                    {"label": "排优化顺序", "node": "vibe-audit", "path": "open-questions.md", "summary": "先修验证和接线，再做架构和功能优化。"},
                ],
            }
        ],
        "evidence": [
            {"claim": "Project types were inferred from manifests and filenames.", "path": "inventory.json", "detail": ", ".join(inventory.get("project_types", []))},
            {"claim": "Vibe audit findings are heuristic leads, not deletion proof.", "path": "vibe_audit.json", "detail": f"{audit['summary']['finding_count']} findings"},
            {"claim": "Import graph edges are file-level static dependencies.", "path": "import_graph.json", "detail": f"{import_graph['summary']['internal_edge_count']} internal edges"},
            {"claim": "Flow map entries are project-kind aware entrypoint hints.", "path": "flow_map.json", "detail": f"{flow_map['summary']['flow_count']} flows"},
            {"claim": "Script checks validate declared command targets without running them.", "path": "script_check.json", "detail": f"{script_check['summary']['check_count']} checks"},
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
    flow_map = create_flow_map(target_path, max_files=max_files)
    script_check = check_scripts(target_path)
    graph = _graph(inventory, audit, import_graph, flow_map, script_check)
    guide = _learning_guide(inventory, import_graph, flow_map, script_check, graph)
    graph["guide"] = guide

    write_inventory(inventory, output_root / "inventory.json")
    write_audit(audit, output_root / "vibe_audit.json")
    write_import_graph(import_graph, output_root / "import_graph.json")
    write_flow_map(flow_map, output_root / "flow_map.json")
    write_script_check(script_check, output_root / "script_check.json")
    _write(output_root / "learning_guide.json", json.dumps(guide, indent=2, ensure_ascii=False))
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

先看 manifest 和入口文件，确认项目实际运行方式；再看 `flow_map.json` 和 `script_check.json` 找用户可触发入口；再看 `import_graph.json` 的内部依赖边确认实际接线；最后看 `vibe_audit.json`，把疑似生成遗留和验证缺口当作下一步追踪线索。

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

`flow_map.json` 提取到 {flow_map['summary']['flow_count']} 条入口/流程线索；`script_check.json` 检查了 {script_check['summary']['check_count']} 个脚本或命令入口声明。

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
1. `code-analyst inventory` 扫描项目形态、manifest、入口候选、目录分布。
2. `code-analyst flow-map` 按项目类型提取 CLI、服务、前端、skill 等入口线索。
3. `code-analyst script-check` 检查声明的脚本、bin、Python entrypoint 是否指向真实目标。
4. `code-analyst import-graph` 提取 Python/JS/TS 的静态 import 边，确认源码文件之间的实际依赖方向。
5. `code-analyst vibe-audit` 检查缺少验证、缺失脚本目标、半接线 UI、疑似未引用文件、重复实现。
6. `code-analyst pack` 生成 Markdown 和 JSON，供 agent 继续做证据化解释。
7. Agent 从入口文件追踪真实行为，并把不确定内容标为 Inference。

Side effects: 只写入中央分析包，不写目标项目。

Output: `overview.md`、`architecture.md`、`flows.md`、`diagrams.md`、`open-questions.md`、`inventory.json`、`flow_map.json`、`script_check.json`、`import_graph.json`、`vibe_audit.json`、`learning_guide.json`、`understanding_graph.json`。
""",
    )

    _write(
        output_root / "diagrams.md",
        """# Diagrams

## Skill + CLI 学习框架

```mermaid
flowchart TD
  User[用户问题] --> Skill[skill 判断模式]
  Skill --> Inventory[code-analyst inventory]
  Skill --> Audit[code-analyst vibe-audit]
  Skill --> Pack[code-analyst pack]
  Inventory --> Evidence[结构证据]
  Audit --> Risks[风险线索]
  Pack --> Notes[学习包]
  Notes --> Improve[优化路线]
```

## 产物管线

```mermaid
flowchart LR
  Target[目标项目] --> Scan[inventory.json]
  Target --> Flow[flow_map.json]
  Target --> Scripts[script_check.json]
  Target --> Imports[import_graph.json]
  Target --> Audit[vibe_audit.json]
  Scan --> Markdown[Markdown notes]
  Flow --> Graph[understanding_graph.json]
  Scripts --> Questions[open-questions.md]
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
        "flow_map": flow_map,
        "script_check": script_check,
        "audit": audit,
        "guide": guide,
        "graph": graph,
    }
