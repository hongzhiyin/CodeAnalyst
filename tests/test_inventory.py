from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_analyst.inventory import create_inventory


class InventoryTest(unittest.TestCase):
    def test_detects_python_project_and_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "cli.py").write_text("def main(): pass\n", encoding="utf-8")

            inventory = create_inventory(root)

        self.assertIn("Python project", inventory["project_types"])
        self.assertIn("pyproject.toml", inventory["manifests"])
        self.assertIn("src/cli.py", inventory["entrypoint_candidates"])


if __name__ == "__main__":
    unittest.main()
