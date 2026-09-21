import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_import_v2', ROOT / 'training/b4artists_ml/import_followup_review_v2.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewImportTests(unittest.TestCase):
    def test_real_capture_and_regression(self):
        result = review.validate()
        self.assertEqual((result['candidate_acceptable'], result['baseline_acceptable']), (7, 5))
        self.assertEqual(result['preferences'], dict(candidate=4, baseline=0, tie=6, neither=6))
        walk = next(c for c in result['cases'] if c['id'] == 'rigify_basic/walk')
        self.assertFalse(walk['candidate_acceptable'])
        self.assertTrue(walk['baseline_acceptable'])
        self.assertFalse(result['training_authorized'])

    def test_invalid_capture_fails_closed(self):
        original = review.read(review.EXPORT)
        mutations = [lambda d: d.update(complete=1), lambda d: d.update(training_authorized=True),
            lambda d: d['cases'].pop(), lambda d: d['cases'].__setitem__(0, d['cases'][1]),
            lambda d: d['cases'][0]['rating'].update(locked=False),
            lambda d: d['cases'][0]['rating']['values'].update(naturalnessA=''),
            lambda d: d['cases'][0]['rating']['values'].update(correctionsA='nan'),
            lambda d: d['cases'][0]['rating']['values'].update(notes='fabricated'),
            lambda d: d['cases'][0]['revealed_identity']['A'].update(variant='baseline'),
            lambda d: d.update(source_data_sha256='0'*64)]
        for mutation in mutations:
            value = copy.deepcopy(original)
            mutation(value)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                review.validate(value)

    def test_duplicate_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.json'
            for invalid in ('{"a":1,"a":2}', '{"a":NaN}'):
                path.write_text(invalid)
                with self.assertRaises(ValueError):
                    review.read(path)


if __name__ == '__main__':
    unittest.main()
