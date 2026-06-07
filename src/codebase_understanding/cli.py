"""Command line interface for the Codebase Understanding framework."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .import_graph import create_import_graph, import_graph_summary, write_import_graph
from .inventory import create_inventory, inventory_summary, write_inventory
from .pack import create_pack
from .render_site import render_site
from .vibe_audit import audit_summary, audit_vibe_project, write_audit


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_inventory(args: argparse.Namespace) -> int:
    inventory = create_inventory(args.target, max_files=args.max_files, tree_depth=args.tree_depth)
    if args.out:
        path = write_inventory(inventory, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(inventory)
    else:
        print(inventory_summary(inventory))
    return 0


def cmd_vibe_audit(args: argparse.Namespace) -> int:
    audit = audit_vibe_project(args.target, max_files=args.max_files)
    if args.out:
        path = write_audit(audit, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(audit)
    else:
        print(audit_summary(audit))
    return 0


def cmd_import_graph(args: argparse.Namespace) -> int:
    graph = create_import_graph(args.target, max_files=args.max_files)
    if args.out:
        path = write_import_graph(graph, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(graph)
    else:
        print(import_graph_summary(graph))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    result = create_pack(args.target, out=args.out, max_files=args.max_files, tree_depth=args.tree_depth)
    output_root = Path(result["output_root"])
    print(f"Wrote pack: {output_root}")
    print(f"Inventory files: {result['inventory']['file_count_scanned']}")
    print(f"Import edges: {result['import_graph']['summary']['edge_count']}")
    print(f"Vibe findings: {result['audit']['summary']['finding_count']}")
    print("Next read:")
    for name in result["inventory"].get("entrypoint_candidates", [])[:8]:
        print(f"- {name}")
    return 0


def cmd_render_site(args: argparse.Namespace) -> int:
    index_path = render_site(args.graph_json, args.out, args.locale)
    print(f"Wrote site: {index_path}")
    return 0


def cmd_visual_pack(args: argparse.Namespace) -> int:
    result = create_pack(args.target, out=args.out, max_files=args.max_files, tree_depth=args.tree_depth)
    output_root = Path(result["output_root"])
    index_path = render_site(output_root / "understanding_graph.json", output_root / "site", args.locale)
    print(f"Wrote pack: {output_root}")
    print(f"Wrote site: {index_path}")
    print(f"Inventory files: {result['inventory']['file_count_scanned']}")
    print(f"Import edges: {result['import_graph']['summary']['edge_count']}")
    print(f"Vibe findings: {result['audit']['summary']['finding_count']}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("python", sys.version_info >= (3, 10), sys.version.split()[0]))
    checks.append(("rg", shutil.which("rg") is not None, shutil.which("rg") or "not found"))
    checks.append(("cbu command", shutil.which("cbu") is not None, shutil.which("cbu") or "not found"))

    installed_skill = Path("/Users/chihoyo/.codex/skills/codebase-understanding")
    checks.append(("installed skill", installed_skill.exists(), str(installed_skill)))
    checks.append(("installed inventory script", (installed_skill / "scripts/inventory.py").exists(), str(installed_skill / "scripts/inventory.py")))
    checks.append(("installed renderer script", (installed_skill / "scripts/render_understanding_site.py").exists(), str(installed_skill / "scripts/render_understanding_site.py")))

    library = Path("/Users/chihoyo/Project/CodebaseUnderstanding/analyses")
    checks.append(("analysis library", library.exists(), str(library)))

    failures = 0
    for name, ok, detail in checks:
        mark = "ok" if ok else "missing"
        print(f"{mark:7} {name}: {detail}")
        if not ok and name not in {"rg", "installed renderer script", "cbu command"}:
            failures += 1

    if failures:
        print(f"Doctor found {failures} blocking issue(s).")
        return 1
    print(f"Codebase Understanding CLI {__version__} is ready.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cbu", description="Fast codebase learning framework.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="Create a deterministic project inventory.")
    inventory.add_argument("target", help="Folder or file to inspect")
    inventory.add_argument("--out", help="Write inventory JSON to this path")
    inventory.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    inventory.add_argument("--max-files", type=int, default=3000)
    inventory.add_argument("--tree-depth", type=int, default=3)
    inventory.set_defaults(func=cmd_inventory)

    audit = sub.add_parser("vibe-audit", help="Find likely vibe-coded leftovers and missing verification signals.")
    audit.add_argument("target", help="Folder or file to inspect")
    audit.add_argument("--out", help="Write audit JSON to this path")
    audit.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    audit.add_argument("--max-files", type=int, default=3000)
    audit.set_defaults(func=cmd_vibe_audit)

    imports = sub.add_parser("import-graph", help="Extract file-level Python and JS/TS import edges.")
    imports.add_argument("target", help="Folder or file to inspect")
    imports.add_argument("--out", help="Write import graph JSON to this path")
    imports.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    imports.add_argument("--max-files", type=int, default=3000)
    imports.set_defaults(func=cmd_import_graph)

    pack = sub.add_parser("pack", help="Generate a Markdown/JSON learning pack.")
    pack.add_argument("target", help="Folder or file to inspect")
    pack.add_argument("--out", help="Output directory. Defaults to the central analysis library.")
    pack.add_argument("--max-files", type=int, default=3000)
    pack.add_argument("--tree-depth", type=int, default=3)
    pack.set_defaults(func=cmd_pack)

    render = sub.add_parser("render-site", help="Render a static site from understanding_graph.json.")
    render.add_argument("graph_json", help="Path to understanding_graph.json")
    render.add_argument("--out", default="site", help="Output site directory")
    render.add_argument("--locale", help="Override UI locale, for example zh-CN or en")
    render.set_defaults(func=cmd_render_site)

    visual = sub.add_parser("visual-pack", help="Generate a learning pack and render its static site.")
    visual.add_argument("target", help="Folder or file to inspect")
    visual.add_argument("--out", help="Output directory. Defaults to the central analysis library.")
    visual.add_argument("--locale", help="Override UI locale, for example zh-CN or en")
    visual.add_argument("--max-files", type=int, default=3000)
    visual.add_argument("--tree-depth", type=int, default=3)
    visual.set_defaults(func=cmd_visual_pack)

    doctor = sub.add_parser("doctor", help="Check local CLI and installed-skill readiness.")
    doctor.set_defaults(func=cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
