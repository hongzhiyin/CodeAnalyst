# Codebase Understanding

This project is docs-driven. Read `docs/SPEC.md` first, then `docs/ROADMAP.md`, then `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` as needed.

Use the local CLI through:

```bash
PYTHONPATH=src python3 -m codebase_understanding.cli doctor
PYTHONPATH=src python3 -m codebase_understanding.cli inventory TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli import-graph TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli vibe-audit TARGET
PYTHONPATH=src python3 -m codebase_understanding.cli pack TARGET
```

Do not write into analyzed target projects unless the user explicitly asks. Default persistent analysis artifacts to `/Users/chihoyo/Project/CodebaseUnderstanding/analyses/`.
