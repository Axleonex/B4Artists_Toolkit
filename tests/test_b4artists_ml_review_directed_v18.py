"""Read-only falsification against the frozen v18 evidence; never edit real reports."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v18_check", ROOT / "training/b4artists_ml/check_review_directed_vertical_slice_v18.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ReviewDirectedEvidenceTests(unittest.TestCase):
    def test_real_frozen_matrix_passes_without_authorizing_learning(self):
        receipt = checker.validate()
        self.assertEqual(receipt["passed"], 16)
        self.assertFalse(receipt["claim_boundary"]["human_visual_improvement_verified"])
        self.assertFalse(receipt["claim_boundary"]["temporal_model_trained"])
        self.assertFalse(receipt["claim_boundary"]["full_goal_complete"])

    def reject_report(self, profile, task, mutate):
        target = checker.CASE_ROOT / profile / task / "report.json"
        original = checker.read
        def fake(path):
            value = original(path)
            if path == target:
                value = copy.deepcopy(value)
                mutate(value)
            return value
        with patch.object(checker, "read", side_effect=fake):
            with self.assertRaises((ValueError, KeyError)):
                checker.validate()

    def test_forged_numeric_and_lifecycle_evidence_rejected(self):
        cases = [
            ("boneforge", "reach", lambda r: r.update(automated_gates={})),
            ("boneforge", "reach", lambda r: r.update(protocol_sha256="0" * 64)),
            ("boneforge", "reach", lambda r: r.update(runtime_sha256={})),
            ("boneforge", "reach", lambda r: r.update(source_restored=False)),
            ("boneforge", "reach", lambda r: r.update(blend_path="../outside.blend")),
            ("boneforge", "reach", lambda r: r["automated_metrics"].update(max_pin_residual=2)),
            ("boneforge", "reach", lambda r: r["automated_metrics"]["review_directed"].update(reach_elbow_flexion_degrees=True)),
            ("boneforge", "jump", lambda r: r["automated_metrics"]["review_directed"].update(jump_apex_rise_body_fraction=float("nan"))),
            ("boneforge", "land", lambda r: r["automated_metrics"]["review_directed"].update(land_preimpact_vertical_velocity_body_per_second=1)),
            ("imported_unity", "land", lambda r: r["automated_metrics"]["review_directed"].update(maximum_priority_lateral_torso_tilt_degrees=30)),
            ("rigify_basic", "walk", lambda r: r["automated_metrics"].update(max_rotation_velocity_jump_rad_s=999)),
        ]
        for profile, task, mutation in cases:
            with self.subTest(profile=profile, task=task, mutation=cases.index((profile, task, mutation))):
                self.reject_report(profile, task, mutation)

    def test_empty_duplicate_or_bad_process_exit_rejected(self):
        original = checker.read
        for mode in ("empty", "duplicate", "exit"):
            def fake(path):
                value = original(path)
                if path == checker.CASE_ROOT / "processes.json":
                    value = copy.deepcopy(value)
                    if mode == "empty":
                        return []
                    if mode == "duplicate":
                        value[-1] = value[0]
                    if mode == "exit":
                        value[0]["host_exit"] = 1
                return value
            with self.subTest(mode=mode), patch.object(checker, "read", side_effect=fake):
                with self.assertRaises(ValueError):
                    checker.validate()

    def test_nonfinite_nested_evidence_rejected(self):
        for bad in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                checker.finite_tree({"frames": [{"height": bad}]})

    def test_stale_review_hash_rejected(self):
        original = checker.read
        def fake(path):
            value = original(path)
            if path == checker.REVIEW_SUMMARY:
                value["human_review_sha256"] = "0" * 64
            return value
        with patch.object(checker, "read", side_effect=fake), self.assertRaises(ValueError):
            checker.validate()


if __name__ == "__main__":
    unittest.main()
