from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.render_site import render_site


class RenderSiteTest(unittest.TestCase):
    def test_render_site_writes_html_and_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = root / "understanding_graph.json"
            out = root / "site"
            graph.write_text(
                json.dumps(
                    {
                        "title": "Demo",
                        "summary": "Demo graph",
                        "nodes": [{"id": "app", "label": "App", "kind": "entrypoint"}],
                        "edges": [],
                        "flows": [],
                        "evidence": [],
                        "questions": [],
                    }
                ),
                encoding="utf-8",
            )

            index = render_site(graph, out)

            self.assertEqual(index.resolve(), (out / "index.html").resolve())
            self.assertTrue(index.exists())
            self.assertTrue((out / "data.json").exists())
            self.assertIn('id="graph-data"', index.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
