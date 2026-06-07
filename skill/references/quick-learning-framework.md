# Quick Learning Framework

Use this framework when the goal is to quickly understand a vibe-coded project, explain its principles, and decide how to improve it.

## 1. Snapshot

Goal: know what exists before guessing what matters.

Commands:

```bash
cbu inventory TARGET --out OUTPUT_ROOT/inventory.json
cbu import-graph TARGET --out OUTPUT_ROOT/import_graph.json
cbu vibe-audit TARGET --out OUTPUT_ROOT/vibe_audit.json
```

Capture:

- project type
- manifest files
- likely entrypoints
- top directories
- internal import edges
- obvious verification signals
- vibe-coded leftovers

## 2. Truth Path

Goal: find the actually wired path.

Read in this order:

1. manifest and scripts
2. app or CLI entrypoint
3. route/component/server handler
4. state/data helpers
5. IO side effects
6. tests or smoke checks

Do not trust folder names alone. Confirm imports, command scripts, handlers, route registration, or generated artifacts.

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
- framework configs without dependencies
- dependencies with no imports
- no tests/typecheck/lint/smoke path

Treat findings as leads. Confirm before deleting.

## 5. Optimization Order

Prefer this order:

1. Verification: add a small test, typecheck, lint, smoke run, or browser check.
2. Wiring: remove dead paths, connect half-wired controls, fix missing scripts.
3. Boundaries: clarify modules, data ownership, and naming.
4. Behavior: improve real user flows.
5. Polish: UI, performance, docs, and deployment niceties.

This order prevents optimizing a demo-shaped project before proving what actually works.

## 6. Output Shape

For a fast chat answer:

- project identity
- most important entrypoints
- how the main flow works
- likely leftovers or verification gaps
- next 3 reading or improvement steps

For a pack:

- `overview.md`: shortest useful mental model
- `architecture.md`: responsibilities and data direction
- `flows.md`: triggers, paths, side effects, outputs
- `diagrams.md`: behavior diagrams
- `open-questions.md`: unknowns and risk leads
- `inventory.json` and `vibe_audit.json`: machine-readable evidence
- `import_graph.json`: static file-level dependency evidence
