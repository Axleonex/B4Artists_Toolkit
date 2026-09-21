import unittest

from training.b4artists_ml.build_action_disjoint_protocol_v1 import build_protocol


class ActionDisjointProtocolTests(unittest.TestCase):
    def test_partition_is_deterministic_and_group_safe(self):
        manifest = {
            "files": [
                {"clip": "07_01", "split": "train", "sha256": "a"},
                {"clip": "08_01", "split": "validation", "sha256": "b"},
                {"clip": "09_02", "split": "train", "sha256": "c"},
                {"clip": "16_03", "split": "test", "sha256": "d"},
                {"clip": "35_04", "split": "test", "sha256": "e"},
                {"clip": "13_05", "split": "train", "sha256": "f"},
                {"clip": "13_06", "split": "train", "sha256": "g"},
            ]
        }
        first = build_protocol(manifest, manifest_hash="fixture")
        second = build_protocol(manifest, manifest_hash="fixture")
        self.assertEqual(first, second)
        self.assertTrue(first["action_partition_has_no_group_leakage"])
        self.assertFalse(first["rig_disjoint"])
        self.assertFalse(first["training_authorized"])
        self.assertEqual(len(first["action_group_assignment"]), 6)

    def test_requires_enough_action_groups(self):
        manifest = {"files": [
            {"clip": "07_01", "split": "train", "sha256": "a"},
            {"clip": "08_02", "split": "test", "sha256": "b"},
            {"clip": "09_03", "split": "validation", "sha256": "c"},
            {"clip": "16_04", "split": "test", "sha256": "d"},
            {"clip": "35_05", "split": "test", "sha256": "e"},
        ]}
        with self.assertRaisesRegex(ValueError, "six action groups"):
            build_protocol(manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
