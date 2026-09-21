"""Host-independent diagnostics for the optional Cascadeur console handoff."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "cascadeur_import_audit_console_v1.py"


class CascadeurConsoleDiagnosticTests(unittest.TestCase):
    def test_missing_csc_writes_bounded_diagnostic_without_overwriting_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            output = repo / "training" / "b4artists_ml" / "results"
            output.mkdir(parents=True)
            success = output / "cascadeur-import-audit-v1.json"
            success.write_text('{"status":"PASS"}\n', encoding="utf-8")
            previous = os.environ.get("B4ML_REPO")
            os.environ["B4ML_REPO"] = str(repo)
            try:
                spec = importlib.util.spec_from_file_location("b4ml_cascadeur_console", SCRIPT)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                report = module.run()
            finally:
                if previous is None:
                    os.environ.pop("B4ML_REPO", None)
                else:
                    os.environ["B4ML_REPO"] = previous
            diagnostic = output / "cascadeur-import-audit-diagnostic-v1.json"
            self.assertEqual(report["status"], "BLOCKED_CSC_UNAVAILABLE")
            self.assertEqual(report["diagnostic"]["missing_module"], "csc")
            self.assertTrue(diagnostic.is_file())
            self.assertEqual(json.loads(success.read_text(encoding="utf-8"))["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
