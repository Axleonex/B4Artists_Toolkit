import copy
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"

import sys
sys.path.insert(0, str(TRAIN))
import import_followup_review_v11 as importer


class FollowupReviewImportV11Tests(unittest.TestCase):
    def test_exact_capture_qualifies_v58_only(self):
        result = importer.validate()
        accepted = [case["id"] for case in result["cases"] if case["candidate_qualified_acceptance"]]
        self.assertEqual(accepted, ["rigify_basic/run"])
        self.assertEqual(result["production_candidates_accepted"], 1)
        self.assertEqual(result["preserve_exact_cases"], ["boneforge/run@v54", "rigify_basic/run@v58"])
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["model_promotion_authorized"])
        self.assertFalse(result["cascadeur_connector_authorized"])

    def test_changed_rating_fails_capture_identity(self):
        value = importer.read(importer.EXPORT)
        changed = copy.deepcopy(value)
        changed["cases"][0]["rating"]["values"]["naturalnessB"] = "5"
        with self.assertRaisesRegex(ValueError, "visible browser state"):
            importer.validate(changed)

    def test_training_claim_fails_closed(self):
        value = importer.read(importer.EXPORT)
        changed = copy.deepcopy(value)
        changed["training_authorized"] = True
        with self.assertRaisesRegex(ValueError, "authorization"):
            importer.validate(changed, require_capture=False)


if __name__ == "__main__":
    unittest.main()
