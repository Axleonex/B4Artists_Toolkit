"""Host-independent contract checks for the procedural Head evidence receipt."""

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))
import check_head_orientation_evidence_v1 as evidence


class HeadOrientationEvidenceTests(unittest.TestCase):
    def test_current_receipt_is_machine_checked(self):
        report = evidence.main()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["semantic_target"]["joint_index"], 4)
        self.assertTrue(report["semantic_target"]["direct_orientation"])

    def test_fixture_contract_covers_six_direct_orientations(self):
        report = json.loads(evidence.OUT.read_text(encoding="utf-8"))
        self.assertEqual(report["coverage"]["tests"], 10)
        self.assertEqual(len(report["coverage"]["fixtures"]), 5)
        self.assertEqual(report["coverage"]["requested_orientations_per_fixture"], 6)
        self.assertTrue(report["coverage"]["head_in_direct_orientation_set"])

    def test_claim_boundary_stays_closed(self):
        report = json.loads(evidence.OUT.read_text(encoding="utf-8"))
        boundary = report["claim_boundary"]
        self.assertTrue(boundary["procedural_evaluated_rig_constraint"])
        self.assertFalse(boundary["learned_temporal_quality_verified"])
        self.assertFalse(boundary["independent_animator_usability_verified"])
        self.assertFalse(boundary["cascadeur_parity_verified"])
        self.assertFalse(boundary["full_goal_complete"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
