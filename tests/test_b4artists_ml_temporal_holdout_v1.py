"""Static contract tests for the subject-disjoint temporal holdout evaluator."""

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))

from evaluate_temporal_holdout_v1 import holdout_manifest, subject  # noqa: E402


class TemporalHoldoutContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ROOT / "training" / "b4artists_ml"
        cls.protocol = json.loads((cls.root / "holdout_protocol_v1.json").read_text())
        cls.manifest = json.loads((cls.root / "data_manifest.json").read_text())
        cls.training_manifest = json.loads(
            (cls.root / "results" / "training_manifest_v4.json").read_text()
        )

    def test_holdout_is_subject_disjoint_and_excludes_subject_13(self):
        derived, rows = holdout_manifest(self.manifest, self.protocol, self.training_manifest)
        self.assertEqual({subject(row["clip"]) for row in rows}, {"16", "35"})
        self.assertTrue(all(row["split"] == "holdout" for row in derived["files"]))
        train_validation = {
            subject(row["clip"])
            for row in self.manifest["files"]
            if row["split"] in {"train", "validation"}
        }
        train_validation.update(
            subject(row["clip"])
            for row in self.training_manifest["files"]
            if row["split"] in {"train", "validation"}
        )
        self.assertTrue({"16", "35"}.isdisjoint(train_validation))
        self.assertNotIn("13", {subject(row["clip"]) for row in rows})

    def test_protocol_requires_validation_selection_and_no_observed_development(self):
        self.assertEqual(self.protocol["selection_split_required"], "validation")
        self.assertFalse(self.protocol["observed_development_loaded_required"])

    def test_source_test_rows_are_present(self):
        _, rows = holdout_manifest(self.manifest, self.protocol, self.training_manifest)
        self.assertEqual([row["clip"] for row in rows], ["16_01", "16_17", "35_01", "35_17"])
        self.assertTrue(all(row["source_split"] == "test" for row in rows))


if __name__ == "__main__":
    unittest.main()
