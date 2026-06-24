from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.render_site import render_site


class RenderSiteTest(unittest.TestCase):
    def test_render_site_writes_guide_html_and_data(self) -> None:
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
                        "guide": {
                            "quickstart": {
                                "title": "Demo learning path",
                                "problem": "Start from a concrete user action.",
                                "why_this_path": "It teaches entrypoint first.",
                                "learning_goals": ["Find the entrypoint", "Follow evidence"],
                                "start_node": "app",
                                "start_path": "src/App.tsx",
                                "project_types": "frontend",
                            },
                            "case_study": {
                                "title": "Run the app",
                                "trigger": "User opens the UI.",
                                "mental_model": "Entrypoint to rendering.",
                                "steps": [
                                    {
                                        "label": "Open entrypoint",
                                        "summary": "Read the app entry.",
                                        "node": "app",
                                        "path": "src/App.tsx",
                                        "evidence_type": "confirmed",
                                        "evidence": "inventory.json",
                                        "takeaway": "Start from the user path.",
                                    }
                                ],
                            },
                            "chapters": [
                                {
                                    "title": "Chapter 1",
                                    "summary": "Entrypoint first.",
                                    "steps": [
                                        {
                                            "label": "Open entrypoint",
                                            "node": "app",
                                            "path": "src/App.tsx",
                                        }
                                    ],
                                }
                            ],
                            "steps": [{"label": "Open entrypoint", "node": "app", "path": "src/App.tsx"}],
                            "evidence": [{"type": "confirmed", "path": "inventory.json"}],
                        },
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
            self.assertIn("guide-section", html)
            self.assertIn("reader-grid", html)
            self.assertIn("reference-section", html)
            self.assertIn("Reference Index", html)
            self.assertIn("Demo learning path", html)
            self.assertIn("guide-jump", html)
            self.assertIn("insight-card", html)
            self.assertIn("relation-button", html)
            data = json.loads((out / "data.json").read_text(encoding="utf-8"))
            self.assertEqual(data["nodes"][0]["meaning"], "Interactive app entry.")
            self.assertEqual(data["guide"]["quickstart"]["title"], "Demo learning path")

    def test_render_site_without_guide_still_writes_graph_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = root / "understanding_graph.json"
            out = root / "site"
            graph.write_text(
                json.dumps(
                    {
                        "title": "Legacy Demo",
                        "summary": "Old graph without guide",
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

            html = index.read_text(encoding="utf-8")
            self.assertIn('id="guideSection"', html)
            self.assertIn('hidden', html)
            data = json.loads((out / "data.json").read_text(encoding="utf-8"))
            self.assertNotIn("guide", data)


if __name__ == "__main__":
    unittest.main()
