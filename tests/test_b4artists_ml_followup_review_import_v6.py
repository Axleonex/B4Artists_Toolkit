import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "review_import_v6", ROOT / "training/b4artists_ml/import_followup_review_v6.py"
)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewImportV6Tests(unittest.TestCase):
    def test_real_capture_preserves_acceptance_and_directs_bounded_repairs(self):
        result = review.validate()
        self.assertEqual(result["candidate_acceptable"], 2)
        self.assertEqual(result["candidate_qualified_acceptance"], 2)
        self.assertEqual(result["acceptance_contradictions"], 0)
        self.assertEqual(result["baseline_acceptable"], 2)
        self.assertEqual(
            result["preferences"],
            dict(candidate=1, baseline=0, tie=2, neither=5),
        )
        accepted = {
            case["id"]
            for case in result["cases"]
            if case["candidate_qualified_acceptance"]
        }
        self.assertEqual(accepted, {"rigify_default/land", "imported_unity/land"})
        jump = next(case for case in result["cases"] if case["id"] == "boneforge/jump")
        self.assertEqual(jump["preference"], "candidate")
        self.assertEqual(jump["candidate_scores"], [5, 4, 5, 5])
        self.assertIn("stops", jump["notes"])
        run = next(case for case in result["cases"] if case["id"] == "rigify_basic/run")
        self.assertIn("Center of balance", run["notes"])
        self.assertEqual(result["production_candidates_accepted"], 2)
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["model_promotion_authorized"])
        self.assertFalse(result["cascadeur_connector_authorized"])

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
            lambda data: data["cases"][0]["revealed_identity"]["A"].update(variant="candidate"),
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
