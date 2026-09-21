"""Consolidate the corrected boundary-window experiments without promoting them."""
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "training" / "b4artists_ml"
RESULTS = TRAINING / "results"
SUMMARY = RESULTS / "boundary-window-trajectory-summary-v1.json"
FINAL_LIMITS = {"com": 2e-4, "contact": 2e-4, "orientation": 0.001}


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_result(directory, script):
    base = RESULTS / directory
    report = read(base / "report.json")
    process = read(base / "process.json")
    assert report["complete"] and not report["qualified"]
    assert report["script_sha256"] == sha256(TRAINING / script)
    assert process["complete"] and process["exit_code"] == 3221225477
    assert process["log_sha256"] == sha256(base / "host.log")
    assert not report.get("method_promoted", False)
    assert not report["production_changed"] and not report["confirmation_read"]
    return report, process


def main():
    started = time.perf_counter()
    corrected_world, _ = checked_result(
        "world-metric-boundary-v2", "probe_world_metric_boundary_v2.py")
    assert not corrected_world["feasibility_demonstrated"]
    final_gate_candidates = []
    for case in corrected_world["cases"]:
        source_speed = case["source_seed_boundary_speed"]["max_rad_s"]
        candidate = next(row for row in case["lambdas"] if row["strength"] == 1000.0)
        assert all(candidate["hard"][name] <= limit for name, limit in FINAL_LIMITS.items())
        final_gate_candidates.append({
            "phase": case["phase"],
            "source_speed_rad_s": source_speed,
            "weighted_speed_rad_s": case["weighted_seed_boundary_speed"]["max_rad_s"],
            "candidate_speed_rad_s": candidate["boundary_speed"]["max_rad_s"],
            "candidate_to_source_ratio": candidate["boundary_speed"]["max_rad_s"] / source_speed,
            "strict_inner_pass": candidate["hard_pass"],
            "published_final_gate_pass": True,
            "spatial": candidate["hard"],
        })

    names = [
        ("sqp_v3", "boundary-window-sqp-v3", "solve_boundary_window_sqp_v3.py"),
        ("sqp_v5", "boundary-window-sqp-v5", "solve_boundary_window_sqp_v5.py"),
        ("sqp_v6", "boundary-window-sqp-v6", "solve_boundary_window_sqp_v6.py"),
        ("adaptive_hermite_v7", "boundary-window-sqp-v7", "solve_boundary_window_sqp_v7.py"),
        ("linear_v8", "boundary-window-linear-v8", "solve_boundary_window_linear_v8.py"),
        ("linear_convergence_v9", "boundary-window-linear-v9", "solve_boundary_window_linear_v9.py"),
        ("linear_continuation_v10", "boundary-window-continuation-v10", "solve_boundary_window_continuation_v10.py"),
        ("c1_continuation_v11", "boundary-window-c1-v11", "solve_boundary_window_c1_v11.py"),
        ("fixed_lattice_v12", "boundary-window-fixed-lattice-v12", "solve_boundary_window_fixed_lattice_v12.py"),
        ("fixed_lattice_merit_v13", "boundary-window-fixed-lattice-v13", "solve_boundary_window_fixed_lattice_v13.py"),
        ("fixed_lattice_continuation_v14", "boundary-window-fixed-lattice-v14", "solve_boundary_window_fixed_lattice_v14.py"),
    ]
    experiments = []
    loaded = {}
    for label, directory, script in names:
        report, process = checked_result(directory, script)
        loaded[label] = report
        experiments.append({
            "label": label,
            "method": report["method"],
            "sampled_spatial_pass": report["sampled_constraints_passed"],
            "failed_samples": len(report.get("failed_samples", [])),
            "validation_samples": report["validation_samples"],
            "selection_score": report["selection_score"],
            "score_to_grouped_baseline": report["score_to_grouped_baseline"],
            "spatial_max": report["spatial_max"],
            "adaptive_passes": len(report.get("adaptive_passes", [])),
            "seconds": report["seconds"],
            "host_shutdown_clean": process["exit_code"] == 0,
            "report_sha256": sha256(RESULTS / directory / "report.json"),
            "trajectory_sha256": sha256(RESULTS / directory / "optimized.npz"),
        })
    assert loaded["sqp_v3"]["sampled_constraints_passed"]
    assert not loaded["sqp_v5"]["sampled_constraints_passed"]
    assert not loaded["sqp_v6"]["sampled_constraints_passed"]
    assert not loaded["adaptive_hermite_v7"]["sampled_constraints_passed"]
    assert not loaded["linear_v8"]["sampled_constraints_passed"]
    assert not loaded["linear_convergence_v9"]["sampled_constraints_passed"]
    assert loaded["linear_continuation_v10"]["sampled_constraints_passed"]
    assert loaded["c1_continuation_v11"]["sampled_constraints_passed"]
    assert not loaded["fixed_lattice_v12"]["sampled_constraints_passed"]
    assert not loaded["fixed_lattice_merit_v13"]["sampled_constraints_passed"]
    assert not loaded["fixed_lattice_continuation_v14"]["sampled_constraints_passed"]
    assert loaded["fixed_lattice_continuation_v14"]["continued_from_sha256"] == sha256(
        RESULTS / "boundary-window-fixed-lattice-v13" / "optimized.npz")

    audit_path = RESULTS / "boundary-window-c1-audit-v1" / "report.json"
    audit = read(audit_path)
    assert audit["complete"] and audit["candidate_spatial_pass"]
    assert audit["authored_pins_exact"] and audit["subinterval_temporal_regression"]
    assert audit["candidate_report_sha256"] == sha256(
        RESULTS / "boundary-window-c1-v11" / "report.json")
    assert audit["candidate_trajectory_sha256"] == sha256(
        RESULTS / "boundary-window-c1-v11" / "optimized.npz")

    summary = {
        "schema": 1,
        "complete": True,
        "full_goal_complete": False,
        "method_promoted": False,
        "corrected_world_metric": {
            "supersedes": "world-metric-boundary-v1",
            "source": "world-metric-boundary-v2",
            "report_sha256": sha256(RESULTS / "world-metric-boundary-v2" / "report.json"),
            "strict_inner_source_recovery_feasible": False,
            "published_final_gate_source_recovery_feasible": True,
            "candidates": final_gate_candidates,
        },
        "experiments": experiments,
        "c1_candidate": {
            "spatial_pass": True,
            "spatial_max": loaded["c1_continuation_v11"]["spatial_max"],
            "validation_samples": loaded["c1_continuation_v11"]["validation_samples"],
            "quarter_rate_selection_score": loaded["c1_continuation_v11"]["selection_score"],
            "quarter_rate_to_grouped_baseline": loaded["c1_continuation_v11"]["score_to_grouped_baseline"],
            "authored_pins_exact": audit["authored_pins_exact"],
            "minimum_frame_span": audit["minimum_frame_span"],
            "subinterval_max_speed_rad_s": audit["candidate"]["max_speed_rad_s"],
            "subinterval_speed_to_baseline_ratio": audit["speed_to_baseline_ratio"],
            "subinterval_max_acceleration_rad_s2": audit["candidate"]["max_acceleration_rad_s2"],
            "subinterval_acceleration_to_baseline_ratio": audit["acceleration_to_baseline_ratio"],
            "subinterval_temporal_regression": True,
            "promoted": False,
        },
        "fixed_lattice": {
            "output_knots": 221,
            "added_output_knots": 0,
            "v12_direction_accepted": False,
            "v13_final_failed_samples": len(loaded["fixed_lattice_merit_v13"]["failed_samples"]),
            "v13_selection_score": loaded["fixed_lattice_merit_v13"]["selection_score"],
            "v14_final_failed_samples": len(loaded["fixed_lattice_continuation_v14"]["failed_samples"]),
            "v14_selection_score": loaded["fixed_lattice_continuation_v14"]["selection_score"],
            "v14_spatial_max": loaded["fixed_lattice_continuation_v14"]["spatial_max"],
            "v14_plateaued": not loaded["fixed_lattice_continuation_v14"]["adaptive_passes"][-1]["accepted"],
            "promoted": False,
        },
        "source_preserved": True,
        "production_changed": False,
        "confirmation_read": False,
        "host_shutdown_clean": False,
        "decision": (
            "Keep grouped16 as the retained research baseline. Reject every boundary-window candidate for production. "
            "The C1 continuation candidate proves that exact pins and dense spatial gates can coexist, but adaptive "
            "samples serialized as output knots hide severe sub-quarter-frame temporal regressions. Fixed-lattice "
            "least-squares collocation lowers aggregate violation and quarter-rate temporal score but plateaus above "
            "the spatial gates."
        ),
        "next_experiment": (
            "Defer boundary tuning until a fixed-lattice nonlinear constrained solver can use cached spatial Jacobians, "
            "an active-set or augmented-Lagrangian merit, exact authored pins, and interval-wide speed/acceleration "
            "evaluation. Do not spend more evaluations on local penalty or line-search variants."
        ),
        "limitations": [
            "One artificial BoneForge jump and three recorded jumps from one actor.",
            "No boundary-window candidate is integrated into production.",
            "The Bforartists host completes assertions but exits with the independently reproduced Windows shutdown crash.",
            "No visual/human assessment, learned behavior, force validation, other motions, other rigs or Cascadeur comparison."
        ],
        "artifacts": {
            "audit_script": sha256(TRAINING / "audit_boundary_window_c1_v1.py"),
            "audit_report": sha256(audit_path),
            "documentation": sha256(ROOT / "docs/b4artists_ml/BOUNDARY-WINDOW-TRAJECTORY-v1.md"),
            "routing": sha256(ROOT / "docs/b4artists_ml/boundary-window-fixed-lattice-routing-v1.json"),
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "experiments": len(experiments),
        "c1_spatial_pass": summary["c1_candidate"]["spatial_pass"],
        "c1_subinterval_speed_ratio": summary["c1_candidate"]["subinterval_speed_to_baseline_ratio"],
        "c1_subinterval_acceleration_ratio": summary["c1_candidate"]["subinterval_acceleration_to_baseline_ratio"],
        "method_promoted": False,
        "full_goal_complete": False,
    }, indent=2))


if __name__ == "__main__":
    main()
