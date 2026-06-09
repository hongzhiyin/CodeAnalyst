from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_analyst.flow_map import create_flow_map


class FlowMapTest(unittest.TestCase):
    def test_detects_python_cli_and_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cli.py").write_text("import argparse\nif __name__ == '__main__': pass\n", encoding="utf-8")
            (root / "server.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

            flow_map = create_flow_map(root)

        kinds = {flow["kind"] for flow in flow_map["flows"]}
        self.assertIn("python-cli", kinds)
        self.assertIn("service", kinds)

    def test_detects_frontend_and_node_flows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            src.mkdir()
            (root / "package.json").write_text(
                json.dumps({"scripts": {"dev": "vite --host 0.0.0.0"}, "bin": {"demo": "src/cli.js"}}),
                encoding="utf-8",
            )
            (src / "App.tsx").write_text(
                "export default function App(){ const [x,setX]=useState(0); return <button onClick={() => setX(x+1)}>Go</button> }\n",
                encoding="utf-8",
            )
            (src / "cli.js").write_text("#!/usr/bin/env node\n", encoding="utf-8")

            flow_map = create_flow_map(root)

        kinds = {flow["kind"] for flow in flow_map["flows"]}
        self.assertIn("frontend", kinds)
        self.assertIn("frontend-ui", kinds)
        self.assertIn("node-cli", kinds)


if __name__ == "__main__":
    unittest.main()
