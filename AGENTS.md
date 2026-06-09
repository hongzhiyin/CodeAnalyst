# CodeAnalyst

This project is docs-driven. Read `docs/SPEC.md` first, then `docs/ROADMAP.md`, then `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` as needed.

Use the local CLI through:

```bash
PYTHONPATH=src python3 -m code_analyst.cli doctor
PYTHONPATH=src python3 -m code_analyst.cli inventory TARGET
PYTHONPATH=src python3 -m code_analyst.cli flow-map TARGET
PYTHONPATH=src python3 -m code_analyst.cli script-check TARGET
PYTHONPATH=src python3 -m code_analyst.cli import-graph TARGET
PYTHONPATH=src python3 -m code_analyst.cli vibe-audit TARGET
PYTHONPATH=src python3 -m code_analyst.cli pack TARGET
PYTHONPATH=src python3 -m code_analyst.cli review-pack TARGET
PYTHONPATH=src python3 -m code_analyst.cli visual-pack TARGET
```

Do not write into analyzed target projects unless the user explicitly asks. Default persistent analysis artifacts to `/Users/chihoyo/Project/CodeAnalyst/analyses/`.
