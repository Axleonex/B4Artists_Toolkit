import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "review_import_v5", ROOT / "training/b4artists_ml/import_followup_review_v5.py"
)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewImportV5Tests(unittest.TestCase):
    def test_real_capture_qualifies_feedback_but_accepts_no_candidate(self):
        result = review.validate()
        self.assertEqual(result["candidate_acceptable"], 0)
        self.assertEqual(result["candidate_qualified_acceptance"], 0)
        self.assertEqual(result["acceptance_contradictions"], 0)
        self.assertEqual(result["baseline_acceptable"], 0)
        self.assertEqual(
            result["preferences"],
            dict(candidate=1, baseline=0, tie=0, neither=7),
        )
        preferred = next(
            case for case in result["cases"] if case["id"] == "rigify_default/jump"
        )
        self.assertEqual(preferred["preference"], "candidate")
        self.assertEqual(preferred["candidate_scores"], [3, 2, 2, 3])
        run = next(case for case in result["cases"] if case["id"] == "rigify_basic/run")
        self.assertIn("Center of gravity", run["notes"])
        self.assertFalse(any(case["candidate_qualified_acceptance"] for case in result["cases"]))
        self.assertTrue(result["display_representation_qualified"])
        self.assertTrue(result["relative_pose_feedback_qualified"])
        self.assertTrue(result["global_motion_feedback_qualified"])
        self.assertTrue(result["jump_height_feedback_qualified"])
        self.assertTrue(result["production_acceptance_qualified"])
        self.assertEqual(result["production_candidates_accepted"], 0)
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["model_promotion_authorized"])

    def test_invalid_capture_fails_closed(self):
        original = review.read(review.EXPORT)
        mutations = [
            lambda data: data.update(complete=1),
            lambda data: data.update(native_display_validated=False),
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
