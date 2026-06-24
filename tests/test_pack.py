from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.pack import create_pack


class PackTest(unittest.TestCase):
    def test_pack_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "demo"
            out = workspace / "out"
            target.mkdir()
            (target / "SKILL.md").write_text("---\nname: demo\n---\n# Demo\n", encoding="utf-8")

            result = create_pack(target, out=out)

            self.assertEqual(result["output_root"], str(out.resolve()))
            for name in [
                "source.md",
                "overview.md",
                "architecture.md",
                "flows.md",
                "diagrams.md",
                "open-questions.md",
                "inventory.json",
                "flow_map.json",
                "script_check.json",
                "import_graph.json",
                "vibe_audit.json",
                "learning_guide.json",
                "understanding_graph.json",
            ]:
                self.assertTrue((out / name).exists(), name)

            graph = json.loads((out / "understanding_graph.json").read_text(encoding="utf-8"))
            guide = json.loads((out / "learning_guide.json").read_text(encoding="utf-8"))
            self.assertTrue(any(node.get("meaning") for node in graph["nodes"]))
            self.assertTrue(any(node.get("next_read") for node in graph["nodes"]))
            self.assertTrue(any(node.get("signals") for node in graph["nodes"]))
            self.assertTrue(any(flow.get("name") == "推荐阅读路线" for flow in graph["flows"]))
            self.assertEqual(graph["guide"], guide)
            self.assertIn("quickstart", guide)
            self.assertIn("case_study", guide)
            self.assertIn("chapters", guide)
            self.assertTrue(guide["steps"])
            known_nodes = {node["id"] for node in graph["nodes"]}
            for step in guide["steps"]:
                self.assertTrue(step.get("path") or step.get("node"))
                if step.get("node"):
                    self.assertIn(step["node"], known_nodes)


if __name__ == "__main__":
    unittest.main()
