"""Host-independent tests for the one-call Cascadeur handoff runner."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "cascadeur_embedded_gate_runner_console_v1.py"


class CascadeurEmbeddedGateRunnerTests(unittest.TestCase):
    def test_missing_csc_fails_closed_without_claims(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            output = repo / "training" / "b4artists_ml" / "results"
            output.mkdir(parents=True)
            previous = os.environ.get("B4ML_REPO")
            os.environ["B4ML_REPO"] = str(repo)
            try:
                spec = importlib.util.spec_from_file_location(
                    "b4ml_cascadeur_embedded_gate_runner", SCRIPT
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                report = module.run()
            finally:
                if previous is None:
                    os.environ.pop("B4ML_REPO", None)
                else:
                    os.environ["B4ML_REPO"] = previous
            diagnostic = output / "cascadeur-embedded-gate-runner-diagnostic-v1.json"
            self.assertEqual(report["status"], "BLOCKED_CSC_UNAVAILABLE")
            self.assertEqual(report["diagnostic"]["missing_module"], "csc")
            self.assertTrue(diagnostic.is_file())
            self.assertFalse(report["claim_boundary"]["conversion_verified"])
            self.assertFalse(report["claim_boundary"]["parity_verified"])

    def test_embedded_command_is_documented(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("<b4ml-cascadeur-gate-runner>", source)
        self.assertIn("run()", source)
        self.assertIn("conversion_verified\": False", source)


if __name__ == "__main__":
    unittest.main()

