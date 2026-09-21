"""Regression coverage for the static external-gate handoff contract."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "check_human_gates_handoff_v1.py"


class HumanGatesHandoffTests(unittest.TestCase):
    def test_complete_static_surface_passes_and_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            previous = os.environ.get("B4ML_REPO")
            os.environ["B4ML_REPO"] = str(repo)
            try:
                spec = importlib.util.spec_from_file_location(
                    "b4ml_human_gates_handoff", SCRIPT
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for path in module.REQUIRED.values():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"fixture\n")
                report = module.main()
                self.assertEqual(report["status"], "PASS")
                self.assertFalse(report["human_input_performed"])
                self.assertFalse(report["training_authorized"])
                missing = next(iter(module.REQUIRED.values()))
                missing.unlink()
                with self.assertRaises(RuntimeError):
                    module.main()
            finally:
                if previous is None:
                    os.environ.pop("B4ML_REPO", None)
                else:
                    os.environ["B4ML_REPO"] = previous


if __name__ == "__main__":
    unittest.main()
