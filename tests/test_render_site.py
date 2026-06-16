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
                        "nodes": [
                            {
                                "id": "app",
                                "label": "App",
                                "kind": "entrypoint",
                                "path": "src/App.tsx",
                                "meaning": "Interactive app entry.",
                                "next_read": "Follow imports from here.",
                                "signals": ["entrypoint candidate"],
                                "metrics": {"outgoing_internal_imports": 2},
                            }
                        ],
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
            html = index.read_text(encoding="utf-8")
            self.assertIn('id="graph-data"', html)
            self.assertIn("insight-card", html)
            self.assertIn("relation-button", html)
            data = json.loads((out / "data.json").read_text(encoding="utf-8"))
            self.assertEqual(data["nodes"][0]["meaning"], "Interactive app entry.")


if __name__ == "__main__":
    unittest.main()
