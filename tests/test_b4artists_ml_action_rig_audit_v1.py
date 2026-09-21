import unittest

from training.b4artists_ml.audit_action_rig_disjoint_v1 import build_report


class ActionRigDisjointAuditTests(unittest.TestCase):
    def test_frozen_manifest_is_not_action_or_rig_disjoint(self):
        manifest = {
            "files": [
                {"clip": "07_01", "split": "train", "sha256": "a"},
                {"clip": "08_01", "split": "validation", "sha256": "b"},
                {"clip": "16_02", "split": "test", "sha256": "c"},
            ]
        }
        report = build_report(manifest, manifest_hash="fixture")
        self.assertEqual(report["status"], "UNQUALIFIED_ACTION_AND_RIG_DISJOINTNESS")
        self.assertFalse(report["action_disjoint"])
        self.assertFalse(report["rig_disjoint"])
        self.assertEqual(report["cross_split_action_groups"]["01"][0]["clip"], "07_01")
        self.assertEqual(report["manifest_rig_identity_fields"], [])

    def test_rig_identity_is_required_even_when_actions_are_disjoint(self):
        manifest = {
            "files": [
                {"clip": "07_01", "split": "train", "sha256": "a"},
                {"clip": "08_02", "split": "validation", "sha256": "b"},
                {"clip": "16_03", "split": "test", "sha256": "c"},
            ]
        }
        report = build_report(manifest, manifest_hash="fixture")
        self.assertTrue(report["action_disjoint"])
        self.assertFalse(report["rig_disjoint"])
        self.assertIn("manifest contains no rig or skeleton identity", report["reasons"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
