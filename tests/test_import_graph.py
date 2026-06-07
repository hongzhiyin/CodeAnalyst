from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase_understanding.import_graph import create_import_graph


class ImportGraphTest(unittest.TestCase):
    def test_python_internal_import_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "pkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "app.py").write_text("from .helper import run\nimport json\n", encoding="utf-8")
            (pkg / "helper.py").write_text("def run(): pass\n", encoding="utf-8")

            graph = create_import_graph(root)

        internal = {(edge["from"], edge["to"]) for edge in graph["edges"] if edge["scope"] == "internal"}
        external = {edge["module"] for edge in graph["edges"] if edge["scope"] == "external"}
        self.assertIn(("pkg/app.py", "pkg/helper.py"), internal)
        self.assertIn("json", external)

    def test_python_src_layout_import_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "src" / "demo_pkg"
            tests = root / "tests"
            pkg.mkdir(parents=True)
            tests.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
            (tests / "test_core.py").write_text("from demo_pkg.core import VALUE\n", encoding="utf-8")

            graph = create_import_graph(root)

        internal = {(edge["from"], edge["to"]) for edge in graph["edges"] if edge["scope"] == "internal"}
        self.assertIn(("tests/test_core.py", "src/demo_pkg/core.py"), internal)

    def test_javascript_internal_import_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            src.mkdir()
            (src / "app.ts").write_text("import { run } from './lib';\nconst x = require('./extra.js');\n", encoding="utf-8")
            (src / "lib.ts").write_text("export function run() {}\n", encoding="utf-8")
            (src / "extra.js").write_text("module.exports = {}\n", encoding="utf-8")

            graph = create_import_graph(root)

        internal = {(edge["from"], edge["to"]) for edge in graph["edges"] if edge["scope"] == "internal"}
        self.assertIn(("src/app.ts", "src/lib.ts"), internal)
        self.assertIn(("src/app.ts", "src/extra.js"), internal)


if __name__ == "__main__":
    unittest.main()
