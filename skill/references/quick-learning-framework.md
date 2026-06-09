# Quick Learning Framework

Use this framework when the goal is to quickly understand a vibe-coded project, explain its principles, and decide how to improve it. The framework is an analysis assistant: it reads code, explains parts and flows, and proposes improvement directions. It does not normally modify the target project.

## 1. Snapshot

Goal: know what exists before guessing what matters.

Commands:

```bash
code-analyst inventory TARGET --out OUTPUT_ROOT/inventory.json
code-analyst flow-map TARGET --out OUTPUT_ROOT/flow_map.json
code-analyst script-check TARGET --out OUTPUT_ROOT/script_check.json
code-analyst import-graph TARGET --out OUTPUT_ROOT/import_graph.json
code-analyst vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
code-analyst review-pack TARGET --out OUTPUT_ROOT
code-analyst review-pack --from-pack OUTPUT_ROOT
code-analyst verify-site OUTPUT_ROOT/site --out OUTPUT_ROOT/site_verification.json
```

Capture:

- project type
- manifest files
- likely entrypoints
- top directories
- project-kind flow hints
- declared script and bin health
- internal import edges
- obvious verification signals
- vibe-coded leftovers

## 2. Truth Path

Goal: find the actually wired path.

Read in this order:

1. manifest and declared scripts
2. `flow_map.json` entrypoint hints
3. app, CLI, service, skill, or frontend entrypoint
4. route/component/server handler
5. state/data helpers
6. IO side effects
7. tests or smoke checks

Do not trust folder names alone. Confirm imports, command scripts, handlers, route registration, or generated artifacts.

Use `script_check.json` before running commands. A script can be useful evidence even if it has not been executed, but missing file targets should be resolved before treating it as a working workflow.

Use `flow_map.json` to stay project-kind agnostic. CLI projects, backend services, frontend apps, Node packages, and Codex skills expose different first-class entrypoints.

Use `import_graph.json` as first-pass wiring evidence. Internal import edges show likely connected source paths; files with no incoming internal edge are not automatically dead, but they deserve extra attention.

## 3. Principle Model

Goal: explain the system in concepts, not files.

Write four short answers:

- What is the core object or state?
- What event changes it?
- Where does data enter and leave?
- What invariant should never break?

Useful diagrams:

- module map
- runtime flow
- data transformation
- state lifecycle
- evidence/risk map

## 4. Vibe Audit

Goal: identify where AI-generated code may have left plausible but untrue structure.

Check:

- unused source files
- duplicated components/services
- UI controls without handlers
- handlers with no rendered effect
- scripts that reference missing files
- package bins or Python entrypoints that point nowhere
- framework configs without dependencies
- dependencies with no imports
- no tests/typecheck/lint/smoke path

Treat findings as leads. Confirm before deleting.

## 5. Optimization Order

Prefer this order:

1. Verification: add a small test, typecheck, lint, smoke run, `verify-site`, or browser check.
2. Wiring: remove dead paths, connect half-wired controls, fix missing scripts.
3. Boundaries: clarify modules, data ownership, and naming.
4. Behavior: improve real user flows.
5. Polish: UI, performance, docs, and deployment niceties.

This order prevents optimizing a demo-shaped project before proving what actually works.

The output should be actionable but not patch-shaped by default. Give the target project a clear next implementation path, with risks and tradeoffs, then let that project own the actual edits, tests, and commits.

## 6. Output Shape

For a fast chat answer:

- project identity
- most important entrypoints
- how the main flow works
- what each major part is responsible for
- likely leftovers or verification gaps
- next 3 reading, review, or improvement steps

For a pack:

- `overview.md`: shortest useful mental model
- `architecture.md`: responsibilities and data direction
- `flows.md`: triggers, paths, side effects, outputs
- `diagrams.md`: behavior diagrams
- `open-questions.md`: unknowns and risk leads
- review/design outputs: ranked risks, refactor directions, and architecture options
- `review.md`: human-readable read-only review and improvement guidance
- `review_pack.json`: machine-readable advice, severity, confidence, evidence, and implementation order
- `inventory.json` and `vibe_audit.json`: machine-readable evidence
- `flow_map.json`: CLI/service/frontend/skill flow hints
- `script_check.json`: declared command target checks
- `import_graph.json`: static file-level dependency evidence
