"""Validate and summarize temporal-envelope and weighted-boundary experiments."""
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "training" / "b4artists_ml"
ENVELOPE_DIR = TRAINING / "results" / "jump-temporal-envelope-v1"
WEIGHTED_DIR = TRAINING / "results" / "group-weighted-trajectory-v3"
BOUNDARY_DIR = TRAINING / "results" / "world-metric-boundary-v1"
SUMMARY = TRAINING / "results" / "jump-temporal-envelope-summary-v1.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.perf_counter()
    checkpoint = read(ROOT / "docs/b4artists_ml/checkpoint-recorded-jump-reference-v1.json")
    evidence = read(ROOT / checkpoint["evidence"])
    assert checkpoint["round"] == 69 and not checkpoint["active_jobs"]
    assert all(sha256(ROOT / path) == digest for path, digest in evidence["artifacts"].items())

    envelope = read(ENVELOPE_DIR / "report.json")
    weighted = read(WEIGHTED_DIR / "report.json")
    weighted_process = read(WEIGHTED_DIR / "process.json")
    boundary = read(BOUNDARY_DIR / "report.json")
    boundary_process = read(BOUNDARY_DIR / "process.json")
    assert envelope["complete"] and not envelope["qualified"] and not envelope["method_promoted"]
    assert envelope["script_sha256"] == sha256(TRAINING / "compare_jump_temporal_envelopes_v1.py")
    assert envelope["plot_sha256"] == sha256(ENVELOPE_DIR / "temporal-envelope-ratios.png")
    assert len(envelope["material_exceedances"]) == 5 and not envelope["confirmation_read"]
    assert weighted["complete"] and weighted["selected"] == "grouped16" and not weighted["method_promoted"]
    assert weighted["script_sha256"] == sha256(TRAINING / "solve_group_weighted_trajectory_v3.py")
    assert len(weighted["variants"]) == 3 and all(row["sampled_constraints_passed"] for row in weighted["variants"])
    assert all(row["trajectory_sha256"] == sha256(WEIGHTED_DIR / f"{row['name']}.npz")
               for row in weighted["variants"])
    assert weighted_process["complete"] and weighted_process["exit_code"] == 3221225477
    assert weighted_process["log_sha256"] == sha256(WEIGHTED_DIR / "host.log")
    assert boundary["script_sha256"] == sha256(TRAINING / "probe_world_metric_boundary_v1.py")
    assert not boundary["complete"] and "assert feasible" in boundary["error"]
    assert len(boundary["cases"]) == 2 and all(len(case["lambdas"]) == 4 for case in boundary["cases"])
    assert not any(row["hard_pass"] for case in boundary["cases"] for row in case["lambdas"])
    assert boundary_process["exit_code"] == 3221225477 and not boundary_process["complete"]
    assert boundary_process["log_sha256"] == sha256(BOUNDARY_DIR / "host.log")

    final_spatial_limits = {"com": 2e-4, "contact": 2e-4, "orientation": 0.001}
    boundary_rows = []
    for case in boundary["cases"]:
        candidates = []
        for row in case["lambdas"]:
            final_gate_pass = all(row["hard"][name] <= limit for name, limit in final_spatial_limits.items())
            candidates.append({
                "strength": row["strength"],
                "strict_inner_projection_pass": row["hard_pass"],
                "final_spatial_gate_pass": final_gate_pass,
                "hard": row["hard"],
                "boundary_speed_rad_s": row["boundary_speed"]["max_rad_s"],
                "boundary_speed_member": row["boundary_speed"]["max_member"],
                "speed_vs_source_ratio": (row["boundary_speed"]["max_rad_s"] /
                                          case["source_seed_boundary_speed"]["max_rad_s"]),
                "speed_vs_recorded_max_ratio": row["boundary_speed_recorded_max_ratio"],
            })
        assert all(row["final_spatial_gate_pass"] for row in candidates)
        best = min(candidates, key=lambda row: row["speed_vs_source_ratio"])
        boundary_rows.append({
            "phase": case["phase"],
            "source_speed_rad_s": case["source_seed_boundary_speed"]["max_rad_s"],
            "group_weighted_speed_rad_s": case["weighted_seed_boundary_speed"]["max_rad_s"],
            "group_weighted_amplification": (case["weighted_seed_boundary_speed"]["max_rad_s"] /
                                             case["source_seed_boundary_speed"]["max_rad_s"]),
            "recorded_max_rad_s": case["recorded_upper_speed_max_envelope"],
            "source_vs_recorded_max_ratio": (case["source_seed_boundary_speed"]["max_rad_s"] /
                                             case["recorded_upper_speed_max_envelope"]),
            "best_world_metric_candidate": best,
            "candidates": candidates,
        })

    selected = next(row for row in weighted["variants"] if row["name"] == weighted["selected"])
    baseline = next(row for row in weighted["variants"] if row["name"] == "uniform")
    distal = next(row for row in weighted["variants"] if row["name"] == "distal64")
    summary = {
        "schema": 1,
        "complete": True,
        "full_goal_complete": False,
        "method_promoted": False,
        "material_exceedances": [{
            "phase": row["phase"], "group": row["group"], "quantity": row["quantity"],
            "p99_ratio": row["ratios"]["p99"], "max_ratio": row["ratios"]["max"],
            "max_member": row["stress"]["max_member"],
        } for row in envelope["material_exceedances"]],
        "weighted_projection": {
            "baseline_score": weighted["baseline_score"],
            "selected": weighted["selected"],
            "selected_score": weighted["selected_score"],
            "selected_to_baseline_ratio": weighted["score_improvement_ratio"],
            "selected_spatial_max": selected["spatial_max"],
            "selected_samples": selected["passes"][-1]["samples"],
            "distal_score": distal["selection_score"],
            "all_variants_spatial_pass": True,
        },
        "boundary_world_metric": boundary_rows,
        "strict_inner_projection_feasible": False,
        "published_final_spatial_gate_feasible_at_two_boundaries": True,
        "host_shutdown_clean": False,
        "source_preserved": True,
        "production_changed": False,
        "confirmation_read": False,
        "decision": (
            "Use a trajectory-level world-orientation objective to minimize correction amplification relative to the "
            "authored source around contact boundaries. Keep final spatial gates and pins exact. Recorded envelopes "
            "calibrate group/phase weighting but do not override authored timing, especially in the recovery stress case."
        ),
        "next_experiment": (
            "Coupled boundary-window SQP with source-relative upper-body world-orientation residuals, explicit endpoint/pin "
            "anchors, and the existing final COM/contact/orientation gates."
        ),
        "limitations": [
            "Three recorded jumps from one actor and one artificial BoneForge stress request.",
            "The world-metric probe checks two boundary samples, not full-trajectory acceleration or interpolation.",
            "Its candidates pass the published final spatial gate but miss the stricter internal 2e-5 projector target.",
            "No production integration, learned behavior, visual/human assessment, force validation, or Cascadeur comparison."
        ],
        "artifacts": {
            "envelope_report": sha256(ENVELOPE_DIR / "report.json"),
            "weighted_report": sha256(WEIGHTED_DIR / "report.json"),
            "boundary_report": sha256(BOUNDARY_DIR / "report.json"),
        },
        "runtime_seconds": time.perf_counter() - started,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "material_exceedances": len(summary["material_exceedances"]),
        "weighted_selected": summary["weighted_projection"],
        "boundaries": boundary_rows,
        "full_goal_complete": False,
        "method_promoted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
