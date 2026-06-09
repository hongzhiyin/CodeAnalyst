from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.render_site import render_site
from code_analyst.verify_site import verify_site


class VerifySiteTest(unittest.TestCase):
    def test_verify_site_accepts_rendered_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = root / "understanding_graph.json"
            site = root / "site"
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
            render_site(graph, site)

            report = verify_site(site)

            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["node_count"], 1)
            self.assertIn("file://", report["file_url"])

    def test_verify_site_rejects_missing_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = verify_site(Path(tmp) / "missing-site")

            self.assertFalse(report["ok"])
            statuses = {item["status"] for item in report["checks"]}
            self.assertIn("missing", statuses)


if __name__ == "__main__":
    unittest.main()
