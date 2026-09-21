import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "review_import_v8", ROOT / "training/b4artists_ml/import_followup_review_v8.py"
)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewImportV8Tests(unittest.TestCase):
    def test_real_capture_rejects_both_run_candidates(self):
        result = review.validate()
        self.assertEqual(result["candidate_acceptable"], 0)
        self.assertEqual(result["candidate_qualified_acceptance"], 0)
        self.assertEqual(result["baseline_acceptable"], 0)
        self.assertEqual(result["preferences"]["neither"], 2)
        self.assertTrue(all("skipping" in case["notes"] for case in result["cases"]))
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["model_promotion_authorized"])
        self.assertFalse(result["cascadeur_connector_authorized"])

    def test_mutations_fail_closed(self):
        original = review.read(review.EXPORT)
        mutations = (
            lambda value: value.update(training_authorized=True),
            lambda value: value.update(source_qualification_sha256="0" * 64),
            lambda value: value["cases"].pop(),
            lambda value: value["cases"][0]["rating"].update(locked=False),
            lambda value: value["cases"][0]["rating"]["values"].update(notes="changed"),
            lambda value: value["cases"][0]["revealed_identity"]["A"].update(variant="candidate"),
        )
        for mutation in mutations:
            value = copy.deepcopy(original)
            mutation(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                review.validate(value)


if __name__ == "__main__":
    unittest.main()
