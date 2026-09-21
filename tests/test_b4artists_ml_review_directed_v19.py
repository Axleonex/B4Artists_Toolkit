import importlib.util
from pathlib import Path
import unittest
import copy
import json
import subprocess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_diag_v19', ROOT / 'training/b4artists_ml/diagnose_review_directed_v19.py')
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)
spec2 = importlib.util.spec_from_file_location('review_build_v19', ROOT / 'training/b4artists_ml/build_review_directed_v19.py')
builder = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(builder)


class DisplayTransformTests(unittest.TestCase):
    def test_motion_translation_not_dropped(self):
        matrix = [[1,0,0,0],[0,1,0,0],[0,0,1,2],[0,0,0,1]]
        self.assertEqual(diag.transform_point(matrix, [1,2,3]), [1,2,5])

    def test_rotation_and_translation_order(self):
        matrix = [[0,-1,0,2],[1,0,0,3],[0,0,1,4],[0,0,0,1]]
        self.assertEqual(diag.transform_point(matrix, [1,2,3]), [0,4,7])

    def test_existing_export_reproduces_missing_jump(self):
        value = diag.read(diag.OLD / 'extracted/candidate-rigify_basic-jump.json')
        self.assertLess(diag.metrics(value)['maximum_two_foot_clearance'], .002)
        report = diag.read(diag.ROOT / value['blend_path'].replace('rigify_basic-jump.blend', 'report.json'))
        self.assertGreater(report['automated_metrics']['review_directed']['jump_apex_rise_body_fraction'], .3)

    def test_native_matrix_checks_reject_malformed_values(self):
        for matrix in ([[1]], [[1,0,0,0],[0,1,0,0],[0,0,1,float('nan')],[0,0,0,1]],
                       [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,2]]):
            with self.assertRaises(ValueError):
                diag.transform_point(matrix, [1,2,3])

    def test_native_32_and_affected_only(self):
        payload, recovery = builder.assemble()
        self.assertEqual(len(payload['cases']), 10)
        self.assertEqual(len(recovery['unaffected_cases']), 6)
        self.assertEqual(recovery['native_comparisons'], 32)
        self.assertEqual({c['task'] for c in payload['cases']}, {'jump', 'land', 'run'})
        for case in payload['cases']:
            if case['task'] != 'jump':
                continue
            candidate = next(k for k,v in case['reveal'].items() if v['variant'] == 'candidate')
            self.assertGreater(diag.metrics(case['methods'][candidate])['maximum_two_foot_clearance'], .25)
        self.assertTrue(payload['prior_exposure'])
        self.assertFalse(payload['training_authorized'])
        self.assertFalse(recovery['native_animation_modified'])

    def test_stale_native_evidence_rejected(self):
        case = diag.read(diag.OLD / 'review-data.json')['cases'][0]
        real_read = builder.diag.read
        def corrupted(path):
            value = copy.deepcopy(real_read(path))
            if 'processes' in path.parts:
                value['extract_sha256'] = '0' * 64
            return value
        with patch.object(builder.diag, 'read', side_effect=corrupted), self.assertRaises(ValueError):
            builder.validate_extraction('candidate', case)

    def test_fabricated_native_parity_rejected(self):
        case = diag.read(diag.OLD / 'review-data.json')['cases'][0]
        real_read = builder.diag.read
        def corrupted(path):
            value = copy.deepcopy(real_read(path))
            if path.parent == diag.OUT / 'extracted':
                value['maximum_native_instance_error'] = .5
            return value
        with patch.object(builder.diag, 'read', side_effect=corrupted), self.assertRaises(ValueError):
            builder.validate_extraction('candidate', case)

    def test_native_exit_evidence(self):
        value = dict(variant='candidate', profile='fixture', task='jump', complete=True)
        marker = diag.marker(value)
        self.assertTrue(diag.qualified_exit(0, marker, value))
        self.assertTrue(diag.qualified_exit(3221225477, marker+'EXCEPTION_ACCESS_VIOLATION ucrtbase.dll', value))
        self.assertFalse(diag.qualified_exit(0, '', value))
        self.assertFalse(diag.qualified_exit(3221225477, 'EXCEPTION_ACCESS_VIOLATION ucrtbase.dll'+marker, value))
        self.assertFalse(diag.qualified_exit(1, marker, value))

    def test_nonblind_export_separate_storage_and_no_inherited_locks(self):
        payload, _ = builder.assemble()
        page = builder.render_page(payload, 'fixture')
        self.assertIn('b4ml-review-directed-followup-v3-', page)
        self.assertNotIn('b4ml-review-directed-followup-v2-', page)
        self.assertNotIn('localStorage.clear', page)
        self.assertNotIn('localStorage.removeItem', page)
        core = page.split('<script>', 1)[1].split('// Browser initialization', 1)[0]
        checks = r'''
const assert=require('node:assert/strict');
const rating={values:Object.fromEntries(fields.map(k=>[k,''])),failures:{A:[],B:[]}};
for(const dim of dimensions)for(const label of labels)rating.values[dim+label]='3';
for(const label of labels)rating.values['acceptable'+label]='no';
rating.values.preference='neither';
let state={reviews:{},reviewer:'test fixture',experience:'not human evidence'};
assert.equal(exportValue(state,'test').complete,false);
state=lockCase(state,data.cases[0].id,rating,'test');
assert.equal(state.reviews[data.cases[0].id].blind_at_rating,false);
let output=exportValue(state,'test');
assert.equal(output.prior_exposure,true);
assert.equal(output.schema,'b4ml-review-directed-followup-human-review-v3');
assert.equal(output.training_authorized,false);
assert.equal(output.cases.filter(c=>c.rating?.locked).length,1);
assert.equal(output.complete,false);
'''
        result = subprocess.run(['node','-'], input=core+checks, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
