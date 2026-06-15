from __future__ import annotations

import contextlib
import io
import unittest

from code_analyst import cli


class CliTest(unittest.TestCase):
    def test_sync_skill_dry_run_delegates_to_script(self) -> None:
        self.assertEqual(cli.main(["sync-skill", "--targets", "codex", "--dry-run"]), 0)

    def test_update_help_is_available(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                cli.main(["update", "--help"])
        self.assertEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
