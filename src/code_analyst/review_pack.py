"""Generate read-only review and design guidance from existing evidence."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .pack import _write, create_pack


SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2, "info": 3}


def _evidence(path: str, detail: str) -> dict[str, str]:
    return {"path": path, "detail": detail}


def _advice(
    *,
    category: str,
    title: str,
    severity: str,
    confidence: str,
    implementation_risk: str,
    why: str,
    recommendation: str,
    evidence: list[dict[str, str]],
) -> dict[str, Any]:
    advice_id = "-".join(part.lower() for part in f"{category} {title}".replace("/", " ").split())[:90]
    return {
        "id": advice_id,
        "category": category,
        "title": title,
        "severity": severity,
        "confidence": confidence,
        "implementation_risk": implementation_risk,
        "why": why,
        "recommendation": recommendation,
        "evidence": evidence,
    }


def _responsibility_for(name: str) -> str:
    clean = name.rstrip("/")
    lower = clean.lower()
    if lower == "readme.md":
        return "项目入口说明、快速开始和导航。"
    if lower == "agents.md":
        return "agent 在本项目内工作的本地约束。"
    if lower == "index.md":
        return "中央分析库或项目索引说明。"
    if lower == "pyproject.toml":
        return "Python 包元数据、命令入口和构建配置。"
    if lower == ".gitignore":
        return "版本控制忽略规则。"
    if lower in {"src", "lib", "app"}:
        return "主要产品或工具实现代码。"
    if lower in {"tests", "test", "__tests__"}:
        return "回归测试和行为验证。"
    if lower in {"docs", "doc"}:
        return "项目契约、设计记录和使用说明。"
    if lower in {"skill", "skills"}:
        return "agent-facing skill 指令、引用资料和运行包装。"
    if lower in {"scripts", "bin"}:
        return "本地安装、同步、检查或命令入口脚本。"
    if lower in {"components", "pages", "routes"}:
        return "用户界面、路由或可交互页面。"
    if lower in {"server", "api", "services"}:
        return "服务端接口、后台流程或外部系统集成。"
    if lower in {"config", "configs"}:
        return "运行、构建或工具配置。"
    if lower.startswith("."):
        return "工具或平台配置。"
    return "需要结合入口和 import graph 进一步确认职责。"


def _part_summaries(pack: dict[str, Any]) -> list[dict[str, Any]]:
    inventory = pack["inventory"]
    import_graph = pack["import_graph"]
    flow_map = pack["flow_map"]
    parts: list[dict[str, Any]] = []
    flows = flow_map.get("flows", [])
    edges = import_graph.get("edges", [])

    for name, count in list(inventory.get("top_directories", {}).items())[:16]:
        prefix = name
        incoming = 0
        outgoing = 0
        for edge in edges:
            source = edge.get("from") or ""
            target = edge.get("to") or ""
            if source.startswith(prefix):
                outgoing += 1
            if target.startswith(prefix):
                incoming += 1

        related_flows = [
            flow["title"]
            for flow in flows
            if any(str(entry).startswith(prefix) or str(entry) == name.rstrip("/") for entry in flow.get("entrypoints", []))
        ][:6]
        parts.append(
            {
                "path": name,
                "file_count": count,
                "responsibility": _responsibility_for(name),
                "connections": {
                    "incoming_internal_imports": incoming,
                    "outgoing_internal_imports": outgoing,
                    "related_flows": related_flows,
                },
                "next_read": "从相关 flow、入口文件和 import 边开始追踪真实行为。" if related_flows or outgoing else "先确认它是否属于真实运行路径。",
            }
        )
    return parts


def _verification_advice(pack: dict[str, Any]) -> list[dict[str, Any]]:
    audit = pack["audit"]
    findings = audit.get("findings", [])
    advice: list[dict[str, Any]] = []
    for finding in findings:
        if finding.get("category") == "verification":
            advice.append(
                _advice(
                    category="verification",
                    title=finding["title"],
                    severity=finding["severity"],
                    confidence="medium",
                    implementation_risk="low",
                    why=finding["detail"],
                    recommendation=finding["recommendation"],
                    evidence=[_evidence("vibe_audit.json", finding["title"])],
                )
            )
    return advice


def _script_advice(pack: dict[str, Any]) -> list[dict[str, Any]]:
    checks = pack["script_check"].get("checks", [])
    advice: list[dict[str, Any]] = []
    for check in checks:
        if check.get("status") not in {"missing", "warn"}:
            continue
        severity = "high" if check.get("status") == "missing" else "medium"
        advice.append(
            _advice(
                category="reliability",
                title=f"Script or entrypoint needs attention: {check['name']}",
                severity=severity,
                confidence="high",
                implementation_risk="low",
                why=check["detail"],
                recommendation="先修复声明的命令入口，再把它当作项目验证或运行路径使用。",
                evidence=[_evidence("script_check.json", f"{check['source']}:{check['name']} -> {check.get('target')}")],
            )
        )
    return advice


def _vibe_advice(pack: dict[str, Any]) -> list[dict[str, Any]]:
    advice: list[dict[str, Any]] = []
    for finding in pack["audit"].get("findings", []):
        if finding.get("category") == "verification":
            continue
        implementation_risk = "medium" if finding.get("severity") == "high" else "low"
        advice.append(
            _advice(
                category=finding.get("category", "review"),
                title=finding["title"],
                severity=finding["severity"],
                confidence="medium",
                implementation_risk=implementation_risk,
                why=finding["detail"],
                recommendation=finding["recommendation"],
                evidence=[_evidence("vibe_audit.json", finding.get("path") or finding["title"])],
            )
        )
    return advice


def _architecture_advice(pack: dict[str, Any]) -> list[dict[str, Any]]:
    inventory = pack["inventory"]
    import_graph = pack["import_graph"]
    flow_map = pack["flow_map"]
    advice: list[dict[str, Any]] = []

    if import_graph["summary"].get("internal_edge_count", 0) == 0 and inventory["file_count_scanned"] > 3:
        advice.append(
            _advice(
                category="architecture",
                title="Internal wiring is not visible from static imports",
                severity="medium",
                confidence="medium",
                implementation_risk="medium",
                why="当前扫描没有发现内部 import 边；这可能是项目很小，也可能说明运行路径依赖框架约定、动态加载或还没有真正接线。",
                recommendation="从 flow-map 的入口开始人工追踪运行路径，并补一个 smoke check 来证明核心路径真实可运行。",
                evidence=[_evidence("import_graph.json", "internal_edge_count=0"), _evidence("flow_map.json", f"flows={flow_map['summary']['flow_count']}")],
            )
        )

    if flow_map["summary"].get("flow_count", 0) == 0:
        advice.append(
            _advice(
                category="architecture",
                title="No obvious user-facing or runtime flow was detected",
                severity="medium",
                confidence="medium",
                implementation_risk="medium",
                why="没有检测到 CLI、服务、前端、Node package 或 skill 入口线索。",
                recommendation="先补清楚项目入口：README、manifest script、CLI entrypoint 或服务启动点至少需要一个可信入口。",
                evidence=[_evidence("flow_map.json", "flow_count=0")],
            )
        )

    if len(inventory.get("top_directories", {})) >= 8:
        advice.append(
            _advice(
                category="architecture",
                title="Clarify module boundaries before feature expansion",
                severity="low",
                confidence="medium",
                implementation_risk="medium",
                why="顶层目录较多，继续扩功能前最好确认每个目录的职责、依赖方向和归属边界。",
                recommendation="按用户入口或业务对象重画模块边界，把共享工具、运行入口、生成产物和测试支持分清。",
                evidence=[_evidence("inventory.json", f"top_directories={len(inventory.get('top_directories', {}))}")],
            )
        )
    return advice


def _implementation_plan(advice_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = [
        {
            "step": "验证优先",
            "goal": "先找到或补齐一个能失败的最小检查。",
            "reason": "没有验证闭环时，review 和重构建议都容易变成猜测。",
        },
        {
            "step": "入口可信",
            "goal": "修复缺失脚本、命令入口或不清楚的启动路径。",
            "reason": "入口不可信时，后续流程图和架构判断都缺少锚点。",
        },
        {
            "step": "接线确认",
            "goal": "从 flow-map 和 import graph 追踪真实用户路径。",
            "reason": "先确认哪些文件真的参与运行，再处理疑似遗留代码。",
        },
        {
            "step": "边界整理",
            "goal": "按职责收拢目录、模块和命名。",
            "reason": "边界清楚后，目标项目再做重构实现会更稳。",
        },
        {
            "step": "体验与性能",
            "goal": "最后再扩功能、做 UX/性能/部署 polish。",
            "reason": "先证明核心行为，再提高完成度。",
        },
    ]
    categories = {item["category"] for item in advice_items}
    if "ui" in categories:
        plan.insert(
            3,
            {
                "step": "交互走查",
                "goal": "逐个确认控件、handler、state 和渲染结果是否闭环。",
                "reason": "UI 半接线是 vibe-coded 项目里最常见的假完成状态之一。",
            },
        )
    return plan


def build_review(pack: dict[str, Any]) -> dict[str, Any]:
    advice_items: list[dict[str, Any]] = []
    advice_items.extend(_verification_advice(pack))
    advice_items.extend(_script_advice(pack))
    advice_items.extend(_vibe_advice(pack))
    advice_items.extend(_architecture_advice(pack))
    advice_items.sort(key=lambda item: (SEVERITY_RANK.get(item["severity"], 99), item["category"], item["title"]))

    severity_counts = Counter(item["severity"] for item in advice_items)
    category_counts = Counter(item["category"] for item in advice_items)
    return {
        "target": pack["inventory"]["root"],
        "output_root": pack["output_root"],
        "mode": "read-only analysis assistant",
        "summary": {
            "project_types": pack["inventory"].get("project_types", []),
            "part_count": len(pack["inventory"].get("top_directories", {})),
            "advice_count": len(advice_items),
            "severity_counts": dict(sorted(severity_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "flow_count": pack["flow_map"]["summary"]["flow_count"],
            "script_check_count": pack["script_check"]["summary"]["check_count"],
        },
        "parts": _part_summaries(pack),
        "advice": advice_items,
        "implementation_plan": _implementation_plan(advice_items),
        "boundary": "This pack provides analysis and recommendations only. Apply changes inside the target project.",
    }


def _format_evidence(items: list[dict[str, str]]) -> str:
    if not items:
        return "无"
    return "; ".join(f"{item['path']}: {item['detail']}" for item in items)


def render_review_markdown(review: dict[str, Any]) -> str:
    parts = review.get("parts", [])
    advice = review.get("advice", [])
    plan = review.get("implementation_plan", [])

    part_lines = []
    for part in parts[:16]:
        flows = ", ".join(part["connections"].get("related_flows", [])) or "暂无直接 flow 线索"
        part_lines.append(
            f"- `{part['path']}`: {part['responsibility']} 文件数 {part['file_count']}；"
            f"内部入边 {part['connections']['incoming_internal_imports']}，出边 {part['connections']['outgoing_internal_imports']}；"
            f"{flows}。"
        )
    if not part_lines:
        part_lines = ["- 暂无可归纳的顶层部分。"]

    advice_lines = []
    for item in advice[:40]:
        advice_lines.append(
            f"- [{item['severity']}/{item['confidence']}/{item['implementation_risk']}] "
            f"{item['title']}: {item['recommendation']} Evidence: {_format_evidence(item['evidence'])}"
        )
    if not advice_lines:
        advice_lines = ["- 暂无明显自动化 review 建议；建议人工从入口路径继续阅读。"]

    plan_lines = [f"{index}. {item['step']}: {item['goal']} {item['reason']}" for index, item in enumerate(plan, start=1)]

    return f"""# Review Pack

## 定位

这是只读代码分析建议，不是目标项目 patch。真正修改请回到目标项目自己的测试、提交和迭代流程里完成。

## 项目概况

- Target: `{review['target']}`
- Project types: {", ".join(review['summary']['project_types'])}
- Flow hints: {review['summary']['flow_count']}
- Script checks: {review['summary']['script_check_count']}
- Advice count: {review['summary']['advice_count']}

## 每个部分在做什么

{chr(10).join(part_lines)}

## Review 与改进建议

{chr(10).join(advice_lines)}

## 建议实施顺序

{chr(10).join(plan_lines)}
"""


def create_review_pack(
    target: Path | str,
    out: str | Path | None = None,
    max_files: int = 3000,
    tree_depth: int = 3,
) -> dict[str, Any]:
    pack = create_pack(target, out=out, max_files=max_files, tree_depth=tree_depth)
    output_root = Path(pack["output_root"])
    review = build_review(pack)
    _write(output_root / "review_pack.json", json.dumps(review, indent=2, ensure_ascii=False))
    _write(output_root / "review.md", render_review_markdown(review))
    return {**pack, "review": review}
