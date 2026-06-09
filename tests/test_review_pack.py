from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from code_analyst.review_pack import create_review_from_pack, create_review_pack


class ReviewPackTest(unittest.TestCase):
    def test_review_pack_writes_guidance_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "demo"
            out = workspace / "out"
            (target / "src").mkdir(parents=True)
            (target / "package.json").write_text(
                '{"scripts": {"build": "node scripts/build.js"}}\n',
                encoding="utf-8",
            )
            (target / "src" / "cli.py").write_text(
                "import argparse\n\ndef main():\n    argparse.ArgumentParser()\n",
                encoding="utf-8",
            )

            result = create_review_pack(target, out=out)

            self.assertEqual(result["output_root"], str(out.resolve()))
            self.assertTrue((out / "review.md").exists())
            self.assertTrue((out / "review_pack.json").exists())

            review = json.loads((out / "review_pack.json").read_text(encoding="utf-8"))
            self.assertEqual(review["mode"], "read-only analysis assistant")
            self.assertGreaterEqual(review["summary"]["advice_count"], 2)
            self.assertIn("verification", review["summary"]["category_counts"])
            self.assertIn("reliability", review["summary"]["category_counts"])
            self.assertIn("project-specific", review["summary"]["category_counts"])
            self.assertIn("recommendations only", review["boundary"])
            self.assertIn("no patches", review["non_goals"])

    def test_review_from_pack_does_not_rescan_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "demo"
            out = workspace / "out"
            (target / "src").mkdir(parents=True)
            (target / "pyproject.toml").write_text(
                '[project]\nname = "demo"\n[project.scripts]\ndemo = "demo.cli:main"\n',
                encoding="utf-8",
            )
            (target / "src" / "demo").mkdir()
            (target / "src" / "demo" / "cli.py").write_text("def main(): pass\n", encoding="utf-8")

            create_review_pack(target, out=out)
            (out / "review.md").unlink()
            (out / "review_pack.json").unlink()
            shutil.rmtree(target)

            result = create_review_from_pack(out)

            self.assertEqual(result["source_pack_root"], str(out.resolve()))
            self.assertTrue((out / "review.md").exists())
            self.assertTrue((out / "review_pack.json").exists())
            review = json.loads((out / "review_pack.json").read_text(encoding="utf-8"))
            self.assertIn("Python project", review["summary"]["project_types"])


if __name__ == "__main__":
    unittest.main()
