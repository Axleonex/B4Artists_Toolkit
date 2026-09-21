import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "review_import_v4", ROOT / "training/b4artists_ml/import_followup_review_v4.py"
)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewImportV4Tests(unittest.TestCase):
    def test_real_capture_fails_closed_on_contradictory_acceptance(self):
        result = review.validate()
        self.assertEqual(result["candidate_acceptable"], 1)
        self.assertEqual(result["candidate_qualified_acceptance"], 0)
        self.assertEqual(result["acceptance_contradictions"], 1)
        self.assertEqual(result["baseline_acceptable"], 0)
        self.assertEqual(
            result["preferences"],
            dict(candidate=0, baseline=0, tie=0, neither=8),
        )
        jump = next(case for case in result["cases"] if case["id"] == "boneforge/jump")
        self.assertIn("jump higher", jump["notes"])
        run = next(case for case in result["cases"] if case["id"] == "rigify_basic/run")
        self.assertTrue(run["candidate_acceptable"])
        self.assertFalse(run["candidate_qualified_acceptance"])
        self.assertEqual(run["preference"], "neither")
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["model_promotion_authorized"])
        self.assertFalse(result["display_representation_qualified"])
        self.assertTrue(result["relative_pose_feedback_qualified"])
        self.assertFalse(result["global_motion_feedback_qualified"])
        self.assertFalse(result["jump_height_feedback_qualified"])
        self.assertFalse(result["production_acceptance_qualified"])

    def test_invalid_capture_fails_closed(self):
        original = review.read(review.EXPORT)
        mutations = [
            lambda data: data.update(complete=1),
            lambda data: data.update(training_authorized=True),
            lambda data: data.update(source_human_review_sha256="0" * 64),
            lambda data: data.update(source_qualification_sha256="0" * 64),
            lambda data: data["cases"].pop(),
            lambda data: data["cases"][0]["rating"].update(locked=False),
            lambda data: data["cases"][0]["rating"].update(blind_at_rating=True),
            lambda data: data["cases"][0]["rating"]["values"].update(naturalnessA=""),
            lambda data: data["cases"][0]["rating"]["values"].update(correctionsA="nan"),
            lambda data: data["cases"][0]["rating"]["values"].update(notes="fabricated"),
            lambda data: data["cases"][0]["revealed_identity"]["A"].update(variant="baseline"),
        ]
        for mutation in mutations:
            value = copy.deepcopy(original)
            mutation(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                review.validate(value)

    def test_duplicate_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.json"
            for invalid in ('{"a":1,"a":2}', '{"a":NaN}'):
                path.write_text(invalid)
                with self.assertRaises(ValueError):
                    review.read(path)


if __name__ == "__main__":
    unittest.main()
