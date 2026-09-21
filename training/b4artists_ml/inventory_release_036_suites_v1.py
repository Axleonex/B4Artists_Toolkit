"""Freeze the exact unittest-loader inventory for the 0.36 release gate."""
from pathlib import Path
import hashlib
import importlib
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
BASELINE = RESULTS / "full-regression-032-v1-regression.json"
OUTPUT = RESULTS / "release-036-v1-suite-plan.json"
ADDED = (
    "test_b4artists_ml_joint_limit_presets_v1",
    "test_b4artists_ml_chest_target_v1",
    "test_b4artists_ml_chest_orientation_v1",
    "test_b4artists_ml_neck_target_v1",
    "test_b4artists_ml_target_reset_v1",
    "test_b4artists_ml_target_mirror_v1",
    "test_b4artists_ml_rig_diagnostics_v1",
    "test_b4artists_ml_mapping_corrections_v1",
    "test_b4artists_ml_pose_reuse_v1",
    "test_b4artists_ml_pole_align_v1",
    "test_b4artists_ml_pole_flip_v1",
    "test_b4artists_ml_pole_distance_v1",
    "test_b4artists_ml_pose_asset_v1",
    "test_b4artists_ml_contact_interval_edit_v1",
    "test_b4artists_ml_prop_holds_v1",
    "test_b4artists_ml_moving_platforms_v1",
    "test_b4artists_ml_contact_visualization_v1",
    "test_b4artists_ml_quadruped_head_v1",
    "test_b4artists_ml_quadruped_spine_follow_v1",
    "test_b4artists_ml_quadruped_poles_v1",
    "test_b4artists_ml_quadruped_pole_match_v1",
    "test_b4artists_ml_quadruped_gait_phase_v1",
    "test_b4artists_ml_quadruped_target_reset_v1",
    "test_b4artists_ml_quadruped_target_mirror_v1",
    "test_b4artists_ml_quadruped_pose_asset_v1",
    "test_b4artists_ml_quadruped_pole_align_v1",
    "test_b4artists_ml_quadruped_pole_controls_v1",
    "test_b4artists_ml_timing_controls_v1",
    "test_b4artists_ml_transition_timing_v1",
    "test_b4artists_ml_transition_window_v1",
    "test_b4artists_ml_breakdown_pose_v1",
    "test_b4artists_ml_transition_timing_transfer_v1",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise RuntimeError("Suite inventory already exists; retain it or choose a new run identifier")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8-sig"))
    modules = [row["suite"] for row in baseline] + list(ADDED)
    if len(modules) != 87 or len(set(modules)) != 87:
        raise ValueError("Unexpected release suite identity set")
    candidates = sorted(path.stem for path in (ROOT / "tests").glob("test_b4artists_ml*.py"))
    excluded_names = sorted(set(candidates) - set(modules))
    if len(candidates) != 124 or len(excluded_names) != 37 or set(modules) - set(candidates):
        raise ValueError("Unexpected B4Artists ML test-candidate inventory")
    exclusions = [{
        "suite": name,
        "reason": ("Goal/evaluator orchestration test outside the distributable add-on runtime."
                   if "goal_progress" in name else
                   "Deferred experimental learned/research pipeline outside the 0.36 procedural release surface."),
        "test_sha256": sha(ROOT / "tests" / (name + ".py")),
    } for name in excluded_names]
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    suites = []
    for name in modules:
        module = importlib.import_module(name)
        count = unittest.defaultTestLoader.loadTestsFromModule(module).countTestCases()
        test_path = ROOT / "tests" / (name + ".py")
        if count <= 0 or not test_path.is_file():
            raise ValueError("Invalid suite inventory entry: " + name)
        suites.append({"suite": name, "tests": count, "test_sha256": sha(test_path)})
    report = {
        "schema": 1,
        "release": "0.36.0",
        "loader": "unittest.defaultTestLoader.loadTestsFromModule",
        "suite_count": len(suites),
        "tests": sum(row["tests"] for row in suites),
        "suites": suites,
        "candidate_suite_count": len(candidates),
        "excluded_suite_count": len(exclusions),
        "excluded_suites": exclusions,
        "baseline_suite_plan": BASELINE.relative_to(ROOT).as_posix(),
        "baseline_suite_plan_sha256": sha(BASELINE),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suites": report["suite_count"], "tests": report["tests"],
                      "output": str(OUTPUT)}), flush=True)


if __name__ == "__main__":
    main()
