"""Independent timing, review preservation and evidence-binding tests."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
spec = importlib.util.spec_from_file_location("followup_v2", TRAIN / "build_review_directed_followup_reviewer_v2.py")
reviewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer)


class FollowupReviewerTests(unittest.TestCase):
    def test_browser_core_timing_and_amendments(self):
        page = reviewer.TEMPLATE.read_text(encoding="utf-8")
        core = page.split("<script>", 1)[1].split("// Browser initialization", 1)[0]
        fixture = {"cases": [{"id": "one", "reveal": {}}, {"id": "two", "reveal": {}}], "source_qualification_sha256": "fixture"}
        core = core.replace("__REVIEW_DATA__", json.dumps(fixture)).replace("__DATA_SHA256__", "fixture")
        checks = r'''
const assert=require('node:assert/strict');
function method(end){return {frames:[1,end],fps:24,duration_seconds:(end-1)/24,samples:[[[0,0,0]],[[100,0,0]]]};}
assert.equal(sampleAt(method(25),.5).points[0][0],50);
assert.equal(sampleAt(method(49),.5).points[0][0],25);
assert.equal(sampleAt(method(25),5).points[0][0],100);
assert.equal(sampleAt(method(25),5).ended,true);
assert.equal(sampleAt(method(49),-.5).points[0][0],0);
assert.equal(sampleAt(method(49),.5).sourceFrame,13);
const rating={values:Object.fromEntries(fields.map(k=>[k,''])),failures:{A:[],B:[]}};
for(const dimension of dimensions)for(const label of labels)rating.values[dimension+label]='3';
for(const label of labels)rating.values['acceptable'+label]='no';
rating.values.preference='neither';rating.values.notes='human fixture, not a real review';
assert.equal(ratingError(rating),''); // estimates are optional
rating.values.correctionsA='-1';assert.notEqual(ratingError(rating),'');rating.values.correctionsA='';
rating.values.naturalnessA='';assert.notEqual(ratingError(rating),'');rating.values.naturalnessA='3';
let state={reviews:{},reviewer:'fixture',experience:'fixture'};
state=setDraft(state,'one',rating);
assert.equal(exportValue(state,'now').complete,false);
state=lockCase(state,'one',rating,'first');
state=lockCase(state,'two',rating,'first');
assert.equal(exportValue(state,'now').complete,true);
const other=JSON.stringify(state.reviews.two);
assert.throws(()=>setDraft(state,'one',rating));
state=amendCase(state,'one','second');
assert.equal(exportValue(state,'now').complete,false);
assert.equal(state.reviews.one.history.length,1);
assert.equal(state.reviews.one.history[0].blind_at_rating,true);
const amended=structuredClone(rating);amended.values.notes='added landing note';
state=lockCase(state,'one',amended,'third');
assert.equal(state.reviews.one.blind_at_rating,false);
assert.equal(state.reviews.one.history[0].values.notes,rating.values.notes);
assert.equal(JSON.stringify(state.reviews.two),other);
assert.equal(exportValue(state,'now').training_authorized,false);
assert.equal(exportValue(state,'now').cases.length,2);
console.log('timing, holding, optional estimates, draft, lock, amendment history, other-case preservation, and export gates: PASS');
'''
        result = subprocess.run(["node", "-"], input=core + checks, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_host_exit_requires_result_before_shutdown_fault(self):
        value = dict(variant="candidate", profile="boneforge", task="jump", complete=True, error=None, seconds=1)
        marker = "B4ML_FOLLOWUP_REVIEW_EXTRACT=" + json.dumps(value)
        self.assertTrue(reviewer.qualified_exit(0, marker, value))
        self.assertTrue(reviewer.qualified_exit(3221225477, marker + "\nEXCEPTION_ACCESS_VIOLATION\nucrtbase.dll", value))
        self.assertFalse(reviewer.qualified_exit(3221225477, "EXCEPTION_ACCESS_VIOLATION\nucrtbase.dll\n" + marker, value))
        self.assertFalse(reviewer.qualified_exit(1, marker + "\nucrtbase.dll", value))
        self.assertFalse(reviewer.qualified_exit(0, "", value))

    def test_extraction_shape_and_staleness(self):
        source = reviewer.OUT / "extracted/baseline-boneforge-reach.json"
        value = reviewer.read(source)
        reviewer.validate_extraction(value, "baseline", "boneforge", "reach")
        mutations = [lambda v: v.update(samples=v["samples"][:-1]),
                     lambda v: v.update(frames=v["frames"][:-1]),
                     lambda v: v.update(fps=0),
                     lambda v: v.update(fps=True),
                     lambda v: v.update(blend_sha256="0" * 64),
                     lambda v: v["samples"][0][0].__setitem__(0, float("nan")),
                     lambda v: v["frames"].__setitem__(1, v["frames"][0])]
        for i, mutate in enumerate(mutations):
            invalid = copy.deepcopy(value)
            mutate(invalid)
            with self.subTest(mutation=i), self.assertRaises(ValueError):
                reviewer.validate_extraction(invalid, "baseline", "boneforge", "reach")

    def test_page_has_separate_storage_no_global_erase_and_visible_export(self):
        page = reviewer.TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('storageKey="b4ml-review-directed-followup-v2-"', page)
        self.assertNotIn("localStorage.removeItem", page)
        self.assertNotIn("localStorage.clear", page)
        self.assertIn('id="amend"', page)
        self.assertIn('id="exportPayload"', page)
        self.assertIn('addEventListener("input",saveDraft)', page)

    def test_completed_packet_binding_and_balance(self):
        manifest_path = reviewer.OUT / "manifest.json"
        manifest = reviewer.read(manifest_path)
        self.assertEqual(manifest["cases"], 16)
        for name, key in (("review-data.json", "data_sha256"), ("reviewer.html", "html_sha256"), ("processes.json", "processes_sha256")):
            self.assertEqual(reviewer.sha(reviewer.OUT / name), manifest[key])
        data = reviewer.read(reviewer.OUT / "review-data.json")
        self.assertEqual(sum(c["reveal"]["A"]["variant"] == "candidate" for c in data["cases"]), 8)
        self.assertEqual({c["id"] for c in data["cases"]}, {f"{p}/{t}" for p, t in reviewer.CASES})
        self.assertFalse(data["training_authorized"])
        self.assertFalse(manifest["full_goal_complete"])
        for case in data["cases"]:
            for method in case["methods"].values():
                self.assertAlmostEqual(method["duration_seconds"], (method["frames"][-1]-method["frames"][0])/method["fps"])


if __name__ == "__main__":
    unittest.main()
