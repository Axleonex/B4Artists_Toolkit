"""Fail-closed tests for the smallest temporal learner boundary."""
from pathlib import Path
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))

from train_temporal_minimal_v1 import build_preflight, evaluate_preflight, run_pipeline


class TemporalMinimalPipelineTests(unittest.TestCase):
    def test_current_receipts_stop_before_model_import_and_artifact_creation(self):
        with tempfile.TemporaryDirectory(
            dir=ROOT / "training" / "b4artists_ml" / "cache"
        ) as temporary:
            report_path = Path(temporary) / "report.json"
            candidate_path = Path(temporary) / "candidate.npz"
            report = run_pipeline(report_path=report_path, candidate_path=candidate_path)
            self.assertEqual(report["status"], "BLOCKED_BEFORE_TRAINING")
            self.assertFalse(report["training_started"])
            self.assertFalse(report["candidate_artifact_created"])
            self.assertFalse(candidate_path.exists())
            self.assertFalse(report["model_promotion_permitted"])
            saved = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "BLOCKED_BEFORE_TRAINING")
            self.assertIn("action-disjointness", " ".join(saved["preflight"]["failures"]))
            self.assertIn("human-reviewed contact/intent", " ".join(saved["preflight"]["failures"]))
            self.assertIn("identity/authorization", " ".join(saved["preflight"]["failures"]))

    def test_preflight_requires_manifest_bound_review_identity_and_disjoint_corpus(self):
        decision = build_preflight()
        self.assertFalse(decision["training_authorized"])
        self.assertFalse(decision["model_training_permitted"])
        self.assertFalse(decision["model_promotion_permitted"])
        failures = " ".join(decision["failures"])
        self.assertIn("action-disjointness", failures)
        self.assertIn("human-reviewed contact/intent", failures)
        self.assertIn("identity/authorization", failures)

    def test_forged_stored_intake_cannot_replace_source_receipt_recomputation(self):
        audit = {"action_disjoint": True}
        protocol = {
            "action_partition_has_no_group_leakage": True,
            "rig_disjoint": True,
            "reviewed_contact_intent_available": True,
        }
        forged = {
            "status": "QUALIFIED_FOR_PARENT_BOUNDARY",
            "qualified_for_parent_boundary": True,
            "failures": [],
            "manifest": {"manifest_sha256": "a" * 64},
            "reviewed_contact_intent": {"valid": True, "receipt_sha256": "b" * 64},
            "identity_authorization": {"valid": True, "receipt_sha256": "c" * 64},
        }
        recomputed = {
            **forged,
            "status": "BLOCKED_INTAKE_MISSING_EVIDENCE",
            "qualified_for_parent_boundary": False,
            "failures": ["source receipt missing"],
            "reviewed_contact_intent": {"valid": False},
            "identity_authorization": {"valid": False},
        }
        boundary = {
            "status": "BLOCKED_DATA_BOUNDARY_UNQUALIFIED",
            "model_training_permitted": False,
            "model_promotion_permitted": False,
        }
        decision = evaluate_preflight(
            audit, protocol, None, None, forged, recomputed, boundary, "a" * 64
        )
        self.assertFalse(decision["training_authorized"])
        self.assertIn("does not match recomputed", " ".join(decision["failures"]))


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TemporalMinimalPipelineTests)
    )
    print("B4ML_TEMPORAL_MINIMAL_RESULT:", "PASS" if result.wasSuccessful() else "FAIL", flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
