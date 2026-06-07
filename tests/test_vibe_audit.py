from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codebase_understanding.vibe_audit import audit_vibe_project


class VibeAuditTest(unittest.TestCase):
    def test_detects_missing_script_target_and_test_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"scripts": {"build": "node scripts/missing.js"}}),
                encoding="utf-8",
            )
            audit = audit_vibe_project(root)

        titles = {item["title"] for item in audit["findings"]}
        self.assertIn("No obvious test or verification signal", titles)
        self.assertIn("Script 'build' references a missing file", titles)


if __name__ == "__main__":
    unittest.main()
