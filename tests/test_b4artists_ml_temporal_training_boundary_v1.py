import unittest

from training.b4artists_ml.check_temporal_training_boundary_v1 import build_gate


class TemporalTrainingBoundaryTests(unittest.TestCase):
    def test_missing_rig_and_reviewed_provenance_blocks_training(self):
        audit = {"action_disjoint": False}
        protocol = {
            "action_partition_has_no_group_leakage": True,
            "rig_disjoint": False,
            "reviewed_contact_intent_available": False,
        }
        report = build_gate(audit, protocol)
        self.assertEqual(report["status"], "BLOCKED_DATA_BOUNDARY_UNQUALIFIED")
        self.assertFalse(report["model_training_permitted"])
        self.assertIn("rig/skeleton identity", " ".join(report["failures"]))
        self.assertIn("reviewed contact/intent", " ".join(report["failures"]))

    def test_all_boundaries_are_required_before_training(self):
        audit = {"action_disjoint": True}
        protocol = {
            "action_partition_has_no_group_leakage": True,
            "rig_disjoint": True,
            "reviewed_contact_intent_available": True,
        }
        intake = {"qualified_for_parent_boundary": True}
        report = build_gate(audit, protocol, intake=intake)
        self.assertEqual(report["status"], "QUALIFIED")
        self.assertTrue(report["model_training_permitted"])
        self.assertFalse(report["model_promotion_permitted"])

    def test_missing_intake_blocks_even_when_legacy_boundaries_pass(self):
        audit = {"action_disjoint": True}
        protocol = {
            "action_partition_has_no_group_leakage": True,
            "rig_disjoint": True,
            "reviewed_contact_intent_available": True,
        }
        report = build_gate(audit, protocol)
        self.assertEqual(report["status"], "BLOCKED_DATA_BOUNDARY_UNQUALIFIED")
        self.assertFalse(report["model_training_permitted"])
        self.assertIn("temporal corpus intake", " ".join(report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
