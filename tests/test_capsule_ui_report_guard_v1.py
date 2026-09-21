"""Host-independent protection for stronger capsule lifecycle receipts."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training" / "b4artists_ml" / "check_capsule_ui_v1.py"
SPEC = importlib.util.spec_from_file_location("b4ml_capsule_ui_guard", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CapsuleUiReportGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs" / "b4artists_ml").mkdir(parents=True)
        self.old_root = MODULE.ROOT
        self.old_tag = MODULE.TAG
        MODULE.ROOT = self.root
        MODULE.TAG = "capsule-ui-guard-test-v1"

    def tearDown(self):
        MODULE.ROOT = self.old_root
        MODULE.TAG = self.old_tag
        self.temp.cleanup()

    def test_weaker_report_is_sidecar_and_authoritative_report_is_preserved(self):
        path = self.root / "docs" / "b4artists_ml" / "capsule-ui-guard-test-v1.json"
        stronger = {"passed": True, "native_undo_redo": {"status": "passed"}, "step_count": 50}
        weaker = {"passed": True, "native_undo_redo": {"status": "blocked"}, "step_count": 48}
        path.write_text(json.dumps(stronger), encoding="utf-8")

        MODULE._write_report(weaker)

        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), stronger)
        sidecar = path.with_name("capsule-ui-guard-test-v1-weaker-observation.json")
        self.assertEqual(json.loads(sidecar.read_text(encoding="utf-8")), weaker)

    def test_passing_modal_report_can_refresh_same_receipt(self):
        path = self.root / "docs" / "b4artists_ml" / "capsule-ui-guard-test-v1.json"
        stronger = {"passed": True, "native_undo_redo": {"status": "passed"}, "step_count": 50}
        refreshed = {"passed": True, "native_undo_redo": {"status": "passed"}, "step_count": 51}
        path.write_text(json.dumps(stronger), encoding="utf-8")

        MODULE._write_report(refreshed)

        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), refreshed)


if __name__ == "__main__":
    unittest.main()
