"""Command line interface for CodeAnalyst."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from . import __version__
from .flow_map import create_flow_map, flow_map_summary, write_flow_map
from .import_graph import create_import_graph, import_graph_summary, write_import_graph
from .inventory import create_inventory, inventory_summary, write_inventory
from .pack import create_pack
from .render_site import render_site
from .review_pack import create_review_from_pack, create_review_pack
from .script_check import check_scripts, script_check_summary, write_script_check
from .verify_site import site_verification_summary, verify_site, write_site_verification
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


def cmd_script_check(args: argparse.Namespace) -> int:
    report = check_scripts(args.target)
    if args.out:
        path = write_script_check(report, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(report)
    else:
        print(script_check_summary(report))
    return 0


def cmd_flow_map(args: argparse.Namespace) -> int:
    flow_map = create_flow_map(args.target, max_files=args.max_files)
    if args.out:
        path = write_flow_map(flow_map, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(flow_map)
    else:
        print(flow_map_summary(flow_map))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    result = create_pack(args.target, out=args.out, max_files=args.max_files, tree_depth=args.tree_depth)
    output_root = Path(result["output_root"])
    print(f"Wrote pack: {output_root}")
    print(f"Inventory files: {result['inventory']['file_count_scanned']}")
    print(f"Import edges: {result['import_graph']['summary']['edge_count']}")
    print(f"Flow hints: {result['flow_map']['summary']['flow_count']}")
    print(f"Script checks: {result['script_check']['summary']['check_count']}")
    print(f"Vibe findings: {result['audit']['summary']['finding_count']}")
    print("Next read:")
    for name in result["inventory"].get("entrypoint_candidates", [])[:8]:
        print(f"- {name}")
    return 0


def cmd_render_site(args: argparse.Namespace) -> int:
    index_path = render_site(args.graph_json, args.out, args.locale)
    print(f"Wrote site: {index_path}")
    return 0


def cmd_verify_site(args: argparse.Namespace) -> int:
    report = verify_site(args.site)
    if args.out:
        path = write_site_verification(report, args.out)
        print(f"Wrote: {path}")
    if args.json:
        _print_json(report)
    else:
        print(site_verification_summary(report))
    return 0 if report["ok"] else 1


def cmd_visual_pack(args: argparse.Namespace) -> int:
    result = create_pack(args.target, out=args.out, max_files=args.max_files, tree_depth=args.tree_depth)
    output_root = Path(result["output_root"])
    index_path = render_site(output_root / "understanding_graph.json", output_root / "site", args.locale)
    print(f"Wrote pack: {output_root}")
    print(f"Wrote site: {index_path}")
    print(f"Inventory files: {result['inventory']['file_count_scanned']}")
    print(f"Import edges: {result['import_graph']['summary']['edge_count']}")
    print(f"Flow hints: {result['flow_map']['summary']['flow_count']}")
    print(f"Script checks: {result['script_check']['summary']['check_count']}")
    print(f"Vibe findings: {result['audit']['summary']['finding_count']}")
    if args.verify_site:
        report = verify_site(index_path.parent)
        write_site_verification(report, output_root / "site_verification.json")
        print(site_verification_summary(report))
        if not report["ok"]:
            return 1
    return 0


def cmd_review_pack(args: argparse.Namespace) -> int:
    if args.from_pack:
        result = create_review_from_pack(args.from_pack, out=args.out)
    else:
        if not args.target:
            raise SystemExit("review-pack requires TARGET unless --from-pack is supplied")
        result = create_review_pack(args.target, out=args.out, max_files=args.max_files, tree_depth=args.tree_depth)
    output_root = Path(result["output_root"])
    review = result["review"]
    print(f"Wrote review pack: {output_root}")
    print(f"Review file: {output_root / 'review.md'}")
    print(f"Advice items: {review['summary']['advice_count']}")
    if review["summary"]["severity_counts"]:
        counts = ", ".join(f"{key}={value}" for key, value in review["summary"]["severity_counts"].items())
        print(f"Severity: {counts}")
    print("Boundary: recommendations only; implement changes in the target project.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("python", sys.version_info >= (3, 10), sys.version.split()[0]))
    checks.append(("rg", shutil.which("rg") is not None, shutil.which("rg") or "not found"))
    checks.append(("code-analyst command", shutil.which("code-analyst") is not None, shutil.which("code-analyst") or "not found"))

    installed_skill = Path("/Users/chihoyo/.codex/skills/code-analyst")
    checks.append(("installed skill", installed_skill.exists(), str(installed_skill)))
    checks.append(("installed skill-local code-analyst wrapper", (installed_skill / "bin/code-analyst").exists(), str(installed_skill / "bin/code-analyst")))

    library = Path("/Users/chihoyo/Project/CodeAnalyst/analyses")
    checks.append(("analysis library", library.exists(), str(library)))

    failures = 0
    for name, ok, detail in checks:
        mark = "ok" if ok else "missing"
        print(f"{mark:7} {name}: {detail}")
        if not ok and name not in {
            "rg",
            "code-analyst command",
            "installed skill-local code-analyst wrapper",
        }:
            failures += 1

    if failures:
        print(f"Doctor found {failures} blocking issue(s).")
        return 1
    print(f"CodeAnalyst CLI {__version__} is ready.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    prog = os.environ.get("CODE_ANALYST_CLI_PROG", "code-analyst")
    parser = argparse.ArgumentParser(prog=prog, description="CodeAnalyst personal code analysis assistant.")
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

    scripts = sub.add_parser("script-check", help="Check declared scripts and command entrypoint references.")
    scripts.add_argument("target", help="Folder or file to inspect")
    scripts.add_argument("--out", help="Write script check JSON to this path")
    scripts.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    scripts.set_defaults(func=cmd_script_check)

    flows = sub.add_parser("flow-map", help="Discover project-kind aware flow and entrypoint hints.")
    flows.add_argument("target", help="Folder or file to inspect")
    flows.add_argument("--out", help="Write flow map JSON to this path")
    flows.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    flows.add_argument("--max-files", type=int, default=3000)
    flows.set_defaults(func=cmd_flow_map)

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

    verify = sub.add_parser("verify-site", help="Verify a generated visual site before opening it in a browser.")
    verify.add_argument("site", help="Path to site/ or site/index.html")
    verify.add_argument("--out", help="Write verification JSON to this path")
    verify.add_argument("--json", action="store_true", help="Print JSON instead of a text summary")
    verify.set_defaults(func=cmd_verify_site)

    visual = sub.add_parser("visual-pack", help="Generate a learning pack and render its static site.")
    visual.add_argument("target", help="Folder or file to inspect")
    visual.add_argument("--out", help="Output directory. Defaults to the central analysis library.")
    visual.add_argument("--locale", help="Override UI locale, for example zh-CN or en")
    visual.add_argument("--verify-site", action="store_true", help="Verify the generated site and write site_verification.json")
    visual.add_argument("--max-files", type=int, default=3000)
    visual.add_argument("--tree-depth", type=int, default=3)
    visual.set_defaults(func=cmd_visual_pack)

    review = sub.add_parser("review-pack", help="Generate read-only review, refactor, and architecture guidance.")
    review.add_argument("target", nargs="?", help="Folder or file to inspect")
    review.add_argument("--from-pack", help="Regenerate review files from an existing pack root without rescanning the target")
    review.add_argument("--out", help="Output directory. Defaults to the central analysis library.")
    review.add_argument("--max-files", type=int, default=3000)
    review.add_argument("--tree-depth", type=int, default=3)
    review.set_defaults(func=cmd_review_pack)

    doctor = sub.add_parser("doctor", help="Check local CLI and installed-skill readiness.")
    doctor.set_defaults(func=cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
