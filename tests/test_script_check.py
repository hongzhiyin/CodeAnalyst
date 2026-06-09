from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.script_check import check_scripts


class ScriptCheckTest(unittest.TestCase):
    def test_package_scripts_and_bins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "ok.js").write_text("console.log('ok')\n", encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "ok": "node scripts/ok.js",
                            "missing": "node scripts/missing.js",
                        },
                        "bin": {"demo": "scripts/ok.js"},
                    }
                ),
                encoding="utf-8",
            )

            report = check_scripts(root)

        targets = {(item["status"], item["target"]) for item in report["checks"]}
        self.assertIn(("ok", "scripts/ok.js"), targets)
        self.assertIn(("missing", "scripts/missing.js"), targets)

    def test_pyproject_script_resolves_src_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "src" / "demo"
            pkg.mkdir(parents=True)
            (pkg / "cli.py").write_text("def main(): pass\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\ndemo = 'demo.cli:main'\n",
                encoding="utf-8",
            )

            report = check_scripts(root)

        self.assertEqual(report["summary"]["status_counts"].get("ok"), 1)
        self.assertEqual(report["checks"][0]["target"], "src/demo/cli.py")


if __name__ == "__main__":
    unittest.main()
